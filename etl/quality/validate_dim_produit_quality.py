from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection
from etl.common.normalization import normalize_code, normalize_formula_code


REPORT_PATH = PROJECT_ROOT / "docs" / "dim_produit_quality_validation.md"
REFERENCE_FILE = PROJECT_ROOT / "data" / "reference" / "fichierStagiaire.xlsx"
AUTO_PRODUCT_PREFIX = "5"
DATA_QUALITY_CHECK_NAMES = (
    "dim_produit_duplicate_product_formula_count",
    "dim_produit_natural_key_mismatch_count",
    "dim_produit_real_row_null_code_formule_count",
    "dim_produit_missing_libelle_formule_count",
    "dim_produit_missing_libelle_famille_count",
    "dim_produit_reference_auto_product_formula_missing_count",
    "fact_prime_unknown_produit_count",
    "fact_sinistre_unknown_produit_count",
    "iris_mart_invalid_view_count",
    "dim_produit_validation_status",
)


def main() -> None:
    args = _parse_args()
    report_path = _resolve_project_path(args.report_path)
    results = validate_dim_produit_quality()
    markdown = _build_markdown(results)
    print(_build_console(results))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(markdown, encoding="utf-8")
    print(f"\n[OK] Markdown validation written to {report_path}")
    print(f"validation_status={results['validation_status']}")
    _write_data_quality_checks(args.etl_run_id, results)


def validate_dim_produit_quality() -> dict[str, Any]:
    generated_at = datetime.now().isoformat(timespec="seconds")
    failures: list[str] = []
    warnings: list[str] = []
    reference_pairs = _load_auto_reference_pairs(warnings)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            columns = _table_columns(cur, "iris_dw", "dim_produit")
            required_columns = {
                "produit_sk",
                "produit_natural_key",
                "code_produit",
                "libelle_produit",
                "code_formule",
                "libelle_formule",
                "code_famille_produit",
                "libelle_famille_produit",
            }
            missing_columns = sorted(required_columns - columns)
            if missing_columns:
                failures.append(
                    "dim_produit missing columns: " + ", ".join(missing_columns)
                )

            metrics = _dim_produit_metrics(cur) if not missing_columns else {}
            duplicate_rows = _duplicate_product_formula_rows(cur) if not missing_columns else []
            reference_gap_rows = (
                _reference_gap_rows(cur, reference_pairs) if not missing_columns else []
            )
            fact_metrics = _fact_metrics(cur)
            mart_metrics = _mart_metrics(cur)
    finally:
        conn.close()

    if metrics.get("duplicate_product_formula_count", 0):
        failures.append("dim_produit has duplicate code_produit + code_formule rows.")
    if metrics.get("natural_key_mismatch_count", 0):
        failures.append("produit_natural_key is not code_produit || '|' || code_formule.")
    if metrics.get("real_row_null_code_formule_count", 0):
        failures.append("Non-UNKNOWN dim_produit rows have null code_formule.")
    if reference_gap_rows:
        warnings.append("Automobile reference product-formula pairs are missing from dim_produit.")
    if metrics.get("missing_libelle_formule_count", 0):
        warnings.append("Some dim_produit rows are missing libelle_formule.")
    if metrics.get("missing_libelle_famille_count", 0):
        warnings.append("Some dim_produit rows are missing libelle_famille_produit.")
    if fact_metrics.get("fact_prime_unknown_produit_count", 0):
        warnings.append("fact_prime contains rows linked to UNKNOWN produit_sk.")
    if fact_metrics.get("fact_sinistre_unknown_produit_count", 0):
        warnings.append("fact_sinistre contains rows linked to UNKNOWN produit_sk.")
    if mart_metrics.get("invalid_view_count", 0):
        failures.append("One or more iris_mart views cannot be queried.")

    validation_status = "FAIL" if failures else "WARNING" if warnings else "OK"
    return {
        "generated_at": generated_at,
        "metrics": metrics,
        "duplicate_rows": duplicate_rows,
        "reference_pair_count": len(reference_pairs),
        "reference_gap_rows": reference_gap_rows,
        "fact_metrics": fact_metrics,
        "mart_metrics": mart_metrics,
        "failures": failures,
        "warnings": warnings,
        "validation_status": validation_status,
    }


