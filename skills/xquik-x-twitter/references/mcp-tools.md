# Xquik MCP Tools Reference (Legacy v1)

Complete reference for all 18 MCP tools exposed by the legacy v1 server at `https://xquik.com/mcp/v1`. The default v2 server at `/mcp` uses a code-execution sandbox with 2 tools (`explore` + `xquik`) that can call all 76 REST API endpoints. See [mcp-setup.md](mcp-setup.md) for the v2 architecture.

## Tool Selection Rules

Pick the simplest tool that answers the question:

| Goal | Tool | Returns |
|------|------|---------|
| Single tweet by ID or URL | `lookup-tweet` | Full metrics: likes, retweets, replies, quotes, views, bookmarks, author verification |
| Search tweets by keyword/hashtag/from:user | `search-tweets` | Basic tweet info: id, text, author, date (no engagement metrics) |
| User profile, bio, follower/following counts | `get-user-info` | Name, username, bio, follower count, following count, profile picture (no verification, tweet count, or join date) |
| Download images/videos/GIFs from tweets | `download-media` | Permanent hosted URLs on media.xquik.com. First download metered, cached free |
| Check follow relationship | `check-follow` | Both directions: following and followedBy |
| Trending topics by region (X) | `get-trends` | Names, ranks, search queries. Metered |
| Trending topics from 7 sources | `get-radar` | Google Trends, HN, Polymarket, TrustMRR, Wikipedia, GitHub, Reddit. Free |
| Activity from monitored accounts | `events` | Only YOUR monitors, not all of X |
| Budget, plan, usage percent | `get-account` | Plan, monitor quota, current period usage percent |
| Start/stop tracking an account | `monitors` action=add/remove | Webhooks are optional, add separately with `webhooks` action=add |
| Set up webhook push notifications | `webhooks` action=add | HMAC-signed HTTP POST delivery |
| Run a giveaway/raffle | `draws` action=run | Handles reply fetching, filtering, deduplication, and random selection automatically |
| Past giveaway results | `draws` action=list/get | Draw details with winners |
| Subscribe, billing, manage plan | `subscribe` | Returns Stripe Checkout or Customer Portal URL. Free |
| Write/compose/draft a tweet | `compose-tweet` step=compose FIRST | Returns algorithm signals + follow-up questions. Then step=refine, then step=score. Free |
| Link your X username | `set-x-identity` | Required for own-account detection in style analysis |
| Analyze how someone tweets | `styles` action=analyze | Fetches & caches recent tweets. Metered |
| Get cached style for reference | `styles` action=get | Check before calling action=analyze |
| Compare two styles | `styles` action=compare | Both must be cached with action=analyze first |
| Tweet engagement metrics | `styles` action=analyze-performance | Live metrics for cached tweets. Metered |
| Save a tweet draft | `drafts` action=save | Store for later |
| List/get/delete drafts | `drafts` action=list/get/delete | Manage saved drafts |

Use `extractions` action=run ONLY for bulk data that simpler tools cannot provide:

- All followers/following of an account (not just the count; use `get-user-info` for counts)
- All replies/retweets/quotes of a tweet (comprehensive list; use `lookup-tweet` for just the counts)
- Full tweet thread, article extraction, community/list/space members
- People search, mention history, all posts from a user
- Always call `extractions` action=estimate first to check cost. Requires active subscription.

## Workflow Patterns

Multi-step tool sequences for common tasks:

| Workflow | Steps |
|----------|-------|
| **Set up real-time alerts** | `monitors` action=add -> `webhooks` action=add -> `webhooks` action=test |
| **Run a giveaway** | `get-account` (check budget) -> `draws` action=run |
| **Bulk extraction** | `get-account` (check subscription) -> `extractions` action=estimate -> `extractions` action=run -> `extractions` action=get (results) |
| **Full tweet analysis** | `lookup-tweet` (metrics) -> `extractions` action=run with `thread_extractor` (full thread) |
| **Find and analyze user** | `get-user-info` (profile) -> `search-tweets` from:username (recent tweets) -> `lookup-tweet` (metrics on specific tweet) |
| **Compose algorithm-optimized tweet** | `compose-tweet` step=compose -> AI asks follow-ups -> `compose-tweet` step=refine -> AI drafts tweet -> `compose-tweet` step=score -> iterate |
| **Compose from trending topics** | `get-radar` (find topic) -> `compose-tweet` step=compose with item title as topic -> step=refine with item URL as additionalContext |
| **Analyze tweet style** | `styles` action=analyze (fetch & cache tweets) -> `styles` action=get (reference) -> `compose-tweet` step=compose with `styleUsername` |
| **Compare styles** | `styles` action=analyze for both accounts -> `styles` action=compare |
| **Track performance** | `styles` action=analyze (cache tweets) -> `styles` action=analyze-performance (live metrics) |
| **Download & share media** | `download-media` (returns permanent hosted URLs, share directly) |
| **Save & manage drafts** | `compose-tweet` step=compose -> step=refine -> step=score -> `drafts` action=save -> `drafts` action=list |
| **Subscribe or manage billing** | `subscribe` (returns Stripe URL) |

## Cost Categories

