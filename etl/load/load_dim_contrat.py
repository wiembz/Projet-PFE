from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection
from etl.common.normalization import (
    normalize_code,
    normalize_formula_code,
    normalize_product_natural_key,
)


SILVER_DIR = PROJECT_ROOT / "data" / "silver"
TARGET_SCHEMA = "iris_dw"
TARGET_TABLE = "dim_contrat"
SOURCE_NATURAL_KEY = "contrat_natural_key"
SOURCE_SYSTEM_VALUE = "Production.xlsx"
TARGET_KEY_CANDIDATES = (
    "contrat_natural_key",
    "contrat_business_key",
)
NEVER_INSERT_COLUMNS = {"contrat_sk", "created_at", "updated_at"}
NULL_MARKERS = {"", "nan", "none", "<na>"}
CONTRAT_KEY_COLUMNS = ("NUMCNT", "NUMAVT", "NUMMAJ")
SOURCE_REQUIRED_COLUMNS = (
    "NUMCNT",
    "NUMAVT",
    "NUMMAJ",
    "CODFAM",
    "CODPROD",
    "IDDELEGA",
    "NATINT",
    "IDINT",
)

SOURCE_TO_TARGET_CANDIDATES = {
    SOURCE_NATURAL_KEY: TARGET_KEY_CANDIDATES,
    "NUMCNT": ("numero_contrat", "num_contrat", "numcnt"),
    "NUMAVT": ("numero_avenant", "num_avenant", "numavt"),
    "NUMMAJ": ("numero_maj", "num_mise_a_jour", "nummaj"),
    "produit_sk": ("produit_sk",),
    "delegation_sk": ("delegation_sk",),
    "intermediaire_sk": ("intermediaire_sk",),
    "NATCLT": ("nature_client",),
    "IDCLT": ("id_client_source",),
    "CODFAM": ("code_famille_produit",),
    "CODPROD": ("code_produit",),
    "DUREE": ("duree", "duree_contrat"),
    "DEBCNT": ("date_debut_contrat", "debcnt"),
    "FINCNT": ("date_fin_contrat", "fincnt"),
    "DEBEFFET": ("date_debut_effet", "debeffet"),
    "FINEFFET": ("date_fin_effet", "fineffet"),
    "COASSUR": ("coassurance",),
    "SITUAT": ("situation_contrat",),
    "DATEPREC": ("date_precedente", "date_precision", "dateprec"),
    "TYPERESIL": ("type_resiliation",),
    "LIB_RESIL": ("libelle_resiliation",),
    "source_system": ("source_system",),
}


@dataclass(frozen=True)
class LookupDefinition:
    label: str
    table_name: str
    lookup_key_column: str
    lookup_sk_column: str
    source_key_column: str
    output_sk_column: str


LOOKUPS = (
    LookupDefinition(
        label="produit",
        table_name="dim_produit",
        lookup_key_column="produit_natural_key",
        lookup_sk_column="produit_sk",
        source_key_column="produit_natural_key",
        output_sk_column="produit_sk",
    ),
    LookupDefinition(
        label="delegation",
        table_name="dim_delegation",
        lookup_key_column="delegation_natural_key",
        lookup_sk_column="delegation_sk",
        source_key_column="delegation_natural_key",
        output_sk_column="delegation_sk",
    ),
    LookupDefinition(
        label="intermediaire",
        table_name="dim_intermediaire",
        lookup_key_column="intermediaire_natural_key",
        lookup_sk_column="intermediaire_sk",
        source_key_column="intermediaire_natural_key",
        output_sk_column="intermediaire_sk",
    ),
)


@dataclass(frozen=True)
class LookupStats:
    unknown_produit_count: int
    unknown_delegation_count: int
    unknown_intermediaire_count: int
    product_exact_formula_match_count: int
    product_unknown_formula_match_count: int
    product_controlled_product_fallback_count: int
    product_no_match_count: int


