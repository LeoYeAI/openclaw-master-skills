"""
Agent Memory System - 冷热度管理器

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证
- 标准配置文件:
  ```text
  # requirements.txt
  pydantic>=2.0.0
  ```
=== 声明结束 ===

安全提醒：定期运行 pip audit 进行安全审计
"""

from __future__ import annotations

from typing import Any

from .types import HeatLevel


class HeatManager:
    """
    记忆冷热度管理器

    负责计算和管理记忆的热度分数，决定记忆在热/温/冷层之间的迁移
    """

    def __init__(self) -> None:
        """初始化冷热度管理器"""
        # 热度计算权重
        self._recency_weight: float = 0.35
        self._frequency_weight: float = 0.30
        self._importance_weight: float = 0.20
        self._user_interaction_weight: float = 0.15

        # 热度阈值
        self._hot_threshold: float = 70.0
        self._warm_threshold: float = 30.0

        # 时间衰减因子
        self._decay_factor: float = 0.95

    def calculate_heat_score(
        self,
        days_since_access: float,
        access_count: int,
        importance: float,
        user_interaction: float,
    ) -> float:
        """
        计算热度分数

        Args:
            days_since_access: 距上次访问的天数
            access_count: 访问次数
            importance: 重要性分数 (0-100)
            user_interaction: 用户交互分数 (0-100)

        Returns:
            热度分数 (0-100)
        """
        # 时间衰减因子
        recency_score: float = 100.0 * (self._decay_factor**days_since_access)

        # 访问频率因子
        frequency_score: float = min(100.0, float(access_count) * 5.0)

        # 综合计算
        heat_score: float = (
            recency_score * self._recency_weight
            + frequency_score * self._frequency_weight
            + importance * self._importance_weight
            + user_interaction * self._user_interaction_weight
        )

        return max(0.0, min(100.0, heat_score))

    def determine_level(self, heat_score: float) -> HeatLevel:
        """
        确定记忆层级

        Args:
            heat_score: 热度分数

        Returns:
            热度层级
        """
        if heat_score >= self._hot_threshold:
            return HeatLevel.HOT
        elif heat_score >= self._warm_threshold:
            return HeatLevel.WARM
        else:
            return HeatLevel.COLD

    def get_layer_config(self, level: HeatLevel) -> dict[str, Any]:
        """
        获取层级配置

        Args:
            level: 热度层级

        Returns:
            层级配置信息
        """
        configs: dict[HeatLevel, dict[str, Any]] = {
            HeatLevel.HOT: {
                "storage": "内存 LRU 缓存",
                "max_capacity": 100,
                "access_latency_ms": 5,
                "description": "当前会话相关、核心画像",
            },
            HeatLevel.WARM: {
                "storage": "Redis 缓存",
                "max_capacity": 1000,
                "access_latency_ms": 20,
                "description": "近期记忆、频繁访问",
            },
            HeatLevel.COLD: {
                "storage": "数据库/对象存储",
                "max_capacity": -1,  # 无限制
                "access_latency_ms": 100,
                "description": "归档记忆、历史记录",
            },
        }
        return configs.get(level, configs[HeatLevel.WARM])

    def should_migrate(
        self, current_level: HeatLevel, new_level: HeatLevel
    ) -> bool:
        """
        判断是否需要迁移

        Args:
            current_level: 当前层级
            new_level: 新层级

        Returns:
            是否需要迁移
        """
        return current_level != new_level

    def calculate_access_boost(self, interaction_type: str) -> float:
        """
        计算访问时的热度提升

        Args:
            interaction_type: 交互类型

        Returns:
            热度提升值
        """
        boosts: dict[str, float] = {
            "read": 0.0,
            "activated": 5.0,
            "used_in_response": 10.0,
            "user_referenced": 20.0,
            "user_marked_important": 30.0,
            "user_deleted": -40.0,
        }
        return boosts.get(interaction_type, 0.0)

    def get_decay_factor(self, memory_type: str) -> float:
        """
        获取不同记忆类型的衰减因子

        Args:
            memory_type: 记忆类型

        Returns:
            衰减因子
        """
        # 不同记忆类型有不同的衰减速度
        decay_factors: dict[str, float] = {
            "user_profile": 0.99,  # 用户画像衰减慢
            "procedural": 0.97,  # 程序性记忆
            "narrative": 0.95,  # 叙事记忆
            "semantic": 0.96,  # 语义记忆
            "emotional": 0.98,  # 情感记忆衰减快（时间衰减）
        }
        return decay_factors.get(memory_type, self._decay_factor)


# ============================================================================
# 导出
# ============================================================================

__all__ = ["HeatManager"]
