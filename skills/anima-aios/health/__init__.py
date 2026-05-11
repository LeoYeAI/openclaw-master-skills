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
Anima AIOS v6.0 - Health System

健康系统，包含 5 个子模块：
- manager: 总调度（Doctor 入口）
- hygiene: 数据卫生（完整性 + 去重 + 清理）
- correction: 自动纠错
- evolution: 每日进化（凌晨自动提炼）
- abstraction: 知识抽象

移植自 Z 的 health/ 目录（6 个 JS 文件 → 1 个 Python 模块）。

Author: 清禾
Date: 2026-03-24
Version: 6.0.0
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# core 模块通过相对导入引用（在各方法内按需导入）

logger = logging.getLogger(__name__)


class HealthHygiene:
    """数据卫生检查：完整性 + 去重 + 清理"""

    def __init__(self, agent_name: str, facts_base: str = None):
        self.agent_name = agent_name
        self.base = Path(facts_base) / agent_name

    def check_integrity(self) -> Dict:
        """检查数据完整性"""
        issues = []

        # 检查核心目录
        required_dirs = [
            "facts/episodic", "facts/semantic",
            "palace", "palace/rooms", "pyramid",
            "decay", "health"
        ]
        for d in required_dirs:
            path = self.base / d
            if not path.exists():
                issues.append({"type": "missing_dir", "path": str(path), "severity": "high"})

        # 检查核心文件
        required_files = ["exp_history.jsonl"]
        for f in required_files:
            path = self.base / f
            if not path.exists():
                issues.append({"type": "missing_file", "path": str(path), "severity": "medium"})

        # 检查 facts 格式
        for fact_type in ["episodic", "semantic"]:
            fact_dir = self.base / "facts" / fact_type
            if not fact_dir.exists():
                continue
            for md_file in fact_dir.glob("*.md"):
                content = md_file.read_text(encoding='utf-8')
                if not content.startswith("---"):
                    issues.append({
                        "type": "malformed_fact",
                        "path": str(md_file),
                        "severity": "low",
                        "detail": "缺少 frontmatter"
                    })

        return {
            "status": "healthy" if not issues else "issues_found",
            "issues": issues,
            "checked_at": datetime.now().isoformat()
        }

    def find_duplicates(self) -> List[Dict]:
        """查找重复的 facts"""
        seen_hashes = {}
        duplicates = []

        for fact_type in ["episodic", "semantic"]:
            fact_dir = self.base / "facts" / fact_type
            if not fact_dir.exists():
                continue
            for md_file in fact_dir.glob("*.md"):
                content = md_file.read_text(encoding='utf-8')
                # 取正文部分的哈希
                parts = content.split("---", 2)
                body = parts[2].strip() if len(parts) >= 3 else content.strip()
                import hashlib
                h = hashlib.md5(body.encode()).hexdigest()
                if h in seen_hashes:
                    duplicates.append({
                        "file": str(md_file),
                        "duplicate_of": seen_hashes[h],
                        "hash": h
                    })
                else:
                    seen_hashes[h] = str(md_file)

        return duplicates

    def cleanup_empty(self) -> int:
        """清理空文件"""
        removed = 0
        for fact_type in ["episodic", "semantic"]:
            fact_dir = self.base / "facts" / fact_type
            if not fact_dir.exists():
                continue
            for md_file in fact_dir.glob("*.md"):
                if md_file.stat().st_size == 0:
                    md_file.unlink()
                    removed += 1
        return removed


class HealthCorrection:
    """自动纠错：检测并修复常见数据问题"""

    def __init__(self, agent_name: str, facts_base: str = None):
        self.agent_name = agent_name
        self.base = Path(facts_base) / agent_name

    def fix_missing_dirs(self) -> int:
        """创建缺失的目录"""
        fixed = 0
        required = [
            "facts/episodic", "facts/semantic",
            "palace", "palace/rooms", "pyramid",
            "decay", "health"
        ]
        for d in required:
            path = self.base / d
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                fixed += 1
        return fixed

    def fix_exp_history(self) -> bool:
        """修复损坏的 exp_history.jsonl"""
        exp_file = self.base / "exp_history.jsonl"
        if not exp_file.exists():
            exp_file.touch()
            return True

        # 验证每行是合法 JSON
        lines = exp_file.read_text(encoding='utf-8').splitlines()
        valid_lines = []
        fixed = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
                valid_lines.append(line)
            except json.JSONDecodeError:
                fixed = True  # 跳过损坏行

        if fixed:
            exp_file.write_text('\n'.join(valid_lines) + '\n', encoding='utf-8')

        return fixed

    def run_all_fixes(self) -> Dict:
        """执行所有自动修复"""
        return {
            "dirs_fixed": self.fix_missing_dirs(),
            "exp_fixed": self.fix_exp_history(),
            "timestamp": datetime.now().isoformat()
        }


