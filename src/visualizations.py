# src/visualizations.py
"""
Reusable plotting functions for the Statistics Superstars project.

Matplotlib/Seaborn functions return a `matplotlib.figure.Figure` and never
call `plt.show()`, so they work equally well in a Jupyter notebook
(`fig`), a script (`fig.savefig(...)`), or the Streamlit dashboard
(`st.pyplot(fig)`).

The one interactive function, `create_interactive_scatter`, returns a
Plotly `go.Figure`, for use with `st.plotly_chart(fig)` or `fig.show()`.
"""
from typing import List, Optional
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.figure
import seaborn as sns

try:
    import plotly.express as px
    import plotly.graph_objects as go
    _PLOTLY_AVAILABLE = True
except ImportError:  # plotly is an optional/heavier dependency
    px = None
    go = None
    _PLOTLY_AVAILABLE = False

sns.set_style("whitegrid")

# Distributions supported by plot_histogram_with_distribution /
# fit_distribution-style overlays. 'binomial' and 'poisson' are discrete,
# the rest are continuous.
_CONTINUOUS_DISTS = {
    'normal': stats.norm,
    'exponential': stats.expon,
    'gamma': stats.gamma,
    'lognormal': stats.lognorm,
}
_DISCRETE_DISTS = {'binomial', 'poisson'}


def plot_histogram_with_distribution(
    data: List[float],
    distribution: str = 'normal',
    column_name: str = 'value',
    n_trials: Optional[int] = None,
) -> matplotlib.figure.Figure:
    """
    Create a histogram with a fitted distribution overlay.

    Args:
        data: Numeric values to plot.
        distribution: One of 'normal', 'exponential', 'gamma', 'lognormal'
            (continuous, fit by maximum likelihood), or 'binomial' /
            'poisson' (discrete, fit by matching the sample mean).
        column_name: Label used for the x-axis / title.
        n_trials: Only used for 'binomial' - the number of trials n
            (e.g. for a 0-4 count column, n_trials=4). Defaults to the
            observed maximum value if not given.

    Returns:
        A matplotlib Figure with the histogram and fitted curve.
    """
    arr = np.asarray(pd.Series(data).dropna(), dtype=float)
    fig, ax = plt.subplots(figsize=(9, 5.5))

    if distribution in _CONTINUOUS_DISTS:
        ax.hist(arr, bins=20, density=True, alpha=0.6, color='#A8D0E6',
                edgecolor='white', label='Data')
        dist = _CONTINUOUS_DISTS[distribution]
        params = dist.fit(arr)
        x = np.linspace(arr.min(), arr.max(), 200)
        pdf = dist.pdf(x, *params)
        ks_stat, p_value = stats.kstest(arr, dist.name, args=params)
        ax.plot(x, pdf, color='#E4572E', linewidth=2,
                label=f'{distribution.title()} fit (p={p_value:.3f})')

    elif distribution in _DISCRETE_DISTS:
        # Discrete columns (like a count of 0-4 vessels) - show a bar
        # chart of observed frequencies vs. the fitted PMF.
        values, counts = np.unique(arr.astype(int), return_counts=True)
        observed = counts / counts.sum()
        ax.bar(values, observed, width=0.4, alpha=0.6, color='#A8D0E6',
               edgecolor='white', label='Data', align='edge')

        mean = arr.mean()
        if distribution == 'poisson':
            fitted = stats.poisson(mu=mean)
            label = f'Poisson fit (\u03bb={mean:.2f})'
        else:  # binomial
            n = n_trials if n_trials is not None else int(arr.max())
            p = mean / n if n > 0 else 0
            fitted = stats.binom(n=n, p=p)
            label = f'Binomial fit (n={n}, p={p:.2f})'

        x = np.arange(values.min(), values.max() + 1)
        pmf = fitted.pmf(x)
        ax.bar(x, pmf, width=0.4, alpha=0.8, color='#E4572E',
               edgecolor='white', label=label, align='edge')
    else:
        raise ValueError(f"Unsupported distribution: {distribution}")

    ax.set_title(f'Distribution of {column_name}')
    ax.set_xlabel(column_name)
    ax.set_ylabel('Density' if distribution in _CONTINUOUS_DISTS else 'Proportion')
    ax.legend()
    fig.tight_layout()
    return fig


