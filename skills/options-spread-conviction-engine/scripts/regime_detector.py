"""
Market Regime Detection for Options Conviction Engine
Classifies market state using VIX percentiles

Author: Leonardo Da Pinchy
Version: 1.0.0
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional, Literal
from dataclasses import dataclass
import warnings
import threading


@dataclass
class RegimeResult:
    """Container for regime detection results."""
    regime: str
    confidence: float
    vix_level: float
    percentile: float
    vix_ma20: float
    threshold_low: float
    threshold_high: float
    lookback_days: int
    regime_metadata: Dict


class RegimeDetector:
    """
    Detects market regime based on VIX levels and percentiles.
    
    Regimes:
    - CRISIS: VIX > 80th percentile (extreme fear)
    - HIGH_VOL: VIX 60-80th percentile (elevated volatility)
    - NORMAL: VIX 40-60th percentile (normal conditions)
    - LOW_VOL: VIX 20-40th percentile (compressed volatility)
    - EUPHORIA: VIX < 20th percentile (complacency)
    
    The VIX (CBOE Volatility Index) measures implied volatility of S&P 500
    options and serves as a "fear gauge" for the broader market.
    
    References:
    - Whaley, R. (2000). "The Investor Fear Gauge." Journal of Portfolio Management
    - Sinclair, E. (2013). "Volatility Trading." Wiley
    """
    
    REGIMES = ['CRISIS', 'HIGH_VOL', 'NORMAL', 'LOW_VOL', 'EUPHORIA']
    
    # Default lookback for percentile calculation (252 trading days = 1 year)
    DEFAULT_LOOKBACK = 252
    
    # Regime thresholds (percentiles)
    THRESHOLDS = {
        'CRISIS': (80.0, 100.0),
        'HIGH_VOL': (60.0, 80.0),
        'NORMAL': (40.0, 60.0),
        'LOW_VOL': (20.0, 40.0),
        'EUPHORIA': (0.0, 20.0)
    }
    
    def __init__(self, lookback_days: int = DEFAULT_LOOKBACK):
        """
        Initialize RegimeDetector.
        
        Args:
            lookback_days: Number of trading days for percentile calculation (default: 252)
        """
        self.lookback = lookback_days
        self.vix_ticker = "^VIX"
        self._vix_cache: Optional[pd.Series] = None
        self._cache_date: Optional[datetime] = None
        self._cache_lock = threading.Lock()
        self.cache_ttl = 3600  # Cache TTL in seconds (configurable)
        
    def fetch_vix_history(self, end_date: Optional[datetime] = None) -> pd.Series:
        """
        Fetch VIX historical data for percentile calculation.
        
        Args:
            end_date: End date for historical data (default: today)
            
        Returns:
            Series of VIX closing prices indexed by date
            
        Raises:
            ValueError: If unable to fetch VIX data
        """
        if end_date is None:
            end_date = datetime.now()
            
        # Need extra days for lookback + percentile calculation buffer
        start_date = end_date - timedelta(days=int(self.lookback * 1.5) + 30)
        
        try:
            vix = yf.Ticker(self.vix_ticker)
            hist = vix.history(start=start_date, end=end_date)
            
            if hist.empty:
                raise ValueError("No VIX data returned from yfinance")
                
            # Use closing prices
            closes = hist['Close'].dropna()
            
            if len(closes) < self.lookback // 2:
                warnings.warn(f"Limited VIX data: only {len(closes)} days available")
                
            return closes
            
        except Exception as e:
            raise ValueError(f"Failed to fetch VIX data: {e}")
    
    def calculate_percentile(self, current_vix: float, 
                            vix_history: pd.Series,
                            date: Optional[datetime] = None) -> float:
        """
        Calculate VIX percentile rank over lookback period.
        
        Args:
            current_vix: Current VIX level
            vix_history: Historical VIX series
            date: Optional date being evaluated (for excluding current observation)
            
        Returns:
            Percentile rank (0-100)
        """
        if len(vix_history) < 60:  # Require at least 60 days
            raise ValueError(f"Insufficient VIX history: {len(vix_history)} days (min 60)")
            
        # Use last lookback_days for percentile calculation
        recent = vix_history.tail(self.lookback)
        
        # Exclude current observation from historical comparison
        if date is None or date >= vix_history.index[-1]:
            comparison_data = recent.iloc[:-1]  # Exclude most recent
        else:
            comparison_data = recent
            
        percentile = (comparison_data <= current_vix).mean() * 100
        
        return float(percentile)
    
    def detect_regime(self, date: Optional[datetime] = None,
                     use_cache: bool = True) -> RegimeResult:
        """
        Detect current market regime based on VIX percentiles.
        
        Args:
            date: Date to evaluate (default: latest available)
            use_cache: Whether to use cached VIX data if available
            
        Returns:
            RegimeResult with regime classification and metadata
        """
        # Fetch VIX history with thread-safe cache
        with self._cache_lock:
            cache_valid = (
                use_cache and 
                self._vix_cache is not None and 
                self._cache_date is not None and
                (datetime.now() - self._cache_date).seconds < self.cache_ttl
            )
            
            if cache_valid:
                vix_history = self._vix_cache
            else:
                vix_history = self.fetch_vix_history(date)
                if use_cache:
                    self._vix_cache = vix_history
                    self._cache_date = datetime.now()
        
        # Get current VIX level
        if date is not None:
            # Find nearest available date
            mask = vix_history.index <= pd.Timestamp(date)
            if not mask.any():
                raise ValueError(f"No VIX data available for date {date}")
            current_vix = vix_history[mask].iloc[-1]
            available_date = vix_history[mask].index[-1]
        else:
            current_vix = vix_history.iloc[-1]
            available_date = vix_history.index[-1]
        
        # Calculate percentile
        percentile = self.calculate_percentile(current_vix, vix_history, date)
        
        # Calculate 20-day moving average for trend context
        vix_ma20 = vix_history.tail(20).mean()
        
        # Determine regime
        regime = self._percentile_to_regime(percentile)
        
        # Calculate confidence (distance from nearest threshold, normalized)
        confidence = self._calculate_confidence(percentile, regime)
        
        # Get threshold boundaries
        threshold_low, threshold_high = self.THRESHOLDS[regime]
        
        # Build metadata
        metadata = {
            'available_date': available_date.strftime('%Y-%m-%d') if hasattr(available_date, 'strftime') else str(available_date),
            'data_points': len(vix_history),
            'vix_vs_ma20': 'above' if current_vix > vix_ma20 else 'below',
            'percentile_distance_from_center': abs(percentile - 50),
            'regime_duration_estimate': self._estimate_regime_duration(vix_history, regime)
        }
        
        return RegimeResult(
            regime=regime,
            confidence=confidence,
            vix_level=round(current_vix, 2),
            percentile=round(percentile, 1),
            vix_ma20=round(vix_ma20, 2),
            threshold_low=threshold_low,
            threshold_high=threshold_high,
            lookback_days=self.lookback,
            regime_metadata=metadata
        )
    
    def _percentile_to_regime(self, percentile: float) -> str:
        """Convert percentile to regime classification."""
        if percentile >= 80:
            return 'CRISIS'
        elif percentile >= 60:
            return 'HIGH_VOL'
        elif percentile >= 40:
            return 'NORMAL'
        elif percentile >= 20:
            return 'LOW_VOL'
        else:
            return 'EUPHORIA'
    
    def _calculate_confidence(self, percentile: float, regime: str) -> float:
        """
        Calculate confidence score based on distance from threshold.
        
        Returns 0.5 to 1.0 where:
        - 1.0 = Deep in regime (far from threshold)
        - 0.5 = At threshold boundary
        """
        low, high = self.THRESHOLDS[regime]
        
        if regime == 'CRISIS':
            distance = (percentile - low) / 20  # Always 80-100 range
        elif regime == 'EUPHORIA':
            distance = (high - percentile) / 20  # Always 0-20 range
        else:
            dist_to_low = percentile - low
            dist_to_high = high - percentile
            distance = max(dist_to_low, dist_to_high) / 20
        
        return round(0.5 + (distance * 0.5), 3)
    
    def _estimate_regime_duration(self, vix_history: pd.Series, 
                                   current_regime: str) -> int:
        """Count consecutive days in current regime."""
        if len(vix_history) < 20:
            return 0
        
        # Calculate regime for each historical day
        recent = vix_history.tail(60)
        regimes = []
        
        for i in range(len(recent)):
            # Calculate percentile using data up to that point
            window = recent.iloc[:i+1]
            if len(window) < 20:
                regimes.append(None)
                continue
            current_vix = window.iloc[-1]
            comparison = window.iloc[:-1] if len(window) > 1 else window
            pct = (comparison <= current_vix).mean() * 100 if len(comparison) > 0 else 50
            regimes.append(self._percentile_to_regime(pct))
        
        # Count consecutive current regime at end
        count = 0
        for regime in reversed(regimes):
            if regime == current_regime:
                count += 1
            else:
                break
        return count
    
    def get_regime_weights(self, regime: str) -> Dict[str, Dict[str, float]]:
        """
        Return weight adjustments per regime for each strategy.
        
        These adjustments modify the conviction score based on how well
        a strategy fits the current market regime.
        
        Philosophy:
        - CRISIS/HIGH_VOL: Credit spreads benefit from elevated IV (selling premium)
        - LOW_VOL/EUPHORIA: Debit spreads benefit from compressed IV (buying options)
        - NORMAL: No systematic edge from regime
        
        Returns:
            Dict mapping strategy names to weight adjustment dicts.
            Adjustments are additive to base conviction scores.
        """
        adjustments = {
            'CRISIS': {
                'bull_put': {'credit_boost': 0.15, 'mean_reversion_boost': 0.10},
                'bear_call': {'credit_boost': 0.15, 'mean_reversion_boost': 0.10},
                'iron_condor': {'premium_boost': 0.25, 'iv_edge': 0.15},
                'butterfly': {'range_bound_boost': 0.10},
                'calendar': {'iv_term_structure_boost': 0.20},
                'bull_call': {'debit_penalty': -0.15, 'breakout_penalty': -0.10},
                'bear_put': {'debit_penalty': -0.15, 'breakout_penalty': -0.10}
            },
            'HIGH_VOL': {
                'bull_put': {'credit_boost': 0.12, 'mean_reversion_boost': 0.08},
                'bear_call': {'credit_boost': 0.12, 'mean_reversion_boost': 0.08},
                'iron_condor': {'premium_boost': 0.18, 'iv_edge': 0.10},
                'butterfly': {'range_bound_boost': 0.08},
                'calendar': {'iv_term_structure_boost': 0.15},
                'bull_call': {'debit_penalty': -0.10, 'breakout_penalty': -0.05},
                'bear_put': {'debit_penalty': -0.10, 'breakout_penalty': -0.05}
            },
            'NORMAL': {
                'bull_put': {},
                'bear_call': {},
                'iron_condor': {},
                'butterfly': {},
                'calendar': {},
                'bull_call': {},
                'bear_put': {}
            },
            'LOW_VOL': {
                'bull_put': {'credit_penalty': -0.08, 'mean_reversion_penalty': -0.05},
                'bear_call': {'credit_penalty': -0.08, 'mean_reversion_penalty': -0.05},
                'iron_condor': {'premium_penalty': -0.12, 'iv_edge': -0.08},
                'butterfly': {'range_bound_penalty': -0.05},
                'calendar': {'iv_term_structure_penalty': -0.10},
                'bull_call': {'debit_boost': 0.12, 'breakout_boost': 0.08},
                'bear_put': {'debit_boost': 0.12, 'breakout_boost': 0.08}
            },
            'EUPHORIA': {
                'bull_put': {'credit_penalty': -0.15, 'mean_reversion_penalty': -0.12},
                'bear_call': {'credit_penalty': -0.15, 'mean_reversion_penalty': -0.12},
                'iron_condor': {'premium_penalty': -0.20, 'iv_edge': -0.15},
                'butterfly': {'range_bound_penalty': -0.10},
                'calendar': {'iv_term_structure_penalty': -0.15},
                'bull_call': {'debit_boost': 0.18, 'breakout_boost': 0.15, 'momentum_boost': 0.10},
                'bear_put': {'debit_boost': 0.18, 'breakout_boost': 0.15, 'contrarian_boost': 0.08}
            }
        }
        
        return adjustments.get(regime, adjustments['NORMAL'])
    
    def regime_aware_score(self, base_score: float, regime: str,
                          strategy: str) -> Tuple[float, str]:
        """
        Adjust conviction score based on regime fit.
        
        Args:
            base_score: Original conviction score (0-100)
            regime: Current market regime
            strategy: Options strategy being evaluated
            
        Returns:
            Tuple of (adjusted_score, reasoning)
        """
        weights = self.get_regime_weights(regime)
        strategy_weights = weights.get(strategy, {})
        
        if not strategy_weights:
            return base_score, f"No regime adjustment for {strategy} in {regime} regime"
        
        # Calculate total adjustment
        total_adjustment = sum(strategy_weights.values())
        
        # Apply adjustment (convert from fraction to points, max +/- 15 points)
        adjustment_points = total_adjustment * 100
        adjustment_points = max(-15, min(15, adjustment_points))  # Cap at +/- 15 points
        
        adjusted_score = base_score + adjustment_points
        adjusted_score = max(0, min(100, adjusted_score))  # Keep in valid range
        
        # Build reasoning
        reasons = []
        for key, value in strategy_weights.items():
            if value > 0:
                reasons.append(f"+{value:.0%} {key.replace('_', ' ')}")
            elif value < 0:
                reasons.append(f"{value:.0%} {key.replace('_', ' ')}")
        
        reasoning = f"{regime} regime: {', '.join(reasons)}" if reasons else f"Neutral in {regime} regime"
        
        return round(adjusted_score, 1), reasoning
    
    def is_favorable_for_strategy(self, regime: str, strategy: str) -> Tuple[bool, str]:
        """
        Quick check if regime is favorable for a given strategy.
        
        Returns:
            Tuple of (is_favorable, explanation)
        """
        favorable_combos = {
            'CRISIS': ['iron_condor', 'bull_put', 'bear_call', 'calendar'],
            'HIGH_VOL': ['iron_condor', 'bull_put', 'bear_call'],
            'NORMAL': ['all'],  # No systematic bias
            'LOW_VOL': ['bull_call', 'bear_put', 'butterfly'],
            'EUPHORIA': ['bull_call', 'bear_put']  # Momentum plays
        }
        
        favorable = favorable_combos.get(regime, [])
        
        if 'all' in favorable or strategy in favorable:
            return True, f"{regime} regime is favorable for {strategy}"
        else:
            return False, f"{regime} regime creates headwinds for {strategy}"


# Convenience function for quick regime check
def get_current_regime() -> RegimeResult:
    """Get current market regime with default settings."""
    detector = RegimeDetector()
    return detector.detect_regime()


if __name__ == "__main__":
    """Demo: Print current market regime and strategy recommendations."""
    print("=" * 70)
    print("MARKET REGIME DETECTION - OPTIONS CONVICTION ENGINE")
    print("=" * 70)
    
    try:
        detector = RegimeDetector()
        result = detector.detect_regime()
        
        print(f"\nCurrent Regime: {result.regime}")
        print(f"Confidence: {result.confidence:.1%}")
        print(f"\nVIX Level: {result.vix_level}")
        print(f"VIX Percentile: {result.percentile}%")
        print(f"VIX 20-Day MA: {result.vix_ma20}")
        print(f"Regime Threshold: {result.threshold_low}% - {result.threshold_high}%")
        print(f"\nEstimated Regime Duration: {result.regime_metadata['regime_duration_estimate']} days")
        print(f"VIX vs 20-MA: {result.regime_metadata['vix_vs_ma20']}")
        
        print("\n" + "-" * 70)
        print("STRATEGY RECOMMENDATIONS")
        print("-" * 70)
        
        strategies = ['bull_put', 'bear_call', 'bull_call', 'bear_put', 
                     'iron_condor', 'butterfly', 'calendar']
        
        for strategy in strategies:
            is_fav, explanation = detector.is_favorable_for_strategy(
                result.regime, strategy
            )
            weights = detector.get_regime_weights(result.regime).get(strategy, {})
            
            if weights:
                net_adjustment = sum(weights.values())
                adj_str = f" (adjustment: {net_adjustment:+.0%})"
            else:
                adj_str = ""
                
            status = "✓ FAVORABLE" if is_fav else "⚠ CHALLENGING"
            print(f"\n{strategy.upper()}: {status}{adj_str}")
            print(f"  → {explanation}")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"Error detecting regime: {e}")
        import traceback
        traceback.print_exc()
