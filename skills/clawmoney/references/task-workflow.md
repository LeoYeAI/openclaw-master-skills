# Task Execution Workflow

Step-by-step guide for executing bounty tasks using BNBot MCP tools.

## Prerequisites

1. BNBot Chrome Extension must be active in Chrome
2. User must be logged into Twitter/X
3. Verify connection: call `get_extension_status` — expect `{ connected: true }`

## Execution Steps

### Step 1: Navigate to Tweet

```
Tool: navigate_to_tweet
Params: { tweetUrl: "https://x.com/user/status/123456" }
```

Wait 2-3 seconds for the page to fully load.

### Step 2: Like (if required)

```
Tool: like_tweet
Params: { tweetUrl: "https://x.com/user/status/123456" }
```

- Returns `{ success: true }` on success
- Returns `{ success: true, data: { alreadyDone: true } }` if already liked
- Wait 2-3 seconds after liking

### Step 3: Retweet (if required)

```
Tool: retweet
Params: { tweetUrl: "https://x.com/user/status/123456" }
```

- Clicks the retweet button and confirms the "Repost" option
- Returns `{ success: true }` on success
- Returns `{ success: true, data: { alreadyDone: true } }` if already retweeted
- Wait 2-3 seconds after retweeting

### Step 4: Reply (if required)

```
Tool: submit_reply
Params: { text: "Your reply text here", tweetUrl: "https://x.com/user/status/123456" }
```

**Important:**
- Always show the reply content to the user and get confirmation before calling
- If the task has `replyGuidelines`, follow them when composing the reply
- Keep replies genuine and relevant to the tweet content

### Step 5: Follow (if required)

```
Tool: follow_user
Params: { username: "targetuser" }
```

- Returns `{ success: true }` on success
- Returns `{ success: true, data: { alreadyDone: true } }` if already following

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Extension not connected | BNBot not running | Ask user to open browser with extension |
| Button not found | Page not loaded / wrong page | Wait and retry, or re-navigate |
| Timeout | Slow network or page | Increase wait time and retry |

## Action Pacing

Add delays between actions for natural pacing and to respect platform rate limits:
- Add **2-5 second delays** between each action
- Do not execute all actions instantly
- For replies, allow time between composing and submitting
