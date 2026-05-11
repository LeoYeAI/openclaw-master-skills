# node-edge-tts Reference

node-edge-tts is a Node.js module that utilizes Microsoft Edge's online TTS (Text-to-Speech) service. It supports multiple voices, languages, and audio formats.

## Installation

```bash
npm install node-edge-tts
# or
npx node-edge-tts -t "Hello world"
```

## Core Concepts

### Voices

node-edge-tts provides access to Microsoft Edge's neural voices. Voice names follow this pattern:
- `en-US-AriaNeural` - English (US), female voice
- `en-US-GuyNeural` - English (US), male voice
- `es-ES-ElviraNeural` - Spanish (Spain), female voice

Format: `{language_code}-{region_code}-{Name}{VoiceType}`

### Output Formats

node-edge-tts supports various output formats for audio quality:
- `audio-24khz-48kbitrate-mono-mp3` - 24kHz, 48kbps, mono MP3 (default)
- `audio-24khz-96kbitrate-mono-mp3` - 24kHz, 96kbps, mono MP3 (higher quality)
- `audio-48khz-96kbitrate-stereo-mp3` - 48kHz, 96kbps, stereo MP3 (highest quality)

## Common Voice Names

### English
- `en-US-AriaNeural` (female, natural, recommended)
- `en-US-GuyNeural` (male, natural)
- `en-GB-SoniaNeural` (female, British)
- `en-GB-RyanNeural` (male, British)

### Spanish
- `es-ES-ElviraNeural` (female, Spain)
- `es-MX-DaliaNeural` (female, Mexico)

### French
- `fr-FR-DeniseNeural` (female)
- `fr-FR-HenriNeural` (male)

### German
- `de-DE-KatjaNeural` (female)
- `de-DE-ConradNeural` (male)

### Asian Languages
- `ja-JP-NanamiNeural` (Japanese, female)
- `zh-CN-XiaoxiaoNeural` (Chinese, female)
- `ko-KR-SunHiNeural` (Korean, female)

### Arabic
- `ar-SA-ZariyahNeural` (female)
- `ar-SA-HamedNeural` (male)

## Usage Patterns

### Command Line Usage

```bash
# Basic usage
npx node-edge-tts -t "Hello world" -f output.mp3

# With voice and language
npx node-edge-tts -t "Hello world" -v en-US-AriaNeural -l en-US -f output.mp3

# With pitch and rate
npx node-edge-tts -t "Hello world" --rate "+10%" --pitch "-10%" -f output.mp3

# With subtitles
npx node-edge-tts -t "Hello world" -f output.mp3 -s
```

### Module Usage

```javascript
const { EdgeTTS } = require('node-edge-tts');

async function generateSpeech(text, outputFile) {
  const tts = new EdgeTTS({
    voice: 'en-US-AriaNeural',
    lang: 'en-US',
    outputFormat: 'audio-24khz-48kbitrate-mono-mp3',
    pitch: 'default',
    rate: 'default',
    volume: 'default',
  });

  await tts.ttsPromise(text, outputFile);
}

generateSpeech('Hello world!', 'output.mp3');
```

### With Options

```javascript
const { EdgeTTS } = require('node-edge-tts');

async function generateSpeech(text, outputFile) {
  const tts = new EdgeTTS({
    voice: 'en-US-AriaNeural',
    lang: 'en-US',
    outputFormat: 'audio-24khz-96kbitrate-mono-mp3',
    saveSubtitles: true,
    proxy: 'http://localhost:7890',
    timeout: 10000,
    pitch: '+10%',
    rate: '+20%',
    volume: '-10%',
  });

  await tts.ttsPromise(text, outputFile);
  // Subtitles saved to output.json
}
```

## Prosody Options

### Rate (Speed)
Control speech speed with percentage adjustments:
- `"default"` - Normal speed (default)
- `"+10%"` - 10% faster
- `"-20%"` - 20% slower
- `"+50%"` - 50% faster

### Pitch
Adjust voice pitch in percentages:
- `"default"` - Normal pitch (default)
- `"+10%"` - Higher pitch
- `"-10%"` - Lower pitch

### Volume
Adjust volume level in percentages:
- `"default"` - Normal volume (default)
- `"+10%"` - 10% louder
- `"-20%"` - 20% quieter

## Subtitles

node-edge-tts supports JSON subtitle generation with word-level timing:

```bash
npx node-edge-tts -t "Hello world" -f output.mp3 -s
```

This generates:
- `output.mp3` - Audio file
- `output.json` - Subtitle file with timing data

**Subtitle format:**
```json
[
  {
    "part": "Hello ",
    "start": 100,
    "end": 500
  },
  {
    "part": "world",
    "start": 500,
    "end": 900
  }
]
```

- `part`: Word or phrase
- `start`: Start time in milliseconds
- `end`: End time in milliseconds

## Best Practices

1. **Choose appropriate voices**: Neural voices (ending in `Neural`) are higher quality
2. **Adjust rate for content**: Faster for news, slower for stories
3. **Use natural phrasing**: Punctuation affects speech rhythm
4. **Test voices**: Different voices work better for different content types
5. **Consider audience**: Choose voices that match your target audience
6. **Use subtitles for accessibility**: Generate subtitles for videos and presentations
7. **Optimize output format**: Higher bitrate for music/pro use, lower for voice notes

## CLI Options Reference

| Option | Short | Description | Default |
|--------|---------|-------------|----------|
| --help | -h | Show help | - |
| --version | | Show version number | - |
| --text | -t | Text to convert (required) | - |
| --filepath | -f | Output file path | "./output.mp3" |
| --voice | -v | Voice name | "zh-CN-XiaoyiNeural" |
| --lang | -l | Language code | "zh-CN" |
| --outputFormat | -o | Output format | "audio-24khz-48kbitrate-mono-mp3" |
| --pitch | | Pitch of voice | "default" |
| --rate | -r | Rate of voice | "default" |
| --volume | | Volume of voice | "default" |
| --saveSubtitles | -s | Save subtitles | false |
| --proxy | -p | Proxy URL | - |
| --timeout | | Request timeout (ms) | 10000 |

## Limitations

- Requires internet connection (uses Microsoft Edge online service)
- Maximum text length depends on the service
- Rate limiting may apply for excessive use
- Voice availability depends on Microsoft Edge service
- Not all prosody options work with all voices

## Integration with Clawdbot

When using with the `tts` tool:
1. Generate audio using node-edge-tts
2. Save the audio file to the workspace
3. Return the MEDIA: path to Clawdbot
4. Clawdbot routes the audio to the appropriate channel

Example flow:
```javascript
// Generate audio
const outputPath = await textToSpeech("Your text here", {
  voice: "en-US-AriaNeural",
  lang: "en-US",
});

// Return to Clawdbot via tts tool
// (handled internally by Clawdbot when you call the tts tool)
```

## Version Information

- Current version: 1.2.9
- Last published: 3 days ago
- License: MIT
- Homepage: github.com/SchneeHertz/node-edge-tts
