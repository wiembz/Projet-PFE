from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


SILVER_DIR = PROJECT_ROOT / "data" / "silver"
REPORT_PATH = PROJECT_ROOT / "docs" / "contrat_pair_uniqueness_diagnostic.md"
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}
SINISTRE_COLUMNS = (
    "NUMCNT",
    "NUMAVT",
    "NUMMAJ",
    "contrat_business_key",
    "NUMSNT",
    "GRNTSINI",
    "DTSURV",
)
CONTRAT_COLUMNS = (
    "contrat_sk",
    "contrat_natural_key",
    "num_contrat",
    "num_avenant",
    "num_mise_a_jour",
    "date_debut_effet",
    "date_fin_effet",
    "created_at",
)


@dataclass(frozen=True)
class PairSelection:
    candidate_num_mise_a_jour_list: str
    selected_max_num_mise_a_jour: str | None
    selected_contrat_sk: int | None
    is_deterministic: bool


@dataclass(frozen=True)
class DiagnosticResults:
    input_count: int
    total_distinct_pair_key: int
    pair_key_single_row_count: int
    pair_key_multi_row_count: int
    top_multi_nummaj_pairs: list[dict[str, Any]]
    exact_matched_rows: int
    exact_unmatched_rows: int
    no_pair_candidate_rows: int
    one_pair_candidate_rows: int
    multiple_pair_candidate_rows: int
    max_nummaj_deterministic_count: int
    exact_plus_pair_unique_matched_rows: int
    exact_plus_pair_max_nummaj_matched_rows: int
    remaining_unmatched_rows: int
    sample_rows: list[dict[str, Any]]


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
                    "This diagnostic is read-only. It reads Silver sinistres "
                    "and `iris_dw.dim_contrat`; it does not write to PostgreSQL."
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

    def table(self, rows: list[dict[str, Any]], columns: list[str]) -> None:
        if not rows:
            self.console_lines.append("No rows.")
            self.markdown_lines.append("No rows.")
            return

        dataframe = pd.DataFrame(rows, columns=columns)
        dataframe = dataframe.astype(object).where(pd.notna(dataframe), "")
        self.console_lines.append(dataframe.to_string(index=False))
        self.markdown_lines.extend(_dataframe_to_markdown(dataframe))

    def render_console(self) -> str:
        return "\n".join(self.console_lines)

    def render_markdown(self) -> str:
        return "\n".join(self.markdown_lines).rstrip() + "\n"


def main() -> None:
    args = _parse_args()
    results = diagnose_contrat_pair_uniqueness(args.etl_run_id)
    report = _build_report(results, args.etl_run_id)

    print(report.render_console())
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report.render_markdown(), encoding="utf-8")
    print(f"\n[OK] Markdown diagnostic written to {REPORT_PATH}")


def diagnose_contrat_pair_uniqueness(etl_run_id: str) -> DiagnosticResults:
    _validate_etl_run_id(etl_run_id)
    sinistres = _read_sinistres(etl_run_id)
    contrats = _read_dim_contrat()

    _normalize_sinistres(sinistres)
    _normalize_contrats(contrats)

    pair_counts = contrats.groupby("pair_key", dropna=True).size()
    pair_selections = _build_pair_selections(contrats, pair_counts)
    top_multi_nummaj_pairs = _top_multi_nummaj_pairs(contrats)

    exact_keys = set(contrats["contrat_natural_key"].dropna())
    exact_match = sinistres["exact_contrat_key"].isin(exact_keys)
    exact_unmatched = sinistres.loc[~exact_match].copy()

    candidate_counts = (
        exact_unmatched["pair_key"].map(pair_counts).fillna(0).astype("int64")
    )
    no_pair_candidate = candidate_counts.eq(0)
    one_pair_candidate = candidate_counts.eq(1)
    multiple_pair_candidate = candidate_counts.gt(1)

    deterministic_pair_keys = {
        pair_key
        for pair_key, selection in pair_selections.items()
        if selection.is_deterministic
    }
    deterministic_max_mask = (
        multiple_pair_candidate
        & exact_unmatched["pair_key"].isin(deterministic_pair_keys)
    )

    sample_rows = _sample_multiple_pair_rows(
        exact_unmatched.loc[multiple_pair_candidate].copy(),
        pair_selections,
    )

    exact_matched_rows = int(exact_match.sum())
    one_pair_candidate_rows = int(one_pair_candidate.sum())
    max_nummaj_deterministic_count = int(deterministic_max_mask.sum())
    exact_plus_pair_unique = exact_matched_rows + one_pair_candidate_rows
    exact_plus_pair_max = exact_plus_pair_unique + max_nummaj_deterministic_count

    return DiagnosticResults(
        input_count=len(sinistres),
        total_distinct_pair_key=int(pair_counts.shape[0]),
        pair_key_single_row_count=int(pair_counts.eq(1).sum()),
        pair_key_multi_row_count=int(pair_counts.gt(1).sum()),
        top_multi_nummaj_pairs=top_multi_nummaj_pairs,
        exact_matched_rows=exact_matched_rows,
        exact_unmatched_rows=int((~exact_match).sum()),
        no_pair_candidate_rows=int(no_pair_candidate.sum()),
        one_pair_candidate_rows=one_pair_candidate_rows,
        multiple_pair_candidate_rows=int(multiple_pair_candidate.sum()),
        max_nummaj_deterministic_count=max_nummaj_deterministic_count,
        exact_plus_pair_unique_matched_rows=exact_plus_pair_unique,
        exact_plus_pair_max_nummaj_matched_rows=exact_plus_pair_max,
        remaining_unmatched_rows=len(sinistres) - exact_plus_pair_max,
        sample_rows=sample_rows,
    )


