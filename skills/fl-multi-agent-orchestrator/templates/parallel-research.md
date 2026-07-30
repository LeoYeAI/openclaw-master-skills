# Parallel Research Template (Fan-Out / Fan-In)

## Overview
Spawn N agents to research different aspects of a topic simultaneously, then aggregate results into a single deliverable.

## When to Use
- Market research across multiple dimensions
- Competitor analysis (each agent covers one competitor)
- Multi-source data gathering
- Any task where N independent research queries can run in parallel

## Configuration

```yaml
orchestration:
  pattern: fan-out-fan-in
  max_concurrent: 5
  budget_usd: 3.00
  timeout_minutes: 15

agents:
  researcher:
    model: sonnet
    tools: [Read, Grep, Glob, WebSearch, WebFetch]
    max_turns: 15
    budget_usd: 0.50

  aggregator:
    model: opus
    tools: [Read, Write, Edit]
    max_turns: 10
    budget_usd: 0.50
```

## Execution Plan

### Phase 1: Decompose
The planner identifies N independent research dimensions.

Example for "Analyze the AI code assistant market":
```json
{
  "research_dimensions": [
    {"id": "r1", "topic": "Competitor products and features", "agent": "researcher"},
    {"id": "r2", "topic": "Pricing models and revenue estimates", "agent": "researcher"},
    {"id": "r3", "topic": "User sentiment and community feedback", "agent": "researcher"},
    {"id": "r4", "topic": "Technical architecture and limitations", "agent": "researcher"},
    {"id": "r5", "topic": "Market trends and growth projections", "agent": "researcher"}
  ]
}
```

### Phase 2: Fan-Out (Parallel Execution)
Each researcher agent gets a focused prompt:

```
You are Research Agent [N] in a parallel research team of 5.

YOUR ASSIGNMENT: [specific research dimension]

INSTRUCTIONS:
1. Research this specific topic thoroughly
2. Use WebSearch and WebFetch for current data
3. Structure your findings in the output format below
4. DO NOT research topics assigned to other agents
5. Cite your sources

OUTPUT FORMAT:
## [Topic Name]

### Key Findings
- Finding 1 (source: URL)
- Finding 2 (source: URL)
- Finding 3 (source: URL)

### Data Points
| Metric | Value | Source |
|--------|-------|--------|

### Analysis
[2-3 paragraph analysis of what the data means]

### Confidence Level
[HIGH/MEDIUM/LOW] — [brief justification]
```

### Phase 3: Fan-In (Aggregation)
The aggregator receives all research outputs and synthesizes:

```
You are the Research Aggregator.

You have received research from 5 parallel agents. Your job:
1. Read all 5 research outputs
2. Cross-reference findings — flag contradictions
3. Synthesize into a single coherent report
4. Identify gaps — what wasn't covered?
5. Produce executive summary + detailed sections

OUTPUT STRUCTURE:
## Executive Summary (3-5 bullet points)
## Key Findings by Dimension
## Cross-Cutting Themes
## Contradictions and Uncertainties
## Recommendations
## Gaps for Further Research
```

## Error Handling

| Scenario | Response |
|----------|----------|
| Agent fails to return results | Aggregator notes the gap; report mentions missing dimension |
| Agent returns low-confidence data | Aggregator flags as unverified |
| Budget hit before all agents finish | Aggregate available results; note incomplete dimensions |
| Conflicting data between agents | Aggregator evaluates sources and picks the more credible one |

## Cost Estimate
- 5 researcher agents (Sonnet): ~$0.10-0.30 each = $0.50-1.50
- 1 aggregator agent (Opus): ~$0.20-0.50
- **Total: $0.70-2.00** for comprehensive multi-dimensional research

## Real-World Example: YouTube Niche Research

```json
{
  "task": "Research the best YouTube niches for high CPM in 2026",
  "agents": [
    {"id": "r1", "topic": "Top 20 niches by CPM with current rates"},
    {"id": "r2", "topic": "Audience demographics and advertiser demand per niche"},
    {"id": "r3", "topic": "Competition level — channels per niche, saturation index"},
    {"id": "r4", "topic": "Content production difficulty and automation potential"},
    {"id": "r5", "topic": "Trending niches — growth rate over last 12 months"}
  ],
  "aggregation": "Produce a ranked list of niches scored by: CPM, competition, difficulty, growth"
}
```
