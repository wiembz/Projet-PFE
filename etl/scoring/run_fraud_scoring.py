from __future__ import annotations

import argparse
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterator

import pandas as pd
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


TARGET_SCHEMA = "iris_score"
DW_SCHEMA = "iris_dw"
ADMIN_SCHEMA = "iris_admin"
RUN_TYPE = "FRAUD"
NOTES = "Rule-based fraud scoring v1"
CONFIDENCE_LEVEL = "RULE_BASED"
BATCH_SIZE = 10_000
VALID_RISK_LEVELS = {"NORMAL", "FAIBLE", "MOYEN", "ELEVE"}

REQUIRED_FACT_SINISTRE_COLUMNS = (
    "sinistre_sk",
    "is_declaration_tardive",
    "is_declaration_antidatee",
    "is_sinistre_avant_contrat",
    "is_sinistre_precoce",
    "montant_total",
    "montant_total_net",
    "contrat_sk",
    "client_sk",
    "delai_declaration_jours",
    "anciennete_contrat_jours",
)

REQUIRED_RULE_CODES = (
    "DECLARATION_TARDIVE",
    "DECLARATION_ANTIDATEE",
    "SINISTRE_AVANT_CONTRAT",
    "SINISTRE_PRECOCE",
    "MONTANT_TOTAL_ELEVE",
    "MONTANT_TOTAL_NET_NEGATIF",
    "CONTRAT_INCONNU",
    "CLIENT_INCONNU",
)

SCORE_COLUMNS = (
    "sinistre_sk",
    "run_id",
    "score_rule",
    "score_rule_norm",
    "score_ml",
    "score_cross",
    "score_global",
    "risk_level",
    "confidence_level",
    "rules_triggered_count",
    "scored_at",
)

DETAIL_COLUMNS = (
    "fraud_score_sk",
    "sinistre_sk",
    "rule_sk",
    "rule_code",
    "run_id",
    "observed_value",
    "threshold_value",
    "rule_weight",
    "rule_contribution",
)


@dataclass(frozen=True)
class FraudRule:
    rule_sk: int
    rule_code: str
    weight: Decimal
    threshold_value: str | None


@dataclass(frozen=True)
class ScoreStats:
    run_id: str
    input_count: int
    scored_count: int
    detail_count: int
    active_rule_count: int
    total_weight_active: Decimal
    risk_normal_count: int
    risk_faible_count: int
    risk_moyen_count: int
    risk_eleve_count: int
    scoring_run_status: str


def main() -> None:
    args = _parse_args()
    stats = run_fraud_scoring(
        etl_run_id=args.etl_run_id,
        run_version=args.run_version,
        rules_version=args.rules_version,
    )
    print(f"run_id={stats.run_id}")
    print(f"input_count={stats.input_count}")
    print(f"scored_count={stats.scored_count}")
    print(f"detail_count={stats.detail_count}")
    print(f"active_rule_count={stats.active_rule_count}")
    print(f"total_weight_active={stats.total_weight_active}")
    print(f"risk_NORMAL_count={stats.risk_normal_count}")
    print(f"risk_FAIBLE_count={stats.risk_faible_count}")
    print(f"risk_MOYEN_count={stats.risk_moyen_count}")
    print(f"risk_ELEVE_count={stats.risk_eleve_count}")
    print(f"scoring_run_status={stats.scoring_run_status}")