| Category | Tools |
|----------|-------|
| **Free** | `monitors`, `events`, `webhooks`, `extractions` action=list/get/estimate, `draws` action=list/get, `get-account`, `subscribe`, `get-radar`, `compose-tweet`, `set-x-identity`, `styles` action=get/list/save/delete/compare, `drafts` |
| **Metered** (counts toward monthly quota) | `search-tweets`, `get-user-info`, `lookup-tweet`, `download-media` (first download only, cached free), `check-follow`, `extractions` action=run, `draws` action=run, `styles` action=analyze/analyze-performance, `get-trends` |

---

## Monitoring Tool

### monitors

Manage monitored X accounts. Use `action` to list, add, or remove monitors.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | `list` = show all monitors, `add` = start monitoring, `remove` = stop monitoring |
| `username` | string | action=add | X username without @ prefix (e.g. "elonmusk") |
| `eventTypes` | string[] | action=add | Event types: `tweet.new`, `tweet.reply`, `tweet.retweet`, `tweet.quote`, `follower.gained`, `follower.lost` |
| `monitorId` | string | action=remove | Monitor ID (use `monitors` action=list to find IDs) |

**Output (action=list):**

| Field | Type | Description |
|-------|------|-------------|
| `monitors[].id` | string | Monitor ID (use with action=remove, events monitorId filter) |
| `monitors[].xUsername` | string | Monitored X username |
| `monitors[].eventTypes` | string[] | Subscribed event types |
| `monitors[].isActive` | boolean | Whether the monitor is currently active |
| `monitors[].createdAt` | string | ISO 8601 timestamp |

**Output (action=add):** Monitor object with `id`, `xUsername`, `eventTypes`, `isActive`, `createdAt`.

**Output (action=remove):** Text confirmation.

**Annotations:** openWorld | **Cost:** Free (add requires subscription)

---

## Events Tool

### events

Retrieve activity from monitored X accounts. Provide `id` for single event details, omit for paginated list. Only returns events from accounts YOU monitor via `monitors` action=add. Does NOT search all of X. Use `search-tweets` for that.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | No | Event ID for single event details |
| `limit` | number | No | Events to return (1-50, default 50) |
| `afterCursor` | string | No | Pagination cursor from previous response |
| `monitorId` | string | No | Filter to a specific monitor |
| `eventType` | string | No | Filter: `tweet.new`, `tweet.reply`, `tweet.retweet`, `tweet.quote`, `follower.gained`, `follower.lost` |

**Output (list):**

| Field | Type | Description |
|-------|------|-------------|
| `events[].id` | string | Event ID (pass as `id` for full details) |
| `events[].xUsername` | string | Username of the monitored account |
| `events[].eventType` | string | Event type (tweet.new, tweet.reply, etc.) |
| `events[].eventData` | object | Full event payload (tweet text, author, metrics) |
| `events[].monitoredAccountId` | string | ID of the monitored account |
| `events[].createdAt` | string | ISO 8601 timestamp when event was recorded |
| `events[].occurredAt` | string | ISO 8601 timestamp when event occurred on X |
| `hasMore` | boolean | Whether more results are available |
| `nextCursor` | string | Pass as afterCursor to fetch the next page |

**Output (single event by id):** Single event object with `id`, `xUsername`, `eventType`, `eventData`, `monitoredAccountId`, `createdAt`, `occurredAt`.

**Annotations:** readOnly, idempotent | **Cost:** Free

---

## Search & Lookup Tools

### search-tweets

Search X for tweets matching a query. Returns basic tweet info only (id, text, author, date). For engagement metrics, use `lookup-tweet` on individual results.

Supports X search syntax: keywords, `#hashtags`, `from:user`, `to:user`, `"exact phrases"`, `OR`, `-exclude`.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | X search query |

**Output:**

| Field | Type | Description |
|-------|------|-------------|
| `tweets[].id` | string | Tweet ID (use with lookup-tweet for full metrics) |
| `tweets[].text` | string | Full tweet text |
| `tweets[].authorUsername` | string | X username of the tweet author |
| `tweets[].authorName` | string | Display name of the tweet author |
| `tweets[].createdAt` | string | ISO 8601 timestamp when tweet was posted |
| `tweets[].media[]` | array | Optional. Attached photos/videos: `mediaUrl`, `type`, `url` |

**Annotations:** readOnly, idempotent, openWorld | **Cost:** Metered

---

### lookup-tweet

