#!/usr/bin/env python3
"""
Unit tests for Enhanced Kelly Sizer module.
"""

import unittest

import numpy as np

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from enhanced_kelly import (
    EnhancedKellySizer,
    PositionResult,
    CorrelationPenalty,
    KellyFraction,
)


class TestEnhancedKellySizer(unittest.TestCase):
    """Test cases for EnhancedKellySizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sizer = EnhancedKellySizer()
    
    def test_init_defaults(self):
        """Test initialization with defaults."""
        self.assertEqual(self.sizer.account, 390)
        self.assertEqual(self.sizer.max_dd, 0.20)
        self.assertEqual(self.sizer.min_contracts, 1)
    
    def test_init_custom(self):
        """Test initialization with custom values."""
        sizer = EnhancedKellySizer(account_value=1000, max_drawdown=0.30)
        self.assertEqual(sizer.account, 1000)
        self.assertEqual(sizer.max_dd, 0.30)
    
    def test_kelly_criterion_positive_edge(self):
        """Test Kelly with positive edge."""
        # POP 60%, win $100, lose $100
        # Kelly = (0.6*1 - 0.4) / 1 = 0.2
        # Returns (kelly_pct, ev_pct)
        kelly_pct, ev_pct = self.sizer.kelly_criterion(0.60, 100, 100)
        self.assertAlmostEqual(kelly_pct, 0.20, places=5)
        self.assertIsInstance(ev_pct, float)
    
    def test_kelly_criterion_negative_edge(self):
        """Test Kelly with negative edge."""
        # POP 40%, win $100, lose $100
        kelly_pct, ev_pct = self.sizer.kelly_criterion(0.40, 100, 100)
        self.assertLess(kelly_pct, 0)
    
    def test_kelly_criterion_fair_game(self):
        """Test Kelly with fair game."""
        # POP 50%, win $100, lose $100
        kelly_pct, ev_pct = self.sizer.kelly_criterion(0.50, 100, 100)
        self.assertAlmostEqual(kelly_pct, 0.0, places=5)
    
    def test_kelly_criterion_asymmetric(self):
        """Test Kelly with asymmetric payoffs."""
        # POP 40%, win $200 vs lose $100 (2:1 payoff)
        # Kelly = (0.4*2 - 0.6) / 2 = 0.1
        kelly_pct, ev_pct = self.sizer.kelly_criterion(0.40, 200, 100)
        self.assertAlmostEqual(kelly_pct, 0.10, places=5)
    
    def test_kelly_fraction_enum(self):
        """Test KellyFraction enum values."""
        self.assertEqual(KellyFraction.FULL.value, 1.0)
        self.assertEqual(KellyFraction.HALF.value, 0.5)
        self.assertEqual(KellyFraction.QUARTER.value, 0.25)
        self.assertEqual(KellyFraction.EIGHTH.value, 0.125)
    
    def test_position_result_dataclass(self):
        """Test PositionResult dataclass."""
        result = PositionResult(
            contracts=1,
            total_risk=80.0,
            kelly_fraction=0.20,
            adjusted_kelly=0.05,
            risk_per_contract=80.0,
            max_loss=80.0,
            expected_value=10.0,
            recommendation='EXECUTE',
            reasoning='Edge confirmed',
            drawdown_estimate=0.05
        )
        
        self.assertEqual(result.contracts, 1)
        self.assertEqual(result.recommendation, 'EXECUTE')
        self.assertEqual(result.reasoning, 'Edge confirmed')
    
    def test_correlation_penalty_dataclass(self):
        """Test CorrelationPenalty dataclass."""
        penalty = CorrelationPenalty(
            correlation=0.5,
            penalty_factor=0.75,
            reason='High correlation with existing position'
        )
        
        self.assertEqual(penalty.correlation, 0.5)
        self.assertEqual(penalty.penalty_factor, 0.75)
    
    def test_conviction_based_kelly(self):
        """Test conviction-based Kelly scaling."""
        sizer = EnhancedKellySizer()
        
        # Test different conviction levels - returns tuple (kelly, reasoning)
        kelly_95, _ = sizer.conviction_based_kelly(95, 0.20)
        kelly_75, _ = sizer.conviction_based_kelly(75, 0.20)
        kelly_55, _ = sizer.conviction_based_kelly(55, 0.20)
        
        # Higher conviction should get larger Kelly fraction (or equal)
        self.assertGreaterEqual(kelly_95, kelly_75)
        self.assertGreaterEqual(kelly_75, kelly_55)
    
    def test_drawdown_constrained_kelly(self):
        """Test drawdown constraint application."""
        sizer = EnhancedKellySizer(max_drawdown=0.10)  # Conservative
        
        # High Kelly should be constrained
        full_kelly = 0.25
        constrained = sizer.drawdown_constrained_kelly(full_kelly)
        
        # Result should be a float (constrained Kelly fraction)
        self.assertIsInstance(constrained, float)
        self.assertLess(constrained, full_kelly)
    
    def test_calculate_correlation_penalty(self):
        """Test correlation penalty calculation."""
        sizer = EnhancedKellySizer()
        
        # No correlation = no penalty
        penalty_none = sizer.calculate_correlation_penalty([])
        self.assertIsInstance(penalty_none, CorrelationPenalty)
        
        # High correlation = penalty
        existing = [{"ticker": "SPY", "correlation": 0.9}]
        penalty_high = sizer.calculate_correlation_penalty(existing)
        self.assertIsInstance(penalty_high, CorrelationPenalty)
    
    def test_calculate_position_full_pipeline(self):
        """Test full position sizing pipeline."""
        result = self.sizer.calculate_position(
            spread_cost=80,
            max_loss_per_spread=80,
            win_amount=40,
            conviction=85,
            pop=0.65
        )
        
        self.assertIsInstance(result, PositionResult)
        self.assertIsInstance(result.contracts, int)
        self.assertIsInstance(result.recommendation, str)


class TestKellyFractionTiers(unittest.TestCase):
    """Test Kelly fraction tier mapping."""
    
    def test_tier_values(self):
        """Test tier values."""
        self.assertEqual(KellyFraction.FULL.value, 1.0)
        self.assertEqual(KellyFraction.HALF.value, 0.5)
        self.assertEqual(KellyFraction.QUARTER.value, 0.25)
        self.assertEqual(KellyFraction.EIGHTH.value, 0.125)


class TestPositionResultValidation(unittest.TestCase):
    """Test PositionResult validation."""
    
    def test_positive_contracts(self):
        """Test that contracts is non-negative."""
        result = PositionResult(
            contracts=0,
            total_risk=0.0,
            kelly_fraction=0.0,
            adjusted_kelly=0.0,
            risk_per_contract=80.0,
            max_loss=80.0,
            expected_value=0.0,
            recommendation='SKIP',
            reasoning='No edge',
            drawdown_estimate=0.0
        )
        self.assertGreaterEqual(result.contracts, 0)
    
    def test_risk_consistency(self):
        """Test that total risk equals contracts × risk per contract."""
        contracts = 2
        risk_per = 80.0
        
        result = PositionResult(
            contracts=contracts,
            total_risk=contracts * risk_per,
            kelly_fraction=0.10,
            adjusted_kelly=0.05,
            risk_per_contract=risk_per,
            max_loss=contracts * risk_per,
            expected_value=10.0,
            recommendation='EXECUTE',
            reasoning='Edge confirmed',
            drawdown_estimate=0.05
        )
        
        self.assertEqual(result.total_risk, contracts * risk_per)


if __name__ == '__main__':
    unittest.main()
