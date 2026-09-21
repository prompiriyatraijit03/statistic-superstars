# Statistics Superstars

## Team Members
- Student A (Prompiriya Traijit) - Project Lead & Data Curator
- Student B (Min Thaw Chan) - Statistical Analyst
- Student C (Aung Kyaw Phyo) - Visualization Specialist

## Project Overview
A multi-week statistical analysis of the **Heart Disease** dataset. Week 1 covers
data inspection, cleaning, descriptive statistics, and visualization. Week 2 builds
on the cleaned data with hypothesis testing, distribution fitting, and confidence
intervals. Week 3 turns that analysis into a reusable plotting module and an
interactive Streamlit dashboard, backed by unit tests - to understand, and let
others explore, which clinical measurements are associated with a heart disease
diagnosis.

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
                07:    Week 3 (visualization module demo)
reports/        Generated tables, figures, and the Week 1, 2 & 3 reports
scripts/        download_data.py - loads the dataset into data/processed
src/            data_loader.py - Week 1 loading/inspection utilities
                statistics.py - Week 2 StatisticalAnalyzer (t-tests, ANOVA,
                chi-square, confidence intervals, bootstrap, distribution fitting)
                visualizations.py - Week 3 plotting functions (histogram +
                fitted distribution, correlation heatmap, boxplots by
                category, interactive scatter, Q-Q plot, dashboard layout)
dashboard/      app.py - Week 3 Streamlit dashboard
tests/          test_statistics.py, test_visualizations.py - unit tests (pytest)
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

# Week 3 (uses the same cleaned data + src/statistics.py from Week 2)
jupyter notebook notebooks/07_visualization_dashboard.ipynb
streamlit run dashboard/app.py
```

Run the test suite any time with:
```bash
pytest tests/ -v
```

**Note on notebook numbering:** the assignment sheets' example code refers to
Week 2's notebooks as `02`-`04` and Week 3's as `01`-`03`, but this repo
already uses `00`-`03` for Week 1. Since all weeks live in the same project,
we numbered them continuously instead - Week 2 is `04`-`06`, Week 3 is `07` -
so the whole sequence still runs in order without overwriting earlier work.

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

**Week 3** (`reports/week3_report.md`): all of the above is now available as an
interactive Streamlit dashboard (`dashboard/app.py`) with three tabs -
Overview, Distributions, and Hypothesis Testing - plus a reusable plotting
module (`src/visualizations.py`) and a unit test suite (`tests/`) covering
both the statistics and visualization code.
