# Utilities

## Bookmarks

- Add: `cd BASE_DIR && uv run scripts/bookmark.py add <url> [--note "text"]`
- List: `cd BASE_DIR && uv run scripts/bookmark.py list`
- Remove: `cd BASE_DIR && uv run scripts/bookmark.py remove <url>`
- When running a recipe on a bookmarked URL, mark it as used

## Scheduled discovery

By default, the skill generates the cron command for the user to install manually. With `--auto`, the skill writes the crontab directly and notifies Discord.

### Setup (default, manual)
1. Run: `cd BASE_DIR && uv run scripts/schedule.py setup BASE_DIR/brand-graphs/<brand>/ --interval <1h|30m|etc>`
2. Show the `cron_command` and `manual_steps` from the output to the user
3. User installs the cron themselves via `crontab -e`

### Setup (auto, opt-in)
If the user explicitly asks for automatic scheduling:
`cd BASE_DIR && uv run scripts/schedule.py setup BASE_DIR/brand-graphs/<brand>/ --interval <1h|30m|etc> --auto`
This writes the crontab entry directly and notifies Discord. Only use when the user explicitly opts in.

### Status
`cd BASE_DIR && uv run scripts/schedule.py status`

### Stop
`cd BASE_DIR && uv run scripts/schedule.py stop`
If auto mode was used, this removes the crontab entry and notifies Discord. If manual, it shows instructions.

## Platform credentials

### Recommended: /setup-browser-cookies (gstack)
Tell user to run `/setup-browser-cookies`. Opens picker UI, user selects browser, imports cookies for reddit.com and x.com automatically.

### Manual fallback
1. Export cookies as JSON from browser DevTools or extension
2. Save to `BASE_DIR/creds/reddit-cookies.json` or `BASE_DIR/creds/x-cookies.json`
3. Format: `[{"name": "...", "value": "...", "domain": "...", "path": "/"}]`
4. Reddit needs: `reddit_session`, `token_v2`
5. X needs: `auth_token`, `ct0`

Cookies are gitignored and never sent to external services.

## History

Scan `BASE_DIR/content/` directories. Show recent runs with: date, recipe, brand, block count, publish status. Sort by most recent.

## Error handling

- Unreachable URL: tell user, ask for alternative
- Malformed recipe YAML: tell user which field is broken
- Failed prerequisite: report error, ask to continue with remaining steps
- Empty synthesis output: retry once, then show warning
- Never silently skip a step
