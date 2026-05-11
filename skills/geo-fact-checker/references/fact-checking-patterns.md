# Fact-Checking Patterns for GEO Content

This reference file describes reusable patterns and checklists for using the `geo-fact-checker` skill effectively, especially for AI-citable content and GEO (Generative Engine Optimization).

Use these patterns when the main SKILL.md instructions are not specific enough for the task at hand.

---

## 1. Numeric statistics pattern

**Goal:** Safely handle numbers that affect trust (user counts, revenue, growth, ROI, etc.).

### Checklist

- Identify:
  - What is being measured? (users, customers, revenue, traffic, etc.).
  - Which unit? (USD, %, monthly active users, annual revenue, etc.).
  - Time frame? (as of 2020, Q4 2025, last 12 months, etc.).
  - Scope? (global, US, EMEA, specific niche or industry).
- Search for:
  - Official company reports, investor decks, or press releases.
  - Recent third-party reports from credible firms or research orgs.
  - Government or standards bodies for macro statistics.
- Compare:
  - Is the number within a reasonable range of reported values?
  - Are there known updates (e.g., “5M in 2020, 8M in 2024”)?

### Recommended phrasing tactics

- Add time qualifiers:
  - “As of 2024, …”
  - “Between 2021 and 2023, …”
- Avoid false precision:
  - Prefer “about 5 million” over “5,023,871” when not quoting a precise report.
- Clearly attribute to sources when appropriate:
  - “According to [source name], …”

---

## 2. Rankings and “#1” claims pattern

**Goal:** Prevent unsupported or misleading “#1” and “top X” statements.

### Checklist

- Clarify:
  - Ranking according to whom? (which report, which dataset).
  - Ranking for what metric? (revenue, users, traffic, satisfaction).
  - Ranking where? (global vs. regional).
  - Time period? (which year or report cycle).
- Search for:
  - Widely cited rankings from industry analysts or research firms.
  - Multiple independent sources to confirm consistency.

### Safer alternative phrasing

- When support is weak or mixed:
  - “a leading platform for …”
  - “one of the most widely used tools for …”
  - “frequently ranked among the top [N] in …”
- When you have strong, specific evidence:
  - “Ranked #1 by [report name] in [year] for [metric] in [region].”

Avoid absolute, context-free claims like “the #1 tool in the world” unless the evidence is exceptionally clear and unambiguous (this is rare).

---

## 3. Competitor and comparison pattern

**Goal:** Keep competitor descriptions fair, accurate, and defensible.

### Checklist

- For each competitor claim:
  - Identify exactly what is being asserted (size, market segment, positioning).
  - Search for the competitor’s own description and third-party views.
  - Check that the claim does not rely on outdated or cherry-picked data.
- Pay special attention to:
  - Extreme statements (“only”, “always”, “never”).
  - Statements that may be perceived as misleading or defamatory.

### Safer comparative language

- Prefer:
  - “Popular among …”
  - “Commonly used by …”
  - “Positions itself as …”
- For direct comparisons:
  - “Compared with [competitor], [product] focuses more on …”
  - “In [specific report], [product] received higher scores than [competitor] for [metric].”

---

## 4. Time and recency pattern

**Goal:** Make it clear when a claim is anchored in time and avoid silent drift as years pass.

### Checklist

- Identify all date-sensitive claims:
  - User counts, revenue, market share.
  - Product launch dates.
  - Regulatory or standard changes.
- For each date-sensitive claim:
  - Confirm whether the value is still accurate today.
  - If not, decide whether to:
    - Preserve it as a historical statement, or
    - Update to a more recent value.

### Phrasing guidelines

- Historical:
  - “In 2019, the company reached …”
  - “Between 2018 and 2020, …”
- Current:
  - “As of 2026, the platform serves …”
  - “Recent reports from [year] indicate …”

When the user does not specify, prefer current data for “today” claims and explicit years for historical context.

---

## 5. Source evaluation pattern

**Goal:** Prioritize high-quality sources and be transparent about limitations.

### Preferred source types

- Official:
  - Company sites, investor relations pages, official blogs.
  - Government data portals.
  - Recognized standards organizations.
- Reputable third parties:
  - Known market research firms.
  - Major news outlets with fact-checking processes.

### Watch out for

- Scraped content farms with weak editorial standards.
- Undated or poorly dated pages.
- Single, uncorroborated sources for controversial claims.

When in doubt, mark a claim as `uncertain` rather than fabricating certainty.

---

## 6. Risk and sensitivity pattern

**Goal:** Handle sensitive domains with extra care.

Particularly cautious domains:

- Health and medicine.
- Finance and investment advice.
- Legal or regulatory guidance.
- Safety-critical technologies.

In these domains:

- Prefer conservative phrasing:
  - “may help”, “is associated with”, “is often used for”.
- Encourage consultation of primary experts or official guidelines.
- Clearly mark limitations of your verification and knowledge.

---

## 7. GEO and AI citation alignment

**Goal:** Make fact-checked content as easy as possible for AI systems to understand and reuse accurately.

Guidelines:

- Use clear, explicit, and self-contained sentences for key facts.
- Attach time markers (`as of [year]`) to numbers that may change.
- Avoid mixing multiple claims into a single long sentence; separate them.
- Prefer stable concepts and reputable entities in your evidence summaries.

By following these patterns, you increase the likelihood that AI systems will:

- Correctly interpret the scope and reliability of your claims.
- Reuse your content without distorting or overstating its conclusions.
- Cite your pages as trustworthy references for factual questions.