def run_fraud_scoring(
    *,
    etl_run_id: str,
    run_version: str,
    rules_version: str,
) -> ScoreStats:
    _validate_required_text(etl_run_id, "--etl-run-id")
    _validate_required_text(run_version, "--run-version")
    _validate_required_text(rules_version, "--rules-version")

    run_id = _generate_run_id()
    conn = get_connection()
    scoring_run_inserted = False

    try:
        with conn.cursor() as cur:
            _assert_etl_run_exists(cur, etl_run_id)
            _assert_contracts(cur)
            fact_columns = _get_table_columns(cur, DW_SCHEMA, "fact_sinistre")
            _assert_fact_sinistre_contract(fact_columns)
            rules = _load_active_rules(cur, rules_version)
            total_weight_active = sum((rule.weight for rule in rules.values()), Decimal("0"))
            if total_weight_active <= 0:
                raise RuntimeError("Active fraud rules total weight must be greater than 0")

            _insert_scoring_run(cur, run_id, etl_run_id, run_version, rules_version)
            scoring_run_inserted = True
            conn.commit()

            sinistres, filter_warning = _load_fact_sinistres(cur, etl_run_id, fact_columns)
            if filter_warning:
                print(filter_warning, flush=True)
            if sinistres.empty:
                raise RuntimeError("No fact_sinistre rows selected for fraud scoring")

            score_rows, detail_source_rows, risk_counts = _score_sinistres(
                sinistres,
                run_id,
                rules,
                total_weight_active,
            )

            loaded_score_count = _upsert_score_rows(cur, score_rows)
            fraud_score_lookup = _load_fraud_score_lookup(cur, run_id)
            detail_rows = _build_detail_rows(detail_source_rows, fraud_score_lookup)
            detail_count = _upsert_detail_rows(cur, detail_rows)

            _activate_successful_run(
                cur,
                run_id,
                total_input=len(sinistres),
                total_scored=loaded_score_count,
            )
            conn.commit()

        return ScoreStats(
            run_id=run_id,
            input_count=len(sinistres),
            scored_count=loaded_score_count,
            detail_count=detail_count,
            active_rule_count=len(rules),
            total_weight_active=total_weight_active,
            risk_normal_count=risk_counts["NORMAL"],
            risk_faible_count=risk_counts["FAIBLE"],
            risk_moyen_count=risk_counts["MOYEN"],
            risk_eleve_count=risk_counts["ELEVE"],
            scoring_run_status="SUCCESS",
        )
    except Exception as exc:
        conn.rollback()
        if scoring_run_inserted:
            _mark_run_failed(conn, run_id, str(exc))
        raise
    finally:
        conn.close()


def _assert_etl_run_exists(cur: Any, etl_run_id: str) -> None:
    cur.execute(
        """
        SELECT 1
        FROM iris_admin.etl_run
        WHERE etl_run_id = %s
        LIMIT 1
        """,
        (etl_run_id,),
    )
    if cur.fetchone() is None:
        raise RuntimeError(f"iris_admin.etl_run does not contain {etl_run_id}")


def _assert_contracts(cur: Any) -> None:
    scoring_run_columns = _get_table_columns(cur, TARGET_SCHEMA, "scoring_run")
    _assert_required_columns(
        TARGET_SCHEMA,
        "scoring_run",
        scoring_run_columns,
        {
            "run_id",
            "run_type",
            "run_version",
            "started_at",
            "ended_at",
            "status",
            "is_active",
            "source_etl_run_id",
            "rules_version",
            "model_version",
            "total_input",
            "total_scored",
            "notes",
        },
    )

    score_columns = _get_table_columns(cur, TARGET_SCHEMA, "fact_fraud_score")
    _assert_required_columns(TARGET_SCHEMA, "fact_fraud_score", score_columns, set(SCORE_COLUMNS))
    _assert_constraint_exists(cur, "fact_fraud_score", "uq_fact_fraud_score")

    detail_columns = _get_table_columns(cur, TARGET_SCHEMA, "fact_fraud_rule_detail")
    _assert_required_columns(
        TARGET_SCHEMA,
        "fact_fraud_rule_detail",
        detail_columns,
        set(DETAIL_COLUMNS),
    )
    _assert_constraint_exists(cur, "fact_fraud_rule_detail", "uq_fraud_rule_detail")

    rule_columns = _get_table_columns(cur, TARGET_SCHEMA, "dim_fraud_rule")
    _assert_required_columns(
        TARGET_SCHEMA,
        "dim_fraud_rule",
        rule_columns,
        {
            "rule_sk",
            "rule_code",
            "is_active",
            "weight",
            "threshold_value",
            "rule_version",
        },
    )


