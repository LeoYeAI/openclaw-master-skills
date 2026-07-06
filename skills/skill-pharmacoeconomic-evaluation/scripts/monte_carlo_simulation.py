"""
Pharmacoeconomic Evaluation - Monte Carlo Simulation Tool
Monte Carlo Simulation for Pharmacoeconomic Evaluation
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Callable, List
from scipy import stats
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None


class MonteCarloSimulator:
    """
    Monte Carlo Simulator
    """

    def __init__(self, n_simulations: int = 10000, seed: int = None):
        """
        Initialize Monte Carlo Simulator

        Parameters:
        -----------
        n_simulations : int
            Number of simulations
        seed : int, optional
            Random seed
        """
        self.n_simulations = n_simulations
        self.seed = seed

        if seed is not None:
            np.random.seed(seed)

    def generate_samples(
        self,
        distribution: str,
        params: tuple,
        size: int,
        min_value: float = None,
        max_value: float = None
    ) -> np.ndarray:
        """
        Generate samples from specified distribution

        Parameters:
        -----------
        distribution : str
            Distribution type ('normal', 'beta', 'gamma', 'lognormal', 'uniform', 'triangular')
        params : tuple
            Distribution parameters
        size : int
            Sample size
        min_value : float, optional
            Minimum value (for truncation)
        max_value : float, optional
            Maximum value (for truncation)

        Returns:
        --------
        np.ndarray: Generated samples
        """
        if distribution == 'normal':
            samples = np.random.normal(*params, size)
        elif distribution == 'beta':
            samples = np.random.beta(*params, size)
        elif distribution == 'gamma':
            samples = np.random.gamma(*params, size)
        elif distribution == 'lognormal':
            samples = np.random.lognormal(*params, size)
        elif distribution == 'uniform':
            samples = np.random.uniform(*params, size)
        elif distribution == 'triangular':
            samples = np.random.triangular(*params, size)
        else:
            raise ValueError(f"Unsupported distribution type: {distribution}")

        # Truncate to specified range
        if min_value is not None:
            samples = np.maximum(samples, min_value)
        if max_value is not None:
            samples = np.minimum(samples, max_value)

        return samples

    def probabilistic_sensitivity_analysis(
        self,
        parameters: Dict[str, Dict],
        outcome_func: Callable,
        threshold: float = None
    ) -> pd.DataFrame:
        """
        Probabilistic Sensitivity Analysis (PSA)

        Parameters:
        -----------
        parameters : dict
            Parameter dictionary {
                'param_name': {
                    'distribution': 'normal',
                    'params': (mean, std),
                    'min_value': 0,
                    'max_value': None
                }
            }
        outcome_func : callable
            Function to calculate results, accepts parameter dictionary and returns result dictionary
        threshold : float, optional
            Willingness-to-pay threshold

        Returns:
        --------
        pd.DataFrame: Simulation results
        """
        results = []

        # Generate samples for each parameter
        samples = {}
        for param_name, param_config in parameters.items():
            samples[param_name] = self.generate_samples(
                param_config['distribution'],
                param_config['params'],
                self.n_simulations,
                param_config.get('min_value'),
                param_config.get('max_value')
            )

        # Execute simulation
        iterator = range(self.n_simulations)
        if tqdm is not None:
            iterator = tqdm(iterator, desc="Running PSA")
        for i in iterator:
            # Build parameter set
            params = {name: samples[name][i] for name in samples}

            # Calculate results
            outcome = outcome_func(params)
            outcome['simulation'] = i
            results.append(outcome)

        df = pd.DataFrame(results)

        # If threshold is provided, calculate cost-effectiveness probability
        if threshold is not None and 'icer' in df.columns:
            df['cost_effective'] = df['icer'] <= threshold
            df['cost_effective_probability'] = df['cost_effective'].mean()

        return df

    def calculate_net_benefit(
        self,
        costs: np.ndarray,
        effects: np.ndarray,
        threshold: float
    ) -> np.ndarray:
        """
        Calculate Net Benefit

        Parameters:
        -----------
        costs : np.ndarray
            Cost array
        effects : np.ndarray
            Effect array
        threshold : float
            Willingness-to-pay threshold

        Returns:
        --------
        np.ndarray: Net benefit array
        """
        return threshold * effects - costs

    def generate_ceac(
        self,
        costs: np.ndarray,
        effects: np.ndarray,
        thresholds: np.ndarray
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Generate Cost-Effectiveness Acceptability Curve (CEAC)

        Parameters:
        -----------
        costs : np.ndarray
            Cost array
        effects : np.ndarray
            Effect array
        thresholds : np.ndarray
            Willingness-to-pay threshold array

        Returns:
        --------
        tuple: (Probability array, detailed results DataFrame)
        """
        ceac_data = []

        for threshold in thresholds:
            net_benefits = self.calculate_net_benefit(costs, effects, threshold)
            probability = np.mean(net_benefits > 0)

            ceac_data.append({
                'threshold': threshold,
                'probability': probability,
                'mean_nb': net_benefits.mean(),
                'std_nb': net_benefits.std(),
                'ci_lower': np.percentile(net_benefits, 2.5),
                'ci_upper': np.percentile(net_benefits, 97.5)
            })

        probabilities = np.array([d['probability'] for d in ceac_data])
        return probabilities, pd.DataFrame(ceac_data)

    def scatter_plot_data(
        self,
        costs: np.ndarray,
        effects: np.ndarray,
        reference_cost: float,
        reference_effect: float
    ) -> pd.DataFrame:
        """
        Prepare Cost-Effectiveness Scatter Plot Data

        Parameters:
        -----------
        costs : np.ndarray
            Intervention group cost array
        effects : np.ndarray
            Intervention group effect array
        reference_cost : float
            Control group cost
        reference_effect : float
            Control group effect

        Returns:
        --------
        pd.DataFrame: Scatter plot data
        """
        delta_costs = costs - reference_cost
        delta_effects = effects - reference_effect

        icers = np.zeros(len(costs))
        valid_mask = delta_effects != 0
        icers[valid_mask] = delta_costs[valid_mask] / delta_effects[valid_mask]

        df = pd.DataFrame({
            'cost': costs,
            'effect': effects,
            'delta_cost': delta_costs,
            'delta_effect': delta_effects,
            'icer': icers
        })

        # Mark dominance type
        df['quadrant'] = np.where(
            (delta_costs < 0) & (delta_effects > 0), 'dominant',
            np.where(
                (delta_costs > 0) & (delta_effects < 0), 'dominated',
                'other'
            )
        )

        return df

    def value_of_information_analysis(
        self,
        results_df: pd.DataFrame,
        threshold: float,
        population: int = None
    ) -> Dict:
        """
        Value of Information Analysis (VOI)

        Parameters:
        -----------
        results_df : pd.DataFrame
            Simulation results
        threshold : float
            Willingness-to-pay threshold
        population : int, optional
            Target population size

        Returns:
        --------
        dict: VOI analysis results
        """
        # Calculate net benefit
        if 'net_benefit' not in results_df.columns:
            results_df['net_benefit'] = self.calculate_net_benefit(
                results_df['cost'].values,
                results_df['effect'].values,
                threshold
            )

        # Calculate expected net benefit
        enb = results_df['net_benefit'].mean()

        # Calculate net benefit difference between each simulation and optimal decision
        max_nb = results_df['net_benefit'].max()
        losses = max_nb - results_df['net_benefit']

        # Calculate Expected Value of Perfect Information (EVPI)
        evpi = losses.mean()

        # If population is provided, calculate total EVPI
        evpi_total = evpi * population if population else None

        # Calculate cost-effectiveness plane distribution
        ce_plane = results_df[['delta_cost', 'delta_effect']].copy()
        quadrant_counts = ce_plane.apply(
            lambda row: 'NE' if row['delta_cost'] > 0 and row['delta_effect'] > 0 else
                        'NW' if row['delta_cost'] < 0 and row['delta_effect'] > 0 else
                        'SE' if row['delta_cost'] > 0 and row['delta_effect'] < 0 else 'SW',
            axis=1
        ).value_counts()

        return {
            'expected_net_benefit': enb,
            'evpi_per_patient': evpi,
            'evpi_total': evpi_total,
            'population': population,
            'quadrant_distribution': quadrant_counts.to_dict(),
            'probability_cost_effective': (results_df['net_benefit'] > 0).mean()
        }

    def tornado_plot_data_from_psa(
        self,
        results_df: pd.DataFrame,
        base_params: Dict,
        outcome_func: Callable,
        threshold: float = None
    ) -> pd.DataFrame:
        """
        Generate Tornado Plot Data from PSA Results

        Parameters:
        -----------
        results_df : pd.DataFrame
            PSA results
        base_params : dict
            Baseline parameters
        outcome_func : callable
            Function to calculate results
        threshold : float, optional
            Willingness-to-pay threshold

        Returns:
        --------
        pd.DataFrame: Tornado plot data
        """
        tornado_data = []

        # Calculate baseline results
        base_outcome = outcome_func(base_params)
        base_value = base_outcome.get('icer', 0)

        # Perform one-way sensitivity analysis for each parameter
        for param in results_df.columns:
            if param in ['simulation', 'cost_effective', 'icer', 'cost', 'effect',
                        'delta_cost', 'delta_effect', 'quadrant', 'net_benefit']:
                continue

            # Calculate parameter percentiles
            p25 = results_df[param].quantile(0.25)
            p75 = results_df[param].quantile(0.75)

            # Calculate lower bound results
            params_low = base_params.copy()
            params_low[param] = p25
            outcome_low = outcome_func(params_low)
            value_low = outcome_low.get('icer', base_value)

            # Calculate upper bound results
            params_high = base_params.copy()
            params_high[param] = p75
            outcome_high = outcome_func(params_high)
            value_high = outcome_high.get('icer', base_value)

            tornado_data.append({
                'parameter': param,
                'p25': p25,
                'p75': p75,
                'value_low': value_low,
                'value_base': base_value,
                'value_high': value_high,
                'range': abs(value_high - value_low)
            })

        df = pd.DataFrame(tornado_data)
        df = df.sort_values('range', ascending=True)
        return df

    def calculate_statistics(self, data: np.ndarray, ci: float = 0.95) -> Dict:
        """
        Calculate Statistics

        Parameters:
        -----------
        data : np.ndarray
            Data array
        ci : float
            Confidence interval

        Returns:
        --------
        dict: Statistics
        """
        alpha = 1 - ci
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        return {
            'mean': np.mean(data),
            'median': np.median(data),
            'std': np.std(data),
            'min': np.min(data),
            'max': np.max(data),
            'ci_lower': np.percentile(data, lower_percentile),
            'ci_upper': np.percentile(data, upper_percentile),
            'ci_level': ci
        }


