#!/usr/bin/env python3
"""
Quantitative Options Scanner with Unified Conviction Engine

A mathematically-rigorous options scanner built from first principles.
Combines options chain analysis with technical indicators, regime detection,
volatility forecasting, and Kelly-optimal position sizing.

Features:
- Options chain analysis (IV surfaces, skew, term structure)
- Multi-leg strategy optimization (spreads, iron condors, butterflies, calendars)
- Black-Scholes/Monte Carlo POP calculations
- Expected Value and risk-adjusted return scoring
- Market regime detection (VIX-based)
- GARCH volatility forecasting with VRP analysis
- Kelly-optimal, drawdown-constrained position sizing
- Walk-forward backtesting validation
- Account-aware filtering for small accounts

Usage:
    quant_scanner.py SPY --mode pop
    quant_scanner.py AAPL TSLA NVDA --mode income --max-loss 100
    quant_scanner.py SPY --mode ev --dte 30
    quant_scanner.py SPY --unified --strategy bull_put  # Use unified engine

Account Constraints:
- Total Account: $500 (default, override with --account)
- Max Risk Per Trade: $100
- Min Cash Buffer: $150
- Available Capital: Account - Buffer
"""

import argparse
import re
import sys
import json
from typing import List, Optional, Protocol, runtime_checkable, Dict, Tuple, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from options_math import (
    BlackScholes, ProbabilityCalculator, VolatilityAnalyzer,
    fits_account_constraints, MAX_RISK_PER_TRADE, DEFAULT_ACCOUNT_TOTAL,
    ACCOUNT_TOTAL, AVAILABLE_CAPITAL, MIN_CASH_BUFFER
)
from chain_analyzer import ChainFetcher, ChainAnalyzer, OptionChain
from leg_optimizer import LegOptimizer, MultiLegStrategy, validate_strategy_risk

# Import quantitative modules
from regime_detector import RegimeDetector, RegimeResult, get_current_regime
from vol_forecaster import VolatilityForecaster, VRPSignal
from enhanced_kelly import EnhancedKellySizer, PositionResult
from backtest_validator import BacktestValidator

VALID_SPREAD_TYPES = {'put_credit', 'call_credit', 'put_debit', 'call_debit'}

# Ticker validation: standard equity/options format only
_TICKER_PATTERN = re.compile(r'^[A-Z0-9.\-=]+$')


@runtime_checkable
class ChainFetcherProtocol(Protocol):
    """Protocol for options chain data fetchers."""

    def fetch_quote(self, ticker: str) -> Optional[dict]: ...

    def fetch_multiple_expirations(
        self, ticker: str, num_expirations: int = 4,
        min_dte: int = 7, max_dte: int = 45
    ) -> list: ...


def validate_tickers(tickers: List[str]) -> List[str]:
    """Validate ticker symbols against safe pattern."""
    validated = []
    for raw in tickers:
        t = raw.strip().upper()
        if not t:
            raise ValueError(f"Empty ticker symbol: {raw!r}")
        if not _TICKER_PATTERN.match(t):
            raise ValueError(
                f"Invalid ticker symbol: {raw!r}. "
                "Tickers must match ^[A-Z0-9.=-]+$ (no spaces, slashes, or shell characters)."
            )
        if len(t) > 20:
            raise ValueError(f"Ticker symbol too long: {raw!r} ({len(t)} chars, max 20)")
        validated.append(t)
    return validated


