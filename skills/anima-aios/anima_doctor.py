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
Anima Doctor - Anima-AIOS 自检自修工具

用法:
    anima doctor              # 自检
    anima doctor --fix        # 自修
    anima doctor --fix --yes  # 自动修复（无需确认）

修复记录:
- v5.0.3 (2026-03-22): 修复 Agent 名称检测
  - 优先级：环境变量 > OpenClaw 上下文 > 自动扫描 > 默认值
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# 项目路径（v5.0.5 修复：自动检测 workspace）
ANIMA_HOME = Path(os.path.expanduser("~/.anima"))
FACTS_BASE = Path(os.getenv("ANIMA_FACTS_BASE", os.path.expanduser("~/.anima/data")))

# 工作空间名称 → Agent 名称映射（可自定义，默认为空，优先通过 SOUL.md 检测）
WORKSPACE_AGENT_MAP = {}

def _map_workspace_to_agent(workspace_name: str) -> str:
    """
    将工作空间名称映射到 Agent 中文名称
    
    Args:
        workspace_name: 工作空间名称（如 shuheng）
    
    Returns:
        Agent 名称
    """
    return WORKSPACE_AGENT_MAP.get(workspace_name, workspace_name)

def _parse_soul_file(file_path: Path) -> Optional[str]:
    """
    从 SOUL.md 解析 Agent 名称
    
    示例格式:
    ```markdown
    # SOUL.md - MyAgent 的灵魂
    
    ## ⚖️ 我是谁
    **姓名：** MyAgent
    ```
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # 匹配模式 1: # SOUL.md - MyAgent 的灵魂
        match = re.search(r'#\s*SOUL\.md\s*-\s*(.+) 的', content)
        if match:
            return match.group(1).strip()
        
        # 匹配模式 2: **姓名：** {Agent名}
        match = re.search(r'\*\*姓名：\*\*\s*([^(]+)', content)
        if match:
            name = match.group(1).strip()
            name = re.sub(r'\s*\(.*\)', '', name)
            return name
    except Exception:
        pass
    
    return None

def _parse_identity_file(file_path: Path) -> Optional[str]:
    """
    从 IDENTITY.md 解析 Agent 名称
    
    示例格式:
    ```markdown
    # IDENTITY.md - Who Am I?
    
    - **Name:** MyAgent
    - **Creature:** AI 系统架构师
    ```
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # 匹配模式：- **Name:** MyAgent
        match = re.search(r'\*\*Name:\*\*\s*([^(]+)', content)
        if match:
            name = match.group(1).strip()
            # 清理括号和空格
            name = re.sub(r'\s*\(.*\)', '', name)
            return name
    except Exception:
        pass
    
    return None

def _detect_workspace():
    """
    自动检测当前 workspace 路径（v5.0.5 修复版）
    
    优先级：
    1. ANIMA_WORKSPACE 环境变量
    2. 当前工作目录推断
    3. 默认路径（兼容旧版）
    """
    # 方式 1: 从 ANIMA_WORKSPACE 环境变量获取
    workspace = os.getenv("ANIMA_WORKSPACE")
    if workspace and Path(workspace).exists():
        return Path(workspace)
    
    # 方式 2: 从当前工作目录推断
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if parent.name.startswith("workspace-") and ".openclaw" in str(parent):
            return parent
    
    # 方式 3: 默认路径（兼容旧版，仅作为最后降级）
    default = Path(os.path.expanduser("~/.openclaw/workspace"))
    if default.exists():
        return default
    
    # 方式 4: 返回当前目录
    return cwd

WORKSPACE = _detect_workspace()
SKILL_DIR = Path(__file__).parent  # 自动检测，不硬编码
CORE_DIR = ANIMA_HOME / "core"  # Core 是全局共享的


