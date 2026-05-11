#!/usr/bin/env python3
"""
Test runner for Options Spread Conviction Engine quantitative modules.
"""

import unittest
import sys
import os

# Add paths
scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
tests_dir = os.path.dirname(__file__)
sys.path.insert(0, scripts_dir)
sys.path.insert(0, tests_dir)

# Import test modules
import test_regime_detector
import test_vol_forecaster
import test_enhanced_kelly
import test_backtest_validator


def run_tests():
    """Run all unit tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test modules
    suite.addTests(loader.loadTestsFromModule(test_regime_detector))
    suite.addTests(loader.loadTestsFromModule(test_vol_forecaster))
    suite.addTests(loader.loadTestsFromModule(test_enhanced_kelly))
    suite.addTests(loader.loadTestsFromModule(test_backtest_validator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
