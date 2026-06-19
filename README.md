# Educational Analytics Dashboard

A professional Streamlit demo for educational data cleaning, validation, descriptive analytics, dashboarding, and exportable reporting. The app is designed as a freelance-friendly portfolio project that shows how messy tabular education data can be transformed into clear, reproducible outputs using Python and pandas.

## Features

- Upload CSV or XLSX files.
- Use a built-in synthetic educational dataset when no file is uploaded.
- Preview rows, columns, dataset shape, and column names.
- Normalize column names and trim extra whitespace in text fields.
- Detect empty columns and missing values.
- Download a cleaned CSV dataset.
- Calculate top-level metrics for records, attendance, grades, failed subjects, and high-risk students.
- Summarize educational indicators by course.
- Visualize students by course, average attendance by course, and risk-level distribution.
- Export the course-level summary as CSV.

## Technical Stack

Python · Streamlit · pandas · NumPy · openpyxl · pytest

## Repository Structure

```text
educational-analytics-dashboard/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
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

## Run Tests

```bash
pytest -q
```

## Privacy Note

This demo does not use real student records. The sample dataset in `data/sample_educational_data.csv` is fully synthetic and includes controlled missing values only to demonstrate data-cleaning workflows. It should not be interpreted as institutional, personal, or confidential data.

## Deployment

A future version can be deployed on Streamlit Cloud once the project repository is published. The app is structured so the sample dataset and source modules can run from a clean public environment.

## Portfolio Connection

This project complements my portfolio focus on AI model evaluation, STEM reasoning review, reproducible Python workflows, educational analytics, and public-facing data products.
