from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATHS_CONFIG = PROJECT_ROOT / "etl" / "config" / "paths.yaml"


@dataclass(frozen=True)
class SourceConfig:
    name: str
    file_path: Path
    sheet_name: int | str


@dataclass(frozen=True)
class PathsConfig:
    raw_dir: Path
    bronze_dir: Path
    sources: tuple[SourceConfig, ...]


def project_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_paths_config(config_path: str | Path = DEFAULT_PATHS_CONFIG) -> PathsConfig:
    config_file = project_path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Paths config not found: {config_file}")

    with config_file.open("r", encoding="utf-8") as handle:
        payload: dict[str, Any] = yaml.safe_load(handle) or {}

    raw_dir = project_path(_required(payload, "raw_dir"))
    bronze_dir = project_path(_required(payload, "bronze_dir"))
    source_payload = _required(payload, "sources")

    if not isinstance(source_payload, dict) or not source_payload:
        raise ValueError("paths.yaml must define a non-empty 'sources' mapping")

    sources: list[SourceConfig] = []
    for source_name, source_config in source_payload.items():
        if not isinstance(source_config, dict):
            raise ValueError(f"Source '{source_name}' must be a mapping")

        file_name = _required(source_config, "file")
        sheet_name = source_config.get("sheet_name", 0)
        source_file = raw_dir / str(file_name)

        if not source_file.exists():
            raise FileNotFoundError(f"Raw source file not found: {source_file}")

        sources.append(
            SourceConfig(
                name=str(source_name),
                file_path=source_file,
                sheet_name=sheet_name,
            )
        )

    return PathsConfig(raw_dir=raw_dir, bronze_dir=bronze_dir, sources=tuple(sources))


def create_bronze_run_dir(etl_run_id: str, config: PathsConfig) -> Path:
    run_dir = config.bronze_dir / etl_run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def _required(payload: dict[str, Any], key: str) -> Any:
    if key not in payload:
        raise ValueError(f"Missing required paths config key: {key}")
    return payload[key]
