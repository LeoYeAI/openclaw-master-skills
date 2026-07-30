"""
Variance Reduction Techniques for Monte Carlo Pricing
=======================================================
Three stackable variance reduction techniques for European call option
pricing via Monte Carlo simulation, each exploiting a different structural
property of the problem.

1. Antithetic Variates
   For every standard normal draw Z, also evaluate the payoff at -Z.
   The paired payoffs are negatively correlated: when S_T(+Z) is above
   strike, S_T(-Z) tends to be below. Averaging the pair before taking
   the overall mean removes much of this noise. Typical variance reduction
   is 50-75% at zero extra cost beyond the doubled function evaluations.

2. Control Variates
   Use S_T as a control variate with known expectation E[S_T] = S0*exp(r*T)
   under the risk-neutral measure. Estimate regression coefficient beta as
   Cov(payoff, S_T) divided by Var(S_T), then form the adjusted estimator:
       Y_adj = payoff - beta*(S_T - E[S_T])
   Y_adj has the same expectation but reduced variance, exploiting the
   correlation between the option payoff and the underlying.

3. Stratified Sampling
   Partition [0,1] into n equal strata. Draw one uniform per stratum,
   convert via inverse CDF (probit). Forces full coverage of the
   probability space; variance is guaranteed <= crude MC by the law of
   total variance.

4. Combined
   All three stacked: stratified Z values -> antithetic pairs -> control
   variate adjustment. Routinely achieves 100-500x variance reduction
   vs crude MC. This is table stakes in production.

Based on: "How to Simulate Like a Quant Desk" by @gemchange_ltd
"""

import numpy as np
from scipy.stats import norm as sp_norm


# ---------------------------------------------------------------------------
# Black-Scholes analytical reference (European call)
# ---------------------------------------------------------------------------

def bs_call_price(S0: float, K: float, sigma: float, T: float, r: float) -> float:
    """
    Black-Scholes European call price (analytical).

    C = S0 * N(d1) - K * exp(-r*T) * N(d2)

    Parameters
    ----------
    S0, K, sigma, T, r : float
        Standard Black-Scholes parameters.

    Returns
    -------
    float
        European call option price.
    """
    denom = sigma * np.sqrt(T)
    d1 = (np.log(S0/K) + (r + 0.5*sigma**2)*T) / denom
    d2 = d1 - sigma * np.sqrt(T)
    return float(S0 * sp_norm.cdf(d1) - K * np.exp(-r * T) * sp_norm.cdf(d2))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _gbm_terminal(
    S0: float, sigma: float, T: float, r: float, Z: np.ndarray
) -> np.ndarray:
    """Risk-neutral GBM terminal prices from standard normals Z."""
    return S0 * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)


def _call_payoff(S_T: np.ndarray, K: float, r: float, T: float) -> np.ndarray:
    """Discounted European call payoff: exp(-r*T) * max(S_T - K, 0)."""
    return np.exp(-r * T) * np.maximum(S_T - K, 0.0)


# ---------------------------------------------------------------------------
# Pricing methods
# ---------------------------------------------------------------------------

def crude_mc(
    S0: float,
    K: float,
    sigma: float,
    T: float,
    r: float,
    n_paths: int,
    rng: np.random.Generator,
) -> tuple:
    """
    Plain Monte Carlo European call pricing with no variance reduction.

    Simulates n_paths independent GBM paths, computes discounted call
    payoffs max(S_T - K, 0)*exp(-r*T), and takes the sample mean.

    Parameters
    ----------
    S0, K, sigma, T, r : float
        Option and market parameters.
    n_paths : int
        Number of simulated paths.
    rng : np.random.Generator
        Random generator (np.random.default_rng).

    Returns
    -------
    price_estimate : float
        MC estimate of the call price.
    variance : float
        Estimator variance: sample variance of payoffs divided by n_paths.
    """
    Z = rng.standard_normal(n_paths)
    S_T = _gbm_terminal(S0, sigma, T, r, Z)
    payoffs = _call_payoff(S_T, K, r, T)
    price = float(payoffs.mean())
    variance = float(payoffs.var()/n_paths)
    return price, variance


