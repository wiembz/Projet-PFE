from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


TARGET_SCHEMA = "iris_dw"
REPORT_PATH = PROJECT_ROOT / "docs" / "reference_labels_auto_diagnostic.md"
AUTO_PRODUCT_PREFIX = "5"

TABLES = (
    "dim_produit",
    "fact_prime",
    "fact_sinistre",
    "dim_garantie",
    "dim_cause_sinistre",
    "dim_intermediaire",
    "dim_delegation",
)

PRODUCT_CODE_CANDIDATES = (
    "code_produit",
    "produit_code",
    "cod_prd",
    "code_branche",
    "product_code",
)
PRODUCT_CODE_COMPATIBILITY_CANDIDATES = (
    "codprod",
    "code_famille_produit",
    "codfam",
)
PRODUCT_LABEL_CANDIDATES = (
    "libelle_produit",
    "produit_libelle",
    "libelle",
    "product_label",
    "nom_produit",
)

GARANTIE_CODE_CANDIDATES = (
    "code_garantie",
    "garantie_code",
    "cod_gar",
    "code_garantie_sinistre",
    "grntsini",
    "garantie_natural_key",
)
GARANTIE_LABEL_CANDIDATES = (
    "libelle_garantie",
    "garantie_libelle",
    "libelle",
    "garantie_label",
    "nom_garantie",
)

CAUSE_CODE_CANDIDATES = (
    "code_cause_sinistre",
    "cause_sinistre_code",
    "code_cause",
    "cod_cause",
    "cause_code",
    "causesini",
    "cause_sinistre_natural_key",
)
CAUSE_LABEL_CANDIDATES = (
    "libelle_cause_sinistre",
    "cause_sinistre_libelle",
    "libelle_cause",
    "cause_label",
    "libelle",
)
SOUS_NATURE_LABEL_CANDIDATES = (
    "libelle_sous_nature_sinistre",
    "libelle_sous_nature",
    "sous_nature_libelle",
    "libelle_sous_cause",
    "sous_nature_label",
)

INTERMEDIAIRE_CODE_CANDIDATES = (
    "code_intermediaire",
    "intermediaire_code",
    "cod_intermediaire",
    "id_intermediaire",
    "idint",
    "code_agent",
    "intermediaire_natural_key",
)
INTERMEDIAIRE_LABEL_CANDIDATES = (
    "libelle_intermediaire",
    "intermediaire_libelle",
    "nom_intermediaire",
    "raison_sociale",
    "libelle",
)

DELEGATION_CODE_CANDIDATES = (
    "code_delegation",
    "delegation_code",
    "cod_delegation",
    "id_delegation",
    "iddelega",
    "code_agence",
    "delegation_natural_key",
)
DELEGATION_LABEL_CANDIDATES = (
    "libelle_delegation",
    "delegation_libelle",
    "nom_delegation",
    "libelle_agence",
    "libelle",
)

MISSING_LABEL_MARKERS = ("UNKNOWN", "N/A", "NA", "NULL", "NONE", "NAN", "<NA>")


class Report:
    def __init__(self) -> None:
        self.console_lines: list[str] = []
        self.markdown_lines: list[str] = []

    def title(self, text: str, generated_at: str) -> None:
        self.console_lines.extend(
            [
                "=" * 100,
                text,
                f"Generated at: {generated_at}",
                "=" * 100,
            ]
        )
        self.markdown_lines.extend(
            [
                f"# {text}",
                "",
                f"Generated at: {generated_at}",
                "",
                (
                    "This diagnostic is read-only. It profiles the automobile "
                    "reference-label perimeter in `iris_dw`; it does not modify "
                    "PostgreSQL, Silver files, loaders, scoring, marts, or "
                    "orchestration."
                ),
                "",
                "Automobile perimeter: product codes starting with `5`.",
                "",
            ]
        )

    def section(self, text: str) -> None:
        self.console_lines.extend(["", "-" * 100, text])
        self.markdown_lines.extend(["", f"## {text}", ""])

    def subsection(self, text: str) -> None:
        self.console_lines.extend(["", text])
        self.markdown_lines.extend(["", f"### {text}", ""])

    def metric(self, label: str, value: Any) -> None:
        self.console_lines.append(f"{label}: {_display_value(value)}")
        self.markdown_lines.append(f"- {label}: `{_display_value(value)}`")

    def table(self, rows: list[dict[str, Any]], columns: list[str]) -> None:
        if not rows:
            self.console_lines.append("No rows.")
            self.markdown_lines.append("No rows.")
            return

        dataframe = pd.DataFrame(rows, columns=columns)
        dataframe = dataframe.astype(object).where(pd.notna(dataframe), "")
        self.console_lines.append(dataframe.to_string(index=False))
        self.markdown_lines.extend(
            _rows_to_markdown(dataframe.to_dict(orient="records"), columns)
        )

    def bullets(self, values: list[str]) -> None:
        if not values:
            self.console_lines.append("No items.")
            self.markdown_lines.append("- No items.")
            return
        for value in values:
            self.console_lines.append(f"- {value}")
            self.markdown_lines.append(f"- {value}")

    def render_console(self) -> str:
        return "\n".join(self.console_lines)

    def render_markdown(self) -> str:
        return "\n".join(self.markdown_lines).rstrip() + "\n"


def main() -> None:
    _parse_args()
    results = diagnose_reference_labels_auto()
    report = _build_report(results)

    print(report.render_console())
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report.render_markdown(), encoding="utf-8")
    print(f"\n[OK] Markdown diagnostic written to {REPORT_PATH}")
    print(f"validation_status: {results['summary']['validation_status']}")


