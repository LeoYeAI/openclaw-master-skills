---
name: skywork-music-maker
description: AI song and music generator — create songs with vocals, instrumentals, beats, and lyrics from a text description in any language. Generate lo-fi beats, pop songs, orchestral scores, K-POP, reggaetón, guofeng, and more. Supports vocal cloning, reference track style transfer, lyric writing, and full music production workflows. Just say "make me a chill lo-fi beat" or describe any musical idea and this skill handles the rest.
metadata:
  openclaw:
    requires:
      env:
        - MUREKA_API_KEY
      bins:
        - python3
    install:
      - kind: uv
        package: requests
    primaryEnv: MUREKA_API_KEY
    homepage: https://clawhub.ai/gxcun17/skywork-music-maker
---

# Skywork Music Maker (Mureka API)

Generate professional-quality music using the Mureka API at https://api.mureka.ai. This skill covers the complete music production workflow: lyrics writing → song/instrumental generation.

## 多语言简介 | Multilingual Overview

### 中文简介
Skywork Music Maker 是基于 Mureka AI API 的专业音乐创作工具。支持从自然语言描述生成歌曲、纯音乐和歌词，覆盖完整的音乐制作流程。支持中文输入，可根据中文描述自动生成英文提示词。适用于流行音乐、国风音乐、电子音乐等多种风格。主要功能包括：AI 作词、歌曲生成（含人声）、纯音乐生成、人声克隆、参考音频风格迁移。

### 日本語の概要
Skywork Music Maker は Mureka AI API を使用したプロフェッショナルな音楽制作ツールです。自然言語の説明から楽曲・インストゥルメンタル・歌詞を生成でき、完全な音楽制作ワークフローをカバーします。日本語入力に対応し、日本語の説明から自動的に英語プロンプトを生成します。ポップス、ロック、J-POP、アニソン風、エレクトロニカなど、多様なジャンルに対応。主な機能：AI 作詞、ボーカル付き楽曲生成、インストゥルメンタル生成、ボーカルクローン、リファレンストラックによるスタイル転写。

### 한국어 개요
Skywork Music Maker는 Mureka AI API를 기반으로 한 전문 음악 제작 도구입니다. 자연어 설명으로 노래, 인스트루멘탈, 가사를 생성하며 완전한 음악 제작 워크플로우를 지원합니다. 한국어 입력을 지원하며, 한국어 설명에서 자동으로 영어 프롬프트를 생성합니다. K-POP, 발라드, 힙합, 인디, 트로트 등 다양한 장르에 대응합니다. 주요 기능: AI 작사, 보컬 포함 곡 생성, 인스트루멘탈 생성, 보컬 클론, 레퍼런스 트랙 기반 스타일 전사.

### Descripción en español
Skywork Music Maker es una herramienta profesional de creación musical basada en la API de Mureka AI. Permite generar canciones, instrumentales y letras a partir de descripciones en lenguaje natural, cubriendo el flujo completo de producción musical. Compatible con entrada en español: describe tu idea musical en español y el sistema generará automáticamente prompts optimizados en inglés. Soporta una amplia variedad de géneros: reggaetón, salsa, bachata, cumbia, pop latino, flamenco, bossa nova, rock en español y más. Funciones principales: composición de letras con IA, generación de canciones con vocales, producción de instrumentales, clonación de voz y transferencia de estilo mediante pistas de referencia.

---

## Privacy & Data Usage

- **API endpoint**: All API calls are made exclusively to `https://api.mureka.ai` (official Mureka endpoint by Skywork AI)
- **Data transmitted**: Lyrics text, music prompts, and uploaded audio files (reference tracks, vocal samples, melodies) are sent to Mureka servers for music generation
- **No third-party sharing**: No data is sent to any service beyond the official Mureka API
- **Local output**: Generated audio files and lyrics are saved locally to the user-specified output directory
- **No local caching of credentials**: The API key is read from the `MUREKA_API_KEY` environment variable at runtime; this skill does not store or cache credentials
- **User-managed billing**: Users must register their own Mureka account at https://platform.mureka.ai; all usage billing is handled directly by Mureka
- **Upload consent**: File uploads (reference audio, vocal samples, melodies) are initiated only when the user explicitly requests reference-based or vocal-cloning generation

