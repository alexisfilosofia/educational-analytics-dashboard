# Educational Analytics Dashboard

A professional Streamlit demo for educational data cleaning, validation, descriptive analytics, dashboarding, filtering, and exportable reporting. The app is designed as a freelance-friendly portfolio project that shows how messy tabular education data can be transformed into clear, reproducible outputs using Python and pandas.

## Live demo

Streamlit app: https://educational-analytics-dashboard-h7upkza2ggpfqv25u4uskv.streamlit.app/

## Features

- Upload CSV or XLSX files.
- Use a built-in synthetic educational dataset when no file is uploaded.
- Work in a light, clean Streamlit theme aligned with the portfolio palette.
- Preview rows, columns, dataset shape, and column names.
- Normalize column names and trim extra whitespace in text fields.
- Detect empty columns and missing values.
- Filter clean data by year, course, risk level, gender group, and neighborhood group when those columns exist.
- Review recommended educational analytics columns found or missing.
- Generate a downloadable Data Quality Report with missing values, empty columns, duplicate IDs, and out-of-range checks.
- Download a cleaned CSV dataset.
- Download a filtered CSV dataset.
- Calculate top-level metrics for records, attendance, grades, failed subjects, high-risk student count, and high-risk percentage.
- Summarize educational indicators by course.
- Visualize students by course, average attendance by course, average grade by course, failed subjects by risk level, and risk-level distribution.
- Export the course-level summary as CSV.
- Export risk summary by course as CSV when risk and course columns exist.

## Technical Stack

Python · Streamlit · pandas · NumPy · openpyxl · pytest

## Repository Structure

```text
educational-analytics-dashboard/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml
├── data/
│   └── sample_educational_data.csv
├── src/
│   ├── __init__.py
│   ├── data_cleaning.py
│   ├── analytics.py
│   └── visualization.py
└── tests/
    └── test_analytics.py
```

## Run Locally

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the Streamlit app:

```bash
streamlit run app.py
```

The local app uses the same light Streamlit theme configured in `.streamlit/config.toml`.

## Run Tests

```bash
pytest -q
```

Optional compile check:

```bash
python -m compileall .
```

## Privacy Note

This demo does not use real student records. The sample dataset in `data/sample_educational_data.csv` is fully synthetic and includes controlled missing values only to demonstrate data-cleaning workflows. It should not be interpreted as institutional, personal, or confidential data.

## Deployment

The app is deployed on Streamlit Cloud:

https://educational-analytics-dashboard-h7upkza2ggpfqv25u4uskv.streamlit.app/

## Portfolio Connection

This project complements my portfolio focus on AI model evaluation, STEM reasoning review, reproducible Python workflows, educational analytics, and public-facing data products.
