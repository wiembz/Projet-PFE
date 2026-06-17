from __future__ import annotations

import argparse
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
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
RUN_TYPE = "VHS"
NOTES = "VHS scoring v1"
SOURCE_SYSTEM_VALUE = "FicheVoitureStafim.xlsx"
UNKNOWN_CHECKPOINT_KEY = "UNKNOWN"
BATCH_SIZE = 10_000
VALID_GRADES = {"A", "B", "C", "D"}
BAD_STATUS_CODES = {"CASSE", "NON_FAIT"}
FUNCTIONAL_CATEGORIES = {"SOUS_CAPOT", "SOUS_VEHICULE", "INTERIEUR"}
COSMETIC_CATEGORIES = {"TOUR_DU_VEHICULE"}

REQUIRED_FACT_INSPECTION_COLUMNS = (
    "inspection_sk",
    "vehicule_sk",
    "kilometrage",
)

REQUIRED_CHECKPOINT_FACT_COLUMNS = (
    "inspection_sk",
    "checkpoint_sk",
    "statut_code",
    "statut_libelle",
    "enc_valeur",
)

REQUIRED_DIM_CHECKPOINT_COLUMNS = (
    "checkpoint_sk",
    "checkpoint_natural_key",
    "checkpoint_category",
    "is_active",
    "is_vital",
    "is_important",
    "is_immobilizing",
    "penalty_worn",
    "penalty_broken",
)

SCORE_COLUMNS = (
    "inspection_sk",
    "vehicule_sk",
    "run_id",
    "vhs_score_raw",
    "kilometrage_penalty",
    "vhs_score_final",
    "vhs_score_displayed",
    "safety_score",
    "functional_score",
    "cosmetic_score",
    "safety_grade",
    "vhs_decision",
    "is_drivable",
    "scored_at",
)

DETAIL_COLUMNS = (
    "vhs_score_sk",
    "inspection_sk",
    "checkpoint_sk",
    "vehicule_sk",
    "run_id",
    "observed_value",
    "penalty_applied",
    "penalty_reason",
)


@dataclass(frozen=True)
class ScoreStats:
    run_id: str
    input_inspection_count: int
    scored_count: int
    penalty_detail_count: int
    active_checkpoint_count: int
    grade_a_count: int
    grade_b_count: int
    grade_c_count: int
    grade_d_count: int
    immobiliser_count: int
    surveiller_count: int
    accepter_count: int
    scoring_run_status: str


def main() -> None:
    args = _parse_args()
    stats = run_vhs_scoring(
        etl_run_id=args.etl_run_id,
        run_version=args.run_version,
        rules_version=args.rules_version,
    )
    print(f"run_id={stats.run_id}")
    print(f"input_inspection_count={stats.input_inspection_count}")
    print(f"scored_count={stats.scored_count}")
    print(f"penalty_detail_count={stats.penalty_detail_count}")
    print(f"active_checkpoint_count={stats.active_checkpoint_count}")
    print(f"grade_A_count={stats.grade_a_count}")
    print(f"grade_B_count={stats.grade_b_count}")
    print(f"grade_C_count={stats.grade_c_count}")
    print(f"grade_D_count={stats.grade_d_count}")
    print(f"immobiliser_count={stats.immobiliser_count}")
    print(f"surveiller_count={stats.surveiller_count}")
    print(f"accepter_count={stats.accepter_count}")
    print(f"scoring_run_status={stats.scoring_run_status}")


