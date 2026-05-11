#!/usr/bin/env python3
"""
元认知增强集成测试

测试场景敏感度增强和策略选择优化的集成效果。
"""

import sys
import os

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from objectivity_evaluator import ObjectivityEvaluator, ObjectivityMetric
from personality_layer_pure import PersonalityLayer, Personality, PersonalityType
from strategy_selector import StrategySelector, Strategy


def test_dynamic_requirement():
    """测试动态客观性要求"""
    print("=== 测试1：动态客观性要求 ===\n")
    
    evaluator = ObjectivityEvaluator()
    personality_layer = PersonalityLayer()
    
    # 初始化人格
    personality = personality_layer.init_from_preset(
        preset_type=PersonalityType.CAUTIOUS_EXPLORER,
        nickname="测试AI"
    )
    
    # 测试不同场景的动态要求
    scenarios = ['scientific', 'creative', 'medical', 'general']
    
    for scenario in scenarios:
        base_requirement = evaluator.context_requirements.get(scenario, 0.5)
        dynamic_requirement = evaluator.calculate_dynamic_requirement(
            context_type=scenario,
            personality=personality
        )
        
        adjustment_ratio = dynamic_requirement / base_requirement if base_requirement > 0 else 1.0
        
        print(f"场景: {scenario}")
        print(f"  基础要求: {base_requirement:.3f}")
        print(f"  动态要求: {dynamic_requirement:.3f}")
        print(f"  人格调整系数: {adjustment_ratio:.3f}")
        print()
    
    # 测试不同人格类型的影响
    print("人格类型对比（scientific场景）:")
    print()
    
    personality_types = [
        PersonalityType.CAUTIOUS_EXPLORER,
        PersonalityType.RADICAL_INNOVATOR,
        PersonalityType.BALANCED_STABLE
    ]
    base_requirement = evaluator.context_requirements.get('scientific', 0.5)
    
    for ptype in personality_types:
        personality = personality_layer.init_from_preset(
            preset_type=ptype,
            nickname="测试AI"
        )
        
        dynamic_requirement = evaluator.calculate_dynamic_requirement(
            context_type='scientific',
            personality=personality
        )
        
        adjustment_ratio = dynamic_requirement / base_requirement if base_requirement > 0 else 1.0
        
        print(f"  {ptype}:")
        print(f"    动态要求: {dynamic_requirement:.3f}")
        print(f"    调整系数: {adjustment_ratio:.3f}")
    
    print("\n✅ 测试通过\n")


