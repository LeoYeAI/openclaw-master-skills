# SHIFT — CONSULT
# Sub-identity-to-sub-identity consultation protocol.
# Allows one sub-identity to call on another for specialized context.

## When Consultation Happens

A sub-identity may consult another when:
1. The persona's `consults` list includes the target identity
2. The sub-identity detects it would benefit from specialist knowledge
3. Example: Codex is writing a Twitter sentiment module → consults Researcher for the best analysis approach

Consultation is **NOT** automatic — the sub-identity decides when to call `consult()`.

## The consult() Function

Inside a sub-agent session, `consult()` is available as a tool-like function:

```javascript
consult({
  target: "researcher",           // persona name from consults list
  question: "What is the best approach for Twitter sentiment analysis?",
  context: "I'm building a trading bot that reacts to social media sentiment."
})
```

## Consultation Protocol (Step by Step)

```
1. Sub-identity (Codex) decides to consult Researcher
         ↓
2. Codex checks: is "researcher" in my consults list? ✓
   Is "researcher" in my consultsNever list? ✗
         ↓
3. Codex checks: am I within consultation timeout budget?
   available = persona.timeout - elapsed
   consultationTimeout = min(available * 0.5, persona.consultationTimeout)
         ↓
4. Codex writes CONSULT-INBOUND.md to session folder
         ↓
5. Codex sends status update to master:
   "Codex is consulting Researcher on sentiment analysis approach..."
         ↓
6. Master updates user (in transparent mode):
   "[Assistant] ↔ [Codex → Researcher] consulting on sentiment analysis..."
         ↓
7. Codex calls sessions_spawn for Researcher (child session)
         ↓
8. Researcher reads CONSULT-INBOUND.md
         ↓
9. Researcher writes CONSULT-OUTBOUND.md
         ↓
10. Codex reads CONSULT-OUTBOUND.md
         ↓
11. Codex continues task with enriched context
         ↓
12. Codex writes final OUTBOUND.md (with ConsultationLog)
         ↓
13. Master reads OUTBOUND.md, detects consultation, mentions it
```

## CONSULT-INBOUND.md

```markdown
# CONSULT-INBOUND — Codex → Researcher

## From: codex
## To: researcher
## Timestamp: 2026-03-18T15:42:30Z
## Parent runId: run-20260318-1542-codex-001

## Question
What is the best approach for Twitter/X sentiment analysis for a trading bot?

## Context
Building a trading bot that reacts to social media sentiment.
Currently implementing the data fetching layer — need to decide between:
- VADER (rule-based)
- TextBlob (rule-based)
- FinBERT (ML-based, finance-specific)
- Twitter API + custom ML pipeline

## Constraints
- Real-time or near-real-time (minutes, not hours)
- Works on short text (tweets)
- Available as Python library or API

## ConsultationTimeout
30 seconds (budget-constrained)
```

## CONSULT-OUTBOUND.md

```markdown
# CONSULT-OUTBOUND — Researcher → Codex

## Status: complete

## Answer

For a trading bot with real-time requirements on short text:

**Recommended: FinBERT + VADER hybrid**

1. **VADER** for baseline sentiment (fast, rule-based, good for short text)
2. **FinBERT** for financial-specific nuance (pretrained on financial text)
3. Combine scores: `final_score = 0.4 * vader + 0.6 * finbert`

**Libraries:**
- VADER: `pip install vaderSentiment`
- FinBERT: `pip install finbert-ai[gpu]` or use HuggingFace Transformers

**Twitter/X data:**
- Use `snscrape` or `tweepy` for historical
- Use Twitter API v2 for real-time (requires elevated access)

**Avoid:** TextBlob for financial text — it's trained on general text and underperforms on finance-specific content.

## Key Takeaways for Codex
1. Use VADER + FinBERT hybrid, weighted toward FinBERT
2. Both are available as Python libraries
3. For real-time Twitter data, consider the Twitter API v2 with elevated access
4. Score normalization is important — tweet sentiment scores are noisy

## Cost
inputTokens: 890, outputTokens: 234, estimatedCost: 0.018
```

## Depth Limit: Max 1

**Critical rule: A sub-identity cannot consult another sub-identity that then consults a third.**

When Codex calls `consult(researcher, ...)`:
- Researcher is now in a child session (depth = 2)
- Researcher CANNOT call `consult()` — its own `consults` list is ignored
- This prevents infinite loops and runaway costs

Implementation: When spawning a consultation child session, set `maxConsultDepth: 1` in the spawn call.

## Loop Prevention

Two mechanisms prevent consultation loops:

1. **Max depth** (enforced by DELEGATOR):
   - Child sessions cannot call `consult()`
   - Only top-level sub-identities can

2. **consultsNever** (enforced by sub-identity's own logic):
   - Even if Researcher were somehow callable, Codex has `consultsNever: [runner]`
   - Runner can never be consulted by anyone in v1

## Timeout Handling

```
ConsultationTimeout reached:
    → child session cancelled
    → Codex falls back to its own knowledge
    → logs: "consult_timeout: researcher, falling back"
    → OUTBOUND.md ConsultationLog records: {status: "timeout"}
```

## Visibility to User

Consultation is ALWAYS visible to the user (not gated by `displayMode`):

```
[Transparent mode]
[Assistant] ↔ [Codex → Researcher] consulting on sentiment analysis approach...

[Hidden mode]
[Assistant]: Codex is checking something... (consultation happening invisibly)
```

The consultation itself is visible in both modes because:
- It represents real work being done on the user's behalf
- It builds trust — the user sees the system being thorough
- It helps the user understand why certain tasks take longer

## Cost Attribution

Consultation costs are attributed to the **parent sub-identity's delegation**, not separate.

```
Codex delegation cost: $0.023
  └── Researcher consultation: $0.018 (included in Codex's total)
Total: $0.023 (only Codex's runId tracks the cost)
```

The cost-tracking.json records consultation cost as part of the parent's delegation entry.

## consult() Function Definition (for sub-identity prompt)

Sub-identities receive this in their task prompt:

```markdown
## Calling consult()

If you need specialized knowledge from another sub-identity, you may call consult():

Function: consult(target: string, question: string, context: string): ConsultResult

Rules:
- target must be in your consults list (codex can consult researcher, etc.)
- target must NOT be in your consultsNever list
- You can only call consult() once per task
- Maximum wait time: min(remaining_time * 0.5, your consultationTimeout)

What happens:
1. Your question is written to a shared context file
2. The target sub-identity answers your question
3. Their answer is returned to you as context
4. You continue your task with their input

When to use consult():
- You need domain knowledge outside your specialty
- You're unsure about an approach and want a second opinion
- A technical decision would benefit from specialist input

When NOT to use consult():
- You already know the answer
- The question is trivial
- Time is running low (check remaining timeout first)
```

## Edge Cases

| Scenario | Behavior |
|---|---|
| Target not in `consults` | consult() returns error: "not allowed to consult {target}" |
| Target in `consultsNever` | consult() returns error: "{target} is blocked from consultation" |
| Consult called twice | Error: "consult() already called in this session" |
| Child times out | Parent falls back to own knowledge, logs warning |
| Child errors | Parent falls back to own knowledge, logs error |
| No consultationTimeout left | consult() returns error: "insufficient time for consultation" |
| displayMode is hidden | Final attribution hidden, but consultation status still shown |