def run_vhs_scoring(
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
            table_columns = _assert_contracts(cur)
            active_checkpoint_count = _count_active_checkpoints(cur)
            if active_checkpoint_count == 0:
                raise RuntimeError("iris_dw.dim_checkpoint has no active checkpoints beyond UNKNOWN")

            inspection_rows, warnings = _load_scoring_input(
                cur,
                etl_run_id,
                table_columns["fact_inspection"],
                table_columns["fact_inspection_checkpoint"],
            )
            for warning in warnings:
                print(warning, flush=True)

            if inspection_rows.empty:
                raise RuntimeError("No fact_inspection rows selected for VHS scoring")
            if int(inspection_rows["checkpoint_sk"].notna().sum()) == 0:
                raise RuntimeError(
                    "iris_dw.fact_inspection_checkpoint has no active checkpoint rows "
                    "for the selected inspections"
                )

            _insert_scoring_run(cur, run_id, etl_run_id, run_version, rules_version)
            scoring_run_inserted = True
            conn.commit()

            score_rows, detail_source_rows, grade_counts, decision_counts = _score_inspections(
                inspection_rows,
                run_id,
            )
            loaded_score_count = _upsert_score_rows(cur, score_rows)
            vhs_score_lookup = _load_vhs_score_lookup(cur, run_id)
            detail_rows = _build_detail_rows(detail_source_rows, vhs_score_lookup)
            _delete_penalty_details_for_run(cur, run_id)
            penalty_detail_count = _insert_penalty_detail_rows(cur, detail_rows)

            _activate_successful_run(
                cur,
                run_id,
                total_input=len(score_rows),
                total_scored=loaded_score_count,
            )
            conn.commit()

        return ScoreStats(
            run_id=run_id,
            input_inspection_count=len(score_rows),
            scored_count=loaded_score_count,
            penalty_detail_count=penalty_detail_count,
            active_checkpoint_count=active_checkpoint_count,
            grade_a_count=grade_counts["A"],
            grade_b_count=grade_counts["B"],
            grade_c_count=grade_counts["C"],
            grade_d_count=grade_counts["D"],
            immobiliser_count=decision_counts["IMMOBILISER"],
            surveiller_count=decision_counts["SURVEILLER"],
            accepter_count=decision_counts["ACCEPTER"],
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


def _assert_contracts(cur: Any) -> dict[str, set[str]]:
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
    _assert_run_type_allowed(cur)

    score_columns = _get_table_columns(cur, TARGET_SCHEMA, "fact_vhs_score")
    _assert_required_columns(TARGET_SCHEMA, "fact_vhs_score", score_columns, set(SCORE_COLUMNS))
    _assert_constraint_exists(cur, TARGET_SCHEMA, "fact_vhs_score", "uq_fact_vhs_score")

    detail_columns = _get_table_columns(cur, TARGET_SCHEMA, "fact_vhs_penalty_detail")
    _assert_required_columns(
        TARGET_SCHEMA,
        "fact_vhs_penalty_detail",
        detail_columns,
        set(DETAIL_COLUMNS),
    )

    fact_inspection_columns = _get_table_columns(cur, DW_SCHEMA, "fact_inspection")
    _assert_required_columns(
        DW_SCHEMA,
        "fact_inspection",
        fact_inspection_columns,
        set(REQUIRED_FACT_INSPECTION_COLUMNS),
    )

    checkpoint_fact_columns = _get_table_columns(
        cur,
        DW_SCHEMA,
        "fact_inspection_checkpoint",
    )
    _assert_required_columns(
        DW_SCHEMA,
        "fact_inspection_checkpoint",
        checkpoint_fact_columns,
        set(REQUIRED_CHECKPOINT_FACT_COLUMNS),
    )

    dim_checkpoint_columns = _get_table_columns(cur, DW_SCHEMA, "dim_checkpoint")
    _assert_required_columns(
        DW_SCHEMA,
        "dim_checkpoint",
        dim_checkpoint_columns,
        set(REQUIRED_DIM_CHECKPOINT_COLUMNS),
    )

    return {
        "fact_inspection": fact_inspection_columns,
        "fact_inspection_checkpoint": checkpoint_fact_columns,
        "dim_checkpoint": dim_checkpoint_columns,
    }


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


def _assert_constraint_exists(
    cur: Any,
    schema_name: str,
    table_name: str,
    constraint_name: str,
) -> None:
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
        (schema_name, table_name, constraint_name),
    )
    if cur.fetchone() is None:
        raise RuntimeError(f"{schema_name}.{table_name} is missing {constraint_name}")


def _assert_run_type_allowed(cur: Any) -> None:
    cur.execute(
        """
        SELECT pg_get_constraintdef(c.oid)
        FROM pg_constraint c
        JOIN pg_namespace n
          ON n.oid = c.connamespace
        JOIN pg_class t
          ON t.oid = c.conrelid
        WHERE n.nspname = %s
          AND t.relname = 'scoring_run'
          AND c.contype = 'c'
          AND pg_get_constraintdef(c.oid) ILIKE '%%run_type%%'
        """,
        (TARGET_SCHEMA,),
    )
    run_type_checks = [row[0] for row in cur.fetchall()]
    if run_type_checks and not any(RUN_TYPE in check_def for check_def in run_type_checks):
        raise RuntimeError("iris_score.scoring_run check constraints do not allow run_type='VHS'")


def _count_active_checkpoints(cur: Any) -> int:
    cur.execute(
        """
        SELECT COUNT(*)
        FROM iris_dw.dim_checkpoint
        WHERE is_active IS TRUE
          AND checkpoint_natural_key <> %s
        """,
        (UNKNOWN_CHECKPOINT_KEY,),
    )
    return int(cur.fetchone()[0])


def _load_scoring_input(
    cur: Any,
    etl_run_id: str,
    fact_inspection_columns: set[str],
    checkpoint_fact_columns: set[str],
) -> tuple[pd.DataFrame, list[str]]:
    warnings: list[str] = []
    inspection_filters = ["1 = 1"]
    params: dict[str, Any] = {
        "unknown_checkpoint_key": UNKNOWN_CHECKPOINT_KEY,
        "source_system": SOURCE_SYSTEM_VALUE,
    }

    if "etl_run_id" in fact_inspection_columns:
        inspection_filters.append("fi.etl_run_id = %(etl_run_id)s")
        params["etl_run_id"] = etl_run_id
    else:
        warnings.append(
            "WARNING: iris_dw.fact_inspection has no etl_run_id column; "
            "scoring all inspection rows."
        )

    if "source_system" in fact_inspection_columns:
        inspection_filters.append("fi.source_system = %(source_system)s")
    else:
        warnings.append(
            "WARNING: iris_dw.fact_inspection has no source_system column; "
            "not filtering inspections by source system."
        )

    checkpoint_source_filter = ""
    if "source_system" in checkpoint_fact_columns:
        checkpoint_source_filter = "AND fic.source_system = %(source_system)s"
    else:
        warnings.append(
            "WARNING: iris_dw.fact_inspection_checkpoint has no source_system column; "
            "not filtering checkpoints by source system."
        )

    query = f"""
        SELECT
            fi.inspection_sk,
            fi.vehicule_sk,
            fi.kilometrage,
            c.checkpoint_sk,
            c.statut_code,
            c.statut_libelle,
            c.enc_valeur,
            c.checkpoint_category,
            c.is_vital,
            c.is_important,
            c.is_immobilizing,
            c.penalty_worn,
            c.penalty_broken
        FROM iris_dw.fact_inspection fi
        LEFT JOIN (
            SELECT
                fic.inspection_sk,
                fic.checkpoint_sk,
                fic.statut_code,
                fic.statut_libelle,
                fic.enc_valeur,
                dc.checkpoint_category,
                dc.is_vital,
                dc.is_important,
                dc.is_immobilizing,
                dc.penalty_worn,
                dc.penalty_broken
            FROM iris_dw.fact_inspection_checkpoint fic
            JOIN iris_dw.dim_checkpoint dc
              ON dc.checkpoint_sk = fic.checkpoint_sk
            WHERE dc.is_active IS TRUE
              AND dc.checkpoint_natural_key <> %(unknown_checkpoint_key)s
              {checkpoint_source_filter}
        ) c
          ON c.inspection_sk = fi.inspection_sk
        WHERE {" AND ".join(inspection_filters)}
    """
    cur.execute(query, params)

    columns = (
        "inspection_sk",
        "vehicule_sk",
        "kilometrage",
        "checkpoint_sk",
        "statut_code",
        "statut_libelle",
        "enc_valeur",
        "checkpoint_category",
        "is_vital",
        "is_important",
        "is_immobilizing",
        "penalty_worn",
        "penalty_broken",
    )
    return pd.DataFrame(cur.fetchall(), columns=columns), warnings


def _score_inspections(
    rows: pd.DataFrame,
    run_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int], dict[str, int]]:
    frame = rows.copy()
    frame["enc_numeric"] = pd.to_numeric(frame["enc_valeur"], errors="coerce")
    frame["penalty_worn_numeric"] = pd.to_numeric(frame["penalty_worn"], errors="coerce").fillna(0)
    frame["penalty_broken_numeric"] = (
        pd.to_numeric(frame["penalty_broken"], errors="coerce").fillna(0)
    )
    frame["statut_code"] = frame["statut_code"].map(_text_or_none)
    frame["statut_libelle"] = frame["statut_libelle"].map(_text_or_none)
    frame["checkpoint_category"] = frame["checkpoint_category"].map(_text_or_none)
    frame["is_vital"] = frame["is_vital"].fillna(False).astype(bool)
    frame["is_important"] = frame["is_important"].fillna(False).astype(bool)
    frame["is_immobilizing"] = frame["is_immobilizing"].fillna(False).astype(bool)

    inspection_frame = (
        frame[["inspection_sk", "vehicule_sk", "kilometrage"]]
        .drop_duplicates(subset=["inspection_sk"])
        .copy()
    )
    inspection_frame["kilometrage_numeric"] = pd.to_numeric(
        inspection_frame["kilometrage"],
        errors="coerce",
    )
    inspection_frame["kilometrage_penalty"] = inspection_frame["kilometrage_numeric"].map(
        _kilometrage_penalty
    )

    active_checkpoint_rows = frame.loc[frame["checkpoint_sk"].notna()].copy()
    valid_rows = active_checkpoint_rows.loc[active_checkpoint_rows["enc_numeric"].notna()]

    raw_scores = _mean_score(valid_rows)
    safety_scores = _mean_score(
        valid_rows.loc[valid_rows["is_vital"] | valid_rows["is_important"]]
    )
    functional_scores = _mean_score(
        valid_rows.loc[valid_rows["checkpoint_category"].isin(FUNCTIONAL_CATEGORIES)]
    )
    cosmetic_scores = _mean_score(
        valid_rows.loc[valid_rows["checkpoint_category"].isin(COSMETIC_CATEGORIES)]
    )

    penalty_rows = _calculate_checkpoint_penalties(active_checkpoint_rows)
    checkpoint_penalties = (
        penalty_rows.groupby("inspection_sk")["penalty_applied"].sum()
        if not penalty_rows.empty
        else pd.Series(dtype="float64")
    )

    immobilizing_bad = active_checkpoint_rows.loc[
        active_checkpoint_rows["is_immobilizing"]
        & active_checkpoint_rows["statut_code"].isin(BAD_STATUS_CODES)
    ]
    immobilizing_by_inspection = (
        immobilizing_bad.groupby("inspection_sk").size().gt(0)
        if not immobilizing_bad.empty
        else pd.Series(dtype="bool")
    )

    scored_at = datetime.now()
    score_rows: list[dict[str, Any]] = []
    for row in inspection_frame.itertuples(index=False):
        inspection_sk = int(row.inspection_sk)
        vehicule_sk = int(row.vehicule_sk)
        raw_score = _series_value(raw_scores, inspection_sk)
        checkpoint_penalty = _series_value(checkpoint_penalties, inspection_sk, default=0)
        kilometrage_penalty = float(row.kilometrage_penalty)

        if raw_score is None:
            final_score = None
            displayed_score = None
        else:
            final_score = max(0.0, float(raw_score) - float(checkpoint_penalty) - kilometrage_penalty)
            displayed_score = round(final_score, 2)

        safety_grade = _safety_grade(final_score)
        is_drivable = _is_drivable(
            final_score,
            bool(_series_value(immobilizing_by_inspection, inspection_sk, default=False)),
        )
        decision = _vhs_decision(safety_grade, is_drivable)

        score_rows.append(
            {
                "inspection_sk": inspection_sk,
                "vehicule_sk": vehicule_sk,
                "run_id": run_id,
                "vhs_score_raw": _decimal_or_none(raw_score, "0.0000"),
                "kilometrage_penalty": _decimal_or_none(kilometrage_penalty, "0.00"),
                "vhs_score_final": _decimal_or_none(final_score, "0.0000"),
                "vhs_score_displayed": _decimal_or_none(displayed_score, "0.00"),
                "safety_score": _decimal_or_none(
                    _series_value(safety_scores, inspection_sk),
                    "0.0000",
                ),
                "functional_score": _decimal_or_none(
                    _series_value(functional_scores, inspection_sk),
                    "0.0000",
                ),
                "cosmetic_score": _decimal_or_none(
                    _series_value(cosmetic_scores, inspection_sk),
                    "0.0000",
                ),
                "safety_grade": safety_grade,
                "vhs_decision": decision,
                "is_drivable": is_drivable,
                "scored_at": scored_at,
            }
        )

    _validate_grades([row["safety_grade"] for row in score_rows])
    detail_source_rows = _build_penalty_detail_sources(penalty_rows, run_id)
    grade_counts = {
        grade: sum(1 for row in score_rows if row["safety_grade"] == grade)
        for grade in ("A", "B", "C", "D")
    }
    decision_counts = {
        decision: sum(1 for row in score_rows if row["vhs_decision"] == decision)
        for decision in ("IMMOBILISER", "SURVEILLER", "ACCEPTER")
    }

    return score_rows, detail_source_rows, grade_counts, decision_counts


