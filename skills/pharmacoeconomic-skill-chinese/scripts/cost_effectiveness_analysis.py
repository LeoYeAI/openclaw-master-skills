"""
药物经济学评价 - 成本-效果分析计算脚本
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
    计算增量成本-效果比 (Incremental Cost-Effectiveness Ratio, ICER)

    Parameters:
    -----------
    cost_a : float
        干预组A的成本
    effect_a : float
        干预组A的效果（如获得的生命年、QALYs等）
    cost_b : float
        对照组B的成本
    effect_b : float
        对照组B的效果
    threshold : float, optional
        支付阈值（willingness-to-pay threshold）

    Returns:
    --------
    dict: 包含ICER、增量成本、增量效果等结果的字典
    """
    delta_cost = cost_a - cost_b
    delta_effect = effect_a - effect_b

    result = {
        'incremental_cost': delta_cost,
        'incremental_effect': delta_effect,
        'dominance': None
    }

    # 判断优势情况
    if delta_cost > 0 and delta_effect < 0:
        result['dominance'] = 'dominated'  # 严格劣势
        result['icer'] = None
    elif delta_cost < 0 and delta_effect > 0:
        result['dominance'] = 'dominant'  # 严格优势
        result['icer'] = None
    elif delta_effect == 0:
        result['icer'] = None
        result['note'] = '增量效果为零，无法计算ICER'
    else:
        result['icer'] = delta_cost / delta_effect

    # 评估经济性
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
    计算成本-效果可接受曲线 (Cost-Effectiveness Acceptability Curve, CEAC)

    Parameters:
    -----------
    costs : np.ndarray
        干预组的成本数组（用于bootstrap）
    effects : np.ndarray
        干预组的效果数组（用于bootstrap）
    thresholds : np.ndarray
        支付阈值数组
    bootstrap_iter : int
        Bootstrap迭代次数
    seed : int, optional
        随机种子

    Returns:
    --------
    tuple: (概率数组, 统计信息字典)
    """
    if seed is not None:
        np.random.seed(seed)

    n = len(thresholds)
    probabilities = np.zeros(n)

    for i, threshold in enumerate(thresholds):
        # Bootstrap重采样
        boot_costs = np.random.choice(costs, size=(bootstrap_iter, len(costs)))
        boot_effects = np.random.choice(effects, size=(bootstrap_iter, len(effects)))

        # 计算每次迭代的净收益
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
    确定性敏感性分析 (单因素敏感性分析)

    Parameters:
    -----------
    base_params : dict
        基准参数值
    param_ranges : dict
        参数范围 {param_name: (min_value, max_value)}
    outcome_func : callable
        计算结果的函数，接受参数字典，返回ICER等结果

    Returns:
    --------
    pd.DataFrame: 敏感性分析结果
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
    为龙卷风图准备数据

    Parameters:
    -----------
    base_params : dict
        基准参数值
    param_ranges : dict
        参数范围
    outcome_func : callable
        计算ICER的函数
    threshold : float
        支付阈值

    Returns:
    --------
    pd.DataFrame: 龙卷风图数据
    """
    base_outcome = outcome_func(base_params)
    base_icer = base_outcome.get('icer', 0)

    tornado_data = []

    for param, (low, high) in param_ranges.items():
        # 下限值
        params_low = base_params.copy()
        params_low[param] = low
        outcome_low = outcome_func(params_low)
        icer_low = outcome_low.get('icer', base_icer)

        # 上限值
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
    df = df.sort_values('range', ascending=True)  # 按影响范围排序
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
    蒙特卡洛模拟

    Parameters:
    -----------
    n_simulations : int
        模拟次数
    cost_dist : str
        成本分布类型 ('normal', 'gamma', 'lognormal')
    cost_params : tuple
        成本分布参数
    effect_dist : str
        效果分布类型
    effect_params : tuple
        效果分布参数
    threshold : float, optional
        支付阈值
    seed : int, optional
        随机种子

    Returns:
    --------
    dict: 模拟结果统计
    """
    if seed is not None:
        np.random.seed(seed)

    # 生成成本和效果
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

    # 确保成本为正
    costs = np.maximum(costs, 0)

    # 计算ICERs
    icers = np.zeros(n_simulations)
    for i in range(n_simulations):
        # 与基准比较（假设基准为第一个模拟）
        delta_cost = costs[i] - costs[0]
        delta_effect = effects[i] - effects[0]
        if delta_effect != 0:
            icers[i] = delta_cost / delta_effect

    # 计算统计量
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
        # 计算净收益
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
    计算质量调整生命年 (Quality-Adjusted Life Years, QALYs)

    Parameters:
    -----------
    life_years : float
        生命年
    utility_scores : np.ndarray
        效用分数数组（每个时间段的效用）
    discount_rate : float
        贴现率

    Returns:
    --------
    float: QALYs
    """
    periods = len(utility_scores)
    period_length = life_years / periods

    # 计算贴现因子
    discount_factors = np.array([
        1 / ((1 + discount_rate) ** (i * period_length))
        for i in range(periods)
    ])

    # 计算QALYs
    qalys = np.sum(utility_scores * period_length * discount_factors)

    return qalys


