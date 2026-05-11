# Publishing & Tracking

## Publish content

### Dry run first (always)
`cd BASE_DIR && uv run scripts/publish.py <content-dir> <platform> --dry-run [--subreddit <name>]`

Show preview. Ask: "Ready to publish?"

### Reddit
`cd BASE_DIR && uv run scripts/publish.py <content-dir> reddit --subreddit <name>`
- Requires cookies in BASE_DIR/creds/reddit-cookies.json
- UTM tracking auto-added to links
- Bot fills form and clicks submit via Driver.dev/Playwright
- Returns live post URL

### X
`cd BASE_DIR && uv run scripts/publish.py <content-dir> x`
- Requires cookies in BASE_DIR/creds/x-cookies.json
- Content trimmed to 280 chars
- Returns live tweet URL

Publish records saved to `<content-dir>/publish_records.json`.

## Track engagement

`cd BASE_DIR && uv run scripts/track_engagement.py --brand BASE_DIR/brand-graphs/<brand>/`

Visits each published URL, extracts:
- Reddit: upvotes, comments, live/removed
- X: likes, retweets, replies, views, live/removed

Updates `feedback.yaml` automatically. Show results as a table.

Alerts fire when metrics cross threshold (default 50).

## Content queue

`cd BASE_DIR && uv run scripts/queue.py [--brand <name>] [--status unpublished]`

Shows: run name, recipe, status (unpublished/published/partial), platforms, preview. Offer to publish or remix.

## Digest

`cd BASE_DIR && uv run scripts/digest.py BASE_DIR/brand-graphs/<brand>/ --period <hourly|daily|weekly> [--notify]`

Shows: posts tracked, total engagement, top/worst performer, platform breakdown. `--notify` sends to Discord.

## Stats (leaderboard)

The digest output includes a `leaderboard` field ranking recipes by avg engagement per platform. Show top 10.
