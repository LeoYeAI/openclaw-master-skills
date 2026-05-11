# Reddit Skill for Clawdbot

Browse, search, post to, and moderate any subreddit from your agent.

## Quick Start

**Read-only** (no setup needed):
```bash
node scripts/reddit.mjs posts news --limit 5
node scripts/reddit.mjs search all "breaking news"
```

**Posting & Moderation** (requires OAuth):
1. Create a Reddit app at https://www.reddit.com/prefs/apps
2. Set environment variables (see Setup below)
3. Run `node scripts/reddit.mjs login` once to authorize

---

## Setup for Posting/Moderation

### 1. Create a Reddit App

1. Go to https://www.reddit.com/prefs/apps
2. Scroll down and click **"create another app..."**
3. Fill in:
   - **name**: anything (e.g., "clawdbot")
   - **type**: select **script**
   - **redirect uri**: `http://localhost:8080/callback`
4. Click **Create app**
5. Note your:
   - **Client ID** — the string under your app name
   - **Client Secret** — labeled "secret"

### 2. Set Environment Variables

Add these to your shell profile or Clawdbot's environment:

```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USERNAME="your_reddit_username"
export REDDIT_PASSWORD="your_reddit_password"
```

### 3. Authorize (One Time)

```bash
node scripts/reddit.mjs login
```

This opens a browser for OAuth. After authorizing, a token is saved to `~/.reddit-token.json` and auto-refreshes.

---

## Personalizing the Skill

The `SKILL.md` file tells your agent how to use this skill. You'll want to customize it for your setup:

### Update the Examples

Replace the generic subreddit names (`wallstreetbets`, `yoursubreddit`) with the ones you actually use:

```markdown
# Before
node {baseDir}/scripts/reddit.mjs posts wallstreetbets

# After
node {baseDir}/scripts/reddit.mjs posts mysubreddit
```

### Add Your Subreddits to the Notes

At the bottom of `SKILL.md`, add a section listing your subreddits:

```markdown
## My Subreddits

- **r/mysubreddit** — I'm a mod here (full access)
- **r/interestingtopic** — I follow this one
- **r/anotherone** — Read-only
```

This helps your agent know what it can do where.

### Customize the User-Agent (Optional)

In `scripts/reddit.mjs`, you can personalize the User-Agent string:

```javascript
// Find this line near the top:
const USER_AGENT = 'script:clawdbot-reddit:v1.0.0';

// Change to something like:
const USER_AGENT = 'script:my-reddit-bot:v1.0.0 (by /u/your_username)';
```

Reddit recommends including your username so they can contact you if needed.

---

## Commands Reference

| Command | Auth Required | Description |
|---------|---------------|-------------|
| `posts <subreddit>` | No | Get hot/new/top posts |
| `search <subreddit\|all> <query>` | No | Search posts |
| `comments <post_id>` | No | Get comments on a post |
| `submit <subreddit> --title "..." --text "..."` | Yes | Create a text post |
| `submit <subreddit> --title "..." --url "..."` | Yes | Create a link post |
| `reply <thing_id> "text"` | Yes | Reply to a post or comment |
| `mod remove <thing_id>` | Yes + Mod | Remove post/comment |
| `mod approve <thing_id>` | Yes + Mod | Approve post/comment |
| `mod sticky <post_id>` | Yes + Mod | Sticky a post |
| `mod queue <subreddit>` | Yes + Mod | View mod queue |
| `login` | — | Start OAuth flow |
| `whoami` | Yes | Check logged-in user |

### Options

- `--sort hot|new|top|controversial` — Sort order for posts
- `--time day|week|month|year|all` — Time filter for top/controversial
- `--limit N` — Number of results (default: 25)

---

## Rate Limits

- **With OAuth**: ~60 requests/minute
- **Without OAuth**: ~10 requests/minute

The skill handles token refresh automatically.

---

## Troubleshooting

**"Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET"**  
→ Environment variables aren't set. Check your shell profile or Clawdbot config.

**"Not logged in. Run: node reddit.mjs login"**  
→ You need to authorize first. Run the login command.

**"Reddit returned HTML instead of JSON"**  
→ Reddit sometimes does this under load. Wait a moment and try again.

**Token file location**: `~/.reddit-token.json`  
→ Delete this file to force re-authorization.

---

## License

MIT — do whatever you want with it.
