# Music Prompt Guide

This guide helps the AI write the `--prompt` argument for `generate.py`. The value is passed directly to the Tunee API as the `style` field, which controls the musical character of the generated track.

---

## Format

**Comma-separated English keywords only.** No sentences, no punctuation other than commas.

```
pop, female vocal, melancholic, acoustic guitar, slow, lo-fi
```

---

## Six Dimensions

Build the prompt by combining keywords across these dimensions. You do not need all six every time — 3 to 6 keywords is the typical effective range.

| Dimension | Role | Examples |
|-----------|------|---------|
| **Genre** | Core musical style | `pop`, `r&b`, `indie folk`, `hip-hop`, `jazz`, `rock`, `electronic`, `classical`, `bossa nova`, `k-pop` |
| **Mood / Atmosphere** | Emotional tone | `melancholic`, `uplifting`, `nostalgic`, `dark`, `romantic`, `tense`, `dreamy`, `bittersweet`, `hopeful`, `haunting` |
| **Vocal** | Voice character | `female vocal`, `male vocal`, `soft vocal`, `powerful vocal`, `falsetto`, `breathy`, `raspy`, `choir`, `no vocal` |
| **Tempo / Energy** | Speed and intensity | `slow`, `mid-tempo`, `uptempo`, `120bpm`, `driving`, `laid-back`, `intense`, `half-time` |
| **Instruments** | Featured sounds | `acoustic guitar`, `piano`, `strings`, `synth`, `bass`, `drums`, `cello`, `brass`, `pad`, `violin` |
| **Production Style** | Sound and texture | `lo-fi`, `cinematic`, `distorted`, `warm`, `ambient`, `minimal`, `lush`, `dry`, `reverb-heavy`, `vintage` |

---

## Keyword Selection Rules

**Always include Genre** — it anchors the entire generation. All other dimensions are optional but additive.

**Match mood to lyrics** — if lyrics were written first, the prompt mood should align with the emotional arc of the song, not contradict it.

**Vocals: explicit is better** — always specify `female vocal` or `male vocal` unless the user has not expressed a preference. Omitting vocal keywords leaves it to chance.

**Keep it focused** — 3 to 6 keywords produce the most coherent results. More than 8 keywords risk conflicting signals.

**No sentences or descriptive phrases** — `a sad song with piano` is wrong. `melancholic, piano, slow` is correct.

---

## Examples

### Pop ballad with lyrics (female, sad)
```
pop, female vocal, melancholic, piano, slow, cinematic
```

### Upbeat K-pop (no lyrics provided yet)
```
k-pop, female vocal, uplifting, uptempo, synth, bright
```

### Hip-hop instrumental
```
hip-hop, instrumental, dark, bass-heavy, lo-fi, mid-tempo
```

### Indie folk (male, nostalgic)
```
indie folk, male vocal, nostalgic, acoustic guitar, fingerpicking, warm
```

### Cinematic electronic
```
electronic, cinematic, ambient, synth pad, slow build, haunting
```

### R&B with attitude
```
r&b, female vocal, confident, uptempo, bass, distorted
```

---

## Style–Lyrics Consistency

When generating with lyrics, cross-check the prompt against the lyric content:

| Lyric tone | Avoid in prompt | Prefer in prompt |
|------------|----------------|-----------------|
| Loss / grief | `uplifting`, `bright`, `uptempo` | `melancholic`, `slow`, `bittersweet` |
| Joy / celebration | `dark`, `haunting`, `tense` | `uplifting`, `warm`, `driving` |
| Nostalgia | `distorted`, `intense` | `nostalgic`, `vintage`, `acoustic` |
| Tension / conflict | `dreamy`, `lush` | `tense`, `minimal`, `dry` |

---

## Reference: Common Keywords by Category

```
Genre:
  pop, indie pop, r&b, soul, hip-hop, rap, jazz, blues, rock, indie rock,
  metal, folk, indie folk, country, electronic, edm, ambient, classical,
  bossa nova, latin, k-pop, j-pop, reggae, gospel

Mood:
  melancholic, sad, bittersweet, nostalgic, longing, heartbroken,
  uplifting, joyful, hopeful, romantic, tender, warm,
  dark, haunting, tense, eerie, mysterious,
  confident, powerful, rebellious, energetic, euphoric, dreamy

Vocal:
  female vocal, male vocal, duet, choir,
  soft vocal, powerful vocal, breathy, raspy, falsetto, whisper

Tempo:
  slow, ballad tempo, mid-tempo, uptempo, driving, fast,
  laid-back, half-time, 80bpm, 100bpm, 120bpm, 140bpm

Instruments:
  piano, acoustic guitar, electric guitar, bass, drums, percussion,
  strings, violin, cello, brass, horns, flute,
  synth, pad, organ, keys, banjo, ukulele

Production:
  lo-fi, cinematic, ambient, minimal, sparse, lush, layered,
  warm, bright, dark, dry, reverb-heavy, distorted, vintage, modern
```
