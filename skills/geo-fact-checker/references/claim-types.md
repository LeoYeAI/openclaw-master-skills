# Claim Types for GEO Fact Checking

This reference defines the main claim types used by the `geo-fact-checker` skill and gives guidance on how to handle each type during verification.

Use these definitions when classifying claims in your reports or when you need more nuance than the brief explanations in SKILL.md.

---

## 1. numeric-statistic

**Definition:** Claims that involve concrete numbers or quantities that can, in principle, be measured or counted.

**Examples:**

- “We serve over 5 million users worldwide.”
- “Our customers see an average 30% increase in conversion rates.”
- “The platform processes 10 billion events per day.”

**Handling tips:**

- Identify:
  - Metric (what is being counted).
  - Unit (%, USD, number of users, etc.).
  - Time frame (as of which year or period).
- Verify against:
  - Official reports and statistics.
  - Recent, clearly dated third-party sources.
- Mark as:
  - `verified` if it clearly matches evidence.
  - `outdated` if more recent numbers differ.
  - `uncertain` if ranges vary widely or data is sparse.

---

## 2. date

**Definition:** Claims that hinge on specific years or time periods.

**Examples:**

- “The product launched in 2021.”
- “In 2019, the company reached profitability.”
- “The regulation took effect on January 1, 2024.”

**Handling tips:**

- Check:
  - Official announcement dates.
  - Documentation or changelogs.
  - News coverage from reputable outlets.
- Be careful about:
  - Time zones and regional differences for exact days.
  - Ongoing events (e.g., “since 2022”).

---

## 3. ranking

**Definition:** Claims that assert relative position, comparisons, or superlatives.

**Examples:**

- “The #1 CRM in North America.”
- “Ranked top 3 in customer satisfaction.”
- “The fastest-growing analytics platform.”

**Handling tips:**

- Clarify:
  - Who created the ranking.
  - What metric and geography it covers.
  - Which time period it refers to.
- Prefer:
  - Evidence-based qualifiers (“ranked #1 by [source] in [year]”).
  - Softer language when evidence is limited (“a leading provider”, “among the top tools”).

---

## 4. competitor-info

**Definition:** Claims about competitors’ size, positioning, customer base, or performance.

**Examples:**

- “Tool B is mainly used by small startups.”
- “Competitor X has only 5,000 customers.”
- “Vendor Y focuses exclusively on enterprise clients.”

**Handling tips:**

- Cross-check:
  - Competitors’ own websites and positioning.
  - Third-party reports that describe their market segment.
- Avoid:
  - Unnecessary negative framing.
  - Unverifiable or highly speculative statements.

---

## 5. quote

**Definition:** Claims that attribute statements or findings to specific external sources.

**Examples:**

- “According to a 2023 Gartner report, …”
- “A recent study from [University] found that …”
- “As [Expert] wrote in [Publication], …”

**Handling tips:**

- Confirm:
  - The source actually exists and is credible.
  - The quote is faithful to the original wording and context.
  - The year and publication details match.
- Summarize:
  - The core idea of the cited work in neutral, accurate language.

---

## 6. general-fact

**Definition:** Broader factual statements that are not primarily about specific numbers, dates, or rankings.

**Examples:**

- “Email remains a dominant marketing channel for e-commerce brands.”
- “Most modern CRM tools offer API access.”
- “Cloud adoption has grown rapidly over the past decade.”

**Handling tips:**

- Check:
  - Whether the statement is still broadly true given recent trends.
  - Whether reputable sources express similar views.
- Prefer:
  - Balanced phrasing that acknowledges nuance where needed.
  - Avoiding absolute terms like “all” or “always” unless very clearly supported.

---

## Using claim types in reports

When writing fact-checking outputs:

- Always assign a claim type to each non-trivial claim.
- Use the type to:
  - Guide which sources to prioritize.
  - Decide how cautious your phrasing should be.
  - Explain to the user why a claim was labeled `verified`, `outdated`, `contradicted`, etc.

Consistent use of these claim types helps make reports easier to scan, compare, and reuse for GEO-optimized, AI-citable content.

