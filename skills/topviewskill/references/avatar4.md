# Avatar4 Module

Generate a realistic talking avatar video from a single photo.

## When to Use

When you need to create a talking-head video from a portrait image — for marketing, education, product demos, or social media content.

## Subcommands

| Subcommand | When to use | Polls? |
|------------|-------------|--------|
| `run` | **Default.** New request, start to finish | Yes — waits until done |
| `submit` | Batch: fire multiple tasks without waiting | No — exits immediately |
| `query` | Recovery: resume polling a known `taskId` | Yes — waits until done |
| `list-captions` | Discover available caption styles for `--caption` | No |

## Usage

```bash
python {baseDir}/scripts/avatar4.py <subcommand> [options]
```

## Examples

### `run` — Full Flow (DEFAULT)

```bash
python {baseDir}/scripts/avatar4.py run \
  --image <fileId> \
  --text "Hello from Avatar 4!" \
  --voice <voiceId>
```

Local image (auto-uploads):

```bash
python {baseDir}/scripts/avatar4.py run \
  --image /path/to/photo.png \
  --text "Welcome to Topview." \
  --voice LaaHTrXZCVOQmB1wZUhnwmbPTAWDFtW6
```

Audio-driven mode:

```bash
python {baseDir}/scripts/avatar4.py run \
  --image /path/to/photo.png \
  --audio /path/to/recording.mp3
```

Download result:

```bash
python {baseDir}/scripts/avatar4.py run \
  --image <fileId> --text "Hello!" --voice <voiceId> \
  --output result.mp4
```

### `submit` — Batch

```bash
T1=$(python {baseDir}/scripts/avatar4.py submit \
  --image img1.png --text "Video 1" --voice <id> -q)
T2=$(python {baseDir}/scripts/avatar4.py submit \
  --image img2.png --text "Video 2" --voice <id> -q)

python {baseDir}/scripts/avatar4.py query --task-id "$T1"
python {baseDir}/scripts/avatar4.py query --task-id "$T2"
```

### `query` — Recovery

```bash
python {baseDir}/scripts/avatar4.py query --task-id <taskId> --timeout 1200
```

## Options

### `run` and `submit`

| Option | Description |
|--------|-------------|
| `--image ID` | Image fileId or local file path (required) |
| `--text TEXT` | TTS text for the avatar to speak (use with `--voice`) |
| `--voice ID` | Voice ID (required when using `--text`) |
| `--audio ID` | Audio fileId or local path for audio-driven mode (alternative to `--text`) |
| `--mode MODE` | `avatar4` (default) or `avatar4Fast` |
| `--motion TEXT` | Custom action description (max 600 chars) |
| `--caption ID` | Caption style ID |
| `--save-avatar` | Save the image as a reusable custom avatar |
| `--notice-url URL` | Webhook URL for completion notification |

### Polling (`run` and `query`)

| Option | Description |
|--------|-------------|
| `--timeout SECS` | Max polling time in seconds (default: 600) |
| `--interval SECS` | Polling interval in seconds (default: 5) |

### Global

| Option | Description |
|--------|-------------|
| `--output FILE` | Download result video to this local path |
| `--json` | Output full JSON response |
| `-q, --quiet` | Suppress status messages on stderr |

## Mode Comparison

| Mode | Max Duration | Speed | Quality |
|------|-------------|-------|---------|
| `avatar4` | 120s | Slow | Best |
| `avatar4Fast` | 120s | Fast | Good |

## Caption Discovery

Use `list-captions` to find available caption styles, then pass the `captionId` to `--caption`:

```bash
# List all caption styles
python {baseDir}/scripts/avatar4.py list-captions

# Use a captionId with a generation task
python {baseDir}/scripts/avatar4.py run \
  --image photo.png --text "Hello!" --voice <voiceId> \
  --caption <captionId>
```

Each caption entry includes a `thumbnail` URL for visual preview.

## Output

`run` and `query` print the video URL. With `--json`, full API response.
