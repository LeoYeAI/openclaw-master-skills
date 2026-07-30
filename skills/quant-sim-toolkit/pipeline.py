"""
pipeline.py -- Full Quantitative Simulation Pipeline
======================================================

This module is the complete end-to-end quantitative simulation pipeline,
connecting all seven tools in the quant-sim-toolkit into a single workflow.

It demonstrates the complete sequence a quant desk would execute:

  1. PROBABILITY ESTIMATION
     Monte Carlo binary pricing with confidence intervals and an analytical
     Black-Scholes benchmark. Converts market prices into calibrated
     event probabilities.

  2. VARIANCE REDUCTION
     Stack antithetic variates, control variates, and stratified sampling
     to price European call options with 100-500x less variance than crude
     Monte Carlo -- this is table stakes in production.

  3. TAIL RISK ASSESSMENT
     Importance sampling with exponential tilting to estimate crash
     probabilities that crude MC cannot measure reliably. For rare events
     (P ~ 0.001), IS provides 100-10,000x variance reduction.

  4. DEPENDENCY MODELING
     Gaussian, Student-t, and Clayton copulas to model joint outcomes for
     a portfolio of correlated binary contracts. The Gaussian copula
     zero-models tail dependence; the t-copula and Clayton show how extreme
     co-movements are systematically more likely than linear correlation
     predicts.

  5. MARKET SIMULATION
     Agent-based model of prediction market microstructure: informed
     traders with private information, noise traders, and a Kyle-lambda
     market maker whose price converges to the true probability.

  6. REAL-TIME FILTERING
     Bootstrap particle filter for Bayesian probability updating as
     streaming observations arrive. Tracks the hidden true probability
     through noisy binary data in real time.

  7. SUMMARY TABLE
     Aggregate key metrics from every stage into a single formatted table.

Based on: "How to Simulate Like a Quant Desk" by @gemchange_ltd
Dependencies: numpy, scipy, and all six sibling modules in this toolkit.
"""

import sys
import numpy as np

# ---------------------------------------------------------------------------
# Graceful imports from sibling modules
# ---------------------------------------------------------------------------

try:
    from binary_pricer import mc_binary_price, analytical_binary_price
    _HAS_BINARY_PRICER = True
except ImportError:
    _HAS_BINARY_PRICER = False
    print("[WARNING] binary_pricer.py not found -- Stage 1 will be skipped.")

try:
    from variance_reduction import crude_mc, combined_mc
    _HAS_VARIANCE_REDUCTION = True
except ImportError:
    _HAS_VARIANCE_REDUCTION = False
    print("[WARNING] variance_reduction.py not found -- Stage 2 will be skipped.")

try:
    from tail_risk import crude_mc_crash, importance_sampling_crash, optimal_theta
    _HAS_TAIL_RISK = True
except ImportError:
    _HAS_TAIL_RISK = False
    print("[WARNING] tail_risk.py not found -- Stage 3 will be skipped.")

try:
    from copula_sim import gaussian_copula_sim, student_t_copula_sim, clayton_copula_sim
    _HAS_COPULA_SIM = True
except ImportError:
    _HAS_COPULA_SIM = False
    print("[WARNING] copula_sim.py not found -- Stage 4 will be skipped.")

try:
    from market_abm import simulate_market
    _HAS_MARKET_ABM = True
except ImportError:
    _HAS_MARKET_ABM = False
    print("[WARNING] market_abm.py not found -- Stage 5 will be skipped.")

try:
    from particle_filter import run_particle_filter, logit, expit, generate_observations
    _HAS_PARTICLE_FILTER = True
except ImportError:
    _HAS_PARTICLE_FILTER = False
    print("[WARNING] particle_filter.py not found -- Stage 6 will be skipped.")


# ---------------------------------------------------------------------------
# Shared contract parameters (used across multiple stages)
# ---------------------------------------------------------------------------

