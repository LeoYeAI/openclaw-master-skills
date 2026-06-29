# RedNote Community Intelligence Scoring Rubric

Use this file when the task needs more careful judgment than the short rubric in `SKILL.md`.

## Source classes

1. **Official / documentary**
   - official brand, school, shop, regulator, or platform pages
   - government notices, court judgments, company registrations, policy releases

2. **Reported / journalistic**
   - established media or industry reporting with named sources

3. **First-hand user account**
   - detailed personal experience with dates, prices, screenshots, names, order details, or concrete specifics

4. **Community discussion / anecdote**
   - RedNote/Xiaohongshu snippets, Zhihu answers, Tieba/forum threads, reposts, roundups

5. **Low-trust pages**
   - SEO farms, scraped aggregators, unverifiable reposts

## Credibility cues

Increase credibility when a source has:
- named entity and consistent branding
- concrete dates, fees, store names, policy text, screenshots, or timeline details
- direct first-hand experience
- corroboration from independent sources
- recent publication date when the topic is time-sensitive

Lower credibility when a source has:
- vague emotional wording without specifics
- no visible date or context
- engagement bait wording like "千万别去" or "塌房实锤" with no evidence
- copied text across many pages
- obvious marketing or affiliate incentives
- edited screenshots or second-hand relays with no provenance

## Risk and recommendation cues by category

### Education reputation
High-signal red flags:
- guaranteed admission, job, or offer claims
- refund disputes or impossible refund conditions
- mismatch between sales pitch and contract
- fake or inflated employment or admission outcomes
- repeated complaints about absent teaching or support

### Policy or community updates
High-signal caution signs:
- claims of a new rule with no primary source
- community over-reading a vague official notice
- screenshots without source link or date
- old policy being recirculated as new

### Gossip or controversy
High-signal caution signs:
- anonymous chat logs with no provenance
- "everyone is saying" rumor loops
- clipped videos or gifs stripped of context
- quote screenshots without original post link

### Local recommendations
Useful decision cues:
- repeated praise on a specific dish or service strength
- repeated complaints on price, queue, hygiene, or service attitude
- consistency across different source types such as RedNote plus maps/reviews plus official menu or hours pages
- recency, because local quality can shift quickly

## Suggested scoring method

For each source:
- assign `credibility: 0-5`
- assign `score: 0-5`
- tag one or more themes such as `policy`, `refund`, `pricing`, `support`, `controversy`, `taste`, `service`, `environment`

Interpret `score` carefully:
- for risk-oriented tasks, higher = more caution or downside risk
- for recommendation tasks, either relabel the field clearly or explain whether high means stronger recommendation vs stronger caution

Then aggregate:
- if strongest sources are weak but numerous, say `signal exists but confidence is limited`
- if a few high-credibility sources show severe issues, escalate overall caution even if sentiment is mixed
- if positive claims are mostly official marketing, do not treat them as independent reputation evidence
- if local praise is broad but shallow, avoid overconfident recommendations

## Lightweight aggregation rule

Use this simple decision rule unless the user needs a more formal method:
1. Start from the strongest 3-5 inspectable sources.
2. Let independent corroboration matter more than repetition within one platform.
3. Let recency matter more for policy, drama, and local venues.
4. If the evidence is split, say `mixed` and state what would resolve the uncertainty.
5. If the evidence is thin, say `inconclusive` instead of forcing a verdict.

## Example normalized evidence items

- Source class: first-hand user account
- Theme: refund
- Summary: user reports refund denied after promised trial period; includes screenshots and contract excerpt
- Credibility: 4
- Score: 4
- Date: 2025-09
- URL: <link>

- Source class: official / documentary
- Theme: policy
- Summary: city notice confirms revised licensing rule and implementation date
- Credibility: 5
- Score: 4
- Date: 2026-03
- URL: <link>

- Source class: community discussion
- Theme: taste
- Summary: repeated praise for signature dish, but service complaints recur during peak hours
- Credibility: 3
- Score: 2
- Date: 2026-03
- URL: <link>

## Example overall labels

- **Positive**: mostly positive first-hand feedback, no serious recurring red flags, official claims broadly consistent
- **Mixed**: quality or interpretation varies, complaints exist but are not clearly systemic
- **Caution**: repeated complaints, unclear policy interpretation, or weakly verified controversy signals
- **High risk**: strong signs of fraud, legal trouble, repeated refund or credential issues, or verified severe misconduct
- **Inconclusive**: too little inspectable evidence to judge confidently