def create_correlation_heatmap(df: pd.DataFrame) -> matplotlib.figure.Figure:
    """
    Generate a correlation matrix heatmap for all numeric columns.

    Args:
        df: DataFrame to analyze.

    Returns:
        A matplotlib Figure containing the heatmap.
    """
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    corr = df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(9, 7.5))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, square=True, linewidths=0.5, ax=ax)
    ax.set_title('Correlation Heatmap')
    fig.tight_layout()
    return fig


def plot_boxplots_by_category(
    df: pd.DataFrame,
    numeric_col: str,
    category_col: str,
) -> matplotlib.figure.Figure:
    """
    Create a boxplot of a numeric column, grouped by a categorical column.

    Args:
        df: DataFrame to analyze.
        numeric_col: Numeric column to summarize.
        category_col: Categorical column to group by.

    Returns:
        A matplotlib Figure with the boxplot.
    """
    fig, ax = plt.subplots(figsize=(8, 5.5))
    sns.boxplot(data=df, x=category_col, y=numeric_col, ax=ax)
    ax.set_title(f'{numeric_col} by {category_col}')
    ax.set_xlabel(category_col)
    ax.set_ylabel(numeric_col)
    fig.tight_layout()
    return fig


def create_interactive_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: Optional[str] = None,
):
    """
    Create an interactive scatter plot with Plotly.

    Args:
        df: DataFrame to analyze.
        x_col: Column for the x-axis.
        y_col: Column for the y-axis.
        color_col: Optional column to color points by.

    Returns:
        A plotly.graph_objects.Figure.
    """
    if not _PLOTLY_AVAILABLE:
        raise ImportError(
            "plotly is required for create_interactive_scatter(). "
            "Install it with: pip install plotly"
        )

    fig = px.scatter(
        df, x=x_col, y=y_col, color=color_col,
        title=f'{y_col} vs {x_col}' + (f' by {color_col}' if color_col else ''),
        opacity=0.75,
    )
    fig.update_layout(template='plotly_white')
    return fig


def plot_qq_comparison(
    data: List[float],
    distribution: str = 'norm',
    column_name: str = 'value',
) -> matplotlib.figure.Figure:
    """
    Create a Q-Q plot to visually check normality (or fit to another
    distribution).

    Args:
        data: Numeric values to plot.
        distribution: A scipy.stats distribution name (default 'norm').
        column_name: Label used for the title.

    Returns:
        A matplotlib Figure with the Q-Q plot.
    """
    arr = np.asarray(pd.Series(data).dropna(), dtype=float)
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    stats.probplot(arr, dist=distribution, plot=ax)
    ax.set_title(f'Q-Q Plot: {column_name} vs {distribution}')

    if len(arr) > 3 and distribution == 'norm':
        _, p_value = stats.shapiro(arr)
        ax.text(0.05, 0.95, f'Shapiro-Wilk p = {p_value:.3f}',
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    fig.tight_layout()
    return fig


def dashboard_layout() -> dict:
    """
    Streamlit dashboard layout configuration.

    This returns plain data (page config + menu options) rather than
    calling any Streamlit functions directly, so it can be unit tested
    without a Streamlit runtime. `dashboard/app.py` unpacks this dict
    into `st.set_page_config(**config["page_config"])` and uses the
    option lists to build the sidebar.
    """
    return {
        "page_config": {
            "page_title": "Statistics Superstars - Heart Disease Dashboard",
            "page_icon": "\U0001FA7A",  # stethoscope emoji
            "layout": "wide",
        },
        "sidebar_title": "\U0001F4CA Data Detective: Heart Disease",
        "datasets": ["Heart Disease"],
        "analysis_types": ["Overview", "Distributions", "Hypothesis Testing"],
        "numeric_columns": [
            "age", "trestbps", "chol", "thalach", "oldpeak",
            "hr_reserve", "chol_age_ratio",
        ],
        "categorical_columns": [
            "target", "sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal",
        ],
    }
