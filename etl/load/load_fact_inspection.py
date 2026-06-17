from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from datetime import date, datetime, time
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
TARGET_TABLE = "fact_inspection"
SOURCE_SYSTEM_VALUE = "FicheVoitureStafim.xlsx"
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}
NEVER_INSERT_COLUMNS = {"inspection_sk", "created_at"}
BATCH_SIZE = 10_000

SOURCE_REQUIRED_COLUMNS = (
    "vehicule_business_key",
    "inspection_date",
    "work_order_number",
)

SOURCE_KEY_COLUMNS = (
    "vehicule_business_key",
    "inspection_date_key",
    "work_order_number",
)

SOURCE_COLUMN_CANDIDATES = {
    "commande_travaux": ("work_order_number", "N\u00b0 COMMANDE DE TRAVAUX"),
    "heure_entree": ("HEURE D'ENTREE :",),
    "agent_name": ("NOM DE L'AGENT",),
    "nom_prenom_client": ("NOM ET PRENOM ", "NOM ET PRENOM"),
    "telephone": ("TELEPHONE",),
    "immatriculation_source": ("N\u00b0 D'IMMATRICULATION",),
    "vin_source": ("V.I.N", "V.I.N "),
    "kilometrage": ("KILOMETRAGE",),
    "motorisation": ("MOTORISATION", " [MOTORISATION]", "[MOTORISATION]"),
}

FACT_COLUMN_SOURCES = {
    "inspection_natural_key": "inspection_natural_key",
    "vehicule_sk": "vehicule_sk",
    "date_inspection_sk": "date_inspection_sk",
    "commande_travaux": "commande_travaux",
    "heure_entree": "heure_entree",
    "agent_name": "agent_name",
    "nom_prenom_client": "nom_prenom_client",
    "telephone": "telephone",
    "immatriculation_source": "immatriculation_source",
    "vin_source": "vin_source",
    "kilometrage": "kilometrage",
    "motorisation": "motorisation",
    "source_system": "source_system",
    "etl_run_id": "etl_run_id",
}


@dataclass(frozen=True)
class LookupStats:
    unknown_vehicule_count: int
    unknown_date_inspection_count: int


@dataclass(frozen=True)
class LoadStats:
    input_count: int
    loaded_count: int
    target_count: int
    unknown_vehicule_count: int
    unknown_date_inspection_count: int
    null_kilometrage_count: int
    populated_vin_count: int
    populated_motorisation_count: int


def main() -> None:
    args = _parse_args()
    stats = load_fact_inspection(args.etl_run_id)
    print(f"input_count={stats.input_count}")
    print(f"loaded_count={stats.loaded_count}")
    print(f"target_count={stats.target_count}")
    print(f"unknown_vehicule_count={stats.unknown_vehicule_count}")
    print(f"unknown_date_inspection_count={stats.unknown_date_inspection_count}")
    print(f"null_kilometrage_count={stats.null_kilometrage_count}")
    print(f"populated_vin_count={stats.populated_vin_count}")
    print(f"populated_motorisation_count={stats.populated_motorisation_count}")


def load_fact_inspection(etl_run_id: str) -> LoadStats:
    _validate_etl_run_id(etl_run_id)

    input_file = SILVER_DIR / etl_run_id / "fiche_voiture_stafim.parquet"
    if not input_file.exists():
        raise FileNotFoundError(f"Silver inspection file not found: {input_file}")

    dataframe = pd.read_parquet(input_file)
    input_count = len(dataframe)
    _assert_input_contract(dataframe)
    inspection_rows = _build_inspection_rows(dataframe, etl_run_id)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_columns = _get_table_columns(cur, TARGET_TABLE)
            _assert_fact_inspection_contract(cur, table_columns)
            _assert_lookup_tables(cur)

            lookup_stats = _apply_lookup_sks(cur, inspection_rows)
            insert_columns = _insert_columns(table_columns, inspection_rows)
            load_rows = _build_load_rows(inspection_rows, insert_columns)
            loaded_count = _upsert_fact_inspection_rows(
                cur,
                load_rows,
                insert_columns,
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
        loaded_count=loaded_count,
        target_count=target_count,
        unknown_vehicule_count=lookup_stats.unknown_vehicule_count,
        unknown_date_inspection_count=lookup_stats.unknown_date_inspection_count,
        null_kilometrage_count=int(inspection_rows["kilometrage"].isna().sum()),
        populated_vin_count=int(inspection_rows["vin_source"].notna().sum()),
        populated_motorisation_count=int(inspection_rows["motorisation"].notna().sum()),
    )


