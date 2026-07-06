# Lyrics Writing Guide

This guide helps the AI produce higher-quality lyrics before calling the Tunee music generation API. It applies to song mode with vocals.

---

## 1. Structure

### Section Roles

| Section | Role | Line Count |
|---------|------|------------|
| **[Verse]** | Narrative, scene-setting, story progression | **Must be 2, 4, or 8 lines** (AI singing constraint — other counts cause missed syllables) |
| **[Pre-Chorus]** | Emotional build-up into chorus | 2–4 lines |
| **[Chorus]** | Core emotion, memorable hook, repeated | 4–8 lines |
| **[Bridge]** | Introduces a new emotional layer not yet expressed | 2–4 lines |
| **[Intro]** / **[Inst]** / **[Outro]** | Instrumental only — **must be included in the output as empty sections** (write the tag, leave the body blank) | — |

### Structure Templates by Style

| Style | Recommended Structure |
|-------|----------------------|
| Standard Pop | `[Intro] - [Verse 1] - [Pre-Chorus] - [Chorus] - [Inst] - [Verse 2] - [Pre-Chorus] - [Chorus] - [Bridge] - [Chorus] - [Outro]` |
| Ballad / Folk | `[Intro] - [Verse 1] - [Verse 2] - [Pre-Chorus] - [Chorus] - [Inst] - [Bridge] - [Chorus] - [Outro]` |
| High-intensity | `[Intro] - [Verse 1] - [Chorus] - [Verse 2] - [Chorus] - [Bridge] - [Chorus]` |
| Hip-hop / Rap | `[Intro] - [Verse 1] - [Hook] - [Verse 2] - [Hook] - [Verse 3] - [Hook]` |
| Rock | `[Intro] - [Verse 1] - [Chorus] - [Verse 2] - [Chorus] - [Solo] - [Bridge] - [Chorus]` |

### Bridge Rules
- Bridge appears **only once**, immediately before the **final Chorus**
- Forbidden combinations: `[Bridge] - [Outro]` / `[Verse] - [Bridge]` (without a Chorus in between) / Bridge appearing twice

### [Inst] Placement Rules
- **Must appear**: after the first Chorus (`[Chorus] - [Inst] - [Verse 2]`), or after Bridge before the final Chorus
- **Forbidden**: between two Verses
- **Forbidden**: after `[Intro]` and before the first `[Chorus]`

### [Intro] / [Inst] / [Outro] Output Format
These tags **must appear in the lyrics output** — do not omit them. Write the tag on its own line and leave the body empty:

```
[Intro]

[Verse 1]
...

[Chorus]
...

[Inst]

[Verse 2]
...
```

Never place any text after these tags. The blank line is intentional — it signals a pure instrumental section to the music model.

### Multiple Choruses
- Repeated Choruses must not be identical — adjust 1–2 lines in the second, and consider shifting perspective or tone in the third

### Length Guidelines

- **Short**: 80–150 words (approx. 1–2 minutes)
- **Standard**: 150–300 words (approx. 3–4 minutes)
- **Long**: 300–500 words (approx. 4–5 minutes)

---

## 2. Rhyme and Rhythm

### Rhyme Density by Section

| Section | Scheme | Notes |
|---------|--------|-------|
| Verse | Loose — ABCB | Lines 2 and 4 rhyme; narrative flow takes priority |
| Chorus | Tight — AAAA | Every line rhymes or near-rhymes; natural near-rhyme beats forced exact rhyme |
| Bridge | Free | Follow emotional need |

### Syllables and Meter

- 7–12 syllables per line works well for melody
- Keep adjacent lines similar in length for symmetric phrasing
- Avoid very long (>15 syllables) or very short (<4 syllables) lines

### Phrasing and Breath Breaks

Use spacing or line breaks to simulate natural singing breath points:

- **Inline space**: split a line at a natural pause — `遮丑的布 就别来戳破`
- **Line break**: split one idea across two lines for emphasis — isolate the final word for weight

