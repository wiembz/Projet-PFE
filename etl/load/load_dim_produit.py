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
from etl.common.normalization import normalize_code, normalize_formula_code


SILVER_DIR = PROJECT_ROOT / "data" / "silver"
REFERENCE_FILE = PROJECT_ROOT / "data" / "reference" / "fichierStagiaire.xlsx"
TARGET_SCHEMA = "iris_dw"
TARGET_TABLE = "dim_produit"
SOURCE_NATURAL_KEY = "produit_natural_key"
UNKNOWN = "UNKNOWN"
SOURCE_SYSTEM_VALUE = "Production.xlsx/fichierStagiaire.xlsx"
SOURCE_REQUIRED_COLUMNS = ("CODPROD",)
NEVER_INSERT_COLUMNS = {"produit_sk", "created_at", "updated_at"}
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}

SOURCE_TO_TARGET_CANDIDATES = {
    SOURCE_NATURAL_KEY: ("produit_natural_key",),
    "CODPROD": ("code_produit",),
    "LIBPRDT": ("libelle_produit",),
    "CODFORMU": ("code_formule",),
    "LIBFORMU": ("libelle_formule",),
    "CODFAM": ("code_famille_produit",),
    "LIBFAMIL": ("libelle_famille_produit",),
    "source_system": ("source_system",),
}


@dataclass(frozen=True)
class LoadStats:
    input_count: int
    distinct_product_formula_count: int
    loaded_count: int
    target_count: int
    missing_libelle_produit_count: int
    missing_libelle_formule_count: int
    missing_libelle_famille_count: int


@dataclass(frozen=True)
class ProductRows:
    dataframe: pd.DataFrame
    libelle_conflict_count: int


def main() -> None:
    args = _parse_args()
    stats = load_dim_produit(args.etl_run_id)
    print(f"input_count={stats.input_count}")
    print(f"distinct_product_formula_count={stats.distinct_product_formula_count}")
    print(f"loaded_count={stats.loaded_count}")
    print(f"target_count={stats.target_count}")
    print(f"missing_libelle_produit_count={stats.missing_libelle_produit_count}")
    print(f"missing_libelle_formule_count={stats.missing_libelle_formule_count}")
    print(f"missing_libelle_famille_count={stats.missing_libelle_famille_count}")


def load_dim_produit(etl_run_id: str) -> LoadStats:
    _validate_etl_run_id(etl_run_id)
    input_file = SILVER_DIR / etl_run_id / "production.parquet"
    if not input_file.exists():
        raise FileNotFoundError(f"Silver production file not found: {input_file}")

    dataframe = pd.read_parquet(input_file)
    input_count = len(dataframe)
    _assert_input_contract(dataframe)

    references = _load_references()
    sinistres = _read_sinistres_product_rows(etl_run_id)
    product_rows = _build_distinct_product_formula_rows(
        dataframe,
        sinistres,
        references,
    )
    if product_rows.libelle_conflict_count:
        print(
            "WARNING libelle_produit_conflict_count="
            f"{product_rows.libelle_conflict_count}",
            flush=True,
        )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            table_columns = _get_table_columns(cur)
            _assert_dim_produit_contract(cur, table_columns)

            column_mapping = _build_column_mapping(table_columns)
            rows = _build_load_rows(product_rows.dataframe, column_mapping)
            loaded_count = _upsert_dim_produit_rows(cur, rows, table_columns)
            target_count = _count_target_rows(cur)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    frame = product_rows.dataframe
    return LoadStats(
        input_count=input_count,
        distinct_product_formula_count=len(frame),
        loaded_count=loaded_count,
        target_count=target_count,
        missing_libelle_produit_count=_missing_count(frame, "LIBPRDT"),
        missing_libelle_formule_count=_missing_count(frame, "LIBFORMU"),
        missing_libelle_famille_count=_missing_count(frame, "LIBFAMIL"),
    )


