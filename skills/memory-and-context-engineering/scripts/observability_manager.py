"""
Agent Memory System - Observability Manager（可观测性管理器）

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证
  * redis: >=4.5.0
    - 用途：指标存储和缓存
- 标准配置文件:
  ```text
  # requirements.txt
  pydantic>=2.0.0
  redis>=4.5.0
  ```
=== 声明结束 ===

安全提醒：监控数据可能包含敏感信息，需做好脱敏处理
"""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, Field

from .redis_adapter import RedisAdapter


# ============================================================================
# 枚举类型
# ============================================================================


class MetricType(str, Enum):
    """指标类型"""

    COUNTER = "counter"      # 计数器
    GAUGE = "gauge"          # 仪表盘
    HISTOGRAM = "histogram"  # 直方图
    SUMMARY = "summary"      # 摘要


class AlertLevel(str, Enum):
    """告警级别"""

    INFO = "info"            # 信息
    WARNING = "warning"      # 警告
    ERROR = "error"          # 错误
    CRITICAL = "critical"    # 严重


class MetricCategory(str, Enum):
    """指标类别"""

    TOKEN_COST = "token_cost"          # Token 成本
    LATENCY = "latency"                # 延迟
    QUALITY = "quality"                # 质量
    THROUGHPUT = "throughput"          # 吞吐量
    ERROR_RATE = "error_rate"          # 错误率
    CACHE = "cache"                    # 缓存
    MEMORY = "memory"                  # 内存
    CONTEXT = "context"                # 上下文


# ============================================================================
# 数据模型
# ============================================================================


class MetricPoint(BaseModel):
    """指标数据点"""

    name: str
    value: float
    timestamp: datetime = Field(default_factory=datetime.now)
    labels: dict[str, str] = Field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


class TokenUsage(BaseModel):
    """Token 使用记录"""

    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)

    # Token 分类统计
    system_tokens: int = Field(default=0)
    user_tokens: int = Field(default=0)
    memory_tokens: int = Field(default=0)
    retrieval_tokens: int = Field(default=0)
    tool_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)

    # 成本估算（美元）
    cost_estimate: float = Field(default=0.0)

    # 元数据
    model: str = Field(default="gpt-4")
    metadata: dict[str, Any] = Field(default_factory=dict)


class LatencyRecord(BaseModel):
    """延迟记录"""

    operation: str
    duration_ms: float
    timestamp: datetime = Field(default_factory=datetime.now)

    # 分阶段延迟
    stages: dict[str, float] = Field(default_factory=dict)

    # 元数据
    success: bool = Field(default=True)
    error: str | None = None


class QualityMetrics(BaseModel):
    """质量指标"""

    timestamp: datetime = Field(default_factory=datetime.now)

    # 上下文质量
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    coherence_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # 检索质量
    retrieval_precision: float = Field(default=0.0, ge=0.0, le=1.0)
    retrieval_recall: float = Field(default=0.0, ge=0.0, le=1.0)

    # 压缩质量
    compression_ratio: float = Field(default=0.0)
    information_retention: float = Field(default=0.0, ge=0.0, le=1.0)

    # 综合评分
    overall_quality: float = Field(default=0.0, ge=0.0, le=1.0)


