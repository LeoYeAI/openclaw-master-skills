"""
Options Profit Calculator - Core Calculation Logic

Supports multi-leg options strategies including vertical spreads,
iron condors, and butterflies. Calculates P/L profiles, breakeven
points, max profit/loss, Greeks, and Probability of Profit (POP)
using Black-Scholes closed-form solutions and Monte Carlo simulation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

import numpy as np
from scipy.stats import norm


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OptionType(Enum):
    CALL = "call"
    PUT = "put"


class Position(Enum):
    LONG = "long"
    SHORT = "short"


# ---------------------------------------------------------------------------
# Option Leg
# ---------------------------------------------------------------------------

@dataclass
class OptionLeg:
    """Represents a single leg of an options strategy.

    Attributes:
        strike: Strike price of the option.
        option_type: CALL or PUT.
        position: LONG (bought) or SHORT (sold/written).
        iv: Annualized implied volatility as a decimal (e.g. 0.30 for 30%).
        days_to_expiry: Calendar days until expiration.
        premium: Per-share premium paid (positive) or received (positive).
                 Sign convention: always stored as a positive number; the
                 position (long/short) determines cash flow direction.
        quantity: Number of contracts (each contract = 100 shares).
        risk_free_rate: Annualized risk-free interest rate (decimal).
    """

    strike: float
    option_type: OptionType
    position: Position
    iv: float
    days_to_expiry: float
    premium: float
    quantity: int = 1
    risk_free_rate: float = 0.05

    def __post_init__(self) -> None:
        _validate_positive(self.strike, "strike")
        _validate_positive(self.iv, "implied volatility")
        _validate_positive(self.days_to_expiry, "days_to_expiry")
        _validate_non_negative(self.premium, "premium")
        if self.quantity < 1:
            raise ValueError("quantity must be >= 1")

    @property
    def T(self) -> float:
        """Time to expiry in years."""
        return self.days_to_expiry / 365.0

    # -- intrinsic value at a given underlying price at expiration ----------

    def intrinsic_at_expiry(self, underlying_price: float) -> float:
        """Per-share intrinsic value at expiration for a given underlying price."""
        if self.option_type == OptionType.CALL:
            return max(underlying_price - self.strike, 0.0)
        else:
            return max(self.strike - underlying_price, 0.0)

    def pnl_at_expiry(self, underlying_price: float) -> float:
        """Per-share P/L at expiration for this leg (accounts for position direction).

        Returns a dollar amount per share.  Multiply by (quantity * 100)
        for total dollar P/L.
        """
        intrinsic = self.intrinsic_at_expiry(underlying_price)
        if self.position == Position.LONG:
            return intrinsic - self.premium
        else:  # SHORT
            return self.premium - intrinsic

    def total_pnl_at_expiry(self, underlying_price: float) -> float:
        """Total dollar P/L at expiration (quantity * 100 shares)."""
        return self.pnl_at_expiry(underlying_price) * self.quantity * 100


# ---------------------------------------------------------------------------
# Black-Scholes primitives
# ---------------------------------------------------------------------------

def _d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Calculate d1 in the Black-Scholes formula."""
    if T < 1e-10:
        return float('inf') if S > K else float('-inf') if S < K else 0.0
    return (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))


