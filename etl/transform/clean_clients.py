from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"

BRONZE_METADATA_COLUMNS = (
    "etl_run_id",
    "source_name",
    "source_file",
    "source_row_number",
    "source_file_hash",
    "ingested_at",
)
KEY_COLUMNS = ("CNAT", "NUMPERS")
DATE_COLUMNS = ("DATE_NAISS", "DEBCNT")
NULL_MARKERS = {"", "0", "nan", "none"}
HELPER_COLUMNS = {"_original_order", "_completeness_score"}


@dataclass(frozen=True)
class CleanStats:
    input_count: int
    output_count: int
    duplicate_count: int
    null_key_count: int
    output_file: Path


def main() -> None:
    args = _parse_args()
    stats = clean_clients(args.etl_run_id)
    print(f"input_count={stats.input_count}")
    print(f"output_count={stats.output_count}")
    print(f"duplicate_count={stats.duplicate_count}")
    print(f"null_key_count={stats.null_key_count}")
    print(f"output_file={stats.output_file}")


def clean_clients(etl_run_id: str) -> CleanStats:
    _validate_etl_run_id(etl_run_id)

    input_file = BRONZE_DIR / etl_run_id / "clients.parquet"
    output_file = SILVER_DIR / etl_run_id / "clients.parquet"

    if not input_file.exists():
        raise FileNotFoundError(f"Bronze clients file not found: {input_file}")

    dataframe = pd.read_parquet(input_file)
    input_count = len(dataframe)

    _assert_required_columns(dataframe)
    cleaned = _clean_client_dataframe(dataframe)

    null_key_mask = cleaned["client_business_key"].isna()
    null_key_count = int(null_key_mask.sum())
    keyed = cleaned.loc[~null_key_mask].copy()

    deduplicated = _deduplicate_clients(keyed)
    duplicate_count = len(keyed) - len(deduplicated)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    deduplicated.to_parquet(output_file, index=False, engine="pyarrow")

    return CleanStats(
        input_count=input_count,
        output_count=len(deduplicated),
        duplicate_count=duplicate_count,
        null_key_count=null_key_count,
        output_file=output_file,
    )


def _clean_client_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned = dataframe.copy()
    cleaned["_original_order"] = range(len(cleaned))

    _strip_text_columns(cleaned)
    _nullify_business_markers(cleaned)
    _keep_key_columns_as_strings(cleaned)
    _convert_date_columns(cleaned)
    _normalize_domain_columns(cleaned)
    _add_client_business_key(cleaned)

    return cleaned


def _strip_text_columns(dataframe: pd.DataFrame) -> None:
    text_columns = dataframe.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        if column in BRONZE_METADATA_COLUMNS or column in HELPER_COLUMNS:
            continue
        dataframe[column] = dataframe[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )


def _nullify_business_markers(dataframe: pd.DataFrame) -> None:
    for column in _business_columns(dataframe):
        if column in HELPER_COLUMNS:
            continue
        marker_mask = dataframe[column].map(_is_null_marker)
        dataframe.loc[marker_mask, column] = pd.NA


def _keep_key_columns_as_strings(dataframe: pd.DataFrame) -> None:
    for column in KEY_COLUMNS:
        dataframe[column] = dataframe[column].astype("string")


def _convert_date_columns(dataframe: pd.DataFrame) -> None:
    for column in DATE_COLUMNS:
        if column in dataframe.columns:
            dataframe[column] = parse_iris_date(dataframe[column])


def _normalize_domain_columns(dataframe: pd.DataFrame) -> None:
    if "SEXE" in dataframe.columns:
        dataframe["SEXE"] = normalize_sexe(dataframe["SEXE"])


def _add_client_business_key(dataframe: pd.DataFrame) -> None:
    key_mask = dataframe["CNAT"].notna() & dataframe["NUMPERS"].notna()
    business_key = pd.Series(pd.NA, index=dataframe.index, dtype="string")
    business_key.loc[key_mask] = (
        dataframe.loc[key_mask, "CNAT"].astype("string")
        + "|"
        + dataframe.loc[key_mask, "NUMPERS"].astype("string")
    )

    insert_at = dataframe.columns.get_loc("NUMPERS") + 1
    dataframe.insert(insert_at, "client_business_key", business_key)


