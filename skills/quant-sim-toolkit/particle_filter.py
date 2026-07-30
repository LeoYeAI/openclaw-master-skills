"""
Particle Filter: Sequential Monte Carlo for Real-Time Probability Updating
==========================================================================

The FILTERING PROBLEM: a hidden state evolves over time and we observe noisy
signals. We want to track the posterior p(x_t | y_1:t) as each observation arrives.

APPLICATION -- Election Night Tracking:
Hidden state x_t = logit(p_t) is the log-odds of a candidate winning.
It evolves as a random walk; each observation y_t is a binary county result.

STATE-SPACE MODEL:
    Transition: x_t = x_{t-1} + epsilon_t,  epsilon_t ~ N(0, noise^2)
    Observation: y_t ~ Bernoulli(expit(x_t))

SIR PARTICLE FILTER:
Maintain N particles {x_t^(i), w_t^(i)}. For each new observation y_t:
    1. PREDICT:   x_t^(i) = x_{t-1}^(i) + N(0, process_noise^2)
    2. REWEIGHT:  w_t^(i) proportional to Bernoulli likelihood p(y_t | x_t^(i))
    3. NORMALIZE: divide weights by their sum
    4. ESTIMATE:  filtered_prob = weighted mean of expit(x_t^(i))
    5. RESAMPLE:  if ESS = 1/sum(w^2) < N/2, apply systematic resampling

SYSTEMATIC RESAMPLING:
One draw U ~ Uniform(0,1). Positions = (arange(N)+U)/N. Exactly one position
falls in each equal-width stratum, giving lower variance than multinomial.
"""

import numpy as np


def logit(p):
    """
    Log-odds transform: log(p/(1-p)).

    Maps probability p in (0,1) to the real line.
    Clips p to avoid log(0).

    Parameters
    ----------
    p : float or np.ndarray

    Returns
    -------
    float or np.ndarray
    """
    p = np.clip(p, 1e-10, 1.0 - 1e-10)
    return np.log(p/(1.0 - p))


def expit(x):
    """
    Inverse logit (sigmoid): 1/(1+exp(-x)).

    Maps log-odds back to probability in (0,1).
    Numerically stable: avoids overflow on large inputs.

    Parameters
    ----------
    x : float or np.ndarray

    Returns
    -------
    float or np.ndarray
    """
    return np.where(
        x >= 0,
        1.0/(1.0 + np.exp(-x)),
        np.exp(x)/(1.0 + np.exp(x))
    )


def systematic_resample(weights, rng):
    """
    Systematic resampling for particle filters.

    One draw U ~ Uniform(0,1). N positions at (arange(N)+U)/N spaced through
    the cumulative weight distribution. Returns indices of selected particles.

    Lower variance than multinomial: one position per equal-probability stratum.

    Parameters
    ----------
    weights : np.ndarray -- normalised weights summing to 1, length N.
    rng : np.random.Generator

    Returns
    -------
    indices : np.ndarray of int, length N
    """
    N = len(weights)
    U = rng.uniform(0.0, 1.0)
    positions = (np.arange(N) + U)/N
    cumsum = np.cumsum(weights)
    indices = np.searchsorted(cumsum, positions)
    indices = np.clip(indices, 0, N - 1)
    return indices


def generate_observations(true_probs, rng):
    """
    Generate binary observations from a sequence of true probabilities.

    Draws y_t ~ Bernoulli(p_t) for each true probability p_t.

    Parameters
    ----------
    true_probs : np.ndarray -- true probabilities, one per time step.
    rng : np.random.Generator

    Returns
    -------
    observations : np.ndarray of int -- binary array of 0s and 1s.
    """
    u = rng.uniform(size=len(true_probs))
    return (u < true_probs).astype(int)


