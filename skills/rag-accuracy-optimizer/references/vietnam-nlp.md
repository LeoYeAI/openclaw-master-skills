# Vietnamese NLP Processing for RAG

## Overview

Vietnamese has many unique characteristics that affect RAG quality: **diacritics**, **compound words**, **abbreviations**, **proper names**, and **domain-specific terms**. This file guides handling each issue.

---

## 1. Models for Vietnamese

### Comparison

| Model | Type | VN Quality | Use Case | Maintenance |
|---|---|---|---|---|
| **PhoBERT-v2** (VinAI) | Encoder only | ⭐⭐⭐⭐⭐ | NER, classification, fine-tune | Active |
| **ViBERT** | Encoder only | ⭐⭐⭐ | Basic NLP tasks | Ít maintain |
| **multilingual-e5-large** | Embedding | ⭐⭐⭐⭐ | RAG retrieval (recommended) | Active |
| **BGE-M3** | Embedding (hybrid) | ⭐⭐⭐⭐⭐ | RAG retrieval (best) | Active |
| **mBERT** | Encoder only | ⭐⭐⭐ | Baseline multilingual | Stable |
| **XLM-RoBERTa** | Encoder only | ⭐⭐⭐⭐ | Cross-lingual tasks | Active |

### Recommendations

```
RAG Retrieval (embedding):
  → BGE-M3 (best quality, hybrid dense+sparse)
  → multilingual-e5-large (good alternative)

NER / Entity Extraction:
  → PhoBERT-v2 + fine-tune trên domain data

Classification / Sentiment:
  → PhoBERT-v2

Word Segmentation:
  → underthesea (đơn giản, nhanh)
  → VnCoreNLP (chính xác hơn, cần Java)
```

---

## 2. Vietnamese Tokenization

### The Problem

Vietnamese is an **analytic language** — compound words are formed from multiple syllables:
- "bảo hiểm" = 1 từ (2 âm tiết)
- "nhân thọ" = 1 từ (2 âm tiết)
- "bảo hiểm nhân thọ" = 1 cụm từ (4 âm tiết)

Without word segmentation, models may misunderstand the meaning.

### underthesea

```bash
pip install underthesea
```

```python
from underthesea import word_tokenize, pos_tag, ner, sent_tokenize

# Word segmentation
text = "Bảo hiểm nhân thọ Manulife có nhiều gói sản phẩm tốt"
segmented = word_tokenize(text)
print(segmented)
# "Bảo_hiểm nhân_thọ Manulife có nhiều gói sản_phẩm tốt"

# POS tagging
tagged = pos_tag(text)
print(tagged)
# [('Bảo_hiểm', 'N'), ('nhân_thọ', 'N'), ('Manulife', 'Np'), ...]

# Named Entity Recognition
entities = ner(text)
print(entities)
# [('Manulife', 'B-ORG'), ...]

# Sentence segmentation
paragraph = "Gói ATHT có thời hạn 20 năm. Phí đóng 10 triệu/năm."
sentences = sent_tokenize(paragraph)
# ['Gói ATHT có thời hạn 20 năm.', 'Phí đóng 10 triệu/năm.']
```

### VnCoreNLP

```bash
# Cần Java 8+
pip install vncorenlp
# Download models
mkdir -p vncorenlp/models
wget https://raw.githubusercontent.com/vncorenlp/VnCoreNLP/master/VnCoreNLP-1.1.1.jar
wget https://raw.githubusercontent.com/vncorenlp/VnCoreNLP/master/models/wordsegmenter/wordsegmenter.rdr
```

```python
from vncorenlp import VnCoreNLP

# Start server
annotator = VnCoreNLP("VnCoreNLP-1.1.1.jar", annotators="wseg,pos,ner", max_heap_size='-Xmx2g')

text = "Bảo hiểm nhân thọ Manulife"
result = annotator.annotate(text)
# Word segmentation + POS + NER cùng lúc

annotator.close()
```

### Comparison underthesea vs VnCoreNLP

