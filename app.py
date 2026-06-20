"""Streamlit educational analytics dashboard demo."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.analytics import (
    categorical_distribution,
    data_quality_report,
    dataset_overview,
    educational_metrics,
    filter_dataset,
    numeric_summary,
    recommended_columns_status,
    risk_distribution,
    risk_summary_by_course,
    summarize_by_course,
)
from src.data_cleaning import clean_dataset
from src.visualization import (
    course_metric_chart_data,
    failed_subjects_by_risk_chart_data,
    risk_chart_data,
    students_by_course_chart_data,
)

SAMPLE_DATA_PATH = Path(__file__).parent / "data" / "sample_educational_data.csv"
FILTER_COLUMNS = ["year", "course", "risk_level", "gender_group", "neighborhood_group"]


@st.cache_data
def load_sample_data() -> pd.DataFrame:
    return pd.read_csv(SAMPLE_DATA_PATH)


def load_uploaded_data(uploaded_file: Any) -> pd.DataFrame:
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


def format_decimal(value: float | int | None, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}"


def apply_visual_polish() -> None:
    """Add a small CSS layer for card-like metrics without overriding the theme."""
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #d8d3c7;
            border-radius: 0.75rem;
            padding: 1rem;
            box-shadow: 0 14px 30px rgba(23, 74, 124, 0.08);
        }
        div[data-testid="stMetricLabel"] p {
            color: #607080;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .stDownloadButton button {
            border-radius: 999px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def filter_options(series: pd.Series) -> list[str]:
    values = series.fillna("Missing").astype(str).str.strip().replace("", "Missing")
    return ["All"] + sorted(values.dropna().unique().tolist())


def build_sidebar_filters(df: pd.DataFrame) -> dict[str, list[str]]:
    filters: dict[str, list[str]] = {}
    with st.sidebar:
        st.header("Filters")
        available_filter_columns = [column for column in FILTER_COLUMNS if column in df.columns]
        if not available_filter_columns:
            st.caption("No standard filter columns found in this dataset.")
            return filters

        for column in available_filter_columns:
            label = column.replace("_", " ").title()
            filters[column] = st.multiselect(label, filter_options(df[column]), default=["All"], key=f"filter_{column}")

    return filters


def show_column_readiness(df: pd.DataFrame) -> None:
    status = recommended_columns_status(df)
    found = status["found"]
    missing = status["missing"]

    st.subheader("Column readiness")
    col_a, col_b = st.columns(2)
    col_a.success(f"Recommended columns found: {len(found)}")
    if found:
        col_a.write(", ".join(found))
    if missing:
        col_b.warning(f"Missing recommended columns: {len(missing)}")
        col_b.write(", ".join(missing))
    else:
        col_b.success("All recommended columns are available.")


def main() -> None:
    st.set_page_config(
        page_title="Educational Analytics Dashboard",
        layout="wide",
    )
    apply_visual_polish()

    st.title("Educational Analytics Dashboard")
    st.markdown(
        "Upload a CSV or Excel file, clean educational data, generate course-level summaries, "
        "visualize key indicators, and export cleaned results."
    )
    st.info("This demo uses synthetic data by default. No real student data is included.")

    with st.sidebar:
        st.header("Data source")
        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
        use_sample = st.checkbox("Use synthetic sample dataset", value=True, disabled=uploaded_file is not None)

        st.header("Cleaning options")
        normalize_columns = st.checkbox("Normalize column names", value=True)
        trim_strings = st.checkbox("Trim whitespace in text values", value=True)
        drop_empty_columns = st.checkbox("Drop empty columns", value=False)

    try:
        if uploaded_file is not None:
            raw_df = load_uploaded_data(uploaded_file)
            source_label = uploaded_file.name
        elif use_sample:
            raw_df = load_sample_data()
            source_label = "data/sample_educational_data.csv"
        else:
            st.info("Upload a CSV/XLSX file or enable the synthetic sample dataset to begin.")
            return
    except Exception as exc:  # pragma: no cover - defensive Streamlit UI guard
        st.error(f"Could not load the selected file: {exc}")
        return

    cleaned_df, cleaning_report = clean_dataset(
        raw_df,
        normalize_columns=normalize_columns,
        trim_strings=trim_strings,
        drop_empty_columns=drop_empty_columns,
    )

    filters = build_sidebar_filters(cleaned_df)
    filtered_df = filter_dataset(cleaned_df, filters)
    with st.sidebar:
        st.metric("Filtered records", f"{len(filtered_df):,}")
        st.caption(f"From {len(cleaned_df):,} clean records.")

    st.subheader("Dataset preview")
    st.write(f"Source: `{source_label}`")
    overview = dataset_overview(raw_df)
    metric_cols = st.columns(3)
    metric_cols[0].metric("Rows", f"{overview['rows']:,}")
    metric_cols[1].metric("Columns", f"{overview['columns']:,}")
    metric_cols[2].metric("Missing cells", f"{overview['missing_cells']:,}")

    st.dataframe(raw_df.head(10), width="stretch")
    with st.expander("Column names"):
        st.write(list(raw_df.columns))

    st.subheader("Cleaning report")
    col_a, col_b = st.columns(2)
    col_a.write("Empty columns detected")
    col_a.write(cleaning_report["empty_columns"] or "None")
    col_b.write("Shape change")
    col_b.write(f"{cleaning_report['original_shape']} -> {cleaning_report['cleaned_shape']}")

    st.dataframe(cleaning_report["missing_values"], width="stretch")
    st.download_button(
        "Download cleaned dataset as CSV",
        data=dataframe_to_csv_bytes(cleaned_df),
        file_name="cleaned_educational_data.csv",
        mime="text/csv",
        key="download_cleaned_dataset",
    )

    show_column_readiness(cleaned_df)

    st.subheader("Filtered dataset")
    st.write(f"{len(filtered_df):,} records selected after filters.")
    st.dataframe(filtered_df.head(20), width="stretch")

    st.subheader("Data Quality Report")
    quality_report = data_quality_report(filtered_df)
    quality_cols = st.columns(4)
    quality_cols[0].metric("Rows", f"{len(filtered_df):,}")
    quality_cols[1].metric("Columns", f"{len(filtered_df.columns):,}")
    duplicate_rows = quality_report.loc[quality_report["check"] == "duplicate_student_id", "value"]
    quality_cols[2].metric("Duplicate IDs", f"{int(duplicate_rows.iloc[0]):,}" if not duplicate_rows.empty else "N/A")
    empty_columns = quality_report.loc[quality_report["check"] == "empty_columns", "value"]
    quality_cols[3].metric("Empty columns", f"{int(empty_columns.iloc[0]):,}" if not empty_columns.empty else "0")
    st.dataframe(quality_report, width="stretch")
    st.download_button(
        "Download data quality report as CSV",
        data=dataframe_to_csv_bytes(quality_report),
        file_name="data_quality_report.csv",
        mime="text/csv",
        key="download_quality_report",
    )

    st.subheader("Key educational indicators")
    metrics = educational_metrics(filtered_df)
    indicator_cols = st.columns(6)
    indicator_cols[0].metric("Total records", f"{metrics['total_records']:,}")
    indicator_cols[1].metric("Average attendance", format_percent(metrics["average_attendance"]))
    indicator_cols[2].metric("Average grade", format_decimal(metrics["average_grade"]))
    indicator_cols[3].metric("Average failed subjects", format_decimal(metrics["average_failed_subjects"]))
    indicator_cols[4].metric("High-risk students", f"{metrics['high_risk_count']:,}" if metrics["high_risk_count"] is not None else "N/A")
    indicator_cols[5].metric("High-risk percentage", format_percent(metrics["high_risk_percentage"]))
    if "risk_level" not in filtered_df.columns:
        st.caption("No `risk_level` column found; high-risk metrics are unavailable for this dataset.")

    st.subheader("Educational analysis")
    course_summary = summarize_by_course(filtered_df)
    risk_course_summary = risk_summary_by_course(filtered_df)
    if course_summary.empty:
        st.warning("Course-level analysis requires a `course` column.")
    else:
        st.write("Course summary")
        st.dataframe(course_summary, width="stretch")

    st.subheader("Visualizations")
    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.write("Students by course")
        students_chart = students_by_course_chart_data(filtered_df)
        if students_chart.empty:
            st.info("Requires a `course` column.")
        else:
            st.bar_chart(students_chart)

        st.write("Risk level distribution")
        risk_chart = risk_chart_data(filtered_df)
        if risk_chart.empty:
            st.info("Requires a `risk_level` column.")
        else:
            st.bar_chart(risk_chart)

        st.write("Average grade by course")
        grade_chart = course_metric_chart_data(filtered_df, "average_grade")
        if grade_chart.empty:
            st.info("Requires `course` and `average_grade` columns.")
        else:
            st.bar_chart(grade_chart)

    with chart_cols[1]:
        st.write("Average attendance by course")
        attendance_chart = course_metric_chart_data(filtered_df, "average_attendance")
        if attendance_chart.empty:
            st.info("Requires `course` and `attendance_rate` columns.")
        else:
            st.bar_chart(attendance_chart)

        st.write("Failed subjects by risk level")
        failed_by_risk_chart = failed_subjects_by_risk_chart_data(filtered_df)
        if failed_by_risk_chart.empty:
            st.info("Requires `risk_level` and `failed_subjects` columns.")
        else:
            st.bar_chart(failed_by_risk_chart)

    st.subheader("Descriptive analysis")
    tabs = st.tabs(["Numeric summary", "Risk distribution", "Categorical distributions"])
    with tabs[0]:
        numeric = numeric_summary(filtered_df)
        if numeric.empty:
            st.info("No numeric columns found.")
        else:
            st.dataframe(numeric, width="stretch")

    with tabs[1]:
        risk = risk_distribution(filtered_df)
        if risk.empty:
            st.info("No `risk_level` column found.")
        else:
            st.dataframe(risk, width="stretch")

    with tabs[2]:
        categorical_columns = filtered_df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
        if not categorical_columns:
            st.info("No categorical columns found.")
        else:
            selected_column = st.selectbox("Select categorical column", categorical_columns)
            st.dataframe(categorical_distribution(filtered_df, selected_column), width="stretch")

    st.subheader("Exports")
    export_cols = st.columns(2)
    with export_cols[0]:
        st.download_button(
            "Download filtered dataset as CSV",
            data=dataframe_to_csv_bytes(filtered_df),
            file_name="filtered_educational_data.csv",
            mime="text/csv",
            key="download_filtered_dataset",
        )
        if not course_summary.empty:
            st.download_button(
                "Download course summary as CSV",
                data=dataframe_to_csv_bytes(course_summary),
                file_name="course_summary.csv",
                mime="text/csv",
                key="download_course_summary",
            )
    with export_cols[1]:
        st.download_button(
            "Download data quality report as CSV",
            data=dataframe_to_csv_bytes(quality_report),
            file_name="data_quality_report.csv",
            mime="text/csv",
            key="download_quality_report_exports",
        )
        if not risk_course_summary.empty:
            st.download_button(
                "Download risk summary by course as CSV",
                data=dataframe_to_csv_bytes(risk_course_summary),
                file_name="risk_summary_by_course.csv",
                mime="text/csv",
                key="download_risk_summary_by_course",
            )

    st.caption("Privacy note: this demo ships with synthetic sample data only. Do not upload sensitive student records.")
    return None


if __name__ == "__main__":
    main()
