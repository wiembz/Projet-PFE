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
REPORT_PATH = PROJECT_ROOT / "docs" / "sinistre_contrat_matching_diagnostic.md"
SINISTRE_COLUMNS = (
    "NUMCNT",
    "NUMAVT",
    "NUMMAJ",
    "contrat_business_key",
    "DTSURV",
    "DEBEFFET",
    "FINEFFET",
    "NUMSNT",
    "GRNTSINI",
)
CONTRAT_COLUMNS = (
    "contrat_sk",
    "contrat_natural_key",
    "num_contrat",
    "num_avenant",
    "num_mise_a_jour",
    "date_debut_effet",
    "date_fin_effet",
    "date_debut_contrat",
    "date_fin_contrat",
)
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}


@dataclass(frozen=True)
class DiagnosticResults:
    input_count: int
    exact_matched_rows: int
    exact_unmatched_rows: int
    exact_matched_distinct_contracts: int
    exact_unmatched_distinct_contracts: int
    numcnt_exists_rows: int
    numcnt_missing_rows: int
    distinct_numcnt_missing: int
    avg_dim_rows_per_numcnt: float
    numcnt_numavt_matched_rows: int
    numcnt_numavt_unmatched_rows: int
    effective_matchable_rows: int
    effective_still_unmatched_rows: int
    effective_multiple_candidate_rows: int
    deterministic_fallback_count: int
    ambiguous_count: int
    no_candidate_count: int
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
    results = diagnose_sinistre_contrat_matching(args.etl_run_id)
    report = _build_report(results, args.etl_run_id)

    print(report.render_console())
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report.render_markdown(), encoding="utf-8")
    print(f"\n[OK] Markdown diagnostic written to {REPORT_PATH}")