Get full details of a specific tweet by its ID or URL. Returns engagement metrics and author info.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tweetId` | string | Yes | Numeric tweet ID (e.g. "1234567890") or ID extracted from a tweet URL |

**Output:**

| Field | Type | Description |
|-------|------|-------------|
| `tweet.id` | string | Tweet ID |
| `tweet.text` | string | Tweet text |
| `tweet.likeCount` | number | Number of likes |
| `tweet.retweetCount` | number | Number of retweets |
| `tweet.replyCount` | number | Number of replies |
| `tweet.quoteCount` | number | Number of quote tweets |
| `tweet.viewCount` | number | Number of views |
| `tweet.bookmarkCount` | number | Number of bookmarks |
| `tweet.media[]` | array | Optional. Attached photos/videos: `mediaUrl`, `type`, `url` |
| `author.id` | string | Author user ID |
| `author.username` | string | Author username |
| `author.followers` | number | Author follower count |
| `author.verified` | boolean | Whether author is verified |

**Annotations:** readOnly, idempotent, openWorld | **Cost:** Metered

---

### get-user-info

Look up an X user profile by username. Does NOT return verification status or tweet count. To check verification, use `search-tweets from:username` + `lookup-tweet` (author.verified). To search for users by name, use `extractions` action=run with `people_search`.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | X username without @ prefix (e.g. "elonmusk") |

**Output:**

| Field | Type | Description |
|-------|------|-------------|
| `username` | string | X username (without @) |
| `name` | string | Display name |
| `description` | string | User bio text |
| `followersCount` | number | Number of followers |
| `followingCount` | number | Number of accounts followed |
| `profilePicture` | string | Profile picture URL |

**Note:** The REST API `GET /x/users/{username}` returns additional fields: `verified`, `location`, `createdAt`, `statusesCount`.

**Annotations:** readOnly, idempotent, openWorld | **Cost:** Metered

---

### download-media

Download images, videos, and GIFs from tweets. Accepts one or more tweet IDs/URLs (up to 50). Returns a shareable gallery URL and permanent download URLs.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tweetIds` | string[] | Yes | Array of tweet IDs or full tweet URLs (1-50 items). Single item = one tweet, multiple = bulk download |

**Output (single, 1 item in tweetIds):**

| Field | Type | Description |
|-------|------|-------------|
| `tweetId` | string | Resolved tweet ID |
| `galleryUrl` | string | Shareable gallery page URL |
| `cacheHit` | boolean | `true` if served from cache (no usage consumed) |
| `media` | array | Array of downloaded media items |
| `media[].url` | string | Permanent download URL hosted on media.xquik.com |
| `media[].type` | string | Media type: `photo`, `video`, or `animated_gif` |
| `media[].index` | number | Position in the tweet's media attachments (0-indexed) |
| `media[].fileSize` | string | File size in bytes (as a string). `null` if unavailable |

**Output (bulk, 2+ items in tweetIds):**

| Field | Type | Description |
|-------|------|-------------|
| `galleryUrl` | string | Combined gallery page URL containing media from all tweets |
| `totalTweets` | number | Number of tweets successfully processed |
| `totalMedia` | number | Total media items downloaded across all tweets |
| `freshDownloads` | number | Number of tweets downloaded fresh (not from cache) |

**Quota:** First download is metered (counts toward your monthly quota). Subsequent requests for the same tweet return cached URLs at no cost (`cacheHit: true`). All downloads are saved to the gallery at `https://xquik.com/gallery`.

**Annotations:** openWorld | **Cost:** Metered (first download only, cached free)

---

### check-follow

