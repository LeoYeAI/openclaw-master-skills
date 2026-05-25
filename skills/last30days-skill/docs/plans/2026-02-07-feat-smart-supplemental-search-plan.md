---
title: "feat: Smart Supplemental Search — Entity-Aware Secondary Passes for Reddit & X"
type: feat
date: 2026-02-07
---

# feat: Smart Supplemental Search — Entity-Aware Secondary Passes for Reddit & X

## Overview

Add an intelligent "discover → drill down" second pass to both Reddit and X searches. After the initial broad search, extract entities (handles, subreddits, hashtags) from results and run targeted secondary searches to surface content the broad pass missed. This supplements — does not replace — the existing search pipeline.

## Problem Statement / Motivation

The current search pipeline does a single broad pass per source (with Reddit having 2 fallbacks for low-result scenarios). This works well for general topics, but misses content that lives in:

- **Niche subreddits** that don't rank for generic queries (e.g., searching "Nano Banana Pro" finds r/generativeAI but misses r/nanobanana, r/localLLaMA)
- **Key accounts on X** that are the authorities on a topic but whose individual posts don't rank for broad keyword search (e.g., @steipete for Open Claw, @karpathy for AI training)
- **Conversation threads** where the most valuable discussion happens in replies, not the original tweet

The product works great today. This is about squeezing 20-30% more high-quality results from sources we already have access to.

## Proposed Solution

### Architecture: Two-Phase Search

```
CURRENT (Phase 1 — unchanged):
  Broad topic search → Reddit results + X results
                                    ↓
NEW (Phase 2 — supplemental):
  Extract entities from Phase 1 results
       ↓                    ↓
  [SUBREDDITS]        [@HANDLES + #HASHTAGS]
       ↓                    ↓
  Targeted Reddit     Targeted X searches
  searches per sub    per handle/hashtag
       ↓                    ↓
  Merge + dedupe with Phase 1 results
```

Phase 2 only runs if Phase 1 returned results (entities need to come from somewhere). Phase 2 results are merged and deduped against Phase 1 — the existing `dedupe.py` handles this.

### Feature 1: Entity Extraction Module (NEW FILE)

**File: `scripts/lib/entity_extract.py`**

A lightweight module that parses Phase 1 results and extracts:

**From X results:**
- `@handles` — from `author_handle` field + any @mentions in post text
- `#hashtags` — from post text
- Rank by frequency: handles that appear 2+ times are "key voices"

**From Reddit results:**
- `subreddit` names — from the `subreddit` field on each result
- Cross-referenced subreddits — from enriched comment text mentioning "r/othersub"
- Rank by frequency: subreddits with 2+ threads are "core communities"

**Output:**
```python
{
    "x_handles": ["steipete", "openclaw", "karpathy"],  # ranked by frequency
    "x_hashtags": ["#openclaw", "#aitools"],
    "reddit_subreddits": ["generativeAI", "localLLaMA", "nanobanana"],
    "reddit_cross_refs": ["singularity", "MachineLearning"],  # mentioned in comments
}
```

**Rules:**
- No hardcoded entities — everything discovered dynamically from Phase 1
- Cap at top 5 handles, top 3 hashtags, top 5 subreddits
- Skip generic handles (@elonmusk, @OpenAI) that appear everywhere — maintain a small exclusion list of "too common" handles (< 20 entries)
- Skip the original topic's "obvious" subreddit if it was already searched

### Feature 2: Supplemental X Search (Bird)

**File: modify `scripts/lib/bird_x.py`**

Add a `search_handles()` function:

```python
def search_handles(handles: list[str], topic: str, from_date: str, count_per: int = 5) -> list:
    """Search top handles for topic-related content."""
    results = []
    for handle in handles[:5]:
        # Uses Bird's support for X search operators
        query = f"from:{handle} {topic} since:{from_date}"
        cmd = ["bird", "search", query, "-n", str(count_per), "--json"]
        # ... parse results, add to list
    return results
```

