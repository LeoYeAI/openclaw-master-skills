# Error Codes and Troubleshooting

## Error Code Reference

| Code | Meaning | Resolution |
|------|---------|------------|
| 0 | Success | No action needed |
| 1004 | Invalid or expired token | Re-authenticate with email/password. The script does this automatically. |
| 2001 | Insufficient credits | Top up credits at pangolinfo.com |
| 2007 | Account expired | Renew account subscription at pangolinfo.com |
| 10000 | Task execution failed | Retry the request. If persistent, check query/URL format. |
| 10001 | Task execution failed | Retry the request. May indicate a temporary server issue. |
| 404 | Incorrect URL address | Verify the target URL format |

## Authentication

### Token Lifecycle

- Tokens are **permanent** -- they do not expire on their own
- A token becomes invalid only if the account is deactivated
- Error code `1004` indicates the token needs to be refreshed
- The script caches tokens at `~/.pangolin_token`

### Token Resolution Order

1. `PANGOLIN_TOKEN` environment variable
2. Cached token at `~/.pangolin_token`
3. Fresh login using `PANGOLIN_EMAIL` + `PANGOLIN_PASSWORD`

### Auth Endpoint

```
POST https://scrapeapi.pangolinfo.com/api/v1/auth
Body: {"email": "<email>", "password": "<password>"}
Response: {"code": 0, "message": "ok", "data": "<token>"}
```

## Credit Management

- AI Mode API: **2 credits** per request
- AI Overview SERP API: **2 credits** per request
- Amazon Scrape API (json): **1 credit** per request
- Amazon Scrape API (rawHtml/markdown): **0.75 credits** per request
- Credits are only consumed on successful requests (code 0)
- Check your credit balance at [pangolinfo.com](https://www.pangolinfo.com)

## Common Issues

**"No authentication credentials" error**
Set environment variables: `export PANGOLIN_EMAIL=... PANGOLIN_PASSWORD=...`

**Empty AI overview in response**
Not all queries trigger an AI overview. Check `ai_overview` field in response. Try a more informational query.

**Timeout or network errors**
The script retries 3 times with exponential backoff. If all retries fail, check your network connection and the API status.

**Screenshot URL not returned**
Ensure `--screenshot` flag is passed (or `"screenshot": true` in request body).
