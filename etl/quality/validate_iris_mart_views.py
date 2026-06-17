from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


MART_SCHEMA = "iris_mart"
REPORT_PATH = PROJECT_ROOT / "docs" / "iris_mart_views_validation.md"
SCORE_DEPENDENT_EMPTY_OK = {
    "vw_score_explanation",
    "vw_worklist_investigation",
}
EXPECTED_NONEMPTY_VIEWS = {
    "vw_client_behavior",
    "vw_dossier_360",
    "vw_vehicle_history",
}
EXPECTED_SINGLE_ROW_VIEWS = {"vw_dashboard_global"}


@dataclass
class ViewValidation:
    view_name: str
    status: str
    row_count: int | None = None
    column_count: int | None = None
    sample_columns: list[str] = field(default_factory=list)
    sample_rows: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    extra_checks: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResults:
    generated_at: str
    final_status: str
    views: list[ViewValidation]
    failures: list[str]
    warnings: list[str]


def main() -> None:
    _parse_args()
    results = validate_iris_mart_views()
    console_report = _build_console_report(results)
    markdown_report = _build_markdown_report(results)

    print(console_report)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(markdown_report, encoding="utf-8")
    print(f"\n[OK] Markdown validation written to {REPORT_PATH}")
    print(f"VALIDATION_STATUS={results.final_status}")


def validate_iris_mart_views() -> ValidationResults:
    generated_at = datetime.now().isoformat(timespec="seconds")
    validations: list[ViewValidation] = []

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            view_names = _discover_mart_views(cur)
            if not view_names:
                validation = ViewValidation(
                    view_name="<none>",
                    status="FAILURE",
                    reason="No iris_mart views exist",
                    failures=["No iris_mart views exist"],
                )
                validations.append(validation)
            else:
                for view_name in view_names:
                    validations.append(_validate_view(cur, view_name))
    finally:
        conn.close()

    failures = [
        f"{view.view_name}: {failure}"
        for view in validations
        for failure in view.failures
    ]
    warnings = [
        f"{view.view_name}: {warning}"
        for view in validations
        for warning in view.warnings
    ]

    if failures:
        final_status = "FAILURE"
    elif warnings:
        final_status = "WARNING"
    else:
        final_status = "OK"

    return ValidationResults(
        generated_at=generated_at,
        final_status=final_status,
        views=validations,
        failures=failures,
        warnings=warnings,
    )


def _discover_mart_views(cur: Any) -> list[str]:
    cur.execute(
        """
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = %s
        ORDER BY table_name
        """,
        (MART_SCHEMA,),
    )
    return [row[0] for row in cur.fetchall()]


def _validate_view(cur: Any, view_name: str) -> ViewValidation:
    validation = ViewValidation(view_name=view_name, status="OK")

    try:
        validation.row_count = _count_view_rows(cur, view_name)
        validation.sample_columns, validation.sample_rows = _sample_view_rows(
            cur,
            view_name,
        )
        validation.column_count = len(validation.sample_columns)
        validation.extra_checks = _run_extra_checks(cur, view_name)
        _add_coherence_warnings(validation)
        _set_final_view_status(validation)
    except Exception as exc:
        validation.status = "FAILURE"
        validation.reason = f"SQL error: {exc}"
        validation.failures.append(validation.reason)

    return validation


def _count_view_rows(cur: Any, view_name: str) -> int:
    query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
        sql.Identifier(MART_SCHEMA),
        sql.Identifier(view_name),
    )
    cur.execute(query)
    return int(cur.fetchone()[0])


