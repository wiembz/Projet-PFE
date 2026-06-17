from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator

import psycopg
from dotenv import load_dotenv
from psycopg import Connection


REQUIRED_ENV_VARS = (
    "IRIS_DB_HOST",
    "IRIS_DB_PORT",
    "IRIS_DB_NAME",
    "IRIS_DB_USER",
    "IRIS_DB_PASSWORD",
)


def _load_db_config() -> dict[str, str]:
    load_dotenv()

    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        names = ", ".join(missing)
        raise RuntimeError(f"Missing PostgreSQL environment variables: {names}")

    return {
        "host": os.environ["IRIS_DB_HOST"],
        "port": os.environ["IRIS_DB_PORT"],
        "dbname": os.environ["IRIS_DB_NAME"],
        "user": os.environ["IRIS_DB_USER"],
        "password": os.environ["IRIS_DB_PASSWORD"],
    }


def get_connection() -> Connection:
    """
    Create a direct psycopg connection using the locked IRIS_DB_* settings.
    """
    return psycopg.connect(**_load_db_config())


@contextmanager
def managed_connection() -> Iterator[Connection]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def get_engine() -> Any:
    """
    Compatibility hook for legacy scripts that still use SQLAlchemy.
    New loaders should prefer get_connection().
    """
    from sqlalchemy import create_engine

    config = _load_db_config()
    url = (
        f"postgresql+psycopg2://{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['dbname']}"
    )

    return create_engine(url, future=True)


def start_etl_run(
    conn: Connection,
    *,
    etl_run_id: str,
    run_name: str,
    started_at: datetime,
    source_snapshot: str,
) -> None:
    _assert_etl_run_contract(conn)
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO iris_admin.etl_run (
                etl_run_id,
                run_name,
                started_at,
                ended_at,
                status,
                source_snapshot,
                input_count,
                output_count,
                rejected_count,
                error_message,
                created_at
            )
            VALUES (
                %(etl_run_id)s,
                %(run_name)s,
                %(started_at)s,
                NULL,
                'STARTED',
                %(source_snapshot)s,
                0,
                0,
                0,
                NULL,
                %(created_at)s
            )
            """,
            {
                "etl_run_id": etl_run_id,
                "run_name": run_name,
                "started_at": started_at,
                "source_snapshot": source_snapshot,
                "created_at": started_at,
            },
        )
    conn.commit()


def finish_etl_run(
    conn: Connection,
    *,
    etl_run_id: str,
    status: str,
    ended_at: datetime,
    source_snapshot: str,
    input_count: int,
    output_count: int,
    rejected_count: int,
    error_message: str | None,
) -> None:
    if status not in {"SUCCESS", "FAILED"}:
        raise ValueError("status must be SUCCESS or FAILED")

    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE iris_admin.etl_run
            SET ended_at = %(ended_at)s,
                status = %(status)s,
                source_snapshot = %(source_snapshot)s,
                input_count = %(input_count)s,
                output_count = %(output_count)s,
                rejected_count = %(rejected_count)s,
                error_message = %(error_message)s
            WHERE etl_run_id = %(etl_run_id)s
            """,
            {
                "etl_run_id": etl_run_id,
                "ended_at": ended_at,
                "status": status,
                "source_snapshot": source_snapshot,
                "input_count": input_count,
                "output_count": output_count,
                "rejected_count": rejected_count,
                "error_message": error_message,
            },
        )
        if cur.rowcount != 1:
            raise RuntimeError(f"etl_run row not found for etl_run_id={etl_run_id}")
    conn.commit()


def assert_etl_run_table_compatible() -> None:
    """
    Fail fast if iris_admin.etl_run is missing required columns.
    No automatic DDL.
    """
    with managed_connection() as conn:
        _assert_etl_run_contract(conn)


def _assert_etl_run_contract(conn: Connection) -> None:
    expected_columns = {
        "etl_run_id",
        "run_name",
        "started_at",
        "ended_at",
        "status",
        "source_snapshot",
        "input_count",
        "output_count",
        "rejected_count",
        "error_message",
        "created_at",
    }

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'iris_admin'
              AND table_name = 'etl_run'
            """
        )
        found_columns = {row[0] for row in cur.fetchall()}

    missing_columns = sorted(expected_columns - found_columns)
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"iris_admin.etl_run is missing required columns: {missing}")
