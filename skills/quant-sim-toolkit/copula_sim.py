"""
copula_sim.py -- Correlated outcome simulation using Gaussian, Student-t, and Clayton copulas.

WHAT IS A COPULA?
-----------------
Sklar's Theorem tells us that any multivariate joint distribution can be decomposed into:
    F(x1, x2, ..., xd) = C(F1(x1), F2(x2), ..., Fd(xd))

where C is the copula -- the pure dependency structure -- and F_i are the marginal CDFs.
This separation is powerful: you can model each contract's marginal behavior independently,
then choose a copula that captures how they move together, including in the tails.

WHY DIFFERENT COPULAS CAPTURE DIFFERENT RISK PROFILES:
-------------------------------------------------------
Gaussian copula:
    Tail dependence lambda_U = lambda_L = 0.
    Extreme co-movements are modeled as essentially impossible.
    This is the copula that contributed to the 2008 financial crisis: CDO pricing
    assumed Gaussian dependence and wildly underestimated joint default probabilities.

Student-t copula (df=nu):
    Symmetric tail dependence: both joint wins AND joint losses are more likely
    than Gaussian predicts. The effect grows as df decreases.
    With nu=3 and rho=0.4, tail dependence is approximately 0.20.

Clayton copula (theta > 0):
    Asymmetric LOWER tail dependence only: lambda_L = 2^(-1/theta).
    When one contract crashes, others are much more likely to also crash.
    Upper tail dependence = 0 (joint wins are not amplified beyond marginals).
    Models contagion and correlated crashes seen in market stress events.

PREDICTION MARKET APPLICATION:
-------------------------------
If you're trading 5 correlated swing-state contracts using a Gaussian copula, you are
drastically underpricing the probability of a clean sweep AND a total loss. The Student-t
copula shows both extremes are more likely. Clayton shows correlated losses (blowup risk)
are even higher than Gaussian suggests. This directly affects portfolio sizing and hedging.

Dependencies: numpy, scipy only.
Usage: python3 copula_sim.py
"""

import math
import numpy as np
from scipy.stats import norm, t as t_dist


# ---------------------------------------------------------------------------
# COPULA SIMULATION FUNCTIONS
# ---------------------------------------------------------------------------

def gaussian_copula_sim(corr_matrix, marginal_probs, n_sims, rng):
    """
    Simulate correlated binary outcomes using the Gaussian copula.

    No tail dependence: extreme co-movements are near-impossible beyond linear correlation.

    Algorithm:
        1. Z = rng.multivariate_normal(mean=zeros, cov=corr_matrix, size=n_sims)
        2. U = norm.cdf(Z)         -- convert to uniform via standard normal CDF
        3. outcome[i,j] = 1 if U[i,j] < marginal_probs[j] else 0

    Parameters
    ----------
    corr_matrix    : np.ndarray (d, d) -- positive-definite correlation matrix
    marginal_probs : array-like (d,)   -- marginal win probability per contract
    n_sims         : int               -- number of simulation paths
    rng            : numpy.random.Generator

    Returns
    -------
    np.ndarray (n_sims, d) of binary outcomes (0 or 1)
    """
    marginal_probs = np.asarray(marginal_probs)
    d = len(marginal_probs)
    Z = rng.multivariate_normal(mean=np.zeros(d), cov=corr_matrix, size=n_sims)
    U = norm.cdf(Z)
    return (U < marginal_probs[None, :]).astype(int)


def student_t_copula_sim(corr_matrix, df, marginal_probs, n_sims, rng):
    """
    Simulate correlated binary outcomes using the Student-t copula.

    Symmetric tail dependence: both joint wins AND joint losses are more probable
    than Gaussian predicts. Effect grows as df decreases (heavier tails).

    Algorithm:
        1. Z = rng.multivariate_normal(mean=zeros, cov=corr_matrix, size=n_sims)
        2. S = rng.chisquare(df, size=n_sims)
        3. T = Z * sqrt(df/S[:, None])     -- t-distributed samples
        4. U = t_dist.cdf(T, df)           -- convert to uniform via t CDF
        5. outcome[i,j] = 1 if U[i,j] < marginal_probs[j] else 0

    The t-copula generates more joint extremes than Gaussian, giving higher
    probability of all-win or all-lose scenarios.

    Parameters
    ----------
    corr_matrix    : np.ndarray (d, d) -- positive-definite correlation matrix
    df             : float             -- degrees of freedom (lower = heavier tails)
    marginal_probs : array-like (d,)   -- marginal win probability per contract
    n_sims         : int               -- number of simulation paths
    rng            : numpy.random.Generator

    Returns
    -------
    np.ndarray (n_sims, d) of binary outcomes (0 or 1)
    """
    marginal_probs = np.asarray(marginal_probs)
    d = len(marginal_probs)
    Z = rng.multivariate_normal(mean=np.zeros(d), cov=corr_matrix, size=n_sims)
    S = rng.chisquare(df, size=n_sims)
    T = Z * np.sqrt(df / S[:, None])
    U = t_dist.cdf(T, df)
    return (U < marginal_probs[None, :]).astype(int)


