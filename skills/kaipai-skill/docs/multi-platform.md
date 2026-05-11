# Multi-Platform Delivery

After processing, send the result image or video back on the user’s IM platform.

## Overview

| Platform | Image result | Video result (`videoscreenclear`, `hdvideoallinone`) |
|---|---|---|
| Feishu | `feishu_send_image.py` | `feishu_send_video.py` — download to `.mp4`; use `--video-url` for a second text link; see [feishu-send-video.md](feishu-send-video.md) |
| Telegram | `telegram_send_image.py` | `telegram_send_video.py` — `sendVideo` + optional `--video-url` text link; ~50 MB limit |
| Discord | OpenClaw `message` + `filePath` | Same; use `.mp4`; ~25 MB — else send URL |
| WhatsApp / Signal / other | `message` + `media` or URL | Same |

| Platform | Mechanism (image) | Key parameters |
|---|---|---|
| Feishu | `feishu_send_image.py` | `--image <url_or_path>` `--to <oc_/ou_ id>` |
| Telegram | `telegram_send_image.py` | `--image <url_or_path>` `--to <chat_id>` `--caption <optional>` |
| Discord | OpenClaw `message` tool | `filePath=/tmp/result.jpg`; over ~25MB send a link |
| WhatsApp / Signal / other | `message` with `media` | or send the result URL |

---

## Feishu

```bash
python3 {baseDir}/scripts/feishu_send_image.py \
  --image "<result_url_or_local_path>" \
  --to "<oc_xxx or ou_xxx>"
```

**deliver-to resolution**

- Group: `conversation_label` or `chat_id` without the `chat:` prefix → `oc_xxx`
- DM: `sender_id` without the `user:` prefix → `ou_xxx`

Credentials are read from `~/.openclaw/openclaw.json` under `channels.feishu.accounts` (e.g. `main` / `default`); no extra CLI flags for secrets.

Supports HTTP(S) URLs (downloaded automatically) or local file paths.

**Video results:** use `feishu_send_video.py` after `curl` download — [feishu-send-video.md](feishu-send-video.md).

---

## Telegram

```bash
TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" python3 {baseDir}/scripts/telegram_send_image.py \
  --image "<result_url_or_local_path>" \
  --to "<chat_id>" \
  --caption "✅ Done"
```

**Security:** pass the bot token only via `TELEGRAM_BOT_TOKEN`; never on the command line (visible in `ps`, logs).

**deliver-to:** inbound message `chat_id` (e.g. `-1001234567890`).

Supports URL or local path.

**Video results:** `telegram_send_video.py` with local `.mp4`; pass `--video-url "<result_url>"` so a second message carries the download link (see overview table).

---

## Discord

Discord upload limit is about 25MB.

**Under ~25MB:** download then send as a file:

```bash
curl -L "<result_url>" -o /tmp/result_image.jpg
```

```
message(action="send", channel="discord", target="<channel_id>", filePath="/tmp/result_image.jpg")
```

**Over ~25MB:** send the result URL:

```
message(action="send", channel="discord", target="<channel_id>", text="Done: <result_url>")
```

**Security:** `DISCORD_BOT_TOKEN` only via environment variables.

---

## WhatsApp / Signal / other

Use the `message` tool with `media`, or send the result URL for the user to open in a browser.

---

## Security rules

- Never pass `TELEGRAM_BOT_TOKEN`, `DISCORD_BOT_TOKEN`, or similar as CLI arguments.
- Inject tokens through the environment to avoid leaking them in `ps` or logs.
