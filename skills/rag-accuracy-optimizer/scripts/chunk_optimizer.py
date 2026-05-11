#!/usr/bin/env python3
"""
Chunk Quality Optimizer — Evaluate chunk quality for RAG systems.

Input:  JSONL file, mỗi dòng: {"text": "...", "metadata": {...}}
Output: JSON report với quality scores và recommendations.

Usage:
    python3 chunk_optimizer.py --input chunks.jsonl --output report.json
    python3 chunk_optimizer.py --input chunks.jsonl  # stdout
"""

import argparse
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ChunkScore:
    """Quality score for a single chunk."""
    chunk_index: int
    text_preview: str
    token_estimate: int
    size_score: float        # 0-1: is chunk size optimal
    density_score: float     # 0-1: information density
    coherence_score: float   # 0-1: is content coherent
    metadata_score: float    # 0-1: is metadata complete
    overlap_score: float     # 0-1: overlap with adjacent chunk
    overall_score: float     # Weighted average
    issues: list[str]        # List of detected issues


@dataclass
class QualityReport:
    """Aggregate report for all chunks."""
    total_chunks: int
    avg_score: float
    min_score: float
    max_score: float
    avg_token_count: int
    median_token_count: int
    size_distribution: dict
    issues_summary: dict
    recommendations: list[str]
    chunk_scores: list[ChunkScore]


def estimate_tokens(text: str) -> int:
    """Estimate token count (without tiktoken)."""
    # Heuristic: ~4 chars per token for English, ~2-3 for Vietnamese
    words = text.split()
    chars = len(text)
    # Blend word-based and char-based estimation
    return max(1, int((len(words) * 1.3 + chars / 4) / 2))


def score_chunk_size(token_count: int) -> tuple[float, list[str]]:
    """
    Evaluate chunk size. Optimal: 256-512 tokens.
    Returns: (score, issues)
    """
    issues = []
    if token_count < 50:
        issues.append(f"Chunk too small ({token_count} tokens) — lacking context")
        return 0.2, issues
    elif token_count < 128:
        issues.append(f"Small chunk ({token_count} tokens) — có thể lacking context")
        return 0.5, issues
    elif token_count <= 256:
        return 0.8, issues
    elif token_count <= 512:
        return 1.0, issues  # Optimal
    elif token_count <= 1024:
        return 0.7, issues
    else:
        issues.append(f"Chunk too large ({token_count} tokens) — too much noise")
        return 0.3, issues


def score_density(text: str) -> tuple[float, list[str]]:
    """
    Evaluate information density.
    Penalize: too much whitespace, repetition, boilerplate.
    """
    issues = []
    if not text.strip():
        return 0.0, ["Empty chunk"]

    # Content vs whitespace ratio
    content_ratio = len(text.strip()) / max(len(text), 1)

    # Check repetition (many similar sentences)
    sentences = [s.strip() for s in re.split(r'[.!?\n]', text) if s.strip()]
    unique_sentences = set(sentences)
    repetition_ratio = len(unique_sentences) / max(len(sentences), 1)

    # Check boilerplate patterns
    boilerplate_patterns = [
        r"(?i)(copyright|all rights reserved|disclaimer)",
        r"(?i)(page \d+ of \d+|trang \d+)",
        r"(?i)(table of contents|mục lục)",
        r"^[\s\-=_*]{10,}$",  # Separator lines
    ]
    boilerplate_count = sum(
        1 for p in boilerplate_patterns if re.search(p, text, re.MULTILINE)
    )

    # Check meaningful word ratio
    words = text.split()
    stopwords_vi = {"và", "của", "là", "cho", "các", "được", "trong", "có", "này", "đã", "với", "để", "từ"}
    stopwords_en = {"the", "is", "at", "which", "on", "a", "an", "and", "or", "but", "in", "to", "for"}
    stopwords = stopwords_vi | stopwords_en
    meaningful = [w for w in words if w.lower() not in stopwords and len(w) > 1]
    meaningful_ratio = len(meaningful) / max(len(words), 1)

    score = (
        content_ratio * 0.2 +
        repetition_ratio * 0.3 +
        max(0, 1 - boilerplate_count * 0.25) * 0.2 +
        meaningful_ratio * 0.3
    )

    if content_ratio < 0.5:
        issues.append("Too much whitespace")
    if repetition_ratio < 0.7:
        issues.append("Many repeated sentences")
    if boilerplate_count > 0:
        issues.append(f"Chứa {boilerplate_count} boilerplate patterns")

    return min(1.0, score), issues


