"""
Agent Memory System - Permission Boundary Controller（权限边界控制器）

=== 依赖与环境声明 ===
- 运行环境：Python >=3.9
- 直接依赖:
  * pydantic: >=2.0.0
    - 用途：数据模型验证
  * redis: >=4.5.0
    - 用途：权限缓存和配置存储
- 标准配置文件:
  ```text
  # requirements.txt
  pydantic>=2.0.0
  redis>=4.5.0
  ```
=== 声明结束 ===

安全提醒：权限控制是系统安全的最后一道防线，必须严格实现
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .redis_adapter import RedisAdapter


# ============================================================================
# 枚举类型
# ============================================================================


class PermissionLevel(str, Enum):
    """权限级别"""

    PUBLIC = "public"          # 公开
    INTERNAL = "internal"      # 内部
    CONFIDENTIAL = "confidential"  # 机密
    RESTRICTED = "restricted"  # 限制级
    TOP_SECRET = "top_secret"  # 绝密


class AccessAction(str, Enum):
    """访问动作"""

    READ = "read"              # 读取
    WRITE = "write"            # 写入
    DELETE = "delete"          # 删除
    EXECUTE = "execute"        # 执行
    SHARE = "share"            # 分享
    EXPORT = "export"          # 导出


class DataCategory(str, Enum):
    """数据类别"""

    USER_PROFILE = "user_profile"          # 用户画像
    CONVERSATION = "conversation"          # 对话内容
    MEMORY = "memory"                      # 记忆数据
    TOOL_OUTPUT = "tool_output"            # 工具输出
    SYSTEM_CONFIG = "system_config"        # 系统配置
    SENSITIVE_INFO = "sensitive_info"      # 敏感信息


class SensitiveType(str, Enum):
    """敏感信息类型"""

    API_KEY = "api_key"              # API 密钥
    PASSWORD = "password"            # 密码
    TOKEN = "token"                  # 令牌
    CREDIT_CARD = "credit_card"      # 信用卡
    SSN = "ssn"                      # 社保号
    EMAIL = "email"                  # 邮箱
    PHONE = "phone"                  # 电话
    IP_ADDRESS = "ip_address"        # IP 地址
    PERSONAL_ID = "personal_id"      # 个人证件
    MEDICAL = "medical"              # 医疗信息


class FilterAction(str, Enum):
    """过滤动作"""

    BLOCK = "block"          # 阻止
    REDACT = "redact"        # 脱敏
    MASK = "mask"            # 掩码
    ALLOW = "allow"          # 允许


# ============================================================================
# 数据模型
# ============================================================================


class Permission(BaseModel):
    """权限定义"""

    resource: str                    # 资源标识
    action: AccessAction             # 允许的动作
    conditions: dict[str, Any] = Field(default_factory=dict)  # 条件
    expires_at: datetime | None = None


class Role(BaseModel):
    """角色定义"""

    role_id: str
    name: str
    permissions: list[Permission] = Field(default_factory=list)
    level: PermissionLevel = PermissionLevel.INTERNAL


class UserPermission(BaseModel):
    """用户权限"""

    user_id: str
    roles: list[str] = Field(default_factory=list)
    direct_permissions: list[Permission] = Field(default_factory=list)
    data_access_restrictions: dict[str, PermissionLevel] = Field(default_factory=dict)


class SensitivePattern(BaseModel):
    """敏感信息模式"""

    type: SensitiveType
    pattern: str                     # 正则表达式
    description: str
    severity: PermissionLevel = PermissionLevel.CONFIDENTIAL
    filter_action: FilterAction = FilterAction.REDACT


class FilterResult(BaseModel):
    """过滤结果"""

    original: str
    filtered: str
    detected: list[dict[str, Any]] = Field(default_factory=list)
    actions_taken: list[FilterAction] = Field(default_factory=list)
    was_modified: bool = False


class AccessCheckResult(BaseModel):
    """访问检查结果"""

    allowed: bool
    user_id: str
    resource: str
    action: AccessAction
    permission_level: PermissionLevel
    reason: str | None = None
    restrictions: list[str] = Field(default_factory=list)


class PermissionConfig(BaseModel):
    """权限控制器配置"""

    # 默认权限级别
    default_level: PermissionLevel = Field(default=PermissionLevel.INTERNAL)

    # 敏感信息检测
    enable_sensitive_detection: bool = Field(default=True)
    enable_auto_redact: bool = Field(default=True)

    # 数据边界
    enable_data_boundary: bool = Field(default=True)
    cross_user_access: bool = Field(default=False)

    # 审计
    enable_audit_log: bool = Field(default=True)
    audit_retention_days: int = Field(default=90)


class AuditLog(BaseModel):
    """审计日志"""

    log_id: str = Field(
        default_factory=lambda: f"audit_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    )
    user_id: str
    action: str
    resource: str
    result: str  # allowed, denied, filtered
    details: dict[str, Any] = Field(default_factory=dict)
    ip_address: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# 敏感信息模式库
# ============================================================================

SENSITIVE_PATTERNS: list[SensitivePattern] = [
    # API Key
    SensitivePattern(
        type=SensitiveType.API_KEY,
        pattern=r"(?i)(api[_-]?key|apikey|api_secret)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
        description="API密钥",
        severity=PermissionLevel.RESTRICTED,
        filter_action=FilterAction.REDACT,
    ),
    # Password
    SensitivePattern(
        type=SensitiveType.PASSWORD,
        pattern=r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?([^'\"]{6,})['\"]?",
        description="密码",
        severity=PermissionLevel.RESTRICTED,
        filter_action=FilterAction.MASK,
    ),
    # Token
    SensitivePattern(
        type=SensitiveType.TOKEN,
        pattern=r"(?i)(token|access_token|auth_token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{20,})['\"]?",
        description="访问令牌",
        severity=PermissionLevel.RESTRICTED,
        filter_action=FilterAction.REDACT,
    ),
    # Credit Card
    SensitivePattern(
        type=SensitiveType.CREDIT_CARD,
        pattern=r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        description="信用卡号",
        severity=PermissionLevel.RESTRICTED,
        filter_action=FilterAction.MASK,
    ),
    # SSN
    SensitivePattern(
        type=SensitiveType.SSN,
        pattern=r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
        description="社保号",
        severity=PermissionLevel.RESTRICTED,
        filter_action=FilterAction.MASK,
    ),
    # Email
    SensitivePattern(
        type=SensitiveType.EMAIL,
        pattern=r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        description="电子邮箱",
        severity=PermissionLevel.CONFIDENTIAL,
        filter_action=FilterAction.REDACT,
    ),
    # Phone
    SensitivePattern(
        type=SensitiveType.PHONE,
        pattern=r"\b(?:\+?1[-\s]?)?(?:\(\d{3}\)|\d{3})[-\s]?\d{3}[-\s]?\d{4}\b",
        description="电话号码",
        severity=PermissionLevel.CONFIDENTIAL,
        filter_action=FilterAction.REDACT,
    ),
    # IP Address
    SensitivePattern(
        type=SensitiveType.IP_ADDRESS,
        pattern=r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        description="IP地址",
        severity=PermissionLevel.CONFIDENTIAL,
        filter_action=FilterAction.MASK,
    ),
    # Personal ID (Chinese ID)
    SensitivePattern(
        type=SensitiveType.PERSONAL_ID,
        pattern=r"\b\d{17}[\dXx]\b",
        description="身份证号",
        severity=PermissionLevel.RESTRICTED,
        filter_action=FilterAction.MASK,
    ),
]


# ============================================================================
# Permission Boundary Controller
# ============================================================================


class PermissionBoundaryController:
    """
    权限边界控制器
    
    职责：
    - 访问权限检查
    - 敏感信息识别与过滤
    - 数据边界控制
    - 审计日志记录
    
    使用示例：
    ```python
    from scripts.permission_boundary_controller import (
        PermissionBoundaryController,
        AccessAction,
        DataCategory,
    )

    controller = PermissionBoundaryController()

    # 检查访问权限
    result = controller.check_access(
        user_id="user123",
        resource="memory:long_term:user_profile",
        action=AccessAction.READ,
    )

    if result.allowed:
        # 过滤敏感信息
        filtered = controller.filter_sensitive(content)
        print(filtered.filtered)
    ```
    """

    def __init__(
        self,
        config: PermissionConfig | None = None,
        redis_adapter: RedisAdapter | None = None,
    ):
        """初始化权限控制器"""
        self._config = config or PermissionConfig()
        self._redis = redis_adapter

        # 权限缓存
        self._user_permissions: dict[str, UserPermission] = {}

        # 角色定义
        self._roles: dict[str, Role] = self._init_default_roles()

        # 敏感模式编译
        self._compiled_patterns: list[tuple[re.Pattern, SensitivePattern]] = []
        self._compile_patterns()

        # 审计日志
        self._audit_logs: list[AuditLog] = []

    def _init_default_roles(self) -> dict[str, Role]:
        """初始化默认角色"""
        return {
            "admin": Role(
                role_id="admin",
                name="管理员",
                level=PermissionLevel.RESTRICTED,
                permissions=[
                    Permission(resource="*", action=action)
                    for action in AccessAction
                ],
            ),
            "user": Role(
                role_id="user",
                name="普通用户",
                level=PermissionLevel.INTERNAL,
                permissions=[
                    Permission(resource="user:*", action=AccessAction.READ),
                    Permission(resource="user:*", action=AccessAction.WRITE),
                    Permission(resource="memory:*", action=AccessAction.READ),
                    Permission(resource="memory:*", action=AccessAction.WRITE),
                ],
            ),
            "guest": Role(
                role_id="guest",
                name="访客",
                level=PermissionLevel.PUBLIC,
                permissions=[
                    Permission(resource="public:*", action=AccessAction.READ),
                ],
            ),
        }

    def _compile_patterns(self) -> None:
        """编译敏感模式"""
        for pattern in SENSITIVE_PATTERNS:
            try:
                compiled = re.compile(pattern.pattern)
                self._compiled_patterns.append((compiled, pattern))
            except re.error:
                pass

    # -----------------------------------------------------------------------
    # 权限管理
    # -----------------------------------------------------------------------

    def set_user_permission(
        self,
        user_id: str,
        roles: list[str] | None = None,
        direct_permissions: list[Permission] | None = None,
        data_access_restrictions: dict[str, PermissionLevel] | None = None,
    ) -> None:
        """设置用户权限"""
        permission = UserPermission(
            user_id=user_id,
            roles=roles or ["user"],
            direct_permissions=direct_permissions or [],
            data_access_restrictions=data_access_restrictions or {},
        )
        self._user_permissions[user_id] = permission

    def get_user_permission(self, user_id: str) -> UserPermission | None:
        """获取用户权限"""
        return self._user_permissions.get(user_id)

    def add_role(self, role: Role) -> None:
        """添加角色"""
        self._roles[role.role_id] = role

    # -----------------------------------------------------------------------
    # 访问检查
    # -----------------------------------------------------------------------

    def check_access(
        self,
        user_id: str,
        resource: str,
        action: AccessAction,
        context: dict[str, Any] | None = None,
    ) -> AccessCheckResult:
        """
        检查访问权限

        Args:
            user_id: 用户 ID
            resource: 资源标识（格式：category:subcategory:item）
            action: 访问动作
            context: 上下文信息

        Returns:
            AccessCheckResult 检查结果
        """
        # 获取用户权限
        user_perm = self._user_permissions.get(user_id)

        if not user_perm:
            # 默认权限
            user_perm = UserPermission(
                user_id=user_id,
                roles=["guest"],
            )
            self._user_permissions[user_id] = user_perm

        # 检查角色权限
        allowed, reason = self._check_role_permissions(
            user_perm.roles, resource, action
        )

        # 检查直接权限
        if not allowed:
            allowed, reason = self._check_direct_permissions(
                user_perm.direct_permissions, resource, action
            )

        # 检查数据访问限制
        restrictions = []
        if allowed:
            restrictions = self._get_data_restrictions(
                user_perm, resource
            )

        # 确定权限级别
        level = self._determine_permission_level(user_perm)

        # 记录审计日志
        if self._config.enable_audit_log:
            self._log_audit(
                user_id=user_id,
                action=f"{action.value}:{resource}",
                resource=resource,
                result="allowed" if allowed else "denied",
                details={"reason": reason},
            )

        return AccessCheckResult(
            allowed=allowed,
            user_id=user_id,
            resource=resource,
            action=action,
            permission_level=level,
            reason=reason if not allowed else None,
            restrictions=restrictions,
        )

    def _check_role_permissions(
        self,
        roles: list[str],
        resource: str,
        action: AccessAction,
    ) -> tuple[bool, str]:
        """检查角色权限"""
        for role_id in roles:
            role = self._roles.get(role_id)
            if not role:
                continue

            for perm in role.permissions:
                if self._match_resource(perm.resource, resource):
                    if perm.action == action or perm.action == AccessAction.EXECUTE:
                        return True, f"Role '{role.name}' grants access"

        return False, "No matching role permission"

    def _check_direct_permissions(
        self,
        permissions: list[Permission],
        resource: str,
        action: AccessAction,
    ) -> tuple[bool, str]:
        """检查直接权限"""
        for perm in permissions:
            if self._match_resource(perm.resource, resource):
                if perm.action == action:
                    # 检查过期时间
                    if perm.expires_at and perm.expires_at < datetime.now():
                        continue
                    return True, "Direct permission granted"

        return False, "No matching direct permission"

    def _match_resource(self, pattern: str, resource: str) -> bool:
        """匹配资源"""
        if pattern == "*":
            return True

        # 简单通配符匹配
        if "*" in pattern:
            prefix = pattern.split("*")[0]
            return resource.startswith(prefix)

        return pattern == resource

    def _get_data_restrictions(
        self,
        user_perm: UserPermission,
        resource: str,
    ) -> list[str]:
        """获取数据访问限制"""
        restrictions = []

        for data_type, level in user_perm.data_access_restrictions.items():
            if data_type in resource:
                restrictions.append(f"Data level restricted to: {level.value}")

        return restrictions

    def _determine_permission_level(
        self,
        user_perm: UserPermission,
    ) -> PermissionLevel:
        """确定权限级别"""
        max_level = PermissionLevel.PUBLIC

        for role_id in user_perm.roles:
            role = self._roles.get(role_id)
            if role and self._level_value(role.level) > self._level_value(max_level):
                max_level = role.level

        return max_level

    def _level_value(self, level: PermissionLevel) -> int:
        """权限级别数值"""
        values = {
            PermissionLevel.PUBLIC: 0,
            PermissionLevel.INTERNAL: 1,
            PermissionLevel.CONFIDENTIAL: 2,
            PermissionLevel.RESTRICTED: 3,
            PermissionLevel.TOP_SECRET: 4,
        }
        return values.get(level, 0)

    # -----------------------------------------------------------------------
    # 敏感信息过滤
    # -----------------------------------------------------------------------

    def filter_sensitive(
        self,
        content: str,
        action: FilterAction = FilterAction.REDACT,
    ) -> FilterResult:
        """
        过滤敏感信息

        Args:
            content: 原始内容
            action: 过滤动作

        Returns:
            FilterResult 过滤结果
        """
        if not self._config.enable_sensitive_detection:
            return FilterResult(
                original=content,
                filtered=content,
                was_modified=False,
            )

        filtered = content
        detected: list[dict[str, Any]] = []
        actions_taken: list[FilterAction] = []

        for compiled, pattern in self._compiled_patterns:
            matches = compiled.findall(filtered)

            for match in matches:
                # 匹配可能是字符串或元组
                match_str = match if isinstance(match, str) else match[-1]

                detected.append({
                    "type": pattern.type.value,
                    "description": pattern.description,
                    "severity": pattern.severity.value,
                    "match": match_str[:3] + "***" if len(match_str) > 3 else "***",
                })

                # 应用过滤动作
                filter_action = pattern.filter_action or action
                actions_taken.append(filter_action)

                if filter_action == FilterAction.REDACT:
                    # 替换为 [REDACTED]
                    if isinstance(match, tuple):
                        # 替换整个匹配组
                        full_match = match[-1]
                        filtered = filtered.replace(full_match, "[REDACTED]")
                    else:
                        filtered = filtered.replace(match, "[REDACTED]")

                elif filter_action == FilterAction.MASK:
                    # 部分掩码
                    if isinstance(match, tuple):
                        full_match = match[-1]
                    else:
                        full_match = match

                    if len(full_match) > 4:
                        masked = full_match[:2] + "*" * (len(full_match) - 4) + full_match[-2:]
                        filtered = filtered.replace(full_match, masked)

        return FilterResult(
            original=content,
            filtered=filtered,
            detected=detected,
            actions_taken=actions_taken,
            was_modified=filtered != content,
        )

    def detect_sensitive(
        self,
        content: str,
    ) -> list[dict[str, Any]]:
        """
        检测敏感信息（不过滤）

        Args:
            content: 内容

        Returns:
            检测到的敏感信息列表
        """
        detected: list[dict[str, Any]] = []

        for compiled, pattern in self._compiled_patterns:
            matches = compiled.findall(content)

            for match in matches:
                match_str = match if isinstance(match, str) else match[-1]
                detected.append({
                    "type": pattern.type.value,
                    "description": pattern.description,
                    "severity": pattern.severity.value,
                    "position": content.find(match_str) if match_str in content else -1,
                })

        return detected

    # -----------------------------------------------------------------------
    # 数据边界控制
    # -----------------------------------------------------------------------

    def check_data_boundary(
        self,
        source_user: str,
        target_user: str,
        data_category: DataCategory,
    ) -> tuple[bool, str]:
        """
        检查数据边界

        Args:
            source_user: 数据来源用户
            target_user: 目标用户
            data_category: 数据类别

        Returns:
            (是否允许, 原因)
        """
        if not self._config.enable_data_boundary:
            return True, "Data boundary check disabled"

        # 同一用户
        if source_user == target_user:
            return True, "Same user access"

        # 跨用户访问
        if not self._config.cross_user_access:
            return False, "Cross-user access not allowed"

        # 检查权限级别
        source_perm = self._user_permissions.get(source_user)
        target_perm = self._user_permissions.get(target_user)

        if source_perm and target_perm:
            source_level = self._determine_permission_level(source_perm)
            target_level = self._determine_permission_level(target_perm)

            # 目标用户权限级别必须 >= 数据敏感度
            if self._level_value(target_level) >= self._level_value(source_level):
                return True, "Permission level sufficient"

        return False, "Permission level insufficient"

    # -----------------------------------------------------------------------
    # 审计日志
    # -----------------------------------------------------------------------

    def _log_audit(
        self,
        user_id: str,
        action: str,
        resource: str,
        result: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """记录审计日志"""
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            result=result,
            details=details or {},
        )
        self._audit_logs.append(log)

    def get_audit_logs(
        self,
        user_id: str | None = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """
        获取审计日志

        Args:
            user_id: 用户 ID（可选，筛选特定用户）
            limit: 最大返回数量

        Returns:
            审计日志列表
        """
        logs = self._audit_logs

        if user_id:
            logs = [log for log in logs if log.user_id == user_id]

        return logs[-limit:]

    # -----------------------------------------------------------------------
    # 内容哈希
    # -----------------------------------------------------------------------

    def hash_content(self, content: str) -> str:
        """生成内容哈希"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# ============================================================================
# 工厂函数
# ============================================================================


def create_permission_controller(
    enable_sensitive_detection: bool = True,
    enable_auto_redact: bool = True,
    enable_audit_log: bool = True,
    redis_adapter: RedisAdapter | None = None,
) -> PermissionBoundaryController:
    """
    创建权限边界控制器

    Args:
        enable_sensitive_detection: 启用敏感信息检测
        enable_auto_redact: 启用自动脱敏
        enable_audit_log: 启用审计日志
        redis_adapter: Redis 适配器（可选）

    Returns:
        PermissionBoundaryController 实例
    """
    config = PermissionConfig(
        enable_sensitive_detection=enable_sensitive_detection,
        enable_auto_redact=enable_auto_redact,
        enable_audit_log=enable_audit_log,
    )

    return PermissionBoundaryController(config=config, redis_adapter=redis_adapter)


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "PermissionLevel",
    "AccessAction",
    "DataCategory",
    "SensitiveType",
    "FilterAction",
    "Permission",
    "Role",
    "UserPermission",
    "SensitivePattern",
    "FilterResult",
    "AccessCheckResult",
    "PermissionConfig",
    "AuditLog",
    "PermissionBoundaryController",
    "create_permission_controller",
]