S0     = 100.0   # current asset price
K      = 105.0   # strike: "Asset above 105 in 6 months"
K_CALL = 100.0   # at-the-money call for variance reduction demo
sigma  = 0.25    # annual volatility
T      = 0.5     # time to expiry in years (6 months)
r      = 0.05    # risk-free rate

# Crash scenario: 30% drawdown
K_CRASH = S0 * 0.70

# Correlated portfolio: 3 binary contracts
MARGINAL_PROBS = [0.55, 0.52, 0.48]
RHO            = 0.5
COPULA_CORR    = np.array([
    [1.0, RHO, RHO],
    [RHO, 1.0, RHO],
    [RHO, RHO, 1.0],
])

# ABM parameters
TRUE_PROB_ABM = 0.65
N_INFORMED    = 5
N_NOISE       = 20

# Particle filter: true probability drifts 0.50 -> 0.65 over 30 steps
N_PF_STEPS = 30


# ---------------------------------------------------------------------------
# Stage functions
# ---------------------------------------------------------------------------

def _section(title: str, stage_num: int) -> None:
    """Print a formatted section header."""
    bar = "=" * 68
    print()
    print(bar)
    print(f"  STAGE {stage_num}: {title}")
    print(bar)


def run_stage_1(rng: np.random.Generator) -> dict:
    """
    Stage 1 -- PROBABILITY ESTIMATION.

    Estimate P(Asset > K in T years) using Monte Carlo and the
    Black-Scholes analytical formula N(d2). Compare the two and
    report the 95% confidence interval.

    Returns
    -------
    dict with keys: mc_prob, ci_lower, ci_upper, analytical_prob, brier
    """
    _section("PROBABILITY ESTIMATION", 1)

    if not _HAS_BINARY_PRICER:
        print("  [SKIPPED] binary_pricer module not available.")
        return {"skipped": True}

    n_paths = 50_000

    print(f"  Contract: Asset above {K} in {T*12:.0f} months")
    print(f"  S0={S0}, K={K}, sigma={sigma:.0%}, T={T}yr, r={r:.0%}")
    print(f"  MC paths: {n_paths:,}")
    print()

    prob, ci_lo, ci_hi = mc_binary_price(S0, K, sigma, T, r, n_paths, rng)
    analytical = analytical_binary_price(S0, K, sigma, T, r)
    brier = float((prob - analytical) ** 2)

    print(f"  MC estimate:       {prob:.6f}")
    print(f"  95% CI:            ({ci_lo:.6f}, {ci_hi:.6f})")
    print(f"  CI width:          {ci_hi - ci_lo:.6f}")
    print(f"  Analytical N(d2):  {analytical:.6f}")
    print(f"  Error vs N(d2):    {abs(prob - analytical):.6f}")
    print(f"  Brier score:       {brier:.8f}  (MC vs analytical, lower is better)")

    return {
        "mc_prob":    prob,
        "ci_lower":   ci_lo,
        "ci_upper":   ci_hi,
        "analytical": analytical,
        "brier":      brier,
    }


