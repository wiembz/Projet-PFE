from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


REPORT_PATH = PROJECT_ROOT / "docs" / "dw_integrity_validation.md"


@dataclass(frozen=True)
class QualityCheck:
    check_name: str
    schema_name: str
    table_name: str
    expected_value: str
    observed_value: str
    status: str
    section: str


FK_CHECKS = (
    ("dw_fact_prime_client_sk_orphan_count", "fact_prime", "client_sk", "dim_client", "client_sk"),
    ("dw_fact_prime_contrat_sk_orphan_count", "fact_prime", "contrat_sk", "dim_contrat", "contrat_sk"),
    ("dw_fact_prime_vehicule_sk_orphan_count", "fact_prime", "vehicule_sk", "dim_vehicule", "vehicule_sk"),
    ("dw_fact_prime_produit_sk_orphan_count", "fact_prime", "produit_sk", "dim_produit", "produit_sk"),
    ("dw_fact_prime_intermediaire_sk_orphan_count", "fact_prime", "intermediaire_sk", "dim_intermediaire", "intermediaire_sk"),
    ("dw_fact_prime_delegation_sk_orphan_count", "fact_prime", "delegation_sk", "dim_delegation", "delegation_sk"),
    ("dw_fact_sinistre_client_sk_orphan_count", "fact_sinistre", "client_sk", "dim_client", "client_sk"),
    ("dw_fact_sinistre_contrat_sk_orphan_count", "fact_sinistre", "contrat_sk", "dim_contrat", "contrat_sk"),
    ("dw_fact_sinistre_vehicule_sk_orphan_count", "fact_sinistre", "vehicule_sk", "dim_vehicule", "vehicule_sk"),
    ("dw_fact_sinistre_produit_sk_orphan_count", "fact_sinistre", "produit_sk", "dim_produit", "produit_sk"),
    ("dw_fact_sinistre_garantie_sk_orphan_count", "fact_sinistre", "garantie_sk", "dim_garantie", "garantie_sk"),
    ("dw_fact_sinistre_intermediaire_sk_orphan_count", "fact_sinistre", "intermediaire_sk", "dim_intermediaire", "intermediaire_sk"),
    ("dw_fact_sinistre_delegation_sk_orphan_count", "fact_sinistre", "delegation_sk", "dim_delegation", "delegation_sk"),
    ("dw_fact_sinistre_cause_sinistre_sk_orphan_count", "fact_sinistre", "cause_sinistre_sk", "dim_cause_sinistre", "cause_sinistre_sk"),
    ("dw_fact_inspection_vehicule_sk_orphan_count", "fact_inspection", "vehicule_sk", "dim_vehicule", "vehicule_sk"),
    ("dw_fact_inspection_checkpoint_inspection_sk_orphan_count", "fact_inspection_checkpoint", "inspection_sk", "fact_inspection", "inspection_sk"),
    ("dw_fact_inspection_checkpoint_checkpoint_sk_orphan_count", "fact_inspection_checkpoint", "checkpoint_sk", "dim_checkpoint", "checkpoint_sk"),
)