def _assert_fact_sinistre_contract(fact_columns: set[str]) -> None:
    _assert_required_columns(
        DW_SCHEMA,
        "fact_sinistre",
        fact_columns,
        set(REQUIRED_FACT_SINISTRE_COLUMNS),
    )


def _assert_required_columns(
    schema_name: str,
    table_name: str,
    columns: set[str],
    required_columns: set[str],
) -> None:
    missing_columns = sorted(required_columns - columns)
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"{schema_name}.{table_name} is missing columns: {missing}")


def _assert_constraint_exists(cur: Any, table_name: str, constraint_name: str) -> None:
    cur.execute(
        """
        SELECT 1
        FROM pg_constraint c
        JOIN pg_namespace n
          ON n.oid = c.connamespace
        JOIN pg_class t
          ON t.oid = c.conrelid
        WHERE n.nspname = %s
          AND t.relname = %s
          AND c.conname = %s
          AND c.contype IN ('p', 'u')
        LIMIT 1
        """,
        (TARGET_SCHEMA, table_name, constraint_name),
    )
    if cur.fetchone() is None:
        raise RuntimeError(f"{TARGET_SCHEMA}.{table_name} is missing {constraint_name}")


def _load_active_rules(cur: Any, rules_version: str) -> dict[str, FraudRule]:
    cur.execute(
        """
        SELECT rule_sk, rule_code, weight, threshold_value
        FROM iris_score.dim_fraud_rule
        WHERE is_active IS TRUE
          AND rule_version = %s
        """,
        (rules_version,),
    )
    rules = {
        str(rule_code): FraudRule(
            rule_sk=int(rule_sk),
            rule_code=str(rule_code),
            weight=Decimal(str(weight)),
            threshold_value=threshold_value,
        )
        for rule_sk, rule_code, weight, threshold_value in cur.fetchall()
    }

    if not rules:
        raise RuntimeError(f"No active fraud rules found for rule_version={rules_version}")

    missing_rules = sorted(set(REQUIRED_RULE_CODES) - set(rules))
    if missing_rules:
        missing = ", ".join(missing_rules)
        raise RuntimeError(f"Missing active fraud rules for v1 scoring: {missing}")

    unexpected_rules = sorted(set(rules) - set(REQUIRED_RULE_CODES))
    if unexpected_rules:
        unexpected = ", ".join(unexpected_rules)
        raise RuntimeError(
            "Active rules exist for this version without v1 trigger logic: "
            f"{unexpected}"
        )

    return rules


def _insert_scoring_run(
    cur: Any,
    run_id: str,
    etl_run_id: str,
    run_version: str,
    rules_version: str,
) -> None:
    cur.execute(
        """
        INSERT INTO iris_score.scoring_run (
            run_id,
            run_type,
            run_version,
            started_at,
            status,
            is_active,
            source_etl_run_id,
            rules_version,
            model_version,
            total_input,
            total_scored,
            notes
        )
        VALUES (
            %(run_id)s,
            'FRAUD',
            %(run_version)s,
            now(),
            'STARTED',
            false,
            %(source_etl_run_id)s,
            %(rules_version)s,
            NULL,
            0,
            0,
            %(notes)s
        )
        """,
        {
            "run_id": run_id,
            "run_version": run_version,
            "source_etl_run_id": etl_run_id,
            "rules_version": rules_version,
            "notes": NOTES,
        },
    )


def _load_fact_sinistres(
    cur: Any,
    etl_run_id: str,
    fact_columns: set[str],
) -> tuple[pd.DataFrame, str | None]:
    select_columns = list(REQUIRED_FACT_SINISTRE_COLUMNS)
    select_list = sql.SQL(", ").join(sql.Identifier(column) for column in select_columns)

    if "etl_run_id" in fact_columns:
        query = sql.SQL(
            """
            SELECT {}
            FROM iris_dw.fact_sinistre
            WHERE etl_run_id = %s
            """
        ).format(select_list)
        cur.execute(query, (etl_run_id,))
        warning = None
    else:
        query = sql.SQL("SELECT {} FROM iris_dw.fact_sinistre").format(select_list)
        cur.execute(query)
        warning = (
            "WARNING: iris_dw.fact_sinistre has no etl_run_id column; "
            "scoring all fact_sinistre rows."
        )

    rows = cur.fetchall()
    return pd.DataFrame(rows, columns=select_columns), warning


