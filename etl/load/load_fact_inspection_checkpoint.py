from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterator

import pandas as pd
import yaml
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


SILVER_DIR = PROJECT_ROOT / "data" / "silver"
CHECKPOINT_CONFIG_FILE = PROJECT_ROOT / "etl" / "config" / "checkpoints.yaml"
TARGET_SCHEMA = "iris_dw"
TARGET_TABLE = "fact_inspection_checkpoint"
SOURCE_SYSTEM_VALUE = "FicheVoitureStafim.xlsx"
UNKNOWN_CHECKPOINT_KEY = "UNKNOWN"
CONFLICT_CONSTRAINT = "uq_fact_inspection_checkpoint"
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}
NEVER_INSERT_COLUMNS = {"inspection_checkpoint_sk", "created_at"}
BATCH_SIZE = 10_000

SOURCE_REQUIRED_COLUMNS = ("inspection_business_key",)

CHECKPOINT_SOURCE_COLUMNS = {
    "tour_plaques": "TOUR DU VEHICULE [Plaques de police]",
    "tour_vitres": "TOUR DU VEHICULE [Vitres et pare brise]",
    "tour_essuie_glace": "TOUR DU VEHICULE [Balais essuie-glace]",
    "tour_eclairage_av": "TOUR DU VEHICULE [Eclairage avant]",
    "tour_eclairage_ar": "TOUR DU VEHICULE [Eclairage arri\u00e8re]",
    "tour_retro_droit": "TOUR DU VEHICULE [R\u00e9troviseur Droit]",
    "tour_retro_gauche": "TOUR DU VEHICULE [R\u00e9troviseur Gauche]",
    "tour_pneus_av": "TOUR DU VEHICULE [Pneus avant]",
    "tour_pneus_ar": "TOUR DU VEHICULE [Pneus arri\u00e8re]",
    "int_essuie_av": (
        "DANS LE VEHICULE [Contr\u00f4le \u00e9tat et fonctionnement des "
        "balais d'essuie-vitres AV]"
    ),
    "int_essuie_ar": (
        "DANS LE VEHICULE [Contr\u00f4le \u00e9tat et fonctionnement des "
        "balais d'essuie-vitres AR]"
    ),
    "int_leve_vitre_av": (
        "DANS LE VEHICULE [Contr\u00f4le \u00e9tat et fonctionnement du "
        "l\u00e8ve-vitre AV]"
    ),
    "int_leve_vitre_ar": (
        "DANS LE VEHICULE [Contr\u00f4le \u00e9tat et fonctionnement du "
        "l\u00e8ve-vitre AR]"
    ),
    "int_feux_av": (
        "DANS LE VEHICULE [Contr\u00f4le fonctionnement des feux, "
        "\u00e9clairages AV]"
    ),
    "int_feux_ar": (
        "DANS LE VEHICULE [Contr\u00f4le fonctionnement des feux, "
        "\u00e9clairages AR]"
    ),
    "int_signal_av": (
        "DANS LE VEHICULE [Contr\u00f4le fonctionnement des feux de "
        "signalisation AV]"
    ),
    "int_signal_ar": (
        "DANS LE VEHICULE [Contr\u00f4le fonctionnement des feux de "
        "signalisation AR]"
    ),
    "int_klaxon": "DANS LE VEHICULE [Contr\u00f4le avertisseur sonore]",
    "capot_batterie": (
        "SOUS LE CAPOT [Contr\u00f4le batterie (\u00e9tat, fixation et charge)]"
    ),
    "capot_huile": "SOUS LE CAPOT [Contr\u00f4le du niveau huile moteur]",
    "capot_refroid": (
        "SOUS LE CAPOT [Contr\u00f4le du niveau du liquide de refroidissement]"
    ),
    "capot_liq_frein": (
        "SOUS LE CAPOT [Contr\u00f4le du niveau du liquide de frein]"
    ),
    "capot_durits": "SOUS LE CAPOT [Contr\u00f4le durits de radiateur]",
    "capot_courroies": (
        "SOUS LE CAPOT [Contr\u00f4le \u00e9tat des courroies d'accessoires]"
    ),
    "sous_plaq_av": (
        "SOUS LE V\u00c9HICULE [Contr\u00f4le des plaquettes de freins AV]"
    ),
    "sous_disques_av": "SOUS LE V\u00c9HICULE [Contr\u00f4le disques AV]",
    "sous_etriens": "SOUS LE V\u00c9HICULE [Contr\u00f4le \u00e9triers]",
    "sous_plaq_ar": (
        "SOUS LE V\u00c9HICULE [Contr\u00f4le des plaquettes de freins  AR "
        "(selon \u00e9quipement)]"
    ),
    "sous_disques_ar": (
        "SOUS LE V\u00c9HICULE [Contr\u00f4le  disques AR  (selon "
        "\u00e9quipement)]"
    ),
    "sous_amort_av": (
        "SOUS LE V\u00c9HICULE [Contr\u00f4le \u00e9tancheit\u00e9 des "
        "amortisseurs AV]"
    ),
    "sous_amort_ar": (
        "SOUS LE V\u00c9HICULE [Contr\u00f4le \u00e9tancheit\u00e9 des "
        "amortisseurs AR]"
    ),
    "sous_gaine": (
        "SOUS LE V\u00c9HICULE [Contr\u00f4le gaine (transmissions, rotules, "
        "cr\u00e9maill\u00e8re de direction)]"
    ),
    "sous_pneus_complet": (
        "SOUS LE V\u00c9HICULE [Contr\u00f4le \u00e9tat approfondi et mise "
        "\u00e0 pression des pneumatiques AV et AR]"
    ),
    "sous_roue_secours": (
        "SOUS LE V\u00c9HICULE [Contr\u00f4le \u00e9tat approfondi et mise "
        "\u00e0 pression de la roue de secours]"
    ),
    "sous_etancheite": (
        "SOUS LE V\u00c9HICULE [Contr\u00f4le \u00e9tanch\u00e9it\u00e9 tous "
        "fluides]"
    ),
    "sous_caisse": (
        "SOUS LE V\u00c9HICULE [Contr\u00f4le \u00e9tat sous caisse "
        "(corrosion, casses, d\u00e9formation, pi\u00e8ces absentes)]"
    ),
    "sous_echappement": (
        "SOUS LE V\u00c9HICULE [Contr\u00f4le ligne d'\u00e9chappement et "
        "fixations]"
    ),
    "ap_entretien": "AUTRES PRESTATIONS [Op\u00e9ration d'entretien]",
    "ap_filtre_air": "AUTRES PRESTATIONS [Contr\u00f4le filtre \u00e0 air]",
    "ap_filtre_habitacle": (
        "AUTRES PRESTATIONS [Contr\u00f4le filtre d'habitacle]"
    ),
    "ap_bougies": "AUTRES PRESTATIONS [Contr\u00f4le bougies d'allumage]",
    "ap_courroie_distrib": "AUTRES PRESTATIONS [Courroie de disribution]",
    "ap_clim": "AUTRES PRESTATIONS [Fonctionnement climatisation]",
}

