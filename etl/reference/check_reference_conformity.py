from __future__ import annotations

import argparse
import re
import sys
import unicodedata
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


DEFAULT_REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "docs" / "reference_conformity_report.md"
DW_SCHEMA = "iris_dw"
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}
AUTOMOBILE_CODFAM = "5"
UNKNOWN_VALUE = "UNKNOWN"


warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default",
    category=UserWarning,
    module="openpyxl.styles.stylesheet",
)


@dataclass(frozen=True)
class DuplicateCheckResult:
    key_columns: tuple[str, ...]
    total_rows: int
    complete_key_rows: int
    incomplete_key_rows: int
    duplicate_row_count: int
    duplicate_group_count: int


@dataclass(frozen=True)
class TableData:
    name: str
    columns: set[str]
    dataframe: pd.DataFrame


class Report:
    def __init__(self) -> None:
        self.console_lines: list[str] = []
        self.markdown_lines: list[str] = []

    def title(self, text: str) -> None:
        generated_at = datetime.now().isoformat(timespec="seconds")
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
                    "This report is read-only. It reads official reference "
                    "Excel files and existing `iris_dw` dimension tables; it "
                    "does not write to PostgreSQL or update DW tables."
                ),
                "",
            ]
        )

    def section(self, text: str) -> None:
        self.console_lines.extend(["", "-" * 100, text])
        self.markdown_lines.extend(["", f"## {text}", ""])

    def metric(self, label: str, value: Any) -> None:
        self.console_lines.append(f"{label}: {value}")
        self.markdown_lines.append(f"- {label}: `{value}`")

    def note(self, text: str) -> None:
        self.console_lines.append(text)
        self.markdown_lines.append(f"- {text}")

    def subheading(self, text: str) -> None:
        self.console_lines.extend(["", text])
        self.markdown_lines.extend(["", f"### {text}", ""])

    def table(self, rows: list[dict[str, Any]], columns: list[str]) -> None:
        if not rows:
            self.console_lines.append("No rows.")
            self.markdown_lines.append("No rows.")
            return

        frame = pd.DataFrame(rows, columns=columns)
        frame = frame.astype(object).where(pd.notna(frame), "")
        self.console_lines.append(frame.to_string(index=False))
        self.markdown_lines.extend(_dataframe_to_markdown(frame))

    def render_console(self) -> str:
        return "\n".join(self.console_lines)

    def render_markdown(self) -> str:
        return "\n".join(self.markdown_lines).rstrip() + "\n"


def main() -> None:
    args = _parse_args()
    reference_dir = _resolve_project_path(args.reference_dir)
    report_path = _resolve_project_path(args.report_path)

    report = Report()
    report.title("IRISv2 Reference Conformity Report")
    report.metric("Reference directory", _relative_to_project(reference_dir))
    report.markdown_lines.append("")

    conn = get_connection()
    try:
        check_garantie_label_stability(conn, reference_dir, report)
        check_cause_sinistre_feasibility(conn, reference_dir, report)
        check_produit_label_stability(conn, reference_dir, report)
        check_delegation(reference_dir, report)
        check_intermediaire(conn, reference_dir, report)
    finally:
        try:
            conn.rollback()
        finally:
            conn.close()

    print(report.render_console())

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report.render_markdown(), encoding="utf-8")
    print(f"\n[OK] Markdown conformity report written to {report_path}")


def check_garantie_label_stability(
    conn: Any,
    reference_dir: Path,
    report: Report,
) -> None:
    report.section("1) Garantie Label Stability")

    garanties = _read_correspondance_garantie(reference_dir)
    _clean_columns(garanties, ("CODPROD", "CODFORMU", "GRNTSINI", "LIBGRNSIN"))
    conflicts = _label_conflicts(garanties, "GRNTSINI", "LIBGRNSIN")
    reference_labels = _reference_values_with_labels(garanties, "GRNTSINI", "LIBGRNSIN")

    report.metric("total rows", len(garanties))
    report.metric("distinct GRNTSINI", _nunique_non_null(garanties, "GRNTSINI"))
    report.metric("GRNTSINI with multiple labels", len(conflicts))
    _report_sample_conflicts(report, conflicts, "GRNTSINI", "LIBGRNSIN")

    dim = _fetch_dimension(
        conn,
        "dim_garantie",
        required_columns=("garantie_natural_key",),
        optional_columns=("garantie_sk", "code_garantie", "libelle_garantie"),
    )
    dim_df = _exclude_unknown_rows(dim.dataframe, "garantie_natural_key")
    _clean_columns(dim_df, ("garantie_natural_key",))

    dim_keys = dim_df["garantie_natural_key"].map(_clean_string)
    has_reference_label = dim_keys.isin(reference_labels)

    report.metric("dim_garantie rows excluding UNKNOWN", len(dim_df))
    report.metric("rows with at least one reference label", int(has_reference_label.sum()))
    report.metric("rows without reference label", int((~has_reference_label).sum()))


