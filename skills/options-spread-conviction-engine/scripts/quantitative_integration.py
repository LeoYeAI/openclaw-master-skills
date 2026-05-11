#!/usr/bin/env python3
"""
===============================================================================
Quantitative Integration — Regime & Vol-Aware Conviction Engine
===============================================================================

Integration module for the Options Spread Conviction Engine that provides:
- Regime-aware scoring
- Volatility forecasting with GARCH
- Enhanced Kelly position sizing
- Walk-forward backtesting

This module re-exports the canonical QuantConvictionEngine from quant_scanner.py
for backwards compatibility.

Usage:
    from quantitative_integration import QuantConvictionEngine
    
    engine = QuantConvictionEngine()
    result = engine.analyze("AAPL", "bull_put", regime_aware=True, vol_aware=True)
    
    # Get position sizing
    sizing = engine.calculate_position(result, pop=0.65, max_loss=80)

===============================================================================
"""

from __future__ import annotations

import warnings
from typing import Optional, Dict, Any, Tuple, List

# Import and extend the canonical QuantConvictionEngine from quant_scanner
# This eliminates duplicate implementations while allowing for extension
from quant_scanner import QuantConvictionEngine as BaseEngine

class QuantConvictionEngine(BaseEngine):
    """
    Extended quantitative conviction engine.
    
    Inherits from quant_scanner.QuantConvictionEngine for unified implementation.
    Additional functionality can be added here as needed.
    """
    pass

# Keep these imports for backwards compatibility
try:
    from regime_detector import RegimeDetector, get_current_regime
    HAS_REGIME = True
except ImportError as e:
    HAS_REGIME = False
    warnings.warn(f"RegimeDetector not available: {e}", UserWarning)

try:
    from vol_forecaster import VolatilityForecaster, VRPSignal
    HAS_VOL = True
except ImportError as e:
    HAS_VOL = False
    warnings.warn(f"VolatilityForecaster not available: {e}", UserWarning)

try:
    from enhanced_kelly import EnhancedKellySizer, PositionResult
    HAS_KELLY = True
except ImportError as e:
    HAS_KELLY = False
    warnings.warn(f"EnhancedKellySizer not available: {e}", UserWarning)

try:
    from backtest_validator import BacktestValidator, ValidationReport
    HAS_BACKTEST = True
except ImportError as e:
    HAS_BACKTEST = False
    warnings.warn(f"BacktestValidator not available: {e}", UserWarning)


# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


# Keep QuantResult for backwards compatibility
from dataclasses import dataclass
from spread_conviction_engine import ConvictionResult

@dataclass
class QuantResult:
    """Extended result with quantitative analysis."""
    base_result: ConvictionResult
    regime: Optional[str] = None
    regime_adjustment: float = 0.0
    regime_reasoning: str = ""
    vrp_signal: Optional[VRPSignal] = None
    vrp_adjustment: float = 0.0
    vrp_reasoning: str = ""
    final_score: float = 0.0
    kelly_sizing: Optional[Dict[str, Any]] = None


def format_quant_report(quant_result: QuantResult, include_kelly: bool = True) -> str:
    """
    Format quantitative analysis report.
    
    Args:
        quant_result: Result from QuantConvictionEngine.analyze().
        include_kelly: Whether to include Kelly sizing in report.
        
    Returns:
        Formatted string report.
    """
    base = quant_result.base_result
    
    lines = [
        "",
        "=" * 70,
        f"  QUANTITATIVE CONVICTION REPORT: {base.ticker}",
        "=" * 70,
        f"  Base Score:       {base.conviction_score:.1f}/100 ({base.tier})",
    ]
    
    if quant_result.regime:
        lines.append(f"  Regime:           {quant_result.regime}")
        lines.append(f"  Regime Adj:       {quant_result.regime_adjustment:+.1f}")
        lines.append(f"    → {quant_result.regime_reasoning}")
    
    if quant_result.vrp_signal:
        lines.append(f"  VRP:              {quant_result.vrp_signal.vrp:+.1%}")
        lines.append(f"  VRP Adj:          {quant_result.vrp_adjustment:+.1f}")
        lines.append(f"    → {quant_result.vrp_reasoning}")
    
    lines.extend([
        "-" * 70,
        f"  FINAL SCORE:      {quant_result.final_score:.1f}/100",
        "=" * 70,
    ])
    
    return "\n".join(lines)