@dataclass(frozen=True)
class LoadStats:
    input_count: int
    loaded_count: int
    target_count: int
    unknown_produit_count: int
    unknown_delegation_count: int
    unknown_intermediaire_count: int
    product_exact_formula_match_count: int
    product_unknown_formula_match_count: int
    product_controlled_product_fallback_count: int
    product_no_match_count: int


def main() -> None:
    args = _parse_args()
    stats = load_dim_contrat(args.etl_run_id)
    print(f"input_count={stats.input_count}")
    print(f"loaded_count={stats.loaded_count}")
    print(f"target_count={stats.target_count}")
    print(f"unknown_produit_count={stats.unknown_produit_count}")
    print(f"product_exact_formula_match_count={stats.product_exact_formula_match_count}")
    print(f"product_unknown_formula_match_count={stats.product_unknown_formula_match_count}")
    print(
        "product_controlled_product_fallback_count="
        f"{stats.product_controlled_product_fallback_count}"
    )
    print(f"product_no_match_count={stats.product_no_match_count}")
    print(f"unknown_delegation_count={stats.unknown_delegation_count}")
    print(f"unknown_intermediaire_count={stats.unknown_intermediaire_count}")


def load_dim_contrat(etl_run_id: str) -> LoadStats:
    _validate_etl_run_id(etl_run_id)
    input_file = SILVER_DIR / etl_run_id / "production.parquet"
    if not input_file.exists():
        raise FileNotFoundError(f"Silver production file not found: {input_file}")

    dataframe = pd.read_parquet(input_file)
    input_count = len(dataframe)
    _assert_input_contract(dataframe)
    contrat_rows = _build_contrat_rows(dataframe)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_columns = _get_table_columns(cur, TARGET_TABLE)
            key_column = _resolve_target_key_column(table_columns)
            _assert_key_conflict_target(cur, key_column)
            _assert_lookup_tables(cur)

            lookup_stats = _apply_lookup_sks(cur, contrat_rows)
            column_mapping = _build_column_mapping(table_columns)
            rows = _build_load_rows(contrat_rows, column_mapping)
            loaded_count = _upsert_dim_contrat_rows(
                cur,
                rows,
                key_column,
                table_columns,
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
        unknown_produit_count=lookup_stats.unknown_produit_count,
        unknown_delegation_count=lookup_stats.unknown_delegation_count,
        unknown_intermediaire_count=lookup_stats.unknown_intermediaire_count,
        product_exact_formula_match_count=(
            lookup_stats.product_exact_formula_match_count
        ),
        product_unknown_formula_match_count=(
            lookup_stats.product_unknown_formula_match_count
        ),
        product_controlled_product_fallback_count=(
            lookup_stats.product_controlled_product_fallback_count
        ),
        product_no_match_count=lookup_stats.product_no_match_count,
    )


def _assert_input_contract(dataframe: pd.DataFrame) -> None:
    missing_columns = [
        column for column in SOURCE_REQUIRED_COLUMNS if column not in dataframe.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"Silver production file is missing columns: {missing}")


def _build_contrat_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    contracts = dataframe.copy()

    for column in _text_columns_to_clean(contracts):
        zero_is_null = column == "IDDELEGA"
        contracts[column] = _clean_text_series(
            contracts[column],
            zero_is_null=zero_is_null,
        )

    null_key_mask = contracts[list(CONTRAT_KEY_COLUMNS)].isna().any(axis=1)
    null_key_count = int(null_key_mask.sum())
    if null_key_count:
        raise RuntimeError(
            f"Silver production file contains {null_key_count} null "
            "contrat_natural_key values"
        )

    contracts[SOURCE_NATURAL_KEY] = _combine_key_parts(contracts, CONTRAT_KEY_COLUMNS)
    duplicate_mask = contracts[SOURCE_NATURAL_KEY].duplicated(keep=False)
    duplicate_count = int(duplicate_mask.sum())
    if duplicate_count:
        raise RuntimeError(
            f"Silver production file contains {duplicate_count} rows with duplicate "
            "contrat_natural_key values"
        )

    _add_product_lookup_columns(contracts)
    contracts["delegation_natural_key"] = contracts["IDDELEGA"]
    contracts["intermediaire_natural_key"] = _combine_key_parts(
        contracts,
        ("NATINT", "IDINT"),
    )
    contracts["source_system"] = _source_system_series(contracts)

    return contracts.reset_index(drop=True)