STATUS_MAP = {
    "bon": ("OK", "Bon", Decimal("1.0")),
    "contr\u00f4le ok": ("OK", "Contr\u00f4le OK", Decimal("1.0")),
    "d\u00e9fectueux": ("CASSE", "D\u00e9fectueux", Decimal("0.0")),
    "contr\u00f4le non ok": ("CASSE", "Contr\u00f4le non OK", Decimal("0.0")),
    "proposition faite": ("USE", "Proposition faite", Decimal("0.5")),
    "intervention conseill\u00e9e": (
        "USE",
        "Intervention conseill\u00e9e",
        Decimal("0.5"),
    ),
    "r\u00e9paration effectu\u00e9e": (
        "USE",
        "R\u00e9paration effectu\u00e9e",
        Decimal("0.5"),
    ),
    "r\u00e9paration effectu\u00e9e suite \u00e0 l'accord client": (
        "USE",
        "R\u00e9paration effectu\u00e9e suite \u00e0 l'accord client",
        Decimal("0.5"),
    ),
    "oui": ("FAIT", "OUI", Decimal("1.0")),
    "non": ("NON_FAIT", "NON", Decimal("0.0")),
}

FACT_COLUMN_SOURCES = {
    "inspection_sk": "inspection_sk",
    "checkpoint_sk": "checkpoint_sk",
    "statut_code": "statut_code",
    "statut_libelle": "statut_libelle",
    "enc_valeur": "enc_valeur",
    "source_column_name": "source_column_name",
    "source_system": "source_system",
    "etl_run_id": "etl_run_id",
}


@dataclass(frozen=True)
class ExtractionStats:
    generated_checkpoint_rows: int
    skipped_empty_status_count: int
    unknown_status_count: int


