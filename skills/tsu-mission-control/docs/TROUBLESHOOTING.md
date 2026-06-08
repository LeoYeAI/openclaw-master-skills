# Troubleshooting

Common problems and how to fix them.

---

## Installation Problems

### "Cannot find module" or dependency errors

Run the install command again:

```bash
cd ~/.openclaw/mission-control
npm run install:all
```

If that fails, delete node_modules and retry:

```bash
rm -rf backend/node_modules frontend/node_modules
npm run install:all
```

### "Permission denied" during install

On Mac/Linux, try:

```bash
sudo npm run install:all
```

Or fix npm permissions: [docs.npmjs.com/resolving-eacces-permissions-errors](https://docs.npmjs.com/resolving-eacces-permissions-errors)

### "Port already in use" error

Something else is using port 8000 or 4173. Find out what:

```bash
lsof -i :8000    # Mac/Linux
netstat -ano | findstr :8000   # Windows
```

Either stop the other program, or change the port in `backend/.env`:

```
PORT=8001
```

And update `CORS_ORIGIN` to match your frontend port if it also changed.

---

## Dashboard Problems

### Dashboard loads but shows no data

This is normal when you first start. The database is empty. Create a project or submit a request to see content.

If you previously had data and it's gone, check the database file:

```bash
ls -la ~/.openclaw/mission-control/backend/data/
```

You should see `mission-control.db`. If it's missing, Mission Control will create a fresh one on next start.

### Dashboard shows "Connecting..." instead of "Live"

The SSE (Server-Sent Events) connection between frontend and backend isn't working. Check:

1. Is the backend running? Visit http://localhost:8000/api/health in your browser
2. Is the frontend proxy configured? Check `frontend/vite.config.js` — the proxy should point to port 8000
3. Are CORS settings correct? Check `CORS_ORIGIN` in `backend/.env`

### Sidebar badge shows wrong count

Click the "↻ Refresh" button in the header. If counts still seem wrong, check the API directly:

```bash
curl http://localhost:8000/api/inbox/counts
```

---

## Agent Integration Problems

### Agents aren't sending updates

Check three things:

1. **Hook installed?**
   ```bash
   openclaw hooks list
   ```
   You should see `mission-control` listed as enabled.

2. **Secrets match?** The `HOOK_SECRET` in `backend/.env` must be **identical** to `MISSION_CONTROL_HOOK_SECRET` in `openclaw.json`. Even one character difference will cause authentication to fail silently.

3. **Backend reachable?** The Mission Control backend must be running when agents try to report. If it's not running, hook events are silently dropped.

### Hook is installed but events aren't arriving

Test the hook manually:

```bash
curl -X POST http://localhost:8000/api/hooks/event \
  -H "Content-Type: application/json" \
  -H "X-Hook-Secret: YOUR_HOOK_SECRET" \
  -d '{"event": "agent:idle", "agentId": "test", "data": {"message": "test"}}'
```

You should get `{"ok": true, "event": "agent:idle"}`. If you get a 401, the secret is wrong. If you get connection refused, the backend isn't running.

### Gateway connection shows errors

Check the backend logs (visible in the terminal where you ran `npm run dev`). Common issues:

- **Wrong gateway URL**: Verify `OPENCLAW_GATEWAY_URL` in `backend/.env` matches your actual gateway address
- **Wrong gateway token**: Get the correct token with `openclaw gateway status --json`
- **Gateway not running**: Start it with `openclaw gateway` or `openclaw gateway restart`

---

## Library Problems

### Documents aren't appearing after agent publishes

1. Check the backend logs for `library:published` events
2. Verify the agent is sending `library:publish` (not `library:published`) as the event name
3. Check that the collection_id is valid (use one of the defaults like `col_research`)

### Search returns no results

FTS5 search requires at least 3 characters. Single-word searches work best. Try broader terms.

If search never returns results, the FTS index may not have been created. Restart the backend — it rebuilds indexes from the migration on startup.

---

## Performance

### Dashboard is slow

The SQLite database handles thousands of documents and tasks without issues. If the dashboard feels slow:

1. Check your browser's dev tools (F12 → Network tab) for slow API calls
2. The Activity feed loads the last 50 events by default — this is fast
3. Library full-text search is indexed — it shouldn't be slow

### Database file is very large

The database grows as activity accumulates. To see its size:

```bash
ls -lh ~/.openclaw/mission-control/backend/data/mission-control.db
```

Under normal use, it should stay under 50MB. If it's much larger, old activity_log entries might be accumulating. You can safely delete old entries:

```bash
sqlite3 backend/data/mission-control.db "DELETE FROM activity_log WHERE created_at < datetime('now', '-30 days')"
```

---

## Getting Help

If none of the above fixes your issue:

1. Check the backend terminal for error messages
2. Check the browser console (F12 → Console tab) for frontend errors
3. Verify all configuration with: `cat backend/.env` and `cat ~/.openclaw/openclaw.json`
4. Try a fresh install: delete the mission-control directory and run `setup.sh` again
