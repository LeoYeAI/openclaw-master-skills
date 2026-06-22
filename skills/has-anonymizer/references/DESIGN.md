# HaS Text CLI — Requirements and Design Document

## 1. Project Overview

`has_text` is the CLI tool for the HaS (Hide and Seek) privacy model. It wraps 6 atomic model capabilities plus helper tool capabilities into **3 user-facing commands**, providing a complete "anonymize → restore" pipeline.

It serves as the technical foundation for the upcoming OpenClaw HaS Plugin and HaS Skills.

### Relationship with Upstream and Downstream

```
has_text_model.gguf (0.6B Qwen3)     ← on-device model
        ↕ llama-server (OpenAI API)
    has_text CLI                      ← this project (current layer)
        ↕
  OpenClaw HaS Skills / Plugin       ← future integration layer
        ↕
    6 major use cases                 ← see has_scenarios.md
```

---

## 2. Design Principles

| Principle | Description |
|-----------|-------------|
| **No exposed atomic capabilities** | Users do not need to understand the internal NER, Hide_with, Hide_without, Pair, Split, Seek model capabilities or Tool-Seek helper capabilities — they only use the `hide`, `seek`, and `scan` commands |
| **Pipeline-friendly** | Supports `--text`, `--file`, and stdin input; JSON output is suitable for script composition |
| **Automatic chunking** | Long model-backed text operations are automatically chunked by token count (preserving sentence integrity). `hide` accumulates mapping across chunks; cross-language `seek` chunks by tag-safe boundaries and carries only the mapping keys present in each chunk |
| **Model + tool dual layer** | Each step uses the most stable mechanism currently available: `hide` keeps mapping extraction model-backed for correctness, while `seek` still prefers deterministic replacement when safe |
| **Fully self-contained** | All code (including language detection and the experimental `pair.py` helper) is built into the `has_text/` directory with no external code dependencies |

---

## 3. Command Design

### 3.1 `hide` — Anonymize

Replaces sensitive entities in text with anonymous tags, outputting anonymized text + mapping table.

**Input**:
- Text (`--text` / `--file` / stdin)
- Entity types (`--types`, JSON array)
- Optional (single-file only): existing mapping table (`--mapping`, for incremental anonymization)

**Output**:
```json
{
  "text": "anonymized text...",
  "mapping": {
    "<person name[1].personal.name>": ["John"],
    "<address[1].city.district>": ["Brooklyn, New York"]
  }
}
```

**Internal workflow (Phase 1 orchestration, invisible to users)**:
```
NER → entities found?
  ├─ has mapping → Model-Hide_with (maintain cross-text/cross-chunk consistency)
  └─ no mapping → Model-Hide_without (first-time anonymization)
→ Model-Pair (mapping extraction)
→ contains composite tags? → Model-Split + Tool-Mapping-Merge
→ mapping self-check
  ├─ pass → output
  └─ fail → error (fail closed)
```

### 3.2 `seek` — Restore

Restores text containing anonymous tags to its original form. Full restoration, no selective restoration.

**Input**:
- Anonymized text (`--text` / `--file` / stdin)
- Mapping table (`--mapping`, required for single-file seek)
- Batch mode: per-file mapping JSON files under `mappings/` by default, or an explicit `--mapping-dir` (no shared `--mapping`)

**Output**:
```json
{
  "text": "restored original text..."
}
```

**Internal workflow (Phase 3 orchestration, invisible to users)**:
```
Does text contain tags?
  ├─ no → output directly
  └─ yes → language detection
       ├─ same language → Tool-Seek (deterministic replacement) → self-check
       │                   └─ fail → Model-Seek (fallback)
       └─ different language → chunk if needed → Model-Seek (cross-language restoration)
```

### 3.3 `scan` — Scan

Identifies sensitive entities in text (identification only, no anonymization).

**Input**:
- Text (`--text` / `--file` / stdin)
- Entity types (`--types`, JSON array)

**Output**:
```json
{
  "entities": {
    "person name": ["John", "Jane"],
    "address": ["Brooklyn, New York"],
    "phone number": []
  }
}
```

**Internal workflow**: Calls Model-NER only.

---

## 4. Recursive Chunking

### 4.1 Why Chunking Is Needed