@dataclass(frozen=True)
class ResolutionStats:
    missing_inspection_count: int
    missing_checkpoint_count: int
    distinct_inspection_count: int
    distinct_checkpoint_count: int


@dataclass(frozen=True)
class LoadStats:
    input_inspection_count: int
    generated_checkpoint_rows: int
    loaded_count: int
    target_count: int
    skipped_empty_status_count: int
    missing_inspection_count: int
    missing_checkpoint_count: int
    unknown_status_count: int
    distinct_inspection_count: int
    distinct_checkpoint_count: int


def main() -> None:
    args = _parse_args()
    stats = load_fact_inspection_checkpoint(args.etl_run_id)
    print(f"input_inspection_count={stats.input_inspection_count}")
    print(f"generated_checkpoint_rows={stats.generated_checkpoint_rows}")
    print(f"loaded_count={stats.loaded_count}")
    print(f"target_count={stats.target_count}")
    print(f"skipped_empty_status_count={stats.skipped_empty_status_count}")
    print(f"missing_inspection_count={stats.missing_inspection_count}")
    print(f"missing_checkpoint_count={stats.missing_checkpoint_count}")
    print(f"unknown_status_count={stats.unknown_status_count}")
    print(f"distinct_inspection_count={stats.distinct_inspection_count}")
    print(f"distinct_checkpoint_count={stats.distinct_checkpoint_count}")


def load_fact_inspection_checkpoint(etl_run_id: str) -> LoadStats:
    _validate_etl_run_id(etl_run_id)

    input_file = SILVER_DIR / etl_run_id / "fiche_voiture_stafim.parquet"
    if not input_file.exists():
        raise FileNotFoundError(f"Silver inspection file not found: {input_file}")

    dataframe = pd.read_parquet(input_file)
    input_inspection_count = len(dataframe)
    _assert_input_contract(dataframe)
    _assert_checkpoint_mapping(dataframe)

    checkpoint_rows, extraction_stats = _extract_checkpoint_rows(dataframe, etl_run_id)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_columns = _get_table_columns(cur, TARGET_TABLE)
            _assert_fact_checkpoint_contract(cur, table_columns)
            _assert_dependencies(cur)

            resolved_rows, resolution_stats = _resolve_keys(
                cur,
                checkpoint_rows,
                etl_run_id,
            )
            insert_columns = _insert_columns(table_columns, resolved_rows)
            load_rows = _build_load_rows(resolved_rows, insert_columns)
            _assert_no_duplicate_grain(load_rows)
            loaded_count = _upsert_fact_inspection_checkpoint_rows(
                cur,
                load_rows,
                insert_columns,
            )
            target_count = _count_target_rows(cur)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return LoadStats(
        input_inspection_count=input_inspection_count,
        generated_checkpoint_rows=extraction_stats.generated_checkpoint_rows,
        loaded_count=loaded_count,
        target_count=target_count,
        skipped_empty_status_count=extraction_stats.skipped_empty_status_count,
        missing_inspection_count=resolution_stats.missing_inspection_count,
        missing_checkpoint_count=resolution_stats.missing_checkpoint_count,
        unknown_status_count=extraction_stats.unknown_status_count,
        distinct_inspection_count=resolution_stats.distinct_inspection_count,
        distinct_checkpoint_count=resolution_stats.distinct_checkpoint_count,
    )


def _assert_input_contract(dataframe: pd.DataFrame) -> None:
    missing_columns = [
        column for column in SOURCE_REQUIRED_COLUMNS if column not in dataframe.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"Silver inspection file is missing columns: {missing}")


def _assert_checkpoint_mapping(dataframe: pd.DataFrame) -> None:
    config_codes = _load_config_checkpoint_codes()
    mapping_codes = set(CHECKPOINT_SOURCE_COLUMNS)
    missing_from_mapping = sorted(config_codes - mapping_codes)
    extra_in_mapping = sorted(mapping_codes - config_codes)
    if missing_from_mapping or extra_in_mapping:
        raise RuntimeError(
            "Checkpoint mapping and checkpoints.yaml are not aligned: "
            f"missing_from_mapping={missing_from_mapping}, "
            f"extra_in_mapping={extra_in_mapping}"
        )

    missing_source_columns = [
        source_column
        for source_column in CHECKPOINT_SOURCE_COLUMNS.values()
        if source_column not in dataframe.columns
    ]
    if missing_source_columns:
        missing = "\n".join(missing_source_columns)
        raise RuntimeError(
            "Silver inspection file is missing checkpoint source columns:\n"
            f"{missing}"
        )


