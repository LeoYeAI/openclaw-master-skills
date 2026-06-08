"""
Agent Memory System - 长期记忆模块

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证
  * typing-extensions: >=4.0.0
    - 用途：类型扩展支持
- 标准配置文件:
  ```text
  # requirements.txt
  pydantic>=2.0.0
  typing-extensions>=4.0.0
  ```
=== 声明结束 ===

安全提醒：定期运行 pip audit 进行安全审计
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from .types import (
    LongTermMemoryContainer,
    UserProfileMemory,
    UserProfileData,
    ProceduralMemory,
    ProceduralMemoryData,
    NarrativeMemory,
    NarrativeMemoryData,
    SemanticMemory,
    SemanticMemoryData,
    EmotionalMemory,
    EmotionalMemoryData,
    HeatLevel,
    MemoryType,
    ToolUsageRecord,
    ToolOptimalContext,
    ToolCombinationPattern,
    NeuroticismTendency,
    GrowthMilestone,
    EmotionState,
    ConceptDefinition,
    # 反思类型
    ReflectionMemoryItem,
    MemoryCategory,
)
from .heat_manager import HeatManager


class LongTermMemoryManager:
    """
    长期记忆管理器

    负责持久化的经验与知识仓库，包括：
    - 用户画像管理
    - 程序性记忆管理（含工具使用模式）
    - 叙事记忆管理
    - 语义记忆管理
    - 情感记忆管理
    - 冷热度分层管理
    """

    def __init__(
        self,
        user_id: str = "default_user",
        storage_path: str = "./memory_storage",
    ) -> None:
        """
        初始化长期记忆管理器

        Args:
            user_id: 用户ID
            storage_path: 存储路径
        """
        self.user_id: str = user_id
        self.storage_path: Path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._container: LongTermMemoryContainer = LongTermMemoryContainer(
            user_id=user_id
        )
        self._heat_manager: HeatManager = HeatManager()

        # 尝试加载已有记忆
        self._load_from_storage()

    def _load_from_storage(self) -> None:
        """
        从存储加载记忆（内部方法）
        """
        storage_file: Path = self.storage_path / f"{self.user_id}_memory.json"

        if storage_file.exists():
            try:
                with open(storage_file, "r", encoding="utf-8") as f:
                    data: dict[str, Any] = json.load(f)
                    self._container = LongTermMemoryContainer.model_validate(data)
            except (json.JSONDecodeError, ValueError):
                # 加载失败，使用空容器
                pass

    def _save_to_storage(self) -> None:
        """
        保存记忆到存储（内部方法）
        """
        storage_file: Path = self.storage_path / f"{self.user_id}_memory.json"
        self._container.last_updated = datetime.now()

        with open(storage_file, "w", encoding="utf-8") as f:
            json.dump(self._container.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

    def get_user_profile(self) -> UserProfileData | None:
        """
        获取用户画像

        Returns:
            用户画像数据，如果不存在返回 None
        """
        if self._container.user_profile:
            return self._container.user_profile.data
        return None

    def update_user_profile(self, profile_data: dict[str, Any]) -> str:
        """
        更新用户画像

        Args:
            profile_data: 用户画像数据

        Returns:
            记忆ID
        """
        if self._container.user_profile is None:
            # 创建新画像
            memory_id: str = f"profile_{uuid.uuid4().hex[:12]}"
            self._container.user_profile = UserProfileMemory(
                memory_id=memory_id,
                user_id=self.user_id,
                data=UserProfileData.model_validate(profile_data),
            )
        else:
            # 更新现有画像
            current_data: UserProfileData = self._container.user_profile.data

            # 合并身份标签
            if "identity" in profile_data:
                for identity in profile_data["identity"]:
                    if identity not in current_data.identity:
                        current_data.identity.append(identity)

            # 更新技术背景
            if "technical_background" in profile_data:
                tb: dict[str, Any] = profile_data["technical_background"]
                if "domains" in tb:
                    for domain in tb["domains"]:
                        if domain not in current_data.technical_background.domains:
                            current_data.technical_background.domains.append(domain)
                if "expertise_level" in tb:
                    current_data.technical_background.expertise_level = tb["expertise_level"]

            # 更新沟通风格
            if "communication_style" in profile_data:
                cs: dict[str, Any] = profile_data["communication_style"]
                if "style" in cs:
                    current_data.communication_style.style = cs["style"]
                if "preference" in cs:
                    current_data.communication_style.preference = cs["preference"]

            # 更新决策模式
            if "decision_pattern" in profile_data:
                dp: dict[str, Any] = profile_data["decision_pattern"]
                if "type" in dp:
                    current_data.decision_pattern.type = dp["type"]
                if "focus" in dp:
                    current_data.decision_pattern.focus = dp["focus"]

            current_data.version += 1

        self._save_to_storage()
        return self._container.user_profile.memory_id

    def get_procedural_memory(self) -> ProceduralMemoryData | None:
        """
        获取程序性记忆

        Returns:
            程序性记忆数据
        """
        if self._container.procedural:
            return self._container.procedural.data
        return None

    def update_procedural_memory(self, procedural_data: dict[str, Any]) -> str:
        """
        更新程序性记忆

        Args:
            procedural_data: 程序性记忆数据

        Returns:
            记忆ID
        """
        if self._container.procedural is None:
            memory_id: str = f"procedural_{uuid.uuid4().hex[:12]}"
            self._container.procedural = ProceduralMemory(
                memory_id=memory_id,
                user_id=self.user_id,
                data=ProceduralMemoryData.model_validate(procedural_data),
            )
        else:
            current_data: ProceduralMemoryData = self._container.procedural.data

            # 合并决策模式
            if "decision_patterns" in procedural_data:
                for pattern in procedural_data["decision_patterns"]:
                    current_data.decision_patterns.append(
                        {
                            "pattern_id": pattern.get("pattern_id", f"dp_{uuid.uuid4().hex[:8]}"),
                            "trigger_condition": pattern.get("trigger_condition", ""),
                            "workflow": pattern.get("workflow", []),
                            "confidence": pattern.get("confidence", 0.5),
                            "usage_count": pattern.get("usage_count", 1),
                            "success_rate": pattern.get("success_rate", 0.5),
                        }
                    )

            # 更新操作偏好
            if "operation_preferences" in procedural_data:
                current_data.operation_preferences.update(
                    procedural_data["operation_preferences"]
                )

        self._save_to_storage()
        return self._container.procedural.memory_id

    def update_tool_usage(
        self,
        tool_name: str,
        task_type: str,
        outcome: str,
        user_feedback: float | None = None,
        effectiveness_score: float = 0.5,
        # P0: 工具调用状态关联参数
        checkpoint_id: str | None = None,
        phase: str | None = None,
        scenario: str | None = None,
        user_state: str | None = None,
    ) -> str:
        """
        更新工具使用记忆

        Args:
            tool_name: 工具名称
            task_type: 任务类型
            outcome: 结果（success/failure）
            user_feedback: 用户反馈评分
            effectiveness_score: 有效度分数
            checkpoint_id: 关联的状态快照ID（来自GlobalStateCapture）
            phase: 调用时的阶段
            scenario: 调用时的场景
            user_state: 调用时的用户状态

        Returns:
            记录ID
        """
        if self._container.procedural is None:
            memory_id: str = f"procedural_{uuid.uuid4().hex[:12]}"
            self._container.procedural = ProceduralMemory(
                memory_id=memory_id,
                user_id=self.user_id,
                data=ProceduralMemoryData(),
            )

        record: ToolUsageRecord = ToolUsageRecord(
            record_id=f"tool_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            task_type=task_type,
            tool_name=tool_name,
            effectiveness_score=effectiveness_score,
            outcome=outcome,
            user_feedback=user_feedback,
            checkpoint_id=checkpoint_id,
            phase=phase,
            scenario=scenario,
            user_state=user_state,
        )

        self._container.procedural.data.tool_effectiveness_records.append(record)
        self._save_to_storage()

        return record.record_id

    def get_tool_recommendation(
        self,
        task_type: str,
        constraints: list[str] | None = None,
        # P0: 状态感知过滤参数
        phase: str | None = None,
        scenario: str | None = None,
        user_state: str | None = None,
        state_weight: float = 0.3,  # 状态匹配的权重
    ) -> dict[str, Any]:
        """
        获取工具推荐（状态感知增强版）

        Args:
            task_type: 任务类型
            constraints: 约束条件
            phase: 当前阶段（用于状态感知过滤）
            scenario: 当前场景（用于状态感知过滤）
            user_state: 当前用户状态（用于状态感知过滤）
            state_weight: 状态匹配的权重系数 (0.0-1.0)

        Returns:
            推荐结果
        """
        default_result: dict[str, Any] = {
            "tool": "代码解释器",
            "confidence": 0.5,
            "reasons": ["无历史记录，使用默认推荐"],
            "all_candidates": [],
            "state_filtered": False,
        }

        if self._container.procedural is None:
            return default_result

        records: list[ToolUsageRecord] = self._container.procedural.data.tool_effectiveness_records

        # 按任务类型过滤
        filtered_records: list[ToolUsageRecord] = [
            r for r in records if r.task_type == task_type or task_type == ""
        ]

        if not filtered_records:
            return default_result

        # 状态感知过滤：如果有状态参数，优先考虑状态匹配的记录
        state_filtered_records: list[ToolUsageRecord] = []
        has_state_filter: bool = phase is not None or scenario is not None or user_state is not None

        if has_state_filter:
            for record in filtered_records:
                match_score: float = 0.0
                match_count: int = 0

                if phase is not None and record.phase == phase:
                    match_score += 1.0
                    match_count += 1
                if scenario is not None and record.scenario == scenario:
                    match_score += 1.0
                    match_count += 1
                if user_state is not None and record.user_state == user_state:
                    match_score += 1.0
                    match_count += 1

                if match_count > 0:
                    state_filtered_records.append(record)

        # 如果有状态匹配的记录，优先使用；否则使用全部记录
        effective_records: list[ToolUsageRecord] = (
            state_filtered_records if state_filtered_records else filtered_records
        )

        # 统计各工具的成功率
        tool_stats: dict[str, dict[str, float]] = {}

        for record in effective_records:
            tool: str = record.tool_name
            if tool not in tool_stats:
                tool_stats[tool] = {"total": 0.0, "success": 0.0, "feedback": 0.0}

            tool_stats[tool]["total"] += 1
            if record.outcome == "success":
                tool_stats[tool]["success"] += 1
            if record.user_feedback:
                tool_stats[tool]["feedback"] += record.user_feedback

        if not tool_stats:
            return default_result

        # 计算综合分数
        best_tool: str = ""
        best_score: float = 0.0

        for tool, stats in tool_stats.items():
            success_rate: float = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            avg_feedback: float = stats["feedback"] / stats["total"] if stats["total"] > 0 else 0

            # 基础分数
            base_score: float = success_rate * 0.5 + avg_feedback / 5.0 * 0.3 + stats["total"] / 10 * 0.2

            # 如果是状态过滤的结果，增加权重
            if state_filtered_records:
                base_score = base_score * (1 + state_weight)

            if base_score > best_score:
                best_score = base_score
                best_tool = tool

        return {
            "tool": best_tool,
            "confidence": min(0.95, best_score),
            "reasons": [
                f"历史成功率: {tool_stats[best_tool]['success'] / tool_stats[best_tool]['total']:.0%}" if tool_stats[best_tool]["total"] > 0 else "无历史记录",
                f"使用次数: {int(tool_stats[best_tool]['total'])}",
            ],
            "all_candidates": [
                {
                    "tool": t,
                    "success_rate": s["success"] / s["total"] if s["total"] > 0 else 0,
                    "usage_count": int(s["total"]),
                    "avg_feedback": s["feedback"] / s["total"] if s["total"] > 0 and s["feedback"] > 0 else None,
                }
                for t, s in sorted(tool_stats.items(), key=lambda x: x[1]["success"] / max(x[1]["total"], 1), reverse=True)
            ],
            "state_filtered": has_state_filter and len(state_filtered_records) > 0,
            "state_match_count": len(state_filtered_records) if has_state_filter else 0,
        }

    def get_tool_effectiveness_summary(
        self,
        tool_name: str | None = None,
        task_type: str | None = None,
    ) -> dict[str, Any]:
        """
        获取工具效果汇总统计

        Args:
            tool_name: 工具名称（可选，不指定则返回所有工具）
            task_type: 任务类型（可选，不指定则返回所有任务类型）

        Returns:
            工具效果汇总数据
        """
        if self._container.procedural is None:
            return {"tools": [], "total_records": 0}

        records: list[ToolUsageRecord] = self._container.procedural.data.tool_effectiveness_records

        # 过滤条件
        if tool_name:
            records = [r for r in records if r.tool_name == tool_name]
        if task_type:
            records = [r for r in records if r.task_type == task_type]

        # 按工具分组统计
        tool_summary: dict[str, dict[str, Any]] = {}
        for record in records:
            tool: str = record.tool_name
            if tool not in tool_summary:
                tool_summary[tool] = {
                    "tool_name": tool,
                    "total_uses": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "total_effectiveness": 0.0,
                    "feedback_sum": 0.0,
                    "feedback_count": 0,
                    "task_types": set(),
                }

            tool_summary[tool]["total_uses"] += 1
            tool_summary[tool]["total_effectiveness"] += record.effectiveness_score
            tool_summary[tool]["task_types"].add(record.task_type)

            if record.outcome == "success":
                tool_summary[tool]["success_count"] += 1
            else:
                tool_summary[tool]["failure_count"] += 1

            if record.user_feedback is not None:
                tool_summary[tool]["feedback_sum"] += record.user_feedback
                tool_summary[tool]["feedback_count"] += 1

        # 计算最终统计
        result: dict[str, Any] = {
            "tools": [],
            "total_records": len(records),
        }

        for tool, stats in tool_summary.items():
            success_rate: float = stats["success_count"] / stats["total_uses"] if stats["total_uses"] > 0 else 0
            avg_effectiveness: float = stats["total_effectiveness"] / stats["total_uses"] if stats["total_uses"] > 0 else 0
            avg_feedback: float = stats["feedback_sum"] / stats["feedback_count"] if stats["feedback_count"] > 0 else 0

            result["tools"].append({
                "tool_name": stats["tool_name"],
                "total_uses": stats["total_uses"],
                "success_rate": round(success_rate, 3),
                "failure_rate": round(1 - success_rate, 3),
                "avg_effectiveness": round(avg_effectiveness, 3),
                "avg_user_feedback": round(avg_feedback, 2) if stats["feedback_count"] > 0 else None,
                "task_types": list(stats["task_types"]),
            })

        # 按成功率排序
        result["tools"].sort(key=lambda x: x["success_rate"], reverse=True)

        return result

    def record_tool_combination(
        self,
        tool_sequence: list[str],
        task_pattern: str,
        effectiveness: float,
    ) -> str:
        """
        记录工具组合使用模式

        Args:
            tool_sequence: 工具使用序列，如 ["web_search", "code_interpreter", "file_write"]
            task_pattern: 任务模式描述，如 "研究并实现功能"
            effectiveness: 整体效果评分 (0.0-1.0)

        Returns:
            模式ID
        """
        if self._container.procedural is None:
            self._container.procedural = ProceduralMemory(
                memory_id=f"procedural_{uuid.uuid4().hex[:12]}",
                user_id=self.user_id,
                data=ProceduralMemoryData(),
            )

        # 检查是否已存在相同序列
        for pattern in self._container.procedural.data.tool_combination_patterns:
            if pattern.sequence == tool_sequence and pattern.task_pattern == task_pattern:
                # 更新已有模式的统计数据
                new_count: int = pattern.usage_count + 1
                new_avg: float = (pattern.effectiveness_avg * pattern.usage_count + effectiveness) / new_count
                pattern.usage_count = new_count
                pattern.effectiveness_avg = new_avg
                self._save_to_storage()
                return f"updated_{pattern.sequence[0]}_{pattern.usage_count}"

        # 创建新模式
        pattern_id: str = f"combo_{uuid.uuid4().hex[:8]}"
        new_pattern: ToolCombinationPattern = ToolCombinationPattern(
            sequence=tool_sequence,
            task_pattern=task_pattern,
            effectiveness_avg=effectiveness,
            usage_count=1,
        )

        self._container.procedural.data.tool_combination_patterns.append(new_pattern)
        self._save_to_storage()

        return pattern_id

    def get_tool_combination_patterns(
        self,
        task_pattern: str | None = None,
        min_effectiveness: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        获取工具组合模式

        Args:
            task_pattern: 任务模式过滤（可选）
            min_effectiveness: 最小效果阈值（可选）

        Returns:
            工具组合模式列表
        """
        if self._container.procedural is None:
            return []

        patterns: list[ToolCombinationPattern] = self._container.procedural.data.tool_combination_patterns

        # 过滤
        if task_pattern:
            patterns = [p for p in patterns if task_pattern.lower() in p.task_pattern.lower()]
        if min_effectiveness > 0:
            patterns = [p for p in patterns if p.effectiveness_avg >= min_effectiveness]

        # 按效果排序
        patterns = sorted(patterns, key=lambda x: x.effectiveness_avg, reverse=True)

        return [
            {
                "sequence": p.sequence,
                "task_pattern": p.task_pattern,
                "effectiveness_avg": round(p.effectiveness_avg, 3),
                "usage_count": p.usage_count,
            }
            for p in patterns
        ]

    def get_optimal_tool_context(self, tool_name: str) -> dict[str, Any]:
        """
        获取工具最优使用场景

        Args:
            tool_name: 工具名称

        Returns:
            最优场景和规避场景信息
        """
        if self._container.procedural is None:
            return {"optimal_scenarios": [], "avoid_scenarios": [], "has_data": False}

        # 从 tool_optimal_contexts 获取
        if tool_name in self._container.procedural.data.tool_optimal_contexts:
            context: ToolOptimalContext = self._container.procedural.data.tool_optimal_contexts[tool_name]
            return {
                "optimal_scenarios": context.optimal_scenarios,
                "avoid_scenarios": context.avoid_scenarios,
                "has_data": True,
            }

        # 基于历史记录推导
        records: list[ToolUsageRecord] = [
            r for r in self._container.procedural.data.tool_effectiveness_records
            if r.tool_name == tool_name
        ]

        if not records:
            return {"optimal_scenarios": [], "avoid_scenarios": [], "has_data": False}

        # 分析成功和失败的场景
        optimal: list[dict[str, Any]] = []
        avoid: list[dict[str, Any]] = []

        success_records: list[ToolUsageRecord] = [r for r in records if r.outcome == "success"]
        failure_records: list[ToolUsageRecord] = [r for r in records if r.outcome != "success"]

        # 成功场景聚合
        task_success: dict[str, list[float]] = {}
        for r in success_records:
            if r.task_type not in task_success:
                task_success[r.task_type] = []
            task_success[r.task_type].append(r.effectiveness_score)

        for task_type, scores in task_success.items():
            if len(scores) >= 2:  # 至少2次成功才纳入
                optimal.append({
                    "task_type": task_type,
                    "success_count": len(scores),
                    "avg_effectiveness": round(sum(scores) / len(scores), 3),
                })

        # 失败场景聚合
        task_failure: dict[str, int] = {}
        for r in failure_records:
            task_failure[r.task_type] = task_failure.get(r.task_type, 0) + 1

        for task_type, count in task_failure.items():
            if count >= 2:  # 至少2次失败才规避
                avoid.append({
                    "task_type": task_type,
                    "failure_count": count,
                })

        return {
            "optimal_scenarios": sorted(optimal, key=lambda x: x["success_count"], reverse=True),
            "avoid_scenarios": sorted(avoid, key=lambda x: x["failure_count"], reverse=True),
            "has_data": True,
            "derived_from_history": True,
        }

    def update_neuroticism_tendency(
        self, adjustment: float, source: str
    ) -> float:
        """
        更新神经质倾向

        Args:
            adjustment: 调整值
            source: 来源描述

        Returns:
            更新后的分数
        """
        if self._container.procedural is None:
            self._container.procedural = ProceduralMemory(
                memory_id=f"procedural_{uuid.uuid4().hex[:12]}",
                user_id=self.user_id,
                data=ProceduralMemoryData(),
            )

        current_score: float = self._container.procedural.data.neuroticism_tendency.score
        new_score: float = max(-1.0, min(1.0, current_score + adjustment))

        self._container.procedural.data.neuroticism_tendency.score = new_score
        self._container.procedural.data.neuroticism_tendency.derived_from.append(source)

        self._save_to_storage()
        return new_score

    def get_neuroticism_tendency(self) -> float:
        """
        获取神经质倾向分数

        Returns:
            神经质倾向分数 (-1.0 ~ 1.0)
        """
        if self._container.procedural:
            return self._container.procedural.data.neuroticism_tendency.score
        return 0.0

    def update_narrative_memory(self, narrative_data: dict[str, Any]) -> str:
        """
        更新叙事记忆

        Args:
            narrative_data: 叙事记忆数据

        Returns:
            记忆ID
        """
        if self._container.narrative is None:
            memory_id: str = f"narrative_{uuid.uuid4().hex[:12]}"
            self._container.narrative = NarrativeMemory(
                memory_id=memory_id,
                user_id=self.user_id,
                data=NarrativeMemoryData.model_validate(narrative_data),
            )
        else:
            current_data: NarrativeMemoryData = self._container.narrative.data

            # 合并成长节点
            if "growth_milestones" in narrative_data:
                for milestone in narrative_data["growth_milestones"]:
                    current_data.growth_milestones.append(
                        GrowthMilestone(
                            timestamp=datetime.fromisoformat(milestone.get("timestamp", datetime.now().isoformat())),
                            event=milestone.get("event", ""),
                            significance=milestone.get("significance", ""),
                            importance_score=milestone.get("importance_score", 0.5),
                        )
                    )

            # 更新当前身份
            if "current_identity" in narrative_data:
                for identity in narrative_data["current_identity"]:
                    if identity not in current_data.current_identity:
                        current_data.current_identity.append(identity)

        self._save_to_storage()
        return self._container.narrative.memory_id

    def update_semantic_memory(self, semantic_data: dict[str, Any]) -> str:
        """
        更新语义记忆

        Args:
            semantic_data: 语义记忆数据

        Returns:
            记忆ID
        """
        if self._container.semantic is None:
            memory_id: str = f"semantic_{uuid.uuid4().hex[:12]}"
            self._container.semantic = SemanticMemory(
                memory_id=memory_id,
                user_id=self.user_id,
                data=SemanticMemoryData.model_validate(semantic_data),
            )
        else:
            current_data: SemanticMemoryData = self._container.semantic.data

            # 合并核心概念
            if "core_concepts" in semantic_data:
                for concept in semantic_data["core_concepts"]:
                    existing: bool = False
                    for existing_concept in current_data.core_concepts:
                        if existing_concept.concept == concept.get("concept"):
                            existing_concept.usage_count += 1
                            existing = True
                            break

                    if not existing:
                        current_data.core_concepts.append(
                            ConceptDefinition(
                                concept=concept.get("concept", ""),
                                definition=concept.get("definition", ""),
                                attributes=concept.get("attributes", {}),
                                related_concepts=concept.get("related_concepts", []),
                                usage_count=1,
                                confidence=concept.get("confidence", 0.5),
                            )
                        )

        self._save_to_storage()
        return self._container.semantic.memory_id

    def update_emotional_memory(self, emotional_data: dict[str, Any]) -> str:
        """
        更新情感记忆

        Args:
            emotional_data: 情感记忆数据

        Returns:
            记忆ID
        """
        if self._container.emotional is None:
            memory_id: str = f"emotional_{uuid.uuid4().hex[:12]}"
            self._container.emotional = EmotionalMemory(
                memory_id=memory_id,
                user_id=self.user_id,
                data=EmotionalMemoryData.model_validate(emotional_data),
            )
        else:
            current_data: EmotionalMemoryData = self._container.emotional.data

            # 添加情绪状态
            if "emotion_states" in emotional_data:
                for state in emotional_data["emotion_states"]:
                    current_data.emotion_states.append(
                        EmotionState(
                            timestamp=datetime.fromisoformat(state.get("timestamp", datetime.now().isoformat())),
                            emotion_type=state.get("emotion_type", "neutral"),
                            intensity=state.get("intensity", 0.5),
                            trigger_context=state.get("trigger_context", ""),
                            topic=state.get("topic", ""),
                            decay_factor=state.get("decay_factor", 0.98),
                        )
                    )

        self._save_to_storage()
        return self._container.emotional.memory_id

    def update_from_extractions(self, extractions: dict[str, Any]) -> dict[str, str]:
        """
        从提炼结果更新记忆

        Args:
            extractions: 提炼结果

        Returns:
            更新的记忆ID映射
        """
        result: dict[str, str] = {}

        if extractions.get("user_profile"):
            result["user_profile"] = self.update_user_profile(
                extractions["user_profile"]
            )

        if extractions.get("procedural"):
            result["procedural"] = self.update_procedural_memory(
                extractions["procedural"]
            )

        if extractions.get("narrative"):
            result["narrative"] = self.update_narrative_memory(
                extractions["narrative"]
            )

        if extractions.get("semantic"):
            result["semantic"] = self.update_semantic_memory(
                extractions["semantic"]
            )

        if extractions.get("emotional"):
            result["emotional"] = self.update_emotional_memory(
                extractions["emotional"]
            )

        return result

    def get_all_memories(self) -> LongTermMemoryContainer:
        """
        获取所有长期记忆

        Returns:
            长期记忆容器
        """
        return self._container

    def apply_heat_policy(self) -> dict[str, Any]:
        """
        应用冷热度策略

        Returns:
            应用结果统计
        """
        result: dict[str, Any] = {
            "total_processed": 0,
            "migrations": [],
        }

        # 处理用户画像（通常保持热状态）
        if self._container.user_profile:
            self._container.user_profile.heat.heat_level = HeatLevel.HOT
            self._container.user_profile.heat.heat_score = 100.0
            result["total_processed"] += 1

        # 处理程序性记忆
        if self._container.procedural:
            memory: ProceduralMemory = self._container.procedural
            new_score: float = self._heat_manager.calculate_heat_score(
                days_since_access=self._days_since(memory.heat.last_accessed_at),
                access_count=memory.heat.access_count,
                importance=0.8,
                user_interaction=0.0,
            )
            new_level: HeatLevel = self._heat_manager.determine_level(new_score)

            if new_level != memory.heat.heat_level:
                result["migrations"].append(
                    {
                        "memory_id": memory.memory_id,
                        "from": memory.heat.heat_level.value,
                        "to": new_level.value,
                    }
                )
                memory.heat.heat_score = new_score
                memory.heat.heat_level = new_level

            result["total_processed"] += 1

        # 处理叙事记忆
        if self._container.narrative:
            memory_n: NarrativeMemory = self._container.narrative
            new_score_n: float = self._heat_manager.calculate_heat_score(
                days_since_access=self._days_since(memory_n.heat.last_accessed_at),
                access_count=memory_n.heat.access_count,
                importance=0.6,
                user_interaction=0.0,
            )
            new_level_n: HeatLevel = self._heat_manager.determine_level(new_score_n)

            memory_n.heat.heat_score = new_score_n
            memory_n.heat.heat_level = new_level_n
            result["total_processed"] += 1

        # 处理情感记忆
        if self._container.emotional:
            memory_e: EmotionalMemory = self._container.emotional
            new_score_e: float = self._heat_manager.calculate_heat_score(
                days_since_access=self._days_since(memory_e.heat.last_accessed_at),
                access_count=memory_e.heat.access_count,
                importance=0.5,
                user_interaction=0.0,
            )
            new_level_e: HeatLevel = self._heat_manager.determine_level(new_score_e)

            memory_e.heat.heat_score = new_score_e
            memory_e.heat.heat_level = new_level_e
            result["total_processed"] += 1

            # 情感衰减
            self._apply_emotion_decay()

        self._save_to_storage()
        return result

    def _days_since(self, timestamp: datetime) -> float:
        """
        计算距今天数（内部方法）

        Args:
            timestamp: 时间戳

        Returns:
            天数
        """
        delta = datetime.now() - timestamp
        return delta.total_seconds() / 86400

    def _apply_emotion_decay(self) -> None:
        """
        应用情感衰减（内部方法）
        """
        if self._container.emotional is None:
            return

        now: datetime = datetime.now()
        updated_states: list[EmotionState] = []

        for state in self._container.emotional.data.emotion_states:
            days_passed: float = (now - state.timestamp).total_seconds() / 86400
            new_intensity: float = state.intensity * (state.decay_factor**days_passed)

            # 保留强度大于 0.1 的情绪
            if new_intensity > 0.1:
                state.intensity = new_intensity
                updated_states.append(state)

        self._container.emotional.data.emotion_states = updated_states[
            -50:
        ]  # 保留最近 50 条

    def get_memory_by_type(self, memory_type: MemoryType) -> Any | None:
        """
        按类型获取记忆

        Args:
            memory_type: 记忆类型

        Returns:
            记忆数据
        """
        mapping: dict[MemoryType, Any] = {
            MemoryType.USER_PROFILE: self._container.user_profile,
            MemoryType.PROCEDURAL: self._container.procedural,
            MemoryType.NARRATIVE: self._container.narrative,
            MemoryType.SEMANTIC: self._container.semantic,
            MemoryType.EMOTIONAL: self._container.emotional,
        }
        return mapping.get(memory_type)

    def clear_all_memories(self) -> None:
        """
        清除所有记忆

        警告：此操作不可逆
        """
        self._container = LongTermMemoryContainer(user_id=self.user_id)
        self._save_to_storage()

    # ========================================================================
    # 反思记忆管理（P0: 链式推理增强）
    # ========================================================================

    def store_reflection(
        self,
        item: ReflectionMemoryItem,
    ) -> str:
        """
        存储反思记忆到长期记忆

        反思记忆被持久化到 EXTENDED_REFLECTION 分类，
        作为元学习训练数据使用。

        Args:
            item: 反思记忆项

        Returns:
            memory_id
        """
        # 构建存储路径
        reflection_dir: Path = self.storage_path / "reflections"
        reflection_dir.mkdir(parents=True, exist_ok=True)

        # 存储为独立文件
        storage_file: Path = reflection_dir / f"{item.memory_id}.json"

        with open(storage_file, "w", encoding="utf-8") as f:
            json.dump(item.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

        # 更新索引
        self._container.reflection_index.append({
            "memory_id": item.memory_id,
            "timestamp": item.timestamp.isoformat(),
            "trigger_type": item.trigger_type.value,
            "outcome": item.outcome.value,
            "learning_value": item.learning_value.value,
            "step_index": item.step_index,
            "task_type": item.task_type,
        })

        self._save_to_storage()
        return item.memory_id

    def get_memories_by_category(
        self,
        category: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        按分类获取记忆

        Args:
            category: 记忆分类（如 EXTENDED_REFLECTION）
            limit: 最大返回数量

        Returns:
            记忆列表
        """
        if category == MemoryCategory.EXTENDED_REFLECTION.value:
            return self._get_reflection_memories(limit)

        # 其他分类（可扩展）
        return []

    def _get_reflection_memories(
        self,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        获取反思记忆列表

        Args:
            limit: 最大返回数量

        Returns:
            反思记忆列表
        """
        reflection_dir: Path = self.storage_path / "reflections"

        if not reflection_dir.exists():
            return []

        # 读取所有反思文件
        memories: list[dict[str, Any]] = []
        for file_path in reflection_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data: dict[str, Any] = json.load(f)
                    memories.append(data)
            except (json.JSONDecodeError, IOError):
                continue

        # 按时间排序（最新的在前）
        memories.sort(
            key=lambda x: x.get("timestamp", ""),
            reverse=True,
        )

        return memories[:limit]

    def get_reflection_statistics(self) -> dict[str, Any]:
        """
        获取反思记忆统计信息

        Returns:
            统计信息
        """
        reflections: list[dict[str, Any]] = self._get_reflection_memories(limit=1000)

        if not reflections:
            return {
                "total_count": 0,
                "outcome_distribution": {},
                "learning_value_distribution": {},
                "trigger_type_distribution": {},
                "task_type_distribution": {},
            }

        # 统计分布
        outcome_dist: dict[str, int] = {}
        learning_dist: dict[str, int] = {}
        trigger_dist: dict[str, int] = {}
        task_dist: dict[str, int] = {}

        for r in reflections:
            # 结果分布
            outcome: str = r.get("outcome", "unknown")
            outcome_dist[outcome] = outcome_dist.get(outcome, 0) + 1

            # 学习价值分布
            lv: str = r.get("learning_value", "low")
            learning_dist[lv] = learning_dist.get(lv, 0) + 1

            # 触发类型分布
            tt: str = r.get("trigger_type", "unknown")
            trigger_dist[tt] = trigger_dist.get(tt, 0) + 1

            # 任务类型分布
            task_type: str = r.get("task_type", "unknown")
            task_dist[task_type] = task_dist.get(task_type, 0) + 1

        return {
            "total_count": len(reflections),
            "outcome_distribution": outcome_dist,
            "learning_value_distribution": learning_dist,
            "trigger_type_distribution": trigger_dist,
            "task_type_distribution": task_dist,
            "high_value_count": learning_dist.get("high", 0),
            "correction_rate": outcome_dist.get("corrected", 0) / len(reflections) if reflections else 0,
        }


# ============================================================================
# 导出
# ============================================================================

__all__ = ["LongTermMemoryManager"]