def _score_sinistres(
    sinistres: pd.DataFrame,
    run_id: str,
    rules: dict[str, FraudRule],
    total_weight_active: Decimal,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    frame = sinistres.copy()
    frame["montant_total"] = pd.to_numeric(frame["montant_total"], errors="coerce")
    frame["montant_total_net"] = pd.to_numeric(frame["montant_total_net"], errors="coerce")
    frame["score_rule"] = Decimal("0")
    frame["rules_triggered_count"] = 0

    detail_rows: list[dict[str, Any]] = []

    _apply_rule(
        frame,
        detail_rows,
        run_id,
        rules["DECLARATION_TARDIVE"],
        frame["is_declaration_tardive"].fillna(False).astype(bool),
        frame["delai_declaration_jours"].map(_text_or_none),
    )
    _apply_rule(
        frame,
        detail_rows,
        run_id,
        rules["DECLARATION_ANTIDATEE"],
        frame["is_declaration_antidatee"].fillna(False).astype(bool),
        pd.Series("true", index=frame.index),
    )
    _apply_rule(
        frame,
        detail_rows,
        run_id,
        rules["SINISTRE_AVANT_CONTRAT"],
        frame["is_sinistre_avant_contrat"].fillna(False).astype(bool),
        pd.Series("true", index=frame.index),
    )
    _apply_rule(
        frame,
        detail_rows,
        run_id,
        rules["SINISTRE_PRECOCE"],
        frame["is_sinistre_precoce"].fillna(False).astype(bool),
        frame["anciennete_contrat_jours"].map(_text_or_none),
    )
    _apply_rule(
        frame,
        detail_rows,
        run_id,
        rules["MONTANT_TOTAL_ELEVE"],
        frame["montant_total"].gt(100000).fillna(False),
        frame["montant_total"].map(_text_or_none),
    )
    _apply_rule(
        frame,
        detail_rows,
        run_id,
        rules["MONTANT_TOTAL_NET_NEGATIF"],
        frame["montant_total_net"].lt(0).fillna(False),
        frame["montant_total_net"].map(_text_or_none),
    )
    _apply_rule(
        frame,
        detail_rows,
        run_id,
        rules["CONTRAT_INCONNU"],
        frame["contrat_sk"].eq(0).fillna(False),
        pd.Series("contrat_sk=0", index=frame.index),
    )
    _apply_rule(
        frame,
        detail_rows,
        run_id,
        rules["CLIENT_INCONNU"],
        frame["client_sk"].eq(0).fillna(False),
        pd.Series("client_sk=0", index=frame.index),
    )

    denominator = float(total_weight_active)
    score_rule_float = frame["score_rule"].map(float)
    frame["score_rule_norm"] = (score_rule_float / denominator * 100).clip(upper=100).round(4)
    frame["score_global"] = frame["score_rule_norm"].round(4)
    frame["risk_level"] = frame["score_global"].map(_risk_level)
    _validate_risk_levels(frame["risk_level"])

    scored_at = datetime.now()
    score_rows: list[dict[str, Any]] = []
    for row in frame.itertuples(index=False):
        score_rows.append(
            {
                "sinistre_sk": int(row.sinistre_sk),
                "run_id": run_id,
                "score_rule": _decimal_from_value(row.score_rule, "0.000000"),
                "score_rule_norm": _decimal_from_value(row.score_rule_norm, "0.0000"),
                "score_ml": None,
                "score_cross": None,
                "score_global": _decimal_from_value(row.score_global, "0.0000"),
                "risk_level": row.risk_level,
                "confidence_level": CONFIDENCE_LEVEL,
                "rules_triggered_count": int(row.rules_triggered_count),
                "scored_at": scored_at,
            }
        )

    risk_counts = {
        "NORMAL": int((frame["risk_level"] == "NORMAL").sum()),
        "FAIBLE": int((frame["risk_level"] == "FAIBLE").sum()),
        "MOYEN": int((frame["risk_level"] == "MOYEN").sum()),
        "ELEVE": int((frame["risk_level"] == "ELEVE").sum()),
    }
    return score_rows, detail_rows, risk_counts


def _apply_rule(
    frame: pd.DataFrame,
    detail_rows: list[dict[str, Any]],
    run_id: str,
    rule: FraudRule,
    trigger_mask: pd.Series,
    observed_values: pd.Series,
) -> None:
    triggered_indexes = frame.index[trigger_mask]
    if triggered_indexes.empty:
        return

    frame.loc[triggered_indexes, "score_rule"] = frame.loc[
        triggered_indexes,
        "score_rule",
    ].map(lambda value: Decimal(str(value)) + rule.weight)
    frame.loc[triggered_indexes, "rules_triggered_count"] += 1

    for index in triggered_indexes:
        detail_rows.append(
            {
                "sinistre_sk": int(frame.at[index, "sinistre_sk"]),
                "rule_sk": rule.rule_sk,
                "rule_code": rule.rule_code,
                "run_id": run_id,
                "observed_value": observed_values.at[index],
                "threshold_value": rule.threshold_value,
                "rule_weight": rule.weight,
                "rule_contribution": rule.weight,
            }
        )


def _risk_level(score_global: float) -> str:
    if score_global < 20:
        return "NORMAL"
    if score_global < 40:
        return "FAIBLE"
    if score_global < 70:
        return "MOYEN"
    return "ELEVE"


def _validate_risk_levels(risk_levels: pd.Series) -> None:
    invalid_values = sorted(set(risk_levels.dropna()) - VALID_RISK_LEVELS)
    if invalid_values:
        invalid = ", ".join(invalid_values)
        raise RuntimeError(f"Invalid risk_level values generated: {invalid}")


def _upsert_score_rows(cur: Any, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    update_columns = [
        column for column in SCORE_COLUMNS if column not in {"sinistre_sk", "run_id"}
    ]
    assignments = [
        sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(column), sql.Identifier(column))
        for column in update_columns
    ]

    query = sql.SQL(
        """
        INSERT INTO iris_score.fact_fraud_score ({})
        VALUES ({})
        ON CONFLICT ON CONSTRAINT uq_fact_fraud_score
        DO UPDATE SET {}
        """
    ).format(
        sql.SQL(", ").join(sql.Identifier(column) for column in SCORE_COLUMNS),
        sql.SQL(", ").join(sql.Placeholder(column) for column in SCORE_COLUMNS),
        sql.SQL(", ").join(assignments),
    )

    loaded_count = 0
    for batch in _chunks(rows, BATCH_SIZE):
        cur.executemany(query, batch)
        loaded_count += cur.rowcount if cur.rowcount >= 0 else len(batch)
    return loaded_count


def _load_fraud_score_lookup(cur: Any, run_id: str) -> dict[int, int]:
    cur.execute(
        """
        SELECT sinistre_sk, fraud_score_sk
        FROM iris_score.fact_fraud_score
        WHERE run_id = %s
        """,
        (run_id,),
    )
    return {int(sinistre_sk): int(fraud_score_sk) for sinistre_sk, fraud_score_sk in cur.fetchall()}


def _build_detail_rows(
    detail_source_rows: list[dict[str, Any]],
    fraud_score_lookup: dict[int, int],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    missing_scores = 0

    for source_row in detail_source_rows:
        sinistre_sk = int(source_row["sinistre_sk"])
        fraud_score_sk = fraud_score_lookup.get(sinistre_sk)
        if fraud_score_sk is None:
            missing_scores += 1
            continue

        row = dict(source_row)
        row["fraud_score_sk"] = fraud_score_sk
        rows.append(row)

    if missing_scores:
        raise RuntimeError(
            f"Missing fraud_score_sk for {missing_scores} triggered rule detail rows"
        )

    return rows


def _upsert_detail_rows(cur: Any, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    update_columns = [
        "sinistre_sk",
        "rule_sk",
        "run_id",
        "observed_value",
        "threshold_value",
        "rule_weight",
        "rule_contribution",
    ]
    assignments = [
        sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(column), sql.Identifier(column))
        for column in update_columns
    ]

    query = sql.SQL(
        """
        INSERT INTO iris_score.fact_fraud_rule_detail ({})
        VALUES ({})
        ON CONFLICT ON CONSTRAINT uq_fraud_rule_detail
        DO UPDATE SET {}
        """
    ).format(
        sql.SQL(", ").join(sql.Identifier(column) for column in DETAIL_COLUMNS),
        sql.SQL(", ").join(sql.Placeholder(column) for column in DETAIL_COLUMNS),
        sql.SQL(", ").join(assignments),
    )

    loaded_count = 0
    for batch in _chunks(rows, BATCH_SIZE):
        cur.executemany(query, batch)
        loaded_count += cur.rowcount if cur.rowcount >= 0 else len(batch)
    return loaded_count


def _activate_successful_run(
    cur: Any,
    run_id: str,
    *,
    total_input: int,
    total_scored: int,
) -> None:
    cur.execute(
        """
        UPDATE iris_score.scoring_run
        SET is_active = false
        WHERE run_type = 'FRAUD'
          AND run_id <> %s
          AND is_active IS TRUE
        """,
        (run_id,),
    )
    cur.execute(
        """
        UPDATE iris_score.scoring_run
        SET
            status = 'SUCCESS',
            ended_at = now(),
            is_active = true,
            total_input = %s,
            total_scored = %s
        WHERE run_id = %s
        """,
        (total_input, total_scored, run_id),
    )


def _mark_run_failed(conn: Any, run_id: str, error_message: str) -> None:
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE iris_score.scoring_run
                SET
                    status = 'FAILED',
                    ended_at = now(),
                    notes = %s
                WHERE run_id = %s
                """,
                (_failure_note(error_message), run_id),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def _failure_note(error_message: str) -> str:
    clipped_error = error_message[:900]
    return f"{NOTES} failed: {clipped_error}"


def _get_table_columns(cur: Any, schema_name: str, table_name: str) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        """,
        (schema_name, table_name),
    )
    columns = {row[0] for row in cur.fetchall()}
    if not columns:
        raise RuntimeError(f"{schema_name}.{table_name} does not exist")
    return columns


def _generate_run_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short_uuid = uuid.uuid4().hex[:8]
    return f"FRAUD_{timestamp}_{short_uuid}"


def _decimal_from_value(value: Any, quantizer: str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal(quantizer))


def _text_or_none(value: Any) -> str | None:
    if pd.isna(value):
        return None
    return str(value)


def _chunks(values: list[Any], size: int) -> Iterator[list[Any]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def _validate_required_text(value: str, option_name: str) -> None:
    if value != value.strip():
        raise ValueError(f"{option_name} cannot contain leading or trailing spaces")
    if not value:
        raise ValueError(f"{option_name} cannot be empty")
    if option_name == "--etl-run-id":
        if any(part in value for part in ("/", "\\", "..")):
            raise ValueError("--etl-run-id must be a single run folder name")
        if value.endswith("."):
            raise ValueError("--etl-run-id cannot end with a dot")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run IRISv2 rule-based fraud scoring v1."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id to score from iris_dw.fact_sinistre.",
    )
    parser.add_argument(
        "--run-version",
        default="v1",
        help="Fraud scoring run version. Defaults to v1.",
    )
    parser.add_argument(
        "--rules-version",
        default="v1",
        help="dim_fraud_rule.rule_version to use. Defaults to v1.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
