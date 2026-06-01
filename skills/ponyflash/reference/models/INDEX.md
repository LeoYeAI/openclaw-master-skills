# Available Models

All models accessible via `pony_flash.models.list()` and `pony_flash.models.get(model_id)`.

## Quick Reference

| Model | Type | Pricing | Doc |
|---|---|---|---|
| `nano-banana-pro` | image | 7/10/15 credits (1K/2K/4K) | [nano-banana-pro.md](nano-banana-pro.md) |
| `nano-banana-2` | image | 7/10/15 credits (1K/2K/4K) | [nano-banana-2.md](nano-banana-2.md) |
| `seedream-5-lite` | image | 4 credits/image | [seedream-5-lite.md](seedream-5-lite.md) |
| `image-pro-1` | image | 20 credits/request | *(placeholder, not yet connected)* |
| `seedance-1.5-pro` | video | 1-12 c/s (by resolution+audio) | [seedance-1.5-pro.md](seedance-1.5-pro.md) |
| `veo-3.1` | video | 20-40 c/s (by audio) | [veo-3.1.md](veo-3.1.md) |
| `veo-3.1-fast` | video | 10-15 c/s (by audio) | [veo-3.1-fast.md](veo-3.1-fast.md) |
| `omnihuman-1.5` | video | 16 credits/second | *(see SKILL.md for usage)* |
| `speech-2.8-hd` | speech | 1 credit/request | [speech-2.8-hd.md](speech-2.8-hd.md) |
| `speech-2.8-turbo` | speech | 1 credit/request | [speech-2.8-turbo.md](speech-2.8-turbo.md) |

---

## Image Models

### nano-banana-pro

Google DeepMind's highest-quality image generation model (Gemini 3 Pro). Accurate text rendering, multi-image blending (up to 14 refs), professional creative controls.

| Field | Values |
|---|---|
| **resolution** | `1K`, `2K` (default), `4K` |
| **aspect_ratio** | `match_input_image`, `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| **output_format** | `jpg` (default), `png` |
| **reference_images** | Up to 14 images (FileInput[]) |
| **Pricing** | 1K = 7 credits, 2K = 10 credits, 4K = 15 credits |

```python
gen = pony_flash.images.generate(
    model="nano-banana-pro",
    prompt="A minimalist logo for a coffee shop",
    resolution="2K",
    aspect_ratio="1:1",
)
```

Extra parameters via `**extra_body`: `safety_filter_level` (`block_low_and_above` / `block_medium_and_above` / `block_only_high`)

---

### nano-banana-2

Google's fast image model (Gemini 3.1 Flash). Same quality as Pro with faster generation. Supports Google Search grounding for real-time info in images.

| Field | Values |
|---|---|
| **resolution** | `1K` (default), `2K`, `4K` |
| **aspect_ratio** | `match_input_image`, `1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9` |
| **output_format** | `jpg` (default), `png` |
| **reference_images** | Up to 14 images (FileInput[]) |
| **Pricing** | 1K = 7 credits, 2K = 10 credits, 4K = 15 credits |

```python
gen = pony_flash.images.generate(
    model="nano-banana-2",
    prompt="Current weather forecast for Tokyo as an infographic",
    resolution="2K",
    aspect_ratio="9:16",
)
```

Extra parameters via `**extra_body`: `google_search` (bool, default true), `image_search` (bool, default true)

---

### seedream-5-lite

ByteDance's image model with built-in reasoning, example-based editing, and batch generation. Lowest cost per image.

| Field | Values |
|---|---|
| **resolution** | `2K` (default), `3K` |
| **aspect_ratio** | `match_input_image`, `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `9:16`, `16:9`, `21:9` |
| **output_format** | `png` (default), `jpg` |
| **reference_images** | Up to 14 images (FileInput[]) |
| **n** | 1-15, number of images to generate (maps to `max_images`) |
| **Pricing** | 4 credits/image (all resolutions) |

