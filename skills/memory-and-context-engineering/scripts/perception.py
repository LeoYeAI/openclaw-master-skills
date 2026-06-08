"""
Agent Memory System - 感知记忆模块

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

import uuid
from datetime import datetime, timedelta
from typing import Any

from .types import (
    ConversationTurn,
    CurrentTask,
    TaskState,
    TemporaryContext,
    PerceptionMemory,
    PerceptionMemoryData,
    SituationAwareness,
    UserCurrentState,
    ContextAnchors,
    TaskType,
    MemoryType,
    UserProfileData,
    ProceduralMemoryData,
    NarrativeMemoryData,
    SemanticMemoryData,
    EmotionalMemoryData,
    TechnicalBackground,
    CommunicationStyle,
    DecisionPattern,
)


class PerceptionMemoryStore:
    """
    感知记忆存储

    负责实时交互的临时缓冲区，包括：
    - 对话上下文存储
    - 情境感知
    - 短期记忆提炼
    """

    def __init__(self, user_id: str = "default_user") -> None:
        """初始化感知记忆存储"""
        self.user_id: str = user_id
        self._memories: dict[str, PerceptionMemory] = {}
        self._current_session_id: str = ""
        self._session_ttl_hours: int = 24

    def create_session(self) -> str:
        """
        创建新的会话

        Returns:
            会话ID
        """
        session_id: str = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self._current_session_id = session_id

        memory_id: str = f"perception_{uuid.uuid4().hex[:12]}"
        self._memories[memory_id] = PerceptionMemory(
            memory_id=memory_id,
            user_id=self.user_id,
            data=PerceptionMemoryData(
                session_id=session_id,
                conversation_history=[],
                task_state=TaskState(),
                temporary_context=TemporaryContext(),
            ),
            expires_at=datetime.now() + timedelta(hours=self._session_ttl_hours),
        )

        return session_id

    def store_conversation(
        self,
        session_id: str,
        user_message: str,
        system_response: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        存储对话上下文

        Args:
            session_id: 会话ID
            user_message: 用户消息
            system_response: 系统响应
            metadata: 元数据（可选）

        Returns:
            记忆ID

        Raises:
            ValueError: 会话不存在时抛出
        """
        # 查找对应的感知记忆
        memory: PerceptionMemory | None = None
        for mem in self._memories.values():
            if isinstance(mem.data, PerceptionMemoryData) and mem.data.session_id == session_id:
                memory = mem
                break

        if memory is None:
            raise ValueError(f"Session {session_id} not found")

        # 添加用户消息
        user_turn: ConversationTurn = ConversationTurn(
            role="user",
            content=user_message,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )
        memory.data.conversation_history.append(user_turn)

        # 添加系统响应
        system_turn: ConversationTurn = ConversationTurn(
            role="system",
            content=system_response,
            timestamp=datetime.now(),
            metadata={},
        )
        memory.data.conversation_history.append(system_turn)

        # 更新临时上下文
        self._update_temporary_context(memory, user_message)

        return memory.memory_id

    def _update_temporary_context(
        self, memory: PerceptionMemory, message: str
    ) -> None:
        """
        更新临时上下文（内部方法）

        Args:
            memory: 感知记忆
            message: 用户消息
        """
        # 简单的关键词提取（实际应使用 NLP）
        words: list[str] = message.split()
        for word in words:
            if len(word) > 3 and word not in memory.data.temporary_context.mentioned_concepts:
                memory.data.temporary_context.mentioned_concepts.append(word)

    def detect_situation(self, session_id: str | None = None) -> SituationAwareness:
        """
        情境感知：识别当前任务类型、用户状态、隐式需求

        Args:
            session_id: 会话ID（可选，默认使用当前会话）

        Returns:
            情境感知结果
        """
        target_session: str = session_id or self._current_session_id
        memory: PerceptionMemory | None = None

        for mem in self._memories.values():
            if isinstance(mem.data, PerceptionMemoryData) and mem.data.session_id == target_session:
                memory = mem
                break

        if memory is None:
            # 返回默认情境
            return SituationAwareness(
                current_task=CurrentTask(task_type=TaskType.PROBLEM_SOLVING),
                user_current_state=UserCurrentState(),
                context_anchors=ContextAnchors(),
            )

        # 分析对话历史
        history: list[ConversationTurn] = memory.data.conversation_history
        user_messages: list[str] = [
            turn.content for turn in history if turn.role == "user"
        ]

        # 任务类型识别
        task_type: TaskType = self._classify_task_type(user_messages)

        # 任务复杂度评估
        complexity: str = self._assess_complexity(user_messages)

        # 任务阶段判断
        phase: str = self._determine_phase(history)

        # 隐式需求提取
        implicit_requirements: list[str] = self._extract_implicit_requirements(
            user_messages
        )

        # 上下文锚点
        anchors: ContextAnchors = self._build_context_anchors(memory)

        return SituationAwareness(
            current_task=CurrentTask(
                task_type=task_type,
                task_complexity=complexity,
                task_phase=phase,
                implicit_requirements=implicit_requirements,
            ),
            user_current_state=UserCurrentState(
                technical_level=self._infer_technical_level(user_messages),
                current_focus=memory.data.task_state.current_topic or "未知",
                mental_model=self._infer_mental_model(user_messages),
                decision_style="balanced",
            ),
            context_anchors=anchors,
        )

    def _classify_task_type(self, messages: list[str]) -> TaskType:
        """
        分类任务类型（内部方法）

        Args:
            messages: 用户消息列表

        Returns:
            任务类型
        """
        if not messages:
            return TaskType.PROBLEM_SOLVING

        combined: str = " ".join(messages).lower()

        # 关键词匹配
        keywords: dict[TaskType, list[str]] = {
            TaskType.TECHNICAL_IMPLEMENTATION: [
                "实现",
                "代码",
                "开发",
                "编程",
                "implement",
                "code",
            ],
            TaskType.CODE_DEBUGGING: [
                "错误",
                "bug",
                "调试",
                "debug",
                "修复",
                "fix",
            ],
            TaskType.PRECISE_CALCULATION: [
                "计算",
                "统计",
                "分析数据",
                "calculate",
                "compute",
            ],
            TaskType.CREATIVE_DESIGN: [
                "设计",
                "创意",
                "构思",
                "design",
                "create",
            ],
            TaskType.BRAINSTORMING: [
                "头脑风暴",
                "想法",
                "brainstorm",
                "idea",
            ],
            TaskType.DATA_ANALYSIS: [
                "数据分析",
                "报表",
                "可视化",
                "data analysis",
            ],
        }

        for task_type, words in keywords.items():
            for word in words:
                if word in combined:
                    return task_type

        return TaskType.PROBLEM_SOLVING

    def _assess_complexity(self, messages: list[str]) -> str:
        """
        评估任务复杂度（内部方法）

        Args:
            messages: 用户消息列表

        Returns:
            复杂度等级（low/medium/high）
        """
        if not messages:
            return "medium"

        combined: str = " ".join(messages)
        word_count: int = len(combined.split())

        # 基于消息长度和关键词判断
        complexity_keywords_high: list[str] = [
            "架构",
            "系统",
            "复杂",
            "多模块",
            "architecture",
            "system",
        ]
        complexity_keywords_low: list[str] = [
            "简单",
            "快速",
            "一下",
            "simple",
            "quick",
        ]

        high_count: int = sum(
            1 for kw in complexity_keywords_high if kw in combined
        )
        low_count: int = sum(
            1 for kw in complexity_keywords_low if kw in combined
        )

        if high_count > low_count or word_count > 200:
            return "high"
        elif low_count > high_count or word_count < 50:
            return "low"
        else:
            return "medium"

    def _determine_phase(self, history: list[ConversationTurn]) -> str:
        """
        判断任务阶段（内部方法）

        Args:
            history: 对话历史

        Returns:
            任务阶段
        """
        turn_count: int = len([t for t in history if t.role == "user"])

        if turn_count <= 2:
            return "exploration"
        elif turn_count <= 5:
            return "design"
        elif turn_count <= 8:
            return "implementation"
        else:
            return "verification"

    def _extract_implicit_requirements(self, messages: list[str]) -> list[str]:
        """
        提取隐式需求（内部方法）

        Args:
            messages: 用户消息列表

        Returns:
            隐式需求列表
        """
        requirements: list[str] = []

        if not messages:
            return requirements

        combined: str = " ".join(messages)

        # 基于关键词推断
        if "快速" in combined or "尽快" in combined:
            requirements.append("效率优先")
        if "详细" in combined or "深入" in combined:
            requirements.append("深度分析")
        if "简单" in combined:
            requirements.append("简洁易懂")
        if "准确" in combined:
            requirements.append("精确可靠")

        return requirements

    def _infer_technical_level(self, messages: list[str]) -> str:
        """
        推断用户技术水平（内部方法）

        Args:
            messages: 用户消息列表

        Returns:
            技术水平等级
        """
        if not messages:
            return "intermediate"

        combined: str = " ".join(messages).lower()

        # 专业术语检测
        advanced_terms: list[str] = [
            "架构",
            "分布式",
            "微服务",
            "架构设计",
            "系统设计",
            "architecture",
        ]
        basic_terms: list[str] = [
            "怎么",
            "如何",
            "什么是",
            "how to",
            "what is",
        ]

        advanced_count: int = sum(
            1 for term in advanced_terms if term in combined
        )
        basic_count: int = sum(
            1 for term in basic_terms if term in combined
        )

        if advanced_count > basic_count:
            return "advanced"
        elif basic_count > advanced_count:
            return "beginner"
        else:
            return "intermediate"

    def _infer_mental_model(self, messages: list[str]) -> str:
        """
        推断用户心智模型（内部方法）

        Args:
            messages: 用户消息列表

        Returns:
            心智模型描述
        """
        if not messages:
            return "未知"

        combined: str = " ".join(messages)

        if "概念" in combined or "原理" in combined:
            return "理论导向"
        elif "实现" in combined or "代码" in combined:
            return "实践导向"
        else:
            return "平衡型"

    def _build_context_anchors(
        self, memory: PerceptionMemory
    ) -> ContextAnchors:
        """
        构建上下文锚点（内部方法）

        Args:
            memory: 感知记忆

        Returns:
            上下文锚点
        """
        history: list[ConversationTurn] = memory.data.conversation_history
        user_messages: list[str] = [
            t.content for t in history if t.role == "user"
        ]

        # 时间锚点：最近的用户消息
        temporal: str = (
            user_messages[-1][:50] if user_messages else ""
        )

        # 语义锚点：提及的概念
        semantic: str = ", ".join(
            memory.data.temporary_context.mentioned_concepts[:5]
        )

        # 叙事锚点：当前任务
        narrative: str = memory.data.task_state.current_topic

        # 情感锚点：从消息推断
        emotional: str = self._infer_emotion(user_messages)

        return ContextAnchors(
            temporal=temporal,
            semantic=semantic,
            narrative=narrative,
            emotional=emotional,
        )

    def _infer_emotion(self, messages: list[str]) -> str:
        """
        推断情感状态（内部方法）

        Args:
            messages: 用户消息列表

        Returns:
            情感状态描述
        """
        if not messages:
            return "中性"

        combined: str = " ".join(messages)

        positive_words: list[str] = ["好", "棒", "喜欢", "感谢", "谢谢"]
        negative_words: list[str] = ["问题", "错误", "困难", "不对"]

        pos_count: int = sum(1 for w in positive_words if w in combined)
        neg_count: int = sum(1 for w in negative_words if w in combined)

        if pos_count > neg_count:
            return "积极"
        elif neg_count > pos_count:
            return "焦虑"
        else:
            return "中性"

    def extract_memories(self, session_id: str | None = None) -> dict[str, Any]:
        """
        短期记忆提炼：从感知记忆中提取有价值的信息

        Args:
            session_id: 会话ID（可选，默认使用当前会话）

        Returns:
            提炼结果，包含各类记忆数据
        """
        target_session: str = session_id or self._current_session_id
        memory: PerceptionMemory | None = None

        for mem in self._memories.values():
            if isinstance(mem.data, PerceptionMemoryData) and mem.data.session_id == target_session:
                memory = mem
                break

        if memory is None:
            return {
                "user_profile": None,
                "procedural": None,
                "narrative": None,
                "semantic": None,
                "emotional": None,
                "extraction_confidence": 0.0,
            }

        history: list[ConversationTurn] = memory.data.conversation_history
        user_messages: list[str] = [
            t.content for t in history if t.role == "user"
        ]

        # 提取用户画像
        user_profile: dict[str, Any] = self._extract_user_profile(user_messages)

        # 提取程序性记忆
        procedural: dict[str, Any] = self._extract_procedural(user_messages, history)

        # 提取叙事记忆
        narrative: dict[str, Any] = self._extract_narrative(user_messages, history)

        # 提取语义记忆
        semantic: dict[str, Any] = self._extract_semantic(user_messages)

        # 提取情感记忆
        emotional: dict[str, Any] = self._extract_emotional(user_messages)

        # 计算提取置信度
        confidence: float = min(1.0, len(user_messages) / 5.0)

        return {
            "user_profile": user_profile,
            "procedural": procedural,
            "narrative": narrative,
            "semantic": semantic,
            "emotional": emotional,
            "extraction_confidence": confidence,
        }

    def _extract_user_profile(self, messages: list[str]) -> dict[str, Any]:
        """
        提取用户画像信息（内部方法）

        Args:
            messages: 用户消息列表

        Returns:
            用户画像数据
        """
        identity_tags: list[str] = []

        # 从消息中提取身份标签
        combined: str = " ".join(messages)

        if "架构" in combined:
            identity_tags.append("架构师")
        if "开发" in combined or "编程" in combined:
            identity_tags.append("开发者")
        if "设计" in combined:
            identity_tags.append("设计师")

        return {
            "identity": identity_tags if identity_tags else ["用户"],
            "technical_background": {
                "domains": [],
                "expertise_level": self._infer_technical_level(messages),
            },
            "communication_style": {
                "style": "直接" if len(combined) < 100 else "详细",
                "preference": "逻辑清晰",
                "dislike": [],
            },
            "decision_pattern": {
                "type": "审慎型" if "考虑" in combined else "果断型",
                "requires": "充分证据",
                "focus": "架构优先" if "架构" in combined else "平衡",
            },
        }

    def _extract_procedural(
        self, messages: list[str], history: list[ConversationTurn]
    ) -> dict[str, Any]:
        """
        提取程序性记忆（内部方法）

        Args:
            messages: 用户消息列表
            history: 对话历史

        Returns:
            程序性记忆数据
        """
        decision_patterns: list[dict[str, Any]] = []
        tool_usages: list[dict[str, Any]] = []

        combined: str = " ".join(messages)

        # 检测决策模式
        if "概念" in combined and "实现" in combined:
            decision_patterns.append(
                {
                    "pattern_id": f"dp_{uuid.uuid4().hex[:8]}",
                    "trigger_condition": "技术讨论",
                    "workflow": ["概念讨论", "设计", "实现"],
                    "confidence": 0.8,
                    "usage_count": 1,
                }
            )

        return {
            "decision_patterns": decision_patterns,
            "tool_usage_patterns": {
                "records": tool_usages,
            },
            "operation_preferences": {
                "communication_style": "直接",
                "detail_level": "中等",
            },
        }

    def _extract_narrative(
        self, messages: list[str], history: list[ConversationTurn]
    ) -> dict[str, Any]:
        """
        提取叙事记忆（内部方法）

        Args:
            messages: 用户消息列表
            history: 对话历史

        Returns:
            叙事记忆数据
        """
        milestones: list[dict[str, Any]] = []

        # 检测关键事件
        combined: str = " ".join(messages)

        if "开始" in combined or "启动" in combined:
            milestones.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "event": "项目启动",
                    "significance": "用户开始新任务",
                    "importance_score": 0.8,
                }
            )

        return {
            "growth_milestones": milestones,
            "current_identity": ["用户"],
        }

    def _extract_semantic(self, messages: list[str]) -> dict[str, Any]:
        """
        提取语义记忆（内部方法）

        Args:
            messages: 用户消息列表

        Returns:
            语义记忆数据
        """
        concepts: list[dict[str, Any]] = []

        combined: str = " ".join(messages)

        # 提取核心概念
        concept_keywords: list[str] = [
            "系统",
            "架构",
            "模块",
            "设计",
            "实现",
        ]

        for concept in concept_keywords:
            if concept in combined:
                concepts.append(
                    {
                        "concept": concept,
                        "definition": f"用户在对话中提及的概念：{concept}",
                        "usage_count": 1,
                        "confidence": 0.7,
                    }
                )

        return {
            "core_concepts": concepts,
        }

    def _extract_emotional(self, messages: list[str]) -> dict[str, Any]:
        """
        提取情感记忆（内部方法）

        Args:
            messages: 用户消息列表

        Returns:
            情感记忆数据
        """
        emotion_states: list[dict[str, Any]] = []

        combined: str = " ".join(messages)

        # 检测情感
        if "好" in combined or "棒" in combined:
            emotion_states.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "emotion_type": "positive",
                    "intensity": 0.7,
                    "trigger_context": "对话进展顺利",
                }
            )
        elif "问题" in combined or "困难" in combined:
            emotion_states.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "emotion_type": "frustrated",
                    "intensity": 0.5,
                    "trigger_context": "遇到问题",
                }
            )

        return {
            "emotion_states": emotion_states,
        }

    def get_conversation_history(
        self, session_id: str | None = None
    ) -> list[ConversationTurn]:
        """
        获取对话历史

        Args:
            session_id: 会话ID（可选，默认使用当前会话）

        Returns:
            对话历史列表
        """
        target_session: str = session_id or self._current_session_id

        for memory in self._memories.values():
            if isinstance(memory.data, PerceptionMemoryData) and memory.data.session_id == target_session:
                return memory.data.conversation_history

        return []

    def update_task_state(
        self,
        session_id: str,
        current_topic: str | None = None,
        pending_questions: list[str] | None = None,
        context_anchors: list[str] | None = None,
    ) -> None:
        """
        更新任务状态

        Args:
            session_id: 会话ID
            current_topic: 当前主题
            pending_questions: 待解决问题
            context_anchors: 上下文锚点
        """
        for memory in self._memories.values():
            if isinstance(memory.data, PerceptionMemoryData) and memory.data.session_id == session_id:
                if current_topic is not None:
                    memory.data.task_state.current_topic = current_topic
                if pending_questions is not None:
                    memory.data.task_state.pending_questions = pending_questions
                if context_anchors is not None:
                    memory.data.task_state.context_anchors = context_anchors
                break

    def cleanup_expired(self) -> int:
        """
        清理过期的感知记忆

        Returns:
            清理的记忆数量
        """
        now: datetime = datetime.now()
        expired_ids: list[str] = [
            mid
            for mid, mem in self._memories.items()
            if mem.expires_at and mem.expires_at < now
        ]

        for mid in expired_ids:
            del self._memories[mid]

        return len(expired_ids)


# ============================================================================
# 导出
# ============================================================================

__all__ = ["PerceptionMemoryStore"]
