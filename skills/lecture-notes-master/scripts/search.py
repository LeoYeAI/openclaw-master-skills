#!/usr/bin/env python3
"""
Lecture Notes Master - Search Engine
BM25-based search across glossary, mermaid templates, writing rules, and review questions.
Supports both English and Chinese queries.

Usage:
    python3 search.py "<query>" --domain glossary
    python3 search.py "<query>" --domain mermaid
    python3 search.py "<query>" --domain writing
    python3 search.py "<query>" --domain questions
    python3 search.py "<query>"                      # auto-detect domain
"""

import csv
import math
import os
import sys
import argparse
import json
import unicodedata
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

# Domain configuration: maps domain name to (csv_file, search_columns, display_columns)
DOMAIN_CONFIG = {
    "glossary": {
        "file": "glossary.csv",
        "search_cols": [
            "English_Term",
            "Chinese_Term",
            "Category",
            "Definition",
            "Related_Courses",
            "Aliases",
        ],
        "display_cols": [
            "No",
            "English_Term",
            "Chinese_Term",
            "Category",
            "Definition",
            "Related_Courses",
        ],
        "title": "Glossary (术语库)",
    },
    "mermaid": {
        "file": "mermaid-templates.csv",
        "search_cols": ["Diagram_Type", "Use_Case", "Best_For", "Keywords"],
        "display_cols": ["No", "Diagram_Type", "Use_Case", "Template_Code", "Best_For"],
        "title": "Mermaid Templates (图表模板)",
    },
    "writing": {
        "file": "writing-rules.csv",
        "search_cols": [
            "Rule_Name",
            "Category",
            "Description",
            "When_To_Apply",
            "Priority",
        ],
        "display_cols": [
            "No",
            "Rule_Name",
            "Priority",
            "Category",
            "Description",
            "Example_Good",
        ],
        "title": "Writing Rules (写作规则)",
    },
    "questions": {
        "file": "review-questions.csv",
        "search_cols": [
            "Question_Type",
            "Level",
            "Template",
            "Example_Topic",
            "Keywords",
            "Bloom_Level",
        ],
        "display_cols": [
            "No",
            "Question_Type",
            "Level",
            "Template",
            "Example_Question",
        ],
        "title": "Review Questions (复习题模板)",
    },
}

# Keywords for auto-detection
DOMAIN_KEYWORDS = {
    "glossary": [
        "term",
        "define",
        "meaning",
        "what is",
        "glossary",
        "bilingual",
        "translate",
        "cuda",
        "gpu",
        "memory",
        "cache",
        "thread",
        "warp",
        "kernel",
        "fpga",
        "neural",
        "algorithm",
        "architecture",
        "optimization",
        "pipeline",
        "bandwidth",
        "术语",
        "定义",
        "含义",
        "翻译",
        "词汇",
    ],
    "mermaid": [
        "diagram",
        "chart",
        "flow",
        "graph",
        "visual",
        "mermaid",
        "sequence",
        "state",
        "class",
        "gantt",
        "pie",
        "timeline",
        "hierarchy",
        "architecture",
        "mindmap",
        "process",
        "pipeline",
        "comparison",
        "before after",
        "图表",
        "流程图",
        "架构图",
        "时序图",
        "可视化",
    ],
    "writing": [
        "style",
        "rule",
        "how to write",
        "format",
        "structure",
        "template",
        "guideline",
        "example",
        "introduction",
        "comparison",
        "code",
        "annotation",
        "bilingual",
        "yaml",
        "frontmatter",
        "link",
        "heading",
        "规则",
        "格式",
        "写作",
        "风格",
        "模板",
    ],
    "questions": [
        "question",
        "quiz",
        "exam",
        "review",
        "test",
        "recall",
        "understanding",
        "application",
        "analysis",
        "calculate",
        "design",
        "compare",
        "evaluate",
        "bloom",
        "exercise",
        "practice",
        "问题",
        "考试",
        "复习",
        "测试",
        "练习",
    ],
}


def _is_cjk(char):
    """Check if a character is CJK (Chinese, Japanese, Korean)."""
    cp = ord(char)
    # CJK Unified Ideographs
    if 0x4E00 <= cp <= 0x9FFF:
        return True
    # CJK Extension A
    if 0x3400 <= cp <= 0x4DBF:
        return True
    # CJK Extension B
    if 0x20000 <= cp <= 0x2A6DF:
        return True
    # CJK Compatibility Ideographs
    if 0xF900 <= cp <= 0xFAFF:
        return True
    return False