def _get_current_agent() -> str:
    """
    获取当前 Agent 名称（优先使用 agent_resolver 公共模块）
    """
    try:
        sys.path.insert(0, str(SKILL_DIR / "core"))
        from agent_resolver import resolve_agent_name
        return resolve_agent_name()
    except ImportError:
        pass

    import os
    import re
    
    # 1. 环境变量（手动覆盖，最高优先级）
    agent_name = os.getenv("ANIMA_AGENT_NAME")
    if agent_name:
        return agent_name
    
    # 2. ANIMA_WORKSPACE（OpenClaw 注入）
    workspace = os.getenv("ANIMA_WORKSPACE") or os.getenv("WORKSPACE")
    if workspace:
        workspace_path = Path(workspace)
        workspace_name = workspace_path.name
        # 处理 workspace-{name} 格式
        if workspace_name.startswith("workspace-"):
            workspace_name = workspace_name.replace("workspace-", "")
        return _map_workspace_to_agent(workspace_name)
    
    # 3. 解析 SOUL.md（OpenClaw 身份 ⭐）
    if WORKSPACE.exists():
        soul_file = WORKSPACE / "SOUL.md"
        if soul_file.exists():
            agent_name = _parse_soul_file(soul_file)
            if agent_name:
                return agent_name
        
        # 4. 解析 IDENTITY.md（OpenClaw 身份 ⭐）
        identity_file = WORKSPACE / "IDENTITY.md"
        if identity_file.exists():
            agent_name = _parse_identity_file(identity_file)
            if agent_name:
                return agent_name
    
    # 5. 工作目录路径解析（自动检测）
    cwd = Path.cwd()
    if ".openclaw" in str(cwd):
        for part in cwd.parts:
            if part.startswith("workspace-"):
                workspace_name = part.replace("workspace-", "")
                return _map_workspace_to_agent(workspace_name)
    
    # 6. 降级：自动扫描 /home/画像/
    if FACTS_BASE.exists():
        for agent_dir in FACTS_BASE.iterdir():
            if agent_dir.is_dir():
                exp_file = agent_dir / "exp_history.jsonl"
                if exp_file.exists():
                    return agent_dir.name
    
    # 7. 默认值
    return "Agent"


