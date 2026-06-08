---
name: ai-photos
description: |
  Personal AI photo album for OpenClaw.

  Use when users say:
  - "index my photos"
  - "set up an AI photo album"
  - "search my photo library"
  - "reconnect my photo album"
  - "find photos of ..."
metadata:
  version: v2.2.0
---

# ai-photos

ai-photos turns one or more local photo sources into a searchable AI photo album for OpenClaw.

Supported formats:
- macOS: `jpg`, `jpeg`, `png`, `webp`, `heic`
- Linux: `jpg`, `jpeg`, `png`, `webp`
- Linux `heic`: best-effort only; do not promise captioning or preview support

When talking to users:
- try to match the user's language
- explain the outcome simply: choose local folders now, then use OpenClaw to search and organize them
- stay focused on the current ai-photos request
- keep user-facing replies short and product-level: progress, readiness, and what the user can do next
- keep implementation details internal unless the user asks or troubleshooting requires them
- once indexing is complete and the backend is confirmed ready, say the album is ready and invite the user to try a search
- when the user asks what ai-photos can do, or when handing off a ready album, briefly describe the product in user terms:
  - natural-language search across captions, scene labels, and tags
  - date-based browsing and filtering
  - a local web gallery for thumbnail browsing and large-photo viewing
  - photo detail view with caption, scene, tags, capture time, device, location, orientation, and file info when available
  - opening the original local file from the web UI
  - manual sync now, optional automatic indexing later
- when introducing the web UI, describe it as a local searchable gallery rather than an API or server unless implementation details are needed
- keep these capability descriptions short, concrete, and user-facing; do not drift into backend details

Suggested user-facing capability summary:

- "You can search your photos in plain language, filter by date, and browse everything in a local gallery."
- "The web UI shows thumbnails, opens large previews, and lets you inspect captions, tags, time, device, location, and other file details when available."
- "You can also open the original local file directly, and later either sync changes manually or turn on automatic indexing."

## Required outcome

This task is not complete until all of the following are true:

1. at least one photo source is chosen and readable for a new album
2. image analysis is verified to work in the current OpenClaw runtime
3. the album backend is created or reconnected and writable
4. the first import succeeds, or an existing album is verified reachable
5. the user explicitly approved automatic indexing or explicitly declined it
6. if automatic indexing was approved, OpenClaw heartbeat is configured without breaking existing heartbeat tasks, the ai-photos block is present in `HEARTBEAT.md`, and one verification heartbeat has run
7. the user has been told the album is ready and has been invited to try a search
8. the user has been sent the final handoff

## Internal terms

Use these terms for agent reasoning, troubleshooting, or recovery only.
Do not introduce them to the user unless needed.

- `photo sources`: one or more local paths scanned into the same album
- `album backend`: where the searchable photo index is stored
- `album profile`: saved reconnect information, stored automatically under `~/.openclaw/ai-photos/albums/default.json`
- `caption input JSONL`: the manifest file that still needs vision captions and import

If the user asks what to save for later, explain that OpenClaw saves the reconnect information automatically at `~/.openclaw/ai-photos/albums/default.json`, and that they only need to keep that file if they want a manual backup.

## Caption schema

Each captioned JSONL line should contain the original manifest fields plus vision-model output.

Required base fields:
- `file_path`
- `filename`
- `sha256`
- `mime_type`
- `size_bytes`
- `width`
- `height`
- `taken_at`
- `exif`

Vision fields:
- `caption`: one short factual sentence
- `tags`: array of 5-12 short tags
- `scene`: short scene label
- `objects`: array of the main visible objects
- `text_in_image`: visible text or `null`

Optional fields:
- `metadata`: free-form JSON object
- `search_text`: concatenated retrieval text; if omitted, the importer builds it

Example:

```json
{
  "file_path": "/photos/2026/03/cat.jpg",
  "filename": "cat.jpg",
  "sha256": "abc123",
  "mime_type": "image/jpeg",
  "size_bytes": 231231,
  "width": 3024,
  "height": 4032,
  "taken_at": "2026-03-12T09:12:00+00:00",
  "exif": {"Make": "Apple", "Model": "iPhone 15 Pro"},
  "caption": "A white cat resting on a gray sofa near a sunlit window.",
  "tags": ["cat", "sofa", "indoor", "sunlight", "pet"],
  "scene": "living room",
  "objects": ["cat", "sofa", "window"],
  "text_in_image": null,
  "metadata": {"source": "demo"}
}
```

## CLI runtime

This skill does not depend on a local Python environment or a checked-out Go source tree.
It uses the latest published `ai-photos` CLI release from:

- repository: `https://github.com/zoubingwu/openclaw-ai-photos`
- install dir: `~/.openclaw/ai-photos/bin`
- binary path: `~/.openclaw/ai-photos/bin/ai-photos`

At the start of every ai-photos task, run the bootstrap flow exactly once and reuse the resulting binary path for the rest of the task.

### Bootstrap flow

Run this shell block and capture its stdout as `AI_PHOTOS_BIN`:

```bash
ensure_ai_photos() {
  AI_PHOTOS_REPO="zoubingwu/openclaw-ai-photos"
  AI_PHOTOS_BIN_DIR="$HOME/.openclaw/ai-photos/bin"
  AI_PHOTOS_BIN="$AI_PHOTOS_BIN_DIR/ai-photos"

  mkdir -p "$AI_PHOTOS_BIN_DIR"

  os="$(uname -s | tr '[:upper:]' '[:lower:]')"
  case "$os" in
    darwin) goos="darwin" ;;
    linux) goos="linux" ;;
    *)
      echo "unsupported platform: $os" >&2
      return 1
      ;;
  esac

  arch="$(uname -m)"
  case "$arch" in
    x86_64|amd64) goarch="amd64" ;;
    arm64|aarch64) goarch="arm64" ;;
    *)
      echo "unsupported architecture: $arch" >&2
      return 1
      ;;
  esac

  archive_name="ai-photos_${goos}_${goarch}.tar.gz"
  archive_url="https://github.com/${AI_PHOTOS_REPO}/releases/latest/download/${archive_name}"
  tmp_dir="$(mktemp -d)"
  had_existing_binary=0
  if [ -x "$AI_PHOTOS_BIN" ]; then
    had_existing_binary=1
  fi

  if curl -fL "${archive_url}" -o "$tmp_dir/${archive_name}" \
    && tar -xzf "$tmp_dir/${archive_name}" -C "$tmp_dir" \
    && install -m 0755 "$tmp_dir/ai-photos" "$AI_PHOTOS_BIN"; then
    rm -rf "$tmp_dir"
    printf '%s\n' "$AI_PHOTOS_BIN"
    return 0
  fi

  rm -rf "$tmp_dir"
  if [ "$had_existing_binary" -eq 1 ]; then
    printf '%s\n' "$AI_PHOTOS_BIN"
    return 0
  fi

  echo "could not download ai-photos release archive" >&2
  return 1
}

AI_PHOTOS_BIN="$(ensure_ai_photos)"
```

Rules:
- always run the bootstrap flow before using the CLI
- the bootstrap flow downloads the latest stable release asset from `releases/latest/download/...` and does not call `api.github.com`
- if the latest asset download or unpack step fails, continue with the cached binary when one already exists
- if the latest asset download fails and no cached binary exists, setup is blocked
- do not tell the user to clone the repository or build the CLI locally unless troubleshooting requires it
- if you need command details, use `"$AI_PHOTOS_BIN" help` or `"$AI_PHOTOS_BIN" help <subcommand>`

## Onboarding

### Step 0 - Choose mode

User-facing:

- Ask whether the user wants to create a new photo album, reconnect an existing one, or search an already configured album.
- If they want to reconnect, explain that you will try the saved connection first and only ask for more details if needed.

`[AGENT]` Branching:

- `1`: continue to Step 1
- `2`: continue to Step 3 and Step 4
- `3`: go directly to Search flow
- if the user wants search but no configured album exists, tell them setup is required first

### Step 1 - Ask for photo folders

User-facing:

- Ask for one or more local folder paths that contain photos.

`[AGENT]`

Do not continue until the user has provided at least one photo source.

### Step 2 - Run preflight

User-facing:

- Tell the user you will quickly verify that the folders are readable and that image analysis works before importing anything.

`[AGENT]`

Before indexing anything, verify:
- each photo source exists and is readable
- the selected sources contain supported image files
- `agents.defaults.imageModel` is vision-capable
- image analysis actually works on a real image in the current OpenClaw runtime
- the installed CLI runs successfully
- local image preparation works on a real sample image through `"$AI_PHOTOS_BIN" prepare-image`

Suggested preflight sequence:
1. choose one real sample image from the provided sources
2. run `"$AI_PHOTOS_BIN" prepare-image --mode caption <sample-file>`
3. on macOS, also run `"$AI_PHOTOS_BIN" prepare-image --mode preview <sample-file>`
4. inspect the JSON result