DIMENSION_NULL_CHECKS = (
    ("dw_dim_vehicule_marque_null_count", "dim_vehicule", "vehicule_sk", "marque", "WARNING", "WARNING"),
    ("dw_dim_vehicule_modele_null_count", "dim_vehicule", "vehicule_sk", "modele", "WARNING", "WARNING"),
    ("dw_dim_vehicule_genre_vehicule_null_count", "dim_vehicule", "vehicule_sk", "genre_vehicule", "WARNING", "WARNING"),
    ("dw_dim_vehicule_usage_vehicule_null_count", "dim_vehicule", "vehicule_sk", "usage_vehicule", "WARNING", "WARNING"),
    ("dw_dim_vehicule_energie_null_count", "dim_vehicule", "vehicule_sk", "energie", "WARNING", "WARNING"),
    ("dw_dim_vehicule_puissance_null_count", "dim_vehicule", "vehicule_sk", "puissance", "WARNING", "WARNING"),
    ("dw_dim_vehicule_date_mise_circulation_null_count", "dim_vehicule", "vehicule_sk", "date_mise_circulation", "WARNING", "WARNING"),
    ("dw_dim_garantie_libelle_garantie_null_count", "dim_garantie", "garantie_sk", "libelle_garantie", "FAIL", "WARNING"),
    ("dw_dim_garantie_famille_garantie_null_count", "dim_garantie", "garantie_sk", "famille_garantie", "WARNING", "WARNING"),
    ("dw_dim_delegation_libelle_delegation_null_count", "dim_delegation", "delegation_sk", "libelle_delegation", "WARNING", "WARNING"),
    ("dw_dim_intermediaire_nom_intermediaire_null_count", "dim_intermediaire", "intermediaire_sk", "nom_intermediaire", "WARNING", "WARNING"),
    ("dw_dim_intermediaire_type_intermediaire_null_count", "dim_intermediaire", "intermediaire_sk", "type_intermediaire", "FAIL", "WARNING"),
    ("dw_dim_cause_sinistre_libelle_cause_sinistre_null_count", "dim_cause_sinistre", "cause_sinistre_sk", "libelle_cause_sinistre", "FAIL", "WARNING"),
    ("dw_dim_cause_sinistre_libelle_nature_sinistre_null_count", "dim_cause_sinistre", "cause_sinistre_sk", "libelle_nature_sinistre", "WARNING", "WARNING"),
    ("dw_dim_cause_sinistre_libelle_sous_nature_sinistre_null_count", "dim_cause_sinistre", "cause_sinistre_sk", "libelle_sous_nature_sinistre", "FAIL", "WARNING"),
)

OPTIONAL_DIMENSION_NULL_CHECKS = (
    ("dw_dim_vehicule_immatriculation_null_count", "dim_vehicule", "vehicule_sk", "immatriculation", "FAIL", "FAIL"),
    ("dw_dim_vehicule_vin_null_count", "dim_vehicule", "vehicule_sk", "vin", "WARNING", "WARNING"),
    ("dw_dim_vehicule_motorisation_null_count", "dim_vehicule", "vehicule_sk", "motorisation", "WARNING", "WARNING"),
    ("dw_dim_vehicule_kilometrage_null_count", "dim_vehicule", "vehicule_sk", "kilometrage", "WARNING", "WARNING"),
    ("dw_dim_vehicule_numero_risque_null_count", "dim_vehicule", "vehicule_sk", "numero_risque", "WARNING", "WARNING"),
    ("dw_dim_vehicule_source_system_null_count", "dim_vehicule", "vehicule_sk", "source_system", "FAIL", "FAIL"),
)

KIMBALL_COLUMN_CHECKS = (
    ("dw_fact_inspection_agent_name_column_presence", "fact_inspection", "agent_name"),
    ("dw_fact_inspection_nom_prenom_client_column_presence", "fact_inspection", "nom_prenom_client"),
    ("dw_fact_inspection_telephone_column_presence", "fact_inspection", "telephone"),
    ("dw_fact_inspection_immatriculation_source_column_presence", "fact_inspection", "immatriculation_source"),
    ("dw_fact_inspection_vin_source_column_presence", "fact_inspection", "vin_source"),
    ("dw_fact_inspection_motorisation_column_presence", "fact_inspection", "motorisation"),
    ("dw_fact_sinistre_code_etat_sinistre_column_presence", "fact_sinistre", "code_etat_sinistre"),
    ("dw_fact_sinistre_etat_garantie_column_presence", "fact_sinistre", "etat_garantie"),
    ("dw_fact_sinistre_motif_cloture_column_presence", "fact_sinistre", "motif_cloture"),
    ("dw_fact_inspection_checkpoint_statut_code_column_presence", "fact_inspection_checkpoint", "statut_code"),
    ("dw_fact_inspection_checkpoint_statut_libelle_column_presence", "fact_inspection_checkpoint", "statut_libelle"),
    ("dw_fact_inspection_checkpoint_source_column_name_column_presence", "fact_inspection_checkpoint", "source_column_name"),
)


def main() -> None:
    args = _parse_args()
    report_path = _resolve_project_path(args.report_path)
    checks = validate_dw_integrity()
    validation_status = _validation_status(checks)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_markdown(checks, validation_status), encoding="utf-8")
    _write_data_quality_checks(args.etl_run_id, checks)

    pass_count = _status_count(checks, "PASS")
    warning_count = _status_count(checks, "WARNING")
    fail_count = _status_count(checks, "FAIL")
    print(f"total_checks={len(checks)}")
    print(f"pass_count={pass_count}")
    print(f"warning_count={warning_count}")
    print(f"fail_count={fail_count}")
    print(f"validation_status={validation_status}")


