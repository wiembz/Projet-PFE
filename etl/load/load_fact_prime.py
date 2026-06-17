from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator

import pandas as pd
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


SILVER_DIR = PROJECT_ROOT / "data" / "silver"
TARGET_SCHEMA = "iris_dw"
TARGET_TABLE = "fact_prime"
SOURCE_SYSTEM_VALUE = "Production.xlsx"
SOURCE_KEY_COLUMNS = ("NUMCNT", "NUMAVT", "NUMMAJ")
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}
NEVER_INSERT_COLUMNS = {"prime_sk", "created_at"}
BATCH_SIZE = 10_000

SOURCE_REQUIRED_COLUMNS = (
    "NUMCNT",
    "NUMAVT",
    "NUMMAJ",
    "NATCLT",
    "IDCLT",
    "CODFAM",
    "CODPROD",
    "NATINT",
    "IDINT",
    "IDDELEGA",
    "DEBCNT",
    "FINCNT",
    "DEBEFFET",
    "FINEFFET",
    "TOTAL_PRIME",
)

FACT_COLUMN_SOURCES = {
    "prime_natural_key": "prime_natural_key",
    "client_sk": "client_sk",
    "contrat_sk": "contrat_sk",
    "vehicule_sk": "vehicule_sk",
    "produit_sk": "produit_sk",
    "intermediaire_sk": "intermediaire_sk",
    "delegation_sk": "delegation_sk",
    "date_debut_contrat_sk": "date_debut_contrat_sk",
    "date_fin_contrat_sk": "date_fin_contrat_sk",
    "date_debut_effet_sk": "date_debut_effet_sk",
    "date_fin_effet_sk": "date_fin_effet_sk",
    "total_prime": "TOTAL_PRIME",
    "source_system": "source_system",
    "etl_run_id": "etl_run_id",
}


@dataclass(frozen=True)
class LookupDefinition:
    label: str
    table_name: str
    key_column: str
    sk_column: str
    source_key_column: str
    output_sk_column: str


LOOKUPS = (
    LookupDefinition(
        label="client",
        table_name="dim_client",
        key_column="client_natural_key",
        sk_column="client_sk",
        source_key_column="client_natural_key",
        output_sk_column="client_sk",
    ),
    LookupDefinition(
        label="contrat",
        table_name="dim_contrat",
        key_column="contrat_natural_key",
        sk_column="contrat_sk",
        source_key_column="contrat_natural_key",
        output_sk_column="contrat_sk",
    ),
    LookupDefinition(
        label="produit",
        table_name="dim_produit",
        key_column="produit_natural_key",
        sk_column="produit_sk",
        source_key_column="produit_natural_key",
        output_sk_column="produit_sk",
    ),
    LookupDefinition(
        label="intermediaire",
        table_name="dim_intermediaire",
        key_column="intermediaire_natural_key",
        sk_column="intermediaire_sk",
        source_key_column="intermediaire_natural_key",
        output_sk_column="intermediaire_sk",
    ),
    LookupDefinition(
        label="delegation",
        table_name="dim_delegation",
        key_column="delegation_natural_key",
        sk_column="delegation_sk",
        source_key_column="delegation_natural_key",
        output_sk_column="delegation_sk",
    ),
)

DATE_LOOKUPS = {
    "DEBCNT": "date_debut_contrat_sk",
    "FINCNT": "date_fin_contrat_sk",
    "DEBEFFET": "date_debut_effet_sk",
    "FINEFFET": "date_fin_effet_sk",
}


@dataclass(frozen=True)
class LookupStats:
    unknown_client_count: int
    unknown_contrat_count: int
    unknown_vehicule_count: int
    unknown_produit_count: int
    unknown_intermediaire_count: int
    unknown_delegation_count: int
    unknown_date_debut_contrat_count: int
    unknown_date_fin_contrat_count: int
    unknown_date_debut_effet_count: int
    unknown_date_fin_effet_count: int


@dataclass(frozen=True)
class LoadStats:
    input_count: int
    loaded_count: int
    target_count: int
    unknown_client_count: int
    unknown_contrat_count: int
    unknown_vehicule_count: int
    unknown_produit_count: int
    unknown_intermediaire_count: int
    unknown_delegation_count: int
    unknown_date_debut_contrat_count: int
    unknown_date_fin_contrat_count: int
    unknown_date_debut_effet_count: int
    unknown_date_fin_effet_count: int