def _assert_input_contract(dataframe: pd.DataFrame) -> None:
    missing_columns = [
        column for column in SOURCE_REQUIRED_COLUMNS if column not in dataframe.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"Silver inspection file is missing columns: {missing}")


def _build_inspection_rows(dataframe: pd.DataFrame, etl_run_id: str) -> pd.DataFrame:
    inspections = dataframe.copy()

    for column in ("inspection_business_key", "vehicule_business_key", "work_order_number"):
        if column in inspections.columns:
            inspections[column] = inspections[column].map(_clean_key_value)

    inspections["inspection_date"] = inspections["inspection_date"].map(_to_date)
    inspections["inspection_date_key"] = inspections["inspection_date"].map(
        lambda value: value.isoformat() if value is not None else None
    )

    derived_key = _combine_key_parts(inspections, SOURCE_KEY_COLUMNS)
    if "inspection_business_key" in inspections.columns:
        preferred_key = inspections["inspection_business_key"].map(_clean_key_value)
        inspections["inspection_natural_key"] = preferred_key.where(
            preferred_key.notna(),
            derived_key,
        )
    else:
        inspections["inspection_natural_key"] = derived_key

    null_key_count = int(inspections["inspection_natural_key"].isna().sum())
    if null_key_count:
        raise RuntimeError(
            f"Silver inspection file contains {null_key_count} null "
            "inspection_natural_key values"
        )

    duplicate_key_count = int(
        inspections["inspection_natural_key"].duplicated(keep=False).sum()
    )
    if duplicate_key_count:
        raise RuntimeError(
            f"Silver inspection file contains {duplicate_key_count} rows with "
            "duplicate inspection_natural_key values"
        )

    inspections["vehicule_natural_key"] = inspections["vehicule_business_key"].map(
        _clean_key_value
    )
    inspections["source_system"] = SOURCE_SYSTEM_VALUE
    inspections["etl_run_id"] = etl_run_id

    for target_column, source_candidates in SOURCE_COLUMN_CANDIDATES.items():
        source_column = _first_existing_column(inspections, source_candidates)
        if source_column is None:
            inspections[target_column] = pd.NA
        elif target_column == "kilometrage":
            inspections[target_column] = inspections[source_column].map(
                _to_integer
            ).astype("Int64")
        elif target_column == "heure_entree":
            inspections[target_column] = inspections[source_column].map(_clean_time_text)
        else:
            inspections[target_column] = inspections[source_column].map(
                _clean_optional_text
            )

    return inspections.reset_index(drop=True)


def _apply_lookup_sks(cur: Any, dataframe: pd.DataFrame) -> LookupStats:
    vehicle_lookup = _load_lookup_values(
        cur,
        table_name="dim_vehicule",
        key_column="vehicule_natural_key",
        sk_column="vehicule_sk",
        source_keys=dataframe["vehicule_natural_key"],
    )
    vehicule_sks, unknown_vehicule_count = _resolve_sks(
        dataframe["vehicule_natural_key"],
        vehicle_lookup,
    )
    dataframe["vehicule_sk"] = vehicule_sks

    date_lookup = _load_date_lookup(cur, dataframe["inspection_date"])
    date_sks, unknown_date_inspection_count = _resolve_date_sks(
        dataframe["inspection_date"],
        date_lookup,
    )
    dataframe["date_inspection_sk"] = date_sks

    return LookupStats(
        unknown_vehicule_count=unknown_vehicule_count,
        unknown_date_inspection_count=unknown_date_inspection_count,
    )


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


