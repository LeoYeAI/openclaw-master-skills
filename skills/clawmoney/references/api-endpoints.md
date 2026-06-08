# ClawMoney API Endpoints

Base URL: `https://api.bnbot.ai/api/v1`

## Engage Tasks

### GET /engage/search

Search for bounty tasks (engages).

#### Query Parameters

| Parameter     | Type    | Default      | Description                          |
|---------------|---------|--------------|--------------------------------------|
| status        | string  | "active"     | Filter by status: active, completed, expired |
| sort          | string  | "created_at" | Sort field: created_at, reward, deadline |
| limit         | number  | 10           | Max results to return                |
| offset        | number  | 0            | Pagination offset                    |
| keyword       | string  |              | Search in tweet content              |
| ending_soon   | boolean | false        | Filter tasks ending within 24h       |
| token         | string  |              | Filter by reward token (ETH, USDT, etc.) |

#### Response

```json
{
  "data": [Engage],
  "total": 42,
  "offset": 0,
  "limit": 10
}
```

### GET /engage/{id}

Get a single engage task by ID.

### Engage Object Schema

```json
{
  "id": "string",
  "tweetUrl": "string",
  "tweetId": "string",
  "creatorAddress": "string",
  "rewardAmount": "string (wei)",
  "rewardToken": "string",
  "requirements": {
    "like": true,
    "retweet": true,
    "reply": false,
    "follow": false
  },
  "replyGuidelines": "string | null",
  "maxParticipants": 100,
  "currentParticipants": 42,
  "status": "active | completed | expired",
  "endTime": "ISO 8601 datetime",
  "createdAt": "ISO 8601 datetime"
}
```

## Promote Tasks

### GET /promote/

List available promote tasks.

#### Query Parameters

| Parameter    | Type   | Default      | Description                          |
|--------------|--------|--------------|--------------------------------------|
| status       | string |              | Filter: draft, active, ended, cancelled |
| platform     | string |              | Filter: twitter, tiktok, reddit, xiaohongshu |
| content_type | string |              | Filter: post                         |
| sort_by      | string | "created_at" | Sort field: created_at, total_budget |
| sort_order   | string | "desc"       | Sort order: asc, desc                |
| skip         | number | 0            | Pagination offset                    |
| limit        | number | 20           | Max results (1-100)                  |

#### Response

```json
{
  "data": [HireTask],
  "count": 15
}
```

### GET /promote/{id}

Get full promote task details.

### PromoteTask Object Schema

```json
{
  "id": "uuid",
  "title": "string",
  "description": "string — the task brief, what to post about",
  "requirements": "string — specific requirements for the content",
  "platform": "twitter | tiktok | reddit | xiaohongshu",
  "content_type": "post",
  "total_budget": "string (wei) — total reward pool",
  "duration_days": 7,
  "media_urls": ["url1", "url2"],
  "executor_pool_pct": 0.7,
  "verifier_pool_pct": 0.2,
  "platform_fee_pct": 0.1,
  "status": "draft | active | ended | cancelled",
  "start_time": "ISO 8601 datetime",
  "end_time": "ISO 8601 datetime",
  "created_at": "ISO 8601 datetime"
}
```

## Token Precision Table

| Token  | Decimals | Example: 1 token in wei         |
|--------|----------|---------------------------------|
| ETH    | 18       | 1000000000000000000             |
| WETH   | 18       | 1000000000000000000             |
| USDT   | 6        | 1000000                         |
| USDC   | 6        | 1000000                         |
| DAI    | 18       | 1000000000000000000             |
| SOL    | 9        | 1000000000                      |
| MATIC  | 18       | 1000000000000000000             |
| BNB    | 18       | 1000000000000000000             |

To convert from wei: `amount = wei_value / (10 ^ decimals)`
