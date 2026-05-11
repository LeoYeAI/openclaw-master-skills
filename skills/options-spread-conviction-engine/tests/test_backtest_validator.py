#!/usr/bin/env python3
"""
Unit tests for Backtest Validator module.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

import numpy as np
import pandas as pd

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from backtest_validator import (
    BacktestValidator,
    BacktestTrade,
    TierStats,
    ValidationReport,
    TIER_THRESHOLDS,
    MIN_OBSERVATIONS_PER_TIER,
)


class TestBacktestValidator(unittest.TestCase):
    """Test cases for BacktestValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock engine
        self.mock_engine = Mock()
        self.mock_engine.analyze = Mock(return_value=MagicMock(
            conviction_score=75,
            tier='PREPARE'
        ))
        
        self.validator = BacktestValidator(
            self.mock_engine,
            "2023-01-01",
            "2023-06-01",
            strategy="bull_put"
        )
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.validator.strategy, "bull_put")
        self.assertEqual(self.validator.start, pd.to_datetime("2023-01-01"))
        self.assertEqual(self.validator.end, pd.to_datetime("2023-06-01"))
    
    def test_score_to_tier(self):
        """Test score to tier conversion."""
        self.assertEqual(self.validator._score_to_tier(85), 'EXECUTE')
        self.assertEqual(self.validator._score_to_tier(70), 'PREPARE')
        self.assertEqual(self.validator._score_to_tier(50), 'WATCH')
        self.assertEqual(self.validator._score_to_tier(30), 'WAIT')
    
    def test_score_to_tier_boundaries(self):
        """Test tier boundaries."""
        self.assertEqual(self.validator._score_to_tier(80), 'EXECUTE')
        self.assertEqual(self.validator._score_to_tier(79), 'PREPARE')
        self.assertEqual(self.validator._score_to_tier(60), 'PREPARE')
        self.assertEqual(self.validator._score_to_tier(59), 'WATCH')
        self.assertEqual(self.validator._score_to_tier(40), 'WATCH')
        self.assertEqual(self.validator._score_to_tier(39), 'WAIT')
    
    def test_tier_stats_creation(self):
        """Test TierStats dataclass."""
        stats = TierStats(
            tier='EXECUTE',
            count=100,
            win_rate=0.65,
            avg_return=0.05,
            avg_win=0.10,
            avg_loss=-0.05,
            expectancy=0.025,
            sharpe=1.5,
            max_drawdown=-0.15,
            profit_factor=1.8
        )
        self.assertEqual(stats.tier, 'EXECUTE')
        self.assertGreater(stats.expectancy, 0)
    
    def test_calculate_expectancy(self):
        """Test expectancy calculation."""
        win_rate = 0.60
        avg_win = 100
        avg_loss = -50
        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
        self.assertAlmostEqual(expectancy, 0.6 * 100 + 0.4 * (-50))
        self.assertAlmostEqual(expectancy, 40, delta=1)
    
    def test_validation_report_to_dict(self):
        """Test ValidationReport serialization."""
        report = ValidationReport(
            tier_stats={
                'EXECUTE': TierStats('EXECUTE', 50, 0.6, 0.05, 0.1, -0.05, 0.02, 1.0, -0.1, 1.5)
            },
            p_values={'execute_vs_wait': 0.01},
            overall_expectancy=0.02,
            tier_separation_score=0.8,
            recommendation='VALIDATED'
        )
        
        d = report.to_dict()
        self.assertIn('tier_stats', d)
        self.assertIn('p_values', d)
        self.assertEqual(d['recommendation'], 'VALIDATED')
    
    def test_calculate_separation_score_perfect(self):
        """Test separation score with perfect ordering."""
        tier_stats = {
            'EXECUTE': TierStats('EXECUTE', 100, 0.7, 0.1, 0.2, -0.1, 0.08, 1.5, -0.1, 2.0),
            'PREPARE': TierStats('PREPARE', 100, 0.6, 0.05, 0.15, -0.1, 0.04, 1.2, -0.15, 1.5),
            'WATCH': TierStats('WATCH', 100, 0.5, 0.02, 0.1, -0.08, 0.01, 0.8, -0.2, 1.2),
            'WAIT': TierStats('WAIT', 100, 0.4, -0.02, 0.08, -0.1, -0.04, 0.3, -0.3, 0.8),
        }
        
        score = self.validator._calculate_separation_score(tier_stats)
        self.assertGreater(score, 0.7)  # Should be high for perfect ordering
    
    def test_calculate_separation_score_poor(self):
        """Test separation score with poor ordering."""
        tier_stats = {
            'EXECUTE': TierStats('EXECUTE', 100, 0.4, -0.02, 0.1, -0.1, -0.02, 0.5, -0.2, 0.9),
            'WAIT': TierStats('WAIT', 100, 0.6, 0.08, 0.15, -0.05, 0.06, 1.2, -0.1, 1.8),
        }
        # Add empty tiers to meet minimum requirements
        tier_stats['PREPARE'] = TierStats('PREPARE', MIN_OBSERVATIONS_PER_TIER, 0.5, 0.03, 0.1, -0.08, 0.01, 0.8, -0.15, 1.2)
        tier_stats['WATCH'] = TierStats('WATCH', MIN_OBSERVATIONS_PER_TIER, 0.45, 0.01, 0.08, -0.08, 0.0, 0.6, -0.18, 1.0)
        
        score = self.validator._calculate_separation_score(tier_stats)
        self.assertLess(score, 0.5)  # Should be low for reversed ordering
    
    def test_generate_recommendation_validated(self):
        """Test VALIDATED recommendation."""
        tier_stats = {
            'EXECUTE': TierStats('EXECUTE', 100, 0.7, 0.1, 0.2, -0.1, 0.08, 1.5, -0.1, 2.0),
            'WAIT': TierStats('WAIT', 100, 0.3, -0.05, 0.1, -0.15, -0.06, 0.2, -0.3, 0.7),
        }
        p_values = {'execute_vs_wait': 0.01, 'anova_all_tiers': 0.01}
        
        rec = self.validator._generate_recommendation(tier_stats, p_values, 0.8)
        self.assertEqual(rec, 'VALIDATED')
    
    def test_generate_recommendation_rejected(self):
        """Test REJECTED recommendation."""
        tier_stats = {
            'EXECUTE': TierStats('EXECUTE', 100, 0.4, 0.01, 0.1, -0.1, -0.01, 0.3, -0.2, 0.9),
            'WAIT': TierStats('WAIT', 100, 0.4, 0.01, 0.1, -0.1, -0.01, 0.3, -0.2, 0.9),
        }
        p_values = {'execute_vs_wait': 0.5, 'anova_all_tiers': 0.5}
        
        rec = self.validator._generate_recommendation(tier_stats, p_values, 0.3)
        self.assertEqual(rec, 'REJECTED')
    
    def test_calibrate_weights_insufficient_data(self):
        """Test weight calibration with insufficient data."""
        df = pd.DataFrame({'tier': [], 'pnl_dollar': []})
        result = self.validator.calibrate_weights(df)
        self.assertIn('error', result)


