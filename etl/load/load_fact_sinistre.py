from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator

import pandas as pd
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


SILVER_DIR = PROJECT_ROOT / "data" / "silver"
TARGET_SCHEMA = "iris_dw"
TARGET_TABLE = "fact_sinistre"
SOURCE_SYSTEM_VALUE = "Sinistres.xlsx"
SOURCE_KEY_COLUMNS = ("NUMSNT", "GRNTSINI")
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}
NEVER_INSERT_COLUMNS = {"sinistre_sk", "created_at"}
BATCH_SIZE = 10_000
LATE_DECLARATION_DAYS = 5
EARLY_CLAIM_DAYS = 30

SOURCE_REQUIRED_COLUMNS = (
    "NUMSNT",
    "GRNTSINI",
    "NUMCNT",
    "NUMAVT",
    "NUMMAJ",
    "NATCLT",
    "IDCLT",
    "CODFAM",
    "CODPROD",
    "NATINT",
    "IDINT",
    "IDDELEGA",
    "CAUSESINI",
    "NATSINI",
    "SOUNATSIN",
    "DTSURV",
    "DTDECSNT",
    "DTOUVSNT",
    "DTCLTSNT",
    "DEBEFFET",
    "FINEFFET",
)

DATE_LOOKUPS = {
    "DTSURV": "date_survenance_sk",
    "DTDECSNT": "date_declaration_sk",
    "DTOUVSNT": "date_ouverture_sk",
    "DTCLTSNT": "date_cloture_sk",
    "DEBEFFET": "date_debut_effet_sk",
    "FINEFFET": "date_fin_effet_sk",
}

MEASURE_SOURCES = {
    "montant_evaluation_initiale": "EVAL_INIT",
    "montant_provision": "MNTPROVIS",
    "montant_paye_garantie": "MNTPAIGRN",
    "montant_declare": "MNTDECLAR",
    "montant_prevision": "MNTPREVIS",
    "montant_recours": "MNTRECOUR",
    "montant_total": "MNTTOTAL",
    "montant_total_net": "MNTTOTNET",
}

OPTIONAL_ATTRIBUTE_SOURCES = {
    "code_etat_sinistre": "CODE_ETAT",
    "etat_garantie": "ETATGRNT",
    "motif_cloture": "MOTIFCLOT",
}

FACT_COLUMN_SOURCES = {
    "sinistre_natural_key": "sinistre_natural_key",
    "num_sinistre": "NUMSNT",
    "client_sk": "client_sk",
    "contrat_sk": "contrat_sk",
    "vehicule_sk": "vehicule_sk",
    "produit_sk": "produit_sk",
    "garantie_sk": "garantie_sk",
    "intermediaire_sk": "intermediaire_sk",
    "delegation_sk": "delegation_sk",
    "cause_sinistre_sk": "cause_sinistre_sk",
    "date_survenance_sk": "date_survenance_sk",
    "date_declaration_sk": "date_declaration_sk",
    "date_ouverture_sk": "date_ouverture_sk",
    "date_cloture_sk": "date_cloture_sk",
    "date_debut_effet_sk": "date_debut_effet_sk",
    "date_fin_effet_sk": "date_fin_effet_sk",
    "numero_risque": "NUMRISQ",
    "code_etat_sinistre": "CODE_ETAT",
    "etat_garantie": "ETATGRNT",
    "motif_cloture": "MOTIFCLOT",
    "montant_evaluation_initiale": "EVAL_INIT",
    "montant_provision": "MNTPROVIS",
    "montant_paye_garantie": "MNTPAIGRN",
    "montant_declare": "MNTDECLAR",
    "montant_prevision": "MNTPREVIS",
    "montant_recours": "MNTRECOUR",
    "montant_total": "MNTTOTAL",
    "montant_total_net": "MNTTOTNET",
    "delai_declaration_jours": "delai_declaration_jours",
    "delai_ouverture_jours": "delai_ouverture_jours",
    "anciennete_contrat_jours": "anciennete_contrat_jours",
    "is_declaration_antidatee": "is_declaration_antidatee",
    "is_declaration_tardive": "is_declaration_tardive",
    "is_sinistre_avant_contrat": "is_sinistre_avant_contrat",
    "is_sinistre_precoce": "is_sinistre_precoce",
    "source_system": "source_system",
    "etl_run_id": "etl_run_id",
}


@dataclass(frozen=True)
class LookupDefinition:
    label: str
    table_name: str
    key_column: str
    sk_column: str
    source_key_column: str
    output_sk_column: str


