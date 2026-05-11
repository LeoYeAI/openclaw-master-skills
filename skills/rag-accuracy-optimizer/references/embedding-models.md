# Embedding Models — Detailed Comparison

## Overview

Choosing an embedding model directly impacts retrieval quality. Consider: **quality** (MTEB score), **cost**, **latency**, **dimension**, và **language support**.

---

## Cloud Models

### OpenAI text-embedding-3-small

| Thuộc tính | Giá trị |
|---|---|
| Dimensions | 1536 (default), hỗ trợ giảm xuống 512/256 |
| Max tokens | 8191 |
| MTEB Average | ~62.3 |
| Cost | $0.02 / 1M tokens |
| Latency | ~50-100ms / request |
| Multilingual | Tốt (bao gồm tiếng Việt) |

**Ưu điểm:** Rẻ nhất trong dòng OpenAI, dimension reduction linh hoạt, API ổn định.
**Nhược điểm:** Quality thấp hơn large, phụ thuộc API.

### OpenAI text-embedding-3-large

| Thuộc tính | Giá trị |
|---|---|
| Dimensions | 3072 (default), hỗ trợ giảm xuống 1024/512/256 |
| Max tokens | 8191 |
| MTEB Average | ~64.6 |
| Cost | $0.13 / 1M tokens |
| Latency | ~80-150ms / request |
| Multilingual | Tốt |

**Ưu điểm:** Chất lượng cao nhất dòng OpenAI, Matryoshka dimension reduction.
**Nhược điểm:** Đắt gấp 6.5x so với small, dimension lớn tốn storage.

### Cohere embed-v4

| Thuộc tính | Giá trị |
|---|---|
| Dimensions | 1024 |
| Max tokens | 512 |
| MTEB Average | ~66.1 |
| Cost | $0.10 / 1M tokens |
| Latency | ~60-120ms / request |
| Multilingual | 100+ ngôn ngữ |
| Special | Input type (search_document, search_query, classification, clustering) |

**Ưu điểm:** MTEB score cao, hỗ trợ input_type giúp tối ưu cho từng use case, multilingual mạnh, kết hợp tốt với Cohere Rerank.
**Nhược điểm:** Max tokens thấp (512), cần chunk nhỏ hơn.

---

## Local / Open-Source Models

### BGE-M3 (BAAI)

| Thuộc tính | Giá trị |
|---|---|
| Dimensions | 1024 |
| Max tokens | 8192 |
| MTEB Average | ~65.0 |
| Cost | Free (self-host) |
| GPU RAM | ~2-4 GB (FP16) |
| Multilingual | 100+ ngôn ngữ (tốt cho tiếng Việt) |
| Special | Hybrid (dense + sparse + colbert) |

**Ưu điểm:** Multi-functionality (dense, sparse, ColBERT trong 1 model), context window lớn (8K), multilingual xuất sắc, **miễn phí**.
**Nhược điểm:** Cần GPU để inference nhanh, phức tạp hơn khi deploy.

```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

# Dense + Sparse cùng lúc
output = model.encode(
    ["Bảo hiểm nhân thọ có chi trả khi tự tử không?"],
    return_dense=True,
    return_sparse=True,
    return_colbert_vecs=False
)
dense_embedding = output['dense_vecs']   # (1, 1024)
sparse_embedding = output['lexical_weights']  # dict {token_id: weight}
```

### E5-large-v2 (Microsoft)

| Thuộc tính | Giá trị |
|---|---|
| Dimensions | 1024 |
| Max tokens | 512 |
| MTEB Average | ~62.2 |
| Cost | Free |
| GPU RAM | ~1.3 GB (FP16) |
| Multilingual | Chủ yếu English |

**Ưu điểm:** Nhẹ, nhanh, chất lượng tốt cho English.
**Nhược điểm:** Multilingual yếu, cần prefix "query:" / "passage:" khi encode.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('intfloat/e5-large-v2')
# Cần prefix
queries = ["query: What is life insurance?"]
passages = ["passage: Life insurance provides financial protection..."]
q_emb = model.encode(queries)
p_emb = model.encode(passages)
```

### all-MiniLM-L6-v2

| Thuộc tính | Giá trị |
|---|---|
| Dimensions | 384 |
| Max tokens | 256 |
| MTEB Average | ~56.3 |
| Cost | Free |
| GPU RAM | ~90 MB |
| Speed | Rất nhanh (~14K sentences/s trên GPU) |

**Ưu điểm:** Siêu nhẹ, siêu nhanh, chạy được trên CPU. Tốt cho prototype/POC.
**Nhược điểm:** Dimension nhỏ → quality thấp hơn, max tokens chỉ 256, English-only.

---

## Vietnam-Specific Models

### PhoBERT (VinAI)

| Thuộc tính | Giá trị |
|---|---|
| Dimensions | 768 (base) / 1024 (large) |
| Max tokens | 256 |
| Pretrained on | 20GB Vietnamese text |
| Tokenizer | BPE trên tiếng Việt có dấu |

**Ưu điểm:** Được train trực tiếp trên tiếng Việt, hiểu tốt ngữ pháp và ngữ nghĩa tiếng Việt, tốt cho NER/classification.
**Nhược điểm:** Không phải embedding model chuyên dụng (cần fine-tune cho retrieval), max tokens thấp, cần word segmentation (VnCoreNLP/underthesea).

```python
from transformers import AutoModel, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
model = AutoModel.from_pretrained("vinai/phobert-base-v2")

