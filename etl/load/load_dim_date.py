from __future__ import annotations

import argparse
import calendar
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


TARGET_SCHEMA = "iris_dw"
TARGET_TABLE = "dim_date"
REQUIRED_COLUMNS = (
    "date_sk",
    "date_val",
    "annee",
    "trimestre",
    "mois",
    "nom_mois",
    "jour",
    "jour_semaine",
    "nom_jour_semaine",
    "annee_mois",
)
OPTIONAL_COLUMNS = (
    "week_of_year",
    "is_weekend",
)


@dataclass(frozen=True)
class LoadStats:
    total_generated: int
    total_loaded: int


def main() -> None:
    args = _parse_args()
    stats = load_dim_date(args.start_date, args.end_date)
    print(f"total_generated={stats.total_generated}")
    print(f"total_loaded={stats.total_loaded}")


def load_dim_date(start_date: str, end_date: str) -> LoadStats:
    start = _parse_iso_date(start_date, "--start-date")
    end = _parse_iso_date(end_date, "--end-date")
    if start > end:
        raise ValueError("--start-date must be less than or equal to --end-date")

    rows = _generate_date_rows(start, end)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_columns = _get_table_columns(cur)
            _assert_required_columns(table_columns)
            _assert_date_sk_conflict_target(cur)

            load_columns = _load_columns(table_columns)
            total_loaded = _upsert_dim_date_rows(cur, rows, load_columns)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return LoadStats(total_generated=len(rows), total_loaded=total_loaded)


def _generate_date_rows(start_date: date, end_date: date) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current = start_date

    while current <= end_date:
        iso_calendar = current.isocalendar()
        rows.append(
            {
                "date_sk": int(current.strftime("%Y%m%d")),
                "date_val": current,
                "annee": current.year,
                "trimestre": ((current.month - 1) // 3) + 1,
                "mois": current.month,
                "nom_mois": calendar.month_name[current.month],
                "jour": current.day,
                "jour_semaine": current.isoweekday(),
                "nom_jour_semaine": calendar.day_name[current.weekday()],
                "annee_mois": f"{current.year}-{current.month:02d}",
                "week_of_year": iso_calendar.week,
                "is_weekend": current.isoweekday() in (6, 7),
            }
        )
        current += timedelta(days=1)

    return rows


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


def _assert_required_columns(table_columns: set[str]) -> None:
    missing_columns = sorted(set(REQUIRED_COLUMNS) - table_columns)
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} is missing required columns: {missing}"
        )


def _assert_date_sk_conflict_target(cur: Any) -> None:
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
          AND a.attname = 'date_sk'
        LIMIT 1
        """,
        {
            "schema": TARGET_SCHEMA,
            "table": TARGET_TABLE,
        },
    )
    if cur.fetchone() is None:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} must have a primary or unique "
            "constraint on date_sk for idempotent loading"
        )


def _load_columns(table_columns: set[str]) -> list[str]:
    columns = list(REQUIRED_COLUMNS)
    columns.extend(column for column in OPTIONAL_COLUMNS if column in table_columns)
    return columns


def _upsert_dim_date_rows(
    cur: Any,
    rows: list[dict[str, Any]],
    columns: list[str],
) -> int:
    update_columns = [column for column in columns if column != "date_sk"]
    assignments = sql.SQL(", ").join(
        sql.SQL("{} = EXCLUDED.{}").format(
            sql.Identifier(column),
            sql.Identifier(column),
        )
        for column in update_columns
    )

    query = sql.SQL(
        """
        INSERT INTO {}.{} ({})
        VALUES ({})
        ON CONFLICT (date_sk) DO UPDATE
        SET {}
        """
    ).format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        sql.SQL(", ").join(sql.Placeholder(column) for column in columns),
        assignments,
    )

    cur.executemany(
        query,
        [{column: row[column] for column in columns} for row in rows],
    )
    return cur.rowcount if cur.rowcount >= 0 else len(rows)


def _parse_iso_date(value: str, argument_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{argument_name} must use YYYY-MM-DD format") from exc


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load iris_dw.dim_date for a calendar date range."
    )
    parser.add_argument(
        "--start-date",
        required=True,
        help="Inclusive start date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--end-date",
        required=True,
        help="Inclusive end date in YYYY-MM-DD format.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
