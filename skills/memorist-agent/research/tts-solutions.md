# TTS Solutions Research for Memoirist Voice Notes

**Date:** 2026-03-11
**Use Case:** AI memoir interview agent sends warm, conversational voice replies to elderly narrators via WhatsApp
**Languages:** English + Chinese (Mandarin)
**Output:** .ogg or .mp3 (WhatsApp-compatible)
**Platform:** macOS Apple Silicon

---

## 1. Local / Offline TTS Options

### 1.1 macOS Built-in `say` Command

The `say` command ships with every Mac. It can output to file via `-o`.

**Chinese support:** Yes -- you must download Chinese Siri voices from System Settings > Accessibility > Spoken Content. Voices include Siri (Chinese) and several legacy voices.

**Output formats:** AIFF natively. No direct MP3/OGG -- requires piping through `ffmpeg`:
```bash
# English
say -v Samantha -o /tmp/out.aiff "Hello, how are you today?"
ffmpeg -i /tmp/out.aiff -codec:a libmp3lame -q:a 2 out.mp3

# Chinese (after downloading a Chinese voice)
say -v Tingting -o /tmp/out.aiff "你好，今天感觉怎么样？"
ffmpeg -i /tmp/out.aiff -codec:a libmp3lame -q:a 2 out_zh.mp3
```

**Quality:** English premium voices (Samantha, Zoe) score ~5/10. Chinese voices score ~4/10. The newer Siri voices are better but still noticeably synthetic. Default sample rate is 22 KHz, which is low for modern standards.

| Metric | Rating |
|---|---|
| Voice quality (EN) | 5/10 |
| Voice quality (ZH) | 4/10 |
| Latency | Instant (< 1s for 30s audio) |
| Cost | Free |
| Integration | CLI one-liner |
| Apple Silicon | Native |
| Output formats | AIFF (convert via ffmpeg) |

**Verdict:** Good for prototyping only. Not warm or natural enough for elderly narrators.

---

### 1.2 edge-tts (Microsoft Edge Online TTS)

Uses Microsoft Edge's neural TTS service. Despite being "online," it requires **no API key, no account, no cost** -- it uses the same free endpoint that the Edge browser uses. Technically not offline, but behaves like a free local tool.

**Install:**
```bash
pip install edge-tts
```

**Chinese Mandarin voices (neural, high-quality):**
- `zh-CN-XiaoxiaoNeural` -- female, warm, versatile (best default)
- `zh-CN-YunxiNeural` -- male, supports role adjustments
- `zh-CN-XiaoyiNeural` -- female, youthful
- `zh-CN-YunjianNeural` -- male, confident
- 20+ additional zh-CN voices

**English voices:**
- `en-US-JennyNeural` -- female, warm
- `en-US-GuyNeural` -- male, friendly
- 50+ additional en-US voices

**CLI usage:**
```bash
# English
edge-tts --voice en-US-JennyNeural --text "Hello, let's continue your story." --write-media out.mp3

# Chinese
edge-tts --voice zh-CN-XiaoxiaoNeural --text "你好，我们继续聊聊你的故事吧。" --write-media out.mp3

# With rate/pitch adjustment for warmth
edge-tts --voice zh-CN-XiaoxiaoNeural --rate=-5% --pitch=-2Hz --text "你好" --write-media warm.mp3

# From file input
edge-tts --voice zh-CN-XiaoxiaoNeural -f input.txt --write-media out.mp3

# List all voices
edge-tts --list-voices
```

**Python usage:**
```python
import edge_tts
import asyncio

async def generate():
    communicate = edge_tts.Communicate("你好，我们继续聊聊你的故事吧。", "zh-CN-XiaoxiaoNeural")
    await communicate.save("output.mp3")

asyncio.run(generate())
```

| Metric | Rating |
|---|---|
| Voice quality (EN) | 7.5/10 |
| Voice quality (ZH) | 8/10 (XiaoxiaoNeural is excellent) |
| Latency | 2-5s for 30s audio (network dependent) |
| Cost | **Free** (no API key) |
| Integration | `pip install edge-tts`, CLI or Python |
| Apple Silicon | Yes (pure Python) |
| Output formats | MP3 natively |