class BM25:
    """BM25 ranking algorithm for text search with CJK support."""

    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.doc_len = []
        self.avg_dl = 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_count = 0
        self.corpus = []

    @staticmethod
    def tokenize(text):
        """Tokenizer with CJK bigram support.

        For Latin text: split on non-alphanumeric, lowercase.
        For CJK text: emit individual characters AND bigrams for better matching.
        """
        if not text:
            return []

        text = text.lower()
        tokens = []
        current_latin = []
        cjk_buffer = []

        def flush_latin():
            if current_latin:
                tokens.append("".join(current_latin))
                current_latin.clear()

        def flush_cjk():
            # Emit individual CJK characters
            for ch in cjk_buffer:
                tokens.append(ch)
            # Emit bigrams for better phrase matching
            for i in range(len(cjk_buffer) - 1):
                tokens.append(cjk_buffer[i] + cjk_buffer[i + 1])
            cjk_buffer.clear()

        for ch in text:
            if _is_cjk(ch):
                flush_latin()
                cjk_buffer.append(ch)
            elif ch.isalnum() or ch in "-_":
                flush_cjk()
                current_latin.append(ch)
            else:
                flush_latin()
                flush_cjk()

        flush_latin()
        flush_cjk()

        return tokens

    def fit(self, corpus):
        """Build BM25 index from corpus (list of strings)."""
        self.corpus = corpus
        self.doc_count = len(corpus)
        self.doc_len = []
        self.doc_freqs = []

        df = Counter()

        for doc in corpus:
            tokens = self.tokenize(doc)
            self.doc_len.append(len(tokens))
            freq = Counter(tokens)
            self.doc_freqs.append(freq)
            for token in set(tokens):
                df[token] += 1

        self.avg_dl = sum(self.doc_len) / self.doc_count if self.doc_count > 0 else 0

        # Calculate IDF
        self.idf = {}
        for token, freq in df.items():
            self.idf[token] = math.log((self.doc_count - freq + 0.5) / (freq + 0.5) + 1)

    def score(self, query):
        """Score all documents against query. Returns list of (index, score)."""
        query_tokens = self.tokenize(query)
        scores = []

        for i in range(self.doc_count):
            s = 0
            dl = self.doc_len[i]
            freq = self.doc_freqs[i]

            for token in query_tokens:
                if token not in self.idf:
                    continue
                tf = freq.get(token, 0)
                idf = self.idf[token]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * dl / self.avg_dl)
                s += idf * numerator / denominator

            scores.append((i, s))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


def detect_domain(query):
    """Auto-detect the best domain based on query keywords."""
    query_lower = query.lower()
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        scores[domain] = score

    best = max(scores.keys(), key=lambda k: scores[k])
    if scores[best] == 0:
        return "glossary"  # Default fallback
    return best


def load_csv(domain):
    """Load CSV data for a domain."""
    config = DOMAIN_CONFIG[domain]
    filepath = os.path.join(DATA_DIR, config["file"])

    if not os.path.exists(filepath):
        print(f"Error: Data file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def search(query, domain, max_results=10):
    """Search a domain using BM25."""
    config = DOMAIN_CONFIG[domain]
    rows = load_csv(domain)

    # Build corpus from search columns
    corpus = []
    for row in rows:
        doc = " ".join(row.get(col, "") for col in config["search_cols"])
        corpus.append(doc)

    # Run BM25
    bm25 = BM25()
    bm25.fit(corpus)
    scores = bm25.score(query)

    # Filter results with score > 0
    results = []
    for idx, score in scores:
        if score > 0 and len(results) < max_results:
            result = {col: rows[idx].get(col, "") for col in config["display_cols"]}
            result["_score"] = round(score, 3)
            results.append(result)

    return results


def format_results(results, domain, query, output_format="markdown"):
    """Format search results."""
    config = DOMAIN_CONFIG[domain]
    title = config["title"]

    if not results:
        return f"No results found for '{query}' in {title}"

    lines = []
    lines.append(f"## {title} - Search Results")
    lines.append(f"**Query**: {query} | **Results**: {len(results)}")
    lines.append("")

    if domain == "glossary":
        lines.append("| # | English Term | Chinese Term | Category | Definition |")
        lines.append("|---|-------------|-------------|----------|------------|")
        for r in results:
            lines.append(
                f"| {r.get('No', '')} | **{r.get('English_Term', '')}** | {r.get('Chinese_Term', '')} | {r.get('Category', '')} | {r.get('Definition', '')[:80]}... |"
            )

    elif domain == "mermaid":
        for r in results:
            lines.append(f"### {r.get('Diagram_Type', '')} - {r.get('Use_Case', '')}")
            lines.append(f"**Best For**: {r.get('Best_For', '')}")
            lines.append("")
            lines.append("```mermaid")
            lines.append(r.get("Template_Code", ""))
            lines.append("```")
            lines.append("")

    elif domain == "writing":
        for r in results:
            priority = r.get("Priority", "")
            badge = (
                "🔴" if priority == "CRITICAL" else "🟡" if priority == "HIGH" else "🔵"
            )
            lines.append(f"### {badge} {r.get('Rule_Name', '')} [{priority}]")
            lines.append(f"{r.get('Description', '')}")
            lines.append("")
            good = r.get("Example_Good", "")
            if good:
                lines.append(f"**Good Example**: {good[:150]}")
            lines.append("")

    elif domain == "questions":
        lines.append("| # | Type | Level | Template | Example |")
        lines.append("|---|------|-------|----------|---------|")
        for r in results:
            lines.append(
                f"| {r.get('No', '')} | {r.get('Question_Type', '')} | {r.get('Level', '')} | {r.get('Template', '')[:50]} | {r.get('Example_Question', '')[:60]} |"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Lecture Notes Master - Search Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 search.py "shared memory cuda" --domain glossary
  python3 search.py "hierarchy architecture" --domain mermaid
  python3 search.py "how to write introduction" --domain writing
  python3 search.py "exam calculation" --domain questions
  python3 search.py "内存优化"  # auto-detect, Chinese supported
  python3 search.py "memory optimization"  # auto-detect domain
        """,
    )
    parser.add_argument("query", help="Search query (English or Chinese)")
    parser.add_argument(
        "--domain",
        "-d",
        choices=list(DOMAIN_CONFIG.keys()),
        help="Domain to search (auto-detected if not specified)",
    )
    parser.add_argument(
        "-n",
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    args = parser.parse_args()

    # Auto-detect domain if not specified
    domain = args.domain or detect_domain(args.query)

    results = search(args.query, domain, args.max_results)

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        output = format_results(results, domain, args.query)
        print(output)


if __name__ == "__main__":
    # Ensure UTF-8 output on all platforms
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
