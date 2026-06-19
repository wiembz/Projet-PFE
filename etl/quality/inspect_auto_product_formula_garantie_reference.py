from __future__ import annotations

import argparse
import re
import sys
import unicodedata
import warnings
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
GARANTIE_REFERENCE_FILE = REFERENCE_DIR / "correspondance garantie.xlsx"
REPORT_PATH = PROJECT_ROOT / "docs" / "auto_product_formula_garantie_reference_inspection.md"
TARGET_SCHEMA = "iris_dw"
TARGET_TABLE = "dim_produit"
AUTO_PRODUCT_PREFIX = "5"

TARGET_GARANTIE_CODES = (
    "CAS",
    "RCM",
    "IDA",
    "BG",
    "REM",
    "ASR",
    "RCC",
    "TR",
    "RCDE",
    "DOC",
    "INC",
    "DEPC",
    "VOL",
    "EXT",
    "DEPA",
    "RCR",
    "RCA",
    "CONS",
    "IC",
    "DC",
    "FM",
    "CAT",
    "EME",
    "IPT",
    "IND",
)
SPECIFIC_TARGET_CODES = ("REM", "DEPC", "EXT", "DEPA")

KNOWN_GARANTIE_COLUMNS = ("CODPROD", "CODFORMU", "GRNTSINI", "CODGRNT", "LIBGRNSIN")
FORMULA_LABEL_CANDIDATE_TOKENS = (
    "FORM",
    "FORMU",
    "FORMULE",
    "LIBFORM",
    "LIBFORMU",
    "LIBELLE_FORMULE",
)
CODE_COLUMN_KEYWORDS = ("code", "cod", "prod", "form", "formu", "grnt", "garantie")
LABEL_COLUMN_KEYWORDS = ("lib", "label", "libelle", "designation", "desc", "nom")
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}


warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default",
    category=UserWarning,
    module="openpyxl.styles.stylesheet",
)


@dataclass(frozen=True)
class SheetInspection:
    file_path: Path
    sheet_name: str
    row_count: int
    columns: tuple[str, ...]
    code_columns: tuple[str, ...]
    label_columns: tuple[str, ...]
    dataframe: pd.DataFrame


class Report:
    def __init__(self) -> None:
        self.console_lines: list[str] = []
        self.markdown_lines: list[str] = []

    def title(self, text: str, generated_at: str) -> None:
        self.console_lines.extend(["=" * 100, text, f"Generated at: {generated_at}", "=" * 100])
        self.markdown_lines.extend(
            [
                f"# {text}",
                "",
                f"Generated at: {generated_at}",
                "",
                (
                    "This inspection is read-only. It reads local reference Excel files "
                    "and `iris_dw.dim_produit`; it does not update PostgreSQL, modify "
                    "`iris_dw`, Silver, loaders, scoring, marts, or orchestration, and "
                    "it does not create or alter tables."
                ),
                "",
                "Automobile perimeter: `CODPROD` / `code_produit` starts with `5`.",
                "",
            ]
        )

    def section(self, text: str) -> None:
        self.console_lines.extend(["", "-" * 100, text])
        self.markdown_lines.extend(["", f"## {text}", ""])

    def metric(self, label: str, value: Any) -> None:
        self.console_lines.append(f"{label}: {_display_value(value)}")
        self.markdown_lines.append(f"- {label}: `{_display_value(value)}`")

    def table(self, rows: list[dict[str, Any]], columns: list[str]) -> None:
        if not rows:
            self.console_lines.append("No rows.")
            self.markdown_lines.append("No rows.")
            return
        frame = pd.DataFrame(rows, columns=columns)
        frame = frame.astype(object).where(pd.notna(frame), "")
        self.console_lines.append(frame.to_string(index=False))
        self.markdown_lines.extend(_rows_to_markdown(frame.to_dict(orient="records"), columns))

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
    args = _parse_args()
    report_path = _resolve_project_path(args.report_path)
    results = inspect_auto_product_formula_garantie_reference()
    report = _build_report(results)

    print(report.render_console())
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report.render_markdown(), encoding="utf-8")
    print(f"\n[OK] Markdown inspection written to {report_path}")
    print(f"validation_status: {results['summary']['validation_status']}")