def _load_date_lookup(cur: Any, source_dates: pd.Series) -> dict[date, int]:
    dates = sorted(
        {
            value
            for value in source_dates
            if value is not None and not pd.isna(value)
        }
    )
    values_by_date: dict[date, int] = {}
    if not dates:
        return values_by_date

    query = """
        SELECT date_val, date_sk
        FROM iris_dw.dim_date
        WHERE date_val = ANY(%s)
    """
    for date_batch in _chunks(dates, BATCH_SIZE):
        cur.execute(query, (date_batch,))
        values_by_date.update(
            {date_val: int(date_sk) for date_val, date_sk in cur.fetchall()}
        )

    return values_by_date


def _assert_lookup_tables(cur: Any) -> None:
    vehicule_columns = _get_table_columns(cur, "dim_vehicule")
    missing_vehicule_columns = sorted(
        {"vehicule_natural_key", "vehicule_sk"} - vehicule_columns
    )
    if missing_vehicule_columns:
        missing = ", ".join(missing_vehicule_columns)
        raise RuntimeError(f"{TARGET_SCHEMA}.dim_vehicule is missing columns: {missing}")

    date_columns = _get_table_columns(cur, "dim_date")
    missing_date_columns = sorted({"date_val", "date_sk"} - date_columns)
    if missing_date_columns:
        missing = ", ".join(missing_date_columns)
        raise RuntimeError(f"{TARGET_SCHEMA}.dim_date is missing columns: {missing}")


def _assert_fact_inspection_contract(cur: Any, table_columns: set[str]) -> None:
    if "inspection_natural_key" not in table_columns:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} is missing inspection_natural_key"
        )
    _assert_key_conflict_target(cur, "inspection_natural_key")


def _insert_columns(table_columns: set[str], dataframe: pd.DataFrame) -> list[str]:
    columns = [
        column
        for column, source_column in FACT_COLUMN_SOURCES.items()
        if (
            column in table_columns
            and column not in NEVER_INSERT_COLUMNS
            and source_column in dataframe.columns
        )
    ]
    if "inspection_natural_key" not in columns:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} has no insertable "
            "inspection_natural_key"
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
    return [
        {key: _to_python_value(value) for key, value in row.items()}
        for row in load_frame.to_dict(orient="records")
    ]


def _upsert_fact_inspection_rows(
    cur: Any,
    rows: list[dict[str, Any]],
    insert_columns: list[str],
) -> int:
    if not rows:
        return 0

    update_columns = [
        column for column in insert_columns if column != "inspection_natural_key"
    ]
    if not update_columns:
        raise RuntimeError("No fact_inspection columns available to update on rerun")

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
        sql.Identifier("inspection_natural_key"),
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


def _first_existing_column(
    dataframe: pd.DataFrame,
    candidates: tuple[str, ...],
) -> str | None:
    for candidate in candidates:
        if candidate in dataframe.columns:
            return candidate
    return None


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


def _clean_optional_text(value: Any) -> str | None:
    if pd.isna(value):
        return None

    cleaned = str(value).strip()
    if cleaned.casefold() in NULL_MARKERS:
        return None

    return cleaned


def _clean_time_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, time):
        return value.isoformat()
    return _clean_optional_text(value)


def _to_integer(value: Any) -> int | None:
    if value is None or pd.isna(value):
        return None

    text_value = str(value).strip().replace("\u00a0", "").replace(" ", "")
    if text_value.casefold() in NULL_MARKERS:
        return None

    numeric = pd.to_numeric(text_value, errors="coerce")
    if pd.isna(numeric):
        return None

    numeric_value = float(numeric)
    if not math.isfinite(numeric_value) or not numeric_value.is_integer():
        return None

    return int(numeric_value)


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


def _to_python_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except (AttributeError, ValueError):
            return value
    return value


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
        description="Load Silver inspection rows into iris_dw.fact_inspection."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help=(
            "ETL run id containing "
            "data/silver/<etl_run_id>/fiche_voiture_stafim.parquet."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
