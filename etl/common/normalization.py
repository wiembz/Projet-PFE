from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd


NULL_MARKERS = {"", "nan", "none", "<na>", "nat", "null"}
UNKNOWN = "UNKNOWN"


def normalize_code(value: Any) -> str | None:
    text = _clean_text(value)
    if text is None:
        return None
    return text.upper()


def normalize_formula_code(value: Any) -> str:
    text = _clean_text(value)
    if text is None:
        return UNKNOWN

    upper_text = text.upper()
    numeric = _normalize_numeric_text(upper_text)
    if numeric is not None:
        return numeric
    return upper_text


def normalize_product_natural_key(value: Any) -> str | None:
    text = _clean_text(value)
    if text is None or "|" not in text:
        return normalize_code(value)

    product_code, formula_code = text.split("|", 1)
    normalized_product = normalize_code(product_code)
    if normalized_product is None:
        return None
    return f"{normalized_product}|{normalize_formula_code(formula_code)}"


def _clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if text.casefold() in NULL_MARKERS:
        return None
    return text


def _normalize_numeric_text(value: str) -> str | None:
    try:
        number = Decimal(value)
    except InvalidOperation:
        return None

    if not number.is_finite():
        return None
    if number == number.to_integral_value():
        return str(int(number))

    normalized = format(number.normalize(), "f")
    return normalized.rstrip("0").rstrip(".")
