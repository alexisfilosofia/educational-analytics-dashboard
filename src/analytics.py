"""Analytical summaries for educational datasets."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import pandas as pd

HIGH_RISK_LABEL = "high"
RECOMMENDED_COLUMNS = [
    "student_id",
    "year",
    "course",
    "attendance_rate",
    "average_grade",
    "failed_subjects",
    "risk_level",
    "gender_group",
    "neighborhood_group",
]


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


def recommended_columns_status(df: pd.DataFrame, recommended_columns: Sequence[str] = RECOMMENDED_COLUMNS) -> dict[str, list[str]]:
    """Return which recommended dashboard columns are present or missing."""
    found = [column for column in recommended_columns if column in df.columns]
    missing = [column for column in recommended_columns if column not in df.columns]
    return {"found": found, "missing": missing}


def filter_dataset(df: pd.DataFrame, filters: Mapping[str, Sequence[object]]) -> pd.DataFrame:
    """Return a filtered copy while ignoring missing columns and All selections."""
    filtered = df.copy()

    for column, selected_values in filters.items():
        if column not in filtered.columns:
            continue

        selected = [value for value in selected_values if value != "All"]
        if not selected:
            continue

        comparable = filtered[column].fillna("Missing").astype(str).str.strip().replace("", "Missing")
        filtered = filtered[comparable.isin([str(value) for value in selected])]

    return filtered.reset_index(drop=True)


def detect_out_of_range_values(df: pd.DataFrame, column: str, minimum: float, maximum: float) -> pd.DataFrame:
    """Return rows where a numeric column falls outside the expected range."""
    if column not in df.columns:
        return pd.DataFrame(columns=df.columns)

    values = _to_numeric(df[column])
    mask = values.notna() & ((values < minimum) | (values > maximum))
    return df.loc[mask].copy()


def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Build a compact quality report for the current dataset."""
    rows: list[dict[str, object]] = [
        {
            "check": "total_rows",
            "column": "dataset",
            "value": int(len(df)),
            "details": "Rows in the current clean filtered dataset.",
        },
        {
            "check": "total_columns",
            "column": "dataset",
            "value": int(len(df.columns)),
            "details": "Columns in the current clean filtered dataset.",
        },
    ]

    for column in df.columns:
        missing_count = int(df[column].isna().sum())
        if pd.api.types.is_object_dtype(df[column]) or pd.api.types.is_string_dtype(df[column]):
            missing_count = int((df[column].isna() | df[column].astype("string").str.strip().eq("")).sum())

        rows.append(
            {
                "check": "missing_values",
                "column": column,
                "value": missing_count,
                "details": f"{round((missing_count / len(df)) * 100, 2) if len(df) else 0.0}% missing",
            }
        )

    empty_columns = [
        column
        for column in df.columns
        if (
            df[column].isna() | df[column].astype("string").str.strip().eq("")
            if pd.api.types.is_object_dtype(df[column]) or pd.api.types.is_string_dtype(df[column])
            else df[column].isna()
        ).all()
    ]
    rows.append(
        {
            "check": "empty_columns",
            "column": "dataset",
            "value": len(empty_columns),
            "details": ", ".join(empty_columns) if empty_columns else "None",
        }
    )

    if "student_id" in df.columns:
        duplicate_count = int(df["student_id"].duplicated().sum())
        rows.append(
            {
                "check": "duplicate_student_id",
                "column": "student_id",
                "value": duplicate_count,
                "details": "Duplicate student_id values after the first occurrence.",
            }
        )

    if "attendance_rate" in df.columns:
        out_of_range = detect_out_of_range_values(df, "attendance_rate", 0, 100)
        rows.append(
            {
                "check": "out_of_range",
                "column": "attendance_rate",
                "value": int(len(out_of_range)),
                "details": "Expected range: 0 to 100.",
            }
        )

    if "average_grade" in df.columns:
        out_of_range = detect_out_of_range_values(df, "average_grade", 0, 10)
        rows.append(
            {
                "check": "out_of_range",
                "column": "average_grade",
                "value": int(len(out_of_range)),
                "details": "Expected range: 0 to 10.",
            }
        )

    return pd.DataFrame(rows, columns=["check", "column", "value", "details"])


def educational_metrics(df: pd.DataFrame) -> dict[str, float | int | None]:
    """Return top-level metrics for the current educational dataset."""
    metrics: dict[str, float | int | None] = {
        "total_records": int(len(df)),
        "average_attendance": None,
        "average_grade": None,
        "average_failed_subjects": None,
        "high_risk_count": None,
        "high_risk_percentage": None,
    }

    if "attendance_rate" in df.columns:
        metrics["average_attendance"] = float(_to_numeric(df["attendance_rate"]).mean())
    if "average_grade" in df.columns:
        metrics["average_grade"] = float(_to_numeric(df["average_grade"]).mean())
    if "failed_subjects" in df.columns:
        metrics["average_failed_subjects"] = float(_to_numeric(df["failed_subjects"]).mean())
    if "risk_level" in df.columns:
        high_risk = df["risk_level"].astype("string").str.strip().str.lower().eq(HIGH_RISK_LABEL)
        metrics["high_risk_count"] = int(high_risk.sum())
        metrics["high_risk_percentage"] = float(high_risk.mean() * 100) if len(df) else 0.0

    return metrics


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
            .agg(high_risk_count=("is_high_risk", "sum"), high_risk_percentage=("is_high_risk", "mean"))
            .reset_index()
        )
        risk["high_risk_percentage"] = risk["high_risk_percentage"] * 100
        summary = summary.merge(risk, on="course", how="left")

    numeric_columns = summary.select_dtypes(include="number").columns
    summary[numeric_columns] = summary[numeric_columns].round(2)
    return summary.sort_values("course", kind="stable").reset_index(drop=True)


def risk_summary_by_course(df: pd.DataFrame) -> pd.DataFrame:
    """Return risk-level counts by course when both columns are available."""
    if "course" not in df.columns or "risk_level" not in df.columns:
        return pd.DataFrame(columns=["course", "risk_level", "student_count", "course_percentage"])

    working = df.copy()
    working["risk_level"] = working["risk_level"].fillna("Missing").astype(str).str.strip().replace("", "Missing")
    summary = working.groupby(["course", "risk_level"], dropna=False).size().reset_index(name="student_count")
    totals = summary.groupby("course")["student_count"].transform("sum")
    summary["course_percentage"] = (summary["student_count"] / totals * 100).round(2)
    return summary.sort_values(["course", "risk_level"], kind="stable").reset_index(drop=True)


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