```python
gen = pony_flash.images.generate(
    model="seedream-5-lite",
    prompt="A photorealistic interior rendering from this floor plan sketch",
    reference_images=[open("floor_plan.jpg", "rb")],
    resolution="3K",
    aspect_ratio="16:9",
)
```

Extra parameters via `**extra_body`: `sequential_image_generation` (`disabled` (default) / `auto`)

---

## Video Models

### seedance-1.5-pro

ByteDance's cinema-quality video model. Synchronized audio+video, lip-sync, multilingual.

| Field | Values |
|---|---|
| **duration** | 2-12 (any integer) |
| **resolution** | `480p`, `720p` (default), `1080p` |
| **aspect_ratio** | `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9`, `9:21` |
| **generate_audio** | bool (default false) |
| **first_frame** | Starting image (FileInput) |
| **last_frame** | Ending image (FileInput) |
| **Pricing** | 480p: 3/1 c/s, 720p: 5/3 c/s, 1080p: 12/6 c/s (audio/silent) |

Extra via `**extra_body`: `camera_fixed` (bool)

### veo-3.1

Google's SOTA video model. Synchronized audio, reference images, first/last frame, 720p/1080p.

| Field | Values |
|---|---|
| **duration** | `4`, `6`, `8` |
| **resolution** | `720p`, `1080p` (default) |
| **aspect_ratio** | `16:9` (default), `9:16` |
| **generate_audio** | bool (default true) |
| **first_frame** | Starting image (FileInput) |
| **last_frame** | Ending image (FileInput) |
| **reference_images** | Up to 3 images (FileInput[]) |
| **negative_prompt** | What to exclude |
| **Pricing** | with_audio: 40 c/s, without: 20 c/s |

Extra via `**extra_body`: `seed` (int)

### veo-3.1-fast

Faster Veo 3.1. Same params, lower cost. Best for iteration.

| Field | Values |
|---|---|
| Same as veo-3.1 | All params identical |
| **Pricing** | with_audio: 15 c/s, without: 10 c/s |

### omnihuman-1.5

ByteDance OmniHuman. Portrait image + audio to talking-head video with lip-sync.

| Field | Values |
|---|---|
| **first_frame** | Human portrait image (required, FileInput) |
| **audio** | Speech/music audio, max 35s (required, FileInput) |
| **prompt** | Scene/action description (optional) |
| **Pricing** | 16 credits/second (duration = audio length) |

Extra parameters via `**extra_body`: `seed` (int), `fast_mode` (bool)

---

## Speech Models

### speech-2.8-hd

MiniMax Speech 2.8 HD. Ranked #1 on TTS benchmarks. Studio-grade quality, 330+ voices, 40+ languages, interjection tags, emotion control.

| Field | Values |
|---|---|
| **input** | Text to synthesize, max 10000 chars |
| **voice** | Voice ID (required). See voice list below |
| **emotion** | `auto` (default), `happy`, `calm`, `sad`, `angry`, `fearful`, `disgusted`, `surprised` |
| **speed** | `0.5` - `2.0` (default `1.0`) |
| **pitch** | `-12` to `+12` semitones (default `0`) |
| **format** | `mp3` (default), `wav`, `flac`, `pcm` |
| **sample_rate** | `8000`, `16000`, `22050`, `24000`, `32000` (default), `44100` |
| **language** | Language hint or `auto`. See language list below |
| **Pricing** | 1 credit/request (provisional) |

```python
gen = pony_flash.speech.generate(
    model="speech-2.8-hd",
    input="Hello (laughs), welcome to PonyFlash!",
    voice="English_Graceful_Lady",
    emotion="happy",
)
```

Extra parameters via `**extra_body`: `volume` (0-10), `bitrate` (int), `channel` (`mono`/`stereo`), `english_normalization` (bool)

#### Preset Voices (17)