def diagnose_reference_labels_auto() -> dict[str, Any]:
    generated_at = datetime.now().isoformat(timespec="seconds")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            schemas = _load_table_columns(cur)
            product_config = _product_config(schemas["dim_produit"])

            product = _diagnose_dim_produit(cur, schemas, product_config)
            prime = _diagnose_fact_product_usage(
                cur,
                schemas,
                product_config,
                fact_table="fact_prime",
                fact_alias="fp",
                fact_label="prime",
            )
            sinistre = _diagnose_fact_product_usage(
                cur,
                schemas,
                product_config,
                fact_table="fact_sinistre",
                fact_alias="fs",
                fact_label="sinistre",
            )
            garantie = _diagnose_garantie(cur, schemas, product_config)
            cause = _diagnose_cause_sinistre(cur, schemas, product_config)
            intermediaire = _diagnose_portfolio_dimension(
                cur,
                schemas,
                product_config,
                dimension_table="dim_intermediaire",
                dimension_alias="di",
                key_column="intermediaire_sk",
                code_candidates=INTERMEDIAIRE_CODE_CANDIDATES,
                label_candidates=INTERMEDIAIRE_LABEL_CANDIDATES,
                label="intermediaire",
            )
            delegation = _diagnose_portfolio_dimension(
                cur,
                schemas,
                product_config,
                dimension_table="dim_delegation",
                dimension_alias="dd",
                key_column="delegation_sk",
                code_candidates=DELEGATION_CODE_CANDIDATES,
                label_candidates=DELEGATION_LABEL_CANDIDATES,
                label="delegation",
            )
    finally:
        conn.close()

    sections = {
        "dim_produit": product,
        "fact_prime": prime,
        "fact_sinistre": sinistre,
        "dim_garantie": garantie,
        "dim_cause_sinistre": cause,
        "dim_intermediaire": intermediaire,
        "dim_delegation": delegation,
    }
    failures = [failure for section in sections.values() for failure in section["failures"]]
    warnings = [warning for section in sections.values() for warning in section["warnings"]]

    summary = {
        "auto_product_count": product["auto_product_count"],
        "auto_product_missing_label_count": product["auto_product_missing_label_count"],
        "auto_prime_rows": prime["auto_rows"],
        "auto_sinistre_rows": sinistre["auto_rows"],
        "auto_garantie_missing_label_count": garantie["missing_label_count"],
        "auto_cause_missing_label_count": cause["missing_cause_label_count"],
        "auto_intermediaire_missing_label_count": intermediaire["missing_label_count"],
        "auto_delegation_missing_label_count": delegation["missing_label_count"],
    }
    summary["validation_status"] = _validation_status(summary, warnings, failures)

    return {
        "generated_at": generated_at,
        "schemas": schemas,
        "product_config": product_config,
        "sections": sections,
        "summary": summary,
        "warnings": warnings,
        "failures": failures,
        "recommendations": _recommendations(sections),
    }


def _diagnose_dim_produit(
    cur: Any,
    schemas: dict[str, set[str]],
    config: dict[str, Any],
) -> dict[str, Any]:
    result = _empty_result(
        auto_product_count=0,
        auto_product_missing_label_count=0,
        total_product_rows=0,
        missing_label_rows=[],
    )
    columns = schemas["dim_produit"]
    if not columns:
        result["failures"].append("iris_dw.dim_produit does not exist")
        return result
    if not config["code_column"]:
        candidates = ", ".join(PRODUCT_CODE_CANDIDATES)
        result["failures"].append(
            "iris_dw.dim_produit has no automobile product code column; "
            f"expected one of: {candidates}"
        )
        return result

    total_query = sql.SQL(
        "SELECT COUNT(*) FROM {} AS dp WHERE {}"
    ).format(
        _table_ref("dim_produit"),
        _product_not_unknown_condition(config, "dp"),
    )
    result["total_product_rows"] = _fetch_scalar(cur, total_query)

    auto_where = _auto_product_condition(config, "dp")
    auto_query = sql.SQL(
        "SELECT COUNT(*) FROM {} AS dp WHERE {}"
    ).format(_table_ref("dim_produit"), auto_where)
    result["auto_product_count"] = _fetch_scalar(cur, auto_query)

    label_column = config["label_column"]
    if label_column:
        missing_count_query = sql.SQL(
            """
            SELECT COUNT(*)
            FROM {} AS dp
            WHERE {}
              AND {}
            """
        ).format(
            _table_ref("dim_produit"),
            auto_where,
            _missing_text_condition("dp", label_column),
        )
        result["auto_product_missing_label_count"] = _fetch_scalar(
            cur,
            missing_count_query,
        )
        missing_filter = _missing_text_condition("dp", label_column)
        label_status = _label_status_sql("dp", label_column)
    else:
        result["auto_product_missing_label_count"] = result["auto_product_count"]
        result["warnings"].append(
            "iris_dw.dim_produit has no product label column; all automobile "
            "products are reported as label unavailable."
        )
        missing_filter = sql.SQL("TRUE")
        label_status = sql.Literal("NO_LABEL_COLUMN")

    missing_rows_query = sql.SQL(
        """
        SELECT
            {} AS product_code,
            {} AS product_label,
            {} AS label_status
        FROM {} AS dp
        WHERE {}
          AND {}
        ORDER BY product_code
        LIMIT 100
        """
    ).format(
        _trim_text("dp", config["code_column"]),
        _label_display_sql("dp", label_column),
        label_status,
        _table_ref("dim_produit"),
        auto_where,
        missing_filter,
    )
    result["missing_label_rows"] = _fetch_dicts(cur, missing_rows_query)

    if result["auto_product_missing_label_count"]:
        result["warnings"].append(
            "Automobile dim_produit rows with missing or weak product labels found."
        )

    return result