# Cần word segmentation trước
from underthesea import word_tokenize
text = word_tokenize("Bảo hiểm nhân thọ")  # "Bảo_hiểm nhân_thọ"
```

### ViBERT

| Thuộc tính | Giá trị |
|---|---|
| Dimensions | 768 |
| Max tokens | 512 |
| Pretrained on | Vietnamese Wikipedia + News |

**Ưu điểm:** Thiết kế cho tiếng Việt.
**Nhược điểm:** Dataset training nhỏ hơn PhoBERT, ít được maintain, community nhỏ.

### multilingual-e5-large (Microsoft)

| Thuộc tính | Giá trị |
|---|---|
| Dimensions | 1024 |
| Max tokens | 512 |
| MTEB Average | ~61.5 (multilingual tasks) |
| Languages | 100+ bao gồm tiếng Việt |
| Cost | Free |

**Ưu điểm:** Embedding model thực sự (không cần fine-tune cho retrieval), hỗ trợ tiếng Việt tốt, dimension cao.
**Nhược điểm:** Cần prefix "query:"/"passage:", nặng hơn MiniLM.

**⭐ Khuyến nghị cho tiếng Việt:** `multilingual-e5-large` hoặc `BGE-M3` là lựa chọn tốt nhất cho RAG tiếng Việt vì được thiết kế cho retrieval + multilingual tốt.

---

## Summary Comparison Table

| Model | Dim | MTEB | Cost/1M tok | Latency | Vietnamese | Best For |
|---|---|---|---|---|---|---|
| OAI embed-3-small | 1536 | 62.3 | $0.02 | ~75ms | Tốt | Production giá rẻ |
| OAI embed-3-large | 3072 | 64.6 | $0.13 | ~115ms | Tốt | Production chất lượng cao |
| Cohere embed-v4 | 1024 | 66.1 | $0.10 | ~90ms | Tốt | Production + Rerank combo |
| BGE-M3 | 1024 | 65.0 | Free | ~30ms* | Xuất sắc | Self-host, hybrid search |
| E5-large-v2 | 1024 | 62.2 | Free | ~25ms* | Kém | English-only projects |
| all-MiniLM-L6-v2 | 384 | 56.3 | Free | ~5ms* | Kém | POC, prototype |
| PhoBERT-base-v2 | 768 | N/A | Free | ~20ms* | Xuất sắc | VN NER/classification |
| multilingual-e5-large | 1024 | 61.5 | Free | ~30ms* | Tốt | VN RAG (khuyến nghị) |
| BGE-M3 | 1024 | 65.0 | Free | ~30ms* | Xuất sắc | VN RAG (khuyến nghị) |

*Latency local: đo trên GPU A100, batch_size=1

---

## Model Selection Guide

### Decision Tree

```
Budget cho embedding API?
├── Có → Cần chất lượng cao nhất?
│   ├── Có → Cohere embed-v4 + Rerank
│   └── Không → OpenAI text-embedding-3-small
└── Không (self-host) → Ngôn ngữ?
    ├── Tiếng Việt → BGE-M3 hoặc multilingual-e5-large
    ├── English → E5-large-v2
    └── POC/Prototype → all-MiniLM-L6-v2
```

### Dimension Reduction (Matryoshka)

OpenAI embed-3 hỗ trợ giảm dimension để tiết kiệm storage:

```python
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-large",
    input="Bảo hiểm nhân thọ",
    dimensions=512  # Giảm từ 3072 → 512
)
# Trade-off: quality giảm ~2-5% nhưng storage giảm 6x
```

### Batch Processing Best Practices

```python
# OpenAI: batch tối đa ~2000 inputs / request
# Cohere: batch tối đa 96 texts / request
# Local: batch_size tùy GPU RAM

# Ví dụ batch encoding local
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-m3')
chunks = ["chunk1", "chunk2", ...]  # 10K chunks

# Batch encode
embeddings = model.encode(
    chunks,
    batch_size=256,
    show_progress_bar=True,
    normalize_embeddings=True  # Important for cosine similarity
)
```
