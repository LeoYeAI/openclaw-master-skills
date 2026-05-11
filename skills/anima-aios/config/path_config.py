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

r"""
Anima-AIOS - 路径配置 (v6.2.2)

支持不同操作系统和环境的路径配置：
- Linux 服务器：/home/画像
- macOS: /Users/用户名/画像
- Windows: C:/Users/用户名/画像

v6.2.2 新增：支持 per-Agent 配置覆盖

使用方法：
    from config.path_config import Config
    config = Config()
    facts_base = config.facts_base
    openclaw_base = config.openclaw_base
"""

import os
import platform
from pathlib import Path
from typing import Optional


class Config:
    """路径配置类"""
    
    # 默认路径（Linux）
    DEFAULT_FACTS_BASE = '/home/画像'
    DEFAULT_OPENCLAW_BASE = os.path.expanduser('~/.openclaw')
    
    def __init__(self, facts_base: Optional[str] = None, 
                 openclaw_base: Optional[str] = None):
        """
        初始化路径配置
        
        Args:
            facts_base: facts 基础路径（可选，默认自动检测）
            openclaw_base: OpenClaw 基础路径（可选，默认自动检测）
        """
        self._facts_base = facts_base
        self._openclaw_base = openclaw_base
        
        # 自动检测系统
        self.system = platform.system()
        self.is_linux = self.system == 'Linux'
        self.is_macos = self.system == 'Darwin'
        self.is_windows = self.system == 'Windows'
    
    @property
    def facts_base(self) -> Path:
        """获取 facts 基础路径
        
        优先级：
        1. 构造函数传入的 facts_base
        2. 环境变量 ANIMA_FACTS_BASE
        3. 新配置加载器（支持 per-Agent 覆盖，v6.2.2+）
        4. 旧配置文件 ~/.anima/config/anima_config.json 中的 facts_base（向后兼容）
        5. 系统自动检测（Linux: /home/画像，macOS: ~/画像，Windows: ~/画像）
        """
        if self._facts_base:
            return Path(self._facts_base)
        
        # 环境变量优先
        env_base = os.getenv("ANIMA_FACTS_BASE")
        if env_base:
            return Path(env_base)
        
        # 新配置加载器（v6.2.2+）
        try:
            from config.config_loader import get_config
            config = get_config()
            if config.get("facts_base"):
                return Path(config["facts_base"])
        except Exception:
            pass
        
        # 向后兼容：旧配置文件
        config_file = Path(os.path.expanduser("~/.anima/config/anima_config.json"))
        if config_file.exists():
            try:
                import json
                with open(config_file) as f:
                    cfg = json.load(f)
                if cfg.get("facts_base"):
                    return Path(cfg["facts_base"])
            except Exception:
                pass
        
        # 系统自动检测
        if self.is_linux:
            return Path('/home/画像')
        elif self.is_macos:
            username = os.getenv('USER', 'user')
            return Path(f'/Users/{username}/画像')
        elif self.is_windows:
            username = os.getenv('USERNAME', 'user')
            return Path(f'C:/Users/{username}/画像')
        else:
            return Path(self.DEFAULT_FACTS_BASE)
    
    @property
    def openclaw_base(self) -> Path:
        """获取 OpenClaw 基础路径"""
        if self._openclaw_base:
            return Path(self._openclaw_base)
        
        # 自动检测
        if self.is_linux:
            return Path(os.path.expanduser('~/.openclaw'))
        elif self.is_macos:
            username = os.getenv('USER', 'user')
            return Path(f'/Users/{username}/.openclaw')
        elif self.is_windows:
            username = os.getenv('USERNAME', 'user')
            return Path(f'C:/Users/{username}/.openclaw')
        else:
            # 默认 Linux
            return Path(self.DEFAULT_OPENCLAW_BASE)
    
    @property
    def agents_dir(self) -> Path:
        """获取 Agent 目录"""
        return self.facts_base
    
    @property
    def backup_dir(self) -> Path:
        """获取备份目录"""
        return self.facts_base / '.backup'
    
    @property
    def shared_dir(self) -> Path:
        """获取共享目录"""
        return self.facts_base / 'shared'
    
    @property
    def message_queue_base(self) -> Path:
        """获取消息队列基础路径"""
        return self.facts_base.parent / '消息队列'
    
    @property
    def openclaw_agents_dir(self) -> Path:
        """获取 OpenClaw Agents 目录"""
        return self.openclaw_base / 'agents'
    
    def get_agent_dir(self, agent_name: str) -> Path:
        """
        获取指定 Agent 的目录
        
        Args:
            agent_name: Agent 名称
        
        Returns:
            Agent 目录路径
        """
        return self.facts_base / agent_name
    
    def get_agent_facts_dir(self, agent_name: str) -> Path:
        """
        获取指定 Agent 的 facts 目录
        
        Args:
            agent_name: Agent 名称
        
        Returns:
            facts 目录路径
        """
        return self.facts_base / agent_name / 'facts'
    
    def get_agent_inbox_dir(self, agent_name: str) -> Path:
        """
        获取指定 Agent 的 inbox 目录
        
        Args:
            agent_name: Agent 名称
        
        Returns:
            inbox 目录路径
        """
        return self.message_queue_base / 'inbox' / agent_name
    
    def to_dict(self) -> dict:
        """
        导出配置为字典
        
        Returns:
            配置字典
        """
        return {
            'system': self.system,
            'facts_base': str(self.facts_base),
            'openclaw_base': str(self.openclaw_base),
            'agents_dir': str(self.agents_dir),
            'backup_dir': str(self.backup_dir),
            'shared_dir': str(self.shared_dir),
            'message_queue_base': str(self.message_queue_base),
            'openclaw_agents_dir': str(self.openclaw_agents_dir),
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return (f"Config(system={self.system}, "
                f"facts_base={self.facts_base}, "
                f"openclaw_base={self.openclaw_base})")


# 全局配置实例
config = Config()


def get_config() -> Config:
    """获取全局配置实例"""
    return config


# 测试
if __name__ == '__main__':
    cfg = Config()
    print("=== 路径配置测试 ===")
    print()
    print(f"系统：{cfg.system}")
    print(f"facts_base: {cfg.facts_base}")
    print(f"openclaw_base: {cfg.openclaw_base}")
    print()
    print("完整配置:")
    for key, value in cfg.to_dict().items():
        print(f"  {key}: {value}")