class HealthEvolution:
    """每日进化：自动提炼高价值记忆"""

    def __init__(self, agent_name: str, facts_base: str = None):
        self.agent_name = agent_name
        if facts_base is None:
            try:
                from ..config.path_config import get_config
            except ImportError:
                from config.path_config import get_config
            facts_base = str(get_config().facts_base)
        self.facts_base = facts_base
        self.log_file = Path(facts_base) / agent_name / "health" / "evolution-log.jsonl"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def run_daily(self) -> Dict:
        """
        执行每日进化（设计为凌晨 3:00 由 cron 触发）

        流程：
        1. 运行提炼引擎（L2→L3）
        2. 运行宫殿分类
        3. 运行金字塔提炼
        4. 记录日志
        """
        stats = {"timestamp": datetime.now().isoformat(), "steps": {}}

        # Step 1: L2→L3 提炼
        try:
            try:
                from ..core.distill_engine import DistillEngine
            except ImportError:
                from distill_engine import DistillEngine
            engine = DistillEngine(self.agent_name, self.facts_base)
            distill_result = engine.run(batch_size=50)
            stats["steps"]["distill"] = distill_result
        except Exception as e:
            stats["steps"]["distill"] = {"error": str(e)}

        # Step 2: 宫殿分类
        try:
            try:
                from ..core.palace_classifier import PalaceClassifier
            except ImportError:
                from palace_classifier import PalaceClassifier
            classifier = PalaceClassifier(self.agent_name, self.facts_base)
            unclassified = classifier.get_unclassified()
            if unclassified:
                classify_result = classifier.classify_batch(unclassified)
                stats["steps"]["classify"] = classify_result
            else:
                stats["steps"]["classify"] = {"message": "无待分类知识"}
        except Exception as e:
            stats["steps"]["classify"] = {"error": str(e)}

        # Step 3: 金字塔自动提炼
        try:
            try:
                from ..core.pyramid_engine import PyramidEngine
            except ImportError:
                from pyramid_engine import PyramidEngine
            pyramid = PyramidEngine(self.agent_name, self.facts_base, auto_distill=True)
            topics = pyramid.get_topics()
            distilled_topics = 0
            for topic, level_counts in topics.items():
                if level_counts.get("instances", 0) >= 3 and level_counts.get("rules", 0) == 0:
                    pyramid.distill_up(topic, "instances")
                    distilled_topics += 1
            stats["steps"]["pyramid"] = {"topics_distilled": distilled_topics}
        except Exception as e:
            stats["steps"]["pyramid"] = {"error": str(e)}

        # 记录日志
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(stats, ensure_ascii=False) + '\n')

        return stats


class HealthAbstraction:
    """知识抽象：举一反三，从已有知识中发现新关联"""

    def __init__(self, agent_name: str, facts_base: str = None,
                 llm_config: Dict = None):
        self.agent_name = agent_name
        if facts_base is None:
            try:
                from ..config.path_config import get_config
            except ImportError:
                from config.path_config import get_config
            facts_base = str(get_config().facts_base)
        self.facts_base = facts_base
        self.llm = None
        if llm_config:
            try:
                try:
                    from ..core.distill_engine import LLMClient
                except ImportError:
                    from distill_engine import LLMClient
                self.llm = LLMClient(llm_config)
            except ImportError:
                pass

    def find_connections(self, limit: int = 5) -> List[Dict]:
        """
        发现跨房间的知识关联
        """
        try:
            try:
                from ..core.palace_index import PalaceIndex
            except ImportError:
                from palace_index import PalaceIndex
            palace = PalaceIndex(self.agent_name, self.facts_base)
        except ImportError:
            return []

        rooms = palace.list_rooms()
        all_items = []
        for room in rooms:
            if room["id"] == "_inbox":
                continue
            items = palace.get_room_items(room["id"])
            for item in items:
                item["room_id"] = room["id"]
                item["room_name"] = room["name"]
                all_items.append(item)

        if len(all_items) < 2:
            return []

        connections = []
        # 简单关联：不同房间中有相同标签的知识
        from collections import defaultdict
        tag_map = defaultdict(list)
        for item in all_items:
            for tag in item.get("tags", []):
                tag_map[tag].append(item)

        for tag, items in tag_map.items():
            rooms_involved = set(i["room_id"] for i in items)
            if len(rooms_involved) >= 2:
                connections.append({
                    "type": "shared_tag",
                    "tag": tag,
                    "rooms": list(rooms_involved),
                    "items": [i["fact_id"] for i in items]
                })

        return connections[:limit]