`Wise_Woman`, `Friendly_Person`, `Inspirational_girl`, `Deep_Voice_Man`, `Calm_Woman`, `Casual_Guy`, `Lively_Girl`, `Patient_Man`, `Young_Knight`, `Determined_Man`, `Lovely_Girl`, `Decent_Boy`, `Imposing_Manner`, `Elegant_Man`, `Abbess`, `Sweet_Girl_2`, `Exuberant_Girl`

#### Extended Voice IDs (330+)

Also accepts MiniMax official voice IDs by language prefix:

| Language | Example Voice IDs |
|---|---|
| English (45) | `English_Graceful_Lady`, `English_radiant_girl`, `English_magnetic_voiced_man`, `English_Trustworth_Man`, `English_CalmWoman`, `English_PlayfulGirl`, `English_ManWithDeepVoice` |
| Chinese (34) | `Chinese (Mandarin)_Sweet_Lady`, `Chinese (Mandarin)_Gentleman`, `Chinese (Mandarin)_Radio_Host`, `Chinese (Mandarin)_Lyrical_Voice` |
| Japanese (15) | `Japanese_GentleButler`, `Japanese_KindLady`, `Japanese_CalmLady`, `Japanese_GracefulMaiden` |
| Korean (38) | `Korean_CalmGentleman`, `Korean_SweetGirl`, `Korean_CheerfulBoyfriend` |
| Spanish (39) | `Spanish_SereneWoman`, `Spanish_CaptivatingStoryteller`, `Spanish_Narrator` |
| Portuguese (72) | `Portuguese_SentimentalLady`, `Portuguese_Narrator`, `Portuguese_Comedian` |
| French (6) | `French_CasualMan`, `French_MovieLeadFemale`, `French_FemaleAnchor` |
| Others | Indonesian (9), German (3), Russian (8), Italian (4), Dutch (2), Arabic (2), Turkish (2), Ukrainian (2), Thai (4), Polish (4), Romanian (4), Greek (3), Czech (3), Finnish (3), Hindi (2) |

Custom cloned voice IDs (from MiniMax Voice Clone) are also accepted.

#### Supported Languages (40+)

`auto`, Chinese, English, Arabic, Russian, Spanish, French, Portuguese, German, Turkish, Dutch, Ukrainian, Vietnamese, Indonesian, Japanese, Italian, Korean, Thai, Polish, Romanian, Greek, Czech, Finnish, Hindi, Bulgarian, Danish, Hebrew, Malay, Persian, Slovak, Swedish, Croatian, Filipino, Hungarian, Norwegian, Slovenian, Catalan, Nynorsk, Tamil, Afrikaans

#### Interjection Tags

Place inline in text: `(laughs)`, `(chuckle)`, `(coughs)`, `(clear-throat)`, `(groans)`, `(breath)`, `(pant)`, `(inhale)`, `(exhale)`, `(gasps)`, `(sniffs)`, `(sighs)`, `(snorts)`, `(burps)`, `(lip-smacking)`, `(humming)`, `(hissing)`, `(emm)`, `(sneezes)`

#### Pause Control

Insert `<#x#>` for custom pauses (x = 0.01-99.99 seconds): `"First sentence.<#2.5#>Second sentence."`

---

### speech-2.8-turbo

MiniMax Speech 2.8 Turbo. Same parameters as HD, faster generation, slightly lower quality.

| Field | Values |
|---|---|
| Same as speech-2.8-hd | All parameters identical |
| **Pricing** | 1 credit/request (provisional) |

```python
gen = pony_flash.speech.generate(
    model="speech-2.8-turbo",
    input="Quick draft narration for review",
    voice="Casual_Guy",
)
```

---

## API Usage

```python
# List all models
page = pony_flash.models.list()
for m in page.items:
    print(f"{m.id} ({m.type})")

# Filter by type
images = pony_flash.models.list(type="image")

# Get model details
detail = pony_flash.models.get("nano-banana-pro")
print(detail.supported_resolutions)
print(detail.supported_aspect_ratios)
print(detail.pricing)
```
