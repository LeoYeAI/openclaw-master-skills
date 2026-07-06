"""
Pharmacoeconomic Evaluation - Budget Impact Analysis Calculation Script
Budget Impact Analysis Calculator
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


class BudgetImpactModel:
    """
    Budget Impact Analysis Model
    """

    def __init__(
        self,
        target_population: int,
        treatment_cost_new: float,
        treatment_cost_old: float,
        horizon_years: int,
        uptake_rate: float = 0.0,
        market_share_new: float = 0.0,
        market_share_old: float = 1.0,
        discount_rate: float = 0.03
    ):
        """
        Initialize Budget Impact Analysis Model

        Parameters:
        -----------
        target_population : int
            Target population size
        treatment_cost_new : float
            Per capita cost of new treatment
        treatment_cost_old : float
            Per capita cost of old treatment
        horizon_years : int
            Analysis period (years)
        uptake_rate : float
            Uptake rate of new therapy (0-1)
        market_share_new : float
            Market share of new therapy (0-1)
        market_share_old : float
            Market share of old therapy (0-1)
        discount_rate : float
            Discount rate
        """
        self.target_population = target_population
        self.treatment_cost_new = treatment_cost_new
        self.treatment_cost_old = treatment_cost_old
        self.horizon_years = horizon_years
        self.uptake_rate = uptake_rate
        self.market_share_new = market_share_new
        self.market_share_old = market_share_old
        self.discount_rate = discount_rate

    def population_growth(self, year: int, growth_rate: float) -> int:
        """
        Calculate target population size considering population growth

        Parameters:
        -----------
        year : int
            Year
        growth_rate : float
            Population growth rate

        Returns:
        --------
        int: Target population size for that year
        """
        return int(self.target_population * ((1 + growth_rate) ** year))

    def calculate_annual_budget_impact(
        self,
        year: int,
        population_growth_rate: float = 0.0,
        treatment_cost_inflation: float = 0.0
    ) -> Dict:
        """
        Calculate single-year budget impact

        Parameters:
        -----------
        year : int
            Year (0-based)
        population_growth_rate : float
            Population growth rate
        treatment_cost_inflation : float
            Treatment cost inflation rate

        Returns:
        --------
        dict: Single-year budget impact results
        """
        # Calculate population for the year
        population = self.population_growth(year, population_growth_rate)

        # Adjust costs (consider inflation)
        cost_new = self.treatment_cost_new * ((1 + treatment_cost_inflation) ** year)
        cost_old = self.treatment_cost_old * ((1 + treatment_cost_inflation) ** year)

        # Calculate patient numbers for each treatment
        patients_new = int(population * self.market_share_new)
        patients_old = int(population * self.market_share_old)

        # Calculate costs
        total_cost_new = patients_new * cost_new
        total_cost_old = patients_old * cost_old
        total_cost = total_cost_new + total_cost_old

        # Discounting
        discount_factor = 1 / ((1 + self.discount_rate) ** year)
        discounted_cost = total_cost * discount_factor

        return {
            'year': year,
            'population': population,
            'patients_new': patients_new,
            'patients_old': patients_old,
            'cost_new': total_cost_new,
            'cost_old': total_cost_old,
            'total_cost': total_cost,
            'discounted_cost': discounted_cost,
            'discount_factor': discount_factor
        }

    def calculate_budget_impact_scenario(
        self,
        scenario_name: str,
        uptake_rates: List[float],
        population_growth_rate: float = 0.0,
        treatment_cost_inflation: float = 0.0
    ) -> pd.DataFrame:
        """
        Calculate budget impact for specific scenario

        Parameters:
        -----------
        scenario_name : str
            Scenario name
        uptake_rates : list
            Annual uptake rate list
        population_growth_rate : float
            Population growth rate
        treatment_cost_inflation : float
            Treatment cost inflation rate

        Returns:
        --------
        pd.DataFrame: Budget impact analysis table
        """
        results = []

        for year in range(self.horizon_years):
            # Update uptake rate
            self.uptake_rate = uptake_rates[year] if year < len(uptake_rates) else uptake_rates[-1]

            # Update market share
            self.market_share_new = self.uptake_rate
            self.market_share_old = 1.0 - self.uptake_rate

            # Calculate budget impact for the year
            annual_result = self.calculate_annual_budget_impact(
                year, population_growth_rate, treatment_cost_inflation
            )
            annual_result['scenario'] = scenario_name
            annual_result['uptake_rate'] = self.uptake_rate
            results.append(annual_result)

        return pd.DataFrame(results)

    def compare_scenarios(
        self,
        scenarios: Dict[str, List[float]],
        population_growth_rate: float = 0.0,
        treatment_cost_inflation: float = 0.0
    ) -> pd.DataFrame:
        """
        Compare multiple scenarios

        Parameters:
        -----------
        scenarios : dict
            Scenario dictionary {scenario_name: uptake_rate_list}
        population_growth_rate : float
            Population growth rate
        treatment_cost_inflation : float
            Treatment cost inflation rate

        Returns:
        --------
        pd.DataFrame: Multi-scenario comparison results
        """
        all_results = []

        for scenario_name, uptake_rates in scenarios.items():
            scenario_results = self.calculate_budget_impact_scenario(
                scenario_name, uptake_rates, population_growth_rate, treatment_cost_inflation
            )
            all_results.append(scenario_results)

        return pd.concat(all_results, ignore_index=True)

    def generate_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate budget impact analysis summary

        Parameters:
        -----------
        df : pd.DataFrame
            Budget impact analysis results

        Returns:
        --------
        dict: Analysis summary
        """
        summary = {
            'total_discounted_cost': df['discounted_cost'].sum(),
            'total_undiscounted_cost': df['total_cost'].sum(),
            'average_annual_cost': df['discounted_cost'].mean(),
            'total_patients': df['patients_new'].sum() + df['patients_old'].sum(),
            'cost_per_patient': df['total_cost'].sum() / (df['patients_new'].sum() + df['patients_old'].sum())
        }

        if 'scenario' in df.columns:
            # Group by scenario
            scenario_summary = df.groupby('scenario').agg({
                'discounted_cost': 'sum',
                'total_cost': 'sum'
            }).to_dict('index')
            summary['by_scenario'] = scenario_summary

        return summary

    def sensitivity_analysis(
        self,
        parameter: str,
        values: List[float],
        base_scenario: Dict[str, List[float]],
        population_growth_rate: float = 0.0,
        treatment_cost_inflation: float = 0.0
    ) -> pd.DataFrame:
        """
        One-Way Sensitivity Analysis

        Parameters:
        -----------
        parameter : str
            Parameter name ('population', 'cost_new', 'cost_old', 'discount_rate')
        values : list
            Parameter value list
        base_scenario : dict
            Base scenario
        population_growth_rate : float
            Population growth rate
        treatment_cost_inflation : float
            Treatment cost inflation rate

        Returns:
        --------
        pd.DataFrame: Sensitivity analysis results
        """
        # Save original value
        original_value = getattr(self, parameter)

        results = []

        for value in values:
            # Update parameter
            setattr(self, parameter, value)

            # Calculate scenario
            for scenario_name, uptake_rates in base_scenario.items():
                scenario_results = self.calculate_budget_impact_scenario(
                    scenario_name, uptake_rates, population_growth_rate, treatment_cost_inflation
                )
                scenario_results[f'{parameter}_value'] = value
                results.append(scenario_results)

        # Restore original value
        setattr(self, parameter, original_value)

        return pd.concat(results, ignore_index=True)