def _mean_score(frame: pd.DataFrame) -> pd.Series:
    if frame.empty:
        return pd.Series(dtype="float64")
    return frame.groupby("inspection_sk")["enc_numeric"].mean() * 100


def _calculate_checkpoint_penalties(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=list(frame.columns) + ["penalty_applied", "penalty_reason"])

    penalty_frame = frame.copy()
    penalty_frame["penalty_applied"] = 0.0
    penalty_frame["penalty_reason"] = None

    worn_mask = penalty_frame["statut_code"].eq("USE")
    broken_mask = penalty_frame["statut_code"].isin(BAD_STATUS_CODES)

    penalty_frame.loc[worn_mask, "penalty_applied"] = penalty_frame.loc[
        worn_mask,
        "penalty_worn_numeric",
    ]
    penalty_frame.loc[worn_mask, "penalty_reason"] = "WORN_OR_ATTENTION"

    penalty_frame.loc[broken_mask, "penalty_applied"] = penalty_frame.loc[
        broken_mask,
        "penalty_broken_numeric",
    ]
    penalty_frame.loc[broken_mask, "penalty_reason"] = "BROKEN_OR_NOT_DONE"

    return penalty_frame.loc[penalty_frame["penalty_applied"].gt(0)].copy()


def _build_penalty_detail_sources(
    penalty_rows: pd.DataFrame,
    run_id: str,
) -> list[dict[str, Any]]:
    if penalty_rows.empty:
        return []

    rows: list[dict[str, Any]] = []
    for row in penalty_rows.itertuples(index=False):
        observed_value = row.statut_libelle if row.statut_libelle else row.statut_code
        rows.append(
            {
                "inspection_sk": int(row.inspection_sk),
                "checkpoint_sk": int(row.checkpoint_sk),
                "vehicule_sk": int(row.vehicule_sk),
                "run_id": run_id,
                "observed_value": observed_value,
                "penalty_applied": _decimal_or_none(row.penalty_applied, "0.00"),
                "penalty_reason": row.penalty_reason,
            }
        )
    return rows


