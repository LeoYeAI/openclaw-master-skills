# IM attachments and `resolve-input`

How to turn chat media into a **local path** or URL for `kaipai_ai.py run-task --input …`.

## Platform cheat sheet

| Platform | Typical source | Easiest path |
|----------|----------------|--------------|
| **Discord** | `attachments[0].url` | Often a public URL → pass directly to `--input`, or `resolve-input --url` |
| **Generic URL** | User paste | `--input "<url>"` or `resolve-input --url` |
| **Local file** | Host downloaded attachment | `--input /path/to/file` or `resolve-input --file` (copies to a unique name under `--output-dir`) |
| **Telegram** | `message.photo[-1].file_id` or video `file_id` | `resolve-input --telegram-file-id "…"` (**requires `TELEGRAM_BOT_TOKEN`**) |
| **Feishu** | `image_key` + `message_id` in content | `resolve-input --feishu-image-key … --feishu-message-id …` (**requires `FEISHU_APP_TOKEN`**) |

## `resolve-input` CLI

Writes a file under **`--output-dir`** (default `/tmp`) and prints JSON: `path`, `filename`, `bytes`.

```bash
# Local path (e.g. host saved an attachment)
python3 {baseDir}/scripts/kaipai_ai.py resolve-input \
  --file /tmp/user_upload.jpg \
  --output-dir /tmp

# Public URL (download first — useful if Kaipai cannot fetch the URL)
python3 {baseDir}/scripts/kaipai_ai.py resolve-input \
  --url "https://cdn.example.com/clip.mp4" \
  --output-dir /tmp
```

**Telegram** — token **only** via environment (never CLI):

```bash
TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" python3 {baseDir}/scripts/kaipai_ai.py resolve-input \
  --telegram-file-id "AgACAgIAAxk..." \
  --output-dir /tmp
```

**Feishu** — tenant token from your Feishu app (same as other IM resource downloads):

```bash
FEISHU_APP_TOKEN="$FEISHU_APP_TOKEN" python3 {baseDir}/scripts/kaipai_ai.py resolve-input \
  --feishu-message-id "om_xxx" \
  --feishu-image-key "img_v3_xxx" \
  --output-dir /tmp
```

Optional: **`--feishu-app-token`** instead of env.

## Limits

Max download/copy size: **100 MB** (same guard as similar skills). For larger assets, use a direct URL if Kaipai can fetch it, or another upload path your tenant supports.

## Then run Kaipai

Use the printed **`path`** as **`--input`**:

```bash
python3 {baseDir}/scripts/kaipai_ai.py run-task \
  --task eraser_watermark \
  --input "/tmp/kaipai_in_xxxxxxxxxx_user_upload.jpg"
```

Replace `{baseDir}` with the skill root (the parent of `scripts/`).
