# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

"""EMR Skill 配置管理。

本模块提供统一的 EMR Serverless 访问配置加载能力，支持：

- 从环境变量读取 AK/SK、Region、Endpoint、Service；
- 可选从简单的本地配置文件中读取缺省值（KEY=VALUE 格式）；
- 提供默认队列名，方便上层 Skill 在未显式指定队列时回退使用；
- 在出现配置问题时给出清晰的错误提示，但不会打印任何 AK/SK 明文。

- 环境变量约定（统一使用 `VOLCENGINE_*` 前缀）：

- ``VOLCENGINE_AK`` / ``VOLCENGINE_SK``：访问凭证（必填）；
- ``VOLCENGINE_REGION``：区域，默认为 ``cn-beijing``；
- ``VOLCENGINE_ENDPOINT``：服务 Endpoint，未设置时根据 Region 推导
  （形如 ``emr-serverless.{region}.volcengineapi.com``）；
- ``VOLCENGINE_SERVICE``：服务名称，默认为 ``emr_serverless``；
- ``EMR_DEFAULT_QUEUE``：默认队列名称（可选）；
- ``EMR_SKILL_CONFIG`` 或 ``EMR_SKILLS_CONFIG``：可选配置文件路径，
  文件格式为 ``KEY=VALUE``，键名沿用上述环境变量名。
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional, Iterable, Any

try:
    from serverless.client import ServerlessClient
except Exception as e:
    ServerlessClient = Any

class EMRSkillConfigError(Exception):
    """在加载 EMR Skill 配置时发生错误。"""


@dataclass
class EMRSkillConfig:
    """EMR Skill 运行所需的最小配置集合。

    Attributes:
        access_key: 火山引擎访问密钥 AK。
        secret_key: 火山引擎访问密钥 SK。
        region: 区域，例如 ``cn-beijing``。
        endpoint: EMR Serverless 服务的 Endpoint。
        service: 服务名称，通常为 ``emr_serverless``。
        default_queue: 默认队列名称（可选），在未显式指定队列时可回退使用。
    """

    access_key: str
    secret_key: str
    region: str
    endpoint: str
    service: str
    default_queue: Optional[str] = None


def _load_simple_kv_file(path: str) -> Dict[str, str]:
    """加载简单 ``KEY=VALUE`` 格式的配置文件。

    读取失败或文件不存在时返回空字典，不会抛出异常。
    """

    data: Dict[str, str] = {}
    if not path or not os.path.exists(path):
        return data

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()
    except OSError:
        # 配置文件读取失败时退化为仅使用环境变量
        return {}

    return data


def _get_with_fallback(
        key: str,
        file_cfg: Dict[str, str],
        default: Optional[str] = None,
) -> Optional[str]:
    """优先从环境变量读取，其次从配置文件，最后使用默认值。"""

    return os.getenv(key) or file_cfg.get(key, default)


def _get_any_of(
        keys: Iterable[str],
        file_cfg: Dict[str, str],
        default: Optional[str] = None,
) -> Optional[str]:
    """按顺序从多组键中选择首个有效值。

    读取优先级：环境变量 > 配置文件 > 默认值。
    """

    for k in keys:
        val = os.getenv(k) or file_cfg.get(k)
        if val:
            return val
    return default


def load_emr_skill_config(config_file: Optional[str] = None) -> EMRSkillConfig:
    """从环境变量与可选配置文件加载 EMR Skill 配置。

    优先级：环境变量 > 配置文件 > 内置默认值。

    环境变量 ``VOLCENGINE_AK`` 与 ``VOLCENGINE_SK`` 为必填项，缺失时会抛出
    :class:`EMRSkillConfigError`，错误信息仅包含缺失字段名，不包含
    任何明文凭证内容。

    Args:
        config_file: 可选配置文件路径（KEY=VALUE 格式）。如未显式传入，
            将依次尝试环境变量 ``EMR_SKILL_CONFIG`` 与 ``EMR_SKILLS_CONFIG``。

    Returns:
        EMRSkillConfig: 解析后的配置对象。

    Raises:
        EMRSkillConfigError: 当缺少必要的访问凭证或配置不完整时抛出。
    """

    file_path = (
            config_file
            or os.getenv("EMR_SKILL_CONFIG")
            or os.getenv("EMR_SKILLS_CONFIG")
    )
    file_cfg: Dict[str, str] = _load_simple_kv_file(file_path) if file_path else {}

    ak = _get_with_fallback("VOLCENGINE_AK", file_cfg)
    sk = _get_with_fallback("VOLCENGINE_SK", file_cfg)
    region = _get_with_fallback("VOLCENGINE_REGION", file_cfg, "cn-beijing") or "cn-beijing"

    # Endpoint：优先使用显式配置，其次根据 Region 推导
    endpoint = _get_with_fallback("VOLCENGINE_ENDPOINT", file_cfg)
    if not endpoint:
        endpoint = f"emr-serverless.{region}.volcengineapi.com"

    service = _get_with_fallback("VOLCENGINE_SERVICE", file_cfg, "emr_serverless") or "emr_serverless"
    default_queue = _get_with_fallback("EMR_DEFAULT_QUEUE", file_cfg)

    missing = [name for name, value in (("VOLCENGINE_AK", ak), ("VOLCENGINE_SK", sk)) if not value]
    if missing:
        # 注意：这里仅提示缺失字段名，不打印任何密钥内容
        raise EMRSkillConfigError(
            "缺少必要的访问凭证: {}。请通过环境变量或配置文件进行设置。".format(
                ", ".join(missing)
            )
        )

    return EMRSkillConfig(
        access_key=ak or "",
        secret_key=sk or "",
        region=region,
        endpoint=endpoint,
        service=service,
        default_queue=default_queue,
    )


def build_serverless_client() -> ServerlessClient:
    from serverless.auth import StaticCredentials
    from scripts.config import load_emr_skill_config
    from scripts.config import EMRSkillConfigError
    try:
        skill_cfg = load_emr_skill_config()
    except EMRSkillConfigError as exc:
        raise RuntimeError(f"EMR Skill 配置错误: {exc}") from exc
    try:
        credentials = StaticCredentials(skill_cfg.access_key, skill_cfg.secret_key)
        client = ServerlessClient(
            credentials=credentials,
            endpoint=skill_cfg.endpoint,
            service=skill_cfg.service,
            region=skill_cfg.region,
            scheme="https",
            connection_timeout=60,
            socket_timeout=60,
        )
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"初始化 EMR Serverless SDK Client 失败: {exc}") from exc
    return client


# 半托管region-endpoint映射
semi_managed_region_endpoint_map = {
    "cn-shanghai": "emr.cn-shanghai.volcengineapi.com",
    "cn-guangzhou": "emr.cn-guangzhou.volcengineapi.com",
    "cn-beijing": "emr.cn-beijing.volcengineapi.com",
    "ap-southeast-1": "emr.ap-southeast-1.volcengineapi.com",
    "cn-beijing-selfdrive": "emr.cn-beijing-selfdrive.volcengineapi.com",
    "cn-beijing-autodriving": "emr.cn-beijing-autodriving.volcengineapi.com",
    "cn-shanghai-autodriving": "emr.cn-shanghai-autodriving.volcengineapi.com",
}

# 全托管region-endpoint映射
full_managed_region_endpoint_map = {
    "cn-shanghai": "emr-serverless.cn-shanghai.volcengineapi.com",
    "cn-guangzhou": "emr-serverless.cn-guangzhou.volcengineapi.com",
    "cn-beijing": "emr-serverless.cn-beijing.volcengineapi.com",
    "ap-southeast-1": "emr-serverless.ap-southeast-1.volcengineapi.com",
    "cn-beijing-selfdrive": "emr-serverless.cn-beijing-selfdrive.volcengineapi.com",
    "cn-hongkong": "emr-serverless.cn-hongkong.volcengineapi.com",
    "cn-shanghai-autodriving": "emr-serverless.cn-shanghai-autodriving.volcengineapi.com",
}

cloud_monitor_endpoint_map = {
    "cn-beijing-autodriving": "cloudmonitor.cn-beijing-autodriving.volcengineapi.com",
    "ap-southeast-1": "cloudmonitor.ap-southeast-1.volcengineapi.com",
    "cn-hongkong": "cloudmonitor.cn-hongkong.volcengineapi.com",
    "ap-southeast-2": "cloudmonitor.ap-southeast-2.volcengineapi.com",
    "ap-southeast-3": "cloudmonitor.ap-southeast-3.volcengineapi.com",
    "cn-beijing": "cloudmonitor.cn-beijing.volcengineapi.com",
    "cn-shanghai": "cloudmonitor.cn-shanghai.volcengineapi.com",
    "cn-guangzhou": "cloudmonitor.cn-guangzhou.volcengineapi.com",
    "cn-beijing-selfdrive": "cloudmonitor.cn-beijing-selfdrive.volcengineapi.com",
    "cn-shanghai-autodriving": "cloudmonitor.cn-shanghai-autodriving.volcengineapi.com"
}