def _diagnose_fact_product_usage(
    cur: Any,
    schemas: dict[str, set[str]],
    config: dict[str, Any],
    *,
    fact_table: str,
    fact_alias: str,
    fact_label: str,
) -> dict[str, Any]:
    result = _empty_result(
        total_rows=0,
        auto_rows=0,
        missing_product_label_rows=0,
        top_product_rows=[],
    )
    fact_columns = schemas[fact_table]
    if not fact_columns:
        result["warnings"].append(f"iris_dw.{fact_table} does not exist; skipped.")
        return result

    required = _missing_required_columns(
        {
            fact_table: (fact_columns, ("produit_sk",)),
            "dim_produit": (schemas["dim_produit"], ("produit_sk",)),
        }
    )
    if required or not config["code_column"]:
        reason = "; ".join(required) or "dim_produit product code column is unavailable"
        result["warnings"].append(f"{fact_table} automobile usage skipped: {reason}.")
        return result

    result["total_rows"] = _fetch_scalar(
        cur,
        sql.SQL("SELECT COUNT(*) FROM {} AS {}").format(
            _table_ref(fact_table),
            sql.Identifier(fact_alias),
        ),
    )

    auto_where = _auto_product_condition(config, "dp")
    auto_count_query = sql.SQL(
        """
        SELECT COUNT(*)
        FROM {} AS {}
        JOIN {} AS dp
          ON {}.produit_sk = dp.produit_sk
        WHERE {}
        """
    ).format(
        _table_ref(fact_table),
        sql.Identifier(fact_alias),
        _table_ref("dim_produit"),
        sql.Identifier(fact_alias),
        auto_where,
    )
    result["auto_rows"] = _fetch_scalar(cur, auto_count_query)

    product_label = config["label_column"]
    if product_label:
        missing_count_query = sql.SQL(
            """
            SELECT COUNT(*)
            FROM {} AS {}
            JOIN {} AS dp
              ON {}.produit_sk = dp.produit_sk
            WHERE {}
              AND {}
            """
        ).format(
            _table_ref(fact_table),
            sql.Identifier(fact_alias),
            _table_ref("dim_produit"),
            sql.Identifier(fact_alias),
            auto_where,
            _missing_text_condition("dp", product_label),
        )
        result["missing_product_label_rows"] = _fetch_scalar(cur, missing_count_query)
    else:
        result["missing_product_label_rows"] = result["auto_rows"]

    top_query = sql.SQL(
        """
        SELECT
            {} AS product_code,
            {} AS product_label,
            COUNT(*) AS row_count,
            {} AS label_status
        FROM {} AS {}
        JOIN {} AS dp
          ON {}.produit_sk = dp.produit_sk
        WHERE {}
        GROUP BY 1, 2, 4
        ORDER BY row_count DESC, product_code
        LIMIT 50
        """
    ).format(
        _trim_text("dp", config["code_column"]),
        _label_display_sql("dp", product_label),
        _label_status_sql("dp", product_label),
        _table_ref(fact_table),
        sql.Identifier(fact_alias),
        _table_ref("dim_produit"),
        sql.Identifier(fact_alias),
        auto_where,
    )
    result["top_product_rows"] = _fetch_dicts(cur, top_query)

    if result["missing_product_label_rows"]:
        result["warnings"].append(
            f"Automobile {fact_label} rows linked to missing product labels found."
        )

    return result


def _diagnose_garantie(
    cur: Any,
    schemas: dict[str, set[str]],
    product_config: dict[str, Any],
) -> dict[str, Any]:
    result = _empty_result(
        distinct_code_count=0,
        missing_label_count=0,
        top_rows=[],
        code_column=None,
        label_column=None,
    )
    fact_columns = schemas["fact_sinistre"]
    dim_columns = schemas["dim_garantie"]
    if not fact_columns or not dim_columns:
        result["warnings"].append(
            "Guarantee label usage skipped: fact_sinistre or dim_garantie is missing."
        )
        return result

    required = _missing_required_columns(
        {
            "fact_sinistre": (fact_columns, ("produit_sk", "garantie_sk")),
            "dim_produit": (schemas["dim_produit"], ("produit_sk",)),
            "dim_garantie": (dim_columns, ("garantie_sk",)),
        }
    )
    if required or not product_config["code_column"]:
        reason = "; ".join(required) or "dim_produit product code column is unavailable"
        result["warnings"].append(f"Guarantee label usage skipped: {reason}.")
        return result

    code_column = _detect_column(dim_columns, GARANTIE_CODE_CANDIDATES)
    label_column = _detect_column(dim_columns, GARANTIE_LABEL_CANDIDATES)
    result["code_column"] = code_column
    result["label_column"] = label_column
    if not code_column:
        result["warnings"].append(
            "dim_garantie has no recognized garantie code column; using garantie_sk."
        )
    if not label_column:
        result["warnings"].append(
            "dim_garantie has no recognized garantie label column; missing-label "
            "count is not evaluated."
        )
        result["missing_label_count"] = "N/A"

    code_expr = _dimension_code_or_sk("dg", "fs", code_column, "garantie_sk", "GARANTIE")
    auto_where = _auto_product_condition(product_config, "dp")

    counts_query = sql.SQL(
        """
        SELECT
            COUNT(DISTINCT {}) AS distinct_code_count,
            {} AS missing_label_count
        FROM {} AS fs
        JOIN {} AS dp
          ON fs.produit_sk = dp.produit_sk
        LEFT JOIN {} AS dg
          ON fs.garantie_sk = dg.garantie_sk
        WHERE {}
          AND fs.garantie_sk IS NOT NULL
        """
    ).format(
        code_expr,
        _distinct_missing_count_sql(code_expr, "dg", label_column),
        _table_ref("fact_sinistre"),
        _table_ref("dim_produit"),
        _table_ref("dim_garantie"),
        auto_where,
    )
    counts = _fetch_one_dict(cur, counts_query)
    result["distinct_code_count"] = counts["distinct_code_count"]
    if label_column:
        result["missing_label_count"] = counts["missing_label_count"]

    top_query = sql.SQL(
        """
        SELECT
            {} AS garantie_code,
            {} AS garantie_label,
            COUNT(*) AS row_count,
            {} AS label_status
        FROM {} AS fs
        JOIN {} AS dp
          ON fs.produit_sk = dp.produit_sk
        LEFT JOIN {} AS dg
          ON fs.garantie_sk = dg.garantie_sk
        WHERE {}
          AND fs.garantie_sk IS NOT NULL
        GROUP BY 1, 2, 4
        ORDER BY row_count DESC, garantie_code
        LIMIT 50
        """
    ).format(
        code_expr,
        _label_display_sql("dg", label_column),
        _label_status_sql("dg", label_column),
        _table_ref("fact_sinistre"),
        _table_ref("dim_produit"),
        _table_ref("dim_garantie"),
        auto_where,
    )
    result["top_rows"] = _fetch_dicts(cur, top_query)

    if _positive_count(result["missing_label_count"]):
        result["warnings"].append(
            "Automobile sinistres use garantie codes with missing labels."
        )

    return result