@dataclass(frozen=True)
class ContratPairCandidate:
    contrat_sk: int
    num_mise_a_jour: str | None


LOOKUPS = (
    LookupDefinition(
        label="client",
        table_name="dim_client",
        key_column="client_natural_key",
        sk_column="client_sk",
        source_key_column="client_natural_key",
        output_sk_column="client_sk",
    ),
    LookupDefinition(
        label="vehicule",
        table_name="dim_vehicule",
        key_column="vehicule_natural_key",
        sk_column="vehicule_sk",
        source_key_column="vehicule_natural_key",
        output_sk_column="vehicule_sk",
    ),
    LookupDefinition(
        label="produit",
        table_name="dim_produit",
        key_column="produit_natural_key",
        sk_column="produit_sk",
        source_key_column="produit_natural_key",
        output_sk_column="produit_sk",
    ),
    LookupDefinition(
        label="garantie",
        table_name="dim_garantie",
        key_column="garantie_natural_key",
        sk_column="garantie_sk",
        source_key_column="garantie_natural_key",
        output_sk_column="garantie_sk",
    ),
    LookupDefinition(
        label="intermediaire",
        table_name="dim_intermediaire",
        key_column="intermediaire_natural_key",
        sk_column="intermediaire_sk",
        source_key_column="intermediaire_natural_key",
        output_sk_column="intermediaire_sk",
    ),
    LookupDefinition(
        label="delegation",
        table_name="dim_delegation",
        key_column="delegation_natural_key",
        sk_column="delegation_sk",
        source_key_column="delegation_natural_key",
        output_sk_column="delegation_sk",
    ),
    LookupDefinition(
        label="cause_sinistre",
        table_name="dim_cause_sinistre",
        key_column="cause_sinistre_natural_key",
        sk_column="cause_sinistre_sk",
        source_key_column="cause_sinistre_natural_key",
        output_sk_column="cause_sinistre_sk",
    ),
)


@dataclass(frozen=True)
class ContratLookupStats:
    unknown_contrat_count: int
    contrat_exact_match_count: int
    contrat_pair_unique_fallback_count: int
    contrat_pair_max_nummaj_fallback_count: int
    contrat_no_match_count: int


@dataclass(frozen=True)
class LookupStats:
    unknown_client_count: int
    unknown_contrat_count: int
    unknown_vehicule_count: int
    unknown_produit_count: int
    unknown_garantie_count: int
    unknown_intermediaire_count: int
    unknown_delegation_count: int
    unknown_cause_sinistre_count: int
    unknown_date_survenance_count: int
    unknown_date_declaration_count: int
    unknown_date_ouverture_count: int
    unknown_date_cloture_count: int
    unknown_date_debut_effet_count: int
    unknown_date_fin_effet_count: int
    contrat_exact_match_count: int
    contrat_pair_unique_fallback_count: int
    contrat_pair_max_nummaj_fallback_count: int
    contrat_no_match_count: int


@dataclass(frozen=True)
class IndicatorStats:
    declaration_antidatee_count: int
    declaration_tardive_count: int
    sinistre_avant_contrat_count: int
    sinistre_precoce_count: int


@dataclass(frozen=True)
class LoadStats:
    input_count: int
    loaded_count: int
    target_count: int
    unknown_client_count: int
    unknown_contrat_count: int
    contrat_exact_match_count: int
    contrat_pair_unique_fallback_count: int
    contrat_pair_max_nummaj_fallback_count: int
    contrat_no_match_count: int
    unknown_vehicule_count: int
    unknown_produit_count: int
    unknown_garantie_count: int
    unknown_intermediaire_count: int
    unknown_delegation_count: int
    unknown_cause_sinistre_count: int
    unknown_date_survenance_count: int
    unknown_date_declaration_count: int
    unknown_date_ouverture_count: int
    unknown_date_cloture_count: int
    unknown_date_debut_effet_count: int
    unknown_date_fin_effet_count: int
    declaration_antidatee_count: int
    declaration_tardive_count: int
    sinistre_avant_contrat_count: int
    sinistre_precoce_count: int


