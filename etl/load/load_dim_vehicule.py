from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


SILVER_DIR = PROJECT_ROOT / "data" / "silver"
TARGET_SCHEMA = "iris_dw"
TARGET_TABLE = "dim_vehicule"
SOURCE_NATURAL_KEY = "vehicule_natural_key"
SOURCE_SYSTEM_VALUE = "Sinistres.xlsx/FicheVoitureStafim.xlsx"
TARGET_KEY_CANDIDATES = (
    "vehicule_natural_key",
    "vehicule_business_key",
)
NEVER_INSERT_COLUMNS = {"vehicule_sk", "created_at", "updated_at"}
NULL_MARKERS = {"", "nan", "none", "<na>", "0"}
SINISTRES_FILE = "sinistres.parquet"
STAFIM_FILE = "fiche_voiture_stafim.parquet"
STAFIM_VIN_COLUMN = "V.I.N "
STAFIM_MOTORISATION_COLUMN = " [MOTORISATION]"
STAFIM_KILOMETRAGE_COLUMN = "KILOMETRAGE"

SOURCE_TO_TARGET_CANDIDATES = {
    SOURCE_NATURAL_KEY: TARGET_KEY_CANDIDATES,
    "immatriculation": ("immatriculation", "numero_immatriculation"),
    "vin": ("vin",),
    "motorisation": ("motorisation",),
    "kilometrage": ("kilometrage",),
    "NUMRISQ": ("numero_risque", "numrisq"),
    "source_system": ("source_system",),
}


@dataclass(frozen=True)
class LoadStats:
    input_count: int
    distinct_vehicule_count: int
    null_key_count: int
    loaded_count: int
    target_count: int


def main() -> None:
    args = _parse_args()
    stats = load_dim_vehicule(args.etl_run_id)
    print(f"input_count={stats.input_count}")
    print(f"distinct_vehicule_count={stats.distinct_vehicule_count}")
    print(f"null_key_count={stats.null_key_count}")
    print(f"loaded_count={stats.loaded_count}")
    print(f"target_count={stats.target_count}")


def load_dim_vehicule(etl_run_id: str) -> LoadStats:
    _validate_etl_run_id(etl_run_id)

    dataframe = _read_inputs(etl_run_id)
    input_count = len(dataframe)
    vehicule_rows, null_key_count = _build_distinct_vehicule_rows(dataframe)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_columns = _get_table_columns(cur)
            key_column = _resolve_target_key_column(table_columns)
            _assert_key_conflict_target(cur, key_column)

            column_mapping = _build_column_mapping(table_columns)
            rows = _build_load_rows(vehicule_rows, column_mapping)
            loaded_count = _upsert_dim_vehicule_rows(
                cur,
                rows,
                key_column,
                table_columns,
            )
            target_count = _count_target_rows(cur)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return LoadStats(
        input_count=input_count,
        distinct_vehicule_count=len(vehicule_rows),
        null_key_count=null_key_count,
        loaded_count=loaded_count,
        target_count=target_count,
    )


def _read_inputs(etl_run_id: str) -> pd.DataFrame:
    input_dir = SILVER_DIR / etl_run_id
    frames: list[pd.DataFrame] = []
    missing_files: list[Path] = []

    sinistres_file = input_dir / SINISTRES_FILE
    if sinistres_file.exists():
        sinistres = pd.read_parquet(sinistres_file)
        if "vehicule_business_key" not in sinistres.columns:
            raise RuntimeError("Silver sinistres file is missing vehicule_business_key")
        frames.append(_extract_sinistres_rows(sinistres))
    else:
        missing_files.append(sinistres_file)

    stafim_file = input_dir / STAFIM_FILE
    if stafim_file.exists():
        stafim = pd.read_parquet(stafim_file)
        if "vehicule_business_key" not in stafim.columns:
            raise RuntimeError(
                "Silver fiche_voiture_stafim file is missing vehicule_business_key"
            )
        frames.append(_extract_stafim_rows(stafim))
    else:
        missing_files.append(stafim_file)

    if not frames:
        missing = "\n".join(str(path) for path in missing_files)
        raise FileNotFoundError(f"Silver vehicle input files not found:\n{missing}")

    return pd.concat(frames, ignore_index=True)