def _sample_view_rows(
    cur: Any,
    view_name: str,
) -> tuple[list[str], list[dict[str, Any]]]:
    query = sql.SQL("SELECT * FROM {}.{} LIMIT 5").format(
        sql.Identifier(MART_SCHEMA),
        sql.Identifier(view_name),
    )
    cur.execute(query)
    columns = [description.name for description in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    return columns, rows


def _run_extra_checks(cur: Any, view_name: str) -> dict[str, Any]:
    if view_name == "vw_dossier_360":
        return _single_row_metrics(
            cur,
            view_name,
            {
                "row_count": "COUNT(*)",
                "sinistre_sk_null_count": "COUNT(*) FILTER (WHERE sinistre_sk IS NULL)",
                "score_global_not_null_count": (
                    "COUNT(*) FILTER (WHERE score_global IS NOT NULL)"
                ),
            },
        )

    if view_name == "vw_worklist_investigation":
        return _single_row_metrics(
            cur,
            view_name,
            {
                "row_count": "COUNT(*)",
                "score_global_not_null_count": (
                    "COUNT(*) FILTER (WHERE score_global IS NOT NULL)"
                ),
            },
        )

    if view_name == "vw_score_explanation":
        return _single_row_metrics(cur, view_name, {"row_count": "COUNT(*)"})

    if view_name == "vw_vehicle_history":
        return _single_row_metrics(
            cur,
            view_name,
            {
                "row_count": "COUNT(*)",
                "dernier_vhs_score_not_null_count": (
                    "COUNT(*) FILTER (WHERE dernier_vhs_score IS NOT NULL)"
                ),
            },
        )

    if view_name == "vw_dashboard_global":
        full_row = _sample_view_rows(cur, view_name)[1]
        return {
            **_single_row_metrics(cur, view_name, {"row_count": "COUNT(*)"}),
            "full_row": full_row[0] if full_row else None,
        }

    return {}


def _single_row_metrics(
    cur: Any,
    view_name: str,
    metrics: dict[str, str],
) -> dict[str, Any]:
    select_list = [
        sql.SQL("{} AS {}").format(sql.SQL(expression), sql.Identifier(alias))
        for alias, expression in metrics.items()
    ]
    query = sql.SQL("SELECT {} FROM {}.{}").format(
        sql.SQL(", ").join(select_list),
        sql.Identifier(MART_SCHEMA),
        sql.Identifier(view_name),
    )
    cur.execute(query)
    row = cur.fetchone()
    return {alias: row[index] for index, alias in enumerate(metrics)}


def _add_coherence_warnings(validation: ViewValidation) -> None:
    row_count = validation.row_count or 0
    view_name = validation.view_name

    if view_name in EXPECTED_NONEMPTY_VIEWS and row_count == 0:
        validation.warnings.append(
            "View returned 0 rows even though loaded DW facts should feed it"
        )

    if view_name in EXPECTED_SINGLE_ROW_VIEWS and row_count != 1:
        validation.warnings.append(
            f"Aggregate dashboard view returned {row_count} rows instead of 1"
        )

    if view_name in SCORE_DEPENDENT_EMPTY_OK and row_count == 0:
        validation.warnings.append(
            "Score-dependent view is empty; iris_score may not have run yet"
        )

    if view_name == "vw_dossier_360":
        if _extra_int(validation, "sinistre_sk_null_count") > 0:
            validation.warnings.append("vw_dossier_360 has rows with null sinistre_sk")
        if row_count > 0 and _extra_int(validation, "score_global_not_null_count") == 0:
            validation.warnings.append(
                "score_global is null for all sampled population; iris_score may not have run yet"
            )

    if view_name == "vw_worklist_investigation" and row_count > 0:
        if _extra_int(validation, "score_global_not_null_count") == 0:
            validation.warnings.append(
                "score_global is null for all worklist rows; iris_score may not have run yet"
            )

    if view_name == "vw_vehicle_history" and row_count > 0:
        if _extra_int(validation, "dernier_vhs_score_not_null_count") == 0:
            validation.warnings.append(
                "dernier_vhs_score is null for all vehicle rows; VHS scoring may not have run yet"
            )

    if view_name == "vw_dashboard_global":
        full_row = validation.extra_checks.get("full_row")
        if isinstance(full_row, dict) and full_row.get("score_global_moyen") is None:
            validation.warnings.append(
                "score_global_moyen is null; iris_score may not have run yet"
            )


def _set_final_view_status(validation: ViewValidation) -> None:
    if validation.failures:
        validation.status = "FAILURE"
        validation.reason = "; ".join(validation.failures)
        return
    if validation.warnings:
        validation.status = "WARNING"
        validation.reason = "; ".join(validation.warnings)
        return
    validation.status = "OK"
    validation.reason = "View compiled and returned coherent row counts"


def _extra_int(validation: ViewValidation, key: str) -> int:
    value = validation.extra_checks.get(key)
    if value is None:
        return 0
    return int(value)


def _build_console_report(results: ValidationResults) -> str:
    lines = [
        "=" * 100,
        "IRISv2 Mart Views Validation",
        f"Generated at: {results.generated_at}",
        "=" * 100,
        "",
        "View validation:",
    ]

    for view in results.views:
        row_count = "n/a" if view.row_count is None else view.row_count
        column_count = "n/a" if view.column_count is None else view.column_count
        lines.append(
            f"{view.view_name} | status={view.status} | row_count={row_count} | "
            f"column_count={column_count} | reason={view.reason}"
        )

    if results.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in results.warnings)

    if results.failures:
        lines.extend(["", "Failures:"])
        lines.extend(f"- {failure}" for failure in results.failures)

    return "\n".join(lines)


