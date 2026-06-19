from __future__ import annotations

from etl.common.db import get_connection


STARTED_STATUS = "STARTED"
FINISH_STATUSES = {"SUCCESS", "FAILED", "SKIPPED"}


def start_step_run(
    etl_run_id: str,
    step_name: str,
    step_order: int | None = None,
    script_path: str | None = None,
) -> int:
    """Create an ETL step audit row and return its generated id."""
    if _is_blank(etl_run_id):
        raise ValueError("etl_run_id must not be empty")
    if _is_blank(step_name):
        raise ValueError("step_name must not be empty")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO iris_admin.etl_step_run (
                    etl_run_id,
                    step_name,
                    step_order,
                    script_path,
                    status
                )
                VALUES (
                    %(etl_run_id)s,
                    %(step_name)s,
                    %(step_order)s,
                    %(script_path)s,
                    %(status)s
                )
                RETURNING step_run_id
                """,
                {
                    "etl_run_id": etl_run_id,
                    "step_name": step_name,
                    "step_order": step_order,
                    "script_path": script_path,
                    "status": STARTED_STATUS,
                },
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError("etl_step_run insert did not return step_run_id")
            step_run_id = int(row[0])
        conn.commit()
        return step_run_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def finish_step_run(
    step_run_id: int,
    status: str = "SUCCESS",
    input_count: int | None = None,
    output_count: int | None = None,
    rejected_count: int | None = None,
    warning_count: int | None = None,
    error_message: str | None = None,
) -> None:
    """Close an ETL step audit row with status and optional counters."""
    if status not in FINISH_STATUSES:
        allowed = ", ".join(sorted(FINISH_STATUSES))
        raise ValueError(f"status must be one of: {allowed}")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE iris_admin.etl_step_run
                SET ended_at = now(),
                    status = %(status)s,
                    input_count = COALESCE(%(input_count)s, input_count),
                    output_count = COALESCE(%(output_count)s, output_count),
                    rejected_count = COALESCE(%(rejected_count)s, rejected_count),
                    warning_count = COALESCE(%(warning_count)s, warning_count),
                    error_message = %(error_message)s
                WHERE step_run_id = %(step_run_id)s
                """,
                {
                    "step_run_id": step_run_id,
                    "status": status,
                    "input_count": input_count,
                    "output_count": output_count,
                    "rejected_count": rejected_count,
                    "warning_count": warning_count,
                    "error_message": error_message,
                },
            )
            if cur.rowcount != 1:
                raise RuntimeError(
                    f"etl_step_run row not found for step_run_id={step_run_id}"
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fail_step_run(
    step_run_id: int,
    error: BaseException | str,
    input_count: int | None = None,
    output_count: int | None = None,
    rejected_count: int | None = None,
    warning_count: int | None = None,
) -> None:
    """Close an ETL step audit row as FAILED with the error message."""
    finish_step_run(
        step_run_id,
        status="FAILED",
        input_count=input_count,
        output_count=output_count,
        rejected_count=rejected_count,
        warning_count=warning_count,
        error_message=str(error),
    )


def _is_blank(value: str) -> bool:
    return not value or not value.strip()
