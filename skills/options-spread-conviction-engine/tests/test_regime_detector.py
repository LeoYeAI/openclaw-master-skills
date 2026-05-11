#!/usr/bin/env python3
"""
Unit tests for Regime Detector module.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from regime_detector import (
    RegimeDetector,
    RegimeResult,
)


class TestRegimeDetector(unittest.TestCase):
    """Test cases for RegimeDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = RegimeDetector()
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.detector.lookback, 252)
        self.assertEqual(self.detector.vix_ticker, "^VIX")
    
    def test_regimes_defined(self):
        """Test that all regimes are defined."""
        self.assertEqual(len(self.detector.REGIMES), 5)
        self.assertIn('CRISIS', self.detector.REGIMES)
        self.assertIn('EUPHORIA', self.detector.REGIMES)
        self.assertIn('NORMAL', self.detector.REGIMES)
    
    def test_thresholds_defined(self):
        """Test threshold definitions."""
        self.assertEqual(len(self.detector.THRESHOLDS), 5)
        # Crisis is 80-100th percentile
        self.assertEqual(self.detector.THRESHOLDS['CRISIS'], (80.0, 100.0))
        # Euphoria is 0-20th percentile
        self.assertEqual(self.detector.THRESHOLDS['EUPHORIA'], (0.0, 20.0))
    
    def test_get_regime_weights(self):
        """Test regime weights retrieval."""
        for regime in self.detector.REGIMES:
            weights = self.detector.get_regime_weights(regime)
            self.assertIsInstance(weights, dict)
            # Check that weights contains strategy keys
            self.assertGreater(len(weights), 0)
    
    def test_regime_aware_score(self):
        """Test regime-aware score adjustment."""
        base_score = 70
        
        # Test all regimes
        for regime in self.detector.REGIMES:
            adjusted, reason = self.detector.regime_aware_score(
                base_score, regime, 'bull_put'
            )
            self.assertIsInstance(adjusted, (int, float))
            self.assertIsInstance(reason, str)
            # Score should be within bounds
            self.assertGreaterEqual(adjusted, 0)
            self.assertLessEqual(adjusted, 100)
    
    def test_is_favorable_for_strategy(self):
        """Test strategy favorability check."""
        # Iron condor should be favorable in CRISIS
        result = self.detector.is_favorable_for_strategy('CRISIS', 'iron_condor')
        # Returns tuple (is_favorable, reasoning)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], bool)
        self.assertIsInstance(result[1], str)
    
    def test_calculate_percentile(self):
        """Test percentile calculation."""
        # Create mock VIX data
        vix_data = pd.Series([10, 15, 20, 25, 30, 35, 40, 45, 50])
        current = 30
        
        percentile = self.detector.calculate_percentile(current, vix_data)
        self.assertIsInstance(percentile, float)
        self.assertGreaterEqual(percentile, 0)
        self.assertLessEqual(percentile, 100)
    
    def test_calculate_percentile_bounds(self):
        """Test percentile bounds."""
        vix_data = pd.Series([10, 20, 30, 40, 50])
        
        # Min value should be 0th percentile
        min_pct = self.detector.calculate_percentile(10, vix_data)
        self.assertEqual(min_pct, 0.0)
        
        # Max value should be 100th percentile
        max_pct = self.detector.calculate_percentile(50, vix_data)
        self.assertEqual(max_pct, 100.0)


class TestRegimeBoundaries(unittest.TestCase):
    """Test regime classification boundaries."""
    
    def test_crisis_boundary(self):
        """Test crisis threshold."""
        detector = RegimeDetector()
        self.assertEqual(detector.THRESHOLDS['CRISIS'][0], 80.0)
    
    def test_euphoria_boundary(self):
        """Test euphoria threshold."""
        detector = RegimeDetector()
        self.assertEqual(detector.THRESHOLDS['EUPHORIA'][1], 20.0)
    
    def test_normal_boundaries(self):
        """Test normal regime boundaries."""
        detector = RegimeDetector()
        self.assertEqual(detector.THRESHOLDS['NORMAL'], (40.0, 60.0))


class TestRegimeResult(unittest.TestCase):
    """Test RegimeResult dataclass."""
    
    def test_creation(self):
        """Test RegimeResult creation."""
        result = RegimeResult(
            regime='CRISIS',
            confidence=0.85,
            vix_level=35.0,
            percentile=85.0,
            vix_ma20=30.0,
            threshold_low=80.0,
            threshold_high=100.0,
            lookback_days=252,
            regime_metadata={'source': 'test'}
        )
        self.assertEqual(result.regime, 'CRISIS')
        self.assertEqual(result.confidence, 0.85)


if __name__ == '__main__':
    unittest.main()
