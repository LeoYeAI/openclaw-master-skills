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
Anima-AIOS - Agent 名称检测公共模块

统一的 Agent 名称检测逻辑，替代分散在各模块中的独立实现。

优先级：
1. ANIMA_AGENT_NAME 环境变量
2. ANIMA_WORKSPACE 环境变量
3. 解析 SOUL.md
4. 解析 IDENTITY.md
5. 工作目录路径解析
6. 自动扫描 facts_base
7. 默认值 "Agent"
"""

import os
import re
from pathlib import Path
from typing import Optional


def resolve_agent_name(workspace: Optional[Path] = None,
                       facts_base: Optional[Path] = None) -> str:
    """
    获取当前 Agent 名称（统一入口）
    
    Args:
        workspace: OpenClaw workspace 路径（可选）
        facts_base: facts 基础路径（可选）
    
    Returns:
        Agent 名称
    """
    # 1. 环境变量（手动覆盖，最高优先级）
    agent_name = os.getenv("ANIMA_AGENT_NAME")
    if agent_name:
        return agent_name
    
    # 2. ANIMA_WORKSPACE（OpenClaw 注入）
    ws = os.getenv("ANIMA_WORKSPACE") or os.getenv("WORKSPACE")
    if ws:
        workspace = Path(ws)
    
    # 如果没传 workspace，尝试自动检测
    if workspace is None:
        openclaw_dir = Path(os.path.expanduser("~/.openclaw"))
        cwd = Path.cwd()
        # 从当前工作目录推断
        if ".openclaw" in str(cwd):
            for part in cwd.parts:
                if part.startswith("workspace-"):
                    workspace = openclaw_dir / part
                    break
        # 默认使用 ~/.openclaw/workspace
        if workspace is None:
            workspace = openclaw_dir / "workspace"
    
    # 从 workspace 名称推断
    ws_name = workspace.name
    if ws_name.startswith("workspace-"):
        ws_name = ws_name[len("workspace-"):]
    
    # 3. 解析 SOUL.md
    if workspace.exists():
        soul_file = workspace / "SOUL.md"
        if soul_file.exists():
            name = parse_soul_file(soul_file)
            if name:
                return name
        
        # 4. 解析 IDENTITY.md
        identity_file = workspace / "IDENTITY.md"
        if identity_file.exists():
            name = parse_identity_file(identity_file)
            if name:
                return name
    
    # 5. 如果 workspace 名称不是 "workspace"，直接用它
    if ws_name and ws_name != "workspace":
        return ws_name
    
    # 6. 自动扫描 facts_base
    if facts_base and facts_base.exists():
        for agent_dir in facts_base.iterdir():
            if agent_dir.is_dir():
                exp_file = agent_dir / "exp_history.jsonl"
                if exp_file.exists():
                    return agent_dir.name
    
    # 7. 默认值
    return "Agent"


def parse_soul_file(file_path: Path) -> Optional[str]:
    """
    从 SOUL.md 解析 Agent 名称
    
    支持格式：
    - # SOUL.md - 清禾 的灵魂
    - **姓名：** 清禾 (Qīng Hé)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # 模式 1: # SOUL.md - {Name} 的灵魂
        match = re.search(r'#\s*SOUL\.md\s*-\s*(.+?)(?:\s*的)', content)
        if match:
            name = match.group(1).strip().split('\n')[0].strip()
            if name:
                return name
        
        # 模式 2: **姓名：** {Name}
        match = re.search(r'\*\*姓名[：:]\*\*\s*(.+)', content)
        if match:
            name = match.group(1).strip().split('\n')[0].strip()
            # 清理括号（如 "清禾 (Qīng Hé)" → "清禾"）
            name = re.sub(r'\s*\(.*?\)', '', name).strip()
            if name:
                return name
    except Exception:
        pass
    
    return None


def parse_identity_file(file_path: Path) -> Optional[str]:
    """
    从 IDENTITY.md 解析 Agent 名称
    
    支持格式：
    - **Name:** 清禾 (Qīng Hé)
    
    修复 Z-BUG-001: 正则截断，防止把整个文件内容当名字
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # 匹配 **Name:** 后面的内容，只取第一行
        match = re.search(r'\*\*Name:\*\*\s*(.+)', content)
        if match:
            name = match.group(1).strip().split('\n')[0].strip()
            # 清理括号
            name = re.sub(r'\s*\(.*?\)', '', name).strip()
            # 清理多余的 markdown 格式
            name = name.rstrip('*').strip()
            if name and len(name) < 50:  # 安全检查：名字不应该超过 50 字符
                return name
    except Exception:
        pass
    
    return None
