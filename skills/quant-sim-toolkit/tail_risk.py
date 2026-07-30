"""
Importance Sampling for Tail Risk Estimation
=============================================

Crude Monte Carlo is fundamentally inefficient for estimating the probability
of rare, extreme events. When P(crash) ~ 0.001, a simulation with 100,000 paths
might see only ~100 hits -- producing a noisy, high-variance estimate.

IMPORTANCE SAMPLING (IS) fixes this by changing the sampling distribution to one
that oversamples the rare region, then correcting for bias using likelihood ratios.

    E_P[f(X)] = E_Q[ f(X) * (dP/dQ)(X) ]

EXPONENTIAL TILTING for GBM crash probability:
Under the tilted measure Q, draw Z_tilde ~ N(0,1) and set Z = Z_tilde - theta.
Likelihood ratio: LR = exp(theta*Z_tilde - 0.5*theta^2)

Variance Reduction Factor:
    VR = crude_var/IS_var

Higher VR = more efficient IS. Values of 100x to 10,000x are typical for
extreme tail events.
"""

import numpy as np


def crude_mc_crash(S0, K_crash, sigma, T, r, n_paths, rng):
    """
    Estimate P(S_T < K_crash) using crude Monte Carlo simulation.

    Parameters
    ----------
    S0 : float -- Current asset price.
    K_crash : float -- Crash threshold (crash if S_T < K_crash).
    sigma : float -- Annual volatility.
    T : float -- Time horizon in years.
    r : float -- Risk-free rate.
    n_paths : int -- Number of Monte Carlo paths.
    rng : np.random.Generator

    Returns
    -------
    prob : float -- Estimated P(S_T < K_crash).
    variance : float -- Estimator variance: p*(1-p)/n_paths.
    """
    Z = rng.standard_normal(n_paths)
    log_return = (r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z
    S_T = S0*np.exp(log_return)
    hits = (S_T < K_crash).astype(float)
    prob = hits.mean()
    variance = prob*(1.0 - prob)/n_paths
    return prob, variance


def importance_sampling_crash(S0, K_crash, sigma, T, r, theta, n_paths, rng):
    """
    Estimate P(S_T < K_crash) using importance sampling with exponential tilting.

    Under tilted measure Q: draw Z_tilde ~ N(0,1), set Z = Z_tilde - theta.
    Likelihood ratio: LR = exp(theta*Z_tilde - 0.5*theta^2)
    IS estimator = mean(indicator(S_T < K_crash) * LR)

    Parameters
    ----------
    S0 : float -- Current asset price.
    K_crash : float -- Crash threshold.
    sigma : float -- Annual volatility.
    T : float -- Time horizon in years.
    r : float -- Risk-free rate.
    theta : float -- Tilting parameter. Use optimal_theta() for best efficiency.
    n_paths : int -- Number of IS paths.
    rng : np.random.Generator

    Returns
    -------
    prob : float -- IS estimate of P(S_T < K_crash).
    variance : float -- IS estimator variance: Var(indicator*LR)/n_paths.
    """
    Z_tilde = rng.standard_normal(n_paths)
    Z = Z_tilde - theta
    log_return = (r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z
    S_T = S0*np.exp(log_return)
    likelihood_ratio = np.exp(theta*Z_tilde - 0.5*theta**2)
    indicator = (S_T < K_crash).astype(float)
    is_weights = indicator*likelihood_ratio
    prob = is_weights.mean()
    variance = is_weights.var()/n_paths
    return prob, variance


def optimal_theta(S0, K_crash, sigma, T, r):
    """
    Compute the approximately optimal exponential tilting parameter theta.

    Shifts the mean of log(S_T) from its original value down to log(K_crash),
    giving roughly 50% hit rate under the tilted measure (maximum efficiency).

    Formula:
        mu = r - 0.5*sigma^2
        theta = (log(S0) + mu*T - log(K_crash))/(sigma*sqrt(T))

    Parameters
    ----------
    S0 : float -- Current asset price.
    K_crash : float -- Crash threshold.
    sigma : float -- Annual volatility.
    T : float -- Time horizon in years.
    r : float -- Risk-free rate.

    Returns
    -------
    theta : float -- Optimal tilting parameter (positive for downside events).
    """
    mu = r - 0.5*sigma**2
    original_mean = np.log(S0) + mu*T
    target_mean = np.log(K_crash)
    theta = (original_mean - target_mean)/(sigma*np.sqrt(T))
    return theta


if __name__ == "__main__":
    print("=" * 60)
    print("  IMPORTANCE SAMPLING FOR TAIL RISK")
    print("=" * 60)

    rng = np.random.default_rng(42)

    S0 = 100.0
    K_crash = 50.0
    sigma = 0.3
    T = 1.0
    r = 0.05

    print()
    print("Scenario: Estimating P(50% crash in 1 year)")
    print(f"  Asset:      S0 = ${S0:.0f}")
    print(f"  Crash at:   K  = ${K_crash:.0f}  ({(1 - K_crash/S0)*100:.0f}% drawdown)")
    print(f"  Volatility: sigma = {sigma:.0%}")
    print(f"  Horizon:    T = {T:.0f} year")
    print(f"  Risk-free:  r = {r:.0%}")

    theta_opt = optimal_theta(S0, K_crash, sigma, T, r)
    print()
    print(f"Optimal theta: {theta_opt:.4f}")
    print("  (Centers the tilted distribution on the crash threshold)")

    N = 100_000
    print()
    print(f"{'Method':<30} {'P(crash)':<14} {'Variance':<16} {'Std Error':<12}")
    print("-" * 72)

    p_crude, var_crude = crude_mc_crash(
        S0, K_crash, sigma, T, r, N, np.random.default_rng(42))
    se_crude = np.sqrt(var_crude)
    print(f"{'Crude Monte Carlo':<30} {p_crude:<14.6f} {var_crude:<16.4e} {se_crude:<12.4e}")

    p_is, var_is = importance_sampling_crash(
        S0, K_crash, sigma, T, r, theta_opt, N, np.random.default_rng(42))
    se_is = np.sqrt(var_is)
    print(f"{'Importance Sampling':<30} {p_is:<14.6f} {var_is:<16.4e} {se_is:<12.4e}")

    vr_factor = var_crude/var_is if var_is > 0 else float('inf')
    print()
    print(f"Variance Reduction Factor: {vr_factor:.1f}x")
    print(f"  IS is ~{vr_factor:.0f}x more efficient than crude MC")
    print(f"  Equivalent to crude MC with {int(N*vr_factor):,} paths")

    print()
    print("Raw hit counts (paths reaching crash level):")
    rng_h = np.random.default_rng(42)
    Z = rng_h.standard_normal(N)
    S_T = S0*np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)
    crude_hits = int((S_T < K_crash).sum())
    print(f"  Crude MC  ({N:,} paths):  {crude_hits:,} hits  ({crude_hits/N:.4%})")

    rng_i = np.random.default_rng(42)
    Z_t = rng_i.standard_normal(N)
    Z_s = Z_t - theta_opt
    S_T_is = S0*np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z_s)
    is_hits = int((S_T_is < K_crash).sum())
    oversample = is_hits/max(crude_hits, 1)
    print(f"  IS        ({N:,} paths):  {is_hits:,} hits  ({is_hits/N:.4%})")
    print(f"  IS oversamples crash region by ~{oversample:.0f}x")

    print()
    print("Stability across sample sizes:")
    print(f"{'N':>10}  {'Crude P':>12}  {'Crude SE':>12}  "
          f"{'IS P':>12}  {'IS SE':>12}  {'VR':>8}")
    print("-" * 72)

    for n_test in [1_000, 10_000, 100_000]:
        pc, vc = crude_mc_crash(
            S0, K_crash, sigma, T, r, n_test, np.random.default_rng(42))
        pi, vi = importance_sampling_crash(
            S0, K_crash, sigma, T, r, theta_opt, n_test, np.random.default_rng(42))
        vr = vc/vi if vi > 0 else float('inf')
        print(f"{n_test:>10,}  {pc:>12.6f}  {np.sqrt(vc):>12.4e}  "
              f"{pi:>12.6f}  {np.sqrt(vi):>12.4e}  {vr:>8.1f}x")

    print()
    print("Key insight: IS estimate is stable across all sample sizes.")
    print("Crude MC is unstable at small N because hits are extremely rare.")
    print("=" * 60)
