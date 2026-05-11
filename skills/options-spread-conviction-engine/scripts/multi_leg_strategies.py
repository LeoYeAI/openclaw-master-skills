#!/usr/bin/env python3
"""
===============================================================================
Multi-Leg Strategy Extensions — Iron Condors, Butterflies, Calendar Spreads
===============================================================================

Author:     Financial Toolkit (OpenClaw)
Created:    2026-02-12
Version:    2.0.0
License:    MIT

Description:
    Extends the Spread Conviction Engine with non-directional and
    theta-harvesting multi-leg strategies:

    ┌────────────────┬────────┬─────────────────────────────────────────────┐
    │ Strategy       │ Type   │ Ideal Setup                                 │
    ├────────────────┼────────┼─────────────────────────────────────────────┤
    │ iron_condor    │ Credit │ High IV rank, neutral RSI, range-bound      │
    │ butterfly      │ Debit  │ BB squeeze, dead-center RSI, no trend       │
    │ calendar       │ Debit  │ Inverted IV term structure, stable price    │
    └────────────────┴────────┴─────────────────────────────────────────────┘

    These strategies are fundamentally different from vertical spreads:
    they profit from *lack of movement* (iron condors, butterflies) or
    from *time decay differentials* (calendars), rather than directional
    conviction.

    Scoring Philosophy:
    ───────────────────
    Iron Condors  → premium richness (IV rank) + neutrality + range structure
    Butterflies   → volatility compression (squeeze) + price centering
    Calendars     → IV term structure inversion + price stability + theta edge

Dependencies:
    Same as spread_conviction_engine.py (pandas, pandas_ta, yfinance)

===============================================================================
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import pandas as pd
import yfinance as yf

# Import shared infrastructure from the main engine
from spread_conviction_engine import (
    # Constants
    ICHIMOKU_TENKAN, ICHIMOKU_KIJUN, ICHIMOKU_SENKOU,
    RSI_LENGTH, ADX_LENGTH,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    BBANDS_LENGTH, BBANDS_STD,
    VOLUME_WINDOW,
    # Functions
    fetch_ohlcv, compute_all_indicators,
    # Enumerations
    ConvictionTier, TrendBias,
)


# =============================================================================
# Module Version
# =============================================================================

__version__ = "2.0.0"


# =============================================================================
# Multi-Leg Strategy Types
# =============================================================================

class MultiLegStrategyType(str, Enum):
    """
    Supported multi-leg options strategies.

    Unlike vertical spreads which are directional, these strategies profit
    from range-bound conditions, volatility compression, or time decay
    differentials.
    """
    IRON_CONDOR = "iron_condor"
    BUTTERFLY = "butterfly"
    CALENDAR = "calendar"

    @property
    def label(self) -> str:
        labels = {
            MultiLegStrategyType.IRON_CONDOR: "Iron Condor (Credit)",
            MultiLegStrategyType.BUTTERFLY:   "Long Butterfly (Debit)",
            MultiLegStrategyType.CALENDAR:    "Calendar Spread (Debit)",
        }
        return labels[self]

    @property
    def philosophy(self) -> str:
        philosophies = {
            MultiLegStrategyType.IRON_CONDOR: "Premium Selling / Range-Bound",
            MultiLegStrategyType.BUTTERFLY:   "Pinning / Volatility Compression",
            MultiLegStrategyType.CALENDAR:    "Theta Harvesting / IV Term Structure",
        }
        return philosophies[self]

    @property
    def ideal_setup(self) -> str:
        setups = {
            MultiLegStrategyType.IRON_CONDOR: (
                "IV Rank >70, RSI neutral (40-60), price centered in range, ADX <25"
            ),
            MultiLegStrategyType.BUTTERFLY: (
                "BB squeeze (low bandwidth), RSI dead-center (45-55), ADX <20, flat MACD"
            ),
            MultiLegStrategyType.CALENDAR: (
                "Front-month IV > back-month IV by >5%, stable price, moderate trend"
            ),
        }
        return setups[self]

    @property
    def legs(self) -> int:
        """Number of option legs in the strategy."""
        leg_counts = {
            MultiLegStrategyType.IRON_CONDOR: 4,
            MultiLegStrategyType.BUTTERFLY: 4,  # 3 strikes, but 4 contracts (1+2+1)
            MultiLegStrategyType.CALENDAR: 2,
        }
        return leg_counts[self]


# =============================================================================
# Component Weights per Strategy
# =============================================================================

# Iron Condor: Premium selling in range-bound, high-IV environment
# ┌───────────────────────┬────────┬──────────────────────────────────────┐
# │ Component             │ Weight │ Rationale                            │
# ├───────────────────────┼────────┼──────────────────────────────────────┤
# │ IV Rank (BBW %ile)    │ 25     │ Rich premiums to sell                │
# │ RSI Neutrality        │ 20     │ No directional momentum              │
# │ ADX (Range-Bound)     │ 20     │ Weak trend = range structure         │
# │ Price Position (%B)   │ 20     │ Centered in range = safe margins     │
# │ MACD Neutrality       │ 15     │ No acceleration in either direction  │
# └───────────────────────┴────────┴──────────────────────────────────────┘

IRON_CONDOR_WEIGHTS = {
    "iv_rank": 25,
    "rsi_neutrality": 20,
    "adx_range": 20,
    "price_position": 20,
    "macd_neutrality": 15,
}

# Butterfly: Pinning play in low-volatility, compressed environment
# ┌───────────────────────┬────────┬──────────────────────────────────────┐
# │ Component             │ Weight │ Rationale                            │
# ├───────────────────────┼────────┼──────────────────────────────────────┤
# │ BB Squeeze            │ 30     │ Vol compression = narrow range       │
# │ RSI Neutrality        │ 25     │ Price at equilibrium                 │
# │ ADX Weakness          │ 20     │ No directional trend at all          │
# │ Price Centering (%B)  │ 15     │ At center of range for max profit    │
# │ MACD Flatness         │ 10     │ No momentum                          │
# └───────────────────────┴────────┴──────────────────────────────────────┘

BUTTERFLY_WEIGHTS = {
    "squeeze": 30,
    "rsi_neutrality": 25,
    "adx_weakness": 20,
    "price_centering": 15,
    "macd_flatness": 10,
}

# Calendar: Theta harvesting from IV term structure differential
# ┌───────────────────────┬────────┬──────────────────────────────────────┐
# │ Component             │ Weight │ Rationale                            │
# ├───────────────────────┼────────┼──────────────────────────────────────┤
# │ IV Term Structure     │ 30     │ Front IV > Back IV = theta edge      │
# │ Price Stability       │ 20     │ Price stays near strike              │
# │ RSI Neutrality        │ 20     │ Not trending away from strike        │
# │ ADX (Moderate)        │ 15     │ Some structure, not trending hard    │
# │ MACD Neutrality       │ 15     │ No directional acceleration          │
# └───────────────────────┴────────┴──────────────────────────────────────┘

CALENDAR_WEIGHTS = {
    "iv_term_structure": 30,
    "price_stability": 20,
    "rsi_neutrality": 20,
    "adx_moderate": 15,
    "macd_neutrality": 15,
}


# =============================================================================
# Strike Data Classes
# =============================================================================

@dataclass
class IronCondorStrikes:
    """
    Iron Condor: 4 legs — sell OTM put & call spreads, buy further OTM wings.

    Payoff diagram:
        Loss ─────────┐                          ┌──────────── Loss
                      │                          │
                      └──────┐            ┌──────┘
         Max Loss            │  Max Profit│            Max Loss
                             └────────────┘
        put_long   put_short              call_short   call_long
    """
    put_long: float       # buy far OTM put (wing protection)
    put_short: float      # sell OTM put (inner leg)
    call_short: float     # sell OTM call (inner leg)
    call_long: float      # buy far OTM call (wing protection)
    max_profit_low: float   # lower bound of max profit zone
    max_profit_high: float  # upper bound of max profit zone
    breakeven_lower: float
    breakeven_upper: float
    wing_width: float       # width of each wing (put_short - put_long)
    description: str


@dataclass
class ButterflyStrikes:
    """
    Long Butterfly: Buy 1 low, Sell 2 middle, Buy 1 high strike.

    Payoff diagram:
                             ╱╲
                            ╱  ╲
                           ╱    ╲
        ──────────────────╱      ╲──────────────────
        lower_long     middle     upper_long
                      (short x2)
    """
    lower_long: float     # buy 1 call/put at lower strike
    middle_short: float   # sell 2 calls/puts at middle strike
    upper_long: float     # buy 1 call/put at upper strike
    max_profit_price: float   # price of maximum profit (= middle)
    breakeven_lower: float
    breakeven_upper: float
    width: float              # wing width (middle - lower = upper - middle)
    description: str


@dataclass
class CalendarStrikes:
    """
    Calendar Spread: Same strike, different expirations.
    Sell short-dated, buy longer-dated.
    """
    strike: float
    front_expiry: str           # short-dated (sell)
    back_expiry: str            # long-dated (buy)
    front_iv: Optional[float]   # IV of front-month option (%)
    back_iv: Optional[float]    # IV of back-month option (%)
    iv_differential_pct: Optional[float]  # (front - back) / back * 100
    theta_advantage: str        # qualitative description
    description: str


# =============================================================================
# Component Signal Data Classes
# =============================================================================

@dataclass
class IVRankSignal:
    """
    Implied Volatility Rank approximated from Bollinger Bandwidth percentile.

    IV Rank = (Current BBW - 1Y Low BBW) / (1Y High BBW - 1Y Low BBW) * 100

    This is a well-established proxy: BBW tracks realized volatility, which
    correlates with implied volatility rank over time (Sinclair, 2013).
    """
    iv_rank: float         # 0-100 percentile
    current_bbw: float     # current Bollinger Bandwidth
    bbw_1y_high: float     # highest BBW in trailing 252 days
    bbw_1y_low: float      # lowest BBW in trailing 252 days
    regime: str            # VERY_LOW, LOW, MODERATE, HIGH, VERY_HIGH
    component_score: float = 0.0


@dataclass
class NeutralitySignal:
    """
    Composite measure of market neutrality / lack of directional bias.
    Used by iron condors and butterflies.
    """
    rsi_value: float
    rsi_distance_from_50: float
    adx_value: float
    macd_histogram: float
    macd_hist_pct_of_price: float
    percent_b: float
    percent_b_distance_from_50: float
    component_score: float = 0.0


@dataclass
class SqueezeSignal:
    """
    Bollinger Band squeeze detection for butterfly strategies.

    A squeeze occurs when bandwidth drops to historically low levels,
    indicating volatility compression — ideal for butterfly payoffs.
    """
    bandwidth: float
    bandwidth_percentile: float   # where current BBW ranks vs 1Y history
    is_squeezing: bool            # BBW below 25th percentile
    squeeze_duration: int         # consecutive bars in squeeze
    component_score: float = 0.0


@dataclass
class IVTermStructureSignal:
    """
    IV Term Structure analysis for calendar spreads.

    An inverted term structure (front IV > back IV) creates a theta
    harvesting opportunity: sell expensive short-dated options, buy
    cheaper long-dated options at the same strike.

    Data Sources:
        'options_chain' — real IV from yfinance options data (preferred)
        'hv_proxy'      — HV(10) vs HV(30) as fallback proxy
        'unavailable'   — no IV data could be obtained
    """
    front_iv: Optional[float]           # front-month IV (%) or HV(10)
    back_iv: Optional[float]            # back-month IV (%) or HV(30)
    iv_differential_pct: Optional[float] # (front - back) / back * 100
    is_inverted: bool                    # True if front > back by >5%
    data_source: str                     # 'options_chain', 'hv_proxy', or error
    front_expiry: Optional[str] = None
    back_expiry: Optional[str] = None
    component_score: float = 0.0


# =============================================================================
# Multi-Leg Conviction Result
# =============================================================================

@dataclass
class MultiLegResult:
    """
    Final output of the Multi-Leg Strategy Engine.

    Parallels ConvictionResult from the vertical spread engine but with
    fields specific to non-directional / multi-leg strategies.
    """
    ticker: str
    strategy: str
    strategy_label: str
    strategy_type: str           # "multi_leg"
    price: float
    conviction_score: float
    tier: str
    # Component signals (populated based on strategy)
    iv_rank: Optional[IVRankSignal] = None
    neutrality: Optional[NeutralitySignal] = None
    squeeze: Optional[SqueezeSignal] = None
    iv_term_structure: Optional[IVTermStructureSignal] = None
    # Volume
    relative_volume: float = 0.0
    volume_adjustment: float = 0.0
    # Strikes (exactly one will be populated depending on strategy)
    iron_condor_strikes: Optional[IronCondorStrikes] = None
    butterfly_strikes: Optional[ButterflyStrikes] = None
    calendar_strikes: Optional[CalendarStrikes] = None
    # Meta
    data_quality: str = "HIGH"
    rationale: list = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary (JSON-safe)."""
        return asdict(self)


