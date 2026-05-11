#!/usr/bin/env python3
"""
策略选择器（四步纠错法的智能增强）

负责智能决策：
1. 是否需要纠错
2. 选择纠错策略
3. 确定优先级
4. 生成执行建议

特点：
- 基于场景敏感度决策
- 考虑人格偏好
- 避免过度纠错
- 提供可操作的建议
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum


class Strategy(Enum):
    """纠错策略"""
    SKIP = "skip"                 # 跳过纠错
    SOFT = "soft"                 # 软性建议（提示用户验证）
    CORRECT = "correct"           # 直接修正
    RECONSTRUCT = "reconstruct"   # 重构推理链


@dataclass
class StrategyDecision:
    """策略决策"""
    should_correct: bool          # 是否需要纠错
    strategy: Strategy            # 纠错策略
    priority: int                 # 优先级（0-10）
    reason: str                   # 决策理由
    confidence: float             # 决策置信度（0-1）
    suggested_actions: List[str]  # 建议的纠错动作

    def to_dict(self) -> dict:
        result = asdict(self)
        result['strategy'] = self.strategy.value
        return result


class StrategySelector:
    """
    策略选择器
    
    基于客观性标注、场景类型和人格特质，智能决策是否纠错及如何纠错。
    """

    def __init__(self):
        # 场景客观性要求
        self.context_requirements = {
            'scientific': 0.9,
            'legal': 0.85,
            'medical': 0.9,
            'technical': 0.8,
            'general': 0.6,
            'creative': 0.3,
            'emotional': 0.2,
            'artistic': 0.1,
        }

        # 场景类型对应的纠错策略偏好
        self.context_strategy_preference = {
            'scientific': [Strategy.RECONSTRUCT, Strategy.CORRECT],
            'legal': [Strategy.RECONSTRUCT, Strategy.CORRECT],
            'medical': [Strategy.RECONSTRUCT, Strategy.CORRECT],
            'technical': [Strategy.CORRECT, Strategy.SOFT],
            'general': [Strategy.SOFT, Strategy.CORRECT],
            'creative': [Strategy.SKIP, Strategy.SOFT],
            'emotional': [Strategy.SKIP, Strategy.SOFT],
            'artistic': [Strategy.SKIP, Strategy.SOFT],
        }

    def select_strategy(
        self,
        objectivity_metric: Dict,
        context_type: str,
        personality_type: Optional[str] = None,
        learning_stage: Optional[dict] = None
    ) -> StrategyDecision:
        """
        选择纠错策略（四步决策法）
        
        Args:
            objectivity_metric: 客观性标注
            context_type: 场景类型
            personality_type: 人格类型（可选）
            learning_stage: 学习阶段（可选）
        
        Returns:
            StrategyDecision: 策略决策
        """
        # 步骤1：判断是否需要纠错
        should_correct = self._should_correct(objectivity_metric, context_type)
        
        if not should_correct:
            return StrategyDecision(
                should_correct=False,
                strategy=Strategy.SKIP,
                priority=0,
                reason=f"{context_type}场景下，客观性评分{objectivity_metric['objectivity_score']:.2f}符合要求",
                confidence=0.9,
                suggested_actions=[]
            )
        
        # 步骤2：选择纠错策略
        strategy = self._select_correction_strategy(
            objectivity_metric,
            context_type,
            personality_type
        )
        
        # 步骤3：确定优先级
        priority = self._determine_priority(
            objectivity_metric,
            context_type,
            personality_type
        )
        
        # 步骤4：生成建议动作
        suggested_actions = self._generate_suggested_actions(
            strategy,
            objectivity_metric,
            context_type
        )
        
        # 生成决策理由
        reason = self._generate_decision_reason(
            objectivity_metric,
            context_type,
            strategy,
            priority
        )
        
        # 计算置信度
        confidence = self._calculate_confidence(
            objectivity_metric,
            context_type,
            personality_type
        )
        
        return StrategyDecision(
            should_correct=True,
            strategy=strategy,
            priority=priority,
            reason=reason,
            confidence=confidence,
            suggested_actions=suggested_actions
        )

    def _should_correct(self, objectivity_metric: Dict, context_type: str) -> bool:
        """
        步骤1：判断是否需要纠错
        
        基于偏差幅度和场景适切性判断。
        """
        objectivity_score = objectivity_metric['objectivity_score']
        required_objectivity = objectivity_metric['required_objectivity']
        gap = objectivity_metric['gap']
        severity = objectivity_metric['severity']
        
        # 情况1：客观性评分低于要求
        if objectivity_score < required_objectivity:
            # 判断偏差幅度
            if gap > 0.3:  # 大幅偏差
                return True
            elif gap > 0.1:  # 中等偏差
                # 严格场景必须纠错，宽松场景可跳过
                required = self.context_requirements.get(context_type, 0.5)
                if required >= 0.7:  # 严格场景
                    return True
                else:  # 宽松场景
                    return severity in ['severe', 'moderate']
        
        # 情况2：检测到严重主观性特征
        subjectivity_dims = objectivity_metric.get('subjectivity_dimensions', {})
        hallucination_score = subjectivity_dims.get('hallucination', 0.0)
        if hallucination_score > 0.7:  # 严重幻觉倾向
            return True
        
        # 情况3：适度偏差 + 严格场景
        if gap > 0.05 and severity in ['moderate', 'severe']:
            required = self.context_requirements.get(context_type, 0.5)
            if required >= 0.8:  # 极严格场景（scientific, legal, medical）
                return True
        
        # 其他情况：跳过纠错
        return False

    def _select_correction_strategy(
        self,
        objectivity_metric: Dict,
        context_type: str,
        personality_type: Optional[str] = None
    ) -> Strategy:
        """
        步骤2：选择纠错策略
        
        基于错误类型、场景类型和人格偏好选择策略。
        """
        # 获取场景偏好策略
        preferred_strategies = self.context_strategy_preference.get(
            context_type,
            [Strategy.SOFT, Strategy.CORRECT]
        )
        
        # 分析错误类型
        subjectivity_dims = objectivity_metric.get('subjectivity_dimensions', {})
        hallucination_score = subjectivity_dims.get('hallucination', 0.0)
        speculation_score = subjectivity_dims.get('speculation', 0.0)
        severity = objectivity_metric['severity']
        
        # 策略选择逻辑
        if severity == 'severe':
            # 严重错误：重构或直接修正
            if hallucination_score > 0.7:  # 严重幻觉
                return Strategy.RECONSTRUCT
            else:
                return Strategy.CORRECT
        
        elif severity == 'moderate':
            # 中度错误：根据场景偏好
            return preferred_strategies[0]  # 首选策略
        
        else:  # mild
            # 轻微错误：软性建议或跳过
            if context_type in ['creative', 'emotional', 'artistic']:
                return Strategy.SKIP
            else:
                return Strategy.SOFT

    def _determine_priority(
        self,
        objectivity_metric: Dict,
        context_type: str,
        personality_type: Optional[str] = None
    ) -> int:
        """
        步骤3：确定优先级
        
        基于偏差严重度和人格特质确定优先级（0-10）。
        """
        severity = objectivity_metric['severity']
        gap = objectivity_metric['gap']
        subjectivity_dims = objectivity_metric.get('subjectivity_dimensions', {})
        hallucination_score = subjectivity_dims.get('hallucination', 0.0)
        
        # 基准优先级
        priority_map = {
            'none': 0,
            'mild': 3,
            'moderate': 6,
            'severe': 10
        }
        base_priority = priority_map.get(severity, 5)
        
        # 根据偏差幅度调整
        if gap > 0.3:  # 大幅偏差
            base_priority += 2
        elif gap < 0.1:  # 小幅偏差
            base_priority -= 1
        
        # 根据幻觉倾向调整
        if hallucination_score > 0.8:  # 极高幻觉倾向
            base_priority = min(base_priority + 3, 10)
        elif hallucination_score > 0.6:  # 高幻觉倾向
            base_priority = min(base_priority + 2, 10)
        
        # 根据人格调整
        if personality_type:
            # 谨慎型人格：提高优先级
            if '谨慎' in personality_type:
                base_priority = min(base_priority + 2, 10)
            # 激进型人格：降低优先级
            elif '激进' in personality_type:
                base_priority = max(base_priority - 1, 0)
        
        # 限制在0-10范围内
        return max(0, min(10, base_priority))

    def _generate_suggested_actions(
        self,
        strategy: Strategy,
        objectivity_metric: Dict,
        context_type: str
    ) -> List[str]:
        """
        步骤4：生成建议动作
        """
        actions = []
        severity = objectivity_metric['severity']
        subjectivity_dims = objectivity_metric.get('subjectivity_dimensions', {})
        
        if strategy == Strategy.SKIP:
            actions.append("跳过纠错，保持原响应")
            actions.append("建议：在后续交互中注意客观性")
        
        elif strategy == Strategy.SOFT:
            actions.append("在响应末尾添加不确定性声明")
            actions.append("提示用户对关键信息进行验证")
            if subjectivity_dims.get('hallucination', 0.0) > 0.5:
                actions.append("标记可能存在幻觉的内容")
        
        elif strategy == Strategy.CORRECT:
            actions.append("修正主观性表达")
            actions.append("替换模糊词汇为确定性表达")
            if severity in ['moderate', 'severe']:
                actions.append("补充事实依据或数据来源")
        
        elif strategy == Strategy.RECONSTRUCT:
            actions.append("重新评估问题")
            actions.append("重构推理链")
            actions.append("验证所有关键事实")
            if subjectivity_dims.get('hallucination', 0.0) > 0.6:
                actions.append("识别并移除幻觉内容")
            actions.append("重新生成响应")
        
        return actions

    def _generate_decision_reason(
        self,
        objectivity_metric: Dict,
        context_type: str,
        strategy: Strategy,
        priority: int
    ) -> str:
        """生成决策理由"""
        severity = objectivity_metric['severity']
        objectivity_score = objectivity_metric['objectivity_score']
        gap = objectivity_metric['gap']
        
        reason_parts = []
        
        # 描述问题
        if severity == 'severe':
            reason_parts.append(f"检测到严重偏差（客观性评分{objectivity_score:.2f}，差距{gap:.2f}）")
        elif severity == 'moderate':
            reason_parts.append(f"检测到中度偏差（客观性评分{objectivity_score:.2f}，差距{gap:.2f}）")
        else:
            reason_parts.append(f"检测到轻微偏差（客观性评分{objectivity_score:.2f}）")
        
        # 描述场景
        reason_parts.append(f"在{context_type}场景下")
        
        # 描述策略选择
        strategy_names = {
            Strategy.SKIP: "选择跳过纠错",
            Strategy.SOFT: "选择软性建议",
            Strategy.CORRECT: "选择直接修正",
            Strategy.RECONSTRUCT: "选择重构推理链"
        }
        reason_parts.append(strategy_names.get(strategy, "选择纠错"))
        
        # 描述优先级
        if priority >= 8:
            reason_parts.append("（高优先级）")
        elif priority >= 5:
            reason_parts.append("（中优先级）")
        else:
            reason_parts.append("（低优先级）")
        
        return "；".join(reason_parts) + "。"

    def _calculate_confidence(
        self,
        objectivity_metric: Dict,
        context_type: str,
        personality_type: Optional[str] = None
    ) -> float:
        """计算决策置信度"""
        base_confidence = 0.8
        
        # 根据严重程度调整置信度
        severity = objectivity_metric['severity']
        if severity == 'severe':
            base_confidence += 0.1
        elif severity == 'none':
            base_confidence -= 0.1
        
        # 根据场景熟悉度调整
        if context_type in ['general', 'creative', 'emotional']:
            base_confidence -= 0.05
        
        # 限制在0.5-1.0范围内
        return max(0.5, min(1.0, base_confidence))


# 测试代码（当直接运行此文件时执行）
if __name__ == '__main__':
    print("=== 策略选择器（测试模式） ===\n")
    
    selector = StrategySelector()
    
    # 测试1：严重幻觉
    metric1 = {
        'objectivity_score': 0.45,
        'required_objectivity': 0.9,
        'gap': 0.45,
        'severity': 'severe',
        'subjectivity_dimensions': {
            'hallucination': 0.8,
            'speculation': 0.3,
            'assumption': 0.2,
            'emotion': 0.1,
            'preference': 0.1
        }
    }
    
    decision1 = selector.select_strategy(metric1, 'scientific')
    print(f"测试1：严重幻觉（scientific场景）")
    print(f"  应该纠错: {decision1.should_correct}")
    print(f"  策略: {decision1.strategy.value}")
    print(f"  优先级: {decision1.priority}")
    print(f"  理由: {decision1.reason}")
    print()
    
    # 测试2：创意场景的推测性
    metric2 = {
        'objectivity_score': 0.6,
        'required_objectivity': 0.3,
        'gap': -0.3,
        'severity': 'mild',
        'subjectivity_dimensions': {
            'hallucination': 0.1,
            'speculation': 0.5,
            'assumption': 0.3,
            'emotion': 0.2,
            'preference': 0.1
        }
    }
    
    decision2 = selector.select_strategy(metric2, 'creative')
    print(f"测试2：创意场景的推测性")
    print(f"  应该纠错: {decision2.should_correct}")
    print(f"  策略: {decision2.strategy.value}")
    print(f"  优先级: {decision2.priority}")
    print(f"  理由: {decision2.reason}")
    print()
    
    # 测试3：中度逻辑错误
    metric3 = {
        'objectivity_score': 0.65,
        'required_objectivity': 0.8,
        'gap': 0.15,
        'severity': 'moderate',
        'subjectivity_dimensions': {
            'hallucination': 0.2,
            'speculation': 0.4,
            'assumption': 0.5,
            'emotion': 0.1,
            'preference': 0.1
        }
    }
    
    decision3 = selector.select_strategy(metric3, 'technical')
    print(f"测试3：中度逻辑错误（technical场景）")
    print(f"  应该纠错: {decision3.should_correct}")
    print(f"  策略: {decision3.strategy.value}")
    print(f"  优先级: {decision3.priority}")
    print(f"  理由: {decision3.reason}")
    print()
    
    print("=== 所有测试完成 ===")
