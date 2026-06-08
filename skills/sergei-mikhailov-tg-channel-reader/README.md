# sergei-mikhailov-tg-channel-reader

> OpenClaw skill for reading Telegram channels via MTProto (Pyrogram or Telethon)

An [OpenClaw](https://openclaw.ai) skill that lets your AI agent fetch and summarize posts from any Telegram channel — public or private (if you're subscribed).

## Features

- Fetch posts from one or multiple channels in one command
- Flexible time windows: `24h`, `7d`, `2w`, or specific date
- JSON output with views, forwards, and direct links
- Secure credential storage via env vars or config file
- Works with any public channel — no bot admin required

## Why Use This Skill Instead of Web Monitoring?

OpenClaw can monitor Telegram channels via web scraping, but this skill uses **MTProto** — the same official protocol used by the Telegram app itself. Here's why it matters:

| | Web monitoring | This skill (MTProto) |
|---|---|---|
| **Reliability** | Breaks when Telegram updates its web UI | Always works — official protocol |
| **Speed** | Slow (browser rendering) | Fast — direct API calls |
| **Private channels** | Public only | Any channel you're subscribed to |
| **Data richness** | Text only | Views, forwards, links, dates |
| **Rate limits** | Frequent blocks & captchas | Soft limits, sufficient for personal use |
| **Agent integration** | Requires extra parsing | Clean JSON, ready for agent to analyze |

**Bottom line:** if you follow Telegram channels regularly and want your agent to summarize them, this skill is faster, more reliable, and gives you richer data than web monitoring.

## Install via ClawHub

```bash
npx clawhub@latest install sergei-mikhailov-tg-channel-reader
```

Then install Python dependencies:

```bash
cd ~/.openclaw/workspace/skills/sergei-mikhailov-tg-channel-reader
pip install pyrogram tgcrypto telethon
pip install -e .
```

> **Linux users:** if you get `externally-managed-environment` error, use a virtual environment:
> ```bash
> python3 -m venv ~/.venv/tg-reader
> ~/.venv/tg-reader/bin/pip install pyrogram tgcrypto telethon
> ~/.venv/tg-reader/bin/pip install -e .
> echo 'export PATH="$HOME/.venv/tg-reader/bin:$PATH"' >> ~/.bashrc
> source ~/.bashrc
> ```

## Manual Install

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/bzSega/sergei-mikhailov-tg-channel-reader
cd sergei-mikhailov-tg-channel-reader
pip install pyrogram tgcrypto telethon
pip install -e .
```

## Setup

### Step 1 — Get Telegram API credentials

You need a personal Telegram API key. This is free and takes 2 minutes.

1. Open https://my.telegram.org in your browser
2. Enter your phone number (with country code, e.g. `+79991234567`) and click **Send Code**
3. Enter the confirmation code you receive in Telegram
4. Click **"API Development Tools"**
5. Fill in the form:
   - **App title**: any name (e.g. `MyReader`)
   - **Short name**: any short word (e.g. `myreader`)
   - Other fields can be left as default
6. Click **"Create application"**
7. You'll see your credentials:
   - **App api_id** — a number like `12345678`
   - **App api_hash** — a 32-character string like `a1b2c3d4e5f6789012345678abcdef12`

> Keep these credentials private. Never share or commit them to git.

### Step 2 — Set credentials securely

Choose the method that fits your setup. Avoid writing `TG_API_HASH` to shell profiles (`~/.bashrc`) — it ends up in backups, shell history, and is visible to other users on shared machines.

**Option A: `~/.tg-reader.json` (recommended)**
```bash
cat > ~/.tg-reader.json << 'EOF'
{
  "api_id": 12345678,
  "api_hash": "your_api_hash_here"
}
EOF
chmod 600 ~/.tg-reader.json
```
Works everywhere — agents, servers, interactive shells. File is outside the project and never committed.

**Option B: `direnv` (recommended for developers)**
```bash
# Install direnv, then create .envrc in your working directory
echo 'export TG_API_ID=12345678' >> .envrc
echo 'export TG_API_HASH=your_api_hash_here' >> .envrc
echo '.envrc' >> .gitignore
direnv allow
```

**Option C: System keychain (most secure)**
```bash
# Linux (secret-tool)
secret-tool store --label="TG API" service tg-reader username api
# Then retrieve at runtime: secret-tool lookup service tg-reader username api
```

**Option D: Environment variables (interactive shell only)**
```bash
export TG_API_ID=12345678
export TG_API_HASH="your_api_hash_here"
```
Set in your current shell session. For persistent storage, use Option A instead.

> Avoid storing `TG_API_HASH` in files that are backed up to the cloud or shared between users.

### Step 3 — Authenticate once

```bash
tg-reader auth
```

You'll be asked for your phone number. Enter it with country code (e.g. `+79991234567`) and confirm with `y` when prompted. You'll then receive a confirmation code in your Telegram app — look for a message from the official **"Telegram"** service chat (not SMS).

> If the code doesn't arrive — check all devices where Telegram is open (phone, desktop, web).

Authentication creates a session file at `~/.tg-reader-session.session`. You only need to do this once.

### Step 4 — Choose your library (optional)

By default, `tg-reader` uses **Pyrogram**. You can switch to **Telethon** if needed:

| Method | Command |
|--------|---------|
| One-time flag | `tg-reader fetch @durov --since 24h --telethon` |
| Persistent env var | `export TG_USE_TELETHON=true` (or add `"use_telethon": true` to `~/.tg-reader.json`) |
| Direct command | `tg-reader-pyrogram` or `tg-reader-telethon` |

Both implementations use the same API credentials and provide identical functionality. Telethon uses a separate session file (`~/.telethon-reader.session`).

### Step 5 — Start reading

```bash
# Last 24 hours from a channel
tg-reader fetch @durov --since 24h

# Last week, multiple channels
tg-reader fetch @channel1 @channel2 --since 7d --limit 200

# Human-readable format
tg-reader fetch @channel_name --since 24h --format text
```

## Usage with OpenClaw

Once installed and authenticated, just ask your agent:

> "Summarize the last 24 hours from @durov"
> "What's new in @hacker_news_feed this week?"
> "Check all my tracked channels and give me a digest"

The agent will automatically use `tg-reader` and summarize the results.

## Output Example

```json
{
  "channel": "@durov",
  "fetched_at": "2026-02-22T10:00:00Z",
  "count": 3,
  "messages": [
    {
      "id": 735,
      "date": "2026-02-22T08:15:00Z",
      "text": "Post content here...",
      "views": 120000,
      "forwards": 4200,
      "link": "https://t.me/durov/735"
    }
  ]
}
```

## Troubleshooting

**`tg-reader: command not found`**

If installed via venv, make sure the venv bin is in your PATH:
```bash
echo 'export PATH="$HOME/.venv/tg-reader/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Otherwise add `~/.local/bin`:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Or run directly with Python:
```bash
python3 -m tg_reader_unified auth
python3 -m tg_reader_unified fetch @channel --since 24h
```

**Confirmation code not arriving**
- Check all your Telegram devices — the code goes to the Telegram app, not SMS
- Look for a message from the official "Telegram" service chat
- If you hit a rate limit on my.telegram.org, wait a few hours and try again

**`ChannelInvalid` error**
- For public channels: double-check the username spelling
- For private channels: make sure you're subscribed with the authenticated account

**`FloodWait` error**
- Telegram is rate-limiting requests
- The error shows how many seconds to wait — just retry after that

## Security

This skill uses **MTProto** — the same protocol as the official Telegram app. This means:

- **`TG_API_HASH` is a secret** — treat it like a password. Never commit it to git, never share it.
- **Session file = full account access** — `~/.tg-reader-session.session` grants complete access to your Telegram account. Keep it on your machine only.
- **Never copy session files** between machines or share them with anyone.
- **Your agent can read private channels** you're subscribed to — this is by design, but be aware of it.

**What the skill does NOT do:**
- Does not send messages on your behalf
- Does not modify or delete anything
- Does not share your data with third parties

**Best practices:**
- Store credentials in env vars or `~/.tg-reader.json` (outside the project), not in files tracked by git
- Add `*.session` and `.tg-reader.json` to `.gitignore`
- Revoke your API app on my.telegram.org if credentials are compromised

## Legal

By using this skill you agree to the terms in [DISCLAIMER.md](./DISCLAIMER.md).

## License

MIT — made by [@bzSega](https://github.com/bzSega)