# =============================================================================
# CLI Integration
# =============================================================================

def main():
    """CLI entry point for quantitative analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Quantitative Conviction Engine — Extended analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quantitative_integration.py AAPL --regime-aware
  python quantitative_integration.py SPY --vol-aware
  python quantitative_integration.py TSLA --regime-aware --vol-aware --json
  python quantitative_integration.py --backtest SPY QQQ --start 2022-01-01 --end 2024-01-01
        """,
    )
    parser.add_argument("tickers", nargs="*", help="Ticker symbols")
    parser.add_argument("--strategy", default="bull_put", help="Strategy type")
    parser.add_argument("--regime-aware", action="store_true", help="Apply regime detection")
    parser.add_argument("--vol-aware", action="store_true", help="Apply VRP analysis")
    parser.add_argument("--iv", type=float, help="Implied volatility override")
    parser.add_argument("--pop", type=float, help="Probability of profit for Kelly sizing")
    parser.add_argument("--max-loss", type=float, help="Max loss per contract")
    parser.add_argument("--win-amount", type=float, help="Max win per contract")
    parser.add_argument("--backtest", action="store_true", help="Run backtest")
    parser.add_argument("--start", default="2022-01-01", help="Backtest start date")
    parser.add_argument("--end", default="2024-01-01", help="Backtest end date")
    parser.add_argument("--hold-days", type=int, default=5, help="Hold days for backtest")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    engine = QuantConvictionEngine()
    
    if args.backtest:
        if not args.tickers:
            print("Error: --backtest requires tickers")
            return
        
        print(f"Running backtest for {args.tickers}...")
        report = engine.run_backtest(
            args.tickers,
            args.start,
            args.end,
            args.strategy,
            args.hold_days
        )
        
        if report:
            if args.json:
                import json
                print(json.dumps(report.to_dict(), indent=2))
            else:
                print("\nBacktest Report:")
                print(f"  Overall Expectancy: ${report.overall_expectancy:.0f}")
                print(f"  Tier Separation:    {report.tier_separation_score:.2f}")
                print(f"  Recommendation:     {report.recommendation}")
                print("\n  Tier Statistics:")
                for tier, stats in report.tier_stats.items():
                    if stats.count > 0:
                        print(f"    {tier}: n={stats.count}, win_rate={stats.win_rate:.1%}, "
                              f"exp=${stats.expectancy:.0f}")
        else:
            print("Backtest not available")
    
    else:
        # Run analysis for each ticker
        results = []
        for ticker in args.tickers:
            try:
                result = engine.analyze(
                    ticker,
                    args.strategy,
                    regime_aware=args.regime_aware,
                    vol_aware=args.vol_aware,
                    iv_override=args.iv
                )
                results.append(result)
                
                if not args.json:
                    print(format_quant_report(result))
                    
                    # Show Kelly sizing if POP provided
                    if args.pop and args.max_loss:
                        win = args.win_amount or args.max_loss * 0.5
                        sizing = engine.calculate_position(
                            result, args.pop, args.max_loss, win, ticker=ticker
                        )
                        if sizing:
                            print(f"\n  Position Sizing:")
                            print(f"    Contracts:    {sizing.contracts}")
                            print(f"    Total Risk:   ${sizing.total_risk:.0f}")
                            print(f"    Kelly Frac:   {sizing.kelly_fraction:.2%}")
                            print(f"    Recommendation: {sizing.recommendation}")
                            print("=" * 70)
                
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
        
        if args.json and results:
            import json
            output = []
            for r in results:
                out = {
                    "ticker": r.base_result.ticker,
                    "base_score": r.base_result.conviction_score,
                    "base_tier": r.base_result.tier,
                    "final_score": r.final_score,
                    "regime": r.regime,
                    "regime_adjustment": r.regime_adjustment,
                    "vrp": r.vrp_signal.vrp if r.vrp_signal else None,
                    "vrp_adjustment": r.vrp_adjustment,
                }
                if r.kelly_sizing:
                    out["kelly_sizing"] = r.kelly_sizing
                output.append(out)
            print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
