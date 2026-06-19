"""Small helpers that shape data for Streamlit charts."""

from __future__ import annotations

import pandas as pd

from .analytics import risk_distribution, summarize_by_course


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
