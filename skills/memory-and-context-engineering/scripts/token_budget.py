"""
Agent Memory System - Token 预算管理器

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * redis: >=4.5.0
    - 用途：原子计数器
  * pydantic: >=2.0.0
    - 用途：配置模型验证
  * tiktoken: >=0.5.0 (可选)
    - 用途：精确 Token 计数
- 标准配置文件:
  ```text
  # requirements.txt
  redis>=4.5.0
  pydantic>=2.0.0
  tiktoken>=0.5.0
  ```
=== 声明结束 ===

安全提醒：Token 预算管理有助于控制成本，但不应完全依赖此模块进行计费
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .redis_adapter import RedisAdapter, create_redis_adapter


# ============================================================================
# 枚举类型
# ============================================================================


class TokenType(str, Enum):
    """Token 类型"""

    SYSTEM = "system"  # 系统指令
    MEMORY = "memory"  # 记忆上下文
    RETRIEVAL = "retrieval"  # 检索结果
    TOOL_RESULT = "tool_result"  # 工具返回
    USER_INPUT = "user_input"  # 用户输入
    RESPONSE = "response"  # 模型响应


class BudgetPolicy(str, Enum):
    """预算策略"""

    STRICT = "strict"  # 严格模式：超预算拒绝
    COMPRESS = "compress"  # 压缩模式：超预算压缩
    TRUNCATE = "truncate"  # 截断模式：超预算截断
    WARN = "warn"  # 警告模式：超预算警告但继续


# ============================================================================
# 配置模型
# ============================================================================


class TokenBudgetConfig(BaseModel):
    """
    Token 预算配置

    使用示例：
    ```python
    config = TokenBudgetConfig(
        total_budget=128000,  # 总预算（对应模型上下文窗口）
        memory_budget_ratio=0.3,  # 记忆分配 30%
        retrieval_budget_ratio=0.2,  # 检索分配 20%
        tool_result_budget_ratio=0.2,  # 工具结果分配 20%
    )
    ```
    """

    # 总预算
    total_budget: int = Field(default=128000, description="总 Token 预算")

    # 各模块预算比例
    system_budget_ratio: float = Field(default=0.1, description="系统指令预算比例")
    memory_budget_ratio: float = Field(default=0.3, description="记忆上下文预算比例")
    retrieval_budget_ratio: float = Field(default=0.2, description="检索结果预算比例")
    tool_result_budget_ratio: float = Field(default=0.2, description="工具返回预算比例")
    user_input_budget_ratio: float = Field(default=0.1, description="用户输入预算比例")
    response_budget_ratio: float = Field(default=0.1, description="响应预算比例")

    # 策略
    policy: BudgetPolicy = Field(default=BudgetPolicy.COMPRESS, description="超预算策略")

    # 警告阈值
    warn_threshold: float = Field(default=0.8, description="警告阈值（比例）")

    # 模型编码
    model_encoding: str = Field(default="cl100k_base", description="tiktoken 编码名称")

    def get_budget(self, token_type: TokenType) -> int:
        """获取指定类型的预算"""
        ratios = {
            TokenType.SYSTEM: self.system_budget_ratio,
            TokenType.MEMORY: self.memory_budget_ratio,
            TokenType.RETRIEVAL: self.retrieval_budget_ratio,
            TokenType.TOOL_RESULT: self.tool_result_budget_ratio,
            TokenType.USER_INPUT: self.user_input_budget_ratio,
            TokenType.RESPONSE: self.response_budget_ratio,
        }
        ratio = ratios.get(token_type, 0.1)
        return int(self.total_budget * ratio)


# ============================================================================
# Token 计数器
# ============================================================================


class TokenCounter:
    """
    Token 计数器

    支持：
    - 精确计数（tiktoken）
    - 估算计数（字符数 / 4）

    使用示例：
    ```python
    counter = TokenCounter(encoding="cl100k_base")

    # 精确计数
    count = counter.count("Hello, world!")

    # 批量计数
    total = counter.count_batch(["text1", "text2"])
    ```
    """

    def __init__(self, encoding: str = "cl100k_base") -> None:
        """
        初始化计数器

        Args:
            encoding: tiktoken 编码名称
        """
        self._encoding = encoding
        self._encoder: Any | None = None

        # 尝试加载 tiktoken
        try:
            import tiktoken
            self._encoder = tiktoken.get_encoding(encoding)
        except ImportError:
            self._encoder = None

    def count(self, text: str) -> int:
        """
        计算 Token 数量

        Args:
            text: 文本

        Returns:
            Token 数量
        """
        if self._encoder is not None:
            try:
                return len(self._encoder.encode(text))
            except Exception:
                pass

        # 估算：约 4 字符 = 1 Token
        return len(text) // 4 + 1

    def count_batch(self, texts: list[str]) -> int:
        """
        批量计算 Token 数量

        Args:
            texts: 文本列表

        Returns:
            总 Token 数量
        """
        return sum(self.count(text) for text in texts)

    def estimate_for_json(self, data: dict[str, Any] | list[Any]) -> int:
        """
        估算 JSON 数据的 Token 数量

        Args:
            data: JSON 数据

        Returns:
            Token 数量
        """
        import json
        text = json.dumps(data, ensure_ascii=False)
        return self.count(text)


# ============================================================================
# Token 预算管理器
# ============================================================================


class TokenBudgetManager:
    """
    Token 预算管理器

    特性：
    - 基于 Redis 的原子计数
    - 实时预算检查
    - 多模块预算分配
    - 超预算策略处理

    使用示例：
    ```python
    from scripts.redis_adapter import create_redis_adapter
    from scripts.token_budget import TokenBudgetManager, TokenBudgetConfig, TokenType

    # 初始化
    redis_adapter = create_redis_adapter(host="localhost", port=6379)
    config = TokenBudgetConfig(total_budget=128000)
    manager = TokenBudgetManager(
        redis_adapter=redis_adapter,
        session_id="session_123",
        config=config,
    )

    # 开始新会话
    manager.start_session()

    # 记录 Token 使用
    manager.record(TokenType.SYSTEM, 500)
    manager.record(TokenType.MEMORY, 3000)

    # 检查预算
    if manager.can_use(TokenType.RETRIEVAL, 2000):
        # 执行检索...
        manager.record(TokenType.RETRIEVAL, 2000)

    # 获取统计
    stats = manager.get_stats()
    print(f"已使用: {stats['used']}, 剩余: {stats['remaining']}")

    # 结束会话
    manager.end_session()
    ```
    """

    def __init__(
        self,
        redis_adapter: RedisAdapter,
        session_id: str,
        config: TokenBudgetConfig | None = None,
    ) -> None:
        """
        初始化预算管理器

        Args:
            redis_adapter: Redis 适配器
            session_id: 会话 ID
            config: 配置参数
        """
        self._redis = redis_adapter
        self._session_id = session_id
        self._config = config or TokenBudgetConfig()
        self._counter = TokenCounter(self._config.model_encoding)

        # 计数器 Key
        self._counter_key = self._redis.keys.token_counter(session_id)
        self._budget_key = self._redis.keys.token_budget(session_id)

    # -----------------------------------------------------------------------
    # 会话管理
    # -----------------------------------------------------------------------

    def start_session(self) -> None:
        """开始新会话（重置计数器）"""
        # 初始化各类型计数器
        for token_type in TokenType:
            key = f"{self._counter_key}:{token_type.value}"
            self._redis.set(key, "0")

        # 设置总预算
        self._redis.hset_multi(self._budget_key, {
            "total": str(self._config.total_budget),
            "policy": self._config.policy.value,
        })

    def end_session(self) -> dict[str, Any]:
        """
        结束会话

        Returns:
            会话统计
        """
        stats = self.get_stats()

        # 清理计数器
        for token_type in TokenType:
            key = f"{self._counter_key}:{token_type.value}"
            self._redis.delete(key)

        self._redis.delete(self._budget_key)

        return stats

    # -----------------------------------------------------------------------
    # Token 记录
    # -----------------------------------------------------------------------

    def record(self, token_type: TokenType, count: int) -> int:
        """
        记录 Token 使用

        Args:
            token_type: Token 类型
            count: Token 数量

        Returns:
            更新后的总使用量
        """
        key = f"{self._counter_key}:{token_type.value}"
        new_value = self._redis.incr(key, count)

        # 同时更新总计数器
        total_key = f"{self._counter_key}:total"
        self._redis.incr(total_key, count)

        return new_value or 0

    def record_text(self, token_type: TokenType, text: str) -> int:
        """
        记录文本的 Token 使用

        Args:
            token_type: Token 类型
            text: 文本

        Returns:
            Token 数量
        """
        count = self._counter.count(text)
        self.record(token_type, count)
        return count

    # -----------------------------------------------------------------------
    # 预算检查
    # -----------------------------------------------------------------------

    def get_used(self, token_type: TokenType | None = None) -> int:
        """
        获取已使用的 Token 数量

        Args:
            token_type: Token 类型（None 表示总使用量）

        Returns:
            Token 数量
        """
        if token_type is None:
            key = f"{self._counter_key}:total"
        else:
            key = f"{self._counter_key}:{token_type.value}"

        value = self._redis.get(key)
        return int(value) if value else 0

    def get_remaining(self, token_type: TokenType | None = None) -> int:
        """
        获取剩余 Token 预算

        Args:
            token_type: Token 类型（None 表示总剩余）

        Returns:
            剩余 Token 数量
        """
        if token_type is None:
            used = self.get_used()
            return self._config.total_budget - used
        else:
            budget = self._config.get_budget(token_type)
            used = self.get_used(token_type)
            return budget - used

    def can_use(self, token_type: TokenType, count: int) -> bool:
        """
        检查是否可以使用指定数量的 Token

        Args:
            token_type: Token 类型
            count: 需要的 Token 数量

        Returns:
            是否可以
        """
        remaining = self.get_remaining(token_type)
        return remaining >= count

    def check_policy(self, token_type: TokenType, count: int) -> dict[str, Any]:
        """
        检查预算策略

        Args:
            token_type: Token 类型
            count: 需要的 Token 数量

        Returns:
            {
                "allowed": bool,
                "action": str,  # "proceed", "compress", "truncate", "warn"
                "remaining": int,
                "ratio": float,
            }
        """
        remaining = self.get_remaining(token_type)
        ratio = count / remaining if remaining > 0 else float("inf")

        result: dict[str, Any] = {
            "remaining": remaining,
            "ratio": ratio,
        }

        if remaining >= count:
            result["allowed"] = True
            result["action"] = "proceed"
        else:
            policy = self._config.policy

            if policy == BudgetPolicy.STRICT:
                result["allowed"] = False
                result["action"] = "reject"
            elif policy == BudgetPolicy.COMPRESS:
                result["allowed"] = True
                result["action"] = "compress"
            elif policy == BudgetPolicy.TRUNCATE:
                result["allowed"] = True
                result["action"] = "truncate"
            else:  # WARN
                result["allowed"] = True
                result["action"] = "warn"

        return result

    # -----------------------------------------------------------------------
    # 统计信息
    # -----------------------------------------------------------------------

    def get_stats(self) -> dict[str, Any]:
        """
        获取统计信息

        Returns:
            {
                "total_budget": int,
                "used": int,
                "remaining": int,
                "usage_ratio": float,
                "by_type": {TokenType: int},
                "is_over_budget": bool,
                "should_warn": bool,
            }
        """
        used = self.get_used()
        remaining = self.get_remaining()
        usage_ratio = used / self._config.total_budget if self._config.total_budget > 0 else 0

        by_type: dict[str, int] = {}
        for token_type in TokenType:
            by_type[token_type.value] = self.get_used(token_type)

        return {
            "total_budget": self._config.total_budget,
            "used": used,
            "remaining": remaining,
            "usage_ratio": round(usage_ratio, 4),
            "by_type": by_type,
            "is_over_budget": used > self._config.total_budget,
            "should_warn": usage_ratio >= self._config.warn_threshold,
        }

    def get_allocation(self) -> dict[str, int]:
        """
        获取预算分配

        Returns:
            各类型的预算分配
        """
        allocation: dict[str, int] = {}
        for token_type in TokenType:
            allocation[token_type.value] = self._config.get_budget(token_type)
        return allocation

    # -----------------------------------------------------------------------
    # Token 计数工具
    # -----------------------------------------------------------------------

    def count(self, text: str) -> int:
        """
        计算 Token 数量

        Args:
            text: 文本

        Returns:
            Token 数量
        """
        return self._counter.count(text)

    def count_json(self, data: dict[str, Any] | list[Any]) -> int:
        """
        计算 JSON 数据的 Token 数量

        Args:
            data: JSON 数据

        Returns:
            Token 数量
        """
        return self._counter.estimate_for_json(data)

    # -----------------------------------------------------------------------
    # 辅助方法
    # -----------------------------------------------------------------------

    def suggest_compression(self, token_type: TokenType, text: str) -> dict[str, Any]:
        """
        建议压缩策略

        Args:
            token_type: Token 类型
            text: 文本

        Returns:
            {
                "original_count": int,
                "budget_remaining": int,
                "target_count": int,
                "compression_ratio": float,
                "suggestion": str,
            }
        """
        original_count = self._counter.count(text)
        remaining = self.get_remaining(token_type)

        if original_count <= remaining:
            return {
                "original_count": original_count,
                "budget_remaining": remaining,
                "target_count": original_count,
                "compression_ratio": 1.0,
                "suggestion": "无需压缩",
            }

        compression_ratio = remaining / original_count
        target_count = remaining

        suggestions = {
            TokenType.MEMORY: "建议使用话题摘要代替完整记忆",
            TokenType.RETRIEVAL: "建议仅保留最相关的检索结果",
            TokenType.TOOL_RESULT: "建议压缩日志输出，保留关键信息",
            TokenType.SYSTEM: "建议精简系统指令",
            TokenType.USER_INPUT: "用户输入无法压缩",
            TokenType.RESPONSE: "建议限制响应长度",
        }

        return {
            "original_count": original_count,
            "budget_remaining": remaining,
            "target_count": target_count,
            "compression_ratio": round(compression_ratio, 2),
            "suggestion": suggestions.get(token_type, "建议减少内容量"),
        }


# ============================================================================
# 工厂函数
# ============================================================================


def create_token_budget_manager(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    session_id: str = "default_session",
    total_budget: int = 128000,
) -> TokenBudgetManager:
    """
    创建 Token 预算管理器

    Args:
        redis_host: Redis 主机
        redis_port: Redis 端口
        session_id: 会话 ID
        total_budget: 总 Token 预算

    Returns:
        TokenBudgetManager 实例
    """
    redis_adapter = create_redis_adapter(host=redis_host, port=redis_port)
    config = TokenBudgetConfig(total_budget=total_budget)

    return TokenBudgetManager(
        redis_adapter=redis_adapter,
        session_id=session_id,
        config=config,
    )


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "TokenType",
    "BudgetPolicy",
    "TokenBudgetConfig",
    "TokenCounter",
    "TokenBudgetManager",
    "create_token_budget_manager",
]
