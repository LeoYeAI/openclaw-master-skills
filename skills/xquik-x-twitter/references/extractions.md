# Xquik Extraction Tools

20 bulk data extraction tools. Each requires a specific target parameter.

**Endpoint:** `POST /extractions`

**Always estimate first:** `POST /extractions/estimate` with the same body to preview cost and check quota.

## Tool Types

### Tweet-Based (require `targetTweetId`)

| Tool Type | Description |
|-----------|-------------|
| `reply_extractor` | Extract users who replied to a tweet |
| `repost_extractor` | Extract users who retweeted a tweet |
| `quote_extractor` | Extract users who quote-tweeted a tweet |
| `thread_extractor` | Extract all tweets in a thread |
| `article_extractor` | Extract article content linked in a tweet |

**Example:**
```json
{
  "toolType": "reply_extractor",
  "targetTweetId": "1893704267862470862"
}
```

### User-Based (require `targetUsername`)

| Tool Type | Description |
|-----------|-------------|
| `follower_explorer` | Extract followers of an account |
| `following_explorer` | Extract accounts followed by a user |
| `verified_follower_explorer` | Extract verified followers of an account |
| `mention_extractor` | Extract tweets mentioning an account |
| `post_extractor` | Extract posts from an account |

**Example:**
```json
{
  "toolType": "follower_explorer",
  "targetUsername": "elonmusk"
}
```

The `@` prefix is automatically stripped if included.

### Community-Based (require `targetCommunityId`)

| Tool Type | Description |
|-----------|-------------|
| `community_extractor` | Extract members of a community |
| `community_moderator_explorer` | Extract moderators of a community |
| `community_post_extractor` | Extract posts from a community |
| `community_search` | Search posts within a community (also requires `searchQuery`) |

**Example:**
```json
{
  "toolType": "community_extractor",
  "targetCommunityId": "1234567890"
}
```

### List-Based (require `targetListId`)

| Tool Type | Description |
|-----------|-------------|
| `list_member_extractor` | Extract members of a list |
| `list_post_extractor` | Extract posts from a list |
| `list_follower_explorer` | Extract followers of a list |

**Example:**
```json
{
  "toolType": "list_member_extractor",
  "targetListId": "1234567890"
}
```

### Space-Based (require `targetSpaceId`)

| Tool Type | Description |
|-----------|-------------|
| `space_explorer` | Extract participants of a Space |

**Example:**
```json
{
  "toolType": "space_explorer",
  "targetSpaceId": "1YqKDqDXAbwKV"
}
```

### Search-Based (require `searchQuery`)

| Tool Type | Description |
|-----------|-------------|
| `people_search` | Search for users by keyword |
| `tweet_search_extractor` | Search and extract tweets by keyword or hashtag (bulk, up to 1,000) |

**Example (people search):**
```json
{
  "toolType": "people_search",
  "searchQuery": "machine learning engineer"
}
```

**Example (tweet search):**
```json
{
  "toolType": "tweet_search_extractor",
  "searchQuery": "#AI",
  "resultsLimit": 100
}
```

`resultsLimit` (optional): Maximum results to extract. Stops early instead of fetching all. Pass this on both `POST /extractions/estimate` and `POST /extractions` when you only need a specific count.

## Response

```json
{
  "id": "77777",
  "toolType": "reply_extractor",
  "status": "completed",
  "totalResults": 150
}
```

Statuses: `pending`, `running`, `completed`, `failed`.

## Retrieving Results

```
GET /extractions/{id}
```

Returns paginated results (up to 1,000 per page). Each result includes:

- `xUserId`, `xUsername`, `xDisplayName`
- `xFollowersCount`, `xVerified`, `xProfileImageUrl`
- `tweetId`, `tweetText`, `tweetCreatedAt` (for tweet-based extractions)

## Exporting Results

```
GET /extractions/{id}/export?format=csv
```

Formats: `csv`, `xlsx`, `md`. 50,000 row limit.

Exports include enrichment columns not present in the API response.

## Estimating Cost

```
POST /extractions/estimate
```

Same body as create. Response:

```json
{
  "allowed": true,
  "source": "replyCount",
  "estimatedResults": 150,
  "usagePercent": 45,
  "projectedPercent": 48
}
```

If `allowed` is `false`, the extraction would exceed your monthly quota.

For common mistakes and tool selection rules, see [mcp-tools.md](mcp-tools.md#common-mistakes).