def _diagnose_cause_sinistre(
    cur: Any,
    schemas: dict[str, set[str]],
    product_config: dict[str, Any],
) -> dict[str, Any]:
    result = _empty_result(
        distinct_code_count=0,
        missing_cause_label_count=0,
        missing_sous_nature_label_count="N/A",
        top_rows=[],
        code_column=None,
        label_column=None,
        sous_nature_label_column=None,
    )
    fact_columns = schemas["fact_sinistre"]
    dim_columns = schemas["dim_cause_sinistre"]
    if not fact_columns or not dim_columns:
        result["warnings"].append(
            "Cause label usage skipped: fact_sinistre or dim_cause_sinistre is missing."
        )
        return result

    required = _missing_required_columns(
        {
            "fact_sinistre": (fact_columns, ("produit_sk", "cause_sinistre_sk")),
            "dim_produit": (schemas["dim_produit"], ("produit_sk",)),
            "dim_cause_sinistre": (dim_columns, ("cause_sinistre_sk",)),
        }
    )
    if required or not product_config["code_column"]:
        reason = "; ".join(required) or "dim_produit product code column is unavailable"
        result["warnings"].append(f"Cause label usage skipped: {reason}.")
        return result

    code_column = _detect_column(dim_columns, CAUSE_CODE_CANDIDATES)
    label_column = _detect_column(dim_columns, CAUSE_LABEL_CANDIDATES)
    nature_code_column = _detect_column(
        dim_columns,
        ("code_nature_sinistre", "nature_sinistre_code", "natsini"),
    )
    sous_nature_code_column = _detect_column(
        dim_columns,
        ("code_sous_nature_sinistre", "sous_nature_sinistre_code", "sounatsin"),
    )
    sous_nature_label_column = _detect_column(dim_columns, SOUS_NATURE_LABEL_CANDIDATES)

    result["code_column"] = code_column
    result["label_column"] = label_column
    result["sous_nature_label_column"] = sous_nature_label_column

    if not code_column:
        result["warnings"].append(
            "dim_cause_sinistre has no recognized cause code column; "
            "using cause_sinistre_sk."
        )
    if not label_column:
        result["warnings"].append(
            "dim_cause_sinistre has no recognized cause label column; "
            "missing cause-label count is not evaluated."
        )
        result["missing_cause_label_count"] = "N/A"

    code_expr = _dimension_code_or_sk(
        "dc",
        "fs",
        code_column,
        "cause_sinistre_sk",
        "CAUSE",
    )
    auto_where = _auto_product_condition(product_config, "dp")

    counts_query = sql.SQL(
        """
        SELECT
            COUNT(DISTINCT {}) AS distinct_code_count,
            {} AS missing_cause_label_count,
            {} AS missing_sous_nature_label_count
        FROM {} AS fs
        JOIN {} AS dp
          ON fs.produit_sk = dp.produit_sk
        LEFT JOIN {} AS dc
          ON fs.cause_sinistre_sk = dc.cause_sinistre_sk
        WHERE {}
          AND fs.cause_sinistre_sk IS NOT NULL
        """
    ).format(
        code_expr,
        _distinct_missing_count_sql(code_expr, "dc", label_column),
        _distinct_missing_count_sql(code_expr, "dc", sous_nature_label_column),
        _table_ref("fact_sinistre"),
        _table_ref("dim_produit"),
        _table_ref("dim_cause_sinistre"),
        auto_where,
    )
    counts = _fetch_one_dict(cur, counts_query)
    result["distinct_code_count"] = counts["distinct_code_count"]
    if label_column:
        result["missing_cause_label_count"] = counts["missing_cause_label_count"]
    if sous_nature_label_column:
        result["missing_sous_nature_label_count"] = counts[
            "missing_sous_nature_label_count"
        ]

    top_query = sql.SQL(
        """
        SELECT
            {} AS cause_code,
            {} AS nature_code,
            {} AS sous_nature_code,
            {} AS cause_label,
            {} AS sous_nature_label,
            COUNT(*) AS row_count,
            {} AS cause_label_status,
            {} AS sous_nature_label_status
        FROM {} AS fs
        JOIN {} AS dp
          ON fs.produit_sk = dp.produit_sk
        LEFT JOIN {} AS dc
          ON fs.cause_sinistre_sk = dc.cause_sinistre_sk
        WHERE {}
          AND fs.cause_sinistre_sk IS NOT NULL
        GROUP BY 1, 2, 3, 4, 5, 7, 8
        ORDER BY row_count DESC, cause_code
        LIMIT 50
        """
    ).format(
        code_expr,
        _nullable_text("dc", nature_code_column),
        _nullable_text("dc", sous_nature_code_column),
        _label_display_sql("dc", label_column),
        _label_display_sql("dc", sous_nature_label_column),
        _label_status_sql("dc", label_column),
        _label_status_sql("dc", sous_nature_label_column),
        _table_ref("fact_sinistre"),
        _table_ref("dim_produit"),
        _table_ref("dim_cause_sinistre"),
        auto_where,
    )
    result["top_rows"] = _fetch_dicts(cur, top_query)

    if _positive_count(result["missing_cause_label_count"]):
        result["warnings"].append(
            "Automobile sinistres use cause codes with missing cause labels."
        )
    if _positive_count(result["missing_sous_nature_label_count"]):
        result["warnings"].append(
            "Automobile sinistres use cause codes with missing sous-nature labels."
        )

    return result