def _load_auto_reference_pairs(warnings: list[str]) -> set[tuple[str, str]]:
    if not REFERENCE_FILE.exists():
        warnings.append(f"Reference file missing: {REFERENCE_FILE}")
        return set()
    with pd.ExcelFile(REFERENCE_FILE, engine="openpyxl") as workbook:
        sheet_by_stripped_name = {
            sheet_name.strip(): sheet_name for sheet_name in workbook.sheet_names
        }
        if "CODPROD" not in sheet_by_stripped_name:
            warnings.append("fichierStagiaire lacks CODPROD sheet.")
            return set()
        frame = pd.read_excel(
            workbook,
            sheet_name=sheet_by_stripped_name["CODPROD"],
            dtype=object,
        )
    frame.columns = [str(column).strip() for column in frame.columns]
    required = {"CODPROD", "CODFORMU"}
    if not required.issubset(frame.columns):
        warnings.append("fichierStagiaire CODPROD sheet lacks CODPROD/CODFORMU.")
        return set()
    frame["CODPROD"] = frame["CODPROD"].map(normalize_code)
    frame["CODFORMU"] = frame["CODFORMU"].map(normalize_formula_code)
    frame = frame[
        frame["CODPROD"].fillna("").str.startswith(AUTO_PRODUCT_PREFIX, na=False)
        & frame["CODFORMU"].notna()
    ]
    return {
        (str(row.CODPROD), str(row.CODFORMU))
        for row in frame[["CODPROD", "CODFORMU"]].drop_duplicates().itertuples(index=False)
    }


def _table_columns(cur: Any, schema: str, table: str) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        """,
        (schema, table),
    )
    return {row[0] for row in cur.fetchall()}


def _dim_produit_metrics(cur: Any) -> dict[str, int]:
    cur.execute(
        """
        SELECT
            COUNT(*) AS total_rows,
            COUNT(*) FILTER (WHERE produit_sk = 0) AS unknown_rows,
            COUNT(*) FILTER (
                WHERE produit_sk <> 0
                  AND (code_formule IS NULL OR btrim(code_formule) = '')
            ) AS real_row_null_code_formule_count,
            COUNT(*) FILTER (
                WHERE produit_sk <> 0
                  AND (libelle_produit IS NULL OR btrim(libelle_produit) = '')
            ) AS missing_libelle_produit_count,
            COUNT(*) FILTER (
                WHERE produit_sk <> 0
                  AND (libelle_formule IS NULL OR btrim(libelle_formule) = '')
            ) AS missing_libelle_formule_count,
            COUNT(*) FILTER (
                WHERE produit_sk <> 0
                  AND (
                    libelle_famille_produit IS NULL
                    OR btrim(libelle_famille_produit) = ''
                  )
            ) AS missing_libelle_famille_count,
            COUNT(*) FILTER (
                WHERE produit_sk <> 0
                  AND produit_natural_key <> code_produit || '|' || code_formule
            ) AS natural_key_mismatch_count
        FROM iris_dw.dim_produit
        """
    )
    row = cur.fetchone()
    names = [description.name for description in cur.description]
    metrics = {name: int(value or 0) for name, value in zip(names, row)}
    cur.execute(
        """
        SELECT COUNT(*)
        FROM (
            SELECT code_produit, code_formule
            FROM iris_dw.dim_produit
            GROUP BY code_produit, code_formule
            HAVING COUNT(*) > 1
        ) AS duplicates
        """
    )
    metrics["duplicate_product_formula_count"] = int(cur.fetchone()[0])
    cur.execute(
        """
        SELECT COUNT(*)
        FROM iris_dw.dim_produit
        WHERE code_produit LIKE %s
          AND produit_sk <> 0
        """,
        (f"{AUTO_PRODUCT_PREFIX}%",),
    )
    metrics["automobile_product_formula_rows"] = int(cur.fetchone()[0])
    return metrics


def _duplicate_product_formula_rows(cur: Any) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT code_produit, code_formule, COUNT(*) AS row_count
        FROM iris_dw.dim_produit
        GROUP BY code_produit, code_formule
        HAVING COUNT(*) > 1
        ORDER BY row_count DESC, code_produit, code_formule
        LIMIT 50
        """
    )
    names = [description.name for description in cur.description]
    return [dict(zip(names, row)) for row in cur.fetchall()]


def _reference_gap_rows(
    cur: Any,
    reference_pairs: set[tuple[str, str]],
) -> list[dict[str, Any]]:
    if not reference_pairs:
        return []
    cur.execute(
        """
        SELECT code_produit, code_formule
        FROM iris_dw.dim_produit
        WHERE code_produit LIKE %s
          AND produit_sk <> 0
        """,
        (f"{AUTO_PRODUCT_PREFIX}%",),
    )
    loaded_pairs = {(str(code), str(formule)) for code, formule in cur.fetchall()}
    missing_pairs = sorted(reference_pairs - loaded_pairs)
    return [
        {"code_produit": code, "code_formule": formule}
        for code, formule in missing_pairs[:100]
    ]