# =============================================================================
# Helper Functions
# =============================================================================

def _round_to_strike(price: float, stock_price: float) -> float:
    """
    Round a price to the nearest standard option strike interval.

    Standard intervals:
        Stock < $25:   $0.50 or $1.00 strikes
        Stock $25-$50: $1.00 strikes
        Stock $50-$200: $2.50 or $5.00 strikes
        Stock > $200:  $5.00 strikes
    """
    if stock_price < 25:
        interval = 1.0
    elif stock_price < 50:
        interval = 1.0
    elif stock_price < 200:
        interval = 5.0
    else:
        interval = 5.0
    return round(price / interval) * interval


def _get_atm_iv(chain_df: pd.DataFrame, price: float) -> Optional[float]:
    """
    Find at-the-money implied volatility from a yfinance options chain.

    Parameters:
        chain_df: DataFrame of calls or puts from yf.Ticker.option_chain()
        price:    Current stock price

    Returns:
        ATM implied volatility as a decimal (e.g. 0.30 for 30%), or None
    """
    if chain_df.empty or "impliedVolatility" not in chain_df.columns:
        return None

    chain = chain_df.copy()
    chain["_distance"] = (chain["strike"] - price).abs()
    atm_row = chain.loc[chain["_distance"].idxmin()]

    iv = float(atm_row["impliedVolatility"])
    # Sanity check: IV should be between 0 and 10 (0% to 1000%)
    if 0 < iv < 10:
        return iv
    return None


