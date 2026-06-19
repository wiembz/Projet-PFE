from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from psycopg import sql


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from etl.common.db import get_connection


REPORT_PATH = PROJECT_ROOT / "docs" / "dim_client_quality_diagnostic.md"
TARGET_SCHEMA = "iris_dw"
TARGET_TABLE = "dim_client"
NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}

KNOWN_DIM_CLIENT_COLUMNS = (
    "client_sk",
    "client_natural_key",
    "code_nature_client",
    "num_client",
    "type_identifiant",
    "identifiant_client",
    "adresse",
    "code_postal",
    "localite_client",
    "gouvernorat_client",
    "date_naissance",
    "sexe",
    "profession",
    "situation_familiale",
    "nombre_enfants",
    "date_debut_client",
    "source_system",
    "created_at",
    "updated_at",
)

TEXT_COLUMNS = (
    "client_natural_key",
    "code_nature_client",
    "num_client",
    "type_identifiant",
    "identifiant_client",
    "adresse",
    "code_postal",
    "localite_client",
    "gouvernorat_client",
    "sexe",
    "profession",
    "situation_familiale",
    "source_system",
)

NULL_PROFILE_COLUMNS = (
    "sexe",
    "situation_familiale",
    "nombre_enfants",
    "date_naissance",
    "profession",
    "type_identifiant",
    "identifiant_client",
)

TYPE_IDENTIFIANT_MORAL_TOKENS = {
    "FIS",
    "FISCAL",
    "MF",
    "M F",
    "M.F",
    "MATRICULE FISCAL",
    "PATENTE",
    "REG",
    "RC",
    "R C",
    "R.C",
    "RNE",
    "REGISTRE COMMERCE",
}

MORAL_TEXT_PATTERNS = (
    "SOCIETE",
    "STE",
    "SARL",
    "SUARL",
    "S A",
    "SA ",
    "ENTREPRISE",
    "ASSOCIATION",
    "BANQUE",
    "CLINIQUE",
    "HOTEL",
    "MINISTERE",
    "MUNICIPALITE",
    "OFFICE",
    "GROUPE",
    "COMPAGNIE",
    "ASSURANCE",
    "USINE",
    "ADMINISTRATION",
)

ALLOWED_SITUATION_FAMILIALE_VALUES = {
    "A",
    "C",
    "CELIBATAIRE",
    "CELIBATAIRE.",
    "D",
    "DIVORCE",
    "DIVORCEE",
    "M",
    "MARIE",
    "MARIEE",
    "N",
    "S",
    "SEPARE",
    "SEPAREE",
    "V",
    "VEUF",
    "VEUVE",
}


class Report:
    def __init__(self) -> None:
        self.console_lines: list[str] = []
        self.markdown_lines: list[str] = []

    def title(self, text: str, generated_at: str) -> None:
        self.console_lines.extend(
            [
                "=" * 100,
                text,
                f"Generated at: {generated_at}",
                "=" * 100,
            ]
        )
        self.markdown_lines.extend(
            [
                f"# {text}",
                "",
                f"Generated at: {generated_at}",
                "",
                (
                    "This diagnostic is read-only. It profiles "
                    "`iris_dw.dim_client`; it does not modify PostgreSQL, "
                    "Silver files, loaders, scoring, or marts."
                ),
                "",
            ]
        )

    def section(self, text: str) -> None:
        self.console_lines.extend(["", "-" * 100, text])
        self.markdown_lines.extend(["", f"## {text}", ""])

    def metric(self, label: str, value: Any) -> None:
        self.console_lines.append(f"{label}: {value}")
        self.markdown_lines.append(f"- {label}: `{_display_value(value)}`")

    def table(self, rows: list[dict[str, Any]], columns: list[str]) -> None:
        if not rows:
            self.console_lines.append("No rows.")
            self.markdown_lines.append("No rows.")
            return

        dataframe = pd.DataFrame(rows, columns=columns)
        dataframe = dataframe.astype(object).where(pd.notna(dataframe), "")
        self.console_lines.append(dataframe.to_string(index=False))
        self.markdown_lines.extend(_rows_to_markdown(dataframe.to_dict(orient="records"), columns))

    def bullets(self, values: list[str]) -> None:
        if not values:
            self.console_lines.append("No items.")
            self.markdown_lines.append("- No items.")
            return
        for value in values:
            self.console_lines.append(f"- {value}")
            self.markdown_lines.append(f"- {value}")

    def render_console(self) -> str:
        return "\n".join(self.console_lines)

    def render_markdown(self) -> str:
        return "\n".join(self.markdown_lines).rstrip() + "\n"


def main() -> None:
    _parse_args()
    results = diagnose_dim_client_quality()
    report = _build_report(results)

    print(report.render_console())
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report.render_markdown(), encoding="utf-8")
    print(f"\n[OK] Markdown diagnostic written to {REPORT_PATH}")


