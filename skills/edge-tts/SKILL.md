---
name: edge-tts
description: |
  Text-to-speech conversion using node-edge-tts npm package for generating audio from text.
  Supports multiple voices, languages, speed adjustment, pitch control, and subtitle generation.
  Use when: (1) User requests audio/voice output with the "tts" trigger or keyword. (2) Content needs to be spoken rather than read (multitasking, accessibility, driving, cooking). (3) User wants a specific voice, speed, pitch, or format for TTS output.
---

# Edge-TTS Skill

## Overview

Generate high-quality text-to-speech audio using Microsoft Edge's neural TTS service via the node-edge-tts npm package. Supports multiple languages, voices, adjustable speed/pitch, and subtitle generation.

## Quick Start

When you detect TTS intent from triggers or user request:

1. **Call the tts tool** (Clawdbot built-in) to convert text to speech
2. The tool returns a MEDIA: path
3. Clawdbot routes the audio to the current channel

```javascript
// Example: Built-in tts tool usage
tts("Your text to convert to speech")
// Returns: MEDIA: /path/to/audio.mp3
```

## Trigger Detection

Recognize "tts" keyword as TTS requests. The skill automatically filters out TTS-related keywords from text before conversion to avoid converting the trigger words themselves to audio.

## Advanced Customization

### Using the Node.js Scripts

For more control, use the bundled scripts directly:

#### TTS Converter
```bash
cd scripts
npm install
node tts-converter.js "Your text" --voice en-US-AriaNeural --rate +10% --output output.mp3
```

**Options:**
- `--voice, -v`: Voice name (default: en-US-AriaNeural)
- `--lang, -l`: Language code (e.g., en-US, es-ES)
- `--format, -o`: Output format (default: audio-24khz-48kbitrate-mono-mp3)
- `--pitch`: Pitch adjustment (e.g., +10%, -20%, default)
- `--rate, -r`: Rate adjustment (e.g., +10%, -20%, default)
- `--volume`: Volume adjustment (e.g., +0%, -10%, default)
- `--save-subtitles, -s`: Save subtitles as JSON file
- `--output, -f`: Output file path (default: tts_output.mp3)
- `--proxy, -p`: Proxy URL (e.g., http://localhost:7890)
- `--timeout`: Request timeout in milliseconds (default: 10000)
- `--list-voices, -L`: List available voices

#### Configuration Manager
```bash
cd scripts
npm install
node config-manager.js --set-voice en-US-AriaNeural

node config-manager.js --set-rate +10%

node config-manager.js --get

node config-manager.js --reset
```

### Voice Selection

Common voices (use `--list-voices` for full list):

**English:**
- `en-US-MichelleNeural` (female, natural, **default**)
- `en-US-AriaNeural` (female, natural)
- `en-US-GuyNeural` (male, natural)
- `en-GB-SoniaNeural` (female, British)
- `en-GB-RyanNeural` (male, British)

**Other Languages:**
- `es-ES-ElviraNeural` (Spanish, Spain)
- `fr-FR-DeniseNeural` (French)
- `de-DE-KatjaNeural` (German)
- `ja-JP-NanamiNeural` (Japanese)
- `zh-CN-XiaoxiaoNeural` (Chinese)
- `ar-SA-ZariyahNeural` (Arabic)

### Rate Guidelines

Rate values use percentage format:
- `"default"`: Normal speed
- `"-20%"` to `"-10%"`: Slow, clear (tutorials, stories, accessibility)
- `"+10%"` to `"+20%"`: Slightly fast (summaries)
- `"+30%"` to `"+50%"`: Fast (news, efficiency)

### Output Formats

Choose audio quality based on use case:
- `audio-24khz-48kbitrate-mono-mp3`: Standard quality (voice notes, messages)
- `audio-24khz-96kbitrate-mono-mp3`: High quality (presentations, content)
- `audio-48khz-96kbitrate-stereo-mp3`: Highest quality (professional audio, music)

## Resources

### scripts/tts-converter.js
Main TTS conversion script using node-edge-tts. Generates audio files with customizable voice, rate, volume, pitch, and format. Supports subtitle generation and voice listing.

### scripts/config-manager.js
Manages persistent user preferences for TTS settings (voice, language, format, pitch, rate, volume). Stores config in `~/.tts-config.json`.

### scripts/package.json
NPM package configuration with node-edge-tts dependency.

### references/node_edge_tts_guide.md
Complete documentation for node-edge-tts npm package including:
- Full voice list by language
- Prosody options (rate, pitch, volume)
- Usage examples (CLI and Module)
- Subtitle generation
- Output formats
- Best practices and limitations

### Voice Testing
Test different voices and preview audio quality at: https://tts.travisvn.com/

Refer to this when you need specific voice details or advanced features.

## Installation

To use the bundled scripts:

```bash
cd /home/user/clawd/skills/public/tts-skill/scripts
npm install
```

This installs:
- `node-edge-tts` - TTS library
- `commander` - CLI argument parsing

## Workflow

1. **Detect intent**: Check for "tts" trigger or keyword in user message
2. **Choose method**: Use built-in `tts` tool for simple requests, or `scripts/tts-converter.js` for customization
3. **Generate audio**: Convert the target text (message, search results, summary)
4. **Return to user**: The tts tool returns a MEDIA: path; Clawdbot handles delivery

## Testing

### Basic Test
Run the test script to verify TTS functionality:
```bash
cd /home/user/clawd/skills/public/edge-tts/scripts
npm test
```
This generates a test audio file and verifies the TTS service is working.

### Voice Testing
Test different voices and preview audio quality at: https://tts.travisvn.com/

### Integration Test
Use the built-in `tts` tool for quick testing:
```javascript
// Example: Test TTS with default settings
tts("This is a test of the TTS functionality.")
```

### Configuration Test
Verify configuration persistence:
```bash
cd /home/user/clawd/skills/public/edge-tts/scripts
node config-manager.js --get
node config-manager.js --set-voice en-US-GuyNeural
node config-manager.js --get
```

## Troubleshooting

- **Test connectivity**: Run `npm test` to check if TTS service is accessible
- **Check voice availability**: Use `node tts-converter.js --list-voices` to see available voices
- **Verify proxy settings**: If using proxy, test with `node tts-converter.js "test" --proxy http://localhost:7890`
- **Check audio output**: The test should generate `test-output.mp3` in the scripts directory

## Notes

- node-edge-tts uses Microsoft Edge's online TTS service (updated, working authentication)
- No API key needed (free service)
- Output is MP3 format by default
- Requires internet connection
- Supports subtitle generation (JSON format with word-level timing)
- **Temporary File Handling**: By default, audio files are saved to the system's temporary directory (`/tmp/edge-tts-temp/` on Unix, `C:\Users\<user>\AppData\Local\Temp\edge-tts-temp\` on Windows) with unique filenames (e.g., `tts_1234567890_abc123.mp3`). Files are not automatically deleted - the calling application (Clawdbot) should handle cleanup after use. You can specify a custom output path with the `--output` option if permanent storage is needed.
- **TTS keyword filtering**: The skill automatically filters out TTS-related keywords (tts, TTS, text-to-speech) from text before conversion to avoid converting the trigger words themselves to audio
- For repeated preferences, use `config-manager.js` to set defaults
- **Default voice**: `en-US-MichelleNeural` (female, natural)
- Neural voices (ending in `Neural`) provide higher quality than Standard voices
