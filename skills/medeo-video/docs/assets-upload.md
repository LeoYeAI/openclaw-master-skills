# Uploading Assets (Images & Videos)

Medeo accepts user-provided images and videos as input assets for video generation. These can be used as reference images, character photos, scene backgrounds, or video clips to incorporate.

There are **three upload paths** depending on where the image comes from:

| Path | When to use | Command |
|------|-------------|---------|
| **URL upload** | Image already has a public URL | `upload --url "https://..."` |
| **Direct file upload** | Local file, IM attachment, or URL requiring download-first | `upload-file --file PATH` / `--url URL` / platform-specific flags |
| **Inline in generation** | Pass URLs directly to `spawn-task` (auto-uploaded) | `spawn-task --media-urls "https://..."` |

## 1. Upload via Public URL

Best when the image is already hosted publicly (e.g., product page, CDN link).

```bash
python3 {baseDir}/scripts/medeo_video.py upload --url "https://example.com/photo.jpg"
```

Returns:
```json
{"media_id": "media_01...", "media_ids": ["media_01..."], "job_id": "..."}
```

**API flow:** `POST /api/v2/medias:create_from_url` → poll job → media_id

## 2. Direct File Upload (`upload-file`)

Use when you have a local file or need to download from a platform that requires authentication (Telegram, Feishu, etc.).

**API flow:** `prepare_for_upload` → S3 presigned PUT → `create_from_upload` → poll job → media_id

### From a local file

```bash
python3 {baseDir}/scripts/medeo_video.py upload-file --file /tmp/photo.jpg
```

### From a URL (download first, then upload)

Useful when the URL might block server-side fetch (some CDNs, Discord attachments, etc.):

```bash
python3 {baseDir}/scripts/medeo_video.py upload-file --url "https://cdn.example.com/image.jpg"
```

### From Telegram attachment

```bash
python3 {baseDir}/scripts/medeo_video.py upload-file \
  --telegram-file-id "AgACAgIAAxk..." \
  --telegram-bot-token "$TELEGRAM_BOT_TOKEN"
```

- `--telegram-file-id`: from `message.photo[-1].file_id` (highest resolution)
- Bot token via env var `TELEGRAM_BOT_TOKEN` or `--telegram-bot-token` flag

### From Feishu attachment

```bash
python3 {baseDir}/scripts/medeo_video.py upload-file \
  --feishu-image-key "img_v3_xxx" \
  --feishu-message-id "om_xxx" \
  --feishu-app-token "$FEISHU_APP_TOKEN"
```

- `--feishu-image-key`: from the message content JSON
- `--feishu-message-id`: the message containing the image
- App token via env var `FEISHU_APP_TOKEN` or `--feishu-app-token` flag

### Output

All `upload-file` variants return:
```json
{"media_id": "media_01...", "filename": "photo.jpg"}
```

### Platform-Specific Image Extraction Guide

| Platform | How to get image source | `upload-file` arg |
|----------|------------------------|-------------------|
| **Telegram** | `message.photo[-1].file_id` | `--telegram-file-id` |
| **Discord** | `message.attachments[0].url` (public CDN URL) | `--url` |
| **Feishu** | `message_id` + `image_key` from message content JSON | `--feishu-image-key` + `--feishu-message-id` |
| **WhatsApp** | Download attachment binary → save to `/tmp` | `--file` |
| **Generic URL** | Any direct image URL | `--url` |

**Note:** Discord attachment URLs are public CDN links — `--url` works directly. All other IM platforms require authentication to download.

## 3. Inline Upload in Generation Pipeline

Pass URLs directly to `spawn-task` — they're auto-uploaded before compose:

```bash
python3 {baseDir}/scripts/medeo_video.py spawn-task \
  --message "Create a product showcase video for this sneaker" \
  --media-urls "https://example.com/sneaker-front.jpg" "https://example.com/sneaker-side.jpg"
```

Or pass pre-uploaded media IDs:

```bash
# Step 1: Upload first
python3 {baseDir}/scripts/medeo_video.py upload-file --file /tmp/photo.jpg
# → {"media_id": "media_01ABC..."}

# Step 2: Generate with the media_id
python3 {baseDir}/scripts/medeo_video.py spawn-task \
  --message "Create a video featuring this person" \
  --media-ids "media_01ABC..."
```

## Supported Formats

`.jpg`, `.png`, `.webp`, `.mp4`, `.mov`, `.gif`

## Common Use Cases

| Use Case | How |
|----------|-----|
| Character reference photo | Upload image → `--media-ids "media_01..."` + describe character in `--message` |
| Product showcase | Upload product images → `--media-ids` or `--media-urls` + describe video style |
| Scene background | Upload background → describe what happens in the scene |
| IM user sends image | `upload-file` with platform flag → get `media_id` → pass to `spawn-task` |
| Multiple references | Upload each → pass all IDs: `--media-ids "id1" "id2" "id3"` |

## Tips

- **Image quality matters** — higher resolution images produce better results
- **Multiple angles help** — for character/product videos, provide 2-3 reference images from different angles
- **IM images**: When a user sends an image directly in chat and asks for video generation, use `upload-file` to upload it — don't ask them for a URL
- **`upload-file --url` vs `upload --url`**: Use `upload-file --url` when the URL might block server-side fetch (the file is downloaded locally first then uploaded via S3). Use `upload --url` for reliable public URLs (faster, single API call)
- Medeo's AI agent will intelligently incorporate the assets into the video based on your `--message` description
