#!/usr/bin/env python3
"""
Personality Core Pure Python Fallback

当 C 扩展不可用时，提供纯 Python 实现的核心算法。
所有函数与 personality_core.so 接口完全一致。
"""

import math
from typing import List


def normalize_weights(weights: List[float]) -> List[float]:
    """
    归一化马斯洛权重

    参数:
        weights: 包含6个权重的列表 [physiological, safety, belonging, esteem, self_actualization, self_transcendence]

    返回:
        归一化后的权重列表
    """
    if len(weights) != 6:
        raise ValueError("weights must have exactly 6 elements")

    total = sum(weights)
    if total == 0:
        return [1/6] * 6

    return [w / total for w in weights]


def calculate_similarity(trait1: List[float], trait2: List[float]) -> float:
    """
    计算大五人格相似度

    参数:
        trait1: 包含5个特质值的列表 [openness, conscientiousness, extraversion, agreeableness, neuroticism]
        trait2: 包含5个特质值的列表

    返回:
        相似度分数 (0.0-1.0)，1.0表示完全相似
    """
    if len(trait1) != 5 or len(trait2) != 5:
        raise ValueError("traits must have exactly 5 elements")

    # 计算欧氏距离
    distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(trait1, trait2)))

    # 转换为相似度 (距离越小，相似度越高)
    # 最大可能距离 = sqrt(5 * 1.0^2) = sqrt(5) ≈ 2.236
    similarity = 1.0 - (distance / 2.236)
    return max(0.0, similarity)


def compute_maslow_priority(maslow_weights: List[float], intent_weights: List[float]) -> float:
    """
    计算马斯洛优先级

    参数:
        maslow_weights: 包含6个马斯洛权重的列表
        intent_weights: 包含6个意图权重的列表

    返回:
        加权优先级分数
    """
    if len(maslow_weights) != 6 or len(intent_weights) != 6:
        raise ValueError("weights must have exactly 6 elements")

    return sum(m * i for m, i in zip(maslow_weights, intent_weights))


def compute_all_scores(maslow_weights: List[float], intent_weights_list: List[List[float]]) -> List[float]:
    """
    批量计算所有优先级分数

    参数:
        maslow_weights: 包含6个马斯洛权重的列表
        intent_weights_list: 包含多个意图权重的列表的列表

    返回:
        包含所有优先级分数的列表
    """
    if len(maslow_weights) != 6:
        raise ValueError("maslow weights must have exactly 6 elements")

    return [compute_maslow_priority(maslow_weights, intent) for intent in intent_weights_list]


# 性能测试
if __name__ == "__main__":
    import time

    # 测试归一化
    print("=== 测试 normalize_weights ===")
    weights = [0.35, 0.35, 0.1, 0.1, 0.08, 0.02]
    normalized = normalize_weights(weights)
    print(f"输入: {weights}")
    print(f"输出: {normalized}")
    print(f"总和: {sum(normalized):.6f}")

    # 测试相似度
    print("\n=== 测试 calculate_similarity ===")
    trait1 = [0.6, 0.8, 0.4, 0.6, 0.5]
    trait2 = [0.5, 0.7, 0.5, 0.6, 0.4]
    similarity = calculate_similarity(trait1, trait2)
    print(f"Trait 1: {trait1}")
    print(f"Trait 2: {trait2}")
    print(f"相似度: {similarity:.6f}")

    # 测试优先级
    print("\n=== 测试 compute_maslow_priority ===")
    maslow = [0.35, 0.35, 0.1, 0.1, 0.08, 0.02]
    intent = [0.2, 0.3, 0.15, 0.15, 0.1, 0.1]
    priority = compute_maslow_priority(maslow, intent)
    print(f"马斯洛权重: {maslow}")
    print(f"意图权重: {intent}")
    print(f"优先级: {priority:.6f}")

    # 性能测试
    print("\n=== 性能测试 ===")
    n = 10000

    start = time.time()
    for _ in range(n):
        normalize_weights(weights)
    print(f"归一化 {n} 次: {(time.time() - start) * 1000:.2f}ms")

    start = time.time()
    for _ in range(n):
        calculate_similarity(trait1, trait2)
    print(f"相似度计算 {n} 次: {(time.time() - start) * 1000:.2f}ms")

    start = time.time()
    for _ in range(n):
        compute_maslow_priority(maslow, intent)
    print(f"优先级计算 {n} 次: {(time.time() - start) * 1000:.2f}ms")

    # 批量计算测试
    intent_list = [[0.2, 0.3, 0.15, 0.15, 0.1, 0.1] for _ in range(1000)]
    start = time.time()
    scores = compute_all_scores(maslow, intent_list)
    print(f"批量计算 {len(intent_list)} 个优先级: {(time.time() - start) * 1000:.2f}ms")
    print(f"平均每个: {(time.time() - start) * 1000 / len(intent_list):.4f}ms")
