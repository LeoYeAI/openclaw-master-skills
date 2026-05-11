"""
Multi-Leg Strategy Optimizer

Finds optimal combinations of options legs for various strategies:
- Vertical spreads (credit/debit)
- Iron condors / inverse iron condors
- Iron butterflies / inverse iron butterflies
- Straddles (long/short)
- Strangles (long/short)
- Single-leg (long call, long put)
- Ratio backspreads (call/put)
- Calendars

Optimizes for: max POP, max EV, min risk, delta neutrality
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import logging
import numpy as np

logger = logging.getLogger(__name__)

from options_math import (
    BlackScholes, ProbabilityCalculator, Greeks,
    fits_account_constraints, optimal_spread_width,
    DEFAULT_ACCOUNT_TOTAL, ACCOUNT_TOTAL, MAX_RISK_PER_TRADE, MIN_CASH_BUFFER, AVAILABLE_CAPITAL
)
from chain_analyzer import OptionChain, ChainAnalyzer


@dataclass
class TradeLeg:
    """Single option leg in a multi-leg strategy"""
    strike: float
    expiration: str
    dte: int
    premium: float  # Per share
    option_type: str  # 'call' or 'put'
    action: str  # 'buy' or 'sell'
    quantity: int = 1
    greeks: Optional[Greeks] = None
    
    def __post_init__(self):
        """Validate TradeLeg inputs after initialization."""
        if self.option_type not in {'call', 'put'}:
            raise ValueError(f"option_type must be 'call' or 'put', got {self.option_type}")
        if self.action not in {'buy', 'sell'}:
            raise ValueError(f"action must be 'buy' or 'sell', got {self.action}")
        if self.strike <= 0:
            raise ValueError(f"strike must be positive, got {self.strike}")
        if self.dte < 0:
            raise ValueError(f"dte must be non-negative, got {self.dte}")
        if self.premium < 0:
            raise ValueError(f"premium must be non-negative, got {self.premium}")
        if self.quantity <= 0:
            raise ValueError(f"quantity must be positive, got {self.quantity}")
    
    @property
    def net_premium(self) -> float:
        """Net premium for this leg (positive = credit, negative = debit)"""
        if self.action == 'sell':
            return self.premium * self.quantity
        else:
            return -self.premium * self.quantity


@dataclass
class MultiLegStrategy:
    """Complete multi-leg options strategy"""
    ticker: str
    strategy_type: str  # 'vertical_credit', 'vertical_debit', 'iron_condor', etc.
    underlying_price: float
    legs: List[TradeLeg] = field(default_factory=list)
    
    # Trade metrics
    max_profit: float = 0.0
    max_loss: float = 0.0
    breakevens: List[float] = field(default_factory=list)
    pop: float = 0.0  # Probability of Profit
    expected_value: float = 0.0
    risk_adjusted_return: float = 0.0
    
    # Greeks
    total_greeks: Optional[Greeks] = None
    
    # Account fit
    margin_required: float = 0.0
    fits_account: bool = False
    
    # Scores
    pop_score: float = 0.0
    ev_score: float = 0.0
    income_score: float = 0.0
    
    def __str__(self) -> str:
        return f"{self.strategy_type.upper()} on {self.ticker} @ ${self.underlying_price:.2f}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'ticker': self.ticker,
            'strategy_type': self.strategy_type,
            'underlying_price': self.underlying_price,
            'legs': [
                {
                    'strike': l.strike,
                    'expiration': l.expiration,
                    'dte': l.dte,
                    'premium': l.premium,
                    'option_type': l.option_type,
                    'action': l.action
                }
                for l in self.legs
            ],
            'max_profit': self.max_profit,
            'max_loss': self.max_loss,
            'breakevens': self.breakevens,
            'pop': self.pop,
            'expected_value': self.expected_value,
            'risk_adjusted_return': self.risk_adjusted_return,
            'margin_required': self.margin_required,
            'fits_account': self.fits_account
        }


def validate_strategy_risk(strategy: MultiLegStrategy) -> Tuple[bool, str]:
    """
    Validate that a strategy has defined, finite risk.
    
    Returns (is_valid, reason).
    Checks for:
    - Infinite risk (naked shorts, ratio spreads)
    - Undefined P&L (zero/negative max_profit or max_loss)
    - Invalid spread construction
    """
    legs = strategy.legs
    if not legs:
        return False, "no legs"

    # --- Check for naked positions (short without matching long) ---
    short_calls = [l for l in legs if l.action == 'sell' and l.option_type == 'call']
    long_calls = [l for l in legs if l.action == 'buy' and l.option_type == 'call']
    short_puts = [l for l in legs if l.action == 'sell' and l.option_type == 'put']
    long_puts = [l for l in legs if l.action == 'buy' and l.option_type == 'put']

    short_call_qty = sum(l.quantity for l in short_calls)
    long_call_qty = sum(l.quantity for l in long_calls)
    short_put_qty = sum(l.quantity for l in short_puts)
    long_put_qty = sum(l.quantity for l in long_puts)

    # Allow known unlimited-risk strategies to pass through
    known_unlimited = {'short_straddle', 'short_strangle', 'call_ratio_backspread', 'put_ratio_backspread'}
    if strategy.strategy_type not in known_unlimited:
        # Naked short calls = infinite risk
        if short_call_qty > 0 and long_call_qty == 0:
            return False, "naked short call(s) — infinite risk"
        # Naked short puts = undefined risk (strike * 100)
        if short_put_qty > 0 and long_put_qty == 0:
            return False, "naked short put(s) — undefined risk"

        # --- Ratio spreads (more shorts than longs) ---
        if short_call_qty > long_call_qty:
            return False, f"ratio call spread ({short_call_qty}:{long_call_qty} short:long) — undefined risk"
        if short_put_qty > long_put_qty:
            return False, f"ratio put spread ({short_put_qty}:{long_put_qty} short:long) — undefined risk"

    # --- P&L validation ---
    if strategy.max_profit < 0:
        return False, f"negative max_profit ({strategy.max_profit:.2f})"
    if strategy.max_loss < 0:
        return False, f"negative max_loss ({strategy.max_loss:.2f})"
    if strategy.max_profit == 0:
        return False, "zero max_profit — breakeven-only trade"
    if strategy.max_loss == 0:
        return False, "zero max_loss — likely bad data or arbitrage"

    # --- Breakeven validation ---
    if not strategy.breakevens or any(b <= 0 or not np.isfinite(b) for b in strategy.breakevens):
        return False, f"invalid breakeven(s): {strategy.breakevens}"

    # --- Finite check on all numeric fields ---
    for field_name, val in [('max_profit', strategy.max_profit),
                             ('max_loss', strategy.max_loss),
                             ('pop', strategy.pop),
                             ('expected_value', strategy.expected_value),
                             ('risk_adjusted_return', strategy.risk_adjusted_return)]:
        if not np.isfinite(val):
            return False, f"non-finite {field_name}: {val}"

    return True, "ok"


class LegOptimizer:
    """
    Optimize multi-leg option strategies
    """
    
    def __init__(self, risk_free_rate: float = 0.045, account_total: float = DEFAULT_ACCOUNT_TOTAL,
                 max_risk_per_trade: float = MAX_RISK_PER_TRADE,
                 min_cash_buffer: float = MIN_CASH_BUFFER):
        self.bs = BlackScholes()
        self.calc = ProbabilityCalculator(risk_free_rate)
        self.analyzer = ChainAnalyzer()
        self.account_total = account_total
        self.max_risk_per_trade = max_risk_per_trade
        self.min_cash_buffer = min_cash_buffer
    
    # Minimum IV floor — pre-market/post-market data often reports near-zero IV
    # which produces 100% POP and meaningless greeks.  15% is a conservative
    # floor (VIX rarely stays below 12 for extended periods).
    IV_FLOOR = 0.15

    def calculate_strategy_metrics(self, strategy: MultiLegStrategy,
                                   iv: float = 0.25) -> MultiLegStrategy:
        """
        Calculate all metrics for a strategy
        """
        if not strategy.legs:
            return strategy

        # Enforce IV floor for realistic probability/greeks calculations
        # (pre-market/post-market data often reports near-zero IV)
        iv = max(iv, self.IV_FLOOR)
        
        # Calculate net premium (per share)
        net_premium = sum(leg.net_premium for leg in strategy.legs)
        
        # Get strategy type and calculate max P/L
        if strategy.strategy_type == 'put_credit_spread':
            # Sell higher strike put, buy lower strike put
            short_leg = [l for l in strategy.legs if l.action == 'sell' and l.option_type == 'put'][0]
            long_leg = [l for l in strategy.legs if l.action == 'buy' and l.option_type == 'put'][0]
            
            width = short_leg.strike - long_leg.strike
            strategy.max_profit = net_premium * 100  # Per contract
            strategy.max_loss = max(0, (width - net_premium) * 100)  # Width minus credit, min $0
            strategy.breakevens = [short_leg.strike - net_premium]
            
        elif strategy.strategy_type == 'call_credit_spread':
            # Sell lower strike call, buy higher strike call
            short_leg = [l for l in strategy.legs if l.action == 'sell' and l.option_type == 'call'][0]
            long_leg = [l for l in strategy.legs if l.action == 'buy' and l.option_type == 'call'][0]
            
            width = long_leg.strike - short_leg.strike
            strategy.max_profit = net_premium * 100
            strategy.max_loss = max(0, (width - net_premium) * 100)  # Width minus credit, min $0
            strategy.breakevens = [short_leg.strike + net_premium]
            
        elif strategy.strategy_type == 'iron_condor':
            # Short put spread + short call spread
            puts = [l for l in strategy.legs if l.option_type == 'put']
            calls = [l for l in strategy.legs if l.option_type == 'call']
            
            put_short = [l for l in puts if l.action == 'sell'][0]
            put_long = [l for l in puts if l.action == 'buy'][0]
            call_short = [l for l in calls if l.action == 'sell'][0]
            call_long = [l for l in calls if l.action == 'buy'][0]
            
            put_width = put_short.strike - put_long.strike
            call_width = call_long.strike - call_short.strike
            max_width = max(put_width, call_width)
            
            strategy.max_profit = net_premium * 100
            strategy.max_loss = (max_width - net_premium) * 100
            strategy.breakevens = [put_short.strike - net_premium, call_short.strike + net_premium]
            
        elif strategy.strategy_type in ['put_debit_spread', 'call_debit_spread']:
            # Debit spreads
            if strategy.strategy_type == 'put_debit_spread':
                long_leg = [l for l in strategy.legs if l.action == 'buy' and l.option_type == 'put'][0]
                short_leg = [l for l in strategy.legs if l.action == 'sell' and l.option_type == 'put'][0]
                width = long_leg.strike - short_leg.strike
            else:
                long_leg = [l for l in strategy.legs if l.action == 'buy' and l.option_type == 'call'][0]
                short_leg = [l for l in strategy.legs if l.action == 'sell' and l.option_type == 'call'][0]
                width = short_leg.strike - long_leg.strike
            
            strategy.max_profit = (width + net_premium) * 100  # net_premium is negative for debit
            strategy.max_loss = -net_premium * 100

        elif strategy.strategy_type == 'inverse_iron_butterfly':
            # Long ATM straddle + short OTM strangle
            # net_premium is negative (net debit)
            long_call = [l for l in strategy.legs if l.action == 'buy' and l.option_type == 'call'][0]
            short_call = [l for l in strategy.legs if l.action == 'sell' and l.option_type == 'call'][0]
            long_put = [l for l in strategy.legs if l.action == 'buy' and l.option_type == 'put'][0]
            short_put = [l for l in strategy.legs if l.action == 'sell' and l.option_type == 'put'][0]
            
            wing_width = short_call.strike - long_call.strike  # distance ATM to OTM wing
            net_debit = -net_premium  # positive number
            strategy.max_profit = (wing_width - net_debit) * 100
            strategy.max_loss = net_debit * 100
            strategy.breakevens = [long_call.strike - net_debit, long_call.strike + net_debit]

        elif strategy.strategy_type == 'iron_butterfly':
            # Short ATM straddle + long OTM strangle
            short_call = [l for l in strategy.legs if l.action == 'sell' and l.option_type == 'call'][0]
            long_call = [l for l in strategy.legs if l.action == 'buy' and l.option_type == 'call'][0]
            short_put = [l for l in strategy.legs if l.action == 'sell' and l.option_type == 'put'][0]
            long_put = [l for l in strategy.legs if l.action == 'buy' and l.option_type == 'put'][0]
            
            wing_width = long_call.strike - short_call.strike
            strategy.max_profit = net_premium * 100  # net credit
            strategy.max_loss = (wing_width - net_premium) * 100
            strategy.breakevens = [short_call.strike - net_premium, short_call.strike + net_premium]

        elif strategy.strategy_type == 'inverse_iron_condor':
            # Long closer strangle + short wider strangle (net debit)
            long_call = [l for l in strategy.legs if l.action == 'buy' and l.option_type == 'call'][0]
            short_call = [l for l in strategy.legs if l.action == 'sell' and l.option_type == 'call'][0]
            long_put = [l for l in strategy.legs if l.action == 'buy' and l.option_type == 'put'][0]
            short_put = [l for l in strategy.legs if l.action == 'sell' and l.option_type == 'put'][0]
            
            call_width = short_call.strike - long_call.strike
            put_width = long_put.strike - short_put.strike
            max_wing = max(call_width, put_width)
            net_debit = -net_premium
            strategy.max_profit = (max_wing - net_debit) * 100
            strategy.max_loss = net_debit * 100
            strategy.breakevens = [long_put.strike - net_debit, long_call.strike + net_debit]

        elif strategy.strategy_type == 'long_straddle':
            # BUY ATM call + BUY ATM put
            call_leg = [l for l in strategy.legs if l.option_type == 'call'][0]
            put_leg = [l for l in strategy.legs if l.option_type == 'put'][0]
            total_debit = call_leg.premium + put_leg.premium
            strategy.max_profit = 99999 * 100  # Effectively unlimited
            strategy.max_loss = total_debit * 100
            strategy.breakevens = [call_leg.strike - total_debit, call_leg.strike + total_debit]

        elif strategy.strategy_type == 'long_strangle':
            # BUY OTM call + BUY OTM put
            call_leg = [l for l in strategy.legs if l.option_type == 'call'][0]
            put_leg = [l for l in strategy.legs if l.option_type == 'put'][0]
            total_debit = call_leg.premium + put_leg.premium
            strategy.max_profit = 99999 * 100
            strategy.max_loss = total_debit * 100
            strategy.breakevens = [put_leg.strike - total_debit, call_leg.strike + total_debit]

        elif strategy.strategy_type == 'short_straddle':
            # SELL ATM call + SELL ATM put
            call_leg = [l for l in strategy.legs if l.option_type == 'call'][0]
            put_leg = [l for l in strategy.legs if l.option_type == 'put'][0]
            total_credit = call_leg.premium + put_leg.premium
            strategy.max_profit = total_credit * 100
            strategy.max_loss = 99999 * 100  # Unlimited
            strategy.breakevens = [call_leg.strike - total_credit, call_leg.strike + total_credit]

        elif strategy.strategy_type == 'short_strangle':
            # SELL OTM call + SELL OTM put
            call_leg = [l for l in strategy.legs if l.option_type == 'call'][0]
            put_leg = [l for l in strategy.legs if l.option_type == 'put'][0]
            total_credit = call_leg.premium + put_leg.premium
            strategy.max_profit = total_credit * 100
            strategy.max_loss = 99999 * 100  # Unlimited
            strategy.breakevens = [put_leg.strike - total_credit, call_leg.strike + total_credit]

        elif strategy.strategy_type == 'long_call':
            leg = strategy.legs[0]
            strategy.max_profit = 99999 * 100  # Unlimited
            strategy.max_loss = leg.premium * 100
            strategy.breakevens = [leg.strike + leg.premium]

        elif strategy.strategy_type == 'long_put':
            leg = strategy.legs[0]
            strategy.max_profit = max(0, (leg.strike - leg.premium) * 100)
            strategy.max_loss = leg.premium * 100
            strategy.breakevens = [leg.strike - leg.premium]

        elif strategy.strategy_type == 'call_ratio_backspread':
            # SELL 1 lower call, BUY 2 higher calls
            short_leg = [l for l in strategy.legs if l.action == 'sell'][0]
            long_legs = [l for l in strategy.legs if l.action == 'buy']
            long_leg = long_legs[0]
            
            strike_diff = long_leg.strike - short_leg.strike
            # net_premium: positive = credit, negative = debit
            strategy.max_profit = 99999 * 100  # Unlimited above upper BE
            strategy.max_loss = (strike_diff - net_premium) * 100 if net_premium >= 0 else (strike_diff + abs(net_premium)) * 100
            # Max loss occurs at long strike at expiration
            if net_premium >= 0:
                # Entered for credit: lower BE exists
                lower_be = short_leg.strike + net_premium
                upper_be = long_leg.strike + strike_diff - net_premium
            else:
                upper_be = long_leg.strike + strike_diff + abs(net_premium)
                lower_be = short_leg.strike + net_premium  # below short strike
            strategy.breakevens = [lower_be, upper_be]

        elif strategy.strategy_type == 'put_ratio_backspread':
            # SELL 1 higher put, BUY 2 lower puts
            short_leg = [l for l in strategy.legs if l.action == 'sell'][0]
            long_legs = [l for l in strategy.legs if l.action == 'buy']
            long_leg = long_legs[0]
            
            strike_diff = short_leg.strike - long_leg.strike
            # At stock=0: gain from 2 long puts = 2*long_strike, loss from short put = short_strike
            max_profit_at_zero = 2 * long_leg.strike - short_leg.strike
            strategy.max_profit = max(0, (max_profit_at_zero + net_premium) * 100)
            strategy.max_loss = (strike_diff - net_premium) * 100 if net_premium >= 0 else (strike_diff + abs(net_premium)) * 100
            if net_premium >= 0:
                upper_be = short_leg.strike - net_premium
                lower_be = long_leg.strike - (strike_diff - net_premium)
            else:
                upper_be = short_leg.strike - net_premium
                lower_be = long_leg.strike - strike_diff - abs(net_premium)
            strategy.breakevens = [max(0, lower_be), upper_be]

        else:
            # Default: sum of premiums
            strategy.max_profit = abs(net_premium) * 100
            strategy.max_loss = abs(net_premium) * 100
        
        # --- Guard: skip strategies with non-positive P&L ---
        if strategy.max_profit <= 0 or strategy.max_loss <= 0:
            logger.debug("Skipping strategy: max_profit=%.2f, max_loss=%.2f",
                         strategy.max_profit, strategy.max_loss)
            return strategy
        
        # Calculate POP
        T = max(strategy.legs[0].dte, 1) / 365.0  # Ensure minimum 1 day
        S = strategy.underlying_price
        
        # Use Monte Carlo simulation for more accurate POP calculation
        # Monte Carlo simulates terminal price distribution using GBM,
        # which can produce more accurate results than Black-Scholes closed-form
        # especially for wider spreads where log-normal assumptions matter more.
        # This aligns better with how platforms like TastyTrade calculate POP.
        
        if strategy.strategy_type == 'put_credit_spread':
            try:
                breakeven = strategy.breakevens[0] if strategy.breakevens else (short_leg.strike - net_premium)
                mc_pop = self.calc.monte_carlo_pop_vertical(
                    S, breakeven, T, iv, 'put_credit', n_sims=100000
                )
                strategy.pop = mc_pop
            except Exception as e:
                logger.debug(f"Monte Carlo POP failed for put credit spread, falling back to Black-Scholes: {e}")
                strategy.pop = self.calc.pop_vertical_spread(
                    S, short_leg.strike, long_leg.strike, T, iv,
                    net_premium, 'put_credit'
                )
        elif strategy.strategy_type == 'call_credit_spread':
            try:
                breakeven = strategy.breakevens[0] if strategy.breakevens else (short_leg.strike + net_premium)
                mc_pop = self.calc.monte_carlo_pop_vertical(
                    S, breakeven, T, iv, 'call_credit', n_sims=100000
                )
                strategy.pop = mc_pop
            except Exception as e:
                logger.debug(f"Monte Carlo POP failed for call credit spread, falling back to Black-Scholes: {e}")
                strategy.pop = self.calc.pop_vertical_spread(
                    S, short_leg.strike, long_leg.strike, T, iv,
                    net_premium, 'call_credit'
                )
        elif strategy.strategy_type == 'iron_condor':
            # Get breakevens for Monte Carlo simulation
            lower_breakeven = strategy.breakevens[0] if strategy.breakevens else (put_short.strike - net_premium)
            upper_breakeven = strategy.breakevens[1] if len(strategy.breakevens) > 1 else (call_short.strike + net_premium)

            # Use Monte Carlo simulation for more accurate POP calculation
            # Monte Carlo simulates price paths and checks if price stays within
            # bounds at ANY point ("touch" probability), which matches how
            # brokers like Tastytrade calculate POP for Iron Condors.
            # Black-Scholes only calculates probability AT expiration.
            try:
                mc_pop = self.calc.monte_carlo_pop_iron_condor(
                    S, lower_breakeven, upper_breakeven, T, iv,
                    n_sims=100000, steps_per_day=2
                )
                strategy.pop = mc_pop
            except Exception as e:
                logger.debug(f"Monte Carlo POP failed, falling back to Black-Scholes: {e}")
                # Fallback to Black-Scholes closed-form solution
                # Correct POP for Iron Condor: P(Lower BE < S_T < Upper BE)
                # This is P(S_T < Upper BE) - P(S_T < Lower BE)
                # pop_vertical_spread(call_credit) returns P(S_T < Upper BE)
                # pop_vertical_spread(put_credit) returns P(S_T > Lower BE)
                put_pop = self.calc.pop_vertical_spread(
                    S, put_short.strike, put_long.strike, T, iv,
                    net_premium, 'put_credit'
                )
                call_pop = self.calc.pop_vertical_spread(
                    S, call_short.strike, call_long.strike, T, iv,
                    net_premium, 'call_credit'
                )
                # P(S_T < Lower BE) = 1 - put_pop
                # So POP = call_pop - (1 - put_pop) = call_pop + put_pop - 1
                strategy.pop = max(0, put_pop + call_pop - 1)
        elif strategy.strategy_type == 'put_debit_spread':
             strategy.pop = self.calc.pop_vertical_spread(S, long_leg.strike, short_leg.strike, T, iv, net_premium, 'put_debit')
        elif strategy.strategy_type == 'call_debit_spread':
             strategy.pop = self.calc.pop_vertical_spread(S, long_leg.strike, short_leg.strike, T, iv, net_premium, 'call_debit')
        elif strategy.strategy_type in ('inverse_iron_butterfly', 'inverse_iron_condor',
                                         'long_straddle', 'long_strangle'):
            # Profit if price moves beyond breakevens (either direction)
            if len(strategy.breakevens) == 2:
                lower_be, upper_be = strategy.breakevens
                # P(profit) = P(S < lower_be) + P(S > upper_be) = 1 - P(lower_be < S < upper_be)
                from scipy.stats import norm
                d_lower = (np.log(S / lower_be) + (0.045 - 0.5 * iv**2) * T) / (iv * np.sqrt(T))
                d_upper = (np.log(S / upper_be) + (0.045 - 0.5 * iv**2) * T) / (iv * np.sqrt(T))
                prob_between = norm.cdf(d_lower) - norm.cdf(d_upper)
                strategy.pop = max(0.0, 1.0 - prob_between)
            else:
                strategy.pop = 0.5
        elif strategy.strategy_type in ('iron_butterfly', 'short_straddle', 'short_strangle'):
            # Profit if price stays between breakevens
            if len(strategy.breakevens) == 2:
                lower_be, upper_be = strategy.breakevens
                from scipy.stats import norm
                d_lower = (np.log(S / lower_be) + (0.045 - 0.5 * iv**2) * T) / (iv * np.sqrt(T))
                d_upper = (np.log(S / upper_be) + (0.045 - 0.5 * iv**2) * T) / (iv * np.sqrt(T))
                strategy.pop = max(0.0, norm.cdf(d_lower) - norm.cdf(d_upper))
            else:
                strategy.pop = 0.5
        elif strategy.strategy_type == 'long_call':
            # P(S > breakeven)
            be = strategy.breakevens[0]
            from scipy.stats import norm
            d = (np.log(S / be) + (0.045 - 0.5 * iv**2) * T) / (iv * np.sqrt(T))
            strategy.pop = max(0.0, norm.cdf(d))
        elif strategy.strategy_type == 'long_put':
            # P(S < breakeven)
            be = strategy.breakevens[0]
            from scipy.stats import norm
            d = (np.log(S / be) + (0.045 - 0.5 * iv**2) * T) / (iv * np.sqrt(T))
            strategy.pop = max(0.0, 1.0 - norm.cdf(d))
        elif strategy.strategy_type in ('call_ratio_backspread', 'put_ratio_backspread'):
            # Approximate: profit beyond breakevens
            if len(strategy.breakevens) == 2:
                lower_be, upper_be = sorted(strategy.breakevens)
                from scipy.stats import norm
                d_lower = (np.log(S / lower_be) + (0.045 - 0.5 * iv**2) * T) / (iv * np.sqrt(T))
                d_upper = (np.log(S / upper_be) + (0.045 - 0.5 * iv**2) * T) / (iv * np.sqrt(T))
                if strategy.strategy_type == 'call_ratio_backspread':
                    # Profit below lower BE (if credit) + above upper BE
                    if net_premium >= 0:
                        strategy.pop = max(0.0, (1 - norm.cdf(d_lower)) + norm.cdf(d_upper))
                    else:
                        strategy.pop = max(0.0, norm.cdf(d_upper))  # Only profit above upper BE
                else:
                    if net_premium >= 0:
                        strategy.pop = max(0.0, norm.cdf(d_upper) + (1 - norm.cdf(d_lower)))
                    else:
                        strategy.pop = max(0.0, 1 - norm.cdf(d_lower))
            else:
                strategy.pop = 0.5
        else:
            strategy.pop = 0.5
            
        # Expected Value (guard: POP must be in [0,1])
        pop_clamped = max(0.0, min(1.0, strategy.pop))
        strategy.pop = pop_clamped
        strategy.expected_value = self.calc.expected_value(
            pop_clamped, strategy.max_profit, strategy.max_loss
        )
        
        # Risk-adjusted return (annualized EV / risk)
        if strategy.max_loss > 0:
            annual_factor = 365.0 / max(strategy.legs[0].dte, 1)
            raw_return = strategy.expected_value / strategy.max_loss * annual_factor
            # Cap at reasonable bounds to avoid absurd numbers
            strategy.risk_adjusted_return = max(-10.0, min(10.0, raw_return))
        else:
            strategy.risk_adjusted_return = 0.0
        
        # Margin requirement (simplified)
        strategy.margin_required = strategy.max_loss
        
        # Check account fit
        strategy.fits_account = fits_account_constraints(
            strategy.max_loss, strategy.margin_required, self.account_total,
            self.max_risk_per_trade, self.min_cash_buffer
        )
        
        # Calculate total Greeks
        total_delta = sum(
            (leg.greeks.delta if leg.greeks else 0) * leg.quantity * (1 if leg.action == 'buy' else -1)
            for leg in strategy.legs
        ) if any(leg.greeks for leg in strategy.legs) else 0
        
        total_theta = sum(
            (leg.greeks.theta if leg.greeks else 0) * leg.quantity * (1 if leg.action == 'buy' else -1)
            for leg in strategy.legs
        ) if any(leg.greeks for leg in strategy.legs) else 0
        
        strategy.total_greeks = Greeks(
            delta=total_delta,
            gamma=0,  # Simplified
            theta=total_theta,
            vega=0,
            rho=0
        )
        
        return strategy
    
    def score_strategies(self, strategies: List[MultiLegStrategy], 
                         mode: str = 'ev') -> List[MultiLegStrategy]:
        """
        Score and sort strategies based on specified mode
        
        Args:
            strategies: List of MultiLegStrategy objects
            mode: Scoring mode - 'pop' (maximize POP), 'ev' (maximize expected value),
                  'income' (maximize theta/income)
        
        Returns:
            Sorted list of strategies (highest score first)
        """
        # Ensure all strategies have metrics calculated
        for strategy in strategies:
            if strategy.pop == 0 and strategy.legs:
                # Need to calculate metrics - use default IV
                self.calculate_strategy_metrics(strategy)
        
        # Sort based on mode
        if mode == 'pop':
            # Sort by POP (highest first), then by max_loss (lowest first)
            scored = sorted(strategies, 
                          key=lambda s: (s.pop, -s.max_loss), 
                          reverse=True)
        elif mode == 'ev':
            # Sort by EV score (already calculated in metrics)
            scored = sorted(strategies, 
                          key=lambda s: (s.ev_score, s.pop), 
                          reverse=True)
        elif mode == 'income':
            # Sort by income score (theta-based)
            scored = sorted(strategies, 
                          key=lambda s: (s.income_score, s.pop), 
                          reverse=True)
        else:
            # Default to EV sorting
            scored = sorted(strategies, 
                          key=lambda s: s.ev_score, 
                          reverse=True)
        
        return scored
    
    def optimize_vertical_spreads(self, chain: OptionChain, 
                                  spread_type: str = 'put_credit',
                                  max_width: float = None,  # Auto-calculate if None
                                  min_dte: int = 7,
                                  max_dte: int = 45) -> List[MultiLegStrategy]:
        """
        Find optimal vertical spreads from options chain
        
        spread_type: 'put_credit', 'call_credit', 'put_debit', 'call_debit'
        max_width: Maximum spread width in dollars. If None, auto-calculates
                   based on underlying price to allow $100+ credit trades.
        """
        strategies = []
        
        if spread_type in ['put_credit', 'put_debit']:
            options = chain.puts
            opt_type = 'put'
        else:
            options = chain.calls
            opt_type = 'call'
        
        if len(options) < 2:
            return strategies
        
        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        
        # Auto-calculate max_width if not provided
        # For $100+ credit, need ~5-10 point wide spreads on QQQ/SPY
        # Formula: wider spreads for higher-priced underlyings
        if max_width is None:
            if S >= 500:  # QQQ, SPY, high-priced stocks
                max_width = 25.0
            elif S >= 200:  # Mid-priced stocks
                max_width = 15.0
            else:  # Lower-priced stocks
                max_width = 10.0
        
        # Get widths to try - now includes wider spreads for larger credits
        # $1-wide spreads: critical for high-priced underlyings where OTM credit 
        #                  spreads need narrow widths to fit small accounts
        # $5-10 wide: balanced risk/reward for medium accounts
        # $15-25 wide: for larger accounts seeking $100+ credits
        widths = [w for w in [1, 2, 3, 5, 7, 10, 12, 15, 18, 20, 25] if w <= max_width]
        
        for width in widths:
            # Try different short strikes
            for i, short_opt in enumerate(options):
                # OTM/ATM validation: reject deep ITM short strikes
                # For credit spreads, short strike must be OTM or near ATM
                if spread_type == 'put_credit':
                    # Short put must be at or below current price (OTM/ATM)
                    # Allow small buffer (2% ITM) for near-ATM strikes
                    if short_opt['strike'] > S * 1.02:
                        continue
                elif spread_type == 'call_credit':
                    # Short call must be at or above current price (OTM/ATM)
                    if short_opt['strike'] < S * 0.98:
                        continue
                
                # Liquidity filter: require valid bid/ask OR lastPrice fallback
                # Pre-market / post-market: bid/ask are often 0 but lastPrice exists
                has_bid_ask = short_opt.get('has_valid_bid_ask', False)
                if not has_bid_ask and short_opt['mid_price'] <= 0:
                    logger.debug("Skipping short strike %.0f: no bid/ask and no lastPrice", short_opt['strike'])
                    continue
                if short_opt['mid_price'] <= 0.05:
                    continue
                # Only apply spread width filter when we have real bid/ask data
                if has_bid_ask and short_opt['spread_pct'] > 0.20:
                    logger.debug("Skipping short strike %.0f: wide spread %.1f%%",
                                 short_opt['strike'], short_opt['spread_pct'] * 100)
                    continue
                
                # Require non-zero bid for a real market (avoid $0.00 bid / $0.01 ask phantom quotes)
                bid = short_opt.get('bid', 0) or 0
                if bid <= 0:
                    logger.debug("Skipping short strike %.0f: zero bid (no real market)", short_opt['strike'])
                    continue
                
                # Volume/Open Interest filter - avoid phantom quotes with no actual market
                volume = short_opt.get('volume', 0) or 0
                oi = short_opt.get('open_interest', 0) or 0
                if volume == 0 and oi == 0:
                    logger.debug("Skipping short strike %.0f: zero volume and open interest", short_opt['strike'])
                    continue
                
                # For $1-wide spreads on expensive underlyings, skip deep OTM 
                # where net credit would be negligible (< $0.05/share)
                # This is checked after pairing below
                
                # Find matching long strike
                if spread_type in ['put_credit', 'put_debit']:
                    target_long_strike = short_opt['strike'] - width
                else:
                    target_long_strike = short_opt['strike'] + width
                
                # Find closest long option
                long_opt = None
                long_idx = None
                min_diff = float('inf')
                
                for j, opt in enumerate(options):
                    diff = abs(opt['strike'] - target_long_strike)
                    if diff < min_diff:
                        min_diff = diff
                        long_opt = opt
                        long_idx = j
                
                if not long_opt or min_diff > 0.5:
                    continue
                
                # Skip if same strike
                if short_opt['strike'] == long_opt['strike']:
                    continue
                
                # Volume/Open Interest filter for long strike
                long_volume = long_opt.get('volume', 0) or 0
                long_oi = long_opt.get('open_interest', 0) or 0
                if long_volume == 0 and long_oi == 0:
                    logger.debug("Skipping long strike %.0f: zero volume and open interest", long_opt['strike'])
                    continue
                
                # Require non-zero bid for long strike too
                long_bid = long_opt.get('bid', 0) or 0
                if long_bid <= 0:
                    logger.debug("Skipping long strike %.0f: zero bid (no real market)", long_opt['strike'])
                    continue
                
                # Calculate implied vol for Black-Scholes
                # Use strike-specific IV for more accurate POP calculation
                # Use strike-specific IVs for each leg
                # For credit spreads, the short leg IV is most important as it determines breakeven
                short_iv = max(short_opt.get('implied_vol') or 0.25, self.IV_FLOOR)
                long_iv = max(long_opt.get('implied_vol') or 0.25, self.IV_FLOOR)
                
                # For POP calculation, use short leg IV specifically
                # The short strike determines the breakeven for credit spreads
                # The long leg is just protection and doesn't affect POP as much
                iv = short_iv
                
                # Calculate Greeks for both legs using their specific IVs
                short_greeks = self.bs.calculate_greeks(
                    S, short_opt['strike'], T, r, short_iv, opt_type
                )
                long_greeks = self.bs.calculate_greeks(
                    S, long_opt['strike'], T, r, long_iv, opt_type
                )
                
                # Use mid-point pricing for realistic fill estimates:
                # Most limit orders fill near the mid-point, not at bid/ask extremes.
                # Conservative bid/ask pricing understates credit spreads and
                # overstates debit spreads, skewing EV and POP comparisons.
                short_premium = short_opt['mid_price']
                long_premium = long_opt['mid_price']

                # Skip if mid-point is 0 (no real market)
                if short_premium <= 0 or long_premium <= 0:
                    logger.debug("Skipping %s/%s: short_mid=%.2f, long_mid=%.2f (no market)",
                                 short_opt['strike'], long_opt['strike'], short_premium, long_premium)
                    continue

                # Build legs based on spread type
                if spread_type == 'put_credit':
                    legs = [
                        TradeLeg(
                            strike=short_opt['strike'],
                            expiration=chain.expiration_date,
                            dte=chain.dte,
                            premium=short_premium,
                            option_type='put',
                            action='sell',
                            greeks=short_greeks
                        ),
                        TradeLeg(
                            strike=long_opt['strike'],
                            expiration=chain.expiration_date,
                            dte=chain.dte,
                            premium=long_premium,
                            option_type='put',
                            action='buy',
                            greeks=long_greeks
                        )
                    ]
                    strategy_type = 'put_credit_spread'
                elif spread_type == 'call_credit':
                    legs = [
                        TradeLeg(
                            strike=short_opt['strike'],
                            expiration=chain.expiration_date,
                            dte=chain.dte,
                            premium=short_premium,
                            option_type='call',
                            action='sell',
                            greeks=short_greeks
                        ),
                        TradeLeg(
                            strike=long_opt['strike'],
                            expiration=chain.expiration_date,
                            dte=chain.dte,
                            premium=long_premium,
                            option_type='call',
                            action='buy',
                            greeks=long_greeks
                        )
                    ]
                    strategy_type = 'call_credit_spread'
                else:
                    # Debit spreads - reverse actions
                    continue  # Skip for now, focus on credit spreads
                
                # Minimum net credit filter: skip if credit < $0.05/share
                # (avoids deep OTM $1 spreads with $1-2 total credit for $98-99 risk)
                net_credit = sum(l.net_premium for l in legs)
                if net_credit < 0.05:
                    continue
                
                # Minimum credit-to-width ratio: at least 10% of width
                # Ensures reasonable risk/reward (e.g., $0.20 credit on $2 width)
                actual_width = abs(legs[0].strike - legs[1].strike)
                if actual_width > 0 and net_credit / actual_width < 0.10:
                    continue
                
                strategy = MultiLegStrategy(
                    ticker=chain.ticker,
                    strategy_type=strategy_type,
                    underlying_price=S,
                    legs=legs
                )
                
                strategy = self.calculate_strategy_metrics(strategy, iv)
                
                # Skip unrealistic scenarios (credit >= width means no risk, likely bad data)
                if strategy.max_loss <= 0:
                    continue
                
                # Only include if it fits account (use 50% of account as max risk ceiling)
                # This allows larger spreads for larger accounts while keeping risk managed
                account_max_risk = self.account_total * 0.50
                if strategy.max_loss <= account_max_risk:
                    strategies.append(strategy)
        
        return strategies
    
    def optimize_iron_condors(self, chain: OptionChain,
                             put_width: float = 5.0,
                             call_width: float = 5.0,
                             otm_target: float = 0.10) -> List[MultiLegStrategy]:
        """
        Find optimal iron condors
        
        otm_target: Target delta for short options (default 10 delta ~ 10% OTM)
        """
        strategies = []
        
        if not chain.puts or not chain.calls:
            return strategies
        
        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        
        # Find 10% OTM strikes
        put_target = S * (1 - otm_target)
        call_target = S * (1 + otm_target)
        
        # Find closest puts
        put_short = None
        put_long = None
        call_short = None
        call_long = None
        
        for put in chain.puts:
            if put['strike'] <= put_target and not put_short:
                put_short = put
        for put in chain.puts:
            if put_short and put['strike'] == put_short['strike'] - put_width:
                put_long = put
                break
        
        for call in chain.calls:
            if call['strike'] >= call_target and not call_short:
                call_short = call
        for call in chain.calls:
            if call_short and call['strike'] == call_short['strike'] + call_width:
                call_long = call
                break
        
        if not all([put_short, put_long, call_short, call_long]):
            return strategies
        
        # Get IV from the short strikes (higher due to skew/vol smile)
        put_short_iv = next((p['implied_vol'] for p in chain.puts if abs(p['strike'] - put_short['strike']) < 0.01), None)
        call_short_iv = next((c['implied_vol'] for c in chain.calls if abs(c['strike'] - call_short['strike']) < 0.01), None)
        
        # Use the maximum of the two short strike IVs to be conservative
        # (OTM puts typically have much higher IV than ATM due to skew)
        iv = max(put_short_iv or 0.20, call_short_iv or 0.20, self.IV_FLOOR)
        
        # Use mid-point pricing for realistic fill estimates
        ps_prem = put_short['mid_price']
        pl_prem = put_long['mid_price']
        cs_prem = call_short['mid_price']
        cl_prem = call_long['mid_price']

        # Calculate Greeks
        legs = [
            TradeLeg(put_short['strike'], chain.expiration_date, chain.dte,
                    ps_prem, 'put', 'sell',
                    greeks=self.bs.calculate_greeks(S, put_short['strike'], T, r, iv, 'put')),
            TradeLeg(put_long['strike'], chain.expiration_date, chain.dte,
                    pl_prem, 'put', 'buy',
                    greeks=self.bs.calculate_greeks(S, put_long['strike'], T, r, iv, 'put')),
            TradeLeg(call_short['strike'], chain.expiration_date, chain.dte,
                    cs_prem, 'call', 'sell',
                    greeks=self.bs.calculate_greeks(S, call_short['strike'], T, r, iv, 'call')),
            TradeLeg(call_long['strike'], chain.expiration_date, chain.dte,
                    cl_prem, 'call', 'buy',
                    greeks=self.bs.calculate_greeks(S, call_long['strike'], T, r, iv, 'call'))
        ]
        
        strategy = MultiLegStrategy(
            ticker=chain.ticker,
            strategy_type='iron_condor',
            underlying_price=S,
            legs=legs
        )
        
        strategy = self.calculate_strategy_metrics(strategy, iv)
        
        if strategy.max_loss <= self.max_risk_per_trade * 1.5:
            strategies.append(strategy)
        
        return strategies

    # ----------------------------------------------------------------
    # Helper: find option nearest a target strike with liquidity filters
    # ----------------------------------------------------------------
    def _find_option(self, options: list, target_strike: float,
                     tolerance: float = 1.0, require_liquidity: bool = True):
        """Return the option dict closest to *target_strike*, or None."""
        best = None
        best_diff = float('inf')
        for opt in options:
            diff = abs(opt['strike'] - target_strike)
            if diff < best_diff:
                best_diff = diff
                best = opt
        if best is None or best_diff > tolerance:
            return None
        if require_liquidity:
            bid = best.get('bid', 0) or 0
            if bid <= 0 or best['mid_price'] <= 0:
                return None
        return best

    def _atm_iv(self, chain: OptionChain) -> float:
        """Return ATM implied vol from the chain (calls preferred)."""
        S = chain.underlying_price
        options = chain.calls or chain.puts or []
        if not options:
            return 0.25
        atm = min(options, key=lambda o: abs(o['strike'] - S))
        return max(atm.get('implied_vol') or 0.25, self.IV_FLOOR)

    # ----------------------------------------------------------------
    # 1. Inverse Iron Butterfly  (long straddle + short strangle)
    # ----------------------------------------------------------------
    def optimize_inverse_iron_butterfly(self, chain: OptionChain,
                                        body_width: float = 0.5,
                                        wing_width: float = 5.0) -> List[MultiLegStrategy]:
        """
        BUY ATM Call + BUY ATM Put (straddle body)
        SELL OTM Call + SELL OTM Put (strangle wings)

        body_width: max % distance from ATM for body strikes (0.5 = 0.5%)
        wing_width: dollar distance from ATM to wing strikes
        """
        strategies = []
        if not chain.calls or not chain.puts:
            return strategies

        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        iv = self._atm_iv(chain)

        # ATM strikes
        atm_call = self._find_option(chain.calls, S, tolerance=S * body_width / 100 + 1)
        atm_put = self._find_option(chain.puts, S, tolerance=S * body_width / 100 + 1)
        if not atm_call or not atm_put:
            return strategies

        for w in ([wing_width] if isinstance(wing_width, (int, float)) else wing_width):
            otm_call = self._find_option(chain.calls, S + w)
            otm_put = self._find_option(chain.puts, S - w)
            if not otm_call or not otm_put:
                continue

            legs = [
                TradeLeg(atm_call['strike'], chain.expiration_date, chain.dte,
                         atm_call['mid_price'], 'call', 'buy',
                         greeks=self.bs.calculate_greeks(S, atm_call['strike'], T, r, iv, 'call')),
                TradeLeg(atm_put['strike'], chain.expiration_date, chain.dte,
                         atm_put['mid_price'], 'put', 'buy',
                         greeks=self.bs.calculate_greeks(S, atm_put['strike'], T, r, iv, 'put')),
                TradeLeg(otm_call['strike'], chain.expiration_date, chain.dte,
                         otm_call['mid_price'], 'call', 'sell',
                         greeks=self.bs.calculate_greeks(S, otm_call['strike'], T, r, iv, 'call')),
                TradeLeg(otm_put['strike'], chain.expiration_date, chain.dte,
                         otm_put['mid_price'], 'put', 'sell',
                         greeks=self.bs.calculate_greeks(S, otm_put['strike'], T, r, iv, 'put')),
            ]

            strat = MultiLegStrategy(ticker=chain.ticker, strategy_type='inverse_iron_butterfly',
                                     underlying_price=S, legs=legs)
            strat = self.calculate_strategy_metrics(strat, iv)
            if strat.max_profit > 0 and strat.max_loss > 0:
                strategies.append(strat)

        return strategies

    # ----------------------------------------------------------------
    # 2. Iron Butterfly  (short straddle + long strangle)
    # ----------------------------------------------------------------
    def optimize_iron_butterfly(self, chain: OptionChain,
                                body_width: float = 0.5,
                                wing_width: float = 5.0) -> List[MultiLegStrategy]:
        """
        SELL ATM Call + SELL ATM Put (straddle body)
        BUY OTM Call + BUY OTM Put (strangle wings)
        """
        strategies = []
        if not chain.calls or not chain.puts:
            return strategies

        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        iv = self._atm_iv(chain)

        atm_call = self._find_option(chain.calls, S, tolerance=S * body_width / 100 + 1)
        atm_put = self._find_option(chain.puts, S, tolerance=S * body_width / 100 + 1)
        if not atm_call or not atm_put:
            return strategies

        for w in ([wing_width] if isinstance(wing_width, (int, float)) else wing_width):
            otm_call = self._find_option(chain.calls, S + w)
            otm_put = self._find_option(chain.puts, S - w)
            if not otm_call or not otm_put:
                continue

            legs = [
                TradeLeg(atm_call['strike'], chain.expiration_date, chain.dte,
                         atm_call['mid_price'], 'call', 'sell',
                         greeks=self.bs.calculate_greeks(S, atm_call['strike'], T, r, iv, 'call')),
                TradeLeg(atm_put['strike'], chain.expiration_date, chain.dte,
                         atm_put['mid_price'], 'put', 'sell',
                         greeks=self.bs.calculate_greeks(S, atm_put['strike'], T, r, iv, 'put')),
                TradeLeg(otm_call['strike'], chain.expiration_date, chain.dte,
                         otm_call['mid_price'], 'call', 'buy',
                         greeks=self.bs.calculate_greeks(S, otm_call['strike'], T, r, iv, 'call')),
                TradeLeg(otm_put['strike'], chain.expiration_date, chain.dte,
                         otm_put['mid_price'], 'put', 'buy',
                         greeks=self.bs.calculate_greeks(S, otm_put['strike'], T, r, iv, 'put')),
            ]

            strat = MultiLegStrategy(ticker=chain.ticker, strategy_type='iron_butterfly',
                                     underlying_price=S, legs=legs)
            strat = self.calculate_strategy_metrics(strat, iv)
            if strat.max_profit > 0 and strat.max_loss > 0:
                strategies.append(strat)

        return strategies

    # ----------------------------------------------------------------
    # 3. Inverse Iron Condor  (long closer strangle + short wider strangle)
    # ----------------------------------------------------------------
    def optimize_inverse_iron_condor(self, chain: OptionChain,
                                     inner_pct: float = 0.03,
                                     outer_width: float = 5.0) -> List[MultiLegStrategy]:
        """
        BUY OTM Call/Put (closer to ATM)
        SELL further OTM Call/Put (wider)

        inner_pct: % OTM for long strangle legs (e.g. 0.03 = 3%)
        outer_width: $ distance from inner to outer strikes
        """
        strategies = []
        if not chain.calls or not chain.puts:
            return strategies

        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        iv = self._atm_iv(chain)

        inner_call_target = S * (1 + inner_pct)
        inner_put_target = S * (1 - inner_pct)

        inner_call = self._find_option(chain.calls, inner_call_target)
        inner_put = self._find_option(chain.puts, inner_put_target)
        if not inner_call or not inner_put:
            return strategies

        for w in ([outer_width] if isinstance(outer_width, (int, float)) else outer_width):
            outer_call = self._find_option(chain.calls, inner_call['strike'] + w)
            outer_put = self._find_option(chain.puts, inner_put['strike'] - w)
            if not outer_call or not outer_put:
                continue

            legs = [
                TradeLeg(inner_call['strike'], chain.expiration_date, chain.dte,
                         inner_call['mid_price'], 'call', 'buy',
                         greeks=self.bs.calculate_greeks(S, inner_call['strike'], T, r, iv, 'call')),
                TradeLeg(inner_put['strike'], chain.expiration_date, chain.dte,
                         inner_put['mid_price'], 'put', 'buy',
                         greeks=self.bs.calculate_greeks(S, inner_put['strike'], T, r, iv, 'put')),
                TradeLeg(outer_call['strike'], chain.expiration_date, chain.dte,
                         outer_call['mid_price'], 'call', 'sell',
                         greeks=self.bs.calculate_greeks(S, outer_call['strike'], T, r, iv, 'call')),
                TradeLeg(outer_put['strike'], chain.expiration_date, chain.dte,
                         outer_put['mid_price'], 'put', 'sell',
                         greeks=self.bs.calculate_greeks(S, outer_put['strike'], T, r, iv, 'put')),
            ]

            strat = MultiLegStrategy(ticker=chain.ticker, strategy_type='inverse_iron_condor',
                                     underlying_price=S, legs=legs)
            strat = self.calculate_strategy_metrics(strat, iv)
            if strat.max_profit > 0 and strat.max_loss > 0:
                strategies.append(strat)

        return strategies

    # ----------------------------------------------------------------
    # 4. Long Straddle
    # ----------------------------------------------------------------
    def optimize_long_straddle(self, chain: OptionChain) -> List[MultiLegStrategy]:
        """BUY ATM Call + BUY ATM Put (same strike)."""
        strategies = []
        if not chain.calls or not chain.puts:
            return strategies

        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        iv = self._atm_iv(chain)

        atm_call = self._find_option(chain.calls, S)
        atm_put = self._find_option(chain.puts, S)
        if not atm_call or not atm_put:
            return strategies

        legs = [
            TradeLeg(atm_call['strike'], chain.expiration_date, chain.dte,
                     atm_call['mid_price'], 'call', 'buy',
                     greeks=self.bs.calculate_greeks(S, atm_call['strike'], T, r, iv, 'call')),
            TradeLeg(atm_put['strike'], chain.expiration_date, chain.dte,
                     atm_put['mid_price'], 'put', 'buy',
                     greeks=self.bs.calculate_greeks(S, atm_put['strike'], T, r, iv, 'put')),
        ]

        strat = MultiLegStrategy(ticker=chain.ticker, strategy_type='long_straddle',
                                 underlying_price=S, legs=legs)
        strat = self.calculate_strategy_metrics(strat, iv)
        if strat.max_loss > 0:
            strategies.append(strat)
        return strategies

    # ----------------------------------------------------------------
    # 5. Long Strangle
    # ----------------------------------------------------------------
    def optimize_long_strangle(self, chain: OptionChain,
                               call_otm_pct: float = 0.05,
                               put_otm_pct: float = 0.05) -> List[MultiLegStrategy]:
        """BUY OTM Call + BUY OTM Put."""
        strategies = []
        if not chain.calls or not chain.puts:
            return strategies

        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        iv = self._atm_iv(chain)

        otm_call = self._find_option(chain.calls, S * (1 + call_otm_pct))
        otm_put = self._find_option(chain.puts, S * (1 - put_otm_pct))
        if not otm_call or not otm_put:
            return strategies

        legs = [
            TradeLeg(otm_call['strike'], chain.expiration_date, chain.dte,
                     otm_call['mid_price'], 'call', 'buy',
                     greeks=self.bs.calculate_greeks(S, otm_call['strike'], T, r, iv, 'call')),
            TradeLeg(otm_put['strike'], chain.expiration_date, chain.dte,
                     otm_put['mid_price'], 'put', 'buy',
                     greeks=self.bs.calculate_greeks(S, otm_put['strike'], T, r, iv, 'put')),
        ]

        strat = MultiLegStrategy(ticker=chain.ticker, strategy_type='long_strangle',
                                 underlying_price=S, legs=legs)
        strat = self.calculate_strategy_metrics(strat, iv)
        if strat.max_loss > 0:
            strategies.append(strat)
        return strategies

    # ----------------------------------------------------------------
    # 6. Short Straddle
    # ----------------------------------------------------------------
    def optimize_short_straddle(self, chain: OptionChain) -> List[MultiLegStrategy]:
        """SELL ATM Call + SELL ATM Put."""
        strategies = []
        if not chain.calls or not chain.puts:
            return strategies

        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        iv = self._atm_iv(chain)

        atm_call = self._find_option(chain.calls, S)
        atm_put = self._find_option(chain.puts, S)
        if not atm_call or not atm_put:
            return strategies

        legs = [
            TradeLeg(atm_call['strike'], chain.expiration_date, chain.dte,
                     atm_call['mid_price'], 'call', 'sell',
                     greeks=self.bs.calculate_greeks(S, atm_call['strike'], T, r, iv, 'call')),
            TradeLeg(atm_put['strike'], chain.expiration_date, chain.dte,
                     atm_put['mid_price'], 'put', 'sell',
                     greeks=self.bs.calculate_greeks(S, atm_put['strike'], T, r, iv, 'put')),
        ]

        strat = MultiLegStrategy(ticker=chain.ticker, strategy_type='short_straddle',
                                 underlying_price=S, legs=legs)
        strat = self.calculate_strategy_metrics(strat, iv)
        if strat.max_profit > 0:
            strategies.append(strat)
        return strategies

    # ----------------------------------------------------------------
    # 7. Short Strangle
    # ----------------------------------------------------------------
    def optimize_short_strangle(self, chain: OptionChain,
                                call_otm_pct: float = 0.05,
                                put_otm_pct: float = 0.05) -> List[MultiLegStrategy]:
        """SELL OTM Call + SELL OTM Put."""
        strategies = []
        if not chain.calls or not chain.puts:
            return strategies

        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        iv = self._atm_iv(chain)

        otm_call = self._find_option(chain.calls, S * (1 + call_otm_pct))
        otm_put = self._find_option(chain.puts, S * (1 - put_otm_pct))
        if not otm_call or not otm_put:
            return strategies

        legs = [
            TradeLeg(otm_call['strike'], chain.expiration_date, chain.dte,
                     otm_call['mid_price'], 'call', 'sell',
                     greeks=self.bs.calculate_greeks(S, otm_call['strike'], T, r, iv, 'call')),
            TradeLeg(otm_put['strike'], chain.expiration_date, chain.dte,
                     otm_put['mid_price'], 'put', 'sell',
                     greeks=self.bs.calculate_greeks(S, otm_put['strike'], T, r, iv, 'put')),
        ]

        strat = MultiLegStrategy(ticker=chain.ticker, strategy_type='short_strangle',
                                 underlying_price=S, legs=legs)
        strat = self.calculate_strategy_metrics(strat, iv)
        if strat.max_profit > 0:
            strategies.append(strat)
        return strategies

    # ----------------------------------------------------------------
    # 8. Long Call
    # ----------------------------------------------------------------
    def optimize_long_call(self, chain: OptionChain,
                           moneyness: str = 'atm') -> List[MultiLegStrategy]:
        """
        BUY Call option.
        moneyness: 'atm', 'otm_5' (5% OTM), 'itm_5' (5% ITM)
        """
        strategies = []
        if not chain.calls:
            return strategies

        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        iv = self._atm_iv(chain)

        if moneyness == 'atm':
            target = S
        elif moneyness.startswith('otm_'):
            pct = float(moneyness.split('_')[1]) / 100
            target = S * (1 + pct)
        elif moneyness.startswith('itm_'):
            pct = float(moneyness.split('_')[1]) / 100
            target = S * (1 - pct)
        else:
            target = S

        opt = self._find_option(chain.calls, target)
        if not opt:
            return strategies

        legs = [
            TradeLeg(opt['strike'], chain.expiration_date, chain.dte,
                     opt['mid_price'], 'call', 'buy',
                     greeks=self.bs.calculate_greeks(S, opt['strike'], T, r, iv, 'call')),
        ]

        strat = MultiLegStrategy(ticker=chain.ticker, strategy_type='long_call',
                                 underlying_price=S, legs=legs)
        strat = self.calculate_strategy_metrics(strat, iv)
        if strat.max_loss > 0:
            strategies.append(strat)
        return strategies

    # ----------------------------------------------------------------
    # 9. Long Put
    # ----------------------------------------------------------------
    def optimize_long_put(self, chain: OptionChain,
                          moneyness: str = 'atm') -> List[MultiLegStrategy]:
        """
        BUY Put option.
        moneyness: 'atm', 'otm_5' (5% OTM), 'itm_5' (5% ITM)
        """
        strategies = []
        if not chain.puts:
            return strategies

        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        iv = self._atm_iv(chain)

        if moneyness == 'atm':
            target = S
        elif moneyness.startswith('otm_'):
            pct = float(moneyness.split('_')[1]) / 100
            target = S * (1 - pct)
        elif moneyness.startswith('itm_'):
            pct = float(moneyness.split('_')[1]) / 100
            target = S * (1 + pct)
        else:
            target = S

        opt = self._find_option(chain.puts, target)
        if not opt:
            return strategies

        legs = [
            TradeLeg(opt['strike'], chain.expiration_date, chain.dte,
                     opt['mid_price'], 'put', 'buy',
                     greeks=self.bs.calculate_greeks(S, opt['strike'], T, r, iv, 'put')),
        ]

        strat = MultiLegStrategy(ticker=chain.ticker, strategy_type='long_put',
                                 underlying_price=S, legs=legs)
        strat = self.calculate_strategy_metrics(strat, iv)
        if strat.max_loss > 0:
            strategies.append(strat)
        return strategies

    # ----------------------------------------------------------------
    # 10. Call Ratio Backspread  (sell 1 lower call, buy 2 higher calls)
    # ----------------------------------------------------------------
    def optimize_call_ratio_backspread(self, chain: OptionChain,
                                       strike_width: float = 5.0) -> List[MultiLegStrategy]:
        """
        SELL 1 ATM/ITM Call + BUY 2 OTM Calls (higher strike).
        Bullish with volatility expansion.
        """
        strategies = []
        if not chain.calls:
            return strategies

        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        iv = self._atm_iv(chain)

        # Short leg: ATM call
        short_opt = self._find_option(chain.calls, S)
        if not short_opt:
            return strategies

        for w in ([strike_width] if isinstance(strike_width, (int, float)) else strike_width):
            long_opt = self._find_option(chain.calls, short_opt['strike'] + w)
            if not long_opt:
                continue

            short_greeks = self.bs.calculate_greeks(S, short_opt['strike'], T, r, iv, 'call')
            long_greeks = self.bs.calculate_greeks(S, long_opt['strike'], T, r, iv, 'call')

            legs = [
                TradeLeg(short_opt['strike'], chain.expiration_date, chain.dte,
                         short_opt['mid_price'], 'call', 'sell', quantity=1,
                         greeks=short_greeks),
                TradeLeg(long_opt['strike'], chain.expiration_date, chain.dte,
                         long_opt['mid_price'], 'call', 'buy', quantity=2,
                         greeks=long_greeks),
            ]

            strat = MultiLegStrategy(ticker=chain.ticker, strategy_type='call_ratio_backspread',
                                     underlying_price=S, legs=legs)
            strat = self.calculate_strategy_metrics(strat, iv)
            if strat.max_loss > 0:
                strategies.append(strat)

        return strategies

    # ----------------------------------------------------------------
    # 11. Put Ratio Backspread  (sell 1 higher put, buy 2 lower puts)
    # ----------------------------------------------------------------
    def optimize_put_ratio_backspread(self, chain: OptionChain,
                                      strike_width: float = 5.0) -> List[MultiLegStrategy]:
        """
        SELL 1 ATM/ITM Put + BUY 2 OTM Puts (lower strike).
        Bearish with volatility expansion.
        """
        strategies = []
        if not chain.puts:
            return strategies

        S = chain.underlying_price
        T = chain.dte / 365.0
        r = 0.045
        iv = self._atm_iv(chain)

        # Short leg: ATM put
        short_opt = self._find_option(chain.puts, S)
        if not short_opt:
            return strategies

        for w in ([strike_width] if isinstance(strike_width, (int, float)) else strike_width):
            long_opt = self._find_option(chain.puts, short_opt['strike'] - w)
            if not long_opt:
                continue

            short_greeks = self.bs.calculate_greeks(S, short_opt['strike'], T, r, iv, 'put')
            long_greeks = self.bs.calculate_greeks(S, long_opt['strike'], T, r, iv, 'put')

            legs = [
                TradeLeg(short_opt['strike'], chain.expiration_date, chain.dte,
                         short_opt['mid_price'], 'put', 'sell', quantity=1,
                         greeks=short_greeks),
                TradeLeg(long_opt['strike'], chain.expiration_date, chain.dte,
                         long_opt['mid_price'], 'put', 'buy', quantity=2,
                         greeks=long_greeks),
            ]

            strat = MultiLegStrategy(ticker=chain.ticker, strategy_type='put_ratio_backspread',
                                     underlying_price=S, legs=legs)
            strat = self.calculate_strategy_metrics(strat, iv)
            if strat.max_loss > 0:
                strategies.append(strat)

        return strategies
