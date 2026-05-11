#!/usr/bin/env python3
"""
意向性驱动的触发判断模块

功能：
- 自主判断是否需要生成软调节建议
- 基于5个触发条件进行判断
- 支持动态阈值调整
- 支持人格化触发

设计原则：
- 自主运行，不依赖主循环触发
- 基于意向性累积、突变、偏离等触发
- 支持超然性检查（不破坏独立性）
- 可配置的触发阈值

触发条件：
1. 意向性累积阈值突破
2. 意向性模式突变
3. 意向性与主循环状态偏离
4. 时间窗口触发
5. 人格进化需求
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict


class IntentionalityTrigger:
    """意向性驱动的触发判断器"""
    
    def __init__(self, memory_dir: str = "./agi_memory"):
        self.memory_dir = memory_dir
        
        # 触发阈值配置
        self.thresholds = {
            # 条件1：意向性累积阈值
            "cumulative": {
                "perception": 15,
                "belief": 10,
                "desire": 8,
                "rising_intensity_count": 3
            },
            
            # 条件2：意向性模式突变
            "pattern_mutation_threshold": 0.7,  # 模式距离阈值
            "min_history_window": 5,  # 最小历史窗口
            
            # 条件3：意向性与主循环状态偏离
            "deviation": 0.6,  # 综合偏离阈值
            
            # 条件4：时间窗口触发
            "periodic_interval": 10,  # 每N次交互
            "max_idle_time": 300,  # 最大空闲时间（秒）
            
            # 条件5：人格进化需求
            "adoption_rate_threshold": 0.8,  # 采纳率阈值
            "maslow_satisfaction_threshold": 0.9  # 马斯洛需求满足度阈值
        }
        
        # 上次触发时间
        self.last_trigger_time = None
        
        # 交互计数
        self.interaction_count = 0
    
    def check_trigger(self, intentionality: Dict[str, Any],
                      history: List[Dict[str, Any]],
                      main_loop_state: Dict[str, Any] = None,
                      personality: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        检查是否需要触发软调节建议生成
        
        Args:
            intentionality: 当前意向性数据
            history: 意向性历史数据
            main_loop_state: 主循环状态（可选）
            personality: 人格数据（可选）
            
        Returns:
            (是否触发, 触发详情)
        """
        trigger_results = []
        
        # 条件1：意向性累积阈值突破
        triggered1, detail1 = self.check_cumulative_threshold(history)
        if triggered1:
            trigger_results.append({
                "condition": "cumulative_threshold",
                "priority": "high",
                "detail": detail1
            })
        
        # 条件2：意向性模式突变
        triggered2, detail2 = self.check_pattern_mutation(intentionality, history)
        if triggered2:
            trigger_results.append({
                "condition": "pattern_mutation",
                "priority": "high",
                "detail": detail2
            })
        
        # 条件3：意向性与主循环状态偏离
        if main_loop_state:
            triggered3, detail3 = self.check_deviation_from_main_loop(
                intentionality, main_loop_state
            )
            if triggered3:
                trigger_results.append({
                    "condition": "main_loop_deviation",
                    "priority": "medium",
                    "detail": detail3
                })
        
        # 条件4：时间窗口触发
        triggered4, detail4 = self.check_time_window_trigger()
        if triggered4:
            trigger_results.append({
                "condition": "time_window",
                "priority": "low",
                "detail": detail4
            })
        
        # 条件5：人格进化需求
        if personality:
            triggered5, detail5 = self.check_personality_evolution_need(personality)
            if triggered5:
                trigger_results.append({
                    "condition": "personality_evolution",
                    "priority": "medium",
                    "detail": detail5
                })
        
        # 如果没有任何触发条件满足
        if not trigger_results:
            return False, {"reason": "no_trigger_condition_met"}
        
        # 基于人格特质调整触发置信度
        confidence = self._calculate_confidence(trigger_results, personality)
        
        # 超然性检查：确保触发不破坏独立性
        passed_transcendence = self._check_transcendence(trigger_results)
        
        if not passed_transcendence:
            return False, {
                "reason": "transcendence_check_failed",
                "trigger_results": trigger_results
            }
        
        # 更新触发时间
        self.last_trigger_time = datetime.now()
        
        return True, {
            "trigger_time": self.last_trigger_time.isoformat(),
            "trigger_count": len(trigger_results),
            "triggers": trigger_results,
            "confidence": confidence,
            "passed_transcendence": passed_transcendence
        }
    
    def check_cumulative_threshold(self, history: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any]]:
        """
        检测意向性累积阈值
        
        Args:
            history: 意向性历史数据
            
        Returns:
            (是否触发, 详情)
        """
        if len(history) < 3:
            return False, {"reason": "insufficient_history"}
        
        # 1. 按类型统计
        type_counts = defaultdict(int)
        for item in history:
            classification = item.get("classification", {})
            content = classification.get("content", "unknown")
            type_counts[content] += 1
        
        # 2. 检测阈值突破
        triggered = False
        triggered_types = []
        
        for type_name, count in type_counts.items():
            threshold = self.thresholds["cumulative"].get(type_name, 10)
            if count >= threshold:
                triggered = True
                triggered_types.append(type_name)
        
        # 3. 检测强度趋势
        intensity_trend = self._analyze_intensity_trend(history[-5:])
        if intensity_trend == "rising" and len(history) >= 3:
            triggered = True
        
        return triggered, {
            "type_counts": dict(type_counts),
            "triggered_types": triggered_types,
            "intensity_trend": intensity_trend
        }
    
    def check_pattern_mutation(self, current_intentionality: Dict[str, Any],
                                history_window: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any]]:
        """
        检测意向性模式突变
        
        Args:
            current_intentionality: 当前意向性
            history_window: 历史窗口数据
            
        Returns:
            (是否触发, 详情)
        """
        if len(history_window) < self.thresholds["min_history_window"]:
            return False, {"reason": "insufficient_history_window"}
        
        # 1. 获取历史模式
        historical_pattern = self._extract_pattern(history_window)
        
        # 2. 获取当前模式
        current_pattern = self._extract_pattern([current_intentionality])
        
        # 3. 计算模式距离
        pattern_distance = self._calculate_pattern_distance(
            historical_pattern,
            current_pattern
        )
        
        # 4. 判断是否突变
        triggered = pattern_distance > self.thresholds["pattern_mutation_threshold"]
        
        return triggered, {
            "historical_pattern": historical_pattern,
            "current_pattern": current_pattern,
            "pattern_distance": pattern_distance
        }
    
    def check_deviation_from_main_loop(self, intentionality: Dict[str, Any],
                                        main_loop_state: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        检测意向性与主循环状态的偏离
        
        Args:
            intentionality: 意向性数据
            main_loop_state: 主循环状态
            
        Returns:
            (是否触发, 详情)
        """
        # 1. 提取用户意向性期望
        user_expectation = self._extract_user_expectation(intentionality)
        
        # 2. 提取主循环实际响应
        actual_response = self._extract_main_loop_response(main_loop_state)
        
        # 3. 计算偏离度
        deviation_metrics = {
            "intensity_match": self._compare_intensity(
                user_expectation.get("intensity", 0.5),
                actual_response.get("intensity", 0.5)
            ),
            "type_match": self._compare_type(
                user_expectation.get("type", "unknown"),
                actual_response.get("type", "unknown")
            ),
            "direction_match": self._compare_direction(
                user_expectation.get("direction", "unknown"),
                actual_response.get("direction", "unknown")
            )
        }
        
        # 4. 判断是否偏离
        overall_deviation = sum(deviation_metrics.values()) / len(deviation_metrics)
        triggered = overall_deviation > self.thresholds["deviation"]
        
        return triggered, {
            "deviation_metrics": deviation_metrics,
            "overall_deviation": overall_deviation
        }
    
    def check_time_window_trigger(self) -> Tuple[bool, Dict[str, Any]]:
        """
        检测时间窗口触发条件
        
        Returns:
            (是否触发, 详情)
        """
        triggered = False
        trigger_reason = None
        
        # 1. 定期触发
        self.interaction_count += 1
        if self.interaction_count % self.thresholds["periodic_interval"] == 0:
            triggered = True
            trigger_reason = f"periodic_trigger_every_{self.thresholds['periodic_interval']}_interactions"
        
        # 2. 时间点触发（空闲超时）
        if self.last_trigger_time:
            time_since_last_trigger = (datetime.now() - self.last_trigger_time).total_seconds()
            if time_since_last_trigger > self.thresholds["max_idle_time"]:
                triggered = True
                trigger_reason = f"idle_timeout_{int(time_since_last_trigger)}_seconds"
        
        return triggered, {"reason": trigger_reason}
    
    def check_personality_evolution_need(self, personality: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        检测人格进化需求
        
        Args:
            personality: 人格数据
            
        Returns:
            (是否触发, 详情)
        """
        # 简化实现：基于人格特质判断
        # 实际应该基于采纳历史数据
        
        triggered = False
        adjustment_dimensions = []
        
        # 检测谨慎性（如果谨慎性过高，可能需要降低）
        conscientiousness = personality.get("conscientiousness", 0.5)
        if conscientiousness > 0.8:
            triggered = True
            adjustment_dimensions.append("conscientiousness")
        
        # 检测马斯洛需求层次
        maslow_weights = personality.get("maslow_weights", {})
        if maslow_weights:
            # 如果当前层需求满足度高，可能需要提升层次
            satisfaction = 0.95  # 简化实现
            if satisfaction > self.thresholds["maslow_satisfaction_threshold"]:
                triggered = True
        
        return triggered, {
            "adjustment_dimensions": adjustment_dimensions,
            "maslow_promotion_needed": True
        }
    
    def _calculate_confidence(self, trigger_results: List[Dict[str, Any]],
                               personality: Dict[str, Any] = None) -> float:
        """
        计算触发置信度
        
        Args:
            trigger_results: 触发结果列表
            personality: 人格数据
            
        Returns:
            置信度（0.0-1.0）
        """
        if not trigger_results:
            return 0.0
        
        # 基于触发条件的优先级计算基础置信度
        priority_weights = {
            "high": 0.9,
            "medium": 0.6,
            "low": 0.3
        }
        
        base_confidence = sum(
            priority_weights.get(result.get("priority", "medium"), 0.5)
            for result in trigger_results
        ) / len(trigger_results)
        
        # 基于人格特质调整
        if personality:
            # 谨慎性越高，置信度要求越高
            conscientiousness = personality.get("conscientiousness", 0.5)
            confidence = base_confidence * (1 - conscientiousness * 0.3)
        else:
            confidence = base_confidence
        
        return min(max(confidence, 0.0), 1.0)
    
    def _check_transcendence(self, trigger_results: List[Dict[str, Any]]) -> bool:
        """
        超然性检查：确保触发不破坏独立性
        
        Args:
            trigger_results: 触发结果列表
            
        Returns:
            是否通过超然性检查
        """
        # 简化实现：检查是否有"强制执行"类型的触发
        for result in trigger_results:
            condition = result.get("condition", "")
            if "force" in condition or "mandatory" in condition:
                return False
        
        return True
    
    def _analyze_intensity_trend(self, recent_history: List[Dict[str, Any]]) -> str:
        """
        分析强度趋势
        
        Args:
            recent_history: 最近的历史数据
            
        Returns:
            趋势：rising/falling/stable
        """
        if len(recent_history) < 2:
            return "stable"
        
        intensities = []
        for item in recent_history:
            analysis = item.get("analysis", {})
            intensity = analysis.get("intensity", {}).get("score", 0.5)
            intensities.append(intensity)
        
        # 简化的趋势判断
        if len(intensities) >= 2:
            if all(intensities[i] < intensities[i+1] for i in range(len(intensities)-1)):
                return "rising"
            elif all(intensities[i] > intensities[i+1] for i in range(len(intensities)-1)):
                return "falling"
        
        return "stable"
    
    def _extract_pattern(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        提取意向性模式
        
        Args:
            data: 意向性数据列表
            
        Returns:
            模式字典
        """
        if not data:
            return {}
        
        # 统计各维度的分布
        agent_dist = defaultdict(int)
        direction_dist = defaultdict(int)
        content_dist = defaultdict(int)
        
        for item in data:
            classification = item.get("classification", {})
            
            agent = classification.get("agent", "unknown")
            direction = classification.get("direction", "unknown")
            content = classification.get("content", "unknown")
            
            agent_dist[agent] += 1
            direction_dist[direction] += 1
            content_dist[content] += 1
        
        total = len(data)
        
        return {
            "agent_distribution": {
                k: v/total for k, v in agent_dist.items()
            },
            "direction_distribution": {
                k: v/total for k, v in direction_dist.items()
            },
            "content_distribution": {
                k: v/total for k, v in content_dist.items()
            }
        }
    
    def _calculate_pattern_distance(self, pattern1: Dict[str, Any],
                                     pattern2: Dict[str, Any]) -> float:
        """
        计算模式距离
        
        Args:
            pattern1: 模式1
            pattern2: 模式2
            
        Returns:
            模式距离（0.0-1.0）
        """
        if not pattern1 or not pattern2:
            return 0.0
        
        total_distance = 0.0
        dimension_count = 0
        
        for dimension in ["agent_distribution", "direction_distribution", "content_distribution"]:
            dist1 = pattern1.get(dimension, {})
            dist2 = pattern2.get(dimension, {})
            
            # 计算该维度的距离
            all_keys = set(dist1.keys()) | set(dist2.keys())
            dim_distance = 0.0
            
            for key in all_keys:
                value1 = dist1.get(key, 0.0)
                value2 = dist2.get(key, 0.0)
                dim_distance += abs(value1 - value2)
            
            dim_distance /= max(len(all_keys), 1)
            total_distance += dim_distance
            dimension_count += 1
        
        return total_distance / max(dimension_count, 1)
    
    def _extract_user_expectation(self, intentionality: Dict[str, Any]) -> Dict[str, Any]:
        """提取用户意向性期望"""
        analysis = intentionality.get("analysis", {})
        return {
            "intensity": analysis.get("intensity", {}).get("score", 0.5),
            "type": intentionality.get("classification", {}).get("content", "unknown"),
            "direction": intentionality.get("classification", {}).get("direction", "unknown")
        }
    
    def _extract_main_loop_response(self, main_loop_state: Dict[str, Any]) -> Dict[str, Any]:
        """提取主循环实际响应"""
        return {
            "intensity": main_loop_state.get("intensity", 0.5),
            "type": main_loop_state.get("type", "unknown"),
            "direction": main_loop_state.get("direction", "unknown")
        }
    
    def _compare_intensity(self, intensity1: float, intensity2: float) -> float:
        """比较强度"""
        return 1.0 - abs(intensity1 - intensity2)
    
    def _compare_type(self, type1: str, type2: str) -> float:
        """比较类型"""
        return 1.0 if type1 == type2 else 0.0
    
    def _compare_direction(self, direction1: str, direction2: str) -> float:
        """比较方向"""
        return 1.0 if direction1 == direction2 else 0.0


def main():
    parser = argparse.ArgumentParser(description="意向性驱动的触发判断模块")
    parser.add_argument("--memory-dir", default="./agi_memory", help="记忆目录")
    parser.add_argument("--intentionality", help="当前意向性数据（JSON）")
    parser.add_argument("--history", help="意向性历史数据（JSON文件）")
    parser.add_argument("--main-loop-state", help="主循环状态（JSON）")
    parser.add_argument("--personality", help="人格数据（JSON文件）")
    parser.add_argument("--output", help="输出文件")
    
    args = parser.parse_args()
    
    # 创建触发器
    trigger = IntentionalityTrigger(memory_dir=args.memory_dir)
    
    # 加载数据
    intentionality = json.loads(args.intentionality) if args.intentionality else {}
    
    history = []
    if args.history:
        with open(args.history, 'r', encoding='utf-8') as f:
            history = json.load(f)
    
    main_loop_state = json.loads(args.main_loop_state) if args.main_loop_state else None
    
    personality = None
    if args.personality:
        with open(args.personality, 'r', encoding='utf-8') as f:
            personality = json.load(f)
    
    # 检查触发
    triggered, detail = trigger.check_trigger(
        intentionality,
        history,
        main_loop_state,
        personality
    )
    
    # 输出结果
    result = {
        "triggered": triggered,
        "detail": detail,
        "timestamp": datetime.now().isoformat()
    }
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    sys.exit(0 if not triggered else 1)


if __name__ == "__main__":
    main()