class HealthManager:
    """
    健康系统总调度器

    整合 5 个子模块，提供统一的诊断和修复接口。
    Doctor 命令的后端。
    """

    def __init__(self, agent_name: str, facts_base: str = None,
                 llm_config: Dict = None):
        self.agent_name = agent_name
        if facts_base is None:
            try:
                from ..config.path_config import get_config
            except ImportError:
                from config.path_config import get_config
            facts_base = str(get_config().facts_base)
        self.facts_base = facts_base
        self.hygiene = HealthHygiene(agent_name, facts_base)
        self.correction = HealthCorrection(agent_name, facts_base)
        self.evolution = HealthEvolution(agent_name, facts_base)
        self.abstraction = HealthAbstraction(agent_name, facts_base, llm_config)

    def full_checkup(self) -> Dict:
        """完整健康检查"""
        report = {
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "modules": {}
        }

        # 1. 完整性检查
        report["modules"]["integrity"] = self.hygiene.check_integrity()

        # 2. 重复检查
        dups = self.hygiene.find_duplicates()
        report["modules"]["duplicates"] = {
            "count": len(dups),
            "items": dups[:10]
        }

        # 3. 衰减状态
        try:
            try:
                from ..core.decay_function import DecayManager
            except ImportError:
                from decay_function import DecayManager
            try:
                from ..core.fact_store import FactStore
            except ImportError:
                from fact_store import FactStore
            store = FactStore(self.agent_name, self.facts_base)
            decay = DecayManager(self.agent_name, self.facts_base)

            all_facts = []
            for ft in ["episodic", "semantic"]:
                for f in store.list_facts(ft, limit=100):
                    all_facts.append({"fact_id": f.fact_id, "quality": f.quality, "content": f.content})

            decay_stats = decay.scan_all(all_facts)
            report["modules"]["decay"] = {
                "total": decay_stats["total"],
                "healthy": len(decay_stats["healthy"]),
                "weakening": len(decay_stats["weakening"]),
                "needs_review": len(decay_stats["needs_review"]),
                "forgetting": len(decay_stats["forgetting"]),
                "archivable": len(decay_stats["archivable"])
            }
        except Exception as e:
            report["modules"]["decay"] = {"error": str(e)}

        # 4. 宫殿状态
        try:
            try:
                from ..core.palace_index import PalaceIndex
            except ImportError:
                from palace_index import PalaceIndex
            palace = PalaceIndex(self.agent_name, self.facts_base)
            report["modules"]["palace"] = palace.get_stats()
        except Exception as e:
            report["modules"]["palace"] = {"error": str(e)}

        # 5. 金字塔状态
        try:
            try:
                from ..core.pyramid_engine import PyramidEngine
            except ImportError:
                from pyramid_engine import PyramidEngine
            pyramid = PyramidEngine(self.agent_name, self.facts_base)
            report["modules"]["pyramid"] = pyramid.get_stats()
        except Exception as e:
            report["modules"]["pyramid"] = {"error": str(e)}

        # 6. 知识关联
        connections = self.abstraction.find_connections()
        report["modules"]["connections"] = {
            "count": len(connections),
            "items": connections
        }

        # 总���
        issues = report["modules"]["integrity"].get("issues", [])
        high_issues = [i for i in issues if i.get("severity") == "high"]
        report["overall"] = "healthy" if not high_issues else "needs_attention"

        return report

    def auto_fix(self) -> Dict:
        """执行自动修复"""
        return {
            "corrections": self.correction.run_all_fixes(),
            "empty_cleaned": self.hygiene.cleanup_empty(),
            "timestamp": datetime.now().isoformat()
        }

    def run_evolution(self) -> Dict:
        """触发每日进化"""
        return self.evolution.run_daily()


def main():
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [Health] %(levelname)s: %(message)s'
    )

    parser = argparse.ArgumentParser(description='Anima Health System')
    parser.add_argument('--agent', type=str, default='')
    parser.add_argument('--facts-base', type=str, default='/home/画像')
    parser.add_argument('action', choices=['checkup', 'fix', 'evolve'], help='操作')
    args = parser.parse_args()

    agent = args.agent or os.getenv("ANIMA_AGENT_NAME", "unknown")
    mgr = HealthManager(agent, args.facts_base)

    if args.action == 'checkup':
        report = mgr.full_checkup()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.action == 'fix':
        result = mgr.auto_fix()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.action == 'evolve':
        result = mgr.run_evolution()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
