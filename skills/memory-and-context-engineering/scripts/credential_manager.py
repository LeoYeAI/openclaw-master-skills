"""
Agent Memory System - 凭证管理模块

提供自动化的凭证加密存储与读取能力：
- 存储时自动加密
- 读取时自动解密
- 主密钥自动管理（环境变量或自动生成）

使用示例：
    manager = CredentialManager(storage_path="./memory_data/credentials")
    
    # 存储凭证（自动加密）
    manager.store("github_token", "ghp_xxxxx")
    
    # 读取凭证（自动解密）
    token = manager.get("github_token")
    
    # 列出已存储的凭证
    names = manager.list()
    
    # 删除凭证
    manager.delete("github_token")
"""

from __future__ import annotations

import base64
import json
import os
import secrets
import stat
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

# 延迟导入加密库
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    AESGCM = None  # type: ignore


# ============================================================================
# 常量
# ============================================================================

KEY_LENGTH: int = 32  # 256 bits
NONCE_LENGTH: int = 12  # 96 bits
MASTER_KEY_ENV_VAR: str = "MEMORY_MASTER_KEY"
MASTER_KEY_FILE: str = ".master_key"
CREDENTIALS_FILE: str = "credentials.enc"


# ============================================================================
# 数据模型
# ============================================================================


class CredentialRecord(BaseModel):
    """凭证记录（元数据，不含明文）"""
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CredentialStorage(BaseModel):
    """凭证存储结构"""
    version: str = "1.0"
    algorithm: str = "AES-256-GCM"
    credentials: dict[str, str] = Field(default_factory=dict)  # name -> encrypted_b64
    records: dict[str, CredentialRecord] = Field(default_factory=dict)  # name -> metadata


# ============================================================================
# 凭证管理器
# ============================================================================


