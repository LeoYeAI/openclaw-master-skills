# Advanced Usage Examples

More examples beyond the basics in SKILL.md. For model-specific parameters and capabilities, see [reference/models/INDEX.md](../reference/models/INDEX.md).

## Image editing with reference images

```python
from pathlib import Path

gen = pony_flash.images.generate(
    model="nanobanana",
    prompt="Remove the background",
    images=[Path("photo.jpg")],
    mask=open("mask.png", "rb"),
)
print(gen.url)
```

## Multiple images

```python
gen = pony_flash.images.generate(
    model="nanobanana-pro",
    prompt="A cat in space",
    n=4,
    size="1K",
)
for url in gen.urls:
    print(url)
```

## Text-to-video (Veo 3.1)

```python
gen = pony_flash.video.generate(
    model="veo-3.1",
    prompt="Ocean waves crashing on a rocky coastline at sunset",
    size="1920x1080",
    duration=8,
)
print(gen.url)
```

## First-frame to video (local file)

```python
with open("my_photo.jpg", "rb") as f:
    gen = pony_flash.video.generate(
        model="seedance-1.5-pro",
        first_frame=f,
        prompt="Camera slowly zooms in",
    )
```

## First-frame to video (URL)

```python
gen = pony_flash.video.generate(
    model="seedance-1.5-pro",
    first_frame="https://example.com/photo.jpg",
    prompt="Camera slowly zooms in",
)
```

## OmniHuman — portrait + audio to talking video

```python
with open("portrait.jpg", "rb") as img, open("speech.wav", "rb") as audio:
    gen = pony_flash.video.generate(
        model="omnihuman-1.5",
        first_frame=img,
        audio=audio,
        size="1280x720",
    )
```

## Motion Transfer — person image + dance video

```python
with open("avatar.jpg", "rb") as img, open("dance.mp4", "rb") as vid:
    gen = pony_flash.video.generate(
        model="motion-transfer-1",
        first_frame=img,
        motion_video=vid,
        size="1280x720",
    )
```

## Speech with full voice control

```python
gen = pony_flash.speech.generate(
    model="speech-2.8-hd",
    input="Breaking news (gasps): AI can now compose music.",
    voice="English_Insightful_Speaker",
    language="English",
    speed=1.2,
    pitch=2,
    emotion="happy",
    voice_settings={
        "stability": 0.8,
        "similarity_boost": 0.9,
        "style": 0.5,
        "use_speaker_boost": True,
    },
    sample_rate=44100,
    format="mp3",
)
```

## Music with lyrics and structure tags

```python
gen = pony_flash.music.generate(
    model="music-2.5",
    prompt="Soulful Blues, Rainy Night, Melancholy, Male Vocals, Slow Tempo",
    lyrics="[Verse]\nWaves crash upon the shore\nWhispering forevermore\n\n[Chorus]\nOcean whispers call my name\nNothing here will be the same",
    title="Ocean Whispers",
    style="pop ballad",
    duration=60,
)
```

## Instrumental music

```python
gen = pony_flash.music.generate(
    model="music-2.5",
    prompt="Lo-fi hip hop study beats",
    instrumental=True,
    duration=120,
)
```

## Continue / extend a song

```python
gen = pony_flash.music.generate(
    model="music-2.5",
    prompt="Continue with a guitar solo",
    reference_audio=open("my_song.mp3", "rb"),
    continue_at=45.0,
)
```

## Get model details

```python
detail = pony_flash.models.get("nanobanana-pro")
print(detail.supported_sizes)
print(detail.supported_modes)
```

## Get recharge link

```python
resp = pony_flash.account.recharge(amount=100)
print(resp.recharge_url)
```