def run_stage_2(rng: np.random.Generator) -> dict:
    """
    Stage 2 -- VARIANCE REDUCTION.

    Price a European call option using both crude MC and the combined
    method (stratified + antithetic + control variate). Show how much
    variance is eliminated by stacking all three techniques.

    Returns
    -------
    dict with keys: crude_price, crude_var, combined_price, combined_var,
                    vr_factor
    """
    _section("VARIANCE REDUCTION", 2)

    if not _HAS_VARIANCE_REDUCTION:
        print("  [SKIPPED] variance_reduction module not available.")
        return {"skipped": True}

    n_paths = 50_000

    print(f"  European call: S0={S0}, K={K_CALL}, sigma={sigma:.0%}, T={T}yr, r={r:.0%}")
    print(f"  MC paths: {n_paths:,}")
    print()

    crude_price, crude_var   = crude_mc(S0, K_CALL, sigma, T, r, n_paths, rng)
    combined_price, comb_var = combined_mc(S0, K_CALL, sigma, T, r, n_paths, rng)

    vr_factor = crude_var/comb_var if comb_var > 0 else float("inf")

    print(f"  {'Method':<16}  {'Price':>10}  {'Variance':>14}  {'VR Factor':>10}")
    print(f"  {'-'*16}  {'-'*10}  {'-'*14}  {'-'*10}")
    print(f"  {'Crude MC':<16}  {crude_price:>10.6f}  {crude_var:>14.4e}  {'1.00x':>10}")
    print(f"  {'Combined':<16}  {combined_price:>10.6f}  {comb_var:>14.4e}  {vr_factor:>9.1f}x")

    print()
    print(f"  Variance reduction factor: {vr_factor:.1f}x")
    print(f"  Stacking stratified + antithetic + control variate achieves")
    print(f"  {vr_factor:.0f}x less variance -- equivalent to running crude MC with")
    print(f"  {int(n_paths * vr_factor):,} paths.")

    return {
        "crude_price":    crude_price,
        "crude_var":      crude_var,
        "combined_price": combined_price,
        "combined_var":   comb_var,
        "vr_factor":      vr_factor,
    }


def run_stage_3(rng: np.random.Generator) -> dict:
    """
    Stage 3 -- TAIL RISK ASSESSMENT.

    Estimate P(30% crash within T years) using crude MC and importance
    sampling with exponential tilting. Show the variance reduction factor
    that makes rare-event pricing tractable.

    Returns
    -------
    dict with keys: crude_prob, crude_var, is_prob, is_var, vr_factor,
                    theta_opt
    """
    _section("TAIL RISK ASSESSMENT", 3)

    if not _HAS_TAIL_RISK:
        print("  [SKIPPED] tail_risk module not available.")
        return {"skipped": True}

    n_paths   = 100_000
    crash_pct = (1 - K_CRASH/S0) * 100

    print(f"  Scenario: P(asset drops {crash_pct:.0f}% in {T*12:.0f} months)")
    print(f"  S0={S0}, K_crash={K_CRASH:.1f}, sigma={sigma:.0%}, T={T}yr, r={r:.0%}")
    print(f"  MC paths: {n_paths:,}")
    print()

    theta = optimal_theta(S0, K_CRASH, sigma, T, r)
    print(f"  Optimal tilting parameter theta: {theta:.4f}")
    print()

    p_crude, var_crude = crude_mc_crash(S0, K_CRASH, sigma, T, r, n_paths, rng)
    p_is, var_is       = importance_sampling_crash(S0, K_CRASH, sigma, T, r, theta, n_paths, rng)

    vr_factor = var_crude/var_is if var_is > 0 else float("inf")

    se_crude = float(np.sqrt(var_crude))
    se_is    = float(np.sqrt(var_is))

    print(f"  {'Method':<20}  {'P(crash)':>10}  {'Std Error':>12}  {'VR Factor':>10}")
    print(f"  {'-'*20}  {'-'*10}  {'-'*12}  {'-'*10}")
    print(f"  {'Crude MC':<20}  {p_crude:>10.6f}  {se_crude:>12.4e}  {'1.00x':>10}")
    print(f"  {'Importance Sampling':<20}  {p_is:>10.6f}  {se_is:>12.4e}  {vr_factor:>9.1f}x")

    print()
    print(f"  IS achieves {vr_factor:.0f}x variance reduction.")
    print(f"  At this crash level, crude MC sees ~{int(p_crude * n_paths):,} "
          f"hits in {n_paths:,} paths.")
    print(f"  IS oversamples the crash region to deliver a stable estimate.")

    return {
        "crude_prob": p_crude,
        "crude_var":  var_crude,
        "is_prob":    p_is,
        "is_var":     var_is,
        "vr_factor":  vr_factor,
        "theta_opt":  theta,
    }