**Why Bird, not xAI:** Bird is free (uses your X login). Running 5 secondary searches via xAI would cost ~$0.025 per run, which adds up. Bird costs nothing.

**xAI alternative for users without Bird:** If Bird is not available but xAI is, use `allowed_x_handles` parameter:

```python
# xAI supports filtering to specific handles (max 10)
tools = [{
    "type": "x_search",
    "x_handles": {"allowed_x_handles": top_handles[:10]}
}]
```

### Feature 3: Supplemental Reddit Search

**File: modify `scripts/lib/openai_reddit.py`**

Add a `search_subreddits()` function:

```python
def search_subreddits(subreddits: list[str], topic: str, ...) -> list:
    """Search discovered subreddits for topic-related content."""
    # Build multi-subreddit query for the OpenAI web_search prompt
    sub_query = " OR ".join(f"r/{sub}" for sub in subreddits[:5])
    prompt = f"Search Reddit for threads about {topic} in these communities: {sub_query}"
    # ... single OpenAI API call, same pattern as existing search
```

**Alternative approach — Reddit JSON API (free, no API key):**

```python
def search_subreddit_json(subreddit: str, topic: str) -> list:
    """Search a specific subreddit via Reddit's free JSON endpoint."""
    url = f"https://www.reddit.com/r/{subreddit}/search/.json"
    params = {"q": topic, "restrict_sr": "on", "sort": "new", "limit": 10}
    # ... parse JSON response
```

This is free, requires no API key, and gives us structured data. The `.json` endpoint trick is well-documented and widely used.

### Feature 4: Orchestration Changes

**File: modify `scripts/last30days.py`**

After Phase 1 completes and enrichment is done, run Phase 2:

```python
# Phase 1 (existing — unchanged)
reddit_items, x_items = run_parallel_search(...)

# Phase 2 (new — supplemental)
if reddit_items or x_items:
    entities = entity_extract.extract(reddit_items, x_items)

    supplemental_reddit = []
    supplemental_x = []

    # Run supplemental searches in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        if entities["reddit_subreddits"]:
            reddit_future = executor.submit(
                openai_reddit.search_subreddits,
                entities["reddit_subreddits"], topic, ...
            )
        if entities["x_handles"] and bird_available:
            x_future = executor.submit(
                bird_x.search_handles,
                entities["x_handles"], topic, from_date, ...
            )

    # Merge with Phase 1
    all_reddit = reddit_items + supplemental_reddit
    all_x = x_items + supplemental_x

    # Dedupe handles the rest
```

**Depth-dependent behavior:**
| Depth | Phase 2 behavior |
|---|---|
| `--quick` | Skip Phase 2 entirely (speed matters) |
| default | Run Phase 2 with caps: 3 handles, 3 subreddits, 3 results each |
| `--deep` | Run Phase 2 with caps: 5 handles, 5 subreddits, 5 results each |

### Feature 5: Thread Expansion for High-Engagement Posts (stretch goal)

**File: modify `scripts/lib/bird_x.py`**

For X posts with very high engagement (top 1-2 by likes), expand the conversation thread:

```python
def expand_thread(tweet_id: str) -> list:
    """Fetch full thread for a high-engagement tweet."""
    cmd = ["bird", "thread", tweet_id, "--json"]
    # ... parse thread, extract key replies
```

This surfaces the discussion around viral posts — often more valuable than the original tweet. Only trigger for posts with 100+ likes to avoid noise.

## Technical Considerations

### Performance
- Phase 2 adds 2-5 seconds for Bird (5 subprocess calls) and 3-8 seconds for Reddit subreddit search (1 API call)
- On `--quick` mode, Phase 2 is skipped entirely — zero performance impact
- Phase 2 runs AFTER Phase 1, not in parallel with it (needs Phase 1 results for entity extraction)