| | underthesea | VnCoreNLP |
|---|---|---|
| Language | Python | Java (Python wrapper) |
| Speed | Fast | Slower (JVM startup) |
| Accuracy | Good (~95%) | Better (~97%) |
| Install | `pip install` | Requires Java + model download |
| Features | wseg, pos, ner, sentiment | wseg, pos, ner, dep_parse |
| **Recommend** | Development, prototype | Production accuracy-critical |

---

## 3. Vietnamese Diacritics Handling

### The Problem

Users may search without diacritics: "bao hiem nhan tho" thay vì "bảo hiểm nhân thọ".

### Solution: Dual Indexing

```python
import re
import unicodedata


def remove_vietnamese_diacritics(text: str) -> str:
    """Remove Vietnamese diacritics (tone marks + circumflex marks)."""
    # Normalize to decomposed form
    text = unicodedata.normalize('NFD', text)
    
    # Remove combining diacritical marks
    text = re.sub(r'[\u0300-\u036f]', '', text)
    
    # Handle special Vietnamese characters
    replacements = {
        'đ': 'd', 'Đ': 'D',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def normalize_vietnamese(text: str) -> str:
    """Normalize Vietnamese text for consistent processing."""
    # Normalize unicode (NFC — composed form)
    text = unicodedata.normalize('NFC', text)
    
    # Fix common encoding issues
    text = text.replace('\xa0', ' ')  # Non-breaking space
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces
    text = text.strip()
    
    return text


# Dual indexing strategy
def index_document(text: str) -> dict:
    """Index document with both diacritics and non-diacritics versions."""
    normalized = normalize_vietnamese(text)
    no_diacritics = remove_vietnamese_diacritics(normalized)
    
    return {
        "original": normalized,
        "no_diacritics": no_diacritics,
        # Embed both versions or just the original
        # BM25 index on no_diacritics to match queries without diacritics
    }


# Search strategy
def search_with_diacritics_fallback(query: str, search_fn):
    """Search with diacritics, fallback to non-diacritics."""
    # Try original query first
    results = search_fn(query)
    
    if len(results) < 3:  # Not enough results
        # Try without diacritics
        query_no_diacritics = remove_vietnamese_diacritics(query)
        results_fallback = search_fn(query_no_diacritics, field="no_diacritics")
        # Merge results
        results = merge_and_deduplicate(results, results_fallback)
    
    return results
```

---

## 4. Abbreviation Handling

### Common Vietnamese Abbreviations

```python
VIETNAMESE_ABBREVIATIONS = {
    # Organizations
    "BHXH": "Bảo hiểm Xã hội",
    "BHYT": "Bảo hiểm Y tế",
    "BHTN": "Bảo hiểm Thất nghiệp",
    "BHNT": "Bảo hiểm Nhân thọ",
    "NHNN": "Ngân hàng Nhà nước",
    "UBND": "Ủy ban Nhân dân",
    "HĐQT": "Hội đồng Quản trị",
    "TGĐ": "Tổng Giám đốc",
    "GĐ": "Giám đốc",
    
    # Finance
    "TTCK": "Thị trường Chứng khoán",
    "CTCK": "Công ty Chứng khoán",
    "CK": "Chứng khoán",
    "CP": "Cổ phiếu",
    "TP": "Trái phiếu",
    "LNST": "Lợi nhuận sau thuế",
    "VCSH": "Vốn chủ sở hữu",
    "ROE": "Return on Equity",
    "ROA": "Return on Assets",
    "EPS": "Earnings Per Share",
    "P/E": "Price to Earnings",
    "NAV": "Net Asset Value",
    "VNĐ": "Việt Nam Đồng",
    
    # Legal
    "BLDS": "Bộ luật Dân sự",
    "BLHS": "Bộ luật Hình sự",
    "BLLĐ": "Bộ luật Lao động",
    "NĐ": "Nghị định",
    "TT": "Thông tư",
    "QĐ": "Quyết định",
    "NQ": "Nghị quyết",
    "CV": "Công văn",
    
    # Healthcare
    "BV": "Bệnh viện",
    "BS": "Bác sĩ",
    "BN": "Bệnh nhân",
    "XN": "Xét nghiệm",
    "KCB": "Khám chữa bệnh",
    "BHYT": "Bảo hiểm Y tế",
    "CSYT": "Cơ sở Y tế",
    
    # General
    "TP.HCM": "Thành phố Hồ Chí Minh",
    "HN": "Hà Nội",
    "ĐN": "Đà Nẵng",
    "SĐT": "Số điện thoại",
    "CMND": "Chứng minh Nhân dân",
    "CCCD": "Căn cước Công dân",
    "ĐH": "Đại học",
}


def expand_abbreviations(text: str, domain: str = None) -> str:
    """Expand Vietnamese abbreviations in text.
    
    Args:
        text: Input text
        domain: Optional domain filter (finance, legal, medical)
    
    Returns:
        Text with abbreviations expanded (original kept in parentheses)
    """
    import re
    
    expanded = text
    for abbr, full in VIETNAMESE_ABBREVIATIONS.items():
        # Match whole word only, case-insensitive for non-Vietnamese chars
        pattern = r'\b' + re.escape(abbr) + r'\b'
        # Replace: keep abbreviation, add full form
        replacement = f"{abbr} ({full})"
        expanded = re.sub(pattern, replacement, expanded)
    
    return expanded


def index_with_abbreviation_expansion(text: str) -> dict:
    """Index document with both original and expanded abbreviations."""
    return {
        "original": text,
        "expanded": expand_abbreviations(text),
        # BM25 index on expanded version
        # Vector embed on expanded version (more context)
    }
```