def _deduplicate_clients(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe.drop(columns=list(HELPER_COLUMNS & set(dataframe.columns)))

    business_columns = [
        column
        for column in dataframe.columns
        if column not in BRONZE_METADATA_COLUMNS and column not in HELPER_COLUMNS
    ]
    dataframe["_completeness_score"] = dataframe[business_columns].notna().sum(axis=1)

    sort_columns = ["client_business_key", "_completeness_score", "_original_order"]
    sorted_frame = dataframe.sort_values(
        by=sort_columns,
        ascending=[True, False, True],
        kind="mergesort",
    )

    deduplicated = sorted_frame.drop_duplicates(
        subset=["client_business_key"],
        keep="first",
    ).sort_values(by="_original_order", kind="mergesort")

    return deduplicated.drop(columns=["_original_order", "_completeness_score"])


def parse_iris_date(series: pd.Series) -> pd.Series:
    """
    Parse strict des dates IRIS.
    Formats acceptes :
    - YYYYMMDD
    - DD/MM/YYYY
    - YYYY-MM-DD

    Dates hors plage metier [1900, 2100] => NULL.
    """
    s = series.astype("string").str.strip()

    s = s.replace(
        {
            "": pd.NA,
            "0": pd.NA,
            "00": pd.NA,
            "00000000": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
            "NaT": pd.NA,
            "<NA>": pd.NA,
        }
    )

    parsed = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")

    # YYYYMMDD
    mask_yyyymmdd = s.str.fullmatch(r"\d{8}", na=False)
    years_yyyymmdd = pd.to_numeric(s.str.slice(0, 4), errors="coerce")
    mask_yyyymmdd_valid = mask_yyyymmdd & years_yyyymmdd.between(1900, 2100)

    parsed.loc[mask_yyyymmdd_valid] = pd.to_datetime(
        s.loc[mask_yyyymmdd_valid],
        format="%Y%m%d",
        errors="coerce",
    )

    # DD/MM/YYYY
    mask_ddmmyyyy = s.str.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", na=False)
    years_ddmmyyyy = pd.to_numeric(s.str[-4:], errors="coerce")
    mask_ddmmyyyy_valid = mask_ddmmyyyy & years_ddmmyyyy.between(1900, 2100)

    parsed.loc[mask_ddmmyyyy_valid] = pd.to_datetime(
        s.loc[mask_ddmmyyyy_valid],
        format="%d/%m/%Y",
        errors="coerce",
    )

    # YYYY-MM-DD
    mask_yyyy_mm_dd = s.str.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}", na=False)
    years_yyyy_mm_dd = pd.to_numeric(s.str.slice(0, 4), errors="coerce")
    mask_yyyy_mm_dd_valid = mask_yyyy_mm_dd & years_yyyy_mm_dd.between(1900, 2100)

    parsed.loc[mask_yyyy_mm_dd_valid] = pd.to_datetime(
        s.loc[mask_yyyy_mm_dd_valid],
        format="%Y-%m-%d",
        errors="coerce",
    )

    # Filtre final metier
    parsed = parsed.where(parsed.dt.year.between(1900, 2100))

    return parsed.dt.date


def normalize_sexe(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.strip().str.upper()
    return s.where(s.isin(["M", "F"]), pd.NA)


def _is_null_marker(value: object) -> bool:
    if pd.isna(value):
        return True
    if isinstance(value, str):
        return value.strip().lower() in NULL_MARKERS
    return False


def _business_columns(dataframe: pd.DataFrame) -> list[str]:
    return [
        column
        for column in dataframe.columns
        if column not in BRONZE_METADATA_COLUMNS
    ]


def _assert_required_columns(dataframe: pd.DataFrame) -> None:
    missing_metadata = [
        column for column in BRONZE_METADATA_COLUMNS if column not in dataframe.columns
    ]
    if missing_metadata:
        missing = ", ".join(missing_metadata)
        raise ValueError(f"Bronze clients file is missing metadata columns: {missing}")

    missing_keys = [column for column in KEY_COLUMNS if column not in dataframe.columns]
    if missing_keys:
        missing = ", ".join(missing_keys)
        raise ValueError(f"Bronze clients file is missing key columns: {missing}")


def _validate_etl_run_id(etl_run_id: str) -> None:
    if not etl_run_id.strip():
        raise ValueError("--etl-run-id cannot be empty")
    if any(part in etl_run_id for part in ("/", "\\", "..")):
        raise ValueError("--etl-run-id must be a single run folder name")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean Bronze clients parquet into Silver clients parquet."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id containing data/bronze/<etl_run_id>/clients.parquet",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