def _text_columns_to_clean(dataframe: pd.DataFrame) -> list[str]:
    candidates = [
        "NUMCNT",
        "NUMAVT",
        "NUMMAJ",
        "CODFAM",
        "CODPROD",
        "CODFORMU",
        "NATCLT",
        "IDCLT",
        "NATINT",
        "IDINT",
        "IDDELEGA",
        "COASSUR",
        "SITUAT",
        "TYPERESIL",
        "LIB_RESIL",
        "source_file",
    ]
    return [column for column in candidates if column in dataframe.columns]


def _clean_text_series(series: pd.Series, *, zero_is_null: bool = False) -> pd.Series:
    cleaned = series.astype("string").str.strip()
    null_markers = set(NULL_MARKERS)
    if zero_is_null:
        null_markers.add("0")
    return cleaned.mask(cleaned.str.lower().isin(null_markers), pd.NA)


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


def _combine_key_parts(dataframe: pd.DataFrame, columns: tuple[str, ...]) -> pd.Series:
    null_key_mask = dataframe[list(columns)].isna().any(axis=1)
    combined = dataframe[columns[0]].astype("string")
    for column in columns[1:]:
        combined = combined + "|" + dataframe[column].astype("string")
    return combined.mask(null_key_mask, pd.NA)


def _add_product_lookup_columns(dataframe: pd.DataFrame) -> None:
    if "CODFORMU" not in dataframe.columns:
        dataframe["CODFORMU"] = pd.NA

    product_code = dataframe["CODPROD"].map(normalize_code)
    formula_code = dataframe["CODFORMU"].map(normalize_formula_code)
    formula_missing = formula_code.eq("UNKNOWN")

    dataframe["product_code_lookup"] = product_code
    dataframe["formula_code_lookup"] = formula_code
    dataframe["product_formula_missing"] = formula_missing
    dataframe["produit_natural_key"] = (
        product_code.astype("string") + "|" + formula_code.astype("string")
    ).mask(product_code.isna(), pd.NA)


def _source_system_series(dataframe: pd.DataFrame) -> pd.Series:
    return pd.Series(SOURCE_SYSTEM_VALUE, index=dataframe.index, dtype="string")


def _assert_lookup_tables(cur: Any) -> None:
    for lookup in LOOKUPS:
        columns = _get_table_columns(cur, lookup.table_name)
        missing_columns = [
            column
            for column in (lookup.lookup_key_column, lookup.lookup_sk_column)
            if column not in columns
        ]
        if missing_columns:
            missing = ", ".join(missing_columns)
            raise RuntimeError(
                f"{TARGET_SCHEMA}.{lookup.table_name} is missing lookup columns: "
                f"{missing}"
            )

    produit_columns = _get_table_columns(cur, "dim_produit")
    missing_produit_columns = sorted(
        {"produit_sk", "produit_natural_key", "code_produit"} - produit_columns
    )
    if missing_produit_columns:
        missing = ", ".join(missing_produit_columns)
        raise RuntimeError(f"{TARGET_SCHEMA}.dim_produit is missing columns: {missing}")


