# Voice Module

List/search available voices, clone custom voices from audio samples, and delete cloned voices.

## When to Use

- **Before text2voice** — use `list` to find the right voiceId when the user hasn't specified one
- **Custom voice** — use `clone` when the user wants to create a voice that sounds like a specific person
- **Cleanup** — use `delete` to remove custom voices the user no longer needs

## Subcommands

| Subcommand | Description | Polls? |
|------------|-------------|--------|
| `list` | Search/browse available voices (system + custom) | No |
| `clone` | **Default.** Clone voice from audio: submit + poll until done | Yes |
| `clone-submit` | Submit clone task only, print taskId | No |
| `clone-query` | Poll an existing clone taskId until done | Yes |
| `delete` | Delete a custom (cloned) voice | No |

## Usage

```bash
python {baseDir}/scripts/voice.py <subcommand> [options]
```

## Examples

### List Voices

Browse all English voices:

```bash
python {baseDir}/scripts/voice.py list --language en
```

Filter by gender and style:

```bash
python {baseDir}/scripts/voice.py list --language en --gender female --style UGC
```

List Chinese male voices:

```bash
python {baseDir}/scripts/voice.py list --language zh-CN --gender male
```

Show only custom (cloned) voices:

```bash
python {baseDir}/scripts/voice.py list --custom
```

Full JSON output with pagination:

```bash
python {baseDir}/scripts/voice.py list --language ja --page 1 --size 50 --json
```

### Clone a Voice

From a local audio file:

```bash
python {baseDir}/scripts/voice.py clone \
  --audio recording.mp3 \
  --name "My Brand Voice"
```

With reference text (improves clone quality):

```bash
python {baseDir}/scripts/voice.py clone \
  --audio sample.wav \
  --name "Brand Voice" \
  --text "Welcome to topview.ai, the ultimate AI video platform."
```

With speed adjustment:

```bash
python {baseDir}/scripts/voice.py clone \
  --audio voice_sample.mp3 \
  --name "Fast Narrator" \
  --speed 1.1
```

### Clone Batch / Recovery

```bash
T1=$(python {baseDir}/scripts/voice.py clone-submit \
  --audio sample1.mp3 --name "Voice A" -q)
T2=$(python {baseDir}/scripts/voice.py clone-submit \
  --audio sample2.mp3 --name "Voice B" -q)

python {baseDir}/scripts/voice.py clone-query --task-id "$T1"
python {baseDir}/scripts/voice.py clone-query --task-id "$T2"
```

### Delete a Custom Voice

```bash
python {baseDir}/scripts/voice.py delete --voice-id <voiceId>
```

## Options

### `list`

| Option | Description |
|--------|-------------|
| `--language CODE` | Language code: `en`, `zh-CN`, `ja`, `ko`, `fr`, `de`, etc. |
| `--gender` | `male` / `female` |
| `--age` | `Young` / `Middle Age` / `Old` |
| `--style` | `UGC` / `Advertisement` / `Cartoon_And_Animals` / `Influencer` |
| `--accent` | Accent filter: `American`, `British`, `Chinese`, etc. |
| `--custom` | Show only custom (cloned) voices |
| `--page N` | Page number (default: 1) |
| `--size N` | Items per page (default: 20) |

### `clone` and `clone-submit`

| Option | Description |
|--------|-------------|
| `--audio FILE` | Audio file (fileId or local path). Required. Format: mp3/wav, 10s-5min, <10MB |
| `--name NAME` | Name for the cloned voice (defaults to taskId) |
| `--text TEXT` | Reference text matching the audio content (improves quality) |
| `--speed FLOAT` | Voice speed 0.8-1.2 (default: 1.0) |
| `--notice-url URL` | Webhook URL |

### `delete`

| Option | Description |
|--------|-------------|
| `--voice-id ID` | voiceId of the voice to delete (required) |

### Polling / Global

| Option | Description |
|--------|-------------|
| `--timeout SECS` | Max polling time (default: 300) |
| `--interval SECS` | Polling interval (default: 5) |
| `--json` | Full JSON response |
| `-q, --quiet` | Suppress status messages |

## Voice Clone Audio Requirements

- **Format:** mp3 or wav
- **Duration:** 10 seconds to 5 minutes
- **Size:** under 10MB
- **Quality:** clear speech, minimal background noise produces best results

## Output

### `list` — tab-separated (default)

```
voiceId    voiceName    language    gender    age    style    accent    demoAudioUrl
```

### `clone` — structured

```
status: success
  voiceId:   abc123def456
  voiceName: My Brand Voice
  demoAudio: https://example.com/demo.mp3
```

### Supported Languages

`en`, `ar`, `bg`, `hr`, `cs`, `da`, `nl`, `fil`, `fi`, `fr`, `de`, `el`, `hi`, `hu`, `id`, `it`, `ja`, `ko`, `ms`, `nb`, `pl`, `pt`, `ro`, `ru`, `zh-CN`, `sk`, `es`, `sv`, `zh-Hant`, `tr`, `uk`, `vi`, `th`

### Supported Accents

African, American, Argentinian, Australian, Brazilian, British, Chinese, Colombian, Dutch, Eastern European, Filipino, French, German, Indian, Indonesian, Italian, Japanese, Kazakh, Korean, Malay, Mexican, Middle Eastern, North African, Polish, Portuguese, Russian, Singaporean, Spanish, Swiss, Taiwanese, Thai, Turkish, Vietnamese
