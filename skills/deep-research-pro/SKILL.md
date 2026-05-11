---
name: deep-research-pro
version: 1.0.0
description: "Multi-source deep research agent. Searches the web, synthesizes findings, and delivers cited reports. No API keys required."
homepage: https://github.com/paragshah/deep-research-pro
metadata: {"clawdbot":{"emoji":"🔬","category":"research"}}
---

# Deep Research Pro 🔬

A powerful, self-contained deep research skill that produces thorough, cited reports from multiple web sources. No paid APIs required — uses DuckDuckGo search.

## How It Works

When the user asks for research on any topic, follow this workflow:

### Step 1: Understand the Goal (30 seconds)

Ask 1-2 quick clarifying questions:
- "What's your goal — learning, making a decision, or writing something?"
- "Any specific angle or depth you want?"

If the user says "just research it" — skip ahead with reasonable defaults.

### Step 2: Plan the Research (think before searching)

Break the topic into 3-5 research sub-questions. For example:
- Topic: "Impact of AI on healthcare"
  - What are the main AI applications in healthcare today?
  - What clinical outcomes have been measured?
  - What are the regulatory challenges?
  - What companies are leading this space?
  - What's the market size and growth trajectory?

### Step 3: Execute Multi-Source Search

For EACH sub-question, run the DDG search script:

```bash
# Web search
/home/clawdbot/clawd/skills/ddg-search/scripts/ddg "<sub-question keywords>" --max 8

# News search (for current events)
/home/clawdbot/clawd/skills/ddg-search/scripts/ddg news "<topic>" --max 5
```

**Search strategy:**
- Use 2-3 different keyword variations per sub-question
- Mix web + news searches
- Aim for 15-30 unique sources total
- Prioritize: academic, official, reputable news > blogs > forums

### Step 4: Deep-Read Key Sources

For the most promising URLs, fetch full content:

```bash
curl -sL "<url>" | python3 -c "
import sys, re
html = sys.stdin.read()
# Strip tags, get text
text = re.sub('<[^>]+>', ' ', html)
text = re.sub(r'\s+', ' ', text).strip()
print(text[:5000])
"
```

Read 3-5 key sources in full for depth. Don't just rely on search snippets.

### Step 5: Synthesize & Write Report

Structure the report as:

```markdown
# [Topic]: Deep Research Report
*Generated: [date] | Sources: [N] | Confidence: [High/Medium/Low]*

## Executive Summary
[3-5 sentence overview of key findings]

## 1. [First Major Theme]
[Findings with inline citations]
- Key point ([Source Name](url))
- Supporting data ([Source Name](url))

## 2. [Second Major Theme]
...

## 3. [Third Major Theme]
...

## Key Takeaways
- [Actionable insight 1]
- [Actionable insight 2]
- [Actionable insight 3]

## Sources
1. [Title](url) — [one-line summary]
2. ...

## Methodology
Searched [N] queries across web and news. Analyzed [M] sources.
Sub-questions investigated: [list]
```

### Step 6: Save & Deliver

Save the full report:
```bash
mkdir -p ~/clawd/research/[slug]
# Write report to ~/clawd/research/[slug]/report.md
```

Then deliver:
- **Short topics**: Post the full report in chat
- **Long reports**: Post the executive summary + key takeaways, offer full report as file

## Quality Rules

1. **Every claim needs a source.** No unsourced assertions.
2. **Cross-reference.** If only one source says it, flag it as unverified.
3. **Recency matters.** Prefer sources from the last 12 months.
4. **Acknowledge gaps.** If you couldn't find good info on a sub-question, say so.
5. **No hallucination.** If you don't know, say "insufficient data found."

## Examples

```
"Research the current state of nuclear fusion energy"
"Deep dive into Rust vs Go for backend services in 2026"
"Research the best strategies for bootstrapping a SaaS business"
"What's happening with the US housing market right now?"
```

## For Sub-Agent Usage

When spawning as a sub-agent, include the full research request and context:

```
sessions_spawn(
  task: "Run deep research on [TOPIC]. Follow the deep-research-pro SKILL.md workflow.
  Read /home/clawdbot/clawd/skills/deep-research-pro/SKILL.md first.
  Goal: [user's goal]
  Specific angles: [any specifics]
  Save report to ~/clawd/research/[slug]/report.md
  When done, wake the main session with key findings.",
  label: "research-[slug]",
  model: "opus"
)
```

## Requirements

- DDG search script: `/home/clawdbot/clawd/skills/ddg-search/scripts/ddg`
- curl (for fetching full pages)
- No API keys needed!
