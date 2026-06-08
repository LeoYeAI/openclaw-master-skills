# Agent Memory System - 加密模块指南

## 目录

1. [概述](#概述)
2. [核心概念](#核心概念)
3. [快速开始](#快速开始)
4. [密钥管理](#密钥管理)
5. [数据加密](#数据加密)
6. [文件存储](#文件存储)
7. [最佳实践](#最佳实践)
8. [API 参考](#api-参考)

---

## 概述

加密模块为 Agent Memory System 提供数据安全保护能力，使用 **AES-256-GCM** 算法对敏感数据进行加密存储。

**核心特性**：
- AES-256-GCM 认证加密（提供机密性和完整性）
- 密钥派生（PBKDF2-HMAC-SHA256）
- 密钥管理器（生成、存储、轮换）
- 加密文件存储（透明加密读写）

**安全等级**：
- 密钥长度：256 bits
- Nonce 长度：96 bits
- 认证标签：128 bits
- KDF 迭代次数：100,000

---

## 核心概念

### 加密算法

**AES-256-GCM**：
- 对称加密算法
- 提供认证加密（AEAD）
- 同时保证机密性和完整性
- 性能优秀，适合本地数据加密

### 密钥派生

**PBKDF2-HMAC-SHA256**：
- 从用户密码派生加密密钥
- 使用盐值防止彩虹表攻击
- 高迭代次数增加暴力破解难度

### 数据结构

```python
class EncryptedData(BaseModel):
    version: str = "1.0"
    algorithm: str = "AES-256-GCM"
    nonce: str  # Base64 编码
    ciphertext: str  # Base64 编码
    salt: Optional[str] = None  # 密钥派生时使用
    created_at: datetime
```

---

## 快速开始

### 安装依赖

```bash
pip install cryptography>=41.0.0
```

### 基本使用

```python
from scripts.encryption import (
    KeyManager,
    DataEncryptor,
    generate_encryption_key,
)
import base64

# 1. 生成密钥（首次使用）
key_b64 = generate_encryption_key()
print(f"请保存此密钥: {key_b64}")

# 2. 初始化
key_manager = KeyManager()
key_manager.set_key("my_key", base64.b64decode(key_b64))
encryptor = DataEncryptor(key_manager=key_manager)

# 3. 加密
encrypted = encryptor.encrypt("敏感数据")

# 4. 解密
decrypted = encryptor.decrypt_to_string(encrypted)
```

---

## 密钥管理

### 初始化密钥管理器

```python
from scripts.encryption import KeyManager

# 初始化时必须指定用户ID和存储路径
key_manager = KeyManager(
    user_id="user_123",
    key_storage_path="./memory_data/keys"  # 由调用方指定
)
```

### 生成密钥

```python
from scripts.encryption import generate_encryption_key

# 生成 Base64 编码的密钥
key_b64 = generate_encryption_key()
# 输出示例: "4KTK41VrwAg1j8NNNXMlQjF2zHr8..."

# 存储到环境变量（变量名由调用方决定）
# export MY_ENCRYPTION_KEY="4KTK41VrwAg1j8NNNXMlQjF2zHr8..."
```

### 从环境变量加载

```python
from scripts.encryption import KeyManager

key_manager = KeyManager(
    user_id="user_123",
    key_storage_path="./memory_data/keys"
)

# 从指定环境变量加载（变量名由调用方指定）
env_var_name = "MEMORY_ENCRYPTION_KEY"  # 或其他名称
if key_manager.load_key_from_env(env_var_name):
    print("密钥加载成功")
else:
    print("环境变量未设置")
```

### 从密码派生密钥

```python
from scripts.encryption import KeyManager

key_manager = KeyManager(
    user_id="user_123",
    key_storage_path="./memory_data/keys"
)

# 从密码派生密钥
password = "user_password_123"
key, salt = key_manager.derive_key_from_password(password)

# 保存盐值（需要与密文一起存储）
key_manager.set_key("derived_key", key)
```

### 密钥存储

```python
# 保存密钥到文件（可选密码保护）
key_file = key_manager.save_key_to_file(
    key_id="my_key",
    key=key_bytes,
    password="optional_password"  # 可选
)

# 从文件加载
key = key_manager.load_key_from_file(
    key_id="my_key",
    password="optional_password"  # 如果有密码保护
)
```

---

## 数据加密

### 加密字符串

```python
from scripts.encryption import DataEncryptor

encryptor = DataEncryptor(key_manager=key_manager)

# 加密
encrypted = encryptor.encrypt("敏感字符串")

# 解密
decrypted = encryptor.decrypt_to_string(encrypted)
```

### 加密字典

```python
# 加密字典
data = {
    "name": "张三",
    "phone": "13800138000",
    "preferences": {"theme": "dark"}
}
encrypted = encryptor.encrypt(data)

# 解密为字典
decrypted = encryptor.decrypt_to_dict(encrypted)
```

### 加密二进制数据

```python
# 加密字节
binary_data = b"\x89PNG\r\n\x1a\n..."
encrypted = encryptor.encrypt(binary_data)

# 解密为字节
decrypted_bytes = encryptor.decrypt(encrypted)
```

---

## 文件存储

### 创建加密文件存储

```python
from scripts.encryption import EncryptedFileStorage

storage = EncryptedFileStorage(
    encryptor=encryptor,
    storage_path="./encrypted_data"
)
```

### 保存数据

```python
data = {
    "user_id": "user_123",
    "memories": [
        {"type": "episodic", "content": "..."},
        {"type": "semantic", "content": "..."},
    ]
}

# 保存为加密文件
file_path = storage.save("user_memories", data)
# 文件路径: ./encrypted_data/user_memories.enc
```

### 加载数据

```python
# 加载并自动解密
data = storage.load("user_memories")
print(data["user_id"])  # "user_123"
```

### 管理文件

```python
# 检查是否存在
if storage.exists("user_memories"):
    print("文件存在")

# 删除文件
storage.delete("user_memories")
```

---

## 最佳实践

### 1. 密钥管理

```python
# ✅ 推荐：从环境变量加载
key_manager = KeyManager()
key_manager.load_key_from_env("MEMORY_ENCRYPTION_KEY")

# ✅ 推荐：使用密钥管理服务（生产环境）
# key_manager.load_from_kms("aws-kms-key-id")

# ❌ 禁止：硬编码密钥
# key_manager.set_key("hardcoded", b"1234567890abcdef...")
```

### 2. 密钥轮换

```python
# 定期轮换密钥（如每90天）
def rotate_encryption_key(old_key_manager: KeyManager) -> KeyManager:
    # 1. 生成新密钥
    new_key_id, new_key = old_key_manager.generate_key()
    
    # 2. 创建新加密器
    new_key_manager = KeyManager()
    new_key_manager.set_key(new_key_id, new_key)
    new_encryptor = DataEncryptor(key_manager=new_key_manager)
    
    # 3. 重新加密所有数据
    # ... 遍历并重新加密所有文件 ...
    
    return new_key_manager
```

### 3. 敏感数据处理流程

```python
from scripts.privacy import PrivacyManager, DataSensitivity
from scripts.encryption import DataEncryptor

def process_sensitive_data(
    data: dict,
    privacy_manager: PrivacyManager,
    encryptor: DataEncryptor,
) -> dict:
    """处理敏感数据的完整流程"""
    
    # 1. 分类数据敏感度
    classification = privacy_manager._detector.classify_field(
        "content", data.get("content", "")
    )
    
    # 2. 根据敏感度处理
    if classification.sensitivity == DataSensitivity.RESTRICTED:
        # 受限数据不存储
        return {}
    
    if classification.sensitivity == DataSensitivity.SENSITIVE:
        # 敏感数据加密存储
        return {
            "encrypted": True,
            "data": encryptor.encrypt(data).model_dump()
        }
    
    # 普通数据直接存储
    return data
```

### 4. 错误处理

```python
from scripts.encryption import DataEncryptor

try:
    decrypted = encryptor.decrypt_to_string(encrypted_data)
except ValueError as e:
    # 解密失败（密钥错误或数据损坏）
    print(f"解密失败: {e}")
    # 记录安全事件
    log_security_event("decryption_failed", str(e))
```

### 5. 性能优化

```python
# 批量加密
def batch_encrypt(
    items: list[dict],
    encryptor: DataEncryptor,
) -> list[dict]:
    """批量加密数据"""
    return [
        {"id": item["id"], "encrypted": encryptor.encrypt(item).model_dump()}
        for item in items
    ]

# 使用缓存（非敏感场景）
from functools import lru_cache

@lru_cache(maxsize=100)
def decrypt_cached(encrypted_json: str) -> dict:
    """缓存解密结果（仅非敏感数据）"""
    return encryptor.decrypt_to_dict(
        EncryptedData.model_validate_json(encrypted_json)
    )
```

---

## API 参考

### KeyManager

#### 初始化

```python
KeyManager(
    user_id: str = "default",
    key_storage_path: str = "./keys"
)
```

#### 方法

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `generate_key()` | 无 | `tuple[str, bytes]` | 生成新密钥 |
| `derive_key_from_password(password, salt?)` | 密码, 盐值 | `tuple[bytes, bytes]` | 从密码派生密钥 |
| `set_key(key_id, key)` | 密钥ID, 密钥 | `None` | 设置当前密钥 |
| `get_key()` | 无 | `tuple[str, bytes]` | 获取当前密钥 |
| `load_key_from_env(env_var?)` | 环境变量名 | `bool` | 从环境变量加载 |
| `save_key_to_file(key_id, key, password?)` | 密钥ID, 密钥, 密码 | `Path` | 保存到文件 |
| `load_key_from_file(key_id, password?)` | 密钥ID, 密码 | `Optional[bytes]` | 从文件加载 |

### DataEncryptor

#### 初始化

```python
DataEncryptor(
    key_manager: Optional[KeyManager] = None,
    config: Optional[EncryptionConfig] = None
)
```

#### 方法

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `encrypt(plaintext)` | 字节/字符串/字典 | `EncryptedData` | 加密数据 |
| `decrypt(encrypted_data)` | `EncryptedData` | `bytes` | 解密为字节 |
| `decrypt_to_string(encrypted_data)` | `EncryptedData` | `str` | 解密为字符串 |
| `decrypt_to_dict(encrypted_data)` | `EncryptedData` | `dict` | 解密为字典 |

### EncryptedFileStorage

#### 初始化

```python
EncryptedFileStorage(
    encryptor: DataEncryptor,
    storage_path: str = "./encrypted_storage"
)
```

#### 方法

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `save(filename, data)` | 文件名, 数据字典 | `Path` | 保存加密文件 |
| `load(filename)` | 文件名 | `dict` | 加载并解密 |
| `exists(filename)` | 文件名 | `bool` | 检查是否存在 |
| `delete(filename)` | 文件名 | `bool` | 删除文件 |

### 辅助函数

| 函数 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `generate_encryption_key()` | 无 | `str` | 生成 Base64 密钥 |
| `encrypt_data_with_password(data, password)` | 数据, 密码 | `tuple[bytes, bytes]` | 用密码加密 |
| `decrypt_data_with_password(data, password, salt)` | 数据, 密码, 盐值 | `bytes` | 用密码解密 |

---

## 安全注意事项

### 密钥安全

1. **禁止硬编码密钥**：不要将密钥写入代码或配置文件
2. **使用环境变量**：通过环境变量传递密钥
3. **使用密钥管理服务**：生产环境推荐使用 KMS
4. **定期轮换**：建议每 90 天轮换一次密钥

### 数据安全

1. **Nonce 唯一性**：每次加密使用新的随机 nonce
2. **完整性验证**：GCM 模式自动验证数据完整性
3. **盐值存储**：使用密码派生时，盐值需与密文一起存储
4. **安全删除**：删除敏感数据时使用安全擦除

### 性能考虑

1. **批量处理**：对大量数据使用批量加密
2. **选择性加密**：仅加密敏感字段
3. **缓存策略**：对频繁访问的非敏感数据可缓存解密结果