def main() -> None:
    args = _parse_args()
    stats = load_fact_sinistre(args.etl_run_id)
    print(f"input_count={stats.input_count}")
    print(f"loaded_count={stats.loaded_count}")
    print(f"target_count={stats.target_count}")
    print(f"unknown_client_count={stats.unknown_client_count}")
    print(f"unknown_contrat_count={stats.unknown_contrat_count}")
    print(f"contrat_exact_match_count={stats.contrat_exact_match_count}")
    print(
        "contrat_pair_unique_fallback_count="
        f"{stats.contrat_pair_unique_fallback_count}"
    )
    print(
        "contrat_pair_max_nummaj_fallback_count="
        f"{stats.contrat_pair_max_nummaj_fallback_count}"
    )
    print(f"contrat_no_match_count={stats.contrat_no_match_count}")
    print(f"unknown_vehicule_count={stats.unknown_vehicule_count}")
    print(f"unknown_produit_count={stats.unknown_produit_count}")
    print(f"unknown_garantie_count={stats.unknown_garantie_count}")
    print(f"unknown_intermediaire_count={stats.unknown_intermediaire_count}")
    print(f"unknown_delegation_count={stats.unknown_delegation_count}")
    print(f"unknown_cause_sinistre_count={stats.unknown_cause_sinistre_count}")
    print(f"unknown_date_survenance_count={stats.unknown_date_survenance_count}")
    print(f"unknown_date_declaration_count={stats.unknown_date_declaration_count}")
    print(f"unknown_date_ouverture_count={stats.unknown_date_ouverture_count}")
    print(f"unknown_date_cloture_count={stats.unknown_date_cloture_count}")
    print(f"unknown_date_debut_effet_count={stats.unknown_date_debut_effet_count}")
    print(f"unknown_date_fin_effet_count={stats.unknown_date_fin_effet_count}")
    print(f"declaration_antidatee_count={stats.declaration_antidatee_count}")
    print(f"declaration_tardive_count={stats.declaration_tardive_count}")
    print(f"sinistre_avant_contrat_count={stats.sinistre_avant_contrat_count}")
    print(f"sinistre_precoce_count={stats.sinistre_precoce_count}")


def load_fact_sinistre(etl_run_id: str) -> LoadStats:
    _validate_etl_run_id(etl_run_id)

    input_file = SILVER_DIR / etl_run_id / "sinistres.parquet"
    if not input_file.exists():
        raise FileNotFoundError(f"Silver sinistres file not found: {input_file}")

    dataframe = pd.read_parquet(input_file)
    input_count = len(dataframe)
    _assert_input_contract(dataframe)
    sinistre_rows = _build_sinistre_rows(dataframe, etl_run_id)
    indicator_stats = _add_chronological_indicators(sinistre_rows)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_columns = _get_table_columns(cur, TARGET_TABLE)
            _assert_fact_sinistre_contract(cur, table_columns)
            _assert_lookup_tables(cur)

            lookup_stats = _apply_lookup_sks(cur, sinistre_rows)
            insert_columns = _insert_columns(table_columns, sinistre_rows)
            load_rows = _build_load_rows(sinistre_rows, insert_columns)
            loaded_count = _upsert_fact_sinistre_rows(
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
        input_count=input_count,
        loaded_count=loaded_count,
        target_count=target_count,
        unknown_client_count=lookup_stats.unknown_client_count,
        unknown_contrat_count=lookup_stats.unknown_contrat_count,
        contrat_exact_match_count=lookup_stats.contrat_exact_match_count,
        contrat_pair_unique_fallback_count=(
            lookup_stats.contrat_pair_unique_fallback_count
        ),
        contrat_pair_max_nummaj_fallback_count=(
            lookup_stats.contrat_pair_max_nummaj_fallback_count
        ),
        contrat_no_match_count=lookup_stats.contrat_no_match_count,
        unknown_vehicule_count=lookup_stats.unknown_vehicule_count,
        unknown_produit_count=lookup_stats.unknown_produit_count,
        unknown_garantie_count=lookup_stats.unknown_garantie_count,
        unknown_intermediaire_count=lookup_stats.unknown_intermediaire_count,
        unknown_delegation_count=lookup_stats.unknown_delegation_count,
        unknown_cause_sinistre_count=lookup_stats.unknown_cause_sinistre_count,
        unknown_date_survenance_count=lookup_stats.unknown_date_survenance_count,
        unknown_date_declaration_count=lookup_stats.unknown_date_declaration_count,
        unknown_date_ouverture_count=lookup_stats.unknown_date_ouverture_count,
        unknown_date_cloture_count=lookup_stats.unknown_date_cloture_count,
        unknown_date_debut_effet_count=lookup_stats.unknown_date_debut_effet_count,
        unknown_date_fin_effet_count=lookup_stats.unknown_date_fin_effet_count,
        declaration_antidatee_count=indicator_stats.declaration_antidatee_count,
        declaration_tardive_count=indicator_stats.declaration_tardive_count,
        sinistre_avant_contrat_count=indicator_stats.sinistre_avant_contrat_count,
        sinistre_precoce_count=indicator_stats.sinistre_precoce_count,
    )


