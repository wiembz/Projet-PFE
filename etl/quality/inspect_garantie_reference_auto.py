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


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DEFAULT_REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
PREFERRED_REFERENCE_FILE = DEFAULT_REFERENCE_DIR / "correspondance garantie.xlsx"
REPORT_PATH = PROJECT_ROOT / "docs" / "garantie_reference_auto_inspection.md"

TARGET_AUTO_GARANTIE_CODES = (
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

CODE_COLUMN_KEYWORDS = ("garantie", "code", "cod", "grnt", "grntsini")
LABEL_COLUMN_KEYWORDS = ("libelle", "label", "designation", "desc", "garantie")
LABEL_PRIMARY_KEYWORDS = ("libelle", "label", "designation", "desc")
CODE_EXACT_NAMES = {"grntsini", "codgrnt", "codegarantie", "garantiecode"}
LABEL_EXACT_NAMES = {"libgrnsin", "libgrnt", "libgarantie", "garantielibelle"}
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}

HEADERLESS_WORKBOOK_COLUMNS = {
    "correspondance garantie.xlsx": (
        "CODPROD",
        "CODFORMU",
        "GRNTSINI",
        "CODGRNT",
        "LIBGRNSIN",
        "COLUMN_6",
    ),
}


warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default",
    category=UserWarning,
    module="openpyxl.styles.stylesheet",
)


@dataclass(frozen=True)
class SheetInspection:
    sheet_name: str
    row_count: int
    columns: tuple[str, ...]
    code_columns: tuple[str, ...]
    label_columns: tuple[str, ...]
    dataframe: pd.DataFrame


@dataclass(frozen=True)
class MatchRow:
    target_code: str
    label: str
    label_key: str
    sheet_name: str
    code_column: str
    label_column: str
    excel_row_number: int


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
                    "This inspection is read-only. It reads local reference "
                    "Excel files only; it does not write to PostgreSQL, update "
                    "`iris_dw`, modify loaders, scoring, marts, or create tables."
                ),
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
    reference_file = _resolve_reference_file(args.reference_file)
    report_path = _resolve_project_path(args.report_path)

    results = inspect_garantie_reference_auto(reference_file)
    report = _build_report(results)

    print(report.render_console())
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report.render_markdown(), encoding="utf-8")
    print(f"\n[OK] Markdown inspection written to {report_path}")
    print(f"validation_status: {results['summary']['validation_status']}")


def inspect_garantie_reference_auto(reference_file: Path) -> dict[str, Any]:
    generated_at = datetime.now().isoformat(timespec="seconds")
    failures: list[str] = []
    warnings_list: list[str] = []

    if not reference_file.exists():
        failures.append(f"Reference file not found: {reference_file}")
        sheets: list[SheetInspection] = []
    else:
        sheets = _inspect_workbook(reference_file)

    if not sheets and not failures:
        failures.append(f"No sheets found in reference file: {reference_file}")

    if sheets:
        if not any(sheet.code_columns for sheet in sheets):
            failures.append("No candidate garantie code columns detected in workbook.")
        if not any(sheet.label_columns for sheet in sheets):
            failures.append("No candidate garantie label columns detected in workbook.")

    pair_summaries = _candidate_pair_summaries(sheets)
    recommended_pair = _recommended_pair(pair_summaries)
    target_results = _target_code_results(sheets, recommended_pair)

    status_counts = _status_counts(target_results)
    if recommended_pair is None and not failures:
        failures.append("No usable candidate code/label pair found.")
    elif recommended_pair is not None:
        if status_counts["duplicate_conflicting_label"]:
            failures.append(
                "Recommended candidate pair contains conflicting labels for target codes."
            )
        if status_counts["missing"]:
            warnings_list.append(
                "Recommended candidate pair is missing labels for target codes."
            )
        if status_counts["duplicate_same_label"]:
            warnings_list.append(
                "Some target codes appear more than once with the same label; "
                "this is consistent but not row-unique."
            )

    validation_status = _validation_status(failures, warnings_list, status_counts)
    summary = {
        "reference_file": _relative_to_project(reference_file),
        "sheet_count": len(sheets),
        "target_code_count": len(TARGET_AUTO_GARANTIE_CODES),
        "matched_unique_count": status_counts["matched_unique"],
        "duplicate_same_label_count": status_counts["duplicate_same_label"],
        "missing_count": status_counts["missing"],
        "duplicate_conflicting_count": status_counts["duplicate_conflicting_label"],
        "validation_status": validation_status,
    }

    return {
        "generated_at": generated_at,
        "reference_file": reference_file,
        "sheets": sheets,
        "pair_summaries": pair_summaries,
        "recommended_pair": recommended_pair,
        "target_results": target_results,
        "summary": summary,
        "warnings": warnings_list,
        "failures": failures,
    }


