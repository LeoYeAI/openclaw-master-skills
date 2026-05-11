"""
Core Options Mathematics Module

Provides Black-Scholes pricing, Greeks calculation, Probability of Profit (POP),
and volatility analysis for options trading.

Built from first principles for mathematical rigor.
"""

import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
from dataclasses import dataclass
from typing import Optional, Tuple, List
import warnings
warnings.filterwarnings('ignore')

# Account Constraints (Defaults — override via CLI --account)
DEFAULT_ACCOUNT_TOTAL = 500.0
MAX_RISK_PER_TRADE = 100.0
MIN_CASH_BUFFER = 150.0
# Legacy aliases for backward compatibility
ACCOUNT_TOTAL = DEFAULT_ACCOUNT_TOTAL
AVAILABLE_CAPITAL = DEFAULT_ACCOUNT_TOTAL - MIN_CASH_BUFFER


@dataclass
class OptionData:
    """Container for option contract data"""
    strike: float
    expiration: str
    dte: int
    bid: float
    ask: float
    last_price: float
    implied_vol: float
    volume: int
    open_interest: int = 0
    underlying_price: float = 0.0
    option_type: str = 'call'  # 'call' or 'put'
    
    @property
    def mid_price(self) -> float:
        """Midpoint of bid-ask"""
        if self.bid > 0 and self.ask > 0:
            return (self.bid + self.ask) / 2
        return self.last_price
    
    @property
    def spread(self) -> float:
        """Bid-ask spread"""
        if self.bid > 0 and self.ask > 0:
            return self.ask - self.bid
        return 0.0
    
    @property
    def spread_pct(self) -> float:
        """Bid-ask spread as percentage of mid price"""
        mid = self.mid_price
        if mid > 0:
            return self.spread / mid
        return 1.0


@dataclass 
class Greeks:
    """Option Greeks"""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    
    
