# Output schema (informal)

All commands return JSON: `{ ok, data | error }`.

## Post object

```json
{
  "id": "abc123",
  "fullname": "t3_abc123",
  "subreddit": "python",
  "title": "...",
  "author": "...",
  "score": 123,
  "num_comments": 45,
  "created_utc": 1737060000,
  "created_iso": "2026-01-16T12:00:00.000Z",
  "permalink": "https://www.reddit.com/r/python/comments/abc123/.../",
  "url": "https://...",
  "selftext_snippet": "...",
  "flair": "..."
}
```

## Comment object (flattened)

```json
{
  "id": "def456",
  "fullname": "t1_def456",
  "author": "...",
  "score": 10,
  "created_utc": 1737060100,
  "created_iso": "2026-01-16T12:01:40.000Z",
  "depth": 2,
  "parent_fullname": "t1_...",
  "permalink": "https://www.reddit.com/r/python/comments/abc123/.../def456/",
  "body_snippet": "..."
}
```
