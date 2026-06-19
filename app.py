"""Streamlit educational analytics dashboard demo."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.analytics import (
    categorical_distribution,
    dataset_overview,
    numeric_summary,
    risk_distribution,
    summarize_by_course,
)
from src.data_cleaning import clean_dataset
from src.visualization import course_metric_chart_data, risk_chart_data, students_by_course_chart_data

SAMPLE_DATA_PATH = Path(__file__).parent / "data" / "sample_educational_data.csv"


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    return pd.read_csv(SAMPLE_DATA_PATH)


def load_uploaded_data(uploaded_file) -> pd.DataFrame:
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if uploaded_file.name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    raise ValueError("Unsupported file type. Please upload a CSV or XLSX file.")


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def format_percent(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.1f}%"


def main() -> None:
    st.set_page_config(
        page_title="Educational Analytics Dashboard",
        page_icon="📊",
        layout="wide",
    )

    st.title("Educational Analytics Dashboard")
    st.caption(
        "A Streamlit demo for CSV/Excel upload, basic cleaning, educational indicators, visual summaries, and CSV exports."
    )

    with st.sidebar:
        st.header("Data source")
        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
        use_sample = st.checkbox("Use synthetic sample dataset", value=True, disabled=uploaded_file is not None)

        st.header("Cleaning options")
        normalize_columns = st.checkbox("Normalize column names", value=True)
        trim_strings = st.checkbox("Trim whitespace in text values", value=True)
        drop_empty_columns = st.checkbox("Drop empty columns", value=False)

    if uploaded_file is not None:
        raw_df = load_uploaded_data(uploaded_file)
        source_label = uploaded_file.name
    elif use_sample:
        raw_df = load_sample_data()
        source_label = "data/sample_educational_data.csv"
    else:
        st.info("Upload a CSV/XLSX file or enable the synthetic sample dataset to begin.")
        return

    st.subheader("Dataset preview")
    st.write(f"Source: `{source_label}`")
    overview = dataset_overview(raw_df)
    metric_cols = st.columns(3)
    metric_cols[0].metric("Rows", f"{overview['rows']:,}")
    metric_cols[1].metric("Columns", f"{overview['columns']:,}")
    metric_cols[2].metric("Missing cells", f"{overview['missing_cells']:,}")

    st.dataframe(raw_df.head(10), use_container_width=True)
    with st.expander("Column names"):
        st.write(list(raw_df.columns))

    cleaned_df, cleaning_report = clean_dataset(
        raw_df,
        normalize_columns=normalize_columns,
        trim_strings=trim_strings,
        drop_empty_columns=drop_empty_columns,
    )

    st.subheader("Cleaning report")
    col_a, col_b = st.columns(2)
    col_a.write("Empty columns detected")
    col_a.write(cleaning_report["empty_columns"] or "None")
    col_b.write("Shape change")
    col_b.write(f"{cleaning_report['original_shape']} → {cleaning_report['cleaned_shape']}")

    missing_summary = cleaning_report["missing_values"]
    st.dataframe(missing_summary, use_container_width=True)
    st.download_button(
        "Download cleaned dataset as CSV",
        data=dataframe_to_csv_bytes(cleaned_df),
        file_name="cleaned_educational_data.csv",
        mime="text/csv",
    )

    st.subheader("Key educational indicators")
    indicator_cols = st.columns(5)
    total_records = len(cleaned_df)
    average_attendance = pd.to_numeric(cleaned_df.get("attendance_rate"), errors="coerce").mean() if "attendance_rate" in cleaned_df else None
    average_grade = pd.to_numeric(cleaned_df.get("average_grade"), errors="coerce").mean() if "average_grade" in cleaned_df else None
    average_failed = pd.to_numeric(cleaned_df.get("failed_subjects"), errors="coerce").mean() if "failed_subjects" in cleaned_df else None
    high_risk_share = None
    if "risk_level" in cleaned_df:
        high_risk_share = cleaned_df["risk_level"].astype("string").str.lower().eq("high").mean() * 100

    indicator_cols[0].metric("Records", f"{total_records:,}")
    indicator_cols[1].metric("Avg attendance", format_percent(average_attendance))
    indicator_cols[2].metric("Avg grade", "N/A" if average_grade is None or pd.isna(average_grade) else f"{average_grade:.2f}")
    indicator_cols[3].metric("Avg failed subjects", "N/A" if average_failed is None or pd.isna(average_failed) else f"{average_failed:.2f}")
    indicator_cols[4].metric("High risk", format_percent(high_risk_share))

    st.subheader("Educational analysis")
    course_summary = summarize_by_course(cleaned_df)
    if course_summary.empty:
        st.warning("Course-level analysis requires a `course` column.")
    else:
        chart_cols = st.columns(3)
        with chart_cols[0]:
            st.write("Students by course")
            st.bar_chart(students_by_course_chart_data(cleaned_df))
        with chart_cols[1]:
            st.write("Average attendance by course")
            st.bar_chart(course_metric_chart_data(cleaned_df, "average_attendance"))
        with chart_cols[2]:
            st.write("Risk levels")
            risk_chart = risk_chart_data(cleaned_df)
            if risk_chart.empty:
                st.info("No `risk_level` column found.")
            else:
                st.bar_chart(risk_chart)

        st.write("Course summary")
        st.dataframe(course_summary, use_container_width=True)
        st.download_button(
            "Download course summary as CSV",
            data=dataframe_to_csv_bytes(course_summary),
            file_name="course_summary.csv",
            mime="text/csv",
        )

    st.subheader("Descriptive analysis")
    tabs = st.tabs(["Numeric summary", "Risk distribution", "Categorical distributions"])
    with tabs[0]:
        numeric = numeric_summary(cleaned_df)
        if numeric.empty:
            st.info("No numeric columns found.")
        else:
            st.dataframe(numeric, use_container_width=True)

    with tabs[1]:
        risk = risk_distribution(cleaned_df)
        if risk.empty:
            st.info("No `risk_level` column found.")
        else:
            st.dataframe(risk, use_container_width=True)

    with tabs[2]:
        categorical_columns = cleaned_df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
        if not categorical_columns:
            st.info("No categorical columns found.")
        else:
            selected_column = st.selectbox("Select categorical column", categorical_columns)
            st.dataframe(categorical_distribution(cleaned_df, selected_column), use_container_width=True)

    st.caption("Privacy note: this demo ships with synthetic sample data only. Do not upload sensitive student records.")


if __name__ == "__main__":
    main()

