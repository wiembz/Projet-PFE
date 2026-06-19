from __future__ import annotations

import argparse
import re
import unicodedata
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default",
    category=UserWarning,
    module="openpyxl.styles.stylesheet",
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "docs" / "reference_inventory.md"

REFERENCE_FILES = (
    "fichierStagiaire.xlsx",
    "PR01.xlsx",
    "PE033.xlsx",
    "PE02.xlsx",
    "PE01.xlsx",
    "SI001.xlsx",
    "correspondance garantie.xlsx",
)

NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}
KEY_HINT_PREFIXES = ("COD", "CODE", "ID", "NUM", "NAT", "CLASS")
KEY_HINT_EXACT = {
    "TABLE",
    "CAUSESINI",
    "GRNTSINI",
    "SOUNATSIN",
    "CNAT",
    "CLASSPERS",
}
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


@dataclass(frozen=True)
class CandidateKeyCheck:
    file_name: str
    sheet_name: str | None
    columns: tuple[str, ...]


@dataclass(frozen=True)
class DuplicateCheckResult:
    expected_columns: tuple[str, ...]
    actual_columns: tuple[str, ...]
    missing_columns: tuple[str, ...]
    complete_key_rows: int
    incomplete_key_rows: int
    duplicate_row_count: int
    duplicate_group_count: int


@dataclass(frozen=True)
class SheetProfile:
    file_name: str
    sheet_name: str
    row_count: int
    column_count: int
    columns: tuple[str, ...]
    first_rows: pd.DataFrame
    key_like_null_counts: dict[str, int]
    duplicate_checks: tuple[DuplicateCheckResult, ...]


CANDIDATE_KEY_CHECKS = (
    CandidateKeyCheck("fichierStagiaire.xlsx", "CODFAM", ("CODFAM",)),
    CandidateKeyCheck(
        "fichierStagiaire.xlsx",
        "CODPROD",
        ("CODPROD", "CODFORMU"),
    ),
    CandidateKeyCheck(
        "fichierStagiaire.xlsx",
        "GRNTSINI",
        ("CODPROD", "CODFORMU", "GRNTSINI"),
    ),
    CandidateKeyCheck(
        "fichierStagiaire.xlsx",
        "SOUSNATSIN",
        ("CODFAM", "CAUSESINI", "SOUNATSIN"),
    ),
    CandidateKeyCheck(
        "fichierStagiaire.xlsx",
        "D\u00e9l\u00e9gation",
        ("CODDELEGA",),
    ),
    CandidateKeyCheck(
        "correspondance garantie.xlsx",
        None,
        ("CODPROD", "CODFORMU", "GRNTSINI"),
    ),
    CandidateKeyCheck("SI001.xlsx", None, ("CODFAM", "CAUSESINI")),
    CandidateKeyCheck("PR01.xlsx", None, ("NATINT", "IDINT")),
    CandidateKeyCheck("PE02.xlsx", None, ("CLASSPERS",)),
    CandidateKeyCheck("PE033.xlsx", None, ("CNAT",)),
    CandidateKeyCheck("PE01.xlsx", None, ("TABLE", "CODE")),
)


def main() -> None:
    args = _parse_args()
    reference_dir = _resolve_project_path(args.reference_dir)
    report_path = _resolve_project_path(args.report_path)

    profiles = profile_reference_files(reference_dir)
    console_report = build_console_report(profiles)
    markdown_report = build_markdown_report(profiles, reference_dir)

    print(console_report)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(markdown_report, encoding="utf-8")
    print(f"\n[OK] Markdown inventory written to {report_path}")


def profile_reference_files(reference_dir: Path) -> list[SheetProfile]:
    profiles: list[SheetProfile] = []

    for file_name in REFERENCE_FILES:
        workbook_path = reference_dir / file_name
        if not workbook_path.exists():
            raise FileNotFoundError(f"Reference workbook not found: {workbook_path}")

        with pd.ExcelFile(workbook_path, engine="openpyxl") as workbook:
            for sheet_name in workbook.sheet_names:
                if _is_headerless_workbook(file_name):
                    dataframe = pd.read_excel(
                        workbook,
                        sheet_name=sheet_name,
                        dtype=str,
                        header=None,
                        engine="openpyxl",
                    )
                    dataframe.columns = _headerless_columns_for(
                        file_name,
                        len(dataframe.columns),
                    )
                else:
                    dataframe = pd.read_excel(
                        workbook,
                        sheet_name=sheet_name,
                        dtype=str,
                        engine="openpyxl",
                    )
                dataframe.columns = [
                    str(column).strip()
                    for column in dataframe.columns
                ]
                profiles.append(
                    profile_sheet(file_name, sheet_name, dataframe)
                )

    return profiles