def main() -> None:
    args = _parse_args()
    stats = load_fact_prime(args.etl_run_id)
    print(f"input_count={stats.input_count}")
    print(f"loaded_count={stats.loaded_count}")
    print(f"target_count={stats.target_count}")
    print(f"unknown_client_count={stats.unknown_client_count}")
    print(f"unknown_contrat_count={stats.unknown_contrat_count}")
    print(f"unknown_vehicule_count={stats.unknown_vehicule_count}")
    print(f"unknown_produit_count={stats.unknown_produit_count}")
    print(f"unknown_intermediaire_count={stats.unknown_intermediaire_count}")
    print(f"unknown_delegation_count={stats.unknown_delegation_count}")
    print(
        "unknown_date_debut_contrat_count="
        f"{stats.unknown_date_debut_contrat_count}"
    )
    print(f"unknown_date_fin_contrat_count={stats.unknown_date_fin_contrat_count}")
    print(f"unknown_date_debut_effet_count={stats.unknown_date_debut_effet_count}")
    print(f"unknown_date_fin_effet_count={stats.unknown_date_fin_effet_count}")


def load_fact_prime(etl_run_id: str) -> LoadStats:
    _validate_etl_run_id(etl_run_id)

    input_file = SILVER_DIR / etl_run_id / "production.parquet"
    if not input_file.exists():
        raise FileNotFoundError(f"Silver production file not found: {input_file}")

    dataframe = pd.read_parquet(input_file)
    input_count = len(dataframe)
    _assert_input_contract(dataframe)
    prime_rows = _build_prime_rows(dataframe, etl_run_id)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_columns = _get_table_columns(cur, TARGET_TABLE)
            _assert_fact_prime_contract(cur, table_columns)
            _assert_lookup_tables(cur)

            lookup_stats = _apply_lookup_sks(cur, prime_rows)
            insert_columns = _insert_columns(table_columns)
            load_rows = _build_load_rows(prime_rows, insert_columns)
            loaded_count = _upsert_fact_prime_rows(cur, load_rows, insert_columns)
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
        unknown_client_count=lookup_stats.unknown_client_count,
        unknown_contrat_count=lookup_stats.unknown_contrat_count,
        unknown_vehicule_count=lookup_stats.unknown_vehicule_count,
        unknown_produit_count=lookup_stats.unknown_produit_count,
        unknown_intermediaire_count=lookup_stats.unknown_intermediaire_count,
        unknown_delegation_count=lookup_stats.unknown_delegation_count,
        unknown_date_debut_contrat_count=(
            lookup_stats.unknown_date_debut_contrat_count
        ),
        unknown_date_fin_contrat_count=lookup_stats.unknown_date_fin_contrat_count,
        unknown_date_debut_effet_count=lookup_stats.unknown_date_debut_effet_count,
        unknown_date_fin_effet_count=lookup_stats.unknown_date_fin_effet_count,
    )


def _assert_input_contract(dataframe: pd.DataFrame) -> None:
    missing_columns = [
        column for column in SOURCE_REQUIRED_COLUMNS if column not in dataframe.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"Silver production file is missing columns: {missing}")


def _build_prime_rows(dataframe: pd.DataFrame, etl_run_id: str) -> pd.DataFrame:
    primes = dataframe.copy()

    for column in _key_columns_to_clean(primes):
        primes[column] = primes[column].map(_clean_key_value)

    primes["prime_natural_key"] = _combine_key_parts(primes, SOURCE_KEY_COLUMNS)
    null_key_count = int(primes["prime_natural_key"].isna().sum())
    if null_key_count:
        raise RuntimeError(
            f"Silver production file contains {null_key_count} null "
            "prime_natural_key values"
        )

    duplicate_key_count = int(primes["prime_natural_key"].duplicated(keep=False).sum())
    if duplicate_key_count:
        raise RuntimeError(
            f"Silver production file contains {duplicate_key_count} rows with "
            "duplicate prime_natural_key values"
        )

    primes["client_natural_key"] = _combine_key_parts(primes, ("NATCLT", "IDCLT"))
    primes["contrat_natural_key"] = primes["prime_natural_key"]
    primes["produit_natural_key"] = _combine_key_parts(primes, ("CODFAM", "CODPROD"))
    primes["intermediaire_natural_key"] = _combine_key_parts(
        primes,
        ("NATINT", "IDINT"),
    )
    primes["delegation_natural_key"] = primes["IDDELEGA"]
    primes["source_system"] = SOURCE_SYSTEM_VALUE
    primes["etl_run_id"] = etl_run_id

    for source_column in DATE_LOOKUPS:
        primes[source_column] = primes[source_column].map(_to_date)

    return primes.reset_index(drop=True)


