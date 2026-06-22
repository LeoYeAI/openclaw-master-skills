# /// script
# dependencies = [
#   "pyyaml>=6.0",
# ]
# ///
"""
配置管理模块
从环境变量或YAML文件加载配置，支持全局配置和本地配置
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import yaml


# 宝塔面板最低版本要求
MIN_PANEL_VERSION = "9.0.0"

# 全局配置文件路径
GLOBAL_CONFIG_DIR = Path.home() / ".openclaw"
GLOBAL_CONFIG_FILE = GLOBAL_CONFIG_DIR / "bt-skills.yaml"


@dataclass
class ThresholdConfig:
    """告警阈值配置"""

    cpu: int = 80
    memory: int = 85
    disk: int = 90


@dataclass
class GlobalConfig:
    """全局配置"""

    retry_count: int = 3
    retry_delay: int = 1000
    concurrency: int = 3
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)


@dataclass
class ServerConfig:
    """服务器配置"""

    name: str
    host: str
    token: str
    timeout: int = 10000
    enabled: bool = True


@dataclass
class Config:
    """完整配置"""

    servers: list[ServerConfig] = field(default_factory=list)
    global_config: GlobalConfig = field(default_factory=GlobalConfig)

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """从字典创建配置"""
        servers = []
        for s in data.get("servers", []):
            servers.append(
                ServerConfig(
                    name=s["name"],
                    host=s["host"],
                    token=s["token"],
                    timeout=s.get("timeout", 10000),
                    enabled=s.get("enabled", True),
                )
            )

        global_data = data.get("global", {})
        thresholds_data = global_data.get("thresholds", {})
        thresholds = ThresholdConfig(
            cpu=thresholds_data.get("cpu", 80),
            memory=thresholds_data.get("memory", 85),
            disk=thresholds_data.get("disk", 90),
        )
        global_config = GlobalConfig(
            retry_count=global_data.get("retryCount", 3),
            retry_delay=global_data.get("retryDelay", 1000),
            concurrency=global_data.get("concurrency", 3),
            thresholds=thresholds,
        )

        return cls(servers=servers, global_config=global_config)


def get_global_config_path() -> Path:
    """
    获取全局配置文件路径

    Returns:
        全局配置文件路径
    """
    return GLOBAL_CONFIG_FILE


def ensure_global_config_dir() -> Path:
    """
    确保全局配置目录存在

    Returns:
        全局配置目录路径
    """
    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return GLOBAL_CONFIG_DIR


def create_default_global_config() -> Path:
    """
    创建默认的全局配置文件

    Returns:
        创建的配置文件路径
    """
    ensure_global_config_dir()

    default_config = f"""# 宝塔面板日志巡检技能包配置
# 配置文件路径: {GLOBAL_CONFIG_FILE}
#
# 此配置文件可被 AI 工具读取和修改
# 宝塔面板版本要求: >= {MIN_PANEL_VERSION}

servers:
  # 服务器配置示例
  # - name: "prod-01"
  #   host: "https://your-panel.com:8888"
  #   token: "YOUR_API_TOKEN"
  #   timeout: 10000
  #   enabled: true

global:
  # 请求重试次数
  retryCount: 3
  # 重试间隔（毫秒）
  retryDelay: 1000
  # 并发请求数限制
  concurrency: 3
  # 告警阈值配置
  thresholds:
    cpu: 80        # CPU使用率告警阈值(%)
    memory: 85     # 内存使用率告警阈值(%)
    disk: 90       # 磁盘使用率告警阈值(%)