def _apply_lookup_sks(cur: Any, dataframe: pd.DataFrame) -> LookupStats:
    unknown_counts: dict[str, int] = {}
    product_stats = _apply_product_lookup(cur, dataframe)

    for lookup in LOOKUPS:
        if lookup.label == "produit":
            continue
        values_by_key = _load_lookup_values(
            cur,
            lookup,
            dataframe[lookup.source_key_column],
        )
        sk_values: list[int] = []
        unknown_count = 0

        for raw_key in dataframe[lookup.source_key_column]:
            if pd.isna(raw_key):
                sk_values.append(0)
                unknown_count += 1
                continue

            key = str(raw_key)
            sk = values_by_key.get(key)
            if sk is None:
                sk_values.append(0)
                unknown_count += 1
            else:
                sk_values.append(sk)

        dataframe[lookup.output_sk_column] = sk_values
        unknown_counts[lookup.label] = unknown_count

    return LookupStats(
        unknown_produit_count=product_stats["product_no_match_count"],
        unknown_delegation_count=unknown_counts["delegation"],
        unknown_intermediaire_count=unknown_counts["intermediaire"],
        product_exact_formula_match_count=product_stats[
            "product_exact_formula_match_count"
        ],
        product_unknown_formula_match_count=product_stats[
            "product_unknown_formula_match_count"
        ],
        product_controlled_product_fallback_count=product_stats[
            "product_controlled_product_fallback_count"
        ],
        product_no_match_count=product_stats["product_no_match_count"],
    )


def _apply_product_lookup(cur: Any, dataframe: pd.DataFrame) -> dict[str, int]:
    exact_values, candidates_by_product = _load_product_lookup_values(cur, dataframe)
    produit_sks: list[int] = []
    stats = {
        "product_exact_formula_match_count": 0,
        "product_unknown_formula_match_count": 0,
        "product_controlled_product_fallback_count": 0,
        "product_no_match_count": 0,
    }

    for row in dataframe[
        [
            "product_code_lookup",
            "produit_natural_key",
            "product_formula_missing",
        ]
    ].itertuples(index=False):
        product_code = row.product_code_lookup
        formula_key = row.produit_natural_key
        if pd.isna(product_code) or pd.isna(formula_key):
            produit_sks.append(0)
            stats["product_no_match_count"] += 1
            continue

        exact_sk = exact_values.get(str(formula_key))
        if exact_sk is not None:
            produit_sks.append(exact_sk)
            if bool(row.product_formula_missing):
                stats["product_unknown_formula_match_count"] += 1
            else:
                stats["product_exact_formula_match_count"] += 1
            continue

        candidates = candidates_by_product.get(str(product_code), [])
        if len(candidates) == 1:
            produit_sks.append(candidates[0])
            stats["product_controlled_product_fallback_count"] += 1
            continue

        produit_sks.append(0)
        stats["product_no_match_count"] += 1

    dataframe["produit_sk"] = produit_sks
    return stats


def _load_product_lookup_values(
    cur: Any,
    dataframe: pd.DataFrame,
) -> tuple[dict[str, int], dict[str, list[int]]]:
    keys = sorted(
        {str(key) for key in dataframe["produit_natural_key"] if pd.notna(key)}
    )
    product_codes = sorted(
        {str(key) for key in dataframe["product_code_lookup"] if pd.notna(key)}
    )
    exact_values: dict[str, int] = {}
    candidates_by_product: dict[str, list[int]] = {}
    if not keys and not product_codes:
        return exact_values, candidates_by_product

    query = sql.SQL(
        """
        SELECT produit_sk, produit_natural_key, code_produit
        FROM {}.{}
        WHERE produit_natural_key = ANY(%s)
           OR code_produit = ANY(%s)
        """
    ).format(sql.Identifier(TARGET_SCHEMA), sql.Identifier("dim_produit"))
    cur.execute(query, (keys, product_codes))
    for produit_sk, natural_key, code_produit in cur.fetchall():
        key = normalize_product_natural_key(natural_key)
        if key is not None and key in keys:
            exact_values[key] = int(produit_sk)

        product_code = normalize_code(code_produit)
        if product_code is not None and int(produit_sk) != 0:
            candidates_by_product.setdefault(product_code, []).append(int(produit_sk))

    return exact_values, candidates_by_product