def _kilometrage_penalty(value: Any) -> int:
    if pd.isna(value):
        return 0
    kilometrage = float(value)
    if kilometrage < 100000:
        return 0
    if kilometrage < 200000:
        return 5
    if kilometrage < 300000:
        return 10
    return 15


def _safety_grade(vhs_score_final: float | None) -> str | None:
    if vhs_score_final is None:
        return None
    if vhs_score_final >= 85:
        return "A"
    if vhs_score_final >= 70:
        return "B"
    if vhs_score_final >= 50:
        return "C"
    return "D"


def _is_drivable(vhs_score_final: float | None, has_bad_immobilizing: bool) -> bool | None:
    if has_bad_immobilizing:
        return False
    if vhs_score_final is not None:
        return True
    return None


def _vhs_decision(safety_grade: str | None, is_drivable: bool | None) -> str | None:
    if is_drivable is False:
        return "IMMOBILISER"
    if safety_grade in {"C", "D"}:
        return "SURVEILLER"
    if safety_grade in {"A", "B"}:
        return "ACCEPTER"
    return None


def _validate_grades(grades: list[str | None]) -> None:
    invalid_values = sorted({grade for grade in grades if grade is not None} - VALID_GRADES)
    if invalid_values:
        invalid = ", ".join(invalid_values)
        raise RuntimeError(f"Invalid safety_grade values generated: {invalid}")