def calculate_incremental_budget_impact(
    base_line_cost: float,
    intervention_cost: float,
    target_population: int,
    uptake_rate: float = 1.0,
    time_horizon: int = 5,
    discount_rate: float = 0.03
) -> Dict:
    """
    Calculate incremental budget impact

    Parameters:
    -----------
    base_line_cost : float
        Base per capita cost
    intervention_cost : float
        Intervention per capita cost
    target_population : int
        Target population size
    uptake_rate : float
        Uptake rate
    time_horizon : int
        Time horizon
    discount_rate : float
        Discount rate

    Returns:
    --------
    dict: Incremental budget impact results
    """
    # Annual incremental cost
    annual_incremental_cost = (intervention_cost - base_line_cost) * target_population * uptake_rate

    # Calculate discounted incremental costs for each year
    years = np.arange(time_horizon)
    discount_factors = 1 / ((1 + discount_rate) ** years)
    discounted_incremental_costs = annual_incremental_cost * discount_factors

    return {
        'annual_incremental_cost': annual_incremental_cost,
        'total_incremental_cost': discounted_incremental_costs.sum(),
        'discounted_incremental_costs_by_year': discounted_incremental_costs.tolist(),
        'discounted_annual_incremental_costs': discounted_incremental_costs.tolist(),
        'per_patient_incremental_cost': intervention_cost - base_line_cost
    }


