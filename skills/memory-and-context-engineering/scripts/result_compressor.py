"""
Agent Memory System - Result Compressor（结果压缩器）

=== 功能说明 ===
对应 Context Engineering 核心能力：压缩

实现文档要求：
- "把噪声信息压成因果结构"
- "保留决策依据、关键异常、已完成步骤、未解决问题、影响下一步的约束"

核心能力：
1. 工具结果压缩 - 提取关键信息，去除冗余
2. 日志压缩 - 提取错误、警告、摘要
3. 因果结构提取 - 识别问题→原因→解决方案链条
4. JSON 压缩 - 提取关键字段，去除冗余
5. 压缩质量评估 - 评估信息保留度

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证
  * tiktoken: >=0.5.0
    - 用途：Token 计数
- 标准配置文件:
  ```text
  # requirements.txt
  pydantic>=2.0.0
  tiktoken>=0.5.0
  ```
=== 声明结束 ===

安全提醒：压缩过程不应丢失关键决策信息
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from .token_budget import TokenBudgetManager


# ============================================================================
# 枚举类型
# ============================================================================


class ContentType(str, Enum):
    """内容类型"""

    LOG = "log"                    # 日志输出
    JSON = "json"                  # JSON 数据
    TEXT = "text"                  # 纯文本
    MIXED = "mixed"                # 混合内容
    STACK_TRACE = "stack_trace"    # 堆栈跟踪
    ERROR_REPORT = "error_report"  # 错误报告


class ErrorSeverity(str, Enum):
    """错误严重程度"""

    CRITICAL = "critical"  # 致命错误
    HIGH = "high"          # 高严重性
    MEDIUM = "medium"      # 中严重性
    LOW = "low"            # 低严重性
    INFO = "info"          # 信息


class CompressionStrategy(str, Enum):
    """压缩策略"""

    AGGRESSIVE = "aggressive"    # 激进压缩（高压缩率）
    BALANCED = "balanced"        # 平衡压缩
    CONSERVATIVE = "conservative"  # 保守压缩（低压缩率）
    CAUSAL = "causal"            # 因果结构提取


# ============================================================================
# 数据模型
# ============================================================================


class ErrorInfo(BaseModel):
    """错误信息"""

    error_type: str = Field(description="错误类型")
    error_message: str = Field(description="错误消息")
    severity: ErrorSeverity = Field(default=ErrorSeverity.MEDIUM, description="严重程度")
    line_number: Optional[int] = Field(default=None, description="行号")
    file_name: Optional[str] = Field(default=None, description="文件名")
    stack_trace: Optional[str] = Field(default=None, description="堆栈跟踪")
    context: Optional[str] = Field(default=None, description="上下文")


class WarningInfo(BaseModel):
    """警告信息"""

    warning_type: str = Field(description="警告类型")
    warning_message: str = Field(description="警告消息")
    line_number: Optional[int] = Field(default=None, description="行号")


class CausalChain(BaseModel):
    """因果链"""

    problem: str = Field(description="问题描述")
    cause: str = Field(description="原因")
    solution: Optional[str] = Field(default=None, description="解决方案")
    confidence: float = Field(ge=0.0, le=1.0, default=0.5, description="置信度")


class DecisionPoint(BaseModel):
    """决策点"""

    decision: str = Field(description="决策内容")
    reason: str = Field(description="决策原因")
    alternatives: list[str] = Field(default_factory=list, description="备选方案")
    impact: Optional[str] = Field(default=None, description="影响")


class CompressedResult(BaseModel):
    """压缩结果"""

    # 压缩摘要
    summary: str = Field(description="压缩后的摘要")
    original_tokens: int = Field(description="原始 Token 数")
    compressed_tokens: int = Field(description="压缩后 Token 数")
    compression_ratio: float = Field(description="压缩率")

    # 提取的结构化信息
    errors: list[ErrorInfo] = Field(default_factory=list, description="错误列表")
    warnings: list[WarningInfo] = Field(default_factory=list, description="警告列表")
    causal_chains: list[CausalChain] = Field(default_factory=list, description="因果链")
    decision_points: list[DecisionPoint] = Field(default_factory=list, description="决策点")

    # 质量评估
    information_retention: float = Field(
        ge=0.0, le=1.0, default=0.8, description="信息保留度"
    )
    key_info_preserved: bool = Field(default=True, description="关键信息是否保留")

    # 元数据
    content_type: ContentType = Field(description="内容类型")
    strategy: CompressionStrategy = Field(description="压缩策略")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class CompressionConfig(BaseModel):
    """压缩配置"""

    # 压缩策略
    strategy: CompressionStrategy = Field(
        default=CompressionStrategy.BALANCED, description="压缩策略"
    )

    # 目标压缩率
    target_ratio: float = Field(
        ge=0.1, le=1.0, default=0.3, description="目标压缩率"
    )

    # 最大错误数
    max_errors: int = Field(default=10, description="最大错误数量")

    # 最大警告数
    max_warnings: int = Field(default=10, description="最大警告数量")

    # 是否保留堆栈跟踪
    preserve_stack_trace: bool = Field(default=False, description="保留堆栈跟踪")

    # 关键字列表（匹配这些字的内容不被压缩）
    keywords_to_preserve: list[str] = Field(
        default_factory=lambda: [
            "error", "fail", "exception", "critical", "fatal",
            "warning", "timeout", "refused", "denied",
        ],
        description="保留关键字",
    )


# ============================================================================
# Result Compressor
# ============================================================================


class ResultCompressor:
    """
    结果压缩器

    实现文档要求："把噪声信息压成因果结构"

    核心能力：
    1. 压缩工具返回结果（JSON/文本）
    2. 提取关键错误和异常
    3. 构建因果结构（问题→原因→解决方案）
    4. 评估压缩质量

    使用示例：
    ```python
    from scripts.result_compressor import ResultCompressor

    compressor = ResultCompressor()

    # 压缩工具结果
    result = compressor.compress_tool_result(
        content=long_log_content,
        target_tokens=1000,
    )

    print(f"压缩率: {result.compression_ratio:.2%}")
    print(f"信息保留: {result.information_retention:.2%}")
    print(f"摘要:\\n{result.summary}")

    # 提取因果结构
    if result.causal_chains:
        for chain in result.causal_chains:
            print(f"问题: {chain.problem}")
            print(f"原因: {chain.cause}")
            if chain.solution:
                print(f"解决方案: {chain.solution}")
    ```
    """

    def __init__(
        self,
        config: CompressionConfig | None = None,
        token_budget: TokenBudgetManager | None = None,
    ) -> None:
        """
        初始化结果压缩器

        Args:
            config: 压缩配置
            token_budget: Token 预算管理器（可选）
        """
        self._config = config or CompressionConfig()
        self._token_budget = token_budget

        # 错误模式正则
        self._error_patterns = [
            # Python 错误
            (r"(\w+Error):\s*(.+)", "python_error"),
            (r"(\w+Exception):\s*(.+)", "python_exception"),
            (r"Traceback \(most recent call last\)", "traceback"),
            # 通用错误
            (r"ERROR[:\s]+(.+)", "error_log"),
            (r"FATAL[:\s]+(.+)", "fatal_log"),
            (r"CRITICAL[:\s]+(.+)", "critical_log"),
            # HTTP 错误
            (r"HTTP/\d\.\d\s+(\d{3})\s+(.+)", "http_error"),
            # 系统错误
            (r"Failed to (.+)", "failure"),
            (r"Timeout[:\s]+(.+)", "timeout"),
            (r"Connection refused", "connection_refused"),
            (r"Permission denied", "permission_denied"),
        ]

        # 警告模式正则
        self._warning_patterns = [
            (r"WARNING[:\s]+(.+)", "warning_log"),
            (r"WARN[:\s]+(.+)", "warn_log"),
            (r"DeprecationWarning[:\s]+(.+)", "deprecation"),
        ]

        # 因果模式正则
        self._causal_patterns = [
            # 明确的因果
            (r"because\s+(.+)", "explicit"),
            (r"caused by\s+(.+)", "explicit"),
            (r"due to\s+(.+)", "explicit"),
            (r"reason:\s*(.+)", "explicit"),
            # 推断的因果
            (r"failed to (.+),\s*(.+)", "inferred"),
        ]

    # -----------------------------------------------------------------------
    # 核心方法：压缩工具结果
    # -----------------------------------------------------------------------

    def compress_tool_result(
        self,
        content: str,
        target_tokens: int | None = None,
        strategy: CompressionStrategy | None = None,
    ) -> CompressedResult:
        """
        压缩工具返回结果

        根据内容类型自动选择最佳压缩策略：
        1. 识别内容类型（日志/JSON/文本/混合）
        2. 提取关键信息（错误、警告、因果）
        3. 构建压缩摘要
        4. 评估压缩质量

        Args:
            content: 原始内容
            target_tokens: 目标 Token 数（可选）
            strategy: 压缩策略（可选）

        Returns:
            CompressedResult 压缩结果
        """
        # 确定策略
        actual_strategy = strategy or self._config.strategy

        # 识别内容类型
        content_type = self._detect_content_type(content)

        # 计算 Token
        original_tokens = self._count_tokens(content)
        actual_target = target_tokens or int(original_tokens * self._config.target_ratio)

        # 根据内容类型选择压缩方法
        if content_type == ContentType.JSON:
            return self._compress_json(
                content=content,
                original_tokens=original_tokens,
                target_tokens=actual_target,
                strategy=actual_strategy,
            )
        elif content_type == ContentType.LOG:
            return self._compress_log(
                content=content,
                original_tokens=original_tokens,
                target_tokens=actual_target,
                strategy=actual_strategy,
            )
        elif content_type == ContentType.STACK_TRACE:
            return self._compress_stack_trace(
                content=content,
                original_tokens=original_tokens,
                target_tokens=actual_target,
                strategy=actual_strategy,
            )
        else:
            return self._compress_text(
                content=content,
                original_tokens=original_tokens,
                target_tokens=actual_target,
                strategy=actual_strategy,
            )

    # -----------------------------------------------------------------------
    # 内容类型检测
    # -----------------------------------------------------------------------

    def _detect_content_type(self, content: str) -> ContentType:
        """
        检测内容类型

        Args:
            content: 原始内容

        Returns:
            ContentType 内容类型
        """
        content = content.strip()

        # 检测 JSON
        if content.startswith("{") or content.startswith("["):
            try:
                json.loads(content)
                return ContentType.JSON
            except json.JSONDecodeError:
                pass

        # 检测堆栈跟踪
        if "Traceback (most recent call last)" in content:
            return ContentType.STACK_TRACE

        # 检测日志
        log_indicators = ["ERROR", "WARNING", "INFO", "DEBUG", "FATAL", "CRITICAL"]
        if any(indicator in content for indicator in log_indicators):
            return ContentType.LOG

        # 检测错误报告
        if "Error:" in content or "Exception:" in content:
            return ContentType.ERROR_REPORT

        return ContentType.TEXT

    # -----------------------------------------------------------------------
    # 日志压缩
    # -----------------------------------------------------------------------

    def _compress_log(
        self,
        content: str,
        original_tokens: int,
        target_tokens: int,
        strategy: CompressionStrategy,
    ) -> CompressedResult:
        """
        压缩日志内容

        策略：
        1. 提取所有错误和警告
        2. 提取因果结构
        3. 生成摘要

        Args:
            content: 原始内容
            original_tokens: 原始 Token 数
            target_tokens: 目标 Token 数
            strategy: 压缩策略

        Returns:
            CompressedResult 压缩结果
        """
        # 提取错误
        errors = self._extract_errors(content)

        # 提取警告
        warnings = self._extract_warnings(content)

        # 提取因果结构
        causal_chains = self._extract_causal_chains(content)

        # 构建摘要
        summary_parts: list[str] = []

        # 添加错误摘要
        if errors:
            summary_parts.append("【错误摘要】")
            for i, error in enumerate(errors[:self._config.max_errors]):
                error_line = f"{i+1}. [{error.severity.value}] {error.error_type}: {error.error_message}"
                if error.file_name:
                    error_line += f" (file: {error.file_name}"
                    if error.line_number:
                        error_line += f", line: {error.line_number}"
                    error_line += ")"
                summary_parts.append(error_line)

        # 添加警告摘要
        if warnings:
            summary_parts.append("\n【警告摘要】")
            for i, warning in enumerate(warnings[:self._config.max_warnings]):
                warning_line = f"{i+1}. {warning.warning_type}: {warning.warning_message}"
                summary_parts.append(warning_line)

        # 添加因果结构
        if causal_chains:
            summary_parts.append("\n【因果分析】")
            for chain in causal_chains:
                chain_line = f"- 问题: {chain.problem}"
                chain_line += f"\n  原因: {chain.cause}"
                if chain.solution:
                    chain_line += f"\n  建议: {chain.solution}"
                summary_parts.append(chain_line)

        summary = "\n".join(summary_parts)

        # 计算压缩后 Token
        compressed_tokens = self._count_tokens(summary)

        # 如果还是超预算，进一步压缩
        if compressed_tokens > target_tokens:
            summary = self._further_compress(summary, target_tokens)
            compressed_tokens = self._count_tokens(summary)

        # 评估信息保留度
        information_retention = self._estimate_retention(
            original_content=content,
            compressed_content=summary,
            errors=errors,
            warnings=warnings,
            causal_chains=causal_chains,
        )

        return CompressedResult(
            summary=summary,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            errors=errors,
            warnings=warnings,
            causal_chains=causal_chains,
            information_retention=information_retention,
            key_info_preserved=len(errors) > 0 or len(warnings) > 0,
            content_type=ContentType.LOG,
            strategy=strategy,
        )

    # -----------------------------------------------------------------------
    # JSON 压缩
    # -----------------------------------------------------------------------

    def _compress_json(
        self,
        content: str,
        original_tokens: int,
        target_tokens: int,
        strategy: CompressionStrategy,
    ) -> CompressedResult:
        """
        压缩 JSON 内容

        策略：
        1. 提取关键字段
        2. 去除冗余字段
        3. 保持可读性

        Args:
            content: 原始内容
            original_tokens: 原始 Token 数
            target_tokens: 目标 Token 数
            strategy: 压缩策略

        Returns:
            CompressedResult 压缩结果
        """
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return self._compress_text(content, original_tokens, target_tokens, strategy)

        # 提取关键信息
        key_fields = self._extract_key_json_fields(data)

        # 构建压缩后的 JSON
        compressed_data = self._build_compressed_json(data, key_fields, strategy)

        # 格式化
        summary = json.dumps(compressed_data, ensure_ascii=False, indent=2)
        compressed_tokens = self._count_tokens(summary)

        # 检测是否有错误字段
        errors = self._extract_json_errors(data)

        # 评估信息保留度
        information_retention = self._estimate_json_retention(
            original_data=data,
            compressed_data=compressed_data,
        )

        return CompressedResult(
            summary=summary,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            errors=errors,
            information_retention=information_retention,
            key_info_preserved=True,
            content_type=ContentType.JSON,
            strategy=strategy,
        )

    def _extract_key_json_fields(self, data: Any, path: str = "") -> list[str]:
        """提取 JSON 关键字段路径"""
        key_fields: list[str] = []

        # 关键字段名称
        key_names = {
            "error", "errors", "error_message", "error_code",
            "status", "status_code", "code",
            "message", "msg", "reason",
            "result", "results", "data",
            "success", "failed", "is_success",
            "total", "count", "size",
            "id", "name", "type",
        }

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key

                # 检查是否是关键字段
                if key.lower() in key_names:
                    key_fields.append(current_path)

                # 递归
                if isinstance(value, (dict, list)):
                    key_fields.extend(self._extract_key_json_fields(value, current_path))

        elif isinstance(data, list) and len(data) > 0:
            # 只处理第一个元素（假设列表元素结构相同）
            key_fields.extend(self._extract_key_json_fields(data[0], f"{path}[0]"))

        return key_fields

    def _build_compressed_json(
        self,
        data: Any,
        key_fields: list[str],
        strategy: CompressionStrategy,
    ) -> Any:
        """构建压缩后的 JSON"""
        if isinstance(data, dict):
            result = {}

            for key, value in data.items():
                current_path = key

                # 决定是否保留
                should_keep = (
                    current_path in key_fields
                    or strategy == CompressionStrategy.CONSERVATIVE
                    or (strategy == CompressionStrategy.BALANCED and key.lower() in {
                        "error", "status", "message", "code", "result", "data"
                    })
                )

                if should_keep:
                    if isinstance(value, (dict, list)):
                        result[key] = self._build_compressed_json(value, key_fields, strategy)
                    else:
                        result[key] = value
                elif strategy == CompressionStrategy.AGGRESSIVE:
                    # 激进策略：只保留关键字段
                    pass
                else:
                    # 标记为省略
                    result[key] = "..."

            return result

        elif isinstance(data, list):
            if len(data) == 0:
                return []
            elif len(data) == 1:
                return [self._build_compressed_json(data[0], key_fields, strategy)]
            else:
                # 只保留第一个和数量
                return [
                    self._build_compressed_json(data[0], key_fields, strategy),
                    f"... 还有 {len(data) - 1} 项",
                ]

        return data

    def _extract_json_errors(self, data: Any) -> list[ErrorInfo]:
        """从 JSON 中提取错误信息"""
        errors: list[ErrorInfo] = []

        if isinstance(data, dict):
            # 检查错误字段
            if "error" in data or "errors" in data:
                error_data = data.get("error") or data.get("errors")
                if isinstance(error_data, str):
                    errors.append(ErrorInfo(
                        error_type="json_error",
                        error_message=error_data,
                        severity=ErrorSeverity.HIGH,
                    ))
                elif isinstance(error_data, dict):
                    errors.append(ErrorInfo(
                        error_type=error_data.get("type", "json_error"),
                        error_message=error_data.get("message", str(error_data)),
                        severity=ErrorSeverity.HIGH,
                    ))

            # 检查状态码
            status = data.get("status") or data.get("status_code") or data.get("code")
            if status and str(status).startswith(("4", "5")):
                errors.append(ErrorInfo(
                    error_type="http_error",
                    error_message=f"HTTP {status}: {data.get('message', 'Unknown error')}",
                    severity=ErrorSeverity.HIGH if str(status).startswith("5") else ErrorSeverity.MEDIUM,
                ))

            # 递归
            for value in data.values():
                if isinstance(value, (dict, list)):
                    errors.extend(self._extract_json_errors(value))

        elif isinstance(data, list):
            for item in data:
                errors.extend(self._extract_json_errors(item))

        return errors

    # -----------------------------------------------------------------------
    # 堆栈跟踪压缩
    # -----------------------------------------------------------------------

    def _compress_stack_trace(
        self,
        content: str,
        original_tokens: int,
        target_tokens: int,
        strategy: CompressionStrategy,
    ) -> CompressedResult:
        """
        压缩堆栈跟踪

        策略：
        1. 提取错误类型和消息
        2. 提取关键堆栈帧
        3. 去除重复帧

        Args:
            content: 原始内容
            original_tokens: 原始 Token 数
            target_tokens: 目标 Token 数
            strategy: 压缩策略

        Returns:
            CompressedResult 压缩结果
        """
        # 提取错误
        errors = self._extract_errors(content)

        # 提取堆栈帧
        frames = self._extract_stack_frames(content)

        # 构建摘要
        summary_parts: list[str] = ["【堆栈跟踪摘要】"]

        # 错误信息
        if errors:
            error = errors[0]
            summary_parts.append(f"错误类型: {error.error_type}")
            summary_parts.append(f"错误消息: {error.error_message}")

        # 关键堆栈帧（最多5个）
        summary_parts.append("\n关键调用栈:")
        for i, frame in enumerate(frames[:5]):
            summary_parts.append(f"  {i+1}. {frame}")

        if len(frames) > 5:
            summary_parts.append(f"  ... 还有 {len(frames) - 5} 帧")

        summary = "\n".join(summary_parts)
        compressed_tokens = self._count_tokens(summary)

        return CompressedResult(
            summary=summary,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            errors=errors,
            information_retention=0.9,  # 堆栈跟踪压缩通常保留关键信息
            key_info_preserved=True,
            content_type=ContentType.STACK_TRACE,
            strategy=strategy,
        )

    def _extract_stack_frames(self, content: str) -> list[str]:
        """提取堆栈帧"""
        frames: list[str] = []

        # 匹配 File "xxx", line Y, in Z
        pattern = r'File "([^"]+)", line (\d+), in (\w+)'
        matches = re.findall(pattern, content)

        for file_path, line_num, func_name in matches:
            frames.append(f"{file_path}:{line_num} in {func_name}()")

        return frames

    # -----------------------------------------------------------------------
    # 文本压缩
    # -----------------------------------------------------------------------

    def _compress_text(
        self,
        content: str,
        original_tokens: int,
        target_tokens: int,
        strategy: CompressionStrategy,
    ) -> CompressedResult:
        """
        压缩纯文本内容

        策略：
        1. 提取关键句子
        2. 去除重复内容
        3. 截断到目标长度

        Args:
            content: 原始内容
            original_tokens: 原始 Token 数
            target_tokens: 目标 Token 数
            strategy: 压缩策略

        Returns:
            CompressedResult 压缩结果
        """
        # 提取错误和警告
        errors = self._extract_errors(content)
        warnings = self._extract_warnings(content)

        # 提取因果结构
        causal_chains = self._extract_causal_chains(content)

        # 分割为句子
        sentences = self._split_sentences(content)

        # 选择关键句子
        key_sentences = self._select_key_sentences(
            sentences=sentences,
            errors=errors,
            warnings=warnings,
            target_tokens=target_tokens,
        )

        # 构建摘要
        summary = "\n".join(key_sentences)
        compressed_tokens = self._count_tokens(summary)

        # 评估信息保留度
        information_retention = len(key_sentences) / len(sentences) if sentences else 1.0

        return CompressedResult(
            summary=summary,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            errors=errors,
            warnings=warnings,
            causal_chains=causal_chains,
            information_retention=information_retention,
            key_info_preserved=len(errors) > 0,
            content_type=ContentType.TEXT,
            strategy=strategy,
        )

    # -----------------------------------------------------------------------
    # 错误和警告提取
    # -----------------------------------------------------------------------

    def _extract_errors(self, content: str) -> list[ErrorInfo]:
        """
        从内容中提取错误信息

        Args:
            content: 原始内容

        Returns:
            ErrorInfo 列表
        """
        errors: list[ErrorInfo] = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            for pattern, error_type in self._error_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # 确定严重程度
                    severity = ErrorSeverity.MEDIUM
                    if "FATAL" in line.upper() or "CRITICAL" in line.upper():
                        severity = ErrorSeverity.CRITICAL
                    elif "ERROR" in line.upper():
                        severity = ErrorSeverity.HIGH

                    # 提取错误消息
                    if match.groups():
                        if len(match.groups()) >= 2:
                            error_msg = match.group(2)
                            error_name = match.group(1)
                        else:
                            error_msg = match.group(1)
                            error_name = error_type
                    else:
                        error_msg = line
                        error_name = error_type

                    # 查找堆栈跟踪（如果有）
                    stack_trace = None
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith("  "):
                        stack_lines = []
                        for j in range(i + 1, min(i + 10, len(lines))):
                            if lines[j].strip() and lines[j].startswith("  "):
                                stack_lines.append(lines[j])
                            else:
                                break
                        if stack_lines:
                            stack_trace = "\n".join(stack_lines[:5])

                    errors.append(ErrorInfo(
                        error_type=error_name,
                        error_message=error_msg.strip(),
                        severity=severity,
                        line_number=i + 1,
                        stack_trace=stack_trace if self._config.preserve_stack_trace else None,
                    ))

        return errors[:self._config.max_errors]

    def _extract_warnings(self, content: str) -> list[WarningInfo]:
        """
        从内容中提取警告信息

        Args:
            content: 原始内容

        Returns:
            WarningInfo 列表
        """
        warnings: list[WarningInfo] = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            for pattern, warning_type in self._warning_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    warning_msg = match.group(1) if match.groups() else line
                    warnings.append(WarningInfo(
                        warning_type=warning_type,
                        warning_message=warning_msg.strip(),
                        line_number=i + 1,
                    ))

        return warnings[:self._config.max_warnings]

    # -----------------------------------------------------------------------
    # 因果结构提取
    # -----------------------------------------------------------------------

    def _extract_causal_chains(self, content: str) -> list[CausalChain]:
        """
        从内容中提取因果结构

        实现文档要求："把噪声信息压成因果结构"

        策略：
        1. 识别明确的因果关系（because, caused by, due to）
        2. 识别问题和解决方案模式
        3. 构建结构化输出

        Args:
            content: 原始内容

        Returns:
            CausalChain 列表
        """
        chains: list[CausalChain] = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # 检查因果模式
            for pattern, pattern_type in self._causal_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # 提取问题（通常是前一行或当前行的前半部分）
                    problem = self._extract_problem(line, lines, i)

                    # 提取原因
                    cause = match.group(1).strip() if match.groups() else ""

                    # 尝试找解决方案（后续行）
                    solution = self._extract_solution(lines, i)

                    if problem and cause:
                        chains.append(CausalChain(
                            problem=problem,
                            cause=cause,
                            solution=solution,
                            confidence=0.8 if pattern_type == "explicit" else 0.6,
                        ))

        return chains

    def _extract_problem(self, line: str, lines: list[str], index: int) -> str:
        """提取问题描述"""
        # 如果当前行包含 "because" 等，前半部分可能是问题
        for sep in [" because ", " caused by ", " due to ", ", reason: "]:
            if sep in line.lower():
                parts = re.split(sep, line, flags=re.IGNORECASE)
                if parts:
                    return parts[0].strip()

        # 否则，查看前一行
        if index > 0:
            prev_line = lines[index - 1].strip()
            if prev_line and not prev_line.startswith((" ", "\t")):
                return prev_line

        return ""

    def _extract_solution(self, lines: list[str], index: int) -> str | None:
        """提取解决方案"""
        # 查找后续的建议或解决方案行
        for i in range(index + 1, min(index + 5, len(lines))):
            line = lines[i].strip().lower()
            if any(keyword in line for keyword in ["fix:", "solution:", "suggest:", "try:", "recommend:"]):
                return lines[i].strip()

        return None

    # -----------------------------------------------------------------------
    # 辅助方法
    # -----------------------------------------------------------------------

    def _split_sentences(self, content: str) -> list[str]:
        """分割句子"""
        # 简单分割
        sentences = re.split(r'[。！？\n]', content)
        return [s.strip() for s in sentences if s.strip()]

    def _select_key_sentences(
        self,
        sentences: list[str],
        errors: list[ErrorInfo],
        warnings: list[WarningInfo],
        target_tokens: int,
    ) -> list[str]:
        """选择关键句子"""
        key_sentences: list[str] = []
        current_tokens = 0

        # 先添加包含错误的句子
        for sentence in sentences:
            if any(error.error_message.lower() in sentence.lower() for error in errors):
                tokens = self._count_tokens(sentence)
                if current_tokens + tokens <= target_tokens:
                    key_sentences.append(sentence)
                    current_tokens += tokens

        # 添加包含警告的句子
        for sentence in sentences:
            if any(warning.warning_message.lower() in sentence.lower() for warning in warnings):
                tokens = self._count_tokens(sentence)
                if current_tokens + tokens <= target_tokens:
                    key_sentences.append(sentence)
                    current_tokens += tokens

        # 添加包含关键字的句子
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in self._config.keywords_to_preserve):
                tokens = self._count_tokens(sentence)
                if current_tokens + tokens <= target_tokens:
                    key_sentences.append(sentence)
                    current_tokens += tokens

        # 去重
        seen = set()
        unique_sentences = []
        for sentence in key_sentences:
            if sentence not in seen:
                seen.add(sentence)
                unique_sentences.append(sentence)

        return unique_sentences

    def _further_compress(self, content: str, target_tokens: int) -> str:
        """进一步压缩"""
        lines = content.split("\n")
        result_lines: list[str] = []
        current_tokens = 0

        for line in lines:
            line_tokens = self._count_tokens(line)
            if current_tokens + line_tokens <= target_tokens:
                result_lines.append(line)
                current_tokens += line_tokens

        return "\n".join(result_lines)

    def _count_tokens(self, text: str) -> int:
        """计算 Token 数"""
        if self._token_budget:
            return self._token_budget.count(text)
        # 简单估算：4字符约等于1 Token
        return max(1, len(text) // 4)

    def _estimate_retention(
        self,
        original_content: str,
        compressed_content: str,
        errors: list[ErrorInfo],
        warnings: list[WarningInfo],
        causal_chains: list[CausalChain],
    ) -> float:
        """
        评估信息保留度

        基于以下指标：
        1. 错误保留率
        2. 警告保留率
        3. 因果结构保留
        4. 内容长度比
        """
        # 错误保留
        error_retention = 1.0 if errors else 0.0

        # 警告保留
        warning_retention = 1.0 if warnings else 0.0

        # 因果结构保留
        causal_retention = 1.0 if causal_chains else 0.0

        # 长度比
        length_retention = min(1.0, len(compressed_content) / max(1, len(original_content)))

        # 综合评分
        # 错误和警告是关键，权重较高
        retention = (
            error_retention * 0.4 +
            warning_retention * 0.2 +
            causal_retention * 0.2 +
            length_retention * 0.2
        )

        return min(1.0, retention)

    def _estimate_json_retention(
        self,
        original_data: Any,
        compressed_data: Any,
    ) -> float:
        """评估 JSON 压缩的信息保留度"""
        if isinstance(original_data, dict) and isinstance(compressed_data, dict):
            original_keys = set(original_data.keys())
            compressed_keys = set(compressed_data.keys())

            # 省略标记的键也算保留
            preserved_keys = set()
            for key in compressed_keys:
                if compressed_data[key] != "...":
                    preserved_keys.add(key)

            return len(preserved_keys) / len(original_keys) if original_keys else 1.0

        return 1.0

    # -----------------------------------------------------------------------
    # 因果结构提取（公开方法）
    # -----------------------------------------------------------------------

    def extract_causal_structure(self, content: str) -> list[CausalChain]:
        """
        提取因果结构（公开方法）

        用于单独提取因果结构，不做完整压缩

        Args:
            content: 原始内容

        Returns:
            CausalChain 列表
        """
        return self._extract_causal_chains(content)

    def build_causal_chain(
        self,
        problem: str,
        cause: str,
        solution: str | None = None,
        confidence: float = 0.5,
    ) -> CausalChain:
        """
        手动构建因果链

        Args:
            problem: 问题描述
            cause: 原因
            solution: 解决方案
            confidence: 置信度

        Returns:
            CausalChain 因果链
        """
        return CausalChain(
            problem=problem,
            cause=cause,
            solution=solution,
            confidence=confidence,
        )


# ============================================================================
# 工厂函数
# ============================================================================


def create_result_compressor(
    strategy: CompressionStrategy = CompressionStrategy.BALANCED,
    target_ratio: float = 0.3,
) -> ResultCompressor:
    """
    创建结果压缩器

    Args:
        strategy: 压缩策略
        target_ratio: 目标压缩率

    Returns:
        ResultCompressor 实例
    """
    config = CompressionConfig(
        strategy=strategy,
        target_ratio=target_ratio,
    )

    return ResultCompressor(config=config)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "ContentType",
    "ErrorSeverity",
    "CompressionStrategy",
    "ErrorInfo",
    "WarningInfo",
    "CausalChain",
    "DecisionPoint",
    "CompressedResult",
    "CompressionConfig",
    "ResultCompressor",
    "create_result_compressor",
]
