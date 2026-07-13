"""
药物经济学评价 - 蒙特卡洛模拟工具
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
    蒙特卡洛模拟器
    """

    def __init__(self, n_simulations: int = 10000, seed: int = None):
        """
        初始化蒙特卡洛模拟器

        Parameters:
        -----------
        n_simulations : int
            模拟次数
        seed : int, optional
            随机种子
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
        从指定分布生成样本

        Parameters:
        -----------
        distribution : str
            分布类型 ('normal', 'beta', 'gamma', 'lognormal', 'uniform', 'triangular')
        params : tuple
            分布参数
        size : int
            样本数量
        min_value : float, optional
            最小值（用于截断）
        max_value : float, optional
            最大值（用于截断）

        Returns:
        --------
        np.ndarray: 生成的样本
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
            raise ValueError(f"不支持的分布类型: {distribution}")

        # 截断到指定范围
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
        概率敏感性分析 (PSA)

        Parameters:
        -----------
        parameters : dict
            参数字典 {
                'param_name': {
                    'distribution': 'normal',
                    'params': (mean, std),
                    'min_value': 0,
                    'max_value': None
                }
            }
        outcome_func : callable
            计算结果的函数，接受参数字典，返回结果字典
        threshold : float, optional
            支付阈值

        Returns:
        --------
        pd.DataFrame: 模拟结果
        """
        results = []

        # 为每个参数生成样本
        samples = {}
        for param_name, param_config in parameters.items():
            samples[param_name] = self.generate_samples(
                param_config['distribution'],
                param_config['params'],
                self.n_simulations,
                param_config.get('min_value'),
                param_config.get('max_value')
            )

        # 执行模拟
        iterator = range(self.n_simulations)
        if tqdm is not None:
            iterator = tqdm(iterator, desc="执行PSA")
        for i in iterator:
            # 构建参数集
            params = {name: samples[name][i] for name in samples}

            # 计算结果
            outcome = outcome_func(params)
            outcome['simulation'] = i
            results.append(outcome)

        df = pd.DataFrame(results)

        # 如果有阈值，计算成本效果概率
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
        计算净收益

        Parameters:
        -----------
        costs : np.ndarray
            成本数组
        effects : np.ndarray
            效果数组
        threshold : float
            支付阈值

        Returns:
        --------
        np.ndarray: 净收益数组
        """
        return threshold * effects - costs

    def generate_ceac(
        self,
        costs: np.ndarray,
        effects: np.ndarray,
        thresholds: np.ndarray
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        生成成本-效果可接受曲线 (CEAC)

        Parameters:
        -----------
        costs : np.ndarray
            成本数组
        effects : np.ndarray
            效果数组
        thresholds : np.ndarray
            支付阈值数组

        Returns:
        --------
        tuple: (概率数组, 详细结果DataFrame)
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
        准备成本-效果散点图数据

        Parameters:
        -----------
        costs : np.ndarray
            干预组成本数组
        effects : np.ndarray
            干预组效果数组
        reference_cost : float
            对照组成本
        reference_effect : float
            对照组效果

        Returns:
        --------
        pd.DataFrame: 散点图数据
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

        # 标记优势类型
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
        价值信息分析 (VOI)

        Parameters:
        -----------
        results_df : pd.DataFrame
            模拟结果
        threshold : float
            支付阈值
        population : int, optional
            目标人群数量

        Returns:
        --------
        dict: VOI分析结果
        """
        # 计算净收益
        if 'net_benefit' not in results_df.columns:
            results_df['net_benefit'] = self.calculate_net_benefit(
                results_df['cost'].values,
                results_df['effect'].values,
                threshold
            )

        # 计算期望净收益
        enb = results_df['net_benefit'].mean()

        # 计算每个模拟与最佳决策的净收益差异
        max_nb = results_df['net_benefit'].max()
        losses = max_nb - results_df['net_benefit']

        # 计算期望信息价值 (EVPI)
        evpi = losses.mean()

        # 如果有人群数量，计算总体EVPI
        evpi_total = evpi * population if population else None

        # 计算成本效果平面的分布
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
        从PSA结果生成龙卷风图数据

        Parameters:
        -----------
        results_df : pd.DataFrame
            PSA结果
        base_params : dict
            基准参数
        outcome_func : callable
            计算结果的函数
        threshold : float, optional
            支付阈值

        Returns:
        --------
        pd.DataFrame: 龙卷风图数据
        """
        tornado_data = []

        # 计算基准结果
        base_outcome = outcome_func(base_params)
        base_value = base_outcome.get('icer', 0)

        # 对每个参数进行单因素敏感性分析
        for param in results_df.columns:
            if param in ['simulation', 'cost_effective', 'icer', 'cost', 'effect',
                        'delta_cost', 'delta_effect', 'quadrant', 'net_benefit']:
                continue

            # 计算参数的百分位数
            p25 = results_df[param].quantile(0.25)
            p75 = results_df[param].quantile(0.75)

            # 计算下限结果
            params_low = base_params.copy()
            params_low[param] = p25
            outcome_low = outcome_func(params_low)
            value_low = outcome_low.get('icer', base_value)

            # 计算上限结果
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
        计算统计量

        Parameters:
        -----------
        data : np.ndarray
            数据数组
        ci : float
            置信区间

        Returns:
        --------
        dict: 统计量
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
    生成PSA分析报告

    Parameters:
    -----------
    results_df : pd.DataFrame
        PSA结果
    ceac_df : pd.DataFrame
        CEAC数据
    voi_results : dict
        VOI分析结果
    threshold : float, optional
        支付阈值
    """
    print("=" * 70)
    print("概率敏感性分析 (PSA) 报告")
    print("=" * 70)

    print(f"\n【基本统计】")
    print(f"模拟次数: {len(results_df):,}")

    if 'cost' in results_df.columns:
        cost_stats = {
            'mean': results_df['cost'].mean(),
            'std': results_df['cost'].std(),
            'median': results_df['cost'].median(),
            'ci_lower': results_df['cost'].quantile(0.025),
            'ci_upper': results_df['cost'].quantile(0.975)
        }
        print(f"\n成本统计:")
        print(f"  均值: {cost_stats['mean']:,.2f} 元")
        print(f"  标准差: {cost_stats['std']:,.2f} 元")
        print(f"  中位数: {cost_stats['median']:,.2f} 元")
        print(f"  95% CI: ({cost_stats['ci_lower']:,.2f}, {cost_stats['ci_upper']:,.2f}) 元")

    if 'effect' in results_df.columns:
        effect_stats = {
            'mean': results_df['effect'].mean(),
            'std': results_df['effect'].std(),
            'median': results_df['effect'].median(),
            'ci_lower': results_df['effect'].quantile(0.025),
            'ci_upper': results_df['effect'].quantile(0.975)
        }
        print(f"\n效果统计:")
        print(f"  均值: {effect_stats['mean']:.4f} QALY")
        print(f"  标准差: {effect_stats['std']:.4f} QALY")
        print(f"  中位数: {effect_stats['median']:.4f} QALY")
        print(f"  95% CI: ({effect_stats['ci_lower']:.4f}, {effect_stats['ci_upper']:.4f}) QALY")

    if 'icer' in results_df.columns:
        icers = results_df['icer'][(results_df['icer'] != np.inf) &
                                    (results_df['icer'] != -np.inf) &
                                    (~results_df['icer'].isna())]

        if len(icers) > 0:
            print(f"\nICER统计:")
            print(f"  均值: {icers.mean():,.2f} 元/QALY")
            print(f"  中位数: {icers.median():,.2f} 元/QALY")
            print(f"  95% CI: ({icers.quantile(0.025):,.2f}, {icers.quantile(0.975):,.2f}) 元/QALY")

            # 优势象限分布
            if 'quadrant' in results_df.columns:
                print(f"\n优势象限分布:")
                quadrant_dist = results_df['quadrant'].value_counts()
                for quad, count in quadrant_dist.items():
                    pct = count / len(results_df) * 100
                    print(f"  {quad}: {count} ({pct:.1f}%)")

    if threshold is not None:
        print(f"\n【成本效果概率】 (阈值: {threshold:,.2f} 元/QALY)")
        prob_ce = (results_df['net_benefit'] > 0).mean() if 'net_benefit' in results_df.columns else 0
        print(f"  成本效果概率: {prob_ce * 100:.1f}%")

    print(f"\n【价值信息分析】")
    print(f"  期望净收益: {voi_results['expected_net_benefit']:,.2f} 元/患者")
    print(f"  EVPI (每患者): {voi_results['evpi_per_patient']:,.2f} 元")
    if voi_results['evpi_total']:
        print(f"  EVPI (总体): {voi_results['evpi_total']:,.2f} 元")
    print(f"  成本效果概率: {voi_results['probability_cost_effective'] * 100:.1f}%")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # 示例使用
    print("药物经济学评价 - 蒙特卡洛模拟工具")
    print("=" * 50)

    # 创建模拟器
    simulator = MonteCarloSimulator(n_simulations=10000, seed=42)

    # 定义参数分布
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

    # 定义结果计算函数
    def calculate_outcome(params):
        return {
            'cost': params['cost'],
            'effect': params['effect'],
            'icer': params['cost'] / params['effect'] if params['effect'] > 0 else np.inf
        }

    # 执行PSA
    results = simulator.probabilistic_sensitivity_analysis(parameters, calculate_outcome)

    # 生成CEAC
    thresholds = np.linspace(0, 200000, 100)
    ceac_probs, ceac_df = simulator.generate_ceac(
        results['cost'].values,
        results['effect'].values,
        thresholds
    )

    # VOI分析
    voi_results = simulator.value_of_information_analysis(
        results,
        threshold=50000,
        population=100000
    )

    # 生成报告
    generate_psa_report(results, ceac_df, voi_results, threshold=50000)