def antithetic_mc(
    S0: float,
    K: float,
    sigma: float,
    T: float,
    r: float,
    n_paths: int,
    rng: np.random.Generator,
) -> tuple:
    """
    Antithetic variates Monte Carlo for European call pricing.

    Draws n_paths//2 standard normals Z. For each Z, evaluates the payoff
    at both +Z and -Z, and averages the pair. The paired payoffs are
    negatively correlated, reducing estimator variance by 50-75%.

    Parameters
    ----------
    S0, K, sigma, T, r : float
        Option and market parameters.
    n_paths : int
        Total effective path count (n_paths//2 draws, doubled by antithetics).
    rng : np.random.Generator
        Random generator.

    Returns
    -------
    price_estimate : float
        Antithetic MC call price estimate.
    variance : float
        Estimator variance of the paired mean.
    """
    half = n_paths // 2
    Z = rng.standard_normal(half)

    S_pos = _gbm_terminal(S0, sigma, T, r,  Z)
    S_neg = _gbm_terminal(S0, sigma, T, r, -Z)

    payoff_pos = _call_payoff(S_pos, K, r, T)
    payoff_neg = _call_payoff(S_neg, K, r, T)

    # Average each antithetic pair first, then average across all pairs
    paired = 0.5 * (payoff_pos + payoff_neg)
    price = float(paired.mean())
    variance = float(paired.var()/half)
    return price, variance


def control_variate_mc(
    S0: float,
    K: float,
    sigma: float,
    T: float,
    r: float,
    n_paths: int,
    rng: np.random.Generator,
) -> tuple:
    """
    Control variate Monte Carlo using S_T as the control.

    The terminal asset price S_T has known expectation E[S_T] = S0*exp(r*T)
    under the risk-neutral measure. We estimate the regression coefficient
    beta = Cov(payoff, S_T) divided by Var(S_T) from the MC sample, then
    form the adjusted estimator:

        Y_adj = payoff - beta * (S_T - E[S_T])

    Y_adj has the same expectation as the raw payoff but lower variance,
    because it removes the component of payoff variation that correlates
    with the control variate.

    Parameters
    ----------
    S0, K, sigma, T, r : float
        Option and market parameters.
    n_paths : int
        Number of simulated paths.
    rng : np.random.Generator
        Random generator.

    Returns
    -------
    price_estimate : float
        Control-variate adjusted call price estimate.
    variance : float
        Estimator variance of the adjusted payoffs.
    """
    Z = rng.standard_normal(n_paths)
    S_T = _gbm_terminal(S0, sigma, T, r, Z)
    payoffs = _call_payoff(S_T, K, r, T)

    # Analytical expectation of the control variate under risk-neutral measure
    E_S_T = S0 * np.exp(r * T)

    # Estimate beta via 2x2 sample covariance matrix
    cov_yc = np.cov(payoffs, S_T)
    beta = cov_yc[0,1]/cov_yc[1,1]

    # Adjusted payoffs: same mean, reduced variance
    adjusted = payoffs - beta * (S_T - E_S_T)
    price = float(adjusted.mean())
    variance = float(adjusted.var()/n_paths)
    return price, variance


def stratified_mc(
    S0: float,
    K: float,
    sigma: float,
    T: float,
    r: float,
    n_paths: int,
    rng: np.random.Generator,
) -> tuple:
    """
    Stratified sampling Monte Carlo for European call pricing.

    Partitions [0,1] into n_paths equal strata. For stratum i, draws
    U_i ~ Uniform(i/n, (i+1)/n) and converts to a standard normal via
    the inverse CDF (probit). Forces complete coverage of the probability
    space. Variance is guaranteed <= crude MC by the law of total variance,
    with maximum gain when payoff variance varies across strata.

    Parameters
    ----------
    S0, K, sigma, T, r : float
        Option and market parameters.
    n_paths : int
        Number of equal strata and simulated paths.
    rng : np.random.Generator
        Random generator.

    Returns
    -------
    price_estimate : float
        Stratified MC call price estimate.
    variance : float
        Estimator variance of stratified payoffs.
    """
    # Strata lower and upper bounds using linspace for exact arithmetic
    lo = np.linspace(0.0, 1.0 - 1.0/n_paths, n_paths)
    hi = lo + 1.0/n_paths

    # One stratified uniform draw per stratum
    U = lo + rng.uniform(0.0, 1.0, n_paths) * (hi - lo)

    # Map to standard normal via inverse CDF
    Z = sp_norm.ppf(U)

    S_T = _gbm_terminal(S0, sigma, T, r, Z)
    payoffs = _call_payoff(S_T, K, r, T)

    price = float(payoffs.mean())
    variance = float(payoffs.var()/n_paths)
    return price, variance


