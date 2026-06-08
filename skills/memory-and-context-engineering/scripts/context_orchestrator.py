"""
Agent Memory System - Context Orchestrator（上下文编排器）

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * redis: >=4.5.0
    - 用途：状态协调
  * pydantic: >=2.0.0
    - 用途：配置模型验证
- 标准配置文件:
  ```text
  # requirements.txt
  redis>=4.5.0
  pydantic>=2.0.0
  ```
=== 声明结束 ===

安全提醒：作为总控层，需确保所有子模块的安全性
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, Field

from .types import SemanticBucketType, MemoryCategory
from .redis_adapter import RedisAdapter, RedisConfig, create_redis_adapter
from .short_term_redis import ShortTermMemoryRedis, ShortTermRedisConfig
from .token_budget import (
    TokenBudgetManager,
    TokenBudgetConfig,
    TokenType,
    BudgetPolicy,
)


# ============================================================================
# 枚举类型
# ============================================================================


class ContextPriority(str, Enum):
    """上下文优先级"""

    CRITICAL = "critical"  # 关键：必须包含
    HIGH = "high"  # 高优先级
    MEDIUM = "medium"  # 中优先级
    LOW = "low"  # 低优先级
    OPTIONAL = "optional"  # 可选


class ContextSource(str, Enum):
    """上下文来源"""

    SYSTEM = "system"  # 系统指令
    USER_INPUT = "user_input"  # 用户输入
    SHORT_TERM_MEMORY = "short_term_memory"  # 短期记忆
    LONG_TERM_MEMORY = "long_term_memory"  # 长期记忆
    RETRIEVAL = "retrieval"  # 检索结果
    TOOL_RESULT = "tool_result"  # 工具返回
    INSIGHT = "insight"  # 洞察建议
    REFLECTION = "reflection"  # 反思信息


# ============================================================================
# 数据模型
# ============================================================================


class ContextBlock(BaseModel):
    """
    上下文块

    表示一个可被编排的上下文单元
    """

    source: ContextSource = Field(description="来源")
    priority: ContextPriority = Field(description="优先级")
    content: str = Field(description="内容")
    token_count: int = Field(default=0, description="Token 数量")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")

    # 用于排序和筛选
    relevance_score: float = Field(default=0.5, description="相关性分数")
    freshness_score: float = Field(default=1.0, description="新鲜度分数")


class ContextConfig(BaseModel):
    """
    Context Orchestrator 配置

    使用示例：
    ```python
    config = ContextConfig(
        max_context_tokens=32000,
        enable_auto_compression=True,
    )
    ```
    """

    # Token 预算
    max_context_tokens: int = Field(default=32000, description="最大上下文 Token 数")

    # 优先级权重
    priority_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.3,
            "optional": 0.1,
        },
        description="优先级权重",
    )

    # 自动压缩
    enable_auto_compression: bool = Field(default=True, description="启用自动压缩")

    # 检索配置
    max_retrieval_results: int = Field(default=10, description="最大检索结果数")

    # 短期记忆配置
    max_short_term_items: int = Field(default=50, description="最大短期记忆项数")


class PreparedContext(BaseModel):
    """
    准备好的上下文

    编排器输出的最终上下文结构
    """

    # 最终内容
    content: str = Field(description="完整上下文内容")
    token_count: int = Field(default=0, description="总 Token 数")

    # 组成明细
    blocks: list[ContextBlock] = Field(default_factory=list, description="上下文块列表")

    # 统计信息
    stats: dict[str, Any] = Field(default_factory=dict, description="统计信息")

    # 警告
    warnings: list[str] = Field(default_factory=list, description="警告信息")


# ============================================================================
# Context Orchestrator
# ============================================================================


class ContextOrchestrator:
    """
    上下文编排器（总控层）

    职责：
    - 决定"该让模型看到什么"
    - 决定"按什么顺序看到"
    - 决定"保留什么、丢掉什么"
    - 决定"何时补充什么"

    协调模块：
    - ShortTermMemoryRedis（短期记忆）
    - LongTermMemoryManager（长期记忆）
    - TokenBudgetManager（Token 预算）
    - GlobalStateCapture（状态捕捉）
    - ChainReasoningEnhancer（推理增强）

    使用示例：
    ```python
    from scripts.redis_adapter import create_redis_adapter
    from scripts.context_orchestrator import ContextOrchestrator

    # 初始化
    redis_adapter = create_redis_adapter()
    orchestrator = ContextOrchestrator(
        redis_adapter=redis_adapter,
        user_id="user123",
        session_id="session456",
    )

    # 准备上下文
    context = orchestrator.prepare_context(
        user_input="帮我分析这段代码的性能问题",
        system_instruction="你是一个代码分析专家",
    )

    print(f"Token 数量: {context.token_count}")
    print(f"上下文内容:\\n{context.content}")
    ```
    """

    def __init__(
        self,
        redis_adapter: RedisAdapter,
        user_id: str,
        session_id: str,
        config: ContextConfig | None = None,
        token_budget_config: TokenBudgetConfig | None = None,
    ) -> None:
        """
        初始化上下文编排器

        Args:
            redis_adapter: Redis 适配器
            user_id: 用户 ID
            session_id: 会话 ID
            config: 编排配置
            token_budget_config: Token 预算配置
        """
        self._redis = redis_adapter
        self._user_id = user_id
        self._session_id = session_id
        self._config = config or ContextConfig()

        # 初始化子模块
        self._short_term = ShortTermMemoryRedis(
            redis_adapter=redis_adapter,
            user_id=user_id,
            config=ShortTermRedisConfig(
                max_items=self._config.max_short_term_items,
            ),
        )

        self._token_budget = TokenBudgetManager(
            redis_adapter=redis_adapter,
            session_id=session_id,
            config=token_budget_config or TokenBudgetConfig(
                total_budget=self._config.max_context_tokens,
                policy=BudgetPolicy.COMPRESS,
            ),
        )

        # 注册的内容提供者
        self._providers: dict[str, Callable[[], list[ContextBlock]]] = {}

    # -----------------------------------------------------------------------
    # 提供者注册
    # -----------------------------------------------------------------------

    def register_provider(
        self,
        name: str,
        provider: Callable[[], list[ContextBlock]],
    ) -> None:
        """
        注册上下文提供者

        Args:
            name: 提供者名称
            provider: 提供者函数，返回 ContextBlock 列表
        """
        self._providers[name] = provider

    def unregister_provider(self, name: str) -> None:
        """注销上下文提供者"""
        self._providers.pop(name, None)

    # -----------------------------------------------------------------------
    # 核心方法：准备上下文
    # -----------------------------------------------------------------------

    def prepare_context(
        self,
        user_input: str,
        system_instruction: str | None = None,
        retrieval_results: list[str] | None = None,
        tool_results: list[str] | None = None,
        additional_blocks: list[ContextBlock] | None = None,
    ) -> PreparedContext:
        """
        准备完整上下文

        这是编排器的核心方法，执行以下步骤：
        1. 收集所有上下文块
        2. 计算 Token 预算
        3. 按优先级排序
        4. 应用压缩策略
        5. 组装最终上下文

        Args:
            user_input: 用户输入
            system_instruction: 系统指令
            retrieval_results: 检索结果列表
            tool_results: 工具返回列表
            additional_blocks: 额外的上下文块

        Returns:
            PreparedContext 准备好的上下文
        """
        # 开始会话
        self._token_budget.start_session()

        # 收集所有上下文块
        blocks: list[ContextBlock] = []

        # 1. 系统指令（最高优先级）
        if system_instruction:
            block = self._create_block(
                source=ContextSource.SYSTEM,
                priority=ContextPriority.CRITICAL,
                content=system_instruction,
            )
            blocks.append(block)
            self._token_budget.record_text(TokenType.SYSTEM, system_instruction)

        # 2. 用户输入
        block = self._create_block(
            source=ContextSource.USER_INPUT,
            priority=ContextPriority.CRITICAL,
            content=user_input,
        )
        blocks.append(block)
        self._token_budget.record_text(TokenType.USER_INPUT, user_input)

        # 3. 短期记忆
        short_term_blocks = self._collect_short_term_memory()
        blocks.extend(short_term_blocks)

        # 4. 检索结果
        if retrieval_results:
            retrieval_blocks = self._collect_retrieval_results(retrieval_results)
            blocks.extend(retrieval_blocks)

        # 5. 工具返回
        if tool_results:
            tool_blocks = self._collect_tool_results(tool_results)
            blocks.extend(tool_blocks)

        # 6. 注册的提供者
        for name, provider in self._providers.items():
            try:
                provider_blocks = provider()
                blocks.extend(provider_blocks)
            except Exception:
                pass

        # 7. 额外的上下文块
        if additional_blocks:
            blocks.extend(additional_blocks)

        # 应用预算和压缩
        final_blocks, warnings = self._apply_budget(blocks)

        # 组装最终上下文
        content, total_tokens = self._assemble_context(final_blocks)

        # 获取统计
        stats = self._token_budget.get_stats()

        return PreparedContext(
            content=content,
            token_count=total_tokens,
            blocks=final_blocks,
            stats=stats,
            warnings=warnings,
        )

    # -----------------------------------------------------------------------
    # 上下文收集
    # -----------------------------------------------------------------------

    def _create_block(
        self,
        source: ContextSource,
        priority: ContextPriority,
        content: str,
        relevance_score: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> ContextBlock:
        """创建上下文块"""
        token_count = self._token_budget.count(content)

        return ContextBlock(
            source=source,
            priority=priority,
            content=content,
            token_count=token_count,
            relevance_score=relevance_score,
            metadata=metadata or {},
        )

    def _collect_short_term_memory(self) -> list[ContextBlock]:
        """收集短期记忆"""
        blocks: list[ContextBlock] = []

        # 获取热数据
        hot_items = self._short_term.get_hot_items(
            limit=self._config.max_short_term_items
        )

        for item in hot_items:
            # 根据桶类型确定优先级
            bucket_type = SemanticBucketType(item.bucket_type)
            priority = self._bucket_to_priority(bucket_type)

            block = self._create_block(
                source=ContextSource.SHORT_TERM_MEMORY,
                priority=priority,
                content=item.content,
                relevance_score=item.relevance_score,
                metadata={
                    "item_id": item.item_id,
                    "bucket_type": item.bucket_type,
                    "topic_label": item.topic_label,
                    "access_count": item.access_count,
                },
            )
            blocks.append(block)
            self._token_budget.record_text(TokenType.MEMORY, item.content)

        return blocks

    def _collect_retrieval_results(
        self,
        results: list[str],
    ) -> list[ContextBlock]:
        """收集检索结果"""
        blocks: list[ContextBlock] = []

        for i, result in enumerate(results[:self._config.max_retrieval_results]):
            block = self._create_block(
                source=ContextSource.RETRIEVAL,
                priority=ContextPriority.MEDIUM,
                content=result,
                relevance_score=1.0 - (i * 0.1),  # 按顺序降低相关性
                metadata={"index": i},
            )
            blocks.append(block)
            self._token_budget.record_text(TokenType.RETRIEVAL, result)

        return blocks

    def _collect_tool_results(
        self,
        results: list[str],
    ) -> list[ContextBlock]:
        """收集工具返回"""
        blocks: list[ContextBlock] = []

        for i, result in enumerate(results):
            # 工具结果可能很长，优先级较低
            block = self._create_block(
                source=ContextSource.TOOL_RESULT,
                priority=ContextPriority.LOW,
                content=result,
                relevance_score=0.5,
                metadata={"index": i},
            )
            blocks.append(block)
            self._token_budget.record_text(TokenType.TOOL_RESULT, result)

        return blocks

    def _bucket_to_priority(self, bucket_type: SemanticBucketType) -> ContextPriority:
        """语义桶类型映射到优先级"""
        mapping = {
            SemanticBucketType.USER_INTENT: ContextPriority.HIGH,
            SemanticBucketType.DECISION_CONTEXT: ContextPriority.HIGH,
            SemanticBucketType.TASK_CONTEXT: ContextPriority.MEDIUM,
            SemanticBucketType.KNOWLEDGE_GAP: ContextPriority.MEDIUM,
            SemanticBucketType.EMOTIONAL_TRACE: ContextPriority.LOW,
        }
        return mapping.get(bucket_type, ContextPriority.MEDIUM)

    # -----------------------------------------------------------------------
    # 预算管理
    # -----------------------------------------------------------------------

    def _apply_budget(
        self,
        blocks: list[ContextBlock],
    ) -> tuple[list[ContextBlock], list[str]]:
        """
        应用 Token 预算

        策略：
        1. 按优先级排序
        2. 计算总 Token
        3. 如果超预算，按优先级裁剪

        Args:
            blocks: 所有上下文块

        Returns:
            (最终上下文块列表, 警告列表)
        """
        warnings: list[str] = []

        # 按优先级排序
        priority_order = {
            ContextPriority.CRITICAL: 0,
            ContextPriority.HIGH: 1,
            ContextPriority.MEDIUM: 2,
            ContextPriority.LOW: 3,
            ContextPriority.OPTIONAL: 4,
        }

        sorted_blocks = sorted(
            blocks,
            key=lambda b: (
                priority_order.get(b.priority, 3),
                -b.relevance_score,  # 同优先级按相关性降序
            ),
        )

        # 计算预算
        total_tokens = sum(b.token_count for b in sorted_blocks)
        max_tokens = self._config.max_context_tokens

        if total_tokens <= max_tokens:
            return sorted_blocks, warnings

        # 超预算，需要裁剪
        warnings.append(
            f"上下文超预算: {total_tokens} > {max_tokens}，将裁剪低优先级内容"
        )

        final_blocks: list[ContextBlock] = []
        current_tokens = 0

        for block in sorted_blocks:
            if current_tokens + block.token_count <= max_tokens:
                final_blocks.append(block)
                current_tokens += block.token_count
            elif block.priority == ContextPriority.CRITICAL:
                # 关键内容必须包含，即使超预算
                final_blocks.append(block)
                current_tokens += block.token_count
                warnings.append(
                    f"关键内容 [{block.source.value}] 超预算但仍保留"
                )
            elif self._config.enable_auto_compression:
                # 尝试压缩
                compressed = self._compress_block(block, max_tokens - current_tokens)
                if compressed:
                    final_blocks.append(compressed)
                    current_tokens += compressed.token_count
                    warnings.append(
                        f"内容 [{block.source.value}] 已压缩"
                    )

        return final_blocks, warnings

    def _compress_block(
        self,
        block: ContextBlock,
        target_tokens: int,
    ) -> ContextBlock | None:
        """
        压缩上下文块

        Args:
            block: 原始上下文块
            target_tokens: 目标 Token 数

        Returns:
            压缩后的上下文块，无法压缩返回 None
        """
        if target_tokens <= 0:
            return None

        content = block.content

        # 简单截断策略
        if len(content) > target_tokens * 4:
            truncated = content[: target_tokens * 4]
            truncated += "\n...[内容已截断]..."

            return ContextBlock(
                source=block.source,
                priority=block.priority,
                content=truncated,
                token_count=target_tokens,
                relevance_score=block.relevance_score * 0.8,
                metadata={**block.metadata, "compressed": True},
            )

        return None

    # -----------------------------------------------------------------------
    # 上下文组装
    # -----------------------------------------------------------------------

    def _assemble_context(
        self,
        blocks: list[ContextBlock],
    ) -> tuple[str, int]:
        """
        组装最终上下文

        Args:
            blocks: 上下文块列表

        Returns:
            (完整上下文字符串, 总 Token 数)
        """
        sections: list[str] = []
        total_tokens = 0

        # 按来源分组
        by_source: dict[ContextSource, list[ContextBlock]] = {}
        for block in blocks:
            if block.source not in by_source:
                by_source[block.source] = []
            by_source[block.source].append(block)

        # 系统指令
        if ContextSource.SYSTEM in by_source:
            for block in by_source[ContextSource.SYSTEM]:
                sections.append(f"[系统指令]\n{block.content}\n")
                total_tokens += block.token_count

        # 短期记忆
        if ContextSource.SHORT_TERM_MEMORY in by_source:
            sections.append("[相关记忆]")
            for block in by_source[ContextSource.SHORT_TERM_MEMORY]:
                sections.append(f"- {block.content}")
                total_tokens += block.token_count
            sections.append("")

        # 检索结果
        if ContextSource.RETRIEVAL in by_source:
            sections.append("[检索结果]")
            for block in by_source[ContextSource.RETRIEVAL]:
                sections.append(f"- {block.content}")
                total_tokens += block.token_count
            sections.append("")

        # 工具返回
        if ContextSource.TOOL_RESULT in by_source:
            sections.append("[工具返回]")
            for block in by_source[ContextSource.TOOL_RESULT]:
                sections.append(f"{block.content}")
                total_tokens += block.token_count
            sections.append("")

        # 洞察
        if ContextSource.INSIGHT in by_source:
            sections.append("[系统建议]")
            for block in by_source[ContextSource.INSIGHT]:
                sections.append(f"- {block.content}")
                total_tokens += block.token_count
            sections.append("")

        # 用户输入
        if ContextSource.USER_INPUT in by_source:
            for block in by_source[ContextSource.USER_INPUT]:
                sections.append(f"[用户输入]\n{block.content}")
                total_tokens += block.token_count

        return "\n".join(sections), total_tokens

    # -----------------------------------------------------------------------
    # 便捷方法
    # -----------------------------------------------------------------------

    def get_short_term_memory(self) -> ShortTermMemoryRedis:
        """获取短期记忆管理器"""
        return self._short_term

    def get_token_budget(self) -> TokenBudgetManager:
        """获取 Token 预算管理器"""
        return self._token_budget

    def store_memory(
        self,
        content: str,
        bucket_type: SemanticBucketType,
        topic_label: str | None = None,
        relevance_score: float = 0.5,
    ) -> str:
        """
        存储到短期记忆（便捷方法）

        Args:
            content: 内容
            bucket_type: 语义桶类型
            topic_label: 话题标签
            relevance_score: 相关性分数

        Returns:
            记忆项 ID
        """
        return self._short_term.store(
            content=content,
            bucket_type=bucket_type,
            topic_label=topic_label,
            relevance_score=relevance_score,
        )

    def end_session(self) -> dict[str, Any]:
        """
        结束会话

        Returns:
            会话统计
        """
        return self._token_budget.end_session()


# ============================================================================
# 工厂函数
# ============================================================================


def create_context_orchestrator(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    user_id: str = "default_user",
    session_id: str = "default_session",
    max_context_tokens: int = 32000,
) -> ContextOrchestrator:
    """
    创建上下文编排器

    Args:
        redis_host: Redis 主机
        redis_port: Redis 端口
        user_id: 用户 ID
        session_id: 会话 ID
        max_context_tokens: 最大上下文 Token 数

    Returns:
        ContextOrchestrator 实例
    """
    redis_adapter = create_redis_adapter(host=redis_host, port=redis_port)
    config = ContextConfig(max_context_tokens=max_context_tokens)

    return ContextOrchestrator(
        redis_adapter=redis_adapter,
        user_id=user_id,
        session_id=session_id,
        config=config,
    )


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "ContextPriority",
    "ContextSource",
    "ContextBlock",
    "ContextConfig",
    "PreparedContext",
    "ContextOrchestrator",
    "create_context_orchestrator",
]
