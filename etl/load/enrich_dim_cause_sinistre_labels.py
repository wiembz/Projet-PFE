from __future__ import annotations

import argparse
import re
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
AUTOMOBILE_CODFAM = "5"
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}


warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default",
    category=UserWarning,
    module="openpyxl.styles.stylesheet",
)


@dataclass(frozen=True)
class TargetCauseRow:
    cause_sinistre_sk: int
    code_cause_sinistre: str | None
    code_sous_nature_sinistre: str | None
    libelle_cause_sinistre: str | None
    libelle_sous_nature_sinistre: str | None


@dataclass(frozen=True)
class EnrichmentStats:
    target_rows: int
    matched_cause_label_count: int
    matched_sous_nature_label_count: int
    updated_cause_label_count: int
    updated_sous_nature_label_count: int
    unmatched_count: int


def main() -> None:
    args = _parse_args()
    stats = enrich_dim_cause_sinistre_labels(args.reference_dir)
    print(f"target_rows={stats.target_rows}")
    print(f"matched_cause_label_count={stats.matched_cause_label_count}")
    print(f"matched_sous_nature_label_count={stats.matched_sous_nature_label_count}")
    print(f"updated_cause_label_count={stats.updated_cause_label_count}")
    print(f"updated_sous_nature_label_count={stats.updated_sous_nature_label_count}")
    print(f"unmatched_count={stats.unmatched_count}")


def enrich_dim_cause_sinistre_labels(reference_dir: Path) -> EnrichmentStats:
    reference_dir = _resolve_project_path(reference_dir)
    cause_labels = _read_cause_labels(reference_dir)
    sous_nature_labels = _read_sous_nature_labels(reference_dir)

    conn = get_connection()
    try:
        target_rows = _fetch_target_rows(conn)
        stats = _apply_label_enrichment(
            conn,
            target_rows,
            cause_labels,
            sous_nature_labels,
        )
        conn.commit()
        return stats
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _read_cause_labels(reference_dir: Path) -> dict[str, str]:
    dataframe = _read_sheet(reference_dir / "SI001.xlsx", "Sheet1")
    _require_columns(dataframe, ("CODFAM", "CAUSESINI", "LIBCAUSE"))
    _clean_key_columns(dataframe, ("CODFAM", "CAUSESINI"))
    dataframe["LIBCAUSE"] = dataframe["LIBCAUSE"].map(_clean_label)

    automobile = dataframe.loc[dataframe["CODFAM"] == AUTOMOBILE_CODFAM].copy()
    return _build_unique_label_map(
        automobile,
        key_columns=("CAUSESINI",),
        label_column="LIBCAUSE",
    )


def _read_sous_nature_labels(reference_dir: Path) -> dict[tuple[str, str], str]:
    dataframe = _read_sheet(
        reference_dir / "fichierStagiaire.xlsx",
        "SOUSNATSIN",
    )
    _require_columns(dataframe, ("CODFAM", "CAUSESINI", "SOUNATSIN", "LIBSOUNAT"))
    _clean_key_columns(dataframe, ("CODFAM", "CAUSESINI", "SOUNATSIN"))
    dataframe["LIBSOUNAT"] = dataframe["LIBSOUNAT"].map(_clean_label)

    automobile = dataframe.loc[dataframe["CODFAM"] == AUTOMOBILE_CODFAM].copy()
    return _build_unique_label_map(
        automobile,
        key_columns=("CAUSESINI", "SOUNATSIN"),
        label_column="LIBSOUNAT",
    )


