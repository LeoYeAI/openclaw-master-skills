---
name: reddit
description: Browse, search, post, and moderate Reddit. Read-only works without auth; posting/moderation requires OAuth setup.
metadata: {"clawdbot":{"emoji":"📣","requires":{"bins":["node"]}}}
---

# Reddit

Browse, search, post to, and moderate subreddits. Read-only actions work without auth; posting/moderation requires OAuth setup.

## Setup (for posting/moderation)

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Select "script" type
4. Set redirect URI to `http://localhost:8080`
5. Note your client ID (under app name) and client secret
6. Set environment variables:
   ```bash
   export REDDIT_CLIENT_ID="your_client_id"
   export REDDIT_CLIENT_SECRET="your_client_secret"
   export REDDIT_USERNAME="your_username"
   export REDDIT_PASSWORD="your_password"
   ```

## Read Posts (no auth required)

```bash
# Hot posts from a subreddit
node {baseDir}/scripts/reddit.mjs posts wallstreetbets

# New posts
node {baseDir}/scripts/reddit.mjs posts wallstreetbets --sort new

# Top posts (day/week/month/year/all)
node {baseDir}/scripts/reddit.mjs posts wallstreetbets --sort top --time week

# Limit results
node {baseDir}/scripts/reddit.mjs posts wallstreetbets --limit 5
```

## Search Posts

```bash
# Search within a subreddit
node {baseDir}/scripts/reddit.mjs search wallstreetbets "YOLO"

# Search all of Reddit
node {baseDir}/scripts/reddit.mjs search all "stock picks"
```

## Get Comments on a Post

```bash
# By post ID or full URL
node {baseDir}/scripts/reddit.mjs comments POST_ID
node {baseDir}/scripts/reddit.mjs comments "https://reddit.com/r/subreddit/comments/abc123/..."
```

## Submit a Post (requires auth)

```bash
# Text post
node {baseDir}/scripts/reddit.mjs submit yoursubreddit --title "Weekly Discussion" --text "What's on your mind?"

# Link post
node {baseDir}/scripts/reddit.mjs submit yoursubreddit --title "Great article" --url "https://example.com/article"
```

## Reply to a Post/Comment (requires auth)

```bash
node {baseDir}/scripts/reddit.mjs reply THING_ID "Your reply text here"
```

## Moderation (requires auth + mod permissions)

```bash
# Remove a post/comment
node {baseDir}/scripts/reddit.mjs mod remove THING_ID

# Approve a post/comment
node {baseDir}/scripts/reddit.mjs mod approve THING_ID

# Sticky a post
node {baseDir}/scripts/reddit.mjs mod sticky POST_ID

# Unsticky
node {baseDir}/scripts/reddit.mjs mod unsticky POST_ID

# Lock comments
node {baseDir}/scripts/reddit.mjs mod lock POST_ID

# View modqueue
node {baseDir}/scripts/reddit.mjs mod queue yoursubreddit
```

## Notes

- Read actions use Reddit's public JSON API (no auth needed)
- Post/mod actions require OAuth - run `login` command once to authorize
- Token stored at `~/.reddit-token.json` (auto-refreshes)
- Rate limits: ~60 requests/minute for OAuth, ~10/minute for unauthenticated