def _load_config_checkpoint_codes() -> set[str]:
    if not CHECKPOINT_CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Checkpoint YAML file not found: {CHECKPOINT_CONFIG_FILE}"
        )

    with CHECKPOINT_CONFIG_FILE.open("r", encoding="utf-8") as stream:
        payload = yaml.safe_load(stream)

    if not isinstance(payload, list):
        raise RuntimeError(
            f"{CHECKPOINT_CONFIG_FILE} must contain a YAML list of checkpoints"
        )

    codes: set[str] = set()
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict) or "checkpoint_code" not in item:
            raise RuntimeError(
                f"Checkpoint config entry #{index} must include checkpoint_code"
            )
        code = _clean_optional_text(item["checkpoint_code"])
        if code is None:
            raise RuntimeError(f"Checkpoint config entry #{index} has empty code")
        codes.add(code)

    return codes


def _extract_checkpoint_rows(
    dataframe: pd.DataFrame,
    etl_run_id: str,
) -> tuple[pd.DataFrame, ExtractionStats]:
    rows: list[dict[str, Any]] = []
    skipped_empty_status_count = 0
    unknown_status_count = 0

    for _, source_row in dataframe.iterrows():
        inspection_business_key = _clean_key_value(
            source_row.get("inspection_business_key")
        )

        for checkpoint_code, source_column in CHECKPOINT_SOURCE_COLUMNS.items():
            raw_status = source_row.get(source_column)
            cleaned_status = _clean_optional_text(raw_status)
            if cleaned_status is None:
                skipped_empty_status_count += 1
                continue

            statut_code, statut_libelle, enc_valeur = _normalize_status(cleaned_status)
            if statut_code == "UNKNOWN_STATUS":
                unknown_status_count += 1

            rows.append(
                {
                    "inspection_business_key": inspection_business_key,
                    "checkpoint_code": checkpoint_code,
                    "source_column_name": source_column,
                    "raw_status_value": cleaned_status,
                    "statut_code": statut_code,
                    "statut_libelle": statut_libelle,
                    "enc_valeur": enc_valeur,
                    "source_system": SOURCE_SYSTEM_VALUE,
                    "etl_run_id": etl_run_id,
                }
            )

    checkpoint_rows = pd.DataFrame(rows)
    return checkpoint_rows, ExtractionStats(
        generated_checkpoint_rows=len(checkpoint_rows),
        skipped_empty_status_count=skipped_empty_status_count,
        unknown_status_count=unknown_status_count,
    )


def _normalize_status(value: str) -> tuple[str, str, Decimal | None]:
    key = _status_lookup_key(value)
    mapped_status = STATUS_MAP.get(key)
    if mapped_status is not None:
        return mapped_status

    return "UNKNOWN_STATUS", value, None


def _status_lookup_key(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip())
    normalized = normalized.replace("\u2019", "'")
    return normalized.casefold()


def _resolve_keys(
    cur: Any,
    dataframe: pd.DataFrame,
    etl_run_id: str,
) -> tuple[pd.DataFrame, ResolutionStats]:
    if dataframe.empty:
        empty_frame = dataframe.copy()
        empty_frame["inspection_sk"] = pd.Series(dtype="int64")
        empty_frame["checkpoint_sk"] = pd.Series(dtype="int64")
        return empty_frame, ResolutionStats(
            missing_inspection_count=0,
            missing_checkpoint_count=0,
            distinct_inspection_count=0,
            distinct_checkpoint_count=0,
        )

    inspection_lookup = _load_inspection_lookup(
        cur,
        dataframe["inspection_business_key"],
        etl_run_id,
    )
    checkpoint_lookup = _load_checkpoint_lookup(cur, dataframe["checkpoint_code"])

    resolved_rows: list[dict[str, Any]] = []
    missing_inspection_count = 0
    missing_checkpoint_count = 0

    for row in dataframe.to_dict(orient="records"):
        inspection_key = row["inspection_business_key"]
        inspection_sk = (
            inspection_lookup.get(str(inspection_key))
            if inspection_key is not None and not pd.isna(inspection_key)
            else None
        )
        if inspection_sk is None:
            missing_inspection_count += 1
            continue

        checkpoint_code = row["checkpoint_code"]
        checkpoint_sk = checkpoint_lookup.get(str(checkpoint_code))
        if checkpoint_sk is None:
            missing_checkpoint_count += 1
            continue

        resolved = dict(row)
        resolved["inspection_sk"] = inspection_sk
        resolved["checkpoint_sk"] = checkpoint_sk
        resolved_rows.append(resolved)

    resolved_frame = pd.DataFrame(resolved_rows)
    distinct_inspection_count = (
        int(resolved_frame["inspection_sk"].nunique()) if not resolved_frame.empty else 0
    )
    distinct_checkpoint_count = (
        int(resolved_frame["checkpoint_sk"].nunique()) if not resolved_frame.empty else 0
    )

    return resolved_frame, ResolutionStats(
        missing_inspection_count=missing_inspection_count,
        missing_checkpoint_count=missing_checkpoint_count,
        distinct_inspection_count=distinct_inspection_count,
        distinct_checkpoint_count=distinct_checkpoint_count,
    )


