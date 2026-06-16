from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import finish_etl_run, managed_connection, start_etl_run
from etl.common.paths import SourceConfig, create_bronze_run_dir, load_paths_config


RUN_NAME = "excel_to_bronze"
TECHNICAL_COLUMNS = (
    "etl_run_id",
    "source_name",
    "source_file",
    "source_row_number",
    "source_file_hash",
    "ingested_at",
)


def main() -> None:
    run_excel_to_bronze()


def run_excel_to_bronze() -> str:
    config = load_paths_config()
    etl_run_id = str(uuid4())
    started_at = _utc_now()
    initial_snapshot = _build_source_snapshot(config.sources)

    input_count = 0
    output_count = 0
    rejected_count = 0
    final_snapshot = initial_snapshot

    with managed_connection() as conn:
        start_etl_run(
            conn,
            etl_run_id=etl_run_id,
            run_name=RUN_NAME,
            started_at=started_at,
            source_snapshot=initial_snapshot,
        )

        try:
            create_bronze_run_dir(etl_run_id, config)

            for source in config.sources:
                source_hash = _sha256_file(source.file_path)
                dataframe = _read_excel_raw(source)
                row_count = len(dataframe)

                dataframe = _add_technical_metadata(
                    dataframe,
                    etl_run_id=etl_run_id,
                    source=source,
                    source_file_hash=source_hash,
                    ingested_at=started_at,
                )

                write_bronze_parquet(
                    dataframe,
                    config.bronze_dir,
                    source.name,
                    etl_run_id,
                )

                input_count += row_count
                output_count += row_count

            final_snapshot = _build_source_snapshot(config.sources)
            finish_etl_run(
                conn,
                etl_run_id=etl_run_id,
                status="SUCCESS",
                ended_at=_utc_now(),
                source_snapshot=final_snapshot,
                input_count=input_count,
                output_count=output_count,
                rejected_count=rejected_count,
                error_message=None,
            )
            return etl_run_id

        except Exception as exc:
            conn.rollback()
            finish_etl_run(
                conn,
                etl_run_id=etl_run_id,
                status="FAILED",
                ended_at=_utc_now(),
                source_snapshot=final_snapshot,
                input_count=input_count,
                output_count=output_count,
                rejected_count=rejected_count,
                error_message=str(exc),
            )
            raise


def write_bronze_parquet(
    dataframe: pd.DataFrame,
    bronze_dir: Path,
    source_name: str,
    etl_run_id: str,
) -> Path:
    """
    Ecrit le DataFrame bronze en Parquet.
    Structure validee :
    data/bronze/<etl_run_id>/<source_name>.parquet
    """
    output_dir = bronze_dir / etl_run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{source_name}.parquet"
    dataframe.to_parquet(output_file, index=False, engine="pyarrow")

    return output_file


def _read_excel_raw(source: SourceConfig) -> pd.DataFrame:
    headers = _read_excel_headers(source)
    dataframe = pd.read_excel(
        source.file_path,
        sheet_name=source.sheet_name,
        header=None,
        skiprows=1,
        names=headers,
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )
    _assert_no_technical_column_collision(source.name, dataframe.columns)
    return dataframe


def _read_excel_headers(source: SourceConfig) -> list[str]:
    header_frame = pd.read_excel(
        source.file_path,
        sheet_name=source.sheet_name,
        header=None,
        nrows=1,
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )

    if header_frame.empty:
        raise ValueError(f"Source '{source.name}' has no header row")

    raw_headers = [str(value) for value in header_frame.iloc[0].tolist()]
    if any(value == "" for value in raw_headers):
        raise ValueError(f"Source '{source.name}' contains empty header cells")

    return _make_unique_columns(raw_headers)


def _make_unique_columns(columns: list[str]) -> list[str]:
    seen: Counter[str] = Counter()
    unique_columns: list[str] = []

    for column in columns:
        seen[column] += 1
        if seen[column] == 1:
            unique_columns.append(column)
        else:
            unique_columns.append(f"{column}__dup{seen[column]}")

    return unique_columns


def _assert_no_technical_column_collision(source_name: str, columns: pd.Index) -> None:
    collisions = sorted(set(columns) & set(TECHNICAL_COLUMNS))
    if collisions:
        joined = ", ".join(collisions)
        raise ValueError(
            f"Source '{source_name}' already contains reserved Bronze metadata columns: {joined}"
        )


def _add_technical_metadata(
    dataframe: pd.DataFrame,
    *,
    etl_run_id: str,
    source: SourceConfig,
    source_file_hash: str,
    ingested_at: datetime,
) -> pd.DataFrame:
    result = dataframe.copy()
    row_count = len(result)

    result["etl_run_id"] = etl_run_id
    result["source_name"] = source.name
    result["source_file"] = str(source.file_path)
    result["source_row_number"] = range(2, row_count + 2)
    result["source_file_hash"] = source_file_hash
    result["ingested_at"] = ingested_at.isoformat()

    return result


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _build_source_snapshot(
    sources: tuple[SourceConfig, ...],
) -> str:
    return json.dumps(
        {source.name: source.file_path.name for source in sources},
        ensure_ascii=False,
    )


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


if __name__ == "__main__":
    main()
