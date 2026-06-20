"""Small helpers that shape data for Streamlit charts."""

from __future__ import annotations

import pandas as pd

from .analytics import risk_distribution, risk_summary_by_course, summarize_by_course


def students_by_course_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    summary = summarize_by_course(df)
    if summary.empty or "student_count" not in summary.columns:
        return pd.DataFrame()
    return summary.set_index("course")[["student_count"]]


def course_metric_chart_data(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    summary = summarize_by_course(df)
    if summary.empty or metric not in summary.columns:
        return pd.DataFrame()
    return summary.set_index("course")[[metric]]


def risk_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    distribution = risk_distribution(df)
    if distribution.empty:
        return pd.DataFrame()
    return distribution.set_index("risk_level")[["count"]]


def failed_subjects_by_risk_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    if "risk_level" not in df.columns or "failed_subjects" not in df.columns:
        return pd.DataFrame()

    working = df.copy()
    working["failed_subjects"] = pd.to_numeric(working["failed_subjects"], errors="coerce")
    working["risk_level"] = working["risk_level"].fillna("Missing").astype(str).str.strip().replace("", "Missing")
    chart_data = working.groupby("risk_level", dropna=False)["failed_subjects"].mean().round(2).reset_index()
    return chart_data.set_index("risk_level")[["failed_subjects"]]


def risk_summary_by_course_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    summary = risk_summary_by_course(df)
    if summary.empty:
        return pd.DataFrame()
    return summary.pivot(index="course", columns="risk_level", values="student_count").fillna(0)
