#!/usr/bin/env python3
"""Quick test of QuantConvictionEngine"""
import warnings
warnings.filterwarnings('ignore')

from quantitative_integration import QuantConvictionEngine

# Test instantiation
engine = QuantConvictionEngine(account_value=390)
print(f'Engine created with account: ${engine.account_value}')

if engine.regime_detector:
    regime = engine.regime_detector.detect_regime()
    print(f'Current regime: {regime.regime} (VIX: {regime.vix_level})')

print('\nQuantConvictionEngine ready for use')
print('\nAvailable methods:')
print('  - analyze(ticker, strategy)')
print('  - calculate_position(analysis_result, pop, max_loss, win_amount)')
print('  - backtest(tickers, start_date, end_date)')