def _assert_input_contract(dataframe: pd.DataFrame) -> None:
    missing_columns = [
        column for column in SOURCE_REQUIRED_COLUMNS if column not in dataframe.columns
    ]
    missing_measures = [
        source_column
        for source_column in MEASURE_SOURCES.values()
        if source_column not in dataframe.columns
    ]
    if missing_columns or missing_measures:
        missing = ", ".join(missing_columns + missing_measures)
        raise RuntimeError(f"Silver sinistres file is missing columns: {missing}")


def _build_sinistre_rows(dataframe: pd.DataFrame, etl_run_id: str) -> pd.DataFrame:
    sinistres = dataframe.copy()

    for column in _key_columns_to_clean(sinistres):
        sinistres[column] = sinistres[column].map(_clean_key_value)

    derived_key = _combine_key_parts(sinistres, SOURCE_KEY_COLUMNS)
    if "sinistre_business_key" in sinistres.columns:
        preferred_key = sinistres["sinistre_business_key"].map(_clean_key_value)
        sinistres["sinistre_natural_key"] = preferred_key.where(
            preferred_key.notna(),
            derived_key,
        )
    else:
        sinistres["sinistre_natural_key"] = derived_key

    null_key_count = int(sinistres["sinistre_natural_key"].isna().sum())
    if null_key_count:
        raise RuntimeError(
            f"Silver sinistres file contains {null_key_count} null "
            "sinistre_natural_key values"
        )

    duplicate_key_count = int(
        sinistres["sinistre_natural_key"].duplicated(keep=False).sum()
    )
    if duplicate_key_count:
        raise RuntimeError(
            f"Silver sinistres file contains {duplicate_key_count} rows with "
            "duplicate sinistre_natural_key values"
        )

    sinistres["client_natural_key"] = _combine_key_parts(sinistres, ("NATCLT", "IDCLT"))
    sinistres["contrat_natural_key"] = _combine_key_parts(
        sinistres,
        ("NUMCNT", "NUMAVT", "NUMMAJ"),
    )
    sinistres["contrat_pair_key"] = _combine_key_parts(sinistres, ("NUMCNT", "NUMAVT"))
    sinistres["vehicule_natural_key"] = _source_key_or_null(
        sinistres,
        "vehicule_business_key",
    )
    sinistres["produit_natural_key"] = _combine_key_parts(sinistres, ("CODFAM", "CODPROD"))
    sinistres["garantie_natural_key"] = _source_key_or_null(sinistres, "GRNTSINI")
    sinistres["intermediaire_natural_key"] = _combine_key_parts(
        sinistres,
        ("NATINT", "IDINT"),
    )
    sinistres["delegation_natural_key"] = _source_key_or_null(sinistres, "IDDELEGA")
    sinistres["cause_sinistre_natural_key"] = _combine_key_parts(
        sinistres,
        ("CAUSESINI", "NATSINI", "SOUNATSIN"),
    )
    sinistres["source_system"] = SOURCE_SYSTEM_VALUE
    sinistres["etl_run_id"] = etl_run_id

    for source_column in DATE_LOOKUPS:
        sinistres[source_column] = sinistres[source_column].map(_to_date)

    for source_column in OPTIONAL_ATTRIBUTE_SOURCES.values():
        if source_column in sinistres.columns:
            sinistres[source_column] = sinistres[source_column].map(_clean_optional_text)

    if "NUMRISQ" in sinistres.columns:
        sinistres["NUMRISQ"] = sinistres["NUMRISQ"].map(_clean_optional_text)

    return sinistres.reset_index(drop=True)


def _key_columns_to_clean(dataframe: pd.DataFrame) -> list[str]:
    candidates = [
        "NUMSNT",
        "GRNTSINI",
        "NUMCNT",
        "NUMAVT",
        "NUMMAJ",
        "NATCLT",
        "IDCLT",
        "CODFAM",
        "CODPROD",
        "NATINT",
        "IDINT",
        "IDDELEGA",
        "CAUSESINI",
        "NATSINI",
        "SOUNATSIN",
        "vehicule_business_key",
        "sinistre_business_key",
    ]
    return [column for column in candidates if column in dataframe.columns]


def _source_key_or_null(dataframe: pd.DataFrame, column: str) -> pd.Series:
    if column not in dataframe.columns:
        return pd.Series(pd.NA, index=dataframe.index, dtype="string")
    return dataframe[column].map(_clean_key_value)


