"""
药物经济学评价 - 预算影响分析计算脚本
Budget Impact Analysis Calculator
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


class BudgetImpactModel:
    """
    预算影响分析模型
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
        初始化预算影响分析模型

        Parameters:
        -----------
        target_population : int
            目标人群数量
        treatment_cost_new : float
            新治疗方案的人均成本
        treatment_cost_old : float
            旧治疗方案的人均成本
        horizon_years : int
            分析周期（年）
        uptake_rate : float
            新疗法的采用率（0-1）
        market_share_new : float
            新疗法的市场份额（0-1）
        market_share_old : float
            旧疗法的市场份额（0-1）
        discount_rate : float
            贴现率
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
        计算考虑人口增长后的目标人群数量

        Parameters:
        -----------
        year : int
            年份
        growth_rate : float
            人口增长率

        Returns:
        --------
        int: 该年的目标人群数量
        """
        return int(self.target_population * ((1 + growth_rate) ** year))

    def calculate_annual_budget_impact(
        self,
        year: int,
        population_growth_rate: float = 0.0,
        treatment_cost_inflation: float = 0.0
    ) -> Dict:
        """
        计算单年度的预算影响

        Parameters:
        -----------
        year : int
            年份（0-based）
        population_growth_rate : float
            人口增长率
        treatment_cost_inflation : float
            治疗成本通胀率

        Returns:
        --------
        dict: 单年度预算影响结果
        """
        # 计算该年人口
        population = self.population_growth(year, population_growth_rate)

        # 调整成本（考虑通胀）
        cost_new = self.treatment_cost_new * ((1 + treatment_cost_inflation) ** year)
        cost_old = self.treatment_cost_old * ((1 + treatment_cost_inflation) ** year)

        # 计算各治疗方案的患者数量
        patients_new = int(population * self.market_share_new)
        patients_old = int(population * self.market_share_old)

        # 计算成本
        total_cost_new = patients_new * cost_new
        total_cost_old = patients_old * cost_old
        total_cost = total_cost_new + total_cost_old

        # 贴现
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
        计算特定情境下的预算影响

        Parameters:
        -----------
        scenario_name : str
            情境名称
        uptake_rates : list
            各年采用率列表
        population_growth_rate : float
            人口增长率
        treatment_cost_inflation : float
            治疗成本通胀率

        Returns:
        --------
        pd.DataFrame: 预算影响分析表
        """
        results = []

        for year in range(self.horizon_years):
            # 更新采用率
            self.uptake_rate = uptake_rates[year] if year < len(uptake_rates) else uptake_rates[-1]

            # 更新市场份额
            self.market_share_new = self.uptake_rate
            self.market_share_old = 1.0 - self.uptake_rate

            # 计算该年预算影响
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
        比较多个情境

        Parameters:
        -----------
        scenarios : dict
            情境字典 {情境名称: 采用率列表}
        population_growth_rate : float
            人口增长率
        treatment_cost_inflation : float
            治疗成本通胀率

        Returns:
        --------
        pd.DataFrame: 多情境比较结果
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
        生成预算影响分析摘要

        Parameters:
        -----------
        df : pd.DataFrame
            预算影响分析结果

        Returns:
        --------
        dict: 分析摘要
        """
        summary = {
            'total_discounted_cost': df['discounted_cost'].sum(),
            'total_undiscounted_cost': df['total_cost'].sum(),
            'average_annual_cost': df['discounted_cost'].mean(),
            'total_patients': df['patients_new'].sum() + df['patients_old'].sum(),
            'cost_per_patient': df['total_cost'].sum() / (df['patients_new'].sum() + df['patients_old'].sum())
        }

        if 'scenario' in df.columns:
            # 按情境分组
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
        单因素敏感性分析

        Parameters:
        -----------
        parameter : str
            参数名称 ('population', 'cost_new', 'cost_old', 'discount_rate')
        values : list
            参数值列表
        base_scenario : dict
            基准情境
        population_growth_rate : float
            人口增长率
        treatment_cost_inflation : float
            治疗成本通胀率

        Returns:
        --------
        pd.DataFrame: 敏感性分析结果
        """
        # 保存原始值
        original_value = getattr(self, parameter)

        results = []

        for value in values:
            # 更新参数
            setattr(self, parameter, value)

            # 计算情境
            for scenario_name, uptake_rates in base_scenario.items():
                scenario_results = self.calculate_budget_impact_scenario(
                    scenario_name, uptake_rates, population_growth_rate, treatment_cost_inflation
                )
                scenario_results[f'{parameter}_value'] = value
                results.append(scenario_results)

        # 恢复原始值
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
    计算增量预算影响

    Parameters:
    -----------
    base_line_cost : float
        基准人均成本
    intervention_cost : float
        干预人均成本
    target_population : int
        目标人群数量
    uptake_rate : float
        采用率
    time_horizon : int
        时间周期
    discount_rate : float
        贴现率

    Returns:
    --------
    dict: 增量预算影响结果
    """
    # 年度增量成本
    annual_incremental_cost = (intervention_cost - base_line_cost) * target_population * uptake_rate

    # 计算各年贴现后的增量成本
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
    currency: str = "元"
):
    """
    打印预算影响分析报告

    Parameters:
    -----------
    df : pd.DataFrame
        预算影响分析结果
    summary : dict
        分析摘要
    currency : str
        货币单位
    """
    print("=" * 70)
    print("预算影响分析报告")
    print("=" * 70)

    print(f"\n【摘要】")
    print(f"贴现后总成本: {summary['total_discounted_cost']:,.2f} {currency}")
    print(f"未贴现总成本: {summary['total_undiscounted_cost']:,.2f} {currency}")
    print(f"平均年度成本: {summary['average_annual_cost']:,.2f} {currency}")
    print(f"总患者数: {summary['total_patients']:,}")
    print(f"人均成本: {summary['cost_per_patient']:,.2f} {currency}")

    print(f"\n【年度预算影响】")
    print("-" * 70)
    print(f"{'年份':<6} {'人口':<10} {'新疗法患者':<12} {'旧疗法患者':<12} {'总成本':<15} {'贴现后成本':<15}")
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
    # 示例使用
    print("药物经济学评价 - 预算影响分析计算工具")
    print("=" * 50)

    # 创建预算影响模型
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

    # 定义情境
    scenarios = {
        "基准情境": [0.2, 0.3, 0.4, 0.5, 0.6],
        "乐观情境": [0.3, 0.5, 0.7, 0.8, 0.9],
        "保守情境": [0.1, 0.15, 0.2, 0.25, 0.3]
    }

    # 计算预算影响
    results = model.compare_scenarios(
        scenarios,
        population_growth_rate=0.02,
        treatment_cost_inflation=0.01
    )

    # 生成摘要
    summary = model.generate_summary(results)

    # 打印报告
    base_scenario = results[results['scenario'] == '基准情境'].copy()
    budget_impact_report(base_scenario, summary)

    print("\n【多情境比较】")
    scenario_comparison = results.groupby('scenario')['discounted_cost'].sum()
    for scenario, cost in scenario_comparison.items():
        print(f"{scenario}: {cost:,.2f} 元")
