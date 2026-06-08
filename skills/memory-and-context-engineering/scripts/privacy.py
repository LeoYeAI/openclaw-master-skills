"""
Agent Memory System - 隐私配置模块

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

import hashlib
import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================


class ConsentStatus(str, Enum):
    """同意状态"""

    NOT_REQUESTED = "not_requested"  # 未请求
    PENDING = "pending"  # 待确认
    GRANTED = "granted"  # 已授权
    DENIED = "denied"  # 已拒绝
    WITHDRAWN = "withdrawn"  # 已撤回


class DataSensitivity(str, Enum):
    """数据敏感度级别"""

    PUBLIC = "public"  # 公开数据
    INTERNAL = "internal"  # 内部数据
    SENSITIVE = "sensitive"  # 敏感数据
    RESTRICTED = "restricted"  # 受限数据（不存储）


class StoragePolicy(str, Enum):
    """存储策略"""

    FULL = "full"  # 完整存储
    ANONYMIZED = "anonymized"  # 匿名化存储
    AGGREGATED = "aggregated"  # 聚合存储（仅统计）
    NONE = "none"  # 不存储


class RetentionPeriod(str, Enum):
    """保留期限"""

    SESSION_ONLY = "session_only"  # 仅会话期间
    SHORT_TERM = "short_term"  # 短期（7天）
    MEDIUM_TERM = "medium_term"  # 中期（30天）
    LONG_TERM = "long_term"  # 长期（1年）
    INDEFINITE = "indefinite"  # 无限期


# ============================================================================
# 数据模型
# ============================================================================


class ConsentRecord(BaseModel):
    """同意记录"""

    consent_id: str
    user_id: str
    consent_type: str  # memory_storage, sensitive_data, cross_session
    status: ConsentStatus
    granted_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    version: str = "1.0"
    metadata: dict[str, Any] = Field(default_factory=dict)


class PrivacyConfig(BaseModel):
    """隐私配置"""

    user_id: str
    default_storage_policy: StoragePolicy = StoragePolicy.FULL
    default_retention_period: RetentionPeriod = RetentionPeriod.LONG_TERM
    allowed_categories: list[str] = Field(default_factory=lambda: ["all"])
    blocked_categories: list[str] = Field(default_factory=list)
    anonymize_fields: list[str] = Field(default_factory=list)
    auto_delete_sensitive: bool = Field(default=True)
    require_consent_for_sensitive: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DataClassification(BaseModel):
    """数据分类结果"""

    field_name: str
    original_value: Any
    sensitivity: DataSensitivity
    should_store: bool
    anonymized_value: Optional[str] = None
    classification_reason: str = ""


class PrivacyAuditLog(BaseModel):
    """隐私审计日志"""

    log_id: str
    user_id: str
    action: str  # store, access, delete, export
    data_type: str
    sensitivity: DataSensitivity
    timestamp: datetime = Field(default_factory=datetime.now)
    details: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 敏感数据识别器
# ============================================================================


class SensitiveDataDetector:
    """
    敏感数据检测器

    自动识别文本中的敏感信息类型
    """

    def __init__(self) -> None:
        """初始化敏感数据检测器"""
        # 敏感关键词模式
        self._sensitive_patterns: dict[str, list[str]] = {
            "personal_info": [
                "身份证", "护照", "驾照", "社保号",
                "ID card", "passport", "SSN", "social security"
            ],
            "financial": [
                "银行卡", "信用卡", "账号", "密码", "PIN",
                "bank account", "credit card", "password", "CVV"
            ],
            "health": [
                "病历", "诊断", "处方", "医疗",
                "medical record", "diagnosis", "prescription"
            ],
            "credentials": [
                "token", "API key", "secret", "密钥", "私钥",
                "private key", "access token", "authorization"
            ],
            "contact": [
                "手机号", "电话", "邮箱", "地址",
                "phone", "email", "address"
            ],
        }

        # 受限关键词（绝对不存储）
        self._restricted_patterns: list[str] = [
            "密码是", "密码为", "password is", "my password",
            "卡号是", "card number is", "账号是", "account number"
        ]

    def classify_content(self, content: str) -> DataSensitivity:
        """
        分类内容敏感度

        Args:
            content: 待分类内容

        Returns:
            敏感度级别
        """
        content_lower: str = content.lower()

        # 检查受限关键词
        for pattern in self._restricted_patterns:
            if pattern.lower() in content_lower:
                return DataSensitivity.RESTRICTED

        # 检查敏感关键词
        for category, patterns in self._sensitive_patterns.items():
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    return DataSensitivity.SENSITIVE

        return DataSensitivity.INTERNAL

    def classify_field(
        self, field_name: str, value: Any
    ) -> DataClassification:
        """
        分类字段敏感度

        Args:
            field_name: 字段名
            value: 字段值

        Returns:
            数据分类结果
        """
        sensitivity: DataSensitivity = DataSensitivity.INTERNAL
        reason: str = "默认分类为内部数据"

        # 字段名检查
        field_lower: str = field_name.lower()

        restricted_fields: list[str] = [
            "password", "secret", "token", "api_key", "private_key"
        ]
        if any(rf in field_lower for rf in restricted_fields):
            sensitivity = DataSensitivity.RESTRICTED
            reason = f"字段名 '{field_name}' 匹配受限字段"

        elif isinstance(value, str):
            sensitivity = self.classify_content(value)
            reason = "内容分析结果"

        # 决定是否存储
        should_store: bool = sensitivity != DataSensitivity.RESTRICTED

        # 匿名化处理
        anonymized: Optional[str] = None
        if should_store and sensitivity == DataSensitivity.SENSITIVE:
            anonymized = self._anonymize(value)

        return DataClassification(
            field_name=field_name,
            original_value=value,
            sensitivity=sensitivity,
            should_store=should_store,
            anonymized_value=anonymized,
            classification_reason=reason,
        )

    def _anonymize(self, value: Any) -> str:
        """
        匿名化处理

        Args:
            value: 原始值

        Returns:
            匿名化后的值
        """
        if not isinstance(value, str):
            return "[ANONYMIZED]"

        # 使用哈希处理
        hash_value: str = hashlib.sha256(value.encode()).hexdigest()[:8]
        return f"[ANONYMIZED:{hash_value}]"


# ============================================================================
# 隐私管理器
# ============================================================================


class PrivacyManager:
    """
    隐私管理器

    管理用户同意、数据分类、存储策略
    """

    def __init__(
        self,
        user_id: str = "default_user",
        storage_path: str = "./privacy_data",
    ) -> None:
        """
        初始化隐私管理器

        Args:
            user_id: 用户ID
            storage_path: 存储路径
        """
        self.user_id: str = user_id
        self.storage_path: Path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # 初始化组件
        self._detector: SensitiveDataDetector = SensitiveDataDetector()
        self._config: PrivacyConfig = PrivacyConfig(user_id=user_id)
        self._consents: dict[str, ConsentRecord] = {}
        self._audit_logs: list[PrivacyAuditLog] = []

        # 加载已有配置
        self._load_config()

    def _load_config(self) -> None:
        """加载隐私配置"""
        config_file: Path = self.storage_path / f"{self.user_id}_privacy.json"

        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data: dict[str, Any] = json.load(f)
                    self._config = PrivacyConfig.model_validate(data)
            except (json.JSONDecodeError, ValueError):
                pass

    def _save_config(self) -> None:
        """保存隐私配置"""
        config_file: Path = self.storage_path / f"{self.user_id}_privacy.json"

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(self._config.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

    # ==================== 同意管理 ====================

    def request_consent(
        self,
        consent_type: str,
        description: str,
    ) -> ConsentRecord:
        """
        请求用户同意

        Args:
            consent_type: 同意类型
            description: 描述信息

        Returns:
            同意记录
        """
        consent_id: str = f"consent_{uuid.uuid4().hex[:8]}"

        record: ConsentRecord = ConsentRecord(
            consent_id=consent_id,
            user_id=self.user_id,
            consent_type=consent_type,
            status=ConsentStatus.PENDING,
            metadata={"description": description},
        )

        self._consents[consent_id] = record
        return record

    def grant_consent(self, consent_id: str) -> bool:
        """
        授予同意

        Args:
            consent_id: 同意ID

        Returns:
            是否成功
        """
        record: ConsentRecord | None = self._consents.get(consent_id)

        if record is None:
            return False

        record.status = ConsentStatus.GRANTED
        record.granted_at = datetime.now()

        self._log_audit("consent_granted", "consent", DataSensitivity.INTERNAL)
        return True

    def deny_consent(self, consent_id: str) -> bool:
        """
        拒绝同意

        Args:
            consent_id: 同意ID

        Returns:
            是否成功
        """
        record: ConsentRecord | None = self._consents.get(consent_id)

        if record is None:
            return False

        record.status = ConsentStatus.DENIED
        self._log_audit("consent_denied", "consent", DataSensitivity.INTERNAL)
        return True

    def withdraw_consent(self, consent_type: str) -> bool:
        """
        撤回同意

        Args:
            consent_type: 同意类型

        Returns:
            是否成功
        """
        for record in self._consents.values():
            if record.consent_type == consent_type and record.status == ConsentStatus.GRANTED:
                record.status = ConsentStatus.WITHDRAWN
                record.withdrawn_at = datetime.now()

        self._log_audit("consent_withdrawn", consent_type, DataSensitivity.INTERNAL)
        return True

    def has_consent(self, consent_type: str) -> bool:
        """
        检查是否有同意

        Args:
            consent_type: 同意类型

        Returns:
            是否已同意
        """
        for record in self._consents.values():
            if record.consent_type == consent_type and record.status == ConsentStatus.GRANTED:
                return True
        return False

    def get_consent_status(self, consent_type: str) -> ConsentStatus:
        """
        获取同意状态

        Args:
            consent_type: 同意类型

        Returns:
            同意状态
        """
        for record in self._consents.values():
            if record.consent_type == consent_type:
                return record.status
        return ConsentStatus.NOT_REQUESTED

    # ==================== 存储策略 ====================

    def set_storage_policy(
        self, policy: StoragePolicy, retention: RetentionPeriod | None = None
    ) -> None:
        """
        设置存储策略

        Args:
            policy: 存储策略
            retention: 保留期限
        """
        self._config.default_storage_policy = policy

        if retention:
            self._config.default_retention_period = retention

        self._config.updated_at = datetime.now()
        self._save_config()

        self._log_audit("policy_updated", "storage_policy", DataSensitivity.INTERNAL)

    def set_allowed_categories(self, categories: list[str]) -> None:
        """
        设置允许的记忆类型

        Args:
            categories: 允许的类型列表
        """
        self._config.allowed_categories = categories
        self._config.updated_at = datetime.now()
        self._save_config()

    def set_blocked_categories(self, categories: list[str]) -> None:
        """
        设置禁止的记忆类型

        Args:
            categories: 禁止的类型列表
        """
        self._config.blocked_categories = categories
        self._config.updated_at = datetime.now()
        self._save_config()

    def is_category_allowed(self, category: str) -> bool:
        """
        检查记忆类型是否允许

        Args:
            category: 记忆类型

        Returns:
            是否允许
        """
        if category in self._config.blocked_categories:
            return False

        if "all" in self._config.allowed_categories:
            return True

        return category in self._config.allowed_categories

    # ==================== 数据处理 ====================

    def process_for_storage(
        self,
        data: dict[str, Any],
        category: str,
    ) -> dict[str, Any]:
        """
        处理数据以准备存储

        Args:
            data: 原始数据
            category: 数据类别

        Returns:
            处理后的数据
        """
        # 检查类别是否允许
        if not self.is_category_allowed(category):
            self._log_audit("storage_blocked", category, DataSensitivity.SENSITIVE)
            return {}

        # 根据存储策略处理
        if self._config.default_storage_policy == StoragePolicy.NONE:
            return {}

        result: dict[str, Any] = {}

        for field_name, value in data.items():
            classification: DataClassification = self._detector.classify_field(
                field_name, value
            )

            if not classification.should_store:
                continue

            if self._config.default_storage_policy == StoragePolicy.ANONYMOUS:
                if classification.anonymized_value:
                    result[field_name] = classification.anonymized_value
                else:
                    result[field_name] = value
            else:
                result[field_name] = value

            self._log_audit(
                "field_processed",
                f"{category}.{field_name}",
                classification.sensitivity,
            )

        return result

    def should_store_memory(
        self,
        memory_type: str,
        content: str,
    ) -> tuple[bool, str]:
        """
        判断是否应该存储记忆

        Args:
            memory_type: 记忆类型
            content: 记忆内容

        Returns:
            (是否存储, 原因)
        """
        # 检查类别
        if not self.is_category_allowed(memory_type):
            return False, f"记忆类型 '{memory_type}' 未被允许"

        # 检查敏感度
        sensitivity: DataSensitivity = self._detector.classify_content(content)

        if sensitivity == DataSensitivity.RESTRICTED:
            return False, "内容包含受限敏感信息，禁止存储"

        if sensitivity == DataSensitivity.SENSITIVE:
            if self._config.require_consent_for_sensitive:
                if not self.has_consent("sensitive_data"):
                    return False, "敏感数据需要用户授权"

            if self._config.auto_delete_sensitive:
                return False, "配置为自动跳过敏感数据"

        # 检查存储策略
        if self._config.default_storage_policy == StoragePolicy.NONE:
            return False, "存储策略设置为不存储"

        return True, "允许存储"

    # ==================== 数据权利 ====================

    def export_user_data(self) -> dict[str, Any]:
        """
        导出用户数据

        Returns:
            用户数据
        """
        self._log_audit("data_export", "all", DataSensitivity.SENSITIVE)

        return {
            "user_id": self.user_id,
            "privacy_config": self._config.model_dump(mode="json"),
            "consent_records": [r.model_dump(mode="json") for r in self._consents.values()],
            "exported_at": datetime.now().isoformat(),
        }

    def delete_all_user_data(self) -> dict[str, Any]:
        """
        删除所有用户数据

        Returns:
            删除结果
        """
        self._log_audit("data_deletion", "all", DataSensitivity.SENSITIVE)

        # 撤回所有同意
        for consent_type in ["memory_storage", "sensitive_data", "cross_session"]:
            self.withdraw_consent(consent_type)

        # 清除配置
        self._config = PrivacyConfig(user_id=self.user_id)
        self._save_config()

        # 删除存储文件
        config_file: Path = self.storage_path / f"{self.user_id}_privacy.json"
        if config_file.exists():
            config_file.unlink()

        return {
            "deleted": True,
            "user_id": self.user_id,
            "deleted_at": datetime.now().isoformat(),
        }

    # ==================== 审计 ====================

    def _log_audit(
        self,
        action: str,
        data_type: str,
        sensitivity: DataSensitivity,
    ) -> None:
        """记录审计日志"""
        log: PrivacyAuditLog = PrivacyAuditLog(
            log_id=f"audit_{uuid.uuid4().hex[:8]}",
            user_id=self.user_id,
            action=action,
            data_type=data_type,
            sensitivity=sensitivity,
        )

        self._audit_logs.append(log)

        # 限制日志数量
        if len(self._audit_logs) > 1000:
            self._audit_logs = self._audit_logs[-1000:]

    def get_audit_logs(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        获取审计日志

        Args:
            limit: 返回数量限制

        Returns:
            审计日志列表
        """
        return [log.model_dump(mode="json") for log in self._audit_logs[-limit:]]

    # ==================== 配置 ====================

    def get_config(self) -> PrivacyConfig:
        """
        获取隐私配置

        Returns:
            隐私配置
        """
        return self._config

    def update_config(self, **kwargs: Any) -> None:
        """
        更新隐私配置

        Args:
            **kwargs: 配置参数
        """
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

        self._config.updated_at = datetime.now()
        self._save_config()


