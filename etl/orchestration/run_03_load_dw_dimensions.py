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
class DimensionLoadStep:
    label: str
    script_path: Path
    arguments: tuple[str, ...] = ()
    needs_etl_run_id: bool = False


def main() -> int:
    args = _parse_args()
    return run_dw_dimension_loads(args.etl_run_id)


def run_dw_dimension_loads(etl_run_id: str) -> int:
    _validate_etl_run_id(etl_run_id)

    steps = _dimension_load_steps()
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

    print("DW dimensions orchestration completed successfully.", flush=True)
    return 0


def _dimension_load_steps() -> tuple[DimensionLoadStep, ...]:
    load_dir = PROJECT_ROOT / "etl" / "load"
    return (
        DimensionLoadStep(
            label="Load dim_date",
            script_path=load_dir / "load_dim_date.py",
            arguments=(
                "--start-date",
                "2000-01-01",
                "--end-date",
                "2050-12-31",
            ),
        ),
        DimensionLoadStep(
            label="Load dim_client",
            script_path=load_dir / "load_dim_client.py",
            needs_etl_run_id=True,
        ),
        DimensionLoadStep(
            label="Load dim_produit",
            script_path=load_dir / "load_dim_produit.py",
            needs_etl_run_id=True,
        ),
        DimensionLoadStep(
            label="Load dim_delegation",
            script_path=load_dir / "load_dim_delegation.py",
            needs_etl_run_id=True,
        ),
        DimensionLoadStep(
            label="Load dim_intermediaire",
            script_path=load_dir / "load_dim_intermediaire.py",
            needs_etl_run_id=True,
        ),
        DimensionLoadStep(
            label="Load dim_garantie",
            script_path=load_dir / "load_dim_garantie.py",
            needs_etl_run_id=True,
        ),
        DimensionLoadStep(
            label="Load dim_cause_sinistre",
            script_path=load_dir / "load_dim_cause_sinistre.py",
            needs_etl_run_id=True,
        ),
        DimensionLoadStep(
            label="Enrich dim_cause_sinistre labels",
            script_path=load_dir / "enrich_dim_cause_sinistre_labels.py",
        ),
        DimensionLoadStep(
            label="Load dim_vehicule",
            script_path=load_dir / "load_dim_vehicule.py",
            needs_etl_run_id=True,
        ),
        DimensionLoadStep(
            label="Load dim_contrat",
            script_path=load_dir / "load_dim_contrat.py",
            needs_etl_run_id=True,
        ),
    )


def _run_step(step: DimensionLoadStep, etl_run_id: str) -> int:
    if not step.script_path.exists():
        raise FileNotFoundError(f"Dimension loader not found: {step.script_path}")

    command = [
        sys.executable,
        str(step.script_path),
        *step.arguments,
    ]
    if step.needs_etl_run_id:
        command.extend(("--etl-run-id", etl_run_id))

    completed = subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    return int(completed.returncode)


def _step_banner(index: int, total_steps: int, step: DimensionLoadStep) -> str:
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
        description="Run validated IRISv2 DW dimension loaders only."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id containing data/silver/<etl_run_id> dimension inputs.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