# =============================================================================
# IV Rank Computation
# =============================================================================

def compute_iv_rank(df: pd.DataFrame) -> IVRankSignal:
    """
    Approximate IV Rank using Bollinger Bandwidth percentile.

    IV Rank formula (adapted from TastyTrade convention):
        IV Rank = (Current IV - 52wk Low IV) / (52wk High IV - 52wk Low IV)

    We use BBW as the IV proxy:
        IV Rank ≈ (Current BBW - 252d Low BBW) / (252d High BBW - 252d Low BBW)

    This correlation is well-documented: realized volatility (which BBW
    tracks) and IV rank move in tandem with ~0.7-0.8 correlation
    (Sinclair, "Volatility Trading", 2013).
    """
    bb_suffix = f"{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}"
    bbw_col = f"BBB_{bb_suffix}"

    bbw = df[bbw_col].dropna()
    if len(bbw) < 50:
        return IVRankSignal(50.0, 0, 0, 0, "MODERATE", 0.0)

    lookback = min(252, len(bbw))
    bbw_window = bbw.iloc[-lookback:]
    current_bbw = float(bbw.iloc[-1])

    bbw_high = float(bbw_window.max())
    bbw_low = float(bbw_window.min())

    if bbw_high <= bbw_low:
        iv_rank = 50.0
    else:
        iv_rank = ((current_bbw - bbw_low) / (bbw_high - bbw_low)) * 100.0

    iv_rank = max(0.0, min(100.0, iv_rank))

    if iv_rank >= 80:
        regime = "VERY_HIGH"
    elif iv_rank >= 60:
        regime = "HIGH"
    elif iv_rank >= 40:
        regime = "MODERATE"
    elif iv_rank >= 20:
        regime = "LOW"
    else:
        regime = "VERY_LOW"

    return IVRankSignal(
        iv_rank=round(iv_rank, 1),
        current_bbw=round(current_bbw, 4),
        bbw_1y_high=round(bbw_high, 4),
        bbw_1y_low=round(bbw_low, 4),
        regime=regime,
    )


# =============================================================================
# Neutrality Computation
# =============================================================================

def compute_neutrality(df: pd.DataFrame) -> NeutralitySignal:
    """
    Compute a composite neutrality measure from RSI, ADX, MACD, and %B.

    All sub-metrics express *distance from neutral* — lower values mean
    more neutral conditions, which favours non-directional strategies.
    """
    latest = df.iloc[-1]
    price = float(latest["Close"])

    rsi_val = float(latest["RSI"])
    adx_val = float(latest[f"ADX_{ADX_LENGTH}"])

    hist_col = f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}"
    macd_hist = float(latest[hist_col])
    macd_hist_pct = abs(macd_hist) / price * 100 if price > 0 else 0

    bb_suffix = f"{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}"
    percent_b = float(latest[f"BBP_{bb_suffix}"])

    return NeutralitySignal(
        rsi_value=round(rsi_val, 2),
        rsi_distance_from_50=round(abs(rsi_val - 50.0), 2),
        adx_value=round(adx_val, 2),
        macd_histogram=round(macd_hist, 4),
        macd_hist_pct_of_price=round(macd_hist_pct, 4),
        percent_b=round(percent_b, 4),
        percent_b_distance_from_50=round(abs(percent_b - 0.5), 4),
    )


# =============================================================================
# Squeeze Detection
# =============================================================================

def compute_squeeze(df: pd.DataFrame) -> SqueezeSignal:
    """
    Detect Bollinger Band squeeze conditions.

    A squeeze is identified when the current BBW falls below the 25th
    percentile of the trailing 252-day BBW distribution. Extended
    squeeze durations (>5 bars) strongly favour butterfly plays.
    """
    bb_suffix = f"{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}"
    bbw_col = f"BBB_{bb_suffix}"

    bbw = df[bbw_col].dropna()
    current_bbw = float(bbw.iloc[-1])

    lookback = min(252, len(bbw))
    bbw_window = bbw.iloc[-lookback:]
    percentile = float((bbw_window < current_bbw).sum() / len(bbw_window) * 100)

    # Squeeze threshold: 25th percentile of 1-year BBW
    threshold = float(bbw_window.quantile(0.25))
    is_squeezing = current_bbw <= threshold

    # Count consecutive bars below threshold
    squeeze_duration = 0
    if is_squeezing:
        for i in range(len(bbw) - 1, max(len(bbw) - 60, -1), -1):
            if float(bbw.iloc[i]) <= threshold:
                squeeze_duration += 1
            else:
                break

    return SqueezeSignal(
        bandwidth=round(current_bbw, 4),
        bandwidth_percentile=round(percentile, 1),
        is_squeezing=is_squeezing,
        squeeze_duration=squeeze_duration,
    )


# =============================================================================
# IV Term Structure
# =============================================================================

def _compute_hv_term_structure(df: pd.DataFrame) -> dict:
    """
    Compute historical volatility at 10-day and 30-day windows
    as a fallback proxy for IV term structure.

    HV is annualised: σ_daily × √252 × 100 (expressed as %).
    """
    close = df["Close"]
    returns = close.pct_change().dropna()

    result = {"hv_10": None, "hv_30": None}

    if len(returns) >= 10:
        std_10 = float(returns.iloc[-10:].std())
        result["hv_10"] = round(std_10 * (252 ** 0.5) * 100, 1)

    if len(returns) >= 30:
        std_30 = float(returns.iloc[-30:].std())
        result["hv_30"] = round(std_30 * (252 ** 0.5) * 100, 1)

    return result


def fetch_iv_term_structure(ticker: str) -> IVTermStructureSignal:
    """
    Analyse IV term structure from live options chain data.

    Primary: Fetch ATM call IV for front and back month expirations.
    Fallback: Use HV(10) vs HV(30) as a proxy.

    An inverted term structure (front IV > back IV by >5%) signals a
    calendar spread opportunity: sell expensive near-term options and
    buy cheaper longer-dated options at the same strike.
    """
    front_expiry = None
    back_expiry = None

    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options

        if not expirations or len(expirations) < 2:
            raise ValueError("Fewer than 2 option expirations available")

        front_expiry = expirations[0]

        # Find back month at least 25 days from front
        back_idx = min(2, len(expirations) - 1)
        try:
            front_date = datetime.strptime(front_expiry, "%Y-%m-%d")
            for i, exp in enumerate(expirations[1:], 1):
                exp_date = datetime.strptime(exp, "%Y-%m-%d")
                if (exp_date - front_date).days >= 25:
                    back_idx = i
                    break
        except (ValueError, TypeError):
            pass

        back_expiry = expirations[back_idx]

        # Get current price for ATM identification
        hist = stock.history(period="2d")
        if hist.empty:
            raise ValueError("No price history available")
        price = float(hist["Close"].iloc[-1])

        # Fetch option chains
        front_chain = stock.option_chain(front_expiry)
        back_chain = stock.option_chain(back_expiry)

        front_iv = _get_atm_iv(front_chain.calls, price)
        back_iv = _get_atm_iv(back_chain.calls, price)

        if front_iv is not None and back_iv is not None and back_iv > 0:
            diff_pct = ((front_iv - back_iv) / back_iv) * 100
            is_inverted = diff_pct > 5.0

            return IVTermStructureSignal(
                front_iv=round(front_iv * 100, 1),
                back_iv=round(back_iv * 100, 1),
                iv_differential_pct=round(diff_pct, 1),
                is_inverted=is_inverted,
                data_source="options_chain",
                front_expiry=front_expiry,
                back_expiry=back_expiry,
            )

        raise ValueError("Could not extract ATM IV from chains")

    except Exception:
        # Fallback: use historical volatility term structure proxy
        pass

    # If we reach here, options chain failed — use HV proxy
    return IVTermStructureSignal(
        front_iv=None,
        back_iv=None,
        iv_differential_pct=None,
        is_inverted=False,
        data_source="hv_proxy",
        front_expiry=front_expiry,
        back_expiry=back_expiry,
    )


