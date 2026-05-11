#!/usr/bin/env python3
"""
Embedding Model Benchmark — Test embedding models on a Vietnamese dataset.

Usage:
    python embedding_benchmark.py --models bge-m3,multilingual-e5 --dataset vi_pairs.json
    python embedding_benchmark.py --models all --quick

Input dataset format (vi_pairs.json):
{
    "pairs": [
        {
            "query": "Bảo hiểm nhân thọ có chi trả khi tự tử không?",
            "positive": "Điều khoản loại trừ: tự tử trong 2 năm đầu không được chi trả.",
            "negative": "Phí bảo hiểm được tính theo tuổi và sức khỏe người mua."
        }
    ]
}

Output: Benchmark report with accuracy, latency, and recommendations.

Requirements:
    pip install sentence-transformers numpy torch
    # For OpenAI/Cohere: pip install openai cohere
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# Default Vietnamese test pairs (built-in for quick testing)
DEFAULT_VI_PAIRS = [
    {
        "query": "Bảo hiểm nhân thọ có chi trả khi tự tử không?",
        "positive": "Điều khoản loại trừ: Trường hợp tự tử trong vòng 2 năm kể từ ngày hợp đồng có hiệu lực sẽ không được chi trả quyền lợi bảo hiểm.",
        "negative": "Phí bảo hiểm nhân thọ được tính dựa trên độ tuổi, giới tính và tình trạng sức khỏe của người được bảo hiểm.",
    },
    {
        "query": "Lãi suất tiết kiệm ngân hàng nào cao nhất?",
        "positive": "So sánh lãi suất tiết kiệm kỳ hạn 12 tháng: Techcombank 5.6%, VPBank 5.8%, MB 5.5%, ACB 5.4%.",
        "negative": "Ngân hàng cung cấp dịch vụ chuyển tiền quốc tế với phí từ 0.1% đến 0.3% giá trị giao dịch.",
    },
    {
        "query": "Điều kiện hưởng bảo hiểm xã hội một lần?",
        "positive": "Người lao động được hưởng BHXH một lần khi đủ tuổi nghỉ hưu mà chưa đủ 20 năm đóng BHXH, hoặc ra nước ngoài định cư.",
        "negative": "Bảo hiểm xã hội là chính sách an sinh xã hội quan trọng của Nhà nước Việt Nam.",
    },
    {
        "query": "Cổ phiếu VNM có nên mua không?",
        "positive": "VNM (Vinamilk): P/E 18.5, ROE 32%, doanh thu Q3/2024 tăng 8% YoY, biên lợi nhuận gộp 42%. Consensus: mua với giá mục tiêu 85,000 VNĐ.",
        "negative": "Thị trường chứng khoán Việt Nam có 3 sàn giao dịch: HoSE, HNX và UPCOM.",
    },
    {
        "query": "Quyền lợi nằm viện gói bảo hiểm sức khỏe",
        "positive": "Quyền lợi nằm viện bao gồm: chi phí giường bệnh tối đa 2 triệu/ngày, phẫu thuật tối đa 100 triệu/lần, thuốc và xét nghiệm theo thực tế.",
        "negative": "Khách hàng có thể mua bảo hiểm sức khỏe online qua ứng dụng di động hoặc website công ty.",
    },
    {
        "query": "Thủ tục đăng ký bảo hiểm y tế hộ gia đình",
        "positive": "Đăng ký BHYT hộ gia đình: nộp đơn tại UBND xã/phường kèm sổ hộ khẩu/CCCD. Mức đóng: 4.5% lương cơ sở, giảm 30% cho thành viên thứ 2.",
        "negative": "Bảo hiểm y tế được quản lý bởi cơ quan BHXH Việt Nam, thành lập năm 1995.",
    },
    {
        "query": "Luật lao động quy định về giờ làm thêm",
        "positive": "Theo BLLĐ 2019, giờ làm thêm tối đa 40h/tháng và 200h/năm (300h cho ngành đặc biệt). Tiền lương làm thêm: ngày thường 150%, ngày nghỉ 200%, ngày lễ 300%.",
        "negative": "Bộ luật Lao động 2019 có hiệu lực từ ngày 01/01/2021, thay thế BLLĐ 2012.",
    },
    {
        "query": "Chế độ thai sản cho lao động nữ",
        "positive": "Lao động nữ được nghỉ thai sản 6 tháng, hưởng 100% mức bình quân tiền lương đóng BHXH 6 tháng trước khi nghỉ. Trợ cấp 1 lần: 2 tháng lương cơ sở.",
        "negative": "Tỷ lệ sinh tại Việt Nam năm 2023 là 1.96 con/phụ nữ, giảm so với 2.09 năm 2020.",
    },
]


@dataclass
class BenchmarkResult:
    model_name: str
    accuracy: float  # % correct (positive > negative)
    avg_latency_ms: float
    total_pairs: int
    correct: int
    errors: list = field(default_factory=list)
    details: list = field(default_factory=list)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class EmbeddingModel:
    """Base class for embedding models."""

    def __init__(self, name: str):
        self.name = name

    def encode(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError


class SentenceTransformerModel(EmbeddingModel):
    def __init__(self, name: str, model_id: str):
        super().__init__(name)
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_id)

    def encode(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)


class OpenAIModel(EmbeddingModel):
    def __init__(self, name: str, model_id: str):
        super().__init__(name)
        from openai import OpenAI

        self.client = OpenAI()
        self.model_id = model_id

    def encode(self, texts: list[str]) -> np.ndarray:
        response = self.client.embeddings.create(model=self.model_id, input=texts)
        return np.array([d.embedding for d in response.data])


class CohereModel(EmbeddingModel):
    def __init__(self, name: str, model_id: str):
        super().__init__(name)
        import cohere

        self.client = cohere.Client()
        self.model_id = model_id

    def encode(self, texts: list[str]) -> np.ndarray:
        response = self.client.embed(
            texts=texts,
            model=self.model_id,
            input_type="search_query",
        )
        return np.array(response.embeddings)


# Available models registry
MODEL_REGISTRY = {
    "bge-m3": lambda: SentenceTransformerModel("BGE-M3", "BAAI/bge-m3"),
    "multilingual-e5": lambda: SentenceTransformerModel(
        "multilingual-e5-large", "intfloat/multilingual-e5-large"
    ),
    "e5-large-v2": lambda: SentenceTransformerModel(
        "E5-large-v2", "intfloat/e5-large-v2"
    ),
    "minilm": lambda: SentenceTransformerModel(
        "all-MiniLM-L6-v2", "sentence-transformers/all-MiniLM-L6-v2"
    ),
    "openai-small": lambda: OpenAIModel(
        "OpenAI-3-small", "text-embedding-3-small"
    ),
    "openai-large": lambda: OpenAIModel(
        "OpenAI-3-large", "text-embedding-3-large"
    ),
    "cohere": lambda: CohereModel("Cohere-embed-v3", "embed-multilingual-v3.0"),
}


def benchmark_model(
    model: EmbeddingModel, pairs: list[dict]
) -> BenchmarkResult:
    """Benchmark a single embedding model on query-positive-negative pairs."""
    correct = 0
    total = len(pairs)
    latencies = []
    details = []
    errors = []

    for i, pair in enumerate(pairs):
        try:
            texts = [pair["query"], pair["positive"], pair["negative"]]

            start = time.perf_counter()
            embeddings = model.encode(texts)
            elapsed_ms = (time.perf_counter() - start) * 1000

            latencies.append(elapsed_ms)

            sim_pos = cosine_similarity(embeddings[0], embeddings[1])
            sim_neg = cosine_similarity(embeddings[0], embeddings[2])
            is_correct = sim_pos > sim_neg

            if is_correct:
                correct += 1

            details.append(
                {
                    "index": i,
                    "query": pair["query"][:80],
                    "sim_positive": round(sim_pos, 4),
                    "sim_negative": round(sim_neg, 4),
                    "margin": round(sim_pos - sim_neg, 4),
                    "correct": is_correct,
                }
            )
        except Exception as e:
            errors.append({"index": i, "error": str(e)})

    return BenchmarkResult(
        model_name=model.name,
        accuracy=correct / total if total > 0 else 0,
        avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
        total_pairs=total,
        correct=correct,
        errors=errors,
        details=details,
    )


def print_results(results: list[BenchmarkResult]):
    """Print formatted benchmark results."""
    print("\n" + "=" * 70)
    print("📊 Embedding Model Benchmark Results (Vietnamese)")
    print("=" * 70)

    # Sort by accuracy
    results.sort(key=lambda r: r.accuracy, reverse=True)

    print(f"\n{'Model':<25} {'Accuracy':>10} {'Latency':>12} {'Correct':>10}")
    print("-" * 60)

    for r in results:
        acc_str = f"{r.accuracy:.1%}"
        lat_str = f"{r.avg_latency_ms:.1f}ms"
        cor_str = f"{r.correct}/{r.total_pairs}"
        print(f"  {r.model_name:<23} {acc_str:>10} {lat_str:>12} {cor_str:>10}")

    # Recommendation
    best = results[0]
    print(f"\n🏆 Best: {best.model_name} (accuracy: {best.accuracy:.1%})")

    # Show failed cases for best model
    failed = [d for d in best.details if not d["correct"]]
    if failed:
        print(f"\n⚠️  {best.model_name} failed on:")
        for f in failed:
            print(f"   - [{f['index']}] {f['query']}... (margin: {f['margin']:.4f})")


def main():
    parser = argparse.ArgumentParser(description="Embedding Model Benchmark (Vietnamese)")
    parser.add_argument(
        "--models",
        default="minilm,multilingual-e5",
        help=f"Comma-separated model names or 'all'. Available: {','.join(MODEL_REGISTRY.keys())}",
    )
    parser.add_argument("--dataset", default=None, help="Path to custom dataset JSON")
    parser.add_argument("--quick", action="store_true", help="Use built-in Vietnamese test pairs")
    parser.add_argument("--output", default="benchmark_results.json", help="Output file path")
    args = parser.parse_args()

    # Load dataset
    if args.dataset:
        with open(args.dataset) as f:
            data = json.load(f)
        pairs = data.get("pairs", data.get("test_pairs", []))
    else:
        pairs = DEFAULT_VI_PAIRS
        print("📝 Using built-in Vietnamese test pairs")

    print(f"📊 Test pairs: {len(pairs)}")

    # Select models
    if args.models == "all":
        model_names = list(MODEL_REGISTRY.keys())
    else:
        model_names = [m.strip() for m in args.models.split(",")]

    # Run benchmarks
    results = []
    for name in model_names:
        if name not in MODEL_REGISTRY:
            print(f"⚠️  Unknown model: {name}. Available: {list(MODEL_REGISTRY.keys())}")
            continue

        print(f"\n🔄 Benchmarking: {name}...")
        try:
            model = MODEL_REGISTRY[name]()
            result = benchmark_model(model, pairs)
            results.append(result)
            print(f"   ✅ {result.model_name}: accuracy={result.accuracy:.1%}, latency={result.avg_latency_ms:.1f}ms")
        except Exception as e:
            print(f"   ❌ {name} failed: {e}")

    if not results:
        print("❌ No models benchmarked successfully.")
        return 1

    # Print results
    print_results(results)

    # Save results
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "num_pairs": len(pairs),
        "results": [
            {
                "model": r.model_name,
                "accuracy": round(r.accuracy, 4),
                "avg_latency_ms": round(r.avg_latency_ms, 2),
                "correct": r.correct,
                "total": r.total_pairs,
                "details": r.details,
                "errors": r.errors,
            }
            for r in results
        ],
    }

    Path(args.output).write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\n📄 Full results saved to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
