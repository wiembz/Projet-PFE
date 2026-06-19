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


REPORT_PATH = PROJECT_ROOT / "docs" / "dim_contrat_quality_validation.md"
DECISION_STATUS = "VALIDATED_WITH_SOURCE_LIMITS"


@dataclass(frozen=True)
class QualityCheck:
    check_name: str
    schema_name: str
    table_name: str
    expected_value: str
    observed_value: str
    status: str
    section: str


DATA_QUALITY_CHECK_NAMES = (
    "dim_contrat_row_count_positive",
    "dim_contrat_unknown_row_count",
    "dim_contrat_natural_key_null_count",
    "dim_contrat_natural_key_duplicate_count",
    "dim_contrat_num_contrat_null_count",
    "dim_contrat_num_avenant_null_count",
    "dim_contrat_num_mise_a_jour_null_count",
    "dim_contrat_produit_unknown_count",
    "dim_contrat_delegation_unknown_count",
    "dim_contrat_intermediaire_unknown_count",
    "dim_contrat_date_debut_contrat_null_count",
    "dim_contrat_date_fin_contrat_null_count",
    "dim_contrat_date_debut_effet_null_count",
    "dim_contrat_date_fin_effet_null_count",
    "dim_contrat_fin_before_debut_contrat_count",
    "dim_contrat_fin_effet_before_debut_effet_count",
    "dim_contrat_situation_contrat_null_count",
    "dim_contrat_type_resiliation_null_count",
    "dim_contrat_libelle_resiliation_null_count",
)


def main() -> None:
    args = _parse_args()
    report_path = _resolve_project_path(args.report_path)
    checks = validate_dim_contrat_quality()
    validation_status = _validation_status(checks)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_markdown(checks, validation_status), encoding="utf-8")
    _write_data_quality_checks(args.etl_run_id, checks)

    print(f"total_checks={len(checks)}")
    print(f"pass_count={_status_count(checks, 'PASS')}")
    print(f"warning_count={_status_count(checks, 'WARNING')}")
    print(f"fail_count={_status_count(checks, 'FAIL')}")
    print(f"validation_status={validation_status}")


def validate_dim_contrat_quality() -> list[QualityCheck]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            metrics = _dim_contrat_metrics(cur)
    finally:
        conn.close()

    return _build_checks(metrics)


def _dim_contrat_metrics(cur: Any) -> dict[str, int]:
    return {
        "row_count": _single_count(cur, "SELECT COUNT(*) FROM iris_dw.dim_contrat"),
        "unknown_row_count": _single_count(
            cur,
            """
            SELECT COUNT(*)
            FROM iris_dw.dim_contrat
            WHERE contrat_sk = 0
            """,
        ),
        "natural_key_null_count": _blank_count(cur, "contrat_natural_key", include_unknown=True),
        "natural_key_duplicate_count": _duplicate_count(cur, "contrat_natural_key"),
        "num_contrat_null_count": _blank_count(cur, "num_contrat"),
        "num_avenant_null_count": _blank_count(cur, "num_avenant"),
        "num_mise_a_jour_null_count": _blank_count(cur, "num_mise_a_jour"),
        "produit_unknown_count": _zero_sk_count(cur, "produit_sk"),
        "delegation_unknown_count": _zero_sk_count(cur, "delegation_sk"),
        "intermediaire_unknown_count": _zero_sk_count(cur, "intermediaire_sk"),
        "date_debut_contrat_null_count": _blank_count(cur, "date_debut_contrat"),
        "date_fin_contrat_null_count": _blank_count(cur, "date_fin_contrat"),
        "date_debut_effet_null_count": _blank_count(cur, "date_debut_effet"),
        "date_fin_effet_null_count": _blank_count(cur, "date_fin_effet"),
        "fin_before_debut_contrat_count": _date_order_count(
            cur,
            "date_debut_contrat",
            "date_fin_contrat",
        ),
        "fin_effet_before_debut_effet_count": _date_order_count(
            cur,
            "date_debut_effet",
            "date_fin_effet",
        ),
        "situation_contrat_null_count": _blank_count(cur, "situation_contrat"),
        "type_resiliation_null_count": _blank_count(cur, "type_resiliation"),
        "libelle_resiliation_null_count": _blank_count(cur, "libelle_resiliation"),
    }


def _single_count(cur: Any, query: str) -> int:
    cur.execute(query)
    return int(cur.fetchone()[0] or 0)


def _blank_count(cur: Any, column_name: str, *, include_unknown: bool = False) -> int:
    unknown_filter = "" if include_unknown else "WHERE contrat_sk <> 0"
    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM iris_dw.dim_contrat
        {unknown_filter}
          {"AND" if unknown_filter else "WHERE"} (
              {column_name} IS NULL
              OR btrim({column_name}::text) = ''
          )
        """
    )
    return int(cur.fetchone()[0] or 0)


def _duplicate_count(cur: Any, column_name: str) -> int:
    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM (
            SELECT {column_name}
            FROM iris_dw.dim_contrat
            WHERE contrat_sk <> 0
            GROUP BY {column_name}
            HAVING COUNT(*) > 1
        ) duplicated_values
        """
    )
    return int(cur.fetchone()[0] or 0)


def _zero_sk_count(cur: Any, column_name: str) -> int:
    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM iris_dw.dim_contrat
        WHERE {column_name} = 0
        """
    )
    return int(cur.fetchone()[0] or 0)


def _date_order_count(cur: Any, start_column: str, end_column: str) -> int:
    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM iris_dw.dim_contrat
        WHERE contrat_sk <> 0
          AND {start_column} IS NOT NULL
          AND {end_column} IS NOT NULL
          AND {end_column} < {start_column}
        """
    )
    return int(cur.fetchone()[0] or 0)


