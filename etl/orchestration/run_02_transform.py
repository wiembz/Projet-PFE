from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"
TRANSFORM_DIR = PROJECT_ROOT / "etl" / "transform"


@dataclass(frozen=True)
class SilverTransform:
    label: str
    script_name: str
    output_name: str


TRANSFORMS = (
    SilverTransform(
        label="clients",
        script_name="clean_clients.py",
        output_name="clients.parquet",
    ),
    SilverTransform(
        label="production",
        script_name="clean_production.py",
        output_name="production.parquet",
    ),
    SilverTransform(
        label="sinistres",
        script_name="clean_sinistres.py",
        output_name="sinistres.parquet",
    ),
    SilverTransform(
        label="fiche_voiture_stafim",
        script_name="clean_fiche_stafim.py",
        output_name="fiche_voiture_stafim.parquet",
    ),
)


def main() -> None:
    args = _parse_args()
    run_silver_transforms(args.etl_run_id)


def run_silver_transforms(etl_run_id: str) -> list[Path]:
    _validate_etl_run_id(etl_run_id)

    total_steps = len(TRANSFORMS)
    for index, transform in enumerate(TRANSFORMS, start=1):
        print(f"[{index}/{total_steps}] Silver {transform.label}", flush=True)
        _run_transform_script(transform, etl_run_id)

    output_files = _expected_output_files(etl_run_id)
    _assert_output_files_exist(output_files)

    print("SUCCESS Silver transforms completed", flush=True)
    for output_file in output_files:
        print(output_file, flush=True)

    return output_files


def _run_transform_script(transform: SilverTransform, etl_run_id: str) -> None:
    script_path = TRANSFORM_DIR / transform.script_name
    if not script_path.exists():
        raise FileNotFoundError(f"Transform script not found: {script_path}")

    command = [
        sys.executable,
        str(script_path),
        "--etl-run-id",
        etl_run_id,
    ]
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def _expected_output_files(etl_run_id: str) -> list[Path]:
    return [
        SILVER_DIR / etl_run_id / transform.output_name
        for transform in TRANSFORMS
    ]


def _assert_output_files_exist(output_files: list[Path]) -> None:
    missing_files = [path for path in output_files if not path.exists()]
    if missing_files:
        missing = "\n".join(str(path) for path in missing_files)
        raise FileNotFoundError(f"Missing Silver output files:\n{missing}")


def _validate_etl_run_id(etl_run_id: str) -> None:
    if etl_run_id != etl_run_id.strip():
        raise ValueError("--etl-run-id cannot contain leading or trailing spaces")

    if not etl_run_id:
        raise ValueError("--etl-run-id cannot be empty")

    if any(part in etl_run_id for part in ("/", "\\", "..")):
        raise ValueError("--etl-run-id must be a single run folder name")

    if etl_run_id.endswith("."):
        raise ValueError("--etl-run-id cannot end with a dot")

    bronze_dir = BRONZE_DIR / etl_run_id
    if not bronze_dir.exists():
        raise FileNotFoundError(f"Bronze run folder not found: {bronze_dir}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run all Silver transforms for one ETL run id."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id containing data/bronze/<etl_run_id> input files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
