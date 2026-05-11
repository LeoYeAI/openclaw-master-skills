#!/usr/bin/env python3
"""
===============================================================================
Spread Conviction Engine — Unified Multi-Strategy Vertical Spread Scoring
===============================================================================

Author:     Financial Toolkit (OpenClaw)
Created:    2026-02-09
Version:    2.0.0
License:    MIT

    v2.0.0 Additions:
    - Multi-leg strategies: Iron Condors, Butterflies, Calendar Spreads
    - IV Rank approximation via Bollinger Bandwidth percentile
    - IV Term Structure analysis from live options chains
    - Squeeze detection for butterfly setups
    - See multi_leg_strategies.py for full implementation

Description:
    A unified conviction engine that scores four vertical spread strategies:

    ┌────────────┬────────┬──────────────────┬────────────────────────────────┐
    │ Strategy   │ Type   │ Philosophy       │ Ideal Setup                    │
    ├────────────┼────────┼──────────────────┼────────────────────────────────┤
    │ bull_put   │ Credit │ Mean Reversion   │ Bullish trend + oversold dip   │
    │ bear_call  │ Credit │ Mean Reversion   │ Bearish trend + overbought rip │
    │ bull_call  │ Debit  │ Breakout         │ Strong bullish momentum        │
    │ bear_put   │ Debit  │ Breakout         │ Strong bearish momentum        │
    └────────────┴────────┴──────────────────┴────────────────────────────────┘

    v1.1.0 Additions:
    - Volume Multiplier: Cross-references relative volume (RV) to momentum.
    - Dynamic Strike Suggestions: Recommends strikes based on Bollinger Band 1-sigma levels.

    This extends the original ``advanced_signals.py`` (Bull Put Spread only)
    to a general-purpose spread selection tool.  All four indicator families
    (Ichimoku, RSI, MACD, Bollinger Bands) are computed identically; only
    the *interpretation and scoring weights* change per strategy.

    Credit spreads prioritise **mean-reversion** setups: buying dips
    (bull_put) or selling rips (bear_call) within a prevailing trend.

    Debit spreads prioritise **breakout** setups: strong directional
    momentum confirmed by expanding volatility (Bollinger Bandwidth).

Academic Notes:
    • Ichimoku  → Trend structure & equilibrium (Hosoda, 1968)
    • RSI       → Momentum & mean-reversion potential (Wilder, 1978)
    • MACD      → Trend momentum & acceleration (Appel, 1979)
    • Bollinger → Volatility regime & price envelopes (Bollinger, 2001)
    • Combining orthogonal signals reduces false-positive rate compared to
      any single-indicator strategy (Pring, 2002; Murphy, 1999).

Dependencies:
    pandas >= 2.0, pandas_ta >= 0.4.0, yfinance >= 1.0

Usage:
    $ python3 spread_conviction_engine.py AAPL
    $ python3 spread_conviction_engine.py SPY --strategy bear_call
    $ python3 spread_conviction_engine.py QQQ --strategy bull_call --period 2y
    $ python3 spread_conviction_engine.py AAPL MSFT --strategy bear_put --json

===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================
from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional

# Module version — single source of truth
__version__ = "2.0.0"

import pandas as pd
import pandas_ta as ta
import yfinance as yf

# Suppress noisy FutureWarnings and deprecation warnings from yfinance/pandas
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*deprecated.*")


# =============================================================================
# Constants & Configuration
# =============================================================================

# Indicator parameters — identical to advanced_signals.py.
# Ichimoku uses extended (~3×) periods to filter short-term noise and align
# the cloud with intermediate-term trend structure suitable for multi-week
# options positions.  With senkou=120 and kijun=60, approximately 180 trading
# days of history are required before the cloud is fully populated.
ICHIMOKU_TENKAN: int = 20     # Conversion Line (Tenkan-sen); standard = 9
ICHIMOKU_KIJUN: int = 60      # Base Line (Kijun-sen); standard = 26
ICHIMOKU_SENKOU: int = 120    # Leading Span B (Senkou Span B); standard = 52
ICHIMOKU_CHIKOU: int = 30     # Lagging Span displacement; standard = 26
RSI_LENGTH: int = 14
ADX_LENGTH: int = 14
MACD_FAST: int = 12
MACD_SLOW: int = 26
MACD_SIGNAL: int = 9
BBANDS_LENGTH: int = 20
BBANDS_STD: float = 2.0
VOLUME_WINDOW: int = 20


# =============================================================================
# Strategy Framework
# =============================================================================

class StrategyType(str, Enum):
    """
    Supported vertical spread strategies.

    Properties expose directional and credit/debit classification so that
    scoring functions can branch cleanly without string comparisons.
    """
    BULL_PUT = "bull_put"
    BEAR_CALL = "bear_call"
    BULL_CALL = "bull_call"
    BEAR_PUT = "bear_put"

    @property
    def is_bullish(self) -> bool:
        """True for strategies that profit from upward price movement."""
        return self in (StrategyType.BULL_PUT, StrategyType.BULL_CALL)

    @property
    def is_bearish(self) -> bool:
        """True for strategies that profit from downward price movement."""
        return self in (StrategyType.BEAR_CALL, StrategyType.BEAR_PUT)

    @property
    def is_credit(self) -> bool:
        """True for net-credit strategies (mean-reversion philosophy)."""
        return self in (StrategyType.BULL_PUT, StrategyType.BEAR_CALL)

    @property
    def is_debit(self) -> bool:
        """True for net-debit strategies (breakout philosophy)."""
        return self in (StrategyType.BULL_CALL, StrategyType.BEAR_PUT)

    @property
    def label(self) -> str:
        """Human-friendly strategy label for reports."""
        labels = {
            StrategyType.BULL_PUT:  "Bull Put Spread (Credit)",
            StrategyType.BEAR_CALL: "Bear Call Spread (Credit)",
            StrategyType.BULL_CALL: "Bull Call Spread (Debit)",
            StrategyType.BEAR_PUT:  "Bear Put Spread (Debit)",
        }
        return labels[self]

    @property
    def philosophy(self) -> str:
        """Trading philosophy label."""
        return "Mean Reversion" if self.is_credit else "Breakout / Momentum"

    @property
    def ideal_setup(self) -> str:
        """One-line description of the ideal market conditions."""
        setups = {
            StrategyType.BULL_PUT:  "Bullish trend + oversold pullback → bounce expected",
            StrategyType.BEAR_CALL: "Bearish trend + overbought rally → rejection expected",
            StrategyType.BULL_CALL: "Strong bullish momentum + expanding volatility → breakout",
            StrategyType.BEAR_PUT:  "Strong bearish momentum + expanding volatility → breakdown",
        }
        return setups[self]


@dataclass(frozen=True)
class StrategyWeights:
    """
    Per-strategy component weights (must sum to 100).

    Credit spreads give more weight to RSI (mean-reversion entry timing)
    and Ichimoku (trend structure to revert within).

    Debit spreads give more weight to MACD (momentum confirmation) and
    maintain Bollinger weight (bandwidth expansion validates breakout).
    """
    ichimoku: int
    rsi: int
    macd: int
    bollinger: int
    adx: int

    def __post_init__(self) -> None:
        total = self.ichimoku + self.rsi + self.macd + self.bollinger + self.adx
        assert total == 100, f"Weights must sum to 100, got {total}"


STRATEGY_WEIGHTS: dict[StrategyType, StrategyWeights] = {
    # Credit: Trend structure (25) + entry timing (20) + momentum (15) + vol (25) + strength (15)
    StrategyType.BULL_PUT:  StrategyWeights(ichimoku=25, rsi=20, macd=15, bollinger=25, adx=15),
    StrategyType.BEAR_CALL: StrategyWeights(ichimoku=25, rsi=20, macd=15, bollinger=25, adx=15),
    # Debit: Trend confirm (20) + direction (10) + momentum (30) + vol (25) + strength (15)
    StrategyType.BULL_CALL: StrategyWeights(ichimoku=20, rsi=10, macd=30, bollinger=25, adx=15),
    StrategyType.BEAR_PUT:  StrategyWeights(ichimoku=20, rsi=10, macd=30, bollinger=25, adx=15),
}


# =============================================================================
# Enumerations — Readable Signal Labels
# =============================================================================

class TrendBias(str, Enum):
    """Qualitative trend classification (objective, strategy-independent)."""
    STRONG_BULL = "STRONG_BULL"
    BULL = "BULL"
    NEUTRAL = "NEUTRAL"
    BEAR = "BEAR"
    STRONG_BEAR = "STRONG_BEAR"


class ConvictionTier(str, Enum):
    """
    Maps the raw 0–100 score to an actionable tier.

    The tiers encode a patience framework:
      - WAIT:    Conditions are poor for this strategy. Do nothing.
      - WATCH:   Getting interesting. Add to watchlist.
      - PREPARE: Conditions are favourable. Size the trade.
      - EXECUTE: High conviction. Enter the spread.
    """
    WAIT = "WAIT"         # 0–39
    WATCH = "WATCH"       # 40–59
    PREPARE = "PREPARE"   # 60–79
    EXECUTE = "EXECUTE"   # 80–100

    @classmethod
    def from_score(cls, score: float) -> "ConvictionTier":
        """Classify a numeric conviction score into an action tier."""
        if score >= 80:
            return cls.EXECUTE
        elif score >= 60:
            return cls.PREPARE
        elif score >= 40:
            return cls.WATCH
        else:
            return cls.WAIT


# =============================================================================
# Data Classes — Structured Signal Output
# =============================================================================

@dataclass
class IchimokuSignal:
    """
    Ichimoku Kinko Hyo signal decomposition.

    Attributes:
        price_vs_cloud:   'ABOVE', 'BELOW', or 'INSIDE'
        tk_cross:         'BULLISH' or 'BEARISH' (Tenkan vs Kijun)
        cloud_color:      'GREEN' if Senkou A > Senkou B, else 'RED'
        cloud_thickness:  Absolute distance between Senkou A and B
        tenkan:           Current Tenkan-sen value
        kijun:            Current Kijun-sen value
        senkou_a:         Current Senkou Span A value
        senkou_b:         Current Senkou Span B value
        component_score:  Sub-score contribution (0 to weight)
    """
    price_vs_cloud: str
    tk_cross: str
    cloud_color: str
    cloud_thickness: float
    tenkan: float
    kijun: float
    senkou_a: float
    senkou_b: float
    component_score: float = 0.0


@dataclass
class RSISignal:
    """
    Relative Strength Index signal.

    Attributes:
        value:            Current RSI reading
        zone:             Human-readable zone label (strategy-specific)
        component_score:  Sub-score contribution (0 to weight)
    """
    value: float
    zone: str
    component_score: float = 0.0


@dataclass
class MACDSignal:
    """
    Moving Average Convergence Divergence signal.

    Attributes:
        macd_value:        MACD line value
        signal_value:      Signal line value
        histogram:         Current histogram bar
        hist_direction:    'RISING', 'FALLING', or 'FLAT'
        crossover:         'BULLISH_CROSS', 'BEARISH_CROSS', or 'NONE'
        macd_above_signal: True if MACD line > Signal line
        component_score:   Sub-score contribution (0 to weight)
    """
    macd_value: float
    signal_value: float
    histogram: float
    hist_direction: str
    crossover: str
    macd_above_signal: bool
    component_score: float = 0.0


@dataclass
class BollingerSignal:
    """
    Bollinger Bands signal.

    Key metrics:
        %B = (Price − Lower) / (Upper − Lower)
            0 → at lower band, 0.5 → at SMA, 1.0 → at upper band
        Bandwidth = (Upper − Lower) / Middle × 100

    Attributes:
        upper:            Upper Bollinger Band
        middle:           Middle Band (SMA)
        lower:            Lower Bollinger Band
        percent_b:        %B value
        bandwidth:        Normalised bandwidth
        component_score:  Sub-score contribution (0 to weight)
    """
    upper: float
    middle: float
    lower: float
    percent_b: float
    bandwidth: float
    component_score: float = 0.0


@dataclass
class ADXSignal:
    """
    Average Directional Index (ADX) signal.

    Attributes:
        value:            Current ADX value
        trend_strength:   Label (e.g., 'WEAK', 'MODERATE', 'STRONG')
        component_score:  Sub-score contribution (0 to weight)
    """
    value: float
    trend_strength: str
    component_score: float = 0.0


@dataclass
class VolumeSignal:
    """
    Volume analysis signal.

    Attributes:
        relative_volume:  Current volume / 20-day SMA volume
        is_elevated:      True if relative_volume > 1.25
        adjustment:       Score adjustment (+/- points) based on volume strength
    """
    relative_volume: float
    is_elevated: bool
    adjustment: float = 0.0


@dataclass
class SuggestedStrikes:
    """
    Dynamic strike recommendations based on volatility bands.
    """
    short_strike: float
    long_strike: float
    description: str


@dataclass
class ConvictionResult:
    """
    Final output of the Spread Conviction Engine.

    Attributes:
        ticker:           Symbol analysed
        strategy:         Strategy type string
        strategy_label:   Human-friendly strategy name
        price:            Latest closing price
        conviction_score: Aggregate score (0–100)
        tier:             Action tier (WAIT / WATCH / PREPARE / EXECUTE)
        trend_bias:       Overall qualitative trend assessment
        volume:           Volume strength signal
        strikes:          Recommended short/long strikes
        data_quality:     Assessment of input data (HIGH, MEDIUM, LOW)
        rationale:        Human-readable explanation of the score
    """
    ticker: str
    strategy: str
    strategy_label: str
    price: float
    conviction_score: float
    tier: str
    trend_bias: str
    ichimoku: IchimokuSignal
    rsi: RSISignal
    macd: MACDSignal
    bollinger: BollingerSignal
    adx: ADXSignal
    volume: VolumeSignal
    strikes: SuggestedStrikes
    data_quality: str = "HIGH"
    rationale: list = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary (JSON-safe)."""
        return asdict(self)


