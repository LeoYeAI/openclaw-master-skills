#!/usr/bin/env python3
"""
意向性调节模块

功能：
- 基于历史经验生成最优解
- 生成软调节建议
- 提供给自我迭代顶点
- 收集反馈

设计原则：
- 基于历史数据优化
- 软调节建议不强制执行
- 可配置的策略库
"""

import argparse
import json
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional


class IntentionalityRegulator:
    """意向性调节器"""
    
    def __init__(self, memory_dir: str = "./agi_memory"):
        self.memory_dir = memory_dir
        
        # 导入建议池（延迟导入）
        try:
            from advice_pool import AdvicePool
            self.advice_pool = AdvicePool(memory_dir=memory_dir)
            self.use_advice_pool = True
        except ImportError:
            self.advice_pool = None
            self.use_advice_pool = False
        
        # 调节策略库
        self.regulation_strategies = {
            "parameter_tuning": {
                "description": "参数微调",
                "strength_levels": {
                    "low": 0.1,
                    "medium": 0.3,
                    "high": 0.5
                }
            },
            "strategy_adjustment": {
                "description": "策略调整",
                "strength_levels": {
                    "low": 0.2,
                    "medium": 0.5,
                    "high": 0.7
                }
            },
            "priority_reordering": {
                "description": "优先级重排",
                "strength_levels": {
                    "low": 0.3,
                    "medium": 0.6,
                    "high": 0.9
                }
            }
        }
        
        # 强度到建议类型的映射
        self.strength_mapping = {
            "low": ["parameter_tuning"],
            "medium": ["parameter_tuning", "strategy_adjustment"],
            "high": ["strategy_adjustment", "priority_reordering"]
        }
    
    def generate_optimal_solution(self, analysis: Dict[str, Any], 
                                   history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        生成最优解
        
        Args:
            analysis: 分析结果
            history: 历史数据列表
            
        Returns:
            最优解方案
        """
        intensity = analysis.get("intensity", {}).get("level", "medium")
        urgency = analysis.get("urgency", {}).get("level", "medium")
        priority = analysis.get("priority", {}).get("level", "medium")
        
        # 基于分析结果选择策略
        strategy_types = []
        
        if priority == "high":
            strategy_types.extend(["priority_reordering", "strategy_adjustment"])
        elif priority == "medium":
            strategy_types.append("strategy_adjustment")
        
        if intensity == "high" and urgency == "high":
            strategy_types.append("priority_reordering")
        
        # 如果没有匹配的策略，使用默认
        if not strategy_types:
            strategy_types = ["parameter_tuning"]
        
        # 去重
        strategy_types = list(set(strategy_types))
        
        # 如果有历史数据，基于历史经验调整
        if history:
            solution = self._refine_with_history(analysis, strategy_types, history)
        else:
            solution = {
                "strategy_types": strategy_types,
                "reasoning": f"基于分析结果：强度={intensity}, 紧迫性={urgency}, 优先级={priority}"
            }
        
        return solution
    
    def _refine_with_history(self, analysis: Dict[str, Any], 
                              strategy_types: List[str],
                              history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        基于历史经验优化方案
        
        Args:
            analysis: 分析结果
            strategy_types: 初始策略类型
            history: 历史数据
            
        Returns:
            优化后的方案
        """
        # 简化的历史匹配：查找相似场景
        current_level = analysis.get("overall_score", 0.5)
        
        # 统计历史中各策略的成功率
        strategy_stats = {}
        for record in history:
            strategy = record.get("strategy_type", "unknown")
            success = record.get("success", False)
            
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {"total": 0, "success": 0}
            
            strategy_stats[strategy]["total"] += 1
            if success:
                strategy_stats[strategy]["success"] += 1
        
        # 选择成功率最高的策略
        best_strategies = []
        for strategy_type in strategy_types:
            if strategy_type in strategy_stats:
                stats = strategy_stats[strategy_type]
                if stats["total"] > 0:
                    success_rate = stats["success"] / stats["total"]
                    if success_rate > 0.7:  # 成功率阈值
                        best_strategies.append(strategy_type)
        
        refined_types = best_strategies if best_strategies else strategy_types
        
        return {
            "strategy_types": refined_types,
            "reasoning": f"基于{len(history)}条历史经验优化，选择高成功率策略",
            "history_used": True
        }
    
    def generate_soft_regulation(self, analysis: Dict[str, Any], 
                                  optimal_solution: Dict[str, Any],
                                  write_to_pool: bool = True) -> Dict[str, Any]:
        """
        生成软调节建议
        
        Args:
            analysis: 分析结果
            optimal_solution: 最优解方案
            write_to_pool: 是否写入建议池（默认True）
            
        Returns:
            软调节建议
        """
        priority = analysis.get("priority", {}).get("level", "medium")
        urgency = analysis.get("urgency", {}).get("level", "medium")
        
        # 根据优先级确定建议强度
        if priority == "high":
            strength = "strong"
        elif priority == "medium":
            strength = "medium"
        else:
            strength = "weak"
        
        # 选择策略类型
        strategy_types = optimal_solution.get("strategy_types", ["parameter_tuning"])
        strategy_type = strategy_types[0] if strategy_types else "parameter_tuning"
        
        # 生成具体建议
        suggestions = self._generate_suggestions(analysis, strategy_type, strength)
        
        # 计算置信度
        confidence = analysis.get("overall_score", 0.5)
        
        # 生成期望结果
        expected_outcome = self._generate_expected_outcome(strategy_type, strength)
        
        # 构建建议对象
        regulation = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "target": "self_iteration_vertex",
            "type": strategy_type,
            "suggestion": suggestions,
            "parameters": self._generate_parameters(analysis, strategy_type),
            "expected_outcome": expected_outcome,
            "strength": strength,
            "confidence": round(confidence, 2),
            "reasoning": optimal_solution.get("reasoning", "")
        }
        
        # 如果启用建议池，写入建议池
        if write_to_pool and self.use_advice_pool:
            suggestion_for_pool = {
                "content": regulation,
                "priority": confidence,
                "confidence": confidence,
                "based_on_intentionality": analysis.get("classification", {})
            }
            
            # 根据目标顶点选择写入位置
            target_vertex = regulation.get("target", "iteration")
            if target_vertex == "drive":
                vertex = "drive"
            elif target_vertex == "math":
                vertex = "math"
            else:
                vertex = "iteration"
            
            try:
                suggestion_id = self.advice_pool.add_suggestion(vertex, suggestion_for_pool)
                regulation["pool_id"] = suggestion_id
                regulation["written_to_pool"] = True
            except Exception as e:
                regulation["written_to_pool"] = False
                regulation["pool_error"] = str(e)
        else:
            regulation["written_to_pool"] = False
        
        return regulation
    
    def _generate_suggestions(self, analysis: Dict[str, Any], 
                               strategy_type: str, strength: str) -> List[str]:
        """
        生成建议文本
        
        Args:
            analysis: 分析结果
            strategy_type: 策略类型
            strength: 强度
            
        Returns:
            建议列表
        """
        priority = analysis.get("priority", {}).get("level", "medium")
        urgency = analysis.get("urgency", {}).get("level", "medium")
        
        suggestions = []
        
        if strategy_type == "parameter_tuning":
            suggestions.append(f"建议微调系统参数以适应当前意向性")
            if urgency == "high":
                suggestions.append(f"优先调整响应速度相关参数")
            else:
                suggestions.append(f"平衡准确性与响应速度")
        
        elif strategy_type == "strategy_adjustment":
            suggestions.append(f"建议调整处理策略以匹配当前意向性级别")
            if priority == "high":
                suggestions.append(f"采用更积极的处理策略")
            else:
                suggestions.append(f"采用标准处理策略")
        
        elif strategy_type == "priority_reordering":
            suggestions.append(f"建议重新排列任务优先级")
            if strength == "strong":
                suggestions.append(f"立即将相关任务提升到最高优先级")
            elif strength == "medium":
                suggestions.append(f"将相关任务提升到高优先级队列")
            else:
                suggestions.append(f"适当提高相关任务优先级")
        
        return suggestions
    
    def _generate_parameters(self, analysis: Dict[str, Any], strategy_type: str) -> Dict[str, Any]:
        """
        生成参数建议
        
        Args:
            analysis: 分析结果
            strategy_type: 策略类型
            
        Returns:
            参数字典
        """
        intensity = analysis.get("intensity", {}).get("score", 0.5)
        urgency = analysis.get("urgency", {}).get("score", 0.5)
        
        parameters = {}
        
        if strategy_type == "parameter_tuning":
            parameters = {
                "response_weight": min(intensity + 0.1, 1.0),
                "timeout_adjustment": max(1.0 - urgency * 0.3, 0.5),
                "resource_allocation": min(intensity * 1.5, 1.0)
            }
        
        elif strategy_type == "strategy_adjustment":
            parameters = {
                "aggressiveness": min(urgency * 1.2, 1.0),
                "complexity_level": "high" if intensity > 0.7 else "medium",
                "fallback_enabled": True
            }
        
        elif strategy_type == "priority_reordering":
            parameters = {
                "priority_boost": urgency * 100,
                "queue_position": 1 if urgency > 0.7 else 5,
                "preemptible": urgency > 0.8
            }
        
        return parameters
    
    def _generate_expected_outcome(self, strategy_type: str, strength: str) -> str:
        """
        生成期望结果描述
        
        Args:
            strategy_type: 策略类型
            strength: 强度
            
        Returns:
            期望结果描述
        """
        descriptions = {
            "parameter_tuning": "优化系统参数，提升响应适切性",
            "strategy_adjustment": "调整处理策略，匹配当前意向性需求",
            "priority_reordering": "重新排列任务优先级，确保高优先级意向性得到及时处理"
        }
        
        return descriptions.get(strategy_type, "优化系统行为")
    
    def collect_feedback(self, regulation_id: str, outcome: Dict[str, Any]) -> Dict[str, Any]:
        """
        收集反馈
        
        Args:
            regulation_id: 调节建议ID
            outcome: 执行结果
            
        Returns:
            反馈记录
        """
        feedback = {
            "regulation_id": regulation_id,
            "timestamp": datetime.now().isoformat(),
            "outcome": outcome,
            "success": outcome.get("success", False),
            "effectiveness": outcome.get("effectiveness", 0.5)
        }
        
        # 保存反馈到记忆存储
        feedback_file = f"{self.memory_dir}/regulation_feedback.json"
        
        try:
            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            feedbacks = []
        
        feedbacks.append(feedback)
        
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)
        
        return feedback


