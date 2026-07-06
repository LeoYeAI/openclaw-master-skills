"""
Pharmacoeconomic Evaluation - Cost-Effectiveness Analysis Calculation Script
Cost-Effectiveness Analysis Calculator
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List


def calculate_icere(
    cost_a: float,
    effect_a: float,
    cost_b: float,
    effect_b: float,
    threshold: float = None
) -> Dict:
    """
    Calculate Incremental Cost-Effectiveness Ratio (ICER)

    Parameters:
    -----------
    cost_a : float
        Cost of intervention group A
    effect_a : float
        Effect of intervention group A (e.g., life years gained, QALYs, etc.)
    cost_b : float
        Cost of control group B
    effect_b : float
        Effect of control group B
    threshold : float, optional
        Willingness-to-pay threshold

    Returns:
    --------
    dict: Dictionary containing ICER, incremental cost, incremental effect and other results
    """
    delta_cost = cost_a - cost_b
    delta_effect = effect_a - effect_b

    result = {
        'incremental_cost': delta_cost,
        'incremental_effect': delta_effect,
        'dominance': None
    }

    # Determine dominance situation
    if delta_cost > 0 and delta_effect < 0:
        result['dominance'] = 'dominated'  # Strictly dominated
        result['icer'] = None
    elif delta_cost < 0 and delta_effect > 0:
        result['dominance'] = 'dominant'  # Strictly dominant
        result['icer'] = None
    elif delta_effect == 0:
        result['icer'] = None
        result['note'] = 'Incremental effect is zero, cannot calculate ICER'
    else:
        result['icer'] = delta_cost / delta_effect

    # Evaluate cost-effectiveness
    if threshold is not None and result['icer'] is not None:
        result['cost_effective'] = result['icer'] <= threshold

    return result


def calculate_ceac(
    costs: np.ndarray,
    effects: np.ndarray,
    thresholds: np.ndarray,
    bootstrap_iter: int = 10000,
    seed: int = None
) -> Tuple[np.ndarray, Dict]:
    """
    Calculate Cost-Effectiveness Acceptability Curve (CEAC)

    Parameters:
    -----------
    costs : np.ndarray
        Cost array for intervention group (for bootstrap)
    effects : np.ndarray
        Effect array for intervention group (for bootstrap)
    thresholds : np.ndarray
        Willingness-to-pay threshold array
    bootstrap_iter : int
        Number of bootstrap iterations
    seed : int, optional
        Random seed

    Returns:
    --------
    tuple: (probability array, statistics dictionary)
    """
    if seed is not None:
        np.random.seed(seed)

    n = len(thresholds)
    probabilities = np.zeros(n)

    for i, threshold in enumerate(thresholds):
        # Bootstrap resampling
        boot_costs = np.random.choice(costs, size=(bootstrap_iter, len(costs)))
        boot_effects = np.random.choice(effects, size=(bootstrap_iter, len(effects)))

        # Calculate net benefit for each iteration
        net_benefits = threshold * boot_effects - boot_costs
        probabilities[i] = np.mean(np.mean(net_benefits, axis=1) > 0)

    stats = {
        'bootstrap_iterations': bootstrap_iter,
        'threshold_range': (thresholds.min(), thresholds.max()),
        'cost_mean': costs.mean(),
        'cost_std': costs.std(),
        'effect_mean': effects.mean(),
        'effect_std': effects.std()
    }

    return probabilities, stats


def deterministic_sensitivity_analysis(
    base_params: Dict,
    param_ranges: Dict,
    outcome_func: callable
) -> pd.DataFrame:
    """
    Deterministic Sensitivity Analysis (One-Way Sensitivity Analysis)

    Parameters:
    -----------
    base_params : dict
        Baseline parameter values
    param_ranges : dict
        Parameter ranges {param_name: (min_value, max_value)}
    outcome_func : callable
        Outcome calculation function, accepts parameter dictionary and returns ICER and other results

    Returns:
    --------
    pd.DataFrame: Sensitivity analysis results
    """
    results = []
    param_names = list(param_ranges.keys())

    for param in param_names:
        for value in [param_ranges[param][0], param_ranges[param][1]]:
            params = base_params.copy()
            params[param] = value
            outcome = outcome_func(params)

            result = {
                'parameter': param,
                'value': value,
                **outcome
            }
            results.append(result)

    return pd.DataFrame(results)


def tornado_plot_data(
    base_params: Dict,
    param_ranges: Dict,
    outcome_func: callable,
    threshold: float
) -> pd.DataFrame:
    """
    Prepare data for tornado plot

    Parameters:
    -----------
    base_params : dict
        Baseline parameter values
    param_ranges : dict
        Parameter ranges
    outcome_func : callable
        Function to calculate ICER
    threshold : float
        Willingness-to-pay threshold

    Returns:
    --------
    pd.DataFrame: Tornado plot data
    """
    base_outcome = outcome_func(base_params)
    base_icer = base_outcome.get('icer', 0)

    tornado_data = []

    for param, (low, high) in param_ranges.items():
        # Lower bound value
        params_low = base_params.copy()
        params_low[param] = low
        outcome_low = outcome_func(params_low)
        icer_low = outcome_low.get('icer', base_icer)

        # Upper bound value
        params_high = base_params.copy()
        params_high[param] = high
        outcome_high = outcome_func(params_high)
        icer_high = outcome_high.get('icer', base_icer)

        tornado_data.append({
            'parameter': param,
            'low': icer_low,
            'base': base_icer,
            'high': icer_high,
            'range': abs(icer_high - icer_low)
        })

    df = pd.DataFrame(tornado_data)
    df = df.sort_values('range', ascending=True)  # Sort by impact range
    return df


def monte_carlo_simulation(
    n_simulations: int,
    cost_dist: str,
    cost_params: tuple,
    effect_dist: str,
    effect_params: tuple,
    threshold: float = None,
    seed: int = None
) -> Dict:
    """
    Monte Carlo Simulation

    Parameters:
    -----------
    n_simulations : int
        Number of simulations
    cost_dist : str
        Cost distribution type ('normal', 'gamma', 'lognormal')
    cost_params : tuple
        Cost distribution parameters
    effect_dist : str
        Effect distribution type
    effect_params : tuple
        Effect distribution parameters
    threshold : float, optional
        Willingness-to-pay threshold
    seed : int, optional
        Random seed

    Returns:
    --------
    dict: Simulation result statistics
    """
    if seed is not None:
        np.random.seed(seed)

    # Generate costs and effects
    if cost_dist == 'normal':
        costs = np.random.normal(*cost_params, n_simulations)
    elif cost_dist == 'gamma':
        costs = np.random.gamma(*cost_params, n_simulations)
    elif cost_dist == 'lognormal':
        costs = np.random.lognormal(*cost_params, n_simulations)
    else:
        raise ValueError(f"Unsupported cost distribution: {cost_dist}")

    if effect_dist == 'normal':
        effects = np.random.normal(*effect_params, n_simulations)
    elif effect_dist == 'beta':
        effects = np.random.beta(*effect_params, n_simulations)
    else:
        raise ValueError(f"Unsupported effect distribution: {effect_dist}")

    # Ensure costs are positive
    costs = np.maximum(costs, 0)

    # Calculate ICERs
    icers = np.zeros(n_simulations)
    for i in range(n_simulations):
        # Compare with baseline (assuming baseline is the first simulation)
        delta_cost = costs[i] - costs[0]
        delta_effect = effects[i] - effects[0]
        if delta_effect != 0:
            icers[i] = delta_cost / delta_effect

    # Calculate statistics
    valid_icers = icers[(~np.isinf(icers)) & (~np.isnan(icers))]

    results = {
        'n_simulations': n_simulations,
        'icer_mean': np.mean(valid_icers) if len(valid_icers) > 0 else None,
        'icer_median': np.median(valid_icers) if len(valid_icers) > 0 else None,
        'icer_std': np.std(valid_icers) if len(valid_icers) > 0 else None,
        'icer_ci_lower': np.percentile(valid_icers, 2.5) if len(valid_icers) > 0 else None,
        'icer_ci_upper': np.percentile(valid_icers, 97.5) if len(valid_icers) > 0 else None,
        'cost_mean': costs.mean(),
        'cost_std': costs.std(),
        'effect_mean': effects.mean(),
        'effect_std': effects.std()
    }

    if threshold is not None:
        # Calculate net benefit
        net_benefits = threshold * effects - costs
        results['cost_effective_probability'] = np.mean(net_benefits > 0)
        results['net_benefit_mean'] = net_benefits.mean()
        results['net_benefit_std'] = net_benefits.std()

    return results


def calculate_qaly(
    life_years: float,
    utility_scores: np.ndarray,
    discount_rate: float = 0.03
) -> float:
    """
    Calculate Quality-Adjusted Life Years (QALYs)

    Parameters:
    -----------
    life_years : float
        Life years
    utility_scores : np.ndarray
        Utility score array (utility for each time period)
    discount_rate : float
        Discount rate

    Returns:
    --------
    float: QALYs
    """
    periods = len(utility_scores)
    period_length = life_years / periods

    # Calculate discount factors
    discount_factors = np.array([
        1 / ((1 + discount_rate) ** (i * period_length))
        for i in range(periods)
    ])

    # Calculate QALYs
    qalys = np.sum(utility_scores * period_length * discount_factors)

    return qalys


def markov_model_transition(
    state_dist: np.ndarray,
    transition_matrix: np.ndarray,
    cycles: int,
    discount_rate: float = 0.03
) -> Dict:
    """
    Markov Model Simulation

    Parameters:
    -----------
    state_dist : np.ndarray
        Initial state distribution [n_states]
    transition_matrix : np.ndarray
        Transition matrix [n_states, n_states]
    cycles : int
        Number of simulation cycles
    discount_rate : float
        Discount rate

    Returns:
    --------
    dict: Contains state distribution per cycle, cumulative costs, cumulative QALYs, etc.
    """
    n_states = len(state_dist)
    state_history = []
    cumulative_costs = []
    cumulative_qalys = []

    current_dist = state_dist.copy()
    total_cost = 0
    total_qaly = 0

    for cycle in range(cycles):
        state_history.append(current_dist.copy())

        # Discount factor
        discount_factor = 1 / ((1 + discount_rate) ** cycle)

        # Cumulative costs and QALYs (requires additional parameters)
        total_cost += 0  # This should be calculated based on actual situation
        total_qaly += 0

        cumulative_costs.append(total_cost * discount_factor)
        cumulative_qalys.append(total_qaly * discount_factor)

        # Transition to next cycle
        current_dist = current_dist @ transition_matrix

    return {
        'state_history': np.array(state_history),
        'cumulative_costs': np.array(cumulative_costs),
        'cumulative_qalys': np.array(cumulative_qalys),
        'final_distribution': current_dist
    }


def discount_costs(
    costs: np.ndarray,
    periods: np.ndarray,
    discount_rate: float = 0.03
) -> float:
    """
    Cost Discounting

    Parameters:
    -----------
    costs : np.ndarray
        Cost array for each period
    periods : np.ndarray
        Time period array
    discount_rate : float
        Discount rate

    Returns:
    --------
    float: Total discounted cost
    """
    discount_factors = 1 / ((1 + discount_rate) ** periods)
    discounted_costs = costs * discount_factors
    return discounted_costs.sum()


def print_icer_report(result: Dict, threshold: float = None):
    """
    Print ICER Analysis Report

    Parameters:
    -----------
    result : dict
        ICER calculation result
    threshold : float, optional
        Willingness-to-pay threshold
    """
    print("=" * 60)
    print("Incremental Cost-Effectiveness Ratio Analysis Report")
    print("=" * 60)

    print(f"\nIncremental Cost: {result['incremental_cost']:.2f}")
    print(f"Incremental Effect: {result['incremental_effect']:.4f}")

    if result['dominance'] == 'dominant':
        print("\nConclusion: Intervention group has absolute dominance (lower cost, better effect)")
    elif result['dominance'] == 'dominated':
        print("\nConclusion: Intervention group is dominated (higher cost, worse effect)")
    elif result['icer'] is not None:
        print(f"\nICER: {result['icer']:.2f}")

        if threshold is not None:
            print(f"Willingness-to-pay Threshold: {threshold:.2f}")
            if result['cost_effective']:
                print(f"\nConclusion: Cost-effective (ICER ≤ willingness-to-pay threshold)")
            else:
                print(f"\nConclusion: Not cost-effective (ICER > willingness-to-pay threshold)")
    else:
        print("\nConclusion: Cannot calculate ICER (incremental effect is zero)")

    print("=" * 60)


if __name__ == "__main__":
    # Example usage
    print("Pharmacoeconomic Evaluation - Cost-Effectiveness Analysis Calculation Tool")
    print("=" * 50)

    # Example: Calculate ICER
    cost_intervention = 50000
    effect_intervention = 5.2  # QALYs
    cost_control = 30000
    effect_control = 4.5  # QALYs

    result = calculate_icere(
        cost_intervention, effect_intervention,
        cost_control, effect_control,
        threshold=50000  # China threshold: approximately 1-3 times per capita GDP
    )

    print_icer_report(result, threshold=50000)