def _extract_sinistres_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    extracted = pd.DataFrame(index=dataframe.index)
    extracted["vehicule_business_key"] = dataframe["vehicule_business_key"]
    extracted["immatriculation"] = dataframe.get("IMMAT", dataframe["vehicule_business_key"])
    if "NUMRISQ" in dataframe.columns:
        extracted["NUMRISQ"] = dataframe["NUMRISQ"]
    extracted["source_priority"] = 0
    extracted["source_system"] = SOURCE_SYSTEM_VALUE
    return extracted


def _extract_stafim_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    extracted = pd.DataFrame(index=dataframe.index)
    extracted["vehicule_business_key"] = dataframe["vehicule_business_key"]
    extracted["immatriculation"] = dataframe["vehicule_business_key"]

    if STAFIM_VIN_COLUMN in dataframe.columns:
        extracted["vin"] = dataframe[STAFIM_VIN_COLUMN]
    if STAFIM_MOTORISATION_COLUMN in dataframe.columns:
        extracted["motorisation"] = dataframe[STAFIM_MOTORISATION_COLUMN]
    if STAFIM_KILOMETRAGE_COLUMN in dataframe.columns:
        extracted["kilometrage"] = dataframe[STAFIM_KILOMETRAGE_COLUMN]

    extracted["source_priority"] = 1
    extracted["source_system"] = SOURCE_SYSTEM_VALUE
    return extracted