class QuantConvictionEngine:
    """
    Unified quantitative conviction engine combining:
    - Technical indicator analysis (Ichimoku, RSI, MACD, BB)
    - Market regime detection (VIX-based)
    - Volatility forecasting (GARCH + VRP)
    - Kelly-optimal position sizing
    - Walk-forward validation
    
    This engine provides a comprehensive, quantitatively-rigorous assessment
    of options trade opportunities by combining multiple orthogonal signals.
    """
    
    def __init__(self, account_value: float = 390):
        self.account = account_value
        self.regime_detector = RegimeDetector()
        self.kelly_sizer = EnhancedKellySizer(account_value=account_value)
        self.current_regime: Optional[str] = None
        self.regime_metadata: Optional[Dict] = None
        self._cached_vrp: Optional[VRPSignal] = None
        
    def analyze(self, ticker: str, strategy: str = 'auto') -> Dict[str, Any]:
        """
        Full quantitative analysis pipeline:
        
        1. Detect market regime
        2. Get volatility forecast and VRP
        3. Apply regime-based adjustments
        4. Calculate Kelly-optimal position size
        5. Return unified recommendation
        
        Args:
            ticker: Stock ticker symbol
            strategy: Options strategy ('bull_put', 'bear_call', 'bull_call', 
                     'bear_put', 'iron_condor', or 'auto')
            
        Returns:
            Dictionary with unified conviction analysis including:
            - regime: Current market regime detection
            - vrp_analysis: Volatility risk premium assessment
            - kelly_sizing: Optimal position sizing recommendation
            - final_score: Unified conviction score (0-100)
            - recommendation: EXECUTE, PREPARE, WATCH, or WAIT
        """
        # Step 1: Market regime detection
        regime_result = self.regime_detector.detect_regime()
        self.current_regime = regime_result.regime
        self.regime_metadata = regime_result.regime_metadata
        
        # Step 2: Volatility forecasting and VRP analysis
        vol_forecaster = VolatilityForecaster(ticker)
        try:
            garch = vol_forecaster.fit_garch()
            forecast = vol_forecaster.forecast_vol(horizon=21)
            
            # Get current implied volatility (placeholder - would come from chain)
            # In practice, this would be fetched from options chain
            current_iv = self._estimate_current_iv(ticker, vol_forecaster)
            vrp_signal = vol_forecaster.vol_risk_premium(current_iv)
            self._cached_vrp = vrp_signal
        except Exception as e:
            # If GARCH fails, continue without VRP adjustment
            vrp_signal = None
            garch = None
            forecast = None
        
        # Step 3: Calculate base conviction score
        # This integrates with spread_conviction_engine if available
        base_score, technical_signals = self._get_technical_conviction(ticker, strategy)
        
        # Step 4: Apply regime-based adjustment
        regime_adjusted_score, regime_reason = self.apply_regime_adjustment(
            base_score, strategy
        )
        
        # Step 5: Apply VRP-based adjustment
        if vrp_signal:
            final_score, vrp_reason = self.apply_vrp_adjustment(
                regime_adjusted_score, current_iv, ticker, strategy
            )
        else:
            final_score = regime_adjusted_score
            vrp_reason = "VRP analysis unavailable"
        
        # Step 6: Determine tier
        tier = self._score_to_tier(final_score)
        
        # Step 7: Calculate Kelly-optimal position sizing
        position_result = self._calculate_position_sizing(
            ticker, strategy, final_score, tier
        )
        
        # Build unified result
        result = {
            'ticker': ticker.upper(),
            'strategy': strategy,
            'timestamp': self._get_timestamp(),
            
            # Market regime
            'regime': {
                'current_regime': self.current_regime,
                'confidence': regime_result.confidence,
                'vix_level': regime_result.vix_level,
                'vix_percentile': regime_result.percentile,
                'regime_duration_estimate': regime_result.regime_metadata.get(
                    'regime_duration_estimate', 0
                ),
                'is_favorable': self._is_regime_favorable(strategy)
            },
            
            # Volatility analysis
            'volatility': {
                'garch_fitted': garch is not None,
                'current_iv': current_iv if vrp_signal else None,
                'forecast_rv': vrp_signal.forecast_rv if vrp_signal else None,
                'vrp': vrp_signal.vrp if vrp_signal else None,
                'vrp_zscore': vrp_signal.vrp_zscore if vrp_signal else None,
                'vrp_recommendation': vrp_signal.recommendation if vrp_signal else None,
            },
            
            # Conviction scoring
            'conviction': {
                'base_score': round(base_score, 1),
                'regime_adjusted': round(regime_adjusted_score, 1),
                'final_score': round(final_score, 1),
                'tier': tier,
                'regime_adjustment_reason': regime_reason,
                'vrp_adjustment_reason': vrp_reason,
            },
            
            # Position sizing
            'position': {
                'contracts': position_result.contracts if position_result else 0,
                'total_risk': position_result.total_risk if position_result else 0,
                'kelly_fraction': position_result.kelly_fraction if position_result else 0,
                'recommendation': position_result.recommendation if position_result else 'NO_TRADE',
                'reasoning': position_result.reasoning if position_result else 'Analysis incomplete',
            },
            
            # Technical signals (if available)
            'technical_signals': technical_signals,
            
            # Final recommendation
            'recommendation': self._generate_final_recommendation(
                tier, position_result, vrp_signal
            )
        }
        
        return result
    
    def apply_regime_adjustment(self, base_score: float, strategy: str) -> Tuple[float, str]:
        """
        Apply regime-based weight adjustments to conviction score.
        
        Args:
            base_score: Original conviction score (0-100)
            strategy: Options strategy being evaluated
            
        Returns:
            Tuple of (adjusted_score, reasoning)
        """
        # Ensure we have current regime data
        if not self.current_regime:
            regime_result = self.regime_detector.detect_regime()
            self.current_regime = regime_result.regime
            self.regime_metadata = regime_result.regime_metadata
        
        if not self.current_regime:
            return base_score, "No regime data available"
        
        return self.regime_detector.regime_aware_score(
            base_score, self.current_regime, strategy
        )
    
    def apply_vrp_adjustment(self, base_score: float, current_iv: float, 
                             ticker: str, strategy: str) -> Tuple[float, str]:
        """
        Adjust conviction based on volatility risk premium.
        
        Args:
            base_score: Current conviction score (0-100)
            current_iv: Current implied volatility (annualized %)
            ticker: Stock ticker
            strategy: Options strategy
            
        Returns:
            Tuple of (adjusted_score, reasoning)
        """
        forecaster = VolatilityForecaster(ticker)
        try:
            forecaster.fit_garch()
            vrp_signal = forecaster.vol_risk_premium(current_iv)
            return forecaster.add_to_conviction(base_score, vrp_signal, strategy)
        except Exception as e:
            return base_score, f"VRP adjustment failed: {str(e)}"
    
    def _get_technical_conviction(self, ticker: str, strategy: str) -> Tuple[float, Dict]:
        """
        Get technical conviction score from spread conviction engine.
        
        Returns base score and technical signal details.
        """
        try:
            # Try to import and use spread_conviction_engine
            from spread_conviction_engine import analyse, StrategyType
            
            # Map strategy string to StrategyType
            strategy_map = {
                'bull_put': StrategyType.BULL_PUT,
                'bear_call': StrategyType.BEAR_CALL,
                'bull_call': StrategyType.BULL_CALL,
                'bear_put': StrategyType.BEAR_PUT,
            }
            
            if strategy in strategy_map:
                stype = strategy_map[strategy]
            else:
                # Default to bull_put if auto or unknown
                stype = StrategyType.BULL_PUT
            
            result = analyse(ticker, strategy=stype)
            
            signals = {
                'ichimoku': {
                    'price_vs_cloud': result.ichimoku.price_vs_cloud,
                    'tk_cross': result.ichimoku.tk_cross,
                    'cloud_color': result.ichimoku.cloud_color,
                    'score': result.ichimoku.component_score,
                },
                'rsi': {
                    'value': result.rsi.value,
                    'zone': result.rsi.zone,
                    'score': result.rsi.component_score,
                },
                'macd': {
                    'histogram_direction': result.macd.hist_direction,
                    'crossover': result.macd.crossover,
                    'score': result.macd.component_score,
                },
                'bollinger': {
                    'percent_b': result.bollinger.percent_b,
                    'bandwidth': result.bollinger.bandwidth,
                    'score': result.bollinger.component_score,
                },
                'trend_bias': result.trend_bias,
            }
            
            return result.conviction_score, signals
            
        except Exception as e:
            # If spread_conviction_engine not available, return neutral
            return 50.0, {'error': f'Technical analysis unavailable: {str(e)}'}
    
    def _estimate_current_iv(self, ticker: str, forecaster: VolatilityForecaster) -> float:
        """
        Estimate current implied volatility.
        
        In practice, this would come from the options chain.
        For now, use a heuristic based on realized vol plus typical premium.
        """
        try:
            # Try to fetch from options chain
            fetcher = ChainFetcher(rate_limit_delay=0.1)
            quote = fetcher.fetch_quote(ticker)
            if quote and 'impliedVolatility' in quote:
                return quote['impliedVolatility'] * 100  # Convert to percentage
        except (ValueError, KeyError, ConnectionError) as e:
            logger.warning(f"Failed to fetch IV from options chain: {e}")
        
        # Fallback: use forecast RV plus typical VRP (2-3%)
        if forecaster._garch_result:
            rv = forecaster._garch_result.fitted_vol.iloc[-1]
            return rv + 2.5  # Add typical VRP
        
        # Last resort: assume 20% IV
        return 20.0
    
    def _score_to_tier(self, score: float) -> str:
        """Convert numerical score to action tier."""
        if score >= 80:
            return 'EXECUTE'
        elif score >= 60:
            return 'PREPARE'
        elif score >= 40:
            return 'WATCH'
        else:
            return 'WAIT'
    
    def _calculate_position_sizing(self, ticker: str, strategy: str, 
                                   conviction: float, tier: str) -> Optional[PositionResult]:
        """Calculate Kelly-optimal position size."""
        # Only calculate for viable trades
        if tier not in ['EXECUTE', 'PREPARE']:
            return None
        
        # Estimate trade parameters
        # In practice, these would come from actual strategy analysis
        pop = self._estimate_pop(tier)
        max_loss = 85  # Typical credit spread max loss
        win_amount = 35  # Typical credit spread profit
        
        return self.kelly_sizer.calculate_position(
            spread_cost=max_loss,
            max_loss_per_spread=max_loss,
            win_amount=win_amount,
            conviction=conviction,
            pop=pop,
            ticker=ticker
        )
    
    def _estimate_pop(self, tier: str) -> float:
        """Estimate probability of profit based on tier."""
        pop_map = {
            'EXECUTE': 0.70,
            'PREPARE': 0.60,
            'WATCH': 0.55,
            'WAIT': 0.45
        }
        return pop_map.get(tier, 0.50)
    
    def _is_regime_favorable(self, strategy: str) -> bool:
        """Check if current regime is favorable for strategy."""
        if not self.current_regime:
            return True
        is_fav, _ = self.regime_detector.is_favorable_for_strategy(
            self.current_regime, strategy
        )
        return is_fav
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _generate_final_recommendation(self, tier: str, 
                                       position: Optional[PositionResult],
                                       vrp: Optional[VRPSignal]) -> Dict:
        """Generate final trade recommendation."""
        rec = {
            'action': tier,
            'rationale': [],
        }
        
        if tier == 'EXECUTE':
            rec['rationale'].append('High conviction score (80+)')
        elif tier == 'PREPARE':
            rec['rationale'].append('Moderate conviction (60-79) - monitor for entry')
        elif tier == 'WATCH':
            rec['rationale'].append('Low conviction (40-59) - on watchlist')
        else:
            rec['rationale'].append('Insufficient conviction (<40) - avoid')
        
        if position and position.contracts > 0:
            rec['rationale'].append(
                f"Position size: {position.contracts} contract(s) "
                f"(${position.total_risk} risk)"
            )
        
        if vrp:
            if vrp.recommendation in ['STRONG_SELL', 'SELL']:
                rec['rationale'].append(f"VRP favors selling: {vrp.reasoning}")
            elif vrp.recommendation in ['STRONG_BUY', 'BUY']:
                rec['rationale'].append(f"VRP favors buying: {vrp.reasoning}")
        
        return rec
    
    def run_backtest_validation(self, tickers: List[str], 
                                 start_date: str = "2022-01-01",
                                 end_date: str = "2024-01-01",
                                 strategy: str = "bull_put") -> Dict:
        """
        Run walk-forward backtest validation of the engine.
        
        Args:
            tickers: List of tickers to backtest
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            strategy: Strategy to test
            
        Returns:
            Validation report dictionary
        """
        validator = BacktestValidator(
            self,
            start_date=start_date,
            end_date=end_date,
            strategy=strategy
        )
        
        results = validator.run_walk_forward(tickers)
        report = validator.validate_tiers(results)
        
        return report.to_dict()