def _diagnose_portfolio_dimension(
    cur: Any,
    schemas: dict[str, set[str]],
    product_config: dict[str, Any],
    *,
    dimension_table: str,
    dimension_alias: str,
    key_column: str,
    code_candidates: tuple[str, ...],
    label_candidates: tuple[str, ...],
    label: str,
) -> dict[str, Any]:
    result = _empty_result(
        distinct_used_count=0,
        missing_label_count=0,
        top_missing_rows=[],
        code_column=None,
        label_column=None,
        sources=[],
    )
    dim_columns = schemas[dimension_table]
    if not dim_columns:
        result["warnings"].append(f"iris_dw.{dimension_table} does not exist; skipped.")
        return result
    if key_column not in dim_columns:
        result["warnings"].append(
            f"{dimension_table} missing {key_column}; {label} label usage skipped."
        )
        return result
    if not product_config["code_column"] or "produit_sk" not in schemas["dim_produit"]:
        result["warnings"].append(
            f"{label} label usage skipped: dim_produit automobile join is unavailable."
        )
        return result

    sources: list[sql.Composable] = []
    skipped_sources: list[str] = []
    for fact_table, fact_alias in (
        ("fact_prime", "fp"),
        ("fact_sinistre", "fs"),
    ):
        fact_columns = schemas[fact_table]
        if not fact_columns:
            skipped_sources.append(f"{fact_table} missing")
            continue
        missing = _missing_required_columns(
            {
                fact_table: (fact_columns, ("produit_sk", key_column)),
            }
        )
        if missing:
            skipped_sources.extend(missing)
            continue

        sources.append(
            sql.SQL(
                """
                SELECT {}.{} AS dimension_sk, COUNT(*) AS row_count
                FROM {} AS {}
                JOIN {} AS dp
                  ON {}.produit_sk = dp.produit_sk
                WHERE {}
                  AND {}.{} IS NOT NULL
                GROUP BY {}.{}
                """
            ).format(
                sql.Identifier(fact_alias),
                sql.Identifier(key_column),
                _table_ref(fact_table),
                sql.Identifier(fact_alias),
                _table_ref("dim_produit"),
                sql.Identifier(fact_alias),
                _auto_product_condition(product_config, "dp"),
                sql.Identifier(fact_alias),
                sql.Identifier(key_column),
                sql.Identifier(fact_alias),
                sql.Identifier(key_column),
            )
        )
        result["sources"].append(fact_table)

    if skipped_sources:
        result["warnings"].append(
            f"{label} usage skipped sources: {', '.join(skipped_sources)}."
        )
    if not sources:
        result["warnings"].append(f"No automobile {label} usage source is queryable.")
        return result

    code_column = _detect_column(dim_columns, code_candidates)
    label_column = _detect_column(dim_columns, label_candidates)
    result["code_column"] = code_column
    result["label_column"] = label_column
    if not code_column:
        result["warnings"].append(
            f"{dimension_table} has no recognized {label} code column; using {key_column}."
        )
    if not label_column:
        result["warnings"].append(
            f"{dimension_table} has no recognized {label} label column; "
            "missing-label count is not evaluated."
        )
        result["missing_label_count"] = "N/A"

    usage_cte = _portfolio_usage_cte(sources)
    code_expr = _dimension_code_or_sk(
        dimension_alias,
        "gu",
        code_column,
        "dimension_sk",
        label.upper(),
    )

    counts_query = sql.SQL(
        """
        WITH {}
        SELECT
            COUNT(*) AS distinct_used_count,
            {} AS missing_label_count
        FROM grouped_usage AS gu
        LEFT JOIN {} AS {}
          ON gu.dimension_sk = {}.{}
        """
    ).format(
        usage_cte,
        _row_missing_count_sql(dimension_alias, label_column),
        _table_ref(dimension_table),
        sql.Identifier(dimension_alias),
        sql.Identifier(dimension_alias),
        sql.Identifier(key_column),
    )
    counts = _fetch_one_dict(cur, counts_query)
    result["distinct_used_count"] = counts["distinct_used_count"]
    if label_column:
        result["missing_label_count"] = counts["missing_label_count"]

    missing_filter = (
        _missing_text_condition(dimension_alias, label_column)
        if label_column
        else sql.SQL("TRUE")
    )
    top_query = sql.SQL(
        """
        WITH {}
        SELECT
            {} AS code,
            {} AS label,
            gu.row_count AS usage_rows,
            {} AS label_status
        FROM grouped_usage AS gu
        LEFT JOIN {} AS {}
          ON gu.dimension_sk = {}.{}
        WHERE {}
        ORDER BY usage_rows DESC, code
        LIMIT 50
        """
    ).format(
        usage_cte,
        code_expr,
        _label_display_sql(dimension_alias, label_column),
        _label_status_sql(dimension_alias, label_column),
        _table_ref(dimension_table),
        sql.Identifier(dimension_alias),
        sql.Identifier(dimension_alias),
        sql.Identifier(key_column),
        missing_filter,
    )
    result["top_missing_rows"] = _fetch_dicts(cur, top_query)

    if _positive_count(result["missing_label_count"]):
        result["warnings"].append(
            f"Automobile portfolio uses {label} rows with missing labels."
        )

    return result