def run_stage_4(rng: np.random.Generator) -> dict:
    """
    Stage 4 -- DEPENDENCY MODELING.

    Simulate a portfolio of 3 correlated binary contracts under Gaussian,
    Student-t (df=4), and Clayton (theta=2) copulas. Compare P(all win)
    to show how tail dependence changes joint probabilities.

    Returns
    -------
    dict with keys: p_all_win_gaussian, p_all_win_t, p_all_win_clayton,
                    p_all_lose_gaussian, p_all_lose_t, p_all_lose_clayton
    """
    _section("DEPENDENCY MODELING", 4)

    if not _HAS_COPULA_SIM:
        print("  [SKIPPED] copula_sim module not available.")
        return {"skipped": True}

    n_sims = 100_000
    df_t   = 4
    theta  = 2.0

    print(f"  Portfolio: {len(MARGINAL_PROBS)} correlated binary contracts")
    print(f"  Marginal probabilities: {MARGINAL_PROBS}")
    print(f"  Pairwise correlation: rho = {RHO}")
    print(f"  Student-t df = {df_t},  Clayton theta = {theta}")
    print(f"  Simulations: {n_sims:,}")
    print()

    # Independent baseline
    p_win_indep  = float(np.prod(MARGINAL_PROBS))
    p_lose_indep = float(np.prod([1 - p for p in MARGINAL_PROBS]))

    # Gaussian copula
    gauss_out = gaussian_copula_sim(COPULA_CORR, MARGINAL_PROBS, n_sims, rng)
    p_win_g   = float(gauss_out.all(axis=1).mean())
    p_lose_g  = float((1 - gauss_out).all(axis=1).mean())

    # Student-t copula
    t_out    = student_t_copula_sim(COPULA_CORR, df_t, MARGINAL_PROBS, n_sims, rng)
    p_win_t  = float(t_out.all(axis=1).mean())
    p_lose_t = float((1 - t_out).all(axis=1).mean())

    # Clayton copula
    clay_out  = clayton_copula_sim(theta, MARGINAL_PROBS, n_sims, rng)
    p_win_c   = float(clay_out.all(axis=1).mean())
    p_lose_c  = float((1 - clay_out).all(axis=1).mean())

    ratio_g = p_win_g/p_win_indep
    ratio_t = p_win_t/p_win_indep
    ratio_c = p_win_c/p_win_indep

    print(f"  {'Copula':<14}  {'P(all win)':>12}  {'P(all lose)':>12}  {'Win mult vs indep':>18}")
    print(f"  {'-'*14}  {'-'*12}  {'-'*12}  {'-'*18}")
    print(f"  {'Independent':<14}  {p_win_indep:>12.5f}  {p_lose_indep:>12.5f}  {'1.00x':>18}")
    print(f"  {'Gaussian':<14}  {p_win_g:>12.5f}  {p_lose_g:>12.5f}  {ratio_g:>17.2f}x")
    print(f"  {'Student-t':<14}  {p_win_t:>12.5f}  {p_lose_t:>12.5f}  {ratio_t:>17.2f}x")
    print(f"  {'Clayton':<14}  {p_win_c:>12.5f}  {p_lose_c:>12.5f}  {ratio_c:>17.2f}x")

    print()
    print(f"  Gaussian zero-models tail dependence -- joint extremes near-impossible.")
    print(f"  Student-t raises BOTH win and loss tails symmetrically.")
    print(f"  Clayton amplifies losses (contagion) but not wins.")

    return {
        "p_all_win_gaussian":  p_win_g,
        "p_all_win_t":         p_win_t,
        "p_all_win_clayton":   p_win_c,
        "p_all_lose_gaussian": p_lose_g,
        "p_all_lose_t":        p_lose_t,
        "p_all_lose_clayton":  p_lose_c,
    }