def _key_columns_to_clean(dataframe: pd.DataFrame) -> list[str]:
    candidates = [
        "NUMCNT",
        "NUMAVT",
        "NUMMAJ",
        "NATCLT",
        "IDCLT",
        "CODFAM",
        "CODPROD",
        "NATINT",
        "IDINT",
        "IDDELEGA",
    ]
    return [column for column in candidates if column in dataframe.columns]


def _apply_lookup_sks(cur: Any, dataframe: pd.DataFrame) -> LookupStats:
    unknown_counts: dict[str, int] = {}

    for lookup in LOOKUPS:
        values_by_key = _load_lookup_values(
            cur,
            table_name=lookup.table_name,
            key_column=lookup.key_column,
            sk_column=lookup.sk_column,
            source_keys=dataframe[lookup.source_key_column],
        )
        sk_values, unknown_count = _resolve_sks(
            dataframe[lookup.source_key_column],
            values_by_key,
        )
        dataframe[lookup.output_sk_column] = sk_values
        unknown_counts[lookup.label] = unknown_count

    vehicle_sks, unknown_vehicle_count = _resolve_vehicle_sks(cur, dataframe)
    dataframe["vehicule_sk"] = vehicle_sks

    date_lookup = _load_date_lookup(cur, dataframe)
    date_unknown_counts: dict[str, int] = {}
    for source_column, output_column in DATE_LOOKUPS.items():
        sk_values, unknown_count = _resolve_date_sks(
            dataframe[source_column],
            date_lookup,
        )
        dataframe[output_column] = sk_values
        date_unknown_counts[output_column] = unknown_count

    return LookupStats(
        unknown_client_count=unknown_counts["client"],
        unknown_contrat_count=unknown_counts["contrat"],
        unknown_vehicule_count=unknown_vehicle_count,
        unknown_produit_count=unknown_counts["produit"],
        unknown_intermediaire_count=unknown_counts["intermediaire"],
        unknown_delegation_count=unknown_counts["delegation"],
        unknown_date_debut_contrat_count=date_unknown_counts["date_debut_contrat_sk"],
        unknown_date_fin_contrat_count=date_unknown_counts["date_fin_contrat_sk"],
        unknown_date_debut_effet_count=date_unknown_counts["date_debut_effet_sk"],
        unknown_date_fin_effet_count=date_unknown_counts["date_fin_effet_sk"],
    )


def _resolve_vehicle_sks(
    cur: Any,
    dataframe: pd.DataFrame,
) -> tuple[list[int], int]:
    if "vehicule_business_key" not in dataframe.columns:
        return [0] * len(dataframe), len(dataframe)

    keys = dataframe["vehicule_business_key"].map(_clean_key_value)
    values_by_key = _load_lookup_values(
        cur,
        table_name="dim_vehicule",
        key_column="vehicule_natural_key",
        sk_column="vehicule_sk",
        source_keys=keys,
    )
    return _resolve_sks(keys, values_by_key)


def _resolve_sks(
    source_keys: pd.Series,
    values_by_key: dict[str, int],
) -> tuple[list[int], int]:
    sk_values: list[int] = []
    unknown_count = 0

    for raw_key in source_keys:
        if pd.isna(raw_key):
            sk_values.append(0)
            unknown_count += 1
            continue

        sk = values_by_key.get(str(raw_key))
        if sk is None:
            sk_values.append(0)
            unknown_count += 1
        else:
            sk_values.append(sk)

    return sk_values, unknown_count


def _resolve_date_sks(
    source_dates: pd.Series,
    values_by_date: dict[date, int],
) -> tuple[list[int], int]:
    sk_values: list[int] = []
    unknown_count = 0

    for source_date in source_dates:
        if source_date is None or pd.isna(source_date):
            sk_values.append(0)
            unknown_count += 1
            continue

        sk = values_by_date.get(source_date)
        if sk is None:
            sk_values.append(0)
            unknown_count += 1
        else:
            sk_values.append(sk)

    return sk_values, unknown_count


def _load_lookup_values(
    cur: Any,
    *,
    table_name: str,
    key_column: str,
    sk_column: str,
    source_keys: pd.Series,
) -> dict[str, int]:
    keys = sorted({str(key) for key in source_keys if pd.notna(key)})
    values_by_key: dict[str, int] = {}
    if not keys:
        return values_by_key

    query = sql.SQL(
        """
        SELECT {}, {}
        FROM {}.{}
        WHERE {} = ANY(%s)
        """
    ).format(
        sql.Identifier(key_column),
        sql.Identifier(sk_column),
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(table_name),
        sql.Identifier(key_column),
    )

    for key_batch in _chunks(keys, BATCH_SIZE):
        cur.execute(query, (key_batch,))
        values_by_key.update({str(key): int(sk) for key, sk in cur.fetchall()})

    return values_by_key