Check if one X account follows another. Returns both directions.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sourceUsername` | string | Yes | Account to check (without @) |
| `targetUsername` | string | Yes | Account that may be followed (without @) |

**Output:**

| Field | Type | Description |
|-------|------|-------------|
| `following` | boolean | Whether the source follows the target |
| `followedBy` | boolean | Whether the target follows the source |

**Annotations:** readOnly, idempotent, openWorld | **Cost:** Metered

---

## Trends Tools

### get-trends

Get trending topics on X for a region. Subscription required, metered.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `woeid` | number | No | Region WOEID: 1=Worldwide (default), 23424977=US, 23424975=UK, 23424969=Turkey, 23424950=Spain, 23424829=Germany, 23424819=France, 23424856=Japan, 23424848=India, 23424768=Brazil, 23424775=Canada, 23424900=Mexico |
| `count` | number | No | Trends to return (1-50, default 30) |

**Output:**

| Field | Type | Description |
|-------|------|-------------|
| `woeid` | number | Region WOEID used for this request |
| `total` | number | Total number of trends returned |
| `trends[].name` | string | Trend name or hashtag |
| `trends[].rank` | number | Trend rank position |
| `trends[].description` | string | Trend description or context |
| `trends[].query` | string | Search query to find tweets for this trend |

**Annotations:** readOnly, idempotent, openWorld | **Cost:** Metered (subscription required)

---

### get-radar

Get trending topics and news from 7 sources beyond X. Use a specific item title as `topic` for `compose-tweet`. For TrustMRR items, visit the URL for founder/MRR/growth details.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | string | No | Filter by source: `google_trends`, `hacker_news`, `polymarket`, `trustmrr`, `wikipedia`, `github`, `reddit` |
| `category` | string | No | Filter by category: `general`, `tech`, `dev`, `science`, `culture`, `politics`, `business`, `entertainment` |
| `limit` | number | No | Items per page (1-100, default 50) |
| `hours` | number | No | Look-back window in hours (1-72, default 6) |
| `region` | string | No | Region code: `US`, `GB`, `TR`, `ES`, `DE`, `FR`, `JP`, `IN`, `BR`, `CA`, `MX`, `global` (default) |

**Output:**

| Field | Type | Description |
|-------|------|-------------|
| `items[].id` | string | Unique item identifier |
| `items[].title` | string | Item title (use as `topic` for `compose-tweet`) |
| `items[].description` | string | Optional. Item description or summary |
| `items[].url` | string | Optional. Source URL for more details |
| `items[].imageUrl` | string | Optional. Associated image URL |
| `items[].source` | string | Source name (google_trends, hacker_news, etc.) |
| `items[].sourceId` | string | Unique identifier within the source |
| `items[].category` | string | Item category |
| `items[].region` | string | Region code |
| `items[].language` | string | BCP-47 language code |
| `items[].score` | number | Relevance/trending score |
| `items[].metadata` | object | Source-specific data (varies by source) |
| `items[].publishedAt` | string | ISO 8601 timestamp |
| `items[].createdAt` | string | ISO 8601 timestamp when indexed |
| `hasMore` | boolean | Whether more items are available |
| `nextCursor` | string | Pagination cursor (present when hasMore is true) |

**Annotations:** readOnly, idempotent, openWorld | **Cost:** Free

---

## Webhook Tool

### webhooks

Manage webhook endpoints for real-time event push notifications. Use `action` to list, add, remove, or test webhooks.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | `list` = show webhooks, `add` = register endpoint, `remove` = delete webhook, `test` = send test payload |
| `url` | string (URL) | action=add | HTTPS URL that will receive webhook POST requests |
| `eventTypes` | string[] | action=add | Event types: `tweet.new`, `tweet.reply`, `tweet.retweet`, `tweet.quote`, `follower.gained`, `follower.lost` |
| `webhookId` | string | action=remove/test | Webhook ID (use `webhooks` action=list to find IDs) |

**Output (action=list):**

| Field | Type | Description |
|-------|------|-------------|
| `webhooks[].id` | string | Webhook ID (use with action=remove, action=test) |
| `webhooks[].url` | string | HTTPS endpoint URL |
| `webhooks[].eventTypes` | string[] | Event types delivered to this webhook |
| `webhooks[].isActive` | boolean | Whether the webhook is currently active |
| `webhooks[].createdAt` | string | ISO 8601 timestamp |

**Output (action=add):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Webhook ID |
| `url` | string | HTTPS endpoint URL |
| `eventTypes` | string[] | Event types delivered to this webhook |
| `isActive` | boolean | Whether the webhook is active |
| `createdAt` | string | ISO 8601 timestamp |
| `secret` | string | HMAC signing secret for verifying webhook payloads. Store securely. |

**Output (action=test):**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the test delivery succeeded |
| `statusCode` | number | HTTP status code from the endpoint |
| `error` | string | Error message (present on failure) |

**Output (action=remove):** Text confirmation.

**Annotations:** openWorld | **Cost:** Free

---

## Extraction Tool

### extractions

Bulk data extraction from X with 20 tool types. Use `action` to estimate cost, run jobs, list past jobs, or get results.

For simpler lookups, prefer: `get-user-info` (profiles/counts), `search-tweets` (finding tweets), `lookup-tweet` (single tweet stats), `check-follow` (follow checks).

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | `estimate` = preview cost (always call first), `run` = start extraction, `list` = browse jobs, `get` = retrieve results |
| `toolType` | string | action=run/estimate, optional for list filter | Extraction type (see table below) |
| `id` | string | action=get | Extraction job ID |
| `targetUsername` | string | Conditional | X username without @ |
| `targetTweetId` | string | Conditional | Tweet ID |
| `targetCommunityId` | string | Conditional | Community ID |
| `targetListId` | string | Conditional | List ID |
| `targetSpaceId` | string | Conditional | Space ID |
| `searchQuery` | string | Conditional | Search keywords (for `people_search`, `community_search`, `tweet_search_extractor`) |
| `resultsLimit` | number | No | Maximum results to extract/estimate. Stops early instead of fetching all. Omit for all results |
| `status` | string | No | Filter by status (list): `running`, `completed`, `failed` |
| `limit` | number | No | Results per page (list, get) |
| `afterCursor` | string | No | Pagination cursor (list, get) |

**20 tool types by target:**

| Target | Tool Types |
|--------|-----------|
| Username | `follower_explorer`, `following_explorer`, `verified_follower_explorer`, `mention_extractor`, `post_extractor` |
| Tweet ID | `reply_extractor`, `repost_extractor`, `quote_extractor`, `thread_extractor`, `article_extractor` |
| Community ID | `community_extractor`, `community_moderator_explorer`, `community_post_extractor`, `community_search` |
| List ID | `list_member_extractor`, `list_post_extractor`, `list_follower_explorer` |
| Space ID | `space_explorer` |
| Search query | `people_search`, `tweet_search_extractor` |

**Output (action=estimate):**

| Field | Type | Description |
|-------|------|-------------|
| `allowed` | boolean | Whether the extraction is allowed within budget |
| `estimatedResults` | number | Estimated number of results |
| `projectedPercent` | number | Projected usage percent after extraction |
| `usagePercent` | number | Current usage percent of monthly quota |
| `source` | string | Data source used for estimation |
| `error` | string | Error message if estimation failed |

**Output (action=run):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Extraction job ID (use with action=get for results) |
| `toolType` | string | Extraction tool type used |
| `status` | string | Job status |
| `totalResults` | number | Number of results extracted |

**Output (action=list):**

| Field | Type | Description |
|-------|------|-------------|
| `extractions[].id` | string | Extraction ID (use with action=get for results) |
| `extractions[].toolType` | string | Extraction tool type used |
| `extractions[].status` | string | Job status (running, completed, failed) |
| `extractions[].createdAt` | string | ISO 8601 creation timestamp |
| `extractions[].completedAt` | string | ISO 8601 completion timestamp |
| `extractions[].totalResults` | number | Number of results extracted |
| `hasMore` | boolean | Whether more results are available |
| `nextCursor` | string | Pass as afterCursor to fetch the next page |

**Output (action=get):**

| Field | Type | Description |
|-------|------|-------------|
| `job` | object | Full job metadata |
| `results` | array | Extracted data (user profiles, tweets, etc.) |
| `hasMore` | boolean | Whether more results are available |
| `nextCursor` | string | Pass as afterCursor to fetch the next page |

**Annotations:** openWorld | **Cost:** estimate/list/get = Free, run = Metered

---

## Giveaway Draw Tool

### draws

Giveaway draws from tweet replies. Use `action` to run a draw, list past draws, or get draw details.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | `run` = pick winners, `list` = browse past draws, `get` = draw details |
| `tweetUrl` | string | action=run | Full tweet URL (e.g. "https://x.com/user/status/123") |
| `drawId` | string | action=get | Draw ID |
| `winnerCount` | number | No | Winners to select (default 1) |
| `backupCount` | number | No | Backup winners to select |
| `uniqueAuthorsOnly` | boolean | No | Count only one entry per author |
| `mustRetweet` | boolean | No | Require participants to have retweeted |
| `filterMinFollowers` | number | No | Minimum follower count |
| `filterAccountAgeDays` | number | No | Minimum account age in days |
| `filterLanguage` | string | No | Language code (e.g. "en") |
| `mustFollowUsername` | string | No | Username participants must follow |
| `requiredHashtags` | string[] | No | Hashtags that must appear in replies |
| `requiredKeywords` | string[] | No | Keywords that must appear in replies |
| `requiredMentions` | string[] | No | Usernames that must be mentioned in replies |
| `limit` | number | No | Results per page (list) |
| `afterCursor` | string | No | Pagination cursor (list) |

**Output (action=run):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Draw ID (use with action=get for full details) |
| `tweetId` | string | Giveaway tweet ID |
| `totalEntries` | number | Total reply count before filtering |
| `validEntries` | number | Valid entries after filtering |
| `winners[].position` | number | Winner position (1-based) |
| `winners[].authorUsername` | string | X username of the winner |
| `winners[].tweetId` | string | Tweet ID of the winning reply |
| `winners[].isBackup` | boolean | Whether this is a backup winner |

**Output (action=list):**

| Field | Type | Description |
|-------|------|-------------|
| `draws[].id` | string | Draw ID (use with action=get for full details) |
| `draws[].tweetUrl` | string | Giveaway tweet URL |
| `draws[].status` | string | Draw status |
| `draws[].createdAt` | string | ISO 8601 timestamp |
| `draws[].drawnAt` | string | ISO 8601 timestamp when drawn |
| `draws[].totalEntries` | number | Total reply count |
| `draws[].validEntries` | number | Valid entries after filtering |
| `hasMore` | boolean | Whether more results are available |
| `nextCursor` | string | Pass as afterCursor to fetch the next page |

**Output (action=get):**

| Field | Type | Description |
|-------|------|-------------|
| `draw.id` | string | Draw ID |
| `draw.status` | string | Draw status (completed, failed) |
| `draw.createdAt` | string | ISO 8601 timestamp |
| `draw.drawnAt` | string | ISO 8601 timestamp when winners were drawn |
| `draw.totalEntries` | number | Total reply count before filtering |
| `draw.validEntries` | number | Entries remaining after filters applied |
| `draw.tweetId` | string | Giveaway tweet ID |
| `draw.tweetUrl` | string | Full URL of the giveaway tweet |
| `draw.tweetText` | string | Giveaway tweet text |
| `draw.tweetAuthorUsername` | string | Username of the giveaway tweet author |
| `draw.tweetLikeCount` | number | Tweet like count at draw time |
| `draw.tweetRetweetCount` | number | Tweet retweet count at draw time |
| `draw.tweetReplyCount` | number | Tweet reply count at draw time |
| `draw.tweetQuoteCount` | number | Tweet quote count at draw time |
| `winners[].position` | number | Winner position (1-based) |
| `winners[].authorUsername` | string | X username of the winner |
| `winners[].tweetId` | string | Tweet ID of the winning reply |
| `winners[].isBackup` | boolean | Whether this is a backup winner |

**Annotations:** openWorld | **Cost:** list/get = Free, run = Metered

---

## Account Tool

### get-account

Check Xquik account status, subscription, and usage.

**Input:** None

**Output:**

| Field | Type | Description |
|-------|------|-------------|
| `plan` | string | Current plan name (free or subscriber) |
| `monitorsAllowed` | number | Maximum monitors allowed on current plan |
| `monitorsUsed` | number | Number of active monitors |
| `currentPeriod` | object | Current billing period (present only with active subscription) |
| `currentPeriod.start` | string | ISO 8601 period start date |
| `currentPeriod.end` | string | ISO 8601 period end date |
| `currentPeriod.usagePercent` | number | Percent of monthly quota consumed |

**Annotations:** readOnly, idempotent | **Cost:** Free

---

## Subscription Tool

### subscribe

Get a subscription checkout or management link. Returns a Stripe Checkout URL (for new subscribers) or Customer Portal URL (for existing subscribers). Free, no subscription needed.

**Input:** None

**Output:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | One of: `already_subscribed`, `checkout_created`, `payment_issue` |
| `url` | string | Stripe Checkout or Customer Portal URL. Open in browser. |
| `message` | string | Human-readable status message |

**Annotations:** idempotent, openWorld | **Cost:** Free

---

## Tweet Composition Tool

### compose-tweet

Compose, refine, and score tweets using X algorithm data. Use `step` to progress through the workflow.

- `step=compose` (default): Returns X algorithm weights, content rules, engagement multipliers, follow-up questions, and any saved style profiles. Optionally pass `styleUsername` to include cached style tweets for reference.
- `step=refine`: Returns goal-specific composition guidance, example tweet patterns, media strategy, hashtag advice, and CTA guidance. Call after the user answers follow-up questions from compose.
- `step=score`: Evaluates a draft tweet against 15 algorithm ranking checks with pass/fail and an intent URL for posting.

Subscription required, not metered.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `step` | string | No | Workflow step: `compose` (default), `refine`, `score` |
| `topic` | string | step=compose/refine | What the tweet is about |
| `goal` | string | No | Optimization goal: `engagement` (default), `followers`, `authority`, `conversation` |
| `styleUsername` | string | No | X username whose cached style tweets to include (compose). Must be analyzed with `styles` action=analyze first |
| `tone` | string | step=refine | Desired tone (e.g. casual, professional, provocative, educational) |
| `mediaType` | string | No | `photo`, `video`, or `none` (refine) |
| `callToAction` | string | No | Desired CTA (refine) |
| `additionalContext` | string | No | Additional context about target audience or constraints (refine) |
| `draft` | string | step=score | The draft tweet text to evaluate |
| `hasLink` | boolean | No | Whether a link will be attached (score) |
| `hasMedia` | boolean | No | Whether media will be attached (score) |

**Output (step=compose):**

| Field | Type | Description |
|-------|------|-------------|
| `algorithmInsights[].name` | string | Signal name from PhoenixScores |
| `algorithmInsights[].polarity` | string | `positive` or `negative` (helps or hurts ranking) |
| `algorithmInsights[].description` | string | What this signal measures |
| `contentRules[].rule` | string | Actionable content rule |
| `contentRules[].description` | string | Why this rule matters based on algorithm architecture |
| `engagementMultipliers[].action` | string | Engagement action (e.g. reply chain, quote tweet) |
| `engagementMultipliers[].multiplier` | string | Relative value compared to a like (e.g. "27x a like") |
| `engagementMultipliers[].source` | string | Data source for this multiplier |
| `engagementVelocity` | string | How early engagement velocity affects distribution |
| `followUpQuestions` | string[] | Questions for the AI to ask the user before composing |
| `scorerWeights[].signal` | string | Signal name in the scoring model |
| `scorerWeights[].weight` | number | Weight applied to predicted probability |
| `scorerWeights[].context` | string | Practical meaning of this weight |
| `topPenalties` | string[] | Most severe negative signals to avoid |
| `source` | string | Attribution to algorithm source code |
| `styleTweets` | array | Optional. Cached tweets from the referenced style username |

**Output (step=refine):**

| Field | Type | Description |
|-------|------|-------------|
| `compositionGuidance` | string[] | Targeted guidance based on user preferences |
| `examplePatterns[].pattern` | string | Tweet structure template |
| `examplePatterns[].description` | string | What this pattern achieves |

**Output (step=score):**

| Field | Type | Description |
|-------|------|-------------|
| `totalChecks` | number | Total number of checks performed |
| `passedCount` | number | Number of checks that passed |
| `topSuggestion` | string | Highest-impact improvement suggestion |
| `checklist[].factor` | string | What was checked |
| `checklist[].passed` | boolean | Whether the check passed |
| `checklist[].suggestion` | string | Improvement suggestion (present only if failed) |

**Annotations:** readOnly, idempotent | **Cost:** Free (subscription required)

---

## Identity Tool

### set-x-identity

Link your X (Twitter) username to your Xquik account. Required for own-account detection in style analysis. Subscription required.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | Your X username (without the @ prefix) |

**Output:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the identity was set |

**Annotations:** idempotent | **Cost:** Free (subscription required)

---

## Style Tool

### styles

Manage tweet style profiles. Use `action` to analyze, get, list, save, delete, compare styles, or analyze performance.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | `analyze` = fetch & cache tweets, `get` = cached style, `list` = all cached styles, `save` = save custom style from tweet texts, `delete` = remove cached style, `compare` = side-by-side comparison, `analyze-performance` = engagement metrics |
| `username` | string | action=analyze/get/delete/analyze-performance | X username without @ prefix |
| `username1` | string | action=compare | First X username to compare (without @) |
| `username2` | string | action=compare | Second X username to compare (without @) |
| `label` | string | action=save | Style label name |
| `tweets` | string[] | action=save | Tweet texts defining the style (1-100 items) |

**Output (action=analyze):**

| Field | Type | Description |
|-------|------|-------------|
| `xUsername` | string | Analyzed username |
| `tweetCount` | number | Number of tweets cached |
| `isOwnAccount` | boolean | Whether this is the authenticated user's own account |
| `fetchedAt` | string | ISO 8601 timestamp when tweets were fetched |
| `tweets[].id` | string | Tweet ID |
| `tweets[].text` | string | Tweet text |
| `tweets[].authorUsername` | string | Author username |
| `tweets[].createdAt` | string | ISO 8601 timestamp |

**Output (action=get):** Same shape as action=analyze output.

**Output (action=list):**

| Field | Type | Description |
|-------|------|-------------|
| `styles[].xUsername` | string | Cached username |
| `styles[].tweetCount` | number | Number of cached tweets |
| `styles[].isOwnAccount` | boolean | Whether this is the user's own account |
| `styles[].fetchedAt` | string | ISO 8601 timestamp |

**Output (action=save):** Style object with label and tweet data.

**Output (action=delete):**

| Field | Type | Description |
|-------|------|-------------|
| `deleted` | boolean | Whether the style was deleted |

**Output (action=compare):**

| Field | Type | Description |
|-------|------|-------------|
| `style1` | object | Full style profile for username1 (same shape as action=get output) |
| `style2` | object | Full style profile for username2 (same shape as action=get output) |

**Output (action=analyze-performance):**

| Field | Type | Description |
|-------|------|-------------|
| `xUsername` | string | Analyzed username |
| `tweetCount` | number | Number of tweets analyzed |
| `tweets[].id` | string | Tweet ID |
| `tweets[].text` | string | Tweet text |
| `tweets[].likeCount` | number | Number of likes |
| `tweets[].retweetCount` | number | Number of retweets |
| `tweets[].replyCount` | number | Number of replies |
| `tweets[].quoteCount` | number | Number of quote tweets |
| `tweets[].viewCount` | number | Number of views |
| `tweets[].bookmarkCount` | number | Number of bookmarks |

**Annotations:** openWorld | **Cost:** get/list/save/delete/compare = Free (subscription required), analyze/analyze-performance = Metered

---

## Draft Tool

### drafts

Manage tweet drafts. Use `action` to save, list, get, or delete drafts.

**Input:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | `save` = store draft, `list` = browse drafts, `get` = single draft, `delete` = remove draft |
| `text` | string | action=save | The draft tweet text |
| `topic` | string | No | Topic the tweet is about (save) |
| `goal` | string | No | Optimization goal: `engagement`, `followers`, `authority`, `conversation` (save) |
| `draftId` | string | action=get/delete | Draft ID |
| `limit` | number | No | Results per page (list, 1-50, default 50) |
| `afterCursor` | string | No | Pagination cursor (list) |

**Output (action=save):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Draft ID (use with action=get, action=delete) |
| `text` | string | Draft text |
| `topic` | string | Topic (if provided) |
| `goal` | string | Goal (if provided) |
| `createdAt` | string | ISO 8601 timestamp |
| `updatedAt` | string | ISO 8601 timestamp |

**Output (action=list):**

| Field | Type | Description |
|-------|------|-------------|
| `drafts[].id` | string | Draft ID |
| `drafts[].text` | string | Draft text |
| `drafts[].topic` | string | Topic (if set) |
| `drafts[].goal` | string | Goal (if set) |
| `drafts[].createdAt` | string | ISO 8601 timestamp |
| `drafts[].updatedAt` | string | ISO 8601 timestamp |
| `hasMore` | boolean | Whether more results are available |
| `nextCursor` | string | Pass as afterCursor to fetch the next page |

**Output (action=get):** Single draft object with `id`, `text`, `topic`, `goal`, `createdAt`, `updatedAt`.

**Output (action=delete):**

| Field | Type | Description |
|-------|------|-------------|
| `deleted` | boolean | Whether the draft was deleted |

**Annotations:** --- | **Cost:** Free (subscription required)

---

## MCP vs REST API

Both interfaces access the same Xquik platform. Choose based on your integration:

| | MCP Server (v2) | MCP Server (v1 legacy) | REST API |
|---|------------|----------|----------|
| **URL** | `https://xquik.com/mcp` | `https://xquik.com/mcp/v1` | `https://xquik.com/api/v1` |
| **Transport** | StreamableHTTP | StreamableHTTP | HTTPS + JSON |
| **Auth** | `x-api-key` or OAuth 2.1 | `x-api-key` or OAuth 2.1 | `x-api-key` header |
| **Best for** | AI agents, IDE integrations | Legacy MCP integrations | Custom apps, scripts, backend services |
| **Model** | 2 tools (sandbox) | 18 discrete tools | 76 endpoints |
| **User profile** | Subset: name, bio, follower/following counts, profile picture | Full: adds verified, location, createdAt, statusesCount |
| **Follow check** | `following` / `followedBy` | `isFollowing` / `isFollowedBy` |
| **Monitor username field** | `xUsername` | `username` |
| **Event fields** | `eventType`, `eventData`, `monitoredAccountId` | `type`, `data`, `monitorId` |
| **Search results** | id, text, authorUsername, authorName, createdAt | id, text, createdAt, optional metrics, author object |
| **Webhook update** | Not available (delete + recreate via `webhooks` action=remove then action=add) | `PATCH /webhooks/{id}` |
| **Monitor update** | Not available (delete + recreate via `monitors` action=remove then action=add) | `PATCH /monitors/{id}` |
| **Export** | Not available (use REST) | `GET /extractions/{id}/export`, `GET /draws/{id}/export` |