def markov_model_transition(
    state_dist: np.ndarray,
    transition_matrix: np.ndarray,
    cycles: int,
    discount_rate: float = 0.03
) -> Dict:
    """
    马尔可夫模型模拟

    Parameters:
    -----------
    state_dist : np.ndarray
        初始状态分布 [n_states]
    transition_matrix : np.ndarray
        转移矩阵 [n_states, n_states]
    cycles : int
        模拟周期数
    discount_rate : float
        贴现率

    Returns:
    --------
    dict: 包含每个周期状态分布、累积成本、累积QALYs等
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

        # 贴现因子
        discount_factor = 1 / ((1 + discount_rate) ** cycle)

        # 累积成本和QALYs（需要额外参数）
        total_cost += 0  # 这里应该根据实际情况计算
        total_qaly += 0

        cumulative_costs.append(total_cost * discount_factor)
        cumulative_qalys.append(total_qaly * discount_factor)

        # 转移到下一个周期
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
    成本贴现

    Parameters:
    -----------
    costs : np.ndarray
        各期成本数组
    periods : np.ndarray
        时间周期数组
    discount_rate : float
        贴现率

    Returns:
    --------
    float: 贴现后的总成本
    """
    discount_factors = 1 / ((1 + discount_rate) ** periods)
    discounted_costs = costs * discount_factors
    return discounted_costs.sum()


def print_icer_report(result: Dict, threshold: float = None):
    """
    打印ICER分析报告

    Parameters:
    -----------
    result : dict
        ICER计算结果
    threshold : float, optional
        支付阈值
    """
    print("=" * 60)
    print("增量成本-效果比分析报告")
    print("=" * 60)

    print(f"\n增量成本: {result['incremental_cost']:.2f}")
    print(f"增量效果: {result['incremental_effect']:.4f}")

    if result['dominance'] == 'dominant':
        print("\n结论: 干预组具有绝对优势（成本更低，效果更好）")
    elif result['dominance'] == 'dominated':
        print("\n结论: 干预组处于劣势（成本更高，效果更差）")
    elif result['icer'] is not None:
        print(f"\nICER: {result['icer']:.2f}")

        if threshold is not None:
            print(f"支付阈值: {threshold:.2f}")
            if result['cost_effective']:
                print(f"\n结论: 具有成本效果 (ICER ≤ 支付阈值)")
            else:
                print(f"\n结论: 不具有成本效果 (ICER > 支付阈值)")
    else:
        print("\n结论: 无法计算ICER（增量效果为零）")

    print("=" * 60)


if __name__ == "__main__":
    # 示例使用
    print("药物经济学评价 - 成本-效果分析计算工具")
    print("=" * 50)

    # 示例：计算ICER
    cost_intervention = 50000
    effect_intervention = 5.2  # QALYs
    cost_control = 30000
    effect_control = 4.5  # QALYs

    result = calculate_icere(
        cost_intervention, effect_intervention,
        cost_control, effect_control,
        threshold=50000  # 中国阈值：约1-3倍人均GDP
    )

    print_icer_report(result, threshold=50000)