def _fact_metrics(cur: Any) -> dict[str, int]:
    metrics: dict[str, int] = {}
    for table_name in ("fact_prime", "fact_sinistre"):
        if not _table_columns(cur, "iris_dw", table_name):
            metrics[f"{table_name}_rows"] = 0
            metrics[f"{table_name}_unknown_produit_count"] = 0
            continue
        cur.execute(f"SELECT COUNT(*) FROM iris_dw.{table_name}")
        metrics[f"{table_name}_rows"] = int(cur.fetchone()[0])
        cur.execute(
            f"SELECT COUNT(*) FROM iris_dw.{table_name} WHERE produit_sk = 0"
        )
        metrics[f"{table_name}_unknown_produit_count"] = int(cur.fetchone()[0])
    return metrics


def _mart_metrics(cur: Any) -> dict[str, int]:
    cur.execute(
        """
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'iris_mart'
        ORDER BY table_name
        """
    )
    view_names = [row[0] for row in cur.fetchall()]
    invalid_view_count = 0
    for view_name in view_names:
        cur.execute("SAVEPOINT mart_view_check")
        try:
            cur.execute(f'SELECT COUNT(*) FROM iris_mart."{view_name}"')
            cur.fetchone()
        except Exception:
            invalid_view_count += 1
            cur.execute("ROLLBACK TO SAVEPOINT mart_view_check")
        finally:
            cur.execute("RELEASE SAVEPOINT mart_view_check")
    return {
        "mart_view_count": len(view_names),
        "invalid_view_count": invalid_view_count,
    }