The model's recommended deployment context is 8192 tokens. A single `hide` call needs to fit:
- Two conversation turns (NER question + NER result + Hide instruction + Hide output)
- Mapping table (carried during `hide_with`)

Measured token budgets (Qwen3 tokenizer):

| Scenario | Available text tokens | ≈ Chinese characters |
|----------|----------------------|---------------------|
| hide_without (first chunk) | ~3400 | ~5000 |
| hide_with (10 mapping entries) | ~3280 | ~4900 |
| hide_with (55 mapping entries) | ~3100 | ~4600 |

### 4.2 Chunking Strategy

- **Default threshold**: 3000 tokens/chunk (~400 tokens safety margin)
- **Dynamic `hide_with` budget**: After chunk 1, subtract the tokenized mapping JSON from the text budget before splitting the next chunk
- **Split rule**: Find the nearest sentence boundary near the threshold (`。！？\n`) and cut back, preserving sentence integrity
- **Fallback order**: Paragraph break > Period > Semicolon > Comma > Hard cut

### 4.3 Cross-Chunk Consistency

Recursive chunking reuses the `hide_with` multi-turn conversation mechanism:

```
Chunk 1 → hide_without → anonymized_text₁ + mapping₁
Chunk 2 → shrink budget by mapping₁ → hide_with(mapping₁) → anonymized_text₂ + mapping₂
Chunk 3 → shrink budget by mapping₂ → hide_with(mapping₂) → anonymized_text₃ + mapping₃
...
Final = concatenate all anonymized texts + mapping_N
```

When the same entity appears in different chunks, `hide_with` ensures consistent tag numbering via the mapping table.

### 4.4 Key Metrics

| Metric | Measured Value |
|--------|---------------|
| Chinese token ratio | 1.86 chars/token (0.54 tokens/char) |
| Tag token expansion | Original entity ~2 tok → Tag ~10-13 tok (~5-6x) |
| Chat format overhead | ~8 tokens |
| hide_without fixed overhead | ~57 tokens |
| Average mapping entry size | ~18 tokens/entry |

---

## 5. Internal Architecture

### 5.1 Model Capabilities vs Tool Capabilities

| Component | Type | Purpose |
|-----------|:----:|---------|
| Model-NER | 🔵 Model | Entity recognition |
| Model-Hide | 🔵 Model | First-time anonymization (no mapping) |
| Model-Hide_with | 🔵 Model | Incremental anonymization (with mapping) |
| Model-Split | 🔵 Model | Split composite tags |
| Model-Pair | 🔵 Model | Mapping extraction (primary) |
| Model-Seek | 🔵 Model | Cross-language restoration (fallback) |
| Tool-Pair | 🟢 Tool | Diff-based mapping helper retained for offline/debug use (`pair.py`) |
| Tool-Seek | 🟢 Tool | Deterministic tag replacement |
| Tool-Language Detection | 🟢 Tool | Language detection |
| Tool-Tag Extraction | 🟢 Tool | Composite tag detection |
| Tool-Mapping Merge | 🟢 Tool | Mapping table merge |

### 5.2 File Structure

```
scripts/has_text/
├── __init__.py          # Package init
├── __main__.py          # python -m has_text entry point
├── has_text.py          # CLI argparse dispatcher
├── client.py            # llama-server HTTP client (chat + tokenize)
├── prompts.py           # 6 prompt template builders (character-exact match with training templates)
├── chunker.py           # Token-aware text chunker
├── mapping.py           # Mapping utilities (merge, I/O, tag detection, JSON tolerance)
├── pair.py              # Experimental diff-based mapping helper (not on the main hide path)
├── lang.py              # Language detection: Unicode script heuristics (self-contained)
└── commands/
    ├── __init__.py
    ├── scan.py          # scan command
    ├── hide.py          # hide command (Phase 1 full workflow orchestration)
    └── seek.py          # seek command (Phase 3 full workflow orchestration)
```

### 5.3 Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| `requests` | Python package | HTTP calls to llama-server |
| `llama-server` | External service | Loads `has_text_model.gguf` for inference |

> Note: `pair.py` and language detection (`lang.py`) remain built-in with no external code dependencies, even though `hide` currently uses Model-Pair on the main path.