def check_cause_sinistre_feasibility(
    conn: Any,
    reference_dir: Path,
    report: Report,
) -> None:
    report.section("2) Cause Sinistre Enrichment Feasibility")
    report.metric("automobile CODFAM scope", AUTOMOBILE_CODFAM)

    si001 = _read_sheet(reference_dir / "SI001.xlsx", "Sheet1")
    sousnatsin = _read_sheet(
        reference_dir / "fichierStagiaire.xlsx",
        "SOUSNATSIN",
    )

    _clean_columns(si001, ("CODFAM", "CAUSESINI", "LIBCAUSE"))
    _clean_columns(sousnatsin, ("CODFAM", "CAUSESINI", "SOUNATSIN", "LIBSOUNAT"))

    si_unique = _duplicate_check(si001, ("CODFAM", "CAUSESINI"))
    sous_unique = _duplicate_check(
        sousnatsin,
        ("CODFAM", "CAUSESINI", "SOUNATSIN"),
    )

    _report_duplicate_check(report, "SI001 CODFAM + CAUSESINI", si_unique)
    _report_duplicate_check(
        report,
        "SOUSNATSIN CODFAM + CAUSESINI + SOUNATSIN",
        sous_unique,
    )

    si_auto = si001.loc[si001["CODFAM"] == AUTOMOBILE_CODFAM].copy()
    sous_auto = sousnatsin.loc[sousnatsin["CODFAM"] == AUTOMOBILE_CODFAM].copy()
    si_cause_keys = _reference_values_with_labels(
        si_auto,
        "CAUSESINI",
        "LIBCAUSE",
    )
    sous_key_pairs = _reference_key_pairs_with_labels(
        sous_auto,
        "CAUSESINI",
        "SOUNATSIN",
        "LIBSOUNAT",
    )

    dim = _fetch_dimension(
        conn,
        "dim_cause_sinistre",
        required_columns=("code_cause_sinistre", "code_sous_nature_sinistre"),
        optional_columns=(
            "cause_sinistre_sk",
            "cause_sinistre_natural_key",
            "code_nature_sinistre",
            "libelle_cause_sinistre",
            "libelle_sous_nature_sinistre",
        ),
    )
    dim_df = _exclude_unknown_rows(
        dim.dataframe,
        "cause_sinistre_natural_key",
        "code_cause_sinistre",
        "code_sous_nature_sinistre",
    )
    _clean_columns(
        dim_df,
        ("code_cause_sinistre", "code_sous_nature_sinistre"),
    )

    cause_match = dim_df["code_cause_sinistre"].isin(si_cause_keys)
    sous_match = dim_df.apply(
        lambda row: (
            row["code_cause_sinistre"],
            row["code_sous_nature_sinistre"],
        )
        in sous_key_pairs,
        axis=1,
    )
    not_matched = ~(cause_match | sous_match)

    report.metric("dim_cause_sinistre rows excluding UNKNOWN", len(dim_df))
    report.metric(
        "rows enrichable for libelle_cause_sinistre",
        int(cause_match.sum()),
    )
    report.metric(
        "rows enrichable for libelle_sous_nature_sinistre",
        int(sous_match.sum()),
    )
    report.metric("rows not matched", int(not_matched.sum()))

    sample = dim_df.loc[not_matched].head(10)
    _report_sample_dataframe(
        report,
        "Sample Not Matched",
        sample,
        _existing_columns(
            sample,
            (
                "cause_sinistre_natural_key",
                "code_cause_sinistre",
                "code_nature_sinistre",
                "code_sous_nature_sinistre",
            ),
        ),
    )