---

## 5. Vietnamese Proper Name Handling

```python
from underthesea import ner


def extract_vietnamese_entities(text: str) -> dict:
    """Extract Vietnamese named entities."""
    entities = ner(text)
    
    result = {"PER": [], "ORG": [], "LOC": [], "MISC": []}
    current_entity = []
    current_type = None
    
    for word, _, _, tag in entities:
        if tag.startswith("B-"):
            if current_entity:
                result[current_type].append(" ".join(current_entity))
            current_entity = [word]
            current_type = tag[2:]
        elif tag.startswith("I-") and current_type:
            current_entity.append(word)
        else:
            if current_entity:
                result[current_type].append(" ".join(current_entity))
                current_entity = []
                current_type = None
    
    if current_entity:
        result[current_type].append(" ".join(current_entity))
    
    return result


# Sử dụng
text = "Nguyễn Văn A mua bảo hiểm Manulife tại Hà Nội"
entities = extract_vietnamese_entities(text)
# {'PER': ['Nguyễn Văn A'], 'ORG': ['Manulife'], 'LOC': ['Hà Nội'], 'MISC': []}
```

### Proper Names in Metadata

```python
def enrich_chunk_with_entities(chunk: str) -> dict:
    """Add Vietnamese named entities to chunk metadata."""
    entities = extract_vietnamese_entities(chunk)
    
    return {
        "text": chunk,
        "metadata": {
            "persons": entities["PER"],
            "organizations": entities["ORG"],
            "locations": entities["LOC"],
            # Used for metadata filtering during search
        }
    }
```

---

## 6. Domain-Specific Terms

### Vietnamese Finance

```python
FINANCE_TERMS_VI = {
    # Terms → canonical form
    "lãi suất cơ bản": "lãi suất cơ bản (prime rate)",
    "room ngoại": "room nước ngoài (foreign ownership limit)",
    "margin": "margin (ký quỹ giao dịch)",
    "call margin": "call margin (yêu cầu bổ sung ký quỹ)",
    "T+": "T+ (ngày thanh toán)",
    "phiên ATO": "phiên mở cửa (ATO - At The Opening)",
    "phiên ATC": "phiên đóng cửa (ATC - At The Close)",
    "cổ phiếu penny": "cổ phiếu penny (giá thấp, rủi ro cao)",
    "bluechip": "cổ phiếu bluechip (vốn hóa lớn, ổn định)",
    "sàn": "sàn giao dịch chứng khoán",
    "HoSE": "Sở Giao dịch Chứng khoán TP.HCM",
    "HNX": "Sở Giao dịch Chứng khoán Hà Nội",
    "UPCOM": "sàn giao dịch công ty đại chúng chưa niêm yết",
    "VN-Index": "chỉ số VN-Index (HoSE)",
    "HNX-Index": "chỉ số HNX-Index (Hà Nội)",
}
```