"""

    if not GLOBAL_CONFIG_FILE.exists():
        GLOBAL_CONFIG_FILE.write_text(default_config, encoding="utf-8")

    return GLOBAL_CONFIG_FILE


def find_config_file() -> Optional[str]:
    """
    查找配置文件

    按以下顺序查找:
    1. BT_CONFIG_PATH 环境变量
    2. 全局配置文件 ~/.openclaw/bt-skills.yaml
    3. 当前目录下的 config/servers.local.yaml
    4. 当前目录下的 config/servers.yaml
    """
    # 1. 环境变量
    env_path = os.environ.get("BT_CONFIG_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    # 2. 全局配置文件
    if GLOBAL_CONFIG_FILE.exists():
        return str(GLOBAL_CONFIG_FILE)

    # 3. 本地配置
    local_path = Path("config/servers.local.yaml")
    if local_path.exists():
        return str(local_path)

    # 4. 默认配置
    default_path = Path("config/servers.yaml")
    if default_path.exists():
        return str(default_path)

    return None


def load_config(config_path: Optional[str] = None) -> dict[str, Any]:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径，为None时自动查找

    Returns:
        配置字典

    Raises:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: YAML解析错误
    """
    if config_path is None:
        config_path = find_config_file()

    if config_path is None:
        # 尝试创建默认全局配置
        try:
            config_path = str(create_default_global_config())
        except Exception:
            pass

    if config_path is None:
        raise FileNotFoundError(
            f"未找到配置文件。\n"
            f"解决方案:\n"
            f"1. 设置 BT_CONFIG_PATH 环境变量\n"
            f"2. 创建全局配置文件: {GLOBAL_CONFIG_FILE}\n"
            f"3. 创建本地配置文件: config/servers.local.yaml"
        )

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config or {}


def load_config_object(config_path: Optional[str] = None) -> Config:
    """
    加载配置并返回Config对象

    Args:
        config_path: 配置文件路径

    Returns:
        Config对象
    """
    data = load_config(config_path)
    return Config.from_dict(data)


def get_servers(config_path: Optional[str] = None) -> list[ServerConfig]:
    """
    获取服务器列表

    Args:
        config_path: 配置文件路径

    Returns:
        服务器配置列表
    """
    config = load_config_object(config_path)
    return [s for s in config.servers if s.enabled]


def get_thresholds(config_path: Optional[str] = None) -> ThresholdConfig:
    """
    获取告警阈值配置

    Args:
        config_path: 配置文件路径

    Returns:
        阈值配置
    """
    config = load_config_object(config_path)
    return config.global_config.thresholds


def normalize_host(host: str) -> str:
    """
    规范化面板地址

    处理用户输入的各种格式：
    - 192.168.69.154:8888 -> https://192.168.69.154:8888
    - 192.168.69.154:8888/soft/plugin -> https://192.168.69.154:8888
    - panel.example.com:8888 -> https://panel.example.com:8888
    - https://panel.example.com:8888/ -> https://panel.example.com:8888
    - http://panel.example.com:8888 -> http://panel.example.com:8888

    Args:
        host: 用户输入的面板地址

    Returns:
        规范化后的URL
    """
    host = host.strip()

    # 如果没有 scheme，添加 https://
    if not host.startswith(("http://", "https://")):
        # 检查是否以 IP 或域名开头（可能包含端口或路径）
        host = "https://" + host

    # 解析 URL
    parsed = urlparse(host)

    # 移除路径部分，只保留 scheme://netloc
    # netloc 包含 host:port
    normalized = f"{parsed.scheme}://{parsed.netloc}"

    return normalized


def validate_host(host: str) -> tuple[bool, str]:
    """
    验证面板地址

    Args:
        host: 面板地址

    Returns:
        (是否有效, 错误信息或规范化后的地址)
    """
    try:
        normalized = normalize_host(host)
        parsed = urlparse(normalized)

        # 检查是否有有效的 netloc
        if not parsed.netloc:
            return False, "无效的面板地址：缺少主机名"

        # 检查端口
        if ":" in parsed.netloc:
            _, port_str = parsed.netloc.rsplit(":", 1)
            try:
                port = int(port_str)
                if port < 1 or port > 65535:
                    return False, f"无效的端口号：{port}"
            except ValueError:
                return False, f"无效的端口号：{port_str}"

        return True, normalized

    except Exception as e:
        return False, f"无效的面板地址：{str(e)}"


