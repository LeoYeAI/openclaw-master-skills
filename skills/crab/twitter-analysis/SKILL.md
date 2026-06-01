---
name: twitter-analysis
description: |
  Twitter/X data query. Provides general endpoints (auto data-source) and
  ReadX direct endpoints for deep tweet analysis, conversation threads,
  quote tweets, retweeters, relationship checks, and more.
metadata:
  author: NotevenDe
  version: 2.0.0
---

# Twitter Analysis — Social Data

**Base URL**: `https://crab-skill.opsat.io`

All endpoints are `POST`. Body is JSON. Requires Crab signature headers.

---

## 1. General Endpoints (auto data-source selection)

| Endpoint | Description | Required Fields |
|----------|-------------|-----------------|
| `/api/twitter/user` | User profile | `username` |
| `/api/twitter/tweets` | User tweets (no replies/retweets) | `username` |
| `/api/twitter/replies` | User tweets + replies | `username` |
| `/api/twitter/search` | Search tweets with filters | at least one filter |
| `/api/twitter/kol-followers` | KOL followers (6551 only) | `username` |
| `/api/twitter/deleted-tweets` | Deleted tweet history (6551 only) | `username` |
| `/api/twitter/follower-events` | Follow/unfollow events | `username` |

### Common Optional Fields

| Field | Endpoints | Description |
|-------|-----------|-------------|
| `maxResults` | tweets, replies, search, deleted-tweets, follower-events | Number of results (default 20) |
| `product` | tweets, replies, search | `Latest` / `Top` (default `Latest` for tweets/replies, `Top` for search) |

### Search Filters (`/api/twitter/search`)

| Field | Description |
|-------|-------------|
| `keywords` | Search keywords |
| `fromUser` | Filter by author |
| `toUser` | Filter by reply target |
| `mentionUser` | Mentioned user |
| `hashtag` | Hashtag |
| `excludeReplies` | Exclude replies |
| `excludeRetweets` | Exclude retweets |
| `minLikes` | Minimum likes |
| `minRetweets` | Minimum retweets |
| `minReplies` | Minimum replies |
| `sinceDate` | Start date (YYYY-MM-DD) |
| `untilDate` | End date (YYYY-MM-DD) |
| `lang` | Language code |

### Follower Events Filter

| Field | Description |
|-------|-------------|
| `isFollow` | `true` = new follows, `false` = unfollows (default `true`) |

---

## 2. ReadX Direct Endpoints

ReadX endpoints provide deep tweet-level analysis capabilities.

### Tweet Detail & Content

| Endpoint | Description | Required Fields |
|----------|-------------|-----------------|
| `/api/readx/tweet-detail` | Tweet detail (minimal) | `tweet_id` |
| `/api/readx/tweet-detail-v2` | Tweet detail (recommended, includes views/source) | `tweet_id` |
| `/api/readx/tweet-detail-v3` | Tweet detail (includes view_count) | `tweet_id` |
| `/api/readx/tweet-article` | Long-form article attached to tweet | `tweet_id` |
| `/api/readx/tweet-results-by-ids` | Batch fetch multiple tweets | `tweet_ids` (comma-separated) |

### Conversation & Replies

| Endpoint | Description | Required Fields |
|----------|-------------|-----------------|
| `/api/readx/tweet-detail-conversation` | Tweet + reply thread (single page) | `tweet_id` |
| `/api/readx/tweet-detail-conversation-v2` | Tweet + full reply thread (paginated) | `tweet_id`, optional `cursor` |

### Engagement & Spread

| Endpoint | Description | Required Fields |
|----------|-------------|-----------------|
| `/api/readx/tweet-quotes` | Who quoted this tweet | `tweet_id`, optional `cursor` |
| `/api/readx/tweet-retweeters` | Who retweeted this tweet | `tweet_id`, optional `cursor` |
| `/api/readx/tweet-favoriters` | Who liked this tweet | `tweet_id`, optional `cursor` |

### User Relationships

| Endpoint | Description | Required Fields |
|----------|-------------|-----------------|
| `/api/readx/followers-light` | Follower list (light fields) | `username`, optional `count` |
| `/api/readx/following-light` | Following list (light fields) | `username`, optional `count` |
| `/api/readx/user-verified-followers` | Verified followers (blue check) | `user_id` (rest_id), optional `cursor` |
| `/api/readx/friendships-show` | Relationship between two users | `source_screen_name`, `target_screen_name` |

### Advanced Search

| Endpoint | Description | Required Fields |
|----------|-------------|-----------------|
| `/api/readx/search2` | Twitter advanced search syntax | `q` (full query string) |

Optional fields for search2: `count` (default 20), `type` (`Top`/`Latest`, default `Top`), `cursor`, `safe_search`

**search2 query examples:**
- `bitcoin from:elonmusk min_faves:100`
- `"project name" -filter:replies min_faves:50`
- `@username OR #hashtag since:2025-01-01`

---

## When to Use Which

| Goal | Use |
|------|-----|
| Basic user info | `/api/twitter/user` |
| User's recent posts | `/api/twitter/tweets` |
| Search for mentions/discussions | `/api/twitter/search` or `/api/readx/search2` (advanced) |
| KOL following the project | `/api/twitter/kol-followers` |
| Read tweet replies/comments | `/api/readx/tweet-detail-conversation-v2` |
| Who quoted a tweet (KOL amplification) | `/api/readx/tweet-quotes` |
| Who retweeted (spread network) | `/api/readx/tweet-retweeters` |
| Who the project follows back | `/api/readx/following-light` |
| Verified/notable followers | `/api/readx/user-verified-followers` |
| Check if two people follow each other | `/api/readx/friendships-show` |
| Deleted tweets | `/api/twitter/deleted-tweets` |
| Follow/unfollow events | `/api/twitter/follower-events` |

---

## Fallback Behavior

| Scenario                   | Behavior                         |
|---------------------------|----------------------------------|
| All data sources fail     | Return an error                  |
| Primary source fails      | Automatically fall back to backup source |
| ReadX not configured      | Skip ReadX endpoints, use general endpoints only |
