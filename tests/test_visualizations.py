# tests/test_visualizations.py
"""
Unit tests for src/visualizations.py.

Run with: pytest tests/test_visualizations.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
matplotlib.use('Agg')  # headless backend, so tests can run without a display
import matplotlib.figure
import numpy as np
import pandas as pd
import pytest

from src.visualizations import (
    plot_histogram_with_distribution,
    create_correlation_heatmap,
    plot_boxplots_by_category,
    create_interactive_scatter,
    plot_qq_comparison,
    dashboard_layout,
)


@pytest.fixture
def sample_df():
    rng = np.random.default_rng(7)
    n = 150
    return pd.DataFrame({
        'age': rng.normal(54, 9, size=n),
        'chol': rng.gamma(25, 10, size=n),
        'thalach': rng.normal(150, 20, size=n),
        'ca': rng.poisson(0.7, size=n).clip(0, 4),
        'target': rng.integers(0, 2, size=n),
    })


# ==================== HISTOGRAM + FITTED DISTRIBUTION ====================
def test_plot_histogram_with_distribution_returns_figure(sample_df):
    fig = plot_histogram_with_distribution(sample_df['chol'], distribution='gamma')
    assert isinstance(fig, matplotlib.figure.Figure)


def test_plot_histogram_with_distribution_poisson(sample_df):
    """Discrete distributions (like the vessel-count column) should also work."""
    fig = plot_histogram_with_distribution(sample_df['ca'], distribution='poisson', column_name='ca')
    assert isinstance(fig, matplotlib.figure.Figure)


def test_plot_histogram_with_distribution_invalid_name_raises(sample_df):
    with pytest.raises(ValueError):
        plot_histogram_with_distribution(sample_df['age'], distribution='not_a_real_distribution')


# ==================== CORRELATION HEATMAP ====================
def test_create_correlation_heatmap_returns_figure(sample_df):
    fig = create_correlation_heatmap(sample_df)
    assert isinstance(fig, matplotlib.figure.Figure)


# ==================== BOXPLOTS BY CATEGORY ====================
def test_plot_boxplots_by_category_returns_figure(sample_df):
    fig = plot_boxplots_by_category(sample_df, numeric_col='thalach', category_col='target')
    assert isinstance(fig, matplotlib.figure.Figure)


# ==================== Q-Q PLOT ====================
def test_plot_qq_comparison_returns_figure(sample_df):
    fig = plot_qq_comparison(sample_df['age'], column_name='age')
    assert isinstance(fig, matplotlib.figure.Figure)


# ==================== INTERACTIVE SCATTER (requires plotly) ====================
def test_create_interactive_scatter_returns_figure(sample_df):
    plotly = pytest.importorskip("plotly")
    import plotly.graph_objects as go

    fig = create_interactive_scatter(sample_df, x_col='age', y_col='chol', color_col='target')
    assert isinstance(fig, go.Figure)


# ==================== DASHBOARD LAYOUT ====================
def test_dashboard_layout_has_required_keys():
    config = dashboard_layout()
    assert 'page_config' in config
    assert 'analysis_types' in config
    assert 'Overview' in config['analysis_types']
    assert 'page_title' in config['page_config']
