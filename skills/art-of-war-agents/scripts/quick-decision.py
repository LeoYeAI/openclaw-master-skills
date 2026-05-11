#!/usr/bin/env python3
"""
Art of War Quick Decision Card
Interactive prompt-based decision helper for agent deployment

Usage: python quick-decision.py
"""

import sys

QUESTIONS = [
    # 始计篇 — Task Assessment
    ("始计篇", [
        ("任务目标清晰吗？", "Task goal is clearly defined"),
        ("现在是合适的时机吗？", "Timing is right (dependencies ready)"),
        ("有足够的上下文/数据吗？", "Sufficient context/data available"),
        ("有合适的 agent 吗？", "Right agent(s) available"),
        ("流程清晰吗？", "Workflow and success criteria defined"),
    ]),
    # 谋攻篇 — Planning
    ("谋攻篇", [
        ("这个任务能消除/自动化吗？", "Can task be eliminated/automated"),
        ("单 agent 能解决吗？", "Can single agent handle it"),
        ("还是必须多 agent 协作？", "Or is multi-agent truly necessary"),
    ]),
    # 作战篇 — Cost
    ("作战篇", [
        ("Token 预算是多少？", "What's the token budget"),
        ("有设迭代限制吗？", "Iteration limit set"),
        ("有重用现有输出吗？", "Reusing existing outputs"),
    ]),
    # 军形篇 — Risk
    ("军形篇", [
        ("最坏情况是什么？", "Worst case identified"),
        ("有回滚方案吗？", "Rollback plan exists"),
        ("有验证机制吗？", "Validation mechanism in place"),
    ]),
]

DECISIONS = {
    (17, 20): "✅ DEPLOY — 条件有利，速战速决",
    (13, 16): "⚠ CONDITIONAL — 先补弱点再部署",
    (0, 12): "❌ NO DEPLOY — 重新规划，上兵伐谋",
}


def get_score():
    total = 0
    max_score = 0
    
    print("=" * 60)
    print("ART OF WAR AGENT DECISION CARD")
    print("=" * 60)
    print()
    
    for section, questions in QUESTIONS:
        print(f"\n📍 {section}")
        print("-" * 40)
        for q_cn, q_en in questions:
            print(f"\n  {q_cn}")
            print(f"  ({q_en})")
            while True:
                ans = input("  [0=no, 1=yes, s=skip]: ").strip().lower()
                if ans == 's':
                    break
                elif ans == '1':
                    total += 1
                    max_score += 1
                    break
                elif ans == '0':
                    max_score += 1
                    break
                else:
                    print("  输入 0, 1, 或 s")
    
    return total, max_score


def get_decision(score, max_score):
    for (min_s, max_s), decision in DECISIONS.items():
        if min_s <= score <= max_s:
            return decision
    return "❓ UNKNOWN"


def main():
    score, max_score = get_score()
    pct = (score / max_score * 100) if max_score > 0 else 0
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nScore: {score}/{max_score} ({pct:.0f}%)")
    print()
    print(get_decision(score, max_score))
    print()
    
    # Specific recommendations
    print("=" * 60)
    print("KEY REMINDERS")
    print("=" * 60)
    print()
    print("• 知彼知己 — Understand task + know agent limits")
    print("• 上兵伐谋 — Plan first, execute second")
    print("• 速战速决 — Set iteration limits, force conclusions")
    print("• 先胜后战 — Ensure conditions favor success")
    print("• 三反原则 — Cross-verify with 3+ sources")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