def _add_chronological_indicators(dataframe: pd.DataFrame) -> IndicatorStats:
    delai_declaration: list[int | None] = []
    delai_ouverture: list[int | None] = []
    anciennete_contrat: list[int | None] = []
    is_declaration_antidatee: list[bool] = []
    is_declaration_tardive: list[bool] = []
    is_sinistre_avant_contrat: list[bool] = []
    is_sinistre_precoce: list[bool] = []

    for row in dataframe.itertuples(index=False):
        dates = row._asdict()
        date_survenance = dates.get("DTSURV")
        date_declaration = dates.get("DTDECSNT")
        date_ouverture = dates.get("DTOUVSNT")
        date_debut_effet = dates.get("DEBEFFET")

        declaration_days = _days_between(date_survenance, date_declaration)
        ouverture_days = _days_between(date_declaration, date_ouverture)
        contrat_days = _days_between(date_debut_effet, date_survenance)

        delai_declaration.append(declaration_days)
        delai_ouverture.append(ouverture_days)
        anciennete_contrat.append(contrat_days)

        declaration_antidatee = (
            date_survenance is not None
            and date_declaration is not None
            and date_declaration < date_survenance
        )
        sinistre_avant_contrat = (
            date_survenance is not None
            and date_debut_effet is not None
            and date_survenance < date_debut_effet
        )
        declaration_tardive = (
            declaration_days is not None
            and declaration_days > LATE_DECLARATION_DAYS
        )
        sinistre_precoce = (
            contrat_days is not None
            and 0 <= contrat_days <= EARLY_CLAIM_DAYS
        )

        is_declaration_antidatee.append(declaration_antidatee)
        is_declaration_tardive.append(declaration_tardive)
        is_sinistre_avant_contrat.append(sinistre_avant_contrat)
        is_sinistre_precoce.append(sinistre_precoce)

    dataframe["delai_declaration_jours"] = delai_declaration
    dataframe["delai_ouverture_jours"] = delai_ouverture
    dataframe["anciennete_contrat_jours"] = anciennete_contrat
    dataframe["is_declaration_antidatee"] = is_declaration_antidatee
    dataframe["is_declaration_tardive"] = is_declaration_tardive
    dataframe["is_sinistre_avant_contrat"] = is_sinistre_avant_contrat
    dataframe["is_sinistre_precoce"] = is_sinistre_precoce

    return IndicatorStats(
        declaration_antidatee_count=sum(is_declaration_antidatee),
        declaration_tardive_count=sum(is_declaration_tardive),
        sinistre_avant_contrat_count=sum(is_sinistre_avant_contrat),
        sinistre_precoce_count=sum(is_sinistre_precoce),
    )


def _days_between(start_date: date | None, end_date: date | None) -> int | None:
    if start_date is None or end_date is None:
        return None
    return (end_date - start_date).days


def _apply_lookup_sks(cur: Any, dataframe: pd.DataFrame) -> LookupStats:
    unknown_counts: dict[str, int] = {}
    contrat_stats = _apply_contrat_lookup(cur, dataframe)

    for lookup in LOOKUPS:
        values_by_key = _load_lookup_values(
            cur,
            table_name=lookup.table_name,
            key_column=lookup.key_column,
            sk_column=lookup.sk_column,
            source_keys=dataframe[lookup.source_key_column],
        )
        sk_values, unknown_count = _resolve_sks(
            dataframe[lookup.source_key_column],
            values_by_key,
        )
        dataframe[lookup.output_sk_column] = sk_values
        unknown_counts[lookup.label] = unknown_count

    date_lookup = _load_date_lookup(cur, dataframe)
    date_unknown_counts: dict[str, int] = {}
    for source_column, output_column in DATE_LOOKUPS.items():
        sk_values, unknown_count = _resolve_date_sks(
            dataframe[source_column],
            date_lookup,
        )
        dataframe[output_column] = sk_values
        date_unknown_counts[output_column] = unknown_count

    return LookupStats(
        unknown_client_count=unknown_counts["client"],
        unknown_contrat_count=contrat_stats.unknown_contrat_count,
        unknown_vehicule_count=unknown_counts["vehicule"],
        unknown_produit_count=unknown_counts["produit"],
        unknown_garantie_count=unknown_counts["garantie"],
        unknown_intermediaire_count=unknown_counts["intermediaire"],
        unknown_delegation_count=unknown_counts["delegation"],
        unknown_cause_sinistre_count=unknown_counts["cause_sinistre"],
        unknown_date_survenance_count=date_unknown_counts["date_survenance_sk"],
        unknown_date_declaration_count=date_unknown_counts["date_declaration_sk"],
        unknown_date_ouverture_count=date_unknown_counts["date_ouverture_sk"],
        unknown_date_cloture_count=date_unknown_counts["date_cloture_sk"],
        unknown_date_debut_effet_count=date_unknown_counts["date_debut_effet_sk"],
        unknown_date_fin_effet_count=date_unknown_counts["date_fin_effet_sk"],
        contrat_exact_match_count=contrat_stats.contrat_exact_match_count,
        contrat_pair_unique_fallback_count=(
            contrat_stats.contrat_pair_unique_fallback_count
        ),
        contrat_pair_max_nummaj_fallback_count=(
            contrat_stats.contrat_pair_max_nummaj_fallback_count
        ),
        contrat_no_match_count=contrat_stats.contrat_no_match_count,
    )


