# Conflict Detection Patterns

Rules for detecting contradictions between facts.

## Detection Methods

| Method | Accuracy | Cost | When to Use |
|--------|----------|------|-------------|
| Negation patterns | Medium | Free | First pass, always |
| Sentiment opposition | Medium | Free | When subjects overlap |
| Semantic similarity + LLM | High | $$ | High-confidence facts only |

## Negation Patterns

Simple regex-based detection. Fast and free.

### Direct Negation
```
Pattern: "X is Y" vs "X is not Y"
Example: 
  - "Charles is patient" 
  - "Charles is not patient"
Strength: 0.9
```

### Antonym Pairs
```
Pairs:
  likes ↔ dislikes
  prefers ↔ avoids
  always ↔ never
  loves ↔ hates
  good ↔ bad
  yes ↔ no
  true ↔ false
  can ↔ cannot
  will ↔ won't
  should ↔ shouldn't

Example:
  - "Charles likes verbose explanations"
  - "Charles dislikes verbose explanations"
Strength: 0.8
```

### Quantifier Conflicts
```
Conflicts:
  all ↔ none
  always ↔ never
  everyone ↔ no one
  everything ↔ nothing
  
Example:
  - "Charles always responds quickly"
  - "Charles never responds quickly"
Strength: 0.85
```

## Sentiment Opposition

Detect opposing sentiment toward same subject.

### Implementation
```python
positive = {"likes", "prefers", "enjoys", "loves", "wants", "good", "yes", "always"}
negative = {"dislikes", "hates", "avoids", "bad", "no", "never", "not"}

def check_sentiment_conflict(fact1, fact2):
    words1 = set(fact1.lower().split())
    words2 = set(fact2.lower().split())
    
    # Must share subject (2+ common words)
    common = words1 & words2
    if len(common) < 2:
        return 0.0
    
    # Check sentiment
    f1_pos = words1 & positive
    f1_neg = words1 & negative
    f2_pos = words2 & positive
    f2_neg = words2 & negative
    
    if (f1_pos and f2_neg) or (f1_neg and f2_pos):
        return 0.6
    
    return 0.0
```

## Temporal Conflicts

Facts that were true at different times.

### Detection
- Look for temporal markers: "now", "currently", "used to", "before", "after"
- Date mentions: "in 2023", "last year", "recently"

### Resolution
- **Don't mark as contradiction** if clearly temporal
- Create `updates` edge instead of `contradicts`
- Keep both facts with temporal context

```surql
RELATE fact:new->relates_to->fact:old SET 
  relationship = "updates",
  strength = 1.0,
  detection_method = "temporal";
```

## LLM-Based Detection

For high-stakes conflicts, use LLM verification.

### When to Use
- Both facts have confidence > 0.7
- Pattern-based detection found potential conflict
- Cost is justified by importance

### Prompt Template
```
Given these two statements, determine if they contradict each other.

Statement A: "{fact1}"
Statement B: "{fact2}"

Respond with:
- "CONTRADICT" if they directly contradict
- "COMPATIBLE" if they can both be true
- "TEMPORAL" if one updates/supersedes the other
- "UNCLEAR" if relationship is ambiguous

Explain briefly.
```

### Implementation
```python
async def llm_check_contradiction(fact1: str, fact2: str) -> tuple[str, float]:
    """Use LLM to verify contradiction. Returns (type, confidence)."""
    response = await llm.complete(PROMPT.format(fact1=fact1, fact2=fact2))
    
    if "CONTRADICT" in response:
        return ("contradicts", 0.9)
    elif "TEMPORAL" in response:
        return ("updates", 0.8)
    else:
        return (None, 0.0)
```

## Conflict Resolution Flow

```
New Fact Arrives
       │
       ▼
┌─────────────────┐
│ Embed & Search  │
│ Similar Facts   │
└────────┬────────┘
         │
         ▼ (similarity > 0.85)
┌─────────────────┐
│ Pattern Check   │ ─── No Match ───▶ Store Fact
└────────┬────────┘
         │ Match
         ▼
┌─────────────────┐
│ Sentiment Check │ ─── No Conflict ─▶ Store Fact
└────────┬────────┘
         │ Conflict
         ▼
┌─────────────────┐
│ Both High Conf? │ ─── No ──────────▶ Create Edge, Drain Old
└────────┬────────┘
         │ Yes
         ▼
┌─────────────────┐
│ LLM Verify      │ ─── Not Conflict ─▶ Store Fact
└────────┬────────┘
         │ Confirmed
         ▼
┌─────────────────┐
│ Create Edge     │
│ Drain Lower     │
│ Flag for Review │
└─────────────────┘
```

## Edge Strength Guidelines

| Scenario | Strength |
|----------|----------|
| Direct negation ("is" vs "is not") | 0.9 |
| Antonym pair detected | 0.8 |
| Sentiment opposition | 0.6 |
| LLM confirmed contradiction | 0.9 |
| LLM detected temporal update | 0.8 (for `updates` edge) |
| Manual override | 1.0 |

## Handling Ambiguity

When conflict is unclear:
1. **Don't create edge** - avoid false positives
2. **Log for review** - human can clarify later
3. **Lower confidence slightly** on both facts (-0.05)

```surql
-- Flag ambiguous pair for review
CREATE review CONTENT {
  fact_a: $fact1,
  fact_b: $fact2,
  reason: "potential_conflict",
  similarity: $sim,
  created_at: time::now()
};
```