def inspect_auto_product_formula_garantie_reference() -> dict[str, Any]:
    generated_at = datetime.now().isoformat(timespec="seconds")
    warnings_list: list[str] = []
    failures: list[str] = []

    excel_files = sorted(REFERENCE_DIR.glob("*.xlsx"))
    sheets = _inspect_reference_files(excel_files, warnings_list)
    garantie_sheet = _select_garantie_sheet(sheets)

    if not excel_files:
        failures.append(f"No Excel reference files found under {_relative_to_project(REFERENCE_DIR)}")
    if garantie_sheet is None:
        failures.append(f"Guarantee reference workbook not readable: {_relative_to_project(GARANTIE_REFERENCE_FILE)}")

    garantie_df = (
        _prepared_garantie_dataframe(garantie_sheet)
        if garantie_sheet
        else pd.DataFrame(columns=KNOWN_GARANTIE_COLUMNS)
    )
    auto_ref = _auto_reference_rows(garantie_df)
    product_formula_candidates = _product_formula_candidates(sheets)
    formula_label_columns = sorted(
        {
            row["formula_label_columns"]
            for row in product_formula_candidates
            if row["formula_label_columns"]
        }
    )
    formula_label_source_status = (
        "available:" + ",".join(formula_label_columns)
        if formula_label_columns
        else "formula_label_source_missing"
    )
    if not formula_label_columns:
        warnings_list.append("formula_label_source_missing")

    dim_result = _inspect_dim_produit(auto_ref, warnings_list, failures)
    grain_results = _garantie_grain_stability(auto_ref)
    safest_grain = _safest_grain(grain_results)
    missing_target_rows = _missing_target_code_rows(auto_ref)

    if safest_grain and safest_grain["duplicate_conflicting_label_count"]:
        warnings_list.append("Safest garantie mapping grain still has conflicting labels.")
    if any(row["status"] == "not_found_in_reference" for row in missing_target_rows):
        warnings_list.append("At least one requested target code is absent from GRNTSINI and CODGRNT.")

    summary = {
        "auto_reference_rows": len(auto_ref),
        "distinct_auto_codprod": _distinct_count(auto_ref, ["CODPROD"]),
        "distinct_auto_codprod_codformu": _distinct_count(auto_ref, ["CODPROD", "CODFORMU"]),
        "formula_label_source_status": formula_label_source_status,
        "safest_garantie_mapping_grain": safest_grain["grain"] if safest_grain else "N/A",
        "safest_grain_conflicting_count": (
            safest_grain["duplicate_conflicting_label_count"] if safest_grain else "N/A"
        ),
        "missing_target_codes": ", ".join(
            row["target_code"]
            for row in missing_target_rows
            if row["status"] == "not_found_in_reference"
        )
        or "none",
    }
    summary["validation_status"] = _validation_status(failures, warnings_list)

    return {
        "generated_at": generated_at,
        "excel_files": excel_files,
        "sheets": sheets,
        "garantie_reference_file": GARANTIE_REFERENCE_FILE,
        "auto_ref": auto_ref,
        "product_formula_candidates": product_formula_candidates,
        "formula_label_columns": formula_label_columns,
        "dim_result": dim_result,
        "grain_results": grain_results,
        "safest_grain": safest_grain,
        "missing_target_rows": missing_target_rows,
        "summary": summary,
        "warnings": warnings_list,
        "failures": failures,
    }


