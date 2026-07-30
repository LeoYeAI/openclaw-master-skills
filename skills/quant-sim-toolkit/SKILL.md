---
name: "Quant Simulation Toolkit"
slug: "quant-sim-toolkit"
version: "1.0.0"
description: "7 runnable Monte Carlo simulation tools extracted from a viral quant article. Importance sampling, particle filters, copulas, agent-based markets, variance reduction."
tags: ["quant", "monte-carlo", "simulation", "finance", "prediction-markets", "copula", "particle-filter", "importance-sampling"]
author: "marcindudek"
---

# Quant Simulation Toolkit

Seven self-contained Python tools for quantitative simulation. Every technique here is drawn from the viral X thread by @gemchange_ltd, **"How to Simulate Like a Quant Desk"** (2.7M views). Each file runs standalone with `python3 <file>.py` and prints a formatted demo.

Dependencies: `numpy`, `scipy`. No other packages needed.

```
binary_pricer.py      MC binary option pricing vs Black-Scholes
tail_risk.py          Importance sampling for rare crash events
particle_filter.py    Sequential Monte Carlo for real-time updating
variance_reduction.py Antithetic + control variate + stratified sampling
copula_sim.py         Gaussian, Student-t, Clayton correlated outcomes
market_abm.py         Agent-based prediction market microstructure
pipeline.py           Full end-to-end pipeline connecting all six tools
```

---

## Tool 1: binary_pricer.py

**Question it answers:** What is the probability that an asset finishes above a strike price at expiry?

Prices a binary (digital) contract using Monte Carlo simulation of Geometric Brownian Motion under the risk-neutral measure. Compares the result to the Black-Scholes closed-form N(d2) and reports a 95% confidence interval. Also computes the Brier score to evaluate calibration.

**Key functions**

| Function | What it does |
|---|---|
| `mc_binary_price(S0, K, sigma, T, r, n_paths, rng)` | MC estimate of P(S_T > K) with 95% CI |
| `analytical_binary_price(S0, K, sigma, T, r)` | Black-Scholes N(d2) benchmark |
| `brier_score(predicted_prob, actual_outcome)` | Calibration score, lower is better |

**Run it**

```bash
python3 binary_pricer.py
```

**Example output**

```
Contract parameters:
  S0=100, K=105, sigma=0.25, T=0.5yr, r=0.05

Black-Scholes analytical price [N(d2)]: 0.400562

    n_paths     MC Prob    CI Width       Error     Time(s)
------------------------------------------------------------
      1,000    0.402000    0.030367    0.001438      0.0001
     10,000    0.401500    0.009590    0.000938      0.0003
    100,000    0.400630    0.003039    0.000068      0.0018

Brier score (MC[100k] vs analytical): 0.00000000
  CI width shrinks as O(1/sqrt(n_paths))
```

**Use for:** Calibrating prediction market prices, comparing model probability to market-implied probability, Brier score tracking across forecasters.

---

## Tool 2: tail_risk.py

**Question it answers:** How likely is a rare crash event, and can we estimate it without running billions of paths?

Crude Monte Carlo is fundamentally broken for rare events. When P(crash) ~ 0.001, a run of 100,000 paths produces only ~100 hits -- high variance, unstable across runs. **Importance Sampling with exponential tilting** fixes this by shifting the sampling distribution toward the crash region, then correcting for the bias with likelihood ratios.

```
E_P[f(X)] = E_Q[ f(X) * (dP/dQ)(X) ]
```

The optimal tilting parameter `theta` is calculated analytically to center the tilted distribution exactly on the crash threshold, giving ~50% hit rate under the new measure.

**Key functions**

| Function | What it does |
|---|---|
| `crude_mc_crash(S0, K_crash, sigma, T, r, n_paths, rng)` | Naive MC estimate of P(S_T < K_crash) |
| `importance_sampling_crash(..., theta, ...)` | IS estimate with exponential tilting |
| `optimal_theta(S0, K_crash, sigma, T, r)` | Compute the best tilting parameter |

**Run it**

```bash
python3 tail_risk.py
```

**Example output**

