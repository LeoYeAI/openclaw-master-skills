# Search Strategies - Best Practices

Advanced strategies for effective web research using Nimble Search API.

## Table of Contents

1. [Query Construction](#query-construction)
2. [Multi-Step Research](#multi-step-research)
3. [Domain Filtering](#domain-filtering)
4. [Temporal Strategies](#temporal-strategies)
5. [Result Optimization](#result-optimization)
6. [Answer Generation](#answer-generation)
7. [Content Extraction](#content-extraction)
8. [Error Recovery](#error-recovery)

---

## Query Construction

### Principles of Effective Queries

**Be Specific**
- ❌ "machine learning"
- ✅ "supervised learning algorithms for image classification"

**Include Context**
- ❌ "async patterns"
- ✅ "async/await error handling patterns in Node.js"

**Use Natural Language**
- ❌ "kubernetes +deployment -docker"
- ✅ "how to deploy applications to Kubernetes without Docker"

**Specify Intent**
- Add "tutorial", "example", "guide" for learning
- Add "comparison", "vs", "alternatives" for evaluation
- Add "best practices", "patterns" for architectural guidance

### Query Patterns by Goal

**Learning New Technology**
```
Pattern: "[Technology] [concept] tutorial with examples"
Example: "React hooks tutorial with practical examples"
Focus: coding
Max Results: 10
Answer: false (want multiple perspectives)
```

**Troubleshooting**
```
Pattern: "[Error message] [context] solution"
Example: "CORS error in Next.js API routes solution"
Focus: coding
Max Results: 5-8
Answer: true (want synthesis of solutions)
```

**Research Overview**
```
Pattern: "comprehensive guide to [topic] in [year]"
Example: "comprehensive guide to AI agent frameworks in 2026"
Focus: general or coding
Max Results: 15
Answer: true
Extract Content: true
```

**Comparative Analysis**
```
Pattern: "[Option A] vs [Option B] comparison [context]"
Example: "PostgreSQL vs MySQL for high-traffic applications"
Focus: coding
Max Results: 10
Answer: true
Domain Filter: ["stackoverflow.com", "dba.stackexchange.com"]
```

**Current Events**
```
Pattern: "latest [topic] [timeframe]"
Example: "latest quantum computing breakthroughs 2026"
Focus: news
Max Results: 15
Date Filter: last 30 days
Answer: true
```

---

## Multi-Step Research

### Progressive Research Strategy

Break complex research into sequential steps:

**Step 1: Overview**
- Focus: general
- Goal: Understand landscape
- Result Limit: 10-15
- Answer: true
- Extract: false

**Step 2: Deep Dive**
- Focus: specific mode (coding, academic, etc.)
- Goal: Detailed information
- Result Limit: 15-20
- Answer: false (analyzing sources)
- Extract: true

**Step 3: Current State**
- Focus: news
- Goal: Recent developments
- Result Limit: 10
- Answer: true
- Date Filter: recent

**Step 4: Community Insights**
- Focus: social
- Goal: Real-world experiences
- Result Limit: 10-15
- Answer: false (reviewing discussions)

### Example: Research New Framework

```
# Step 1: Technical Overview
Query: "Svelte 5 complete guide and features"
Focus: coding
Max Results: 12
Answer: true
Extract Content: false

# Step 2: Code Examples
Query: "Svelte 5 runes and state management examples"
Focus: coding
Max Results: 10
Domain Filter: ["svelte.dev", "github.com"]
Answer: false
Extract Content: true

# Step 3: Recent Updates
Query: "Svelte 5 latest changes and updates"
Focus: news
Max Results: 8
Date Filter: last 60 days
Answer: true

# Step 4: Developer Opinions
Query: "developer experiences with Svelte 5"
Focus: social
Max Results: 10
Domain Filter: ["reddit.com", "news.ycombinator.com"]
Answer: false
```

### Research Workflows

**Academic Research Workflow**

```
1. Literature Discovery (academic mode)
   → Identify key papers and authors

2. Citation Tracking (general mode)
   → "papers citing [key paper title]"

3. Methodology Review (academic mode)
   → "[methodology] applied to [domain]"

4. Current Developments (news mode)
   → "recent research in [field]"

5. Synthesis
   → Generate comprehensive answer from all steps
```

**Product Selection Workflow**

```
1. Category Overview (shopping mode)
   → "[product category] options and features"

2. Technical Requirements (coding mode, if technical)
   → "technical specifications for [product]"

3. User Reviews (social mode)
   → "[product] user experiences and reviews"

4. Price Comparison (shopping mode)
   → "best deals on [product]"

5. Final Decision
   → Synthesize findings with answer generation
```

---

## Domain Filtering

### Strategic Domain Usage

**Include Domains: When to Use**

Use `include_domains` to:
- Focus on authoritative sources
- Target specific platforms
- Ensure source quality
- Reduce noise in results

**Example Use Cases**

**Technical Documentation**
```json
{
  "include_domains": [
    "docs.python.org",
    "developer.mozilla.org",
    "reactjs.org"
  ]
}
```

**Open Source Research**
```json
{
  "include_domains": [
    "github.com",
    "gitlab.com",
    "bitbucket.org"
  ]
}
```

**Academic Sources**
```json
{
  "include_domains": [
    "scholar.google.com",
    "arxiv.org",
    "pubmed.ncbi.nlm.nih.gov"
  ]
}
```

**News Outlets**
```json
{
  "include_domains": [
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "npr.org"
  ]
}
```

### Exclude Domains: When to Use

Use `exclude_domains` to:
- Remove spam or low-quality sites
- Filter out specific competitors
- Avoid paywalled content
- Eliminate duplicate sources

**Example Use Cases**

**Avoid Aggregators**
```json
{
  "exclude_domains": [
    "pinterest.com",
    "quora.com"
  ]
}
```

**Skip Paywalls**
```json
{
  "exclude_domains": [
    "medium.com",
    "nytimes.com"
  ]
}
```

**Competitive Research**
```json
{
  "exclude_domains": [
    "competitor1.com",
    "competitor2.com"
  ]
}
```

### Domain Filter Strategies

**Authoritative Sources Pattern**

Combine trusted domains with broad query:

```json
{
  "query": "best practices for API design",
  "focus": "coding",
  "include_domains": [
    "swagger.io",
    "martinfowler.com",
    "developers.google.com",
    "aws.amazon.com"
  ],
  "max_results": 10
}
```

**Platform-Specific Research**

Target specific platforms:

```json
{
  "query": "async programming patterns discussion",
  "focus": "social",
  "include_domains": [
    "reddit.com",
    "news.ycombinator.com",
    "dev.to"
  ],
  "max_results": 15
}
```

**Quality Control Pattern**

Exclude known low-quality sources:

```json
{
  "query": "web development tutorials",
  "focus": "coding",
  "exclude_domains": [
    "w3schools.com",  // if you prefer other sources
    "tutorialspoint.com"
  ],
  "max_results": 12
}
```

---

## Temporal Strategies

### Time Filtering Approaches

**Using time_range (Recommended)**

For simple recency filtering, use `time_range` - better UX:

```json
{
  "query": "AI agent frameworks",
  "focus": "coding",
  "time_range": "month",  // last 30 days
  "max_results": 10
}
```

Available values: `hour`, `day`, `week`, `month`, `year`

**News Monitoring with time_range**

For current events:

```json
{
  "query": "quantum computing developments",
  "focus": "news",
  "time_range": "week",  // last 7 days
  "max_results": 20
}
```

**Using start_date/end_date (Alternative)**

For precise date ranges:

```json
{
  "query": "React trends Q1 2026",
  "focus": "coding",
  "start_date": "2026-01-01",  // From January 1st
  "end_date": "2026-03-31",    // Until March 31st
  "max_results": 15
}
```

**Important:** `time_range` and `start_date`/`end_date` are mutually exclusive.

### Time-Based Research Patterns

**Trend Analysis**

Compare different time periods:

```
# Current State
Query: "serverless architecture trends"
Date Filter: 2026-01-01
Focus: news

# Historical Context
Query: "serverless architecture adoption"
Date Filter: 2024-01-01
Focus: general

# Compare results to identify trends
```

**Technology Evolution**

Track how documentation changes:

```
# Latest Version
Query: "Python 3.12 new features"
Date Filter: 2025-01-01
Focus: coding

# Previous Version
Query: "Python 3.11 features"
Date Filter: 2024-01-01
Focus: coding
```

---

## Result Optimization

### Max Results Guidelines

**Quick Reference (5-10 results)**
- Fast searches
- Known topic
- Specific question
- Time-sensitive queries

**Standard Research (10-15 results)**
- Moderate depth needed
- Balanced speed/coverage
- Most use cases
- Comparison tasks

**Comprehensive Research (15-20 results)**
- Deep analysis required
- Multiple perspectives needed
- Academic research
- Unknown territory

**Budget Considerations**

More results = higher cost:
- Start with fewer results
- Increase if needed
- Use answer generation to synthesize fewer sources
- Cache results to avoid re-fetching

### Result Quality Optimization

**Technique 1: Iterative Refinement**

```
1. Initial Search (10 results)
2. Analyze quality
3. Refine query based on results
4. Search again with refined query
5. Compare and synthesize
```

**Technique 2: Multi-Query Approach**

```
Run parallel searches with variations:
- Different focus modes
- Different phrasings
- Different date ranges
- Merge and deduplicate results
```

**Technique 3: Hierarchical Search**

```
1. Broad query (general understanding)
2. Specific queries (deep dives)
3. Related queries (peripheral knowledge)
4. Synthesis (combine all insights)
```

---

## Answer Generation

### When to Generate Answers

**✅ Generate answers for:**

1. **Synthesis Tasks**
   - Combining multiple sources
   - Comparative analysis
   - Summarizing developments

2. **Overview Requests**
   - Topic introductions
   - Concept explanations
   - "What is X?" queries

3. **Decision Support**
   - "Should I use X or Y?"
   - "Best approach for Z?"
   - Recommendation requests

4. **Current Events**
   - News summaries
   - Trend analysis
   - Recent developments

**❌ Skip answers for:**

1. **Resource Collection**
   - Building reading lists
   - Gathering references
   - Link aggregation

2. **Original Source Needed**
   - Legal/regulatory info
   - Academic citations
   - Official documentation

3. **Manual Analysis Required**
   - Deep technical review
   - Code analysis
   - Detailed comparison

4. **Speed Critical**
   - Quick lookups
   - Simple fact checks
   - URL discovery only

### Answer Quality Tips

**Provide Context in Query**

❌ Poor: "machine learning"
✅ Good: "explain machine learning concepts for software engineers with examples"

**Specify Answer Format**

- Add "with examples" for concrete cases
- Add "step-by-step" for procedures
- Add "comparison" for evaluations
- Add "pros and cons" for balanced view

**Optimize Result Count**

- 10-15 results: Good answer quality
- 5-8 results: Fast but may lack depth
- 15-20 results: Comprehensive but slower

**Combine with Content Extraction**

For best answers, enable content extraction:

```json
{
  "query": "comprehensive guide to Web Workers",
  "focus": "coding",
  "max_results": 12,
  "include_answer": true,
  "deep_search": true  // More context for better answers
}
```

---

## Content Extraction

### When to Extract Content

**✅ Extract content for:**

1. **Deep Analysis**
   - Detailed research
   - Content archiving
   - Full-text search
   - Data collection

2. **Answer Generation**
   - Better LLM context
   - Improved synthesis
   - Complete information

3. **Offline Usage**
   - Save for later
   - Build knowledge base
   - Archive research

**❌ Skip extraction for:**

1. **Quick Searches**
   - URL collection only
   - Fast overview
   - Title/description sufficient

2. **Link Building**
   - Reference lists
   - Resource compilation
   - Bookmark gathering

3. **Cost/Speed Concerns**
   - High-volume searches
   - Tight budgets
   - Time-sensitive queries

### Parsing Format Selection

**Markdown (Recommended Default)**
- Best readability
- Preserves structure
- Good for LLM processing
- Maintains links

**Plain Text**
- Fastest processing
- Smallest size
- Strip all formatting
- Best for analysis/indexing

**Simplified HTML**
- Preserves some structure
- Good for display
- Maintains semantic elements
- Useful for republishing

### Extraction Strategies

**Progressive Extraction**

```
1. Search without extraction (get URLs)
2. Review titles/descriptions
3. Extract content for promising URLs only
4. Analyze extracted content
```

**Selective Extraction**

```json
{
  "query": "React performance optimization",
  "focus": "coding",
  "max_results": 15,
  "deep_search": true,
  "include_domains": [
    "reactjs.org",  // Only extract from trusted sources
    "web.dev"
  ]
}
```

---

## Error Recovery

### Common Error Scenarios

**No Results Found**

Recovery strategies:
1. Broaden query (remove specific terms)
2. Try different focus mode
3. Remove domain filters
4. Adjust date filter
5. Check for typos

**Timeout / Slow Response**

Recovery strategies:
1. Reduce max_results
2. Disable content extraction
3. Remove deep content options
4. Try simpler query
5. Retry after delay

**Rate Limit Exceeded**

Recovery strategies:
1. Add delays between requests
2. Reduce result counts
3. Cache results
4. Batch queries
5. Upgrade API tier

**Poor Result Quality**

Recovery strategies:
1. Change focus mode
2. Add domain filters
3. Refine query phrasing
4. Add more context
5. Use multi-step approach

### Retry Logic

**Exponential Backoff Pattern**

```
Attempt 1: Immediate
Attempt 2: Wait 1 second
Attempt 3: Wait 2 seconds
Attempt 4: Wait 4 seconds
Attempt 5: Wait 8 seconds
Max Attempts: 5
```

**Progressive Simplification**

```
Try 1: Full query with all options
Try 2: Remove content extraction
Try 3: Reduce max_results by half
Try 4: Remove domain filters
Try 5: Simplify query, basic options
```

### Error Handling Best Practices

1. **Log Errors**: Track failures for pattern analysis
2. **Graceful Degradation**: Fallback to simpler searches
3. **User Feedback**: Inform about issues and retries
4. **Cache Successes**: Save good results
5. **Monitor Patterns**: Identify systematic issues

---

## Advanced Patterns

### The Research Sandwich

Combine multiple strategies:

```
1. Broad Overview (general, 10 results, answer)
2. Specific Deep Dives (specific focus, 15 results, extract)
3. Current State (news, 8 results, answer)
4. Synthesis (combine all findings)
```

### The Domain Ladder

Progress through source quality:

```
1. General web (general focus)
2. Curated domains (with include filter)
3. Official docs only (strict domain filter)
4. Primary sources (academic/official)
```

### The Time Machine

Temporal analysis pattern:

```
1. Current (last 30 days)
2. Recent (last year)
3. Historical (2+ years ago)
4. Compare evolution
```

---

## Conclusion

Effective search strategies combine:
- Thoughtful query construction
- Appropriate focus mode selection
- Strategic domain filtering
- Smart result optimization
- Intentional answer generation
- Selective content extraction
- Robust error handling

Master these patterns to maximize research efficiency and result quality.
