from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterator

import pandas as pd
import yaml
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


CONFIG_FILE = PROJECT_ROOT / "etl" / "config" / "fraud_rules.yaml"
TARGET_SCHEMA = "iris_score"
TARGET_TABLE = "dim_fraud_rule"
NATURAL_KEY_COLUMN = "rule_code"
NEVER_INSERT_COLUMNS = {"rule_sk", "created_at", "updated_at"}
BATCH_SIZE = 1_000

REQUIRED_YAML_FIELDS = (
    "rule_code",
    "rule_name",
    "rule_description",
    "rule_category",
    "is_active",
    "weight",
    "threshold_value",
    "severity",
    "requires_business_validation",
    "rule_version",
)

SOURCE_TO_TARGET_COLUMNS = {
    "rule_code": "rule_code",
    "rule_name": "rule_name",
    "rule_description": "rule_description",
    "rule_category": "rule_category",
    "is_active": "is_active",
    "weight": "weight",
    "threshold_value": "threshold_value",
    "severity": "severity",
    "requires_business_validation": "requires_business_validation",
    "rule_version": "rule_version",
}


@dataclass(frozen=True)
class LoadStats:
    input_count: int
    loaded_count: int
    target_count: int
    active_count: int
    total_weight_active: Decimal


def main() -> None:
    _parse_args()
    stats = load_dim_fraud_rule()
    print(f"input_count={stats.input_count}")
    print(f"loaded_count={stats.loaded_count}")
    print(f"target_count={stats.target_count}")
    print(f"active_count={stats.active_count}")
    print(f"total_weight_active={stats.total_weight_active}")


def load_dim_fraud_rule() -> LoadStats:
    rule_rows = _read_fraud_rule_config()
    input_count = len(rule_rows)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_columns = _get_table_columns(cur)
            _assert_dim_fraud_rule_contract(cur, table_columns)

            insert_columns = _insert_columns(table_columns)
            rows = _build_load_rows(rule_rows, insert_columns)
            loaded_count = _upsert_dim_fraud_rule_rows(
                cur,
                rows,
                insert_columns,
                table_columns,
            )
            target_count = _count_target_rows(cur)
            active_count, total_weight_active = _active_rule_metrics(cur)

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
        active_count=active_count,
        total_weight_active=total_weight_active,
    )


def _read_fraud_rule_config() -> pd.DataFrame:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Fraud rules YAML file not found: {CONFIG_FILE}")

    with CONFIG_FILE.open("r", encoding="utf-8") as stream:
        payload = yaml.safe_load(stream)

    if not isinstance(payload, list):
        raise RuntimeError(f"{CONFIG_FILE} must contain a YAML list of fraud rules")

    rows: list[dict[str, Any]] = []
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise RuntimeError(f"Fraud rule entry #{index} must be a mapping")

        missing_fields = [
            field for field in REQUIRED_YAML_FIELDS if field not in item
        ]
        if missing_fields:
            missing = ", ".join(missing_fields)
            raise RuntimeError(f"Fraud rule entry #{index} is missing fields: {missing}")

        rows.append(
            {
                "rule_code": _clean_required_text(item["rule_code"]),
                "rule_name": _clean_required_text(item["rule_name"]),
                "rule_description": _clean_optional_text(item["rule_description"]),
                "rule_category": _clean_optional_text(item["rule_category"]),
                "is_active": _coerce_bool(item["is_active"], "is_active"),
                "weight": _coerce_decimal(item["weight"], "weight"),
                "threshold_value": _clean_optional_text(item["threshold_value"]),
                "severity": _clean_optional_text(item["severity"]),
                "requires_business_validation": _coerce_bool(
                    item["requires_business_validation"],
                    "requires_business_validation",
                ),
                "rule_version": _clean_required_text(item["rule_version"]),
            }
        )

    dataframe = pd.DataFrame(rows)
    if dataframe.empty:
        raise RuntimeError(f"{CONFIG_FILE} contains no fraud rules")

    duplicate_rule_count = int(dataframe["rule_code"].duplicated(keep=False).sum())
    if duplicate_rule_count:
        raise RuntimeError(
            f"{CONFIG_FILE} contains {duplicate_rule_count} rows with duplicate "
            "rule_code values"
        )

    return dataframe


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