### Cost
- Reddit subreddit search: 1 additional OpenAI API call (~$0.005) OR free via `.json` endpoint
- X handle search via Bird: Free (uses your X login)
- X handle search via xAI (fallback): 1 additional API call (~$0.005)
- Thread expansion: Free via Bird

### No New Dependencies
- Entity extraction is string parsing — no NLP libraries needed
- Reddit `.json` endpoint uses existing `http.py` transport
- Bird CLI calls use existing subprocess pattern from `bird_x.py`

### Backward Compatibility
- Phase 2 is purely additive — all existing behavior unchanged
- If Phase 2 finds nothing, output is identical to current
- Deduplication handles any overlap between Phase 1 and Phase 2

## Acceptance Criteria

- [x] Entity extraction module correctly parses handles, hashtags, and subreddits from search results
- [x] Supplemental X searches via Bird find additional content from key handles
- [x] Supplemental Reddit searches find content in discovered subreddits
- [x] Phase 2 results are properly merged and deduped with Phase 1
- [x] `--quick` mode skips Phase 2 entirely
- [x] `--deep` mode searches more handles/subreddits with higher per-query limits
- [x] No performance regression on `--quick` mode
- [ ] Default mode adds < 10 seconds of latency
- [x] Works with Bird-only, xAI-only, and both-available configurations
- [x] Output format unchanged (Phase 2 results look identical to Phase 1 results)

## Implementation Order

1. `scripts/lib/entity_extract.py` — Entity extraction from results (new file)
2. `scripts/lib/bird_x.py` — Add `search_handles()` function
3. `scripts/lib/openai_reddit.py` — Add `search_subreddits()` function
4. `scripts/last30days.py` — Orchestration: Phase 2 after Phase 1
5. Test with real queries: "Open Claw", "Nano Banana Pro", "kanye west"
6. (Stretch) Thread expansion for high-engagement posts

## Research Sources

### Reddit Search Techniques
- [reddit-research-mcp](https://github.com/king-of-the-grackles/reddit-research-mcp) — MCP server with semantic subreddit discovery via 20K+ pre-indexed communities
- [anvaka/sayit](https://github.com/anvaka/sayit) — Subreddit similarity graph via collaborative filtering (Jaccard similarity on user overlap)
- [YARS](https://github.com/datavorous/yars) — No-API-key Reddit scraper using `.json` endpoint trick
- Reddit's free JSON search endpoint: `reddit.com/r/{sub}/search/.json?q=QUERY&restrict_sr=on` — no auth needed
- Reddit search operators: `subreddit:`, `title:`, `selftext:`, `author:`, `flair:` (Lucene-style)

### X/Twitter Search Techniques
- [igorbrigadir/twitter-advanced-search](https://github.com/igorbrigadir/twitter-advanced-search) — Canonical reference of all X search operators
- Bird CLI supports all X operators: `from:`, `to:`, `conversation_id:`, `min_retweets:`, `#hashtag`, `list:`
- xAI x_search `allowed_x_handles` parameter — filter to max 10 specific handles
- xAI x_search semantic search — finds conceptually related content without exact keyword matches
- [Bellingcat OSINT Toolkit](https://bellingcat.gitbook.io/toolkit) — Multi-pass handle discovery methodology

### Key Insight
The biggest gap in the current implementation is that **neither X nor Reddit search does entity extraction from initial results to inform follow-up queries.** Every tool/project researched that achieves better-than-basic results does some form of "discover entities → search entities" two-pass strategy.

## What We're NOT Doing

- **Not adding new API dependencies** — everything uses existing OpenAI, xAI, or Bird infrastructure
- **Not adding NLP/ML libraries** — entity extraction is simple string parsing
- **Not changing the output format** — Phase 2 results merge seamlessly
- **Not hardcoding any entities** — all discovery is dynamic from search results
- **Not slowing down `--quick` mode** — Phase 2 is skipped entirely
- **Not replacing the current search** — Phase 2 supplements Phase 1