def _load_inspection_lookup(
    cur: Any,
    inspection_keys: pd.Series,
    etl_run_id: str,
) -> dict[str, int]:
    keys = sorted({str(key) for key in inspection_keys if pd.notna(key)})
    values_by_key: dict[str, int] = {}
    if not keys:
        return values_by_key

    query = """
        SELECT inspection_natural_key, inspection_sk
        FROM iris_dw.fact_inspection
        WHERE source_system = %s
          AND etl_run_id = %s
          AND inspection_natural_key = ANY(%s)
    """
    for key_batch in _chunks(keys, BATCH_SIZE):
        cur.execute(query, (SOURCE_SYSTEM_VALUE, etl_run_id, key_batch))
        values_by_key.update({str(key): int(sk) for key, sk in cur.fetchall()})

    return values_by_key


def _load_checkpoint_lookup(
    cur: Any,
    checkpoint_codes: pd.Series,
) -> dict[str, int]:
    codes = sorted({str(code) for code in checkpoint_codes if pd.notna(code)})
    values_by_code: dict[str, int] = {}
    if not codes:
        return values_by_code

    query = """
        SELECT checkpoint_sk, checkpoint_natural_key, checkpoint_code
        FROM iris_dw.dim_checkpoint
        WHERE checkpoint_natural_key <> %s
          AND (
              checkpoint_natural_key = ANY(%s)
              OR checkpoint_code = ANY(%s)
          )
    """
    for code_batch in _chunks(codes, BATCH_SIZE):
        cur.execute(query, (UNKNOWN_CHECKPOINT_KEY, code_batch, code_batch))
        for checkpoint_sk, natural_key, checkpoint_code in cur.fetchall():
            if natural_key in codes:
                values_by_code[str(natural_key)] = int(checkpoint_sk)
            if checkpoint_code in codes:
                values_by_code[str(checkpoint_code)] = int(checkpoint_sk)

    return values_by_code