def _enrich_iv_with_hv_proxy(
    signal: IVTermStructureSignal, df: pd.DataFrame
) -> IVTermStructureSignal:
    """
    If the options chain fetch failed, enrich the signal with HV proxy data.
    """
    if signal.data_source != "hv_proxy":
        return signal

    hv = _compute_hv_term_structure(df)
    hv_10 = hv.get("hv_10")
    hv_30 = hv.get("hv_30")

    if hv_10 is not None and hv_30 is not None and hv_30 > 0:
        diff_pct = ((hv_10 - hv_30) / hv_30) * 100
        return IVTermStructureSignal(
            front_iv=hv_10,
            back_iv=hv_30,
            iv_differential_pct=round(diff_pct, 1),
            is_inverted=diff_pct > 5.0,
            data_source="hv_proxy",
            front_expiry=signal.front_expiry,
            back_expiry=signal.back_expiry,
        )

    return signal


# =============================================================================
# Volume Analysis for Neutral Strategies
# =============================================================================

def score_volume_neutral(df: pd.DataFrame) -> tuple[float, float]:
    """
    Volume analysis for non-directional strategies.

    Neutral strategies prefer:
        - Low/average volume → range-bound, no conviction in either direction
        - High volume is a WARNING → may signal impending directional move

    Returns:
        (relative_volume, adjustment)
        Adjustment is ±10 points maximum.
    """
    rv = float(df.iloc[-1]["REL_VOL"])

    if rv < 0.75:
        adj = 5.0     # Low volume — range-bound, ideal
    elif rv < 1.0:
        adj = 3.0     # Below average — slightly favourable
    elif rv < 1.25:
        adj = 0.0     # Average — neutral
    elif rv < 1.5:
        adj = -5.0    # Elevated — caution, directional move possible
    else:
        adj = -10.0   # High volume — likely directional, danger

    return round(rv, 2), adj


# =============================================================================
# Scoring Functions — Iron Condor
# =============================================================================

def score_iron_condor(
    df: pd.DataFrame,
    iv_rank: IVRankSignal,
    neutrality: NeutralitySignal,
) -> tuple[float, dict[str, float]]:
    """
    Score an Iron Condor setup.

    Returns:
        (total_score, component_breakdown)

    Scoring Table:
    ──────────────────────────────────────────────────────────────────
    IV Rank (25 pts): Premium richness
        >80 → 1.0    70-80 → 0.85    50-70 → 0.55
        30-50 → 0.25  <30 → 0.10

    RSI Neutrality (20 pts): Distance from 50
        45-55 → 1.0   40-45/55-60 → 0.75   35-40/60-65 → 0.40
        30-35/65-70 → 0.20   <30/>70 → 0.05

    ADX Range-Bound (20 pts): Trend weakness
        <15 → 0.60   15-20 → 1.0    20-25 → 0.75
        25-30 → 0.35  >30 → 0.10

    Price Position (20 pts): %B centering
        0.40-0.60 → 1.0   0.30-0.40/0.60-0.70 → 0.65
        0.20-0.30/0.70-0.80 → 0.30   <0.20/>0.80 → 0.10

    MACD Neutrality (15 pts): |Histogram| as % of price
        <0.05% → 1.0   0.05-0.10% → 0.70   0.10-0.20% → 0.35
        >0.20% → 0.10
    ──────────────────────────────────────────────────────────────────
    """
    w = IRON_CONDOR_WEIGHTS

    # --- IV Rank ---
    ivr = iv_rank.iv_rank
    if ivr > 80:
        iv_score = 1.0
    elif ivr >= 70:
        iv_score = 0.85
    elif ivr >= 50:
        iv_score = 0.55
    elif ivr >= 30:
        iv_score = 0.25
    else:
        iv_score = 0.10
    iv_pts = round(iv_score * w["iv_rank"], 2)

    # --- RSI Neutrality ---
    rsi_dist = neutrality.rsi_distance_from_50
    if rsi_dist <= 5:
        rsi_score = 1.0
    elif rsi_dist <= 10:
        rsi_score = 0.75
    elif rsi_dist <= 15:
        rsi_score = 0.40
    elif rsi_dist <= 20:
        rsi_score = 0.20
    else:
        rsi_score = 0.05
    rsi_pts = round(rsi_score * w["rsi_neutrality"], 2)

    # --- ADX Range-Bound ---
    adx = neutrality.adx_value
    if adx < 15:
        adx_score = 0.60
    elif adx <= 20:
        adx_score = 1.0
    elif adx <= 25:
        adx_score = 0.75
    elif adx <= 30:
        adx_score = 0.35
    else:
        adx_score = 0.10
    adx_pts = round(adx_score * w["adx_range"], 2)

    # --- Price Position ---
    pctb_dist = neutrality.percent_b_distance_from_50
    if pctb_dist <= 0.10:
        pos_score = 1.0
    elif pctb_dist <= 0.20:
        pos_score = 0.65
    elif pctb_dist <= 0.30:
        pos_score = 0.30
    else:
        pos_score = 0.10
    pos_pts = round(pos_score * w["price_position"], 2)

    # --- MACD Neutrality ---
    macd_pct = neutrality.macd_hist_pct_of_price
    if macd_pct < 0.05:
        macd_score = 1.0
    elif macd_pct < 0.10:
        macd_score = 0.70
    elif macd_pct < 0.20:
        macd_score = 0.35
    else:
        macd_score = 0.10
    macd_pts = round(macd_score * w["macd_neutrality"], 2)

    total = iv_pts + rsi_pts + adx_pts + pos_pts + macd_pts
    breakdown = {
        "iv_rank": iv_pts,
        "rsi_neutrality": rsi_pts,
        "adx_range": adx_pts,
        "price_position": pos_pts,
        "macd_neutrality": macd_pts,
    }

    return round(total, 2), breakdown


# =============================================================================
# Scoring Functions — Butterfly
# =============================================================================

