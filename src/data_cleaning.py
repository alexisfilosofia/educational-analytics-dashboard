"""Data cleaning helpers for educational analytics datasets."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with lowercase, snake_case column names."""
    cleaned = df.copy()
    seen: dict[str, int] = {}
    new_columns: list[str] = []

    for column in cleaned.columns:
        normalized = str(column).strip().lower()
        normalized = re.sub(r"[^0-9a-zA-Z]+", "_", normalized)
        normalized = re.sub(r"_+", "_", normalized).strip("_")
        normalized = normalized or "unnamed_column"

        count = seen.get(normalized, 0) + 1
        seen[normalized] = count
        if count > 1:
            normalized = f"{normalized}_{count}"

        new_columns.append(normalized)

    cleaned.columns = new_columns
    return cleaned


def trim_string_values(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with leading and trailing whitespace removed from strings."""
    cleaned = df.copy()
    for column in cleaned.select_dtypes(include=["object", "string"]).columns:
        cleaned[column] = cleaned[column].map(lambda value: value.strip() if isinstance(value, str) else value)
    return cleaned


def _missing_like_mask(series: pd.Series) -> pd.Series:
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        return series.isna() | series.astype("string").str.strip().eq("")
    return series.isna()


def detect_empty_columns(df: pd.DataFrame) -> list[str]:
    """Return columns where every value is missing or blank."""
    return [column for column in df.columns if _missing_like_mask(df[column]).all()]


def missing_values_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return missing-value counts and percentages by column."""
    if df.empty and len(df.columns) == 0:
        return pd.DataFrame(columns=["column", "missing_count", "missing_percent"])

    rows: list[dict[str, Any]] = []
    total_rows = len(df)

    for column in df.columns:
        missing_count = int(_missing_like_mask(df[column]).sum())
        missing_percent = round((missing_count / total_rows) * 100, 2) if total_rows else 0.0
        rows.append(
            {
                "column": column,
                "missing_count": missing_count,
                "missing_percent": missing_percent,
            }
        )

    return pd.DataFrame(rows).sort_values(["missing_count", "column"], ascending=[False, True]).reset_index(drop=True)


def clean_dataset(
    df: pd.DataFrame,
    *,
    normalize_columns: bool = True,
    trim_strings: bool = True,
    drop_empty_columns: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Apply basic cleaning steps and return the cleaned dataset plus a report."""
    cleaned = df.copy()
    original_shape = cleaned.shape

    if normalize_columns:
        cleaned = normalize_column_names(cleaned)

    if trim_strings:
        cleaned = trim_string_values(cleaned)

    empty_columns = detect_empty_columns(cleaned)
    if drop_empty_columns and empty_columns:
        cleaned = cleaned.drop(columns=empty_columns)

    report = {
        "original_shape": original_shape,
        "cleaned_shape": cleaned.shape,
        "empty_columns": empty_columns,
        "dropped_empty_columns": empty_columns if drop_empty_columns else [],
        "missing_values": missing_values_summary(cleaned),
    }
    return cleaned, report