def _build_markdown_report(results: ValidationResults) -> str:
    lines = [
        "# IRISv2 Mart Views Validation",
        "",
        f"Generated at: {results.generated_at}",
        "",
        (
            "This validation is read-only. It queries existing `iris_mart` views "
            "and does not modify PostgreSQL objects or run scoring."
        ),
        "",
        "## 1. Summary",
        "",
        f"- final_status: `{results.final_status}`",
        f"- view_count: `{len([view for view in results.views if view.view_name != '<none>'])}`",
        f"- warning_count: `{len(results.warnings)}`",
        f"- failure_count: `{len(results.failures)}`",
        "",
        "## 2. View Inventory",
        "",
    ]

    inventory_rows = [
        {
            "view_name": view.view_name,
            "status": view.status,
            "column_count": _display_value(view.column_count),
        }
        for view in results.views
    ]
    lines.extend(_rows_to_markdown(inventory_rows, ["view_name", "status", "column_count"]))

    lines.extend(["", "## 3. Row Counts", ""])
    row_count_rows = [
        {
            "view_name": view.view_name,
            "status": view.status,
            "row_count": _display_value(view.row_count),
            "reason": view.reason,
        }
        for view in results.views
    ]
    lines.extend(
        _rows_to_markdown(row_count_rows, ["view_name", "status", "row_count", "reason"])
    )

    lines.extend(["", "## 4. Score/VHS Readiness Warnings", ""])
    score_warnings = [
        warning
        for warning in results.warnings
        if _is_score_or_vhs_warning(warning)
    ]
    if score_warnings:
        lines.extend(f"- {warning}" for warning in score_warnings)
    else:
        lines.append("- No score/VHS readiness warnings.")

    lines.extend(["", "## 5. Failures", ""])
    if results.failures:
        lines.extend(f"- {failure}" for failure in results.failures)
    else:
        lines.append("- No failures.")

    lines.extend(["", "## 6. Sample Columns Per View", ""])
    column_rows = [
        {
            "view_name": view.view_name,
            "sample_columns": ", ".join(view.sample_columns),
        }
        for view in results.views
    ]
    lines.extend(_rows_to_markdown(column_rows, ["view_name", "sample_columns"]))

    lines.extend(["", "## 7. Optional Sample Rows", ""])
    for view in results.views:
        lines.extend(["", f"### {view.view_name}", ""])
        if view.extra_checks:
            lines.append("Extra checks:")
            for key, value in view.extra_checks.items():
                lines.append(f"- {key}: `{_compact_value(value)}`")
            lines.append("")

        if view.sample_rows:
            lines.extend(_rows_to_markdown(view.sample_rows, view.sample_columns))
        else:
            lines.append("No sample rows.")

    return "\n".join(lines).rstrip() + "\n"


def _rows_to_markdown(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    if not rows:
        return ["No rows."]

    lines = [
        "| " + " | ".join(_markdown_cell(column) for column in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(_markdown_cell(_display_value(row.get(column))) for column in columns)
            + " |"
        )
    return lines


def _is_score_or_vhs_warning(warning: str) -> bool:
    lowered = warning.casefold()
    return any(token in lowered for token in ("score", "vhs", "iris_score"))


def _compact_value(value: Any) -> str:
    if isinstance(value, dict):
        return "; ".join(f"{key}={_display_value(val)}" for key, val in value.items())
    if isinstance(value, list):
        return f"{len(value)} rows"
    return _display_value(value)


def _display_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    if hasattr(value, "isoformat") and not isinstance(value, str):
        try:
            return value.isoformat()
        except TypeError:
            pass
    return str(value)


def _markdown_cell(value: Any) -> str:
    return _display_value(value).replace("|", "\\|").replace("\n", " ")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate existing iris_mart views without modifying PostgreSQL."
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