def _fetch_target_rows(conn: Any) -> list[TargetCauseRow]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                cause_sinistre_sk,
                code_cause_sinistre,
                code_sous_nature_sinistre,
                libelle_cause_sinistre,
                libelle_sous_nature_sinistre
            FROM iris_dw.dim_cause_sinistre
            WHERE cause_sinistre_sk <> 0
              AND COALESCE(cause_sinistre_natural_key, '') <> 'UNKNOWN'
            ORDER BY cause_sinistre_sk
            """
        )
        rows = cur.fetchall()

    return [
        TargetCauseRow(
            cause_sinistre_sk=int(row[0]),
            code_cause_sinistre=_clean_key(row[1]),
            code_sous_nature_sinistre=_clean_key(row[2]),
            libelle_cause_sinistre=_clean_label(row[3]),
            libelle_sous_nature_sinistre=_clean_label(row[4]),
        )
        for row in rows
    ]


def _apply_label_enrichment(
    conn: Any,
    target_rows: list[TargetCauseRow],
    cause_labels: dict[str, str],
    sous_nature_labels: dict[tuple[str, str], str],
) -> EnrichmentStats:
    matched_cause_label_count = 0
    matched_sous_nature_label_count = 0
    updated_cause_label_count = 0
    updated_sous_nature_label_count = 0
    unmatched_count = 0

    with conn.cursor() as cur:
        for row in target_rows:
            cause_label = _matched_cause_label(row, cause_labels)
            sous_nature_label = _matched_sous_nature_label(row, sous_nature_labels)

            if cause_label is not None:
                matched_cause_label_count += 1
                if row.libelle_cause_sinistre != cause_label:
                    updated_cause_label_count += _update_cause_label(
                        cur,
                        row.cause_sinistre_sk,
                        cause_label,
                    )

            if sous_nature_label is not None:
                matched_sous_nature_label_count += 1
                if row.libelle_sous_nature_sinistre != sous_nature_label:
                    updated_sous_nature_label_count += _update_sous_nature_label(
                        cur,
                        row.cause_sinistre_sk,
                        sous_nature_label,
                    )

            if cause_label is None and sous_nature_label is None:
                unmatched_count += 1

    return EnrichmentStats(
        target_rows=len(target_rows),
        matched_cause_label_count=matched_cause_label_count,
        matched_sous_nature_label_count=matched_sous_nature_label_count,
        updated_cause_label_count=updated_cause_label_count,
        updated_sous_nature_label_count=updated_sous_nature_label_count,
        unmatched_count=unmatched_count,
    )


def _matched_cause_label(
    row: TargetCauseRow,
    cause_labels: dict[str, str],
) -> str | None:
    if row.code_cause_sinistre is None:
        return None
    return cause_labels.get(row.code_cause_sinistre)


def _matched_sous_nature_label(
    row: TargetCauseRow,
    sous_nature_labels: dict[tuple[str, str], str],
) -> str | None:
    if row.code_cause_sinistre is None or row.code_sous_nature_sinistre is None:
        return None
    return sous_nature_labels.get(
        (row.code_cause_sinistre, row.code_sous_nature_sinistre)
    )


def _update_cause_label(cur: Any, cause_sinistre_sk: int, label: str) -> int:
    cur.execute(
        """
        UPDATE iris_dw.dim_cause_sinistre
        SET libelle_cause_sinistre = %(label)s
        WHERE cause_sinistre_sk = %(cause_sinistre_sk)s
          AND cause_sinistre_sk <> 0
          AND libelle_cause_sinistre IS DISTINCT FROM %(label)s
        """,
        {
            "cause_sinistre_sk": cause_sinistre_sk,
            "label": label,
        },
    )
    return int(cur.rowcount)


def _update_sous_nature_label(cur: Any, cause_sinistre_sk: int, label: str) -> int:
    cur.execute(
        """
        UPDATE iris_dw.dim_cause_sinistre
        SET libelle_sous_nature_sinistre = %(label)s
        WHERE cause_sinistre_sk = %(cause_sinistre_sk)s
          AND cause_sinistre_sk <> 0
          AND libelle_sous_nature_sinistre IS DISTINCT FROM %(label)s
        """,
        {
            "cause_sinistre_sk": cause_sinistre_sk,
            "label": label,
        },
    )
    return int(cur.rowcount)


def _build_unique_label_map(
    dataframe: pd.DataFrame,
    key_columns: tuple[str, ...],
    label_column: str,
) -> dict[Any, str]:
    result: dict[Any, str] = {}

    for key_values, group in dataframe.groupby(list(key_columns), dropna=True):
        if not isinstance(key_values, tuple):
            key_values = (key_values,)

        labels = sorted(
            {
                label
                for label in group[label_column].tolist()
                if _clean_label(label) is not None
            }
        )
        if not labels:
            continue
        if len(labels) > 1:
            key_text = "|".join(str(value) for value in key_values)
            raise RuntimeError(
                f"Conflicting labels in reference data for {key_text}: {labels}"
            )

        map_key: Any
        if len(key_values) == 1:
            map_key = key_values[0]
        else:
            map_key = tuple(key_values)
        result[map_key] = labels[0]

    return result


def _read_sheet(workbook_path: Path, sheet_name: str) -> pd.DataFrame:
    if not workbook_path.exists():
        raise FileNotFoundError(f"Reference workbook not found: {workbook_path}")

    return pd.read_excel(
        workbook_path,
        sheet_name=sheet_name,
        dtype=str,
        engine="openpyxl",
    )


def _require_columns(dataframe: pd.DataFrame, columns: tuple[str, ...]) -> None:
    missing = [column for column in columns if column not in dataframe.columns]
    if missing:
        raise RuntimeError(f"Reference file is missing columns: {', '.join(missing)}")


def _clean_key_columns(dataframe: pd.DataFrame, columns: tuple[str, ...]) -> None:
    for column in columns:
        dataframe[column] = dataframe[column].map(_clean_key)


def _clean_key(value: Any) -> str | None:
    if pd.isna(value):
        return None

    cleaned = str(value).strip()
    if cleaned.casefold() in NULL_MARKERS:
        return None

    match = re.fullmatch(r"([+-]?\d+)\.0", cleaned)
    if match:
        cleaned = match.group(1)

    return cleaned


def _clean_label(value: Any) -> str | None:
    if pd.isna(value):
        return None

    cleaned = str(value).strip()
    if cleaned.casefold() in NULL_MARKERS:
        return None

    return cleaned


def _resolve_project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Enrich existing iris_dw.dim_cause_sinistre labels from official "
            "automobile reference files."
        )
    )
    parser.add_argument(
        "--reference-dir",
        type=Path,
        default=REFERENCE_DIR,
        help="Directory containing SI001.xlsx and fichierStagiaire.xlsx.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