def _apply_contrat_lookup(cur: Any, dataframe: pd.DataFrame) -> ContratLookupStats:
    exact_values, pair_candidates = _load_contrat_lookup_values(
        cur,
        dataframe["contrat_natural_key"],
        dataframe["contrat_pair_key"],
    )

    contrat_sks: list[int] = []
    exact_match_count = 0
    pair_unique_fallback_count = 0
    pair_max_nummaj_fallback_count = 0
    no_match_count = 0

    for row in dataframe[["contrat_natural_key", "contrat_pair_key"]].itertuples(
        index=False,
    ):
        exact_key = row.contrat_natural_key
        pair_key = row.contrat_pair_key

        # First preserve the strict DW contract grain when Sinistres NUMMAJ agrees
        # with dim_contrat.contrat_natural_key.
        if pd.notna(exact_key):
            exact_sk = exact_values.get(str(exact_key))
            if exact_sk is not None:
                contrat_sks.append(exact_sk)
                exact_match_count += 1
                continue

        # NUMMAJ from Sinistres is not reliable for many rows, so exact misses
        # fall back to the stable NUMCNT + NUMAVT pair.
        candidates = pair_candidates.get(str(pair_key), []) if pd.notna(pair_key) else []
        if len(candidates) == 1:
            contrat_sks.append(candidates[0].contrat_sk)
            pair_unique_fallback_count += 1
            continue

        if len(candidates) > 1:
            # Rare duplicate pair candidates are resolved deterministically by the
            # maximum numeric num_mise_a_jour; non-numeric values sort below numeric.
            selected_candidate = _select_max_nummaj_candidate(candidates)
            contrat_sks.append(selected_candidate.contrat_sk)
            pair_max_nummaj_fallback_count += 1
            continue

        contrat_sks.append(0)
        no_match_count += 1

    dataframe["contrat_sk"] = contrat_sks

    return ContratLookupStats(
        unknown_contrat_count=no_match_count,
        contrat_exact_match_count=exact_match_count,
        contrat_pair_unique_fallback_count=pair_unique_fallback_count,
        contrat_pair_max_nummaj_fallback_count=pair_max_nummaj_fallback_count,
        contrat_no_match_count=no_match_count,
    )


def _resolve_sks(
    source_keys: pd.Series,
    values_by_key: dict[str, int],
) -> tuple[list[int], int]:
    sk_values: list[int] = []
    unknown_count = 0

    for raw_key in source_keys:
        if pd.isna(raw_key):
            sk_values.append(0)
            unknown_count += 1
            continue

        sk = values_by_key.get(str(raw_key))
        if sk is None:
            sk_values.append(0)
            unknown_count += 1
        else:
            sk_values.append(sk)

    return sk_values, unknown_count


def _resolve_date_sks(
    source_dates: pd.Series,
    values_by_date: dict[date, int],
) -> tuple[list[int], int]:
    sk_values: list[int] = []
    unknown_count = 0

    for source_date in source_dates:
        if source_date is None or pd.isna(source_date):
            sk_values.append(0)
            unknown_count += 1
            continue

        sk = values_by_date.get(source_date)
        if sk is None:
            sk_values.append(0)
            unknown_count += 1
        else:
            sk_values.append(sk)

    return sk_values, unknown_count