class Alert(BaseModel):
    """告警"""

    alert_id: str = Field(
        default_factory=lambda: f"alert_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    level: AlertLevel
    category: MetricCategory
    message: str
    value: float
    threshold: float
    timestamp: datetime = Field(default_factory=datetime.now)
    acknowledged: bool = Field(default=False)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AlertRule(BaseModel):
    """告警规则"""

    rule_id: str
    name: str
    category: MetricCategory
    metric_name: str
    condition: str  # gt, lt, eq, gte, lte
    threshold: float
    level: AlertLevel
    enabled: bool = Field(default=True)
    cooldown_seconds: int = Field(default=300)  # 冷却时间


class ObservabilityConfig(BaseModel):
    """可观测性配置"""

    # Token 追踪
    enable_token_tracking: bool = Field(default=True)
    token_cost_per_1k: float = Field(default=0.03)  # 每 1k token 成本（美元）

    # 延迟监控
    enable_latency_tracking: bool = Field(default=True)
    latency_percentiles: list[float] = Field(
        default_factory=lambda: [0.5, 0.9, 0.95, 0.99]
    )

    # 质量指标
    enable_quality_metrics: bool = Field(default=True)

    # 告警
    enable_alerting: bool = Field(default=True)
    alert_rules: list[AlertRule] = Field(default_factory=list)

    # 数据保留
    retention_hours: int = Field(default=24)
    aggregation_interval_seconds: int = Field(default=60)


class ObservabilityStats(BaseModel):
    """可观测性统计"""

    # 时间范围
    start_time: datetime
    end_time: datetime = Field(default_factory=datetime.now)

    # Token 统计
    total_tokens: int = Field(default=0)
    total_cost: float = Field(default=0.0)
    tokens_by_category: dict[str, int] = Field(default_factory=dict)

    # 延迟统计
    total_operations: int = Field(default=0)
    avg_latency_ms: float = Field(default=0.0)
    p50_latency_ms: float = Field(default=0.0)
    p90_latency_ms: float = Field(default=0.0)
    p99_latency_ms: float = Field(default=0.0)

    # 质量统计
    avg_quality_score: float = Field(default=0.0)

    # 告警统计
    total_alerts: int = Field(default=0)
    alerts_by_level: dict[str, int] = Field(default_factory=dict)


# ============================================================================
# Observability Manager
# ============================================================================


class ObservabilityManager:
    """
    可观测性管理器
    
    职责：
    - Token 成本追踪
    - 延迟监控
    - 上下文质量指标
    - 告警机制
    
    使用示例：
    ```python
    from scripts.observability_manager import ObservabilityManager

    manager = ObservabilityManager()

    # 记录 Token 使用
    manager.record_token_usage(
        session_id="session123",
        system_tokens=100,
        user_tokens=50,
        total_tokens=150,
    )

    # 记录延迟
    manager.record_latency(
        operation="context_prepare",
        duration_ms=123.45,
    )

    # 获取统计
    stats = manager.get_stats()
    print(f"Total tokens: {stats.total_tokens}")
    print(f"Total cost: ${stats.total_cost:.4f}")
    ```
    """

    def __init__(
        self,
        config: ObservabilityConfig | None = None,
        redis_adapter: RedisAdapter | None = None,
    ):
        """初始化可观测性管理器"""
        self._config = config or ObservabilityConfig()
        self._redis = redis_adapter

        # 指标存储
        self._metrics: dict[str, list[MetricPoint]] = defaultdict(list)

        # Token 记录
        self._token_records: list[TokenUsage] = []

        # 延迟记录
        self._latency_records: list[LatencyRecord] = []

        # 质量记录
        self._quality_records: list[QualityMetrics] = []

        # 告警
        self._alerts: list[Alert] = []
        self._alert_cooldowns: dict[str, datetime] = {}

        # 初始化默认告警规则
        self._init_default_alert_rules()

    def _init_default_alert_rules(self) -> None:
        """初始化默认告警规则"""
        if self._config.alert_rules:
            return

        self._config.alert_rules = [
            AlertRule(
                rule_id="high_token_usage",
                name="高 Token 使用量",
                category=MetricCategory.TOKEN_COST,
                metric_name="total_tokens",
                condition="gt",
                threshold=100000,
                level=AlertLevel.WARNING,
            ),
            AlertRule(
                rule_id="high_latency",
                name="高延迟",
                category=MetricCategory.LATENCY,
                metric_name="latency_ms",
                condition="gt",
                threshold=5000,
                level=AlertLevel.WARNING,
            ),
            AlertRule(
                rule_id="low_quality",
                name="低质量评分",
                category=MetricCategory.QUALITY,
                metric_name="quality_score",
                condition="lt",
                threshold=0.5,
                level=AlertLevel.WARNING,
            ),
            AlertRule(
                rule_id="critical_token_usage",
                name="严重 Token 超限",
                category=MetricCategory.TOKEN_COST,
                metric_name="total_tokens",
                condition="gt",
                threshold=500000,
                level=AlertLevel.CRITICAL,
            ),
        ]

    # -----------------------------------------------------------------------
    # Token 追踪
    # -----------------------------------------------------------------------

    def record_token_usage(
        self,
        session_id: str,
        system_tokens: int = 0,
        user_tokens: int = 0,
        memory_tokens: int = 0,
        retrieval_tokens: int = 0,
        tool_tokens: int = 0,
        total_tokens: int | None = None,
        model: str = "gpt-4",
        metadata: dict[str, Any] | None = None,
    ) -> TokenUsage:
        """
        记录 Token 使用

        Args:
            session_id: 会话 ID
            system_tokens: 系统 Token
            user_tokens: 用户 Token
            memory_tokens: 记忆 Token
            retrieval_tokens: 检索 Token
            tool_tokens: 工具 Token
            total_tokens: 总 Token（可选，自动计算）
            model: 模型名称
            metadata: 元数据

        Returns:
            TokenUsage 记录
        """
        if not self._config.enable_token_tracking:
            return TokenUsage(session_id=session_id)

        # 计算总 Token
        if total_tokens is None:
            total_tokens = (
                system_tokens + user_tokens + memory_tokens
                + retrieval_tokens + tool_tokens
            )

        # 估算成本
        cost_estimate = (total_tokens / 1000) * self._config.token_cost_per_1k

        record = TokenUsage(
            session_id=session_id,
            system_tokens=system_tokens,
            user_tokens=user_tokens,
            memory_tokens=memory_tokens,
            retrieval_tokens=retrieval_tokens,
            tool_tokens=tool_tokens,
            total_tokens=total_tokens,
            cost_estimate=cost_estimate,
            model=model,
            metadata=metadata or {},
        )

        self._token_records.append(record)

        # 检查告警
        self._check_alerts(
            MetricCategory.TOKEN_COST,
            "total_tokens",
            float(total_tokens),
        )

        return record

    def get_token_stats(
        self,
        session_id: str | None = None,
        hours: int = 24,
    ) -> dict[str, Any]:
        """
        获取 Token 统计

        Args:
            session_id: 会话 ID（可选）
            hours: 统计时间范围（小时）

        Returns:
            Token 统计字典
        """
        cutoff = datetime.now() - timedelta(hours=hours)

        records = [
            r for r in self._token_records
            if r.timestamp >= cutoff
            and (session_id is None or r.session_id == session_id)
        ]

        if not records:
            return {
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_tokens_per_session": 0.0,
            }

        total_tokens = sum(r.total_tokens for r in records)
        total_cost = sum(r.cost_estimate for r in records)

        # 按类别统计
        by_category = {
            "system": sum(r.system_tokens for r in records),
            "user": sum(r.user_tokens for r in records),
            "memory": sum(r.memory_tokens for r in records),
            "retrieval": sum(r.retrieval_tokens for r in records),
            "tool": sum(r.tool_tokens for r in records),
        }

        # 按会话统计
        sessions = set(r.session_id for r in records)
        avg_per_session = total_tokens / len(sessions) if sessions else 0

        return {
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "avg_tokens_per_session": avg_per_session,
            "by_category": by_category,
            "record_count": len(records),
            "session_count": len(sessions),
        }

    # -----------------------------------------------------------------------
    # 延迟监控
    # -----------------------------------------------------------------------

    def record_latency(
        self,
        operation: str,
        duration_ms: float,
        stages: dict[str, float] | None = None,
        success: bool = True,
        error: str | None = None,
    ) -> LatencyRecord:
        """
        记录延迟

        Args:
            operation: 操作名称
            duration_ms: 持续时间（毫秒）
            stages: 分阶段延迟
            success: 是否成功
            error: 错误信息

        Returns:
            LatencyRecord 记录
        """
        if not self._config.enable_latency_tracking:
            return LatencyRecord(
                operation=operation,
                duration_ms=duration_ms,
            )

        record = LatencyRecord(
            operation=operation,
            duration_ms=duration_ms,
            stages=stages or {},
            success=success,
            error=error,
        )

        self._latency_records.append(record)

        # 记录指标
        self._record_metric(
            name=f"latency_{operation}",
            value=duration_ms,
            labels={"success": str(success)},
        )

        # 检查告警
        self._check_alerts(
            MetricCategory.LATENCY,
            "latency_ms",
            duration_ms,
        )

        return record

    def get_latency_stats(
        self,
        operation: str | None = None,
        hours: int = 24,
    ) -> dict[str, Any]:
        """
        获取延迟统计

        Args:
            operation: 操作名称（可选）
            hours: 统计时间范围（小时）

        Returns:
            延迟统计字典
        """
        cutoff = datetime.now() - timedelta(hours=hours)

        records = [
            r for r in self._latency_records
            if r.timestamp >= cutoff
            and (operation is None or r.operation == operation)
        ]

        if not records:
            return {
                "avg_latency_ms": 0.0,
                "p50": 0.0,
                "p90": 0.0,
                "p99": 0.0,
            }

        durations = sorted(r.duration_ms for r in records)
        count = len(durations)

        def percentile(p: float) -> float:
            idx = int(count * p)
            return durations[min(idx, count - 1)]

        return {
            "total_operations": count,
            "avg_latency_ms": sum(durations) / count,
            "p50": percentile(0.5),
            "p90": percentile(0.9),
            "p95": percentile(0.95),
            "p99": percentile(0.99),
            "min": durations[0],
            "max": durations[-1],
            "success_rate": sum(1 for r in records if r.success) / count,
        }

    # -----------------------------------------------------------------------
    # 质量指标
    # -----------------------------------------------------------------------

    def record_quality(
        self,
        relevance_score: float = 0.0,
        completeness_score: float = 0.0,
        coherence_score: float = 0.0,
        retrieval_precision: float = 0.0,
        retrieval_recall: float = 0.0,
        compression_ratio: float = 0.0,
        information_retention: float = 0.0,
    ) -> QualityMetrics:
        """
        记录质量指标

        Args:
            relevance_score: 相关性评分
            completeness_score: 完整性评分
            coherence_score: 连贯性评分
            retrieval_precision: 检索精确率
            retrieval_recall: 检索召回率
            compression_ratio: 压缩比
            information_retention: 信息保留率

        Returns:
            QualityMetrics 记录
        """
        if not self._config.enable_quality_metrics:
            return QualityMetrics()

        # 计算综合评分
        overall = (
            relevance_score * 0.25 +
            completeness_score * 0.20 +
            coherence_score * 0.20 +
            retrieval_precision * 0.15 +
            retrieval_recall * 0.10 +
            information_retention * 0.10
        )

        record = QualityMetrics(
            relevance_score=relevance_score,
            completeness_score=completeness_score,
            coherence_score=coherence_score,
            retrieval_precision=retrieval_precision,
            retrieval_recall=retrieval_recall,
            compression_ratio=compression_ratio,
            information_retention=information_retention,
            overall_quality=overall,
        )

        self._quality_records.append(record)

        # 检查告警
        self._check_alerts(
            MetricCategory.QUALITY,
            "quality_score",
            overall,
        )

        return record

    def get_quality_stats(
        self,
        hours: int = 24,
    ) -> dict[str, Any]:
        """
        获取质量统计

        Args:
            hours: 统计时间范围（小时）

        Returns:
            质量统计字典
        """
        cutoff = datetime.now() - timedelta(hours=hours)

        records = [
            r for r in self._quality_records
            if r.timestamp >= cutoff
        ]

        if not records:
            return {"avg_quality": 0.0}

        return {
            "record_count": len(records),
            "avg_quality": sum(r.overall_quality for r in records) / len(records),
            "avg_relevance": sum(r.relevance_score for r in records) / len(records),
            "avg_completeness": sum(r.completeness_score for r in records) / len(records),
            "avg_coherence": sum(r.coherence_score for r in records) / len(records),
            "avg_retrieval_precision": sum(r.retrieval_precision for r in records) / len(records),
            "avg_compression_ratio": sum(r.compression_ratio for r in records) / len(records),
        }

    # -----------------------------------------------------------------------
    # 告警机制
    # -----------------------------------------------------------------------

    def _check_alerts(
        self,
        category: MetricCategory,
        metric_name: str,
        value: float,
    ) -> None:
        """检查告警规则"""
        if not self._config.enable_alerting:
            return

        for rule in self._config.alert_rules:
            if not rule.enabled:
                continue

            if rule.category != category or rule.metric_name != metric_name:
                continue

            # 检查冷却时间
            cooldown_key = f"{rule.rule_id}_{metric_name}"
            if cooldown_key in self._alert_cooldowns:
                last_alert = self._alert_cooldowns[cooldown_key]
                if datetime.now() - last_alert < timedelta(seconds=rule.cooldown_seconds):
                    continue

            # 检查条件
            triggered = False
            if rule.condition == "gt" and value > rule.threshold:
                triggered = True
            elif rule.condition == "lt" and value < rule.threshold:
                triggered = True
            elif rule.condition == "gte" and value >= rule.threshold:
                triggered = True
            elif rule.condition == "lte" and value <= rule.threshold:
                triggered = True
            elif rule.condition == "eq" and value == rule.threshold:
                triggered = True

            if triggered:
                self._create_alert(rule, value)

    def _create_alert(self, rule: AlertRule, value: float) -> Alert:
        """创建告警"""
        alert = Alert(
            level=rule.level,
            category=rule.category,
            message=f"{rule.name}: {rule.metric_name}={value:.2f}, threshold={rule.threshold:.2f}",
            value=value,
            threshold=rule.threshold,
            metadata={"rule_id": rule.rule_id},
        )

        self._alerts.append(alert)

        # 设置冷却
        cooldown_key = f"{rule.rule_id}_{rule.metric_name}"
        self._alert_cooldowns[cooldown_key] = datetime.now()

        return alert

    def get_alerts(
        self,
        level: AlertLevel | None = None,
        acknowledged: bool | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        """
        获取告警列表

        Args:
            level: 告警级别（可选）
            acknowledged: 确认状态（可选）
            limit: 最大返回数量

        Returns:
            告警列表
        """
        alerts = self._alerts

        if level:
            alerts = [a for a in alerts if a.level == level]

        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]

        return alerts[-limit:]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False

    # -----------------------------------------------------------------------
    # 指标管理
    # -----------------------------------------------------------------------

    def _record_metric(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
        metric_type: MetricType = MetricType.GAUGE,
    ) -> None:
        """记录指标"""
        point = MetricPoint(
            name=name,
            value=value,
            labels=labels or {},
            metric_type=metric_type,
        )
        self._metrics[name].append(point)

    def get_metrics(
        self,
        name: str | None = None,
        hours: int = 1,
    ) -> dict[str, list[MetricPoint]]:
        """
        获取指标数据

        Args:
            name: 指标名称（可选，返回所有）
            hours: 时间范围（小时）

        Returns:
            指标数据字典
        """
        cutoff = datetime.now() - timedelta(hours=hours)

        if name:
            if name in self._metrics:
                return {
                    name: [
                        p for p in self._metrics[name]
                        if p.timestamp >= cutoff
                    ]
                }
            return {}

        return {
            n: [p for p in points if p.timestamp >= cutoff]
            for n, points in self._metrics.items()
        }

    # -----------------------------------------------------------------------
    # 综合统计
    # -----------------------------------------------------------------------

    def get_stats(
        self,
        hours: int = 24,
    ) -> ObservabilityStats:
        """
        获取综合统计

        Args:
            hours: 统计时间范围（小时）

        Returns:
            ObservabilityStats 统计结果
        """
        cutoff = datetime.now() - timedelta(hours=hours)

        # Token 统计
        token_records = [
            r for r in self._token_records
            if r.timestamp >= cutoff
        ]
        total_tokens = sum(r.total_tokens for r in token_records)
        total_cost = sum(r.cost_estimate for r in token_records)

        tokens_by_category: dict[str, int] = defaultdict(int)
        for r in token_records:
            tokens_by_category["system"] += r.system_tokens
            tokens_by_category["user"] += r.user_tokens
            tokens_by_category["memory"] += r.memory_tokens
            tokens_by_category["retrieval"] += r.retrieval_tokens
            tokens_by_category["tool"] += r.tool_tokens

        # 延迟统计
        latency_records = [
            r for r in self._latency_records
            if r.timestamp >= cutoff
        ]
        durations = [r.duration_ms for r in latency_records]
        count = len(durations)

        def percentile(p: float) -> float:
            if not durations:
                return 0.0
            sorted_d = sorted(durations)
            idx = int(len(sorted_d) * p)
            return sorted_d[min(idx, len(sorted_d) - 1)]

        # 质量统计
        quality_records = [
            r for r in self._quality_records
            if r.timestamp >= cutoff
        ]
        avg_quality = (
            sum(r.overall_quality for r in quality_records) / len(quality_records)
            if quality_records else 0.0
        )

        # 告警统计
        alerts = [
            a for a in self._alerts
            if a.timestamp >= cutoff
        ]
        alerts_by_level: dict[str, int] = defaultdict(int)
        for a in alerts:
            alerts_by_level[a.level.value] += 1

        return ObservabilityStats(
            start_time=cutoff,
            end_time=datetime.now(),
            total_tokens=total_tokens,
            total_cost=total_cost,
            tokens_by_category=dict(tokens_by_category),
            total_operations=count,
            avg_latency_ms=sum(durations) / count if count else 0.0,
            p50_latency_ms=percentile(0.5),
            p90_latency_ms=percentile(0.9),
            p99_latency_ms=percentile(0.99),
            avg_quality_score=avg_quality,
            total_alerts=len(alerts),
            alerts_by_level=dict(alerts_by_level),
        )

    # -----------------------------------------------------------------------
    # 清理
    # -----------------------------------------------------------------------

    def cleanup(self, hours: int | None = None) -> dict[str, int]:
        """
        清理过期数据

        Args:
            hours: 保留时间（小时），默认使用配置

        Returns:
            清理统计
        """
        retention = hours or self._config.retention_hours
        cutoff = datetime.now() - timedelta(hours=retention)

        # 清理各类记录
        before = {
            "token_records": len(self._token_records),
            "latency_records": len(self._latency_records),
            "quality_records": len(self._quality_records),
            "alerts": len(self._alerts),
            "metrics": sum(len(v) for v in self._metrics.values()),
        }

        self._token_records = [
            r for r in self._token_records if r.timestamp >= cutoff
        ]
        self._latency_records = [
            r for r in self._latency_records if r.timestamp >= cutoff
        ]
        self._quality_records = [
            r for r in self._quality_records if r.timestamp >= cutoff
        ]
        self._alerts = [
            a for a in self._alerts if a.timestamp >= cutoff
        ]

        for name in list(self._metrics.keys()):
            self._metrics[name] = [
                p for p in self._metrics[name] if p.timestamp >= cutoff
            ]
            if not self._metrics[name]:
                del self._metrics[name]

        after = {
            "token_records": len(self._token_records),
            "latency_records": len(self._latency_records),
            "quality_records": len(self._quality_records),
            "alerts": len(self._alerts),
            "metrics": sum(len(v) for v in self._metrics.values()),
        }

        return {
            f"removed_{k}": before[k] - after[k]
            for k in before
        }


# ============================================================================
# 上下文管理器
# ============================================================================


class LatencyTracker:
    """延迟追踪上下文管理器"""

    def __init__(
        self,
        manager: ObservabilityManager,
        operation: str,
        stages: list[str] | None = None,
    ):
        """初始化追踪器"""
        self._manager = manager
        self._operation = operation
        self._stages = stages or []
        self._start_time = 0.0
        self._stage_times: dict[str, float] = {}
        self._current_stage_start = 0.0

    def __enter__(self) -> "LatencyTracker":
        """进入上下文"""
        self._start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文"""
        duration_ms = (time.time() - self._start_time) * 1000
        self._manager.record_latency(
            operation=self._operation,
            duration_ms=duration_ms,
            stages=self._stage_times,
            success=exc_type is None,
            error=str(exc_val) if exc_val else None,
        )

    def start_stage(self, stage: str) -> None:
        """开始阶段"""
        self._current_stage_start = time.time()

    def end_stage(self, stage: str) -> float:
        """结束阶段"""
        duration_ms = (time.time() - self._current_stage_start) * 1000
        self._stage_times[stage] = duration_ms
        return duration_ms


# ============================================================================
# 工厂函数
# ============================================================================


def create_observability_manager(
    enable_token_tracking: bool = True,
    enable_latency_tracking: bool = True,
    enable_quality_metrics: bool = True,
    enable_alerting: bool = True,
    token_cost_per_1k: float = 0.03,
    redis_adapter: RedisAdapter | None = None,
) -> ObservabilityManager:
    """
    创建可观测性管理器

    Args:
        enable_token_tracking: 启用 Token 追踪
        enable_latency_tracking: 启用延迟追踪
        enable_quality_metrics: 启用质量指标
        enable_alerting: 启用告警
        token_cost_per_1k: 每 1k token 成本
        redis_adapter: Redis 适配器（可选）

    Returns:
        ObservabilityManager 实例
    """
    config = ObservabilityConfig(
        enable_token_tracking=enable_token_tracking,
        enable_latency_tracking=enable_latency_tracking,
        enable_quality_metrics=enable_quality_metrics,
        enable_alerting=enable_alerting,
        token_cost_per_1k=token_cost_per_1k,
    )

    return ObservabilityManager(config=config, redis_adapter=redis_adapter)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "MetricType",
    "AlertLevel",
    "MetricCategory",
    "MetricPoint",
    "TokenUsage",
    "LatencyRecord",
    "QualityMetrics",
    "Alert",
    "AlertRule",
    "ObservabilityConfig",
    "ObservabilityStats",
    "ObservabilityManager",
    "LatencyTracker",
    "create_observability_manager",
]