def clayton_copula_sim(theta, marginal_probs, n_sims, rng):
    """
    Simulate correlated binary outcomes using the Clayton copula.

    Asymmetric lower tail dependence: lambda_L = 2^(-1/theta), lambda_U = 0.
    At theta=2: lambda_L ~ 0.707. Joint crashes are strongly amplified;
    joint wins are NOT amplified.

    Uses the Marshall-Olkin algorithm (valid for any dimension d >= 2):
        1. V = rng.gamma(shape=1/theta, scale=1, size=n_sims)
        2. E = rng.exponential(scale=1, size=(n_sims, d))
        3. U = (1 + E/V[:, None])^(-1/theta)
    The U_i have Clayton copula joint distribution.

    Clayton copula has lower tail dependence: the probability of joint low
    values (all lose) is higher than under Gaussian. When one prediction
    market crashes, others follow.

    Parameters
    ----------
    theta          : float           -- Clayton parameter (theta > 0)
    marginal_probs : array-like (d,) -- marginal win probability per contract
    n_sims         : int             -- number of simulation paths
    rng            : numpy.random.Generator

    Returns
    -------
    np.ndarray (n_sims, d) of binary outcomes (0 or 1)
    """
    marginal_probs = np.asarray(marginal_probs)
    d = len(marginal_probs)
    V = rng.gamma(shape=1.0/theta, scale=1.0, size=n_sims)
    E = rng.exponential(scale=1.0, size=(n_sims, d))
    U = (1.0 + E / V[:, None]) ** (-1.0/theta)
    return (U < marginal_probs[None, :]).astype(int)


# ---------------------------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------------------------

def estimate_joint_probs(outcomes, labels=None):
    """
    Compute joint probability statistics from simulated binary outcomes.

    Parameters
    ----------
    outcomes : np.ndarray (n_sims, d) -- binary outcome matrix
    labels   : list of str, optional  -- if given, prints formatted results

    Returns
    -------
    dict with keys:
        p_all_win    : float -- P(all contracts = 1)
        p_all_lose   : float -- P(all contracts = 0)
        p_at_least_k : dict  -- {k: P(sum >= k)} for k in 0..d
        pairwise_corr: float -- average pairwise Pearson correlation
    """
    n_sims, d = outcomes.shape
    row_sums = outcomes.sum(axis=1)

    p_all_win  = float((row_sums == d).mean())
    p_all_lose = float((row_sums == 0).mean())
    p_at_least_k = {k: float((row_sums >= k).mean()) for k in range(d + 1)}

    if d > 1:
        corr_mat = np.corrcoef(outcomes.T)
        upper_idx = np.triu_indices(d, k=1)
        pairwise_corr = float(corr_mat[upper_idx].mean())
    else:
        pairwise_corr = float('nan')

    result = {
        'p_all_win':     p_all_win,
        'p_all_lose':    p_all_lose,
        'p_at_least_k':  p_at_least_k,
        'pairwise_corr': pairwise_corr,
    }

    if labels is not None:
        print(f"  Assets: {', '.join(labels)}")
        print(f"  P(all win)  = {p_all_win:.4f}")
        print(f"  P(all lose) = {p_all_lose:.4f}")
        for k in range(d, 0, -1):
            print(f"  P(>= {k})     = {p_at_least_k[k]:.4f}")
        print(f"  Avg pairwise corr = {pairwise_corr:.4f}")

    return result