def _load_lookup_values(
    cur: Any,
    *,
    table_name: str,
    key_column: str,
    sk_column: str,
    source_keys: pd.Series,
) -> dict[str, int]:
    keys = sorted({str(key) for key in source_keys if pd.notna(key)})
    values_by_key: dict[str, int] = {}
    if not keys:
        return values_by_key

    query = sql.SQL(
        """
        SELECT {}, {}
        FROM {}.{}
        WHERE {} = ANY(%s)
        """
    ).format(
        sql.Identifier(key_column),
        sql.Identifier(sk_column),
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(table_name),
        sql.Identifier(key_column),
    )

    for key_batch in _chunks(keys, BATCH_SIZE):
        cur.execute(query, (key_batch,))
        values_by_key.update({str(key): int(sk) for key, sk in cur.fetchall()})

    return values_by_key


def _load_contrat_lookup_values(
    cur: Any,
    source_exact_keys: pd.Series,
    source_pair_keys: pd.Series,
) -> tuple[dict[str, int], dict[str, list[ContratPairCandidate]]]:
    exact_keys = {str(key) for key in source_exact_keys if pd.notna(key)}
    pair_keys = {str(key) for key in source_pair_keys if pd.notna(key)}
    values_by_exact_key: dict[str, int] = {}
    candidates_by_pair: dict[str, list[ContratPairCandidate]] = {}
    if not exact_keys and not pair_keys:
        return values_by_exact_key, candidates_by_pair

    query = sql.SQL(
        """
        SELECT
            contrat_sk,
            contrat_natural_key,
            num_contrat,
            num_avenant,
            num_mise_a_jour
        FROM {}.{}
        """
    ).format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier("dim_contrat"),
    )

    cur.execute(query)
    while rows := cur.fetchmany(BATCH_SIZE):
        for (
            contrat_sk,
            contrat_natural_key,
            num_contrat,
            num_avenant,
            num_mise_a_jour,
        ) in rows:
            lookup_key = _clean_optional_text(contrat_natural_key)
            if lookup_key is not None and lookup_key in exact_keys:
                values_by_exact_key[lookup_key] = int(contrat_sk)

            pair_key = _join_clean_key_values((num_contrat, num_avenant))
            if pair_key is None or pair_key not in pair_keys:
                continue

            candidates_by_pair.setdefault(pair_key, []).append(
                ContratPairCandidate(
                    contrat_sk=int(contrat_sk),
                    num_mise_a_jour=_clean_key_value(num_mise_a_jour),
                )
            )

    return values_by_exact_key, candidates_by_pair


def _select_max_nummaj_candidate(
    candidates: list[ContratPairCandidate],
) -> ContratPairCandidate:
    return max(candidates, key=_contrat_candidate_sort_key)


def _contrat_candidate_sort_key(
    candidate: ContratPairCandidate,
) -> tuple[int, float, int]:
    numeric_nummaj = _numeric_nummaj(candidate.num_mise_a_jour)
    if numeric_nummaj is None:
        return (0, float("-inf"), candidate.contrat_sk)
    return (1, numeric_nummaj, candidate.contrat_sk)


def _numeric_nummaj(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _load_date_lookup(cur: Any, dataframe: pd.DataFrame) -> dict[date, int]:
    source_dates: set[date] = set()
    for source_column in DATE_LOOKUPS:
        source_dates.update(
            value
            for value in dataframe[source_column]
            if value is not None and not pd.isna(value)
        )

    values_by_date: dict[date, int] = {}
    if not source_dates:
        return values_by_date

    query = """
        SELECT date_val, date_sk
        FROM iris_dw.dim_date
        WHERE date_val = ANY(%s)
    """
    for date_batch in _chunks(sorted(source_dates), BATCH_SIZE):
        cur.execute(query, (date_batch,))
        values_by_date.update(
            {date_val: int(date_sk) for date_val, date_sk in cur.fetchall()}
        )

    return values_by_date


def _assert_lookup_tables(cur: Any) -> None:
    contrat_columns = _get_table_columns(cur, "dim_contrat")
    missing_contrat_columns = sorted(
        {
            "contrat_sk",
            "contrat_natural_key",
            "num_contrat",
            "num_avenant",
            "num_mise_a_jour",
        }
        - contrat_columns
    )
    if missing_contrat_columns:
        missing = ", ".join(missing_contrat_columns)
        raise RuntimeError(f"{TARGET_SCHEMA}.dim_contrat is missing columns: {missing}")

    for lookup in LOOKUPS:
        columns = _get_table_columns(cur, lookup.table_name)
        missing_columns = [
            column
            for column in (lookup.key_column, lookup.sk_column)
            if column not in columns
        ]
        if missing_columns:
            missing = ", ".join(missing_columns)
            raise RuntimeError(
                f"{TARGET_SCHEMA}.{lookup.table_name} is missing lookup columns: "
                f"{missing}"
            )

    date_columns = _get_table_columns(cur, "dim_date")
    missing_date_columns = sorted({"date_val", "date_sk"} - date_columns)
    if missing_date_columns:
        missing = ", ".join(missing_date_columns)
        raise RuntimeError(f"{TARGET_SCHEMA}.dim_date is missing columns: {missing}")


def _assert_fact_sinistre_contract(cur: Any, table_columns: set[str]) -> None:
    if "sinistre_natural_key" not in table_columns:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} is missing sinistre_natural_key"
        )
    _assert_key_conflict_target(cur, "sinistre_natural_key")


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
    if "sinistre_natural_key" not in columns:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} has no insertable sinistre_natural_key"
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


