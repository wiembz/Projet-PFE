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


REPORT_PATH = PROJECT_ROOT / "docs" / "dim_client_quality_validation.md"
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
    "dim_client_row_count_positive",
    "dim_client_unknown_row_count",
    "dim_client_natural_key_null_count",
    "dim_client_natural_key_duplicate_count",
    "dim_client_num_client_null_count",
    "dim_client_code_nature_client_null_count",
    "dim_client_identifiant_client_null_count",
    "dim_client_identifiant_client_duplicate_value_count",
    "dim_client_identifiant_client_max_duplicate_group_size",
    "dim_client_sexe_null_count",
    "dim_client_situation_familiale_null_count",
    "dim_client_date_naissance_null_count",
    "dim_client_gouvernorat_client_null_count",
    "dim_client_gouvernorat_client_distinct_count",
)


def main() -> None:
    args = _parse_args()
    report_path = _resolve_project_path(args.report_path)
    checks = validate_dim_client_quality()
    validation_status = _validation_status(checks)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_markdown(checks, validation_status), encoding="utf-8")
    _write_data_quality_checks(args.etl_run_id, checks)

    print(f"total_checks={len(checks)}")
    print(f"pass_count={_status_count(checks, 'PASS')}")
    print(f"warning_count={_status_count(checks, 'WARNING')}")
    print(f"fail_count={_status_count(checks, 'FAIL')}")
    print(f"validation_status={validation_status}")


def validate_dim_client_quality() -> list[QualityCheck]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            metrics = _dim_client_metrics(cur)
    finally:
        conn.close()

    return _build_checks(metrics)


def _dim_client_metrics(cur: Any) -> dict[str, int]:
    return {
        "row_count": _single_count(cur, "SELECT COUNT(*) FROM iris_dw.dim_client"),
        "unknown_row_count": _single_count(
            cur,
            """
            SELECT COUNT(*)
            FROM iris_dw.dim_client
            WHERE client_sk = 0
            """,
        ),
        "natural_key_null_count": _blank_count(cur, "client_natural_key", include_unknown=True),
        "natural_key_duplicate_count": _duplicate_count(cur, "client_natural_key"),
        "num_client_null_count": _blank_count(cur, "num_client"),
        "code_nature_client_null_count": _blank_count(cur, "code_nature_client"),
        "identifiant_client_null_count": _blank_count(cur, "identifiant_client"),
        "identifiant_client_duplicate_value_count": _duplicate_count(
            cur,
            "identifiant_client",
            exclude_blank=True,
        ),
        "identifiant_client_max_duplicate_group_size": _max_duplicate_group_size(
            cur,
            "identifiant_client",
        ),
        "sexe_null_count": _blank_count(cur, "sexe"),
        "situation_familiale_null_count": _blank_count(cur, "situation_familiale"),
        "date_naissance_null_count": _blank_count(cur, "date_naissance"),
        "gouvernorat_client_null_count": _blank_count(cur, "gouvernorat_client"),
        "gouvernorat_client_distinct_count": _distinct_count(cur, "gouvernorat_client"),
    }


def _single_count(cur: Any, query: str) -> int:
    cur.execute(query)
    return int(cur.fetchone()[0] or 0)


def _blank_count(cur: Any, column_name: str, *, include_unknown: bool = False) -> int:
    unknown_filter = "" if include_unknown else "WHERE client_sk <> 0"
    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM iris_dw.dim_client
        {unknown_filter}
          {"AND" if unknown_filter else "WHERE"} (
              {column_name} IS NULL
              OR btrim({column_name}::text) = ''
          )
        """
    )
    return int(cur.fetchone()[0] or 0)


def _duplicate_count(
    cur: Any,
    column_name: str,
    *,
    exclude_blank: bool = False,
) -> int:
    blank_filter = (
        f"AND {column_name} IS NOT NULL AND btrim({column_name}::text) <> ''"
        if exclude_blank
        else ""
    )
    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM (
            SELECT {column_name}
            FROM iris_dw.dim_client
            WHERE client_sk <> 0
              {blank_filter}
            GROUP BY {column_name}
            HAVING COUNT(*) > 1
        ) duplicated_values
        """
    )
    return int(cur.fetchone()[0] or 0)