def _write_data_quality_checks(
    etl_run_id: str | None,
    results: dict[str, Any],
) -> None:
    rows = _data_quality_check_rows(etl_run_id, results)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            check_name_placeholders = ", ".join(
                "%s" for _ in DATA_QUALITY_CHECK_NAMES
            )
            if etl_run_id is None:
                cur.execute(
                    f"""
                    DELETE FROM iris_admin.data_quality_check
                    WHERE etl_run_id IS NULL
                      AND check_name IN ({check_name_placeholders})
                    """,
                    DATA_QUALITY_CHECK_NAMES,
                )
            else:
                cur.execute(
                    f"""
                    DELETE FROM iris_admin.data_quality_check
                    WHERE etl_run_id = %s
                      AND check_name IN ({check_name_placeholders})
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


def _data_quality_check_rows(
    etl_run_id: str | None,
    results: dict[str, Any],
) -> list[dict[str, str | None]]:
    metrics = results["metrics"]
    fact_metrics = results["fact_metrics"]
    mart_metrics = results["mart_metrics"]
    reference_missing_count = len(results["reference_gap_rows"])
    validation_status = results["validation_status"]

    return [
        _check_row(
            etl_run_id,
            "dim_produit_duplicate_product_formula_count",
            "iris_dw",
            "dim_produit",
            "0",
            metrics.get("duplicate_product_formula_count", 0),
            _zero_status(metrics.get("duplicate_product_formula_count", 0), "FAIL"),
        ),
        _check_row(
            etl_run_id,
            "dim_produit_natural_key_mismatch_count",
            "iris_dw",
            "dim_produit",
            "0",
            metrics.get("natural_key_mismatch_count", 0),
            _zero_status(metrics.get("natural_key_mismatch_count", 0), "FAIL"),
        ),
        _check_row(
            etl_run_id,
            "dim_produit_real_row_null_code_formule_count",
            "iris_dw",
            "dim_produit",
            "0",
            metrics.get("real_row_null_code_formule_count", 0),
            _zero_status(metrics.get("real_row_null_code_formule_count", 0), "FAIL"),
        ),
        _check_row(
            etl_run_id,
            "dim_produit_missing_libelle_formule_count",
            "iris_dw",
            "dim_produit",
            "0",
            metrics.get("missing_libelle_formule_count", 0),
            _zero_status(metrics.get("missing_libelle_formule_count", 0), "WARNING"),
        ),
        _check_row(
            etl_run_id,
            "dim_produit_missing_libelle_famille_count",
            "iris_dw",
            "dim_produit",
            "0",
            metrics.get("missing_libelle_famille_count", 0),
            _zero_status(metrics.get("missing_libelle_famille_count", 0), "WARNING"),
        ),
        _check_row(
            etl_run_id,
            "dim_produit_reference_auto_product_formula_missing_count",
            "iris_dw",
            "dim_produit",
            "0",
            reference_missing_count,
            _zero_status(reference_missing_count, "WARNING"),
        ),
        _check_row(
            etl_run_id,
            "fact_prime_unknown_produit_count",
            "iris_dw",
            "fact_prime",
            "0",
            fact_metrics.get("fact_prime_unknown_produit_count", 0),
            _zero_status(
                fact_metrics.get("fact_prime_unknown_produit_count", 0),
                "WARNING",
            ),
        ),
        _check_row(
            etl_run_id,
            "fact_sinistre_unknown_produit_count",
            "iris_dw",
            "fact_sinistre",
            "0",
            fact_metrics.get("fact_sinistre_unknown_produit_count", 0),
            _zero_status(
                fact_metrics.get("fact_sinistre_unknown_produit_count", 0),
                "WARNING",
            ),
        ),
        _check_row(
            etl_run_id,
            "iris_mart_invalid_view_count",
            "iris_mart",
            "*",
            "0",
            mart_metrics.get("invalid_view_count", 0),
            _zero_status(mart_metrics.get("invalid_view_count", 0), "FAIL"),
        ),
        _check_row(
            etl_run_id,
            "dim_produit_validation_status",
            "iris_dw",
            "dim_produit",
            "OK",
            validation_status,
            validation_status,
        ),
    ]


def _check_row(
    etl_run_id: str | None,
    check_name: str,
    schema_name: str,
    table_name: str,
    expected_value: str,
    observed_value: Any,
    status: str,
) -> dict[str, str | None]:
    return {
        "etl_run_id": etl_run_id,
        "check_name": check_name,
        "schema_name": schema_name,
        "table_name": table_name,
        "expected_value": expected_value,
        "observed_value": str(observed_value),
        "status": _data_quality_status(status),
    }


def _data_quality_status(status: str) -> str:
    if status == "OK":
        return "PASS"
    if status in {"WARNING", "FAIL"}:
        return status
    raise ValueError(f"Unsupported data quality status: {status}")


def _zero_status(observed_value: Any, non_zero_status: str) -> str:
    return "OK" if int(observed_value or 0) == 0 else non_zero_status


def _build_console(results: dict[str, Any]) -> str:
    lines = [
        "IRISv2 dim_produit Quality Validation",
        f"Generated at: {results['generated_at']}",
    ]
    for section_name in ("metrics", "fact_metrics", "mart_metrics"):
        for key, value in results[section_name].items():
            lines.append(f"{key}={value}")
    lines.append(f"reference_auto_product_formula_pair_count={results['reference_pair_count']}")
    lines.append(f"reference_auto_product_formula_missing_count={len(results['reference_gap_rows'])}")
    lines.append(f"validation_status={results['validation_status']}")
    return "\n".join(lines)


def _build_markdown(results: dict[str, Any]) -> str:
    lines = [
        "# IRISv2 dim_produit Quality Validation",
        "",
        f"Generated at: {results['generated_at']}",
        "",
        "This validation is read-only. It checks `iris_dw.dim_produit`, fact product links, and mart queryability without modifying data.",
        "",
        "## Summary",
        "",
    ]
    for section_name in ("metrics", "fact_metrics", "mart_metrics"):
        for key, value in results[section_name].items():
            lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            f"- reference_auto_product_formula_pair_count: `{results['reference_pair_count']}`",
            f"- reference_auto_product_formula_missing_count: `{len(results['reference_gap_rows'])}`",
            f"- validation_status: `{results['validation_status']}`",
            "",
            "## Duplicate Product Formula Rows",
            "",
            *_rows_to_markdown(
                results["duplicate_rows"],
                ["code_produit", "code_formule", "row_count"],
            ),
            "",
            "## Missing Automobile Reference Pairs",
            "",
            *_rows_to_markdown(
                results["reference_gap_rows"],
                ["code_produit", "code_formule"],
            ),
            "",
            "## Warnings And Failures",
            "",
            *_rows_to_markdown(
                [{"type": "FAILURE", "message": value} for value in results["failures"]]
                + [{"type": "WARNING", "message": value} for value in results["warnings"]],
                ["type", "message"],
            ),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _rows_to_markdown(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    if not rows:
        return ["No rows."]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return lines


def _resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate iris_dw.dim_produit product-formula grain quality."
    )
    parser.add_argument(
        "--report-path",
        default=str(REPORT_PATH),
        help="Markdown report path.",
    )
    parser.add_argument(
        "--etl-run-id",
        default=None,
        help="Optional ETL run id used when persisting data quality checks.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