def _read_sinistres(etl_run_id: str) -> pd.DataFrame:
    input_file = SILVER_DIR / etl_run_id / "sinistres.parquet"
    if not input_file.exists():
        raise FileNotFoundError(f"Silver sinistres file not found: {input_file}")

    dataframe = pd.read_parquet(input_file, columns=list(SINISTRE_COLUMNS))
    missing_columns = [
        column for column in SINISTRE_COLUMNS if column not in dataframe.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"Silver sinistres file is missing columns: {missing}")
    return dataframe


def _read_dim_contrat() -> pd.DataFrame:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            columns = _get_table_columns(cur, "dim_contrat")
            missing_columns = [column for column in CONTRAT_COLUMNS if column not in columns]
            if missing_columns:
                missing = ", ".join(missing_columns)
                raise RuntimeError(f"iris_dw.dim_contrat is missing columns: {missing}")

            cur.execute(
                """
                SELECT
                    contrat_sk,
                    contrat_natural_key,
                    num_contrat,
                    num_avenant,
                    num_mise_a_jour,
                    date_debut_effet,
                    date_fin_effet,
                    created_at
                FROM iris_dw.dim_contrat
                WHERE contrat_sk <> 0
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return pd.DataFrame(rows, columns=list(CONTRAT_COLUMNS))


def _get_table_columns(cur: Any, table_name: str) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'iris_dw'
          AND table_name = %s
        """,
        (table_name,),
    )
    columns = {row[0] for row in cur.fetchall()}
    if not columns:
        raise RuntimeError(f"iris_dw.{table_name} does not exist")
    return columns


def _normalize_sinistres(dataframe: pd.DataFrame) -> None:
    for column in (
        "NUMCNT",
        "NUMAVT",
        "NUMMAJ",
        "contrat_business_key",
        "NUMSNT",
        "GRNTSINI",
    ):
        dataframe[column] = dataframe[column].map(_clean_key_value)

    derived_exact_key = _combine_key_parts(dataframe, ("NUMCNT", "NUMAVT", "NUMMAJ"))
    dataframe["exact_contrat_key"] = dataframe["contrat_business_key"].where(
        dataframe["contrat_business_key"].notna(),
        derived_exact_key,
    )
    dataframe["pair_key"] = _combine_key_parts(dataframe, ("NUMCNT", "NUMAVT"))
    dataframe["DTSURV"] = dataframe["DTSURV"].map(_to_date)


def _normalize_contrats(dataframe: pd.DataFrame) -> None:
    for column in (
        "contrat_natural_key",
        "num_contrat",
        "num_avenant",
        "num_mise_a_jour",
    ):
        dataframe[column] = dataframe[column].map(_clean_key_value)

    dataframe["pair_key"] = _combine_key_parts(
        dataframe,
        ("num_contrat", "num_avenant"),
    )
    dataframe["num_mise_a_jour_numeric"] = pd.to_numeric(
        dataframe["num_mise_a_jour"],
        errors="coerce",
    )


