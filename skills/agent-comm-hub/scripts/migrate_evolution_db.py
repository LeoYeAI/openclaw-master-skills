#!/usr/bin/env python3
"""
evolution.db → comm_hub.db strategies 数据迁移脚本

将 Hermes 旧版 evolution.db 中的 memories 数据迁移到 Hub 的 strategies 表。
经核实（2026-04-24），evolution.db memories 表为空（0 条记录），
本脚本作为未来数据迁移的备用工具。

用法：
    python3 migrate_evolution_db.py [--source /path/to/evolution.db] [--target /path/to/comm_hub.db] [--dry-run]

选项：
    --source   源数据库路径（默认 ~/.workbuddy/memory/evolution.db）
    --target   目标数据库路径（默认 ../comm_hub.db）
    --dry-run  只分析不写入，打印迁移计划
"""

import sqlite3
import hashlib
import sys
import os
import argparse
from datetime import datetime

# ─── 默认路径 ─────────────────────────────────────────────
DEFAULT_SOURCE = os.path.expanduser("~/.workbuddy/memory/evolution.db")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TARGET = os.path.join(SCRIPT_DIR, "..", "comm_hub.db")

# ─── evolution.db memories → strategies 字段映射 ─────────
# memories 表：id, hash, content, category, importance, tags, source, created_at, last_accessed
# strategies 表：id, title, content, category, sensitivity, proposer_id, status, ...

# category 映射
CATEGORY_MAP = {
    "general": "other",
    "workflow": "workflow",
    "fix": "fix",
    "tool_config": "tool_config",
    "prompt_template": "prompt_template",
    "experience": "experience",
    "other": "other",
}

# importance → sensitivity 映射
# evolution.db importance 1-5，5=最高 → sensitivity high/normal
def map_sensitivity(importance: int, content: str) -> str:
    """将 importance 值映射为 sensitivity"""
    if importance >= 4:
        return "high"
    # 高敏感关键词检测（与 Hub 逻辑一致）
    high_patterns = [
        "system_prompt", "系统指令", "capability_declare",
        "能力声明", "permission_change", "权限变更", "role_change",
    ]
    for p in high_patterns:
        if p.lower() in content.lower():
            return "high"
    return "normal"


def generate_title(content: str, max_len: int = 200) -> str:
    """从 content 生成标题（取第一行或前 100 字符）"""
    first_line = content.split("\n")[0].strip()
    if first_line and len(first_line) <= max_len:
        return first_line
    return content[:max_len - 3] + "..."


def migrate(source_path: str, target_path: str, dry_run: bool = False):
    """执行迁移"""
    print(f"=== evolution.db → comm_hub.db 迁移 ===")
    print(f"源: {source_path}")
    print(f"目标: {target_path}")
    print(f"模式: {'DRY RUN' if dry_run else 'LIVE'}")
    print()

    # 检查源文件
    if not os.path.exists(source_path):
        print(f"❌ 源文件不存在: {source_path}")
        return False

    # 连接数据库
    src = sqlite3.connect(source_path)
    tgt = sqlite3.connect(target_path)

    # 读取源数据
    rows = src.execute("SELECT id, hash, content, category, importance, tags, source, created_at FROM memories").fetchall()
    print(f"源 memories 表: {len(rows)} 条记录")

    if not rows:
        print("✅ 无数据需要迁移，退出")
        src.close()
        tgt.close()
        return True

    # 分析可迁移数据
    migrated = 0
    skipped = 0
    errors = 0

    for row in rows:
        mem_id, mem_hash, content, category, importance, tags, source_agent, created_at = row

        # 验证必要字段
        if not content or len(content) < 10:
            print(f"  ⏭️ 跳过 id={mem_id}: 内容过短（<10 字符）")
            skipped += 1
            continue

        if len(content) > 5000:
            print(f"  ⏭️ 跳过 id={mem_id}: 内容过长（>{5000} 字符）")
            skipped += 1
            continue

        # 映射字段
        title = generate_title(content)
        hub_category = CATEGORY_MAP.get(category, "other")
        sensitivity = map_sensitivity(importance, content)
        proposer_id = source_agent if source_agent and source_agent != "manual" else "migration_script"
        tags_json = tags if tags else "[]"

        print(f"  📋 迁移 id={mem_id}: '{title[:50]}...' → category={hub_category}, sensitivity={sensitivity}")

        if not dry_run:
            try:
                tgt.execute("""
                    INSERT INTO strategies (title, content, category, sensitivity, proposer_id, status, proposed_at, task_id, source_trust)
                    VALUES (?, ?, ?, ?, ?, 'approved', ?, ?, 50)
                """, (title, content, hub_category, sensitivity, proposer_id, created_at, tags_json))

                # 获取新 id 并插入 FTS
                new_id = tgt.execute("SELECT last_insert_rowid()").fetchone()[0]
                try:
                    tgt.execute("""
                        INSERT INTO strategies_fts (rowid, title, content, category)
                        VALUES (?, ?, ?, ?)
                    """, (new_id, title, content, hub_category))
                except Exception as fts_err:
                    print(f"    ⚠️ FTS 插入失败: {fts_err}")

                migrated += 1
            except Exception as e:
                print(f"    ❌ 错误: {e}")
                errors += 1

    if not dry_run:
        tgt.commit()

    # 一致性验证
    if not dry_run:
        tgt_total = tgt.execute("SELECT COUNT(*) FROM strategies WHERE proposer_id='migration_script'").fetchone()[0]
        print(f"\n=== 迁移验证 ===")
        print(f"迁移写入: {migrated}")
        print(f"跳过: {skipped}")
        print(f"错误: {errors}")
        print(f"目标表迁移记录: {tgt_total}")
        if tgt_total == migrated:
            print("✅ 一致性验证通过")
        else:
            print("⚠️ 一致性验证不匹配！")
    else:
        print(f"\n=== DRY RUN 摘要 ===")
        print(f"可迁移: {migrated + skipped - errors}")
        print(f"将跳过: {skipped}")

    src.close()
    tgt.close()
    return errors == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="evolution.db → comm_hub.db 数据迁移")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="源 evolution.db 路径")
    parser.add_argument("--target", default=DEFAULT_TARGET, help="目标 comm_hub.db 路径")
    parser.add_argument("--dry-run", action="store_true", help="只分析不写入")
    args = parser.parse_args()

    success = migrate(args.source, args.target, args.dry_run)
    sys.exit(0 if success else 1)
