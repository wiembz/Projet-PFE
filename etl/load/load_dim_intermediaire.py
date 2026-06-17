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
TARGET_TABLE = "dim_intermediaire"
SOURCE_NATURAL_KEY = "intermediaire_natural_key"
SOURCE_SYSTEM_VALUE = "Production.xlsx/Sinistres.xlsx"
KEY_COLUMNS = ("NATINT", "IDINT")
TARGET_KEY_CANDIDATES = (
    "intermediaire_natural_key",
    "intermediaire_business_key",
)
NEVER_INSERT_COLUMNS = {"intermediaire_sk", "created_at", "updated_at"}
NULL_MARKERS = {"", "nan", "none", "<na>"}
INPUT_FILES = (
    ("production", "production.parquet"),
    ("sinistres", "sinistres.parquet"),
)

SOURCE_TO_TARGET_CANDIDATES = {
    SOURCE_NATURAL_KEY: TARGET_KEY_CANDIDATES,
    "NATINT": ("nature_intermediaire", "code_nature_intermediaire", "natint"),
    "IDINT": ("code_intermediaire", "id_intermediaire", "idint"),
    "source_system": ("source_system",),
}


@dataclass(frozen=True)
class LoadStats:
    input_count: int
    distinct_intermediaire_count: int
    null_key_count: int
    loaded_count: int
    target_count: int


def main() -> None:
    args = _parse_args()
    stats = load_dim_intermediaire(args.etl_run_id)
    print(f"input_count={stats.input_count}")
    print(f"distinct_intermediaire_count={stats.distinct_intermediaire_count}")
    print(f"null_key_count={stats.null_key_count}")
    print(f"loaded_count={stats.loaded_count}")
    print(f"target_count={stats.target_count}")


def load_dim_intermediaire(etl_run_id: str) -> LoadStats:
    _validate_etl_run_id(etl_run_id)

    dataframe = _read_inputs(etl_run_id)
    input_count = len(dataframe)
    intermediaire_rows, null_key_count = _build_distinct_intermediaire_rows(dataframe)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_columns = _get_table_columns(cur)
            key_column = _resolve_target_key_column(table_columns)
            _assert_key_conflict_target(cur, key_column)

            column_mapping = _build_column_mapping(table_columns)
            rows = _build_load_rows(intermediaire_rows, column_mapping)
            loaded_count = _upsert_dim_intermediaire_rows(
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
        distinct_intermediaire_count=len(intermediaire_rows),
        null_key_count=null_key_count,
        loaded_count=loaded_count,
        target_count=target_count,
    )


def _read_inputs(etl_run_id: str) -> pd.DataFrame:
    input_dir = SILVER_DIR / etl_run_id
    frames: list[pd.DataFrame] = []
    missing_files: list[Path] = []

    for source_name, file_name in INPUT_FILES:
        input_file = input_dir / file_name
        if not input_file.exists():
            missing_files.append(input_file)
            continue

        frame = pd.read_parquet(input_file)
        missing_columns = [column for column in KEY_COLUMNS if column not in frame.columns]
        if missing_columns:
            missing = ", ".join(missing_columns)
            raise RuntimeError(f"Silver {source_name} file is missing columns: {missing}")

        frames.append(frame[list(KEY_COLUMNS)].copy())

    if not frames:
        missing = "\n".join(str(path) for path in missing_files)
        raise FileNotFoundError(
            f"Silver intermediaire input files not found:\n{missing}"
        )

    return pd.concat(frames, ignore_index=True)


def _build_distinct_intermediaire_rows(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, int]:
    intermediaires = dataframe.copy()
    for column in KEY_COLUMNS:
        intermediaires[column] = intermediaires[column].astype("string").str.strip()
        intermediaires[column] = intermediaires[column].mask(
            intermediaires[column].str.lower().isin(NULL_MARKERS),
            pd.NA,
        )

    null_key_mask = intermediaires["NATINT"].isna() | intermediaires["IDINT"].isna()
    null_key_count = int(null_key_mask.sum())
    intermediaires = intermediaires.loc[~null_key_mask].copy()

    intermediaires[SOURCE_NATURAL_KEY] = (
        intermediaires["NATINT"].astype("string")
        + "|"
        + intermediaires["IDINT"].astype("string")
    )
    intermediaires["source_system"] = SOURCE_SYSTEM_VALUE

    distinct = (
        intermediaires.sort_values(SOURCE_NATURAL_KEY, kind="mergesort")
        .drop_duplicates(subset=[SOURCE_NATURAL_KEY], keep="first")
        .reset_index(drop=True)
    )

    return distinct, null_key_count


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


def _upsert_dim_intermediaire_rows(
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
        description="Load Silver intermediaires into iris_dw.dim_intermediaire."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help=(
            "ETL run id containing production/sinistres parquet files under "
            "data/silver/<etl_run_id>."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
