#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anima AIOS v6.2 - Native Memory Importer

从 OpenClaw 原生记忆导入到 Anima 五层记忆架构：
- Phase 1: MEMORY.md → L3 语义记忆
- Phase 2: memory/*.md → L2 情景记忆
- Phase 3: sessions/*.jsonl → L2 + EXP
- Phase 4: content_hash 去重
- Phase 5: 画像重算

Author: 清禾
Date: 2026-03-25
Version: 6.2.0
"""

import json
import os
import sys
import hashlib
import re
import shutil
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime


# ═══════════════════════════════════════════════════════
# 五维映射表（参考 Z 的 TOOL_DIMENSION_MAP + 枢衡 P1-5）
# ═══════════════════════════════════════════════════════
TOOL_DIMENSION_MAP = {
    # understanding（内化）: 学习/吸收行为
    'read': 'understanding',
    'web_fetch': 'understanding',
    'web_search': 'understanding',
    'memory_get': 'understanding',
    'memory_search': 'understanding',
    'memory_write': 'understanding',
    'feishu_fetch_doc': 'understanding',
    'feishu_search_doc_wiki': 'understanding',

    # application（应用）: 执行/运用行为
    'exec': 'application',
    'process': 'application',
    'browser': 'application',
    'feishu_sheet': 'application',
    'feishu_bitable_app_table_record': 'application',
    'feishu_calendar_event': 'application',
    'feishu_task_task': 'application',
    'feishu_im_user_get_messages': 'application',

    # creation（创造）: 创造新内容
    'write': 'creation',
    'edit': 'creation',
    'sessions_spawn': 'creation',
    'feishu_create_doc': 'creation',
    'feishu_update_doc': 'creation',

    # metacognition（元认知）: 自我管理/反思
    'session_status': 'metacognition',
    'sessions_list': 'metacognition',
    'sessions_history': 'metacognition',
    'cron': 'metacognition',

    # collaboration（协作）: 与他人协作
    'message': 'collaboration',
    'sessions_send': 'collaboration',
    'subagents': 'collaboration',
    'feishu_im_user_message': 'collaboration',
    'feishu_chat': 'collaboration',
    'feishu_chat_members': 'collaboration',
}

# 每种工具的 EXP 基础分值
TOOL_EXP_MAP = {
    'write': 2.0,
    'edit': 1.5,
    'read': 0.5,
    'exec': 1.0,
    'process': 0.5,
    'message': 1.0,
    'sessions_spawn': 2.0,
    'web_search': 1.0,
    'web_fetch': 0.5,
    'memory_write': 2.0,
    'memory_search': 1.0,
    'memory_get': 0.5,
    'browser': 1.0,
    'feishu_create_doc': 3.0,
    'feishu_update_doc': 2.0,
    'feishu_fetch_doc': 0.5,
    'cron': 0.5,
    'session_status': 0.3,
    'sessions_list': 0.3,
    'sessions_send': 1.0,
}

# 默认 EXP（未在映射表中的工具）
DEFAULT_TOOL_EXP = 0.5


class NativeMemoryImporter:
    """OpenClaw 原生记忆导入引擎"""

    def __init__(self, agent_name: str, agent_id: Optional[str] = None,
                 facts_base: str = None, dry_run: bool = False):
        """
        Args:
            agent_name: Agent 中文名（如 '清禾'）
            agent_id: Agent 英文 ID（如 'qinghe'），用于定位 workspace
            facts_base: facts 基础路径
            dry_run: 预览模式，不实际写入
        """
        self.agent_name = agent_name
        self.agent_id = agent_id or agent_name
        self.dry_run = dry_run

        if facts_base is None:
            try:
                parent = Path(__file__).parent.parent
                sys.path.insert(0, str(parent / 'config'))
                from path_config import get_config
                facts_base = str(get_config().facts_base)
            except Exception:
                facts_base = '/home/画像'
        self.facts_base = Path(facts_base)
        self.agent_dir = self.facts_base / agent_name

        # 统计
        self.stats = {
            'semantic_imported': 0,
            'episodic_imported': 0,
            'exp_records': 0,
            'total_exp': 0.0,
            'skipped_duplicate': 0,
            'skipped_error': 0,
        }

        # 已有 content hash 集合（去重用）
        self._existing_hashes = set()

        # bookmark 文件路径（增量导入用）
        self.bookmark_file = self.agent_dir / 'import_bookmark.json'

    # ═══════════════════════════════════════════════════════
    # Bookmark（增量导入支持）
    # ═══════════════════════════════════════════════════════

    def _load_bookmark(self) -> Dict:
        """加载上次导入的 bookmark"""
        if self.bookmark_file.exists():
            try:
                with open(self.bookmark_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_bookmark(self, bookmark: Dict):
        """保存 bookmark"""
        if self.dry_run:
            return
        self.bookmark_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.bookmark_file, 'w', encoding='utf-8') as f:
            json.dump(bookmark, f, ensure_ascii=False, indent=2)

    # ═══════════════════════════════════════════════════════
    # 备份（日安建议：导入前自动备份）
    # ═══════════════════════════════════════════════════════

    def _backup_existing_data(self):
        """导入前备份已有 facts 目录"""
        facts_dir = self.agent_dir / 'facts'
        if not facts_dir.exists():
            return

        backup_name = f"facts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir = self.agent_dir / 'backups' / backup_name
        backup_dir.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copytree(facts_dir, backup_dir)
            print(f"  📦 已备份现有 facts → {backup_dir.relative_to(self.agent_dir)}")
        except Exception as e:
            print(f"  ⚠️  备份失败: {e}（继续导入）")

    # ═══════════════════════════════════════════════════════
    # 路径解析
    # ═══════════════════════════════════════════════════════

    def _resolve_workspace(self) -> Optional[Path]:
        """解析 Agent 的 workspace 路径"""
        openclaw_base = Path(os.path.expanduser('~/.openclaw'))

        # 1. workspace-{agentId}
        ws = openclaw_base / f'workspace-{self.agent_id}'
        if ws.exists():
            return ws

        # 2. workspace（main agent）
        ws = openclaw_base / 'workspace'
        if ws.exists():
            return ws

        return None

    def _resolve_sessions_dir(self) -> Optional[Path]:
        """解析 Agent 的 session 目录"""
        openclaw_base = Path(os.path.expanduser('~/.openclaw'))

        # agents/{agentId}/sessions/
        sessions_dir = openclaw_base / 'agents' / self.agent_id / 'sessions'
        if sessions_dir.exists():
            return sessions_dir

        # main agent
        sessions_dir = openclaw_base / 'agents' / 'main' / 'sessions'
        if sessions_dir.exists():
            return sessions_dir

        return None

    # ═══════════════════════════════════════════════════════
    # 去重
    # ═══════════════════════════════════════════════════════

    def _compute_hash(self, content: str) -> str:
        """计算内容 hash（normalize 后再 hash，枢衡 P1-3）"""
        # normalize: 去首尾空白、合并连续空行为单空行
        normalized = re.sub(r'\n{3,}', '\n\n', content.strip())
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def _load_existing_hashes(self):
        """加载已有 facts 的 content hash（提取正文内容，与导入时的 hash 对齐）"""
        for fact_type in ['episodic', 'semantic']:
            type_dir = self.agent_dir / 'facts' / fact_type
            if not type_dir.exists():
                continue
            for f in type_dir.rglob('*'):
                if f.suffix not in ('.json', '.md'):
                    continue
                try:
                    raw = f.read_text(encoding='utf-8')
                    if f.suffix == '.json':
                        # JSON fact: 提取 content 字段
                        try:
                            data = json.loads(raw)
                            content = data.get('content', raw)
                        except json.JSONDecodeError:
                            content = raw
                    else:
                        # MD fact (frontmatter 格式): 提取 --- 之后的正文
                        fm_match = re.match(r'^---\n[\s\S]*?\n---\n([\s\S]*)', raw)
                        if fm_match:
                            content = fm_match.group(1).strip()
                        else:
                            content = raw
                    self._existing_hashes.add(self._compute_hash(content))
                except Exception:
                    pass

    def _is_duplicate(self, content: str) -> bool:
        """检查内容是否已存在"""
        return self._compute_hash(content) in self._existing_hashes

    # ═══════════════════════════════════════════════════════
    # Phase 1: MEMORY.md → L3 语义记忆
    # ═══════════════════════════════════════════════════════

    def import_memory_md(self, workspace: Path) -> List[Dict]:
        """导入 MEMORY.md 为语义记忆"""
        memory_md = workspace / 'MEMORY.md'
        if not memory_md.exists():
            return []

        content = memory_md.read_text(encoding='utf-8')
        if len(content) < 50:
            return []  # 空模板跳过

        # 按 ## 分段（枢衡 P1-4: 超 20 行按 ### 二次分段）
        sections = self._split_by_headings(content)
        facts = []

        for section in sections:
            title = section.get('title', '')
            body = section.get('body', '').strip()
            if not body or len(body) < 20:
                continue

            if self._is_duplicate(body):
                self.stats['skipped_duplicate'] += 1
                continue

            fact = {
                'id': f"import_semantic_{self._compute_hash(body)[:12]}",
                'type': 'semantic',
                'agent': self.agent_name,
                'content': body,
                'summary': (title + ': ' if title else '') + body[:200],
                'tags': ['import-v6.2', 'source:MEMORY.md'],
                'source': 'import-v6.2',
                'createdAt': datetime.now().isoformat(),
            }
            facts.append(fact)
            self._existing_hashes.add(self._compute_hash(body))

        return facts

    def _split_by_headings(self, content: str) -> List[Dict]:
        """按标题分段，超 20 行按子标题二次分段"""
        sections = []
        current_title = ''
        current_lines = []

        for line in content.split('\n'):
            if line.startswith('## ') and not line.startswith('### '):
                # 保存上一段
                if current_lines:
                    body = '\n'.join(current_lines)
                    # 超 20 行按 ### 二次分段
                    if len(current_lines) > 20:
                        sub_sections = self._split_by_sub_headings(
                            current_title, body
                        )
                        sections.extend(sub_sections)
                    else:
                        sections.append({
                            'title': current_title,
                            'body': body,
                        })
                current_title = line.lstrip('#').strip()
                current_lines = []
            else:
                current_lines.append(line)

        # 最后一段
        if current_lines:
            body = '\n'.join(current_lines)
            if len(current_lines) > 20:
                sub_sections = self._split_by_sub_headings(
                    current_title, body
                )
                sections.extend(sub_sections)
            else:
                sections.append({'title': current_title, 'body': body})

        return sections

    def _split_by_sub_headings(self, parent_title: str,
                                content: str) -> List[Dict]:
        """按 ### 子标题二次分段"""
        sections = []
        current_sub = parent_title
        current_lines = []

        for line in content.split('\n'):
            if line.startswith('### '):
                if current_lines:
                    sections.append({
                        'title': current_sub,
                        'body': '\n'.join(current_lines),
                    })
                current_sub = f"{parent_title} > {line.lstrip('#').strip()}"
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines:
            sections.append({
                'title': current_sub,
                'body': '\n'.join(current_lines),
            })

        return sections

    # ═══════════════════════════════════════════════════════
    # Phase 2: memory/*.md → L2 情景记忆
    # ═══════════════════════════════════════════════════════

    def import_daily_memory(self, workspace: Path) -> List[Dict]:
        """导入 memory/*.md 为情景记忆"""
        memory_dir = workspace / 'memory'
        if not memory_dir.exists():
            return []

        facts = []
        for md_file in sorted(memory_dir.glob('*.md')):
            content = md_file.read_text(encoding='utf-8')
            if len(content) < 20:
                continue

            # 从文件名提取日期
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', md_file.name)
            date_str = date_match.group(1) if date_match else ''

            # 按 ## 分段
            sections = self._split_by_headings(content)

            for section in sections:
                body = section.get('body', '').strip()
                if not body or len(body) < 20:
                    continue

                if self._is_duplicate(body):
                    self.stats['skipped_duplicate'] += 1
                    continue

                fact = {
                    'id': f"import_episodic_{self._compute_hash(body)[:12]}",
                    'type': 'episodic',
                    'agent': self.agent_name,
                    'content': body,
                    'summary': body[:200],
                    'tags': [
                        'import-v6.2',
                        f'source:memory/{md_file.name}',
                    ] + ([f'date:{date_str}'] if date_str else []),
                    'source': 'import-v6.2',
                    'createdAt': (
                        f"{date_str}T00:00:00" if date_str
                        else datetime.now().isoformat()
                    ),
                }
                facts.append(fact)
                self._existing_hashes.add(self._compute_hash(body))

        return facts

    # ═══════════════════════════════════════════════════════
    # Phase 3: sessions/*.jsonl → L2 + EXP
    # ═══════════════════════════════════════════════════════

    def import_sessions(self, sessions_dir: Path) -> Tuple[List[Dict], List[Dict]]:
        """
        导入 session 历史

        Returns:
            (episodic_facts, exp_records)
        """
        facts = []
        exp_by_dimension = {
            'understanding': 0.0,
            'application': 0.0,
            'creation': 0.0,
            'metacognition': 0.0,
            'collaboration': 0.0,
        }
        tool_counts = {}
        session_count = 0

        # 加载 bookmark，跳过已扫描的 session
        bookmark = self._load_bookmark()
        scanned_sessions = set(bookmark.get('scanned_sessions', []))

        # 只读 .jsonl，跳过 .reset 文件（枢衡 P0-2）
        new_sessions = []
        for jsonl_file in sorted(sessions_dir.glob('*.jsonl')):
            if '.reset.' in jsonl_file.name:
                continue
            session_id = jsonl_file.stem
            if session_id in scanned_sessions:
                continue
            new_sessions.append(jsonl_file)

        if not new_sessions:
            print(f"  Phase 3: 无新 session（已扫描 {len(scanned_sessions)} 个）")
            return facts, []

        for jsonl_file in new_sessions:
            try:
                session_info = self._parse_session(jsonl_file)
                session_count += 1

                # 累计工具调用的 EXP
                for tool_name, count in session_info['tool_calls'].items():
                    tool_counts[tool_name] = (
                        tool_counts.get(tool_name, 0) + count
                    )
                    dimension = TOOL_DIMENSION_MAP.get(tool_name)
                    if dimension:
                        exp = TOOL_EXP_MAP.get(tool_name, DEFAULT_TOOL_EXP)
                        exp_by_dimension[dimension] += exp * count

            except Exception:
                self.stats['skipped_error'] += 1
                continue

        # 生成 EXP 记录（按维度）
        exp_records = []
        scan_date = datetime.now().strftime('%Y-%m-%d')
        for dimension, total_exp in exp_by_dimension.items():
            if total_exp <= 0:
                continue
            record = {
                'date': scan_date,
                'dimension': dimension,
                'action': 'import_from_sessions',
                'exp': round(total_exp, 2),
                'base_exp': round(total_exp, 2),
                'quality_multiplier': 1.0,
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'source': 'import-v6.2',
                    'session_count': session_count,
                },
            }
            exp_records.append(record)

        # 更新 bookmark
        all_scanned = list(scanned_sessions | {
            f.stem for f in new_sessions
        })
        self._save_bookmark({
            'scanned_sessions': all_scanned,
            'last_import': datetime.now().isoformat(),
            'total_sessions': len(all_scanned),
        })

        return facts, exp_records

    def _parse_session(self, jsonl_path: Path) -> Dict:
        """解析单个 session JSONL 文件"""
        tool_calls = {}
        message_count = 0
        start_time = None
        end_time = None

        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    d = json.loads(line.strip())
                except Exception:
                    continue

                ts = d.get('timestamp')
                if ts:
                    if start_time is None:
                        start_time = ts
                    end_time = ts

                if d.get('type') != 'message':
                    continue

                msg = d.get('message', {})
                role = msg.get('role', '')

                if role == 'user':
                    message_count += 1

                # 统计 toolCall（驼峰，枢衡 P0-1）
                for content_item in msg.get('content', []):
                    if not isinstance(content_item, dict):
                        continue
                    if content_item.get('type') == 'toolCall':
                        name = content_item.get('name', '?')
                        tool_calls[name] = tool_calls.get(name, 0) + 1

                # toolResult 也记录
                if role == 'toolResult':
                    name = msg.get('toolName', '?')
                    # toolResult 不重复计数，toolCall 已经计过了

        return {
            'tool_calls': tool_calls,
            'message_count': message_count,
            'start_time': start_time,
            'end_time': end_time,
        }

    # ═══════════════════════════════════════════════════════
    # 写入
    # ═══════════════════════════════════════════════════════

    def _write_fact(self, fact: Dict) -> bool:
        """写入单条 fact 到文件（.md frontmatter 格式，与 fact_store.py 对齐）"""
        fact_type = fact.get('type', 'episodic')
        target_dir = self.agent_dir / 'facts' / fact_type
        target_dir.mkdir(parents=True, exist_ok=True)

        filepath = target_dir / f"{fact['id']}.md"
        if filepath.exists():
            return False  # 文件已存在，跳过

        # 生成 .md frontmatter 格式（与 fact_store.Fact.to_markdown() 一致）
        tags_str = json.dumps(fact.get('tags', []), ensure_ascii=False)
        lines = [
            "---",
            f"type: {fact_type}",
            f"quality: pending",
            f"source: {fact.get('source', 'import-v6.2')}",
            f"agent: {fact.get('agent', self.agent_name)}",
            f"created_at: {fact.get('createdAt', datetime.now().isoformat())}",
            f"tags: {tags_str}",
            "---",
            "",
            fact.get('content', ''),
        ]

        filepath.write_text('\n'.join(lines), encoding='utf-8')
        return True

    def _append_exp_records(self, records: List[Dict]):
        """追加 EXP 记录到 exp_history.jsonl"""
        self.agent_dir.mkdir(parents=True, exist_ok=True)
        exp_file = self.agent_dir / 'exp_history.jsonl'

        with open(exp_file, 'a', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

    def _regenerate_profile(self):
        """Phase 5: 导入后重算认知画像"""
        print(f"\n🧠 Phase 5: 重算认知画像...")
        try:
            # 尝试导入 cognitive_profile 模块
            try:
                from .cognitive_profile import CognitiveProfileGenerator
            except ImportError:
                try:
                    from cognitive_profile import CognitiveProfileGenerator
                except ImportError:
                    # 从当前文件向上查找（枢衡 P0-2: 不遍历所有 workspace）
                    repo_paths = [Path(__file__).parent]
                    _search = Path(__file__).resolve().parent
                    for _ in range(5):  # 最多向上 5 层
                        _search = _search.parent
                        _candidate = _search / 'anima-aios' / 'core'
                        if (_candidate / 'cognitive_profile.py').exists():
                            repo_paths.append(_candidate)
                            break
                    loaded = False
                    for rp in repo_paths:
                        if (rp / 'cognitive_profile.py').exists():
                            sys.path.insert(0, str(rp))
                            sys.path.insert(0, str(rp.parent / 'config'))
                            from cognitive_profile import CognitiveProfileGenerator
                            loaded = True
                            break
                    if not loaded:
                        print(f"  ⚠️  cognitive_profile 模块不可用，跳过画像重算")
                        return

            generator = CognitiveProfileGenerator(
                self.agent_name, str(self.facts_base)
            )
            profile = generator.generate_profile(auto_save=False)

            # 保存画像
            output_path = generator.save_profile(profile)
            level = profile.get('level', 0)
            score = profile.get('cognitive_score', 0)
            total_exp = profile.get('exp', 0)
            print(f"  ✅ 画像已更新: Lv.{level} | 认知分数: {score} | EXP: {total_exp}")
            print(f"  📄 保存到: {output_path}")

        except Exception as e:
            print(f"  ⚠️  画像重算失败: {e}（不影响导入数据）")

    # ═══════════════════════════════════════════════════════
    # 主流程
    # ═══════════════════════════════════════════════════════

    def run(self, sources: Optional[List[str]] = None) -> Dict:
        """
        执行导入

        Args:
            sources: 导入源列表，默认全部
                     ['memory', 'sessions'] 或子集

        Returns:
            导入统计
        """
        if sources is None:
            sources = ['memory', 'sessions']

        print(f"\n{'='*50}")
        print(f"Anima v6.2 — 原生记忆导入")
        print(f"Agent: {self.agent_name} ({self.agent_id})")
        print(f"模式: {'预览（dry-run）' if self.dry_run else '正式导入'}")
        print(f"{'='*50}\n")

        # 加载已有 hashes
        self._load_existing_hashes()
        print(f"已有 facts hash: {len(self._existing_hashes)} 条")

        all_semantic = []
        all_episodic = []
        all_exp = []

        # Phase 1-2: 记忆导入
        if 'memory' in sources:
            workspace = self._resolve_workspace()
            if workspace:
                print(f"\n📁 Workspace: {workspace}")

                # Phase 1: MEMORY.md
                semantic_facts = self.import_memory_md(workspace)
                all_semantic.extend(semantic_facts)
                print(f"  Phase 1: MEMORY.md → {len(semantic_facts)} 条语义记忆")

                # Phase 2: memory/*.md
                episodic_facts = self.import_daily_memory(workspace)
                all_episodic.extend(episodic_facts)
                print(f"  Phase 2: memory/*.md → {len(episodic_facts)} 条情景记忆")
            else:
                print(f"\n⚠️  未找到 workspace")

        # Phase 3: Session 导入
        if 'sessions' in sources:
            sessions_dir = self._resolve_sessions_dir()
            if sessions_dir:
                print(f"\n📁 Sessions: {sessions_dir}")
                session_jsonl_count = len([
                    f for f in sessions_dir.glob('*.jsonl')
                    if '.reset.' not in f.name
                ])
                print(f"  Session 文件: {session_jsonl_count} 个")

                session_facts, exp_records = self.import_sessions(
                    sessions_dir
                )
                all_episodic.extend(session_facts)
                all_exp.extend(exp_records)

                total_exp = sum(r['exp'] for r in exp_records)
                print(f"  Phase 3: sessions → {len(exp_records)} 条 EXP 记录，总计 {total_exp:.1f} EXP")
                for r in exp_records:
                    print(f"    {r['dimension']:20s}: +{r['exp']:.1f}")
            else:
                print(f"\n⚠️  未找到 sessions 目录")

        # Phase 4: 去重统计
        print(f"\n📊 去重: 跳过 {self.stats['skipped_duplicate']} 条重复")

        # Phase 5: 写入
        if not self.dry_run:
            # 导入前备份（日安建议）
            self._backup_existing_data()

            print(f"\n✏️  写入中...")
            for fact in all_semantic:
                if self._write_fact(fact):
                    self.stats['semantic_imported'] += 1
                else:
                    self.stats['skipped_duplicate'] += 1

            for fact in all_episodic:
                if self._write_fact(fact):
                    self.stats['episodic_imported'] += 1
                else:
                    self.stats['skipped_duplicate'] += 1

            if all_exp:
                self._append_exp_records(all_exp)
                self.stats['exp_records'] = len(all_exp)
                self.stats['total_exp'] = sum(r['exp'] for r in all_exp)

            print(f"  ✅ 写入完成")

            # Phase 5: 画像重算
            self._regenerate_profile()
        else:
            self.stats['semantic_imported'] = len(all_semantic)
            self.stats['episodic_imported'] = len(all_episodic)
            self.stats['exp_records'] = len(all_exp)
            self.stats['total_exp'] = sum(r['exp'] for r in all_exp)
            print(f"\n🔍 预览模式，未实际写入")

        # 打印统计
        print(f"\n{'='*50}")
        print(f"📊 导入统计")
        print(f"{'='*50}")
        print(f"  语义记忆 (L3): {self.stats['semantic_imported']} 条")
        print(f"  情景记忆 (L2): {self.stats['episodic_imported']} 条")
        print(f"  EXP 记录:      {self.stats['exp_records']} 条")
        print(f"  总 EXP:        {self.stats['total_exp']:.1f}")
        print(f"  跳过(重复):    {self.stats['skipped_duplicate']} 条")
        print(f"  跳过(错误):    {self.stats['skipped_error']} 条")
        print()

        return self.stats


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Anima v6.2 — 原生记忆导入'
    )
    parser.add_argument(
        '--agent', required=True,
        help='Agent 中文名（如 清禾）'
    )
    parser.add_argument(
        '--agent-id',
        help='Agent 英文 ID（如 qinghe），默认从 agent_resolver 推断'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='预览模式，不实际写入'
    )
    parser.add_argument(
        '--sources', nargs='+',
        choices=['memory', 'sessions'],
        default=['memory', 'sessions'],
        help='导入源（默认全部）'
    )
    parser.add_argument(
        '--facts-base',
        help='facts 基础路径（默认从 config 读取）'
    )

    args = parser.parse_args()

    importer = NativeMemoryImporter(
        agent_name=args.agent,
        agent_id=args.agent_id,
        facts_base=args.facts_base,
        dry_run=args.dry_run,
    )

    importer.run(sources=args.sources)


if __name__ == '__main__':
    main()