def budget_impact_report(
    df: pd.DataFrame,
    summary: Dict,
    currency: str = "yuan"
):
    """
    Print budget impact analysis report

    Parameters:
    -----------
    df : pd.DataFrame
        Budget impact analysis results
    summary : dict
        Analysis summary
    currency : str
        Currency unit
    """
    print("=" * 70)
    print("Budget Impact Analysis Report")
    print("=" * 70)

    print(f"\n[Summary]")
    print(f"Total Discounted Cost: {summary['total_discounted_cost']:,.2f} {currency}")
    print(f"Total Undiscounted Cost: {summary['total_undiscounted_cost']:,.2f} {currency}")
    print(f"Average Annual Cost: {summary['average_annual_cost']:,.2f} {currency}")
    print(f"Total Patients: {summary['total_patients']:,}")
    print(f"Cost Per Patient: {summary['cost_per_patient']:,.2f} {currency}")

    print(f"\n[Annual Budget Impact]")
    print("-" * 70)
    print(f"{'Year':<6} {'Population':<10} {'New Therapy Patients':<20} {'Old Therapy Patients':<20} {'Total Cost':<15} {'Discounted Cost':<15}")
    print("-" * 70)

    for _, row in df.iterrows():
        print(f"{row['year']:<6} "
              f"{row['population']:<10,} "
              f"{row['patients_new']:<12,} "
              f"{row['patients_old']:<12,} "
              f"{row['total_cost']:<15,.2f} "
              f"{row['discounted_cost']:<15,.2f}")

    print("=" * 70)


if __name__ == "__main__":
    # Example usage
    print("Pharmacoeconomic Evaluation - Budget Impact Analysis Calculation Tool")
    print("=" * 50)

    # Create budget impact model
    model = BudgetImpactModel(
        target_population=100000,
        treatment_cost_new=15000,
        treatment_cost_old=10000,
        horizon_years=5,
        uptake_rate=0.2,
        market_share_new=0.2,
        market_share_old=0.8,
        discount_rate=0.03
    )

    # Define scenarios
    scenarios = {
        "Base Scenario": [0.2, 0.3, 0.4, 0.5, 0.6],
        "Optimistic Scenario": [0.3, 0.5, 0.7, 0.8, 0.9],
        "Conservative Scenario": [0.1, 0.15, 0.2, 0.25, 0.3]
    }

    # Calculate budget impact
    results = model.compare_scenarios(
        scenarios,
        population_growth_rate=0.02,
        treatment_cost_inflation=0.01
    )

    # Generate summary
    summary = model.generate_summary(results)

    # Print report
    base_scenario = results[results['scenario'] == 'Base Scenario'].copy()
    budget_impact_report(base_scenario, summary)

    print("\n[Multi-Scenario Comparison]")
    scenario_comparison = results.groupby('scenario')['discounted_cost'].sum()
    for scenario, cost in scenario_comparison.items():
        print(f"{scenario}: {cost:,.2f} yuan")
