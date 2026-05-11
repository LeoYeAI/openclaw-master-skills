# Text-to-Voice Module

Convert text into speech audio with customizable voice, speed, emotion, and pronunciation.

## When to Use

When you need to generate speech audio from text — for voiceovers, narration, TTS previews, or as audio input for avatar4 video generation.

## Subcommands

| Subcommand | When to use | Polls? |
|------------|-------------|--------|
| `run` | **Default.** New request, start to finish | Yes — waits until done |
| `submit` | Batch: fire multiple tasks without waiting | No — exits immediately |
| `query` | Recovery: resume polling a known `taskId` | Yes — waits until done |

## Usage

```bash
python {baseDir}/scripts/text2voice.py <subcommand> [options]
```

## Examples

### Basic

```bash
python {baseDir}/scripts/text2voice.py run \
  --text "你好，欢迎使用文本转音频功能。" \
  --voice-id voice-888
```

### With Speed and Emotion

```bash
python {baseDir}/scripts/text2voice.py run \
  --text "今天天气真好！" \
  --voice-id voice-888 \
  --speed 1.2 \
  --emotion happy
```

### With Pronunciation Rules

```bash
python {baseDir}/scripts/text2voice.py run \
  --text "行不行？你行行行。" \
  --voice-id voice-888 \
  --pron-rules '[{"oldStr":"行","newStr":"xing"}]'
```

### Download Audio

```bash
python {baseDir}/scripts/text2voice.py run \
  --text "Hello, welcome!" \
  --voice-id voice-888 \
  --output result.mp3
```

### Batch

```bash
T1=$(python {baseDir}/scripts/text2voice.py submit \
  --text "Segment 1" --voice-id voice-888 -q)
T2=$(python {baseDir}/scripts/text2voice.py submit \
  --text "Segment 2" --voice-id voice-888 -q)

python {baseDir}/scripts/text2voice.py query --task-id "$T1"
python {baseDir}/scripts/text2voice.py query --task-id "$T2"
```

## Options

### `run` and `submit`

| Option | Description |
|--------|-------------|
| `--text TEXT` | Text to convert (required) |
| `--voice-id ID` | Voice ID (required) |
| `--name NAME` | Voice name label |
| `--speed FLOAT` | Speech speed (1.0 = normal) |
| `--emotion NAME` | Emotion: `happy`, `sad`, `angry`, etc. |
| `--origin-voice-file ID` | Original voice file fileId or local path |
| `--pron-rules JSON` | Pronunciation rules: `[{"oldStr":"行","newStr":"xing"}]` |
| `--board-id ID` | Board ID |
| `--notice-url URL` | Webhook URL |

### Polling / Global

| Option | Description |
|--------|-------------|
| `--timeout SECS` | Max polling time (default: 300) |
| `--interval SECS` | Polling interval (default: 3) |
| `--output FILE` | Download audio to local path |
| `--json` | Full JSON response |
| `-q, --quiet` | Suppress status messages |

## Cost

Fixed: **0.1 credits** per task. Failed tasks are refunded.

## Output

```
status: success  cost: 0.1 credits  duration: 12.5s
  audio: https://example.com/audio.mp3
```

With `--json`, includes voice metadata (language, gender, age, accent, duration).
