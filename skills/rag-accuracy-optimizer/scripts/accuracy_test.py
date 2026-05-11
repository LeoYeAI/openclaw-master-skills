#!/usr/bin/env python3
"""
RAG Accuracy Test Framework — Generic test framework for any RAG system.

Test RAG pipeline using ground truth Q&A pairs.
Measures: Retrieval metrics (Precision, Recall, MRR, NDCG) + Answer accuracy.

Usage:
    python3 accuracy_test.py --test-file tests.json --results-dir ./results
    python3 accuracy_test.py --test-file tests.json --retrieval-fn my_module:search
    python3 accuracy_test.py --generate-template --output tests.json

Test file format (JSON):
{
    "config": {
        "name": "RAG Test Suite v1",
        "retrieval_top_k": 10,
        "answer_model": "gpt-4o-mini"
    },
    "test_cases": [
        {
            "id": "tc_001",
            "question": "Câu hỏi?",
            "expected_answer": "Câu trả lời mong đợi",
            "expected_sources": ["source1.pdf"],
            "expected_chunk_ids": ["chunk_01", "chunk_02"],
            "category": "general",
            "difficulty": "easy"
        }
    ]
}
"""

import argparse
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


# ============================================================
# Data Models
# ============================================================

@dataclass
class TestCase:
    """A single test case with ground truth."""
    id: str
    question: str
    expected_answer: str
    expected_sources: list[str] = field(default_factory=list)
    expected_chunk_ids: list[str] = field(default_factory=list)
    category: str = "general"
    difficulty: str = "medium"


@dataclass
class RetrievalResult:
    """Retrieval result for a single query."""
    chunk_id: str
    text: str
    score: float
    source: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class TestResult:
    """Test result for a single test case."""
    test_id: str
    question: str
    category: str
    difficulty: str
    # Retrieval metrics
    retrieved_ids: list[str]
    expected_ids: list[str]
    precision_at_k: float
    recall_at_k: float
    mrr: float
    ndcg: float
    # Answer metrics
    generated_answer: str = ""
    expected_answer: str = ""
    answer_match: float = 0.0  # 0-1 similarity
    # Source metrics
    source_match: bool = False
    # Status
    passed: bool = False
    error: str = ""


@dataclass
class TestSuiteReport:
    """Aggregate results for the entire test suite."""
    name: str
    timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float
    # Aggregate metrics
    avg_precision: float
    avg_recall: float
    avg_mrr: float
    avg_ndcg: float
    avg_answer_match: float
    # By category
    metrics_by_category: dict
    metrics_by_difficulty: dict
    # Details
    test_results: list[TestResult]
    # Recommendations
    recommendations: list[str]


# ============================================================
# Metrics Functions
# ============================================================

def precision_at_k(retrieved: list[str], relevant: list[str], k: int = None) -> float:
    """Precision@K: % retrieved items that are relevant."""
    if not retrieved:
        return 0.0
    if k:
        retrieved = retrieved[:k]
    relevant_set = set(relevant)
    hits = sum(1 for r in retrieved if r in relevant_set)
    return hits / len(retrieved)


def recall_at_k(retrieved: list[str], relevant: list[str], k: int = None) -> float:
    """Recall@K: % relevant items that are retrieved."""
    if not relevant:
        return 1.0  # Vacuously true
    if k:
        retrieved = retrieved[:k]
    relevant_set = set(relevant)
    hits = sum(1 for r in retrieved if r in relevant_set)
    return hits / len(relevant_set)


def mean_reciprocal_rank(retrieved: list[str], relevant: list[str]) -> float:
    """MRR: 1/rank of first relevant result."""
    relevant_set = set(relevant)
    for i, doc_id in enumerate(retrieved):
        if doc_id in relevant_set:
            return 1.0 / (i + 1)
    return 0.0


def ndcg_at_k(retrieved: list[str], relevant: list[str], k: int = None) -> float:
    """NDCG@K: Normalized Discounted Cumulative Gain."""
    if not relevant:
        return 1.0
    if k:
        retrieved = retrieved[:k]

    relevant_set = set(relevant)

    # DCG
    dcg = 0.0
    for i, doc_id in enumerate(retrieved):
        rel = 1.0 if doc_id in relevant_set else 0.0
        dcg += rel / math.log2(i + 2)

    # Ideal DCG
    ideal_rels = sorted([1.0] * min(len(relevant), len(retrieved)), reverse=True)
    idcg = sum(r / math.log2(i + 2) for i, r in enumerate(ideal_rels))

    return dcg / idcg if idcg > 0 else 0.0


