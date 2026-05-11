---
name: reddit-readonly
description: >-
  Browse and search Reddit in read-only mode using public JSON endpoints.
  Use when the user asks to browse subreddits, search for posts by topic,
  inspect comment threads, or build a shortlist of links to review and reply to manually.
metadata: {"clawdbot":{"emoji":"🔎","requires":{"bins":["node"]}}}
---

# Reddit Readonly

Read-only Reddit browsing for Clawdbot.

## What this skill is for

- Finding posts in one or more subreddits (hot/new/top/controversial/rising)
- Searching for posts by query (within a subreddit or across all)
- Pulling a comment thread for context
- Producing a *shortlist of permalinks* so the user can open Reddit and reply manually

## Hard rules

- **Read-only only.** This skill never posts, replies, votes, or moderates.
- Be polite with requests:
  - Prefer small limits (5–10) first.
  - Expand only if needed.
- When returning results to the user, always include **permalinks**.

## Output format

All commands print JSON to stdout.

- Success: `{ "ok": true, "data": ... }`
- Failure: `{ "ok": false, "error": { "message": "...", "details": "..." } }`

## Commands

### 1) List posts in a subreddit

```bash
node {baseDir}/scripts/reddit-readonly.mjs posts <subreddit> \
  --sort hot|new|top|controversial|rising \
  --time day|week|month|year|all \
  --limit 10 \
  --after <token>
```

### 2) Search posts

```bash
# Search within a subreddit
node {baseDir}/scripts/reddit-readonly.mjs search <subreddit> "<query>" --limit 10

# Search all of Reddit
node {baseDir}/scripts/reddit-readonly.mjs search all "<query>" --limit 10
```

### 3) Get comments for a post

```bash
# By post id or URL
node {baseDir}/scripts/reddit-readonly.mjs comments <post_id|url> --limit 50 --depth 6
```

### 4) Recent comments across a subreddit

```bash
node {baseDir}/scripts/reddit-readonly.mjs recent-comments <subreddit> --limit 25
```

### 5) Thread bundle (post + comments)

```bash
node {baseDir}/scripts/reddit-readonly.mjs thread <post_id|url> --commentLimit 50 --depth 6
```

### 6) Find opportunities (multi-subreddit helper)

Use this when the user describes criteria like:
"Find posts about X in r/a, r/b, and r/c posted in the last 48 hours, excluding Y".

```bash
node {baseDir}/scripts/reddit-readonly.mjs find \
  --subreddits "python,learnpython" \
  --query "fastapi deployment" \
  --include "docker,uvicorn,nginx" \
  --exclude "homework,beginner" \
  --minScore 2 \
  --maxAgeHours 48 \
  --perSubredditLimit 25 \
  --maxResults 10 \
  --rank new
```

## Suggested agent workflow

1. **Clarify scope** if needed: subreddits + topic keywords + timeframe.
2. Start with `find` (or `posts`/`search`) using small limits.
3. For 1–3 promising items, fetch context via `thread`.
4. Present the user a shortlist:
   - title, subreddit, score, created time
   - permalink
   - a brief reason why it matched
5. If asked, propose *draft reply ideas* in natural language, but remind the user to post manually.

## Troubleshooting

- If Reddit returns HTML, re-run the command (the script detects this and returns an error).
- If requests fail repeatedly, reduce `--limit` and/or set slower pacing via env vars:

```bash
export REDDIT_RO_MIN_DELAY_MS=800
export REDDIT_RO_MAX_DELAY_MS=1800
export REDDIT_RO_TIMEOUT_MS=25000
export REDDIT_RO_USER_AGENT='script:clawdbot-reddit-readonly:v1.0.0 (personal)'
```
