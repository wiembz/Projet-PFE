from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ScoringStep:
    label: str
    script_path: Path
    arguments: tuple[str, ...] = ()


def main() -> int:
    args = _parse_args()
    return run_scoring(
        etl_run_id=args.etl_run_id,
        fraud_run_version=args.fraud_run_version,
        fraud_rules_version=args.fraud_rules_version,
        vhs_run_version=args.vhs_run_version,
        vhs_rules_version=args.vhs_rules_version,
    )


def run_scoring(
    *,
    etl_run_id: str,
    fraud_run_version: str,
    fraud_rules_version: str,
    vhs_run_version: str,
    vhs_rules_version: str,
) -> int:
    _validate_etl_run_id(etl_run_id)
    _validate_required_text(fraud_run_version, "--fraud-run-version")
    _validate_required_text(fraud_rules_version, "--fraud-rules-version")
    _validate_required_text(vhs_run_version, "--vhs-run-version")
    _validate_required_text(vhs_rules_version, "--vhs-rules-version")

    steps = _scoring_steps(
        etl_run_id=etl_run_id,
        fraud_run_version=fraud_run_version,
        fraud_rules_version=fraud_rules_version,
        vhs_run_version=vhs_run_version,
        vhs_rules_version=vhs_rules_version,
    )
    _assert_scripts_exist(steps)

    total_steps = len(steps)
    for index, step in enumerate(steps, start=1):
        print(_step_banner(index, total_steps, step), flush=True)
        return_code = _run_step(step)
        if return_code != 0:
            print(
                f"[FAILED] {step.label} exited with return code {return_code}",
                flush=True,
            )
            return return_code

    print("Scoring orchestration completed successfully.", flush=True)
    return 0


def _scoring_steps(
    *,
    etl_run_id: str,
    fraud_run_version: str,
    fraud_rules_version: str,
    vhs_run_version: str,
    vhs_rules_version: str,
) -> tuple[ScoringStep, ...]:
    load_dir = PROJECT_ROOT / "etl" / "load"
    scoring_dir = PROJECT_ROOT / "etl" / "scoring"
    quality_dir = PROJECT_ROOT / "etl" / "quality"

    return (
        ScoringStep(
            label="Load fraud rules",
            script_path=load_dir / "load_dim_fraud_rule.py",
        ),
        ScoringStep(
            label="Run fraud scoring",
            script_path=scoring_dir / "run_fraud_scoring.py",
            arguments=(
                "--etl-run-id",
                etl_run_id,
                "--run-version",
                fraud_run_version,
                "--rules-version",
                fraud_rules_version,
            ),
        ),
        ScoringStep(
            label="Run VHS scoring",
            script_path=scoring_dir / "run_vhs_scoring.py",
            arguments=(
                "--etl-run-id",
                etl_run_id,
                "--run-version",
                vhs_run_version,
                "--rules-version",
                vhs_rules_version,
            ),
        ),
        ScoringStep(
            label="Validate iris_mart views",
            script_path=quality_dir / "validate_iris_mart_views.py",
        ),
    )


def _assert_scripts_exist(steps: tuple[ScoringStep, ...]) -> None:
    missing_scripts = [
        str(step.script_path.relative_to(PROJECT_ROOT))
        for step in steps
        if not step.script_path.exists()
    ]
    if missing_scripts:
        missing = "\n".join(missing_scripts)
        raise FileNotFoundError(f"Required scoring orchestration script(s) missing:\n{missing}")


def _run_step(step: ScoringStep) -> int:
    command = [
        sys.executable,
        str(step.script_path),
        *step.arguments,
    ]
    completed = subprocess.run(command, cwd=PROJECT_ROOT)
    return int(completed.returncode)


def _step_banner(index: int, total_steps: int, step: ScoringStep) -> str:
    relative_script = step.script_path.relative_to(PROJECT_ROOT)
    return (
        "\n"
        + "=" * 80
        + f"\n[{index}/{total_steps}] {step.label}\n"
        + f"Script: {relative_script}\n"
        + "=" * 80
    )


def _validate_etl_run_id(etl_run_id: str) -> None:
    _validate_required_text(etl_run_id, "--etl-run-id")
    if any(part in etl_run_id for part in ("/", "\\", "..")):
        raise ValueError("--etl-run-id must be a single run folder name")
    if etl_run_id.endswith("."):
        raise ValueError("--etl-run-id cannot end with a dot")


def _validate_required_text(value: str, option_name: str) -> None:
    if value != value.strip():
        raise ValueError(f"{option_name} cannot contain leading or trailing spaces")
    if not value:
        raise ValueError(f"{option_name} cannot be empty")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run validated IRISv2 scoring scripts and mart validation."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id to score.",
    )
    parser.add_argument(
        "--fraud-run-version",
        default="v1",
        help="Fraud scoring run version. Defaults to v1.",
    )
    parser.add_argument(
        "--fraud-rules-version",
        default="v1",
        help="Fraud rules version. Defaults to v1.",
    )
    parser.add_argument(
        "--vhs-run-version",
        default="v1",
        help="VHS scoring run version. Defaults to v1.",
    )
    parser.add_argument(
        "--vhs-rules-version",
        default="v1",
        help="VHS rules version. Defaults to v1.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
