# RedNote Structured Claim Log

Use this file when the task is noisy, multimodal, rumor-prone, or evidence-heavy. The goal is to separate claims from proof instead of dumping vibes into a summary.

## 1) Core rule

A claim log is not the final answer. It is the working ledger that keeps:
- what was claimed
- where it came from
- what evidence modality supports it
- how strong that support is
- what remains unresolved

## 2) Minimum claim fields

For each material claim, capture:
- `claim_id`
- `claim_text`
- `claim_type`: fact / allegation / praise / complaint / rumor / official statement / recommendation
- `theme`: pricing / service / policy / controversy / quality / fraud-risk / taste / queue / subtitles / audio / image-text / etc.
- `entity`
- `time_scope`
- `geography`
- `status`: supported / mixed / weak / contradicted / unresolved
- `confidence`: low / medium / high
- `notes`

## 3) Evidence item fields

Each claim can map to one or more evidence items.

Capture:
- `evidence_id`
- `claim_id`
- `source_url`
- `source_class`: official / media / first-hand / community / low-trust
- `modality`: text-page / image / screenshot / video / gif / audio / mixed
- `access_level`: direct file / fetched page / search snippet / quoted relay
- `visible_date`
- `extract`
- `summary`
- `credibility`: 0-5
- `score`: 0-5
- `supports`: supports / partially-supports / contradicts / contextual-only

## 4) Compact JSON template

```json
{
  "claims": [
    {
      "claim_id": "c1",
      "claim_text": "...",
      "claim_type": "allegation",
      "theme": ["controversy", "video"],
      "entity": "...",
      "time_scope": "2026-03",
      "geography": "...",
      "status": "weak",
      "confidence": "low",
      "notes": "Only snippet-level video references so far"
    }
  ],
  "evidence": [
    {
      "evidence_id": "e1",
      "claim_id": "c1",
      "source_url": "https://...",
      "source_class": "community",
      "modality": "video",
      "access_level": "search snippet",
      "visible_date": "2026-03-20",
      "extract": "caption or OCR/transcript fragment",
      "summary": "What is directly visible",
      "credibility": 2,
      "score": 3,
      "supports": "partially-supports"
    }
  ]
}
```

## 5) Spreadsheet-style markdown fallback

When JSON is too heavy, use bullets grouped by claim.

Template:
- **Claim c1:** store raised prices after going viral
  - status: mixed
  - confidence: medium
  - evidence: `[credibility 4 | score 3 | image | fetched page | 2026-03] menu screenshot shows updated prices — <url>`
  - evidence: `[credibility 3 | score 2 | community | snippet | 2026-03] repeated complaints mention 贵 but without receipts — <url>`
  - gap: need official menu or multiple dated receipts

## 6) Status meanings

- `supported`: strongest available evidence points in the same direction
- `mixed`: meaningful evidence conflicts or scope is unclear
- `weak`: claim appears repeatedly but evidence is thin
- `contradicted`: stronger evidence cuts against the claim
- `unresolved`: too little inspectable evidence either way

## 7) Multimodal notes

When the evidence is not plain text, add one short modality note:
- image-text legible / partly legible / unclear
- video sequence direct / excerpted / not inspectable
- audio transcript direct / ASR-derived / second-hand quote

## 8) Aggregation guidance

Before writing the final answer:
1. identify which 2-4 claims actually matter to the user's decision
2. collapse duplicate evidence items
3. keep rumor claims visible but clearly downgraded
4. separate "widely discussed" from "well supported"
5. cite the strongest evidence for each conclusion

## 9) Final-answer bridge

Translate the claim log into a human summary using this order:
1. strongest confirmed point
2. most repeated but weaker claim
3. major contradiction or uncertainty
4. practical recommendation or next check