def _inspect_reference_files(files: list[Path], warnings_list: list[str]) -> list[SheetInspection]:
    inspections: list[SheetInspection] = []
    for file_path in files:
        try:
            with pd.ExcelFile(file_path, engine="openpyxl") as workbook:
                for sheet_name in workbook.sheet_names:
                    dataframe = _read_sheet(workbook, file_path.name, sheet_name)
                    columns = tuple(str(column).strip() for column in dataframe.columns)
                    dataframe.columns = columns
                    inspections.append(
                        SheetInspection(
                            file_path=file_path,
                            sheet_name=sheet_name,
                            row_count=len(dataframe),
                            columns=columns,
                            code_columns=tuple(_candidate_code_columns(columns)),
                            label_columns=tuple(_candidate_label_columns(columns)),
                            dataframe=dataframe,
                        )
                    )
        except Exception as exc:  # pragma: no cover - defensive inventory path
            warnings_list.append(f"Could not read {_relative_to_project(file_path)}: {exc}")
    return inspections


def _read_sheet(workbook: pd.ExcelFile, file_name: str, sheet_name: str) -> pd.DataFrame:
    if file_name.casefold() == GARANTIE_REFERENCE_FILE.name.casefold():
        first = pd.read_excel(workbook, sheet_name=sheet_name, dtype=object, engine="openpyxl")
        cleaned = [_clean_column_name(column) for column in first.columns]
        if {"CODPROD", "CODFORMU", "GRNTSINI", "CODGRNT", "LIBGRNSIN"}.issubset(cleaned):
            first.columns = cleaned
            return first
        fallback = pd.read_excel(
            workbook,
            sheet_name=sheet_name,
            dtype=object,
            header=None,
            engine="openpyxl",
        )
        fallback.columns = _known_or_generic_columns(len(fallback.columns))
        return fallback

    dataframe = pd.read_excel(workbook, sheet_name=sheet_name, dtype=object, engine="openpyxl")
    dataframe.columns = [_clean_header(column, index) for index, column in enumerate(dataframe.columns, 1)]
    return dataframe


def _select_garantie_sheet(sheets: list[SheetInspection]) -> SheetInspection | None:
    garantie_sheets = [
        sheet
        for sheet in sheets
        if sheet.file_path.name.casefold() == GARANTIE_REFERENCE_FILE.name.casefold()
    ]
    if not garantie_sheets:
        return None
    return max(garantie_sheets, key=lambda sheet: len(set(KNOWN_GARANTIE_COLUMNS) & set(sheet.columns)))


def _prepared_garantie_dataframe(sheet: SheetInspection) -> pd.DataFrame:
    dataframe = sheet.dataframe.copy()
    rename = {_clean_column_name(column): column for column in dataframe.columns}
    for column in KNOWN_GARANTIE_COLUMNS:
        if column not in dataframe.columns and column in rename:
            dataframe[column] = dataframe[rename[column]]
    for column in KNOWN_GARANTIE_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = pd.NA
        dataframe[column] = dataframe[column].map(_normalize_code if column != "LIBGRNSIN" else _normalize_label)
    return dataframe


def _auto_reference_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe.copy()
    codprod = dataframe["CODPROD"].fillna("").astype(str)
    return dataframe[codprod.str.startswith(AUTO_PRODUCT_PREFIX, na=False)].copy()