**Key differences:**
- REST `GET /x/users/{username}` returns `verified`, `location`, `createdAt`, `statusesCount` that MCP `get-user-info` does not
- REST `GET /x/tweets/search` returns optional engagement metrics; MCP `search-tweets` returns basic info only
- REST supports PATCH for monitors and webhooks; MCP requires delete + recreate
- REST supports file export (CSV, XLSX, Markdown); MCP does not

---

## Annotation Summary

All 18 v1 tools declare MCP annotations indicating their behavior:

| Annotation | Meaning | Tools |
|------------|---------|-------|
| `readOnlyHint: true` | Does not modify any data | events, search-tweets, get-user-info, lookup-tweet, check-follow, get-account, get-trends, get-radar, compose-tweet |
| `destructiveHint: true` | Permanently deletes data | (handled within consolidated tools via action params: monitors action=remove, webhooks action=remove, styles action=delete, drafts action=delete) |
| `idempotentHint: true` | Safe to retry, same result | events, search-tweets, get-user-info, lookup-tweet, download-media, check-follow, get-account, subscribe, get-trends, get-radar, compose-tweet, set-x-identity |
| `openWorldHint: true` | Makes external network requests | monitors, search-tweets, get-user-info, webhooks, lookup-tweet, download-media, check-follow, extractions, draws, subscribe, get-trends, get-radar, styles |