def run_stage_5(rng: np.random.Generator) -> dict:
    """
    Stage 5 -- MARKET SIMULATION.

    Run a short ABM for a single binary contract whose true probability
    is TRUE_PROB_ABM. Show price convergence from 0.50 and PnL attribution
    across informed traders, noise traders, and the market maker.

    Returns
    -------
    dict with keys: final_price, convergence_error, informed_pnl,
                    noise_pnl, mm_pnl, kyle_lambda_estimated
    """
    _section("MARKET SIMULATION", 5)

    if not _HAS_MARKET_ABM:
        print("  [SKIPPED] market_abm module not available.")
        return {"skipped": True}

    n_steps     = 500
    kyle_lambda = 0.05

    print(f"  True probability: {TRUE_PROB_ABM}")
    print(f"  Starting price:   0.50")
    print(f"  Informed traders: {N_INFORMED}")
    print(f"  Noise traders:    {N_NOISE}")
    print(f"  Steps:            {n_steps}")
    print(f"  Kyle lambda:      {kyle_lambda}")
    print()

    result = simulate_market(
        true_prob=TRUE_PROB_ABM,
        n_informed=N_INFORMED,
        n_noise=N_NOISE,
        n_steps=n_steps,
        kyle_lambda=kyle_lambda,
        rng=rng,
    )

    prices = result["prices"]
    checkpoints = [0, 100, 250, 500]

    print(f"  {'Step':>5}  {'Price':>8}  {'vs True':>8}")
    print(f"  {'-'*5}  {'-'*8}  {'-'*8}")
    for step in checkpoints:
        idx = min(step, len(prices) - 1)
        print(f"  {step:>5}  {prices[idx]:>8.4f}  {prices[idx] - TRUE_PROB_ABM:>+8.4f}")

    i_pnl  = result["informed_pnl"]
    n_pnl  = result["noise_pnl"]
    mm_pnl = result["mm_pnl"]
    total  = i_pnl + n_pnl + mm_pnl
    lam_e  = result["kyle_lambda_estimated"]

    print()
    print(f"  PnL attribution:")
    print(f"    Informed traders: {i_pnl:>+.4f}")
    print(f"    Noise traders:    {n_pnl:>+.4f}")
    print(f"    Market maker:     {mm_pnl:>+.4f}")
    print(f"    Total (~0.00):    {total:>+.4f}")
    print()
    print(f"  Kyle lambda -- configured: {kyle_lambda:.4f}  estimated: {lam_e:.4f}")

    return {
        "final_price":           float(prices[-1]),
        "convergence_error":     float(abs(prices[-1] - TRUE_PROB_ABM)),
        "informed_pnl":          i_pnl,
        "noise_pnl":             n_pnl,
        "mm_pnl":                mm_pnl,
        "kyle_lambda_estimated": lam_e,
    }