```
Scenario: Estimating P(50% crash in 1 year)
  Asset: S0=$100, Crash at: K=$50 (50% drawdown), sigma=30%, T=1yr

Optimal theta: 2.3702

Method                         P(crash)       Variance       Std Error
------------------------------------------------------------------------
Crude Monte Carlo              0.000840       8.4000e-09     9.1652e-05
Importance Sampling            0.000837       1.1300e-13     3.3615e-07

Variance Reduction Factor: 74360.2x
  IS is ~74360x more efficient than crude MC
  Equivalent to crude MC with 7,436,020,000 paths

IS oversamples crash region by ~594x
```

**Use for:** Estimating drawdown probabilities, stress testing, pricing deep out-of-the-money puts, risk of ruin calculations.

---

## Tool 3: particle_filter.py

**Question it answers:** As new binary observations arrive one at a time, what is our best real-time estimate of the hidden probability?

Implements a **SIR (Sequential Importance Resampling) Particle Filter** for Bayesian tracking of a hidden probability. The classic application is election night: each county result is a noisy binary observation; the hidden state is the true win probability, which we want to track in real time.

The hidden state lives in logit space and evolves as a random walk. For each new observation:
1. **Predict** -- add process noise to each particle
2. **Reweight** -- update weights via Bernoulli log-likelihood
3. **Estimate** -- compute weighted mean and 95% CI
4. **Resample** -- if ESS < N/2, apply systematic resampling

**Key functions**

| Function | What it does |
|---|---|
| `run_particle_filter(observations, n_particles, process_noise, ...)` | Full SIR filter, returns filtered probs + CI + ESS |
| `generate_observations(true_probs, rng)` | Simulate binary data from known truth |
| `systematic_resample(weights, rng)` | Low-variance resampling step |
| `logit(p)` and `expit(x)` | Log-odds transform and its inverse |

**Run it**

```bash
python3 particle_filter.py
```

**Example output**

```
Scenario: Simulating election night -- tracking hidden win probability
as county results arrive one at a time.

True probability trajectory: 0.500 -> 0.650
Total observations: 50 binary county results

 Step   Obs    True P    Filtered           95% CI     ESS
------------------------------------------------------------------
    1     0     0.500       0.476   (0.309, 0.660)   817.2
    6     1     0.562       0.509   (0.364, 0.671)   720.1
   11     1     0.561       0.562   (0.417, 0.693)   598.4
   26     1     0.609       0.609   (0.484, 0.726)   512.7
   50     1     0.650       0.641   (0.536, 0.740)   441.3

Mean Absolute Error vs true:   0.0289
Final filtered estimate:       0.6410
Final true probability:        0.6500
```

**Use for:** Real-time election tracking, live sports betting probability updates, any streaming binary data where the underlying probability is non-stationary.

---

## Tool 4: variance_reduction.py

**Question it answers:** How do you price options accurately without needing 10 million paths?

Three stackable variance reduction techniques for Monte Carlo option pricing. Each exploits a different structural property of the problem. Combined, they routinely achieve **100-500x variance reduction** -- this is table stakes in production quant desks.

**Techniques**

| Method | Mechanism | Typical VR |
|---|---|---|
| Antithetic variates | For every draw Z, also use -Z. Paired payoffs are negatively correlated. | 2-4x |
| Control variates | Use S_T (known expectation under risk-neutral measure) to subtract correlated noise. | 5-20x |
| Stratified sampling | Partition [0,1] into equal strata; draw one uniform per stratum. Guarantees full coverage. | 2-5x |
| Combined (all three) | Stack stratified Z values, antithetic pairs, then control variate adjustment. | 100-500x |

**Key functions**

| Function | What it does |
|---|---|
| `crude_mc(S0, K, sigma, T, r, n_paths, rng)` | Baseline MC call price + variance |
| `antithetic_mc(...)` | Antithetic variates pricing |
| `control_variate_mc(...)` | Control variate adjusted pricing |
| `stratified_mc(...)` | Stratified sampling pricing |
| `combined_mc(...)` | All three stacked |
| `bs_call_price(...)` | Black-Scholes analytical benchmark |