def diagnose_sinistre_contrat_matching(etl_run_id: str) -> DiagnosticResults:
    _validate_etl_run_id(etl_run_id)
    sinistres = _read_sinistres(etl_run_id)
    contrats = _read_dim_contrat()

    _normalize_sinistres(sinistres)
    _normalize_contrats(contrats)

    exact_key_set = set(contrats["contrat_natural_key"].dropna())
    exact_match = sinistres["sinistre_contrat_key"].isin(exact_key_set)
    exact_unmatched = sinistres.loc[~exact_match].copy()

    dim_numcnt_counts = contrats.groupby("num_contrat", dropna=True).size()
    dim_numcnt_set = set(dim_numcnt_counts.index)
    numcnt_exists = sinistres["NUMCNT"].isin(dim_numcnt_set)

    dim_numcnt_numavt = set(
        zip(
            contrats["num_contrat"].dropna(),
            contrats.loc[contrats["num_contrat"].notna(), "num_avenant"],
        )
    )
    sinistre_numcnt_numavt = list(zip(sinistres["NUMCNT"], sinistres["NUMAVT"]))
    numcnt_numavt_match = pd.Series(
        [
            key[0] is not None
            and key[1] is not None
            and key in dim_numcnt_numavt
            for key in sinistre_numcnt_numavt
        ],
        index=sinistres.index,
    )

    candidate_counts = _effective_candidate_counts(exact_unmatched, contrats)
    effective_counts = pd.Series(0, index=exact_unmatched.index)
    if candidate_counts:
        effective_counts.loc[list(candidate_counts)] = list(candidate_counts.values())

    exact_unmatched = exact_unmatched.copy()
    exact_unmatched["numcnt_exists_in_dim_contrat"] = exact_unmatched["NUMCNT"].isin(
        dim_numcnt_set
    )
    exact_unmatched["candidate_contracts_by_numcnt"] = (
        exact_unmatched["NUMCNT"].map(dim_numcnt_counts).fillna(0).astype(int)
    )
    exact_unmatched["date_effective_candidate_contracts"] = effective_counts.astype(int)

    sample_rows = _sample_unmatched_rows(exact_unmatched)

    return DiagnosticResults(
        input_count=len(sinistres),
        exact_matched_rows=int(exact_match.sum()),
        exact_unmatched_rows=int((~exact_match).sum()),
        exact_matched_distinct_contracts=int(
            sinistres.loc[exact_match, "sinistre_contrat_key"].dropna().nunique()
        ),
        exact_unmatched_distinct_contracts=int(
            sinistres.loc[~exact_match, "sinistre_contrat_key"].dropna().nunique()
        ),
        numcnt_exists_rows=int(numcnt_exists.sum()),
        numcnt_missing_rows=int((~numcnt_exists).sum()),
        distinct_numcnt_missing=int(
            sinistres.loc[~numcnt_exists, "NUMCNT"].dropna().nunique()
        ),
        avg_dim_rows_per_numcnt=float(dim_numcnt_counts.mean())
        if not dim_numcnt_counts.empty
        else 0.0,
        numcnt_numavt_matched_rows=int(numcnt_numavt_match.sum()),
        numcnt_numavt_unmatched_rows=int((~numcnt_numavt_match).sum()),
        effective_matchable_rows=int((effective_counts > 0).sum()),
        effective_still_unmatched_rows=int((effective_counts == 0).sum()),
        effective_multiple_candidate_rows=int((effective_counts > 1).sum()),
        deterministic_fallback_count=int((effective_counts == 1).sum()),
        ambiguous_count=int((effective_counts > 1).sum()),
        no_candidate_count=int((effective_counts == 0).sum()),
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
                    date_debut_contrat,
                    date_fin_contrat
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
    for column in ("NUMCNT", "NUMAVT", "NUMMAJ", "contrat_business_key", "NUMSNT", "GRNTSINI"):
        dataframe[column] = dataframe[column].map(_clean_key_value)

    derived_key = _combine_key_parts(dataframe, ("NUMCNT", "NUMAVT", "NUMMAJ"))
    dataframe["sinistre_contrat_key"] = dataframe["contrat_business_key"].where(
        dataframe["contrat_business_key"].notna(),
        derived_key,
    )

    for column in ("DTSURV", "DEBEFFET", "FINEFFET"):
        dataframe[column] = dataframe[column].map(_to_date)


def _normalize_contrats(dataframe: pd.DataFrame) -> None:
    for column in (
        "contrat_natural_key",
        "num_contrat",
        "num_avenant",
        "num_mise_a_jour",
    ):
        dataframe[column] = dataframe[column].map(_clean_key_value)

    for column in (
        "date_debut_effet",
        "date_fin_effet",
        "date_debut_contrat",
        "date_fin_contrat",
    ):
        dataframe[column] = dataframe[column].map(_to_date)


def _effective_candidate_counts(
    exact_unmatched: pd.DataFrame,
    contrats: pd.DataFrame,
) -> dict[int, int]:
    counts = pd.Series(0, index=exact_unmatched.index, dtype="int64")
    candidate_sinistres = exact_unmatched.loc[
        exact_unmatched["NUMCNT"].notna() & exact_unmatched["DTSURV"].notna(),
        ["NUMCNT", "DTSURV"],
    ].copy()
    if candidate_sinistres.empty:
        return counts.to_dict()

    candidate_sinistres["_sinistre_index"] = candidate_sinistres.index
    candidate_sinistres["DTSURV"] = pd.to_datetime(candidate_sinistres["DTSURV"])

    candidate_contrats = contrats.loc[
        contrats["num_contrat"].notna() & contrats["date_debut_effet"].notna(),
        ["num_contrat", "contrat_sk", "date_debut_effet", "date_fin_effet"],
    ].copy()
    if candidate_contrats.empty:
        return counts.to_dict()

    candidate_contrats["date_debut_effet"] = pd.to_datetime(
        candidate_contrats["date_debut_effet"]
    )
    candidate_contrats["date_fin_effet"] = pd.to_datetime(
        candidate_contrats["date_fin_effet"]
    )

    merged = candidate_sinistres.merge(
        candidate_contrats,
        left_on="NUMCNT",
        right_on="num_contrat",
        how="inner",
    )
    if merged.empty:
        return counts.to_dict()

    effective_mask = (
        (merged["DTSURV"] >= merged["date_debut_effet"])
        & (
            merged["date_fin_effet"].isna()
            | (merged["DTSURV"] <= merged["date_fin_effet"])
        )
    )
    effective_counts = merged.loc[effective_mask].groupby("_sinistre_index").size()
    counts.loc[effective_counts.index] = effective_counts.astype("int64")

    return counts.to_dict()


def _sample_unmatched_rows(exact_unmatched: pd.DataFrame) -> list[dict[str, Any]]:
    columns = [
        "NUMSNT",
        "GRNTSINI",
        "NUMCNT",
        "NUMAVT",
        "NUMMAJ",
        "DTSURV",
        "contrat_business_key",
        "numcnt_exists_in_dim_contrat",
        "candidate_contracts_by_numcnt",
        "date_effective_candidate_contracts",
    ]
    sample = exact_unmatched.loc[:, columns].head(20).copy()
    sample["DTSURV"] = sample["DTSURV"].map(lambda value: value.isoformat() if value else None)
    return sample.to_dict(orient="records")


def _build_report(results: DiagnosticResults, etl_run_id: str) -> Report:
    report = Report()
    report.title("IRISv2 Sinistre-To-Contrat Matching Diagnostic")
    report.metric("ETL run id", etl_run_id)
    report.metric("input_count", results.input_count)

    report.section("1) Exact Key Match")
    report.metric("matched rows", results.exact_matched_rows)
    report.metric("unmatched rows", results.exact_unmatched_rows)
    report.metric("matched distinct contracts", results.exact_matched_distinct_contracts)
    report.metric(
        "unmatched distinct contracts",
        results.exact_unmatched_distinct_contracts,
    )

    report.section("2) NUMCNT Only Match")
    report.metric("rows where NUMCNT exists in dim_contrat", results.numcnt_exists_rows)
    report.metric(
        "rows where NUMCNT does not exist",
        results.numcnt_missing_rows,
    )
    report.metric("distinct NUMCNT missing", results.distinct_numcnt_missing)
    report.metric(
        "average number of dim_contrat rows per NUMCNT",
        f"{results.avg_dim_rows_per_numcnt:.2f}",
    )

    report.section("3) NUMCNT + NUMAVT Match")
    report.metric("matched rows", results.numcnt_numavt_matched_rows)
    report.metric("unmatched rows", results.numcnt_numavt_unmatched_rows)

    report.section("4) Date-Effective Match Candidate")
    report.metric(
        "rows matchable by NUMCNT + DTSURV effective period",
        results.effective_matchable_rows,
    )
    report.metric("rows still unmatched", results.effective_still_unmatched_rows)
    report.metric(
        "rows with multiple candidate contracts",
        results.effective_multiple_candidate_rows,
    )

    report.section("5) Best Fallback Candidate")
    report.metric(
        "deterministic_fallback_count",
        results.deterministic_fallback_count,
    )
    report.metric("ambiguous_count", results.ambiguous_count)
    report.metric("no_candidate_count", results.no_candidate_count)

    report.section("6) Samples")
    report.table(
        results.sample_rows,
        [
            "NUMSNT",
            "GRNTSINI",
            "NUMCNT",
            "NUMAVT",
            "NUMMAJ",
            "DTSURV",
            "contrat_business_key",
            "numcnt_exists_in_dim_contrat",
            "candidate_contracts_by_numcnt",
            "date_effective_candidate_contracts",
        ],
    )

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
        description="Diagnose Silver sinistre to DW contract matching."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id containing data/silver/<etl_run_id>/sinistres.parquet.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