---

## Common Mistakes

- Do NOT use `extractions` action=run to get follower/following COUNT. Use `get-user-info`
- Do NOT use `extractions` action=run with `post_extractor` to find latest tweets. Use `search-tweets from:username`
- Do NOT use `search-tweets` when you have a tweet ID/URL. Use `lookup-tweet`
- Do NOT use `events` for non-monitored accounts. Use `search-tweets`
- Do NOT use `extractions` action=run to get retweet/reply/like COUNTS. Use `lookup-tweet`
- Do NOT use `search-tweets` to find trending topics. Use `get-trends` (X trends) or `get-radar` (multi-source trends)
- Do NOT run extractions without estimating cost. Use `get-account` + `extractions` action=estimate
- Do NOT use `get-user-info` to check verification. Use `search-tweets from:username` + `lookup-tweet` (author.verified)
- Do NOT manually search replies and pick random winners. Use `draws` action=run which handles filtering, deduplication, and cryptographically secure random selection
- Do NOT invent tool types like "like_extractor" or "bookmark_extractor". Likes and bookmarks are NOT available
- Do NOT use `lookup-tweet` to download media. Use `download-media` which downloads and hosts the files permanently
- Do NOT compose tweets without calling `compose-tweet` step=compose first. It provides algorithm-backed signals that dramatically improve engagement. ALWAYS call it before drafting any tweet text
- Do NOT call `styles` action=analyze without checking `styles` action=get first. The cached style may already exist
- Do NOT call `styles` action=analyze-performance without first caching tweets via `styles` action=analyze
- Do NOT forget to call `set-x-identity` before style analysis if you want own-account detection
- Do NOT loop `search-tweets` for bulk results. It returns ~20 tweets with no pagination. Use `extractions` action=run with `tweet_search_extractor` for bulk keyword search (up to 1,000)
- Do NOT run extractions without `resultsLimit` when the user specifies a count. "100 tweets" means `resultsLimit: 100`. Omitting it extracts ALL data and wastes credits
- Do NOT call old tool names like `list-monitors`, `add-monitor`, `remove-monitor`, `get-events`, `get-event`, `list-webhooks`, `add-webhook`, `remove-webhook`, `test-webhook`, `run-extraction`, `estimate-extraction`, `list-extractions`, `get-extraction`, `run-draw`, `list-draws`, `get-draw`, `analyze-style`, `get-style`, `list-styles`, `delete-style`, `compare-styles`, `analyze-performance`, `refine-tweet`, `score-tweet`, `save-draft`, `list-drafts`, `get-draft`, `delete-draft`. These have been consolidated into 18 tools with `action` or `step` parameters

## Unsupported Operations

These are not available through the MCP server or REST API:

- Tweets a user liked or bookmarked
- Posting tweets, liking, retweeting, following
- DMs or private/protected account data
- Exporting extraction results as files (use REST API: `GET /api/v1/extractions/{id}/export`)