def _get_table_columns(cur: Any, table_name: str) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %(schema)s
          AND table_name = %(table)s
        """,
        {
            "schema": TARGET_SCHEMA,
            "table": table_name,
        },
    )
    columns = {row[0] for row in cur.fetchall()}
    if not columns:
        raise RuntimeError(f"{TARGET_SCHEMA}.{table_name} does not exist")
    return columns


def _assert_fact_checkpoint_contract(cur: Any, table_columns: set[str]) -> None:
    missing_columns = sorted({"inspection_sk", "checkpoint_sk"} - table_columns)
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"{TARGET_SCHEMA}.{TARGET_TABLE} is missing columns: {missing}")
    _assert_conflict_constraint(cur)


def _assert_conflict_constraint(cur: Any) -> None:
    cur.execute(
        """
        SELECT 1
        FROM pg_constraint c
        JOIN pg_namespace n
          ON n.oid = c.connamespace
        JOIN pg_class t
          ON t.oid = c.conrelid
        WHERE n.nspname = %(schema)s
          AND t.relname = %(table)s
          AND c.conname = %(constraint_name)s
          AND c.contype IN ('p', 'u')
        LIMIT 1
        """,
        {
            "schema": TARGET_SCHEMA,
            "table": TARGET_TABLE,
            "constraint_name": CONFLICT_CONSTRAINT,
        },
    )
    if cur.fetchone() is None:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} is missing {CONFLICT_CONSTRAINT}"
        )


def _assert_dependencies(cur: Any) -> None:
    cur.execute("SELECT COUNT(*) FROM iris_dw.fact_inspection")
    if int(cur.fetchone()[0]) == 0:
        raise RuntimeError("iris_dw.fact_inspection is empty")

    cur.execute(
        """
        SELECT COUNT(*)
        FROM iris_dw.dim_checkpoint
        WHERE checkpoint_natural_key <> %s
        """,
        (UNKNOWN_CHECKPOINT_KEY,),
    )
    if int(cur.fetchone()[0]) == 0:
        raise RuntimeError("iris_dw.dim_checkpoint contains only UNKNOWN")


def _insert_columns(table_columns: set[str], dataframe: pd.DataFrame) -> list[str]:
    columns = [
        column
        for column, source_column in FACT_COLUMN_SOURCES.items()
        if (
            column in table_columns
            and column not in NEVER_INSERT_COLUMNS
            and source_column in dataframe.columns
        )
    ]
    missing_required = sorted({"inspection_sk", "checkpoint_sk", "source_system"} - set(columns))
    if missing_required:
        missing = ", ".join(missing_required)
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} has no insertable required columns: "
            f"{missing}"
        )
    return columns


def _build_load_rows(
    dataframe: pd.DataFrame,
    insert_columns: list[str],
) -> list[dict[str, Any]]:
    load_frame = pd.DataFrame(index=dataframe.index)

    for target_column in insert_columns:
        source_column = FACT_COLUMN_SOURCES[target_column]
        load_frame[target_column] = dataframe[source_column]

    load_frame = load_frame.astype(object).where(pd.notna(load_frame), None)
    return [
        {key: _to_python_value(value) for key, value in row.items()}
        for row in load_frame.to_dict(orient="records")
    ]


def _assert_no_duplicate_grain(rows: list[dict[str, Any]]) -> None:
    seen_pairs: set[tuple[int, int]] = set()
    duplicate_count = 0
    for row in rows:
        pair = (int(row["inspection_sk"]), int(row["checkpoint_sk"]))
        if pair in seen_pairs:
            duplicate_count += 1
        else:
            seen_pairs.add(pair)

    if duplicate_count:
        raise RuntimeError(
            f"Prepared fact_inspection_checkpoint rows contain {duplicate_count} "
            "duplicate inspection_sk + checkpoint_sk pairs"
        )


def _upsert_fact_inspection_checkpoint_rows(
    cur: Any,
    rows: list[dict[str, Any]],
    insert_columns: list[str],
) -> int:
    if not rows:
        return 0

    requested_update_columns = {
        "statut_code",
        "statut_libelle",
        "enc_valeur",
        "source_column_name",
        "source_system",
        "etl_run_id",
    }
    update_columns = [
        column for column in insert_columns if column in requested_update_columns
    ]
    if not update_columns:
        raise RuntimeError(
            "No fact_inspection_checkpoint columns available to update on rerun"
        )

    assignments = [
        sql.SQL("{} = EXCLUDED.{}").format(
            sql.Identifier(column),
            sql.Identifier(column),
        )
        for column in update_columns
    ]

    query = sql.SQL(
        """
        INSERT INTO {}.{} ({})
        VALUES ({})
        ON CONFLICT ON CONSTRAINT {}
        DO UPDATE SET {}
        """
    ).format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
        sql.SQL(", ").join(sql.Identifier(column) for column in insert_columns),
        sql.SQL(", ").join(sql.Placeholder(column) for column in insert_columns),
        sql.Identifier(CONFLICT_CONSTRAINT),
        sql.SQL(", ").join(assignments),
    )

    loaded_count = 0
    for batch in _chunks(rows, BATCH_SIZE):
        cur.executemany(query, batch)
        loaded_count += cur.rowcount if cur.rowcount >= 0 else len(batch)

    return loaded_count


def _count_target_rows(cur: Any) -> int:
    query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
    )
    cur.execute(query)
    return int(cur.fetchone()[0])


def _clean_key_value(value: Any) -> str | None:
    return _clean_optional_text(value)


def _clean_optional_text(value: Any) -> str | None:
    if pd.isna(value):
        return None

    cleaned = re.sub(r"\s+", " ", str(value).strip())
    if cleaned.casefold() in NULL_MARKERS:
        return None

    return cleaned


def _to_python_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except (AttributeError, ValueError):
            return value
    return value


def _chunks(values: list[Any], size: int) -> Iterator[list[Any]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


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
        description=(
            "Load Silver inspection checkpoint rows into "
            "iris_dw.fact_inspection_checkpoint."
        )
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help=(
            "ETL run id containing "
            "data/silver/<etl_run_id>/fiche_voiture_stafim.parquet."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