def diagnose_dim_client_quality() -> dict[str, Any]:
    generated_at = datetime.now().isoformat(timespec="seconds")
    dataframe, actual_columns = _read_dim_client()
    profile = _prepare_profile_frame(dataframe)

    volume = _general_volume(profile, actual_columns)
    profile_quality = _client_profile_quality(profile, actual_columns)
    moral = _probable_moral_or_incomplete_profiles(profile, actual_columns)
    physical = _physical_person_anomalies(profile, moral["probable_mask"], actual_columns)
    geography = _geographic_quality(profile, actual_columns)
    autocorrect = _autocorrection_candidates(profile, actual_columns)

    summary = {
        "total_clients": volume["total_clients"],
        "duplicate_client_natural_keys": volume["duplicate_client_natural_key_count"],
        "sexe_null_count": moral["sexe_null_count"],
        "sexe_x_count": moral["sexe_x_count"],
        "situation_familiale_null_count": moral["situation_familiale_null_count"],
        "situation_familiale_x_count": moral["situation_familiale_x_count"],
        "date_naissance_null_count": moral["date_naissance_null_count"],
        "probable_moral_or_incomplete_profile_count": (
            moral["probable_moral_or_incomplete_profile_count"]
        ),
        "geo_null_code_postal_count": geography["geo_null_code_postal_count"],
        "geo_null_localite_count": geography["geo_null_localite_count"],
        "geo_null_gouvernorat_count": geography["geo_null_gouvernorat_count"],
        "geo_conflicting_code_postal_count": geography["geo_conflicting_code_postal_count"],
        "geo_autocorrect_candidate_count": autocorrect["geo_autocorrect_candidate_count"],
    }

    return {
        "generated_at": generated_at,
        "actual_columns": sorted(actual_columns),
        "skipped_columns": sorted(set(KNOWN_DIM_CLIENT_COLUMNS) - actual_columns),
        "summary": summary,
        "volume": volume,
        "profile_quality": profile_quality,
        "moral": moral,
        "physical": physical,
        "geography": geography,
        "autocorrect": autocorrect,
    }


def _read_dim_client() -> tuple[pd.DataFrame, set[str]]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            actual_columns = _get_table_columns(cur)
            select_columns = [
                column for column in KNOWN_DIM_CLIENT_COLUMNS if column in actual_columns
            ]
            if not select_columns:
                raise RuntimeError(f"{TARGET_SCHEMA}.{TARGET_TABLE} has no expected columns")

            query = sql.SQL("SELECT {} FROM {}.{}").format(
                sql.SQL(", ").join(sql.Identifier(column) for column in select_columns),
                sql.Identifier(TARGET_SCHEMA),
                sql.Identifier(TARGET_TABLE),
            )
            cur.execute(query)
            rows = cur.fetchall()
    finally:
        conn.close()

    return pd.DataFrame(rows, columns=select_columns), actual_columns