def _build_pair_selections(
    contrats: pd.DataFrame,
    pair_counts: pd.Series,
) -> dict[str, PairSelection]:
    multi_pair_keys = set(pair_counts.loc[pair_counts.gt(1)].index)
    selections: dict[str, PairSelection] = {}

    for pair_key, group in contrats.loc[contrats["pair_key"].isin(multi_pair_keys)].groupby(
        "pair_key",
        sort=False,
    ):
        candidate_values = sorted(
            {value for value in group["num_mise_a_jour"].tolist() if value is not None},
            key=_sort_key_for_text_number,
        )
        numeric_values = group["num_mise_a_jour_numeric"].dropna()
        if numeric_values.empty:
            selections[pair_key] = PairSelection(
                candidate_num_mise_a_jour_list="; ".join(candidate_values),
                selected_max_num_mise_a_jour=None,
                selected_contrat_sk=None,
                is_deterministic=False,
            )
            continue

        max_numeric = numeric_values.max()
        max_rows = group.loc[group["num_mise_a_jour_numeric"].eq(max_numeric)]
        if len(max_rows) == 1:
            selected = max_rows.iloc[0]
            selections[pair_key] = PairSelection(
                candidate_num_mise_a_jour_list="; ".join(candidate_values),
                selected_max_num_mise_a_jour=selected["num_mise_a_jour"],
                selected_contrat_sk=int(selected["contrat_sk"]),
                is_deterministic=True,
            )
        else:
            selections[pair_key] = PairSelection(
                candidate_num_mise_a_jour_list="; ".join(candidate_values),
                selected_max_num_mise_a_jour=str(int(max_numeric))
                if float(max_numeric).is_integer()
                else str(max_numeric),
                selected_contrat_sk=None,
                is_deterministic=False,
            )

    return selections