def _assert_dim_fraud_rule_contract(cur: Any, table_columns: set[str]) -> None:
    required_columns = {
        "rule_code",
        "rule_name",
        "is_active",
        "weight",
        "requires_business_validation",
        "rule_version",
    }
    missing_columns = sorted(required_columns - table_columns)
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"{TARGET_SCHEMA}.{TARGET_TABLE} is missing columns: {missing}")

    _assert_key_conflict_target(cur, NATURAL_KEY_COLUMN)


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


def _insert_columns(table_columns: set[str]) -> list[str]:
    columns = [
        target_column
        for target_column in SOURCE_TO_TARGET_COLUMNS.values()
        if target_column in table_columns and target_column not in NEVER_INSERT_COLUMNS
    ]
    if NATURAL_KEY_COLUMN not in columns:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} has no insertable {NATURAL_KEY_COLUMN}"
        )
    return columns


def _build_load_rows(
    dataframe: pd.DataFrame,
    insert_columns: list[str],
) -> list[dict[str, Any]]:
    source_by_target = {
        target_column: source_column
        for source_column, target_column in SOURCE_TO_TARGET_COLUMNS.items()
    }
    load_frame = pd.DataFrame(index=dataframe.index)

    for target_column in insert_columns:
        source_column = source_by_target[target_column]
        load_frame[target_column] = dataframe[source_column]

    load_frame = load_frame.astype(object).where(pd.notna(load_frame), None)
    return load_frame.to_dict(orient="records")


def _upsert_dim_fraud_rule_rows(
    cur: Any,
    rows: list[dict[str, Any]],
    insert_columns: list[str],
    table_columns: set[str],
) -> int:
    if not rows:
        return 0

    requested_update_columns = {
        "rule_name",
        "rule_description",
        "rule_category",
        "is_active",
        "weight",
        "threshold_value",
        "severity",
        "requires_business_validation",
        "rule_version",
    }
    update_columns = [
        column for column in insert_columns if column in requested_update_columns
    ]
    if not update_columns:
        raise RuntimeError("No dim_fraud_rule columns available to update on rerun")

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
        sql.SQL(", ").join(sql.Identifier(column) for column in insert_columns),
        sql.SQL(", ").join(sql.Placeholder(column) for column in insert_columns),
        sql.Identifier(NATURAL_KEY_COLUMN),
        sql.SQL(", ").join(assignments),
    )

    loaded_count = 0
    for batch in _chunks(rows, BATCH_SIZE):
        cur.executemany(query, batch)
        loaded_count += cur.rowcount if cur.rowcount >= 0 else len(batch)

    return loaded_count


def _count_target_rows(cur: Any) -> int:
    query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
    )
    cur.execute(query)
    return int(cur.fetchone()[0])


def _active_rule_metrics(cur: Any) -> tuple[int, Decimal]:
    query = sql.SQL(
        """
        SELECT
            COUNT(*) FILTER (WHERE is_active IS TRUE) AS active_count,
            COALESCE(SUM(weight) FILTER (WHERE is_active IS TRUE), 0) AS total_weight
        FROM {}.{}
        """
    ).format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
    )
    cur.execute(query)
    active_count, total_weight = cur.fetchone()
    return int(active_count), Decimal(str(total_weight))


def _clean_required_text(value: Any) -> str:
    cleaned = _clean_optional_text(value)
    if cleaned is None:
        raise RuntimeError("Required fraud rule text value cannot be empty")
    return cleaned


def _clean_optional_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    cleaned = str(value).strip()
    return cleaned if cleaned else None


def _coerce_bool(value: Any, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().casefold()
        if normalized in {"true", "yes", "1"}:
            return True
        if normalized in {"false", "no", "0"}:
            return False
    raise RuntimeError(f"{field_name} must be boolean")


def _coerce_decimal(value: Any, field_name: str) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(f"{field_name} must be numeric") from exc


def _chunks(values: list[Any], size: int) -> Iterator[list[Any]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load YAML fraud rule reference rows into iris_score.dim_fraud_rule."
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
