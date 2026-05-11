#!/usr/bin/env python3
"""
Art of War Task Assessment
五事七计评估脚本 — Decide whether to deploy agents

Usage: python assess-task.py "task description"
"""

import sys
import json

FIVE_CONSTANTS = [
    ("道 (Wisdom)", "Does this task align with overall goals?"),
    ("天 (Timing)", "Is now the right time? Dependencies ready?"),
    ("地 (Environment)", "Do we have the right context/data/tools?"),
    ("将 (Capability)", "Which agent(s) have the right skills?"),
    ("法 (Process)", "What's the workflow? Success criteria?"),
]

SEVEN_METRICS = [
    "Task clarity",
    "Agent capability match",
    "Context/data availability",
    "Success criteria clarity",
    "Tool access",
    "Execution discipline",
    "Resource efficiency",
]


def score_constant(name, question):
    """Score a constant 0-1"""
    print(f"\n{name}")
    print(f"  {question}")
    while True:
        answer = input("  Score (0=no, 0.5=partial, 1=yes): ").strip()
        try:
            score = float(answer)
            if 0 <= score <= 1:
                return score
        except ValueError:
            pass
        print("  Invalid. Enter 0, 0.5, or 1")


def score_metric(name):
    """Score a metric 0-1"""
    print(f"\n{name}")
    while True:
        answer = input("  Score (0=them, 0.5=equal, 1=us): ").strip()
        try:
            score = float(answer)
            if 0 <= score <= 1:
                return score
        except ValueError:
            pass
        print("  Invalid. Enter 0, 0.5, or 1")


def assess_task(task_description):
    """Run full assessment"""
    print("=" * 60)
    print("ART OF WAR TASK ASSESSMENT")
    print("=" * 60)
    print(f"\nTask: {task_description}\n")
    
    # Five Constants
    print("\n" + "=" * 60)
    print("五事 (FIVE CONSTANTS)")
    print("=" * 60)
    constants_score = sum(score_constant(name, q) for name, q in FIVE_CONSTANTS)
    constants_max = len(FIVE_CONSTANTS)
    
    # Seven Metrics
    print("\n" + "=" * 60)
    print("七计 (SEVEN METRICS)")
    print("=" * 60)
    print("(Score: 0=task has advantage, 0.5=neutral, 1=you have advantage)\n")
    metrics_score = sum(score_metric(name) for name in SEVEN_METRICS)
    metrics_max = len(SEVEN_METRICS)
    
    # Results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    constants_pct = (constants_score / constants_max) * 100
    metrics_pct = (metrics_score / metrics_max) * 100
    
    print(f"\n五事 Score: {constants_score:.1f}/{constants_max} ({constants_pct:.0f}%)")
    print(f"七计 Score: {metrics_score:.1f}/{metrics_max} ({metrics_pct:.0f}%)")
    
    overall_score = (constants_score + metrics_score) / (constants_max + metrics_max) * 100
    
    print(f"\nOverall: {overall_score:.0f}%")
    
    # Recommendation
    print("\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)
    
    if overall_score >= 70:
        print("\n✓ DEPLOY AGENTS")
        print("  Conditions are favorable. Proceed with deployment.")
        print("  Remember: 速战速决 (speed is essential)")
    elif overall_score >= 50:
        print("\n⚠ CONDITIONAL DEPLOY")
        print("  Conditions are mixed. Address weak areas first:")
        if constants_score < metrics_score:
            print("  - Focus on planning (五事 scores low)")
        else:
            print("  - Focus on competitive advantage (七计 scores low)")
        print("  Then deploy with caution.")
    else:
        print("\n✗ DO NOT DEPLOY")
        print("  Conditions are unfavorable. Plan first.")
        print("  上兵伐谋 — Attack the problem with strategy, not agents.")
    
    print("\n" + "=" * 60)
    
    return {
        "task": task_description,
        "five_constants": {"score": constants_score, "max": constants_max},
        "seven_metrics": {"score": metrics_score, "max": metrics_max},
        "overall": overall_score,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python assess-task.py \"task description\"")
        print("\nOr run without args for interactive mode")
        task = input("\nEnter task description: ").strip()
    else:
        task = " ".join(sys.argv[1:])
    
    result = assess_task(task)
    
    # Output JSON for programmatic use
    print("\nJSON Output:")
    print(json.dumps(result, indent=2))
