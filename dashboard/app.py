# dashboard/app.py
"""
Statistics Superstars - Heart Disease Dashboard

Run with:
    streamlit run dashboard/app.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import DataLoader
from src.statistics import StatisticalAnalyzer
from src.visualizations import (
    plot_histogram_with_distribution,
    create_correlation_heatmap,
    plot_boxplots_by_category,
    create_interactive_scatter,
    plot_qq_comparison,
    dashboard_layout,
)

# ==================== PAGE CONFIG ====================
config = dashboard_layout()
st.set_page_config(**config["page_config"])


# ==================== DATA LOADING (cached) ====================
@st.cache_data
def load_data() -> pd.DataFrame:
    loader = DataLoader()
    df = pd.read_csv(loader.processed_dir / "cleaned_data.csv")
    # Re-apply categorical dtype - it doesn't survive a plain CSV round-trip
    for col in df.columns:
        if df[col].nunique() < 10:
            df[col] = df[col].astype('category')
    return df


df = load_data()
analyzer = StatisticalAnalyzer(df)

numeric_cols = [c for c in config["numeric_columns"] if c in df.columns]
categorical_cols = [c for c in config["categorical_columns"] if c in df.columns]

CATEGORY_LABELS = {
    "target": "Heart disease diagnosis (0 = no, 1 = yes)",
    "sex": "Sex (0 = female, 1 = male)",
    "cp": "Chest pain type (0-3)",
    "fbs": "Fasting blood sugar > 120 mg/dl (0/1)",
    "restecg": "Resting ECG result (0-2)",
    "exang": "Exercise-induced angina (0/1)",
    "slope": "Slope of peak exercise ST segment (0-2)",
    "ca": "Number of major vessels colored (0-4)",
    "thal": "Thalassemia result (0-3)",
}

# ==================== SIDEBAR ====================
st.sidebar.title(config["sidebar_title"])
dataset = st.sidebar.selectbox("Select Dataset", config["datasets"])
analysis_type = st.sidebar.radio("Analysis Type", config["analysis_types"])

st.sidebar.markdown("---")
st.sidebar.caption(
    f"{len(df)} patients (after Week 1 cleaning) \u00b7 "
    f"{df['target'].value_counts().get(1, 0)} with heart disease, "
    f"{df['target'].value_counts().get(0, 0)} without"
)

# ==================== MAIN CONTENT ====================
st.title("\U0001FA7A Heart Disease: Data Detective Dashboard")

if analysis_type == "Overview":
    st.header("Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Patients", len(df))
    col2.metric("With heart disease", int(df['target'].value_counts().get(1, 0)))
    col3.metric("Without heart disease", int(df['target'].value_counts().get(0, 0)))
    col4.metric("Variables", df.shape[1])

    st.subheader("First few rows")
    st.dataframe(df.head(10), use_container_width=True)

    st.subheader("Summary statistics")
    st.dataframe(analyzer.all_descriptive_stats().round(3), use_container_width=True)

    st.subheader("Correlation heatmap")
    fig = create_correlation_heatmap(df)
    st.pyplot(fig)

    st.subheader("Explore two variables")
    c1, c2, c3 = st.columns(3)
    with c1:
        x_col = st.selectbox("X axis", numeric_cols, index=numeric_cols.index('age'))
    with c2:
        y_col = st.selectbox("Y axis", numeric_cols, index=numeric_cols.index('thalach'))
    with c3:
        color_col = st.selectbox("Color by", ["(none)"] + categorical_cols, index=(categorical_cols.index('target') + 1))
    color_arg = None if color_col == "(none)" else color_col
    scatter_fig = create_interactive_scatter(df, x_col, y_col, color_arg)
    st.plotly_chart(scatter_fig, use_container_width=True)

elif analysis_type == "Distributions":
    st.header("Distribution Analysis")

    col = st.selectbox("Select a numeric variable", numeric_cols, index=numeric_cols.index('chol'))

    dist_options = ["normal", "exponential", "gamma", "lognormal"]
    if col == "ca":
        dist_options = ["poisson", "binomial"] + dist_options
    dist = st.selectbox("Distribution to fit", dist_options)

    fig = plot_histogram_with_distribution(df[col], distribution=dist, column_name=col)
    st.pyplot(fig)

    st.subheader("Q-Q plot (normality check)")
    qq_fig = plot_qq_comparison(df[col], column_name=col)
    st.pyplot(qq_fig)

    st.subheader("Best-fitting distribution")
    fit_result = analyzer.fit_distribution(col)
    st.write(f"**Best fit:** {fit_result['best_fit']} (p = {fit_result['best_p_value']:.4f})")
    fit_table = pd.DataFrame([
        {"distribution": name, "p_value": r.get("p_value"), "good_fit": r.get("good_fit")}
        for name, r in fit_result["distributions"].items() if "p_value" in r
    ]).sort_values("p_value", ascending=False)
    st.dataframe(fit_table, use_container_width=True)

elif analysis_type == "Hypothesis Testing":
    st.header("Statistical Tests")

    test_kind = st.radio("Test type", ["Independent t-test", "One-way ANOVA", "Chi-square"], horizontal=True)

    if test_kind == "Independent t-test":
        c1, c2 = st.columns(2)
        with c1:
            numeric_col = st.selectbox("Numeric variable", numeric_cols, index=numeric_cols.index('thalach'))
        with c2:
            group_col = st.selectbox("Group by", categorical_cols, index=categorical_cols.index('target'))

        categories = list(df[group_col].dropna().unique())
        if len(categories) >= 2:
            result = analyzer.t_test(numeric_col, group_col, group1=categories[0], group2=categories[1])
            st.metric("p-value", f"{result['p_value']:.4e}")
            st.write(f"Mean ({group_col}={categories[0]}): {result['mean1']:.3f}")
            st.write(f"Mean ({group_col}={categories[1]}): {result['mean2']:.3f}")
            st.write(f"**{result['interpretation']}**")
            fig = plot_boxplots_by_category(df, numeric_col, group_col)
            st.pyplot(fig)
        else:
            st.warning(f"'{group_col}' needs at least 2 categories for this test.")

    elif test_kind == "One-way ANOVA":
        c1, c2 = st.columns(2)
        with c1:
            numeric_col = st.selectbox("Numeric variable", numeric_cols, index=numeric_cols.index('thalach'))
        with c2:
            group_col = st.selectbox("Group by", categorical_cols, index=categorical_cols.index('cp'))

        result = analyzer.anova_test(numeric_col, group_col)
        if 'error' not in result:
            st.metric("p-value", f"{result['p_value']:.4e}")
            st.write(f"F-statistic: {result['f_statistic']:.3f} across {result['groups']} groups")
            st.write(f"**{result['interpretation']}**")
            fig = plot_boxplots_by_category(df, numeric_col, group_col)
            st.pyplot(fig)
        else:
            st.warning(result['error'])

    elif test_kind == "Chi-square":
        c1, c2 = st.columns(2)
        with c1:
            col1_ = st.selectbox("Variable 1", categorical_cols, index=categorical_cols.index('target'))
        with c2:
            remaining = [c for c in categorical_cols if c != col1_]
            col2_ = st.selectbox("Variable 2", remaining, index=remaining.index('sex') if 'sex' in remaining else 0)

        result = analyzer.chi_square_test(col1_, col2_)
        st.metric("p-value", f"{result['p_value']:.4e}")
        st.write(f"chi2 = {result['chi2_statistic']:.3f}, df = {result['degrees_of_freedom']}")
        st.write(f"**{result['interpretation']}**")

        st.subheader("Contingency table")
        st.dataframe(pd.crosstab(df[col1_], df[col2_]), use_container_width=True)

st.markdown("---")
st.caption(
    "Statistics Superstars \u00b7 CSX 2002 Principles of Statistics \u00b7 "
    "Heart Disease dataset (UCI / processed Cleveland data)"
)