def _inspect_dim_produit(
    auto_ref: pd.DataFrame,
    warnings_list: list[str],
    failures: list[str],
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "available": False,
        "auto_product_rows": "N/A",
        "code_formule_null_rows": "N/A",
        "dim_pairs_not_found_in_reference": "N/A",
        "reference_pairs_not_represented_in_dim": "N/A",
        "columns": [],
        "missing_reference_pair_examples": [],
        "reference_pair_gap_examples": [],
    }

    try:
        conn = get_connection()
    except Exception as exc:
        warnings_list.append(f"Could not connect to PostgreSQL for iris_dw.dim_produit inspection: {exc}")
        return result

    try:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            columns = _get_dim_produit_columns(cur)
            result["columns"] = sorted(columns)
            required = {"code_produit", "code_formule"}
            if "code_produit" not in columns:
                failures.append("iris_dw.dim_produit is missing required column code_produit")
                return result
            result["available"] = True
            rows = _fetch_dim_produit_rows(cur, columns)
    finally:
        conn.close()

    dim_df = pd.DataFrame(rows)
    if dim_df.empty:
        result.update(
            auto_product_rows=0,
            code_formule_null_rows=0,
            dim_pairs_not_found_in_reference=0,
            reference_pairs_not_represented_in_dim=_distinct_count(auto_ref, ["CODPROD", "CODFORMU"]),
        )
        return result

    dim_df["code_produit"] = dim_df["code_produit"].map(_normalize_code)
    dim_df["code_formule"] = dim_df["code_formule"].map(_normalize_code) if "code_formule" in dim_df else pd.NA
    auto_dim = dim_df[dim_df["code_produit"].fillna("").str.startswith(AUTO_PRODUCT_PREFIX, na=False)].copy()
    ref_pairs = _pair_set(auto_ref, "CODPROD", "CODFORMU")
    dim_pairs = _pair_set(auto_dim, "code_produit", "code_formule")

    formula_exists = auto_dim["code_formule"].notna() & (auto_dim["code_formule"] != "")
    dim_pair_gaps = sorted(dim_pairs - ref_pairs)
    ref_pair_gaps = sorted(ref_pairs - dim_pairs)
    result.update(
        auto_product_rows=len(auto_dim),
        code_formule_null_rows=int((~formula_exists).sum()),
        dim_pairs_not_found_in_reference=len(dim_pair_gaps),
        reference_pairs_not_represented_in_dim=len(ref_pair_gaps),
        missing_reference_pair_examples=[f"{left}/{right}" for left, right in dim_pair_gaps[:25]],
        reference_pair_gap_examples=[f"{left}/{right}" for left, right in ref_pair_gaps[:25]],
    )
    return result