Limit inline spaces to **2 per Verse section**; use line breaks mainly at emotional peaks.

---

## 3. Lyric Quality Rules

### Concreteness (Core Rule)

Never state emotions directly. Express them through specific objects, actions, and scenes:

| Instead of | Write |
|------------|-------|
| I miss you | The groceries you bought are still in the fridge |
| I'm lonely | I turned the key twice before remembering no one was waiting inside |
| I'm heartbroken | I deleted the chat then opened it again, reading that last goodnight |
| I regret it | I stood under your window — the light came on, then off — I never rang the bell |

### Colloquial Language

- Prefer everyday spoken language over literary phrasing
- Add rhetorical questions, natural hesitations, and conversational particles
- Avoid formal or poetic constructions unless the style requires it

### No Numbers

No numerals or number words anywhere in the lyrics — no exceptions.

- Forbidden: `三年零一个礼拜` / `凌晨三点` / `a thousand times` / `the first time we met`
- Replace with: specific sensory details or concrete scene description

### Forbidden Music Terms

Do not reference music itself inside the lyrics:

- Instruments: guitar, drums, piano, synth, bass…
- Rhythm/production: beat, groove, tempo, loop, drop, BPM…
- Abstract music words: melody, harmony, chord, note, rhythm…

### Overused / High-Alert Words

Avoid unless anchored to a specific, original image:

> 霓虹、钢筋、废墟、混凝土、夜空、星辰、梦境、回声、伤痛、烟花、剪影、寂静、执着、倔强、伤口、镜子、影子、枷锁、黑暗、玻璃、倒影、心碎、孤独、迷失、漂泊、星空、海洋

Also avoid clichéd pairings and empty constructs:
- Vague emotion words: 无助、彷徨、释怀、执念、思念
- Stock imagery: 风、雨、泪水、微笑、远方
- Empty similes: like a blooming flower / like a soaring bird / like flowing water
- Hollow declarations: forever love you / no matter how the world changes
- Formulaic opposites: 天/地、黑夜/白天、过去/未来

### Chorus Opening Lines

The first two lines of every Chorus are the song's most important lines — they must be singable, memorable, and land the emotion directly. Never open the Chorus with vague filler.

---

## 4. Style Adaptation

| Style | Lyric Characteristics |
|-------|----------------------|
| **Pop** | Conversational, direct emotion, repetitive chorus |
| **Folk** | Narrative, imagery, vivid scenes |
| **Hip-hop / Rap** | Strong rhythm, multi-syllable rhyme, slang OK; use `[Hook]` instead of `[Chorus]`, no `[Bridge]` |
| **Classical / Traditional** | Formal or semi-formal, classical imagery, parallelism |
| **Electronic / Ambient** | Short, repetitive, atmospheric |

---

## 5. Pre-Submission Checklist

Before submitting lyrics, verify every item:

- [ ] Every Verse is exactly 2, 4, or 8 lines
- [ ] No numbers (Arabic or written-out) anywhere in the lyrics
- [ ] No direct emotion words — all feelings expressed through scene or action
- [ ] No music terminology in the lyrics
- [ ] Overused alert words are avoided or grounded in a specific image
- [ ] `[Intro]` / `[Inst]` / `[Outro]` tags are present in the output (not omitted)
- [ ] `[Intro]` / `[Inst]` / `[Outro]` tag bodies are empty — no lyrics after the tag
- [ ] `[Inst]` is placed after a Chorus, not between two Verses or before the first Chorus
- [ ] Bridge appears only once, immediately before the final Chorus
- [ ] Verse 1 and Verse 2 provide different information / perspective (no repeated imagery)
- [ ] Chorus opening lines are specific and emotionally direct
- [ ] Rhyme scheme matches density guidelines (loose in Verse, tight in Chorus)
- [ ] Line length is 7–12 syllables
- [ ] Total length matches target duration