def combined_mc(
    S0: float,
    K: float,
    sigma: float,
    T: float,
    r: float,
    n_paths: int,
    rng: np.random.Generator,
) -> tuple:
    """
    Combined variance reduction: stratified + antithetic + control variate.

    Steps:
      1. Stratified sampling generates n_paths//2 Z values with full
         coverage of the [0,1] probability space.
      2. Antithetic pairing: evaluate payoffs at both +Z and -Z.
      3. Average each antithetic pair to form n_paths//2 reduced payoffs.
      4. Control variate adjustment using paired S_T values as control.

    Routinely achieves 100-500x variance reduction vs crude MC.

    Parameters
    ----------
    S0, K, sigma, T, r : float
        Option and market parameters.
    n_paths : int
        Total effective path count (n_paths//2 draws doubled by antithetics).
    rng : np.random.Generator
        Random generator.

    Returns
    -------
    price_estimate : float
        Combined adjusted call price estimate.
    variance : float
        Estimator variance of the combined adjusted payoffs.
    """
    half = n_paths // 2

    # Step 1: Stratified uniform draws for half paths
    lo = np.linspace(0.0, 1.0 - 1.0/half, half)
    hi = lo + 1.0/half
    U = lo + rng.uniform(0.0, 1.0, half) * (hi - lo)
    Z = sp_norm.ppf(U)

    # Step 2: Antithetic pairs from stratified Z values
    S_pos = _gbm_terminal(S0, sigma, T, r,  Z)
    S_neg = _gbm_terminal(S0, sigma, T, r, -Z)

    payoff_pos = _call_payoff(S_pos, K, r, T)
    payoff_neg = _call_payoff(S_neg, K, r, T)

    # Step 3: Average each antithetic pair
    paired_payoffs = 0.5 * (payoff_pos + payoff_neg)
    paired_S_T     = 0.5 * (S_pos + S_neg)

    # Step 4: Control variate adjustment on the paired quantities
    E_S_T = S0 * np.exp(r * T)
    cov_pc = np.cov(paired_payoffs, paired_S_T)
    beta = cov_pc[0,1]/cov_pc[1,1]

    adjusted = paired_payoffs - beta * (paired_S_T - E_S_T)
    price = float(adjusted.mean())
    variance = float(adjusted.var()/half)
    return price, variance


if __name__ == "__main__":
    print("=" * 70)
    print("  VARIANCE REDUCTION TECHNIQUES")
    print("=" * 70)

    # Demo parameters
    S0      = 100.0
    K       = 100.0
    sigma   = 0.20
    T       = 1.0
    r       = 0.05
    n_paths = 100_000

    print(f"\nOption parameters: S0={S0}, K={K}, sigma={sigma}, T={T}yr, r={r}")
    print(f"Paths per method:  {n_paths:,}")

    # Analytical Black-Scholes reference
    bs_price = bs_call_price(S0, K, sigma, T, r)
    print(f"\nBlack-Scholes analytical call price: {bs_price:.6f}")

    # Run all five methods with the same seed for a fair comparison
    methods = [
        ("Crude MC",        crude_mc),
        ("Antithetic",      antithetic_mc),
        ("Control Variate", control_variate_mc),
        ("Stratified",      stratified_mc),
        ("Combined",        combined_mc),
    ]

    results = {}
    for name, func in methods:
        rng = np.random.default_rng(42)
        price, var = func(S0, K, sigma, T, r, n_paths, rng)
        results[name] = (price, var)

    # Crude MC variance is the denominator for the VR factor
    crude_var = results["Crude MC"][1]

    print(
        f"\n{'Method':<20}  {'Price':>10}  {'Variance':>14}"
        f"  {'VR Factor':>10}  {'Error vs BS':>12}"
    )
    print("-" * 74)

    for name, (price, var) in results.items():
        vr_factor = crude_var / var if var > 0 else float("inf")
        error = abs(price - bs_price)
        print(
            f"{name:<20}  {price:>10.6f}  {var:>14.2e}"
            f"  {vr_factor:>10.2f}x  {error:>12.6f}"
        )

    print(f"\nNotes:")
    print(f"  VR Factor = crude variance divided by method variance (higher = better).")
    print(f"  VR Factor of 1.0x means no improvement over crude MC.")
    print(f"  Combined method stacks all three for maximum variance reduction.")
    print("=" * 70)