def _inspect_workbook(reference_file: Path) -> list[SheetInspection]:
    inspections: list[SheetInspection] = []

    with pd.ExcelFile(reference_file, engine="openpyxl") as workbook:
        for sheet_name in workbook.sheet_names:
            dataframe = _read_sheet(workbook, reference_file.name, sheet_name)
            columns = tuple(str(column).strip() for column in dataframe.columns)
            dataframe.columns = columns
            code_columns = tuple(_candidate_code_columns(columns))
            label_columns = tuple(_candidate_label_columns(columns))
            inspections.append(
                SheetInspection(
                    sheet_name=sheet_name,
                    row_count=len(dataframe),
                    columns=columns,
                    code_columns=code_columns,
                    label_columns=label_columns,
                    dataframe=dataframe,
                )
            )

    return inspections


def _read_sheet(workbook: pd.ExcelFile, file_name: str, sheet_name: str) -> pd.DataFrame:
    if _is_headerless_workbook(file_name):
        dataframe = pd.read_excel(
            workbook,
            sheet_name=sheet_name,
            dtype=object,
            header=None,
            engine="openpyxl",
        )
        dataframe.columns = _headerless_columns_for(file_name, len(dataframe.columns))
        return dataframe

    dataframe = pd.read_excel(
        workbook,
        sheet_name=sheet_name,
        dtype=object,
        engine="openpyxl",
    )
    dataframe.columns = _clean_header_columns(dataframe.columns)
    if not _candidate_code_columns(dataframe.columns) or not _candidate_label_columns(
        dataframe.columns
    ):
        fallback = pd.read_excel(
            workbook,
            sheet_name=sheet_name,
            dtype=object,
            header=None,
            engine="openpyxl",
        )
        fallback.columns = _generic_columns(len(fallback.columns))
        return fallback
    return dataframe


def _is_headerless_workbook(file_name: str) -> bool:
    return file_name.casefold() in {
        name.casefold() for name in HEADERLESS_WORKBOOK_COLUMNS
    }


def _headerless_columns_for(file_name: str, column_count: int) -> tuple[str, ...]:
    known_columns = next(
        (
            columns
            for name, columns in HEADERLESS_WORKBOOK_COLUMNS.items()
            if name.casefold() == file_name.casefold()
        ),
        (),
    )
    if column_count <= len(known_columns):
        return known_columns[:column_count]

    extras = tuple(f"COLUMN_{index}" for index in range(len(known_columns) + 1, column_count + 1))
    return known_columns + extras


def _clean_header_columns(columns: Any) -> list[str]:
    cleaned: list[str] = []
    for index, column in enumerate(columns, start=1):
        text = str(column).strip()
        if not text or text.lower().startswith("unnamed:"):
            text = f"COLUMN_{index}"
        cleaned.append(text)
    return cleaned


def _generic_columns(column_count: int) -> tuple[str, ...]:
    return tuple(f"COLUMN_{index}" for index in range(1, column_count + 1))


def _candidate_code_columns(columns: Any) -> list[str]:
    result: list[str] = []
    for column in columns:
        normalized = _normalize_column_name(column)
        compact = _compact_name(normalized)
        if compact in CODE_EXACT_NAMES:
            result.append(str(column))
            continue
        if any(keyword in normalized or keyword in compact for keyword in CODE_COLUMN_KEYWORDS):
            result.append(str(column))
    return result


