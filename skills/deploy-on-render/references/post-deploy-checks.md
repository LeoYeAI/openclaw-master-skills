# Post-deploy checks

Use this after any deploy or Blueprint apply. Keep it short; stop when a check fails.

## 1) Confirm deploy status (API)

With `RENDER_API_KEY` set:

```bash
# List services to get serviceId
curl -s -H "Authorization: Bearer $RENDER_API_KEY" "https://api.render.com/v1/services" | head -200

# List latest deploy for the service
curl -s -H "Authorization: Bearer $RENDER_API_KEY" "https://api.render.com/v1/services/<serviceId>/deploys?limit=1"
```

- Expect `status: "live"` in the latest deploy.
- If status is `failed`, inspect build/runtime logs (see below).

## 2) Verify service health

- Hit the health endpoint (preferred) or `/` and confirm a 200 response.
- If there is no health endpoint, add one and redeploy.

### Health check troubleshooting

- **404 on health path:** Ensure `healthCheckPath` in render.yaml matches a route the app actually serves (e.g. `/health` or `/`).
- **Timeouts:** App may be slow to start or not listening on `$PORT`. Check start command and that the app binds to `0.0.0.0:$PORT`.
- **5xx after deploy:** Check runtime logs for uncaught errors; verify DB/Redis URLs and migrations.

## 3) Fetch and scan logs via API

With `RENDER_API_KEY`, list recent logs for a service:

```bash
# List logs for a service (use resource type and id from the service/deploy)
curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
  "https://api.render.com/v1/logs?resourceType=service&resourceId=<serviceId>&limit=50"
```

- Pagination: if response has `hasMore: true`, use `nextStartTime` and `nextEndTime` for the next request.
- Real-time: use `GET https://api.render.com/v1/logs/subscribe` (WebSocket) for streaming; see [API docs](https://api-docs.render.com/reference/list-logs).

Filter by level when possible (e.g. error logs) to spot failures quickly.

## 4) Common error patterns and fixes

| Pattern | Likely cause | Fix |
|--------|--------------|-----|
| `EADDRINUSE` / port in use | App not using `$PORT` or binding to wrong host | Bind to `0.0.0.0:$PORT`; read `PORT` from env |
| `Module not found` / `No module named` | Missing dependency or wrong build | Fix buildCommand; ensure lockfile is committed |
| `connection refused` (DB/Redis) | Wrong URL or DB not ready | Check `sync: false` secrets set in Dashboard; use `fromDatabase`/`fromService` names that match Blueprint |
| `Invalid or expired token` | Env var not set or wrong | User must set secret in Dashboard (e.g. API key, JWT secret) |
| Health check failed / timeout | App not listening on PORT or path wrong | Bind to `0.0.0.0:$PORT`; set `healthCheckPath` to existing route or remove to use `/` |

See [troubleshooting-basics.md](troubleshooting-basics.md) for build vs startup vs runtime classification.

## 5) Verify env vars and port binding

- Confirm all required env vars are set in Dashboard (especially secrets marked `sync: false`).
- Ensure the app binds to `0.0.0.0:$PORT` (not localhost).

## 6) Redeploy only after fixing the first failure

- Avoid repeated deploys without changes; fix one issue at a time.