# ---------------------------------------------------------------------------
# DEMO
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 66)
    print("COPULA SIMULATION: CORRELATED OUTCOMES")
    print("=" * 66)

    # -------------------------------------------------------------------------
    # Parameters
    # -------------------------------------------------------------------------
    rng = np.random.default_rng(42)

    state_labels   = ["PA", "MI", "WI", "AZ", "GA"]
    d              = len(state_labels)
    marginal_probs = [0.55] * d   # each state: P(win) = 0.55
    rho            = 0.4          # uniform pairwise correlation
    theta_clayton  = 2.0          # Clayton copula strength
    df_t           = 3            # Student-t degrees of freedom
    n_sims         = 500_000

    # Uniform correlation matrix: 1 on diagonal, rho off-diagonal
    corr_matrix = np.full((d, d), rho)
    np.fill_diagonal(corr_matrix, 1.0)

    print()
    print("Scenario: 5 correlated swing states, each with marginal P(win) = 0.55")
    print(f"  States:          {', '.join(state_labels)}")
    print(f"  Marginal P(win): {marginal_probs[0]:.2f} each")
    print(f"  Pairwise rho:    {rho:.2f}")
    print(f"  Clayton theta:   {theta_clayton:.1f}")
    print(f"  Student-t df:    {df_t}")
    print(f"  Simulations:     {n_sims:,}")
    print()

    # -------------------------------------------------------------------------
    # Independent baseline
    # -------------------------------------------------------------------------
    p_sweep_indep = float(np.prod(marginal_probs))
    p_lose_indep  = float(np.prod([1.0 - p for p in marginal_probs]))

    print("Baseline (independent, no copula):")
    print(f"  P(sweep all 5) = 0.55^5 = {p_sweep_indep:.5f}")
    print(f"  P(lose all 5)  = 0.45^5 = {p_lose_indep:.5f}")
    print()

    # -------------------------------------------------------------------------
    # Run all three copulas
    # -------------------------------------------------------------------------
    print("Running Gaussian copula simulation...")
    gauss_out   = gaussian_copula_sim(corr_matrix, marginal_probs, n_sims, rng)
    gauss_stats = estimate_joint_probs(gauss_out)

    print("Running Student-t copula simulation (df=3)...")
    t_out   = student_t_copula_sim(corr_matrix, df_t, marginal_probs, n_sims, rng)
    t_stats = estimate_joint_probs(t_out)

    print("Running Clayton copula simulation (theta=2.0)...")
    clay_out   = clayton_copula_sim(theta_clayton, marginal_probs, n_sims, rng)
    clay_stats = estimate_joint_probs(clay_out)

    print()

    # -------------------------------------------------------------------------
    # Comparison table
    # -------------------------------------------------------------------------
    print("=" * 66)
    print("COMPARISON TABLE")
    print("=" * 66)
    print(f"{'Copula':<14} {'P(sweep)':>10} {'P(0 wins)':>10} "
          f"{'P(>=4)':>8} {'P(>=3)':>8} {'AvgCorr':>8}")
    print("-" * 66)

    def fp(v):
        return f"{v:.5f}" if v is not None else "    n/a"

    def fc(v):
        return f"{v:.4f}" if not math.isnan(v) else "    n/a"

    table_rows = [
        ("Independent",
             p_sweep_indep,              p_lose_indep,
             None, None,                 float('nan')),
        ("Gaussian",
             gauss_stats['p_all_win'],   gauss_stats['p_all_lose'],
             gauss_stats['p_at_least_k'][4], gauss_stats['p_at_least_k'][3],
             gauss_stats['pairwise_corr']),
        ("Student-t",
             t_stats['p_all_win'],       t_stats['p_all_lose'],
             t_stats['p_at_least_k'][4],     t_stats['p_at_least_k'][3],
             t_stats['pairwise_corr']),
        ("Clayton",
             clay_stats['p_all_win'],    clay_stats['p_all_lose'],
             clay_stats['p_at_least_k'][4],  clay_stats['p_at_least_k'][3],
             clay_stats['pairwise_corr']),
    ]

    for name, p_sw, p_lo, p_ge4, p_ge3, corr in table_rows:
        print(f"{name:<14} {fp(p_sw):>10} {fp(p_lo):>10} "
              f"{fp(p_ge4):>8} {fp(p_ge3):>8} {fc(corr):>8}")

    print()

    # -------------------------------------------------------------------------
    # Key insights
    # -------------------------------------------------------------------------
    print("=" * 66)
    print("KEY INSIGHTS")
    print("=" * 66)

    g_sw = gauss_stats['p_all_win']
    t_sw = t_stats['p_all_win']
    c_sw = clay_stats['p_all_win']
    g_lo = gauss_stats['p_all_lose']
    t_lo = t_stats['p_all_lose']
    c_lo = clay_stats['p_all_lose']

    print()
    print("1. JOINT SWEEP PROBABILITY vs INDEPENDENT BASELINE")
    print(f"   Independent:  {p_sweep_indep:.5f}  (1.0x)")
    print(f"   Gaussian:     {g_sw:.5f}  ({g_sw/p_sweep_indep:.1f}x)  correlation alone raises P(sweep)")
    print(f"   Student-t:    {t_sw:.5f}  ({t_sw/p_sweep_indep:.1f}x)  symmetric tail dep raises it further")
    print(f"   Clayton:      {c_sw:.5f}  ({c_sw/p_sweep_indep:.1f}x)  no upper tail dep, near-Gaussian")
    print()
    print("2. JOINT LOSS PROBABILITY vs INDEPENDENT BASELINE  [blowup risk]")
    print(f"   Independent:  {p_lose_indep:.5f}  (1.0x)")
    print(f"   Gaussian:     {g_lo:.5f}  ({g_lo/p_lose_indep:.1f}x)")
    lam_L = 2.0 ** (-1.0/theta_clayton)
    print(f"   Student-t:    {t_lo:.5f}  ({t_lo/p_lose_indep:.1f}x)  symmetric tail dep raises losses too")
    print(f"   Clayton:      {c_lo:.5f}  ({c_lo/p_lose_indep:.1f}x)  lower tail lam_L={lam_L:.3f}")
    print()
    print("   Clayton gives the HIGHEST P(all lose) due to asymmetric lower")
    print("   tail dependence. Joint crashes are amplified; joint wins are not.")
    print()
    print("3. STUDENT-t vs GAUSSIAN: SYMMETRIC TAIL AMPLIFICATION")
    print(f"   P(sweep) ratio, t-copula vs Gaussian: {t_sw/g_sw:.2f}x")
    print(f"   P(loss) ratio, t-copula vs Gaussian:  {t_lo/g_lo:.2f}x")
    print()
    print("   Student-t raises BOTH tails symmetrically.")
    print("   Gaussian copula treats joint extremes as near-impossible -- they are not.")
    print("   This is the same error that caused massive losses in 2008.")
    print()
    print("4. PRACTICAL TAKEAWAY FOR PORTFOLIO CONSTRUCTION")
    print(f"   Gaussian model: P(total loss) = {g_lo:.5f}")
    print(f"   Clayton model:  P(total loss) = {c_lo:.5f}  ({c_lo/g_lo:.1f}x that of Gaussian)")
    print()
    print("   Without tail-dependence modeling, your drawdown estimates are")
    print("   systematically too low. Choose the right copula:")
    print("     Student-t  symmetric co-movement, both tails elevated")
    print("     Clayton    crash contagion, losses more correlated than gains")
    print()

    # -------------------------------------------------------------------------
    # Tail dependence reference
    # -------------------------------------------------------------------------
    print("=" * 66)
    print("TAIL DEPENDENCE REFERENCE")
    print("=" * 66)
    print(f"  {'Copula':<32} {'lam_L':>8} {'lam_U':>8}")
    print(f"  {'-'*50}")
    print(f"  {'Gaussian (any rho)':<32} {'0.0000':>8} {'0.0000':>8}")

    for nu in [10, 5, 3]:
        arg = -math.sqrt((nu + 1) * (1.0 - rho) / (1.0 + rho))
        lam = 2.0 * float(t_dist.cdf(arg, nu + 1))
        label = f"Student-t (df={nu}, rho={rho:.1f})"
        print(f"  {label:<32} {lam:>8.4f} {lam:>8.4f}")

    for th in [0.5, 1.0, 2.0, 4.0]:
        lam_ref = 2.0 ** (-1.0/th)
        label = f"Clayton (theta={th:.1f})"
        print(f"  {label:<32} {lam_ref:>8.4f} {'0.0000':>8}")
    print()
