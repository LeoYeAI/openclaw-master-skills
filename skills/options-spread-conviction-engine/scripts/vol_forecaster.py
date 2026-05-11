"""
Volatility Forecasting Module for Options Conviction Engine

Implements GARCH(1,1) for realized volatility forecasting and
volatility risk premium analysis to identify options mispricing.

The volatility risk premium (VRP) is the difference between implied
volatility (IV) and realized volatility (RV). When VRP > 0, options
are overpriced relative to expected realized vol (favoring sellers).
When VRP < 0, options are underpriced (favoring buyers).

References:
- Engle, R. (1982). "Autoregressive Conditional Heteroskedasticity." Econometrica
- Bollerslev, T. (1986). "Generalized Autoregressive Conditional Heteroscedasticity"
- Sinclair, E. (2013). "Volatility Trading." Wiley Trading
"""
import numpy as np
import pandas as pd
from scipy import optimize, stats
from typing import Tuple, Dict, Optional, Literal
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings


@dataclass
class GARCHResult:
    """Container for GARCH model results."""
    omega: float  # Long-run variance constant
    alpha: float  # ARCH parameter (reaction to shocks)
    beta: float   # GARCH parameter (persistence)
    persistence: float  # alpha + beta (should be < 1)
    half_life: float  # Days for shock to decay 50%
    log_likelihood: float
    aic: float    # Akaike Information Criterion
    bic: float    # Bayesian Information Criterion
    converged: bool
    fitted_vol: pd.Series  # Fitted conditional volatility
    forecast: pd.Series  # Forecasted volatility


@dataclass
class VRPSignal:
    """Container for Volatility Risk Premium analysis."""
    current_iv: float
    forecast_rv: float
    vrp: float  # IV - RV (annualized percentage points)
    vrp_zscore: float  # VRP in standard deviations
    vrp_percentile: float  # Historical VRP percentile
    signal_strength: float  # 0-1 scale
    recommendation: Literal['STRONG_SELL', 'SELL', 'NEUTRAL', 'BUY', 'STRONG_BUY']
    reasoning: str