def profile_sheet(
    file_name: str,
    sheet_name: str,
    dataframe: pd.DataFrame,
) -> SheetProfile:
    candidate_checks = _candidate_checks_for(file_name, sheet_name)
    key_like_columns = _find_key_like_columns(dataframe.columns, candidate_checks)
    null_counts = {
        column: _null_like_count(dataframe[column])
        for column in key_like_columns
        if column in dataframe.columns
    }
    duplicate_checks = tuple(
        _build_duplicate_check(dataframe, check)
        for check in candidate_checks
    )

    return SheetProfile(
        file_name=file_name,
        sheet_name=sheet_name,
        row_count=len(dataframe),
        column_count=len(dataframe.columns),
        columns=tuple(str(column) for column in dataframe.columns),
        first_rows=dataframe.head(5),
        key_like_null_counts=null_counts,
        duplicate_checks=duplicate_checks,
    )


def build_console_report(profiles: list[SheetProfile]) -> str:
    lines: list[str] = []
    lines.append("=" * 100)
    lines.append("IRISv2 Reference Workbook Inventory")
    lines.append(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("=" * 100)

    for profile in profiles:
        lines.extend(_console_sheet_section(profile))

    return "\n".join(lines)


def build_markdown_report(
    profiles: list[SheetProfile],
    reference_dir: Path,
) -> str:
    lines: list[str] = []
    lines.append("# IRISv2 Reference Workbook Inventory")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Reference directory: `{_relative_to_project(reference_dir)}`")
    lines.append("")
    lines.append(
        "This report profiles the official reference workbooks only. "
        "It does not write to PostgreSQL or change warehouse tables."
    )

    for profile in profiles:
        lines.extend(_markdown_sheet_section(profile))

    lines.append("")
    return "\n".join(lines)


def _console_sheet_section(profile: SheetProfile) -> list[str]:
    lines: list[str] = []
    lines.append("")
    lines.append("-" * 100)
    lines.append(f"file_name: {profile.file_name}")
    lines.append(f"sheet_name: {profile.sheet_name}")
    lines.append(f"row_count: {profile.row_count}")
    lines.append(f"column_count: {profile.column_count}")
    lines.append("columns:")
    lines.extend(f"  - {column}" for column in profile.columns)
    lines.append("first 5 rows:")
    lines.append(_frame_preview(profile.first_rows))
    lines.append("null counts for key-like columns:")
    lines.extend(_null_count_lines(profile.key_like_null_counts, indent="  "))
    lines.append("candidate key duplicate checks:")
    lines.extend(_duplicate_check_lines(profile.duplicate_checks, indent="  "))
    return lines


def _markdown_sheet_section(profile: SheetProfile) -> list[str]:
    lines: list[str] = []
    title = f"{profile.file_name} / {profile.sheet_name}"
    lines.append("")
    lines.append(f"## {title}")
    lines.append("")
    lines.append(f"- file_name: `{profile.file_name}`")
    lines.append(f"- sheet_name: `{profile.sheet_name}`")
    lines.append(f"- row_count: `{profile.row_count}`")
    lines.append(f"- column_count: `{profile.column_count}`")
    lines.append("")
    lines.append("### Columns")
    lines.append("")
    lines.extend(f"- `{column}`" for column in profile.columns)
    lines.append("")
    lines.append("### First 5 Rows")
    lines.append("")
    lines.append("```text")
    lines.append(_frame_preview(profile.first_rows))
    lines.append("```")
    lines.append("")
    lines.append("### Null Counts For Key-Like Columns")
    lines.append("")
    lines.extend(_null_count_lines(profile.key_like_null_counts, indent="- "))
    lines.append("")
    lines.append("### Candidate Key Duplicate Checks")
    lines.append("")
    lines.extend(_duplicate_check_lines(profile.duplicate_checks, indent="- "))
    return lines


def _candidate_checks_for(
    file_name: str,
    sheet_name: str,
) -> tuple[CandidateKeyCheck, ...]:
    normalized_file = _normalize_label(file_name)
    normalized_sheet = _normalize_label(sheet_name)
    checks: list[CandidateKeyCheck] = []

    for check in CANDIDATE_KEY_CHECKS:
        if _normalize_label(check.file_name) != normalized_file:
            continue
        if (
            check.sheet_name is not None
            and _normalize_label(check.sheet_name) != normalized_sheet
        ):
            continue
        checks.append(check)

    return tuple(checks)


def _find_key_like_columns(
    columns: pd.Index,
    candidate_checks: tuple[CandidateKeyCheck, ...],
) -> list[str]:
    expected_key_columns = {
        _normalize_column_name(column)
        for check in candidate_checks
        for column in check.columns
    }

    key_like_columns: list[str] = []
    for column in columns:
        column_name = str(column)
        normalized = _normalize_column_name(column_name)
        is_expected_key = normalized in expected_key_columns
        has_key_prefix = normalized.startswith(KEY_HINT_PREFIXES)
        has_key_exact_name = normalized in KEY_HINT_EXACT

        if is_expected_key or has_key_prefix or has_key_exact_name:
            key_like_columns.append(column_name)

    return key_like_columns


def _build_duplicate_check(
    dataframe: pd.DataFrame,
    check: CandidateKeyCheck,
) -> DuplicateCheckResult:
    column_map = _build_normalized_column_map(dataframe.columns)
    actual_columns: list[str] = []
    missing_columns: list[str] = []

    for expected_column in check.columns:
        normalized = _normalize_column_name(expected_column)
        actual_column = column_map.get(normalized)
        if actual_column is None:
            missing_columns.append(expected_column)
        else:
            actual_columns.append(actual_column)

    if missing_columns:
        return DuplicateCheckResult(
            expected_columns=check.columns,
            actual_columns=tuple(actual_columns),
            missing_columns=tuple(missing_columns),
            complete_key_rows=0,
            incomplete_key_rows=len(dataframe),
            duplicate_row_count=0,
            duplicate_group_count=0,
        )

    key_frame = pd.DataFrame(
        {
            column: dataframe[column].map(_normalize_cell_value)
            for column in actual_columns
        }
    )
    complete_mask = key_frame.notna().all(axis=1)
    complete_key_rows = int(complete_mask.sum())
    incomplete_key_rows = int(len(key_frame) - complete_key_rows)
    complete_keys = key_frame.loc[complete_mask]

    if complete_keys.empty:
        duplicate_row_count = 0
        duplicate_group_count = 0
    else:
        duplicate_row_count = int(complete_keys.duplicated(subset=actual_columns).sum())
        group_sizes = complete_keys.value_counts(subset=actual_columns, dropna=False)
        duplicate_group_count = int((group_sizes > 1).sum())

    return DuplicateCheckResult(
        expected_columns=check.columns,
        actual_columns=tuple(actual_columns),
        missing_columns=tuple(),
        complete_key_rows=complete_key_rows,
        incomplete_key_rows=incomplete_key_rows,
        duplicate_row_count=duplicate_row_count,
        duplicate_group_count=duplicate_group_count,
    )


def _null_count_lines(null_counts: dict[str, int], indent: str) -> list[str]:
    if not null_counts:
        return [f"{indent}No key-like columns found."]

    return [
        f"{indent}{column}: {count}"
        for column, count in null_counts.items()
    ]


def _duplicate_check_lines(
    checks: tuple[DuplicateCheckResult, ...],
    indent: str,
) -> list[str]:
    if not checks:
        return [f"{indent}No candidate key check configured for this sheet."]

    lines: list[str] = []
    for check in checks:
        key_name = " + ".join(check.expected_columns)
        if check.missing_columns:
            missing = ", ".join(check.missing_columns)
            found = ", ".join(check.actual_columns) if check.actual_columns else "none"
            lines.append(
                f"{indent}{key_name}: skipped; missing columns: {missing}; "
                f"matched columns: {found}"
            )
            continue

        lines.append(
            f"{indent}{key_name}: complete_key_rows={check.complete_key_rows}, "
            f"incomplete_key_rows={check.incomplete_key_rows}, "
            f"duplicate_row_count={check.duplicate_row_count}, "
            f"duplicate_group_count={check.duplicate_group_count}"
        )

    return lines


def _frame_preview(dataframe: pd.DataFrame) -> str:
    if dataframe.empty:
        return "<no rows>"

    preview = dataframe.copy()
    preview = preview.astype(object).where(pd.notna(preview), "")
    return preview.to_string(index=False)


def _build_normalized_column_map(columns: pd.Index) -> dict[str, str]:
    column_map: dict[str, str] = {}
    for column in columns:
        column_name = str(column)
        normalized = _normalize_column_name(column_name)
        column_map.setdefault(normalized, column_name)
    return column_map


def _is_headerless_workbook(file_name: str) -> bool:
    normalized_file = _normalize_label(file_name)
    return any(
        _normalize_label(headerless_file) == normalized_file
        for headerless_file in HEADERLESS_WORKBOOK_COLUMNS
    )


def _headerless_columns_for(file_name: str, column_count: int) -> list[str]:
    configured_names = next(
        columns
        for workbook_name, columns in HEADERLESS_WORKBOOK_COLUMNS.items()
        if _normalize_label(workbook_name) == _normalize_label(file_name)
    )

    column_names = list(configured_names[:column_count])
    for column_number in range(len(column_names) + 1, column_count + 1):
        column_names.append(f"COLUMN_{column_number}")

    return column_names


def _null_like_count(series: pd.Series) -> int:
    return int(series.map(lambda value: _normalize_cell_value(value) is None).sum())


def _normalize_cell_value(value: Any) -> str | None:
    if pd.isna(value):
        return None

    normalized = str(value).strip()
    if normalized.casefold() in NULL_MARKERS:
        return None

    return normalized


def _normalize_label(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value).strip())
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_value).casefold()


def _normalize_column_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value).strip())
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Za-z0-9]+", "", ascii_value).upper()


def _relative_to_project(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _resolve_project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile official IRISv2 reference Excel workbooks."
    )
    parser.add_argument(
        "--reference-dir",
        type=Path,
        default=DEFAULT_REFERENCE_DIR,
        help="Directory containing the official reference Excel files.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Markdown report path to write.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