If the image backend check fails:
- on macOS, treat this as blocking because `heic` and local preview preparation depend on `sips`
- on Linux, do not block setup for `jpg`, `jpeg`, `png`, or `webp`; OpenClaw can still caption those files directly from the original path
- on Linux, explain that preview preparation and large-image downscaling are reduced without a local backend
- only suggest installing ImageMagick when the user wants better local image preparation or troubleshooting requires it

If preflight fails:
- tell the user setup is blocked in plain language
- explain exactly what must be fixed without exposing unnecessary implementation details
- stop

### Step 3 - Choose the backend

`[AGENT]`

- if reconnecting, keep the existing backend
- otherwise use `db9` if it is installed and usable
- if `db9` is not available, use `TiDB Cloud Zero`
- if using `TiDB Cloud Zero`, tell the user to claim it if they want to keep it, but do not lead with backend details unless they matter

### Step 4 - Create or reconnect the album

User-facing for a new album:

- Tell the user setup is in progress and that the selected folders will be searchable through OpenClaw when it finishes.
- If useful, add one short product sentence such as: "You'll be able to search in plain language or browse everything in the local gallery once import finishes."

`[AGENT]`

For a new album, run exactly one setup command:

```bash
# db9
"$AI_PHOTOS_BIN" setup --source <photo-source-a> --source <photo-source-b> --backend db9 --target <db>

# TiDB
"$AI_PHOTOS_BIN" setup --source <photo-source-a> --source <photo-source-b> --backend tidb --target /path/to/tidb-target.json
```

Read the JSON output:
- `profile_path` tells you where the default album profile was saved
- `caption_input_jsonl` is the input for the first record ingestion pass
- `sync.to_caption` tells you how many records still need captions and import

`[AGENT]` For reconnect:
- try the saved default album profile first
- verify the backend is reachable
- verify the album can be searched or written
- ask only for missing backend details

Suggested reconnect check:

```bash
"$AI_PHOTOS_BIN" search --recent --limit 1
```

Do not continue until the backend is confirmed reachable.

### Step 5 - Run the shared record ingestion flow

Use this same flow for:
- the first album import
- later incremental updates

User-facing:

- Tell the user photos are being imported and that large libraries may take some time.

`[AGENT]`

Input:
- first import: `caption_input_jsonl` from `ai-photos setup`
- later updates: `incremental_manifest_jsonl` from `ai-photos sync`

Before generating records, read the `Caption schema` section in this file.

`[AGENT]` For each record in the input manifest:
1. run `"$AI_PHOTOS_BIN" prepare-image --mode caption <file_path>`
2. send the returned `output_path` to the vision-capable model
3. preserve the original manifest fields from the source image
4. add `caption`, `tags`, `scene`, `objects`, and `text_in_image`
5. write one JSON object per line into a captioned JSONL file
6. import it with:

```bash
"$AI_PHOTOS_BIN" import /tmp/photos.captioned.jsonl
```

Rules:
- keep captions short, factual, retrieval-oriented, and visually grounded
- `prepare-image` prefers macOS `sips` when available and also supports ImageMagick for Linux-friendly setups
- if `prepare-image` returns the original file path in caption mode, continue with that file instead of blocking the batch
- on Linux, allow direct caption fallback for `jpg`, `jpeg`, `png`, and `webp` when no local image backend is available
- do not promise Linux `heic` captioning or preview support
- do not invent names, sensitive traits, or stories
- do not replace the original `file_path` with the temporary derived image path
- if one file still cannot be captioned, skip only that file and continue the rest of the batch
- if there is nothing to caption, skip this step

### Step 6 - Enable automatic indexing

User-facing:

- Offer automatic indexing in plain language.
- Explain that OpenClaw can periodically check the selected folders for new or changed photos and update the album index.
- Ask whether the user wants to enable that now.

`[AGENT]`

If the user declines:
- skip this step
- do not change heartbeat config
- do not change `HEARTBEAT.md`

If the user says yes:
- inspect the existing heartbeat config before changing anything
- do not overwrite or replace existing heartbeat tasks
- do not tell the user to manually restart Gateway for heartbeat-only changes
- let OpenClaw handle heartbeat configuration using its normal mechanisms unless debugging requires lower-level manual steps
- reuse the existing heartbeat scope and workspace whenever possible
- if there is more than one reasonable heartbeat-enabled scope, do not guess; ask the user which one should own ai-photos automatic indexing
- do not convert an existing per-agent heartbeat setup back into a defaults-based setup
- preserve existing heartbeat behavior unless a missing setting must be filled with a reasonable default
- do not spell out or rely on a fixed command recipe unless the current environment requires debugging

Then update `<workspace>/HEARTBEAT.md` without removing unrelated content:
- if the file does not exist, create it
- if the file exists, preserve all existing user content
- manage only one ai-photos block delimited by stable markers
- if the ai-photos block already exists, replace only that block
- if the ai-photos block does not exist, append it to the end of the file