def score_coherence(text: str) -> tuple[float, list[str]]:
    """
    Evaluate coherence — is the content logically consistent?
    Heuristic-based (no LLM needed).
    """
    issues = []
    sentences = [s.strip() for s in re.split(r'[.!?\n]', text) if len(s.strip()) > 10]

    if len(sentences) < 2:
        return 0.7, []  # Too short to evaluate coherence

    # Check: does the first sentence appear cut mid-sentence (starts lowercase)
    first_sentence = text.strip()
    if first_sentence and first_sentence[0].islower() and not first_sentence.startswith("http"):
        issues.append("Chunk may be cut mid-sentence (starts with lowercase)")
        starts_mid = 0.8
    else:
        starts_mid = 1.0

    # Check: is the last sentence cut off
    ends_complete = 1.0
    last_char = text.rstrip()[-1] if text.rstrip() else ""
    if last_char and last_char not in ".!?:;。」』\n" and len(text) > 200:
        issues.append("Chunk may be cut mid-sentence (does not end with punctuation)")
        ends_complete = 0.8

    # Vocabulary overlap between sentences (topic consistency)
    if len(sentences) >= 2:
        word_sets = [set(s.lower().split()) for s in sentences]
        overlaps = []
        for i in range(len(word_sets) - 1):
            intersection = word_sets[i] & word_sets[i + 1]
            union = word_sets[i] | word_sets[i + 1]
            if union:
                overlaps.append(len(intersection) / len(union))
        avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
        topic_score = min(1.0, avg_overlap * 5)  # Scale up
    else:
        topic_score = 0.7

    score = starts_mid * 0.3 + ends_complete * 0.3 + topic_score * 0.4
    return score, issues


def score_metadata(metadata: dict) -> tuple[float, list[str]]:
    """Evaluate metadata completeness."""
    issues = []
    essential_keys = {"source", "chunk_index"}
    recommended_keys = {"domain", "category", "section", "created_at"}
    enrichment_keys = {"summary", "keywords", "hypothetical_questions", "entities"}

    present = set(metadata.keys())

    # Essential (weight: 0.4)
    essential_present = essential_keys & present
    essential_score = len(essential_present) / max(len(essential_keys), 1)
    if essential_score < 1.0:
        missing = essential_keys - present
        issues.append(f"Missing essential metadata: {', '.join(missing)}")

    # Recommended (weight: 0.3)
    recommended_present = recommended_keys & present
    recommended_score = len(recommended_present) / max(len(recommended_keys), 1)

    # Enrichment (weight: 0.3)
    enrichment_present = enrichment_keys & present
    enrichment_score = len(enrichment_present) / max(len(enrichment_keys), 1)
    if enrichment_score == 0:
        issues.append("No metadata enrichment yet (summary, keywords, questions)")

    score = essential_score * 0.4 + recommended_score * 0.3 + enrichment_score * 0.3
    return score, issues


def detect_overlap(chunks: list[dict]) -> list[float]:
    """Detect overlap between adjacent chunks."""
    overlap_scores = []
    for i in range(len(chunks)):
        if i == 0:
            overlap_scores.append(0.7)  # First chunk, neutral
            continue

        prev_text = chunks[i - 1]["text"]
        curr_text = chunks[i]["text"]

        # Check overlap: does the end of prev appear at the start of curr
        prev_suffix = prev_text[-200:] if len(prev_text) > 200 else prev_text
        curr_prefix = curr_text[:200] if len(curr_text) > 200 else curr_text

        # Find longest common substring
        max_overlap_len = 0
        for length in range(min(len(prev_suffix), len(curr_prefix)), 10, -1):
            if prev_suffix[-length:] == curr_prefix[:length]:
                max_overlap_len = length
                break

        overlap_pct = max_overlap_len / max(len(curr_text), 1)

        if 0.05 <= overlap_pct <= 0.25:
            score = 1.0  # Good overlap range (5-25%)
        elif overlap_pct == 0:
            score = 0.5  # No overlap
        elif overlap_pct > 0.25:
            score = 0.4  # Too much overlap
        else:
            score = 0.7

        overlap_scores.append(score)

    return overlap_scores


