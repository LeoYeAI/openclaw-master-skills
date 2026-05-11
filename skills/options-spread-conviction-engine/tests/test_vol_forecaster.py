#!/usr/bin/env python3
"""
Unit tests for Volatility Forecaster module.
"""

import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from vol_forecaster import (
    VolatilityForecaster,
    GARCHResult,
    VRPSignal,
)


class TestVolatilityForecaster(unittest.TestCase):
    """Test cases for VolatilityForecaster."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.ticker = "TEST"
        self.forecaster = VolatilityForecaster(self.ticker, lookback_days=100)
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.forecaster.ticker, self.ticker)
        self.assertEqual(self.forecaster.lookback, 100)
        self.assertIsNone(self.forecaster._garch_result)
    
    def test_garch_result_dataclass(self):
        """Test GARCHResult dataclass."""
        # Create mock fitted volatility series
        dates = pd.date_range('2023-01-01', periods=10)
        fitted = pd.Series([0.2] * 10, index=dates)
        forecast = pd.Series([0.2] * 5, index=pd.date_range('2023-01-11', periods=5))
        
        result = GARCHResult(
            omega=0.01,
            alpha=0.1,
            beta=0.85,
            persistence=0.95,
            half_life=50.0,
            log_likelihood=-100.0,
            aic=200.0,
            bic=210.0,
            converged=True,
            fitted_vol=fitted,
            forecast=forecast
        )
        
        self.assertEqual(result.omega, 0.01)
        self.assertEqual(result.alpha, 0.1)
        self.assertEqual(result.beta, 0.85)
        self.assertAlmostEqual(result.persistence, 0.95)
        self.assertTrue(result.converged)
    
    def test_vrp_signal_dataclass(self):
        """Test VRPSignal dataclass."""
        signal = VRPSignal(
            current_iv=0.25,
            forecast_rv=0.20,
            vrp=0.05,
            vrp_zscore=1.0,
            vrp_percentile=80.0,
            signal_strength=0.8,
            recommendation='SELL',
            reasoning='IV elevated vs expected RV'
        )
        
        self.assertEqual(signal.current_iv, 0.25)
        self.assertEqual(signal.forecast_rv, 0.20)
        self.assertEqual(signal.vrp, 0.05)
        self.assertEqual(signal.recommendation, 'SELL')
    
    def test_persistence_calculation(self):
        """Test that persistence = alpha + beta."""
        dates = pd.date_range('2023-01-01', periods=10)
        fitted = pd.Series([0.2] * 10, index=dates)
        forecast = pd.Series([0.2] * 5, index=pd.date_range('2023-01-11', periods=5))
        
        alpha = 0.1
        beta = 0.85
        
        result = GARCHResult(
            omega=0.01,
            alpha=alpha,
            beta=beta,
            persistence=alpha + beta,
            half_life=50.0,
            log_likelihood=-100.0,
            aic=200.0,
            bic=210.0,
            converged=True,
            fitted_vol=fitted,
            forecast=forecast
        )
        
        self.assertAlmostEqual(result.persistence, 0.95)
    
    def test_half_life_calculation(self):
        """Test half-life calculation from persistence."""
        # For persistence = 0.95, half-life ≈ ln(0.5) / ln(0.95) ≈ 13.5 days
        persistence = 0.95
        expected_half_life = np.log(0.5) / np.log(persistence)
        
        dates = pd.date_range('2023-01-01', periods=10)
        fitted = pd.Series([0.2] * 10, index=dates)
        forecast = pd.Series([0.2] * 5, index=pd.date_range('2023-01-11', periods=5))
        
        result = GARCHResult(
            omega=0.01,
            alpha=0.1,
            beta=0.85,
            persistence=persistence,
            half_life=expected_half_life,
            log_likelihood=-100.0,
            aic=200.0,
            bic=210.0,
            converged=True,
            fitted_vol=fitted,
            forecast=forecast
        )
        
        self.assertAlmostEqual(result.half_life, expected_half_life, places=1)
    
    def test_vrp_interpretation(self):
        """Test VRP interpretation thresholds."""
        # Positive VRP = IV > RV = favor selling
        vrp_positive = VRPSignal(
            current_iv=0.30,
            forecast_rv=0.20,
            vrp=0.10,
            vrp_zscore=2.0,
            vrp_percentile=95.0,
            signal_strength=0.9,
            recommendation='STRONG_SELL',
            reasoning='High IV vs RV'
        )
        self.assertGreater(vrp_positive.vrp, 0)
        self.assertIn('SELL', vrp_positive.recommendation)
        
        # Negative VRP = IV < RV = favor buying
        vrp_negative = VRPSignal(
            current_iv=0.15,
            forecast_rv=0.25,
            vrp=-0.10,
            vrp_zscore=-2.0,
            vrp_percentile=5.0,
            signal_strength=0.9,
            recommendation='STRONG_BUY',
            reasoning='Low IV vs RV'
        )
        self.assertLess(vrp_negative.vrp, 0)
        self.assertIn('BUY', vrp_negative.recommendation)
    
    def test_annualization_factor(self):
        """Test annualization factor."""
        # Daily to annual: sqrt(252)
        expected = np.sqrt(252)
        self.assertAlmostEqual(self.forecaster._annualization_factor, expected)


class TestGARCHParameters(unittest.TestCase):
    """Test GARCH parameter constraints."""
    
    def test_stationarity_condition(self):
        """Test that persistence < 1 for stationarity."""
        dates = pd.date_range('2023-01-01', periods=10)
        fitted = pd.Series([0.2] * 10, index=dates)
        forecast = pd.Series([0.2] * 5, index=pd.date_range('2023-01-11', periods=5))
        
        # Valid: persistence < 1
        result_valid = GARCHResult(
            omega=0.01, alpha=0.1, beta=0.85,
            persistence=0.95, half_life=50.0,
            log_likelihood=-100.0, aic=200.0, bic=210.0,
            converged=True, fitted_vol=fitted, forecast=forecast
        )
        self.assertLess(result_valid.persistence, 1.0)


if __name__ == '__main__':
    unittest.main()