def _upsert_score_rows(cur: Any, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    update_columns = [
        column for column in SCORE_COLUMNS if column not in {"inspection_sk", "run_id"}
    ]
    assignments = [
        sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(column), sql.Identifier(column))
        for column in update_columns
    ]

    query = sql.SQL(
        """
        INSERT INTO iris_score.fact_vhs_score ({})
        VALUES ({})
        ON CONFLICT ON CONSTRAINT uq_fact_vhs_score
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


def _load_vhs_score_lookup(cur: Any, run_id: str) -> dict[int, int]:
    cur.execute(
        """
        SELECT inspection_sk, vhs_score_sk
        FROM iris_score.fact_vhs_score
        WHERE run_id = %s
        """,
        (run_id,),
    )
    return {
        int(inspection_sk): int(vhs_score_sk)
        for inspection_sk, vhs_score_sk in cur.fetchall()
    }


def _build_detail_rows(
    detail_source_rows: list[dict[str, Any]],
    vhs_score_lookup: dict[int, int],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    missing_scores = 0

    for source_row in detail_source_rows:
        inspection_sk = int(source_row["inspection_sk"])
        vhs_score_sk = vhs_score_lookup.get(inspection_sk)
        if vhs_score_sk is None:
            missing_scores += 1
            continue

        row = dict(source_row)
        row["vhs_score_sk"] = vhs_score_sk
        rows.append(row)

    if missing_scores:
        raise RuntimeError(
            f"Missing vhs_score_sk for {missing_scores} penalty detail rows"
        )

    return rows


def _delete_penalty_details_for_run(cur: Any, run_id: str) -> None:
    cur.execute(
        """
        DELETE FROM iris_score.fact_vhs_penalty_detail
        WHERE run_id = %s
        """,
        (run_id,),
    )


def _insert_penalty_detail_rows(cur: Any, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    query = sql.SQL(
        """
        INSERT INTO iris_score.fact_vhs_penalty_detail ({})
        VALUES ({})
        """
    ).format(
        sql.SQL(", ").join(sql.Identifier(column) for column in DETAIL_COLUMNS),
        sql.SQL(", ").join(sql.Placeholder(column) for column in DETAIL_COLUMNS),
    )

    loaded_count = 0
    for batch in _chunks(rows, BATCH_SIZE):
        cur.executemany(query, batch)
        loaded_count += cur.rowcount if cur.rowcount >= 0 else len(batch)
    return loaded_count


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
            'VHS',
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
        WHERE run_type = 'VHS'
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
    return f"VHS_{timestamp}_{short_uuid}"


def _decimal_or_none(value: Any, quantizer: str) -> Decimal | None:
    if value is None or pd.isna(value):
        return None
    try:
        return Decimal(str(value)).quantize(Decimal(quantizer))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(f"Cannot convert value to Decimal: {value}") from exc


def _text_or_none(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    return str(value)


def _series_value(series: pd.Series, key: int, default: Any = None) -> Any:
    if series.empty or key not in series.index:
        return default
    value = series.loc[key]
    if pd.isna(value):
        return default
    return value


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
    parser = argparse.ArgumentParser(description="Run IRISv2 VHS scoring v1.")
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id to score from iris_dw.fact_inspection.",
    )
    parser.add_argument(
        "--run-version",
        default="v1",
        help="VHS scoring run version. Defaults to v1.",
    )
    parser.add_argument(
        "--rules-version",
        default="v1",
        help="Rules/config version recorded on the scoring run. Defaults to v1.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