class CredentialManager:
    """
    凭证管理器
    
    提供自动化的凭证加密存储与读取：
    - 存储时自动加密
    - 读取时自动解密
    - 主密钥自动管理
    
    密钥来源优先级：
    1. 初始化时传入的 master_key 参数
    2. 环境变量 MEMORY_MASTER_KEY
    3. 自动生成并存储到 {storage_path}/.master_key
    """
    
    def __init__(
        self,
        storage_path: str,
        master_key: Optional[str] = None,
    ) -> None:
        """
        初始化凭证管理器
        
        Args:
            storage_path: 凭证存储路径（必需）
            master_key: 主密钥（Base64编码），不传则自动管理
        """
        self.storage_path: Path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化主密钥
        self._master_key: bytes = self._init_master_key(master_key)
        
        # 加载已有凭证
        self._storage: CredentialStorage = self._load_storage()
    
    def _init_master_key(self, provided_key: Optional[str]) -> bytes:
        """
        初始化主密钥
        
        优先级：
        1. 调用方传入
        2. 环境变量
        3. 自动生成
        """
        # 1. 使用调用方传入的密钥
        if provided_key:
            return base64.b64decode(provided_key)
        
        # 2. 从环境变量读取
        env_key = os.getenv(MASTER_KEY_ENV_VAR)
        if env_key:
            return base64.b64decode(env_key)
        
        # 3. 从密钥文件读取或自动生成
        key_file = self.storage_path / MASTER_KEY_FILE
        
        if key_file.exists():
            key_b64 = key_file.read_text().strip()
            return base64.b64decode(key_b64)
        
        # 自动生成密钥
        new_key = secrets.token_bytes(KEY_LENGTH)
        key_b64 = base64.b64encode(new_key).decode("utf-8")
        
        # 保存密钥文件
        key_file.write_text(key_b64)
        
        # 设置文件权限（仅所有者可读写）
        key_file.chmod(stat.S_IRUSR | stat.S_IWUSR)
        
        return new_key
    
    def _load_storage(self) -> CredentialStorage:
        """加载凭证存储"""
        storage_file = self.storage_path / CREDENTIALS_FILE
        
        if not storage_file.exists():
            return CredentialStorage()
        
        try:
            encrypted_b64 = storage_file.read_text().strip()
            encrypted = base64.b64decode(encrypted_b64)
            decrypted = self._decrypt(encrypted)
            data = json.loads(decrypted)
            return CredentialStorage.model_validate(data)
        except Exception:
            # 加载失败则返回空存储
            return CredentialStorage()
    
    def _save_storage(self) -> None:
        """保存凭证存储"""
        storage_file = self.storage_path / CREDENTIALS_FILE
        
        data = self._storage.model_dump(mode="json")
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        encrypted = self._encrypt(json_str.encode("utf-8"))
        encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")
        
        storage_file.write_text(encrypted_b64)
        
        # 设置文件权限
        storage_file.chmod(stat.S_IRUSR | stat.S_IWUSR)
    
    def _encrypt(self, plaintext: bytes) -> bytes:
        """加密数据"""
        if not CRYPTO_AVAILABLE or AESGCM is None:
            raise RuntimeError("cryptography 库未安装，无法加密")
        
        nonce = secrets.token_bytes(NONCE_LENGTH)
        aesgcm = AESGCM(self._master_key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        return nonce + ciphertext
    
    def _decrypt(self, encrypted: bytes) -> bytes:
        """解密数据"""
        if not CRYPTO_AVAILABLE or AESGCM is None:
            raise RuntimeError("cryptography 库未安装，无法解密")
        
        nonce = encrypted[:NONCE_LENGTH]
        ciphertext = encrypted[NONCE_LENGTH:]
        
        aesgcm = AESGCM(self._master_key)
        return aesgcm.decrypt(nonce, ciphertext, None)
    
    # ========================================================================
    # 公共 API
    # ========================================================================
    
    def store(
        self,
        name: str,
        value: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        存储凭证（自动加密）
        
        Args:
            name: 凭证名称（如 "github_token"）
            value: 凭证明文值
            metadata: 可选元数据
        """
        # 加密凭证值
        encrypted = self._encrypt(value.encode("utf-8"))
        encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")
        
        # 存储
        self._storage.credentials[name] = encrypted_b64
        
        # 更新记录
        if name in self._storage.records:
            record = self._storage.records[name]
            record.updated_at = datetime.now()
            if metadata:
                record.metadata.update(metadata)
        else:
            self._storage.records[name] = CredentialRecord(
                name=name,
                metadata=metadata or {},
            )
        
        self._save_storage()
    
    def get(self, name: str) -> Optional[str]:
        """
        获取凭证（自动解密）
        
        Args:
            name: 凭证名称
            
        Returns:
            凭证明文值，不存在则返回 None
        """
        encrypted_b64 = self._storage.credentials.get(name)
        if not encrypted_b64:
            return None
        
        try:
            encrypted = base64.b64decode(encrypted_b64)
            decrypted = self._decrypt(encrypted)
            return decrypted.decode("utf-8")
        except Exception:
            return None
    
    def exists(self, name: str) -> bool:
        """
        检查凭证是否存在
        
        Args:
            name: 凭证名称
            
        Returns:
            是否存在
        """
        return name in self._storage.credentials
    
    def list(self) -> list[str]:
        """
        列出已存储的凭证名称
        
        Returns:
            凭证名称列表
        """
        return list(self._storage.credentials.keys())
    
    def get_record(self, name: str) -> Optional[CredentialRecord]:
        """
        获取凭证记录（元数据）
        
        Args:
            name: 凭证名称
            
        Returns:
            凭证记录，不存在则返回 None
        """
        return self._storage.records.get(name)
    
    def delete(self, name: str) -> bool:
        """
        删除凭证
        
        Args:
            name: 凭证名称
            
        Returns:
            是否成功删除
        """
        if name not in self._storage.credentials:
            return False
        
        del self._storage.credentials[name]
        self._storage.records.pop(name, None)
        
        self._save_storage()
        return True
    
    def clear(self) -> int:
        """
        清空所有凭证
        
        Returns:
            删除的凭证数量
        """
        count = len(self._storage.credentials)
        self._storage.credentials.clear()
        self._storage.records.clear()
        self._save_storage()
        return count
    
    def export_master_key(self) -> str:
        """
        导出主密钥（用于备份或迁移）
        
        Returns:
            Base64 编码的主密钥
        """
        return base64.b64encode(self._master_key).decode("utf-8")


# ============================================================================
# 便捷函数
# ============================================================================


def create_credential_manager(
    storage_path: str,
    master_key: Optional[str] = None,
) -> CredentialManager:
    """
    创建凭证管理器的便捷函数
    
    Args:
        storage_path: 凭证存储路径
        master_key: 主密钥（可选）
        
    Returns:
        CredentialManager 实例
    """
    return CredentialManager(storage_path=storage_path, master_key=master_key)
