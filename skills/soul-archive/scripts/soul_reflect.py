#!/usr/bin/env python3
"""
🧬 Soul Archive — AI Self-Improvement Engine (soul_reflect.py)

AI 自我反思、自我批评、自我学习引擎。
记录 AI 的工作经验、错误教训和行为模式，实现持续改进。

默认数据目录：~/.skills_data/soul-archive/agent/

Usage:
  # 自我反思：记录一次工作经历
  python3 soul_reflect.py --mode reflect --input "<反思内容>"

  # 自我批评：记录一次错误和修正
  python3 soul_reflect.py --mode critique --input "<批评内容>"

  # 自我学习：从经验中提取模式
  python3 soul_reflect.py --mode learn --input "<学习内容>"

  # 查看状态
  python3 soul_reflect.py --mode status

  # 查看模式库
  python3 soul_reflect.py --mode patterns

Works on: macOS, Linux, Windows
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# Encryption support (optional)
# ============================================================

def _try_import_crypto():
    """Try to import soul_crypto module."""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from soul_crypto import get_crypto_from_config
        return get_crypto_from_config
    except ImportError:
        return None


def load_json(path: Path, default=None, crypto=None):
    """Load JSON file, return default if not exists. Supports encrypted files."""
    if path.exists():
        if crypto and hasattr(crypto, 'decrypt_file'):
            try:
                return crypto.decrypt_file(path)
            except Exception:
                pass
        raw = path.read_text(encoding='utf-8')
        return json.loads(raw)
    return default if default is not None else {}


def save_json(path: Path, data: dict, crypto=None):
    """Save JSON file, supports encryption."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if crypto and hasattr(crypto, 'encrypt_file_save'):
        crypto.encrypt_file_save(path, data)
    else:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def append_jsonl(path: Path, entry: dict, crypto=None):
    """Append a JSON line to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if crypto and hasattr(crypto, 'encrypt_jsonl_line'):
        raw = crypto.encrypt_jsonl_line(entry)
        with open(path, 'ab') as f:
            f.write(raw)
    else:
        line = json.dumps(entry, ensure_ascii=False)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(line + '\n')


def read_jsonl(path: Path, crypto=None) -> list:
    """Read all lines from a JSONL file."""
    if not path.exists():
        return []
    entries = []
    if crypto and hasattr(crypto, 'decrypt_jsonl_line'):
        with open(path, 'rb') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(crypto.decrypt_jsonl_line(line))
                except Exception:
                    try:
                        entries.append(json.loads(line.decode('utf-8')))
                    except Exception:
                        continue
    else:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ============================================================
# ReflectionBuilder — 构建反思/批评/学习结果
# ============================================================

class ReflectionBuilder:
    """Builder for constructing AI self-improvement entries."""

    def __init__(self):
        self.result = {
            "reflections": [],
            "critiques": [],
            "patterns": {},
            "episodes": [],
            "summary": ""
        }

    # --- 自我反思 ---
    def add_reflection(self, task: str, outcome: str = "success",
                       went_well: list = None, went_wrong: list = None,
                       lesson: str = None):
        """Record a self-reflection after completing a task."""
        entry = {
            "timestamp": now_iso(),
            "task": task,
            "outcome": outcome,
        }
        if went_well:
            entry["what_went_well"] = went_well
        if went_wrong:
            entry["what_went_wrong"] = went_wrong
        if lesson:
            entry["lesson"] = lesson
        self.result["reflections"].append(entry)
        return self

    # --- 自我批评 ---
    def add_critique(self, trigger: str, user_said: str,
                     what_i_did_wrong: str, root_cause: str,
                     correction: str, severity: str = "medium",
                     pattern_id: str = None):
        """Record a self-critique when user corrects AI behavior."""
        entry = {
            "timestamp": now_iso(),
            "trigger": trigger,
            "user_said": user_said,
            "what_i_did_wrong": what_i_did_wrong,
            "root_cause": root_cause,
            "correction": correction,
            "severity": severity,
        }
        if pattern_id:
            entry["pattern_id"] = pattern_id
        self.result["critiques"].append(entry)
        return self

    # --- 自我学习（模式） ---
    def add_pattern(self, pattern_id: str, name: str, pattern: str,
                    source: str = "self_reflection", confidence: float = 0.8,
                    category: str = "general"):
        """Add or update a behavioral pattern."""
        self.result["patterns"][pattern_id] = {
            "id": pattern_id,
            "name": name,
            "pattern": pattern,
            "source": source,
            "confidence": confidence,
            "category": category,
            "applications": 0,
            "created": today_str(),
            "last_applied": today_str()
        }
        return self

    # --- 工作经历 ---
    def add_episode(self, task: str, skill_used: str = None,
                    outcome: str = "success", key_insight: str = None,
                    user_feedback: str = None):
        """Record a specific work episode."""
        entry = {
            "timestamp": now_iso(),
            "date": today_str(),
            "task": task,
            "outcome": outcome,
        }
        if skill_used:
            entry["skill_used"] = skill_used
        if key_insight:
            entry["key_insight"] = key_insight
        if user_feedback:
            entry["user_feedback"] = user_feedback
        self.result["episodes"].append(entry)
        return self

    def set_summary(self, summary: str):
        self.result["summary"] = summary
        return self

    def build(self) -> dict:
        return self.result


# ============================================================
# AgentMemory — AI 自我改进记忆管理
# ============================================================

class AgentMemory:
    """Manages the agent/ directory for AI self-improvement."""

    def __init__(self, soul_dir: str or Path, crypto=None):
        self.soul_dir = Path(soul_dir)
        self.agent_dir = self.soul_dir / "agent"
        self.crypto = crypto

        # Ensure directories exist
        (self.agent_dir / "episodes").mkdir(parents=True, exist_ok=True)

    def init_crypto_from_config(self, password: str = None):
        """Initialize encryption from config.json."""
        get_crypto = _try_import_crypto()
        if get_crypto is None:
            return
        config = load_json(self.soul_dir / "config.json", {})
        if config.get("encryption"):
            self.crypto = get_crypto(config, password)

    # --- Patterns ---
    def load_patterns(self) -> dict:
        data = load_json(self.agent_dir / "patterns.json",
                         {"patterns": {}}, self.crypto)
        return data.get("patterns", {})

    def save_patterns(self, patterns: dict):
        save_json(self.agent_dir / "patterns.json",
                  {"patterns": patterns,
                   "_meta": {"last_updated": now_iso(),
                             "total_patterns": len(patterns)}},
                  self.crypto)

    def update_pattern(self, pattern_id: str, pattern_data: dict):
        """Add or update a single pattern."""
        patterns = self.load_patterns()
        if pattern_id in patterns:
            # Update existing: bump applications, update last_applied
            existing = patterns[pattern_id]
            existing["applications"] = existing.get("applications", 0) + 1
            existing["last_applied"] = today_str()
            # Update confidence if new is higher
            if pattern_data.get("confidence", 0) > existing.get("confidence", 0):
                existing["confidence"] = pattern_data["confidence"]
            # Merge other fields
            for k in ["name", "pattern", "category"]:
                if k in pattern_data:
                    existing[k] = pattern_data[k]
        else:
            patterns[pattern_id] = pattern_data
        self.save_patterns(patterns)

    # --- Reflections ---
    def add_reflection(self, entry: dict):
        append_jsonl(self.agent_dir / "reflections.jsonl", entry, self.crypto)

    def load_reflections(self, limit: int = 20) -> list:
        entries = read_jsonl(self.agent_dir / "reflections.jsonl", self.crypto)
        return entries[-limit:]

    # --- Corrections/Critiques ---
    def add_correction(self, entry: dict):
        append_jsonl(self.agent_dir / "corrections.jsonl", entry, self.crypto)

    def load_corrections(self, limit: int = 20) -> list:
        entries = read_jsonl(self.agent_dir / "corrections.jsonl", self.crypto)
        return entries[-limit:]

    # --- Episodes ---
    def add_episode(self, entry: dict):
        date = entry.get("date", today_str())
        path = self.agent_dir / "episodes" / f"{date}.jsonl"
        append_jsonl(path, entry, self.crypto)

    def load_episodes(self, date: str = None, limit: int = 20) -> list:
        if date:
            path = self.agent_dir / "episodes" / f"{date}.jsonl"
            return read_jsonl(path, self.crypto)[-limit:]
        # Load all recent
        episode_dir = self.agent_dir / "episodes"
        if not episode_dir.exists():
            return []
        files = sorted(episode_dir.glob("*.jsonl"), reverse=True)
        entries = []
        for f in files:
            entries.extend(read_jsonl(f, self.crypto))
            if len(entries) >= limit:
                break
        return entries[-limit:]

    # --- Save extraction result ---
    def save_extraction(self, result: dict) -> list:
        """Save a full extraction result from ReflectionBuilder."""
        changes = []

        # Save reflections
        for r in result.get("reflections", []):
            self.add_reflection(r)
            changes.append(f"reflection: {r.get('task', '?')}")

        # Save critiques as corrections
        for c in result.get("critiques", []):
            self.add_correction(c)
            changes.append(f"critique: {c.get('what_i_did_wrong', '?')[:50]}")

        # Save/update patterns
        for pid, pdata in result.get("patterns", {}).items():
            self.update_pattern(pid, pdata)
            changes.append(f"pattern: {pid}")

        # Save episodes
        for e in result.get("episodes", []):
            self.add_episode(e)
            changes.append(f"episode: {e.get('task', '?')[:50]}")

        return changes

    # --- Status ---
    def get_status(self) -> dict:
        patterns = self.load_patterns()
        reflections = read_jsonl(self.agent_dir / "reflections.jsonl", self.crypto)
        corrections = read_jsonl(self.agent_dir / "corrections.jsonl", self.crypto)

        episode_count = 0
        episode_dir = self.agent_dir / "episodes"
        if episode_dir.exists():
            for f in episode_dir.glob("*.jsonl"):
                episode_count += len(read_jsonl(f, self.crypto))

        return {
            "total_patterns": len(patterns),
            "total_reflections": len(reflections),
            "total_corrections": len(corrections),
            "total_episodes": episode_count,
            "top_patterns": sorted(
                patterns.values(),
                key=lambda p: p.get("applications", 0),
                reverse=True
            )[:5]
        }


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="🧬 灵魂存档 — AI 自我改进引擎")
    parser.add_argument("--soul-dir", type=Path,
                        default=Path.home() / ".skills_data" / "soul-archive",
                        help="灵魂数据目录路径")
    parser.add_argument("--mode", choices=["reflect", "critique", "learn", "status", "patterns"],
                        default="status",
                        help="工作模式")
    parser.add_argument("--input", type=str, default=None,
                        help="输入内容（反思/批评/学习的文本）")
    parser.add_argument("--password", type=str, default=None,
                        help="加密密码")
    args = parser.parse_args()

    import os
    password = args.password or os.environ.get("SOUL_PASSWORD")

    agent = AgentMemory(args.soul_dir)
    if password:
        agent.init_crypto_from_config(password=password)

    if args.mode == "status":
        status = agent.get_status()
        print("🧬 AI 自我改进状态")
        print("=" * 40)
        print(f"  行为模式：{status['total_patterns']} 个")
        print(f"  自我反思：{status['total_reflections']} 次")
        print(f"  自我批评：{status['total_corrections']} 次")
        print(f"  工作经历：{status['total_episodes']} 条")
        if status['top_patterns']:
            print()
            print("  📊 高频模式：")
            for p in status['top_patterns']:
                print(f"    [{p.get('applications', 0)}x] {p.get('name', '?')} (置信度 {p.get('confidence', 0):.0%})")

    elif args.mode == "patterns":
        patterns = agent.load_patterns()
        if not patterns:
            print("暂无行为模式记录")
            return
        print(f"🧬 行为模式库 ({len(patterns)} 个)")
        print("=" * 50)
        for pid, p in patterns.items():
            print(f"\n  [{pid}]")
            print(f"    名称：{p.get('name', '?')}")
            print(f"    模式：{p.get('pattern', '?')}")
            print(f"    置信度：{p.get('confidence', 0):.0%}")
            print(f"    应用次数：{p.get('applications', 0)}")
            print(f"    来源：{p.get('source', '?')}")

    elif args.mode in ("reflect", "critique", "learn"):
        if not args.input:
            print(f"请提供 --input 参数（{args.mode} 的内容）")
            return
        print(f"📖 收到{args.mode}内容（{len(args.input)} 字符）")
        print(f"📂 灵魂存档路径：{args.soul_dir}")
        print()
        print("请使用 ReflectionBuilder 构建结果，然后调用 AgentMemory.save_extraction() 保存。")
        print()
        print("示例代码：")
        print("```python")
        print("from soul_reflect import AgentMemory, ReflectionBuilder")
        print(f"agent = AgentMemory('{args.soul_dir}')")
        print("builder = ReflectionBuilder()")
        print("builder.add_reflection(task='完成数据迁移', outcome='success',")
        print("    went_well=['全面扫描了路径'], went_wrong=['遗漏了一个目录'],")
        print("    lesson='迁移前应全面扫描所有目录')")
        print("builder.add_pattern('pat-thorough-scan', '全面扫描',")
        print("    pattern='执行迁移/清理操作前全面扫描目标范围')")
        print("changes = agent.save_extraction(builder.build())")
        print("```")


if __name__ == "__main__":
    main()
