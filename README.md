# Statistics Superstars

## Team Members
- Student A (Prompiriya Traijit) - Project Lead & Data Curator
- Student B (Min Thaw Chan) - Statistical Analyst
- Student C (Aung Kyaw Phyo) - Visualization Specialist

## Project Overview
An exploratory statistical analysis of the **Heart Disease** dataset. The project
walks through data inspection, cleaning, descriptive/inferential statistics, and
visualization to understand which clinical measurements are associated with a
heart disease diagnosis.

## Dataset
**Heart Disease Dataset** (processed Cleveland data), sourced from the
[UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/45/heart+disease)
and distributed on Kaggle as `heart.csv`. It contains 1,025 patient records (a
repeated version of the original 303-instance Cleveland set - see the
Data Quality notes in `reports/week1_report.md`) across 14 clinical variables,
including age, sex, chest pain type, resting blood pressure, cholesterol, and a
binary `target` column indicating the presence of heart disease.

See `reports/data_dictionary.csv` for a full column-by-column description.

## Project Structure
```
data/
  raw/          Original heart.csv
  processed/    raw_data.csv (loaded) and cleaned_data.csv (post-cleaning)
notebooks/      00-03: inspection, cleaning, statistics, visualizations
reports/        Generated tables, figures, and the Week 1 report
scripts/        download_data.py - loads the dataset into data/processed
src/            data_loader.py - shared loading/inspection utilities
```

## Setup Instructions
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Analysis
```bash
python scripts/download_data.py      # loads heart.csv -> data/processed/raw_data.csv
jupyter notebook notebooks/00_initial_inspection.ipynb
jupyter notebook notebooks/01_data_cleaning.ipynb
jupyter notebook notebooks/02_statistical_summary.ipynb
jupyter notebook notebooks/03_exploratory_visualizations.ipynb
```

## Key Findings
See `reports/week1_report.md` for the full write-up. In short: patients with a
heart disease diagnosis in this dataset tend to have a **higher maximum heart
rate achieved** (`thalach`) and a **lower ST depression** (`oldpeak`) than
patients without a diagnosis, and none of the continuous clinical variables are
normally distributed - so Week 2 analysis will lean on non-parametric tests.