def main():
    parser = argparse.ArgumentParser(description="意向性调节模块")
    parser.add_argument("--analysis", required=True,
                        help="分析结果文件路径（JSON格式）")
    parser.add_argument("--history",
                        help="历史数据文件路径（JSON格式，可选）")
    parser.add_argument("--output", help="输出文件路径（JSON格式）")
    parser.add_argument("--collect-feedback", 
                        help="收集反馈模式：regulation_id")
    parser.add_argument("--feedback-data",
                        help="反馈数据（JSON格式）")
    parser.add_argument("--memory-dir", default="./agi_memory",
                        help="记忆存储目录")
    
    args = parser.parse_args()
    
    regulator = IntentionalityRegulator(memory_dir=args.memory_dir)
    
    # 收集反馈模式
    if args.collect_feedback:
        feedback_data = json.loads(args.feedback_data) if args.feedback_data else {}
        feedback = regulator.collect_feedback(args.collect_feedback, feedback_data)
        print(json.dumps(feedback, ensure_ascii=False, indent=2))
        return
    
    # 读取输入数据
    with open(args.analysis, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    history = None
    if args.history:
        with open(args.history, 'r', encoding='utf-8') as f:
            history = json.load(f)
    
    # 生成最优解
    optimal_solution = regulator.generate_optimal_solution(analysis, history)
    
    # 生成软调节建议
    regulation = regulator.generate_soft_regulation(analysis, optimal_solution)
    
    # 输出结果
    output_data = json.dumps(regulation, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_data)
    else:
        print(output_data)


if __name__ == "__main__":
    main()