---

## First-Time Setup

Before running any API command, check if `MUREKA_API_KEY` is set. If not, guide the user to get an API key at https://platform.mureka.ai/ (register → API Keys → generate key → `export MUREKA_API_KEY="..."`), then **STOP** — do not attempt any API calls until the key is configured.

## Smart Prompt Conversion (CRITICAL WORKFLOW)

**Default behavior**: When the user doesn't specify song type, always generate a song with lyrics (use `mureka.py song`). Only use `mureka.py instrumental` when the user explicitly asks for instrumental, BGM, background music, or "no vocals".

**Output defaults**: Use mp3 format unless the user requests otherwise. The `--output` flag specifies a directory — the script creates it and saves all results inside (audio files + lyrics.txt for songs). If the user doesn't specify a location, choose a user-friendly path with a descriptive folder name based on the song theme (e.g., `summer_pop_song/`).

When users provide music descriptions in natural language (in any language), you **MUST** convert them to structured Mureka API prompts using this workflow:

### Conversion Process

**User Input Examples:**
- "upbeat pop song, female vocals, guitar, perfect for summer"
- "sad piano ballad about lost love"
- "epic orchestral music for a fantasy game"
- "traditional Chinese music with bamboo flute and zither, misty atmosphere"
- "明るいJ-POP風の夏の曲を作って" (Japanese: bright J-POP style summer song)
- "슬픈 발라드 만들어줘, 피아노 위주로" (Korean: make a sad ballad, piano-focused)
- "做一首国风古典音乐，要有二胡和古筝" (Chinese: make a guofeng classical piece with erhu and guzheng)
- "Hazme una canción de reggaetón romántico con guitarra acústica" (Spanish: make a romantic reggaeton song with acoustic guitar)

**Your Task:**
1. Extract structured parameters using the extraction rules below
2. Validate the prompt meets quality standards (see Quality Checklist)
3. Present to user for confirmation before generating
4. Run the generation command with the structured prompt

### Parameter Extraction Rules

When users provide natural language music descriptions, directly extract and structure the following parameters:

**Required Parameters:**
- **genres**: music genres including fusion styles (e.g., Pop, Rock, Jazz, Pop Rap Fusion, Alternative Rock, Guofeng, J-POP, K-POP, Trot, Reggaetón, Salsa, Bachata, Cumbia, Flamenco, Bossa Nova)
- **moods**: emotional tones (e.g., Happy, Melancholic, Energetic, Nostalgic, Bright)
- **instruments**: specific instruments (e.g., Piano, Guitar, Drums, Erhu, Guzheng, Synth Pads, Dizi, Shamisen, Gayageum, Cajón, Congas, Bongos, Tres, Charango)
- **rhythms**: rhythm characteristics (e.g., 4/4, Slow, Syncopated, Driving, Flowing)
- **vocals**: vocal attributes (e.g., Female, Husky, Whispered, Male, Soft, Clear) or "instrumental only"
- **key**: musical key if specified (e.g., C Major, A Minor, C# Major)
- **bpm**: beats per minute (e.g., 120) or tempo descriptor (e.g., "slow groove", "uptempo")
- **description**: concise summary (under 50 words) capturing mood progression, melody, harmony, timbre, texture, dynamics

**Extraction Instructions:**
- **Translate non-English terms**: Convert ALL non-English musical terms to English while preserving cultural and musical meaning
- **Preserve specificity**: Keep detailed information including specific styles, subgenres, and cultural context (e.g., "Chinese traditional guofeng" not just "Chinese music")
- **Design dynamic arc**: Include mood progression where appropriate (e.g., "sparse opening → building tension → cathartic chorus")
- **Infer intelligently**: Make reasonable assumptions based on genre conventions when parameters are not explicitly stated
- **English output**: Final prompt string MUST be entirely in English

**Generate Structured Prompt:** Combine all extracted parameters into a comprehensive, natural-flowing description that captures the essence of the user's vision.

### Quality Checklist (Validate BEFORE Generation)

Before running the generation command, verify the prompt meets these criteria:

**MUST HAVE:**
- ☑ Specific genre (NOT "pop song" but "synth-pop, 2020s")
- ☑ BPM or tempo descriptor (e.g., "120 BPM" or "slow groove")
- ☑ 3-5 instruments explicitly named
- ☑ Mood/emotion descriptors (2-3 words)
- ☑ Vocal style (or "instrumental only")
- ☑ Structure tags in lyrics: [Verse], [Chorus], [Bridge], [Outro]

**WATCH OUT FOR:**
- Vague terms: "nice", "good", "beautiful" → replace with specific descriptors
- Contradictions: "slow" + "energetic", "sad" + "uplifting" → pick one direction
- Too short: <50 chars → add more detail
- Long lyric lines: >10 words per line → split into shorter lines
- No dynamic arc: add mood progression (e.g., "sparse → building → full")

**AVOID:**
- Command verbs: "create a song" → use descriptions "upbeat pop song"
- Famous artist names: "sounds like Taylor Swift" → describe qualities instead
- Unrealistic combos: melody_id cannot combine with other control options

After validation, present the generated prompt to the user for confirmation before proceeding.

---

## Core Workflow: Production Pipeline

1. **Conceptualize** → User describes in natural language → YOU convert to structured prompt
2. **Validate** → Check prompt quality against Quality Checklist (see above)
3. **Write Lyrics** → Use lyrics/generate or write manually
4. **Upload References** → Optional: reference track, vocal sample, melody
5. **Generate** → Submit song/instrumental task (async) with validated prompt
6. **Evaluate** → Listen to all N choices, pick best
7. **Iterate** → Refine prompt based on what you heard

**Critical Steps:**
- Step 1 is mandatory when user provides natural language input (especially non-English)
- Step 2 validation prevents 80% of common generation failures
- Step 3: Read `references/prompt_guide.md` for prompt crafting examples, lyrics structure rules (line length, syllable count, rhyme patterns, hook writing), and iteration best practices
- Do NOT skip conceptualization — jumping straight to generation without a clear concept is the #1 reason for generic results

**Your Role as AI Assistant:**
1. Convert user's natural language → structured Mureka prompt (using Smart Prompt Conversion)
2. Validate prompt quality → flag issues → suggest fixes
3. Write or generate lyrics with proper structure
4. Present prompt to user for confirmation
5. Execute generation command with validated prompt
6. Help iterate and refine based on generation results

---

## CLI Tool

All operations go through a single script: `scripts/mureka.py`

```
mureka.py song           Generate a song with lyrics and vocals
mureka.py instrumental   Generate an instrumental track
mureka.py lyrics         Generate or extend lyrics
mureka.py upload         Upload reference audio, vocals, melodies
```

Run `python scripts/mureka.py --help` for full usage. Note: use `-n 2` (single dash) to generate multiple choices, not `--n`.

## Common Scenarios

### "I just want background music for my video"
```bash
python scripts/mureka.py instrumental \
  --prompt "ambient electronic, calm, 80 BPM, soft pads, no percussion, background music for tech product video" \
  --output ./bg_music
```

### "I want a song but don't have lyrics"
```bash
# Step 1: Generate lyrics with proper structure
python scripts/mureka.py lyrics generate "a nostalgic summer love song, bittersweet, looking back at memories"

# Step 2: Copy/refine the output, then generate the song
python scripts/mureka.py song \
  --lyrics "[Verse]\n(paste lyrics here)\n[Chorus]\n(paste chorus here)" \
  --prompt "indie pop, warm, 110 BPM, acoustic guitar, soft drums, male vocal" \
  --output ./summer_song
```

---

## Advanced Features

### Reference-Based Generation
Upload a reference track (must be exactly 30s, mp3/m4a) to guide the style:
```bash
python scripts/mureka.py upload my_reference.mp3 --purpose reference
# → File ID: 542321
python scripts/mureka.py song --lyrics "[Verse]\n..." --reference-id 542321 --output ./song
```

### Vocal Cloning
Upload a vocal sample (15-30s, mp3/m4a) to use a specific voice:
```bash
python scripts/mureka.py upload my_voice.mp3 --purpose vocal
# → File ID: 789012
python scripts/mureka.py song --lyrics "[Verse]\n..." --vocal-id 789012 --prompt "R&B, smooth, 90 BPM" --output ./song
```

---

## Control Options & Rules

### Song Generation Control Combos

| Combo | prompt | reference_id | vocal_id | melody_id |
|-------|--------|-------------|----------|-----------|
| Style only | ✅ | | | |
| Reference only | | ✅ | | |
| Voice only | | | ✅ | |
| Melody only | | | | ✅ |
| Style + Voice | ✅ | | ✅ | |
| Reference + Voice | | ✅ | ✅ | |

**Important:**
- `melody_id` does NOT support any combination — use it alone
- `prompt` and `reference_id` are mutually exclusive — use one or the other

### Instrumental Generation Rules
For instrumentals, `prompt` and `instrumental_id` are mutually exclusive — use one or the other.

### File Upload Requirements

| Purpose | Format | Duration | Notes |
|---------|--------|----------|-------|
| reference | mp3/m4a | exactly 30s | Excess trimmed |
| vocal | mp3/m4a | 15-30s | Excess trimmed |
| melody | mp3/m4a/mid | 5-60s | MIDI recommended |
| instrumental | mp3/m4a | exactly 30s | For instrumental reference |

### Model Selection
Always use `mureka-8` — it is the latest and highest quality model.

---

## Error Handling

Scripts raise `RuntimeError` or `requests.HTTPError` on failure. Handle common errors:

| Error | Cause | Action |
|-------|-------|--------|
| 401 Unauthorized | Invalid or expired API key | Ask user to verify `MUREKA_API_KEY` |
| 429 Too Many Requests | Rate limit exceeded | Wait 30-60 seconds, then retry |
| 402 / Insufficient balance | Account balance depleted | Direct user to https://platform.mureka.ai to top up |
| Task ended with status: failed | Generation failed (bad prompt, server error) | Check prompt against Quality Checklist, retry |
| Task ended with status: timeouted | Generation took too long | Retry; if persistent, simplify the prompt or try a different model |
| ConnectionError / Timeout | Network issue | Retry after a few seconds |

**General strategy:** Read the error message carefully. If it's a client error (4xx), fix the input. If it's a server error (5xx) or timeout, retry once before escalating to the user.

## Troubleshooting Common Issues

| Problem | Solution |
|---------|----------|
| Task failed or timeouted | Check prompt meets quality checklist; verify lyrics have structure tags; retry the generation |
| Vocals sound rushed | Shorten lyric lines (≤10 words); reduce syllables per line |
| Listed instruments not audible | Verify each instrument named explicitly in prompt; add more specific descriptors |
| Prompt doesn't match output | Increase specificity (exact genre, BPM, instruments); add mood progression; generate n=3 choices |
| melody_id error | melody_id MUST be used alone — remove --prompt, --reference-id, --vocal-id |
| Invalid file_id | File IDs only valid for account that uploaded — re-upload file if from another session |

For parameter help:
```bash
python scripts/mureka.py --help
python scripts/mureka.py song --help
```

---

## Environment

- **API Key**: `MUREKA_API_KEY` environment variable (required)
- **Base URL**: https://api.mureka.ai
- **Dependencies**: Python 3, `requests` library
- **Billing**: Check balance with `curl -H "Authorization: Bearer $MUREKA_API_KEY" https://api.mureka.ai/v1/account/billing`
