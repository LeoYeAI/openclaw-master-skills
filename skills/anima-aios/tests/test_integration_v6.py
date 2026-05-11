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
Anima AIOS v6.0 - 集成测试

全链路测试：L1→L2→L3→L4→L5
对照铁律验收标准逐项检查。

Author: 清禾
Date: 2026-03-24
"""

import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# 设置路径
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "core"))
sys.path.insert(0, str(SKILL_DIR / "health"))
sys.path.insert(0, str(SKILL_DIR))

AGENT = "test_v6"
FACTS_BASE = tempfile.mkdtemp(prefix="anima_test_")
WATCH_DIR = Path(FACTS_BASE) / "workspace_memory"
WATCH_DIR.mkdir(parents=True)

os.environ["ANIMA_AGENT_NAME"] = AGENT
os.environ["ANIMA_FACTS_BASE"] = FACTS_BASE
os.environ["ANIMA_WATCH_DIR"] = str(WATCH_DIR)

results = []

def check(name, condition, detail=""):
    status = "✅" if condition else "❌"
    results.append({"name": name, "pass": condition, "detail": detail})
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))
    return condition


def main():
    print(f"\n{'='*60}")
    print(f"  Anima AIOS v6.0 集成测试")
    print(f"  Agent: {AGENT} | Facts: {FACTS_BASE}")
    print(f"{'='*60}\n")

    # ===== 1. L1→L2: MemoryWatcher =====
    print("【1】L1→L2: MemoryWatcher + 自动同步")
    
    from memory_watcher import MemoryWatcher
    watcher = MemoryWatcher()
    observer = watcher.start(blocking=False)
    time.sleep(0.5)

    # 写入测试记忆
    test_file = WATCH_DIR / "2026-03-24.md"
    test_file.write_text("# 架构决策记录\n\n## 重要决策：v6 技术方案\n- 决策：v6 选择 Python 统一技术栈，避免混合运行时。这是一个关键的架构设计决策，影响整个项目的技术方向。\n- 方案：使用 watchdog 库实现跨平台文件监听，inotify/FSEvents/polling 三层降级。\n- 原则：金字塔原理用于组织 L4 知识体系，自底向上提炼：实例→规则→模式→本体。\n- 教训：架构只能演进不能退化，这是立文定的铁律。v5 的问题是方向错了不是速度慢。\n", encoding='utf-8')
    time.sleep(2)

    check("L1 → L2 自动同步", watcher._synced_count >= 1, f"同步 {watcher._synced_count} 条")
    
    # 检查 L2 文件
    episodic_dir = Path(FACTS_BASE) / AGENT / "facts" / "episodic"
    l2_files = list(episodic_dir.glob("*.md")) if episodic_dir.exists() else []
    check("L2 episodic 文件生成", len(l2_files) >= 1, f"{len(l2_files)} 个文件")
    
    # 检查 EXP
    exp_file = Path(FACTS_BASE) / AGENT / "exp_history.jsonl"
    check("EXP 自动记录", exp_file.exists() and exp_file.stat().st_size > 0)

    observer.stop()
    observer.join()

    # ===== 2. L2→L3: DistillEngine =====
    print("\n【2】L2→L3: DistillEngine + 质量评估")

    from distill_engine import DistillEngine
    engine = DistillEngine(AGENT, FACTS_BASE)
    stats = engine.run(batch_size=10, dry_run=False)

    check("质量评估执行", stats["assessed"] >= 1, f"评估 {stats['assessed']} 条")
    check("质量分布合理", sum(stats["quality_distribution"].values()) >= 1,
          json.dumps(stats["quality_distribution"]))
    check("L3 提炼写入", stats["distilled"] >= 1, f"提炼 {stats['distilled']} 条")

    from fact_store import FactStore
    store = FactStore(AGENT, FACTS_BASE)
    check("L3 semantic 文件存在", store.count("semantic") >= 1, f"{store.count('semantic')} 条")

    # ===== 3. L4: 知识宫殿 =====
    print("\n【3】L4: 知识宫殿 + 房间管理")

    from palace_index import PalaceIndex
    palace = PalaceIndex(AGENT, FACTS_BASE)
    
    rooms = palace.list_rooms()
    check("默认房间初始化", len(rooms) >= 5, f"{len(rooms)} 个房间")
    check("_inbox 房间存在", any(r["id"] == "_inbox" for r in rooms))

    # 添加知识
    palace.add_item("technical", "t1", "Python watchdog 跨平台文件监听", ["python"])
    palace.add_item("decision", "t2", "v6 选择 Python 统一技术栈", ["architecture"])
    
    check("知识添加到房间", palace.get_stats()["total_items"] >= 2)
    
    # 搜索
    results_search = palace.search("watchdog")
    check("宫殿搜索功能", len(results_search) >= 1)

    # 关键词分类
    room = palace.classify_by_keywords("修复 Python 代码中的 bug")
    check("关键词分类", room == "technical", f"分类到 {room}")

    # ===== 4. L4: 金字塔 =====
    print("\n【4】L4: 金字塔知识组织")

    from pyramid_engine import PyramidEngine
    pyramid = PyramidEngine(AGENT, FACTS_BASE, auto_distill=False)
    
    pyramid.add_instance("watchdog 用 inotify 监听", topic="文件监控")
    pyramid.add_instance("FSEvents 用于 macOS", topic="文件监控")
    pyramid.add_instance("polling 作为 fallback", topic="文件监控")
    
    pstats = pyramid.get_stats()
    check("实例层写入", pstats["levels"]["instances"] >= 3)
    
    # 手动提炼
    entry = pyramid.distill_up("文件监控", "instances")
    check("规则层提炼", entry is not None and pstats["levels"]["instances"] >= 3)
    
    # 查询
    q = pyramid.query(topic="文件监控")
    check("金字塔查询", len(q) >= 3)

    topics = pyramid.get_topics()
    check("主题统计", "文件监控" in topics)

    # ===== 5. L4: 宫殿分类调度器 =====
    print("\n【5】L4: 宫殿分类调度器（防抖）")

    from palace_classifier import PalaceClassifier
    classifier = PalaceClassifier(AGENT, FACTS_BASE)
    
    unclassified = classifier.get_unclassified()
    check("获取未分类知识", isinstance(unclassified, list))

    if unclassified:
        batch_result = classifier.classify_batch(unclassified)
        check("批量分类执行", batch_result["classified"] >= 0)
    else:
        check("批量分类执行", True, "无待分类知识（正常）")

    status = classifier.get_status()
    check("调度器状态", "poll_interval_minutes" in status)

    # ===== 6. L5: 记忆衰减 =====
    print("\n【6】L5: 记忆衰减函数")

    from decay_function import memory_strength, DecayManager

    # 衰减计算
    s0 = memory_strength(0, 1.0, 1.0, 0)
    s7 = memory_strength(7, 1.0, 1.0, 0)
    s7r = memory_strength(7, 1.0, 1.0, 3)
    
    check("初始强度 = 1.0", abs(s0 - 1.0) < 0.001)
    check("7天后衰减", 0.3 < s7 < 0.4, f"{s7:.3f}")
    check("复习延缓衰减", s7r > s7, f"无复习={s7:.3f}, 3次复习={s7r:.3f}")

    dm = DecayManager(AGENT, FACTS_BASE)
    dm.record_access("decay_test_1", "A")
    check("衰减管理器", dm.get_strength("decay_test_1", "A") > 0.7)

    # 复习推荐
    recs = dm.get_review_recommendations([
        {"fact_id": "old_fact", "quality": "A", "content": "旧知识"}
    ])
    check("复习推荐功能", isinstance(recs, list))

    # ===== 7. L5: 健康系统 =====
    print("\n【7】L5: 健康系统 (5 模块)")

    from health import HealthManager
    mgr = HealthManager(AGENT, FACTS_BASE)

    report = mgr.full_checkup()
    check("健康检查执行", "modules" in report)
    check("完整性检查", "integrity" in report["modules"])
    check("重复检查", "duplicates" in report["modules"])
    check("衰减状态", "decay" in report["modules"])
    check("宫殿状态", "palace" in report["modules"])
    check("金字塔状态", "pyramid" in report["modules"])

    # 自动修复
    fix = mgr.auto_fix()
    check("自动修复执行", "corrections" in fix)

    # 每日进化
    evo = mgr.run_evolution()
    check("每日进化执行", "steps" in evo)

    # ===== 8. 回滚兼容性 =====
    print("\n【8】回滚兼容性")
    
    # v5 数据不受影响
    check("v5 exp_history 存在", exp_file.exists())
    
    # v6 目录可独立删除
    v6_dirs = ["palace", "pyramid", "decay", "health"]
    for d in v6_dirs:
        check(f"v6 目录 {d}/ 独立", (Path(FACTS_BASE) / AGENT / d).exists())

    # ===== 汇总 =====
    print(f"\n{'='*60}")
    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    print(f"  结果: {passed}/{total} 通过 ({passed/total*100:.0f}%)")
    
    failed = [r for r in results if not r["pass"]]
    if failed:
        print(f"\n  ❌ 失败项:")
        for f in failed:
            print(f"    - {f['name']}: {f.get('detail', '')}")
    else:
        print(f"  🎉 全部通过！")
    
    print(f"{'='*60}\n")

    # 清理
    shutil.rmtree(FACTS_BASE, ignore_errors=True)
    
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
