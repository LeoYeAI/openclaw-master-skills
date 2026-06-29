# RedNote Community Intelligence Output Patterns

Use this file when the task needs compact but structured output, especially for comment clustering, fast-moving community updates, local recommendation summaries, and rumor-sensitive writeups.

## 1) Quick scan output

- Subject:
- Category:
- Time scope:
- Overall signal:
- Confidence:
- One-line take:

## 2) Evidence bullet format

Use one bullet per source or per consolidated claim.

Pattern:
- `[credibility 4 | score 3 | first-hand | 2026-03] refund dispute repeated across 3 posts — <url>`
- `[credibility 5 | score 4 | official | 2026-03] regulator notice confirms policy change — <url>`
- `[credibility 3 | score 1 | community | date unknown] many users praise atmosphere but specifics are thin — <url>`

Write the summary so the reader can understand the point without opening the link.

## 3) Comment clustering pattern

Cluster comments only when you have visible text, search snippets, screenshots, or fetched content. Do not imply full-thread access if you only saw snippets.

For each cluster, capture:
- cluster name
- stance: support / oppose / mixed / joking / skeptical / recommendation / complaint
- representative wording pattern
- approximate repetition count
- evidence quality note

Template:
- **Cluster:** price complaints
  - stance: complaint
  - pattern: "贵", "不值这个价", "性价比一般"
  - repetition: ~6 visible mentions
  - note: mostly snippet-level, medium confidence

- **Cluster:** still worth trying once
  - stance: mixed recommendation
  - pattern: "排队久但是拍照出片", "适合打卡"
  - repetition: ~4 visible mentions
  - note: consistent but not deeply verified

### Useful clustering buckets

Use 3-5 buckets unless the evidence is unusually rich:
- price / value
- quality / outcome
- service / attitude
- logistics / queue / wait / access
- credibility / scam / official response
- humor / meme / sarcasm
- support / defense / fandom

## 4) Latest update or policy scan pattern

Use this structure for policy or community updates:
- **What changed:** the claimed update in one sentence
- **Confirmed by:** official / media / community chatter
- **Earliest visible date:**
- **Likely impact:** who is affected and how
- **Disagreement / confusion:** where interpretation diverges
- **Confidence:** low / medium / high

## 5) Gossip or controversy synthesis pattern

Keep allegation, response, and consequence separate.

Template:
- **Trigger event:** what started the discussion
- **Main allegations or rumors:** 2-4 bullets
- **Response:** official or involved-party reaction
- **What is actually verified:** hard facts only
- **What remains rumor-level:** unverified claims, leaks, screenshots, hearsay
- **Current community mood:** mockery / anger / fatigue / split / support

## 6) Local recommendation pattern

Use tradeoffs instead of declaring a single winner.

Template:
- **Best for:** photo spot / date / fast meal / family / specialty dish / late night
- **Strengths:**
- **Common complaints:**
- **Price impression:** cheap / fair / expensive for what it is
- **Queue / booking note:**
- **Decision:** worth trying / only if nearby / hype > quality / avoid for now

### Shortlist comparison pattern

When comparing multiple local options, use one bullet per venue:
- `Name — best for X; common complaint Y; confidence low/medium/high`

## 7) Media analysis guardrails

For post, video, or gif tasks, explicitly mark:
- what is directly visible
- what is inferred from captions or snippets
- what would require login, in-app rendering, full comment expansion, or frame extraction

Safe phrasing examples:
- "Based on the visible snippet..."
- "I can infer a likely reaction split, but not confirm full comment distribution from public search results alone."
- "To analyze the clip itself rather than metadata, I would need the file or extracted frames."

## 8) Verification-aware conclusion pattern

Use this when evidence is noisy:
- **Strongest confirmed point:**
- **Most repeated but weakly verified claim:**
- **Main uncertainty:**
- **Decision posture:** proceed / proceed cautiously / wait for confirmation / avoid for now
