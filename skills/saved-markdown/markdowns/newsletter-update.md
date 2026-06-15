# Newsletter / Update Reference

## When to Use This Template

- User asks for a newsletter, digest, update, announcement, changelog, or release notes
- Keywords: newsletter, update, digest, announcement, release notes, changelog, weekly update, monthly roundup, bulletin
- Output is a periodic communication summarizing news, changes, or highlights
- User is compiling multiple items into a single communication

---

## Structure Template

```markdown
# {Newsletter Title}

**{Edition label}** · {Date or date range}

{One-sentence hook or theme for this edition.}

---

## 🔑 Highlights

- **{Headline 1}** — {One sentence summary}
- **{Headline 2}** — {One sentence summary}
- **{Headline 3}** — {One sentence summary}

---

## {Main Story 1 Title}

{2-3 paragraphs covering the most important item. Include context, what happened, and why it matters.}

---

## {Main Story 2 Title}

{2-3 paragraphs for the second most important item.}

---

## Quick Updates

| Item | Status | Details |
|------|--------|---------|
| {Update 1} | {✅ Done / 🔄 In Progress / 📋 Planned} | {One-line detail} |
| {Update 2} | {Status} | {Detail} |
| {Update 3} | {Status} | {Detail} |

---

## 📅 Upcoming

- **{Date}** — {Event or milestone}
- **{Date}** — {Event or milestone}
- **{Date}** — {Event or milestone}

---

## 💬 Quote / Spotlight

> "{Notable quote or team spotlight}"
> — {Attribution}

---

*{Sign-off or CTA. E.g., "Questions? Reply to this page." or "See you next week!"}*
```

---

## Styling Guidelines

- **Highlights section is the TL;DR** — Write it so skimmers get the full picture without reading anything else
- **Bold the item name in highlights** — "**New API launched** — REST endpoints for billing now live" is scannable
- **Status emoji in quick updates** — ✅ Done, 🔄 In Progress, 📋 Planned, ⚠️ Blocked
- **Upcoming section with bold dates** — Dates should be the most visible element in each line
- **Consistent structure across issues** — Readers learn the layout and find information faster
- **Edition labels** — "Issue #12", "Week of March 10", "Q1 2026" — helps readers orient in a series

---

## Chart Recommendations

Charts are **occasionally useful** in newsletters, especially for metric-focused updates.

**Progress/milestone bar chart:**
```
```markdown-ui-widget
chart-bar
title: Q1 Goals Progress (%)
Goal,Progress
"Launch v2.0",100
"Hire 3 engineers",67
"1000 paying users",82
"SOC 2 certification",45
```
```

**Trend line for key metric:**
```
```markdown-ui-widget
chart-line
title: Weekly Active Users
Week,WAU
W1,2400
W2,2650
W3,2800
W4,3100
W5,3350
```
```

Limit to 1-2 charts. Newsletters should be text-forward and quick to scan.

---

## Professional Tips

1. **Highlights must stand alone** — If someone reads only the top 3 bullets, they should know everything important
2. **Consistent structure across issues** — Same sections in the same order every time. Readers learn the format.
3. **One voice, one tone** — Newsletters feel personal. Pick a voice (casual, professional, enthusiastic) and stick with it.
4. **Quick Updates table for low-priority items** — Not everything deserves a paragraph. Status tables are perfect for "need to mention but not elaborate" items.
5. **Include a forward-looking section** — "Upcoming" creates anticipation and gives readers a reason to come back
6. **Keep editions focused** — 2-3 main stories max. If you have 10 things to say, most belong in Quick Updates.
7. **Sign-off creates connection** — A brief personal note or CTA at the end makes it feel less like a broadcast

---

## Example

```markdown
# DevOps Weekly

**Issue #24** · March 10–16, 2026

This week: v2.1 shipped with the new dashboard, plus two hiring wins.

---

## 🔑 Highlights

- **v2.1 released** — New analytics dashboard and 3x faster report generation
- **Two senior engineers joined** — Platform team is now at full capacity
- **SOC 2 Type II audit scheduled** — Kickoff on April 1st with Vanta

---

## v2.1: New Analytics Dashboard

After 6 weeks of development, v2.1 is live in production. The headline feature is a completely redesigned analytics dashboard that replaces the old metrics page.

Key improvements:
- **3x faster report generation** — Reports that took 45s now render in under 15s
- **Custom date ranges** — Finally! Users can pick any date window instead of preset options
- **Export to PDF** — One-click export for all dashboard views

Rollout was smooth — zero downtime deployment via canary release. 100% of traffic is now on v2.1.

---

## Team Growth: Two New Senior Engineers

We're excited to welcome **Ana Kovacs** (infrastructure) and **David Park** (backend) to the platform team. Both start March 18th.

With these hires, we're at our target headcount of 8 for Q1. The team can now split into two workstreams: reliability (Ana's focus) and feature development (David's focus).

---

## Quick Updates

| Item | Status | Details |
|------|--------|---------|
| CI pipeline migration | ✅ Done | Fully on GitHub Actions — CircleCI decommissioned |
| Staging environment refresh | 🔄 In Progress | New staging cluster 70% provisioned |
| API rate limiting | 📋 Planned | Design doc in review, implementation starts W13 |
| Log retention policy | ⚠️ Blocked | Waiting on legal review of 90-day vs 1-year retention |

---

## 📅 Upcoming

- **Mar 18** — Ana and David's first day / team onboarding
- **Mar 22** — v2.2 sprint kickoff (focus: API rate limiting + webhook reliability)
- **Apr 1** — SOC 2 Type II audit begins
- **Apr 5** — Quarterly planning offsite (Amsterdam)

---

*Questions or feedback? Drop a message in #devops-weekly on Slack. See you next Monday!*
```
