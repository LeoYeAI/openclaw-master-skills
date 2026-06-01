# music-2.5 — Music Generation (MiniMax)

Full-song generation with vocals, lyrics structure control, and instrumental mode. Masters every genre with complete song structures, expressive melodies, and hi-fi audio.

## Supported parameters via PonyFlash SDK

```python
gen = pony_flash.music.generate(
    model="music-2.5",
    prompt="Soulful Blues, Rainy Night, Melancholy, Male Vocals, Slow Tempo",
    lyrics="[Verse]\nThe sky is cryin', Lord\nI can hear it on the roof\n\n[Chorus]\nMidnight rain, fallin' down on me\nLike tears I can't cry",
    duration=60,
)
```

## Prompt guidelines

The `prompt` parameter describes music style, mood, and scenario (0–2000 characters). Use comma-separated descriptors:

```
"Soulful Blues, Rainy Night, Melancholy, Male Vocals, Slow Tempo"
"Upbeat Pop, Summer Vibes, Female Vocals, 120 BPM"
"Lo-fi Hip Hop, Chill, Study Music, Mellow"
```

## Lyrics structure tags

14+ structure tags to control song arrangement:

| Tag | Purpose |
|---|---|
| `[Intro]` | Opening section |
| `[Verse]` | Verse section |
| `[Pre Chorus]` | Build-up before chorus |
| `[Chorus]` | Main hook |
| `[Hook]` | Catchy repeated phrase |
| `[Bridge]` | Contrasting section |
| `[Interlude]` | Instrumental break |
| `[Break]` | Pause/break |
| `[Transition]` | Section transition |
| `[Outro]` | Ending section |
| `[Post Chorus]` | After chorus section |
| `[Build Up]` | Energy build |
| `[Inst]` | Instrumental section |
| `[Solo]` | Solo section |

Lines within lyrics separated by `\n`. Max 3500 characters.

## Modes

| Mode | How to use |
|---|---|
| Vocal song | `prompt` + `lyrics` |
| Instrumental | `prompt` + `instrumental=True` |
| Auto-lyrics | `prompt` only (model generates lyrics from prompt) |
| Continue/extend | `prompt` + `reference_audio` + `continue_at` |

## Audio output settings

| Parameter | Supported values |
|---|---|
| `sample_rate` | 16000, 24000, 32000, 44100 |
| `format` | mp3, wav, pcm |

## Example: full song with structure

```python
gen = pony_flash.music.generate(
    model="music-2.5",
    prompt="Upbeat Pop, Summer Vibes, Female Vocals, 120 BPM",
    lyrics=(
        "[Intro]\n(Oh yeah, here we go)\n\n"
        "[Verse]\nSunshine on my face today\n"
        "Dancing through the light\n"
        "Every worry fades away\n"
        "Everything feels right\n\n"
        "[Chorus]\nThis is our summer song\n"
        "Singing all night long\n"
        "Turn the music up\n"
        "We'll never stop\n\n"
        "[Bridge]\nWhen the stars come out tonight\n"
        "We'll keep the fire burning bright\n\n"
        "[Outro]\n(Fade out...)"
    ),
    title="Summer Song",
    style="pop",
)
print(gen.url)
```

## Example: instrumental

```python
gen = pony_flash.music.generate(
    model="music-2.5",
    prompt="Cinematic Orchestral, Epic, Dramatic, Strings, Brass",
    instrumental=True,
    duration=90,
)
```

## Example: continue a song from timestamp

```python
gen = pony_flash.music.generate(
    model="music-2.5",
    prompt="Continue with an electric guitar solo, blues style",
    reference_audio=open("my_track.mp3", "rb"),
    continue_at=60.0,
)
```
