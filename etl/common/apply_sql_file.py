from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


def main() -> None:
    args = _parse_args()
    sql_path = _resolve_project_path(args.sql_file)
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    sql_text = sql_path.read_text(encoding="utf-8")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql_text)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print(f"[OK] Applied SQL file: {sql_path}")


def _resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply a SQL file using IRIS_DB_* settings and direct psycopg."
    )
    parser.add_argument("sql_file", help="Path to the SQL file to apply.")
    return parser.parse_args()


if __name__ == "__main__":
    main()