class VolatilityForecaster:
    """
    GARCH-based volatility forecasting for options edge detection.
    
    Uses GARCH(1,1) to forecast realized volatility, then compares
to implied volatility to identify volatility risk premium (VRP) edges.
    
    Typical usage:
        forecaster = VolatilityForecaster("SPY")
        garch = forecaster.fit_garch()
        forecast = forecaster.forecast_vol(horizon=21)
        vrp = forecaster.vol_risk_premium(current_iv=25.0)
    """
    
    def __init__(self, ticker: str, lookback_days: int = 252):
        """
        Initialize VolatilityForecaster.
        
        Args:
            ticker: Stock ticker symbol
            lookback_days: Days of historical returns for GARCH fitting
        """
        self.ticker = ticker
        self.lookback = lookback_days
        self._returns: Optional[pd.Series] = None
        self._garch_result: Optional[GARCHResult] = None
        self._annualization_factor = np.sqrt(252)
        
    def fetch_returns(self, end_date: Optional[datetime] = None) -> pd.Series:
        """
        Fetch historical log returns for GARCH modeling.
        
        Args:
            end_date: End date for historical data
            
        Returns:
            Series of log returns
        """
        import yfinance as yf
        
        if end_date is None:
            end_date = datetime.now()
        start_date = end_date - timedelta(days=int(self.lookback * 1.5))
        
        try:
            ticker = yf.Ticker(self.ticker)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                raise ValueError(f"No data returned for {self.ticker}")
            
            # Calculate log returns
            closes = hist['Close'].dropna()
            log_returns = np.log(closes / closes.shift(1)).dropna()
            
            # Use only lookback_days
            self._returns = log_returns.tail(self.lookback)
            return self._returns
            
        except Exception as e:
            raise ValueError(f"Failed to fetch returns for {self.ticker}: {e}")
    
    def _garch_likelihood(self, params: np.ndarray, 
                         returns: np.ndarray) -> float:
        """
        Calculate negative log-likelihood for GARCH(1,1).
        
        GARCH(1,1) variance equation:
        sigma^2_t = omega + alpha * r^2_{t-1} + beta * sigma^2_{t-1}
        """
        omega, alpha, beta = params
        
        # Parameter constraints
        if omega <= 0 or alpha < 0 or beta < 0:
            return 1e10
        if alpha + beta >= 0.999:  # Stationarity constraint
            return 1e10
            
        T = len(returns)
        sigma2 = np.zeros(T)
        
        # Initialize with unconditional variance
        sigma2[0] = np.var(returns)
        
        # Calculate conditional variances
        for t in range(1, T):
            sigma2[t] = omega + alpha * returns[t-1]**2 + beta * sigma2[t-1]
        
        # Calculate log-likelihood (assuming normal distribution)
        log_likelihood = -0.5 * np.sum(np.log(2 * np.pi * sigma2) + 
                                        returns**2 / sigma2)
        
        return -log_likelihood  # Return negative for minimization
    
    def fit_garch(self, returns: Optional[pd.Series] = None,
                  initial_params: Optional[np.ndarray] = None) -> GARCHResult:
        """
        Fit GARCH(1,1) model to returns using maximum likelihood.
        
        Args:
            returns: Series of returns (fetched if None)
            initial_params: Starting guess [omega, alpha, beta]
            
        Returns:
            GARCHResult with fitted parameters and diagnostics
        """
        if returns is None:
            if self._returns is None:
                returns = self.fetch_returns()
            else:
                returns = self._returns
        
        returns_array = returns.values
        
        # Minimum data check
        if len(returns_array) < 60:
            raise ValueError(f"Insufficient data for GARCH: {len(returns_array)} samples, need >= 60")
        
        # Initial parameter guess
        if initial_params is None:
            # Reasonable starting values based on typical GARCH fits
            omega_init = 0.000001
            alpha_init = 0.10
            beta_init = 0.85
            initial_params = np.array([omega_init, alpha_init, beta_init])
        
        # Parameter bounds
        bounds = [
            (1e-8, 1.0),   # omega
            (0.0, 0.999),  # alpha (typically 0.05-0.15)
            (0.0, 0.999)   # beta (typically 0.80-0.95)
        ]
        
        # Optimize
        try:
            result = optimize.minimize(
                self._garch_likelihood,
                initial_params,
                args=(returns_array,),
                method='L-BFGS-B',
                bounds=bounds,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )
            
            converged = result.success
            omega, alpha, beta = result.x
            
        except Exception as e:
            warnings.warn(f"GARCH optimization failed: {e}. Using initial guess.")
            omega, alpha, beta = initial_params
            converged = False
            result = type('obj', (object,), {'fun': 1e10})()
        
        # Calculate fitted conditional variances
        T = len(returns_array)
        sigma2 = np.zeros(T)
        sigma2[0] = np.var(returns_array)
        
        for t in range(1, T):
            sigma2[t] = omega + alpha * returns_array[t-1]**2 + beta * sigma2[t-1]
        
        # Convert to annualized volatility
        fitted_vol = pd.Series(
            np.sqrt(sigma2) * self._annualization_factor,
            index=returns.index
        )
        
        # Calculate diagnostics
        persistence = alpha + beta
        half_life = np.log(0.5) / np.log(persistence) if persistence > 0 else np.inf
        
        # AIC and BIC
        n_params = 3
        log_likelihood = -result.fun
        aic = 2 * n_params - 2 * log_likelihood
        bic = n_params * np.log(T) - 2 * log_likelihood
        
        garch_result = GARCHResult(
            omega=round(omega, 8),
            alpha=round(alpha, 4),
            beta=round(beta, 4),
            persistence=round(persistence, 4),
            half_life=round(half_life, 1),
            log_likelihood=round(log_likelihood, 2),
            aic=round(aic, 2),
            bic=round(bic, 2),
            converged=converged,
            fitted_vol=fitted_vol,
            forecast=pd.Series()  # Will be populated by forecast_vol()
        )
        
        self._garch_result = garch_result
        return garch_result
    
    def forecast_vol(self, horizon: int = 21) -> pd.Series:
        """
        Forecast realized volatility using fitted GARCH model.
        
        Args:
            horizon: Number of days to forecast (default: 21 trading days ≈ 1 month)
            
        Returns:
            Series of forecasted annualized volatilities
            
        Note:
            GARCH forecasts converge to long-run average volatility:
            sigma^2_long_run = omega / (1 - alpha - beta)
        """
        if self._garch_result is None:
            self.fit_garch()
        
        garch = self._garch_result
        omega, alpha, beta = garch.omega, garch.alpha, garch.beta
        
        # Long-run variance
        persistence = alpha + beta
        if persistence >= 1:
            warnings.warn("Non-stationary GARCH: persistence >= 1")
            long_run_var = omega / (1 - 0.999)
        else:
            long_run_var = omega / (1 - persistence)
        
        # Current variance (last fitted value)
        current_var = (garch.fitted_vol.iloc[-1] / self._annualization_factor) ** 2
        
        # Multi-step forecast
        forecasts = []
        for h in range(1, horizon + 1):
            # GARCH(1,1) multi-step forecast formula
            forecast_var = long_run_var + (persistence ** h) * (current_var - long_run_var)
            forecast_vol = np.sqrt(forecast_var) * self._annualization_factor
            forecasts.append(forecast_vol)
        
        # Create forecast series
        last_date = garch.fitted_vol.index[-1]
        forecast_index = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=horizon,
            freq='B'  # Business days
        )
        
        forecast_series = pd.Series(forecasts, index=forecast_index)
        self._garch_result.forecast = forecast_series
        
        return forecast_series
    
    def vol_risk_premium(self, current_iv: float, 
                        iv_source: str = "input",
                        lookback_vrp: int = 126) -> VRPSignal:
        """
        Calculate Volatility Risk Premium and generate trading signal.
        
        VRP = Implied Volatility - Forecast Realized Volatility
        
        Args:
            current_iv: Current implied volatility (annualized %)
            iv_source: Description of IV source (for metadata)
            lookback_vrp: Days to calculate historical VRP distribution
            
        Returns:
            VRPSignal with VRP metrics and trading recommendation
        """
        if self._garch_result is None or len(self._garch_result.forecast) == 0:
            self.fit_garch()
            self.forecast_vol(horizon=21)
        
        # Use average forecast over horizon
        forecast_rv = self._garch_result.forecast.mean()
        
        # Calculate VRP
        vrp = current_iv - forecast_rv
        
        # Simplified VRP z-score using rule-of-thumb thresholds
        # Typical VRP ranges from -5% to +10%
        vrp_mean = 0.025  # Historical average VRP ~2-3% (decimal)
        vrp_std = 0.04    # Typical std dev of VRP (decimal)

        vrp_zscore = (vrp - vrp_mean) / vrp_std
        vrp_percentile = stats.norm.cdf(vrp_zscore) * 100
        
        # Signal strength (0 to 1)
        signal_strength = min(abs(vrp_zscore) / 2.0, 1.0)
        
        # Generate recommendation
        if vrp_zscore > 2.0:
            recommendation = 'STRONG_SELL'  # IV very rich, sell options
        elif vrp_zscore > 1.0:
            recommendation = 'SELL'  # IV moderately rich
        elif vrp_zscore > -1.0:
            recommendation = 'NEUTRAL'  # IV fairly priced
        elif vrp_zscore > -2.0:
            recommendation = 'BUY'  # IV moderately cheap
        else:
            recommendation = 'STRONG_BUY'  # IV very cheap
        
        # Build reasoning
        if vrp > 3:
            reasoning = f"IV ({current_iv:.1f}%) significantly exceeds forecast RV ({forecast_rv:.1f}%). VRP={vrp:+.1f}%. Favorable for selling premium."
        elif vrp < -3:
            reasoning = f"IV ({current_iv:.1f}%) well below forecast RV ({forecast_rv:.1f}%). VRP={vrp:+.1f}%. Favorable for buying options."
        else:
            reasoning = f"IV ({current_iv:.1f}%) near forecast RV ({forecast_rv:.1f}%). VRP={vrp:+.1f}%. Limited edge from vol mispricing."
        
        return VRPSignal(
            current_iv=round(current_iv, 2),
            forecast_rv=round(forecast_rv, 2),
            vrp=round(vrp, 2),
            vrp_zscore=round(vrp_zscore, 2),
            vrp_percentile=round(vrp_percentile, 1),
            signal_strength=round(signal_strength, 2),
            recommendation=recommendation,
            reasoning=reasoning
        )
    
    def add_to_conviction(self, base_score: float, vrp_signal: VRPSignal,
                         strategy: str) -> Tuple[float, str]:
        """
        Adjust conviction score based on VRP signal alignment with strategy.
        
        Credit spreads (selling) benefit from high VRP (IV > RV)
        Debit spreads (buying) benefit from negative VRP (IV < RV)
        
        Args:
            base_score: Original conviction score (0-100)
            vrp_signal: VRPSignal from vol_risk_premium()
            strategy: Options strategy
            
        Returns:
            Tuple of (adjusted_score, reasoning)
        """
        # Strategy categories
        credit_strategies = ['bull_put', 'bear_call', 'iron_condor', 'calendar']
        debit_strategies = ['bull_call', 'bear_put', 'butterfly']
        
        vrp = vrp_signal.vrp
        zscore = vrp_signal.vrp_zscore
        
        # Determine adjustment
        if strategy in credit_strategies:
            # Credit strategies benefit from positive VRP (high IV)
            if zscore > 1.5:
                adjustment = 12
                reason = f"VRP z={zscore:.1f}: IV rich, favorable for credit spread"
            elif zscore > 0.5:
                adjustment = 6
                reason = f"VRP z={zscore:.1f}: IV moderately rich, slight edge for selling"
            elif zscore > -0.5:
                adjustment = 0
                reason = f"VRP z={zscore:.1f}: Fair IV pricing, no VRP edge"
            elif zscore > -1.5:
                adjustment = -5
                reason = f"VRP z={zscore:.1f}: IV moderately cheap, slight headwind for selling"
            else:
                adjustment = -10
                reason = f"VRP z={zscore:.1f}: IV cheap, unfavorable for credit spreads"
                
        elif strategy in debit_strategies:
            # Debit strategies benefit from negative VRP (cheap IV)
            if zscore < -1.5:
                adjustment = 12
                reason = f"VRP z={zscore:.1f}: IV cheap, favorable for debit spread"
            elif zscore < -0.5:
                adjustment = 6
                reason = f"VRP z={zscore:.1f}: IV moderately cheap, slight edge for buying"
            elif zscore < 0.5:
                adjustment = 0
                reason = f"VRP z={zscore:.1f}: Fair IV pricing, no VRP edge"
            elif zscore < 1.5:
                adjustment = -5
                reason = f"VRP z={zscore:.1f}: IV moderately rich, slight headwind for buying"
            else:
                adjustment = -10
                reason = f"VRP z={zscore:.1f}: IV expensive, unfavorable for debit spreads"
        else:
            adjustment = 0
            reason = f"Unknown strategy {strategy}, no VRP adjustment"
        
        adjusted_score = max(0, min(100, base_score + adjustment))
        
        return round(adjusted_score, 1), reason
    
    def get_model_diagnostics(self) -> Dict:
        """
        Return GARCH model diagnostics for validation.
        
        Checks:
        - Stationarity: persistence should be < 1
        - Half-life: should be reasonable (5-100 days typical)
        - Convergence: optimization should succeed
        """
        if self._garch_result is None:
            return {"error": "Model not fitted yet"}
        
        g = self._garch_result
        
        diagnostics = {
            "stationarity": {
                "persistence": g.persistence,
                "stationary": g.persistence < 0.999,
                "assessment": "PASS" if g.persistence < 0.999 else "FAIL"
            },
            "half_life": {
                "days": g.half_life,
                "assessment": "REASONABLE" if 5 <= g.half_life <= 200 else "UNUSUAL"
            },
            "parameters": {
                "alpha (shock)": g.alpha,
                "beta (persistence)": g.beta,
                "ratio": g.alpha / g.beta if g.beta > 0 else None,
                "assessment": "REASONABLE" if 0.05 <= g.alpha <= 0.25 and 0.70 <= g.beta <= 0.95 else "UNUSUAL"
            },
            "convergence": {
                "success": g.converged,
                "assessment": "PASS" if g.converged else "WARNING"
            },
            "information_criteria": {
                "aic": g.aic,
                "bic": g.bic
            }
        }
        
        return diagnostics