# =============================================================================
# Data Fetching
# =============================================================================

def fetch_ohlcv(ticker: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """
    Download OHLCV data from Yahoo Finance.

    Parameters:
        ticker:   Stock symbol (e.g. 'AAPL', 'SPY')
        period:   Lookback period ('6mo', '1y', '2y', '5y', 'max').
                  Default '2y' ensures sufficient data for extended Ichimoku.
        interval: Candle interval ('1h', '1d', '1wk')

    Returns:
        pd.DataFrame with columns: Open, High, Low, Close, Volume

    Raises:
        ValueError: If no data is returned for the given ticker or invalid ticker format,
                   or if period/interval are not valid Yahoo Finance values.
    """
    # Validate ticker format (1-5 uppercase letters)
    if not re.match(r'^[A-Z]{1,5}$', ticker.upper()):
        raise ValueError(f"Invalid ticker format: '{ticker}'. Expected 1-5 uppercase letters (e.g., AAPL, SPY)")
    
    # Validate period and interval
    valid_periods = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
    valid_intervals = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"}
    
    if period not in valid_periods:
        raise ValueError(f"Invalid period: {period}. Must be one of {valid_periods}")
    if interval not in valid_intervals:
        raise ValueError(f"Invalid interval: {interval}. Must be one of {valid_intervals}")

    df = yf.download(ticker, period=period, interval=interval, progress=False)

    if df.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'. "
                         f"Check symbol validity and market hours.")

    # Flatten MultiIndex columns that yfinance sometimes creates
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


# =============================================================================
# Indicator Computation
# =============================================================================

