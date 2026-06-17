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
TARGET_TABLE = "dim_client"
SOURCE_BUSINESS_KEY = "client_business_key"
TARGET_KEY_CANDIDATES = ("client_business_key", "client_natural_key")
NEVER_INSERT_COLUMNS = {"client_sk", "created_at", "updated_at"}

SOURCE_TO_TARGET_CANDIDATES = {
    SOURCE_BUSINESS_KEY: TARGET_KEY_CANDIDATES,
    "CNAT": ("cnat", "code_nature_client"),
    "NUMPERS": ("numpers", "num_client"),
    "TYPEID": ("typeid", "type_id", "type_identifiant"),
    "ID": ("id", "id_client", "identifiant_client"),
    "ADR1": ("adr1", "adresse"),
    "CPOST": ("cpost", "code_postal"),
    "CITE": ("cite", "localite_client"),
    "GOUVERNOR": ("gouvernor", "gouvernorat", "gouvernorat_client"),
    "DATE_NAISS": ("date_naiss", "date_naissance"),
    "PRF": ("prf", "profession"),
    "SEXE": ("sexe",),
    "NBRENF": ("nbrenf", "nombre_enfants"),
    "SITUAFAMI": ("situafami", "situation_familiale"),
    "DEBCNT": ("debcnt", "date_debut_client"),
    "etl_run_id": ("source_etl_run_id",),
}


@dataclass(frozen=True)
class LoadStats:
    input_count: int
    loaded_count: int
    target_count: int


def main() -> None:
    args = _parse_args()
    stats = load_dim_client(args.etl_run_id)
    print(f"input_count={stats.input_count}")
    print(f"loaded_count={stats.loaded_count}")
    print(f"target_count={stats.target_count}")


def load_dim_client(etl_run_id: str) -> LoadStats:
    _validate_etl_run_id(etl_run_id)
    input_file = SILVER_DIR / etl_run_id / "clients.parquet"
    if not input_file.exists():
        raise FileNotFoundError(f"Silver clients file not found: {input_file}")

    dataframe = pd.read_parquet(input_file)
    input_count = len(dataframe)
    _assert_input_contract(dataframe)
    dataframe = _normalize_source_columns(dataframe)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_columns = _get_table_columns(cur)
            key_column = _resolve_target_key_column(table_columns)
            _assert_key_conflict_target(cur, key_column)

            column_mapping = _build_column_mapping(table_columns)
            _assert_sexe_mapping(column_mapping, table_columns)
            rows = _build_load_rows(dataframe, column_mapping)
            loaded_count = _upsert_dim_client_rows(cur, rows, key_column)
            target_count = _count_target_rows(cur)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return LoadStats(
        input_count=input_count,
        loaded_count=loaded_count,
        target_count=target_count,
    )


def _assert_input_contract(dataframe: pd.DataFrame) -> None:
    if SOURCE_BUSINESS_KEY not in dataframe.columns:
        raise RuntimeError(f"Silver clients file is missing {SOURCE_BUSINESS_KEY}")

    null_key_count = int(dataframe[SOURCE_BUSINESS_KEY].isna().sum())
    if null_key_count:
        raise RuntimeError(
            f"Silver clients file contains {null_key_count} null client business keys"
        )

    duplicate_key_count = int(dataframe[SOURCE_BUSINESS_KEY].duplicated().sum())
    if duplicate_key_count:
        raise RuntimeError(
            "Silver clients file contains "
            f"{duplicate_key_count} duplicate client business keys"
        )


def _normalize_source_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    normalized = dataframe.copy()
    if "SEXE" in normalized.columns:
        normalized["SEXE"] = normalized["SEXE"].astype("string").str.strip().str.upper()
        normalized["SEXE"] = normalized["SEXE"].where(
            normalized["SEXE"].isin(["M", "F"]),
            None,
        )
    return normalized


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
        f"{TARGET_SCHEMA}.{TARGET_TABLE} is missing required business key "
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

    if SOURCE_BUSINESS_KEY not in mapping:
        raise RuntimeError(
            f"No insertable target key column found in {TARGET_SCHEMA}.{TARGET_TABLE}"
        )

    return mapping


def _assert_sexe_mapping(
    column_mapping: dict[str, str],
    table_columns: set[str],
) -> None:
    if "sexe" not in table_columns:
        return

    if column_mapping.get("SEXE") != "sexe":
        raise RuntimeError("Target column sexe must be mapped from source column SEXE")

    other_sources = [
        source_column
        for source_column, target_column in column_mapping.items()
        if target_column == "sexe" and source_column != "SEXE"
    ]
    if other_sources:
        joined_sources = ", ".join(other_sources)
        raise RuntimeError(
            "Target column sexe cannot be mapped from source columns: "
            f"{joined_sources}"
        )


def _build_load_rows(
    dataframe: pd.DataFrame,
    column_mapping: dict[str, str],
) -> list[dict[str, Any]]:
    load_frame = pd.DataFrame(index=dataframe.index)

    for source_column, target_column in column_mapping.items():
        if source_column not in dataframe.columns:
            continue
        load_frame[target_column] = dataframe[source_column]

    if "nombre_enfants" in load_frame.columns:
        load_frame["nombre_enfants"] = _to_nullable_int(load_frame["nombre_enfants"])
    if "nbrenf" in load_frame.columns:
        load_frame["nbrenf"] = _to_nullable_int(load_frame["nbrenf"])

    load_frame = load_frame.astype(object).where(pd.notna(load_frame), None)
    return load_frame.to_dict(orient="records")


def _to_nullable_int(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    whole_number_mask = numeric.notna() & numeric.mod(1).eq(0)
    return numeric.where(whole_number_mask).astype("Int64")


def _upsert_dim_client_rows(
    cur: Any,
    rows: list[dict[str, Any]],
    key_column: str,
) -> int:
    if not rows:
        return 0

    columns = list(rows[0].keys())
    update_columns = [column for column in columns if column != key_column]

    if "updated_at" in _current_target_columns(cur):
        assignments = [
            sql.SQL("{} = EXCLUDED.{}").format(
                sql.Identifier(column),
                sql.Identifier(column),
            )
            for column in update_columns
        ]
        assignments.append(sql.SQL("updated_at = now()"))
    else:
        assignments = [
            sql.SQL("{} = EXCLUDED.{}").format(
                sql.Identifier(column),
                sql.Identifier(column),
            )
            for column in update_columns
        ]

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


def _current_target_columns(cur: Any) -> set[str]:
    return _get_table_columns(cur)


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
        description="Load Silver clients parquet into iris_dw.dim_client."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id containing data/silver/<etl_run_id>/clients.parquet.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