def score_butterfly(
    df: pd.DataFrame,
    squeeze: SqueezeSignal,
    neutrality: NeutralitySignal,
) -> tuple[float, dict[str, float]]:
    """
    Score a Long Butterfly setup.

    Returns:
        (total_score, component_breakdown)

    Scoring Table:
    ──────────────────────────────────────────────────────────────────
    BB Squeeze (30 pts): Volatility compression
        Percentile <10 → 1.0    10-25 → 0.80    25-40 → 0.50
        40-60 → 0.25    >60 → 0.05
        Bonus: squeeze_duration >10 → +0.10 (capped at 1.0)

    RSI Neutrality (25 pts): Dead center
        45-55 → 1.0    42-45/55-58 → 0.75    40-42/58-60 → 0.50
        35-40/60-65 → 0.20    <35/>65 → 0.05

    ADX Weakness (20 pts): No trend
        <15 → 1.0    15-18 → 0.80    18-22 → 0.50
        22-28 → 0.20    >28 → 0.05

    Price Centering (15 pts): %B near 0.50
        ±0.05 → 1.0    ±0.10 → 0.75    ±0.15 → 0.45
        ±0.25 → 0.20    >±0.25 → 0.05

    MACD Flatness (10 pts): Histogram near zero
        <0.03% → 1.0    0.03-0.07% → 0.70    0.07-0.15% → 0.30
        >0.15% → 0.05
    ──────────────────────────────────────────────────────────────────
    """
    w = BUTTERFLY_WEIGHTS

    # --- BB Squeeze ---
    pctile = squeeze.bandwidth_percentile
    if pctile < 10:
        sq_score = 1.0
    elif pctile < 25:
        sq_score = 0.80
    elif pctile < 40:
        sq_score = 0.50
    elif pctile < 60:
        sq_score = 0.25
    else:
        sq_score = 0.05

    # Duration bonus
    if squeeze.squeeze_duration > 10:
        sq_score = min(1.0, sq_score + 0.10)
    elif squeeze.squeeze_duration > 5:
        sq_score = min(1.0, sq_score + 0.05)

    sq_pts = round(sq_score * w["squeeze"], 2)

    # --- RSI Neutrality (tighter than iron condor) ---
    rsi_dist = neutrality.rsi_distance_from_50
    if rsi_dist <= 5:
        rsi_score = 1.0
    elif rsi_dist <= 8:
        rsi_score = 0.75
    elif rsi_dist <= 10:
        rsi_score = 0.50
    elif rsi_dist <= 15:
        rsi_score = 0.20
    else:
        rsi_score = 0.05
    rsi_pts = round(rsi_score * w["rsi_neutrality"], 2)

    # --- ADX Weakness ---
    adx = neutrality.adx_value
    if adx < 15:
        adx_score = 1.0
    elif adx < 18:
        adx_score = 0.80
    elif adx < 22:
        adx_score = 0.50
    elif adx < 28:
        adx_score = 0.20
    else:
        adx_score = 0.05
    adx_pts = round(adx_score * w["adx_weakness"], 2)

    # --- Price Centering (tighter than iron condor) ---
    pctb_dist = neutrality.percent_b_distance_from_50
    if pctb_dist <= 0.05:
        ctr_score = 1.0
    elif pctb_dist <= 0.10:
        ctr_score = 0.75
    elif pctb_dist <= 0.15:
        ctr_score = 0.45
    elif pctb_dist <= 0.25:
        ctr_score = 0.20
    else:
        ctr_score = 0.05
    ctr_pts = round(ctr_score * w["price_centering"], 2)

    # --- MACD Flatness ---
    macd_pct = neutrality.macd_hist_pct_of_price
    if macd_pct < 0.03:
        macd_score = 1.0
    elif macd_pct < 0.07:
        macd_score = 0.70
    elif macd_pct < 0.15:
        macd_score = 0.30
    else:
        macd_score = 0.05
    macd_pts = round(macd_score * w["macd_flatness"], 2)

    total = sq_pts + rsi_pts + adx_pts + ctr_pts + macd_pts
    breakdown = {
        "squeeze": sq_pts,
        "rsi_neutrality": rsi_pts,
        "adx_weakness": adx_pts,
        "price_centering": ctr_pts,
        "macd_flatness": macd_pts,
    }

    return round(total, 2), breakdown


# =============================================================================
# Scoring Functions — Calendar Spread
# =============================================================================

def score_calendar(
    df: pd.DataFrame,
    iv_ts: IVTermStructureSignal,
    neutrality: NeutralitySignal,
) -> tuple[float, dict[str, float]]:
    """
    Score a Calendar Spread setup.

    Returns:
        (total_score, component_breakdown)

    Scoring Table:
    ──────────────────────────────────────────────────────────────────
    IV Term Structure (30 pts): Front vs Back IV
        Inverted >15% → 1.0    Inverted 10-15% → 0.85
        Inverted 5-10% → 0.70  Flat (±5%) → 0.35
        Normal (back > front) → 0.10
        Unavailable → 0.35 (neutral default)

    Price Stability (20 pts): Low recent BBW
        BBW percentile <20 → 1.0    20-35 → 0.80    35-50 → 0.55
        50-70 → 0.30    >70 → 0.10

    RSI Neutrality (20 pts): Price staying put
        45-55 → 1.0    40-45/55-60 → 0.75    35-40/60-65 → 0.40
        30-35/65-70 → 0.20    <30/>70 → 0.05

    ADX Moderate (15 pts): Some structure, not trending hard
        <12 → 0.40    12-18 → 0.80    18-25 → 1.0
        25-32 → 0.50   >32 → 0.15

    MACD Neutrality (15 pts): No directional acceleration
        <0.05% → 1.0    0.05-0.10% → 0.70    0.10-0.20% → 0.35
        >0.20% → 0.10
    ──────────────────────────────────────────────────────────────────
    """
    w = CALENDAR_WEIGHTS

    # --- IV Term Structure ---
    if iv_ts.iv_differential_pct is not None:
        diff = iv_ts.iv_differential_pct
        if diff > 15:
            ivts_score = 1.0
        elif diff > 10:
            ivts_score = 0.85
        elif diff > 5:
            ivts_score = 0.70
        elif diff > -5:
            ivts_score = 0.35  # flat
        else:
            ivts_score = 0.10  # normal (back > front)
    else:
        ivts_score = 0.35  # no data → neutral default
    ivts_pts = round(ivts_score * w["iv_term_structure"], 2)

    # --- Price Stability (use BB Width percentile) ---
    bb_suffix = f"{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}"
    bbw_col = f"BBB_{bb_suffix}"
    bbw = df[bbw_col].dropna()
    lookback = min(252, len(bbw))
    bbw_window = bbw.iloc[-lookback:]
    current_bbw = float(bbw.iloc[-1])
    stability_pctile = float((bbw_window < current_bbw).sum() / len(bbw_window) * 100)

    if stability_pctile < 20:
        stab_score = 1.0
    elif stability_pctile < 35:
        stab_score = 0.80
    elif stability_pctile < 50:
        stab_score = 0.55
    elif stability_pctile < 70:
        stab_score = 0.30
    else:
        stab_score = 0.10
    stab_pts = round(stab_score * w["price_stability"], 2)

    # --- RSI Neutrality ---
    rsi_dist = neutrality.rsi_distance_from_50
    if rsi_dist <= 5:
        rsi_score = 1.0
    elif rsi_dist <= 10:
        rsi_score = 0.75
    elif rsi_dist <= 15:
        rsi_score = 0.40
    elif rsi_dist <= 20:
        rsi_score = 0.20
    else:
        rsi_score = 0.05
    rsi_pts = round(rsi_score * w["rsi_neutrality"], 2)

    # --- ADX Moderate (calendar likes some structure, not chaos or strong trend) ---
    adx = neutrality.adx_value
    if adx < 12:
        adx_score = 0.40  # too choppy
    elif adx < 18:
        adx_score = 0.80  # mild
    elif adx <= 25:
        adx_score = 1.0   # ideal moderate range
    elif adx <= 32:
        adx_score = 0.50  # getting trendy
    else:
        adx_score = 0.15  # strong trend — calendar at risk
    adx_pts = round(adx_score * w["adx_moderate"], 2)

    # --- MACD Neutrality ---
    macd_pct = neutrality.macd_hist_pct_of_price
    if macd_pct < 0.05:
        macd_score = 1.0
    elif macd_pct < 0.10:
        macd_score = 0.70
    elif macd_pct < 0.20:
        macd_score = 0.35
    else:
        macd_score = 0.10
    macd_pts = round(macd_score * w["macd_neutrality"], 2)

    total = ivts_pts + stab_pts + rsi_pts + adx_pts + macd_pts
    breakdown = {
        "iv_term_structure": ivts_pts,
        "price_stability": stab_pts,
        "rsi_neutrality": rsi_pts,
        "adx_moderate": adx_pts,
        "macd_neutrality": macd_pts,
    }

    return round(total, 2), breakdown