def _upsert_fact_sinistre_rows(
    cur: Any,
    rows: list[dict[str, Any]],
    insert_columns: list[str],
) -> int:
    if not rows:
        return 0

    update_columns = [
        column for column in insert_columns if column != "sinistre_natural_key"
    ]
    if not update_columns:
        raise RuntimeError("No fact_sinistre columns available to update on rerun")

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
        ON CONFLICT ({}) DO UPDATE
        SET {}
        """
    ).format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
        sql.SQL(", ").join(sql.Identifier(column) for column in insert_columns),
        sql.SQL(", ").join(sql.Placeholder(column) for column in insert_columns),
        sql.Identifier("sinistre_natural_key"),
        sql.SQL(", ").join(assignments),
    )

    loaded_count = 0
    for batch in _chunks(rows, BATCH_SIZE):
        cur.executemany(query, batch)
        loaded_count += cur.rowcount if cur.rowcount >= 0 else len(batch)

    return loaded_count


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


def _assert_key_conflict_target(cur: Any, key_column: str) -> None:
    cur.execute(
        """
        SELECT 1
        FROM pg_constraint c
        JOIN pg_namespace n
          ON n.oid = c.connamespace
        JOIN pg_class t
          ON t.oid = c.conrelid
        JOIN pg_attribute a
          ON a.attrelid = t.oid
         AND a.attnum = c.conkey[1]
        WHERE n.nspname = %(schema)s
          AND t.relname = %(table)s
          AND c.contype IN ('p', 'u')
          AND array_length(c.conkey, 1) = 1
          AND a.attname = %(key_column)s
        LIMIT 1
        """,
        {
            "schema": TARGET_SCHEMA,
            "table": TARGET_TABLE,
            "key_column": key_column,
        },
    )
    if cur.fetchone() is None:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} must have a primary or unique "
            f"constraint on {key_column} for idempotent loading"
        )


def _count_target_rows(cur: Any) -> int:
    query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
    )
    cur.execute(query)
    return int(cur.fetchone()[0])


def _combine_key_parts(dataframe: pd.DataFrame, columns: tuple[str, ...]) -> pd.Series:
    null_key_mask = dataframe[list(columns)].isna().any(axis=1)
    combined = dataframe[columns[0]].astype("string")
    for column in columns[1:]:
        combined = combined + "|" + dataframe[column].astype("string")
    return combined.mask(null_key_mask, pd.NA)


def _join_clean_key_values(values: tuple[Any, ...]) -> str | None:
    cleaned_values = [_clean_key_value(value) for value in values]
    if any(value is None for value in cleaned_values):
        return None
    return "|".join(str(value) for value in cleaned_values)


def _clean_key_value(value: Any) -> str | None:
    if pd.isna(value):
        return None

    cleaned = str(value).strip()
    if cleaned.casefold() in NULL_MARKERS:
        return None

    if cleaned.endswith(".0"):
        prefix = cleaned[:-2]
        if prefix and prefix.lstrip("+-").isdigit():
            cleaned = prefix

    return cleaned


def _clean_optional_text(value: Any) -> str | None:
    if pd.isna(value):
        return None

    cleaned = str(value).strip()
    if cleaned.casefold() in NULL_MARKERS:
        return None

    return cleaned


def _to_date(value: Any) -> date | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text_value = str(value).strip()
    if text_value.casefold() in NULL_MARKERS:
        return None

    if text_value.endswith(".0") and text_value[:-2].isdigit():
        text_value = text_value[:-2]

    formats = ("%Y-%m-%d", "%Y%m%d", "%d/%m/%Y")
    for date_format in formats:
        try:
            return datetime.strptime(text_value, date_format).date()
        except ValueError:
            continue

    parsed = pd.to_datetime(text_value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


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
        description="Load Silver sinistres rows into iris_dw.fact_sinistre."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id containing data/silver/<etl_run_id>/sinistres.parquet.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
