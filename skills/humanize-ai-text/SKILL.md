---
name: humanize-ai-text
description: Humanize AI-generated text to bypass detection. This humanizer rewrites ChatGPT, Claude, and GPT content to sound natural and pass AI detectors like GPTZero, Turnitin, and Originality.ai. Based on Wikipedia's comprehensive "Signs of AI Writing" guide. Makes robotic AI writing undetectable and human-like.
allowed-tools:
  - Read
  - Write
  - StrReplace
  - Glob
---

# Humanize AI Text

Comprehensive CLI for detecting and transforming AI-generated text to bypass detectors. Based on [Wikipedia's Signs of AI Writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing).

## Quick Start

```bash
# Detect AI patterns
python scripts/detect.py text.txt

# Transform to human-like
python scripts/transform.py text.txt -o clean.txt

# Compare before/after
python scripts/compare.py text.txt -o clean.txt
```

---

## Detection Categories

The analyzer checks for **16 pattern categories** from Wikipedia's guide:

### Critical (Immediate AI Detection)
| Category | Examples |
|----------|----------|
| Citation Bugs | `oaicite`, `turn0search`, `contentReference` |
| Knowledge Cutoff | "as of my last training", "based on available information" |
| Chatbot Artifacts | "I hope this helps", "Great question!", "As an AI" |
| Markdown | `**bold**`, `## headers`, ``` code blocks ``` |

### High Signal
| Category | Examples |
|----------|----------|
| AI Vocabulary | delve, tapestry, landscape, pivotal, underscore, foster |
| Significance Inflation | "serves as a testament", "pivotal moment", "indelible mark" |
| Promotional Language | vibrant, groundbreaking, nestled, breathtaking |
| Copula Avoidance | "serves as" instead of "is", "boasts" instead of "has" |

### Medium Signal
| Category | Examples |
|----------|----------|
| Superficial -ing | "highlighting the importance", "fostering collaboration" |
| Filler Phrases | "in order to", "due to the fact that", "Additionally," |
| Vague Attributions | "experts believe", "industry reports suggest" |
| Challenges Formula | "Despite these challenges", "Future outlook" |

### Style Signal
| Category | Examples |
|----------|----------|
| Curly Quotes | "" instead of "" (ChatGPT signature) |
| Em Dash Overuse | Excessive use of — for emphasis |
| Negative Parallelisms | "Not only... but also", "It's not just... it's" |
| Rule of Three | Forced triplets like "innovation, inspiration, and insight" |

---

## Scripts

### detect.py — Scan for AI Patterns

```bash
python scripts/detect.py essay.txt
python scripts/detect.py essay.txt -j  # JSON output
python scripts/detect.py essay.txt -s  # score only
echo "text" | python scripts/detect.py
```

**Output:**
- Issue count and word count
- AI probability (low/medium/high/very high)
- Breakdown by category
- Auto-fixable patterns marked

### transform.py — Rewrite Text

```bash
python scripts/transform.py essay.txt
python scripts/transform.py essay.txt -o output.txt
python scripts/transform.py essay.txt -a  # aggressive
python scripts/transform.py essay.txt -q  # quiet
```

**Auto-fixes:**
- Citation bugs (oaicite, turn0search)
- Markdown (**, ##, ```)
- Chatbot sentences
- Copula avoidance → "is/has"
- Filler phrases → simpler forms
- Curly → straight quotes

**Aggressive (-a):**
- Simplifies -ing clauses
- Reduces em dashes

### compare.py — Before/After Analysis

```bash
python scripts/compare.py essay.txt
python scripts/compare.py essay.txt -a -o clean.txt
```

Shows side-by-side detection scores before and after transformation

---

## Workflow

1. **Scan** for detection risk:
   ```bash
   python scripts/detect.py document.txt
   ```

2. **Transform** with comparison:
   ```bash
   python scripts/compare.py document.txt -o document_v2.txt
   ```

3. **Verify** improvement:
   ```bash
   python scripts/detect.py document_v2.txt -s
   ```

4. **Manual review** for AI vocabulary and promotional language (requires judgment)

---

## AI Probability Scoring

| Rating | Criteria |
|--------|----------|
| Very High | Citation bugs, knowledge cutoff, or chatbot artifacts present |
| High | >30 issues OR >5% issue density |
| Medium | >15 issues OR >2% issue density |
| Low | <15 issues AND <2% density |

---

## Customizing Patterns

Edit `scripts/patterns.json` to add/modify:
- `ai_vocabulary` — words to flag
- `significance_inflation` — puffery phrases
- `promotional_language` — marketing speak
- `copula_avoidance` — phrase → replacement
- `filler_replacements` — phrase → simpler form
- `chatbot_artifacts` — phrases triggering sentence removal

---

## Batch Processing

```bash
# Scan all files
for f in *.txt; do
  echo "=== $f ==="
  python scripts/detect.py "$f" -s
done

# Transform all markdown
for f in *.md; do
  python scripts/transform.py "$f" -a -o "${f%.md}_clean.md" -q
done
```

---

## Reference

Based on Wikipedia's [Signs of AI Writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup. Patterns documented from thousands of AI-generated text examples.

Key insight: "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases."