# =============================================================================
# Strike Calculation
# =============================================================================

def calculate_iron_condor_strikes(
    price: float,
    bb_upper: float,
    bb_middle: float,
    bb_lower: float,
) -> IronCondorStrikes:
    """
    Calculate Iron Condor strikes using Bollinger Band levels.

    Inner strikes (sell) at 1-sigma: midpoint between SMA and band edge.
    Outer strikes (buy) at 2-sigma: the actual BB band edges.

    The 1-sigma / 2-sigma structure gives a natural risk/reward framework:
    the sold strikes are within 1 standard deviation of the mean, and the
    bought wings provide protection at 2 standard deviations.
    """
    # 1-sigma levels (midpoint between SMA and 2-sigma band)
    sigma_1_upper = (bb_middle + bb_upper) / 2.0
    sigma_1_lower = (bb_middle + bb_lower) / 2.0

    # Round to standard strikes
    put_short = _round_to_strike(sigma_1_lower, price)
    put_long = _round_to_strike(bb_lower, price)
    call_short = _round_to_strike(sigma_1_upper, price)
    call_long = _round_to_strike(bb_upper, price)

    # Ensure logical ordering
    if put_long >= put_short:
        put_long = put_short - _strike_interval(price)
    if call_long <= call_short:
        call_long = call_short + _strike_interval(price)

    wing_width = put_short - put_long  # same on both sides ideally

    return IronCondorStrikes(
        put_long=put_long,
        put_short=put_short,
        call_short=call_short,
        call_long=call_long,
        max_profit_low=put_short,
        max_profit_high=call_short,
        breakeven_lower=put_short,   # approx (actual depends on net credit)
        breakeven_upper=call_short,  # approx
        wing_width=wing_width,
        description=(
            f"SELL {put_short}P / BUY {put_long}P + "
            f"SELL {call_short}C / BUY {call_long}C. "
            f"Max profit zone: ${put_short}-${call_short}."
        ),
    )


def calculate_butterfly_strikes(
    price: float,
    bb_upper: float,
    bb_middle: float,
    bb_lower: float,
) -> ButterflyStrikes:
    """
    Calculate Butterfly strikes: Buy 1 low, Sell 2 middle, Buy 1 high.

    Center (sell 2) at SMA. Wings at 1-sigma (midpoints of BB bands).
    Equal-width butterfly ensures balanced risk.
    """
    middle = _round_to_strike(bb_middle, price)

    # 1-sigma width
    sigma_1 = (bb_upper - bb_lower) / 4.0
    wing_width = max(_strike_interval(price), _round_to_strike(sigma_1, price))
    # Ensure wing_width is at least one strike interval
    if wing_width < _strike_interval(price):
        wing_width = _strike_interval(price)

    lower = middle - wing_width
    upper = middle + wing_width

    return ButterflyStrikes(
        lower_long=lower,
        middle_short=middle,
        upper_long=upper,
        max_profit_price=middle,
        breakeven_lower=lower,   # approx (actual depends on net debit)
        breakeven_upper=upper,   # approx
        width=wing_width,
        description=(
            f"BUY 1x {lower}C + SELL 2x {middle}C + BUY 1x {upper}C. "
            f"Max profit at ${middle} expiration."
        ),
    )


def calculate_calendar_strikes(
    price: float,
    iv_ts: IVTermStructureSignal,
) -> CalendarStrikes:
    """
    Calculate Calendar Spread strikes: same strike, different expirations.

    Strike = ATM (current price rounded to nearest strike interval).
    Sell front-month, buy back-month.
    """
    strike = _round_to_strike(price, price)

    front_expiry = iv_ts.front_expiry or "nearest_monthly"
    back_expiry = iv_ts.back_expiry or "next_monthly"

    # Theta advantage description
    if iv_ts.iv_differential_pct is not None and iv_ts.iv_differential_pct > 5:
        theta_adv = (
            f"Front IV ({iv_ts.front_iv}%) > Back IV ({iv_ts.back_iv}%) "
            f"by {iv_ts.iv_differential_pct:.1f}%. Strong theta crush advantage."
        )
    elif iv_ts.iv_differential_pct is not None:
        theta_adv = (
            f"IV differential: {iv_ts.iv_differential_pct:.1f}%. "
            f"Moderate theta advantage."
        )
    else:
        theta_adv = "IV data unavailable. Using HV proxy or neutral assumption."

    return CalendarStrikes(
        strike=strike,
        front_expiry=front_expiry,
        back_expiry=back_expiry,
        front_iv=iv_ts.front_iv,
        back_iv=iv_ts.back_iv,
        iv_differential_pct=iv_ts.iv_differential_pct,
        theta_advantage=theta_adv,
        description=(
            f"SELL {strike}C ({front_expiry}) / BUY {strike}C ({back_expiry}). "
            f"Harvest theta decay on front leg while back leg retains value."
        ),
    )


def _strike_interval(price: float) -> float:
    """Return standard option strike interval for a given stock price."""
    if price < 25:
        return 1.0
    elif price < 50:
        return 1.0
    elif price < 200:
        return 5.0
    else:
        return 5.0


# =============================================================================
# Rationale Builder
# =============================================================================