def validate_dw_integrity() -> list[QualityCheck]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            checks: list[QualityCheck] = []
            checks.extend(_fk_checks(cur))
            checks.extend(_dimension_null_checks(cur))
            checks.extend(_fact_anomaly_checks(cur))
            checks.extend(_kimball_column_checks(cur))
            return checks
    finally:
        conn.close()


def _fk_checks(cur: Any) -> list[QualityCheck]:
    checks: list[QualityCheck] = []
    for check_name, fact_table, fact_column, target_table, target_column in FK_CHECKS:
        orphan_count = _fk_orphan_count(
            cur,
            fact_table=fact_table,
            fact_column=fact_column,
            target_table=target_table,
            target_column=target_column,
        )
        checks.append(
            QualityCheck(
                check_name=check_name,
                schema_name="iris_dw",
                table_name=fact_table,
                expected_value="0",
                observed_value=str(orphan_count),
                status="PASS" if orphan_count == 0 else "FAIL",
                section="Foreign Key Integrity",
            )
        )
    return checks


def _fk_orphan_count(
    cur: Any,
    *,
    fact_table: str,
    fact_column: str,
    target_table: str,
    target_column: str,
) -> int:
    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM iris_dw.{fact_table} f
        LEFT JOIN iris_dw.{target_table} d
          ON f.{fact_column} = d.{target_column}
        WHERE f.{fact_column} IS NOT NULL
          AND d.{target_column} IS NULL
        """
    )
    return int(cur.fetchone()[0])


def _dimension_null_checks(cur: Any) -> list[QualityCheck]:
    checks: list[QualityCheck] = []
    check_definitions = (*DIMENSION_NULL_CHECKS, *OPTIONAL_DIMENSION_NULL_CHECKS)
    table_columns: dict[str, set[str]] = {}
    for (
        check_name,
        table_name,
        sk_column,
        checked_column,
        all_null_status,
        partial_null_status,
    ) in check_definitions:
        if table_name not in table_columns:
            table_columns[table_name] = _table_columns(cur, "iris_dw", table_name)
        if checked_column not in table_columns[table_name]:
            continue
        row_count, null_count = _dimension_null_count(
            cur,
            table_name=table_name,
            sk_column=sk_column,
            checked_column=checked_column,
        )
        checks.append(
            QualityCheck(
                check_name=check_name,
                schema_name="iris_dw",
                table_name=table_name,
                expected_value="0",
                observed_value=str(null_count),
                status=_dimension_null_status(
                    row_count,
                    null_count,
                    all_null_status=all_null_status,
                    partial_null_status=partial_null_status,
                ),
                section="Dimension Completeness",
            )
        )
    return checks


def _dimension_null_count(
    cur: Any,
    *,
    table_name: str,
    sk_column: str,
    checked_column: str,
) -> tuple[int, int]:
    cur.execute(
        f"""
        SELECT
            COUNT(*) AS row_count,
            COUNT(*) FILTER (
                WHERE {checked_column} IS NULL
                   OR btrim({checked_column}::text) = ''
            ) AS null_count
        FROM iris_dw.{table_name}
        WHERE {sk_column} <> 0
        """
    )
    row_count, null_count = cur.fetchone()
    return int(row_count or 0), int(null_count or 0)


def _dimension_null_status(
    row_count: int,
    null_count: int,
    *,
    all_null_status: str,
    partial_null_status: str,
) -> str:
    if null_count == 0:
        return "PASS"
    if row_count > 0 and null_count == row_count:
        return all_null_status
    return partial_null_status


def _fact_anomaly_checks(cur: Any) -> list[QualityCheck]:
    return [
        _fact_count_check(
            cur,
            "dw_fact_prime_total_prime_null_count",
            "fact_prime",
            "total_prime IS NULL",
            "WARNING",
        ),
        _fact_count_check(
            cur,
            "dw_fact_prime_total_prime_negative_count",
            "fact_prime",
            "total_prime < 0",
            "WARNING",
        ),
        _date_order_check(
            cur,
            "dw_fact_prime_date_fin_contrat_before_debut_count",
            "fact_prime",
            "date_debut_contrat_sk",
            "date_fin_contrat_sk",
            "FAIL",
        ),
        _date_order_check(
            cur,
            "dw_fact_prime_date_fin_effet_before_debut_count",
            "fact_prime",
            "date_debut_effet_sk",
            "date_fin_effet_sk",
            "FAIL",
        ),
        _fact_count_check(
            cur,
            "dw_fact_sinistre_montant_total_negative_count",
            "fact_sinistre",
            "montant_total < 0",
            "WARNING",
        ),
        _fact_count_check(
            cur,
            "dw_fact_sinistre_montant_total_net_negative_count",
            "fact_sinistre",
            "montant_total_net < 0",
            "WARNING",
        ),
        _fact_count_check(
            cur,
            "dw_fact_sinistre_delai_declaration_negative_count",
            "fact_sinistre",
            "delai_declaration_jours < 0",
            "WARNING",
        ),
        _fact_count_check(
            cur,
            "dw_fact_sinistre_delai_ouverture_negative_count",
            "fact_sinistre",
            "delai_ouverture_jours < 0",
            "WARNING",
        ),
        _fact_count_check(
            cur,
            "dw_fact_sinistre_anciennete_contrat_negative_count",
            "fact_sinistre",
            "anciennete_contrat_jours < 0",
            "WARNING",
        ),
        _date_order_check(
            cur,
            "dw_fact_sinistre_date_declaration_before_survenance_count",
            "fact_sinistre",
            "date_survenance_sk",
            "date_declaration_sk",
            "WARNING",
        ),
        _date_order_check(
            cur,
            "dw_fact_sinistre_date_ouverture_before_declaration_count",
            "fact_sinistre",
            "date_declaration_sk",
            "date_ouverture_sk",
            "WARNING",
        ),
        _date_order_check(
            cur,
            "dw_fact_sinistre_sinistre_before_effet_count",
            "fact_sinistre",
            "date_debut_effet_sk",
            "date_survenance_sk",
            "WARNING",
        ),
    ]


def _fact_count_check(
    cur: Any,
    check_name: str,
    table_name: str,
    predicate: str,
    non_zero_status: str,
) -> QualityCheck:
    cur.execute(f"SELECT COUNT(*) FROM iris_dw.{table_name} WHERE {predicate}")
    observed_count = int(cur.fetchone()[0])
    return QualityCheck(
        check_name=check_name,
        schema_name="iris_dw",
        table_name=table_name,
        expected_value="0",
        observed_value=str(observed_count),
        status="PASS" if observed_count == 0 else non_zero_status,
        section="Fact Anomalies",
    )


def _date_order_check(
    cur: Any,
    check_name: str,
    table_name: str,
    start_date_sk_column: str,
    end_date_sk_column: str,
    non_zero_status: str,
) -> QualityCheck:
    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM iris_dw.{table_name} f
        JOIN iris_dw.dim_date start_date
          ON f.{start_date_sk_column} = start_date.date_sk
        JOIN iris_dw.dim_date end_date
          ON f.{end_date_sk_column} = end_date.date_sk
        WHERE start_date.date_val IS NOT NULL
          AND end_date.date_val IS NOT NULL
          AND end_date.date_val < start_date.date_val
        """
    )
    observed_count = int(cur.fetchone()[0])
    return QualityCheck(
        check_name=check_name,
        schema_name="iris_dw",
        table_name=table_name,
        expected_value="0",
        observed_value=str(observed_count),
        status="PASS" if observed_count == 0 else non_zero_status,
        section="Fact Anomalies",
    )


