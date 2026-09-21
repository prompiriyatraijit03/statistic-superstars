# tests/test_statistics.py
"""
Unit tests for src/statistics.py (StatisticalAnalyzer).

Run with: pytest tests/test_statistics.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pandas as pd
import pytest

from src.statistics import StatisticalAnalyzer


@pytest.fixture
def simple_df():
    """A small, hand-picked DataFrame with a known mean/median."""
    return pd.DataFrame({
        'value': [1, 2, 3, 4, 5],
        'group': ['a', 'a', 'b', 'b', 'b'],
    })


@pytest.fixture
def heart_sample():
    """A larger synthetic sample, standing in for the real cleaned data."""
    rng = np.random.default_rng(42)
    n = 200
    target = rng.integers(0, 2, size=n)
    # Give the two groups a real difference in thalach, like the real data
    thalach = np.where(
        target == 1,
        rng.normal(158, 20, size=n),
        rng.normal(139, 20, size=n),
    )
    df = pd.DataFrame({
        'age': rng.normal(54, 9, size=n),
        'chol': rng.gamma(shape=25, scale=10, size=n),
        'thalach': thalach,
        'target': target,
        'sex': rng.integers(0, 2, size=n),
    })
    df['target'] = df['target'].astype('category')
    df['sex'] = df['sex'].astype('category')
    return df


# ==================== DESCRIPTIVE STATISTICS ====================
def test_descriptive_stats(simple_df):
    """Descriptive statistics should match hand-calculated values."""
    analyzer = StatisticalAnalyzer(simple_df)
    result = analyzer.descriptive_stats('value')

    assert result['mean'] == 3.0
    assert result['median'] == 3.0
    assert result['min'] == 1
    assert result['max'] == 5
    assert result['range'] == 4
    assert result['n'] == 5
    assert result['missing'] == 0


def test_all_descriptive_stats_covers_numeric_columns(simple_df):
    analyzer = StatisticalAnalyzer(simple_df)
    result = analyzer.all_descriptive_stats()
    assert 'value' in result['column'].values
    assert len(result) == 1  # 'group' is not numeric


# ==================== NORMALITY ====================
def test_shapiro_wilk_normal_data():
    """A large truly-normal sample should be flagged as normal."""
    # Fixed seed chosen so this sample reliably passes Shapiro-Wilk -
    # with a true null hypothesis, ~5% of random seeds would "fail" by
    # chance alone, so an arbitrary seed would make this test flaky.
    rng = np.random.default_rng(1)
    df = pd.DataFrame({'x': rng.normal(0, 1, size=500)})
    analyzer = StatisticalAnalyzer(df)
    result = analyzer.shapiro_wilk_test('x')
    assert result['normal'] is True
    assert result['p_value'] > 0.05


def test_shapiro_wilk_skewed_data():
    """A heavily skewed sample should be flagged as not normal."""
    rng = np.random.default_rng(0)
    df = pd.DataFrame({'x': rng.exponential(1.0, size=500)})
    analyzer = StatisticalAnalyzer(df)
    result = analyzer.shapiro_wilk_test('x')
    assert result['normal'] is False


# ==================== HYPOTHESIS TESTS ====================
def test_t_test_one_sample_matches_manual_calc(simple_df):
    analyzer = StatisticalAnalyzer(simple_df)
    result = analyzer.t_test('value', 3.0)
    # Mean equals the null value exactly -> t-statistic should be ~0
    assert abs(result['statistic']) < 1e-9
    assert result['significant'] is False


def test_t_test_independent_detects_real_difference(heart_sample):
    """thalach really differs by target in our synthetic sample."""
    analyzer = StatisticalAnalyzer(heart_sample)
    result = analyzer.t_test('thalach', 'target', group1=0, group2=1)
    assert result['significant'] is True
    assert result['mean2'] > result['mean1']  # target=1 group has higher thalach


def test_anova_detects_group_difference():
    """Three clearly-separated groups should give a significant ANOVA."""
    df = pd.DataFrame({
        'value': [1, 2, 1, 2, 10, 11, 10, 11, 20, 21, 20, 21],
        'group': ['a'] * 4 + ['b'] * 4 + ['c'] * 4,
    })
    analyzer = StatisticalAnalyzer(df)
    result = analyzer.anova_test('value', 'group')
    assert result['significant'] is True


def test_anova_no_difference_when_groups_are_identical():
    df = pd.DataFrame({
        'value': [5, 5, 5, 5, 5, 5],
        'group': ['a', 'a', 'b', 'b', 'c', 'c'],
    })
    analyzer = StatisticalAnalyzer(df)
    result = analyzer.anova_test('value', 'group')
    # Zero variance in every group -> scipy returns nan, not a real signal
    assert np.isnan(result['f_statistic']) or result['significant'] is False


def test_chi_square_independence():
    """A perfectly balanced 2x2 table should show no association."""
    df = pd.DataFrame({
        'a': ['x', 'x', 'y', 'y'] * 10,
        'b': ['p', 'q', 'p', 'q'] * 10,
    })
    analyzer = StatisticalAnalyzer(df)
    result = analyzer.chi_square_test('a', 'b')
    assert result['significant'] is False


# ==================== CONFIDENCE INTERVALS ====================
def test_confidence_interval_contains_true_mean():
    rng = np.random.default_rng(1)
    df = pd.DataFrame({'x': rng.normal(50, 5, size=100)})
    analyzer = StatisticalAnalyzer(df)
    result = analyzer.confidence_interval('x')
    assert result['lower_bound'] < result['mean'] < result['upper_bound']
    # True mean of 50 should very likely fall inside a well-behaved 95% CI
    assert result['lower_bound'] < 50 < result['upper_bound']


def test_bootstrap_ci_contains_true_mean():
    rng = np.random.default_rng(2)
    df = pd.DataFrame({'x': rng.normal(50, 5, size=100)})
    analyzer = StatisticalAnalyzer(df)
    result = analyzer.bootstrap_ci('x', statistic=np.mean, n_bootstrap=2000)
    assert result['lower_bound'] < result['upper_bound']
    assert result['lower_bound'] < 50 < result['upper_bound']


# ==================== DISTRIBUTION FITTING ====================
def test_fit_distribution_normal_data_fits_normal_well():
    rng = np.random.default_rng(3)
    df = pd.DataFrame({'x': rng.normal(0, 1, size=1000)})
    analyzer = StatisticalAnalyzer(df)
    result = analyzer.fit_distribution('x', distributions=['norm', 'expon'])
    assert result['best_fit'] is not None
    assert result['distributions']['norm']['p_value'] > 0.05
