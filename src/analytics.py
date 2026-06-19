"""Analytical summaries for educational datasets."""

from __future__ import annotations

import pandas as pd

HIGH_RISK_LABEL = "high"


def dataset_overview(df: pd.DataFrame) -> dict[str, object]:
    """Return high-level dataset metadata."""
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "numeric_columns": list(df.select_dtypes(include="number").columns),
        "categorical_columns": list(df.select_dtypes(include=["object", "category", "string"]).columns),
        "missing_cells": int(df.isna().sum().sum()),
    }


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def summarize_by_course(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize key indicators by course when the required column exists."""
    if "course" not in df.columns:
        return pd.DataFrame()

    working = df.copy()
    if "student_id" not in working.columns:
        working["student_id"] = range(1, len(working) + 1)

    for column in ["attendance_rate", "average_grade", "failed_subjects"]:
        if column in working.columns:
            working[column] = _to_numeric(working[column])

    aggregations: dict[str, tuple[str, str]] = {
        "student_count": ("student_id", "count"),
    }

    if "attendance_rate" in working.columns:
        aggregations["average_attendance"] = ("attendance_rate", "mean")
    if "average_grade" in working.columns:
        aggregations["average_grade"] = ("average_grade", "mean")
    if "failed_subjects" in working.columns:
        aggregations["average_failed_subjects"] = ("failed_subjects", "mean")

    summary = working.groupby("course", dropna=False).agg(**aggregations).reset_index()

    if "risk_level" in working.columns:
        risk = (
            working.assign(is_high_risk=working["risk_level"].astype("string").str.lower().eq(HIGH_RISK_LABEL))
            .groupby("course", dropna=False)
            .agg(high_risk_count=("is_high_risk", "sum"), high_risk_share=("is_high_risk", "mean"))
            .reset_index()
        )
        summary = summary.merge(risk, on="course", how="left")

    numeric_columns = summary.select_dtypes(include="number").columns
    summary[numeric_columns] = summary[numeric_columns].round(2)
    return summary.sort_values("course", kind="stable").reset_index(drop=True)


def risk_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return counts and percentages by risk level."""
    if "risk_level" not in df.columns:
        return pd.DataFrame(columns=["risk_level", "count", "percent"])

    counts = df["risk_level"].fillna("Missing").astype(str).str.strip().replace("", "Missing").value_counts(dropna=False)
    distribution = counts.rename_axis("risk_level").reset_index(name="count")
    distribution["percent"] = (distribution["count"] / len(df) * 100).round(2) if len(df) else 0.0
    return distribution


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric columns."""
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        return pd.DataFrame()
    return numeric.describe().T.reset_index(names="column").round(2)


def categorical_distribution(df: pd.DataFrame, column: str, *, max_categories: int = 20) -> pd.DataFrame:
    """Return a compact distribution table for a categorical column."""
    if column not in df.columns:
        return pd.DataFrame(columns=[column, "count", "percent"])

    series = df[column].fillna("Missing").astype(str).str.strip().replace("", "Missing")
    counts = series.value_counts().head(max_categories)
    distribution = counts.rename_axis(column).reset_index(name="count")
    distribution["percent"] = (distribution["count"] / len(df) * 100).round(2) if len(df) else 0.0
    return distribution