class QuantScanner:
    """
    Main quantitative options scanner with optional unified conviction engine.
    """
    
    def __init__(self, account_total: float = DEFAULT_ACCOUNT_TOTAL,
                 max_risk_per_trade: float = MAX_RISK_PER_TRADE,
                 min_cash_buffer: float = MIN_CASH_BUFFER,
                 fetcher: Optional[ChainFetcherProtocol] = None,
                 analyzer: Optional[ChainAnalyzer] = None,
                 optimizer: Optional[LegOptimizer] = None):
        self.account_total = account_total
        self.max_risk_per_trade = max_risk_per_trade
        self.min_cash_buffer = min_cash_buffer
        self.fetcher = fetcher or ChainFetcher(rate_limit_delay=0.3)
        self.analyzer = analyzer or ChainAnalyzer(self.fetcher)
        self.optimizer = optimizer or LegOptimizer(
            account_total=account_total,
            max_risk_per_trade=max_risk_per_trade,
            min_cash_buffer=min_cash_buffer)
        self.vol_analyzer = VolatilityAnalyzer()
        self._unified_engine: Optional[QuantConvictionEngine] = None
    
    def scan_ticker(self, ticker: str, mode: str = 'pop',
                   min_dte: int = 7, max_dte: int = 45,
                   max_loss_limit: float = MAX_RISK_PER_TRADE,
                   min_pop: float = 0.0,
                   min_width: float = 1.0,
                   max_width: float = None,  # None = auto-calculate based on price
                   verbose: bool = False,
                   use_unified_engine: bool = False,
                   unified_strategy: str = 'auto') -> Optional[dict]:
        """
        Scan a single ticker and return best strategies.
        
        Args:
            ticker: Stock ticker symbol
            mode: Scanning mode ('pop', 'ev', 'income', 'earnings')
            use_unified_engine: Whether to use the unified QuantConvictionEngine
            unified_strategy: Strategy for unified engine ('bull_put', 'bear_call', etc.)
            
        Returns:
            Dictionary with scan results or unified engine analysis
        """
        # Use unified engine if requested
        if use_unified_engine:
            if not self._unified_engine:
                self._unified_engine = QuantConvictionEngine(self.account_total)
            
            result = self._unified_engine.analyze(ticker, unified_strategy)
            
            if verbose:
                self._print_unified_result(result)
            
            return result
        
        # Standard scanning logic
        if verbose:
            print(f"\n{'='*60}")
            print(f"Scanning {ticker} | Mode: {mode.upper()}")
            print(f"{'='*60}")
        
        # Fetch quote
        quote = self.fetcher.fetch_quote(ticker)
        if not quote:
            if verbose:
                print(f"ERROR: Could not fetch quote for {ticker}")
            return None
        
        price = quote.get('regularMarketPrice', 0)
        if price == 0:
            if verbose:
                print(f"ERROR: No price data for {ticker}")
            return None
        
        market_state = quote.get('marketState', 'UNKNOWN')
        
        if verbose:
            print(f"\nCurrent Price: ${price:.2f}")
            change = quote.get('regularMarketChange', 0)
            change_pct = quote.get('regularMarketChangePercent', 0)
            print(f"Change: ${change:+.2f} ({change_pct:+.2f}%)")
            if market_state not in ('REGULAR',):
                print(f"  ⚠ Market: {market_state} — bid/ask may be stale/wider than during market hours")
        
        # Fetch multiple expiration chains
        chains = self.fetcher.fetch_multiple_expirations(
            ticker, num_expirations=4, min_dte=min_dte, max_dte=max_dte
        )
        
        if not chains:
            if verbose:
                print(f"ERROR: No options chains available for {ticker}")
            return None
        
        if verbose:
            print(f"\nFound {len(chains)} expiration dates:")
            for chain in chains:
                print(f"  - {chain.expiration_date[:10]} ({chain.dte} DTE)")
        
        # Analyze chains and find strategies
        all_strategies = []
        
        for chain in chains:
            # Skip if too illiquid
            liquidity = self.analyzer.analyze_liquidity(chain)
            if liquidity['score'] < 30:
                if verbose:
                    print(f"  Skipping {chain.dte} DTE - poor liquidity")
                continue
            
            # Find vertical spreads
            put_spreads = self.optimizer.optimize_vertical_spreads(
                chain, spread_type='put_credit', max_width=max_width
            )
            call_spreads = self.optimizer.optimize_vertical_spreads(
                chain, spread_type='call_credit', max_width=max_width
            )
            
            # Find iron condors
            condors = self.optimizer.optimize_iron_condors(chain)
            
            all_strategies.extend(put_spreads)
            all_strategies.extend(call_spreads)
            all_strategies.extend(condors)
        
        if not all_strategies:
            if verbose:
                print(f"\nNo viable strategies found for {ticker}")
            return None
        
        # Validate: reject infinite/undefined risk strategies
        validated = []
        for s in all_strategies:
            is_valid, reason = validate_strategy_risk(s)
            if is_valid:
                validated.append(s)
            elif verbose:
                print(f"  REJECTED: {s.strategy_type} — {reason}")
        all_strategies = validated
        
        if not all_strategies:
            if verbose:
                print(f"\nNo valid strategies after risk validation for {ticker}")
            return None
        
        # Filter by spread width (min and max)
        def _calc_width(strategy, underlying_price: float) -> float:
            """Calculate strategy width."""
            strikes = [leg.strike for leg in strategy.legs]
            if len(strikes) >= 2:
                return max(strikes) - min(strikes)
            elif len(strikes) == 1:
                return abs(strikes[0] - underlying_price)
            return 0.0

        width_filtered = []
        for s in all_strategies:
            width = _calc_width(s, price)
            if width >= min_width and (max_width is None or width <= max_width):
                width_filtered.append(s)
        if verbose and len(width_filtered) != len(all_strategies):
            max_width_str = f"${max_width:.0f}" if max_width else "auto"
            print(f"  Width filter (${min_width:.0f}-{max_width_str}): {len(all_strategies)} → {len(width_filtered)}")
        all_strategies = width_filtered
        
        if not all_strategies:
            if verbose:
                print(f"\nNo strategies after width filter for {ticker}")
            return None
        
        if verbose:
            print(f"\nFound {len(all_strategies)} validated strategies")
        
        # Score strategies based on mode
        scored = self.optimizer.score_strategies(all_strategies, mode=mode)
        
        # Filter by max loss and min POP
        fitting_strategies = [
            s for s in scored 
            if s.max_loss <= max_loss_limit and s.pop >= min_pop
        ]
        
        if not fitting_strategies:
            if min_pop > 0:
                if verbose:
                    print(f"\nNo strategies meet min POP {min_pop*100:.0f}% and max loss ${max_loss_limit:.0f}")
                return None
            fitting_strategies = sorted(scored, key=lambda x: x.max_loss)[:3]
        
        # Take top 3
        top_strategies = fitting_strategies[:3]
        
        if verbose:
            self._print_strategies(ticker, price, top_strategies, mode)
        
        return {
            'ticker': ticker,
            'price': price,
            'mode': mode,
            'strategies': [s.to_dict() for s in top_strategies],
            'total_found': len(all_strategies),
            'fitting_count': len(fitting_strategies)
        }
    
    def _print_unified_result(self, result: Dict):
        """Pretty print unified engine result."""
        print(f"\n{'='*70}")
        print(f"UNIFIED QUANTITATIVE CONVICTION ANALYSIS")
        print(f"{'='*70}")
        print(f"Ticker: {result['ticker']} | Strategy: {result['strategy']}")
        print(f"Timestamp: {result['timestamp']}")
        
        # Market Regime
        print(f"\n📊 MARKET REGIME")
        print(f"  Current: {result['regime']['current_regime']}")
        print(f"  Confidence: {result['regime']['confidence']:.1%}")
        print(f"  VIX Level: {result['regime']['vix_level']}")
        print(f"  VIX Percentile: {result['regime']['vix_percentile']}%")
        print(f"  Favorable for strategy: {'✅ Yes' if result['regime']['is_favorable'] else '⚠️ No'}")
        
        # Volatility Analysis
        vol = result['volatility']
        print(f"\n📈 VOLATILITY ANALYSIS")
        if vol['garch_fitted']:
            print(f"  Current IV: {vol['current_iv']:.1f}%")
            print(f"  Forecast RV: {vol['forecast_rv']:.1f}%")
            print(f"  VRP: {vol['vrp']:+.1f}% (z={vol['vrp_zscore']:+.1f})")
            print(f"  Recommendation: {vol['vrp_recommendation']}")
        else:
            print(f"  GARCH modeling failed")
        
        # Conviction Scoring
        conv = result['conviction']
        print(f"\n🎯 CONVICTION SCORING")
        print(f"  Base Score: {conv['base_score']:.1f}/100")
        print(f"  Regime Adjusted: {conv['regime_adjusted']:.1f}/100")
        print(f"  Final Score: {conv['final_score']:.1f}/100")
        print(f"  Tier: {conv['tier']}")
        print(f"  Regime: {conv['regime_adjustment_reason']}")
        print(f"  VRP: {conv['vrp_adjustment_reason']}")
        
        # Position Sizing
        pos = result['position']
        print(f"\n💰 POSITION SIZING")
        print(f"  Contracts: {pos['contracts']}")
        print(f"  Total Risk: ${pos['total_risk']:.2f}")
        print(f"  Kelly Fraction: {pos['kelly_fraction']:.2%}")
        print(f"  Recommendation: {pos['recommendation']}")
        print(f"  Reasoning: {pos['reasoning']}")
        
        # Final Recommendation
        rec = result['recommendation']
        print(f"\n🚦 FINAL RECOMMENDATION: {rec['action']}")
        for rationale in rec['rationale']:
            print(f"  • {rationale}")
        
        print(f"\n{'='*70}")
    
    def _print_strategies(self, ticker: str, price: float, 
                         strategies: List[MultiLegStrategy], mode: str):
        """Pretty print strategy results"""
        
        print(f"\n{'─'*60}")
        print(f"TOP STRATEGIES FOR {ticker} (Mode: {mode.upper()})")
        print(f"{'─'*60}")
        
        for i, s in enumerate(strategies, 1):
            print(f"\n{'▓'*60}")
            print(f"STRATEGY #{i}: {s.strategy_type.upper()}")
            print(f"{'▓'*60}")
            
            print(f"  Expiration: {s.legs[0].expiration[:10]} ({s.legs[0].dte} DTE)")
            
            print(f"\n  LEGS:")
            for leg in s.legs:
                action = "SELL" if leg.action == 'sell' else "BUY"
                print(f"    {action:4} {leg.option_type.upper():4} @ ${leg.strike:7.2f} "
                      f"| Premium: ${leg.premium:.2f} (mid) | DTE: {leg.dte}")
            
            print(f"\n  P&L PROFILE:")
            print(f"    Max Profit:     ${s.max_profit:7.2f}")
            print(f"    Max Loss:       ${s.max_loss:7.2f} {'✓ FITS' if s.fits_account else '✗ TOO RISKY'}")
            print(f"    Breakeven(s):   {', '.join(f'${b:.2f}' for b in s.breakevens)}")
            
            print(f"\n  PROBABILITY & VALUE:")
            print(f"    Probability of Profit (POP): {s.pop*100:5.1f}%")
            print(f"    Expected Value (EV):         ${s.expected_value:+.2f}")
            print(f"    Risk-Adjusted Return:        {s.risk_adjusted_return:+.2f}")
            
            if s.total_greeks:
                print(f"\n  GREEKS (Per Contract):")
                print(f"    Delta: {s.total_greeks.delta:+.3f}")
                print(f"    Theta: ${s.total_greeks.theta:+.2f}/day")
            
            # Recommendation
            if s.fits_account and s.pop > 0.6 and s.expected_value > 0:
                print(f"\n  ★ RECOMMENDATION: EXECUTE")
            elif s.fits_account and s.pop > 0.5:
                print(f"\n  ○ RECOMMENDATION: CONSIDER")
            else:
                print(f"\n  ✗ RECOMMENDATION: PASS")
        
        print(f"\n{'='*60}")
    
    def scan_multiple(self, tickers: List[str], mode: str = 'pop',
                     min_dte: int = 7, max_dte: int = 45,
                     max_loss_limit: float = MAX_RISK_PER_TRADE,
                     min_pop: float = 0.0,
                     min_width: float = 1.0,
                     max_width: float = None,  # None = auto-calculate based on price
                     json_output: bool = False,
                     use_unified_engine: bool = False,
                     unified_strategy: str = 'auto') -> List[dict]:
        """
        Scan multiple tickers and return aggregated results.
        
        Args:
            use_unified_engine: Whether to use unified QuantConvictionEngine
            unified_strategy: Strategy for unified engine analysis
        """
        tickers = validate_tickers(tickers)
        results = []
        
        if not json_output:
            print(f"\n{'#'*70}")
            print(f"# QUANTITATIVE OPTIONS SCANNER")
            if use_unified_engine:
                print(f"# Mode: UNIFIED CONVICTION ENGINE")
                print(f"# Strategy: {unified_strategy}")
            else:
                print(f"# Mode: {mode.upper()}")
            print(f"# Tickers: {', '.join(tickers)}")
            print(f"# Account: ${self.account_total} | Max Risk: ${max_loss_limit}")
            print(f"# DTE Range: {min_dte}-{max_dte}")
            if not use_unified_engine:
                if min_pop > 0:
                    print(f"# Min POP: {min_pop*100:.0f}%")
                if min_width > 1:
                    print(f"# Min Width: ${min_width:.0f}")
                if max_width is not None and max_width < 5:
                    print(f"# Max Width: ${max_width:.0f}")
            print(f"{'#'*70}\n")
        
        for ticker in tickers:
            result = self.scan_ticker(
                ticker, mode, min_dte, max_dte, max_loss_limit, min_pop,
                min_width=min_width, max_width=max_width, 
                verbose=not json_output,
                use_unified_engine=use_unified_engine,
                unified_strategy=unified_strategy
            )
            if result:
                results.append(result)
        
        # Summary
        if not json_output:
            print(f"\n{'#'*70}")
            print(f"# SCAN SUMMARY")
            print(f"{'#'*70}")
            print(f"\nTickers Scanned: {len(tickers)}")
            print(f"Tickers with Opportunities: {len(results)}")
            
            if use_unified_engine:
                execute_count = sum(1 for r in results if r.get('conviction', {}).get('tier') == 'EXECUTE')
                prepare_count = sum(1 for r in results if r.get('conviction', {}).get('tier') == 'PREPARE')
                print(f"\nEXECUTE Recommendations: {execute_count}")
                print(f"PREPARE Recommendations: {prepare_count}")
            
            print(f"\nAccount Constraints:")
            available = self.account_total - self.min_cash_buffer
            print(f"  Total Account: ${self.account_total}")
            print(f"  Max Risk/Trade: ${max_loss_limit}")
            print(f"  Min Cash Buffer: ${self.min_cash_buffer}")
            print(f"  Available Capital: ${available}")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='Quantitative Options Scanner - Mathematical options analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s SPY --mode pop                    # Maximize POP for SPY
  %(prog)s AAPL TSLA --mode ev               # Max expected value
  %(prog)s SPY QQQ --mode income             # Income/theta plays
  %(prog)s NVDA --mode earnings              # Earnings/vol crush plays
  %(prog)s SPY --json                        # Machine-readable output
  %(prog)s SPY --unified --strategy bull_put # Use unified conviction engine
  %(prog)s AAPL --unified --backtest         # Validate with backtesting
  %(prog)s SPY --min-pop 75                  # Only trades with 75%%+ POP
  %(prog)s SPY --min-width 2 --min-pop 75     # $2+ wide spreads, 75%%+ POP
  %(prog)s SPY --min-width 2 --max-width 3   # Only $2-3 wide spreads
  %(prog)s SPY --dte 14 --max-loss 50        # Custom DTE and risk
        """
    )
    
    parser.add_argument('tickers', nargs='+', 
                       help='Stock ticker(s) to scan')
    
    parser.add_argument('--mode', '-m', 
                       choices=['pop', 'ev', 'income', 'earnings'],
                       default='pop',
                       help='Scanning mode (default: pop)')
    
    parser.add_argument('--min-dte', type=int, default=7,
                       help='Minimum days to expiration (default: 7)')
    
    parser.add_argument('--max-dte', type=int, default=45,
                       help='Maximum days to expiration (default: 45)')
    
    parser.add_argument('--max-loss', type=float, default=MAX_RISK_PER_TRADE,
                       help=f'Maximum loss per trade (default: ${MAX_RISK_PER_TRADE})')
    
    parser.add_argument('--min-pop', type=float, default=0.0,
                       help='Minimum Probability of Profit %% (default: 0)')
    
    parser.add_argument('--min-width', type=float, default=1.0,
                       help='Minimum spread width in dollars (default: 1)')
    
    parser.add_argument('--max-width', type=float, default=None,
                       help='Maximum spread width in dollars (default: auto-calculate based on price)'),
    
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output JSON format')
    
    parser.add_argument('--account', type=float, default=DEFAULT_ACCOUNT_TOTAL,
                       help=f'Total account balance (default: ${DEFAULT_ACCOUNT_TOTAL:.0f})')
    
    parser.add_argument('--max-risk', type=float, default=MAX_RISK_PER_TRADE,
                       help=f'Maximum risk per trade in dollars (default: ${MAX_RISK_PER_TRADE:.0f})')
    
    parser.add_argument('--min-cash', type=float, default=MIN_CASH_BUFFER,
                       help=f'Minimum cash buffer to keep in reserve (default: ${MIN_CASH_BUFFER:.0f})')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    # Unified engine options
    parser.add_argument('--unified', action='store_true',
                       help='Use unified QuantConvictionEngine for comprehensive analysis')
    
    parser.add_argument('--strategy', default='auto',
                       choices=['auto', 'bull_put', 'bear_call', 'bull_call', 'bear_put', 'iron_condor'],
                       help='Strategy for unified engine (default: auto)')
    
    parser.add_argument('--backtest', action='store_true',
                       help='Run backtest validation with unified engine')
    
    parser.add_argument('--backtest-start', default='2022-01-01',
                       help='Backtest start date (default: 2022-01-01)')
    
    parser.add_argument('--backtest-end', default='2024-01-01',
                       help='Backtest end date (default: 2024-01-01)')
    
    args = parser.parse_args()
    
    # Validate
    if args.min_dte < 0 or args.max_dte > 365:
        print("ERROR: DTE must be between 0 and 365")
        sys.exit(1)
    
    if args.min_dte > args.max_dte:
        print(f"ERROR: min-dte ({args.min_dte}) cannot exceed max-dte ({args.max_dte})")
        sys.exit(1)
    
    if not (0 <= args.min_pop <= 100):
        print("ERROR: Min POP must be between 0 and 100 (inclusive)")
        sys.exit(1)
    
    if args.account <= 0:
        print("ERROR: Account balance must be positive")
        sys.exit(1)
    
    if args.max_loss <= 0:
        print("ERROR: Max loss must be positive")
        sys.exit(1)
    
    if args.max_loss > args.account:
        print(f"ERROR: Max loss cannot exceed account total (${args.account:.0f})")
        sys.exit(1)
    
    if args.max_width is not None and args.min_width > args.max_width:
        print(f"ERROR: min-width ({args.min_width}) cannot exceed max-width ({args.max_width})")
        sys.exit(1)
    
    # Run scan
    scanner = QuantScanner(account_total=args.account,
                           max_risk_per_trade=args.max_risk,
                           min_cash_buffer=args.min_cash)
    
    if args.backtest and args.unified:
        # Run backtest validation
        print(f"\n{'='*70}")
        print(f"BACKTEST VALIDATION MODE")
        print(f"{'='*70}")
        print(f"Period: {args.backtest_start} to {args.backtest_end}")
        print(f"Tickers: {', '.join(args.tickers)}")
        print(f"Strategy: {args.strategy}")
        print(f"\nRunning walk-forward backtest...")
        
        engine = QuantConvictionEngine(args.account)
        report = engine.run_backtest_validation(
            args.tickers,
            start_date=args.backtest_start,
            end_date=args.backtest_end,
            strategy=args.strategy
        )
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("\n" + "="*70)
            print("BACKTEST VALIDATION REPORT")
            print("="*70)
            
            if 'error' in report:
                print(f"Error: {report['error']}")
            else:
                print(f"\nTier Statistics:")
                for tier, stats in report.get('tier_stats', {}).items():
                    if stats.get('count', 0) > 0:
                        print(f"  {tier:8s}: n={stats['count']:3d}, "
                              f"win_rate={stats['win_rate']:.1%}, "
                              f"exp=${stats['expectancy']:.0f}")
                
                print(f"\nStatistical Tests:")
                for test, p_val in report.get('p_values', {}).items():
                    sig = "***" if p_val < 0.01 else "**" if p_val < 0.05 else "*" if p_val < 0.1 else ""
                    print(f"  {test}: p={p_val:.4f} {sig}")
                
                print(f"\nTier Separation Score: {report.get('tier_separation_score', 0):.2f}")
                print(f"Overall Expectancy: ${report.get('overall_expectancy', 0):.0f}")
                print(f"Recommendation: {report.get('recommendation', 'UNKNOWN')}")
            
            print("="*70)
        
        sys.exit(0)
    
    # Normal scan mode
    results = scanner.scan_multiple(
        tickers=args.tickers,
        mode=args.mode,
        min_dte=args.min_dte,
        max_dte=args.max_dte,
        max_loss_limit=args.max_loss,
        min_pop=args.min_pop / 100.0,  # Convert percentage to decimal
        min_width=args.min_width,
        max_width=args.max_width,
        json_output=args.json,
        use_unified_engine=args.unified,
        unified_strategy=args.strategy
    )
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    # Exit 0 if any results found, 1 if no viable strategies at all
    sys.exit(0 if results else 1)


if __name__ == '__main__':
    main()