def build_multi_leg_rationale(
    strategy: MultiLegStrategyType,
    result: MultiLegResult,
    breakdown: dict[str, float],
) -> list[str]:
    """
    Generate a human-readable rationale for the multi-leg conviction score.
    """
    lines: list[str] = []

    # Header
    lines.append(f"Strategy: {strategy.label}  ({strategy.philosophy})")
    lines.append(f"Ideal Setup: {strategy.ideal_setup}")
    lines.append(f"Legs: {strategy.legs}")
    lines.append("")
    lines.append(
        f"Score: {result.conviction_score:.1f}/100 -> {result.tier}"
    )
    lines.append("")

    # Volume
    vol_adj_sign = "+" if result.volume_adjustment >= 0 else ""
    lines.append(
        f"Volume: RV={result.relative_volume} "
        f"({vol_adj_sign}{result.volume_adjustment:.0f} adjustment)"
    )
    if result.relative_volume > 1.5:
        lines.append(
            "  WARNING: High volume may signal directional move — "
            "non-directional strategies at risk"
        )
    lines.append("")

    # Strategy-specific components
    if strategy == MultiLegStrategyType.IRON_CONDOR:
        _rationale_iron_condor(lines, result, breakdown)
    elif strategy == MultiLegStrategyType.BUTTERFLY:
        _rationale_butterfly(lines, result, breakdown)
    elif strategy == MultiLegStrategyType.CALENDAR:
        _rationale_calendar(lines, result, breakdown)

    return lines


def _rationale_iron_condor(
    lines: list[str],
    result: MultiLegResult,
    breakdown: dict[str, float],
) -> None:
    """Append iron condor-specific rationale lines."""
    w = IRON_CONDOR_WEIGHTS
    iv = result.iv_rank
    n = result.neutrality

    lines.append(f"[IV Rank +{breakdown['iv_rank']:.1f}/{w['iv_rank']}]")
    if iv:
        lines.append(
            f"  IV Rank (BBW proxy): {iv.iv_rank:.0f}% ({iv.regime})"
        )
        lines.append(
            f"  BBW: {iv.current_bbw:.2f} "
            f"(1Y range: {iv.bbw_1y_low:.2f} - {iv.bbw_1y_high:.2f})"
        )
        if iv.iv_rank >= 70:
            lines.append("  Premiums are RICH — ideal for credit strategy")
        elif iv.iv_rank < 30:
            lines.append("  Premiums are THIN — poor risk/reward for credit")

    lines.append(f"[RSI Neutrality +{breakdown['rsi_neutrality']:.1f}/{w['rsi_neutrality']}]")
    if n:
        lines.append(
            f"  RSI({RSI_LENGTH}) = {n.rsi_value} "
            f"(distance from 50: {n.rsi_distance_from_50:.1f})"
        )

    lines.append(f"[ADX Range +{breakdown['adx_range']:.1f}/{w['adx_range']}]")
    if n:
        lines.append(f"  ADX({ADX_LENGTH}) = {n.adx_value}")
        if n.adx_value < 20:
            lines.append("  Range-bound environment confirmed")
        elif n.adx_value > 30:
            lines.append("  WARNING: Strong trend detected — condor at risk")

    lines.append(
        f"[Price Position +{breakdown['price_position']:.1f}/{w['price_position']}]"
    )
    if n:
        lines.append(
            f"  %B = {n.percent_b:.4f} "
            f"(distance from center: {n.percent_b_distance_from_50:.4f})"
        )

    lines.append(
        f"[MACD Neutrality +{breakdown['macd_neutrality']:.1f}/{w['macd_neutrality']}]"
    )
    if n:
        lines.append(
            f"  |Histogram|/Price = {n.macd_hist_pct_of_price:.4f}%"
        )

    # Strikes
    if result.iron_condor_strikes:
        s = result.iron_condor_strikes
        lines.append("")
        lines.append("Strikes:")
        lines.append(f"  BUY  {s.put_long}P | SELL {s.put_short}P")
        lines.append(f"  SELL {s.call_short}C | BUY  {s.call_long}C")
        lines.append(
            f"  Max Profit Zone: ${s.max_profit_low} - ${s.max_profit_high}"
        )
        lines.append(f"  Wing Width: ${s.wing_width:.2f}")


def _rationale_butterfly(
    lines: list[str],
    result: MultiLegResult,
    breakdown: dict[str, float],
) -> None:
    """Append butterfly-specific rationale lines."""
    w = BUTTERFLY_WEIGHTS
    sq = result.squeeze
    n = result.neutrality

    lines.append(f"[BB Squeeze +{breakdown['squeeze']:.1f}/{w['squeeze']}]")
    if sq:
        lines.append(
            f"  Bandwidth: {sq.bandwidth:.4f} "
            f"(percentile: {sq.bandwidth_percentile:.0f}%)"
        )
        if sq.is_squeezing:
            lines.append(
                f"  SQUEEZE ACTIVE — {sq.squeeze_duration} consecutive bars"
            )
        else:
            lines.append("  No active squeeze")

    lines.append(f"[RSI Neutrality +{breakdown['rsi_neutrality']:.1f}/{w['rsi_neutrality']}]")
    if n:
        lines.append(
            f"  RSI({RSI_LENGTH}) = {n.rsi_value} "
            f"(distance from 50: {n.rsi_distance_from_50:.1f})"
        )

    lines.append(f"[ADX Weakness +{breakdown['adx_weakness']:.1f}/{w['adx_weakness']}]")
    if n:
        lines.append(f"  ADX({ADX_LENGTH}) = {n.adx_value}")
        if n.adx_value < 15:
            lines.append("  Very weak trend — ideal for butterfly")

    lines.append(
        f"[Price Centering +{breakdown['price_centering']:.1f}/{w['price_centering']}]"
    )
    if n:
        lines.append(
            f"  %B = {n.percent_b:.4f} "
            f"(distance from 0.50: {n.percent_b_distance_from_50:.4f})"
        )

    lines.append(
        f"[MACD Flatness +{breakdown['macd_flatness']:.1f}/{w['macd_flatness']}]"
    )
    if n:
        lines.append(
            f"  |Histogram|/Price = {n.macd_hist_pct_of_price:.4f}%"
        )

    # Strikes
    if result.butterfly_strikes:
        s = result.butterfly_strikes
        lines.append("")
        lines.append("Strikes:")
        lines.append(
            f"  BUY 1x {s.lower_long}C | "
            f"SELL 2x {s.middle_short}C | "
            f"BUY 1x {s.upper_long}C"
        )
        lines.append(f"  Max Profit Price: ${s.max_profit_price}")
        lines.append(
            f"  Profit Zone: ~${s.breakeven_lower} - ${s.breakeven_upper}"
        )
        lines.append(f"  Wing Width: ${s.width:.2f}")