```md
<!-- ai-photos:auto-indexing:start -->
## ai-photos automatic indexing

- Read and learn how to use `ai-photos` skill
- Use `~/.openclaw/ai-photos/bin/ai-photos sync` to scan the configured photo folders for changes.
- Check the configured photo folders for changes and keep the album index up to date.
- If `to_caption` is `0`, it means nothing needs attention, reply `HEARTBEAT_OK`.
- If `to_caption` is greater than `0`, run the shared record ingestion flow using `incremental_manifest_jsonl`.
- Stay quiet unless indexing failed or user action is needed.
<!-- ai-photos:auto-indexing:end -->
```

Do not rewrite the whole file just to add this block.

Then verify once:
- trigger one heartbeat run if it is safe and practical in the current environment, otherwise wait for the next scheduled run
- check the heartbeat result and make sure the ai-photos task completed as intended
- do not claim success until the verification result is clear

Then tell the user the result:
- success: explain that automatic indexing is active and the verification run succeeded
- declined: explain that the album is ready, but future changes require a manual re-index
- failed: explain that the album is usable, but automatic indexing is not active yet

### Step 7 - Final handoff

User-facing handoff should include:
- that the album is ready to use
- how the user can use it now: search in plain language or ask OpenClaw to help organize photos
- whether automatic indexing is on or off, in one short sentence only when it matters
- when useful, mention the local gallery capabilities in one short sentence: browse thumbnails, open large previews, inspect metadata, and open the original file

Keep the handoff short and user-facing.
Default to readiness, status, and next actions.
Only include implementation details when the user asks or recovery requires them.

`[AGENT]`

Immediately after setup:
- hand off directly once setup is ready
- tell the user the album is ready to search
- invite the user to search in plain language or ask OpenClaw to help organize photos
- if the user declined automatic indexing, say clearly that the album is in manual-only indexing mode

## Search flow

When the user asks to find photos, run:

```bash
"$AI_PHOTOS_BIN" search --text "cat on sofa"
"$AI_PHOTOS_BIN" search --tag cat
"$AI_PHOTOS_BIN" search --date 2026-03
"$AI_PHOTOS_BIN" search --recent
```

When answering:
- summarize the best matches clearly and in plain language
- mention filenames, dates, or captions when useful
- answer at the product level unless the user asks for implementation details
- before sending an image file, run `"$AI_PHOTOS_BIN" prepare-image --mode preview <matched-file>`
- send the returned `output_path` when possible
- if preview preparation fails on Linux without a local image backend, say so briefly and fall back to the original file only when it is safe to send as-is
- if results are weak, say so and suggest a better query

## Local web search

When the user asks to open a browser view for the album:

1. start the local web service
2. prefer the saved album profile; use environment variables only to fill missing backend fields
3. wait for the JSON startup line and return the local URL to the user
4. keep the process running while the user is browsing

If the user wants to open the gallery from another device:
- recommend Tailscale as the default remote access path
- run `"$AI_PHOTOS_BIN" serve --host 0.0.0.0` only when they explicitly want remote access
- explain that the startup JSON still prints a browser URL for the machine running `ai-photos`; for remote access, share the machine's Tailscale IP or MagicDNS name instead
- do not recommend exposing the port directly to the public internet unless the user explicitly asks for that tradeoff
- clarify that "open original" opens the file on the machine running `ai-photos`, not on the remote client

Run:

```bash
"$AI_PHOTOS_BIN" serve
```

If the user wants a specific album profile:

```bash
"$AI_PHOTOS_BIN" serve --profile default
```

The web service provides:
- a local search page
- search/filter/detail APIs for the page
- thumbnail and preview endpoints
- an action to open the original local file on the machine running `ai-photos`

When handing the web UI to the user:
- describe the page in product terms, for example:
  - "The page lets you search in plain language, filter by date, scroll the gallery, open a large preview, and inspect metadata on the right."
  - "When a photo has metadata, the detail panel can show caption, scene, tags, capture time, device, location, orientation, and file info."
- prefer this product summary over technical endpoint descriptions unless the user is debugging

## Heartbeat run behavior

When a heartbeat arrives for a configured album:

1. run:

```bash
"$AI_PHOTOS_BIN" sync
```

2. read the JSON output
3. if `to_caption` is `0`, return `HEARTBEAT_OK`
4. if `to_caption` is greater than `0`, run the shared record ingestion flow using `incremental_manifest_jsonl`
5. stay quiet unless indexing failed or user attention is needed