def check_produit_label_stability(
    conn: Any,
    reference_dir: Path,
    report: Report,
) -> None:
    report.section("3) Produit Label Stability")

    produits = _read_sheet(reference_dir / "fichierStagiaire.xlsx", "CODPROD")
    _clean_columns(produits, ("CODPROD", "CODFORMU", "LIBFORMU"))

    codprod_conflicts = _label_conflicts(produits, "CODPROD", "LIBFORMU")
    produit_unique = _duplicate_check(produits, ("CODPROD", "CODFORMU"))

    _report_duplicate_check(report, "CODPROD + CODFORMU", produit_unique)
    report.metric("CODPROD with multiple LIBFORMU", len(codprod_conflicts))
    _report_sample_conflicts(report, codprod_conflicts, "CODPROD", "LIBFORMU")

    dim = _fetch_dimension(
        conn,
        "dim_produit",
        required_columns=("code_produit",),
        optional_columns=(
            "produit_sk",
            "produit_natural_key",
            "libelle_produit",
            "code_formule",
        ),
    )
    dim_df = _exclude_unknown_rows(
        dim.dataframe,
        "produit_natural_key",
        "code_produit",
    )
    _clean_columns(dim_df, ("code_produit", "code_formule"))

    has_code_formule = "code_formule" in dim.columns
    if has_code_formule:
        reference_keys = _complete_key_set(produits, ("CODPROD", "CODFORMU"))
        matched = dim_df.apply(
            lambda row: (row["code_produit"], row["code_formule"]) in reference_keys,
            axis=1,
        )
        join_mode = "code_produit + code_formule"
    else:
        reference_keys = set(produits["CODPROD"].dropna())
        matched = dim_df["code_produit"].isin(reference_keys)
        join_mode = "code_produit only; code_formule column not available"

    report.metric("dim_produit rows excluding UNKNOWN", len(dim_df))
    report.metric("join mode", join_mode)
    report.metric("rows matched", int(matched.sum()))
    report.metric("rows unmatched", int((~matched).sum()))


def check_delegation(reference_dir: Path, report: Report) -> None:
    report.section("4) Delegation")

    delegation = _read_sheet(reference_dir / "fichierStagiaire.xlsx", "D\u00e9l\u00e9gation")
    _clean_columns(delegation, ("CODDELEGA", "LIBDELEGA"))

    libelle_empty = delegation["LIBDELEGA"].isna()
    report.metric("reference rows", len(delegation))
    report.metric("empty LIBDELEGA rows", int(libelle_empty.sum()))
    report.metric("non-empty LIBDELEGA rows", int((~libelle_empty).sum()))

    if libelle_empty.all():
        report.note("D\u00e9l\u00e9gation LIBDELEGA is empty and should not be used for enrichment.")
    else:
        sample = delegation.loc[~libelle_empty].head(10)
        _report_sample_dataframe(
            report,
            "Sample Non-Empty LIBDELEGA",
            sample,
            _existing_columns(sample, ("CODDELEGA", "LIBDELEGA")),
        )


def check_intermediaire(
    conn: Any,
    reference_dir: Path,
    report: Report,
) -> None:
    report.section("5) Intermediaire")

    pr01 = _read_sheet(reference_dir / "PR01.xlsx", "Sheet1")
    _clean_columns(pr01, ("NATINT", "IDINT", "LOCAL"))

    intermediaire_unique = _duplicate_check(pr01, ("NATINT", "IDINT"))
    _report_duplicate_check(report, "PR01 NATINT + IDINT", intermediaire_unique)

    dim = _fetch_dimension(
        conn,
        "dim_intermediaire",
        required_columns=("code_nature_intermediaire", "code_intermediaire"),
        optional_columns=(
            "intermediaire_sk",
            "intermediaire_natural_key",
            "nom_intermediaire",
            "type_intermediaire",
            "local_intermediaire",
        ),
    )
    dim_df = _exclude_unknown_rows(
        dim.dataframe,
        "intermediaire_natural_key",
        "code_nature_intermediaire",
        "code_intermediaire",
    )
    _clean_columns(dim_df, ("code_nature_intermediaire", "code_intermediaire"))

    reference_keys = _complete_key_set(pr01, ("NATINT", "IDINT"))
    matched = dim_df.apply(
        lambda row: (
            row["code_nature_intermediaire"],
            row["code_intermediaire"],
        )
        in reference_keys,
        axis=1,
    )
    local_column_exists = "local_intermediaire" in dim.columns

    report.metric("dim_intermediaire rows excluding UNKNOWN", len(dim_df))
    report.metric("matched count", int(matched.sum()))
    report.metric("unmatched count", int((~matched).sum()))
    report.metric("local_intermediaire column exists", "yes" if local_column_exists else "no")
    report.note(
        "Recommendation: do not update current DDL unless local_intermediaire column exists."
    )


def _fetch_dimension(
    conn: Any,
    table_name: str,
    required_columns: tuple[str, ...],
    optional_columns: tuple[str, ...] = (),
) -> TableData:
    columns = _get_table_columns(conn, table_name)
    missing_columns = [column for column in required_columns if column not in columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"{DW_SCHEMA}.{table_name} is missing columns: {missing}")

    selected_columns = [
        column
        for column in dict.fromkeys(required_columns + optional_columns)
        if column in columns
    ]

    query = sql.SQL("SELECT {} FROM {}.{}").format(
        sql.SQL(", ").join(sql.Identifier(column) for column in selected_columns),
        sql.Identifier(DW_SCHEMA),
        sql.Identifier(table_name),
    )

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        result_columns = [description[0] for description in cur.description]

    return TableData(
        name=table_name,
        columns=columns,
        dataframe=pd.DataFrame(rows, columns=result_columns),
    )


