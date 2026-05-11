#!/usr/bin/env python3
"""
RAGAS Evaluation Pipeline for RAG Systems.

Usage:
    python eval_ragas.py --test-file eval_dataset.json --output results.json
    python eval_ragas.py --test-file eval_dataset.json --metrics faithfulness,answer_relevancy

Input format (eval_dataset.json):
{
    "test_cases": [
        {
            "question": "...",
            "answer": "...",           # RAG system's answer
            "contexts": ["chunk1", "chunk2"],  # Retrieved chunks
            "ground_truth": "..."      # Expected correct answer
        }
    ]
}

Output: JSON with metric scores + per-question breakdown.

Requirements:
    pip install ragas langchain-openai datasets
    export OPENAI_API_KEY=your_key
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    from datasets import Dataset
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install ragas langchain-openai datasets")
    sys.exit(1)


AVAILABLE_METRICS = {
    "faithfulness": faithfulness,
    "answer_relevancy": answer_relevancy,
    "context_precision": context_precision,
    "context_recall": context_recall,
}

DEFAULT_THRESHOLDS = {
    "faithfulness": 0.85,
    "answer_relevancy": 0.80,
    "context_precision": 0.75,
    "context_recall": 0.80,
}


def load_test_data(filepath: str) -> dict:
    """Load and validate test data."""
    with open(filepath) as f:
        data = json.load(f)

    test_cases = data.get("test_cases", data.get("samples", []))
    if not test_cases:
        raise ValueError("No test_cases found in input file")

    # Validate required fields
    required = {"question", "answer", "contexts", "ground_truth"}
    for i, case in enumerate(test_cases):
        missing = required - set(case.keys())
        if missing:
            raise ValueError(f"Test case {i} missing fields: {missing}")
        if not isinstance(case["contexts"], list):
            raise ValueError(f"Test case {i}: 'contexts' must be a list of strings")

    return {
        "question": [c["question"] for c in test_cases],
        "answer": [c["answer"] for c in test_cases],
        "contexts": [c["contexts"] for c in test_cases],
        "ground_truth": [c["ground_truth"] for c in test_cases],
    }


def run_evaluation(
    test_data: dict,
    metric_names: list[str] | None = None,
) -> dict:
    """Run RAGAS evaluation."""
    # Select metrics
    if metric_names:
        metrics = [AVAILABLE_METRICS[m] for m in metric_names if m in AVAILABLE_METRICS]
    else:
        metrics = list(AVAILABLE_METRICS.values())
        metric_names = list(AVAILABLE_METRICS.keys())

    if not metrics:
        raise ValueError(f"No valid metrics. Available: {list(AVAILABLE_METRICS.keys())}")

    dataset = Dataset.from_dict(test_data)

    print(f"📊 Running RAGAS evaluation...")
    print(f"   Metrics: {metric_names}")
    print(f"   Test cases: {len(test_data['question'])}")

    results = evaluate(dataset=dataset, metrics=metrics)

    return results


def check_thresholds(scores: dict, thresholds: dict | None = None) -> dict:
    """Check if scores meet thresholds."""
    thresholds = thresholds or DEFAULT_THRESHOLDS
    checks = {}

    for metric, threshold in thresholds.items():
        if metric in scores:
            passed = scores[metric] >= threshold
            checks[metric] = {
                "score": round(scores[metric], 4),
                "threshold": threshold,
                "passed": passed,
                "status": "✅" if passed else "❌",
            }

    return checks


def main():
    parser = argparse.ArgumentParser(description="RAGAS Evaluation Pipeline")
    parser.add_argument("--test-file", required=True, help="Path to test dataset JSON")
    parser.add_argument("--output", default="ragas_results.json", help="Output file path")
    parser.add_argument(
        "--metrics",
        default=None,
        help="Comma-separated metrics (default: all). Options: faithfulness,answer_relevancy,context_precision,context_recall",
    )
    parser.add_argument(
        "--thresholds",
        default=None,
        help="JSON string of custom thresholds, e.g. '{\"faithfulness\": 0.9}'",
    )
    args = parser.parse_args()

    # Parse metrics
    metric_names = args.metrics.split(",") if args.metrics else None

    # Parse thresholds
    thresholds = json.loads(args.thresholds) if args.thresholds else None

    # Load data
    print(f"📂 Loading test data from: {args.test_file}")
    test_data = load_test_data(args.test_file)

    # Run evaluation
    results = run_evaluation(test_data, metric_names)

    # Get scores
    scores = {k: v for k, v in results.items() if isinstance(v, (int, float))}

    # Check thresholds
    threshold_checks = check_thresholds(scores, thresholds)

    # Build output
    output = {
        "timestamp": datetime.now().isoformat(),
        "test_file": args.test_file,
        "num_cases": len(test_data["question"]),
        "scores": {k: round(v, 4) for k, v in scores.items()},
        "threshold_checks": threshold_checks,
        "all_passed": all(c["passed"] for c in threshold_checks.values()),
    }

    # Per-question breakdown
    try:
        df = results.to_pandas()
        output["per_question"] = df.to_dict(orient="records")
    except Exception:
        pass

    # Save results
    output_path = Path(args.output)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\n📄 Results saved to: {output_path}")

    # Print summary
    print("\n" + "=" * 50)
    print("📊 RAGAS Evaluation Results")
    print("=" * 50)
    for metric, check in threshold_checks.items():
        print(f"  {check['status']} {metric}: {check['score']:.4f} (threshold: {check['threshold']})")

    all_passed = output["all_passed"]
    print(f"\n{'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