def _load_date_lookup(cur: Any, dataframe: pd.DataFrame) -> dict[date, int]:
    source_dates: set[date] = set()
    for source_column in DATE_LOOKUPS:
        source_dates.update(
            value
            for value in dataframe[source_column]
            if value is not None and not pd.isna(value)
        )

    values_by_date: dict[date, int] = {}
    if not source_dates:
        return values_by_date

    query = """
        SELECT date_val, date_sk
        FROM iris_dw.dim_date
        WHERE date_val = ANY(%s)
    """
    for date_batch in _chunks(sorted(source_dates), BATCH_SIZE):
        cur.execute(query, (date_batch,))
        values_by_date.update({date_val: int(date_sk) for date_val, date_sk in cur.fetchall()})

    return values_by_date


def _assert_lookup_tables(cur: Any) -> None:
    for lookup in LOOKUPS:
        columns = _get_table_columns(cur, lookup.table_name)
        missing_columns = [
            column
            for column in (lookup.key_column, lookup.sk_column)
            if column not in columns
        ]
        if missing_columns:
            missing = ", ".join(missing_columns)
            raise RuntimeError(
                f"{TARGET_SCHEMA}.{lookup.table_name} is missing lookup columns: "
                f"{missing}"
            )

    date_columns = _get_table_columns(cur, "dim_date")
    missing_date_columns = sorted({"date_val", "date_sk"} - date_columns)
    if missing_date_columns:
        missing = ", ".join(missing_date_columns)
        raise RuntimeError(f"{TARGET_SCHEMA}.dim_date is missing columns: {missing}")


def _assert_fact_prime_contract(cur: Any, table_columns: set[str]) -> None:
    if "prime_natural_key" not in table_columns:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} is missing prime_natural_key"
        )
    _assert_key_conflict_target(cur, "prime_natural_key")


def _insert_columns(table_columns: set[str]) -> list[str]:
    columns = [
        column
        for column in FACT_COLUMN_SOURCES
        if column in table_columns and column not in NEVER_INSERT_COLUMNS
    ]
    if "prime_natural_key" not in columns:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} has no insertable prime_natural_key"
        )
    return columns


def _build_load_rows(
    dataframe: pd.DataFrame,
    insert_columns: list[str],
) -> list[dict[str, Any]]:
    load_frame = pd.DataFrame(index=dataframe.index)

    for target_column in insert_columns:
        source_column = FACT_COLUMN_SOURCES[target_column]
        load_frame[target_column] = dataframe[source_column]

    load_frame = load_frame.astype(object).where(pd.notna(load_frame), None)
    return load_frame.to_dict(orient="records")


def _upsert_fact_prime_rows(
    cur: Any,
    rows: list[dict[str, Any]],
    insert_columns: list[str],
) -> int:
    if not rows:
        return 0

    update_columns = [
        column for column in insert_columns if column != "prime_natural_key"
    ]
    if not update_columns:
        raise RuntimeError("No fact_prime columns available to update on rerun")

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
        sql.SQL(", ").join(sql.Identifier(column) for column in insert_columns),
        sql.SQL(", ").join(sql.Placeholder(column) for column in insert_columns),
        sql.Identifier("prime_natural_key"),
        sql.SQL(", ").join(assignments),
    )

    loaded_count = 0
    for batch in _chunks(rows, BATCH_SIZE):
        cur.executemany(query, batch)
        loaded_count += cur.rowcount if cur.rowcount >= 0 else len(batch)

    return loaded_count


def _get_table_columns(cur: Any, table_name: str) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %(schema)s
          AND table_name = %(table)s
        """,
        {
            "schema": TARGET_SCHEMA,
            "table": table_name,
        },
    )
    columns = {row[0] for row in cur.fetchall()}
    if not columns:
        raise RuntimeError(f"{TARGET_SCHEMA}.{table_name} does not exist")
    return columns


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


def _count_target_rows(cur: Any) -> int:
    query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
    )
    cur.execute(query)
    return int(cur.fetchone()[0])


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


def _chunks(values: list[Any], size: int) -> Iterator[list[Any]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


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
        description="Load Silver production rows into iris_dw.fact_prime."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id containing data/silver/<etl_run_id>/production.parquet.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