def _get_dim_produit_columns(cur: Any) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position
        """,
        (TARGET_SCHEMA, TARGET_TABLE),
    )
    return {row[0] for row in cur.fetchall()}


def _fetch_dim_produit_rows(cur: Any, columns: set[str]) -> list[dict[str, Any]]:
    selected = ["code_produit"]
    if "code_formule" in columns:
        selected.append("code_formule")
    else:
        selected.append("NULL::text AS code_formule")
    query = sql.SQL("SELECT {} FROM {}.{}").format(
        sql.SQL(", ").join(
            sql.SQL(item) if " AS " in item else sql.Identifier(item) for item in selected
        ),
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
    )
    cur.execute(query)
    names = [description.name for description in cur.description]
    return [dict(zip(names, row)) for row in cur.fetchall()]


def _garantie_grain_stability(auto_ref: pd.DataFrame) -> list[dict[str, Any]]:
    grains = [
        ("GRNTSINI", ["GRNTSINI"]),
        ("CODPROD + GRNTSINI", ["CODPROD", "GRNTSINI"]),
        ("CODPROD + CODFORMU + GRNTSINI", ["CODPROD", "CODFORMU", "GRNTSINI"]),
        (
            "CODPROD + CODFORMU + CODGRNT + GRNTSINI",
            ["CODPROD", "CODFORMU", "CODGRNT", "GRNTSINI"],
        ),
    ]
    return [_evaluate_grain(auto_ref, grain_name, columns) for grain_name, columns in grains]


def _evaluate_grain(auto_ref: pd.DataFrame, grain_name: str, columns: list[str]) -> dict[str, Any]:
    if auto_ref.empty:
        return _grain_result(grain_name, columns, 0, len(TARGET_GARANTIE_CODES), 0, 0, 0, 0)

    target_set = set(TARGET_GARANTIE_CODES)
    target_rows = auto_ref[auto_ref["GRNTSINI"].isin(target_set)].copy()
    matched_count = int(target_rows["GRNTSINI"].dropna().nunique())
    missing_count = len(target_set - set(target_rows["GRNTSINI"].dropna()))

    unique_label_count = 0
    duplicate_same_label_count = 0
    duplicate_conflicting_label_count = 0
    safe_mapping_count = 0
    if not target_rows.empty:
        grouped = target_rows.groupby(columns, dropna=False)
        for _, group in grouped:
            labels = {_label_key(value) for value in group["LIBGRNSIN"].dropna() if _normalize_label(value)}
            if len(labels) == 1:
                safe_mapping_count += 1
                if len(group) == 1:
                    unique_label_count += 1
                else:
                    duplicate_same_label_count += 1
            elif len(labels) > 1:
                duplicate_conflicting_label_count += 1

    return _grain_result(
        grain_name,
        columns,
        matched_count,
        missing_count,
        unique_label_count,
        duplicate_same_label_count,
        duplicate_conflicting_label_count,
        safe_mapping_count,
    )


def _grain_result(
    grain_name: str,
    columns: list[str],
    matched_count: int,
    missing_count: int,
    unique_label_count: int,
    duplicate_same_label_count: int,
    duplicate_conflicting_label_count: int,
    safe_mapping_count: int,
) -> dict[str, Any]:
    return {
        "grain": grain_name,
        "grain_columns": ", ".join(columns),
        "target_code_count": len(TARGET_GARANTIE_CODES),
        "matched_count": matched_count,
        "missing_count": missing_count,
        "unique_label_count": unique_label_count,
        "duplicate_same_label_count": duplicate_same_label_count,
        "duplicate_conflicting_label_count": duplicate_conflicting_label_count,
        "safe_mapping_count": safe_mapping_count,
    }


def _safest_grain(grain_results: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not grain_results:
        return None
    return sorted(
        grain_results,
        key=lambda row: (
            row["duplicate_conflicting_label_count"],
            row["missing_count"],
            -row["matched_count"],
            -row["safe_mapping_count"],
        ),
    )[0]


def _missing_target_code_rows(auto_ref: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for code in SPECIFIC_TARGET_CODES:
        matches = auto_ref[(auto_ref["GRNTSINI"] == code) | (auto_ref["CODGRNT"] == code)]
        combos = sorted(_pair_set(matches, "CODPROD", "CODFORMU"))
        status = "found" if combos else "not_found_in_reference"
        rows.append(
            {
                "target_code": code,
                "status": status,
                "grntsini_rows": int((auto_ref["GRNTSINI"] == code).sum()) if not auto_ref.empty else 0,
                "codgrnt_rows": int((auto_ref["CODGRNT"] == code).sum()) if not auto_ref.empty else 0,
                "codprod_codformu_examples": ", ".join(f"{left}/{right}" for left, right in combos[:20]),
            }
        )
    return rows


def _product_formula_candidates(sheets: list[SheetInspection]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sheet in sheets:
        product_columns = _columns_containing(sheet.columns, ("CODPROD", "CODEPRODUIT", "PRODUIT", "PRODUCT"))
        formula_columns = _columns_containing(sheet.columns, ("CODFORMU", "CODEFORMULE", "FORMULE", "FORMU"))
        formula_label_columns = _formula_label_columns(sheet.columns)
        if not (product_columns or formula_columns or formula_label_columns):
            continue
        rows.append(
            {
                "file": _relative_to_project(sheet.file_path),
                "sheet": sheet.sheet_name,
                "row_count": sheet.row_count,
                "product_code_columns": ", ".join(product_columns),
                "formula_code_columns": ", ".join(formula_columns),
                "formula_label_columns": ", ".join(formula_label_columns),
            }
        )
    return rows


def _build_report(results: dict[str, Any]) -> Report:
    report = Report()
    report.title("IRISv2 Automobile Product Formula Garantie Reference Inspection", results["generated_at"])

    report.section("1. Console Summary")
    for key in (
        "auto_reference_rows",
        "distinct_auto_codprod",
        "distinct_auto_codprod_codformu",
        "formula_label_source_status",
        "safest_garantie_mapping_grain",
        "safest_grain_conflicting_count",
        "missing_target_codes",
        "validation_status",
    ):
        report.metric(key, results["summary"][key])

    auto_ref = results["auto_ref"]
    report.metric("distinct_auto_codprod_codformu_grntsini", _distinct_count(auto_ref, ["CODPROD", "CODFORMU", "GRNTSINI"]))

    report.section("2. File Inventory")
    report.table(
        [
            {
                "file": _relative_to_project(sheet.file_path),
                "sheet": sheet.sheet_name,
                "row_count": sheet.row_count,
                "columns": ", ".join(sheet.columns),
                "candidate_code_columns": ", ".join(sheet.code_columns),
                "candidate_label_columns": ", ".join(sheet.label_columns),
            }
            for sheet in results["sheets"]
        ],
        ["file", "sheet", "row_count", "columns", "candidate_code_columns", "candidate_label_columns"],
    )

    report.section("3. Product Formula Coverage")
    report.metric("auto_reference_rows", len(auto_ref))
    report.metric("distinct_CODPROD", _distinct_count(auto_ref, ["CODPROD"]))
    report.metric("distinct_CODPROD_CODFORMU", _distinct_count(auto_ref, ["CODPROD", "CODFORMU"]))
    report.metric("distinct_CODPROD_CODFORMU_GRNTSINI", _distinct_count(auto_ref, ["CODPROD", "CODFORMU", "GRNTSINI"]))
    report.metric("formula_label_source_status", results["summary"]["formula_label_source_status"])

    report.section("4. Product Formula Reference Candidates")
    report.table(
        results["product_formula_candidates"],
        [
            "file",
            "sheet",
            "row_count",
            "product_code_columns",
            "formula_code_columns",
            "formula_label_columns",
        ],
    )

    dim = results["dim_result"]
    report.section("5. iris_dw.dim_produit Comparison")
    report.metric("dim_produit_available", dim["available"])
    report.metric("auto_product_rows_code_produit_starts_5", dim["auto_product_rows"])
    report.metric("code_formule_null_rows", dim["code_formule_null_rows"])
    report.metric("code_formule_exists_but_no_reference_pair", dim["dim_pairs_not_found_in_reference"])
    report.metric("reference_pairs_not_represented_in_dim_produit", dim["reference_pairs_not_represented_in_dim"])
    report.table(
        [{"gap_type": "dim_pair_not_in_reference", "pair": pair} for pair in dim["missing_reference_pair_examples"]]
        + [{"gap_type": "reference_pair_not_in_dim", "pair": pair} for pair in dim["reference_pair_gap_examples"]],
        ["gap_type", "pair"],
    )

    report.section("6. Guarantee Label Stability By Grain")
    report.table(
        results["grain_results"],
        [
            "grain",
            "target_code_count",
            "matched_count",
            "missing_count",
            "unique_label_count",
            "duplicate_same_label_count",
            "duplicate_conflicting_label_count",
            "safe_mapping_count",
        ],
    )

    report.section("7. Missing Target Codes")
    report.table(
        results["missing_target_rows"],
        ["target_code", "status", "grntsini_rows", "codgrnt_rows", "codprod_codformu_examples"],
    )

    report.section("8. Warnings And Failures")
    report.table(
        [{"type": "FAILURE", "message": message} for message in results["failures"]]
        + [{"type": "WARNING", "message": message} for message in results["warnings"]],
        ["type", "message"],
    )

    return report


def _candidate_code_columns(columns: tuple[str, ...]) -> list[str]:
    result: list[str] = []
    for column in columns:
        normalized = _normalize_column_name(column)
        compact = _compact_name(normalized)
        if any(keyword in normalized or keyword in compact for keyword in CODE_COLUMN_KEYWORDS):
            result.append(column)
    return result


def _candidate_label_columns(columns: tuple[str, ...]) -> list[str]:
    result: list[str] = []
    for column in columns:
        normalized = _normalize_column_name(column)
        compact = _compact_name(normalized)
        if any(keyword in normalized or keyword in compact for keyword in LABEL_COLUMN_KEYWORDS):
            result.append(column)
    return result


def _formula_label_columns(columns: Any) -> list[str]:
    result: list[str] = []
    for column in columns:
        compact = _compact_name(_normalize_column_name(column)).upper()
        if any(_compact_name(token).upper() in compact for token in FORMULA_LABEL_CANDIDATE_TOKENS):
            if not compact.startswith("COD"):
                result.append(str(column))
    return result


def _columns_containing(columns: Any, tokens: tuple[str, ...]) -> list[str]:
    result: list[str] = []
    compact_tokens = tuple(_compact_name(token).upper() for token in tokens)
    for column in columns:
        compact = _compact_name(_normalize_column_name(column)).upper()
        if any(token in compact for token in compact_tokens):
            result.append(str(column))
    return result


def _known_or_generic_columns(column_count: int) -> tuple[str, ...]:
    if column_count <= len(KNOWN_GARANTIE_COLUMNS):
        return KNOWN_GARANTIE_COLUMNS[:column_count]
    extras = tuple(f"COLUMN_{index}" for index in range(len(KNOWN_GARANTIE_COLUMNS) + 1, column_count + 1))
    return KNOWN_GARANTIE_COLUMNS + extras


def _clean_header(column: Any, index: int) -> str:
    text = str(column).strip()
    if not text or text.lower().startswith("unnamed:"):
        return f"COLUMN_{index}"
    return text


def _clean_column_name(column: Any) -> str:
    return _compact_name(_normalize_column_name(column)).upper()


def _distinct_count(dataframe: pd.DataFrame, columns: list[str]) -> int:
    if dataframe.empty or any(column not in dataframe.columns for column in columns):
        return 0
    return len(dataframe[columns].dropna(how="any").drop_duplicates())


def _pair_set(dataframe: pd.DataFrame, left_column: str, right_column: str) -> set[tuple[str, str]]:
    if dataframe.empty or left_column not in dataframe.columns or right_column not in dataframe.columns:
        return set()
    subset = dataframe[[left_column, right_column]].copy()
    subset[left_column] = subset[left_column].map(_normalize_code)
    subset[right_column] = subset[right_column].map(_normalize_code)
    subset = subset.dropna(how="any")
    subset = subset[(subset[left_column] != "") & (subset[right_column] != "")]
    return {(str(row[left_column]), str(row[right_column])) for _, row in subset.drop_duplicates().iterrows()}


def _validation_status(failures: list[str], warnings_list: list[str]) -> str:
    if failures:
        return "FAIL"
    if warnings_list:
        return "WARNING"
    return "OK"


def _normalize_code(value: Any) -> str | None:
    text = _clean_text(value)
    if text is None:
        return None
    return re.sub(r"\s+", " ", text).upper()


def _normalize_label(value: Any) -> str | None:
    text = _clean_text(value)
    if text is None:
        return None
    return re.sub(r"\s+", " ", text)


def _clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).strip())
    if text.casefold() in NULL_MARKERS:
        return None
    return text


def _label_key(value: Any) -> str:
    label = _normalize_label(value)
    if not label:
        return ""
    return unicodedata.normalize("NFKC", label).casefold()


def _normalize_column_name(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(character for character in text if not unicodedata.combining(character))
    return re.sub(r"\s+", " ", text.strip().casefold())


def _compact_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value)


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


def _relative_to_project(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only inspection for automobile product/formula/guarantee "
            "reference coverage and mapping grain."
        )
    )
    parser.add_argument(
        "--report-path",
        default=str(REPORT_PATH),
        help="Markdown report path.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