def test_strategy_selection():
    """测试策略选择"""
    print("=== 测试2：策略选择 ===\n")
    
    selector = StrategySelector()
    
    # 测试1：严重偏差
    metric_severe = {
        'objectivity_score': 0.5,
        'required_objectivity': 0.9,
        'gap': 0.4,
        'severity': 'severe',
        'subjectivity_dimensions': {
            'hallucination': 0.8,
            'speculation': 0.3,
            'assumption': 0.2,
            'emotion': 0.1,
            'preference': 0.1
        }
    }
    
    decision_severe = selector.select_strategy(metric_severe, 'scientific')
    print(f"场景1：严重偏差（scientific）")
    print(f"  应该纠错: {decision_severe.should_correct}")
    print(f"  策略: {decision_severe.strategy.value}")
    print(f"  优先级: {decision_severe.priority}")
    print(f"  理由: {decision_severe.reason}")
    print()
    
    # 测试2：创意场景的轻微偏差
    metric_creative = {
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
    
    decision_creative = selector.select_strategy(metric_creative, 'creative')
    print(f"场景2：创意场景的轻微偏差")
    print(f"  应该纠错: {decision_creative.should_correct}")
    print(f"  策略: {decision_creative.strategy.value}")
    print(f"  优先级: {decision_creative.priority}")
    print(f"  理由: {decision_creative.reason}")
    print()
    
    # 测试3：技术场景的中度偏差
    metric_technical = {
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
    
    decision_technical = selector.select_strategy(metric_technical, 'technical')
    print(f"场景3：技术场景的中度偏差")
    print(f"  应该纠错: {decision_technical.should_correct}")
    print(f"  策略: {decision_technical.strategy.value}")
    print(f"  优先级: {decision_technical.priority}")
    print(f"  理由: {decision_technical.reason}")
    print()
    
    # 测试4：人格影响
    decision_caution = selector.select_strategy(metric_technical, 'technical', personality_type="谨慎探索型")
    decision_radical = selector.select_strategy(metric_technical, 'technical', personality_type="激进创新型")
    
    print("人格影响对比（technical场景，中度偏差）:")
    print(f"  谨慎探索型: 优先级={decision_caution.priority}")
    print(f"  激进创新型: 优先级={decision_radical.priority}")
    print()
    
    print("✅ 测试通过\n")


def test_integration():
    """测试完整集成"""
    print("=== 测试3：完整集成 ===\n")
    
    evaluator = ObjectivityEvaluator()
    selector = StrategySelector()
    personality_layer = PersonalityLayer()
    
    # 初始化人格
    personality = personality_layer.init_from_preset(
        preset_type=PersonalityType.CAUTIOUS_EXPLORER,
        nickname="集成测试AI"
    )
    
    # 学习阶段
    learning_stage = {
        'total_interactions': 150,
        'success_rate': 0.75
    }
    
    # 测试响应
    test_response = "根据我的推测，这个方案可能有效。我觉得这是一个很好的想法。"
    
    # 评估客观性（使用动态要求）
    metric = evaluator.evaluate(
        response=test_response,
        context_type='scientific',
        personality=personality,
        learning_stage=learning_stage
    )
    
    print(f"客观性评估:")
    print(f"  客观性评分: {metric.objectivity_score:.3f}")
    print(f"  动态要求: {metric.required_objectivity:.3f}")
    print(f"  适切性: {metric.is_appropriate}")
    print(f"  严重程度: {metric.severity}")
    print(f"  主观性维度:")
    for dim, value in metric.subjectivity_dimensions.items():
        print(f"    {dim}: {value:.3f}")
    print()
    
    # 策略选择
    decision = selector.select_strategy(
        objectivity_metric=metric.to_dict(),
        context_type='scientific',
        personality_type=personality.preset_name,
        learning_stage=learning_stage
    )
    
    print(f"策略决策:")
    print(f"  是否纠错: {decision.should_correct}")
    print(f"  策略: {decision.strategy.value}")
    print(f"  优先级: {decision.priority}")
    print(f"  置信度: {decision.confidence:.3f}")
    print(f"  理由: {decision.reason}")
    print(f"  建议动作:")
    for i, action in enumerate(decision.suggested_actions, 1):
        print(f"    {i}. {action}")
    print()
    
    print("✅ 测试通过\n")


def test_backward_compatibility():
    """测试向后兼容性"""
    print("=== 测试4：向后兼容性 ===\n")
    
    evaluator = ObjectivityEvaluator()
    selector = StrategySelector()
    
    # 不传入 personality 和 learning_stage，应该使用原有逻辑
    metric = evaluator.evaluate(
        response="这是一个测试响应。",
        context_type='general'
    )
    
    print(f"不传人格参数的评估:")
    print(f"  客观性评分: {metric.objectivity_score:.3f}")
    print(f"  场景要求: {metric.required_objectivity:.3f}")
    print(f"  适切性: {metric.is_appropriate}")
    print()
    
    # 策略选择也不传人格参数
    decision = selector.select_strategy(
        objectivity_metric=metric.to_dict(),
        context_type='general'
    )
    
    print(f"不传人格参数的策略选择:")
    print(f"  是否纠错: {decision.should_correct}")
    print(f"  策略: {decision.strategy.value}")
    print(f"  优先级: {decision.priority}")
    print()
    
    print("✅ 向后兼容性测试通过\n")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("元认知增强集成测试套件")
    print("=" * 60)
    print()
    
    tests = [
        ("动态客观性要求", test_dynamic_requirement),
        ("策略选择", test_strategy_selection),
        ("完整集成", test_integration),
        ("向后兼容性", test_backward_compatibility),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {test_name}")
            print(f"错误: {e}")
            print()
            failed += 1
    
    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print(f"\n❌ 有 {failed} 个测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