def _load_lookup_values(
    cur: Any,
    lookup: LookupDefinition,
    source_keys: pd.Series,
) -> dict[str, int]:
    keys = sorted({str(key) for key in source_keys if pd.notna(key)})
    if not keys:
        return {}

    query = sql.SQL(
        """
        SELECT {}, {}
        FROM {}.{}
        WHERE {} = ANY(%s)
        """
    ).format(
        sql.Identifier(lookup.lookup_key_column),
        sql.Identifier(lookup.lookup_sk_column),
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(lookup.table_name),
        sql.Identifier(lookup.lookup_key_column),
    )
    cur.execute(query, (keys,))
    return {str(key): int(sk) for key, sk in cur.fetchall()}


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


def _resolve_target_key_column(table_columns: set[str]) -> str:
    for candidate in TARGET_KEY_CANDIDATES:
        if candidate in table_columns:
            return candidate
    candidates = ", ".join(TARGET_KEY_CANDIDATES)
    raise RuntimeError(
        f"{TARGET_SCHEMA}.{TARGET_TABLE} is missing required natural key "
        f"column; expected one of: {candidates}"
    )


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


def _build_column_mapping(table_columns: set[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    insertable_columns = table_columns - NEVER_INSERT_COLUMNS

    for source_column, target_candidates in SOURCE_TO_TARGET_CANDIDATES.items():
        for target_column in target_candidates:
            if target_column in insertable_columns:
                mapping[source_column] = target_column
                break

    if SOURCE_NATURAL_KEY not in mapping:
        raise RuntimeError(
            f"No insertable target natural key column found in "
            f"{TARGET_SCHEMA}.{TARGET_TABLE}"
        )

    return mapping


def _build_load_rows(
    dataframe: pd.DataFrame,
    column_mapping: dict[str, str],
) -> list[dict[str, Any]]:
    load_frame = pd.DataFrame(index=dataframe.index)

    for source_column, target_column in column_mapping.items():
        if source_column not in dataframe.columns:
            continue
        if source_column == "DUREE":
            load_frame[target_column] = dataframe[source_column].map(_to_nullable_text)
        else:
            load_frame[target_column] = dataframe[source_column]

    load_frame = load_frame.astype(object).where(pd.notna(load_frame), None)
    return load_frame.to_dict(orient="records")


def _to_nullable_text(value: Any) -> str | None:
    if pd.isna(value):
        return None
    text_value = str(value).strip()
    if text_value.lower() in NULL_MARKERS:
        return None
    return text_value


def _upsert_dim_contrat_rows(
    cur: Any,
    rows: list[dict[str, Any]],
    key_column: str,
    table_columns: set[str],
) -> int:
    if not rows:
        return 0

    columns = list(rows[0].keys())
    update_columns = [column for column in columns if column != key_column]

    assignments = [
        sql.SQL("{} = EXCLUDED.{}").format(
            sql.Identifier(column),
            sql.Identifier(column),
        )
        for column in update_columns
    ]
    if "updated_at" in table_columns:
        assignments.append(sql.SQL("updated_at = now()"))

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
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        sql.SQL(", ").join(sql.Placeholder(column) for column in columns),
        sql.Identifier(key_column),
        sql.SQL(", ").join(assignments),
    )

    cur.executemany(query, rows)
    return cur.rowcount if cur.rowcount >= 0 else len(rows)


def _count_target_rows(cur: Any) -> int:
    query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
        sql.Identifier(TARGET_SCHEMA),
        sql.Identifier(TARGET_TABLE),
    )
    cur.execute(query)
    return int(cur.fetchone()[0])


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
        description="Load Silver production contracts into iris_dw.dim_contrat."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id containing data/silver/<etl_run_id>/production.parquet.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