**Run it**

```bash
python3 variance_reduction.py
```

**Example output**

```
Option parameters: S0=100, K=100, sigma=0.20, T=1yr, r=0.05
Paths per method:  100,000
Black-Scholes analytical call price: 10.450584

Method                  Price     Variance     VR Factor   Error vs BS
------------------------------------------------------------------------
Crude MC             10.453142   1.14e-04          1.00x     0.002558
Antithetic           10.451201   3.12e-05          3.65x     0.000617
Control Variate      10.450891   6.83e-06         16.69x     0.000307
Stratified           10.450763   2.71e-05          4.21x     0.000179
Combined             10.450591   3.97e-07        286.97x     0.000007
```

**Use for:** Pricing European options, any payoff function where variance reduction makes the difference between a usable and an unusable estimate.

---

## Tool 5: copula_sim.py

**Question it answers:** If you hold a portfolio of correlated binary contracts, what is the true probability of a sweep win or a total loss?

**The Gaussian copula is wrong.** It treats extreme co-movements as near-impossible. It contributed to the 2008 financial crisis because CDO pricing assumed Gaussian dependence and wildly underestimated joint default probabilities.

This tool simulates correlated binary outcomes under three copulas and shows the difference directly.

**Copula comparison**

| Copula | Lower tail (joint loss) | Upper tail (joint win) | Character |
|---|---|---|---|
| Gaussian | 0 | 0 | Dangerous default -- understates both extremes |
| Student-t (df=3) | ~0.20 | ~0.20 | Symmetric: both tails elevated equally |
| Clayton (theta=2) | 0.707 | 0 | Crash contagion: losses cluster, wins do not |

**Key functions**

| Function | What it does |
|---|---|
| `gaussian_copula_sim(corr_matrix, marginal_probs, n_sims, rng)` | Gaussian copula, no tail dependence |
| `student_t_copula_sim(corr_matrix, df, marginal_probs, n_sims, rng)` | t-copula, symmetric tail dependence |
| `clayton_copula_sim(theta, marginal_probs, n_sims, rng)` | Clayton copula, lower tail only |
| `estimate_joint_probs(outcomes, labels)` | P(all win), P(all lose), P(>=k) for any d |

**Run it**

```bash
python3 copula_sim.py
```

**Example output**

```
Scenario: 5 correlated swing states, each with marginal P(win) = 0.55
  Pairwise rho: 0.40   Clayton theta: 2.0   Student-t df: 3

Baseline (independent, no copula):
  P(sweep all 5) = 0.55^5 = 0.05033
  P(lose all 5)  = 0.45^5 = 0.01845

Copula         P(sweep)   P(0 wins)   P(>=4)   P(>=3)   AvgCorr
-------------------------------------------------------------------
Independent     0.05033     0.01845      n/a      n/a       n/a
Gaussian        0.07421     0.02931   0.2081   0.4573    0.2401
Student-t       0.08103     0.03487   0.2194   0.4631    0.2408
Clayton         0.07289     0.04021   0.2065   0.4538    0.2399

Clayton gives HIGHEST P(all lose) due to asymmetric lower tail dependence.
Student-t raises BOTH tails symmetrically.
```

**Use for:** Portfolio construction on prediction markets, understanding blowup risk in correlated positions, stress testing a book of binary contracts.

---

## Tool 6: market_abm.py

**Question it answers:** How does private information get incorporated into a prediction market price, and who profits?

An **Agent-Based Model (ABM)** of prediction market microstructure with three agent types. Price emerges from collective trading -- no closed-form SDE captures this.

**Agent types**

| Agent | Behavior | Expected PnL |
|---|---|---|
| Informed trader | Knows true probability. Trades toward it proportionally to edge. | Positive (systematic) |
| Noise trader | Random orders. No information content. | Negative (donates to informed) |
| Market maker | Quotes price, adjusts via Kyle lambda after each net flow. | Near zero |

**Kyle lambda** is the price-impact coefficient: `new_price = old_price + lambda * net_order_flow`. Higher lambda means each order is more informative. The market maker estimates lambda empirically via OLS from realized price changes and flows.

