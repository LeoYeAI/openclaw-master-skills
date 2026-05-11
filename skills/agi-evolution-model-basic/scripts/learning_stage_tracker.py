#!/usr/bin/env python3
"""
学习阶段追踪器

追踪智能体在不同场景下的学习阶段，支持学习阶段调整。

学习阶段划分：
- 学习初期（< 50次交互）
- 成长期（50-200次）
- 精通期（200-500次）
- 专家期（> 500次）

特点：
- 基于成功率和交互次数判断学习阶段
- 支持多场景独立追踪
- 提供学习阶段更新接口
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class LearningStage:
    """学习阶段"""
    stage: str           # 学习阶段
    total_interactions: int
    success_count: int
    success_rate: float
    last_updated: str

    def to_dict(self) -> dict:
        return asdict(self)


class LearningStageTracker:
    """
    学习阶段追踪器
    
    追踪智能体在不同场景下的学习阶段。
    """

    def __init__(self, base_dir: str = "./agi_memory"):
        self.base_dir = base_dir
        self.learning_stage_file = os.path.join(base_dir, "learning_stages.json")
        
        # 学习阶段数据
        self._learning_stages: Dict[str, LearningStage] = {}
        
        # 加载现有数据
        self._load()

    def get_learning_stage(self, context_type: str) -> LearningStage:
        """
        获取指定场景的学习阶段
        
        Args:
            context_type: 场景类型
        
        Returns:
            学习阶段
        """
        if context_type not in self._learning_stages:
            # 初始化学习阶段
            self._learning_stages[context_type] = LearningStage(
                stage="learning_early",
                total_interactions=0,
                success_count=0,
                success_rate=0.0,
                last_updated=datetime.now().isoformat()
            )
        
        return self._learning_stages[context_type]

    def update_learning_stage(
        self,
        context_type: str,
        success: bool,
        time_cost: float = 0.0
    ):
        """
        更新学习阶段
        
        Args:
            context_type: 场景类型
            success: 是否成功
            time_cost: 耗时（秒）
        """
        # 获取当前学习阶段
        current_stage = self.get_learning_stage(context_type)
        
        # 更新交互次数
        current_stage.total_interactions += 1
        
        # 更新成功次数
        if success:
            current_stage.success_count += 1
        
        # 计算成功率
        current_stage.success_rate = (
            current_stage.success_count / current_stage.total_interactions
        )
        
        # 判断学习阶段
        total_interactions = current_stage.total_interactions
        success_rate = current_stage.success_rate
        
        if total_interactions < 50:
            new_stage = "learning_early"
        elif total_interactions < 200:
            new_stage = "growth"
        elif total_interactions < 500:
            new_stage = "mastery"
        else:
            new_stage = "expert"
        
        current_stage.stage = new_stage
        current_stage.last_updated = datetime.now().isoformat()
        
        # 保存
        self._save()

    def _determine_stage(
        self,
        total_interactions: int,
        success_rate: float
    ) -> str:
        """
        判断学习阶段
        
        Args:
            total_interactions: 总交互次数
            success_rate: 成功率
        
        Returns:
            学习阶段
        """
        if total_interactions < 50:
            return "learning_early"
        elif total_interactions < 200:
            return "growth"
        elif total_interactions < 500:
            return "mastery"
        else:
            return "expert"

    def get_stage_adjustment_coefficient(
        self,
        context_type: str
    ) -> float:
        """
        获取学习阶段调整系数
        
        Args:
            context_type: 场景类型
        
        Returns:
            调整系数（0.9 - 1.1）
        """
        stage = self.get_learning_stage(context_type)
        
        # 基于学习阶段返回调整系数
        stage_coefficients = {
            "learning_early": 0.95,  # 学习初期：更谨慎
            "growth": 0.98,           # 成长期：适度谨慎
            "mastery": 1.0,          # 精通期：基准
            "expert": 1.05           # 专家期：适度宽松
        }
        
        return stage_coefficients.get(stage.stage, 1.0)

    def get_all_stages(self) -> Dict[str, LearningStage]:
        """
        获取所有场景的学习阶段
        
        Returns:
            所有学习阶段
        """
        return self._learning_stages.copy()

    def _load(self):
        """加载数据"""
        if os.path.exists(self.learning_stage_file):
            try:
                with open(self.learning_stage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for context_type, stage_data in data.items():
                    self._learning_stages[context_type] = LearningStage(**stage_data)
            except Exception as e:
                print(f"⚠️ 加载学习阶段数据失败: {e}")

    def _save(self):
        """保存数据"""
        try:
            os.makedirs(os.path.dirname(self.learning_stage_file), exist_ok=True)
            
            data = {
                context_type: stage.to_dict()
                for context_type, stage in self._learning_stages.items()
            }
            
            with open(self.learning_stage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存学习阶段数据失败: {e}")

    def reset(self, context_type: Optional[str] = None):
        """
        重置学习阶段
        
        Args:
            context_type: 场景类型（None表示重置所有）
        """
        if context_type:
            if context_type in self._learning_stages:
                del self._learning_stages[context_type]
        else:
            self._learning_stages.clear()
        
        self._save()


# 测试代码
if __name__ == '__main__':
    print("=== 学习阶段追踪器（测试模式） ===\n")
    
    tracker = LearningStageTracker("./test_learning_stages")
    
    # 测试1：更新学习阶段
    print("测试1：更新学习阶段")
    for i in range(10):
        tracker.update_learning_stage('scientific', success=(i % 3 != 0))
    
    stage = tracker.get_learning_stage('scientific')
    print(f"  学习阶段: {stage.stage}")
    print(f"  总交互次数: {stage.total_interactions}")
    print(f"  成功次数: {stage.success_count}")
    print(f"  成功率: {stage.success_rate:.2f}")
    print(f"  调整系数: {tracker.get_stage_adjustment_coefficient('scientific'):.3f}")
    print()
    
    # 测试2：多场景追踪
    print("测试2：多场景追踪")
    contexts = ['scientific', 'creative', 'technical', 'general']
    for context in contexts:
        tracker.update_learning_stage(context, success=True)
    
    all_stages = tracker.get_all_stages()
    for context, stage in all_stages.items():
        print(f"  {context}:")
        print(f"    阶段: {stage.stage}")
        print(f"    交互次数: {stage.total_interactions}")
        print(f"    成功率: {stage.success_rate:.2f}")
    print()
    
    # 测试3：学习阶段判断
    print("测试3：学习阶段判断")
    test_cases = [
        (30, 0.7, "learning_early"),
        (100, 0.8, "growth"),
        (300, 0.85, "mastery"),
        (600, 0.9, "expert")
    ]
    
    for interactions, success_rate, expected_stage in test_cases:
        actual_stage = tracker._determine_stage(interactions, success_rate)
        print(f"  交互次数={interactions}, 成功率={success_rate:.2f} → {actual_stage} (期望: {expected_stage})")
    print()
    
    print("=== 测试完成 ===")