def _assert_input_contract(dataframe: pd.DataFrame) -> None:
    missing_columns = [
        column for column in SOURCE_REQUIRED_COLUMNS if column not in dataframe.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(f"Silver production file is missing columns: {missing}")


def _read_sinistres_product_rows(etl_run_id: str) -> pd.DataFrame:
    input_file = SILVER_DIR / etl_run_id / "sinistres.parquet"
    if not input_file.exists():
        print(f"WARNING Silver sinistres file not found: {input_file}", flush=True)
        return pd.DataFrame(columns=["CODFAM", "CODPROD", "CODFORMU"])

    dataframe = pd.read_parquet(input_file)
    required = {"CODPROD", "CODFORMU"}
    if not required.issubset(dataframe.columns):
        missing = ", ".join(sorted(required - set(dataframe.columns)))
        print(
            f"WARNING Silver sinistres file missing product formula columns: {missing}",
            flush=True,
        )
        return pd.DataFrame(columns=["CODFAM", "CODPROD", "CODFORMU"])

    columns = [column for column in ("CODFAM", "CODPROD", "CODFORMU") if column in dataframe.columns]
    return dataframe[columns].copy()


def _load_references() -> dict[str, Any]:
    references = {
        "formula_labels": {},
        "formula_rows": [],
        "family_labels": {},
    }
    if not REFERENCE_FILE.exists():
        print(f"WARNING reference_file_missing={REFERENCE_FILE}", flush=True)
        return references

    with pd.ExcelFile(REFERENCE_FILE, engine="openpyxl") as workbook:
        sheet_by_stripped_name = {
            sheet_name.strip(): sheet_name for sheet_name in workbook.sheet_names
        }
        if "CODPROD" in sheet_by_stripped_name:
            sheet_name = sheet_by_stripped_name["CODPROD"]
            codprod = pd.read_excel(workbook, sheet_name=sheet_name, dtype=object)
            codprod.columns = [str(column).strip() for column in codprod.columns]
            if {"CODPROD", "CODFORMU", "LIBFORMU"}.issubset(codprod.columns):
                for row in codprod.itertuples(index=False):
                    values = row._asdict()
                    code_produit = normalize_code(values["CODPROD"])
                    code_formule = normalize_formula_code(values["CODFORMU"])
                    libelle_formule = _clean_label_value(values["LIBFORMU"])
                    if code_produit and code_formule and libelle_formule:
                        key = f"{code_produit}|{code_formule}"
                        references["formula_labels"].setdefault(key, libelle_formule)
                        references["formula_rows"].append(
                            {
                                "CODPROD": code_produit,
                                "CODFORMU": code_formule,
                                "LIBFORMU": libelle_formule,
                                "CODFAM": normalize_code(values.get("CODFAM")),
                            }
                        )

        if "CODFAM" in sheet_by_stripped_name:
            codfam = pd.read_excel(
                workbook,
                sheet_name=sheet_by_stripped_name["CODFAM"],
                dtype=object,
            )
            codfam.columns = [str(column).strip() for column in codfam.columns]
            if {"CODFAM", "LIBFAMIL"}.issubset(codfam.columns):
                for row in codfam.itertuples(index=False):
                    values = row._asdict()
                    code_famille = normalize_code(values["CODFAM"])
                    libelle_famille = _clean_label_value(values["LIBFAMIL"])
                    if code_famille and libelle_famille:
                        references["family_labels"].setdefault(
                            code_famille,
                            libelle_famille,
                        )

    return references


def _build_distinct_product_formula_rows(
    dataframe: pd.DataFrame,
    sinistres: pd.DataFrame,
    references: dict[str, Any],
) -> ProductRows:
    products = dataframe.copy()
    for column in ("CODFAM", "CODPROD", "CODFORMU", "LIBPRDT"):
        if column in products.columns:
            if column == "LIBPRDT":
                cleaner = _clean_label_value
            elif column == "CODFORMU":
                cleaner = normalize_formula_code
            else:
                cleaner = normalize_code
            products[column] = products[column].map(cleaner)

    if "CODFAM" not in products.columns:
        products["CODFAM"] = pd.NA
    if "CODFORMU" not in products.columns:
        products["CODFORMU"] = pd.NA
    if "LIBPRDT" not in products.columns:
        products["LIBPRDT"] = pd.NA

    null_key_mask = products["CODPROD"].isna()
    null_key_count = int(null_key_mask.sum())
    if null_key_count:
        raise RuntimeError(
            f"Silver production file contains {null_key_count} null product keys"
        )

    duplicate_labels = _count_label_conflicts(products)
    product_labels = _select_most_frequent_values(products, "CODPROD", "LIBPRDT")
    product_families = _select_most_frequent_values(products, "CODPROD", "CODFAM")

    source_rows = _build_source_product_rows(
        products,
        references,
        product_labels,
    )
    reference_rows = _build_reference_formula_rows(
        references,
        product_labels,
        product_families,
    )
    sinistre_rows = _build_sinistre_product_formula_rows(
        sinistres,
        references,
        product_labels,
        product_families,
    )

    combined = pd.concat(
        [source_rows, reference_rows, sinistre_rows],
        ignore_index=True,
    )
    if combined.empty:
        selected = combined
    else:
        selected = (
            combined.sort_values(["row_priority", SOURCE_NATURAL_KEY], kind="mergesort")
            .drop_duplicates(subset=["CODPROD", "CODFORMU"], keep="first")
            .drop(columns=["row_priority"])
            .copy()
        )

    return ProductRows(
        dataframe=selected.reset_index(drop=True),
        libelle_conflict_count=duplicate_labels,
    )


def _build_source_product_rows(
    products: pd.DataFrame,
    references: dict[str, Any],
    product_labels: dict[str, str],
) -> pd.DataFrame:
    source = products[["CODFAM", "CODPROD", "CODFORMU", "LIBPRDT"]].copy()
    source["CODFORMU"] = source["CODFORMU"].fillna(UNKNOWN)
    source[SOURCE_NATURAL_KEY] = (
        source["CODPROD"].astype("string") + "|" + source["CODFORMU"].astype("string")
    )

    source = (
        source.sort_values([SOURCE_NATURAL_KEY], kind="mergesort")
        .drop_duplicates(subset=["CODPROD", "CODFORMU"], keep="first")
        .copy()
    )
    source["LIBPRDT"] = source["CODPROD"].map(product_labels)
    source["LIBFORMU"] = source[SOURCE_NATURAL_KEY].map(
        references["formula_labels"],
    )
    unknown_formula_mask = source["CODFORMU"].eq(UNKNOWN)
    source.loc[unknown_formula_mask, "LIBFORMU"] = "Formule inconnue"
    source["LIBFAMIL"] = source["CODFAM"].map(references["family_labels"])
    source["source_system"] = SOURCE_SYSTEM_VALUE
    source["row_priority"] = 0

    return source


def _build_reference_formula_rows(
    references: dict[str, Any],
    product_labels: dict[str, str],
    product_families: dict[str, str],
) -> pd.DataFrame:
    rows = references["formula_rows"]
    columns = [
        "CODFAM",
        "CODPROD",
        "CODFORMU",
        "LIBPRDT",
        "LIBFORMU",
        "LIBFAMIL",
        SOURCE_NATURAL_KEY,
        "source_system",
        "row_priority",
    ]
    if not rows:
        return pd.DataFrame(columns=columns)

    reference = pd.DataFrame(rows)
    reference["CODFAM"] = reference["CODFAM"].where(
        reference["CODFAM"].notna(),
        reference["CODPROD"].map(product_families),
    )
    reference["LIBPRDT"] = reference["CODPROD"].map(product_labels)
    reference["LIBFAMIL"] = reference["CODFAM"].map(references["family_labels"])
    reference[SOURCE_NATURAL_KEY] = (
        reference["CODPROD"].astype("string")
        + "|"
        + reference["CODFORMU"].astype("string")
    )
    reference["source_system"] = "fichierStagiaire.xlsx"
    reference["row_priority"] = 1

    return reference[columns]


def _build_sinistre_product_formula_rows(
    sinistres: pd.DataFrame,
    references: dict[str, Any],
    product_labels: dict[str, str],
    product_families: dict[str, str],
) -> pd.DataFrame:
    columns = [
        "CODFAM",
        "CODPROD",
        "CODFORMU",
        "LIBPRDT",
        "LIBFORMU",
        "LIBFAMIL",
        SOURCE_NATURAL_KEY,
        "source_system",
        "row_priority",
    ]
    if sinistres.empty:
        return pd.DataFrame(columns=columns)

    source = sinistres.copy()
    if "CODFAM" not in source.columns:
        source["CODFAM"] = pd.NA

    source["CODPROD"] = source["CODPROD"].map(normalize_code)
    source["CODFORMU"] = source["CODFORMU"].map(normalize_formula_code)
    source["CODFAM"] = source["CODFAM"].map(normalize_code)
    source = source[
        source["CODPROD"].notna()
        & source["CODFORMU"].notna()
        & source["CODFORMU"].ne(UNKNOWN)
    ].copy()
    if source.empty:
        return pd.DataFrame(columns=columns)

    source["CODFAM"] = source["CODFAM"].where(
        source["CODFAM"].notna(),
        source["CODPROD"].map(product_families),
    )
    source[SOURCE_NATURAL_KEY] = (
        source["CODPROD"].astype("string") + "|" + source["CODFORMU"].astype("string")
    )
    source = (
        source.sort_values([SOURCE_NATURAL_KEY], kind="mergesort")
        .drop_duplicates(subset=["CODPROD", "CODFORMU"], keep="first")
        .copy()
    )
    source["LIBPRDT"] = source["CODPROD"].map(product_labels)
    source["LIBFORMU"] = source[SOURCE_NATURAL_KEY].map(
        references["formula_labels"],
    )
    source["LIBFORMU"] = source["LIBFORMU"].fillna("Formule inconnue")
    source["LIBFAMIL"] = source["CODFAM"].map(references["family_labels"])
    source["source_system"] = "Sinistres.xlsx"
    source["row_priority"] = 2

    return source[columns]


def _count_label_conflicts(dataframe: pd.DataFrame) -> int:
    labels = dataframe.dropna(subset=["CODPROD", "LIBPRDT"])
    if labels.empty:
        return 0
    counts = labels.groupby("CODPROD")["LIBPRDT"].nunique()
    return int((counts > 1).sum())


def _select_most_frequent_values(
    dataframe: pd.DataFrame,
    key_column: str,
    value_column: str,
) -> dict[str, str]:
    values = dataframe[[key_column, value_column]].dropna(
        subset=[key_column, value_column],
    )
    if values.empty:
        return {}

    selected: dict[str, str] = {}
    for key, group in values.groupby(key_column, sort=False):
        counts = group[value_column].value_counts(dropna=True, sort=False)
        max_count = counts.max()
        selected[str(key)] = str(counts[counts == max_count].index[0])
    return selected


def _get_table_columns(cur: Any) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %(schema)s
          AND table_name = %(table)s
        """,
        {
            "schema": TARGET_SCHEMA,
            "table": TARGET_TABLE,
        },
    )
    columns = {row[0] for row in cur.fetchall()}
    if not columns:
        raise RuntimeError(f"{TARGET_SCHEMA}.{TARGET_TABLE} does not exist")
    return columns


def _assert_dim_produit_contract(cur: Any, table_columns: set[str]) -> None:
    required = {
        "produit_natural_key",
        "code_produit",
        "libelle_produit",
        "code_formule",
        "libelle_formule",
        "code_famille_produit",
        "libelle_famille_produit",
    }
    missing = sorted(required - table_columns)
    if missing:
        raise RuntimeError(
            f"{TARGET_SCHEMA}.{TARGET_TABLE} is missing columns: {', '.join(missing)}"
        )
    _assert_key_conflict_target(cur, "produit_natural_key")


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

    required_sources = {
        SOURCE_NATURAL_KEY,
        "CODPROD",
        "CODFORMU",
        "LIBFORMU",
        "CODFAM",
        "LIBFAMIL",
    }
    missing_sources = sorted(required_sources - set(mapping))
    if missing_sources:
        raise RuntimeError(
            "No insertable target columns found for source fields: "
            f"{', '.join(missing_sources)}"
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
        load_frame[target_column] = dataframe[source_column]

    load_frame = load_frame.astype(object).where(pd.notna(load_frame), None)
    return load_frame.to_dict(orient="records")


def _upsert_dim_produit_rows(
    cur: Any,
    rows: list[dict[str, Any]],
    table_columns: set[str],
) -> int:
    if not rows:
        return 0

    columns = list(rows[0].keys())
    update_columns = [column for column in columns if column != SOURCE_NATURAL_KEY]

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
        sql.Identifier(SOURCE_NATURAL_KEY),
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


def _missing_count(dataframe: pd.DataFrame, column: str) -> int:
    if column not in dataframe.columns:
        return len(dataframe)
    return int(dataframe[column].map(_is_missing_value).sum())


def _clean_label_value(value: Any) -> str | None:
    return _clean_text(value)


def _clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if text.casefold() in NULL_MARKERS:
        return None
    return text


def _is_missing_value(value: Any) -> bool:
    return _clean_text(value) is None


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
        description="Load Silver production products into iris_dw.dim_produit."
    )
    parser.add_argument(
        "--etl-run-id",
        required=True,
        help="ETL run id containing data/silver/<etl_run_id>/production.parquet.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