class AnimaDoctor:
    """Anima 自检自修工具"""
    
    def __init__(self):
        """初始化医生"""
        self.checks = {}
        self.fixes = []
    
    def diagnose(self, auto_fix=False, auto_confirm=False):
        """
        自检 Anima 状态
        
        Args:
            auto_fix: 是否自动修复
            auto_confirm: 是否自动确认修复
        """
        print("=" * 60)
        print("  🏥 Anima-AIOS 自检工具")
        print("=" * 60)
        print(f"  时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
        
        # 执行检查
        self._check_skill_installed()
        self._check_core_installed()
        self._check_config()
        self._check_data_integrity()
        self._check_dependencies()
        self._check_permissions()
        
        # 打印结果
        self._print_results()
        
        # 发现问题时提示修复
        has_issues = any(check['status'] != 'ok' for check in self.checks.values())
        
        if has_issues:
            print("\n⚠️  检测到问题，建议修复")
            
            if auto_fix:
                if auto_confirm or self._user_confirm("执行修复？"):
                    self.recover()
            else:
                print("\n💡 提示：运行以下命令修复")
                print("   anima doctor --fix")
        
        return has_issues
    
    def _check_skill_installed(self):
        """检查 skill 是否安装"""
        skill_files = [
            SKILL_DIR / "SKILL.md",
            SKILL_DIR / "_meta.json",
            SKILL_DIR / "anima_tools.py",
        ]
        
        missing = [f for f in skill_files if not f.exists()]
        
        if missing:
            self.checks['skill_installed'] = {
                'status': 'error',
                'message': f'Skill 未安装，缺失文件：{len(missing)} 个',
                'fix': '运行 clawhub install anima 或手动安装'
            }
        else:
            self.checks['skill_installed'] = {
                'status': 'ok',
                'message': 'Skill 已安装'
            }
    
    def _check_core_installed(self):
        """检查 core 是否安装"""
        core_files = [
            ANIMA_HOME / "core" / "exp_tracker.py",
            ANIMA_HOME / "core" / "cognitive_profile.py",
            ANIMA_HOME / "core" / "dimension_calculator.py",
        ]
        
        missing = [f for f in core_files if not f.exists()]
        
        if missing:
            self.checks['core_installed'] = {
                'status': 'warning',
                'message': f'Core 未完全安装，缺失文件：{len(missing)} 个',
                'fix': '运行 post-install.sh 或重新安装'
            }
        else:
            self.checks['core_installed'] = {
                'status': 'ok',
                'message': 'Core 已安装'
            }
    
    def _check_config(self):
        """检查配置文件"""
        config_file = ANIMA_HOME / "anima_config.json"
        
        if not config_file.exists():
            self.checks['config'] = {
                'status': 'warning',
                'message': '配置文件不存在',
                'fix': '创建默认配置文件'
            }
        else:
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # 检查必要配置
                required_keys = ['exp', 'quest', 'profile']
                missing_keys = [k for k in required_keys if k not in config]
                
                if missing_keys:
                    self.checks['config'] = {
                        'status': 'warning',
                        'message': f'配置不完整，缺失：{missing_keys}',
                        'fix': '补充配置项'
                    }
                else:
                    self.checks['config'] = {
                        'status': 'ok',
                        'message': '配置正确'
                    }
            except json.JSONDecodeError:
                self.checks['config'] = {
                    'status': 'error',
                    'message': '配置文件格式错误',
                    'fix': '修复或重建配置文件'
                }
    
    def _check_data_integrity(self):
        """检查数据完整性（v5.0.3 修复：支持多 Agent）"""
        # 获取当前 Agent 名称
        agent_name = _get_current_agent()
        
        # 检查两个位置的 EXP 历史
        exp_files = [
            ANIMA_HOME / agent_name / "exp_history.jsonl",  # 新位置（按 Agent 分开）
            FACTS_BASE / agent_name / "exp_history.jsonl",  # 旧位置
            ANIMA_HOME / "exp_history.jsonl",  # 通用位置（降级）
        ]
        
        found_exp = False
        total_records = 0
        
        for exp_file in exp_files:
            if exp_file.exists():
                try:
                    with open(exp_file, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    total_records += len(lines)
                    found_exp = True
                except Exception:
                    pass
        
        if found_exp:
            self.checks['data_integrity'] = {
                'status': 'ok',
                'message': f'数据完整 ({total_records} 条记录，Agent: {agent_name})'
            }
        else:
            self.checks['data_integrity'] = {
                'status': 'warning',
                'message': f'EXP 历史文件不存在（首次使用正常，Agent: {agent_name}）',
                'fix': '开始使用后自动生成'
            }
    
    def _check_dependencies(self):
        """检查依赖"""
        missing_deps = []
        
        # 检查 Python 包
        try:
            import watchdog
        except ImportError:
            missing_deps.append('watchdog')
        
        try:
            import requests
        except ImportError:
            missing_deps.append('requests')
        
        if missing_deps:
            self.checks['dependencies'] = {
                'status': 'error',
                'message': f'缺少依赖：{", ".join(missing_deps)}',
                'fix': f'pip install {" ".join(missing_deps)}'
            }
        else:
            self.checks['dependencies'] = {
                'status': 'ok',
                'message': '依赖齐全'
            }
    
    def _check_permissions(self):
        """检查权限（v5.0.3 修复：增加 Agent 目录检查）"""
        # 获取当前 Agent 名称
        agent_name = _get_current_agent()
        
        # 检查关键目录权限
        dirs_to_check = [
            ANIMA_HOME,
            WORKSPACE / "memory",
            FACTS_BASE / agent_name,  # Agent 专属目录
        ]
        
        permission_issues = []
        for dir_path in dirs_to_check:
            if dir_path.exists():
                if not os.access(dir_path, os.W_OK):
                    permission_issues.append(str(dir_path))
        
        if permission_issues:
            self.checks['permissions'] = {
                'status': 'error',
                'message': f'无写入权限：{len(permission_issues)} 个目录',
                'fix': 'chmod -R 755 ' + ' '.join(permission_issues)
            }
        else:
            self.checks['permissions'] = {
                'status': 'ok',
                'message': f'权限正常 (Agent: {agent_name})'
            }
    
    def _print_results(self):
        """打印检查结果（v5.0.3 修复：显示当前 Agent）"""
        agent_name = _get_current_agent()
        
        print("诊断结果:")
        print("-" * 60)
        print(f"当前 Agent: {agent_name}")
        print("-" * 60)
        
        for check_name, check_result in self.checks.items():
            status_icon = {
                'ok': '✅',
                'warning': '⚠️',
                'error': '❌'
            }.get(check_result['status'], '❓')
            
            print(f"{status_icon} {check_name}: {check_result['message']}")
        
        print("-" * 60)
        
        ok_count = sum(1 for c in self.checks.values() if c['status'] == 'ok')
        warning_count = sum(1 for c in self.checks.values() if c['status'] == 'warning')
        error_count = sum(1 for c in self.checks.values() if c['status'] == 'error')
        
        print(f"总计：{ok_count} 正常，{warning_count} 警告，{error_count} 错误")
    
    def _user_confirm(self, message):
        """用户确认"""
        response = input(f"{message} (y/N): ")
        return response.lower() in ['y', 'yes']
    
    def recover(self):
        """自修 Anima 问题"""
        print("\n开始自动修复...")
        print("-" * 60)
        
        fixes = []
        
        # 1. 修复配置文件
        if self.checks.get('config', {}).get('status') != 'ok':
            if self._fix_config():
                fixes.append('config_fixed')
        
        # 2. 修复依赖
        if self.checks.get('dependencies', {}).get('status') != 'ok':
            if self._fix_dependencies():
                fixes.append('dependencies_fixed')
        
        # 3. 修复权限
        if self.checks.get('permissions', {}).get('status') != 'ok':
            if self._fix_permissions():
                fixes.append('permissions_fixed')
        
        # 4. 重新安装 core
        if self.checks.get('core_installed', {}).get('status') == 'error':
            if self._reinstall_core():
                fixes.append('core_reinstalled')
        
        # 5. 全员生成 cognitive_profile（v6.1 新增）
        if self._generate_all_profiles():
            fixes.append('profiles_generated')
        
        # 打印修复结果
        print("-" * 60)
        if fixes:
            print("修复结果:")
            for fix in fixes:
                print(f"✅ {fix}")
            print("-" * 60)
            print("✅ 修复完成！建议重新运行 anima doctor 验证")
        else:
            print("⚠️  部分问题需要手动修复，请查看上方提示")
        
        return fixes
    
    def _fix_config(self):
        """修复配置文件"""
        try:
            config_file = ANIMA_HOME / "anima_config.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            default_config = {
                "exp": {
                    "enabled": True,
                    "dailyLimit": 100
                },
                "quest": {
                    "enabled": True,
                    "autoRefresh": True
                },
                "profile": {
                    "autoUpdate": True,
                    "updateInterval": 3600
                },
                "data": {
                    "backupEnabled": True,
                    "backupTime": "03:00"
                }
            }
            
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            
            print("✅ 配置文件已创建")
            return True
        except Exception as e:
            print(f"❌ 创建配置文件失败：{e}")
            return False
    
    def _fix_dependencies(self):
        """修复依赖"""
        print("⚠️  请手动安装缺失依赖：")
        print("   pip install inotify requests")
        return False
    
    def _fix_permissions(self):
        """修复权限"""
        print("⚠️  请手动修复权限：")
        print(f"   chmod -R 755 {ANIMA_HOME}")
        print(f"   chmod -R 755 {WORKSPACE / 'memory'}")
        return False
    
    def _reinstall_core(self):
        """重新安装 core"""
        print("⚠️  请手动重新安装 Core：")
        print(f"   cd {SKILL_DIR}")
        print(f"   bash post-install.sh")
        return False
    
    def _generate_all_profiles(self):
        """全员生成 cognitive_profile（v6.1 新增，解决 BUG-001）"""
        try:
            sys.path.insert(0, str(SKILL_DIR / "core"))
            from cognitive_profile import CognitiveProfileGenerator
            
            generated = 0
            for agent_dir in FACTS_BASE.iterdir():
                if not agent_dir.is_dir():
                    continue
                if agent_dir.name.startswith('.') or agent_dir.name == 'shared':
                    continue
                
                try:
                    generator = CognitiveProfileGenerator(agent_dir.name, facts_base=str(FACTS_BASE))
                    generator.generate_profile(auto_scan=False, auto_save=True)
                    generated += 1
                except Exception:
                    pass
            
            if generated > 0:
                print(f"✅ 已为 {generated} 个 Agent 生成/更新认知画像")
                return True
        except Exception as e:
            print(f"⚠️  画像生成失败: {e}")
        return False
    
    def check_sync_status(self):
        """检查记忆同步状态（v5.0.4 新增）"""
        print("=" * 60)
        print("  📊 Anima 记忆同步状态检查")
        print("=" * 60)
        
        agent_name = _get_current_agent()
        print(f"当前 Agent: {agent_name}")
        print("-" * 60)
        
        # 检查 OpenClaw Memory
        openclaw_memory = WORKSPACE / "memory"
        openclaw_files = list(openclaw_memory.glob("*.md")) if openclaw_memory.exists() else []
        
        # 检查 Anima Facts
        anima_facts = FACTS_BASE / agent_name / "facts"
        episodic_facts = list(anima_facts.glob("episodic/*.md")) if anima_facts.exists() else []
        semantic_facts = list(anima_facts.glob("semantic/*.md")) if anima_facts.exists() else []
        
        print(f"OpenClaw Memory 文件数：{len(openclaw_files)}")
        print(f"Anima Facts 文件数：{len(episodic_facts) + len(semantic_facts)}")
        print(f"  - Episodic: {len(episodic_facts)}")
        print(f"  - Semantic: {len(semantic_facts)}")
        print("-" * 60)
        
        # 计算同步率
        if len(openclaw_files) > 0:
            sync_rate = (len(episodic_facts) + len(semantic_facts)) / len(openclaw_files) * 100
            print(f"同步率：{sync_rate:.1f}%")
            
            if sync_rate >= 100:
                print("✅ 记忆已完全同步")
            elif sync_rate >= 50:
                print("⚠️  记忆部分同步，建议执行同步")
            else:
                print("❌ 记忆同步率低，建议执行同步")
                print("\n💡 运行以下命令同步:")
                print("   anima doctor --sync-memory")
        else:
            print("ℹ️  暂无 OpenClaw Memory 记录")
        
        print("=" * 60)
    
    def sync_memory_to_facts(self):
        """同步历史记忆到 Anima Facts（v5.0.4 新增）"""
        print("=" * 60)
        print("  🔄 Anima 记忆同步工具")
        print("=" * 60)
        
        agent_name = _get_current_agent()
        print(f"当前 Agent: {agent_name}")
        print("-" * 60)
        
        # 获取 OpenClaw Memory 文件
        openclaw_memory = WORKSPACE / "memory"
        if not openclaw_memory.exists():
            print("❌ OpenClaw Memory 目录不存在")
            return
        
        memory_files = sorted(openclaw_memory.glob("*.md"))
        if not memory_files:
            print("ℹ️  暂无记忆文件需要同步")
            return
        
        print(f"找到 {len(memory_files)} 个记忆文件")
        print("-" * 60)
        
        # 确保 Facts 目录存在
        facts_dir = FACTS_BASE / agent_name / "facts"
        facts_dir.mkdir(parents=True, exist_ok=True)
        (facts_dir / "episodic").mkdir(exist_ok=True)
        (facts_dir / "semantic").mkdir(exist_ok=True)
        
        # 同步计数器
        synced_count = 0
        skipped_count = 0
        error_count = 0
        
        # 遍历记忆文件
        for memory_file in memory_files:
            try:
                content = memory_file.read_text(encoding="utf-8")
                date = memory_file.stem  # YYYY-MM-DD
                
                # 解析记忆内容（简单实现：按行解析）
                lines = content.split("\n")
                file_synced = 0
                
                for line in lines:
                    # 跳过空行和标题行
                    if not line.strip() or line.strip().startswith("#"):
                        continue
                    
                    # 提取时间戳和内容（支持多种格式）
                    import re
                    # 格式 1: - [08:55] 内容 #episodic
                    match = re.search(r'-\s*\[(\d{2}:\d{2})\]\s*(.+?)\s*#(\w+)', line)
                    if not match:
                        # 格式 2: [08:55] 内容 #episodic
                        match = re.search(r'\[(\d{2}:\d{2})\]\s*(.+?)\s*#(\w+)', line)
                    
                    if match:
                        time = match.group(1)
                        memory_content = match.group(2).strip()
                        memory_type = match.group(3).strip()
                        
                        # 创建 Fact 文件
                        fact_id = f"{memory_type}_{date.replace('-', '')}_{time.replace(':', '')}_{synced_count:04d}"
                        fact_file = facts_dir / memory_type / f"{fact_id}.md"
                        
                        if fact_file.exists():
                            skipped_count += 1
                            continue
                        
                        # 写入 Fact 文件
                        fact_content = f"""# {memory_type.capitalize()} Fact

**ID:** {fact_id}
**日期:** {date} {time}
**作者:** {agent_name}
**类型:** {memory_type}

---

## 内容

{memory_content}

---

## 标签

自动同步自 OpenClaw Memory

---

## 元数据

- 创建时间：{datetime.now().isoformat()}
- 内容长度：{len(memory_content)} 字符
- 来源：OpenClaw Memory ({memory_file.name})

"""
                        fact_file.write_text(fact_content, encoding="utf-8")
                        file_synced += 1
                        synced_count += 1
                
                if file_synced > 0:
                    print(f"✅ {memory_file.name}: 同步 {file_synced} 条记忆")
                
            except Exception as e:
                error_count += 1
                print(f"❌ {memory_file.name}: 同步失败 - {e}")
        
        # 打印总结
        print("-" * 60)
        print("同步完成:")
        print(f"  ✅ 成功：{synced_count} 条")
        print(f"  ⚠️  跳过：{skipped_count} 条（已存在）")
        print(f"  ❌ 失败：{error_count} 条")
        print("=" * 60)
        
        if synced_count > 0:
            print("💡 建议运行 'anima doctor' 验证同步结果")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Anima-AIOS 自检自修工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  anima doctor                    # 自检
  anima doctor --fix              # 自修（交互确认）
  anima doctor --fix --yes        # 自修（无需确认，适合非交互环境）
  anima doctor --sync-memory      # 同步历史记忆到 Anima Facts
  anima doctor --check-sync       # 检查同步状态
        '''
    )
    parser.add_argument('--fix', action='store_true', help='自检并修复')
    parser.add_argument('--yes', '-y', action='store_true', help='自动确认修复')
    parser.add_argument('--auto', '-a', action='store_true', help='自动模式（无需确认）')
    parser.add_argument('--sync-memory', action='store_true', help='同步历史记忆到 Anima Facts（v5.0.4 新增）')
    parser.add_argument('--check-sync', action='store_true', help='检查记忆同步状态（v5.0.4 新增）')
    
    args = parser.parse_args()
    
    doctor = AnimaDoctor()
    
    if args.sync_memory:
        doctor.sync_memory_to_facts()
    elif args.check_sync:
        doctor.check_sync_status()
    elif args.fix:
        doctor.diagnose(auto_fix=True, auto_confirm=args.auto or args.yes)
    else:
        doctor.diagnose()


if __name__ == "__main__":
    main()
