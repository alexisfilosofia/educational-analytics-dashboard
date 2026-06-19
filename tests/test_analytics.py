import pandas as pd

from src.analytics import risk_distribution, summarize_by_course
from src.data_cleaning import (
    clean_dataset,
    missing_values_summary,
    normalize_column_names,
    trim_string_values,
)


def test_normalize_column_names_handles_spaces_symbols_and_duplicates():
    df = pd.DataFrame(
        {
            " Student ID ": [1],
            "Average Grade (%)": [8.5],
            "Average Grade %": [8.6],
            "": ["empty"],
        }
    )

    normalized = normalize_column_names(df)

    assert list(normalized.columns) == [
        "student_id",
        "average_grade",
        "average_grade_2",
        "unnamed_column",
    ]


def test_trim_string_values_strips_object_columns():
    df = pd.DataFrame(
        {
            "course": [" Grade 1 ", "Grade 2"],
            "attendance_rate": [91.5, 86.0],
        }
    )

    trimmed = trim_string_values(df)

    assert trimmed.loc[0, "course"] == "Grade 1"
    assert trimmed.loc[1, "course"] == "Grade 2"


def test_missing_values_summary_counts_blank_strings():
    df = pd.DataFrame(
        {
            "student_id": ["S001", "S002", "S003"],
            "risk_level": ["High", "", None],
        }
    )

    summary = missing_values_summary(df)
    risk_missing = summary.loc[summary["column"] == "risk_level", "missing_count"].iloc[0]

    assert risk_missing == 2


def test_clean_dataset_can_drop_empty_columns():
    df = pd.DataFrame(
        {
            " Student ID ": [" S001 ", " S002 "],
            "Empty Column": ["", None],
            "Course": [" Grade 1 ", " Grade 2 "],
        }
    )

    cleaned, report = clean_dataset(df, drop_empty_columns=True)

    assert "empty_column" not in cleaned.columns
    assert report["dropped_empty_columns"] == ["empty_column"]
    assert cleaned.loc[0, "student_id"] == "S001"


def test_summarize_by_course_returns_expected_course_metrics():
    df = pd.DataFrame(
        {
            "student_id": ["S001", "S002", "S003"],
            "course": ["Grade 1", "Grade 1", "Grade 2"],
            "attendance_rate": [90, 80, 70],
            "average_grade": [8, 6, 7],
            "failed_subjects": [0, 2, 1],
            "risk_level": ["Low", "High", "Medium"],
        }
    )

    summary = summarize_by_course(df)
    grade_1 = summary.loc[summary["course"] == "Grade 1"].iloc[0]

    assert grade_1["student_count"] == 2
    assert grade_1["average_attendance"] == 85
    assert grade_1["average_grade"] == 7
    assert grade_1["high_risk_count"] == 1
    assert grade_1["high_risk_share"] == 0.5


def test_risk_distribution_counts_and_percentages():
    df = pd.DataFrame({"risk_level": ["Low", "High", "High", "", None]})

    distribution = risk_distribution(df)
    high = distribution.loc[distribution["risk_level"] == "High"].iloc[0]
    missing = distribution.loc[distribution["risk_level"] == "Missing"].iloc[0]

    assert high["count"] == 2
    assert high["percent"] == 40
    assert missing["count"] == 2