def generate_psa_report(
    results_df: pd.DataFrame,
    ceac_df: pd.DataFrame,
    voi_results: Dict,
    threshold: float = None
):
    """
    Generate PSA Analysis Report

    Parameters:
    -----------
    results_df : pd.DataFrame
        PSA results
    ceac_df : pd.DataFrame
        CEAC data
    voi_results : dict
        VOI analysis results
    threshold : float, optional
        Willingness-to-pay threshold
    """
    print("=" * 70)
    print("Probabilistic Sensitivity Analysis (PSA) Report")
    print("=" * 70)

    print(f"\n[Basic Statistics]")
    print(f"Number of simulations: {len(results_df):,}")

    if 'cost' in results_df.columns:
        cost_stats = {
            'mean': results_df['cost'].mean(),
            'std': results_df['cost'].std(),
            'median': results_df['cost'].median(),
            'ci_lower': results_df['cost'].quantile(0.025),
            'ci_upper': results_df['cost'].quantile(0.975)
        }
        print(f"\nCost Statistics:")
        print(f"  Mean: {cost_stats['mean']:,.2f} yuan")
        print(f"  Standard Deviation: {cost_stats['std']:,.2f} yuan")
        print(f"  Median: {cost_stats['median']:,.2f} yuan")
        print(f"  95% CI: ({cost_stats['ci_lower']:,.2f}, {cost_stats['ci_upper']:,.2f}) yuan")

    if 'effect' in results_df.columns:
        effect_stats = {
            'mean': results_df['effect'].mean(),
            'std': results_df['effect'].std(),
            'median': results_df['effect'].median(),
            'ci_lower': results_df['effect'].quantile(0.025),
            'ci_upper': results_df['effect'].quantile(0.975)
        }
        print(f"\nEffect Statistics:")
        print(f"  Mean: {effect_stats['mean']:.4f} QALY")
        print(f"  Standard Deviation: {effect_stats['std']:.4f} QALY")
        print(f"  Median: {effect_stats['median']:.4f} QALY")
        print(f"  95% CI: ({effect_stats['ci_lower']:.4f}, {effect_stats['ci_upper']:.4f}) QALY")

    if 'icer' in results_df.columns:
        icers = results_df['icer'][(results_df['icer'] != np.inf) &
                                    (results_df['icer'] != -np.inf) &
                                    (~results_df['icer'].isna())]

        if len(icers) > 0:
            print(f"\nICER Statistics:")
            print(f"  Mean: {icers.mean():,.2f} yuan/QALY")
            print(f"  Median: {icers.median():,.2f} yuan/QALY")
            print(f"  95% CI: ({icers.quantile(0.025):,.2f}, {icers.quantile(0.975):,.2f}) yuan/QALY")

            # Dominance quadrant distribution
            if 'quadrant' in results_df.columns:
                print(f"\nDominance Quadrant Distribution:")
                quadrant_dist = results_df['quadrant'].value_counts()
                for quad, count in quadrant_dist.items():
                    pct = count / len(results_df) * 100
                    print(f"  {quad}: {count} ({pct:.1f}%)")

    if threshold is not None:
        print(f"\n[Cost-Effectiveness Probability] (Threshold: {threshold:,.2f} yuan/QALY)")
        prob_ce = (results_df['net_benefit'] > 0).mean() if 'net_benefit' in results_df.columns else 0
        print(f"  Cost-effectiveness probability: {prob_ce * 100:.1f}%")

    print(f"\n[Value of Information Analysis]")
    print(f"  Expected Net Benefit: {voi_results['expected_net_benefit']:,.2f} yuan/patient")
    print(f"  EVPI (per patient): {voi_results['evpi_per_patient']:,.2f} yuan")
    if voi_results['evpi_total']:
        print(f"  EVPI (total): {voi_results['evpi_total']:,.2f} yuan")
    print(f"  Cost-effectiveness probability: {voi_results['probability_cost_effective'] * 100:.1f}%")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Example usage
    print("Pharmacoeconomic Evaluation - Monte Carlo Simulation Tool")
    print("=" * 50)

    # Create simulator
    simulator = MonteCarloSimulator(n_simulations=10000, seed=42)

    # Define parameter distributions
    parameters = {
        'cost': {
            'distribution': 'gamma',
            'params': (2, 15000),  # shape, scale
            'min_value': 0
        },
        'effect': {
            'distribution': 'beta',
            'params': (5, 3),  # alpha, beta
            'min_value': 0,
            'max_value': 10
        }
    }

    # Define outcome calculation function
    def calculate_outcome(params):
        return {
            'cost': params['cost'],
            'effect': params['effect'],
            'icer': params['cost'] / params['effect'] if params['effect'] > 0 else np.inf
        }

    # Execute PSA
    results = simulator.probabilistic_sensitivity_analysis(parameters, calculate_outcome)

    # Generate CEAC
    thresholds = np.linspace(0, 200000, 100)
    ceac_probs, ceac_df = simulator.generate_ceac(
        results['cost'].values,
        results['effect'].values,
        thresholds
    )

    # VOI analysis
    voi_results = simulator.value_of_information_analysis(
        results,
        threshold=50000,
        population=100000
    )

    # Generate report
    generate_psa_report(results, ceac_df, voi_results, threshold=50000)
