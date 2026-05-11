#!/usr/bin/env python3
"""
===============================================================================
Options Market Scanner — Multi-Strategy EXECUTE Play Finder
===============================================================================

Scans a stock universe (S&P 500, Nasdaq 100, or custom list) for high-conviction
options spread opportunities across all 7 supported strategies:

  - bull_put, bear_call (credit spreads)
  - bull_call, bear_put (debit spreads)  
  - iron_condor, butterfly, calendar (multi-leg strategies)

Filters for EXECUTE tier (conviction >= 80) and runs position sizing
to ensure trades fit within account guardrails ($390 account default).

Features:
  - Rate limiting to avoid Yahoo Finance API bans
  - Configurable batch size and delay
  - Parallel processing support (with rate limiting)
  - JSON or formatted table output

Usage:
  python3 market_scanner.py --universe sp500
  python3 market_scanner.py --universe ndx100 --batch-size 10 --delay 2
  python3 market_scanner.py --universe /path/to/custom_tickers.txt --json
  python3 market_scanner.py --universe sp500 --parallel 4

Author: Leonardo Da Pinchy
Version: 1.0.0
License: MIT
===============================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

# Suppress noisy warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Import conviction engine components
sys.path.insert(0, str(Path(__file__).parent))
from spread_conviction_engine import (
    StrategyType, analyse as analyse_vertical,
    fetch_ohlcv, compute_all_indicators
)
from multi_leg_strategies import (
    MultiLegStrategyType, analyse_multi_leg
)

# Import calculator and position sizer
from calculator import bull_call_spread, bear_put_spread
from position_sizer import calculate_position, format_recommendation, DEFAULT_ACCOUNT_VALUE


# =============================================================================
# Constants
# =============================================================================

VERSION = "1.0.0"
DEFAULT_BATCH_SIZE = 5
DEFAULT_DELAY = 1.5  # seconds between API calls
DEFAULT_PARALLEL = 1  # Sequential by default for rate limiting safety

# Strategy configurations
ALL_STRATEGIES = [
    ("bull_put", StrategyType.BULL_PUT, "vertical"),
    ("bear_call", StrategyType.BEAR_CALL, "vertical"),
    ("bull_call", StrategyType.BULL_CALL, "vertical"),
    ("bear_put", StrategyType.BEAR_PUT, "vertical"),
    ("iron_condor", MultiLegStrategyType.IRON_CONDOR, "multi"),
    ("butterfly", MultiLegStrategyType.BUTTERFLY, "multi"),
    ("calendar", MultiLegStrategyType.CALENDAR, "multi"),
]

EXECUTE_THRESHOLD = 80.0  # Minimum conviction for EXECUTE tier


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ScannerResult:
    """Complete result for a single ticker-strategy combination."""
    ticker: str
    price: float
    strategy: str
    conviction: float
    tier: str
    strikes: dict = field(default_factory=dict)
    max_loss: Optional[float] = None
    max_profit: Optional[float] = None
    pop: Optional[float] = None
    position_size: int = 0
    position_recommendation: str = "SKIP"
    position_reason: str = ""
    error: Optional[str] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ScanConfig:
    """Scanner configuration."""
    universe: str  # 'sp500', 'ndx100', or path to custom file
    batch_size: int
    delay: float
    parallel: int
    account_value: float
    output_json: bool
    min_conviction: float
    max_loss_cap: float  # Per position sizer rules
    strategies: list[str]  # Subset of strategies to scan


# =============================================================================
# Universe Loading
# =============================================================================

def get_data_dir() -> Path:
    """Get the data directory path."""
    script_dir = Path(__file__).parent
    return script_dir.parent / "data"


def load_tickers(universe: str) -> list[str]:
    """
    Load ticker list from universe specification.
    
    Args:
        universe: 'sp500', 'ndx100', or path to custom file
        
    Returns:
        List of ticker symbols
    """
    data_dir = get_data_dir()
    
    if universe == "sp500":
        ticker_file = data_dir / "sp500_tickers.txt"
    elif universe == "ndx100":
        ticker_file = data_dir / "ndx100_tickers.txt"
    else:
        # Custom file path - check if it's just a filename (no slashes)
        # and if so, look in the data directory
        if "/" not in universe and "\\" not in universe and not universe.endswith(".txt"):
            # Try with .txt extension in data dir
            ticker_file = data_dir / f"{universe}.txt"
        elif "/" not in universe and "\\" not in universe:
            ticker_file = data_dir / universe
        else:
            ticker_file = Path(universe)
    
    if not ticker_file.exists():
        raise FileNotFoundError(f"Ticker file not found: {ticker_file}")
    
    with open(ticker_file, 'r') as f:
        tickers = [line.strip().upper() for line in f if line.strip()]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tickers = []
    for t in tickers:
        if t and t not in seen:
            seen.add(t)
            unique_tickers.append(t)
    
    return unique_tickers


# =============================================================================
# Strategy Analysis
# =============================================================================

def analyze_ticker_strategy(
    ticker: str,
    strategy_name: str,
    strategy_type: Any,
    strategy_kind: str,
    period: str = "2y",
    interval: str = "1d",
) -> Optional[dict]:
    """
    Analyze a single ticker-strategy combination.
    
    Returns:
        Dictionary with analysis results or None if not EXECUTE tier
    """
    try:
        if strategy_kind == "vertical":
            result = analyse_vertical(ticker, strategy=strategy_type, period=period, interval=interval)
        else:
            result = analyse_multi_leg(ticker, strategy=strategy_type, period=period, interval=interval)
        
        # Only return EXECUTE tier results
        if result.conviction_score < EXECUTE_THRESHOLD:
            return None
        
        return {
            "ticker": ticker,
            "price": result.price,
            "strategy": strategy_name,
            "conviction": result.conviction_score,
            "tier": result.tier,
            "strikes": _extract_strikes(result),
            "data_quality": getattr(result, "data_quality", "HIGH"),
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "strategy": strategy_name,
            "error": str(e),
        }


def _extract_strikes(result: Any) -> dict:
    """Extract strike information from result."""
    strikes = {}
    
    if hasattr(result, "strikes"):
        s = result.strikes
        if hasattr(s, "short_strike"):
            strikes["short"] = s.short_strike
        if hasattr(s, "long_strike"):
            strikes["long"] = s.long_strike
        if hasattr(s, "put_long"):
            strikes["put_long"] = s.put_long
        if hasattr(s, "put_short"):
            strikes["put_short"] = s.put_short
        if hasattr(s, "call_short"):
            strikes["call_short"] = s.call_short
        if hasattr(s, "call_long"):
            strikes["call_long"] = s.call_long
        if hasattr(s, "lower_long"):
            strikes["lower_long"] = s.lower_long
        if hasattr(s, "middle_short"):
            strikes["middle_short"] = s.middle_short
        if hasattr(s, "upper_long"):
            strikes["upper_long"] = s.upper_long
        if hasattr(s, "strike"):
            strikes["atm"] = s.strike
        if hasattr(s, "front_expiry"):
            strikes["front_expiry"] = s.front_expiry
        if hasattr(s, "back_expiry"):
            strikes["back_expiry"] = s.back_expiry
    
    return strikes


# =============================================================================
# Profit/Loss Calculation
# =============================================================================

def estimate_strategy_pl(
    ticker: str,
    price: float,
    strategy: str,
    strikes: dict,
) -> tuple[float, float, float]:
    """
    Estimate max loss, max profit, and POP for a strategy.
    
    Uses simplified assumptions for quick estimation:
    - 30 days to expiry
    - 30% implied volatility
    - Credit spreads: collect ~30% of strike width
    
    Returns:
        (max_loss, max_profit, pop)
    """
    try:
        iv = 0.30
        dte = 30
        rfr = 0.05
        
        if strategy == "bull_put":
            short_strike = strikes.get("short", price * 0.95)
            long_strike = strikes.get("long", short_strike - price * 0.02)
            width = short_strike - long_strike
            credit = width * 0.30  # Collect 30% of width
            max_loss = (width - credit) * 100
            max_profit = credit * 100
            # Simplified POP estimate based on strike distance
            pop = 0.60 + (short_strike / price - 1.0) * 2  # Higher POP for OTM
            
        elif strategy == "bear_call":
            short_strike = strikes.get("short", price * 1.05)
            long_strike = strikes.get("long", short_strike + price * 0.02)
            width = long_strike - short_strike
            credit = width * 0.30
            max_loss = (width - credit) * 100
            max_profit = credit * 100
            pop = 0.60 + (1.0 - short_strike / price) * 2
            
        elif strategy in ["bull_call", "bear_put"]:
            # Debit spreads
            if strategy == "bull_call":
                long_strike = strikes.get("long", price)
                short_strike = strikes.get("short", price * 1.05)
            else:
                long_strike = strikes.get("long", price)
                short_strike = strikes.get("short", price * 0.95)
            
            width = abs(long_strike - short_strike)
            debit = width * 0.50  # Pay ~50% of width
            max_loss = debit * 100
            max_profit = (width - debit) * 100
            pop = 0.45  # Debit spreads typically have lower POP
            
        elif strategy == "iron_condor":
            # Two credit spreads
            put_width = strikes.get("put_short", price * 0.95) - strikes.get("put_long", price * 0.93)
            call_width = strikes.get("call_long", price * 1.07) - strikes.get("call_short", price * 1.05)
            put_credit = put_width * 0.30
            call_credit = call_width * 0.30
            total_credit = put_credit + call_credit
            max_profit = total_credit * 100
            # Max loss is the wider wing minus credit
            max_loss = (max(put_width, call_width) - total_credit) * 100
            pop = 0.65  # Iron condors have high POP if well-constructed
            
        elif strategy == "butterfly":
            # Debit strategy with limited risk/reward
            wing_width = strikes.get("middle_short", price) - strikes.get("lower_long", price * 0.95)
            debit = wing_width * 0.15  # Butterflies are cheap
            max_loss = debit * 100
            max_profit = (wing_width - debit) * 100
            pop = 0.25  # Low POP but high reward
            
        elif strategy == "calendar":
            # Calendar spread - debit with theta focus
            debit = price * 0.02  # ~2% of stock price
            max_loss = debit * 100
            max_profit = debit * 200  # Theoretical max is ~2x debit
            pop = 0.55
            
        else:
            return 0.0, 0.0, 0.0
        
        return (
            round(max_loss, 2),
            round(max_profit, 2),
            round(max(min(pop, 0.95), 0.05), 2)  # Clamp between 5% and 95%
        )
    except Exception:
        return 0.0, 0.0, 0.0


# =============================================================================
# Position Sizing Integration
# =============================================================================

def size_position(
    max_loss: float,
    max_profit: float,
    pop: float,
    account_value: float = DEFAULT_ACCOUNT_VALUE,
) -> dict:
    """
    Run position sizer on a trade candidate.
    
    Returns:
        Position sizing result dictionary
    """
    return calculate_position(
        account_value=account_value,
        max_loss_per_spread=max_loss,
        win_amount=max_profit,
        pop=pop,
    )


# =============================================================================
# Scanner Core
# =============================================================================

def scan_ticker(
    ticker: str,
    config: ScanConfig,
) -> list[ScannerResult]:
    """
    Scan a single ticker across all requested strategies.
    
    Args:
        ticker: Stock symbol
        config: Scanner configuration
        
    Returns:
        List of ScannerResult (may be empty if no EXECUTE plays)
    """
    results = []
    
    for strategy_name, strategy_type, strategy_kind in ALL_STRATEGIES:
        # Skip if not in requested strategies
        if config.strategies and strategy_name not in config.strategies:
            continue
        
        # Analyze
        analysis = analyze_ticker_strategy(
            ticker, strategy_name, strategy_type, strategy_kind
        )
        
        if analysis is None:
            continue  # Not EXECUTE tier
        
        if "error" in analysis:
            results.append(ScannerResult(
                ticker=ticker,
                price=0.0,
                strategy=strategy_name,
                conviction=0.0,
                tier="ERROR",
                error=analysis["error"],
            ))
            continue
        
        # Estimate P/L
        max_loss, max_profit, pop = estimate_strategy_pl(
            ticker,
            analysis["price"],
            strategy_name,
            analysis["strikes"],
        )
        
        # Run position sizer
        sizing = size_position(max_loss, max_profit, pop, config.account_value)
        
        # Build result
        result = ScannerResult(
            ticker=ticker,
            price=analysis["price"],
            strategy=strategy_name,
            conviction=analysis["conviction"],
            tier=analysis["tier"],
            strikes=analysis["strikes"],
            max_loss=max_loss,
            max_profit=max_profit,
            pop=pop,
            position_size=sizing["contracts"],
            position_recommendation=sizing["recommendation"],
            position_reason=sizing["reason"],
        )
        
        results.append(result)
    
    return results


def run_scanner(config: ScanConfig) -> list[ScannerResult]:
    """
    Run the full market scan.
    
    Args:
        config: Scanner configuration
        
    Returns:
        List of all EXECUTE-tier ScannerResults
    """
    # Load tickers
    tickers = load_tickers(config.universe)
    print(f"📊 Loaded {len(tickers)} tickers from {config.universe}")
    print(f"🔍 Scanning for EXECUTE-tier plays (conviction >= {EXECUTE_THRESHOLD})")
    print(f"⏱️  Rate limit: {config.delay}s delay between calls")
    print(f"💰 Account value: ${config.account_value:.0f}")
    print()
    
    all_results: list[ScannerResult] = []
    processed = 0
    errors = 0
    
    # Process in batches with rate limiting
    for i in range(0, len(tickers), config.batch_size):
        batch = tickers[i:i + config.batch_size]
        
        if config.parallel > 1:
            # Parallel processing with ThreadPoolExecutor
            # Note: Still rate-limited via delays between batches
            with ThreadPoolExecutor(max_workers=config.parallel) as executor:
                futures = {
                    executor.submit(scan_ticker, ticker, config): ticker
                    for ticker in batch
                }
                
                for future in as_completed(futures):
                    ticker = futures[future]
                    try:
                        results = future.result()
                        all_results.extend(results)
                        processed += 1
                        
                        if results:
                            print(f"  ✓ {ticker}: Found {len(results)} EXECUTE play(s)")
                        else:
                            print(f"  · {ticker}: No EXECUTE plays")
                            
                    except Exception as e:
                        errors += 1
                        print(f"  ✗ {ticker}: Error - {e}")
        else:
            # Sequential processing
            for ticker in batch:
                try:
                    results = scan_ticker(ticker, config)
                    all_results.extend(results)
                    processed += 1
                    
                    if results:
                        print(f"  ✓ {ticker}: Found {len(results)} EXECUTE play(s)")
                    else:
                        print(f"  · {ticker}: No EXECUTE plays")
                        
                except Exception as e:
                    errors += 1
                    print(f"  ✗ {ticker}: Error - {e}")
        
        # Rate limiting between batches
        if i + config.batch_size < len(tickers):
            time.sleep(config.delay)
    
    print()
    print(f"✅ Scan complete: {processed} tickers processed, {errors} errors")
    print(f"🎯 Found {len(all_results)} total EXECUTE play(s)")
    
    return all_results


# =============================================================================
# Output Formatting
# =============================================================================

def print_table(results: list[ScannerResult]) -> None:
    """Print results as a formatted table."""
    if not results:
        print("\n❌ No EXECUTE-tier plays found matching criteria.\n")
        return
    
    # Header
    print("\n" + "=" * 140)
    print(f"{'TICKER':<8} {'PRICE':>8} {'STRATEGY':<15} {'CONV':>6} {'STRIKES':<40} {'MAX LOSS':>10} {'POP':>6} {'POS':>4} {'REC':<8}")
    print("=" * 140)
    
    for r in results:
        # Format strikes
        strikes_str = ""
        if r.strikes:
            if "short" in r.strikes and "long" in r.strikes:
                strikes_str = f"S:{r.strikes['short']:.1f} L:{r.strikes['long']:.1f}"
            elif "put_short" in r.strikes:
                strikes_str = f"P:{r.strikes.get('put_short',0):.0f}/{r.strikes.get('call_short',0):.0f}"
            elif "middle_short" in r.strikes:
                strikes_str = f"B:{r.strikes.get('lower_long',0):.0f}/{r.strikes.get('middle_short',0):.0f}"
            elif "atm" in r.strikes:
                strikes_str = f"C:{r.strikes['atm']:.0f}"
        
        max_loss_str = f"${r.max_loss:.0f}" if r.max_loss else "N/A"
        pop_str = f"{r.pop*100:.0f}%" if r.pop else "N/A"
        
        print(
            f"{r.ticker:<8} ${r.price:>7.2f} {r.strategy:<15} "
            f"{r.conviction:>5.1f} {strikes_str:<40} "
            f"{max_loss_str:>10} {pop_str:>6} {r.position_size:>4} {r.position_recommendation:<8}"
        )
    
    print("=" * 140)
    print()
    
    # Detail view for executable plays
    executable = [r for r in results if r.position_recommendation == "EXECUTE"]
    if executable:
        print(f"\n📋 DETAILED EXECUTABLE PLAYS ({len(executable)}):\n")
        for r in executable:
            print(f"{'='*70}")
            print(f"  {r.ticker} — {r.strategy.upper()}")
            print(f"  Price: ${r.price:.2f} | Conviction: {r.conviction:.1f}/100")
            print()
            print(f"  Strikes: {r.strikes}")
            print(f"  Max Loss: ${r.max_loss:.0f} | Max Profit: ${r.max_profit:.0f} | POP: {r.pop*100:.1f}%")
            print()
            print(f"  Position Size: {r.position_size} contract(s)")
            print(f"  Reason: {r.position_reason}")
            print(f"{'='*70}")
        print()


def print_json(results: list[ScannerResult]) -> None:
    """Print results as JSON."""
    output = [r.to_dict() for r in results]
    print(json.dumps(output, indent=2, default=str))


# =============================================================================
# CLI Interface
# =============================================================================

def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Options Market Scanner — Find EXECUTE-tier spread opportunities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 market_scanner.py --universe sp500
  python3 market_scanner.py --universe ndx100 --batch-size 10 --delay 2
  python3 market_scanner.py --universe /path/to/tickers.txt --json
  python3 market_scanner.py --universe sp500 --strategy bull_put bear_call
  python3 market_scanner.py --universe sp500 --parallel 4 --batch-size 20

Stock Universes:
  sp500      S&P 500 constituents
  ndx100     Nasdaq 100 constituents
  <path>     Custom file with one ticker per line

Strategies:
  bull_put, bear_call    Credit spreads (directional)
  bull_call, bear_put    Debit spreads (directional)
  iron_condor            Range-bound premium selling
  butterfly              Volatility compression pinning
  calendar               Theta harvesting from IV term structure
        """,
    )
    
    parser.add_argument(
        "--universe",
        required=True,
        help="Stock universe: 'sp500', 'ndx100', or path to custom ticker file",
    )
    
    parser.add_argument(
        "--strategy",
        nargs="+",
        choices=["bull_put", "bear_call", "bull_call", "bear_put", "iron_condor", "butterfly", "calendar"],
        help="Specific strategies to scan (default: all)",
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Number of tickers per batch (default: {DEFAULT_BATCH_SIZE})",
    )
    
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=f"Seconds between API calls (default: {DEFAULT_DELAY})",
    )
    
    parser.add_argument(
        "--parallel",
        type=int,
        default=DEFAULT_PARALLEL,
        help=f"Parallel workers (default: {DEFAULT_PARALLEL}, use with caution)",
    )
    
    parser.add_argument(
        "--account-value",
        type=float,
        default=DEFAULT_ACCOUNT_VALUE,
        help=f"Account value in dollars (default: ${DEFAULT_ACCOUNT_VALUE:.0f})",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of table",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    
    args = parser.parse_args()
    
    # Build config
    config = ScanConfig(
        universe=args.universe,
        batch_size=args.batch_size,
        delay=args.delay,
        parallel=args.parallel,
        account_value=args.account_value,
        output_json=args.json,
        min_conviction=EXECUTE_THRESHOLD,
        max_loss_cap=100.0,  # $100 max risk per position sizer
        strategies=args.strategy or [],
    )
    
    # Run scan
    results = run_scanner(config)
    
    # Output
    if args.json:
        print_json(results)
    else:
        print_table(results)


if __name__ == "__main__":
    main()