def _build_checks(metrics: dict[str, int]) -> list[QualityCheck]:
    return [
        _check("dim_contrat_row_count_positive", ">0", metrics["row_count"], "FAIL", metrics["row_count"] > 0),
        _check("dim_contrat_unknown_row_count", "1", metrics["unknown_row_count"], "FAIL", metrics["unknown_row_count"] == 1),
        _zero_check("dim_contrat_natural_key_null_count", metrics["natural_key_null_count"], "FAIL"),
        _zero_check("dim_contrat_natural_key_duplicate_count", metrics["natural_key_duplicate_count"], "FAIL"),
        _zero_check("dim_contrat_num_contrat_null_count", metrics["num_contrat_null_count"], "FAIL"),
        _zero_check("dim_contrat_num_avenant_null_count", metrics["num_avenant_null_count"], "WARNING"),
        _zero_check(
            "dim_contrat_num_mise_a_jour_null_count",
            metrics["num_mise_a_jour_null_count"],
            "WARNING",
        ),
        _check(
            "dim_contrat_produit_unknown_count",
            "<=1",
            metrics["produit_unknown_count"],
            "WARNING",
            metrics["produit_unknown_count"] <= 1,
        ),
        _check(
            "dim_contrat_delegation_unknown_count",
            "<=1",
            metrics["delegation_unknown_count"],
            "WARNING",
            metrics["delegation_unknown_count"] <= 1,
        ),
        _check(
            "dim_contrat_intermediaire_unknown_count",
            "<=1",
            metrics["intermediaire_unknown_count"],
            "WARNING",
            metrics["intermediaire_unknown_count"] <= 1,
        ),
        _zero_check(
            "dim_contrat_date_debut_contrat_null_count",
            metrics["date_debut_contrat_null_count"],
            "WARNING",
        ),
        _zero_check(
            "dim_contrat_date_fin_contrat_null_count",
            metrics["date_fin_contrat_null_count"],
            "WARNING",
        ),
        _zero_check(
            "dim_contrat_date_debut_effet_null_count",
            metrics["date_debut_effet_null_count"],
            "WARNING",
        ),
        _zero_check(
            "dim_contrat_date_fin_effet_null_count",
            metrics["date_fin_effet_null_count"],
            "WARNING",
        ),
        _zero_check(
            "dim_contrat_fin_before_debut_contrat_count",
            metrics["fin_before_debut_contrat_count"],
            "WARNING",
        ),
        _zero_check(
            "dim_contrat_fin_effet_before_debut_effet_count",
            metrics["fin_effet_before_debut_effet_count"],
            "WARNING",
        ),
        _zero_check(
            "dim_contrat_situation_contrat_null_count",
            metrics["situation_contrat_null_count"],
            "WARNING",
        ),
        _zero_check(
            "dim_contrat_type_resiliation_null_count",
            metrics["type_resiliation_null_count"],
            "WARNING",
        ),
        _zero_check(
            "dim_contrat_libelle_resiliation_null_count",
            metrics["libelle_resiliation_null_count"],
            "WARNING",
        ),
    ]


def _zero_check(check_name: str, observed_value: int, non_zero_status: str) -> QualityCheck:
    return _check(check_name, "0", observed_value, non_zero_status, observed_value == 0)


def _check(
    check_name: str,
    expected_value: str,
    observed_value: int,
    failed_status: str,
    condition: bool,
) -> QualityCheck:
    return QualityCheck(
        check_name=check_name,
        schema_name="iris_dw",
        table_name="dim_contrat",
        expected_value=expected_value,
        observed_value=str(observed_value),
        status="PASS" if condition else failed_status,
        section=_section_for_check(check_name),
    )


def _section_for_check(check_name: str) -> str:
    if "natural_key" in check_name or "row_count" in check_name:
        return "Structural Checks"
    if check_name.endswith("_unknown_count"):
        return "Relationship Checks"
    if "date" in check_name or "fin_before" in check_name:
        return "Date Semantics"
    return "Attribute Completeness"


def _write_data_quality_checks(
    etl_run_id: str | None,
    checks: list[QualityCheck],
) -> None:
    rows = [_check_to_row(etl_run_id, check) for check in checks]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            placeholders = ", ".join("%s" for _ in DATA_QUALITY_CHECK_NAMES)
            if etl_run_id is None:
                cur.execute(
                    f"""
                    DELETE FROM iris_admin.data_quality_check
                    WHERE etl_run_id IS NULL
                      AND check_name IN ({placeholders})
                    """,
                    DATA_QUALITY_CHECK_NAMES,
                )
            else:
                cur.execute(
                    f"""
                    DELETE FROM iris_admin.data_quality_check
                    WHERE etl_run_id = %s
                      AND check_name IN ({placeholders})
                    """,
                    (etl_run_id, *DATA_QUALITY_CHECK_NAMES),
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
        "# IRISv2 dim_contrat Quality Validation",
        "",
        f"Generated at: {generated_at}",
        "",
        "This validation reads `iris_dw.dim_contrat`, writes audit checks to `iris_admin.data_quality_check`, and does not modify DW tables.",
        "",
        "## Decision",
        "",
        f"- dim_contrat.status: `{DECISION_STATUS}`",
        "- `contrat_natural_key` is the reliable DW contract key.",
        "- `delegation_sk = 0` is mostly explained by missing source `IDDELEGA`.",
        "- Date anomalies are treated as source/business semantics warnings.",
        "- No automatic date inversion or correction should be applied in ETL.",
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
        "Structural Checks",
        "Relationship Checks",
        "Date Semantics",
        "Attribute Completeness",
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
        description="Validate iris_dw.dim_contrat quality without modifying DW data."
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