def analyze_chunks(chunks: list[dict]) -> QualityReport:
    """Analyze quality of all chunks."""
    if not chunks:
        return QualityReport(
            total_chunks=0, avg_score=0, min_score=0, max_score=0,
            avg_token_count=0, median_token_count=0,
            size_distribution={}, issues_summary={},
            recommendations=["No chunks to analyze."],
            chunk_scores=[],
        )

    overlap_scores = detect_overlap(chunks)
    chunk_scores = []
    all_issues = Counter()
    token_counts = []
    size_buckets = {"tiny(<128)": 0, "small(128-256)": 0, "optimal(256-512)": 0,
                    "large(512-1024)": 0, "huge(>1024)": 0}

    for i, chunk in enumerate(chunks):
        text = chunk.get("text", "")
        metadata = chunk.get("metadata", {})
        tokens = estimate_tokens(text)
        token_counts.append(tokens)

        # Categorize size
        if tokens < 128:
            size_buckets["tiny(<128)"] += 1
        elif tokens < 256:
            size_buckets["small(128-256)"] += 1
        elif tokens <= 512:
            size_buckets["optimal(256-512)"] += 1
        elif tokens <= 1024:
            size_buckets["large(512-1024)"] += 1
        else:
            size_buckets["huge(>1024)"] += 1

        # Score components
        size_s, size_issues = score_chunk_size(tokens)
        density_s, density_issues = score_density(text)
        coherence_s, coherence_issues = score_coherence(text)
        metadata_s, metadata_issues = score_metadata(metadata)
        overlap_s = overlap_scores[i]

        all_chunk_issues = size_issues + density_issues + coherence_issues + metadata_issues
        for issue in all_chunk_issues:
            all_issues[issue] += 1

        overall = (
            size_s * 0.25 +
            density_s * 0.20 +
            coherence_s * 0.20 +
            metadata_s * 0.20 +
            overlap_s * 0.15
        )

        chunk_scores.append(ChunkScore(
            chunk_index=i,
            text_preview=text[:100] + "..." if len(text) > 100 else text,
            token_estimate=tokens,
            size_score=round(size_s, 3),
            density_score=round(density_s, 3),
            coherence_score=round(coherence_s, 3),
            metadata_score=round(metadata_s, 3),
            overlap_score=round(overlap_s, 3),
            overall_score=round(overall, 3),
            issues=all_chunk_issues,
        ))

    scores = [cs.overall_score for cs in chunk_scores]
    sorted_tokens = sorted(token_counts)
    median_tokens = sorted_tokens[len(sorted_tokens) // 2]

    # Generate recommendations
    recommendations = []
    avg = sum(scores) / len(scores)

    if avg < 0.6:
        recommendations.append("⚠️ Low chunk quality. Review chunking strategy.")

    if size_buckets["tiny(<128)"] > len(chunks) * 0.2:
        recommendations.append("📏 >20% chunks too small (<128 tokens). Consider merging small chunks.")

    if size_buckets["huge(>1024)"] > len(chunks) * 0.1:
        recommendations.append("📏 >10% chunks too large (>1024 tokens). Consider splitting further.")

    no_metadata_count = sum(1 for cs in chunk_scores if cs.metadata_score < 0.4)
    if no_metadata_count > len(chunks) * 0.5:
        recommendations.append("🏷️ >50% chunks missing metadata. Add source, domain, category.")

    no_enrichment = all_issues.get("No metadata enrichment yet (summary, keywords, questions)", 0)
    if no_enrichment > len(chunks) * 0.8:
        recommendations.append("✨ >80% chunks not enriched. Run metadata enrichment (LLM-generated summary, keywords, questions).")

    mid_cut = all_issues.get("Chunk may be cut mid-sentence (starts with lowercase)", 0)
    if mid_cut > len(chunks) * 0.15:
        recommendations.append("✂️ >15% chunks cut mid-sentence. Use sentence-boundary splitting.")

    overlap_low = sum(1 for s in overlap_scores if s == 0.5)
    if overlap_low > len(chunks) * 0.7:
        recommendations.append("🔗 >70% chunks have no overlap. Add 10-20% overlap between chunks.")

    if not recommendations:
        recommendations.append("✅ Overall chunk quality is good!")

    return QualityReport(
        total_chunks=len(chunks),
        avg_score=round(avg, 3),
        min_score=round(min(scores), 3),
        max_score=round(max(scores), 3),
        avg_token_count=int(sum(token_counts) / len(token_counts)),
        median_token_count=median_tokens,
        size_distribution=size_buckets,
        issues_summary=dict(all_issues.most_common(10)),
        recommendations=recommendations,
        chunk_scores=chunk_scores,
    )


def load_chunks(file_path: str) -> list[dict]:
    """Load chunks from JSONL or JSON file."""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    chunks = []
    content = path.read_text(encoding="utf-8")

    # Try JSONL first
    try:
        for line_num, line in enumerate(content.strip().split("\n"), 1):
            line = line.strip()
            if not line:
                continue
            try:
                chunk = json.loads(line)
                if "text" not in chunk:
                    print(f"⚠️ Dòng {line_num}: missing 'text' field, skipping", file=sys.stderr)
                    continue
                chunks.append(chunk)
            except json.JSONDecodeError:
                # Có thể là JSON array, thử parse toàn bộ
                break

        if chunks:
            return chunks
    except Exception:
        pass

    # Try JSON array
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return [c for c in data if "text" in c]
        elif isinstance(data, dict) and "chunks" in data:
            return [c for c in data["chunks"] if "text" in c]
    except json.JSONDecodeError:
        pass

    print(f"❌ Cannot parse file: {file_path}. Supports JSONL or JSON array.", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate chunk quality for RAG systems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python3 chunk_optimizer.py --input chunks.jsonl --output report.json
  python3 chunk_optimizer.py --input chunks.jsonl  # in ra stdout

Input format (JSONL):
  {"text": "Chunk 1 content", "metadata": {"source": "doc.pdf", "chunk_index": 0}}
  {"text": "Chunk 2 content", "metadata": {"source": "doc.pdf", "chunk_index": 1}}
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to JSONL/JSON file containing chunks")
    parser.add_argument("--output", "-o", help="Output report path (JSON). Default: stdout")
    parser.add_argument("--top-issues", type=int, default=5, help="Number of lowest-scoring chunks to highlight")
    args = parser.parse_args()

    # Load chunks
    chunks = load_chunks(args.input)
    print(f"📊 Loaded {len(chunks)} chunks from {args.input}", file=sys.stderr)

    # Analyze
    report = analyze_chunks(chunks)

    # Output
    report_dict = asdict(report)

    # Highlight worst chunks
    worst = sorted(report.chunk_scores, key=lambda x: x.overall_score)[:args.top_issues]
    report_dict["worst_chunks"] = [asdict(cs) for cs in worst]

    output_json = json.dumps(report_dict, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output_json, encoding="utf-8")
        print(f"✅ Report saved: {args.output}", file=sys.stderr)
    else:
        print(output_json)

    # Summary to stderr
    print(f"\n{'='*50}", file=sys.stderr)
    print(f"📈 CHUNK QUALITY REPORT", file=sys.stderr)
    print(f"{'='*50}", file=sys.stderr)
    print(f"Total chunks:       {report.total_chunks}", file=sys.stderr)
    print(f"Average score:      {report.avg_score:.3f}", file=sys.stderr)
    print(f"Min/Max score:      {report.min_score:.3f} / {report.max_score:.3f}", file=sys.stderr)
    print(f"Avg tokens:         {report.avg_token_count}", file=sys.stderr)
    print(f"Median tokens:      {report.median_token_count}", file=sys.stderr)
    print(f"\nSize distribution:", file=sys.stderr)
    for bucket, count in report.size_distribution.items():
        pct = count / report.total_chunks * 100 if report.total_chunks > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"  {bucket:20s}: {count:4d} ({pct:5.1f}%) {bar}", file=sys.stderr)
    print(f"\n📋 Recommendations:", file=sys.stderr)
    for rec in report.recommendations:
        print(f"  {rec}", file=sys.stderr)


if __name__ == "__main__":
    main()
