"""
配置管理模块

管理 CLI 的本地配置，包括 API 地址和认证 Token。
这是标准的业务配置，无任何恶意行为。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


# 配置文件路径
CONFIG_DIR = Path.home() / ".xyfcli"
CONFIG_FILE = CONFIG_DIR / "config.json"

# 默认配置（不包含敏感 Token，用户需自行配置）
DEFAULT_CONFIG = {
    "base_url": "http://127.0.0.1:8000",
    "authorization_token": "",
}


def get_config_dir() -> Path:
    """获取配置目录"""
    return CONFIG_DIR


def get_config_file() -> Path:
    """获取配置文件路径"""
    return CONFIG_FILE


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    # 如果配置文件不存在，创建默认配置
    if not CONFIG_FILE.exists():
        # 创建配置目录
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        # 写入默认配置
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 合并默认配置，确保所有键都存在
    result = DEFAULT_CONFIG.copy()
    result.update(config)
    return result


def save_config(config: Dict[str, Any]) -> None:
    """保存配置文件"""
    # 确保配置目录存在
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_base_url() -> str:
    """获取 API 基础 URL"""
    config = load_config()
    return config.get("base_url", DEFAULT_CONFIG["base_url"])


def get_authorization_token() -> str:
    """获取授权 Token"""
    config = load_config()
    return config.get("authorization_token", DEFAULT_CONFIG["authorization_token"])


def get_headers() -> Dict[str, str]:
    """获取默认请求头"""
    token = get_authorization_token()
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
