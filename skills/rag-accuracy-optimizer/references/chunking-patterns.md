# Chunking Patterns — Python Code Examples

## Table of Contents

1. [Fixed Size Chunking](#1-fixed-size-chunking)
2. [Semantic Chunking (by Heading)](#2-semantic-chunking-theo-heading)
3. [Overlap Chunking](#3-overlap-chunking)
4. [Hierarchical Chunking (Parent-Child)](#4-hierarchical-chunking-parent-child)
5. [Domain-Specific Chunking](#5-domain-specific-chunking)
6. [Metadata Enrichment](#6-metadata-enrichment)
7. [Recursive Character Splitting (LangChain)](#7-recursive-character-splitting-langchain)

---

## 1. Fixed Size Chunking

Split by fixed token count. Simple but may cut in the middle of a sentence.

```python
import tiktoken

def fixed_size_chunk(text: str, chunk_size: int = 512, model: str = "cl100k_base") -> list[dict]:
    """Split text into fixed-size chunks by token count."""
    enc = tiktoken.get_encoding(model)
    tokens = enc.encode(text)
    chunks = []

    for i in range(0, len(tokens), chunk_size):
        chunk_tokens = tokens[i:i + chunk_size]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "chunk_index": len(chunks),
                "token_count": len(chunk_tokens),
                "char_start": len(enc.decode(tokens[:i])),
            }
        })

    return chunks

# Usage
chunks = fixed_size_chunk(long_text, chunk_size=512)
```

---

## 2. Semantic Chunking (by Heading)

Split by heading/section — preserves the semantic meaning of each section.

```python
import re

def semantic_chunk_by_heading(text: str, heading_pattern: str = r"^#{1,3}\s+.+$") -> list[dict]:
    """Split text by markdown headings."""
    lines = text.split("\n")
    chunks = []
    current_chunk = []
    current_heading = "Introduction"

    for line in lines:
        if re.match(heading_pattern, line):
            # Save previous chunk
            if current_chunk:
                chunks.append({
                    "text": "\n".join(current_chunk).strip(),
                    "metadata": {
                        "heading": current_heading,
                        "chunk_index": len(chunks),
                    }
                })
            current_heading = line.strip("# ").strip()
            current_chunk = [line]
        else:
            current_chunk.append(line)

    # Last chunk
    if current_chunk:
        chunks.append({
            "text": "\n".join(current_chunk).strip(),
            "metadata": {
                "heading": current_heading,
                "chunk_index": len(chunks),
            }
        })

    return chunks


def semantic_chunk_by_paragraph(text: str, min_size: int = 100, max_size: int = 1500) -> list[dict]:
    """Split by paragraph, merge small paragraphs together."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    buffer = []
    buffer_len = 0

    for para in paragraphs:
        para_len = len(para)

        if buffer_len + para_len > max_size and buffer:
            chunks.append({
                "text": "\n\n".join(buffer),
                "metadata": {"chunk_index": len(chunks), "char_count": buffer_len}
            })
            buffer = []
            buffer_len = 0

        buffer.append(para)
        buffer_len += para_len

    if buffer:
        chunks.append({
            "text": "\n\n".join(buffer),
            "metadata": {"chunk_index": len(chunks), "char_count": buffer_len}
        })

    return chunks
```

---

## 3. Overlap Chunking

Thêm overlap giữa các chunks để không mất context ở ranh giới.

```python
import tiktoken

def overlap_chunk(
    text: str,
    chunk_size: int = 512,
    overlap_pct: float = 0.15,
    model: str = "cl100k_base"
) -> list[dict]:
    """Split tokens with overlap between chunks."""
    enc = tiktoken.get_encoding(model)
    tokens = enc.encode(text)
    overlap = int(chunk_size * overlap_pct)
    step = chunk_size - overlap
    chunks = []

    for i in range(0, len(tokens), step):
        chunk_tokens = tokens[i:i + chunk_size]
        if not chunk_tokens:
            break

        chunks.append({
            "text": enc.decode(chunk_tokens),
            "metadata": {
                "chunk_index": len(chunks),
                "token_count": len(chunk_tokens),
                "overlap_tokens": overlap,
                "has_overlap_prev": i > 0,
                "has_overlap_next": i + chunk_size < len(tokens),
            }
        })

        if len(chunk_tokens) < chunk_size:
            break

    return chunks

# Usage: 512 tokens, 15% overlap ≈ 77 tokens overlap
chunks = overlap_chunk(text, chunk_size=512, overlap_pct=0.15)
```

---

## 4. Hierarchical Chunking (Parent-Child)

Create hierarchical structure: Document → Section → Paragraph.

```python
import uuid
import re

def hierarchical_chunk(text: str, source: str = "document") -> dict:
    """
    Create hierarchical chunks: document → sections → paragraphs.
    Returns dict with levels: document, sections, paragraphs.
    """
    doc_id = str(uuid.uuid4())[:8]

    # Level 0: Document (summary)
    document = {
        "id": doc_id,
        "text": text[:2000],  # Or use LLM summarize
        "level": "document",
        "metadata": {"source": source}
    }

    # Level 1: Sections (split by headings)
    section_pattern = r"(?=^#{1,2}\s+.+$)"
    raw_sections = re.split(section_pattern, text, flags=re.MULTILINE)
    raw_sections = [s.strip() for s in raw_sections if s.strip()]

    sections = []
    paragraphs = []

    for i, sec_text in enumerate(raw_sections):
        sec_id = f"{doc_id}_s{i}"
        lines = sec_text.split("\n", 1)
        heading = lines[0].strip("# ").strip() if lines else f"Section {i}"

        sections.append({
            "id": sec_id,
            "text": sec_text,
            "level": "section",
            "metadata": {
                "parent_id": doc_id,
                "heading": heading,
                "section_index": i,
                "source": source,
            }
        })

        # Level 2: Paragraphs
        body = lines[1] if len(lines) > 1 else sec_text
        paras = [p.strip() for p in body.split("\n\n") if p.strip() and len(p.strip()) > 50]

        for j, para in enumerate(paras):
            paragraphs.append({
                "id": f"{sec_id}_p{j}",
                "text": para,
                "level": "paragraph",
                "metadata": {
                    "parent_id": sec_id,
                    "grandparent_id": doc_id,
                    "heading": heading,
                    "paragraph_index": j,
                    "source": source,
                }
            })

    return {
        "document": document,
        "sections": sections,
        "paragraphs": paragraphs,
    }

# Usage
result = hierarchical_chunk(markdown_text, source="policy_v2.pdf")
# Search trên paragraphs, kéo parent section khi cần thêm context
```

---

## 5. Domain-Specific Chunking

### Insurance — Chunk by Clause

```python
import re

def chunk_insurance_clauses(text: str, policy_id: str = "") -> list[dict]:
    """Split insurance document by clauses."""
    # Pattern: "Điều X:" hoặc "Điều X." hoặc "Article X"
    pattern = r"(?=(?:Điều|Article|Clause)\s+\d+[.:]\s*)"
    raw_clauses = re.split(pattern, text, flags=re.IGNORECASE)
    raw_clauses = [c.strip() for c in raw_clauses if c.strip()]

    chunks = []
    for clause_text in raw_clauses:
        # Extract clause number
        match = re.match(r"(?:Điều|Article|Clause)\s+(\d+)", clause_text, re.IGNORECASE)
        clause_num = match.group(1) if match else str(len(chunks))

        # Extract title (first line after clause number)
        lines = clause_text.split("\n", 1)
        title = lines[0].strip()

        chunks.append({
            "text": clause_text,
            "metadata": {
                "policy_id": policy_id,
                "clause_number": int(clause_num),
                "title": title,
                "domain": "insurance",
                "chunk_type": "clause",
                "chunk_index": len(chunks),
            }
        })

    return chunks
```

### Finance — Chunk by Report Section

```python
def chunk_financial_report(text: str, ticker: str, period: str) -> list[dict]:
    """Split financial report by section."""
    # Common financial report sections
    section_keywords = [
        "Tổng quan", "Kết quả kinh doanh", "Bảng cân đối",
        "Lưu chuyển tiền tệ", "Thuyết minh", "Rủi ro",
        "Overview", "Income Statement", "Balance Sheet",
        "Cash Flow", "Notes", "Risk Factors"
    ]

    pattern = "|".join(re.escape(kw) for kw in section_keywords)
    splits = re.split(f"(?=(?:{pattern}))", text, flags=re.IGNORECASE)
    splits = [s.strip() for s in splits if s.strip()]

    chunks = []
    for section_text in splits:
        heading = section_text.split("\n", 1)[0].strip()
        chunks.append({
            "text": section_text,
            "metadata": {
                "ticker": ticker,
                "period": period,
                "section": heading,
                "domain": "finance",
                "chunk_type": "report_section",
                "chunk_index": len(chunks),
            }
        })

    return chunks
```

### E-commerce — Chunk by Review

```python
def chunk_product_reviews(reviews: list[dict], product_id: str) -> list[dict]:
    """Each review is 1 chunk, with enriched metadata."""
    chunks = []
    for i, review in enumerate(reviews):
        chunks.append({
            "text": review["content"],
            "metadata": {
                "product_id": product_id,
                "rating": review.get("rating", 0),
                "reviewer": review.get("reviewer", "anonymous"),
                "date": review.get("date", ""),
                "domain": "ecommerce",
                "chunk_type": "review",
                "chunk_index": i,
                "sentiment": "positive" if review.get("rating", 0) >= 4 else
                             "negative" if review.get("rating", 0) <= 2 else "neutral",
            }
        })
    return chunks
```

---

## 6. Metadata Enrichment

Use LLM to enrich metadata for each chunk.

```python
from openai import OpenAI

client = OpenAI()

def enrich_chunk_metadata(chunk: dict) -> dict:
    """Add summary, keywords, hypothetical questions to chunk."""
    text = chunk["text"]

    prompt = f"""Analyze the following text and return JSON:
{{
    "summary": "1-2 sentences summarizing the main content",
    "keywords": ["keyword 1", "keyword 2", ...],
    "questions": ["question this chunk can answer 1", "question 2", "question 3"],
    "entities": ["entity 1", "entity 2", ...]
}}

Text:
{text[:2000]}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )

    import json
    enrichment = json.loads(response.choices[0].message.content)

    chunk["metadata"].update({
        "summary": enrichment.get("summary", ""),
        "keywords": enrichment.get("keywords", []),
        "hypothetical_questions": enrichment.get("questions", []),
        "entities": enrichment.get("entities", []),
    })

    return chunk


def batch_enrich(chunks: list[dict], batch_size: int = 10) -> list[dict]:
    """Enrich metadata in batches to save API calls."""
    enriched = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        for chunk in batch:
            enriched.append(enrich_chunk_metadata(chunk))
        print(f"Enriched {min(i + batch_size, len(chunks))}/{len(chunks)} chunks")
    return enriched
```

---

## 7. Recursive Character Splitting (LangChain)

Using LangChain's built-in splitter cho convenience.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def langchain_chunk(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> list[dict]:
    """Use LangChain RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    docs = splitter.create_documents([text])
    chunks = []
    for i, doc in enumerate(docs):
        chunks.append({
            "text": doc.page_content,
            "metadata": {
                "chunk_index": i,
                "char_count": len(doc.page_content),
            }
        })

    return chunks

# With tiktoken length function
import tiktoken

def tiktoken_len(text: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=77,  # ~15%
    length_function=tiktoken_len,
    separators=["\n\n", "\n", ". ", " ", ""],
)
```