def _build_report(results: dict[str, Any]) -> Report:
    report = Report()
    report.title(
        "IRISv2 Automobile Reference Label Diagnostic",
        results["generated_at"],
    )

    summary = results["summary"]
    report.section("1. Executive Summary")
    for label in (
        "auto_product_count",
        "auto_product_missing_label_count",
        "auto_prime_rows",
        "auto_sinistre_rows",
        "auto_garantie_missing_label_count",
        "auto_cause_missing_label_count",
        "auto_intermediaire_missing_label_count",
        "auto_delegation_missing_label_count",
        "validation_status",
    ):
        report.metric(label, summary[label])

    report.section("2. Schema Discovery")
    config = results["product_config"]
    report.table(
        [
            {
                "table": table,
                "exists": bool(columns),
                "detected_code_column": _detected_code_column(table, results),
                "detected_label_column": _detected_label_column(table, results),
                "available_columns": ", ".join(sorted(columns)),
            }
            for table, columns in results["schemas"].items()
        ],
        [
            "table",
            "exists",
            "detected_code_column",
            "detected_label_column",
            "available_columns",
        ],
    )
    if config.get("code_column_source") == "compatibility":
        report.bullets(
            [
                (
                    "Product code was detected through a compatibility alias "
                    f"(`{config['code_column']}`), not the primary requested "
                    "candidate list."
                )
            ]
        )

    product = results["sections"]["dim_produit"]
    report.section("3. dim_produit Automobile Labels")
    report.metric("total_product_rows_excluding_unknown", product["total_product_rows"])
    report.metric("auto_product_rows", product["auto_product_count"])
    report.metric(
        "auto_product_missing_label_rows",
        product["auto_product_missing_label_count"],
    )
    report.metric("product_code_column", config["code_column"] or "N/A")
    report.metric("product_label_column", config["label_column"] or "N/A")
    report.table(
        product["missing_label_rows"],
        ["product_code", "product_label", "label_status"],
    )

    prime = results["sections"]["fact_prime"]
    report.section("4. fact_prime Automobile Usage")
    report.metric("total_prime_rows", prime["total_rows"])
    report.metric("auto_prime_rows", prime["auto_rows"])
    report.metric(
        "auto_prime_rows_with_missing_product_label",
        prime["missing_product_label_rows"],
    )
    report.table(
        prime["top_product_rows"],
        ["product_code", "product_label", "row_count", "label_status"],
    )

    sinistre = results["sections"]["fact_sinistre"]
    report.section("5. fact_sinistre Automobile Usage")
    report.metric("total_sinistre_rows", sinistre["total_rows"])
    report.metric("auto_sinistre_rows", sinistre["auto_rows"])
    report.metric(
        "auto_sinistre_rows_with_missing_product_label",
        sinistre["missing_product_label_rows"],
    )
    report.table(
        sinistre["top_product_rows"],
        ["product_code", "product_label", "row_count", "label_status"],
    )

    garantie = results["sections"]["dim_garantie"]
    report.section("6. dim_garantie Labels Used In Automobile Sinistres")
    report.metric("garantie_code_column", garantie["code_column"] or "N/A")
    report.metric("garantie_label_column", garantie["label_column"] or "N/A")
    report.metric("distinct_garantie_codes_used", garantie["distinct_code_count"])
    report.metric("garantie_missing_label_count", garantie["missing_label_count"])
    report.table(
        garantie["top_rows"],
        ["garantie_code", "garantie_label", "row_count", "label_status"],
    )

    cause = results["sections"]["dim_cause_sinistre"]
    report.section("7. dim_cause_sinistre Labels Used In Automobile Sinistres")
    report.metric("cause_code_column", cause["code_column"] or "N/A")
    report.metric("cause_label_column", cause["label_column"] or "N/A")
    report.metric(
        "sous_nature_label_column",
        cause["sous_nature_label_column"] or "N/A",
    )
    report.metric("distinct_cause_codes_used", cause["distinct_code_count"])
    report.metric("cause_missing_label_count", cause["missing_cause_label_count"])
    report.metric(
        "sous_nature_missing_label_count",
        cause["missing_sous_nature_label_count"],
    )
    report.table(
        cause["top_rows"],
        [
            "cause_code",
            "nature_code",
            "sous_nature_code",
            "cause_label",
            "sous_nature_label",
            "row_count",
            "cause_label_status",
            "sous_nature_label_status",
        ],
    )

    intermediaire = results["sections"]["dim_intermediaire"]
    delegation = results["sections"]["dim_delegation"]
    report.section("8. Intermediaire And Delegation Automobile Portfolio Labels")
    report.subsection("dim_intermediaire")
    report.metric("sources", ", ".join(intermediaire["sources"]) or "N/A")
    report.metric("intermediaire_code_column", intermediaire["code_column"] or "N/A")
    report.metric("intermediaire_label_column", intermediaire["label_column"] or "N/A")
    report.metric("distinct_intermediaire_used", intermediaire["distinct_used_count"])
    report.metric(
        "intermediaire_missing_label_count",
        intermediaire["missing_label_count"],
    )
    report.table(
        intermediaire["top_missing_rows"],
        ["code", "label", "usage_rows", "label_status"],
    )

    report.subsection("dim_delegation")
    report.metric("sources", ", ".join(delegation["sources"]) or "N/A")
    report.metric("delegation_code_column", delegation["code_column"] or "N/A")
    report.metric("delegation_label_column", delegation["label_column"] or "N/A")
    report.metric("distinct_delegation_used", delegation["distinct_used_count"])
    report.metric("delegation_missing_label_count", delegation["missing_label_count"])
    report.table(
        delegation["top_missing_rows"],
        ["code", "label", "usage_rows", "label_status"],
    )

    report.section("9. Recommendations")
    for section_name, values in results["recommendations"].items():
        report.subsection(section_name)
        report.bullets(values)

    report.section("10. Warnings And Failures")
    report.subsection("Failures")
    report.bullets(results["failures"])
    report.subsection("Warnings")
    report.bullets(results["warnings"])

    return report