def _build_distinct_vehicule_rows(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    vehicules = dataframe.copy()
    vehicules["vehicule_business_key"] = normalize_vehicle_key(
        vehicules["vehicule_business_key"]
    )
    vehicules["immatriculation"] = normalize_vehicle_key(vehicules["immatriculation"])

    if "vin" in vehicules.columns:
        vehicules["vin"] = normalize_identifier(vehicules["vin"])
    if "motorisation" in vehicules.columns:
        vehicules["motorisation"] = clean_nullable_string(vehicules["motorisation"])
    if "NUMRISQ" in vehicules.columns:
        vehicules["NUMRISQ"] = clean_nullable_string(vehicules["NUMRISQ"])
    if "kilometrage" in vehicules.columns:
        vehicules["kilometrage"] = pd.to_numeric(vehicules["kilometrage"], errors="coerce")

    null_key_count = int(vehicules["vehicule_business_key"].isna().sum())
    vehicules = vehicules.loc[vehicules["vehicule_business_key"].notna()].copy()
    vehicules[SOURCE_NATURAL_KEY] = vehicules["vehicule_business_key"]

    sort_columns = [SOURCE_NATURAL_KEY, "source_priority"]
    vehicules = vehicules.sort_values(
        sort_columns,
        ascending=[True, False],
        kind="mergesort",
    )

    value_columns = [
        column
        for column in (
            SOURCE_NATURAL_KEY,
            "immatriculation",
            "vin",
            "motorisation",
            "kilometrage",
            "NUMRISQ",
            "source_system",
        )
        if column in vehicules.columns
    ]

    distinct_rows: list[dict[str, Any]] = []
    for _, group in vehicules.groupby(SOURCE_NATURAL_KEY, sort=False):
        row: dict[str, Any] = {}
        for column in value_columns:
            row[column] = first_non_null(group[column])
        distinct_rows.append(row)

    return pd.DataFrame(distinct_rows), null_key_count


def normalize_vehicle_key(series: pd.Series) -> pd.Series:
    normalized = series.astype("string").str.strip().str.upper()
    normalized = normalized.str.replace(r"\s+", "", regex=True)
    normalized = normalized.mask(normalized.str.lower().isin(NULL_MARKERS), pd.NA)
    return normalized


def normalize_identifier(series: pd.Series) -> pd.Series:
    normalized = series.astype("string").str.strip().str.upper()
    normalized = normalized.str.replace(r"\s+", "", regex=True)
    normalized = normalized.mask(normalized.str.lower().isin(NULL_MARKERS), pd.NA)
    return normalized


def clean_nullable_string(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.strip()
    return cleaned.mask(cleaned.str.lower().isin(NULL_MARKERS), pd.NA)


def first_non_null(series: pd.Series) -> Any:
    non_null = series.dropna()
    if non_null.empty:
        return None
    return non_null.iloc[0]


def _get_table_columns(cur: Any) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %(schema)s
          AND table_name = %(table)s
        """,
        {
            "schema": TARGET_SCHEMA,
            "table": TARGET_TABLE,
        },
    )
    columns = {row[0] for row in cur.fetchall()}
    if not columns:
        raise RuntimeError(f"{TARGET_SCHEMA}.{TARGET_TABLE} does not exist")
    return columns


def _resolve_target_key_column(table_columns: set[str]) -> str:
    for candidate in TARGET_KEY_CANDIDATES:
        if candidate in table_columns:
            return candidate
    candidates = ", ".join(TARGET_KEY_CANDIDATES)
    raise RuntimeError(
        f"{TARGET_SCHEMA}.{TARGET_TABLE} is missing required natural key "
        f"column; expected one of: {candidates}"
    )


def _assert_key_conflict_target(cur: Any, key_column: str) -> None:
    cur.execute(
        """
        SELECT 1
        FROM pg_constraint c
        JOIN pg_namespace n
          ON n.oid = c.connamespace
        JOIN pg_class t
          ON t.oid = c.conrelid
        JOIN pg_attribute a
          ON a.attrelid = t.oid
         AND a.attnum = c.conkey[1]
        WHERE n.nspname = %(schema)s
          AND t.relname = %(table)s
          AND c.contype IN ('p', 'u')
          AND array_length(c.conkey, 1) = 1
          AND a.attname = %(key_column)s
        LIMIT 1
        """,
        {
            "schema": TARGET_SCHEMA,
            "table": TARGET_TABLE,
            "key_column": key_column,
        },
    )
    if cur.fetchone() is None:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} must have a primary or unique "
            f"constraint on {key_column} for idempotent loading"
        )


def _build_column_mapping(table_columns: set[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    insertable_columns = table_columns - NEVER_INSERT_COLUMNS

    for source_column, target_candidates in SOURCE_TO_TARGET_CANDIDATES.items():
        for target_column in target_candidates:
            if target_column in insertable_columns:
                mapping[source_column] = target_column
                break

    if SOURCE_NATURAL_KEY not in mapping:
        raise RuntimeError(
            f"No insertable target natural key column found in "
            f"{TARGET_SCHEMA}.{TARGET_TABLE}"
        )

    return mapping


def _build_load_rows(
    dataframe: pd.DataFrame,
    column_mapping: dict[str, str],
) -> list[dict[str, Any]]:
    load_frame = pd.DataFrame(index=dataframe.index)

    for source_column, target_column in column_mapping.items():
        if source_column not in dataframe.columns:
            continue
        load_frame[target_column] = dataframe[source_column]

    load_frame = load_frame.astype(object).where(pd.notna(load_frame), None)
    return load_frame.to_dict(orient="records")


def _upsert_dim_vehicule_rows(
    cur: Any,
    rows: list[dict[str, Any]],
    key_column: str,
    table_columns: set[str],
) -> int:
    if not rows:
        return 0

    columns = list(rows[0].keys())
    update_columns = [column for column in columns if column != key_column]

    assignments = [
        sql.SQL("{} = EXCLUDED.{}").format(
            sql.Identifier(column),
            sql.Identifier(column),
        )
        for column in update_columns
    ]
    if "updated_at" in table_columns:
        assignments.append(sql.SQL("updated_at = now()"))

    query = sql.SQL(
        """
        INSERT INTO {}.{} ({})
        VALUES ({})
        ON CONFLICT ({}) DO UPDATE
        SET {}
        """
    ).format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        sql.SQL(", ").join(sql.Placeholder(column) for column in columns),
        sql.Identifier(key_column),
        sql.SQL(", ").join(assignments),
    )

    cur.executemany(query, rows)
    return cur.rowcount if cur.rowcount >= 0 else len(rows)


def _count_target_rows(cur: Any) -> int:
    query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
    )
    cur.execute(query)
    return int(cur.fetchone()[0])


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
        description="Load Silver vehicles into iris_dw.dim_vehicule."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help=(
            "ETL run id containing sinistres/fiche_voiture_stafim parquet files "
            "under data/silver/<etl_run_id>."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
