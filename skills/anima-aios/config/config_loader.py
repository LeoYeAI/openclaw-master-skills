#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2026 Anima-AIOS Contributors
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

"""
Anima-AIOS - 配置加载器 (v6.2.2)

支持 per-Agent 配置覆盖：
- 全局配置：~/.anima/config/config.json
- Agent 覆盖：~/.anima/config/agents/{agent_name}.json
- 最终配置 = 全局默认 + Agent 覆盖（深度合并）

优先级：
1. 环境变量（最高）
2. Agent 覆盖配置
3. 全局配置
4. 代码默认值
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器，支持 per-Agent 覆盖"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "version": "6.2.3",
        "facts_base": "/home/画像",
        "normalization": {
            "mode": "auto",
            "use_global_benchmark": False,
            "team_size_threshold": {
                "percentile": 5,
                "hybrid": 2,
                "absolute": 1
            }
        },
        "weights": {
            "understanding": 0.20,
            "application": 0.20,
            "creation": 0.25,
            "metacognition": 0.15,
            "collaboration": 0.20
        },
        "benchmarks": {
            "understanding": {"novice": 10, "beginner": 30, "competent": 60, "proficient": 100, "expert": 200},
            "application": {"novice": 5, "beginner": 15, "competent": 30, "proficient": 60, "expert": 120},
            "creation": {"novice": 0, "beginner": 5, "competent": 15, "proficient": 30, "expert": 50},
            "metacognition": {"novice": 2, "beginner": 8, "competent": 15, "proficient": 30, "expert": 60},
            "collaboration": {"novice": 3, "beginner": 10, "competent": 25, "proficient": 50, "expert": 100}
        },
        "daily_exp_limits": {
            "understanding": 50,
            "application": 40,
            "creation": 60,
            "metacognition": 30,
            "collaboration": 50
        },
        "quality_thresholds": {
            "fact": {"short": 50, "normal": 200, "long": 200}
        },
        "daily_quests": {
            "enabled": True,
            "refresh_time": "05:00",
            "check_interval_hours": 1,
            "all_complete_bonus": 50
        },
        "llm": {
            "provider": "current_agent",
            "models": {
                "quality_assess": "current_agent",
                "dedup_analyze": "current_agent",
                "palace_classify": "current_agent"
            }
        },
        "palace": {
            "classify_mode": "deferred",
            "poll_interval_minutes": 30,
            "quiet_threshold_seconds": 60,
            "retry_delay_seconds": 60
        },
        "pyramid": {
            "auto_distill": False,
            "distill_threshold": 3
        },
        "team_mode": False
    }
    
    def __init__(self, agent_name: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            agent_name: Agent 名称（可选，不传则从环境变量或自动检测）
        """
        self.agent_name = agent_name or self._detect_agent_name()
        self.config_dir = Path(os.path.expanduser("~/.anima/config"))
        self.global_config_path = self.config_dir / "config.json"
        self.agent_config_path = self.config_dir / "agents" / f"{self.agent_name}.json"
    
    def _detect_agent_name(self) -> str:
        """检测 Agent 名称
        
        优先级：
        1. 环境变量 ANIMA_AGENT_NAME（最高）
        2. OpenClaw 上下文（OPENCLAW_WORKSPACE，兼容模式）
        3. 自动扫描 SOUL.md
        4. 兜底值 "unknown"
        """
        # 1. 主要环境变量
        env_name = os.getenv("ANIMA_AGENT_NAME")
        if env_name:
            return env_name
        
        # 2. OpenClaw 上下文（兼容模式，deprecated 警告）
        workspace = os.getenv("OPENCLAW_WORKSPACE")
        if workspace:
            import warnings
            warnings.warn(
                "OPENCLAW_WORKSPACE is deprecated, use ANIMA_AGENT_NAME instead",
                DeprecationWarning,
                stacklevel=2
            )
            # 从路径提取 Agent 名称
            parts = workspace.split("/")
            for part in reversed(parts):
                if part.startswith("workspace-"):
                    return part.replace("workspace-", "")
        
        # 3. 自动扫描 SOUL.md
        soul_path = Path(workspace or "~/.openclaw/workspace").expanduser() / "SOUL.md"
        if soul_path.exists():
            try:
                with open(soul_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # 查找 **姓名：** 行
                for line in content.split("\n"):
                    if "**姓名：**" in line:
                        name = line.split("**姓名：**")[1].strip()
                        return name
            except Exception:
                pass
        
        # 4. 兜底
        return "unknown"
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """加载 JSON 文件，不存在返回空字典"""
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """深度合并两个字典
        
        Args:
            base: 基础字典
            override: 覆盖字典
        
        Returns:
            合并后的字典
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # 递归合并子字典
                result[key] = self._deep_merge(result[key], value)
            else:
                # 直接覆盖
                result[key] = value
        
        return result
    
    def load(self) -> Dict[str, Any]:
        """加载配置
        
        优先级：
        1. 环境变量（最高）
        2. Agent 覆盖配置
        3. 全局配置
        4. 代码默认值
        
        Returns:
            最终配置字典
        """
        # 1. 加载全局配置
        global_config = self._load_json(self.global_config_path)
        
        # 2. 加载 Agent 覆盖配置
        agent_config = self._load_json(self.agent_config_path)
        
        # 3. 深度合并：默认 + 全局 + Agent
        config = self._deep_merge(self.DEFAULT_CONFIG, global_config)
        config = self._deep_merge(config, agent_config)
        
        # 4. 环境变量覆盖（最高优先级）
        if os.getenv("ANIMA_FACTS_BASE"):
            config["facts_base"] = os.getenv("ANIMA_FACTS_BASE")
        
        if os.getenv("ANIMA_TEAM_MODE"):
            config["team_mode"] = os.getenv("ANIMA_TEAM_MODE").lower() == "true"
        
        # 5. 确保 version 是最新的
        config["version"] = self.DEFAULT_CONFIG["version"]
        
        return config
    
    def save_global(self, config: Dict[str, Any]) -> None:
        """保存全局配置"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.global_config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def save_agent(self, config: Dict[str, Any]) -> None:
        """保存 Agent 覆盖配置"""
        agent_config_dir = self.config_dir / "agents"
        agent_config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.agent_config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


# 全局配置加载器实例
_loader: Optional[ConfigLoader] = None


def get_config(agent_name: Optional[str] = None) -> Dict[str, Any]:
    """获取配置（单例模式）
    
    Args:
        agent_name: Agent 名称（可选）
    
    Returns:
        配置字典
    """
    global _loader
    if _loader is None:
        _loader = ConfigLoader(agent_name)
    return _loader.load()


def reload_config(agent_name: Optional[str] = None) -> Dict[str, Any]:
    """重新加载配置
    
    Args:
        agent_name: Agent 名称（可选）
    
    Returns:
        配置字典
    """
    global _loader
    _loader = ConfigLoader(agent_name)
    return _loader.load()


# 测试
if __name__ == "__main__":
    print("=== Anima-AIOS 配置加载器测试 (v6.2.2) ===\n")
    
    # 测试配置加载
    config = get_config()
    print(f"当前 Agent: {ConfigLoader().agent_name}")
    print(f"配置版本：{config['version']}")
    print(f"facts_base: {config['facts_base']}")
    print(f"team_mode: {config['team_mode']}")
    print(f"llm.provider: {config['llm']['provider']}")
    print()
    print("完整配置:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
