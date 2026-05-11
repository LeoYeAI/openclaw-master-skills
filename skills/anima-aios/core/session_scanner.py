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
Memora v4.0 - Session Scanner

扫描 OpenClaw 的 session 记录，初始化 Agent 的初始等级

扫描路径：/root/.openclaw/agents/{agent 名称}/sessions/

EXP 计算规则：
- 每条 session 记录：+1 EXP（基础参与）
- 每次 toolCall（工具调用）：+1 EXP（实际操作）
- 每次代码写入（write 工具）：+2 EXP（创造性工作）
- 每次文件读取（read 工具）：+0.5 EXP（学习行为）
- 每次 exec（命令执行）：+1 EXP（系统操作）

等级公式：level = max(1, int(exp ^ 0.28))

Author: 枢衡
Date: 2026-03-20
Version: 5.0.0
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 导入路径配置
try:
    from ..config.path_config import get_config
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).parent.parent / 'config'))
    from path_config import get_config


class SessionScanner:
    """Session 记录扫描器"""
    
    # EXP 奖励规则
    EXP_RULES = {
        'session_base': 1,      # 每条 session 基础 EXP
        'tool_call': 1,         # 每次工具调用
        'write_tool': 2,        # write 工具（创造性工作）
        'read_tool': 0.5,       # read 工具（学习行为）
        'exec_tool': 1,         # exec 工具（系统操作）
        'message_assistant': 0.5,  # 每条 assistant 消息
    }
    
    # Agent 名称映射：动态从 SOUL.md/IDENTITY.md 解析，不再硬编码
    AGENT_NAME_MAP = {}  # 运行时动态填充

    @classmethod
    def _resolve_agent_cn_name(cls, agent_dir_name: str, openclaw_base: Path) -> str:
        """从 workspace 的 SOUL.md/IDENTITY.md 动态解析 Agent 中文名"""
        if agent_dir_name in cls.AGENT_NAME_MAP:
            return cls.AGENT_NAME_MAP[agent_dir_name]
        
        try:
            from .agent_resolver import parse_soul_file, parse_identity_file
        except ImportError:
            from agent_resolver import parse_soul_file, parse_identity_file
        
        ws_name = f"workspace-{agent_dir_name}" if agent_dir_name != "main" else "workspace"
        ws_path = openclaw_base / ws_name
        
        # 尝试解析
        soul = ws_path / "SOUL.md"
        if soul.exists():
            name = parse_soul_file(soul)
            if name:
                cls.AGENT_NAME_MAP[agent_dir_name] = name
                return name
        
        identity = ws_path / "IDENTITY.md"
        if identity.exists():
            name = parse_identity_file(identity)
            if name:
                cls.AGENT_NAME_MAP[agent_dir_name] = name
                return name
        
        cls.AGENT_NAME_MAP[agent_dir_name] = agent_dir_name
        return agent_dir_name
    
    def __init__(self, openclaw_base: Optional[str] = None,
                 facts_base: Optional[str] = None):
        """
        初始化扫描器
        
        Args:
            openclaw_base: OpenClaw 基础目录（可选，默认自动检测）
            facts_base: facts 基础目录（可选，默认自动检测）
        """
        config = get_config()
        
        if openclaw_base:
            self.openclaw_base = Path(openclaw_base)
        else:
            self.openclaw_base = config.openclaw_base
        
        if facts_base:
            self.facts_base = Path(facts_base)
        else:
            self.facts_base = config.facts_base
        
        self.agents_dir = self.openclaw_base / 'agents'
    
    def scan_all_agents(self) -> Dict[str, Dict]:
        """
        扫描所有 Agent 的 session 记录
        
        Returns:
            {agent_name: {'exp': int, 'level': int, 'sessions': int, 'tool_calls': int}}
        """
        results = {}
        
        if not self.agents_dir.exists():
            print(f"⚠️  Agents 目录不存在：{self.agents_dir}")
            return results
        
        # 扫描所有 Agent 目录
        for agent_dir in self.agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            
            agent_name = agent_dir.name
            
            # 跳过特殊目录（但保留 main）
            if agent_name.startswith('.'):
                continue
            
            # 扫描该 Agent 的 sessions
            exp_data = self.scan_agent(agent_name)
            
            if exp_data['sessions'] > 0:
                # 转换为中文名
                cn_name = self._resolve_agent_cn_name(agent_name, self.openclaw_base)
                results[cn_name] = exp_data
                print(f"✅ {cn_name}: {exp_data['sessions']} sessions, {exp_data['tool_calls']} tool calls, {exp_data['exp']} EXP, Lv.{exp_data['level']}")
        
        return results
    
    def scan_agent(self, agent_name: str) -> Dict:
        """
        扫描单个 Agent 的 session 记录
        
        Args:
            agent_name: Agent 目录名（英文）
        
        Returns:
            {'exp': int, 'level': int, 'sessions': int, 'tool_calls': int}
        """
        sessions_dir = self.agents_dir / agent_name / 'sessions'
        
        if not sessions_dir.exists():
            return {'exp': 0, 'level': 1, 'sessions': 0, 'tool_calls': 0}
        
        total_exp = 0
        session_count = 0
        tool_call_count = 0
        
        # 扫描所有 session 文件（包括.deleted 文件，因为日安是主 Agent 需要完整历史）
        for session_file in sessions_dir.glob('*.jsonl*'):
            session_exp, session_tool_calls = self._process_session(session_file)
            total_exp += session_exp
            tool_call_count += session_tool_calls
            session_count += 1
        
        # 计算等级
        level = self._exp_to_level(total_exp)
        
        return {
            'exp': int(total_exp),
            'level': level,
            'sessions': session_count,
            'tool_calls': tool_call_count,
        }
    
    def _process_session(self, session_file: Path) -> Tuple[float, int]:
        """
        处理单个 session 文件
        
        Args:
            session_file: session 文件路径
        
        Returns:
            (exp, tool_call_count)
        """
        exp = 0
        tool_calls = 0
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        record_type = record.get('type', '')
                        
                        # 基础 session 记录
                        if record_type == 'session':
                            exp += self.EXP_RULES['session_base']
                        
                        # 工具调用（独立记录）
                        elif record_type == 'toolCall':
                            tool_calls += 1
                            exp += self.EXP_RULES['tool_call']
                            
                            # 根据工具类型给予不同 EXP
                            tool_name = record.get('name', '')
                            if tool_name == 'write':
                                exp += self.EXP_RULES['write_tool']
                            elif tool_name == 'read':
                                exp += self.EXP_RULES['read_tool']
                            elif tool_name == 'exec':
                                exp += self.EXP_RULES['exec_tool']
                        
                        # assistant 消息（可能包含 toolCall）
                        elif record_type == 'message' and record.get('message', {}).get('role') == 'assistant':
                            exp += self.EXP_RULES['message_assistant']
                            
                            # 解析 content 数组中的 toolCall
                            message = record.get('message', {})
                            content_list = message.get('content', [])
                            
                            if isinstance(content_list, list):
                                for item in content_list:
                                    if isinstance(item, dict) and item.get('type') == 'toolCall':
                                        tool_calls += 1
                                        exp += self.EXP_RULES['tool_call']
                                        
                                        # 根据工具类型给予不同 EXP
                                        tool_name = item.get('name', '')
                                        if tool_name == 'write':
                                            exp += self.EXP_RULES['write_tool']
                                        elif tool_name == 'read':
                                            exp += self.EXP_RULES['read_tool']
                                        elif tool_name == 'exec':
                                            exp += self.EXP_RULES['exec_tool']
                    
                    except json.JSONDecodeError:
                        continue
        
        except Exception as e:
            print(f"⚠️  处理 {session_file} 时出错：{e}")
        
        return exp, tool_calls
    
    def _exp_to_level(self, total_exp: float) -> int:
        """
        根据 EXP 计算等级
        
        公式：level = max(1, int(exp ^ 0.28))
        
        Args:
            total_exp: 累计 EXP
        
        Returns:
            等级（1-100）
        """
        if total_exp <= 0:
            return 1
        
        import math
        level = int(math.pow(total_exp, 0.28))
        
        return max(1, min(level, 100))
    
    def initialize_exp_history(self, agent_name: str, exp_data: Dict):
        """
        初始化 Agent 的 EXP 历史记录
        
        Args:
            agent_name: Agent 中文名称
            exp_data: EXP 数据
        """
        agent_dir = self.facts_base / agent_name
        
        if not agent_dir.exists():
            print(f"⚠️  Agent 目录不存在：{agent_dir}")
            return
        
        exp_file = agent_dir / 'exp_history.jsonl'
        
        # 创建初始化记录
        record = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'action': 'init_from_sessions',
            'exp': exp_data['exp'],
            'details': {
                'source': 'OpenClaw sessions',
                'sessions_count': exp_data['sessions'],
                'tool_calls_count': exp_data['tool_calls'],
                'scan_time': datetime.now().isoformat()
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # 写入 EXP 历史
        with open(exp_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"✅ {agent_name}: EXP 历史已初始化 ({exp_data['exp']} EXP)")


def main():
    """主函数"""
    print("=" * 60)
    print("  Memora v4.0 - Session 扫描初始化")
    print("=" * 60)
    print()
    
    scanner = SessionScanner()
    
    # 扫描所有 Agent
    print("🔍 扫描所有 Agent 的 session 记录...\n")
    results = scanner.scan_all_agents()
    
    print()
    print("=" * 60)
    print(f"  扫描完成！共扫描 {len(results)} 个 Agent")
    print("=" * 60)
    print()
    
    # 初始化 EXP 历史
    print("📝 初始化 EXP 历史记录...\n")
    for agent_name, exp_data in results.items():
        scanner.initialize_exp_history(agent_name, exp_data)
    
    print()
    print("=" * 60)
    print("  初始化完成！")
    print("=" * 60)
    
    # 生成统计报告
    print()
    print("📊 统计报告:")
    print()
    print(f"{'Agent':<10} | {'EXP':<8} | {'等级':<8} | {'Sessions':<10} | {'Tool Calls':<12}")
    print("-" * 60)
    
    # 按 EXP 排序
    sorted_agents = sorted(results.items(), key=lambda x: x[1]['exp'], reverse=True)
    
    for agent_name, exp_data in sorted_agents:
        print(f"{agent_name:<10} | {exp_data['exp']:<8} | Lv.{exp_data['level']:<6} | {exp_data['sessions']:<10} | {exp_data['tool_calls']:<12}")
    
    print()


if __name__ == '__main__':
    main()
