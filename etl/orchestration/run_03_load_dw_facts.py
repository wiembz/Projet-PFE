from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.step_logging import fail_step_run, finish_step_run, start_step_run


@dataclass(frozen=True)
class FactLoadStep:
    label: str
    script_path: Path


def main() -> int:
    args = _parse_args()
    return run_dw_fact_loads(args.etl_run_id)


def run_dw_fact_loads(etl_run_id: str) -> int:
    _validate_etl_run_id(etl_run_id)

    steps = _fact_load_steps()
    total_steps = len(steps)

    for index, step in enumerate(steps, start=1):
        print(_step_banner(index, total_steps, step), flush=True)
        relative_script = str(step.script_path.relative_to(PROJECT_ROOT))
        step_run_id = start_step_run(
            etl_run_id,
            step.label,
            step_order=index,
            script_path=relative_script,
        )
        try:
            _run_step(step, etl_run_id)
        except subprocess.CalledProcessError as exc:
            fail_step_run(step_run_id, exc)
            print(
                f"[FAILED] {step.label} exited with return code {exc.returncode}",
                flush=True,
            )
            raise
        except Exception as exc:
            fail_step_run(step_run_id, exc)
            raise
        else:
            finish_step_run(step_run_id, status="SUCCESS")

    print("DW facts orchestration completed successfully.", flush=True)
    return 0


def _fact_load_steps() -> tuple[FactLoadStep, ...]:
    load_dir = PROJECT_ROOT / "etl" / "load"
    return (
        FactLoadStep(
            label="Load fact_prime",
            script_path=load_dir / "load_fact_prime.py",
        ),
        FactLoadStep(
            label="Load fact_sinistre",
            script_path=load_dir / "load_fact_sinistre.py",
        ),
        FactLoadStep(
            label="Load fact_inspection",
            script_path=load_dir / "load_fact_inspection.py",
        ),
        FactLoadStep(
            label="Load fact_inspection_checkpoint",
            script_path=load_dir / "load_fact_inspection_checkpoint.py",
        ),
    )


def _run_step(step: FactLoadStep, etl_run_id: str) -> int:
    if not step.script_path.exists():
        raise FileNotFoundError(f"Fact loader not found: {step.script_path}")

    command = [
        sys.executable,
        str(step.script_path),
        "--etl-run-id",
        etl_run_id,
    ]

    completed = subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    return int(completed.returncode)


def _step_banner(index: int, total_steps: int, step: FactLoadStep) -> str:
    relative_script = step.script_path.relative_to(PROJECT_ROOT)
    return (
        "\n"
        + "=" * 80
        + f"\n[{index}/{total_steps}] {step.label}\n"
        + f"Script: {relative_script}\n"
        + "=" * 80
    )


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
        description="Run validated IRISv2 DW fact loaders only."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id containing data/silver/<etl_run_id> fact inputs.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