def f1_score(precision: float, recall: float) -> float:
    """F1 = harmonic mean of precision and recall."""
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def simple_answer_similarity(generated: str, expected: str) -> float:
    """
    Simple: word overlap similarity.
    For production, use LLM judge or embedding similarity.
    """
    if not generated or not expected:
        return 0.0

    gen_words = set(generated.lower().split())
    exp_words = set(expected.lower().split())

    if not exp_words:
        return 0.0

    intersection = gen_words & exp_words
    # Jaccard-like nhưng weighted toward expected
    recall = len(intersection) / len(exp_words)
    precision = len(intersection) / len(gen_words) if gen_words else 0

    return f1_score(precision, recall)


# ============================================================
# Test Runner
# ============================================================

class RAGTestRunner:
    """
    Generic test runner for RAG systems.
    Inject retrieval_fn and answer_fn to test any RAG pipeline.
    """

    def __init__(
        self,
        retrieval_fn: Callable[[str], list[RetrievalResult]] | None = None,
        answer_fn: Callable[[str, list[RetrievalResult]], str] | None = None,
        answer_similarity_fn: Callable[[str, str], float] | None = None,
        top_k: int = 10,
    ):
        """
        Args:
            retrieval_fn: Function: query → returns list[RetrievalResult]
            answer_fn: Function: (query, retrieved_chunks) → returns answer string
            answer_similarity_fn: Function: (generated, expected) → score 0-1
            top_k: Max results to evaluate
        """
        self.retrieval_fn = retrieval_fn
        self.answer_fn = answer_fn
        self.similarity_fn = answer_similarity_fn or simple_answer_similarity
        self.top_k = top_k

    def run_single(self, test_case: TestCase) -> TestResult:
        """Run a single test case."""
        result = TestResult(
            test_id=test_case.id,
            question=test_case.question,
            category=test_case.category,
            difficulty=test_case.difficulty,
            retrieved_ids=[],
            expected_ids=test_case.expected_chunk_ids,
            precision_at_k=0.0,
            recall_at_k=0.0,
            mrr=0.0,
            ndcg=0.0,
            expected_answer=test_case.expected_answer,
        )

        try:
            # Retrieval
            if self.retrieval_fn:
                retrieved = self.retrieval_fn(test_case.question)
                result.retrieved_ids = [r.chunk_id for r in retrieved[:self.top_k]]

                # Retrieval metrics (chỉ khi có expected_chunk_ids)
                if test_case.expected_chunk_ids:
                    result.precision_at_k = precision_at_k(
                        result.retrieved_ids, test_case.expected_chunk_ids, self.top_k
                    )
                    result.recall_at_k = recall_at_k(
                        result.retrieved_ids, test_case.expected_chunk_ids, self.top_k
                    )
                    result.mrr = mean_reciprocal_rank(
                        result.retrieved_ids, test_case.expected_chunk_ids
                    )
                    result.ndcg = ndcg_at_k(
                        result.retrieved_ids, test_case.expected_chunk_ids, self.top_k
                    )

                # Source matching
                if test_case.expected_sources:
                    retrieved_sources = {r.source for r in retrieved[:self.top_k]}
                    result.source_match = any(
                        s in retrieved_sources for s in test_case.expected_sources
                    )

                # Answer generation
                if self.answer_fn:
                    result.generated_answer = self.answer_fn(test_case.question, retrieved)
                    result.answer_match = self.similarity_fn(
                        result.generated_answer, test_case.expected_answer
                    )
            else:
                # Không có retrieval_fn → chỉ test answer similarity nếu có sẵn answer
                if self.answer_fn:
                    result.generated_answer = self.answer_fn(test_case.question, [])
                    result.answer_match = self.similarity_fn(
                        result.generated_answer, test_case.expected_answer
                    )

            # Pass/fail logic
            result.passed = (
                (result.recall_at_k >= 0.5 or not test_case.expected_chunk_ids) and
                (result.answer_match >= 0.3 or not self.answer_fn)
            )

        except Exception as e:
            result.error = str(e)
            result.passed = False

        return result

    def run_suite(self, test_cases: list[TestCase], suite_name: str = "RAG Test") -> TestSuiteReport:
        """Run the entire test suite."""
        results = []
        for i, tc in enumerate(test_cases):
            print(f"  [{i+1}/{len(test_cases)}] Testing: {tc.question[:60]}...", file=sys.stderr)
            result = self.run_single(tc)
            status = "✅" if result.passed else "❌"
            print(f"  {status} {tc.id} (P={result.precision_at_k:.2f} R={result.recall_at_k:.2f} MRR={result.mrr:.2f})", file=sys.stderr)
            results.append(result)

        return self._compile_report(results, suite_name)

    def _compile_report(self, results: list[TestResult], suite_name: str) -> TestSuiteReport:
        """Compile results into a report."""
        total = len(results)
        passed = sum(1 for r in results if r.passed)

        def avg(values: list[float]) -> float:
            return sum(values) / len(values) if values else 0.0

        # Aggregate metrics
        avg_p = avg([r.precision_at_k for r in results])
        avg_r = avg([r.recall_at_k for r in results])
        avg_mrr = avg([r.mrr for r in results])
        avg_ndcg = avg([r.ndcg for r in results])
        avg_answer = avg([r.answer_match for r in results])

        # By category
        by_cat = defaultdict(list)
        by_diff = defaultdict(list)
        for r in results:
            by_cat[r.category].append(r)
            by_diff[r.difficulty].append(r)

        def group_metrics(group: list[TestResult]) -> dict:
            return {
                "count": len(group),
                "pass_rate": sum(1 for r in group if r.passed) / len(group) if group else 0,
                "avg_precision": avg([r.precision_at_k for r in group]),
                "avg_recall": avg([r.recall_at_k for r in group]),
                "avg_mrr": avg([r.mrr for r in group]),
                "avg_ndcg": avg([r.ndcg for r in group]),
                "avg_answer_match": avg([r.answer_match for r in group]),
            }

        metrics_cat = {cat: group_metrics(rs) for cat, rs in by_cat.items()}
        metrics_diff = {diff: group_metrics(rs) for diff, rs in by_diff.items()}

        # Recommendations
        recommendations = []
        if avg_r < 0.7:
            recommendations.append("⚠️ Low recall (<0.7). Improve chunking or add multi-query.")
        if avg_p < 0.5:
            recommendations.append("⚠️ Low precision (<0.5). Add reranking or metadata filtering.")
        if avg_mrr < 0.6:
            recommendations.append("⚠️ Low MRR (<0.6). Correct results often ranked low → needs reranking.")
        if avg_answer < 0.5 and avg_answer > 0:
            recommendations.append("⚠️ Low answer accuracy. Improve generation prompt or add few-shot.")

        # Analyze failures by category
        for cat, metrics in metrics_cat.items():
            if metrics["pass_rate"] < 0.5:
                recommendations.append(f"📂 Category '{cat}' has pass rate <50%. Review chunking for this category.")

        for diff, metrics in metrics_diff.items():
            if metrics["pass_rate"] < 0.3 and diff == "hard":
                recommendations.append("🔴 Hard questions have pass rate <30%. Consider multi-query + reranking.")

        if not recommendations:
            recommendations.append("✅ Overall results are good!")

        return TestSuiteReport(
            name=suite_name,
            timestamp=datetime.now().isoformat(),
            total_tests=total,
            passed_tests=passed,
            failed_tests=total - passed,
            pass_rate=passed / total if total > 0 else 0,
            avg_precision=round(avg_p, 4),
            avg_recall=round(avg_r, 4),
            avg_mrr=round(avg_mrr, 4),
            avg_ndcg=round(avg_ndcg, 4),
            avg_answer_match=round(avg_answer, 4),
            metrics_by_category=metrics_cat,
            metrics_by_difficulty=metrics_diff,
            test_results=results,
            recommendations=recommendations,
        )