def _candidate_label_columns(columns: Any) -> list[str]:
    primary: list[str] = []
    fallback: list[str] = []

    for column in columns:
        column_text = str(column)
        normalized = _normalize_column_name(column_text)
        compact = _compact_name(normalized)
        is_primary = (
            compact in LABEL_EXACT_NAMES
            or compact.startswith("lib")
            or any(
                keyword in normalized or keyword in compact
                for keyword in LABEL_PRIMARY_KEYWORDS
            )
        )
        if is_primary:
            primary.append(column_text)
            continue

        if ("garantie" in normalized or "garantie" in compact) and not _is_code_like_name(
            normalized,
            compact,
        ):
            fallback.append(column_text)

    return primary or fallback


def _is_code_like_name(normalized: str, compact: str) -> bool:
    return compact in CODE_EXACT_NAMES or any(
        keyword in normalized or keyword in compact
        for keyword in ("code", "cod", "grnt", "grntsini")
    )


def _candidate_pair_summaries(sheets: list[SheetInspection]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for sheet in sheets:
        for code_column in sheet.code_columns:
            for label_column in sheet.label_columns:
                if code_column == label_column:
                    continue
                target_results = _target_code_results(
                    sheets,
                    {
                        "sheet_name": sheet.sheet_name,
                        "code_column": code_column,
                        "label_column": label_column,
                    },
                )
                counts = _status_counts(target_results)
                summaries.append(
                    {
                        "sheet_name": sheet.sheet_name,
                        "code_column": code_column,
                        "label_column": label_column,
                        "matched_unique_count": counts["matched_unique"],
                        "duplicate_same_label_count": counts["duplicate_same_label"],
                        "missing_count": counts["missing"],
                        "duplicate_conflicting_count": counts[
                            "duplicate_conflicting_label"
                        ],
                        "safe_label_count": (
                            counts["matched_unique"] + counts["duplicate_same_label"]
                        ),
                        "rank_score": _pair_rank_score(
                            sheet.sheet_name,
                            code_column,
                            label_column,
                            counts,
                        ),
                    }
                )
    summaries.sort(
        key=lambda row: (
            row["rank_score"],
            row["safe_label_count"],
            -row["duplicate_conflicting_count"],
            -row["missing_count"],
        ),
        reverse=True,
    )
    return summaries


def _recommended_pair(pair_summaries: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not pair_summaries:
        return None
    best = pair_summaries[0].copy()
    best.pop("rank_score", None)
    return best


def _pair_rank_score(
    sheet_name: str,
    code_column: str,
    label_column: str,
    counts: dict[str, int],
) -> int:
    safe_label_count = counts["matched_unique"] + counts["duplicate_same_label"]
    score = 0
    score += safe_label_count * 10_000
    score -= counts["missing"] * 100
    score -= counts["duplicate_conflicting_label"] * 1_000
    score += _code_column_score(code_column)
    score += _label_column_score(label_column)
    if sheet_name.casefold() in {"feuil1", "sheet1"}:
        score += 1
    return score


def _code_column_score(column: str) -> int:
    compact = _compact_name(_normalize_column_name(column))
    if compact == "grntsini":
        return 500
    if "grntsini" in compact:
        return 450
    if compact in {"codegarantie", "garantiecode"}:
        return 350
    if compact == "codgrnt":
        return 250
    if "grnt" in compact:
        return 200
    if "codprod" in compact or "codformu" in compact:
        return 0
    if "code" in compact or "cod" in compact:
        return 100
    return 0


def _label_column_score(column: str) -> int:
    compact = _compact_name(_normalize_column_name(column))
    if compact == "libgrnsin":
        return 500
    if compact in LABEL_EXACT_NAMES:
        return 450
    if compact.startswith("lib"):
        return 350
    if any(keyword in compact for keyword in ("label", "designation", "desc")):
        return 250
    if "garantie" in compact:
        return 100
    return 0


def _target_code_results(
    sheets: list[SheetInspection],
    recommended_pair: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if recommended_pair is None:
        return [
            {
                "target_code": code,
                "status": "missing",
                "label": "",
                "distinct_label_count": 0,
                "match_row_count": 0,
                "sheet_name": "",
                "code_column": "",
                "label_column": "",
            }
            for code in TARGET_AUTO_GARANTIE_CODES
        ]

    matches_by_code = _matches_for_pair(sheets, recommended_pair)
    rows: list[dict[str, Any]] = []
    for code in TARGET_AUTO_GARANTIE_CODES:
        matches = matches_by_code.get(code, [])
        distinct_labels: dict[str, str] = {}
        for match in matches:
            distinct_labels.setdefault(match.label_key, match.label)

        if not matches:
            status = "missing"
        elif len(distinct_labels) == 1 and len(matches) == 1:
            status = "matched_unique"
        elif len(distinct_labels) == 1:
            status = "duplicate_same_label"
        else:
            status = "duplicate_conflicting_label"

        rows.append(
            {
                "target_code": code,
                "status": status,
                "label": "; ".join(sorted(distinct_labels.values())),
                "distinct_label_count": len(distinct_labels),
                "match_row_count": len(matches),
                "sheet_name": recommended_pair.get("sheet_name", ""),
                "code_column": recommended_pair.get("code_column", ""),
                "label_column": recommended_pair.get("label_column", ""),
            }
        )

    return rows


def _matches_for_pair(
    sheets: list[SheetInspection],
    pair: dict[str, Any],
) -> dict[str, list[MatchRow]]:
    target_set = set(TARGET_AUTO_GARANTIE_CODES)
    matches: dict[str, list[MatchRow]] = {code: [] for code in TARGET_AUTO_GARANTIE_CODES}

    for sheet in sheets:
        if sheet.sheet_name != pair.get("sheet_name"):
            continue
        code_column = pair.get("code_column")
        label_column = pair.get("label_column")
        if code_column not in sheet.dataframe.columns or label_column not in sheet.dataframe.columns:
            continue

        for row_index, row in sheet.dataframe.iterrows():
            code = _normalize_code(row.get(code_column))
            if code not in target_set:
                continue

            label = _normalize_label(row.get(label_column))
            if not label:
                continue

            matches[code].append(
                MatchRow(
                    target_code=code,
                    label=label,
                    label_key=_label_key(label),
                    sheet_name=sheet.sheet_name,
                    code_column=code_column,
                    label_column=label_column,
                    excel_row_number=int(row_index) + 1,
                )
            )

    return matches


def _status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "matched_unique": 0,
        "missing": 0,
        "duplicate_same_label": 0,
        "duplicate_conflicting_label": 0,
    }
    for row in rows:
        status = row.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def _validation_status(
    failures: list[str],
    warnings_list: list[str],
    counts: dict[str, int],
) -> str:
    if failures:
        return "FAIL"
    if warnings_list or counts["missing"]:
        return "WARNING"
    return "OK"


def _build_report(results: dict[str, Any]) -> Report:
    report = Report()
    report.title(
        "IRISv2 Automobile Garantie Reference Inspection",
        results["generated_at"],
    )

    summary = results["summary"]
    report.section("1. Console Summary")
    for label in (
        "reference_file",
        "sheet_count",
        "target_code_count",
        "matched_unique_count",
        "duplicate_same_label_count",
        "missing_count",
        "duplicate_conflicting_count",
        "validation_status",
    ):
        report.metric(label, summary[label])

    report.section("2. Sheet Inventory")
    report.table(
        [
            {
                "sheet_name": sheet.sheet_name,
                "row_count": sheet.row_count,
                "column_count": len(sheet.columns),
                "columns": ", ".join(sheet.columns),
                "candidate_code_columns": ", ".join(sheet.code_columns),
                "candidate_label_columns": ", ".join(sheet.label_columns),
            }
            for sheet in results["sheets"]
        ],
        [
            "sheet_name",
            "row_count",
            "column_count",
            "columns",
            "candidate_code_columns",
            "candidate_label_columns",
        ],
    )

    report.section("3. Candidate Pair Evaluation")
    report.metric(
        "recommended_sheet",
        (results["recommended_pair"] or {}).get("sheet_name", "N/A"),
    )
    report.metric(
        "recommended_code_column",
        (results["recommended_pair"] or {}).get("code_column", "N/A"),
    )
    report.metric(
        "recommended_label_column",
        (results["recommended_pair"] or {}).get("label_column", "N/A"),
    )
    report.table(
        [
            {
                key: value
                for key, value in row.items()
                if key != "rank_score"
            }
            for row in results["pair_summaries"]
        ],
        [
            "sheet_name",
            "code_column",
            "label_column",
            "matched_unique_count",
            "duplicate_same_label_count",
            "missing_count",
            "duplicate_conflicting_count",
            "safe_label_count",
        ],
    )

    report.section("4. Target Automobile Guarantee Code Results")
    report.table(
        results["target_results"],
        [
            "target_code",
            "status",
            "label",
            "distinct_label_count",
            "match_row_count",
            "sheet_name",
            "code_column",
            "label_column",
        ],
    )

    report.section("5. Interpretation")
    report.bullets(_interpretation(results))

    report.section("6. Warnings And Failures")
    report.metric("validation_status", summary["validation_status"])
    report.table(
        [{"type": "FAILURE", "message": message} for message in results["failures"]]
        + [{"type": "WARNING", "message": message} for message in results["warnings"]],
        ["type", "message"],
    )

    return report


def _interpretation(results: dict[str, Any]) -> list[str]:
    summary = results["summary"]
    pair = results["recommended_pair"]
    messages: list[str] = []

    if pair is None:
        return ["No usable candidate code/label pair was found."]

    if summary["duplicate_conflicting_count"]:
        messages.append(
            "Do not enrich dim_garantie from the recommended pair yet; at least "
            "one target code maps to conflicting labels."
        )
    elif summary["missing_count"]:
        messages.append(
            "Partial enrichment is possible, but some target automobile guarantee "
            "codes are missing from the recommended reference pair."
        )
    else:
        messages.append(
            "The recommended reference pair has one distinct non-empty label for "
            "each target automobile guarantee code."
        )

    if summary["duplicate_same_label_count"]:
        messages.append(
            "Duplicate_same_label rows indicate repeated product/formula rows "
            "with the same label; this is consistent, but enrichment should use "
            "a distinct code-to-label mapping."
        )

    messages.append(
        "This inspection does not enrich dim_garantie; a dedicated enrichment "
        "loader or reference update should implement any correction later."
    )
    return messages


def _resolve_reference_file(cli_path: str | None) -> Path:
    if cli_path:
        return _resolve_project_path(cli_path)

    if PREFERRED_REFERENCE_FILE.exists():
        return PREFERRED_REFERENCE_FILE

    candidates = sorted(
        path
        for path in DEFAULT_REFERENCE_DIR.rglob("*.xls*")
        if "garantie" in _normalize_column_name(path.name)
    )
    if candidates:
        return candidates[0]

    return PREFERRED_REFERENCE_FILE


def _resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _relative_to_project(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


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


def _label_key(label: str) -> str:
    return unicodedata.normalize("NFKC", label).casefold()


def _normalize_column_name(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(character for character in text if not unicodedata.combining(character))
    return re.sub(r"\s+", " ", text.strip().casefold())


def _compact_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value)


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
            "Inspect local garantie reference labels for automobile guarantee "
            "codes without modifying data."
        )
    )
    parser.add_argument(
        "--reference-file",
        help=(
            "Optional reference workbook path. Defaults to "
            "data/reference/correspondance garantie.xlsx, or the first Excel "
            "file under data/reference containing 'garantie'."
        ),
    )
    parser.add_argument(
        "--report-path",
        default=str(REPORT_PATH),
        help="Markdown report path.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
