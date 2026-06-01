"""EMR Skill 顶层配置包。

提供从环境变量或本地文件加载 EMR Serverless 访问配置的统一入口，
供 openclaw skill 或其他集成代码复用。
"""

from .config import EMRSkillConfig, EMRSkillConfigError, load_emr_skill_config, build_serverless_client

__all__ = [
    "EMRSkillConfig",
    "EMRSkillConfigError",
    "load_emr_skill_config",
    "build_serverless_client"
]