# ============================================================
# File I/O
# ============================================================

def load_test_suite(file_path: str) -> tuple[dict, list[TestCase]]:
    """Load test suite from JSON file."""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(path.read_text(encoding="utf-8"))
    config = data.get("config", {})

    test_cases = []
    for tc in data.get("test_cases", []):
        test_cases.append(TestCase(
            id=tc.get("id", f"tc_{len(test_cases):03d}"),
            question=tc["question"],
            expected_answer=tc.get("expected_answer", ""),
            expected_sources=tc.get("expected_sources", []),
            expected_chunk_ids=tc.get("expected_chunk_ids", []),
            category=tc.get("category", "general"),
            difficulty=tc.get("difficulty", "medium"),
        ))

    return config, test_cases


def generate_template(output_path: str):
    """Generate template test file."""
    template = {
        "config": {
            "name": "RAG Test Suite v1",
            "description": "Ground truth test cases cho RAG system",
            "retrieval_top_k": 10,
            "pass_threshold": {
                "recall": 0.7,
                "answer_match": 0.3
            }
        },
        "test_cases": [
            {
                "id": "tc_001",
                "question": "Bảo hiểm nhân thọ có chi trả khi tự tử không?",
                "expected_answer": "Bảo hiểm nhân thọ không chi trả trong trường hợp tự tử trong 2 năm đầu kể từ ngày hợp đồng có hiệu lực.",
                "expected_sources": ["policy_life_v2.pdf"],
                "expected_chunk_ids": ["chunk_015", "chunk_016"],
                "category": "exclusions",
                "difficulty": "medium"
            },
            {
                "id": "tc_002",
                "question": "Thời gian chờ bảo hiểm sức khỏe là bao lâu?",
                "expected_answer": "Thời gian chờ là 30 ngày đối với bệnh thông thường và 12 tháng đối với bệnh đặc biệt.",
                "expected_sources": ["policy_health_v3.pdf"],
                "expected_chunk_ids": ["chunk_042"],
                "category": "waiting_period",
                "difficulty": "easy"
            },
            {
                "id": "tc_003",
                "question": "So sánh quyền lợi gói Gold và Platinum?",
                "expected_answer": "Gói Gold bao gồm nội trú với hạn mức 500 triệu/năm. Gói Platinum bao gồm nội trú + ngoại trú với hạn mức 1 tỷ/năm, thêm quyền lợi nha khoa và thai sản.",
                "expected_sources": ["product_comparison.pdf"],
                "expected_chunk_ids": ["chunk_101", "chunk_102", "chunk_103"],
                "category": "comparison",
                "difficulty": "hard"
            }
        ]
    }

    Path(output_path).write_text(
        json.dumps(template, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"✅ Template saved: {output_path}")


def save_report(report: TestSuiteReport, results_dir: str):
    """Save report to file."""
    path = Path(results_dir)
    path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = path / f"report_{timestamp}.json"
    summary_file = path / f"summary_{timestamp}.txt"

    # Full JSON report
    report_dict = asdict(report)
    report_file.write_text(
        json.dumps(report_dict, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8"
    )

    # Human-readable summary
    summary_lines = [
        f"{'='*60}",
        f"📊 RAG ACCURACY TEST REPORT",
        f"{'='*60}",
        f"Suite:        {report.name}",
        f"Timestamp:    {report.timestamp}",
        f"Total tests:  {report.total_tests}",
        f"Passed:       {report.passed_tests} ({report.pass_rate:.1%})",
        f"Failed:       {report.failed_tests}",
        f"",
        f"{'─'*60}",
        f"RETRIEVAL METRICS",
        f"{'─'*60}",
        f"Avg Precision@K:  {report.avg_precision:.4f}",
        f"Avg Recall@K:     {report.avg_recall:.4f}",
        f"Avg F1:           {f1_score(report.avg_precision, report.avg_recall):.4f}",
        f"Avg MRR:          {report.avg_mrr:.4f}",
        f"Avg NDCG:         {report.avg_ndcg:.4f}",
        f"",
        f"ANSWER METRICS",
        f"{'─'*60}",
        f"Avg Match Score:  {report.avg_answer_match:.4f}",
        f"",
    ]

    if report.metrics_by_category:
        summary_lines.append(f"BY CATEGORY")
        summary_lines.append(f"{'─'*60}")
        for cat, m in report.metrics_by_category.items():
            summary_lines.append(
                f"  {cat:20s}: pass={m['pass_rate']:.1%} P={m['avg_precision']:.2f} "
                f"R={m['avg_recall']:.2f} MRR={m['avg_mrr']:.2f}"
            )
        summary_lines.append("")

    if report.metrics_by_difficulty:
        summary_lines.append(f"BY DIFFICULTY")
        summary_lines.append(f"{'─'*60}")
        for diff, m in report.metrics_by_difficulty.items():
            summary_lines.append(
                f"  {diff:20s}: pass={m['pass_rate']:.1%} P={m['avg_precision']:.2f} "
                f"R={m['avg_recall']:.2f} MRR={m['avg_mrr']:.2f}"
            )
        summary_lines.append("")

    summary_lines.append(f"RECOMMENDATIONS")
    summary_lines.append(f"{'─'*60}")
    for rec in report.recommendations:
        summary_lines.append(f"  {rec}")

    # Failed tests detail
    failed = [r for r in report.test_results if not r.passed]
    if failed:
        summary_lines.append(f"\nFAILED TESTS ({len(failed)})")
        summary_lines.append(f"{'─'*60}")
        for r in failed[:20]:
            summary_lines.append(f"  ❌ {r.test_id}: {r.question[:50]}...")
            if r.error:
                summary_lines.append(f"     Error: {r.error}")
            else:
                summary_lines.append(
                    f"     P={r.precision_at_k:.2f} R={r.recall_at_k:.2f} "
                    f"MRR={r.mrr:.2f} Answer={r.answer_match:.2f}"
                )

    summary_text = "\n".join(summary_lines)
    summary_file.write_text(summary_text, encoding="utf-8")

    print(f"\n✅ Report saved:", file=sys.stderr)
    print(f"   JSON: {report_file}", file=sys.stderr)
    print(f"   Text: {summary_file}", file=sys.stderr)
    print(f"\n{summary_text}", file=sys.stderr)


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="RAG Accuracy Test Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate template test file
  python3 accuracy_test.py --generate-template --output tests.json

  # Run test (dry run — no retrieval function)
  python3 accuracy_test.py --test-file tests.json --results-dir ./results

  # Run test with custom retrieval function
  python3 accuracy_test.py --test-file tests.json --retrieval-fn my_rag:search

To integrate into a RAG system:
  from accuracy_test import RAGTestRunner, load_test_suite, RetrievalResult

  def my_search(query: str) -> list[RetrievalResult]:
      # Implement your retrieval here
      ...

  config, test_cases = load_test_suite("tests.json")
  runner = RAGTestRunner(retrieval_fn=my_search, top_k=10)
  report = runner.run_suite(test_cases)
        """,
    )
    parser.add_argument("--test-file", "-t", help="Path to test suite JSON file")
    parser.add_argument("--results-dir", "-r", default="./results", help="Directory to save results")
    parser.add_argument("--generate-template", action="store_true", help="Generate template test file")
    parser.add_argument("--output", "-o", default="tests_template.json", help="Output path for template")
    parser.add_argument("--top-k", type=int, default=10, help="Top K for retrieval evaluation")
    args = parser.parse_args()

    if args.generate_template:
        generate_template(args.output)
        return

    if not args.test_file:
        parser.print_help()
        print("\n❌ Need --test-file or --generate-template", file=sys.stderr)
        sys.exit(1)

    # Load test suite
    config, test_cases = load_test_suite(args.test_file)
    suite_name = config.get("name", "RAG Test Suite")
    top_k = config.get("retrieval_top_k", args.top_k)

    print(f"📋 Loaded {len(test_cases)} test cases from {args.test_file}", file=sys.stderr)
    print(f"   Suite: {suite_name}, Top K: {top_k}", file=sys.stderr)

    # Dry run (no retrieval function)
    print(f"\n⚠️ Running dry run (no retrieval function).", file=sys.stderr)
    print(f"   For actual testing, import RAGTestRunner and inject retrieval_fn.", file=sys.stderr)

    runner = RAGTestRunner(top_k=top_k)
    report = runner.run_suite(test_cases, suite_name=suite_name)

    # Save results
    save_report(report, args.results_dir)


if __name__ == "__main__":
    main()