# ============================================================================
# 隐私声明模板
# ============================================================================


PRIVACY_NOTICE_TEMPLATE: str = """
## Agent Memory System 隐私声明

### 数据收集说明
本系统会存储以下类型的交互数据，以提供个性化的智能服务：

1. **用户画像数据**：您的身份标签、技术背景、沟通偏好、决策风格
2. **程序性记忆**：您的问题解决策略、工具使用习惯、操作偏好
3. **叙事记忆**：您的成长节点、身份演化轨迹
4. **语义记忆**：核心概念、知识实体、原则
5. **情感记忆**：情绪状态、态度倾向、满意度记录

### 敏感数据处理
- 系统会自动识别并标记敏感信息（如密码、账号、证件号等）
- 敏感数据默认**不存储**，或仅存储匿名化哈希值
- 您可以随时配置敏感数据的处理策略

### 您的权利
- **知情权**：了解存储了哪些数据
- **访问权**：导出您的所有数据
- **删除权**：请求删除所有数据
- **限制权**：配置存储策略和范围
- **撤回权**：随时撤回同意

### 数据保留
- 默认保留期限：长期（1年）
- 会话结束后短期记忆自动清除
- 您可以配置自定义保留期限

### 如何管理您的隐私
```
# 查看当前配置
privacy_manager.get_config()

# 设置存储策略（不存储/匿名化存储）
privacy_manager.set_storage_policy(StoragePolicy.ANONYMOUS)

# 禁止特定类型记忆存储
privacy_manager.set_blocked_categories(["emotional", "narrative"])

# 导出所有数据
privacy_manager.export_user_data()

# 删除所有数据
privacy_manager.delete_all_user_data()
```
"""


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    # 枚举
    "ConsentStatus",
    "DataSensitivity",
    "StoragePolicy",
    "RetentionPeriod",
    # 数据模型
    "ConsentRecord",
    "PrivacyConfig",
    "DataClassification",
    "PrivacyAuditLog",
    # 组件
    "SensitiveDataDetector",
    "PrivacyManager",
    # 模板
    "PRIVACY_NOTICE_TEMPLATE",
]