def run_particle_filter(
    observations,
    n_particles,
    process_noise,
    initial_logit_mean,
    initial_logit_std,
    rng
):
    """
    SIR Particle Filter for hidden probability estimation.

    Tracks hidden probability p_t via N particles in logit space.
    State: x_t ~ N(x_{t-1}, process_noise^2)
    Observation: y_t ~ Bernoulli(expit(x_t))

    Parameters
    ----------
    observations : np.ndarray of int -- binary observations (0 or 1).
    n_particles : int -- number of particles.
    process_noise : float -- std dev of state transition noise in logit space.
    initial_logit_mean : float -- prior mean of logit(p) at t=0.
    initial_logit_std : float -- prior std dev of logit(p) at t=0.
    rng : np.random.Generator

    Returns
    -------
    dict with keys:
        filtered_probs : np.ndarray -- weighted mean estimate per step.
        ci_lower : np.ndarray -- 2.5th weighted percentile per step.
        ci_upper : np.ndarray -- 97.5th weighted percentile per step.
        ess : np.ndarray -- effective sample size per step.
    """
    T = len(observations)
    N = n_particles

    particles = rng.normal(initial_logit_mean, initial_logit_std, N)
    weights = np.ones(N)/N

    filtered_probs = np.zeros(T)
    ci_lower = np.zeros(T)
    ci_upper = np.zeros(T)
    ess_history = np.zeros(T)

    for t in range(T):
        # 1. PREDICT
        particles = particles + rng.normal(0.0, process_noise, N)

        # 2. CONVERT to probability space
        prob_particles = expit(particles)

        # 3. UPDATE WEIGHTS via Bernoulli log-likelihood
        y = observations[t]
        if y == 1:
            log_likelihood = np.log(np.clip(prob_particles, 1e-10, 1.0))
        else:
            log_likelihood = np.log(np.clip(1.0 - prob_particles, 1e-10, 1.0))

        log_weights = np.log(weights + 1e-300) + log_likelihood
        log_weights -= log_weights.max()
        weights = np.exp(log_weights)
        weights /= weights.sum()

        # 4. EFFECTIVE SAMPLE SIZE: ESS = 1/sum(w^2)
        ess = 1.0/np.sum(weights**2)
        ess_history[t] = ess

        # 5. ESTIMATE: weighted mean + weighted quantile CI
        filtered_probs[t] = np.sum(weights*prob_particles)

        sort_idx = np.argsort(prob_particles)
        sorted_probs = prob_particles[sort_idx]
        sorted_weights = weights[sort_idx]
        cumw = np.cumsum(sorted_weights)
        ci_lower[t] = sorted_probs[np.searchsorted(cumw, 0.025)]
        ci_upper[t] = sorted_probs[np.searchsorted(cumw, 0.975)]

        # 6. RESAMPLE if ESS < N/2
        if ess < N/2.0:
            indices = systematic_resample(weights, rng)
            particles = particles[indices]
            weights = np.ones(N)/N

    return {
        "filtered_probs": filtered_probs,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "ess": ess_history,
    }


if __name__ == "__main__":
    print("=" * 68)
    print("  PARTICLE FILTER: SEQUENTIAL MONTE CARLO")
    print("=" * 68)

    rng = np.random.default_rng(42)

    print()
    print("Scenario: Simulating election night -- tracking hidden win probability")
    print("as county results arrive one at a time.")
    print()

    n_steps = 50
    t_grid = np.linspace(0, 1, n_steps)
    # Logit-space drift: logit(0.50)=0.0 to logit(0.65)~0.619
    true_logits = 0.619*t_grid
    true_probs = expit(true_logits)

    observations = generate_observations(true_probs, rng)

    print(f"True probability trajectory: {true_probs[0]:.3f} -> {true_probs[-1]:.3f}")
    print(f"Total observations:          {n_steps} binary county results")
    print(f"Wins observed:               {observations.sum()} of {n_steps}")
    print()

    n_particles = 1000
    process_noise = 0.1

    results = run_particle_filter(
        observations=observations,
        n_particles=n_particles,
        process_noise=process_noise,
        initial_logit_mean=logit(0.5),
        initial_logit_std=0.5,
        rng=rng,
    )

    filtered = results["filtered_probs"]
    ci_lo = results["ci_lower"]
    ci_hi = results["ci_upper"]
    ess = results["ess"]

    print(f"{'Step':>5}  {'Obs':>4}  {'True P':>8}  {'Filtered':>10}  "
          f"{'95% CI':>20}  {'ESS':>7}")
    print("-" * 62)

    for t in range(0, n_steps, 5):
        ci_str = f"({ci_lo[t]:.3f}, {ci_hi[t]:.3f})"
        print(f"{t+1:>5}  {observations[t]:>4}  {true_probs[t]:>8.3f}"
              f"  {filtered[t]:>10.3f}  {ci_str:>20}  {ess[t]:>7.1f}")

    last = n_steps - 1
    if last % 5 != 0:
        ci_str = f"({ci_lo[last]:.3f}, {ci_hi[last]:.3f})"
        print(f"{last+1:>5}  {observations[last]:>4}  {true_probs[last]:>8.3f}"
              f"  {filtered[last]:>10.3f}  {ci_str:>20}  {ess[last]:>7.1f}")

    print()
    print("Summary:")
    mae = np.mean(np.abs(filtered - true_probs))
    final_error = abs(filtered[-1] - true_probs[-1])
    avg_ess = ess.mean()
    resample_count = int(np.sum(ess < n_particles/2.0))

    print(f"  Mean Absolute Error vs true:   {mae:.4f}")
    print(f"  Final filtered estimate:        {filtered[-1]:.4f}")
    print(f"  Final true probability:         {true_probs[-1]:.4f}")
    print(f"  Final absolute error:           {final_error:.4f}")
    print(f"  Average ESS:                   {avg_ess:.1f} of {n_particles}")
    print(f"  Number of resample events:      {resample_count}")
    print()
    print("The filter tracks the rising probability smoothly,")
    print("incorporating binary county results one at a time.")
    print("The 95% CI narrows as evidence accumulates.")
    print("=" * 68)