if __name__ == "__main__":
    """Demo: Fit GARCH and analyze VRP for SPY."""
    print("=" * 70)
    print("VOLATILITY FORECASTER - GARCH(1,1) DEMO")
    print("=" * 70)
    
    try:
        # Demo with SPY
        ticker = "SPY"
        forecaster = VolatilityForecaster(ticker, lookback_days=252)
        
        print(f"\nFitting GARCH(1,1) to {ticker} returns...")
        garch = forecaster.fit_garch()
        
        print(f"\nGARCH Parameters:")
        print(f"  omega (constant): {garch.omega:.8f}")
        print(f"  alpha (ARCH):     {garch.alpha:.4f}")
        print(f"  beta (GARCH):     {garch.beta:.4f}")
        print(f"  persistence:      {garch.persistence:.4f}")
        print(f"  half-life:        {garch.half_life:.1f} days")
        print(f"  converged:        {garch.converged}")
        
        # Forecast
        print(f"\n21-Day Volatility Forecast:")
        forecast = forecaster.forecast_vol(horizon=21)
        print(f"  Current fitted vol: {garch.fitted_vol.iloc[-1]*100:.1f}%")
        print(f"  Forecast (day 1):   {forecast.iloc[0]*100:.1f}%")
        print(f"  Forecast (day 21):  {forecast.iloc[-1]*100:.1f}%")
        print(f"  Long-run avg:       {forecast.mean()*100:.1f}%")
        
        # VRP Analysis with example IV levels
        print(f"\nVolatility Risk Premium Analysis:")
        test_ivs = [0.15, 0.20, 0.25, 0.30]  # Decimal format (15%, 20%, etc.)
        for iv in test_ivs:
            vrp = forecaster.vol_risk_premium(current_iv=iv)
            print(f"  IV={iv*100:.0f}% → VRP={vrp.vrp*100:+.1f}% (z={vrp.vrp_zscore:+.1f}) [{vrp.recommendation}]")
        
        # Diagnostics
        print(f"\nModel Diagnostics:")
        diag = forecaster.get_model_diagnostics()
        for category, info in diag.items():
            if isinstance(info, dict) and 'assessment' in info:
                print(f"  {category}: {info['assessment']}")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
