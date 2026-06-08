# Agent Memory System - 隐私配置指南

## 目录

1. [概述](#概述)
2. [核心概念](#核心概念)
3. [敏感数据分类](#敏感数据分类)
4. [同意管理](#同意管理)
5. [存储策略](#存储策略)
6. [数据权利](#数据权利)
7. [最佳实践](#最佳实践)
8. [API 参考](#api-参考)

---

## 概述

隐私配置模块为 Agent Memory System 提供完整的隐私保护能力，确保系统符合 GDPR、CCPA 等数据保护法规要求。

**核心目标**：
- 用户知情同意
- 敏感数据识别与保护
- 灵活的存储策略
- 数据权利保障（访问、删除、导出）

---

## 核心概念

### 数据敏感度级别

| 级别 | 说明 | 存储策略 |
|------|------|----------|
| `PUBLIC` | 公开数据 | 完整存储 |
| `INTERNAL` | 内部数据 | 完整存储（默认） |
| `SENSITIVE` | 敏感数据 | 匿名化存储或跳过 |
| `RESTRICTED` | 受限数据 | 禁止存储 |

### 存储策略

```python
class StoragePolicy(str, Enum):
    FULL = "full"                    # 完整存储
    ANONYMIZED = "anonymized"         # 匿名化存储
    AGGREGATED = "aggregated"         # 聚合存储（仅统计）
    NONE = "none"                     # 不存储
```

### 保留期限

```python
class RetentionPeriod(str, Enum):
    SESSION_ONLY = "session_only"     # 仅会话期间
    SHORT_TERM = "short_term"         # 短期（7天）
    MEDIUM_TERM = "medium_term"       # 中期（30天）
    LONG_TERM = "long_term"           # 长期（1年）
    INDEFINITE = "indefinite"         # 无限期
```

---

## 敏感数据分类

### 自动识别的敏感信息类型

| 类别 | 关键词示例 |
|------|-----------|
| **个人身份信息** | 身份证、护照、驾照、社保号、ID card、passport、SSN |
| **金融信息** | 银行卡、信用卡、账号、密码、PIN、bank account、CVV |
| **健康信息** | 病历、诊断、处方、medical record、diagnosis |
| **凭证信息** | token、API key、secret、密钥、私钥、access token |
| **联系方式** | 手机号、电话、邮箱、地址、phone、email |

### 受限数据（绝对不存储）

以下内容会被自动识别为 `RESTRICTED` 并拒绝存储：
- "密码是/密码为/password is/my password"
- "卡号是/card number is"
- "账号是/account number"

### 使用示例

```python
from scripts.privacy import SensitiveDataDetector

detector = SensitiveDataDetector()

# 检测内容敏感度
content = "我的银行卡号是 6222 0000 1234 5678"
sensitivity = detector.classify_content(content)
# 返回: DataSensitivity.RESTRICTED

# 分类字段
classification = detector.classify_field("api_key", "sk-xxxxx")
# 返回: DataClassification(
#   sensitivity=DataSensitivity.RESTRICTED,
#   should_store=False
# )
```

---

## 同意管理

### 同意类型

| 同意类型 | 说明 |
|----------|------|
| `memory_storage` | 允许存储记忆数据 |
| `sensitive_data` | 允许处理敏感数据 |
| `cross_session` | 允许跨会话持久化 |

### 同意状态

```python
class ConsentStatus(str, Enum):
    NOT_REQUESTED = "not_requested"   # 未请求
    PENDING = "pending"               # 待确认
    GRANTED = "granted"               # 已授权
    DENIED = "denied"                 # 已拒绝
    WITHDRAWN = "withdrawn"           # 已撤回
```

### 使用示例

```python
from scripts.privacy import PrivacyManager

privacy_manager = PrivacyManager(user_id="user_123")

# 请求同意
consent = privacy_manager.request_consent(
    consent_type="memory_storage",
    description="是否允许系统存储您的交互记忆以提供个性化服务？"
)

# 用户授权
privacy_manager.grant_consent(consent.consent_id)

# 检查同意状态
if privacy_manager.has_consent("memory_storage"):
    print("用户已授权存储记忆")

# 撤回同意
privacy_manager.withdraw_consent("memory_storage")
```

---

## 存储策略

### 配置存储策略

```python
from scripts.privacy import StoragePolicy, RetentionPeriod

# 设置匿名化存储，保留30天
privacy_manager.set_storage_policy(
    policy=StoragePolicy.ANONYMOUS,
    retention=RetentionPolicy.MEDIUM_TERM
)

# 设置不存储任何数据
privacy_manager.set_storage_policy(StoragePolicy.NONE)
```

### 控制记忆类型

```python
# 仅允许存储语义记忆和程序性记忆
privacy_manager.set_allowed_categories([
    "semantic",
    "procedural",
    "episodic"
])

# 禁止存储情感记忆和叙事记忆
privacy_manager.set_blocked_categories([
    "emotional",
    "narrative"
])

# 检查类型是否允许
if privacy_manager.is_category_allowed("emotional"):
    print("允许存储情感记忆")
else:
    print("情感记忆已被禁止")
```

### 处理数据存储

```python
# 判断是否应该存储
should_store, reason = privacy_manager.should_store_memory(
    memory_type="episodic",
    content="用户表示对Python很感兴趣"
)

if should_store:
    # 处理数据准备存储
    processed_data = privacy_manager.process_for_storage(
        data={"content": content, "timestamp": datetime.now()},
        category="episodic"
    )
else:
    print(f"不存储: {reason}")
```

---

## 数据权利

### 访问权 - 导出数据

```python
user_data = privacy_manager.export_user_data()
# 返回:
# {
#   "user_id": "user_123",
#   "privacy_config": {...},
#   "consent_records": [...],
#   "exported_at": "2025-01-15T10:30:00"
# }
```

### 删除权 - 删除所有数据

```python
result = privacy_manager.delete_all_user_data()
# 返回:
# {
#   "deleted": True,
#   "user_id": "user_123",
#   "deleted_at": "2025-01-15T10:30:00"
# }
```

### 查看审计日志

```python
logs = privacy_manager.get_audit_logs(limit=50)
# 返回最近的50条审计记录
```

---

## 最佳实践

### 1. 初始化时请求同意

```python
# 在首次使用时请求同意
if privacy_manager.get_consent_status("memory_storage") == ConsentStatus.NOT_REQUESTED:
    consent = privacy_manager.request_consent(
        consent_type="memory_storage",
        description=PRIVACY_NOTICE_TEMPLATE  # 使用标准隐私声明
    )
    # 等待用户授权...
```

### 2. 敏感数据处理

```python
# 处理用户输入
user_input = "我的手机号是 13800138000"

should_store, reason = privacy_manager.should_store_memory(
    memory_type="episodic",
    content=user_input
)

if not should_store:
    # 跳过存储或要求匿名化
    processed = privacy_manager.process_for_storage(
        data={"content": user_input},
        category="episodic"
    )
    # processed["content"] == "[ANONYMIZED:abc123ef]"
```

### 3. 定期清理过期数据

```python
# 根据保留期限清理
config = privacy_manager.get_config()
if config.default_retention_period == RetentionPeriod.SHORT_TERM:
    # 7天后清理
    cleanup_memories_older_than(days=7)
```

---

## API 参考

### PrivacyManager

#### 初始化

```python
PrivacyManager(
    user_id: str = "default_user",
    storage_path: str = "./privacy_data"
)
```

#### 同意管理

| 方法 | 参数 | 返回值 |
|------|------|--------|
| `request_consent(consent_type, description)` | 同意类型, 描述 | `ConsentRecord` |
| `grant_consent(consent_id)` | 同意ID | `bool` |
| `deny_consent(consent_id)` | 同意ID | `bool` |
| `withdraw_consent(consent_type)` | 同意类型 | `bool` |
| `has_consent(consent_type)` | 同意类型 | `bool` |
| `get_consent_status(consent_type)` | 同意类型 | `ConsentStatus` |

#### 存储策略

| 方法 | 参数 | 返回值 |
|------|------|--------|
| `set_storage_policy(policy, retention)` | 策略, 期限 | `None` |
| `set_allowed_categories(categories)` | 类型列表 | `None` |
| `set_blocked_categories(categories)` | 类型列表 | `None` |
| `is_category_allowed(category)` | 类型 | `bool` |
| `should_store_memory(memory_type, content)` | 类型, 内容 | `tuple[bool, str]` |
| `process_for_storage(data, category)` | 数据, 类别 | `dict` |

#### 数据权利

| 方法 | 参数 | 返回值 |
|------|------|--------|
| `export_user_data()` | 无 | `dict` |
| `delete_all_user_data()` | 无 | `dict` |
| `get_audit_logs(limit)` | 数量 | `list[dict]` |
| `get_config()` | 无 | `PrivacyConfig` |
| `update_config(**kwargs)` | 配置参数 | `None` |

---

## 集成示例

### 与短期记忆集成

```python
from scripts.short_term import ShortTermMemoryManager
from scripts.privacy import PrivacyManager, StoragePolicy

privacy_manager = PrivacyManager(user_id="user_123")

# 检查同意
if not privacy_manager.has_consent("memory_storage"):
    # 请求同意
    consent = privacy_manager.request_consent(
        consent_type="memory_storage",
        description="允许存储短期记忆？"
    )
    # 等待用户授权...

# 初始化短期记忆
short_term = ShortTermMemoryManager(
    privacy_manager=privacy_manager  # 注入隐私管理器
)

# 添加记忆（自动隐私检查）
short_term.add_memory(
    content="用户提到密码是123456",  # 敏感内容
    semantic_type="episodic"
)
# 自动被隐私管理器拦截，不存储
```

### 与长期记忆集成

```python
from scripts.long_term import LongTermMemoryManager

long_term = LongTermMemoryManager(
    privacy_manager=privacy_manager
)

# 存储前自动处理
memory_id = long_term.store(
    content="用户的手机号是13800138000",
    category="episodic"
)
# 存储为: "用户的手机号是[ANONYMIZED:abc123ef]"
```

---

## 法规合规

### GDPR 合规清单

- ✅ **知情权**: 通过 `PRIVACY_NOTICE_TEMPLATE` 提供
- ✅ **访问权**: 通过 `export_user_data()` 实现
- ✅ **删除权**: 通过 `delete_all_user_data()` 实现
- ✅ **限制权**: 通过 `set_blocked_categories()` 配置
- ✅ **数据可携带权**: 导出为标准 JSON 格式
- ✅ **同意管理**: 完整的同意生命周期管理

### CCPA 合规清单

- ✅ **知情权**: 隐私声明告知数据收集类型
- ✅ **删除权**: 支持删除所有个人数据
- ✅ **选择退出权**: 可配置不存储数据
- ✅ **非歧视权**: 基础功能不依赖同意