def _get_table_columns(conn: Any, table_name: str) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %(schema)s
              AND table_name = %(table)s
            """,
            {
                "schema": DW_SCHEMA,
                "table": table_name,
            },
        )
        columns = {row[0] for row in cur.fetchall()}

    if not columns:
        raise RuntimeError(f"{DW_SCHEMA}.{table_name} does not exist")

    return columns


def _read_correspondance_garantie(reference_dir: Path) -> pd.DataFrame:
    path = reference_dir / "correspondance garantie.xlsx"
    dataframe = _read_sheet(
        path,
        "Feuil1",
        header=None,
    )
    configured_columns = (
        "CODPROD",
        "CODFORMU",
        "GRNTSINI",
        "CODGRNT",
        "LIBGRNSIN",
        "COLUMN_6",
    )
    dataframe.columns = _headerless_columns(configured_columns, len(dataframe.columns))
    return dataframe


def _read_sheet(
    workbook_path: Path,
    sheet_name: str,
    header: int | None = 0,
) -> pd.DataFrame:
    if not workbook_path.exists():
        raise FileNotFoundError(f"Reference workbook not found: {workbook_path}")

    with pd.ExcelFile(workbook_path, engine="openpyxl") as workbook:
        actual_sheet_name = _resolve_sheet_name(workbook.sheet_names, sheet_name)
        dataframe = pd.read_excel(
            workbook,
            sheet_name=actual_sheet_name,
            dtype=str,
            header=header,
            engine="openpyxl",
        )

    dataframe.columns = [str(column).strip() for column in dataframe.columns]
    return dataframe


def _resolve_sheet_name(sheet_names: list[str], requested_name: str) -> str:
    requested_normalized = _normalize_label(requested_name)
    for sheet_name in sheet_names:
        if _normalize_label(sheet_name) == requested_normalized:
            return sheet_name

    available = ", ".join(sheet_names)
    raise ValueError(
        f"Sheet {requested_name!r} not found. Available sheets: {available}"
    )


def _clean_columns(dataframe: pd.DataFrame, columns: Iterable[str]) -> None:
    for column in columns:
        if column in dataframe.columns:
            dataframe[column] = dataframe[column].map(_clean_string)


def _clean_string(value: Any) -> str | None:
    if pd.isna(value):
        return None

    cleaned = str(value).strip()
    if cleaned.casefold() in NULL_MARKERS:
        return None

    return cleaned


def _exclude_unknown_rows(
    dataframe: pd.DataFrame,
    natural_key_column: str,
    *fallback_columns: str,
) -> pd.DataFrame:
    result = dataframe.copy()

    if natural_key_column in result.columns:
        natural_key = result[natural_key_column].map(_clean_string)
        return result.loc[natural_key != UNKNOWN_VALUE].copy()

    mask = pd.Series(True, index=result.index)
    for column in fallback_columns:
        if column in result.columns:
            values = result[column].map(_clean_string)
            mask &= values.notna() & (values != UNKNOWN_VALUE)

    return result.loc[mask].copy()


def _duplicate_check(
    dataframe: pd.DataFrame,
    key_columns: tuple[str, ...],
) -> DuplicateCheckResult:
    missing_columns = [column for column in key_columns if column not in dataframe.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"Reference data is missing key columns: {missing}")

    key_frame = dataframe.loc[:, list(key_columns)].copy()
    for column in key_columns:
        key_frame[column] = key_frame[column].map(_clean_string)

    complete_mask = key_frame.notna().all(axis=1)
    complete_keys = key_frame.loc[complete_mask]

    if complete_keys.empty:
        duplicate_row_count = 0
        duplicate_group_count = 0
    else:
        duplicate_row_count = int(complete_keys.duplicated(subset=list(key_columns)).sum())
        group_sizes = complete_keys.value_counts(subset=list(key_columns), dropna=False)
        duplicate_group_count = int((group_sizes > 1).sum())

    return DuplicateCheckResult(
        key_columns=key_columns,
        total_rows=len(dataframe),
        complete_key_rows=int(complete_mask.sum()),
        incomplete_key_rows=int((~complete_mask).sum()),
        duplicate_row_count=duplicate_row_count,
        duplicate_group_count=duplicate_group_count,
    )


def _label_conflicts(
    dataframe: pd.DataFrame,
    key_column: str,
    label_column: str,
) -> list[dict[str, Any]]:
    labels = dataframe[[key_column, label_column]].copy()
    labels[key_column] = labels[key_column].map(_clean_string)
    labels[label_column] = labels[label_column].map(_clean_string)
    labels = labels.dropna(subset=[key_column, label_column])

    conflicts: list[dict[str, Any]] = []
    for key_value, group in labels.groupby(key_column, sort=True):
        distinct_labels = sorted(group[label_column].dropna().unique())
        if len(distinct_labels) > 1:
            conflicts.append(
                {
                    key_column: key_value,
                    "distinct_label_count": len(distinct_labels),
                    label_column: "; ".join(distinct_labels[:5]),
                }
            )

    return conflicts


def _reference_values_with_labels(
    dataframe: pd.DataFrame,
    key_column: str,
    label_column: str,
) -> set[str]:
    values = dataframe[[key_column, label_column]].copy()
    values[key_column] = values[key_column].map(_clean_string)
    values[label_column] = values[label_column].map(_clean_string)
    values = values.dropna(subset=[key_column, label_column])
    return set(values[key_column])


def _reference_key_pairs_with_labels(
    dataframe: pd.DataFrame,
    first_key_column: str,
    second_key_column: str,
    label_column: str,
) -> set[tuple[str, str]]:
    values = dataframe[[first_key_column, second_key_column, label_column]].copy()
    values[first_key_column] = values[first_key_column].map(_clean_string)
    values[second_key_column] = values[second_key_column].map(_clean_string)
    values[label_column] = values[label_column].map(_clean_string)
    values = values.dropna(subset=[first_key_column, second_key_column, label_column])
    return set(zip(values[first_key_column], values[second_key_column]))


def _complete_key_set(
    dataframe: pd.DataFrame,
    key_columns: tuple[str, ...],
) -> set[tuple[str, ...]]:
    key_frame = dataframe.loc[:, list(key_columns)].copy()
    for column in key_columns:
        key_frame[column] = key_frame[column].map(_clean_string)
    key_frame = key_frame.dropna(subset=list(key_columns))
    return set(map(tuple, key_frame[list(key_columns)].itertuples(index=False, name=None)))


def _nunique_non_null(dataframe: pd.DataFrame, column: str) -> int:
    return int(dataframe[column].dropna().nunique())


def _report_duplicate_check(
    report: Report,
    label: str,
    result: DuplicateCheckResult,
) -> None:
    report.subheading(label)
    report.metric("total rows", result.total_rows)
    report.metric("complete key rows", result.complete_key_rows)
    report.metric("incomplete key rows", result.incomplete_key_rows)
    report.metric("duplicate row count", result.duplicate_row_count)
    report.metric("duplicate group count", result.duplicate_group_count)


def _report_sample_conflicts(
    report: Report,
    conflicts: list[dict[str, Any]],
    key_column: str,
    label_column: str,
) -> None:
    report.subheading("Sample Conflicts")
    if not conflicts:
        report.note("No label conflicts found.")
        return

    report.table(
        conflicts[:10],
        [key_column, "distinct_label_count", label_column],
    )


def _report_sample_dataframe(
    report: Report,
    title: str,
    dataframe: pd.DataFrame,
    columns: list[str],
) -> None:
    report.subheading(title)
    if dataframe.empty or not columns:
        report.note("No sample rows.")
        return

    sample = dataframe.loc[:, columns].head(10).copy()
    rows = sample.astype(object).where(pd.notna(sample), "").to_dict(orient="records")
    report.table(rows, columns)


def _existing_columns(dataframe: pd.DataFrame, columns: tuple[str, ...]) -> list[str]:
    return [column for column in columns if column in dataframe.columns]


def _headerless_columns(
    configured_columns: tuple[str, ...],
    column_count: int,
) -> list[str]:
    column_names = list(configured_columns[:column_count])
    for column_number in range(len(column_names) + 1, column_count + 1):
        column_names.append(f"COLUMN_{column_number}")
    return column_names


def _dataframe_to_markdown(dataframe: pd.DataFrame) -> list[str]:
    columns = [str(column) for column in dataframe.columns]
    lines = [
        "| " + " | ".join(_markdown_cell(column) for column in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]

    for row in dataframe.itertuples(index=False, name=None):
        lines.append(
            "| " + " | ".join(_markdown_cell(value) for value in row) + " |"
        )

    return lines


def _markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _normalize_label(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value).strip())
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_value).casefold()


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
        description="Check official reference files against IRISv2 DW dimensions."
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