class BlackScholes:
    """
    Black-Scholes-Merton option pricing model.
    Implements from first principles without external dependencies.
    """
    
    @staticmethod
    def d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        Calculate d1 for Black-Scholes
        
        S: Underlying price (must be positive)
        K: Strike price (must be positive)
        T: Time to expiration in years (must be non-negative)
        r: Risk-free rate
        sigma: Implied volatility (must be positive)
        
        Raises:
            ValueError: If S <= 0, K <= 0, T < 0, or sigma <= 0
        """
        if S <= 0:
            raise ValueError(f"Spot price must be positive, got {S}")
        if K <= 0:
            raise ValueError(f"Strike price must be positive, got {K}")
        if T < 0:
            raise ValueError(f"Time to expiration must be non-negative, got {T}")
        if sigma <= 0:
            raise ValueError(f"Volatility must be positive, got {sigma}")
        return (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    
    @staticmethod
    def d2(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate d2 for Black-Scholes"""
        return BlackScholes.d1(S, K, T, r, sigma) - sigma * np.sqrt(T)
    
    @staticmethod
    def call_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate call option price"""
        if T <= 0:
            return max(0, S - K)
        if sigma <= 0:
            return max(0, S - K)
        
        d1 = BlackScholes.d1(S, K, T, r, sigma)
        d2 = BlackScholes.d2(S, K, T, r, sigma)
        
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    
    @staticmethod
    def put_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate put option price"""
        if T <= 0:
            return max(0, K - S)
        if sigma <= 0:
            return max(0, K - S)
        
        d1 = BlackScholes.d1(S, K, T, r, sigma)
        d2 = BlackScholes.d2(S, K, T, r, sigma)
        
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    @staticmethod
    def calculate_greeks(S: float, K: float, T: float, r: float, 
                        sigma: float, option_type: str = 'call') -> Greeks:
        """
        Calculate option Greeks using closed-form solutions
        
        All Greeks are per-share (not per-contract)
        """
        if T <= 0 or sigma <= 0:
            # At expiration - delta is 0 or 1, others are 0
            if option_type == 'call':
                delta = 1.0 if S > K else 0.0
            else:
                delta = -1.0 if S < K else 0.0
            return Greeks(delta=delta, gamma=0.0, theta=0.0, vega=0.0, rho=0.0)
        
        d1 = BlackScholes.d1(S, K, T, r, sigma)
        d2 = BlackScholes.d2(S, K, T, r, sigma)
        
        # Standard normal PDF
        nd1 = norm.pdf(d1)
        
        # Delta
        if option_type == 'call':
            delta = norm.cdf(d1)
        else:
            delta = norm.cdf(d1) - 1
        
        # Gamma (same for calls and puts)
        gamma = nd1 / (S * sigma * np.sqrt(T))
        
        # Theta (daily, not annual)
        if option_type == 'call':
            theta = -(S * nd1 * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
        else:
            theta = -(S * nd1 * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)
        theta = theta / 365.0  # Convert to daily
        
        # Vega (per 1% change in vol)
        vega = S * nd1 * np.sqrt(T) / 100.0
        
        # Rho (per 1% change in rate)
        if option_type == 'call':
            rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100.0
        else:
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100.0
        
        return Greeks(delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho)
    
    @staticmethod
    def implied_vol(S: float, K: float, T: float, r: float, 
                   market_price: float, option_type: str = 'call',
                   precision: float = 1e-6) -> Optional[float]:
        """
        Calculate implied volatility using Brent's method
        
        Returns None if implied vol cannot be calculated
        """
        if T <= 0 or market_price <= 0:
            return None
        
        # Intrinsic value bounds
        if option_type == 'call':
            intrinsic = max(0, S - K)
        else:
            intrinsic = max(0, K - S)
        
        if market_price < intrinsic:
            return None
        
        try:
            def price_diff(sigma):
                if sigma <= 0:
                    return float('inf')
                if option_type == 'call':
                    return BlackScholes.call_price(S, K, T, r, sigma) - market_price
                else:
                    return BlackScholes.put_price(S, K, T, r, sigma) - market_price
            
            # Try to find implied vol between 0.001 and 5.0 (0.1% to 500%)
            iv = brentq(price_diff, 0.001, 5.0, xtol=precision)
            return iv
        except (ValueError, RuntimeError):
            return None


class ProbabilityCalculator:
    """
    Calculate probabilities of profit for various option strategies
    """
    
    def __init__(self, risk_free_rate: float = 0.045):
        self.r = risk_free_rate
    
    def pop_single_leg(self, S: float, K: float, T: float, sigma: float,
                      premium: float, option_type: str = 'call',
                      position: str = 'long') -> float:
        """
        Probability of Profit for single leg option
        
        For long call: POP = P(S_T > K + premium_paid)
        For short call: POP = P(S_T < K + premium_received)
        etc.
        """
        if T <= 0 or sigma <= 0:
            return 0.5
        
        # Breakeven price
        if option_type == 'call':
            if position == 'long':
                breakeven = K + premium
                z = (np.log(breakeven / S) - (self.r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
                return 1 - norm.cdf(z)  # P(S_T > breakeven)
            else:  # short
                breakeven = K + premium
                z = (np.log(breakeven / S) - (self.r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
                return norm.cdf(z)  # P(S_T < breakeven)
        else:  # put
            if position == 'long':
                breakeven = K - premium
                z = (np.log(breakeven / S) - (self.r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
                return norm.cdf(z)  # P(S_T < breakeven)
            else:  # short
                breakeven = K - premium
                z = (np.log(breakeven / S) - (self.r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
                return 1 - norm.cdf(z) # P(S_T > breakeven)
    
    def pop_vertical_spread(self, S: float, K1: float, K2: float, T: float, 
                           sigma: float, net_premium: float, 
                           spread_type: str = 'call_credit') -> float:
        """
        Probability of Profit for vertical spreads
        
        spread_type: 'call_credit', 'call_debit', 'put_credit', 'put_debit'
        """
        if T <= 0 or sigma <= 0:
            return 0.5
        
        # Breakeven depends on spread type
        if spread_type in ['call_credit', 'call_debit']:
            # Call spreads: breakeven = lower_strike + net_premium
            lower_strike = min(K1, K2)
            breakeven = lower_strike + net_premium
        else:
            # Put spreads: breakeven = higher_strike - net_premium
            higher_strike = max(K1, K2)
            breakeven = higher_strike - net_premium
        
        # Calculate probability
        if breakeven <= 0 or S <= 0:
            return 0.5
        drift = (self.r - 0.5 * sigma**2) * T
        vol = sigma * np.sqrt(T)
        if vol <= 0:
            return 0.5
        z = (np.log(breakeven / S) - drift) / vol
        
        if spread_type in ['call_credit', 'put_debit']:
            # Profit when price stays below breakeven (call credit) or below (put debit)
            return norm.cdf(z)
        else:
            # Profit when price stays above breakeven (call debit) or above (put credit)
            return 1 - norm.cdf(z)
    
    def monte_carlo_pop_iron_condor(self, S: float, lower_be: float, upper_be: float,
                                     T: float, sigma: float, n_sims: int = 100000,
                                     steps_per_day: int = 1) -> float:
        """
        Monte Carlo simulation for Iron Condor Probability of Profit.

        Unlike Black-Scholes which calculates probability AT expiration only,
        this simulates price paths and checks if price stays within bounds
        at ANY point ("touch" probability). Early touch of breakeven = loss.

        Uses Geometric Brownian Motion: dS/S = r*dt + sigma*sqrt(dt)*Z

        This matches how Tastytrade and other professional platforms calculate
        POP for Iron Condors, accounting for early breach risk.

        Args:
            S: Current underlying price
            lower_be: Lower breakeven price (put side)
            upper_be: Upper breakeven price (call side)
            T: Time to expiration in years
            sigma: Implied volatility (annualized)
            n_sims: Number of Monte Carlo simulations (default 100,000)
            steps_per_day: Number of time steps per trading day (default 1)

        Returns:
            Probability of profit (0.0 to 1.0) - proportion of paths that
            never touched either breakeven during the entire period.
        """
        if T <= 0 or sigma <= 0 or lower_be >= upper_be or S <= 0:
            return 0.5

        # Ensure reasonable bounds
        lower_be = max(lower_be, S * 0.5)  # Sanity check
        upper_be = min(upper_be, S * 2.0)  # Sanity check

        # Trading days to expiration (252 trading days per year)
        trading_days = max(int(T * 252), 1)
        n_steps = trading_days * steps_per_day
        dt = T / n_steps

        # Set random seed for reproducibility
        np.random.seed(42)

        # Geometric Brownian Motion parameters
        # dS/S = r*dt + sigma*sqrt(dt)*Z
        drift = (self.r - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt)

        # Initialize all paths at current price
        # Shape: (n_sims,) - current price for each simulation
        prices = np.full(n_sims, S, dtype=np.float64)

        # Track which paths have remained within bounds (initially all True)
        in_bounds = np.ones(n_sims, dtype=bool)

        # Simulate path evolution step by step
        for _ in range(n_steps):
            # Generate random shocks for this step (only for paths still in bounds)
            Z = np.random.standard_normal(n_sims)

            # Update prices using GBM: S_t+1 = S_t * exp((r - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
            prices = prices * np.exp(drift + diffusion * Z)

            # Check for breaches - paths that exit bounds are marked as out
            in_bounds = in_bounds & (prices > lower_be) & (prices < upper_be)

            # Early termination optimization: if all paths have breached, stop early
            if not np.any(in_bounds):
                return 0.0

        # POP = proportion of paths that never touched either breakeven
        return np.mean(in_bounds)

    def monte_carlo_pop_vertical(self, S: float, breakeven: float, T: float,
                                  sigma: float, spread_type: str = 'put_credit',
                                  n_sims: int = 100000) -> float:
        """
        Monte Carlo simulation for vertical spread Probability of Profit at expiration.
        
        Unlike Black-Scholes closed-form which can underestimate POP due to 
        log-normal distribution assumptions, this simulates price at expiration
        using geometric Brownian motion for more accurate results.
        
        Args:
            S: Current underlying price
            breakeven: Breakeven price at expiration
            T: Time to expiration in years
            sigma: Annualized volatility
            spread_type: 'put_credit' (profit above breakeven) or 
                        'call_credit' (profit below breakeven)
            n_sims: Number of Monte Carlo simulations (default 100k for accuracy)
            
        Returns:
            Probability of profit (0.0 to 1.0)
        """
        if T <= 0 or sigma <= 0 or S <= 0 or breakeven <= 0:
            return 0.5 if S > breakeven else 0.0
        
        # Set random seed for reproducibility
        np.random.seed(42)
        
        # GBM parameters for terminal price distribution
        # ln(S_T/S_0) ~ N((r - 0.5*sigma^2)*T, sigma^2*T)
        drift = (self.r - 0.5 * sigma**2) * T
        vol = sigma * np.sqrt(T)
        
        # Generate terminal prices directly (more efficient than path simulation)
        # S_T = S_0 * exp(drift + vol * Z)
        Z = np.random.standard_normal(n_sims)
        S_T = S * np.exp(drift + vol * Z)
        
        # Calculate POP based on spread type
        if spread_type == 'put_credit':
            # Profit when price stays above breakeven
            profitable = S_T >= breakeven
        elif spread_type == 'call_credit':
            # Profit when price stays below breakeven
            profitable = S_T <= breakeven
        elif spread_type == 'put_debit':
            # Profit when price below breakeven
            profitable = S_T <= breakeven
        elif spread_type == 'call_debit':
            # Profit when price above breakeven
            profitable = S_T >= breakeven
        else:
            return 0.5
        
        return np.mean(profitable)

    def expected_value(self, pop: float, max_profit: float, max_loss: float) -> float:
        """
        Calculate Expected Value of a trade

        EV = (POP × max_profit) - ((1-POP) × max_loss)

        Returns 0.0 if inputs are non-finite or POP is out of range.
        """
        if not (np.isfinite(pop) and np.isfinite(max_profit) and np.isfinite(max_loss)):
            return 0.0
        pop = max(0.0, min(1.0, pop))
        return (pop * max_profit) - ((1 - pop) * max_loss)
    
    def risk_adjusted_return(self, ev: float, max_loss: float, 
                            annualize_factor: float = 1.0) -> float:
        """
        Calculate risk-adjusted return (Sharpe-like metric)
        
        EV per dollar of risk, optionally annualized
        """
        if max_loss <= 0:
            return 0.0
        return (ev / max_loss) * annualize_factor
    
    def monte_carlo_pop(self, S: float, T: float, sigma: float, 
                       payoff_func, n_sims: int = 100000) -> float:
        """
        Monte Carlo simulation for POP
        
        payoff_func: function that takes array of terminal prices and returns 
                     array of payoffs (positive = profit)
        """
        np.random.seed(42)  # Reproducible results
        
        dt = T / 252  # Daily steps (trading days)
        n_steps = int(T)
        
        # Geometric Brownian Motion
        Z = np.random.standard_normal((n_steps, n_sims))
        
        drift = (self.r - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt)
        
        prices = S * np.exp(np.cumsum(drift + diffusion * Z, axis=0))
        terminal_prices = prices[-1]
        
        payoffs = payoff_func(terminal_prices)
        profitable = payoffs > 0
        
        return np.mean(profitable)


class VolatilityAnalyzer:
    """
    Analyze volatility surfaces, skew, and term structure
    """
    
    def __init__(self):
        self.historical_vols = {}  # Cache for historical vol calculations
    
    def calculate_iv_rank(self, current_iv: float, iv_history: List[float]) -> float:
        """
        Calculate IV Rank: where current IV falls in historical range
        
        IVR = (current - min) / (max - min) * 100
        """
        if not iv_history or len(iv_history) < 2:
            return 50.0  # Neutral if no history
        
        min_iv = min(iv_history)
        max_iv = max(iv_history)
        
        if max_iv - min_iv < 0.01:
            return 50.0
        
        ivr = (current_iv - min_iv) / (max_iv - min_iv) * 100
        return max(0, min(100, ivr))
    
    def calculate_iv_percentile(self, current_iv: float, iv_history: List[float]) -> float:
        """
        Calculate IV Percentile: percentage of days IV was below current
        """
        if not iv_history:
            return 50.0
        
        below = sum(1 for iv in iv_history if iv < current_iv)
        return (below / len(iv_history)) * 100
    
    def skew_score(self, atm_iv: float, otm_put_iv: float, otm_call_iv: float) -> float:
        """
        Calculate volatility skew score
        
        Positive = puts more expensive (fear of downside)
        Negative = calls more expensive (speculation/bullish)
        Near 0 = balanced
        """
        if atm_iv <= 0:
            return 0.0
        
        put_skew = (otm_put_iv - atm_iv) / atm_iv
        call_skew = (otm_call_iv - atm_iv) / atm_iv
        
        return put_skew - call_skew
    
    def term_structure_slope(self, ivs_by_dte: dict) -> float:
        """
        Calculate term structure slope
        
        Positive = backwardation (near > far, fear/uncertainty)
        Negative = contango (far > near, normal)
        """
        if len(ivs_by_dte) < 2:
            return 0.0
        
        sorted_dtes = sorted(ivs_by_dte.keys())
        short_dte = sorted_dtes[0]
        long_dte = sorted_dtes[-1]
        
        short_iv = ivs_by_dte[short_dte]
        long_iv = ivs_by_dte[long_dte]
        
        if long_iv <= 0:
            return 0.0
        
        # Annualized slope
        return (short_iv - long_iv) / long_iv * 100


##############################################################################
# Kelly Criterion for Options Trading
##############################################################################

@dataclass
class KellyResult:
    """Result of Kelly criterion calculation."""
    raw_fraction: float
    adjusted_fraction: float
    edge: float
    expected_value: float


def kelly_criterion(pop: float, win_amount: float, loss_amount: float) -> KellyResult:
    """
    Calculate Kelly Criterion with validation.
    
    Args:
        pop: Probability of profit (0-1)
        win_amount: Average win amount
        loss_amount: Average loss amount (positive number)
        
    Returns:
        KellyResult with raw/adjusted fractions and edge
        
    Raises:
        ValueError: If inputs are invalid
    """
    if not 0 <= pop <= 1:
        raise ValueError(f"POP must be in [0,1], got {pop}")
    if win_amount <= 0:
        raise ValueError(f"Win amount must be positive, got {win_amount}")
    if loss_amount <= 0:
        raise ValueError(f"Loss amount must be positive, got {loss_amount}")
    
    loss_prob = 1 - pop
    odds = win_amount / loss_amount
    
    # Raw Kelly
    f_star = (pop * odds - loss_prob) / odds if odds > 0 else 0.0
    
    # Edge calculation
    ev = pop * win_amount - loss_prob * loss_amount
    edge = ev / loss_amount if loss_amount > 0 else 0.0
    
    # Apply half Kelly and cap at 25%
    adjusted = f_star * 0.5
    adjusted = max(0.0, min(adjusted, 0.25))
    
    return KellyResult(
        raw_fraction=f_star,
        adjusted_fraction=adjusted,
        edge=edge,
        expected_value=ev
    )


def fits_account_constraints(max_loss: float, margin_required: float = 0,
                             account_total: float = DEFAULT_ACCOUNT_TOTAL,
                             max_risk_per_trade: float = MAX_RISK_PER_TRADE,
                             min_cash_buffer: float = MIN_CASH_BUFFER) -> bool:
    """
    Check if trade fits within hard account constraints
    
    account_total: Total account balance (passed via --account CLI flag)
    max_risk_per_trade: Max dollar risk per trade (passed via --max-risk CLI flag)
    min_cash_buffer: Min cash to keep in reserve (passed via --min-cash CLI flag)
    """
    if max_loss > max_risk_per_trade:
        return False
    
    available = account_total - min_cash_buffer
    if margin_required > available:
        return False
    
    return True


def optimal_spread_width(underlying_price: float, max_loss: float = MAX_RISK_PER_TRADE) -> float:
    """
    Calculate optimal spread width given account constraints
    
    For small accounts ($100 max risk):
    - Need $2-5 wide spreads to fit account
    """
    # Assuming we sell at ~20% of width, max width for $100 risk
    # is about $5 wide ($100 / 0.20 = $500, but we need cushion)
    
    if underlying_price < 50:
        return 2.0  # Small cap stocks
    elif underlying_price < 200:
        return 3.0  # Mid cap
    else:
        return 5.0  # Large cap/ETFs


def calculate_realized_volatility(prices: List[float], periods: int = 20) -> float:
    """
    Calculate annualized realized volatility from price series
    
    Uses standard deviation of log returns
    """
    if len(prices) < periods + 1:
        return 0.0
    
    # Calculate log returns
    log_returns = np.diff(np.log(prices[-periods:]))
    
    # Annualized volatility (252 trading days)
    daily_vol = np.std(log_returns)
    annual_vol = daily_vol * np.sqrt(252)
    
    return annual_vol