**Key functions**

| Function | What it does |
|---|---|
| `simulate_market(true_prob, n_informed, n_noise, n_steps, kyle_lambda, rng)` | Full simulation, returns price trajectory + PnL breakdown |
| `estimate_kyle_lambda(prices, net_flows)` | OLS recovery of price-impact coefficient |
| `InformedTrader`, `NoiseTrader`, `MarketMaker` | Agent classes, usable independently |

**Run it**

```bash
python3 market_abm.py
```

**Example output**

```
Simulation 1: Baseline
  True probability : 0.70   Informed: 5   Noise: 20   Steps: 1000

--- Price Trajectory ---
  Step     Price   vs True
     0    0.5000   -0.2000
   100    0.5912   -0.1088
   250    0.6378   -0.0622
   500    0.6821   -0.0179
  1000    0.6953   -0.0047

--- PnL Breakdown ---
  Informed traders  : +0.3521
  Noise traders     : -0.3847
  Market maker      : +0.0326
  Total (sum ~= 0)  : +0.0000

Kyle lambda -- configured: 0.0500  estimated: 0.0498
```

**Use for:** Understanding information asymmetry, modeling speed of price discovery, sizing positions when you have information edge, studying market microstructure.

---

## Tool 7: pipeline.py

**Question it answers:** What does the complete quant simulation workflow look like end to end?

Connects all six tools into a single seven-stage pipeline. Runs them in sequence on a shared set of contract parameters and prints a summary table. Each stage degrades gracefully if a sibling module is missing.

**Stages**

| Stage | Tool | What it does |
|---|---|---|
| 1 | binary_pricer | MC probability estimation + Brier score vs N(d2) |
| 2 | variance_reduction | Crude MC vs combined (stratified + antithetic + CV) |
| 3 | tail_risk | Crude MC vs importance sampling for 30% crash |
| 4 | copula_sim | Gaussian, Student-t, Clayton for 3-contract portfolio |
| 5 | market_abm | 500-step ABM, price convergence + PnL attribution |
| 6 | particle_filter | 30-step streaming filter, prob drifts 0.50 to 0.65 |
| 7 | summary | Aggregated metrics table across all stages |

**Run it**

```bash
python3 pipeline.py
```

**Example summary table output**

```
  Stage      Tool                     Primary Metric                         Secondary
  ---------  ------------------------ --------------------------------------  ----------------------------
  Stage 1    Probability Estimation   MC P(S>K) = 0.4002                    N(d2) = 0.4006
  Stage 2    Variance Reduction       Combined price = 10.4507              VR factor = 286.9x
  Stage 3    Tail Risk (IS)           IS P(crash) = 0.021403                VR factor = 41.3x
  Stage 4    Dependency Modeling      P(all win): Gauss=0.1751              t=0.1893  Clayton=0.1688
  Stage 5    Market Simulation        Final price=0.6421 (true=0.65)        Informed PnL=+0.2847
  Stage 6    Real-Time Filtering      Filtered=0.6380  (true=0.6500)        MAE=0.0312

  Pipeline complete. All 6 quantitative simulation tools executed.
```

---

## Installation

No package manager required beyond a standard Python environment.

```bash
git clone <repo>
cd quant-sim-toolkit
pip install numpy scipy
```

All tools run from the same directory. `pipeline.py` imports the six sibling modules directly.

---

## Quick reference

```bash
# Run individual tools
python3 binary_pricer.py       # Binary contract pricing, convergence table
python3 tail_risk.py           # Importance sampling vs crude MC
python3 particle_filter.py     # Particle filter election night demo
python3 variance_reduction.py  # 5-method comparison table
python3 copula_sim.py          # 3 copulas x 5 states comparison
python3 market_abm.py          # ABM price discovery + PnL attribution

# Run the full pipeline
python3 pipeline.py
```

---

## Credit

All seven tools are implementations of techniques from the viral X thread by **@gemchange_ltd**: *"How to Simulate Like a Quant Desk"* (2.7M views). The code adds explicit docstrings, modular functions for reuse, and a pipeline connecting all techniques into a single workflow.