def _d2(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Calculate d2 in the Black-Scholes formula."""
    return _d1(S, K, T, r, sigma) - sigma * math.sqrt(T)


def black_scholes_price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: OptionType,
) -> float:
    """Black-Scholes European option price.

    Args:
        S: Current underlying price.
        K: Strike price.
        T: Time to expiry in years.
        r: Risk-free rate (annualized, decimal).
        sigma: Implied volatility (annualized, decimal).
        option_type: CALL or PUT.

    Returns:
        Theoretical option price (per share).
    """
    if T <= 0:
        # At or past expiry — return intrinsic value
        if option_type == OptionType.CALL:
            return max(S - K, 0.0)
        else:
            return max(K - S, 0.0)

    d1 = _d1(S, K, T, r, sigma)
    d2 = d1 - sigma * math.sqrt(T)

    if option_type == OptionType.CALL:
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


# ---------------------------------------------------------------------------
# Greeks (per share, per leg)
# ---------------------------------------------------------------------------

@dataclass
class Greeks:
    """Option Greeks container."""
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0   # per calendar day
    vega: float = 0.0    # per 1% move in IV
    rho: float = 0.0     # per 1% move in rate


def compute_greeks(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: OptionType,
) -> Greeks:
    """Compute Black-Scholes Greeks for a European option.

    Returns per-share values.  Theta is expressed per calendar day.
    Vega is per 1 percentage-point change in IV.
    """
    if T <= 1e-10:
        return Greeks()

    d1 = _d1(S, K, T, r, sigma)
    d2 = d1 - sigma * math.sqrt(T)
    sqrt_T = math.sqrt(T)
    pdf_d1 = norm.pdf(d1)
    discount = math.exp(-r * T)

    # Gamma (same for call and put)
    gamma = pdf_d1 / (S * sigma * sqrt_T)

    # Vega (same for call and put), per 1% IV change
    vega = S * pdf_d1 * sqrt_T / 100.0

    if option_type == OptionType.CALL:
        delta = norm.cdf(d1)
        theta = (
            -S * pdf_d1 * sigma / (2.0 * sqrt_T)
            - r * K * discount * norm.cdf(d2)
        ) / 365.0
        rho = K * T * discount * norm.cdf(d2) / 100.0
    else:
        delta = norm.cdf(d1) - 1.0
        theta = (
            -S * pdf_d1 * sigma / (2.0 * sqrt_T)
            + r * K * discount * norm.cdf(-d2)
        ) / 365.0
        rho = -K * T * discount * norm.cdf(-d2) / 100.0

    return Greeks(delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho)


# ---------------------------------------------------------------------------
# Strategy (collection of legs)
# ---------------------------------------------------------------------------

@dataclass
class StrategyResult:
    """Aggregated result of a strategy analysis."""
    name: str
    legs: List[OptionLeg]
    net_premium: float          # positive = net credit; negative = net debit
    max_profit: float           # total dollars
    max_loss: float             # total dollars (expressed as negative)
    breakeven_points: List[float]
    pop: float                  # probability of profit [0, 1]
    net_greeks: Greeks
    pnl_curve: Optional[Tuple[np.ndarray, np.ndarray]] = None  # (prices, pnl)


class Strategy:
    """A multi-leg options strategy.

    Build by adding OptionLeg instances, then call analyze() with the
    current underlying price to compute P/L profile, breakeven, max
    profit/loss, Greeks, and POP.
    """

    def __init__(self, name: str = "Custom Strategy") -> None:
        self.name = name
        self.legs: List[OptionLeg] = []

    def add_leg(self, leg: OptionLeg) -> "Strategy":
        """Add an option leg to the strategy. Returns self for chaining."""
        self.legs.append(leg)
        return self

    # -- net premium --------------------------------------------------------

    def net_premium(self) -> float:
        """Net premium of the strategy (per share).

        Positive  → net credit received.
        Negative  → net debit paid.
        """
        total = 0.0
        for leg in self.legs:
            if leg.position == Position.SHORT:
                total += leg.premium
            else:
                total -= leg.premium
        return total

    def net_premium_total(self) -> float:
        """Net premium in total dollars (accounts for quantity * 100)."""
        total = 0.0
        for leg in self.legs:
            multiplier = leg.quantity * 100
            if leg.position == Position.SHORT:
                total += leg.premium * multiplier
            else:
                total -= leg.premium * multiplier
        return total

    # -- P/L at expiry ------------------------------------------------------

    def pnl_at_expiry(self, underlying_price: float) -> float:
        """Total dollar P/L at expiration for a given underlying price."""
        return sum(leg.total_pnl_at_expiry(underlying_price) for leg in self.legs)

    def pnl_curve(
        self,
        underlying_price: float,
        price_range_pct: float = 0.30,
        num_points: int = 500,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate a P/L curve over a range of underlying prices.

        Args:
            underlying_price: Current price of the underlying.
            price_range_pct: Fraction above/below current price to plot.
            num_points: Number of data points.

        Returns:
            (prices, pnl) arrays.
        """
        low = underlying_price * (1.0 - price_range_pct)
        high = underlying_price * (1.0 + price_range_pct)
        prices = np.linspace(low, high, num_points)
        pnl = np.array([self.pnl_at_expiry(p) for p in prices])
        return prices, pnl

    # -- breakeven ----------------------------------------------------------

    def breakeven_points(
        self,
        underlying_price: float,
        price_range_pct: float = 0.50,
        num_points: int = 5000,
    ) -> List[float]:
        """Find breakeven prices (where P/L crosses zero).

        Uses a fine-grained sweep and linear interpolation.
        """
        low = underlying_price * (1.0 - price_range_pct)
        high = underlying_price * (1.0 + price_range_pct)
        prices = np.linspace(max(low, 0.01), high, num_points)
        pnl = np.array([self.pnl_at_expiry(p) for p in prices])

        breakevens: List[float] = []
        for i in range(len(pnl) - 1):
            if pnl[i] * pnl[i + 1] < 0:
                # Linear interpolation
                p = prices[i] - pnl[i] * (prices[i + 1] - prices[i]) / (pnl[i + 1] - pnl[i])
                breakevens.append(round(p, 2))
        return breakevens

    # -- max profit / loss --------------------------------------------------

    def max_profit_loss(
        self,
        underlying_price: float,
        price_range_pct: float = 1.0,
        num_points: int = 10000,
    ) -> Tuple[float, float]:
        """Estimate max profit and max loss over a wide price range.

        Returns (max_profit, max_loss) in total dollars.
        max_loss is returned as a negative number.
        """
        low = max(underlying_price * (1.0 - price_range_pct), 0.01)
        high = underlying_price * (1.0 + price_range_pct)
        prices = np.linspace(low, high, num_points)
        pnl = np.array([self.pnl_at_expiry(p) for p in prices])
        # Also evaluate at 0 (underlying can go to zero)
        pnl_at_zero = self.pnl_at_expiry(0.01)
        all_pnl = np.concatenate([pnl, [pnl_at_zero]])
        max_profit = float(np.max(all_pnl))
        max_loss = float(np.min(all_pnl))

        # For strategies with naked calls, loss is theoretically unlimited.
        # We flag this by checking if the P/L is still declining at the high end.
        if pnl[-1] < pnl[-2] and pnl[-1] < 0:
            max_loss = float("-inf")

        return max_profit, max_loss

    # -- net Greeks ---------------------------------------------------------

    def net_greeks(self, underlying_price: float) -> Greeks:
        """Compute net Greeks for the strategy at the given underlying price."""
        net = Greeks()
        for leg in self.legs:
            g = compute_greeks(
                S=underlying_price,
                K=leg.strike,
                T=leg.T,
                r=leg.risk_free_rate,
                sigma=leg.iv,
                option_type=leg.option_type,
            )
            sign = 1.0 if leg.position == Position.LONG else -1.0
            multiplier = sign * leg.quantity
            net.delta += g.delta * multiplier
            net.gamma += g.gamma * multiplier
            net.theta += g.theta * multiplier
            net.vega += g.vega * multiplier
            net.rho += g.rho * multiplier
        return net

    # -- full analysis ------------------------------------------------------

    def analyze(
        self,
        underlying_price: float,
        num_simulations: int = 100_000,
        price_range_pct: float = 0.30,
    ) -> StrategyResult:
        """Run full strategy analysis.

        Args:
            underlying_price: Current price of the underlying asset.
            num_simulations: Number of Monte Carlo paths for POP.
            price_range_pct: Range around current price for the P/L curve.

        Returns:
            StrategyResult with all computed metrics.
        """
        _validate_positive(underlying_price, "underlying_price")

        prices, pnl = self.pnl_curve(underlying_price, price_range_pct)
        breakevens = self.breakeven_points(underlying_price)
        max_prof, max_loss = self.max_profit_loss(underlying_price)
        greeks = self.net_greeks(underlying_price)

        # Choose POP method
        if len(self.legs) == 1:
            pop = black_scholes_pop(self.legs[0], underlying_price)
        else:
            pop = monte_carlo_pop(self, underlying_price, num_simulations)

        return StrategyResult(
            name=self.name,
            legs=self.legs,
            net_premium=self.net_premium_total(),
            max_profit=max_prof,
            max_loss=max_loss,
            breakeven_points=breakevens,
            pop=pop,
            net_greeks=greeks,
            pnl_curve=(prices, pnl),
        )


# ---------------------------------------------------------------------------
# Probability of Profit — Black-Scholes (single leg)
# ---------------------------------------------------------------------------

def black_scholes_pop(leg: OptionLeg, underlying_price: float) -> float:
    """Probability of profit for a single option leg using Black-Scholes.

    For a long call, POP = P(S_T > K + premium).
    For a long put, POP = P(S_T < K - premium).
    For short positions the inequalities reverse.

    Uses the log-normal distribution of S_T under GBM.
    """
    S = underlying_price
    K = leg.strike
    T = leg.T
    r = leg.risk_free_rate
    sigma = leg.iv

    if T <= 0:
        return 1.0 if leg.pnl_at_expiry(S) > 0 else 0.0

    # Breakeven price for this single leg
    if leg.option_type == OptionType.CALL:
        if leg.position == Position.LONG:
            be = K + leg.premium
        else:
            be = K + leg.premium  # same breakeven, but direction flips
    else:  # PUT
        if leg.position == Position.LONG:
            be = K - leg.premium
        else:
            be = K - leg.premium

    if be <= 0:
        # Breakeven is at or below zero
        if leg.position == Position.SHORT:
            return 1.0
        return 0.0

    # P(S_T > be) under risk-neutral (we use real-world drift ≈ r for simplicity)
    d2_be = (math.log(S / be) + (r - 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))

    prob_above_be = norm.cdf(d2_be)

    if leg.option_type == OptionType.CALL:
        if leg.position == Position.LONG:
            return prob_above_be
        else:
            return 1.0 - prob_above_be
    else:  # PUT
        if leg.position == Position.LONG:
            return 1.0 - prob_above_be
        else:
            return prob_above_be


# ---------------------------------------------------------------------------
# Probability of Profit — Monte Carlo (multi-leg)
# ---------------------------------------------------------------------------

def monte_carlo_pop(
    strategy: Strategy,
    underlying_price: float,
    num_simulations: int = 100_000,
    seed: Optional[int] = 42,
) -> float:
    """Estimate POP via Monte Carlo simulation of geometric Brownian motion.

    Simulates terminal prices at the *earliest* expiry among legs, then
    computes the strategy P/L for each path. POP = fraction of paths
    with P/L > 0.

    For strategies with legs at different expiries, we use the weighted-
    average IV and earliest expiry as a simplification (all legs are
    evaluated at the same terminal price).

    Args:
        strategy: The multi-leg Strategy.
        underlying_price: Current underlying price.
        num_simulations: Number of simulation paths.
        seed: Random seed for reproducibility (None for non-deterministic).

    Returns:
        Estimated probability of profit in [0, 1].
    """
    if not strategy.legs:
        return 0.0

    rng = np.random.default_rng(seed)

    # Use the shortest expiry for terminal simulation
    min_T = min(leg.T for leg in strategy.legs)
    if min_T <= 0:
        min_T = 1.0 / 365.0  # at least 1 day

    # Use quantity-weighted average IV and the first leg's risk-free rate
    total_qty = sum(leg.quantity for leg in strategy.legs)
    avg_iv = sum(leg.iv * leg.quantity for leg in strategy.legs) / total_qty
    r = strategy.legs[0].risk_free_rate

    # GBM terminal price: S_T = S * exp((r - 0.5*sigma^2)*T + sigma*sqrt(T)*Z)
    drift = (r - 0.5 * avg_iv ** 2) * min_T
    diffusion = avg_iv * math.sqrt(min_T)
    Z = rng.standard_normal(num_simulations)
    S_T = underlying_price * np.exp(drift + diffusion * Z)

    # Vectorized P/L computation
    pnl = np.zeros(num_simulations)
    for leg in strategy.legs:
        sign = 1.0 if leg.position == Position.LONG else -1.0
        multiplier = leg.quantity * 100
        if leg.option_type == OptionType.CALL:
            intrinsic = np.maximum(S_T - leg.strike, 0.0)
        else:
            intrinsic = np.maximum(leg.strike - S_T, 0.0)

        # long pays premium, earns intrinsic; short earns premium, pays intrinsic
        if leg.position == Position.LONG:
            pnl += (intrinsic - leg.premium) * multiplier
        else:
            pnl += (leg.premium - intrinsic) * multiplier

    pop = float(np.mean(pnl > 0))
    return pop


# ---------------------------------------------------------------------------
# Pre-built strategy factories
# ---------------------------------------------------------------------------

def bull_call_spread(
    underlying_price: float,
    long_strike: float,
    short_strike: float,
    long_premium: float,
    short_premium: float,
    iv: float,
    days_to_expiry: float,
    risk_free_rate: float = 0.05,
    quantity: int = 1,
) -> Strategy:
    """Create a Bull Call Spread (buy lower call, sell higher call).

    Args:
        underlying_price: Current underlying price (for reference).
        long_strike: Strike of the long (bought) call.
        short_strike: Strike of the short (sold) call. Must be > long_strike.
        long_premium: Premium paid for the long call.
        short_premium: Premium received for the short call.
        iv: Implied volatility (decimal).
        days_to_expiry: Days until expiration.
        risk_free_rate: Risk-free rate (decimal).
        quantity: Number of spreads.

    Returns:
        Configured Strategy.
    """
    if short_strike <= long_strike:
        raise ValueError("short_strike must be greater than long_strike for a bull call spread")

    strat = Strategy("Bull Call Spread")
    strat.add_leg(OptionLeg(
        strike=long_strike, option_type=OptionType.CALL, position=Position.LONG,
        iv=iv, days_to_expiry=days_to_expiry, premium=long_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    strat.add_leg(OptionLeg(
        strike=short_strike, option_type=OptionType.CALL, position=Position.SHORT,
        iv=iv, days_to_expiry=days_to_expiry, premium=short_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    return strat


def bear_put_spread(
    underlying_price: float,
    long_strike: float,
    short_strike: float,
    long_premium: float,
    short_premium: float,
    iv: float,
    days_to_expiry: float,
    risk_free_rate: float = 0.05,
    quantity: int = 1,
) -> Strategy:
    """Create a Bear Put Spread (buy higher put, sell lower put).

    Args:
        long_strike: Strike of the long (bought) put. Should be higher.
        short_strike: Strike of the short (sold) put. Should be lower.
    """
    if long_strike <= short_strike:
        raise ValueError("long_strike must be greater than short_strike for a bear put spread")

    strat = Strategy("Bear Put Spread")
    strat.add_leg(OptionLeg(
        strike=long_strike, option_type=OptionType.PUT, position=Position.LONG,
        iv=iv, days_to_expiry=days_to_expiry, premium=long_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    strat.add_leg(OptionLeg(
        strike=short_strike, option_type=OptionType.PUT, position=Position.SHORT,
        iv=iv, days_to_expiry=days_to_expiry, premium=short_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    return strat


def iron_condor(
    underlying_price: float,
    put_long_strike: float,
    put_short_strike: float,
    call_short_strike: float,
    call_long_strike: float,
    put_long_premium: float,
    put_short_premium: float,
    call_short_premium: float,
    call_long_premium: float,
    iv: float,
    days_to_expiry: float,
    risk_free_rate: float = 0.05,
    quantity: int = 1,
) -> Strategy:
    """Create an Iron Condor.

    Structure (all same expiry):
        - Buy OTM put  (lowest strike)   — protection
        - Sell OTM put (next strike up)   — credit
        - Sell OTM call (next strike up)  — credit
        - Buy OTM call (highest strike)   — protection

    Strikes must satisfy: put_long < put_short < call_short < call_long.
    """
    strikes = [put_long_strike, put_short_strike, call_short_strike, call_long_strike]
    if strikes != sorted(strikes) or len(set(strikes)) != 4:
        raise ValueError(
            "Strikes must be strictly ordered: "
            "put_long < put_short < call_short < call_long"
        )

    strat = Strategy("Iron Condor")
    strat.add_leg(OptionLeg(
        strike=put_long_strike, option_type=OptionType.PUT, position=Position.LONG,
        iv=iv, days_to_expiry=days_to_expiry, premium=put_long_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    strat.add_leg(OptionLeg(
        strike=put_short_strike, option_type=OptionType.PUT, position=Position.SHORT,
        iv=iv, days_to_expiry=days_to_expiry, premium=put_short_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    strat.add_leg(OptionLeg(
        strike=call_short_strike, option_type=OptionType.CALL, position=Position.SHORT,
        iv=iv, days_to_expiry=days_to_expiry, premium=call_short_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    strat.add_leg(OptionLeg(
        strike=call_long_strike, option_type=OptionType.CALL, position=Position.LONG,
        iv=iv, days_to_expiry=days_to_expiry, premium=call_long_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    return strat


def long_call_butterfly(
    underlying_price: float,
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
    lower_premium: float,
    middle_premium: float,
    upper_premium: float,
    iv: float,
    days_to_expiry: float,
    risk_free_rate: float = 0.05,
    quantity: int = 1,
) -> Strategy:
    """Create a Long Call Butterfly spread.

    Structure:
        - Buy 1 call at lower strike
        - Sell 2 calls at middle strike
        - Buy 1 call at upper strike

    The middle strike should ideally be equidistant from lower and upper.
    """
    if not (lower_strike < middle_strike < upper_strike):
        raise ValueError("Strikes must be ordered: lower < middle < upper")

    strat = Strategy("Long Call Butterfly")
    strat.add_leg(OptionLeg(
        strike=lower_strike, option_type=OptionType.CALL, position=Position.LONG,
        iv=iv, days_to_expiry=days_to_expiry, premium=lower_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    strat.add_leg(OptionLeg(
        strike=middle_strike, option_type=OptionType.CALL, position=Position.SHORT,
        iv=iv, days_to_expiry=days_to_expiry, premium=middle_premium,
        quantity=quantity * 2, risk_free_rate=risk_free_rate,
    ))
    strat.add_leg(OptionLeg(
        strike=upper_strike, option_type=OptionType.CALL, position=Position.LONG,
        iv=iv, days_to_expiry=days_to_expiry, premium=upper_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    return strat


def long_put_butterfly(
    underlying_price: float,
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
    lower_premium: float,
    middle_premium: float,
    upper_premium: float,
    iv: float,
    days_to_expiry: float,
    risk_free_rate: float = 0.05,
    quantity: int = 1,
) -> Strategy:
    """Create a Long Put Butterfly spread.

    Structure:
        - Buy 1 put at upper strike
        - Sell 2 puts at middle strike
        - Buy 1 put at lower strike
    """
    if not (lower_strike < middle_strike < upper_strike):
        raise ValueError("Strikes must be ordered: lower < middle < upper")

    strat = Strategy("Long Put Butterfly")
    strat.add_leg(OptionLeg(
        strike=lower_strike, option_type=OptionType.PUT, position=Position.LONG,
        iv=iv, days_to_expiry=days_to_expiry, premium=lower_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    strat.add_leg(OptionLeg(
        strike=middle_strike, option_type=OptionType.PUT, position=Position.SHORT,
        iv=iv, days_to_expiry=days_to_expiry, premium=middle_premium,
        quantity=quantity * 2, risk_free_rate=risk_free_rate,
    ))
    strat.add_leg(OptionLeg(
        strike=upper_strike, option_type=OptionType.PUT, position=Position.LONG,
        iv=iv, days_to_expiry=days_to_expiry, premium=upper_premium,
        quantity=quantity, risk_free_rate=risk_free_rate,
    ))
    return strat


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")


def _validate_non_negative(value: float, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")