def add_server(name: str, host: str, token: str, timeout: int = 10000, enabled: bool = True, config_path: Optional[str] = None) -> bool:
    """
    添加服务器配置

    Args:
        name: 服务器名称
        host: 面板地址（自动规范化）
        token: API Token
        timeout: 超时时间
        enabled: 是否启用
        config_path: 配置文件路径

    Returns:
        是否添加成功

    Raises:
        ValueError: 地址格式无效
    """
    # 规范化地址
    is_valid, result = validate_host(host)
    if not is_valid:
        raise ValueError(result)
    host = result

    if config_path is None:
        config_path = str(GLOBAL_CONFIG_FILE)

    # 确保目录存在
    ensure_global_config_dir()

    # 加载现有配置
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        config = {"servers": [], "global": {}}

    # 检查是否已存在
    servers = config.get("servers", [])
    for s in servers:
        if s.get("name") == name:
            # 更新现有配置
            s["host"] = host
            s["token"] = token
            s["timeout"] = timeout
            s["enabled"] = enabled
            break
    else:
        # 添加新配置
        servers.append({
            "name": name,
            "host": host,
            "token": token,
            "timeout": timeout,
            "enabled": enabled,
        })

    config["servers"] = servers

    # 确保有全局配置
    if "global" not in config:
        config["global"] = {
            "retryCount": 3,
            "retryDelay": 1000,
            "concurrency": 3,
            "thresholds": {"cpu": 80, "memory": 85, "disk": 90},
        }

    # 保存配置
    path = Path(config_path)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return True


def remove_server(name: str, config_path: Optional[str] = None) -> bool:
    """
    移除服务器配置

    Args:
        name: 服务器名称
        config_path: 配置文件路径

    Returns:
        是否移除成功
    """
    if config_path is None:
        config_path = str(GLOBAL_CONFIG_FILE)

    try:
        config = load_config(config_path)
    except FileNotFoundError:
        return False

    servers = config.get("servers", [])
    original_count = len(servers)
    config["servers"] = [s for s in servers if s.get("name") != name]

    if len(config["servers"]) == original_count:
        return False  # 未找到

    # 保存配置
    path = Path(config_path)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return True


def update_thresholds(cpu: Optional[int] = None, memory: Optional[int] = None, disk: Optional[int] = None, config_path: Optional[str] = None) -> bool:
    """
    更新告警阈值配置

    Args:
        cpu: CPU阈值
        memory: 内存阈值
        disk: 磁盘阈值
        config_path: 配置文件路径

    Returns:
        是否更新成功
    """
    if config_path is None:
        config_path = str(GLOBAL_CONFIG_FILE)

    try:
        config = load_config(config_path)
    except FileNotFoundError:
        config = {"servers": [], "global": {}}

    if "global" not in config:
        config["global"] = {}

    if "thresholds" not in config["global"]:
        config["global"]["thresholds"] = {"cpu": 80, "memory": 85, "disk": 90}

    if cpu is not None:
        config["global"]["thresholds"]["cpu"] = cpu
    if memory is not None:
        config["global"]["thresholds"]["memory"] = memory
    if disk is not None:
        config["global"]["thresholds"]["disk"] = disk

    # 保存配置
    path = Path(config_path)
    ensure_global_config_dir()
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return True


def get_config_info() -> dict:
    """
    获取配置信息（供 AI 读取）

    Returns:
        配置信息字典
    """
    config_path = find_config_file()

    info = {
        "min_panel_version": MIN_PANEL_VERSION,
        "global_config_path": str(GLOBAL_CONFIG_FILE),
        "current_config_path": config_path,
        "config_exists": config_path is not None and Path(config_path).exists(),
        "env_var": "BT_CONFIG_PATH",
        "env_var_value": os.environ.get("BT_CONFIG_PATH"),
    }

    if config_path and Path(config_path).exists():
        try:
            config = load_config(config_path)
            info["server_count"] = len(config.get("servers", []))
            info["servers"] = [
                {"name": s.get("name"), "host": s.get("host"), "enabled": s.get("enabled", True)}
                for s in config.get("servers", [])
            ]
            info["thresholds"] = config.get("global", {}).get("thresholds", {})
        except Exception as e:
            info["error"] = str(e)

    return info