def _max_duplicate_group_size(cur: Any, column_name: str) -> int:
    cur.execute(
        f"""
        SELECT COALESCE(MAX(group_size), 0)
        FROM (
            SELECT COUNT(*) AS group_size
            FROM iris_dw.dim_client
            WHERE client_sk <> 0
              AND {column_name} IS NOT NULL
              AND btrim({column_name}::text) <> ''
            GROUP BY {column_name}
        ) grouped_values
        """
    )
    return int(cur.fetchone()[0] or 0)


def _distinct_count(cur: Any, column_name: str) -> int:
    cur.execute(
        f"""
        SELECT COUNT(DISTINCT {column_name})
        FROM iris_dw.dim_client
        WHERE client_sk <> 0
          AND {column_name} IS NOT NULL
          AND btrim({column_name}::text) <> ''
        """
    )
    return int(cur.fetchone()[0] or 0)


def _build_checks(metrics: dict[str, int]) -> list[QualityCheck]:
    return [
        _check("dim_client_row_count_positive", ">0", metrics["row_count"], "FAIL", metrics["row_count"] > 0),
        _check("dim_client_unknown_row_count", "1", metrics["unknown_row_count"], "FAIL", metrics["unknown_row_count"] == 1),
        _zero_check("dim_client_natural_key_null_count", metrics["natural_key_null_count"], "FAIL"),
        _zero_check("dim_client_natural_key_duplicate_count", metrics["natural_key_duplicate_count"], "FAIL"),
        _zero_check("dim_client_num_client_null_count", metrics["num_client_null_count"], "FAIL"),
        _zero_check("dim_client_code_nature_client_null_count", metrics["code_nature_client_null_count"], "FAIL"),
        _zero_check("dim_client_identifiant_client_null_count", metrics["identifiant_client_null_count"], "WARNING"),
        _zero_check(
            "dim_client_identifiant_client_duplicate_value_count",
            metrics["identifiant_client_duplicate_value_count"],
            "WARNING",
        ),
        _check(
            "dim_client_identifiant_client_max_duplicate_group_size",
            "<=1",
            metrics["identifiant_client_max_duplicate_group_size"],
            "WARNING",
            metrics["identifiant_client_max_duplicate_group_size"] <= 1,
        ),
        _zero_check("dim_client_sexe_null_count", metrics["sexe_null_count"], "WARNING"),
        _zero_check(
            "dim_client_situation_familiale_null_count",
            metrics["situation_familiale_null_count"],
            "WARNING",
        ),
        _zero_check("dim_client_date_naissance_null_count", metrics["date_naissance_null_count"], "WARNING"),
        _zero_check(
            "dim_client_gouvernorat_client_null_count",
            metrics["gouvernorat_client_null_count"],
            "WARNING",
        ),
        _check(
            "dim_client_gouvernorat_client_distinct_count",
            "<=100",
            metrics["gouvernorat_client_distinct_count"],
            "WARNING",
            metrics["gouvernorat_client_distinct_count"] <= 100,
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
        table_name="dim_client",
        expected_value=expected_value,
        observed_value=str(observed_value),
        status="PASS" if condition else failed_status,
        section=_section_for_check(check_name),
    )


def _section_for_check(check_name: str) -> str:
    if "natural_key" in check_name or "row_count" in check_name:
        return "Structural Checks"
    if "identifiant_client" in check_name:
        return "Identifier Reliability"
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
        "# IRISv2 dim_client Quality Validation",
        "",
        f"Generated at: {generated_at}",
        "",
        "This validation reads `iris_dw.dim_client`, writes audit checks to `iris_admin.data_quality_check`, and does not modify DW tables.",
        "",
        "## Decision",
        "",
        f"- dim_client.status: `{DECISION_STATUS}`",
        "- `client_natural_key` is the reliable DW key.",
        "- `identifiant_client` must not be used as a unique client key.",
        "- Duplicated `identifiant_client` values are treated as source/migration artifacts.",
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
        "Identifier Reliability",
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
        description="Validate iris_dw.dim_client quality without modifying DW data."
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
