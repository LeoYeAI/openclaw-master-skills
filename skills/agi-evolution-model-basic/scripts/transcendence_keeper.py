#!/usr/bin/env python3
"""
超然性保持模块

功能：
- 客观评估机制
- 冲突避免策略
- 独立性保障机制

设计原则：
- 保持外环的超然性
- 不直接干预主循环
- 确保调节建议的独立性
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional


class TranscendenceKeeper:
    """超然性保持器"""
    
    def __init__(self):
        # 客观性评估指标
        self.objectivity_metrics = {
            "emotional_neutrality": 0.3,  # 情绪中性
            "fact_based": 0.3,  # 基于事实
            "logical_consistency": 0.2,  # 逻辑一致性
            "bias_free": 0.2  # 无偏见
        }
        
        # 冲突检测阈值
        self.conflict_thresholds = {
            "direct_intervention": 0.8,  # 直接干预阈值
            "behavioral_override": 0.7,  # 行为覆盖阈值
            "state_modification": 0.6  # 状态修改阈值
        }
        
        # 独立性评估指标
        self.independence_metrics = {
            "decision_autonomy": 0.4,  # 决策自主性
            "data_isolation": 0.3,  # 数据隔离性
            "no_external_dependency": 0.3  # 无外部依赖
        }
    
    def objective_assess(self, regulation: Dict[str, Any], 
                         system_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        客观评估
        
        Args:
            regulation: 调节建议
            system_state: 系统状态（可选）
            
        Returns:
            客观性评估结果
        """
        scores = {}
        
        # 1. 情绪中性评估
        suggestion_text = " ".join(regulation.get("suggestion", []))
        emotion_keywords = ["紧急", "必须", "强制", "绝对", "立即"]
        emotion_count = sum(1 for kw in emotion_keywords if kw in suggestion_text)
        emotional_neutrality_score = max(1.0 - emotion_count * 0.2, 0.0)
        scores["emotional_neutrality"] = round(
            emotional_neutrality_score * self.objectivity_metrics["emotional_neutrality"], 2
        )
        
        # 2. 基于事实评估
        reasoning = regulation.get("reasoning", "")
        fact_indicators = ["基于", "分析", "数据", "结果", "历史"]
        fact_count = sum(1 for indicator in fact_indicators if indicator in reasoning)
        fact_based_score = min(fact_count * 0.3, 1.0)
        scores["fact_based"] = round(
            fact_based_score * self.objectivity_metrics["fact_based"], 2
        )
        
        # 3. 逻辑一致性评估
        has_parameters = bool(regulation.get("parameters"))
        has_expected_outcome = bool(regulation.get("expected_outcome"))
        logical_consistency_score = 0.5 + (0.25 * has_parameters) + (0.25 * has_expected_outcome)
        scores["logical_consistency"] = round(
            logical_consistency_score * self.objectivity_metrics["logical_consistency"], 2
        )
        
        # 4. 无偏见评估
        confidence = regulation.get("confidence", 0.5)
        strength = regulation.get("strength", "medium")
        bias_free_score = min(confidence * 1.2, 1.0)
        if strength == "strong":
            bias_free_score *= 0.9  # 强建议可能带有倾向性
        scores["bias_free"] = round(
            bias_free_score * self.objectivity_metrics["bias_free"], 2
        )
        
        # 计算总客观性得分
        total_score = round(sum(scores.values()), 2)
        
        # 确定客观性级别
        if total_score >= 0.8:
            level = "high"
        elif total_score >= 0.6:
            level = "medium"
        else:
            level = "low"
        
        return {
            "score": total_score,
            "level": level,
            "components": scores,
            "metrics": self.objectivity_metrics
        }
    
    def detect_conflict(self, regulation: Dict[str, Any], 
                        main_loop_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        冲突检测
        
        Args:
            regulation: 调节建议
            main_loop_state: 主循环状态
            
        Returns:
            冲突检测结果
        """
        conflicts_detected = []
        conflict_scores = {}
        
        # 1. 检测直接干预风险
        parameters = regulation.get("parameters", {})
        if parameters.get("preemptible", False):
            conflict_scores["direct_intervention"] = 0.9
            conflicts_detected.append("检测到抢占式参数，可能直接干预主循环")
        elif parameters.get("priority_boost", 0) > 50:
            conflict_scores["direct_intervention"] = 0.7
            conflicts_detected.append("检测到高优先级提升，可能影响主循环正常运行")
        else:
            conflict_scores["direct_intervention"] = 0.2
        
        # 2. 检测行为覆盖风险
        strategy_type = regulation.get("type", "")
        if strategy_type == "priority_reordering":
            conflict_scores["behavioral_override"] = 0.6
            conflicts_detected.append("优先级重排可能覆盖主循环的决策")
        else:
            conflict_scores["behavioral_override"] = 0.3
        
        # 3. 检测状态修改风险
        if "modification" in str(regulation.get("parameters", {})):
            conflict_scores["state_modification"] = 0.8
            conflicts_detected.append("检测到状态修改操作，可能破坏主循环一致性")
        else:
            conflict_scores["state_modification"] = 0.2
        
        # 计算总冲突风险
        total_conflict_score = max(conflict_scores.values())
        
        # 确定冲突级别
        if total_conflict_score >= self.conflict_thresholds["direct_intervention"]:
            conflict_level = "critical"
        elif total_conflict_score >= self.conflict_thresholds["behavioral_override"]:
            conflict_level = "high"
        elif total_conflict_score >= self.conflict_thresholds["state_modification"]:
            conflict_level = "medium"
        else:
            conflict_level = "low"
        
        return {
            "conflict_detected": total_conflict_score > 0.5,
            "conflict_level": conflict_level,
            "conflict_score": round(total_conflict_score, 2),
            "conflicts_detected": conflicts_detected,
            "conflict_components": conflict_scores,
            "thresholds": self.conflict_thresholds
        }
    
    def ensure_independence(self, regulation: Dict[str, Any]) -> Dict[str, Any]:
        """
        独立性保障
        
        Args:
            regulation: 调节建议
            
        Returns:
            独立性评估结果
        """
        scores = {}
        
        # 1. 决策自主性评估
        has_reasoning = bool(regulation.get("reasoning"))
        has_confidence = "confidence" in regulation
        decision_autonomy_score = 0.5 + (0.25 * has_reasoning) + (0.25 * has_confidence)
        scores["decision_autonomy"] = round(
            decision_autonomy_score * self.independence_metrics["decision_autonomy"], 2
        )
        
        # 2. 数据隔离性评估
        suggestion = regulation.get("suggestion", [])
        external_references = [s for s in suggestion if "用户" in s or "外部" in s]
        if len(external_references) > len(suggestion) * 0.5:
            data_isolation_score = 0.5
        else:
            data_isolation_score = 1.0
        scores["data_isolation"] = round(
            data_isolation_score * self.independence_metrics["data_isolation"], 2
        )
        
        # 3. 无外部依赖评估
        parameters = regulation.get("parameters", {})
        if "external" in str(parameters).lower():
            no_external_dependency_score = 0.5
        else:
            no_external_dependency_score = 1.0
        scores["no_external_dependency"] = round(
            no_external_dependency_score * self.independence_metrics["no_external_dependency"], 2
        )
        
        # 计算总独立性得分
        total_score = round(sum(scores.values()), 2)
        
        # 确定独立性级别
        if total_score >= 0.8:
            level = "high"
        elif total_score >= 0.6:
            level = "medium"
        else:
            level = "low"
        
        return {
            "score": total_score,
            "level": level,
            "components": scores,
            "metrics": self.independence_metrics
        }
    
    def evaluate_transcendence(self, regulation: Dict[str, Any], 
                               main_loop_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        综合评估超然性
        
        Args:
            regulation: 调节建议
            main_loop_state: 主循环状态（可选）
            
        Returns:
            超然性评估结果
        """
        # 执行三项评估
        objective_assessment = self.objective_assess(regulation, main_loop_state)
        conflict_detection = self.detect_conflict(regulation, main_loop_state or {})
        independence_assessment = self.ensure_independence(regulation)
        
        # 综合判断是否允许执行
        objective_score = objective_assessment["score"]
        conflict_score = conflict_detection["conflict_score"]
        independence_score = independence_assessment["score"]
        
        # 综合评分算法
        # 客观性权重40%，独立性权重40%，低冲突权重20%
        composite_score = (
            objective_score * 0.4 +
            independence_score * 0.4 +
            (1.0 - conflict_score) * 0.2
        )
        
        # 判断是否允许
        allowed = (
            objective_score >= 0.6 and
            independence_score >= 0.6 and
            conflict_score <= 0.6
        )
        
        return {
            "allowed": allowed,
            "composite_score": round(composite_score, 2),
            "objective_assessment": objective_assessment,
            "conflict_detection": conflict_detection,
            "independence_assessment": independence_assessment,
            "timestamp": datetime.now().isoformat()
        }


def main():
    parser = argparse.ArgumentParser(description="超然性保持模块")
    parser.add_argument("--regulation", required=True,
                        help="调节建议文件路径（JSON格式）")
    parser.add_argument("--main-loop-state",
                        help="主循环状态文件路径（JSON格式，可选）")
    parser.add_argument("--output", help="输出文件路径（JSON格式）")
    parser.add_argument("--component",
                        choices=["objective", "conflict", "independence", "all"],
                        default="all",
                        help="评估组件")
    
    args = parser.parse_args()
    
    # 读取输入数据
    with open(args.regulation, 'r', encoding='utf-8') as f:
        regulation = json.load(f)
    
    main_loop_state = None
    if args.main_loop_state:
        with open(args.main_loop_state, 'r', encoding='utf-8') as f:
            main_loop_state = json.load(f)
    
    keeper = TranscendenceKeeper()
    
    # 执行评估
    if args.component == "all":
        result = keeper.evaluate_transcendence(regulation, main_loop_state)
    elif args.component == "objective":
        result = keeper.objective_assess(regulation, main_loop_state)
    elif args.component == "conflict":
        result = keeper.detect_conflict(regulation, main_loop_state or {})
    elif args.component == "independence":
        result = keeper.ensure_independence(regulation)
    
    # 输出结果
    output_data = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_data)
    else:
        print(output_data)


if __name__ == "__main__":
    main()