def run_stage_6(rng: np.random.Generator) -> dict:
    """
    Stage 6 -- REAL-TIME FILTERING.

    Simulate N_PF_STEPS streaming binary observations from a true
    probability that drifts from 0.50 to 0.65. Run the particle filter
    and show how the filtered estimate evolves as data accumulates.

    Returns
    -------
    dict with keys: final_filtered_prob, final_true_prob, mae,
                    avg_ess, n_particles
    """
    _section("REAL-TIME FILTERING", 6)

    if not _HAS_PARTICLE_FILTER:
        print("  [SKIPPED] particle_filter module not available.")
        return {"skipped": True}

    n_particles   = 500
    process_noise = 0.1
    prior_prob    = 0.50

    # True probability drifts from 0.50 to 0.65 in logit space
    t_grid      = np.linspace(0, 1, N_PF_STEPS)
    true_logits = logit(0.65) * t_grid  # logit(0.50)=0.0, logit(0.65)~0.619
    true_probs  = expit(true_logits)

    observations = generate_observations(true_probs, rng)

    print(f"  True probability drifts: {true_probs[0]:.3f} -> {true_probs[-1]:.3f}")
    print(f"  Observations (binary):   {N_PF_STEPS} steps")
    print(f"  Wins observed:           {observations.sum()} of {N_PF_STEPS}")
    print(f"  Particles:               {n_particles}")
    print(f"  Process noise:           {process_noise}")
    print()

    results = run_particle_filter(
        observations=observations,
        n_particles=n_particles,
        process_noise=process_noise,
        initial_logit_mean=logit(prior_prob),
        initial_logit_std=0.5,
        rng=rng,
    )

    filtered = results["filtered_probs"]
    ci_lo    = results["ci_lower"]
    ci_hi    = results["ci_upper"]
    ess      = results["ess"]

    print(f"  {'Step':>5}  {'Obs':>4}  {'True P':>8}  {'Filtered':>10}  "
          f"{'95% CI':>22}  {'ESS':>7}")
    print(f"  {'-'*5}  {'-'*4}  {'-'*8}  {'-'*10}  {'-'*22}  {'-'*7}")

    step_print = list(range(0, N_PF_STEPS, max(1, N_PF_STEPS//6)))
    if (N_PF_STEPS - 1) not in step_print:
        step_print.append(N_PF_STEPS - 1)

    for t in step_print:
        ci_str = f"({ci_lo[t]:.3f}, {ci_hi[t]:.3f})"
        print(f"  {t+1:>5}  {observations[t]:>4}  {true_probs[t]:>8.3f}  "
              f"{filtered[t]:>10.3f}  {ci_str:>22}  {ess[t]:>7.1f}")

    mae        = float(np.mean(np.abs(filtered - true_probs)))
    avg_ess    = float(ess.mean())
    final_filt = float(filtered[-1])
    final_true = float(true_probs[-1])

    print()
    print(f"  Mean absolute error (filter vs true): {mae:.4f}")
    print(f"  Final filtered estimate:              {final_filt:.4f}")
    print(f"  Final true probability:               {final_true:.4f}")
    print(f"  Average ESS:                          {avg_ess:.1f} of {n_particles}")

    return {
        "final_filtered_prob": final_filt,
        "final_true_prob":     final_true,
        "mae":                 mae,
        "avg_ess":             avg_ess,
        "n_particles":         n_particles,
    }


def run_stage_7(summaries: dict) -> None:
    """
    Stage 7 -- SUMMARY TABLE.

    Print a formatted summary table aggregating the key metric from
    each stage. Handles missing stages gracefully (marked as SKIPPED).
    """
    _section("SUMMARY", 7)

    rows = []

    # Stage 1
    s1 = summaries.get("stage_1", {})
    if s1.get("skipped"):
        rows.append(("Stage 1", "Probability Estimation", "SKIPPED", ""))
    else:
        rows.append((
            "Stage 1",
            "Probability Estimation",
            f"MC P(S>K) = {s1.get('mc_prob', float('nan')):.4f}",
            f"N(d2) = {s1.get('analytical', float('nan')):.4f}",
        ))

    # Stage 2
    s2 = summaries.get("stage_2", {})
    if s2.get("skipped"):
        rows.append(("Stage 2", "Variance Reduction", "SKIPPED", ""))
    else:
        rows.append((
            "Stage 2",
            "Variance Reduction",
            f"Combined price = {s2.get('combined_price', float('nan')):.4f}",
            f"VR factor = {s2.get('vr_factor', float('nan')):.1f}x",
        ))

    # Stage 3
    s3 = summaries.get("stage_3", {})
    if s3.get("skipped"):
        rows.append(("Stage 3", "Tail Risk (IS)", "SKIPPED", ""))
    else:
        rows.append((
            "Stage 3",
            "Tail Risk (IS)",
            f"IS P(crash) = {s3.get('is_prob', float('nan')):.6f}",
            f"VR factor = {s3.get('vr_factor', float('nan')):.1f}x",
        ))

    # Stage 4
    s4 = summaries.get("stage_4", {})
    if s4.get("skipped"):
        rows.append(("Stage 4", "Dependency Modeling", "SKIPPED", ""))
    else:
        rows.append((
            "Stage 4",
            "Dependency Modeling",
            f"P(all win): Gauss={s4.get('p_all_win_gaussian', float('nan')):.4f}",
            f"t={s4.get('p_all_win_t', float('nan')):.4f}  "
            f"Clayton={s4.get('p_all_win_clayton', float('nan')):.4f}",
        ))

    # Stage 5
    s5 = summaries.get("stage_5", {})
    if s5.get("skipped"):
        rows.append(("Stage 5", "Market Simulation", "SKIPPED", ""))
    else:
        fp   = s5.get('final_price', float('nan'))
        ipnl = s5.get('informed_pnl', float('nan'))
        rows.append((
            "Stage 5",
            "Market Simulation",
            f"Final price={fp:.4f} (true={TRUE_PROB_ABM:.2f})",
            f"Informed PnL={ipnl:+.4f}",
        ))

    # Stage 6
    s6 = summaries.get("stage_6", {})
    if s6.get("skipped"):
        rows.append(("Stage 6", "Real-Time Filtering", "SKIPPED", ""))
    else:
        ff  = s6.get('final_filtered_prob', float('nan'))
        ft  = s6.get('final_true_prob', float('nan'))
        mae = s6.get('mae', float('nan'))
        rows.append((
            "Stage 6",
            "Real-Time Filtering",
            f"Filtered={ff:.4f}  (true={ft:.4f})",
            f"MAE={mae:.4f}",
        ))

    # Print table
    print()
    print(f"  {'Stage':<9}  {'Tool':<24}  {'Primary Metric':<38}  {'Secondary'}")
    print(f"  {'-'*9}  {'-'*24}  {'-'*38}  {'-'*28}")
    for stage, tool, primary, secondary in rows:
        print(f"  {stage:<9}  {tool:<24}  {primary:<38}  {secondary}")

    print()
    print("  Pipeline complete. All 6 quantitative simulation tools executed.")
    print("  Each stage degrades gracefully if a sibling module is missing.")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Run the full quantitative simulation pipeline.

    Uses a single seeded rng throughout for full reproducibility.
    Each stage prints its own results and returns a summary dict.
    Stage 7 aggregates all summaries into a final table.
    """
    print()
    print("=" * 68)
    print("  QUANT SIMULATION PIPELINE")
    print("  Full end-to-end quantitative simulation workflow")
    print("=" * 68)
    print()
    print("  Modules required: binary_pricer, variance_reduction, tail_risk,")
    print("                    copula_sim, market_abm, particle_filter")
    print()
    print(f"  Shared contract parameters:")
    print(f"    Asset: S0={S0}, sigma={sigma:.0%}, r={r:.0%}")
    print(f"    Binary contract: K={K}, T={T}yr  (Asset above {K} in {T*12:.0f} months)")
    print(f"    Call option:     K={K_CALL} (at-the-money, for variance reduction demo)")
    print(f"    Crash threshold: K_crash={K_CRASH:.1f}  ({(1-K_CRASH/S0)*100:.0f}% drawdown)")

    # Single rng for the entire pipeline
    rng = np.random.default_rng(seed=42)

    summaries = {}

    summaries["stage_1"] = run_stage_1(rng)
    summaries["stage_2"] = run_stage_2(rng)
    summaries["stage_3"] = run_stage_3(rng)
    summaries["stage_4"] = run_stage_4(rng)
    summaries["stage_5"] = run_stage_5(rng)
    summaries["stage_6"] = run_stage_6(rng)

    run_stage_7(summaries)

    print()
    print("=" * 68)


if __name__ == "__main__":
    main()