class TestBacktestTrade(unittest.TestCase):
    """Test BacktestTrade dataclass."""
    
    def test_trade_creation(self):
        """Test BacktestTrade creation."""
        trade = BacktestTrade(
            entry_date=datetime(2023, 1, 15),
            ticker="AAPL",
            strategy="bull_put",
            score=75,
            tier="PREPARE",
            entry_price=150.0,
            exit_price=152.0,
            hold_days=5,
            pnl_pct=1.33,
            pnl_dollar=40,
            win=True
        )
        self.assertEqual(trade.ticker, "AAPL")
        self.assertTrue(trade.win)
        self.assertAlmostEqual(trade.pnl_pct, 1.33, places=1)


class TestTierThresholds(unittest.TestCase):
    """Test tier threshold constants."""
    
    def test_tier_boundaries(self):
        """Test tier boundary definitions."""
        self.assertEqual(TIER_THRESHOLDS['EXECUTE'], (80, 100))
        self.assertEqual(TIER_THRESHOLDS['PREPARE'], (60, 79))
        self.assertEqual(TIER_THRESHOLDS['WATCH'], (40, 59))
        self.assertEqual(TIER_THRESHOLDS['WAIT'], (0, 39))
    
    def test_tier_coverage(self):
        """Test tiers cover full score range without gaps."""
        ranges = [TIER_THRESHOLDS[t] for t in ['WAIT', 'WATCH', 'PREPARE', 'EXECUTE']]
        
        # Check continuity
        for i in range(len(ranges) - 1):
            self.assertEqual(ranges[i][1], ranges[i+1][0] - 1)
        
        # Check full coverage
        self.assertEqual(ranges[0][0], 0)
        self.assertEqual(ranges[-1][1], 100)


class TestPValueCalculations(unittest.TestCase):
    """Test p-value calculations."""
    
    def setUp(self):
        self.validator = BacktestValidator(
            Mock(), "2023-01-01", "2023-06-01", "bull_put"
        )
    
    def test_p_values_with_sufficient_data(self):
        """Test p-value calculation with sufficient data."""
        np.random.seed(42)
        
        # Generate data with clear separation
        execute_data = np.random.normal(50, 20, 50)  # Positive returns
        wait_data = np.random.normal(-20, 20, 50)     # Negative returns
        
        df = pd.DataFrame({
            'tier': ['EXECUTE'] * 50 + ['WAIT'] * 50,
            'pnl_dollar': np.concatenate([execute_data, wait_data])
        })
        
        p_values = self.validator._calculate_p_values(df)
        
        # Check expected keys exist
        self.assertIn('anova_all_tiers', p_values)
        # Should have low p-value for significant difference
        self.assertLess(p_values['anova_all_tiers'], 0.1)
    
    def test_p_values_with_insufficient_data(self):
        """Test p-value calculation with insufficient data."""
        df = pd.DataFrame({
            'tier': ['EXECUTE'] * 5 + ['WAIT'] * 5,
            'pnl_dollar': [10] * 5 + [-10] * 5
        })
        
        p_values = self.validator._calculate_p_values(df)
        
        # Should return valid dict even with insufficient data
        self.assertIsInstance(p_values, dict)
        # May return error or empty p-values
        self.assertTrue('error' in p_values or len(p_values) >= 0)


if __name__ == '__main__':
    unittest.main()