def _rationale_calendar(
    lines: list[str],
    result: MultiLegResult,
    breakdown: dict[str, float],
) -> None:
    """Append calendar spread-specific rationale lines."""
    w = CALENDAR_WEIGHTS
    ivts = result.iv_term_structure
    n = result.neutrality

    lines.append(
        f"[IV Term Structure +{breakdown['iv_term_structure']:.1f}/{w['iv_term_structure']}]"
    )
    if ivts:
        lines.append(f"  Data Source: {ivts.data_source}")
        if ivts.front_iv is not None and ivts.back_iv is not None:
            lines.append(
                f"  Front IV: {ivts.front_iv}% | Back IV: {ivts.back_iv}%"
            )
            lines.append(
                f"  Differential: {ivts.iv_differential_pct:+.1f}%"
            )
            if ivts.is_inverted:
                lines.append(
                    "  INVERTED TERM STRUCTURE — calendar opportunity confirmed"
                )
            else:
                lines.append("  Normal term structure — reduced edge")
        else:
            lines.append("  IV data unavailable — using neutral assumption")

    lines.append(
        f"[Price Stability +{breakdown['price_stability']:.1f}/{w['price_stability']}]"
    )
    lines.append(f"  Low recent volatility favours calendar hold")

    lines.append(
        f"[RSI Neutrality +{breakdown['rsi_neutrality']:.1f}/{w['rsi_neutrality']}]"
    )
    if n:
        lines.append(
            f"  RSI({RSI_LENGTH}) = {n.rsi_value} "
            f"(distance from 50: {n.rsi_distance_from_50:.1f})"
        )

    lines.append(
        f"[ADX Moderate +{breakdown['adx_moderate']:.1f}/{w['adx_moderate']}]"
    )
    if n:
        lines.append(f"  ADX({ADX_LENGTH}) = {n.adx_value}")

    lines.append(
        f"[MACD Neutrality +{breakdown['macd_neutrality']:.1f}/{w['macd_neutrality']}]"
    )
    if n:
        lines.append(
            f"  |Histogram|/Price = {n.macd_hist_pct_of_price:.4f}%"
        )

    # Strikes
    if result.calendar_strikes:
        s = result.calendar_strikes
        lines.append("")
        lines.append("Strikes:")
        lines.append(f"  Strike: ${s.strike}")
        lines.append(f"  SELL {s.front_expiry} | BUY {s.back_expiry}")
        lines.append(f"  Theta Advantage: {s.theta_advantage}")


# =============================================================================
# Directional Risk Gate
# =============================================================================

def _compute_directional_penalty(neutrality: NeutralitySignal) -> float:
    """
    Apply a penalty when conditions are too directional for neutral strategies.

    Strong directional signals (RSI extreme + high ADX) get a penalty
    that caps the conviction score, preventing false confidence.
    """
    penalty = 0.0

    # RSI extreme penalty
    if neutrality.rsi_distance_from_50 > 25:
        penalty -= 15.0
    elif neutrality.rsi_distance_from_50 > 20:
        penalty -= 10.0

    # High ADX penalty (strong trend)
    if neutrality.adx_value > 35:
        penalty -= 10.0
    elif neutrality.adx_value > 30:
        penalty -= 5.0

    return penalty


# =============================================================================
# Main Analysis Pipeline
# =============================================================================

def analyse_multi_leg(
    ticker: str,
    strategy: MultiLegStrategyType,
    period: str = "2y",
    interval: str = "1d",
) -> MultiLegResult:
    """
    Run the full multi-leg strategy analysis pipeline.

    Steps:
        1. Fetch OHLCV data
        2. Compute all technical indicators
        3. Compute strategy-specific signals (IV rank, squeeze, term structure)
        4. Score the setup
        5. Apply volume adjustment and directional penalty
        6. Calculate suggested strikes
        7. Build rationale

    Parameters:
        ticker:   Stock symbol (e.g. 'AAPL', 'SPY')
        strategy: Multi-leg strategy to evaluate
        period:   Data lookback period (default '2y')
        interval: Candle interval (default '1d')

    Returns:
        MultiLegResult with full analysis
    """
    # Step 1: Fetch data
    df = fetch_ohlcv(ticker, period=period, interval=interval)

    # Step 2: Compute indicators (reuse from main engine)
    df = compute_all_indicators(df)

    # Step 3: Get current price and BB values
    price = round(float(df.iloc[-1]["Close"]), 2)
    bb_suffix = f"{BBANDS_LENGTH}_{BBANDS_STD}_{BBANDS_STD}"
    bb_upper = float(df.iloc[-1][f"BBU_{bb_suffix}"])
    bb_middle = float(df.iloc[-1][f"BBM_{bb_suffix}"])
    bb_lower = float(df.iloc[-1][f"BBL_{bb_suffix}"])

    # Step 4: Compute shared signals
    neutrality = compute_neutrality(df)

    # Step 5: Strategy-specific scoring
    iv_rank_sig = None
    squeeze_sig = None
    iv_ts_sig = None
    ic_strikes = None
    bf_strikes = None
    cal_strikes = None
    breakdown = {}

    if strategy == MultiLegStrategyType.IRON_CONDOR:
        iv_rank_sig = compute_iv_rank(df)
        iv_rank_sig.component_score = 0  # will be set by scorer
        base_score, breakdown = score_iron_condor(df, iv_rank_sig, neutrality)
        ic_strikes = calculate_iron_condor_strikes(
            price, bb_upper, bb_middle, bb_lower
        )

    elif strategy == MultiLegStrategyType.BUTTERFLY:
        squeeze_sig = compute_squeeze(df)
        base_score, breakdown = score_butterfly(df, squeeze_sig, neutrality)
        bf_strikes = calculate_butterfly_strikes(
            price, bb_upper, bb_middle, bb_lower
        )

    elif strategy == MultiLegStrategyType.CALENDAR:
        iv_ts_sig = fetch_iv_term_structure(ticker)
        iv_ts_sig = _enrich_iv_with_hv_proxy(iv_ts_sig, df)
        base_score, breakdown = score_calendar(df, iv_ts_sig, neutrality)
        cal_strikes = calculate_calendar_strikes(price, iv_ts_sig)

    else:
        raise ValueError(f"Unknown multi-leg strategy: {strategy}")

    # Step 6: Volume adjustment
    rel_vol, vol_adj = score_volume_neutral(df)

    # Step 7: Directional penalty
    dir_penalty = _compute_directional_penalty(neutrality)

    # Step 8: Final score
    conviction = base_score + vol_adj + dir_penalty
    conviction = round(max(0.0, min(100.0, conviction)), 2)
    tier = ConvictionTier.from_score(conviction)

    # Step 9: Build result
    result = MultiLegResult(
        ticker=ticker.upper(),
        strategy=strategy.value,
        strategy_label=strategy.label,
        strategy_type="multi_leg",
        price=price,
        conviction_score=conviction,
        tier=tier.value,
        iv_rank=iv_rank_sig,
        neutrality=neutrality,
        squeeze=squeeze_sig,
        iv_term_structure=iv_ts_sig,
        relative_volume=rel_vol,
        volume_adjustment=vol_adj,
        iron_condor_strikes=ic_strikes,
        butterfly_strikes=bf_strikes,
        calendar_strikes=cal_strikes,
        data_quality="HIGH",
    )

    # Step 10: Rationale
    result.rationale = build_multi_leg_rationale(strategy, result, breakdown)

    return result


# =============================================================================
# Report Printer
# =============================================================================

def print_multi_leg_report(result: MultiLegResult) -> None:
    """Pretty-print a multi-leg conviction report to stdout."""

    print()
    print("=" * 70)
    print(f"  CONVICTION REPORT: {result.ticker} (v{__version__})")
    print(f"  Strategy: {result.strategy_label}")
    print("=" * 70)
    print(f"  Price:       ${result.price}")
    print(f"  Quality:     {result.data_quality}")
    print(f"  Conviction:  {result.conviction_score:.1f} / 100")
    print(f"  Action Tier: {result.tier}")
    print("-" * 70)
    for line in result.rationale:
        print(f"  {line}")
    print("=" * 70)
    print()