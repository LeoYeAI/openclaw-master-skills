# Troubleshooting

Common issues and solutions.

## Contents

- [Environment issues](#environment-issues)
- [API errors](#api-errors)
- [Segment-based TTS issues](#segment-based-tts-issues)
- [Audio issues](#audio-issues)
- [Voice issues](#voice-issues)

---

## Environment issues

### MINIMAX_VOICE_API_KEY not set

**Error**: `ValueError: MINIMAX_VOICE_API_KEY is required`

**Solution**:
```bash
export MINIMAX_VOICE_API_KEY="your-api-key"

# Verify
echo $MINIMAX_VOICE_API_KEY
```

**Or in Python**:
```python
import os
os.environ["MINIMAX_VOICE_API_KEY"] = "your-key"
```

### FFmpeg not found

**Error**: `RuntimeError: FFmpeg not installed`

**Solution**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Verify
ffmpeg -version
```

**Check in Python**:
```python
from scripts import check_ffmpeg_installed

if not check_ffmpeg_installed():
    print("Install FFmpeg")
else:
    print("FFmpeg OK")
```

### Import errors

**Error**: `ModuleNotFoundError: No module named 'websockets'`

**Solution**:
```bash
pip install -r requirements.txt
```

---

## API errors

### Authentication failure

**Error**: `401 Unauthorized`

**Solution**:
- Verify API key is correct
- Check key hasn't expired
- Ensure no extra spaces in key

```python
import os
key = os.getenv("MINIMAX_VOICE_API_KEY")
print(f"Key: {key[:10]}..." if key else "Not set")
```

### Rate limiting

**Error**: `429 Too Many Requests`

**Solution**:
- Add delays between requests
- Use async TTS for batch processing
- Check your plan limits

```python
import time

for text in texts:
    result = synthesize_speech_http(text=text)
    time.sleep(1)  # Delay 1s between requests
```

### Timeout

**Error**: `TimeoutError` or request timeout

**Solution**:
- Use async TTS for long text
- Check network connection
- Increase request timeout in code if needed

---

## Segment-based TTS issues

### Invalid JSON format

**Error**: `Invalid JSON format: Expecting ',' delimiter`

**Solution**: Check segments.json syntax:
```bash
python -c "import json; json.load(open('segments.json'))"
```

Common issues:
- Missing commas between segments
- Trailing comma after last segment
- Unescaped quotes in text

### Missing required field

**Error**: `Segment 0: missing required 'text' field`

**Solution**: Each segment must have `text` and `voice_id`:
```json
{
  "text": "Your text here",
  "voice_id": "male-qn-qingse",
  "emotion": "calm"
}
```

### Invalid emotion value

**Error**: `Segment 0: invalid emotion 'excited'. Valid options: happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper`

**Solution**: Use only valid emotion values:
```python
VALID_EMOTIONS = ["happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm", "fluent", "whisper"]
```

**Note**: 
- `fluent` and `whisper` only work with speech-2.6-hd/turbo models
- speech-2.8-hd/turbo models automatically match emotions (recommended: don't manually specify)

### Empty text

**Error**: `Segment 1: 'text' cannot be empty`

**Solution**: Ensure all text fields contain content:
```json
{"text": "Some content", "voice_id": "...", "emotion": "..."}
```

### Segment generation failed

**Error**: `Audio generation failed for 2/10 segments`

**Causes and solutions**:
1. **API error**: Check API key and network
2. **Invalid voice_id**: Verify voice exists with `python mmvoice.py list-voices`
3. **Text too long**: Split into smaller segments (max 10,000 chars each)

Use `--continue-on-error` to generate remaining segments:
```bash
python mmvoice.py generate segments.json -o output.mp3 --continue-on-error
```

### Merge failed after generation

**Error**: `Audio merge failed: FFmpeg filter_complex error`

**Solutions**:
1. Check FFmpeg installation: `ffmpeg -version`
2. Use `crossfade_ms=0` for simpler merging:
   ```bash
   python mmvoice.py generate segments.json -o output.mp3 --crossfade 0
   ```
3. The script automatically uses fallback merging if filter_complex fails

---

## Audio issues

### Audio quality poor

**Check audio info**:
```python
from scripts import probe_audio_file

info = probe_audio_file("output.mp3")
print(f"Sample rate: {info.sample_rate}")
print(f"Bitrate: {info.bitrate}")
```

**Solution**: Re-generate with higher quality
```python
from scripts import VoiceSetting, AudioSetting, synthesize_speech_http

audio = AudioSetting(
    sample_rate=32000,  # Higher
    bitrate=192000,     # Higher
    format="mp3",
)

result = synthesize_speech_http(text="...", audio_setting=audio)
```

### Merge failed

**Error**: `RuntimeError: FFmpeg command failed`

**Solution**:
- Ensure all input files exist
- Check formats are compatible
- Verify FFmpeg is installed

```python
import os
files = ["a.mp3", "b.mp3"]
for f in files:
    if not os.path.exists(f):
        print(f"Missing: {f}")
```

### Volume inconsistent

**Solution**: Normalize after merging
```python
from scripts import merge_audio_files

merge_audio_files(
    input_files=["a.mp3", "b.mp3"],
    output_path="merged.mp3",
    normalize=True,  # Enable normalization
)
```

---

## Voice issues

### Voice not found

**Error**: Voice ID not recognized

**Solution**: List available voices
```python
from scripts import get_system_voices, get_all_custom_voices, SYSTEM_VOICES

# Check system voices
print("System voices:", SYSTEM_VOICES)

# List all available
get_system_voices()  # Preset voices
get_all_custom_voices()  # Your custom voices
```

### Cloned voice expired

**Issue**: Voice deleted after 7 days

**Solution**: Use voice with TTS within 7 days to save permanently
```python
from scripts import quick_tts

# Using the voice saves it permanently
quick_tts(
    text="Test to save voice",
    voice_id="my-cloned-voice",
    output_path="test.mp3"
)
```

### Clone failed

**Error**: Audio duration or file size issue

**Check requirements**:
- Duration: 10s–5min
- File size: ≤20MB
- Format: mp3, wav, m4a

**Solution**: Trim or convert source audio
```python
from scripts import trim_audio, convert_audio

# Trim to required length
trim_audio("long.wav", "trimmed.wav", start_time=0, end_time=60)

# Convert format
convert_audio("audio.m4a", "audio.mp3")
```

---

## Debug mode

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now run your code
from scripts import quick_tts
quick_tts("Test", "male-qn-qingse", "test.mp3")
```

## Getting help

1. Check [api_documentation.md](api_documentation.md) for full API reference
2. Review workflow guides: [tts-guide.md](tts-guide.md), [cli-guide.md](cli-guide.md)
3. Test with minimal examples from [script-examples.md](script-examples.md)
4. Verify environment with [getting-started.md](getting-started.md#quick-test)

## Common error patterns

| Error | Likely cause | Solution |
|-------|--------------|----------|
| `MINIMAX_VOICE_API_KEY is required` | Key not set | `export MINIMAX_VOICE_API_KEY="key"` |
| `FFmpeg not installed` | FFmpeg missing | `brew install ffmpeg` |
| `Voice not found` | Invalid voice ID | Check with `get_system_voices()` |
| `File not found` | Missing input file | Verify file paths |
| `401 Unauthorized` | Invalid API key | Check key validity |
| `429 Too Many Requests` | Rate limit | Add delays |
| `brotli: decoder process called...` | Brotli decode error | Fixed in latest version (Accept-Encoding header) |
| `unexpected keyword argument 'vol'` | Wrong param name | Use `volume` not `vol` |
| `invalid params, method t2a-v2 not have model` | Wrong model name | Use `speech-2.6-hd` not `speech_01` (hyphens, not underscores) |
| `Audio merging failed...crossfade_ms` | Filter_complex failed | Set `crossfade_ms=0` to enable fallback |

---

## Specific error fixes

### Brotli decode error

**Error**: `Received response with content-encoding: br, but failed to decode it`

**Cause**: Server returned brotli-compressed response, client failed to decode.

**Solution**: Fixed in latest version. If still occurring, ensure you're using the latest `scripts/utils.py` which sets `Accept-Encoding: gzip, deflate` header.

### VoiceSetting parameter error

**Error**: `TypeError: VoiceSetting.__init__() got an unexpected keyword argument 'vol'`

**Cause**: The parameter is named `volume`, not `vol`.

**Solution**:

```python
# Correct usage
voice = VoiceSetting(voice_id="female-shaonv", volume=1.5)
```

### Invalid model name

**Error**: `ValueError: API Error [2013]: invalid params, method t2a-v2 not have model: speech_01`

**Cause**: Model names use hyphens (-) and require a suffix (-hd or -turbo).

**Valid model names**:
- `speech-2.6-hd` (recommended)
- `speech-2.6-turbo`
- `speech-02-hd`
- `speech-02-turbo`
- `speech-01-hd`
- `speech-01-turbo`

**Wrong**: `speech_01`, `speech_2.6`, `speech-01`

### Audio merging with crossfade failed

**Error**: `Audio merging failed (filter_complex path). Crossfade is enabled...`

**Cause**: FFmpeg filter_complex failed, but crossfade prevents fallback to concat demuxer.

**Solutions**:
1. Set `crossfade_ms=0` to enable fallback:
   ```python
   merge_audio_files(files, output, crossfade_ms=0)
   ```
2. Or use `concatenate_audio_files()` for same-format inputs:
   ```python
   concatenate_audio_files(files, output)
   ```