def _kimball_column_checks(cur: Any) -> list[QualityCheck]:
    checks: list[QualityCheck] = []
    table_columns: dict[str, set[str]] = {}
    for check_name, table_name, column_name in KIMBALL_COLUMN_CHECKS:
        if table_name not in table_columns:
            table_columns[table_name] = _table_columns(cur, "iris_dw", table_name)
        is_present = column_name in table_columns[table_name]
        checks.append(
            QualityCheck(
                check_name=check_name,
                schema_name="iris_dw",
                table_name=table_name,
                expected_value="absent",
                observed_value="present" if is_present else "absent",
                status="WARNING" if is_present else "PASS",
                section="Kimball Structure",
            )
        )
    return checks


def _table_columns(cur: Any, schema_name: str, table_name: str) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        """,
        (schema_name, table_name),
    )
    return {row[0] for row in cur.fetchall()}


def _write_data_quality_checks(
    etl_run_id: str | None,
    checks: list[QualityCheck],
) -> None:
    rows = [_check_to_row(etl_run_id, check) for check in checks]
    check_names = tuple(check.check_name for check in checks)
    cleanup_check_names = tuple(
        dict.fromkeys(
            list(check_names)
            + [
                check_name.removeprefix("dw_")
                for check_name in check_names
                if check_name.startswith("dw_")
            ]
        )
    )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            placeholders = ", ".join("%s" for _ in cleanup_check_names)
            if etl_run_id is None:
                cur.execute(
                    f"""
                    DELETE FROM iris_admin.data_quality_check
                    WHERE etl_run_id IS NULL
                      AND check_name IN ({placeholders})
                    """,
                    cleanup_check_names,
                )
            else:
                cur.execute(
                    f"""
                    DELETE FROM iris_admin.data_quality_check
                    WHERE etl_run_id = %s
                      AND check_name IN ({placeholders})
                    """,
                    (etl_run_id, *cleanup_check_names),
                )
            cur.executemany(
                """
                INSERT INTO iris_admin.data_quality_check (
                    etl_run_id,
                    check_name,
                    schema_name,
                    table_name,
                    expected_value,
                    observed_value,
                    status,
                    checked_at
                )
                VALUES (
                    %(etl_run_id)s,
                    %(check_name)s,
                    %(schema_name)s,
                    %(table_name)s,
                    %(expected_value)s,
                    %(observed_value)s,
                    %(status)s,
                    now()
                )
                """,
                rows,
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _check_to_row(
    etl_run_id: str | None,
    check: QualityCheck,
) -> dict[str, str | None]:
    return {
        "etl_run_id": etl_run_id,
        "check_name": check.check_name,
        "schema_name": check.schema_name,
        "table_name": check.table_name,
        "expected_value": check.expected_value,
        "observed_value": check.observed_value,
        "status": check.status,
    }


def _build_markdown(checks: list[QualityCheck], validation_status: str) -> str:
    generated_at = datetime.now().isoformat(timespec="seconds")
    lines = [
        "# IRISv2 DW Integrity Validation",
        "",
        f"Generated at: {generated_at}",
        "",
        "This validation reads `iris_dw`, writes audit checks to `iris_admin.data_quality_check`, and does not modify DW tables.",
        "",
        "## Summary",
        "",
        f"- total_checks: `{len(checks)}`",
        f"- pass_count: `{_status_count(checks, 'PASS')}`",
        f"- warning_count: `{_status_count(checks, 'WARNING')}`",
        f"- fail_count: `{_status_count(checks, 'FAIL')}`",
        f"- validation_status: `{validation_status}`",
        "",
    ]

    for section in (
        "Foreign Key Integrity",
        "Dimension Completeness",
        "Fact Anomalies",
        "Kimball Structure",
    ):
        section_rows = [check for check in checks if check.section == section]
        lines.extend([f"## {section}", ""])
        lines.extend(_checks_to_markdown(section_rows))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _checks_to_markdown(checks: list[QualityCheck]) -> list[str]:
    if not checks:
        return ["No checks."]
    columns = [
        "check_name",
        "schema_name",
        "table_name",
        "expected_value",
        "observed_value",
        "status",
    ]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for check in checks:
        lines.append(
            "| "
            + " | ".join(
                [
                    check.check_name,
                    check.schema_name,
                    check.table_name,
                    check.expected_value,
                    check.observed_value,
                    check.status,
                ]
            )
            + " |"
        )
    return lines


def _validation_status(checks: list[QualityCheck]) -> str:
    if any(check.status == "FAIL" for check in checks):
        return "FAIL"
    if any(check.status == "WARNING" for check in checks):
        return "WARNING"
    return "PASS"


def _status_count(checks: list[QualityCheck], status: str) -> int:
    return sum(1 for check in checks if check.status == status)


def _resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate iris_dw referential integrity and DW quality."
    )
    parser.add_argument(
        "--etl-run-id",
        default=None,
        help="Optional ETL run id used when persisting data quality checks.",
    )
    parser.add_argument(
        "--report-path",
        default=str(REPORT_PATH),
        help="Markdown report path.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