**Verdict:** Best free option. XiaoxiaoNeural is one of the best Chinese voices available anywhere. The catch is it requires internet (uses Microsoft's servers), so it's not truly offline. Microsoft could theoretically rate-limit or deprecate the endpoint.

---

### 1.3 Piper TTS

Fast, local neural TTS using ONNX models. Developed by the Rhasspy project (now moved to OHF-Voice/piper1-gpl).

**Install on Apple Silicon:**
```bash
# Via Homebrew (if available) or download binary
# Download aarch64 macOS build:
wget https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_macos_aarch64.tar.gz
tar xzf piper_macos_aarch64.tar.gz

# Or via pip (piper-tts wrapper)
pip install piper-tts
```

**Chinese support:** Limited. Piper supports 40+ languages, but Chinese (zh_CN) voice models are sparse and lower quality compared to European languages. The phonemizer has known issues with Chinese on some platforms.

**CLI usage:**
```bash
echo "Hello, how are you?" | piper --model en_US-lessac-medium --output_file out.wav
ffmpeg -i out.wav out.mp3
```

| Metric | Rating |
|---|---|
| Voice quality (EN) | 6.5/10 (medium models), 7/10 (high models) |
| Voice quality (ZH) | 4/10 (limited models available) |
| Latency | Very fast, < 1s for 30s audio |
| Cost | Free, fully offline |
| Integration | CLI binary or pip |
| Apple Silicon | Yes (aarch64 build available) |
| Output formats | WAV (convert via ffmpeg) |

**Verdict:** Excellent for English-only offline use. Poor Chinese support disqualifies it for this bilingual use case.

---

### 1.4 Coqui TTS / XTTS-v2

Open-source TTS with voice cloning. Coqui AI shut down in late 2024, but the community maintains the codebase. XTTS-v2 supports 17 languages including Chinese (zh-cn).

**Install:**
```bash
pip install coqui-tts
# or
pip install TTS
```

**Chinese support:** XTTS-v2 officially supports zh-cn. Quality is decent but not as natural as cloud services for Mandarin.

**Apple Silicon:** Not officially supported. MPS acceleration has known bugs. CPU inference works but is slow. XTTS-v2 is a large model (~1.5 GB) and runs slowly without GPU acceleration.

**CLI usage:**
```bash
tts --text "你好，今天怎么样？" --model_name tts_models/multilingual/multi-dataset/xtts_v2 --language_idx zh-cn --out_path out.wav
```

| Metric | Rating |
|---|---|
| Voice quality (EN) | 7/10 |
| Voice quality (ZH) | 5.5/10 |
| Latency | 15-30s for 30s audio (CPU on Mac) |
| Cost | Free, fully offline |
| Integration | pip install, CLI or Python |
| Apple Silicon | Unofficial, CPU-only practical |
| Output formats | WAV (convert via ffmpeg) |

**Verdict:** Voice cloning is interesting for the memoir use case, but slow inference on Mac and mediocre Chinese quality are deal-breakers. The project's uncertain future (company shut down) is a risk.

---

### 1.5 MLX-Audio (Kokoro + Qwen3-TTS on Apple Silicon)

**This is the most exciting local option.** MLX-Audio is a purpose-built TTS library for Apple Silicon using Apple's MLX framework. It runs natively on the Metal GPU and Neural Engine.

**Install:**
```bash
pip install mlx-audio
# For Mandarin Chinese support with Kokoro:
pip install misaki[zh]
```

#### 1.5a Kokoro (82M parameters)

Lightweight, fast, Apache-licensed. Supports Mandarin (language code 'z').

```bash
# CLI
mlx-audio tts --model kokoro --text "Hello, let's talk about your memories." --voice af_heart

# Python
from mlx_audio.tts import generate
generate(model="kokoro", text="你好", voice="zf_xiaobei", lang="z")
```

| Metric | Rating |
|---|---|
| Voice quality (EN) | 7/10 |
| Voice quality (ZH) | 5.5/10 (limited training data) |
| Latency | < 2s for 30s audio (M-series) |
| Cost | Free, fully offline |
| Apple Silicon | Native MLX optimization |

#### 1.5b Qwen3-TTS (by Alibaba, open-sourced Jan 2026)

**This is the standout local model for Chinese.** State-of-the-art multilingual TTS with voice cloning and emotion control. Chinese quality is its strongest language -- outstanding tone accuracy with Beijing and Sichuan dialect support.

**Install & run via MLX-Audio:**
```bash
pip install mlx-audio

# Generate Chinese speech
mlx-audio tts --model qwen3-tts --text "你好，我们来聊聊你小时候的故事吧。"

# Voice cloning from a reference audio
mlx-audio tts --model qwen3-tts --text "你好" --reference-audio grandma.wav

# Voice design (custom voice without reference audio)
mlx-audio tts --model qwen3-tts --text "Hello" --voice-design "A warm elderly female voice, gentle and caring"
```

**Available Chinese voices:** zf_xiaobei, zm_yunxi, and CustomVoice options (Vivian, Serena, Uncle_Fu, Dylan, Eric).

| Metric | Rating |
|---|---|
| Voice quality (EN) | 7.5/10 |
| Voice quality (ZH) | **9/10** (outstanding, best local option) |
| Latency | 3-8s for 30s audio (M-series, ~40% faster than PyTorch) |
| Cost | Free, fully offline |
| Integration | pip install mlx-audio |
| Apple Silicon | Native MLX, optimized for M1-M4 |
| Output formats | WAV (convert via ffmpeg) |
| Voice cloning | Yes, from short reference audio |
| Emotion control | Yes |

**Verdict:** Qwen3-TTS via MLX-Audio is the best local option for this use case. Outstanding Chinese quality, good English, voice cloning capability, and runs natively on Apple Silicon. The voice design feature ("warm elderly female voice") is perfect for creating appropriate voices for memoir narrators.

---

### 1.6 Bark (by Suno)

Generative audio model that can produce multilingual speech with non-verbal sounds (laughter, sighing).

**Install:**
```bash
pip install suno-bark
# Apple Silicon MPS support:
# Run with -enablemps flag
# Or use MLX port: https://github.com/j-csc/mlx_bark
```

**Chinese support:** Supported, but quality is below English. The model auto-detects language from input text.

| Metric | Rating |
|---|---|
| Voice quality (EN) | 7/10 (very natural with non-verbals) |
| Voice quality (ZH) | 5/10 (below English quality) |
| Latency | 30-60s for 30s audio (slow) |
| Cost | Free |
| Apple Silicon | MPS support, also MLX port available |
| Memory | 12 GB VRAM (full), 8 GB (small model) |

**Verdict:** Interesting for its expressiveness (laughs, pauses), but too slow for production use and weak Chinese. Not recommended.

---

### 1.7 OpenVoice (by MyShell)

Lightweight voice cloning system. Clones voice timbre from a short audio clip, then generates speech in multiple languages.

| Metric | Rating |
|---|---|
| Voice quality | 6/10 |
| Voice cloning | Good timbre matching |
| Chinese | Supported via cross-lingual cloning |
| Latency | Moderate |
| Cost | Free |

**Verdict:** Interesting for voice cloning but lower fidelity than Qwen3-TTS. Not the primary recommendation.

---

## 2. API-Based / Cloud TTS Options

### 2.1 OpenAI TTS (tts-1, tts-1-hd)

**Voices:** 6 voices (alloy, echo, fable, onyx, nova, shimmer). Limited selection but all are natural-sounding.

**Chinese support:** Supported. The model handles Chinese text, though voices are primarily English-native speakers producing Chinese -- acceptable but not native-level Mandarin.

**Pricing (as of March 2026):**
- tts-1 (standard): **$15 per 1M characters**
- tts-1-hd: **$30 per 1M characters**
- A 30-second voice note (~100 words / ~300 chars): ~$0.005 - $0.01

**CLI usage (via curl):**
```bash
curl https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "你好，我们继续聊聊你的故事吧。",
    "voice": "nova"
  }' --output out.mp3
```

**Python usage:**
```python
from openai import OpenAI
client = OpenAI()
response = client.audio.speech.create(
    model="tts-1-hd",
    voice="nova",
    input="你好，我们继续聊聊你的故事吧。"
)
response.stream_to_file("out.mp3")
```

| Metric | Rating |
|---|---|
| Voice quality (EN) | 8/10 |
| Voice quality (ZH) | 6.5/10 (acceptable, not native-level) |
| Latency | 1-3s for 30s audio |
| Cost | $15-30 / 1M chars |
| Integration | REST API, Python SDK |
| Output formats | MP3, OGG (Opus), FLAC, WAV |

**Verdict:** Easy to integrate if you already use OpenAI. Good English, passable Chinese. Limited voice selection (only 6). Supports OGG output natively which is ideal for WhatsApp.

---

### 2.2 ElevenLabs

Industry leader in natural-sounding TTS. Their Eleven v3 model is widely considered the best for English expressiveness.

**Chinese support:** Mandarin (cmn) supported in Eleven v3 and Turbo v2.5. Can adapt to regional Mandarin accents.

**Pricing (as of March 2026):**
- Free tier: 10,000 chars/month
- Starter: $5/month (30,000 chars)
- Creator: $22/month (100,000 chars)
- Scale: $330/month (2M chars)
- Enterprise: $1,320/month
- Pay-as-you-go on Scale+: ~$0.30 per 1,000 chars

**Python usage:**
```python
from elevenlabs import ElevenLabs
client = ElevenLabs(api_key="your-key")
audio = client.text_to_speech.convert(
    text="你好，我们继续聊聊你的故事吧。",
    voice_id="your-voice-id",
    model_id="eleven_multilingual_v2"
)
with open("out.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

| Metric | Rating |
|---|---|
| Voice quality (EN) | **9.5/10** (best in class) |
| Voice quality (ZH) | 7/10 (good but not native-quality tones) |
| Latency | 1-2s for 30s audio |
| Cost | $5-330/month (tiered) |
| Integration | REST API, Python/JS SDKs |
| Voice cloning | Yes (professional voice cloning) |
| Output formats | MP3, OGG |

**Verdict:** Best English quality available. Chinese is good but has a "subtle non-native quality on certain tone combinations" according to independent testing. Expensive at scale. Voice cloning could be powerful for memoir use -- clone a family member's voice for familiarity.

---

### 2.3 Fish Audio

**The dark horse -- especially strong for Chinese.** Founded by Chinese developers with deep Mandarin training data. Their Fish Speech model is also open source.

**Chinese quality:** Independently tested as **noticeably better than ElevenLabs for Mandarin**, particularly on tricky tone sequences (e.g., third-tone + fourth-tone). This is Fish Audio's key differentiator.

**Pricing (as of March 2026):**
- Free tier: 8,000 credits/month (~7 min of audio)
- Plus: $11/month (higher limits + commercial rights)
- Pro: $75/month (enterprise-scale)
- API: ~$15 per 1M UTF-8 bytes (~180,000 English words / ~12 hrs of speech)
- **45-70% cheaper than ElevenLabs**

**Voice cloning:** Included at no extra cost (same pricing tier as basic TTS).

**API usage:**
```python
import requests

response = requests.post(
    "https://api.fish.audio/v1/tts",
    headers={"Authorization": "Bearer YOUR_KEY"},
    json={
        "text": "你好，我们继续聊聊你的故事吧。",
        "reference_id": "your-voice-id"
    }
)
with open("output.mp3", "wb") as f:
    f.write(response.content)
```

| Metric | Rating |
|---|---|
| Voice quality (EN) | 8/10 |
| Voice quality (ZH) | **9/10** (best API option for Chinese) |
| Latency | 1-3s for 30s audio |
| Cost | ~$15/1M UTF-8 bytes (cheap) |
| Integration | REST API, Python SDK |
| Voice cloning | Yes, included |
| Output formats | MP3, WAV |

**Verdict:** Best Chinese Mandarin quality among API options. Significantly cheaper than ElevenLabs. Voice cloning included. Strong recommendation for this bilingual memoir use case.

---

### 2.4 Google Cloud TTS

Mature platform with WaveNet and Neural2 voices. 300+ voices across 50+ languages.

**Chinese support:** Strong. Multiple Mandarin voices (cmn-CN) with WaveNet quality. Also supports Cantonese.

**Pricing:**
- Standard voices: $4 per 1M characters
- WaveNet voices: $16 per 1M characters
- Neural2 voices: $16 per 1M characters
- Free tier: 1M standard chars/month, 500K WaveNet chars/month

**CLI usage:**
```bash
gcloud text-to-speech synthesize-speech \
  --text="你好" \
  --voice-name=cmn-CN-Wavenet-A \
  --audio-encoding=MP3 \
  --output=out.mp3
```

| Metric | Rating |
|---|---|
| Voice quality (EN) | 7.5/10 |
| Voice quality (ZH) | 7.5/10 (WaveNet is solid) |
| Latency | 1-2s |
| Cost | $4-16 / 1M chars |
| Integration | REST API, gcloud CLI, client libraries |
| Output formats | MP3, OGG_OPUS, WAV, MULAW |

**Verdict:** Reliable, well-documented, good Chinese. OGG_OPUS output is perfect for WhatsApp. But voices sound less "warm" than ElevenLabs or Fish Audio.

---

### 2.5 Azure Cognitive Services TTS

400+ voices across 140+ languages. Same underlying technology as edge-tts but with more control, SSML support, and SLA guarantees.

**Chinese support:** Excellent. XiaoxiaoNeural and YunxiNeural are among the best Chinese neural voices available. Supports emotion styles (cheerful, gentle, calm) via SSML.

**Pricing:**
- Free tier: 500K chars/month
- Neural voices: $16 per 1M characters
- Custom Neural Voice: $24 per 1M characters

**SSML with emotion (powerful for warm voices):**
```xml
<speak version="1.0" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <voice name="zh-CN-XiaoxiaoNeural">
    <mstts:express-as style="gentle" styledegree="1.5">
      你好，我们来聊聊你小时候的故事吧。
    </mstts:express-as>
  </voice>
</speak>
```

| Metric | Rating |
|---|---|
| Voice quality (EN) | 8/10 |
| Voice quality (ZH) | **8.5/10** (XiaoxiaoNeural with emotion styles) |
| Latency | 1-2s |
| Cost | $16 / 1M chars (neural) |
| Integration | REST API, SDKs, SSML |
| Output formats | MP3, OGG, WAV |
| Emotion control | Yes, via SSML express-as |

**Verdict:** Azure's SSML emotion styles ("gentle", "calm", "cheerful") are uniquely valuable for the memoir use case. XiaoxiaoNeural with `style="gentle"` is arguably the warmest Chinese voice available from any major cloud provider. The same voices are available free via edge-tts, but Azure adds emotion control and reliability guarantees.

---

### 2.6 MiniMax Speech-02

Chinese AI company. Ranked #1 on the Artificial Analysis Speech Arena for overall TTS quality.

**Chinese support:** Excellent. 300+ voices with strong Mandarin and Cantonese support.

**Pricing:**
- Speech-02-HD: ~$50 per 1M characters
- Speech-02-Turbo: cheaper, slightly lower quality
- Supports up to 5,000 chars real-time, 1M chars async

| Metric | Rating |
|---|---|
| Voice quality (EN) | 8.5/10 |
| Voice quality (ZH) | **9/10** |
| Latency | 1-3s (Turbo), 3-5s (HD) |
| Cost | ~$50 / 1M chars (HD) |
| Integration | REST API |
| Output formats | MP3, WAV |

**Verdict:** Top-tier quality but expensive. Best suited if budget is not a concern and maximum quality is needed.

---

### 2.7 ByteDance / Volcano Engine (Doubao TTS)

Powers TikTok/Douyin's voice features. Ultra-natural Chinese TTS with voice cloning.

**Chinese support:** Native -- this is a Chinese-first platform. Doubao Real-Time TTS predicts text emotion and tone automatically.

**Pricing:** Aggressively cheap (~10x cheaper than Western competitors for text models; TTS-specific pricing not publicly documented in English).

| Metric | Rating |
|---|---|
| Voice quality (EN) | 7/10 |
| Voice quality (ZH) | **9/10** |
| Latency | 1-2s |
| Cost | Very cheap (pricing in CNY, limited English docs) |
| Integration | REST API (primarily Chinese documentation) |

**Verdict:** Excellent Chinese quality and cheap pricing, but the platform is primarily documented in Chinese with Chinese payment methods (Alipay). Challenging for international developers.

---

## 3. Comparison Matrix

| Solution | EN Quality | ZH Quality | Latency (30s) | Cost | Offline | Apple Silicon | Chinese Voices |
|---|---|---|---|---|---|---|---|
| macOS `say` | 5/10 | 4/10 | <1s | Free | Yes | Native | Few, basic |
| **edge-tts** | 7.5/10 | **8/10** | 2-5s | **Free** | No* | Yes | 20+ neural |
| Piper TTS | 7/10 | 4/10 | <1s | Free | Yes | Yes | Very few |
| Coqui XTTS-v2 | 7/10 | 5.5/10 | 15-30s | Free | Yes | Partial | 1 model |
| **Qwen3-TTS (MLX)** | 7.5/10 | **9/10** | 3-8s | **Free** | **Yes** | **Native** | Multiple + cloning |
| Kokoro (MLX) | 7/10 | 5.5/10 | <2s | Free | Yes | Native | Few |
| Bark | 7/10 | 5/10 | 30-60s | Free | Yes | MPS | Auto-detect |
| OpenAI TTS | 8/10 | 6.5/10 | 1-3s | $15-30/1M | No | N/A | 6 voices |
| **ElevenLabs** | **9.5/10** | 7/10 | 1-2s | $5-330/mo | No | N/A | Multi |
| **Fish Audio** | 8/10 | **9/10** | 1-3s | ~$15/1M | No | N/A | Multi + cloning |
| Google Cloud | 7.5/10 | 7.5/10 | 1-2s | $4-16/1M | No | N/A | WaveNet |
| **Azure TTS** | 8/10 | **8.5/10** | 1-2s | $16/1M | No | N/A | Emotion styles |
| MiniMax | 8.5/10 | **9/10** | 1-5s | ~$50/1M | No | N/A | 300+ |
| ByteDance | 7/10 | **9/10** | 1-2s | Cheap | No | N/A | Native CN |

*edge-tts uses Microsoft's servers but requires no API key or account.

---

## 4. Top Recommendations

### Best Local Option (Privacy-First): Qwen3-TTS via MLX-Audio

**Why:** Outstanding Chinese quality (9/10), good English, voice cloning, emotion control, and runs natively on Apple Silicon with MLX optimization. Fully offline, free, open-source (Alibaba, open-sourced Jan 2026).

```bash
pip install mlx-audio
mlx-audio tts --model qwen3-tts --text "你好，我们来聊聊你小时候的故事吧。"
# Convert to mp3 for WhatsApp
ffmpeg -i output.wav -codec:a libmp3lame -q:a 2 output.mp3
# Or convert to ogg opus
ffmpeg -i output.wav -codec:a libopus output.ogg
```

**Memory requirement:** Needs ~8-16 GB RAM depending on model size. All M1/M2/M3/M4 Macs with 16+ GB are suitable.

---

### Best API Option (Quality-First): Fish Audio

**Why:** Best Chinese Mandarin quality among API options (tested better than ElevenLabs on Mandarin tones). Good English. Voice cloning included at no extra cost. 45-70% cheaper than ElevenLabs. If English quality is the absolute priority over Chinese, use ElevenLabs instead.

For this specific use case (elderly Chinese narrators), Fish Audio wins because:
- Native Mandarin training data produces the most natural Chinese tones
- Voice cloning could replicate a familiar voice
- Affordable at scale

---

### Best Budget Option (Free): edge-tts

**Why:** Completely free, no API key needed, excellent Chinese voices (XiaoxiaoNeural is 8/10), outputs MP3 directly. The only caveat is it requires internet.

```bash
pip install edge-tts

# Quick one-liner for Chinese voice note
edge-tts --voice zh-CN-XiaoxiaoNeural --text "你好，我们继续聊聊吧。" --write-media note.mp3

# Quick one-liner for English voice note
edge-tts --voice en-US-JennyNeural --text "Hello, shall we continue your story?" --write-media note.mp3
```

If you need truly offline + free: Qwen3-TTS via MLX-Audio (see above).

---

### Best Chinese Voice Quality: Fish Audio (API) / Qwen3-TTS (Local)

**API:** Fish Audio -- independently verified as producing the most natural Mandarin, particularly on difficult tone sequences. ~$15/1M UTF-8 bytes.

**Local:** Qwen3-TTS via MLX-Audio -- Alibaba's model is strongest in Chinese by design. Free, offline, runs natively on Apple Silicon.

**Free cloud-like:** edge-tts with `zh-CN-XiaoxiaoNeural` -- Microsoft's Chinese neural voices are surprisingly excellent and cost nothing.

---

## 5. Recommended Architecture for Memoirist

For the memoir interview agent, a **tiered approach** works best:

```
Priority 1 (Default):  edge-tts (free, fast, good quality, Chinese + English)
Priority 2 (Offline):  Qwen3-TTS via MLX-Audio (when offline or privacy needed)
Priority 3 (Premium):  Fish Audio API (when maximum Chinese quality needed)
```

**Audio pipeline for WhatsApp:**
```bash
# Generate audio (any TTS tool)
edge-tts --voice zh-CN-XiaoxiaoNeural --text "$TEXT" --write-media /tmp/voice.mp3

# Convert to OGG Opus for WhatsApp voice note format
ffmpeg -i /tmp/voice.mp3 -codec:a libopus -b:a 64k /tmp/voice.ogg

# Or keep as MP3 (WhatsApp also accepts MP3 as audio message)
```

**Key consideration for elderly narrators:** Warm, slightly slower speech is preferable. Both edge-tts (with `--rate=-10%`) and Azure TTS (with SSML `style="gentle"`) can achieve this. Qwen3-TTS voice design can create a custom "warm elderly" voice persona.

---

## Sources

- [Piper TTS on macOS](https://www.thoughtasylum.com/2025/08/25/text-to-speech-on-macos-with-piper/)
- [Piper GitHub](https://github.com/rhasspy/piper)
- [edge-tts PyPI](https://pypi.org/project/edge-tts/)
- [edge-tts GitHub](https://github.com/rany2/edge-tts)
- [OpenAI TTS Pricing](https://costgoat.com/pricing/openai-tts)
- [OpenAI TTS-1-HD Model](https://developers.openai.com/api/docs/models/tts-1-hd)
- [ElevenLabs Mandarin Chinese TTS](https://elevenlabs.io/text-to-speech/mandarin-chinese)
- [ElevenLabs Pricing](https://flexprice.io/blog/elevenlabs-pricing-breakdown)
- [Fish Audio TTS Comparison](https://fish.audio/blog/text-to-speech-api-comparison-pricing-features/)
- [Fish Audio Pricing](https://fish.audio/blog/cheapest-text-to-speech-api-developers/)
- [MLX-Audio GitHub](https://github.com/Blaizzy/mlx-audio)
- [MLX-Audio PyPI](https://pypi.org/project/mlx-audio/)
- [Qwen3-TTS Apple Silicon](https://github.com/kapi2800/qwen3-tts-apple-silicon)
- [Qwen3-TTS MLX-Audio Guide](https://mybyways.com/blog/qwen3-tts-with-mlx-audio-on-macos)
- [Qwen3-TTS Complete Guide](https://dev.to/czmilo/qwen3-tts-the-complete-2026-guide-to-open-source-voice-cloning-and-ai-speech-generation-1in6)
- [Kokoro-82M on HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M)
- [Kokoro PyPI](https://pypi.org/project/kokoro/)
- [Bark GitHub](https://github.com/suno-ai/bark)
- [Coqui TTS Review](https://qcall.ai/coqui-tts-review)
- [Google Cloud TTS Pricing](https://cloud.google.com/text-to-speech/pricing)
- [Azure Chinese Voice Enhancement](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-neural-tts-enhanced-expressiveness-for-chinese-voices-with-upgraded-pro/3858411)
- [MiniMax TTS Analysis](https://artificialanalysis.ai/text-to-speech/model-families/minimax-hailuo)
- [Best TTS APIs 2026 Comparison](https://www.speechmatics.com/company/articles-and-news/best-tts-apis-in-2025-top-12-text-to-speech-services-for-developers)
- [macOS say command reference](https://ss64.com/mac/say.html)
