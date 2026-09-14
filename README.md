# Statistics Superstars

## Team Members
- Student A (Prompiriya Traijit) - Project Lead & Data Curator
- Student B (Min Thaw Chan) - Statistical Analyst
- Student C (Aung Kyaw Phyo) - Visualization Specialist

## Project Overview
A multi-week statistical analysis of the **Heart Disease** dataset. Week 1 covers
data inspection, cleaning, descriptive statistics, and visualization. Week 2 builds
on the cleaned data with hypothesis testing, distribution fitting, and confidence
intervals, to understand which clinical measurements are associated with a heart
disease diagnosis.

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
notebooks/      00-03: Week 1 (inspection, cleaning, statistics, visualizations)
                04-06: Week 2 (hypothesis testing, distribution fitting, confidence intervals)
reports/        Generated tables, figures, and the Week 1 & Week 2 reports
scripts/        download_data.py - loads the dataset into data/processed
src/            data_loader.py - Week 1 loading/inspection utilities
                statistics.py - Week 2 StatisticalAnalyzer (t-tests, ANOVA,
                chi-square, confidence intervals, bootstrap, distribution fitting)
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

# Week 1
jupyter notebook notebooks/00_initial_inspection.ipynb
jupyter notebook notebooks/01_data_cleaning.ipynb
jupyter notebook notebooks/02_statistical_summary.ipynb
jupyter notebook notebooks/03_exploratory_visualizations.ipynb

# Week 2 (uses data/processed/cleaned_data.csv from Week 1)
jupyter notebook notebooks/04_hypothesis_testing.ipynb
jupyter notebook notebooks/05_distribution_fitting.ipynb
jupyter notebook notebooks/06_confidence_intervals.ipynb
```

**Note on notebook numbering:** the Week 2 assignment sheet's example code
refers to its notebooks as `02`-`04`, but this repo already uses `02` and `03`
for Week 1. Since Week 1 and Week 2 live in the same project, we numbered the
Week 2 notebooks `04`-`06` instead, so the whole sequence still runs in order
without overwriting Week 1 work.

## Key Findings

**Week 1** (`reports/week1_report.md`): patients with a heart disease diagnosis
tend to have a **higher maximum heart rate achieved** (`thalach`) and a **lower
ST depression** (`oldpeak`) than patients without a diagnosis, and none of the
continuous clinical variables are normally distributed.

**Week 2** (`reports/week2_report.md`): the `thalach`/`oldpeak` differences by
diagnosis are statistically significant (independent t-tests, p < 0.0001), as is
the association between diagnosis and both sex and exercise-induced angina
(chi-square, p < 0.0001). Maximum heart rate also differs significantly across
chest pain types (ANOVA, p < 0.0001). Cholesterol is well described by a Gamma
distribution; traditional and bootstrap 95% confidence intervals agree closely
for every numeric variable.