### Legal Việt Nam

```python
LEGAL_TERMS_VI = {
    "điều": "điều (article)",
    "khoản": "khoản (clause/paragraph)",
    "điểm": "điểm (point/item)",
    "mục": "mục (section)",
    "chương": "chương (chapter)",
    "nghị định": "nghị định (decree)",
    "thông tư": "thông tư (circular)",
    "luật": "luật (law/act)",
    "pháp lệnh": "pháp lệnh (ordinance)",
    "hiến pháp": "hiến pháp (constitution)",
    "quyền lợi": "quyền lợi (benefit/right)",
    "nghĩa vụ": "nghĩa vụ (obligation)",
    "hợp đồng": "hợp đồng (contract)",
    "bồi thường": "bồi thường (compensation/indemnity)",
}
```

### Vietnamese Healthcare

```python
MEDICAL_TERMS_VI = {
    "đơn thuốc": "đơn thuốc (prescription)",
    "kê đơn": "kê đơn (prescribe)",
    "chẩn đoán": "chẩn đoán (diagnosis)",
    "điều trị": "điều trị (treatment)",
    "nội trú": "nội trú (inpatient)",
    "ngoại trú": "ngoại trú (outpatient)",
    "viện phí": "viện phí (hospital fee)",
    "BHYT": "bảo hiểm y tế",
    "KCB": "khám chữa bệnh",
    "toa thuốc": "toa thuốc (prescription - Southern dialect)",
}
```

### Enrichment Pipeline

```python
def enrich_for_domain(text: str, domain: str) -> str:
    """Enrich text with domain-specific term expansions."""
    term_dicts = {
        "finance": FINANCE_TERMS_VI,
        "legal": LEGAL_TERMS_VI,
        "medical": MEDICAL_TERMS_VI,
    }
    
    terms = term_dicts.get(domain, {})
    enriched = text
    
    for term, expansion in terms.items():
        if term.lower() in enriched.lower():
            # Append expansion as context
            enriched = enriched.replace(term, f"{term} [{expansion}]")
    
    return enriched
```

---

## 7. Full Vietnamese RAG Preprocessing Pipeline

```python
def preprocess_vietnamese_for_rag(
    text: str,
    domain: str = None,
    expand_abbr: bool = True,
    segment_words: bool = False,  # Only for PhoBERT
    handle_diacritics: bool = True,
) -> dict:
    """
    Full preprocessing pipeline for Vietnamese RAG.
    
    Returns dict with multiple text versions for different index strategies.
    """
    # 1. Normalize unicode
    normalized = normalize_vietnamese(text)
    
    # 2. Expand abbreviations
    expanded = expand_abbreviations(normalized) if expand_abbr else normalized
    
    # 3. Domain enrichment
    enriched = enrich_for_domain(expanded, domain) if domain else expanded
    
    # 4. Word segmentation (only for PhoBERT)
    segmented = word_tokenize(enriched) if segment_words else None
    
    # 5. No-diacritics version (for BM25 fallback)
    no_diacritics = remove_vietnamese_diacritics(enriched) if handle_diacritics else None
    
    # 6. Extract entities
    entities = extract_vietnamese_entities(normalized)
    
    return {
        "text_for_embedding": enriched,           # Main text for vector embedding
        "text_for_bm25": no_diacritics or enriched,  # For BM25 (supports no-diacritics search)
        "text_segmented": segmented,              # For PhoBERT (if used)
        "text_original": normalized,              # Original normalized text
        "entities": entities,                      # Named entities for metadata
        "metadata": {
            "has_abbreviations": expand_abbr and (enriched != normalized),
            "domain": domain,
            "language": "vi",
        }
    }
```