def _recommendations(sections: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    safe: list[str] = []
    needs_reference: list[str] = []
    ambiguous: list[str] = []
    out_of_scope = [
        "Product codes outside prefix `5` are intentionally excluded.",
        "No scoring, mart, loader, or warehouse correction is part of this diagnostic.",
    ]

    product = sections["dim_produit"]
    if _positive_count(product["auto_product_missing_label_count"]):
        safe.append(
            "Automobile dim_produit labels can be enriched at product grain "
            "when a trusted product-code label source is available."
        )

    for name, section, count_key in (
        ("dim_garantie", sections["dim_garantie"], "missing_label_count"),
        ("dim_cause_sinistre", sections["dim_cause_sinistre"], "missing_cause_label_count"),
        ("dim_intermediaire", sections["dim_intermediaire"], "missing_label_count"),
        ("dim_delegation", sections["dim_delegation"], "missing_label_count"),
    ):
        if section.get("label_column") is None:
            needs_reference.append(
                f"{name} needs a label/reference file or target label column "
                "before enrichment can be evaluated."
            )
        elif _positive_count(section.get(count_key)):
            needs_reference.append(
                f"{name} has automobile usage with missing labels; enrich from "
                "a governed reference file, not from fact free text."
            )

    if sections["dim_cause_sinistre"].get("sous_nature_label_column") is None:
        ambiguous.append(
            "Sous-nature label enrichment cannot be evaluated because no "
            "sous-nature label column was detected."
        )

    if not safe:
        safe.append("No immediate in-place label enrichment candidate was detected.")
    if not needs_reference:
        needs_reference.append("No missing reference-label source need was detected.")
    if not ambiguous:
        ambiguous.append("No ambiguous-grain blocker was detected for the checks run.")

    return {
        "Safe To Enrich Now": safe,
        "Needs Reference File": needs_reference,
        "Cannot Enrich Due To Ambiguous Grain": ambiguous,
        "Not In Automobile Perimeter": out_of_scope,
    }


def _validation_status(
    summary: dict[str, Any],
    warnings: list[str],
    failures: list[str],
) -> str:
    if failures:
        return "FAIL"

    missing_count_keys = (
        "auto_product_missing_label_count",
        "auto_garantie_missing_label_count",
        "auto_cause_missing_label_count",
        "auto_intermediaire_missing_label_count",
        "auto_delegation_missing_label_count",
    )
    if warnings or any(_positive_count(summary[key]) for key in missing_count_keys):
        return "WARNING"
    return "OK"


def _load_table_columns(cur: Any) -> dict[str, set[str]]:
    return {table: _get_table_columns(cur, table) for table in TABLES}


def _get_table_columns(cur: Any, table_name: str) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position
        """,
        (TARGET_SCHEMA, table_name),
    )
    return {row[0] for row in cur.fetchall()}


def _product_config(columns: set[str]) -> dict[str, Any]:
    code_column = _detect_column(columns, PRODUCT_CODE_CANDIDATES)
    code_column_source = "requested"
    if code_column is None:
        code_column = _detect_column(columns, PRODUCT_CODE_COMPATIBILITY_CANDIDATES)
        code_column_source = "compatibility" if code_column else None

    return {
        "code_column": code_column,
        "code_column_source": code_column_source,
        "label_column": _detect_column(columns, PRODUCT_LABEL_CANDIDATES),
        "sk_column": "produit_sk" if "produit_sk" in columns else None,
        "natural_key_column": (
            "produit_natural_key" if "produit_natural_key" in columns else None
        ),
    }


def _detect_column(columns: set[str], candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def _missing_required_columns(
    requirements: dict[str, tuple[set[str], tuple[str, ...]]],
) -> list[str]:
    missing: list[str] = []
    for table_name, (columns, required_columns) in requirements.items():
        table_missing = [column for column in required_columns if column not in columns]
        if table_missing:
            missing.append(f"{table_name} missing {', '.join(table_missing)}")
    return missing


def _empty_result(**values: Any) -> dict[str, Any]:
    return {"warnings": [], "failures": [], **values}


def _table_ref(table_name: str) -> sql.Composed:
    return sql.SQL("{}.{}").format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(table_name),
    )


def _column(alias: str, column_name: str) -> sql.Composed:
    return sql.SQL("{}.{}").format(sql.Identifier(alias), sql.Identifier(column_name))


def _trim_text(alias: str, column_name: str) -> sql.Composed:
    return sql.SQL("btrim({}::text)").format(_column(alias, column_name))


def _nullable_text(alias: str, column_name: str | None) -> sql.Composable:
    if not column_name:
        return sql.SQL("NULL::text")
    return sql.SQL("NULLIF({}, '')").format(_trim_text(alias, column_name))


def _missing_text_condition(alias: str, column_name: str) -> sql.Composed:
    trimmed = _trim_text(alias, column_name)
    markers = sql.SQL(", ").join(sql.Literal(marker) for marker in MISSING_LABEL_MARKERS)
    return sql.SQL(
        "({column} IS NULL OR {trimmed} = '' OR upper({trimmed}) IN ({markers}))"
    ).format(
        column=_column(alias, column_name),
        trimmed=trimmed,
        markers=markers,
    )


def _label_display_sql(alias: str, column_name: str | None) -> sql.Composable:
    if not column_name:
        return sql.SQL("NULL::text")
    return sql.SQL("NULLIF({}, '')").format(_trim_text(alias, column_name))


def _label_status_sql(alias: str, column_name: str | None) -> sql.Composable:
    if not column_name:
        return sql.Literal("NO_LABEL_COLUMN")
    return sql.SQL(
        "CASE WHEN {} THEN 'MISSING_LABEL' ELSE 'OK' END"
    ).format(_missing_text_condition(alias, column_name))


def _distinct_missing_count_sql(
    code_expr: sql.Composable,
    alias: str,
    label_column: str | None,
) -> sql.Composable:
    if not label_column:
        return sql.SQL("NULL::integer")
    return sql.SQL("COUNT(DISTINCT {}) FILTER (WHERE {})").format(
        code_expr,
        _missing_text_condition(alias, label_column),
    )


def _row_missing_count_sql(alias: str, label_column: str | None) -> sql.Composable:
    if not label_column:
        return sql.SQL("NULL::integer")
    return sql.SQL("COUNT(*) FILTER (WHERE {})").format(
        _missing_text_condition(alias, label_column)
    )


def _dimension_code_or_sk(
    dimension_alias: str,
    fact_or_usage_alias: str,
    code_column: str | None,
    sk_column: str,
    label: str,
) -> sql.Composable:
    fallback = sql.SQL("CONCAT({}, {}.{}, {})").format(
        sql.Literal(f"<{label}_SK:"),
        sql.Identifier(fact_or_usage_alias),
        sql.Identifier(sk_column),
        sql.Literal(">"),
    )
    if not code_column:
        return fallback
    return sql.SQL("COALESCE(NULLIF({}, ''), {})").format(
        _trim_text(dimension_alias, code_column),
        fallback,
    )


def _product_not_unknown_condition(config: dict[str, Any], alias: str) -> sql.Composable:
    conditions: list[sql.Composable] = []
    if config["sk_column"]:
        conditions.append(
            sql.SQL("{} <> 0").format(_column(alias, config["sk_column"]))
        )

    for column_name in (config["code_column"], config["natural_key_column"]):
        if column_name:
            conditions.append(
                sql.SQL("({column} IS NULL OR upper({trimmed}) <> 'UNKNOWN')").format(
                    column=_column(alias, column_name),
                    trimmed=_trim_text(alias, column_name),
                )
            )

    if not conditions:
        return sql.SQL("TRUE")
    return sql.SQL(" AND ").join(conditions)


def _auto_product_condition(config: dict[str, Any], alias: str) -> sql.Composable:
    code_column = config["code_column"]
    if not code_column:
        return sql.SQL("FALSE")

    return sql.SQL(
        """
        ({not_unknown})
        AND {code_column} IS NOT NULL
        AND {trimmed_code} <> ''
        AND {trimmed_code} LIKE {prefix}
        """
    ).format(
        not_unknown=_product_not_unknown_condition(config, alias),
        code_column=_column(alias, code_column),
        trimmed_code=_trim_text(alias, code_column),
        prefix=sql.Literal(f"{AUTO_PRODUCT_PREFIX}%"),
    )


def _portfolio_usage_cte(sources: list[sql.Composable]) -> sql.Composed:
    return sql.SQL(
        """
        auto_usage AS (
            {}
        ),
        grouped_usage AS (
            SELECT dimension_sk, SUM(row_count) AS row_count
            FROM auto_usage
            GROUP BY dimension_sk
        )
        """
    ).format(sql.SQL(" UNION ALL ").join(sources))


def _fetch_scalar(cur: Any, query: sql.Composable) -> Any:
    cur.execute(query)
    value = cur.fetchone()[0]
    if isinstance(value, int):
        return value
    return int(value) if value is not None else 0


def _fetch_one_dict(cur: Any, query: sql.Composable) -> dict[str, Any]:
    rows = _fetch_dicts(cur, query)
    if not rows:
        return {}
    return rows[0]


def _fetch_dicts(cur: Any, query: sql.Composable) -> list[dict[str, Any]]:
    cur.execute(query)
    columns = [description.name for description in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def _positive_count(value: Any) -> bool:
    return isinstance(value, int) and value > 0


def _detected_code_column(table: str, results: dict[str, Any]) -> Any:
    if table == "dim_produit":
        return results["product_config"]["code_column"] or ""
    section = results["sections"].get(table)
    if not section:
        return ""
    return section.get("code_column", "")


def _detected_label_column(table: str, results: dict[str, Any]) -> Any:
    if table == "dim_produit":
        return results["product_config"]["label_column"] or ""
    section = results["sections"].get(table)
    if not section:
        return ""
    return section.get("label_column", "")


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


def _display_value(value: Any) -> str:
    if value is None:
        return ""
    if value == "N/A":
        return "N/A"
    if pd.isna(value):
        return ""
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _markdown_cell(value: Any) -> str:
    return _display_value(value).replace("|", "\\|").replace("\n", " ")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Diagnose automobile reference labels in iris_dw without modifying data."
        )
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
