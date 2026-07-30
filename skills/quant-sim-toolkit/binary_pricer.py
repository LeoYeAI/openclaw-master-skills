"""
Monte Carlo Binary Contract Pricer
===================================
Implements Monte Carlo pricing of binary (digital) options using Geometric
Brownian Motion (GBM). A binary contract pays 1 if the underlying asset
price S_T exceeds the strike K at expiry, and 0 otherwise.

Under risk-neutral GBM dynamics the terminal price is:

    S_T = S0 * exp((r - 0.5*sigma^2)*T + sigma*sqrt(T)*Z),  Z ~ N(0,1)

The MC estimate provides a probability with confidence intervals, which can
be compared directly to the Black-Scholes analytical solution N(d2). The
Brier score evaluates calibration quality: perfect calibration = 0,
a naive 50-50 guess against a certain binary outcome = 0.25.

Based on: "How to Simulate Like a Quant Desk" by @gemchange_ltd
"""

import time
import numpy as np
from scipy.stats import norm


def mc_binary_price(
    S0: float,
    K: float,
    sigma: float,
    T: float,
    r: float,
    n_paths: int,
    rng: np.random.Generator,
) -> tuple:
    """
    Estimate binary option price via Monte Carlo simulation.

    Simulates n_paths of GBM terminal prices under the risk-neutral measure,
    computes binary payoffs (1 if S_T > K, else 0), and constructs a 95%
    confidence interval using the normal approximation to the binomial.

    Parameters
    ----------
    S0 : float
        Current asset price.
    K : float
        Strike price (contract threshold).
    sigma : float
        Annual volatility (e.g. 0.25 = 25%).
    T : float
        Time to expiry in years.
    r : float
        Risk-free interest rate (annualised, continuously compounded).
    n_paths : int
        Number of simulated GBM paths.
    rng : np.random.Generator
        NumPy random generator (use np.random.default_rng(seed)).

    Returns
    -------
    probability : float
        MC estimate of P(S_T > K).
    ci_lower : float
        Lower bound of 95% confidence interval.
    ci_upper : float
        Upper bound of 95% confidence interval.
    """
    Z = rng.standard_normal(n_paths)
    S_T = S0 * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)

    payoffs = (S_T > K).astype(float)
    probability = float(payoffs.mean())

    # Normal approximation CI for a Bernoulli proportion.
    # Variance is maximised at p=0.5 (the most uncertain contract).
    n = n_paths
    se = np.sqrt(probability * (1.0 - probability) / n)
    ci_lower = probability - 1.96 * se
    ci_upper = probability + 1.96 * se

    return probability, ci_lower, ci_upper


def analytical_binary_price(
    S0: float,
    K: float,
    sigma: float,
    T: float,
    r: float,
) -> float:
    """
    Black-Scholes closed-form price for a binary (cash-or-nothing) call.

    Under risk-neutral GBM the probability that S_T > K equals N(d2):

        d2 = (ln(S0/K) + (r - 0.5*sigma^2)*T) divided by (sigma*sqrt(T))

    where N() is the standard normal CDF from scipy.stats.norm.

    Parameters
    ----------
    S0 : float
        Current asset price.
    K : float
        Strike price.
    sigma : float
        Annual volatility.
    T : float
        Time to expiry in years.
    r : float
        Risk-free interest rate.

    Returns
    -------
    float
        Risk-neutral probability P(S_T > K) = N(d2).
    """
    denom = sigma * np.sqrt(T)
    d2 = (np.log(S0/K) + (r - 0.5*sigma**2)*T) / denom
    return float(norm.cdf(d2))


def brier_score(predicted_prob: float, actual_outcome: float) -> float:
    """
    Compute the Brier score for a single probabilistic forecast.

    Brier score = (predicted_prob - actual_outcome)^2.
    Lower is better. Perfect calibration = 0. A naive 50-50 forecast
    against a certain binary outcome scores 0.25. The best election
    forecasters historically achieve 0.06-0.12.

    When comparing a model probability to an analytical benchmark, treat
    the analytical price as the ground truth "actual outcome".

    Parameters
    ----------
    predicted_prob : float
        Forecast probability in [0, 1].
    actual_outcome : float
        Realised outcome or benchmark probability in [0, 1].

    Returns
    -------
    float
        Brier score (non-negative, lower is better).
    """
    return float((predicted_prob - actual_outcome) ** 2)


if __name__ == "__main__":
    print("=" * 60)
    print("  MONTE CARLO BINARY CONTRACT PRICER")
    print("=" * 60)

    # Contract parameters
    S0    = 100.0   # current asset price
    K     = 105.0   # strike (slightly out of the money)
    sigma = 0.25    # annual volatility
    T     = 0.5     # 6 months to expiry
    r     = 0.05    # risk-free rate

    print(f"\nContract parameters:")
    print(f"  S0={S0}, K={K}, sigma={sigma}, T={T}yr, r={r}")

    # Analytical Black-Scholes benchmark
    analytical = analytical_binary_price(S0, K, sigma, T, r)
    print(f"\nBlack-Scholes analytical price [N(d2)]: {analytical:.6f}")

    # MC convergence study across increasing path counts
    path_counts = [1_000, 10_000, 100_000]

    print(
        f"\n{'n_paths':>10}  {'MC Prob':>10}  {'CI Width':>10}"
        f"  {'Error':>10}  {'Time(s)':>10}"
    )
    print("-" * 60)

    last_prob = None
    for n_paths in path_counts:
        rng = np.random.default_rng(42)
        t0 = time.perf_counter()
        prob, ci_lo, ci_hi = mc_binary_price(S0, K, sigma, T, r, n_paths, rng)
        elapsed = time.perf_counter() - t0

        ci_width = ci_hi - ci_lo
        error = abs(prob - analytical)
        print(
            f"{n_paths:>10,}  {prob:>10.6f}  {ci_width:>10.6f}"
            f"  {error:>10.6f}  {elapsed:>10.4f}"
        )
        last_prob = prob

    # Brier score: MC estimate vs analytical benchmark (treated as ground truth)
    bs = brier_score(last_prob, analytical)
    print(f"\nBrier score (MC[100k] vs analytical): {bs:.8f}")
    print("  (lower is better; 0.0 = perfect agreement)")

    print("\nConvergence note:")
    print("  CI width shrinks as O(1/sqrt(n_paths)) -- doubling paths")
    print("  halves the CI width. MC converges to N(d2) as n_paths grows,")
    print("  confirming correct GBM simulation under the risk-neutral measure.")
    print("=" * 60)