def compute_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Ichimoku Kinko Hyo indicators and merge into the DataFrame.

    Column names are auto-generated by pandas_ta based on parameter values:
        ITS_20, IKS_60, ISA_20, ISB_60, ICS_60
    """
    ichimoku_df, _ = ta.ichimoku(
        df["High"], df["Low"], df["Close"],
        tenkan=ICHIMOKU_TENKAN,
        kijun=ICHIMOKU_KIJUN,
        senkou=ICHIMOKU_SENKOU,
    )
    return pd.concat([df, ichimoku_df], axis=1)


def compute_rsi(df: pd.DataFrame) -> pd.DataFrame:
    """Compute RSI and add as a column."""
    df["RSI"] = ta.rsi(df["Close"], length=RSI_LENGTH)
    return df


def compute_macd(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute MACD (line, signal, histogram) and merge into the DataFrame.

    Adds columns: MACD_12_26_9, MACDs_12_26_9, MACDh_12_26_9
    """
    macd_df = ta.macd(df["Close"], fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    return pd.concat([df, macd_df], axis=1)


def compute_bbands(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Bollinger Bands and merge into the DataFrame.

    Adds columns: BBL_{l}_{s}_{s}, BBM_{l}_{s}_{s}, BBU_{l}_{s}_{s},
                  BBB_{l}_{s}_{s} (bandwidth), BBP_{l}_{s}_{s} (%B)
    """
    bbands_df = ta.bbands(df["Close"], length=BBANDS_LENGTH, std=BBANDS_STD)
    return pd.concat([df, bbands_df], axis=1)


def compute_adx(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute ADX and merge into the DataFrame.
    Adds columns: ADX_14, DMP_14, DMN_14
    """
    adx_df = ta.adx(df["High"], df["Low"], df["Close"], length=ADX_LENGTH)
    return pd.concat([df, adx_df], axis=1)


def compute_volume_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute relative volume stats.
    """
    df["VOL_SMA"] = ta.sma(df["Volume"], length=VOLUME_WINDOW)
    df["REL_VOL"] = df["Volume"] / df["VOL_SMA"]
    return df


def validate_indicator_columns(df: pd.DataFrame) -> None:
    """
    Validate that all expected indicator columns exist after computation.
    Raises ValueError with descriptive message if columns are missing.
    """
    required_cols = {
        "ichimoku": [
            f"ITS_{ICHIMOKU_TENKAN}",
            f"IKS_{ICHIMOKU_KIJUN}",
            f"ISA_{ICHIMOKU_TENKAN}",
            f"ISB_{ICHIMOKU_KIJUN}",
        ],
        "rsi": ["RSI"],
        "macd": [
            f"MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}",
            f"MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}",
            f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}",
        ],
        "bollinger": [
            f"BBL_{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}",
            f"BBM_{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}",
            f"BBU_{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}",
            f"BBB_{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}",
            f"BBP_{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}",
        ],
        "adx": [f"ADX_{ADX_LENGTH}"],
        "volume": ["VOL_SMA", "REL_VOL"],
    }

    missing = []
    for indicator, cols in required_cols.items():
        for col in cols:
            if col not in df.columns:
                missing.append(f"{indicator}:{col}")

    if missing:
        raise ValueError(
            f"Missing expected indicator columns: {', '.join(missing)}. "
            f"This may indicate a pandas_ta version change or insufficient data. "
            f"Expected columns are based on pandas_ta naming conventions."
        )


def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline: compute every indicator in sequence.

    Single entry point for indicator computation.
    """
    df = compute_ichimoku(df)
    df = compute_rsi(df)
    df = compute_macd(df)
    df = compute_bbands(df)
    df = compute_adx(df)
    df = compute_volume_stats(df)

    # Validate all expected columns exist
    validate_indicator_columns(df)

    return df


# =============================================================================
# Signal Scoring Functions — Strategy-Aware
# =============================================================================
# Each function extracts relevant indicator values, computes a normalised
# sub-score (0.0–1.0), and scales it by the strategy-specific component
# weight.  The sub-score represents "how favourable are conditions for the
# SELECTED STRATEGY from this indicator's perspective?"
# =============================================================================

def score_ichimoku(
    df: pd.DataFrame,
    price: float,
    strategy: StrategyType,
    weights: StrategyWeights,
) -> IchimokuSignal:
    """
    Score Ichimoku signal for the given strategy.

    Bullish strategies (bull_put, bull_call):
        Price above cloud, bullish TK cross, green cloud = high score.

    Bearish strategies (bear_call, bear_put):
        Price below cloud, bearish TK cross, red cloud = high score.

    Sub-Signal Weights (internal):
    ┌──────────────────────────────┬────────┐
    │ Price vs Cloud               │ 0.40   │
    │ TK Cross direction           │ 0.25   │
    │ Cloud colour                 │ 0.20   │
    │ Cloud thickness (normalised) │ 0.15   │
    └──────────────────────────────┴────────┘

    Parameters:
        df:       DataFrame with Ichimoku columns
        price:    Current closing price
        strategy: Active strategy
        weights:  Component weights for this strategy

    Returns:
        IchimokuSignal with populated component_score
    """
    latest = df.iloc[-1]

    # Dynamic column names from constants (pandas_ta naming convention)
    tenkan = float(latest[f"ITS_{ICHIMOKU_TENKAN}"])
    kijun = float(latest[f"IKS_{ICHIMOKU_KIJUN}"])
    senkou_a = float(latest[f"ISA_{ICHIMOKU_TENKAN}"])
    senkou_b = float(latest[f"ISB_{ICHIMOKU_KIJUN}"])

    cloud_top = max(senkou_a, senkou_b)
    cloud_bottom = min(senkou_a, senkou_b)
    cloud_green = senkou_a > senkou_b

    # --- Sub-signal: Price vs Cloud ---
    if price > cloud_top:
        cloud_status = "ABOVE"
    elif price < cloud_bottom:
        cloud_status = "BELOW"
    else:
        cloud_status = "INSIDE"

    if strategy.is_bullish:
        # Bullish: above cloud = good
        price_cloud_score = {"ABOVE": 1.0, "INSIDE": 0.3, "BELOW": 0.0}[cloud_status]
    else:
        # Bearish: below cloud = good
        price_cloud_score = {"BELOW": 1.0, "INSIDE": 0.3, "ABOVE": 0.0}[cloud_status]

    # --- Sub-signal: TK Cross ---
    tk_bullish = tenkan > kijun
    tk_label = "BULLISH" if tk_bullish else "BEARISH"

    if strategy.is_bullish:
        tk_score = 1.0 if tk_bullish else 0.0
    else:
        tk_score = 0.0 if tk_bullish else 1.0

    # --- Sub-signal: Cloud Colour ---
    cloud_color_label = "GREEN" if cloud_green else "RED"

    if strategy.is_bullish:
        cloud_score = 1.0 if cloud_green else 0.0
    else:
        cloud_score = 0.0 if cloud_green else 1.0

    # --- Sub-signal: Cloud Thickness ---
    # Normalise thickness relative to price; 5% of price = max score.
    thickness = abs(senkou_a - senkou_b)
    thickness_pct = (thickness / price) if price > 0 else 0.0
    thickness_score = min(thickness_pct / 0.05, 1.0)

    # Penalise thick cloud that works AGAINST the strategy direction.
    # For bullish strategies: thick red cloud is resistance (bad).
    # For bearish strategies: thick green cloud is support (bad).
    if strategy.is_bullish and not cloud_green:
        thickness_score *= 0.3
    elif strategy.is_bearish and cloud_green:
        thickness_score *= 0.3

    # --- Weighted combination ---
    raw = (
        0.40 * price_cloud_score
        + 0.25 * tk_score
        + 0.20 * cloud_score
        + 0.15 * thickness_score
    )
    component_score = round(raw * weights.ichimoku, 2)

    return IchimokuSignal(
        price_vs_cloud=cloud_status,
        tk_cross=tk_label,
        cloud_color=cloud_color_label,
        cloud_thickness=round(thickness, 4),
        tenkan=round(tenkan, 2),
        kijun=round(kijun, 2),
        senkou_a=round(senkou_a, 2),
        senkou_b=round(senkou_b, 2),
        component_score=component_score,
    )


def score_rsi(
    df: pd.DataFrame,
    strategy: StrategyType,
    weights: StrategyWeights,
) -> RSISignal:
    """
    Score RSI for the given strategy using a lookup table for contiguous ranges.
    """
    rsi_val = float(df.iloc[-1]["RSI"])

    # Lookup tables: (min_inclusive, max_exclusive, score, label)
    # The last entry in each list uses a high max (101) to cover up to 100.
    # We sort them by min_inclusive to ensure predictable lookup.
    tables = {
        StrategyType.BULL_PUT: [
            (0,  25, 0.10, "EXTREME_OVERSOLD (<25)"),
            (25, 30, 0.40, "DEEP_OVERSOLD (25-30)"),
            (30, 45, 1.00, "OVERSOLD_BOUNCE (30-45)"),
            (45, 55, 0.80, "NEUTRAL_BULLISH (45-55)"),
            (55, 65, 0.60, "BULLISH (55-65)"),
            (65, 75, 0.30, "OVERBOUGHT_CAUTION (65-75)"),
            (75, 101, 0.10, "EXTREME_OVERBOUGHT (>75)"),
        ],
        StrategyType.BEAR_CALL: [
            (0,  25, 0.10, "EXTREME_OVERSOLD (<25)"),
            (25, 35, 0.30, "OVERSOLD_CAUTION (25-35)"),
            (35, 45, 0.60, "BEARISH (35-45)"),
            (45, 55, 0.80, "NEUTRAL_BEARISH (45-55)"),
            (55, 70, 1.00, "OVERBOUGHT_REJECTION (55-70)"),
            (70, 75, 0.40, "DEEP_OVERBOUGHT (70-75)"),
            (75, 101, 0.10, "EXTREME_OVERBOUGHT (>75)"),
        ],
        StrategyType.BULL_CALL: [
            (0,  35, 0.05, "WRONG_DIRECTION (<35)"),
            (35, 45, 0.25, "WEAK_MOMENTUM (35-45)"),
            (45, 55, 0.70, "BUILDING_MOMENTUM (45-55)"),
            (55, 70, 1.00, "STRONG_BULLISH_MOMENTUM (55-70)"),
            (70, 80, 0.50, "VERY_STRONG (70-80)"),
            (80, 101, 0.15, "PARABOLIC_RISK (>80)"),
        ],
        StrategyType.BEAR_PUT: [
            (0,  20, 0.15, "CAPITULATION_RISK (<20)"),
            (20, 30, 0.50, "VERY_STRONG_BEARISH (20-30)"),
            (30, 45, 1.00, "STRONG_BEARISH_MOMENTUM (30-45)"),
            (45, 55, 0.70, "BUILDING_BEARISH (45-55)"),
            (55, 65, 0.25, "WEAK_BEARISH (55-65)"),
            (65, 101, 0.05, "WRONG_DIRECTION (>65)"),
        ]
    }

    raw, zone = 0.0, "UNKNOWN"
    for (low, high, score, label) in tables[strategy]:
        if low <= rsi_val < high:
            raw, zone = score, label
            break

    component_score = round(raw * weights.rsi, 2)

    return RSISignal(
        value=round(rsi_val, 2),
        zone=zone,
        component_score=component_score,
    )


def _detect_crossover(df: pd.DataFrame, macd_col: str, signal_col: str, lookback: int = 3) -> tuple[str, bool, bool]:
    """
    Detect MACD/Signal crossover within the last ``lookback`` bars.

    Returns:
        Tuple of (crossover_label, is_bullish_cross, is_bearish_cross)
    """
    n = min(lookback + 1, len(df))
    for i in range(2, n + 1):
        row_curr = df.iloc[-i + 1]
        row_prev = df.iloc[-i]
        prev_macd = float(row_prev[macd_col])
        prev_sig = float(row_prev[signal_col])
        curr_macd = float(row_curr[macd_col])
        curr_sig = float(row_curr[signal_col])

        if prev_macd <= prev_sig and curr_macd > curr_sig:
            return "BULLISH_CROSS", True, False
        elif prev_macd >= prev_sig and curr_macd < curr_sig:
            return "BEARISH_CROSS", False, True

    return "NONE", False, False


def score_macd(
    df: pd.DataFrame,
    price: float,
    strategy: StrategyType,
    weights: StrategyWeights,
) -> MACDSignal:
    """
    Score MACD for the given strategy.

    Credit strategies (mean reversion) focus on *decelerating* adverse
    momentum — a rising histogram in a dip (bull_put) or a falling
    histogram in a rally (bear_call).

    Debit strategies (breakout) focus on *accelerating* favourable
    momentum — both the MACD line position and histogram strength matter.

    ── Credit Sub-Signal Weights ──────────────────────────────────────
    │ MACD vs Signal (favourable side)   │ 0.40                       │
    │ Histogram direction (decelerating) │ 0.35                       │
    │ Recent favourable crossover        │ 0.25                       │
    ──────────────────────────────────────────────────────────────────

    ── Debit Sub-Signal Weights ───────────────────────────────────────
    │ MACD vs Signal + zero-line         │ 0.30                       │
    │ Histogram strength (dir + sign)    │ 0.45                       │
    │ Recent favourable crossover        │ 0.25                       │
    ──────────────────────────────────────────────────────────────────

    Parameters:
        df:       DataFrame with MACD columns
        strategy: Active strategy
        weights:  Component weights for this strategy

    Returns:
        MACDSignal with populated component_score
    """
    macd_col = f"MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"
    signal_col = f"MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"
    hist_col = f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    macd_val = float(latest[macd_col])
    signal_val = float(latest[signal_col])
    hist_val = float(latest[hist_col])
    prev_hist = float(prev[hist_col])

    macd_above = macd_val > signal_val

    # --- Histogram direction ---
    # Threshold for FLAT is relative to price (0.01%)
    hist_diff = hist_val - prev_hist
    threshold = price * 0.0001
    if abs(hist_diff) < threshold:
        hist_direction = "FLAT"
    elif hist_diff > 0:
        hist_direction = "RISING"
    else:
        hist_direction = "FALLING"

    # --- Crossover detection ---
    crossover_label, is_bull_cross, is_bear_cross = _detect_crossover(
        df, macd_col, signal_col, lookback=3
    )

    # --- Strategy-specific scoring ---
    if strategy.is_credit:
        # ── Credit: Mean Reversion ───────────────────────────────────
        # bull_put wants: MACD above signal, rising histogram, bullish cross
        # bear_call wants: MACD below signal, falling histogram, bearish cross
        if strategy.is_bullish:
            # bull_put
            above_score = 1.0 if macd_above else 0.0
            hist_dir_score = (
                1.0 if hist_direction == "RISING"
                else 0.4 if hist_direction == "FLAT"
                else 0.0
            )
            cross_score = (
                1.0 if is_bull_cross
                else 0.0 if is_bear_cross
                else 0.2
            )
        else:
            # bear_call (inverted)
            above_score = 0.0 if macd_above else 1.0
            hist_dir_score = (
                1.0 if hist_direction == "FALLING"
                else 0.4 if hist_direction == "FLAT"
                else 0.0
            )
            cross_score = (
                1.0 if is_bear_cross
                else 0.0 if is_bull_cross
                else 0.2
            )

        raw = (
            0.40 * above_score
            + 0.35 * hist_dir_score
            + 0.25 * cross_score
        )

    else:
        # ── Debit: Breakout / Momentum ───────────────────────────────
        # Needs strong, *accelerating* directional momentum.
        if strategy.is_bullish:
            # bull_call
            # Sub-signal 1: MACD above signal + positive territory
            if macd_above and macd_val > 0:
                position_score = 1.0
            elif macd_above and macd_val <= 0:
                position_score = 0.5
            else:
                position_score = 0.0

            # Sub-signal 2: Histogram positive AND rising
            if hist_val > 0 and hist_direction == "RISING":
                hist_strength_score = 1.0
            elif hist_val > 0 and hist_direction == "FALLING":
                hist_strength_score = 0.35
            elif hist_val <= 0 and hist_direction == "RISING":
                hist_strength_score = 0.25
            else:  # negative and falling
                hist_strength_score = 0.0

            # Sub-signal 3: Crossover
            cross_score = (
                1.0 if is_bull_cross
                else 0.0 if is_bear_cross
                else 0.15
            )
        else:
            # bear_put (mirror of bull_call)
            # Sub-signal 1: MACD below signal + negative territory
            if not macd_above and macd_val < 0:
                position_score = 1.0
            elif not macd_above and macd_val >= 0:
                position_score = 0.5
            else:
                position_score = 0.0

            # Sub-signal 2: Histogram negative AND falling
            if hist_val < 0 and hist_direction == "FALLING":
                hist_strength_score = 1.0
            elif hist_val < 0 and hist_direction == "RISING":
                hist_strength_score = 0.35
            elif hist_val >= 0 and hist_direction == "FALLING":
                hist_strength_score = 0.25
            else:  # positive and rising
                hist_strength_score = 0.0

            # Sub-signal 3: Crossover
            cross_score = (
                1.0 if is_bear_cross
                else 0.0 if is_bull_cross
                else 0.15
            )

        raw = (
            0.30 * position_score
            + 0.45 * hist_strength_score
            + 0.25 * cross_score
        )

    component_score = round(raw * weights.macd, 2)

    return MACDSignal(
        macd_value=round(macd_val, 4),
        signal_value=round(signal_val, 4),
        histogram=round(hist_val, 4),
        hist_direction=hist_direction,
        crossover=crossover_label,
        macd_above_signal=macd_above,
        component_score=component_score,
    )


def score_bollinger(
    df: pd.DataFrame,
    strategy: StrategyType,
    weights: StrategyWeights,
) -> BollingerSignal:
    """
    Score Bollinger Bands for the given strategy.

    Credit strategies want price near a band (support/resistance) with
    *moderate* bandwidth — the mean-reversion sweet spot.

    Debit strategies want price pushing through a band with *expanding*
    bandwidth — confirming a genuine breakout, not a false signal.

    ── bull_put %B (Credit) ───────────────────────────────────────────
    │ 0.20–0.45 → 1.00  Near lower band, holding. Ideal support.      │
    │ 0.45–0.60 → 0.80  Near middle band. Balanced.                    │
    │ 0.10–0.20 → 0.55  Testing lower band. Could bounce or break.    │
    │ 0.60–0.80 → 0.50  Upper half. Less margin of safety.             │
    │ < 0.10    → 0.15  Breaking below bands. Breakdown risk.          │
    │ > 0.80    → 0.25  Near upper band. Overextended.                  │
    ────────────────────────────────────────────────────────────────────

    ── bear_call %B (Credit) ──────────────────────────────────────────
    │ 0.55–0.80 → 1.00  Near upper band, rejecting. Ideal resistance.  │
    │ 0.40–0.55 → 0.80  Near middle band. Balanced.                    │
    │ 0.80–0.90 → 0.55  Testing upper band. Could reject or break.    │
    │ 0.20–0.40 → 0.50  Lower half. Less margin of safety.             │
    │ > 0.90    → 0.15  Breaking above bands. Breakout risk.           │
    │ < 0.20    → 0.25  Near lower band. Move already made.             │
    ────────────────────────────────────────────────────────────────────

    ── bull_call %B (Debit) ───────────────────────────────────────────
    │ > 0.80    → 1.00  Breaking above upper band. Strong breakout.    │
    │ 0.60–0.80 → 0.85  Upper half, pushing higher. Good.              │
    │ 0.45–0.60 → 0.50  Middle zone. Not yet breaking out.             │
    │ 0.20–0.45 → 0.20  Lower half. Wrong direction.                   │
    │ < 0.20    → 0.05  Near lower band. Completely wrong.              │
    ────────────────────────────────────────────────────────────────────

    ── bear_put %B (Debit) ────────────────────────────────────────────
    │ < 0.20    → 1.00  Breaking below lower band. Strong breakdown.   │
    │ 0.20–0.40 → 0.85  Lower half, pushing lower. Good.               │
    │ 0.40–0.55 → 0.50  Middle zone. Not yet breaking down.            │
    │ 0.55–0.80 → 0.20  Upper half. Wrong direction.                   │
    │ > 0.80    → 0.05  Near upper band. Completely wrong.              │
    ────────────────────────────────────────────────────────────────────

    Bandwidth Scoring:
        Credit:  Moderate (3–10) is ideal; extremes are penalised.
        Debit:   Expanding (>7) is ideal; tight squeezes are uncertain.

    Parameters:
        df:       DataFrame with Bollinger Band columns
        strategy: Active strategy
        weights:  Component weights for this strategy

    Returns:
        BollingerSignal with populated component_score
    """
    bb_suffix = f"{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}"
    latest = df.iloc[-1]

    upper = float(latest[f"BBU_{bb_suffix}"])
    middle = float(latest[f"BBM_{bb_suffix}"])
    lower = float(latest[f"BBL_{bb_suffix}"])
    percent_b = float(latest[f"BBP_{bb_suffix}"])
    bandwidth = float(latest[f"BBB_{bb_suffix}"])

    # --- Sub-signal 1: %B positioning (strategy-specific) ---

    if strategy == StrategyType.BULL_PUT:
        if 0.20 <= percent_b <= 0.45:
            pctb_score = 1.00
        elif 0.45 < percent_b <= 0.60:
            pctb_score = 0.80
        elif 0.10 <= percent_b < 0.20:
            pctb_score = 0.55
        elif 0.60 < percent_b <= 0.80:
            pctb_score = 0.50
        elif percent_b < 0.10:
            pctb_score = 0.15
        else:  # > 0.80
            pctb_score = 0.25

    elif strategy == StrategyType.BEAR_CALL:
        if 0.55 <= percent_b <= 0.80:
            pctb_score = 1.00
        elif 0.40 <= percent_b < 0.55:
            pctb_score = 0.80
        elif 0.80 < percent_b <= 0.90:
            pctb_score = 0.55
        elif 0.20 <= percent_b < 0.40:
            pctb_score = 0.50
        elif percent_b > 0.90:
            pctb_score = 0.15
        else:  # < 0.20
            pctb_score = 0.25

    elif strategy == StrategyType.BULL_CALL:
        if percent_b > 0.80:
            pctb_score = 1.00
        elif 0.60 <= percent_b <= 0.80:
            pctb_score = 0.85
        elif 0.45 <= percent_b < 0.60:
            pctb_score = 0.50
        elif 0.20 <= percent_b < 0.45:
            pctb_score = 0.20
        else:  # < 0.20
            pctb_score = 0.05

    else:  # BEAR_PUT
        if percent_b < 0.20:
            pctb_score = 1.00
        elif 0.20 <= percent_b <= 0.40:
            pctb_score = 0.85
        elif 0.40 < percent_b <= 0.55:
            pctb_score = 0.50
        elif 0.55 < percent_b <= 0.80:
            pctb_score = 0.20
        else:  # > 0.80
            pctb_score = 0.05

    # --- Sub-signal 2: Bandwidth regime (credit vs debit) ---

    if strategy.is_credit:
        # Credit: moderate bandwidth is ideal (3–10%)
        if 3.0 <= bandwidth <= 10.0:
            bw_score = 1.0
        elif 10.0 < bandwidth <= 15.0:
            bw_score = 0.6   # Expanding — move already happening
        elif 2.0 <= bandwidth < 3.0:
            bw_score = 0.5   # Squeeze — direction uncertain
        elif bandwidth > 15.0:
            bw_score = 0.3   # Extreme expansion
        else:  # < 2.0
            bw_score = 0.3   # Very tight squeeze
    else:
        # Debit: expanding bandwidth confirms breakout
        if bandwidth > 10.0:
            bw_score = 1.0   # Strong expansion — breakout confirmed
        elif 7.0 <= bandwidth <= 10.0:
            bw_score = 0.80  # Starting to expand
        elif 3.0 <= bandwidth < 7.0:
            bw_score = 0.50  # Moderate — could go either way
        elif 2.0 <= bandwidth < 3.0:
            bw_score = 0.30  # Squeeze — breakout direction unknown
        else:  # < 2.0
            bw_score = 0.20  # Extremely tight — no momentum confirmation

    # --- Weighted combination ---
    # Credit: %B matters more (positioning for mean reversion)
    # Debit:  bandwidth matters more (confirming breakout strength)
    if strategy.is_credit:
        raw = 0.65 * pctb_score + 0.35 * bw_score
    else:
        raw = 0.55 * pctb_score + 0.45 * bw_score

    component_score = round(raw * weights.bollinger, 2)

    return BollingerSignal(
        upper=round(upper, 2),
        middle=round(middle, 2),
        lower=round(lower, 2),
        percent_b=round(percent_b, 4),
        bandwidth=round(bandwidth, 4),
        component_score=component_score,
    )


def score_adx(
    df: pd.DataFrame,
    strategy: StrategyType,
    weights: StrategyWeights,
) -> ADXSignal:
    """
    Score ADX for the given strategy.

    ADX measures trend strength, regardless of direction.
    - ADX > 25: Strong trend
    - ADX < 20: Weak trend / range-bound

    Scoring logic:
    - If strategy is CREDIT (mean reversion):
        Likes moderate ADX (15-25). Too high (>35) means trend is too strong
        to fade. Too low (<15) means no clear structure.
    - If strategy is DEBIT (breakout):
        Likes rising and strong ADX (>25).

    Returns:
        ADXSignal with populated component_score
    """
    latest = df.iloc[-1]
    adx_val = float(latest[f"ADX_{ADX_LENGTH}"])

    if adx_val >= 40:
        strength = "VERY_STRONG"
    elif adx_val >= 25:
        strength = "STRONG"
    elif adx_val >= 20:
        strength = "MODERATE"
    else:
        strength = "WEAK"

    if strategy.is_credit:
        # Credit likes moderate trend strength
        if 15 <= adx_val <= 30:
            raw = 1.0
        elif 30 < adx_val <= 40:
            raw = 0.6
        elif 10 <= adx_val < 15:
            raw = 0.5
        elif adx_val > 40:
            raw = 0.2  # Trend too strong to fade
        else:
            raw = 0.1
    else:
        # Debit likes strong trend strength
        if adx_val >= 25:
            raw = 1.0
        elif 20 <= adx_val < 25:
            raw = 0.7
        elif 15 <= adx_val < 20:
            raw = 0.4
        else:
            raw = 0.1

    component_score = round(raw * weights.adx, 2)

    return ADXSignal(
        value=round(adx_val, 2),
        trend_strength=strength,
        component_score=component_score,
    )


def score_volume(df: pd.DataFrame, strategy: StrategyType) -> VolumeSignal:
    """
    Determine volume adjustment for conviction.
    Breakouts (debit) require high volume confirmation.
    Mean-reversion (credit) benefits from low-volume exhaustion at levels.

    Returns an adjustment factor (±10 points max) rather than a multiplier
    to prevent volume from masking weak indicator signals.
    """
    rv = float(df.iloc[-1]["REL_VOL"])
    elevated = rv > 1.25

    # Base adjustment is 0 (no change)
    adjustment = 0.0

    if strategy.is_debit:
        # Debit: breakout needs volume confirmation
        if rv > 1.5:
            adjustment = 10.0  # Strong confirmation
        elif rv > 1.25:
            adjustment = 5.0   # Moderate confirmation
        elif rv < 0.75:
            adjustment = -10.0 # Weak volume, questionable breakout
        elif rv < 1.0:
            adjustment = -5.0  # Below average volume
    else:
        # Credit: mean-reversion likes volume exhaustion (low volume)
        if rv < 0.75:
            adjustment = 10.0  # Exhaustion at support/resistance
        elif rv < 1.0:
            adjustment = 5.0   # Below average
        elif rv > 1.5:
            adjustment = -10.0 # High volume move may continue
        elif rv > 1.25:
            adjustment = -5.0  # Elevated volume caution

    return VolumeSignal(
        relative_volume=round(rv, 2),
        is_elevated=elevated,
        adjustment=adjustment
    )


def calculate_strikes(
    price: float,
    strategy: StrategyType,
    bollinger: BollingerSignal
) -> SuggestedStrikes:
    """
    Calculate dynamic strikes based on 1-sigma Bollinger levels.
    Uses BBM (SMA) and bands to find logical targets.

    For credit spreads (bull_put, bear_call):
        short_strike = strike you SELL (collect premium)
        long_strike = strike you BUY (pay premium) for protection

    For debit spreads (bull_call, bear_put):
        long_strike = strike you BUY (pay premium, directional bet)
        short_strike = strike you SELL (collect premium) to reduce cost
    """
    if strategy == StrategyType.BULL_PUT:
        # SELL put at support (BBL), BUY put further OTM for protection
        short_strike_price = bollinger.lower
        long_strike_price = short_strike_price - (price * 0.02)
        desc = "SELL put at support (BBL), BUY put 2% below for protection."
    elif strategy == StrategyType.BEAR_CALL:
        # SELL call at resistance (BBU), BUY call further OTM for protection
        short_strike_price = bollinger.upper
        long_strike_price = short_strike_price + (price * 0.02)
        desc = "SELL call at resistance (BBU), BUY call 2% above for protection."
    elif strategy == StrategyType.BULL_CALL:
        # BUY call at middle band (lower strike), SELL call at upper band (higher strike)
        long_strike_price = bollinger.middle   # Buy lower strike
        short_strike_price = bollinger.upper   # Sell higher strike
        desc = "BUY call at middle band (lower), SELL call at upper band (higher)."
    else:  # BEAR_PUT
        # BUY put at middle band (higher strike), SELL put at lower band (lower strike)
        long_strike_price = bollinger.middle   # Buy higher strike
        short_strike_price = bollinger.lower   # Sell lower strike
        desc = "BUY put at middle band (higher), SELL put at lower band (lower)."

    return SuggestedStrikes(
        short_strike=round(short_strike_price, 2),
        long_strike=round(long_strike_price, 2),
        description=desc
    )


# =============================================================================
# Trend Classification (Objective — Strategy-Independent)
# =============================================================================

def classify_trend(ichimoku: IchimokuSignal, macd: MACDSignal) -> TrendBias:
    """
    Synthesise Ichimoku and MACD into an overall trend classification.

    This is an *objective* market read — independent of the chosen strategy.
    The conviction score captures whether the trend is *favourable* for a
    given strategy; this function simply labels what the trend IS.

    Logic:
        STRONG_BULL = Above cloud + Bullish TK + MACD above signal + Rising hist
        BULL        = Above cloud + at least one MACD condition
        NEUTRAL     = Mixed signals or inside cloud
        BEAR        = Below cloud + one bearish MACD signal
        STRONG_BEAR = Below cloud + Bearish TK + MACD below + Falling hist
    """
    bull_points = 0

    if ichimoku.price_vs_cloud == "ABOVE":
        bull_points += 2
    elif ichimoku.price_vs_cloud == "INSIDE":
        bull_points += 1

    if ichimoku.tk_cross == "BULLISH":
        bull_points += 1

    if macd.macd_above_signal:
        bull_points += 1

    if macd.hist_direction == "RISING":
        bull_points += 1

    if bull_points >= 5:
        return TrendBias.STRONG_BULL
    elif bull_points >= 3:
        return TrendBias.BULL
    elif bull_points >= 2:
        return TrendBias.NEUTRAL
    elif bull_points >= 1:
        return TrendBias.BEAR
    else:
        return TrendBias.STRONG_BEAR


# =============================================================================
# Rationale Builder
# =============================================================================

def build_rationale(
    strategy: StrategyType,
    weights: StrategyWeights,
    ichimoku: IchimokuSignal,
    rsi: RSISignal,
    macd: MACDSignal,
    bollinger: BollingerSignal,
    adx: ADXSignal,
    volume: VolumeSignal,
    strikes: SuggestedStrikes,
    trend: TrendBias,
    score: float,
    tier: ConvictionTier,
) -> list[str]:
    """
    Generate a human-readable rationale explaining the conviction score.
    """
    lines: list[str] = []

    # Strategy header
    lines.append(f"Strategy: {strategy.label}  ({strategy.philosophy})")
    lines.append(f"Ideal Setup: {strategy.ideal_setup}")
    lines.append("")
    lines.append(f"Market Trend: {trend.value} | Score: {score:.1f}/100 → {tier.value}")

    # ADX Gate check
    if strategy.is_credit and adx.value < 20:
        lines.append("WARNING: TREND STRENGTH GATE: ADX < 20. Credit spread capped at WATCH tier.")

    # Volume check
    vol_status = "ELEVATED" if volume.is_elevated else "NORMAL"
    adj_sign = "+" if volume.adjustment >= 0 else ""
    if strategy.is_debit and volume.is_elevated:
        lines.append(f"Volume: {vol_status} (RV={volume.relative_volume}) - Breakthrough confirmed ({adj_sign}{volume.adjustment:.0f})")
    elif strategy.is_credit and volume.relative_volume < 0.8:
        lines.append(f"Volume: EXHAUSTED (RV={volume.relative_volume}) - Level holding ({adj_sign}{volume.adjustment:.0f})")
    else:
        lines.append(f"Volume: {vol_status} (RV={volume.relative_volume}) ({adj_sign}{volume.adjustment:.0f})")

    # Trend alignment check
    if strategy.is_bullish and trend.value in ("STRONG_BULL", "BULL"):
        lines.append("Trend aligns with bullish strategy")
    elif strategy.is_bearish and trend.value in ("STRONG_BEAR", "BEAR"):
        lines.append("Trend aligns with bearish strategy")
    elif trend.value == "NEUTRAL":
        lines.append("Trend is neutral - mixed alignment")
    else:
        lines.append("ALERT: Trend opposes strategy direction - Conflict penalty applied")
    lines.append("")

    # Strikes
    lines.append(f"Suggested Strikes: ${strikes.short_strike} / ${strikes.long_strike}")
    lines.append(f"Logic: {strikes.description}")
    lines.append("")

    # Ichimoku
    lines.append(f"[Ichimoku +{ichimoku.component_score:.1f}/{weights.ichimoku}]")
    if ichimoku.price_vs_cloud == "UNKNOWN":
        lines.append("  DATA MISSING - Component skipped")
    else:
        lines.append(f"  Price is {ichimoku.price_vs_cloud} the cloud")
        lines.append(f"  TK Cross: {ichimoku.tk_cross} "
                     f"(Tenkan {ichimoku.tenkan} vs Kijun {ichimoku.kijun})")
        lines.append(f"  Cloud: {ichimoku.cloud_color}, "
                     f"thickness {ichimoku.cloud_thickness:.2f}")

    # RSI
    lines.append(f"[RSI +{rsi.component_score:.1f}/{weights.rsi}]")
    if rsi.zone == "UNKNOWN":
        lines.append("  DATA MISSING - Component skipped")
    else:
        lines.append(f"  RSI({RSI_LENGTH}) = {rsi.value} -> {rsi.zone}")

    # MACD
    lines.append(f"[MACD +{macd.component_score:.1f}/{weights.macd}]")
    if macd.hist_direction == "UNKNOWN":
        lines.append("  DATA MISSING - Component skipped")
    else:
        direction = "above" if macd.macd_above_signal else "below"
        lines.append(f"  MACD {direction} Signal "
                     f"({macd.macd_value:.4f} vs {macd.signal_value:.4f})")
        lines.append(f"  Histogram: {macd.histogram:.4f} ({macd.hist_direction})")
        if macd.crossover != "NONE":
            lines.append(f"  Recent crossover: {macd.crossover}")

    # Bollinger
    lines.append(f"[Bollinger +{bollinger.component_score:.1f}/{weights.bollinger}]")
    if bollinger.middle == 0:
        lines.append("  DATA MISSING - Component skipped")
    else:
        lines.append(f"  %B = {bollinger.percent_b:.4f} | "
                     f"Bandwidth = {bollinger.bandwidth:.4f}")
        lines.append(f"  Bands: [{bollinger.lower:.2f} — "
                     f"{bollinger.middle:.2f} — {bollinger.upper:.2f}]")

    # ADX
    lines.append(f"[ADX +{adx.component_score:.1f}/{weights.adx}]")
    if adx.trend_strength == "UNKNOWN":
        lines.append("  DATA MISSING - Component skipped")
    else:
        lines.append(f"  ADX({ADX_LENGTH}) = {adx.value} ({adx.trend_strength})")

    return lines


# =============================================================================
# Analysis Engine — The Heart of the System
# =============================================================================

def analyse(
    ticker: str,
    strategy: StrategyType = StrategyType.BULL_PUT,
    period: str = "2y",
    interval: str = "1d",
) -> ConvictionResult:
    """
    Run the full conviction analysis pipeline for a single ticker.
    """
    weights = STRATEGY_WEIGHTS[strategy]

    # Step 1: Fetch data
    df = fetch_ohlcv(ticker, period=period, interval=interval)

    # Data sufficiency check for Ichimoku (requires ~180 periods for full ISA/ISB)
    min_periods = ICHIMOKU_SENKOU + ICHIMOKU_KIJUN
    if len(df) < min_periods:
        warnings.warn(f"Insufficient data for ticker {ticker}. "
                      f"Found {len(df)} rows, need {min_periods} for full "
                      f"Ichimoku cloud. Results may be skewed.")

    # Step 2: Compute indicators
    df = compute_all_indicators(df)

    # Step 3: Get current price
    price = round(float(df.iloc[-1]["Close"]), 2)

    # Step 4: Score each component (strategy-aware)
    # We detect NaNs BEFORE scoring and renormalize if necessary.
    
    latest = df.iloc[-1]
    
    # 1. Ichimoku
    ichimoku_cols = [f"ITS_{ICHIMOKU_TENKAN}", f"IKS_{ICHIMOKU_KIJUN}", f"ISA_{ICHIMOKU_TENKAN}", f"ISB_{ICHIMOKU_KIJUN}"]
    ichimoku_available = not latest[ichimoku_cols].isna().any()
    if ichimoku_available:
        ichimoku_sig = score_ichimoku(df, price, strategy, weights)
    else:
        ichimoku_sig = IchimokuSignal("UNKNOWN", "UNKNOWN", "UNKNOWN", 0, 0, 0, 0, 0, 0)

    # 2. RSI
    rsi_available = not pd.isna(latest["RSI"])
    if rsi_available:
        rsi_sig = score_rsi(df, strategy, weights)
    else:
        rsi_sig = RSISignal(0, "UNKNOWN", 0)

    # 3. MACD
    macd_cols = [f"MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}", f"MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"]
    macd_available = not latest[macd_cols].isna().any()
    if macd_available:
        macd_sig = score_macd(df, price, strategy, weights)
    else:
        macd_sig = MACDSignal(0, 0, 0, "UNKNOWN", "NONE", False, 0)

    # 4. Bollinger
    bb_suffix = f"{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}"
    bb_cols = [f"BBL_{bb_suffix}", f"BBM_{bb_suffix}", f"BBU_{bb_suffix}"]
    bollinger_available = not latest[bb_cols].isna().any()
    if bollinger_available:
        bollinger_sig = score_bollinger(df, strategy, weights)
    else:
        bollinger_sig = BollingerSignal(0, 0, 0, 0, 0, 0)

    # 5. ADX
    adx_available = not pd.isna(latest[f"ADX_{ADX_LENGTH}"])
    if adx_available:
        adx_sig = score_adx(df, strategy, weights)
    else:
        adx_sig = ADXSignal(0, "UNKNOWN", 0)

    # Volume (Adjustment, not a primary component)
    volume_sig = score_volume(df, strategy)

    # Renormalization logic
    total_score = 0.0
    total_weight_available = 0
    available_count = 0
    
    if ichimoku_available:
        total_score += ichimoku_sig.component_score
        total_weight_available += weights.ichimoku
        available_count += 1
    if rsi_available:
        total_score += rsi_sig.component_score
        total_weight_available += weights.rsi
        available_count += 1
    if macd_available:
        total_score += macd_sig.component_score
        total_weight_available += weights.macd
        available_count += 1
    if bollinger_available:
        total_score += bollinger_sig.component_score
        total_weight_available += weights.bollinger
        available_count += 1
    if adx_available:
        total_score += adx_sig.component_score
        total_weight_available += weights.adx
        available_count += 1

    if total_weight_available < 50:
        # Too much missing data
        raise ValueError(f"Insufficient valid indicator data for {ticker} (only {total_weight_available}% weight available).")

    # Data Quality Flag
    if available_count == 5:
        data_quality = "HIGH"
    elif available_count >= 3:
        data_quality = "MEDIUM"
    else:
        data_quality = "LOW"

    # Scale to 100
    base_conviction = (total_score / total_weight_available) * 100.0

    # Apply volume adjustment (additive, max ±10 points)
    conviction = base_conviction + volume_sig.adjustment
    
    # Step 5: Trend alignment and ADX Gating
    trend = classify_trend(ichimoku_sig, macd_sig)
    
    # Trend Conflict Penalty (-15 points)
    penalty = 0.0
    if strategy.is_bullish and trend == TrendBias.STRONG_BEAR:
        penalty = -15.0
    elif strategy.is_bearish and trend == TrendBias.STRONG_BULL:
        penalty = -15.0
    elif strategy.is_bullish and trend == TrendBias.BEAR:
        penalty = -10.0
    elif strategy.is_bearish and trend == TrendBias.BULL:
        penalty = -10.0
        
    conviction += penalty
    conviction = round(max(0.0, min(100.0, conviction)), 2)

    tier = ConvictionTier.from_score(conviction)
    
    # ADX Gate: ADX < 20 caps credit spreads at WATCH and adjusts score
    if strategy.is_credit and adx_sig.value < 20:
        if tier in (ConvictionTier.PREPARE, ConvictionTier.EXECUTE):
            tier = ConvictionTier.WATCH
            # Adjust score to tier boundary to maintain consistency
            conviction = min(conviction, 59.9)
    
    strikes = calculate_strikes(price, strategy, bollinger_sig)

    # Step 6: Rationale
    rationale = build_rationale(
        strategy, weights,
        ichimoku_sig, rsi_sig, macd_sig, bollinger_sig, adx_sig,
        volume_sig, strikes,
        trend, conviction, tier,
    )

    return ConvictionResult(
        ticker=ticker.upper(),
        strategy=strategy.value,
        strategy_label=strategy.label,
        price=price,
        conviction_score=conviction,
        tier=tier.value,
        trend_bias=trend.value,
        ichimoku=ichimoku_sig,
        rsi=rsi_sig,
        macd=macd_sig,
        bollinger=bollinger_sig,
        adx=adx_sig,
        volume=volume_sig,
        strikes=strikes,
        data_quality=data_quality,
        rationale=rationale,
    )


# =============================================================================
# CLI Interface
# =============================================================================

def print_report(result: ConvictionResult) -> None:
    """Pretty-print a conviction report to stdout."""

    print()
    print("=" * 70)
    print(f"  CONVICTION REPORT: {result.ticker} (v{__version__})")
    print(f"  Strategy: {result.strategy_label}")
    print("=" * 70)
    print(f"  Price:       ${result.price}")
    print(f"  Trend:       {result.trend_bias}")
    print(f"  Quality:     {result.data_quality}")
    print(f"  Conviction:  {result.conviction_score:.1f} / 100")
    print(f"  Action Tier: {result.tier}")
    print("-" * 70)
    for line in result.rationale:
        print(f"  {line}")
    print("=" * 70)
    print()


def main() -> None:
    """
    CLI entry point.

    Examples:
        python3 spread_conviction_engine.py AAPL
        python3 spread_conviction_engine.py SPY --strategy bear_call
        python3 spread_conviction_engine.py QQQ AAPL --strategy bull_call --json
        python3 spread_conviction_engine.py SPY --strategy iron_condor
        python3 spread_conviction_engine.py AAPL --strategy butterfly
        python3 spread_conviction_engine.py TSLA --strategy calendar --json
    """
    # Strategy classifications for routing
    VERTICAL_STRATEGIES = {"bull_put", "bear_call", "bull_call", "bear_put"}
    MULTI_LEG_STRATEGIES = {"iron_condor", "butterfly", "calendar"}
    ALL_STRATEGIES = sorted(VERTICAL_STRATEGIES | MULTI_LEG_STRATEGIES)

    parser = argparse.ArgumentParser(
        description=(
            "Spread Conviction Engine v" + __version__ + " — "
            "Multi-strategy options spread scoring."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Vertical Spreads (directional):\n"
            "  bull_put     Credit spread. Mean reversion: bullish dip.\n"
            "  bear_call    Credit spread. Mean reversion: bearish rally.\n"
            "  bull_call    Debit spread.  Breakout: bullish momentum.\n"
            "  bear_put     Debit spread.  Breakout: bearish momentum.\n"
            "\n"
            "Multi-Leg Strategies (non-directional / theta):\n"
            "  iron_condor  Credit. Sell OTM put+call spreads. Range-bound, high IV.\n"
            "  butterfly    Debit.  Buy 1 low, sell 2 mid, buy 1 high. Pinning play.\n"
            "  calendar     Debit.  Sell front-month, buy back-month. Theta harvest.\n"
            "\n"
            "Conviction Tiers:\n"
            "  WAIT    (0-39)   Conditions unfavourable. Stay patient.\n"
            "  WATCH   (40-59)  Getting interesting. Monitor closely.\n"
            "  PREPARE (60-79)  Favourable. Size your trade.\n"
            "  EXECUTE (80-100) High conviction. Enter the spread.\n"
        ),
    )
    parser.add_argument(
        "tickers",
        nargs="+",
        help="One or more stock ticker symbols (e.g., AAPL SPY QQQ)",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="bull_put",
        choices=ALL_STRATEGIES,
        help=(
            "Spread strategy to score (default: bull_put). "
            "Use iron_condor, butterfly, or calendar for multi-leg."
        ),
    )
    parser.add_argument(
        "--interval",
        default="1d",
        help="Candle interval: 1h, 1d, 1wk (default: 1d)",
    )
    parser.add_argument(
        "--period",
        default="2y",
        help="Data lookback: 6mo, 1y, 2y, 5y (default: 2y)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (for piping to other tools)",
    )

    args = parser.parse_args()
    is_multi_leg = args.strategy in MULTI_LEG_STRATEGIES

    results = []
    for ticker in args.tickers:
        try:
            if is_multi_leg:
                # Route to multi-leg strategy engine
                from multi_leg_strategies import (
                    MultiLegStrategyType,
                    analyse_multi_leg,
                    print_multi_leg_report,
                    MultiLegResult,
                )
                ml_strategy = MultiLegStrategyType(args.strategy)
                result = analyse_multi_leg(
                    ticker,
                    strategy=ml_strategy,
                    period=args.period,
                    interval=args.interval,
                )
                results.append(result)
                if not args.json:
                    print_multi_leg_report(result)
            else:
                # Existing vertical spread engine
                strategy = StrategyType(args.strategy)
                result = analyse(
                    ticker,
                    strategy=strategy,
                    period=args.period,
                    interval=args.interval,
                )
                results.append(result)
                if not args.json:
                    print_report(result)
        except Exception as e:
            error_msg = f"Error analysing {ticker}: {e}"
            if args.json:
                results.append({"ticker": ticker, "error": str(e)})
            else:
                print(f"\n  ❌ {error_msg}\n", file=sys.stderr)

    if args.json:
        output = []
        for r in results:
            if hasattr(r, "to_dict"):
                output.append(r.to_dict())
            else:
                output.append(r)
        print(json.dumps(output, indent=2, default=str))


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    main()