def _get_table_columns(cur: Any) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        """,
        (TARGET_SCHEMA, TARGET_TABLE),
    )
    columns = {row[0] for row in cur.fetchall()}
    if not columns:
        raise RuntimeError(f"{TARGET_SCHEMA}.{TARGET_TABLE} does not exist")
    return columns


def _prepare_profile_frame(dataframe: pd.DataFrame) -> pd.DataFrame:
    profile = dataframe.copy()

    for column in TEXT_COLUMNS:
        if column in profile.columns:
            profile[f"_norm_{column}"] = profile[column].map(_normalize_text)

    if "nombre_enfants" in profile.columns:
        profile["_nombre_enfants_numeric"] = pd.to_numeric(
            profile["nombre_enfants"],
            errors="coerce",
        )

    if "date_naissance" in profile.columns:
        profile["_date_naissance_dt"] = pd.to_datetime(
            profile["date_naissance"],
            errors="coerce",
        )

    return profile


def _general_volume(profile: pd.DataFrame, actual_columns: set[str]) -> dict[str, Any]:
    total_clients = len(profile)
    unknown_mask = pd.Series(False, index=profile.index)

    if "client_sk" in actual_columns:
        unknown_mask = unknown_mask | pd.to_numeric(
            profile["client_sk"],
            errors="coerce",
        ).eq(0)
    if "client_natural_key" in actual_columns:
        unknown_mask = unknown_mask | _norm_series(profile, "client_natural_key").eq("UNKNOWN")
        natural_keys = _norm_series(profile, "client_natural_key")
        key_counts = natural_keys.dropna().value_counts()
        duplicate_key_count = int(key_counts.gt(1).sum())
        duplicate_row_count = int(key_counts.loc[key_counts.gt(1)].sum())
        distinct_key_count = int(natural_keys.dropna().nunique())
    else:
        duplicate_key_count = 0
        duplicate_row_count = 0
        distinct_key_count = 0

    return {
        "total_clients": total_clients,
        "unknown_row_count": int(unknown_mask.sum()),
        "distinct_client_natural_key_count": distinct_key_count,
        "duplicate_client_natural_key_count": duplicate_key_count,
        "duplicate_client_natural_key_row_count": duplicate_row_count,
    }


def _client_profile_quality(
    profile: pd.DataFrame,
    actual_columns: set[str],
) -> dict[str, Any]:
    null_counts = []
    for column in NULL_PROFILE_COLUMNS:
        if column not in actual_columns:
            null_counts.append({"column": column, "status": "missing", "null_count": ""})
            continue

        if column == "nombre_enfants":
            null_count = int(profile["_nombre_enfants_numeric"].isna().sum())
        elif column == "date_naissance":
            null_count = int(profile["_date_naissance_dt"].isna().sum())
        else:
            null_count = int(_norm_series(profile, column).isna().sum())

        null_counts.append({"column": column, "status": "available", "null_count": null_count})

    return {
        "code_nature_distribution": _distribution(profile, ["code_nature_client"]),
        "type_identifiant_distribution": _distribution(profile, ["type_identifiant"]),
        "code_nature_type_distribution": _distribution(
            profile,
            ["code_nature_client", "type_identifiant"],
        ),
        "code_nature_sexe_distribution": _distribution(
            profile,
            ["code_nature_client", "sexe"],
        ),
        "code_nature_situation_distribution": _distribution(
            profile,
            ["code_nature_client", "situation_familiale"],
        ),
        "code_nature_nombre_enfants_distribution": _distribution(
            profile,
            ["code_nature_client", "nombre_enfants"],
        ),
        "null_counts": null_counts,
    }


def _probable_moral_or_incomplete_profiles(
    profile: pd.DataFrame,
    actual_columns: set[str],
) -> dict[str, Any]:
    sexe = _norm_series(profile, "sexe")
    situation = _norm_series(profile, "situation_familiale")
    nombre_enfants = _numeric_series(profile, "_nombre_enfants_numeric")
    date_naissance = _datetime_series(profile, "_date_naissance_dt")

    sexe_null = sexe.isna()
    sexe_x = sexe.eq("X").fillna(False)
    situation_null = situation.isna()
    situation_x = situation.eq("X").fillna(False)
    nombre_null = nombre_enfants.isna()
    nombre_zero = nombre_enfants.eq(0).fillna(False)
    date_null = date_naissance.isna()

    base_incomplete_profile = (
        (sexe_null | sexe_x)
        & date_null
        & (situation_null | situation_x)
        & (nombre_null | nombre_zero)
    )

    type_indicator = _contains_type_moral_indicator(_norm_series(profile, "type_identifiant"))
    profession_indicator = _contains_text_indicator(_norm_series(profile, "profession"))
    adresse_indicator = _contains_text_indicator(_norm_series(profile, "adresse"))

    probable_mask = (
        base_incomplete_profile
        | type_indicator
        | profession_indicator
        | adresse_indicator
    )

    indicator_rows = [
        {
            "indicator": "base incomplete personal profile",
            "count": int(base_incomplete_profile.sum()),
        },
        {"indicator": "type_identifiant moral indicator", "count": int(type_indicator.sum())},
        {"indicator": "profession moral indicator", "count": int(profession_indicator.sum())},
        {"indicator": "adresse moral indicator", "count": int(adresse_indicator.sum())},
    ]

    sample_rows = _sample_rows(
        profile.loc[probable_mask],
        [
            "client_sk",
            "client_natural_key",
            "code_nature_client",
            "type_identifiant",
            "sexe",
            "date_naissance",
            "situation_familiale",
            "nombre_enfants",
            "profession",
        ],
        limit=20,
    )

    return {
        "probable_mask": probable_mask,
        "sexe_x_count": int(sexe_x.sum()),
        "situation_familiale_x_count": int(situation_x.sum()),
        "sexe_null_count": int(sexe_null.sum()),
        "situation_familiale_null_count": int(situation_null.sum()),
        "date_naissance_null_count": int(date_null.sum()),
        "nombre_enfants_null_count": int(nombre_null.sum()),
        "probable_moral_or_incomplete_profile_count": int(probable_mask.sum()),
        "indicator_rows": indicator_rows,
        "sample_rows": sample_rows,
    }


def _physical_person_anomalies(
    profile: pd.DataFrame,
    probable_moral_mask: pd.Series,
    actual_columns: set[str],
) -> dict[str, Any]:
    sexe = _norm_series(profile, "sexe")
    situation = _norm_series(profile, "situation_familiale")
    nombre_enfants = _numeric_series(profile, "_nombre_enfants_numeric")
    date_naissance = _datetime_series(profile, "_date_naissance_dt")
    profession = _norm_series(profile, "profession")

    personal_signal = (
        sexe.isin(["M", "F"]).fillna(False)
        | date_naissance.notna()
        | (situation.notna() & ~situation.eq("X").fillna(False))
        | nombre_enfants.notna()
        | profession.notna()
    )
    physical_like = (~probable_moral_mask) & personal_signal

    today = pd.Timestamp(date.today())
    invalid_or_null_sexe = physical_like & ~sexe.isin(["M", "F"]).fillna(False)
    negative_children = physical_like & nombre_enfants.lt(0).fillna(False)
    children_gt_20 = physical_like & nombre_enfants.gt(20).fillna(False)
    future_birth_date = physical_like & date_naissance.gt(today).fillna(False)
    age_gt_120 = physical_like & (
        ((today - date_naissance).dt.days / 365.25).gt(120).fillna(False)
    )
    suspicious_situation = (
        physical_like
        & situation.notna()
        & ~situation.isin(ALLOWED_SITUATION_FAMILIALE_VALUES).fillna(False)
    )

    anomaly_masks = {
        "physical_like_rows": physical_like,
        "sexe_not_m_f_or_null": invalid_or_null_sexe,
        "nombre_enfants_negative": negative_children,
        "nombre_enfants_gt_20": children_gt_20,
        "date_naissance_in_future": future_birth_date,
        "age_gt_120": age_gt_120,
        "situation_familiale_suspicious": suspicious_situation,
    }
    counts = [
        {"anomaly": name, "count": int(mask.sum())}
        for name, mask in anomaly_masks.items()
    ]

    any_anomaly = (
        invalid_or_null_sexe
        | negative_children
        | children_gt_20
        | future_birth_date
        | age_gt_120
        | suspicious_situation
    )
    sample = profile.loc[any_anomaly].copy()
    for name, mask in anomaly_masks.items():
        if name != "physical_like_rows":
            sample[name] = mask.loc[sample.index]

    sample_rows = _sample_rows(
        sample,
        [
            "client_sk",
            "client_natural_key",
            "code_nature_client",
            "type_identifiant",
            "sexe",
            "date_naissance",
            "situation_familiale",
            "nombre_enfants",
            "sexe_not_m_f_or_null",
            "nombre_enfants_negative",
            "nombre_enfants_gt_20",
            "date_naissance_in_future",
            "age_gt_120",
            "situation_familiale_suspicious",
        ],
        limit=50,
    )

    return {
        "counts": counts,
        "sample_rows": sample_rows,
        "missing_columns": sorted(
            set(["sexe", "nombre_enfants", "date_naissance", "situation_familiale"])
            - actual_columns
        ),
    }


def _geographic_quality(profile: pd.DataFrame, actual_columns: set[str]) -> dict[str, Any]:
    code_postal = _norm_series(profile, "code_postal")
    localite = _norm_series(profile, "localite_client")
    gouvernorat = _norm_series(profile, "gouvernorat_client")

    geo = pd.DataFrame(
        {
            "code_postal": code_postal,
            "localite_client": localite,
            "gouvernorat_client": gouvernorat,
        }
    )

    cp_stats = _code_postal_conflicts(geo)
    localite_stats = _localite_conflicts(geo)
    distinct_count_rows = _distinct_geo_count_rows(geo)

    return {
        "geo_null_code_postal_count": int(code_postal.isna().sum()),
        "geo_null_localite_count": int(localite.isna().sum()),
        "geo_null_gouvernorat_count": int(gouvernorat.isna().sum()),
        "geo_conflicting_code_postal_count": len(cp_stats),
        "geo_conflicting_localite_count": len(localite_stats),
        "distinct_count_rows": distinct_count_rows,
        "conflicting_code_postal_rows": cp_stats[:50],
        "conflicting_localite_rows": localite_stats[:50],
        "missing_columns": sorted(
            set(["code_postal", "localite_client", "gouvernorat_client"]) - actual_columns
        ),
    }


def _code_postal_conflicts(geo: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for code_postal, group in geo.loc[geo["code_postal"].notna()].groupby(
        "code_postal",
        sort=False,
    ):
        distinct_localite_count = int(group["localite_client"].dropna().nunique())
        distinct_gouvernorat_count = int(group["gouvernorat_client"].dropna().nunique())
        if distinct_localite_count <= 1 and distinct_gouvernorat_count <= 1:
            continue

        dominant_pair = _dominant_pair(group, "localite_client", "gouvernorat_client")
        rows.append(
            {
                "code_postal": code_postal,
                "distinct_localite_count": distinct_localite_count,
                "distinct_gouvernorat_count": distinct_gouvernorat_count,
                "total_rows": int(len(group)),
                "dominant_localite": _dominant_value(group["localite_client"]),
                "dominant_gouvernorat": _dominant_value(group["gouvernorat_client"]),
                "dominant_pair_count": dominant_pair["count"],
                "dominance_percentage": _percent(dominant_pair["count"], len(group)),
            }
        )

    rows.sort(
        key=lambda row: (
            row["distinct_localite_count"],
            row["distinct_gouvernorat_count"],
            row["total_rows"],
        ),
        reverse=True,
    )
    return rows


def _localite_conflicts(geo: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for localite, group in geo.loc[geo["localite_client"].notna()].groupby(
        "localite_client",
        sort=False,
    ):
        distinct_gouvernorat_count = int(group["gouvernorat_client"].dropna().nunique())
        if distinct_gouvernorat_count <= 1:
            continue

        dominant = _dominant_count(group["gouvernorat_client"])
        rows.append(
            {
                "localite_client": localite,
                "distinct_gouvernorat_count": distinct_gouvernorat_count,
                "total_rows": int(len(group)),
                "dominant_gouvernorat": dominant["value"],
                "dominance_percentage": _percent(dominant["count"], len(group)),
            }
        )

    rows.sort(
        key=lambda row: (row["distinct_gouvernorat_count"], row["total_rows"]),
        reverse=True,
    )
    return rows


def _distinct_geo_count_rows(geo: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cp_groups = geo.loc[geo["code_postal"].notna()].groupby("code_postal")
    rows.append(
        {
            "metric": "code_postal values",
            "group_count": int(cp_groups.ngroups),
            "max_distinct_localite_per_group": int(
                cp_groups["localite_client"].nunique().max() if cp_groups.ngroups else 0
            ),
            "max_distinct_gouvernorat_per_group": int(
                cp_groups["gouvernorat_client"].nunique().max() if cp_groups.ngroups else 0
            ),
        }
    )

    localite_groups = geo.loc[geo["localite_client"].notna()].groupby("localite_client")
    rows.append(
        {
            "metric": "localite_client values",
            "group_count": int(localite_groups.ngroups),
            "max_distinct_localite_per_group": "",
            "max_distinct_gouvernorat_per_group": int(
                localite_groups["gouvernorat_client"].nunique().max()
                if localite_groups.ngroups
                else 0
            ),
        }
    )
    return rows


def _autocorrection_candidates(
    profile: pd.DataFrame,
    actual_columns: set[str],
) -> dict[str, Any]:
    required_geo_columns = {"code_postal", "localite_client", "gouvernorat_client"}
    if not required_geo_columns.issubset(actual_columns):
        return {
            "type_a_rows": [],
            "type_b_rows": [],
            "type_c_rows": [],
            "geo_autocorrect_candidate_count": 0,
            "geo_autocorrect_candidate_row_count": 0,
            "missing_columns": sorted(required_geo_columns - actual_columns),
        }

    geo = pd.DataFrame(
        {
            "code_postal": _norm_series(profile, "code_postal"),
            "localite_client": _norm_series(profile, "localite_client"),
            "gouvernorat_client": _norm_series(profile, "gouvernorat_client"),
        }
    )

    type_a = _candidate_type_a(geo)
    type_b = _candidate_type_b(geo)
    type_c = _candidate_type_c(geo)
    candidate_row_count = sum(
        int(row.get("candidate_rows", 0))
        for row in [*type_a, *type_b, *type_c]
    )

    return {
        "type_a_rows": type_a,
        "type_b_rows": type_b,
        "type_c_rows": type_c,
        "geo_autocorrect_candidate_count": len(type_a) + len(type_b) + len(type_c),
        "geo_autocorrect_candidate_row_count": candidate_row_count,
        "missing_columns": [],
    }


def _candidate_type_a(geo: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source = geo.loc[geo["code_postal"].notna() & geo["localite_client"].notna()]
    for (code_postal, localite), group in source.groupby(
        ["code_postal", "localite_client"],
        sort=False,
    ):
        null_gouvernorat_rows = int(group["gouvernorat_client"].isna().sum())
        if null_gouvernorat_rows == 0:
            continue

        known_counts = group["gouvernorat_client"].dropna().value_counts()
        if known_counts.empty:
            continue

        recommended = str(known_counts.index[0])
        dominant_count = int(known_counts.iloc[0])
        known_rows = int(known_counts.sum())
        dominance_ratio = dominant_count / known_rows if known_rows else 0
        if dominance_ratio < 0.95:
            continue

        rows.append(
            {
                "candidate_type": "A",
                "code_postal": code_postal,
                "localite_client": localite,
                "candidate_rows": null_gouvernorat_rows,
                "known_gouvernorat_rows": known_rows,
                "recommended_gouvernorat": recommended,
                "dominance_percentage": _percent(dominant_count, known_rows),
            }
        )

    rows.sort(key=lambda row: (row["candidate_rows"], row["known_gouvernorat_rows"]), reverse=True)
    return rows


def _candidate_type_b(geo: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source = geo.loc[geo["code_postal"].notna()]
    for code_postal, group in source.groupby("code_postal", sort=False):
        pair_counts = (
            group.dropna(subset=["localite_client", "gouvernorat_client"])
            .groupby(["localite_client", "gouvernorat_client"])
            .size()
            .sort_values(ascending=False)
        )
        if pair_counts.empty:
            continue

        recommended_localite, recommended_gouvernorat = pair_counts.index[0]
        dominant_count = int(pair_counts.iloc[0])
        known_pair_rows = int(pair_counts.sum())
        dominance_ratio = dominant_count / known_pair_rows if known_pair_rows else 0
        candidate_rows = int(len(group) - dominant_count)
        if dominance_ratio < 0.95 or candidate_rows == 0:
            continue

        rows.append(
            {
                "candidate_type": "B",
                "code_postal": code_postal,
                "candidate_rows": candidate_rows,
                "known_pair_rows": known_pair_rows,
                "recommended_localite": recommended_localite,
                "recommended_gouvernorat": recommended_gouvernorat,
                "dominance_percentage": _percent(dominant_count, known_pair_rows),
            }
        )

    rows.sort(key=lambda row: (row["candidate_rows"], row["known_pair_rows"]), reverse=True)
    return rows


def _candidate_type_c(geo: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source = geo.loc[geo["localite_client"].notna()]
    for localite, group in source.groupby("localite_client", sort=False):
        known_counts = group["gouvernorat_client"].dropna().value_counts()
        if known_counts.empty:
            continue

        recommended = str(known_counts.index[0])
        dominant_count = int(known_counts.iloc[0])
        known_rows = int(known_counts.sum())
        dominance_ratio = dominant_count / known_rows if known_rows else 0
        candidate_rows = int(len(group) - dominant_count)
        if dominance_ratio < 0.95 or candidate_rows == 0:
            continue

        rows.append(
            {
                "candidate_type": "C",
                "localite_client": localite,
                "candidate_rows": candidate_rows,
                "known_gouvernorat_rows": known_rows,
                "recommended_gouvernorat": recommended,
                "dominance_percentage": _percent(dominant_count, known_rows),
            }
        )

    rows.sort(key=lambda row: (row["candidate_rows"], row["known_gouvernorat_rows"]), reverse=True)
    return rows


def _build_report(results: dict[str, Any]) -> Report:
    report = Report()
    report.title("IRISv2 dim_client Data Quality Diagnostic", results["generated_at"])

    summary = results["summary"]
    report.section("1. Executive Summary")
    for key in (
        "total_clients",
        "duplicate_client_natural_keys",
        "sexe_null_count",
        "sexe_x_count",
        "situation_familiale_null_count",
        "situation_familiale_x_count",
        "date_naissance_null_count",
        "probable_moral_or_incomplete_profile_count",
        "geo_null_code_postal_count",
        "geo_null_localite_count",
        "geo_null_gouvernorat_count",
        "geo_conflicting_code_postal_count",
        "geo_autocorrect_candidate_count",
    ):
        report.metric(key, summary[key])

    volume = results["volume"]
    report.section("2. General Volume")
    report.metric("total row count", volume["total_clients"])
    report.metric("UNKNOWN row count", volume["unknown_row_count"])
    report.metric(
        "distinct client_natural_key count",
        volume["distinct_client_natural_key_count"],
    )
    report.metric(
        "duplicate client_natural_key count",
        volume["duplicate_client_natural_key_count"],
    )
    report.metric(
        "duplicate client_natural_key row count",
        volume["duplicate_client_natural_key_row_count"],
    )
    report.metric("available dim_client columns", ", ".join(results["actual_columns"]))
    if results["skipped_columns"]:
        report.metric("skipped missing known columns", ", ".join(results["skipped_columns"]))

    profile_quality = results["profile_quality"]
    report.section("3. Client Profile Quality")
    report.metric("Distribution limit", "top 50 rows per table")
    report.table(profile_quality["null_counts"], ["column", "status", "null_count"])

    report.section("3.1 code_nature_client Distribution")
    report.table(profile_quality["code_nature_distribution"], ["code_nature_client", "row_count"])

    report.section("3.2 type_identifiant Distribution")
    report.table(profile_quality["type_identifiant_distribution"], ["type_identifiant", "row_count"])

    report.section("3.3 code_nature_client + type_identifiant")
    report.table(
        profile_quality["code_nature_type_distribution"],
        ["code_nature_client", "type_identifiant", "row_count"],
    )

    report.section("3.4 code_nature_client + sexe")
    report.table(
        profile_quality["code_nature_sexe_distribution"],
        ["code_nature_client", "sexe", "row_count"],
    )

    report.section("3.5 code_nature_client + situation_familiale")
    report.table(
        profile_quality["code_nature_situation_distribution"],
        ["code_nature_client", "situation_familiale", "row_count"],
    )

    report.section("3.6 code_nature_client + nombre_enfants")
    report.table(
        profile_quality["code_nature_nombre_enfants_distribution"],
        ["code_nature_client", "nombre_enfants", "row_count"],
    )

    moral = results["moral"]
    report.section("4. Probable Moral/Incomplete Profiles")
    report.metric("sexe = X", moral["sexe_x_count"])
    report.metric("situation_familiale = X", moral["situation_familiale_x_count"])
    report.metric("rows where sexe is null", moral["sexe_null_count"])
    report.metric(
        "rows where situation_familiale is null",
        moral["situation_familiale_null_count"],
    )
    report.metric("rows where date_naissance is null", moral["date_naissance_null_count"])
    report.metric("rows where nombre_enfants is null", moral["nombre_enfants_null_count"])
    report.metric(
        "probable_moral_or_incomplete_profile",
        moral["probable_moral_or_incomplete_profile_count"],
    )
    report.table(moral["indicator_rows"], ["indicator", "count"])
    report.section("4.1 Sample probable moral/incomplete profiles")
    report.table(
        moral["sample_rows"],
        [
            "client_sk",
            "client_natural_key",
            "code_nature_client",
            "type_identifiant",
            "sexe",
            "date_naissance",
            "situation_familiale",
            "nombre_enfants",
            "profession",
        ],
    )

    physical = results["physical"]
    report.section("5. Physical-Person Anomalies")
    if physical["missing_columns"]:
        report.metric("skipped anomaly columns", ", ".join(physical["missing_columns"]))
    report.table(physical["counts"], ["anomaly", "count"])
    report.section("5.1 Sample physical-person anomaly rows")
    report.table(
        physical["sample_rows"],
        [
            "client_sk",
            "client_natural_key",
            "code_nature_client",
            "type_identifiant",
            "sexe",
            "date_naissance",
            "situation_familiale",
            "nombre_enfants",
            "sexe_not_m_f_or_null",
            "nombre_enfants_negative",
            "nombre_enfants_gt_20",
            "date_naissance_in_future",
            "age_gt_120",
            "situation_familiale_suspicious",
        ],
    )

    geography = results["geography"]
    report.section("6. Geographic Conflicts")
    if geography["missing_columns"]:
        report.metric("skipped geographic columns", ", ".join(geography["missing_columns"]))
    report.metric("null/empty code_postal count", geography["geo_null_code_postal_count"])
    report.metric("null/empty localite_client count", geography["geo_null_localite_count"])
    report.metric("null/empty gouvernorat_client count", geography["geo_null_gouvernorat_count"])
    report.metric(
        "conflicting code_postal count",
        geography["geo_conflicting_code_postal_count"],
    )
    report.metric(
        "conflicting localite_client count",
        geography["geo_conflicting_localite_count"],
    )
    report.table(
        geography["distinct_count_rows"],
        [
            "metric",
            "group_count",
            "max_distinct_localite_per_group",
            "max_distinct_gouvernorat_per_group",
        ],
    )

    report.section("6.1 Top 50 conflicting code_postal values")
    report.table(
        geography["conflicting_code_postal_rows"],
        [
            "code_postal",
            "distinct_localite_count",
            "distinct_gouvernorat_count",
            "total_rows",
            "dominant_localite",
            "dominant_gouvernorat",
            "dominant_pair_count",
            "dominance_percentage",
        ],
    )

    report.section("6.2 Top 50 conflicting localite_client values")
    report.table(
        geography["conflicting_localite_rows"],
        [
            "localite_client",
            "distinct_gouvernorat_count",
            "total_rows",
            "dominant_gouvernorat",
            "dominance_percentage",
        ],
    )

    autocorrect = results["autocorrect"]
    report.section("7. Auto-Correction Candidates")
    if autocorrect["missing_columns"]:
        report.metric("skipped auto-correction columns", ", ".join(autocorrect["missing_columns"]))
    report.metric("candidate group count", autocorrect["geo_autocorrect_candidate_count"])
    report.metric("candidate row count", autocorrect["geo_autocorrect_candidate_row_count"])

    report.section("7.1 Candidate Type A: code_postal + localite -> gouvernorat")
    report.table(
        autocorrect["type_a_rows"],
        [
            "candidate_type",
            "code_postal",
            "localite_client",
            "candidate_rows",
            "known_gouvernorat_rows",
            "recommended_gouvernorat",
            "dominance_percentage",
        ],
    )

    report.section("7.2 Candidate Type B: code_postal -> localite + gouvernorat")
    report.table(
        autocorrect["type_b_rows"],
        [
            "candidate_type",
            "code_postal",
            "candidate_rows",
            "known_pair_rows",
            "recommended_localite",
            "recommended_gouvernorat",
            "dominance_percentage",
        ],
    )

    report.section("7.3 Candidate Type C: localite -> gouvernorat")
    report.table(
        autocorrect["type_c_rows"],
        [
            "candidate_type",
            "localite_client",
            "candidate_rows",
            "known_gouvernorat_rows",
            "recommended_gouvernorat",
            "dominance_percentage",
        ],
    )

    report.section("8. Recommended Next Actions")
    report.bullets(
        [
            (
                "Review probable_moral_or_incomplete_profile as a diagnostic flag only; "
                "do not recode client type directly from these indicators."
            ),
            (
                "Implement any accepted personal-field cleanups later in "
                "etl/transform/clean_clients.py, before loading dim_client."
            ),
            (
                "Use the geographic candidate tables as review queues for deterministic "
                "normalization rules; keep a human-approved whitelist for corrections."
            ),
            (
                "Do not mutate iris_dw.dim_client directly; rerun the loader after "
                "transform-level fixes are approved."
            ),
        ]
    )

    return report


def _distribution(profile: pd.DataFrame, columns: list[str], limit: int = 50) -> list[dict[str, Any]]:
    missing_columns = [column for column in columns if column not in profile.columns]
    if missing_columns:
        return [
            {
                **{column: "<MISSING>" for column in columns},
                "row_count": f"missing columns: {', '.join(missing_columns)}",
            }
        ]

    work = pd.DataFrame(index=profile.index)
    for column in columns:
        if column == "nombre_enfants":
            work[column] = _numeric_series(profile, "_nombre_enfants_numeric").map(
                _group_value,
            )
        else:
            work[column] = _norm_series(profile, column).map(_group_value)

    grouped = (
        work.groupby(columns, dropna=False)
        .size()
        .reset_index(name="row_count")
        .sort_values("row_count", ascending=False)
        .head(limit)
    )
    return grouped.to_dict(orient="records")


def _sample_rows(
    dataframe: pd.DataFrame,
    columns: list[str],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    if dataframe.empty:
        return []

    available_columns = [column for column in columns if column in dataframe.columns]
    if not available_columns:
        return []

    sample = dataframe.loc[:, available_columns].head(limit).copy()
    for column in sample.columns:
        if pd.api.types.is_datetime64_any_dtype(sample[column]):
            sample[column] = sample[column].dt.date
    sample = sample.astype(object).where(pd.notna(sample), "")
    return sample.to_dict(orient="records")


def _norm_series(profile: pd.DataFrame, column: str) -> pd.Series:
    normalized_column = f"_norm_{column}"
    if normalized_column in profile.columns:
        return profile[normalized_column]
    return pd.Series(pd.NA, index=profile.index, dtype="object")


def _numeric_series(profile: pd.DataFrame, column: str) -> pd.Series:
    if column in profile.columns:
        return profile[column]
    return pd.Series(pd.NA, index=profile.index, dtype="float64")


def _datetime_series(profile: pd.DataFrame, column: str) -> pd.Series:
    if column in profile.columns:
        return profile[column]
    return pd.Series(pd.NaT, index=profile.index, dtype="datetime64[ns]")


def _contains_type_moral_indicator(series: pd.Series) -> pd.Series:
    if series.empty:
        return pd.Series(False, index=series.index)
    return series.fillna("").map(
        lambda value: any(token in value for token in TYPE_IDENTIFIANT_MORAL_TOKENS)
    )


def _contains_text_indicator(series: pd.Series) -> pd.Series:
    if series.empty:
        return pd.Series(False, index=series.index)
    return series.fillna("").map(
        lambda value: any(token in value for token in MORAL_TEXT_PATTERNS)
    )


def _dominant_value(series: pd.Series) -> str | None:
    dominant = _dominant_count(series)
    return dominant["value"]


def _dominant_count(series: pd.Series) -> dict[str, Any]:
    counts = series.dropna().value_counts()
    if counts.empty:
        return {"value": None, "count": 0}
    return {"value": str(counts.index[0]), "count": int(counts.iloc[0])}


def _dominant_pair(group: pd.DataFrame, first_column: str, second_column: str) -> dict[str, Any]:
    pair_counts = (
        group.dropna(subset=[first_column, second_column])
        .groupby([first_column, second_column])
        .size()
        .sort_values(ascending=False)
    )
    if pair_counts.empty:
        return {"first": None, "second": None, "count": 0}
    first, second = pair_counts.index[0]
    return {"first": first, "second": second, "count": int(pair_counts.iloc[0])}


def _normalize_text(value: Any) -> str | None:
    if pd.isna(value):
        return None

    cleaned = re.sub(r"\s+", " ", str(value).strip()).upper()
    if cleaned.casefold() in NULL_MARKERS:
        return None
    return cleaned


def _group_value(value: Any) -> str:
    if value is None or pd.isna(value):
        return "<NULL>"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _percent(numerator: int | float, denominator: int | float) -> str:
    if denominator == 0:
        return "0.00%"
    return f"{(float(numerator) / float(denominator) * 100):.2f}%"


def _rows_to_markdown(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    if not rows:
        return ["No rows."]

    lines = [
        "| " + " | ".join(_markdown_cell(column) for column in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(_markdown_cell(_display_value(row.get(column))) for column in columns)
            + " |"
        )
    return lines


def _display_value(value: Any) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _markdown_cell(value: Any) -> str:
    return _display_value(value).replace("|", "\\|").replace("\n", " ")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnose iris_dw.dim_client data quality without modifying data."
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