def _top_multi_nummaj_pairs(contrats: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pair_key, group in contrats.groupby("pair_key", dropna=True, sort=False):
        values = sorted(
            {value for value in group["num_mise_a_jour"].tolist() if value is not None},
            key=_sort_key_for_text_number,
        )
        if len(values) <= 1:
            continue

        rows.append(
            {
                "pair_key": pair_key,
                "dim_contrat_rows": int(len(group)),
                "distinct_num_mise_a_jour": int(len(values)),
                "num_mise_a_jour_values": "; ".join(values[:20]),
            }
        )

    rows.sort(
        key=lambda row: (
            row["dim_contrat_rows"],
            row["distinct_num_mise_a_jour"],
            row["pair_key"],
        ),
        reverse=True,
    )
    return rows[:20]


def _sample_multiple_pair_rows(
    exact_unmatched_multiple: pd.DataFrame,
    pair_selections: dict[str, PairSelection],
) -> list[dict[str, Any]]:
    if exact_unmatched_multiple.empty:
        return []

    sample = exact_unmatched_multiple.head(20).copy()
    rows: list[dict[str, Any]] = []
    for row in sample.itertuples(index=False):
        row_dict = row._asdict()
        selection = pair_selections.get(row_dict["pair_key"])
        rows.append(
            {
                "NUMSNT": row_dict["NUMSNT"],
                "GRNTSINI": row_dict["GRNTSINI"],
                "NUMCNT": row_dict["NUMCNT"],
                "NUMAVT": row_dict["NUMAVT"],
                "NUMMAJ": row_dict["NUMMAJ"],
                "candidate_num_mise_a_jour_list": (
                    selection.candidate_num_mise_a_jour_list if selection else ""
                ),
                "selected_max_num_mise_a_jour": (
                    selection.selected_max_num_mise_a_jour if selection else None
                ),
                "selected_contrat_sk": (
                    selection.selected_contrat_sk if selection else None
                ),
            }
        )

    return rows


def _build_report(results: DiagnosticResults, etl_run_id: str) -> Report:
    report = Report()
    report.title("IRISv2 Contrat Pair Uniqueness Diagnostic")
    report.metric("ETL run id", etl_run_id)
    report.metric("input_count", results.input_count)

    report.section("1) Pair Uniqueness In dim_contrat")
    report.metric("total distinct pair_key", results.total_distinct_pair_key)
    report.metric(
        "pair_key with exactly one dim_contrat row",
        results.pair_key_single_row_count,
    )
    report.metric(
        "pair_key with multiple dim_contrat rows",
        results.pair_key_multi_row_count,
    )
    report.table(
        results.top_multi_nummaj_pairs,
        [
            "pair_key",
            "dim_contrat_rows",
            "distinct_num_mise_a_jour",
            "num_mise_a_jour_values",
        ],
    )

    report.section("2) Impact On Exact-Unmatched Sinistres")
    report.metric("exact_unmatched_rows", results.exact_unmatched_rows)
    report.metric("rows with no pair candidate", results.no_pair_candidate_rows)
    report.metric(
        "rows with exactly one pair candidate",
        results.one_pair_candidate_rows,
    )
    report.metric(
        "rows with multiple pair candidates",
        results.multiple_pair_candidate_rows,
    )

    report.section("3) Candidate Deterministic Rule")
    report.metric(
        "deterministic fallback using max numeric num_mise_a_jour",
        results.max_nummaj_deterministic_count,
    )
    report.table(
        results.sample_rows,
        [
            "NUMSNT",
            "GRNTSINI",
            "NUMCNT",
            "NUMAVT",
            "NUMMAJ",
            "candidate_num_mise_a_jour_list",
            "selected_max_num_mise_a_jour",
            "selected_contrat_sk",
        ],
    )

    report.section("4) Compare Match Coverage")
    report.metric("exact only matched rows", results.exact_matched_rows)
    report.metric(
        "exact + pair unique fallback matched rows",
        results.exact_plus_pair_unique_matched_rows,
    )
    report.metric(
        "exact + pair max-nummaj fallback matched rows",
        results.exact_plus_pair_max_nummaj_matched_rows,
    )
    report.metric("remaining unmatched rows", results.remaining_unmatched_rows)

    return report


def _combine_key_parts(dataframe: pd.DataFrame, columns: tuple[str, ...]) -> pd.Series:
    null_key_mask = dataframe[list(columns)].isna().any(axis=1)
    combined = dataframe[columns[0]].astype("string")
    for column in columns[1:]:
        combined = combined + "|" + dataframe[column].astype("string")
    return combined.mask(null_key_mask, pd.NA)


def _clean_key_value(value: Any) -> str | None:
    if pd.isna(value):
        return None

    cleaned = str(value).strip()
    if cleaned.casefold() in NULL_MARKERS:
        return None

    if cleaned.endswith(".0"):
        prefix = cleaned[:-2]
        if prefix and prefix.lstrip("+-").isdigit():
            cleaned = prefix

    return cleaned


def _to_date(value: Any) -> date | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text_value = str(value).strip()
    if text_value.casefold() in NULL_MARKERS:
        return None

    if text_value.endswith(".0") and text_value[:-2].isdigit():
        text_value = text_value[:-2]

    formats = ("%Y-%m-%d", "%Y%m%d", "%d/%m/%Y")
    for date_format in formats:
        try:
            return datetime.strptime(text_value, date_format).date()
        except ValueError:
            continue

    parsed = pd.to_datetime(text_value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _sort_key_for_text_number(value: str) -> tuple[int, float | str]:
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return (1, value)
    return (0, float(numeric_value))


def _dataframe_to_markdown(dataframe: pd.DataFrame) -> list[str]:
    columns = [str(column) for column in dataframe.columns]
    lines = [
        "| " + " | ".join(_markdown_cell(column) for column in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]

    for row in dataframe.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(_markdown_cell(value) for value in row) + " |")

    return lines


def _markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _validate_etl_run_id(etl_run_id: str) -> None:
    if etl_run_id != etl_run_id.strip():
        raise ValueError("--etl-run-id cannot contain leading or trailing spaces")
    if not etl_run_id:
        raise ValueError("--etl-run-id cannot be empty")
    if any(part in etl_run_id for part in ("/", "\\", "..")):
        raise ValueError("--etl-run-id must be a single run folder name")
    if etl_run_id.endswith("."):
        raise ValueError("--etl-run-id cannot end with a dot")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnose NUMCNT + NUMAVT fallback uniqueness for sinistres."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id containing data/silver/<etl_run_id>/sinistres.parquet.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
