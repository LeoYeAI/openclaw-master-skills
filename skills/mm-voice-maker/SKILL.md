---
name: mm-voice-maker
description: Enables voice synthesis, voice cloning, voice design, and audio post-processing using MiniMax Voice API and FFmpeg. Use when converting text to speech, creating custom voices, or processing/merging audio.
---

# MiniMax Voice Maker

Professional text-to-speech skill with emotion detection, voice cloning, and audio processing capabilities powered by MiniMax Voice API and FFmpeg.


## Capabilities

| Area | Features |
|------|----------|
| **TTS** | Sync (HTTP/WebSocket), async (long text), streaming |
| **Segment-based** | Multi-voice, multi-emotion synthesis from segments.json, auto merge |
| **Voice** | Cloning (10s–5min), design (text prompt), management |
| **Audio** | Format conversion, merge, normalize, trim, remove silence (FFmpeg) |

## File structure:
```
mmVoice_Maker/
├── SKILL.md                       # This overview
├── mmvoice.py                     # CLI tool (recommended for Agents)
├── check_environment.py           # Environment verification
├── requirements.txt
├── scripts/                       # Entry: scripts/__init__.py
│   ├── utils.py                   # Config, data classes
│   ├── sync_tts.py                # HTTP/WebSocket TTS
│   ├── async_tts.py               # Long text TTS
│   ├── segment_tts.py             # Segment-based TTS (multi-voice, multi-emotion)
│   ├── voice_clone.py             # Voice cloning
│   ├── voice_design.py            # Voice design
│   ├── voice_management.py        # List/delete voices
│   └── audio_processing.py        # FFmpeg audio tools
└── reference/                     # Load as needed
    ├── cli-guide.md               # CLI usage guide
    ├── getting-started.md         # Setup and quick test
    ├── tts-guide.md               # Sync/async TTS workflows
    ├── voice-guide.md             # Clone/design/manage
    ├── audio-guide.md             # Audio processing
    ├── script-examples.md         # Runnable code snippets
    ├── troubleshooting.md         # Common issues
    ├── api_documentation.md       # Complete API reference
    └── voice_catalog.md           # Voice selection guide
```


## Main Workflow Guideline (Text to Speech)

**6-step workflow:**
[step1]. Verify environment

[step2-preparation]⚠️NOTE: Before processing the text, you must read [voice-catalog.md](reference/voice-catalog.md) for voice selection.

[step2]. Process text into script → `<cwd>/audio/segments.json`. Note: [Step2.4] is really important, you must check it twice before sending the script to the user.

[step2.5]. ⚠️ Generate preview for user confirmation (highly recommended for multi-voice content)

[step3]. Present plan to user for confirmation

[step4]. Validate segments.json

[step5]. Generate and merge audio → intermediate files in `<cwd>/audio/tmp/`, final output in `<cwd>/audio/output.mp3`

[step6]. ⚠️ **CRITICAL**: User confirms audio quality FIRST → THEN cleanup temp files (only after user is satisfied)

> `<cwd>` is Claude's current working directory (not the skill directory). Audio files are saved relative to where Claude is running commands.

### Step 1: Verify environment

```bash
python check_environment.py
```

Checks:
- Python 3.8+
- Required packages (requests, websockets)
- FFmpeg installation
- MINIMAX_VOICE_API_KEY environment variable

If API key is not set, ask user for keys and set it:
```bash
export MINIMAX_VOICE_API_KEY="your-api-key-here"
```

### Step 2: Decision and Pre-processing

**⚠️ MOST IMPORTANT PRINCIPLE: Gender Matching First**

Before selecting voices, you MUST always match gender first. This is non-negotiable.

**Golden Rule:**
> **If a character is male → use male voice**
> **If a character is female → use female voice**
> **If a character is neutral/other → choose appropriate neutral voice**

**Why this matters:**
- Violating gender matching (e.g., male character with female voice) breaks immersion
- Even if personality traits match, gender comes first
- This is especially critical for classic literature, historical content, and professional narration

**Examples:**
| Character | Wrong Voice | Correct Voice |
|-----------|-------------|---------------|
| 唐三藏 (male monk) | `female-yujie` ❌ | `Chinese (Mandarin)_Gentleman` ✅ |
| 林黛玉 (female) | `male-qn-badao` ❌ | `female-shaonv` ✅ |
| 曹操 (male warlord) | `female-chengshu` ❌ | `Chinese (Mandarin)_Unrestrained_Young_Man` ✅ |

**Decision guide:**
Evaluate based on:
- Does the user specify a model? → Use that model, or use the default one "speech-2.8"
- Is multi-voice needed? → Different voice_id per speaker/character
- For speech-2.8: emotion is auto-matched (leave `emotion` empty)
- For older models: manually specify emotion tags

**Use case scenarios:**

| Scenario | Description | Segments | Voice Selection |
|----------|-------------|----------|-----------------|
| **Single Voice** | User needs one voice for the entire content. Segment only by length (≤1,000,000 chars per segment). | Split by length only | One voice_id for all segments |
| **Multi-Voice** | Multiple characters/speakers, each with different voice. Segment by speaker/role changes. | Split by logical unit (speaker, dialogue, etc.) | Different voice_id per role |
| **Podcast/Interview** | Host and guest speakers with distinct voices. | Split by speaker | Voice per host/guest |
| **Audiobook/Fiction** | Narrator and character voices. | Split by narration vs. dialogue | Voice per narrator/character |
| **Documentary** | Mostly narration with occasional quotes. | Keep as one segment | Single narrator voice |
| **Report/Announcement** | Formal content with consistent tone. | Keep as one segment | Professional voice |

**Processing Workflow (4 sub-steps):**

**Step 2.1: Text Segmentation and Role Analysis**
First, segment your text into logical units and identify the role/character for each segment.

**Key principle (Important!): Split by logical unit, NOT simply by sentence**

**When to split (Important!):**
- Different speakers clearly marked
- Narrator vs. character dialogue (in fiction/audiobooks/interview etc.)
- In some scenarios (like audiobooks, multi-voice fiction etc.), where speaker's identity is important, split when narration and dialogue mix in the same sentence.

**When NOT to split (Important!):**
- Third-person narration like "John said..." or "The reporter noted..."
- Quoted speech in narration (in documentary/podcast/report etc.) should keep in narrator's voice
- Keep in narrator's voice unless specific characterization is needed

**Decision depends on use case:**

| Use case | Example | Split strategy |
|----------|---------|----------------|
| **Single Voice** | Long article, news piece, announcement | Split by length (≤1,000,000 chars), same voice for all |
| **Podcast/Interview** | "Host: Welcome to the show. Guest: Thank you for having me." | Split by speaker |
| **Documentary narration** | "The scientist explained, 'The results are promising.'" | Keep as one segment (narrator voice) |
| **Audiobook/Fiction** | "'Who's there?' she whispered." | Split: "'Who's there?'" should be in character voice, while "she whispered." should be in narrator's voice |
| **Report** | "According to the report, the economy is growing." | Keep as one segment |

**Example1: Single Voice (speech-2.8)**
For single-voice content (e.g., news, announcements, articles), segment only by length while maintaining the same voice:
```json
[
  {"text": "First part of the article (under 1,000,000 chars)...", "role": "narrator", "voice_id": "female-shaonv", "emotion": ""},
  {"text": "Second part of the article (under 1,000,000 chars)...", "role": "narrator", "voice_id": "female-shaonv", "emotion": ""},
  {"text": "Third part of the article (under 1,000,000 chars)...", "role": "narrator", "voice_id": "female-shaonv", "emotion": ""}
]
```

**Example2: Audiobook with characters (speech-2.8)**
In audiobooks (multi-voice fiction), split when narration and dialogue mix in the same sentence:
```json
[
  {"text": "The detective entered the room.", "role": "narrator", "voice_id": "", "emotion": ""},
  {"text": "\"Who's there?\"", "role": "female_character", "voice_id": "", "emotion": ""},
  {"text": "she whispered.", "role": "narrator", "voice_id": "", "emotion": ""},
  {"text": "\"It's me,\"", "role": "male_character", "voice_id": "", "emotion": ""},
  {"text": "he replied calmly.", "role": "narrator", "voice_id": "", "emotion": ""}
]
```

**Example3: Documentary/podcast narration (speech-2.8)**
Quoted speech in narration stays in narrator's voice (no need to split):
```json
[
  {
    "text": "The scientist explained, \"The results show significant improvement in all test groups.\"",
    "role": "narrator",
    "voice_id": "",
    "emotion": ""
  },
  {
    "text": "According to the latest report, the economy has grown by 3% this quarter.",
    "role": "narrator",
    "voice_id": "",
    "emotion": ""
  }
]

**Note:** In the preliminary `segments.json`:
- Fill in the `text` field with segment content
- Fill in the `role` field to identify the character (narrator, male_character, female_character, host, guest, etc.)
- Leave `voice_id` empty (to be filled in Step 2.2)
- Leave `emotion` empty for speech-2.8 models


**Step 2.2: Voice Selection**

After segmenting and labeling roles, analyze all detected characters in your text. Consult [voice_catalog.md](reference/voice_catalog.md) **Section 1 "How to Choose a Voice"** to match voices to characters.

**⚠️ CRITICAL: Follow the two-step selection process below**

**Path A — Professional domains (Story/Narration, News/Announcements, Documentary):**
If the content belongs to one of these three professional domains, prioritize selecting from the recommended voices in **voice_catalog.md Section 2.1** (filter by scenario + gender). These voices are specifically optimized for their professional use cases.

**Path B — All other scenarios:**
Select from **voice_catalog.md Section 2.2**, following this strict priority hierarchy:

1. **First: Match Gender** (non-negotiable) — Male characters MUST use male voices, female characters MUST use female voices
2. **Second: Match Language** — The voice MUST match the content language (Chinese content → Chinese voice, Korean content → Korean voice, English content → English voice, etc.). Never assign a voice from the wrong language.
3. **Third: Match Age** — Determine the age group (Children / Youth / Adult / Elderly / Professional) and select from the corresponding subsection in Section 2.2
4. **Fourth: Match Personality & Role** — Choose the best fit based on personality traits, tone, and character role

**Voice Selection Decision Tree:**
```
Is this a professional domain (Story/News/Documentary)?
├── YES → Select from voice_catalog Section 2.1 (filter by scenario + gender)
└── NO → Select from voice_catalog Section 2.2:
    Step 1: Match Gender
    ├── Male character → Male voices only
    └── Female character → Female voices only
    Step 2: Match Age Group
    └── Children / Youth / Adult / Elderly / Professional
    Step 3: Match Language
    └── Filter to voices matching the content language
    Step 4: Match Personality & Role
    └── Choose best fit by tone, personality, character role
```

**Step 2.3: Emotions Segmentation** *(For non-2.8 series models only)*
For models other than speech-2.8 series, analyze emotions in your segments:
- For **long segments**, split further based on **emotional transitions**
- Add appropriate **emotion tags** to each segment
- Refer to Section 3 in [text-processing.md](reference/text-processing.md) for emotion tags and examples
- Skip this step for speech-2.8 models (emotion is auto-matched)

**Emotion Tags:**
- For speech-2.6 series (speech-2.6-hd and speech-2.6-turbo): happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper
- For older models: happy, sad, angry, fearful, disgusted, surprised, calm (7 emotions)


**Step 2.4: Check and Post-processing**
Finally, review and optimize your script:
- Verify segment length limits (async TTS ≤1,000,000 characters)
- Clean up conversational text (remove speaker names if needed)
- Ensure consistency in voice and emotion tags
- **Critical check for multi-voice content**: For audiobooks, multi-voice fiction, or content where dialogue is presented from a first-person perspective, verify that narration and dialogue mixed in the same sentence are properly split.

  **When splitting IS needed (first-person dialogue in fiction/audiobooks):**
  
  Example: `"John asked, 'Where are you going?'"` should be split into:
  - Segment 1: `"John asked, "` - uses narrator voice (describes who is speaking)
  - Segment 2: `"Where are you going?"` - uses the character's voice (actual dialogue in first-person)

  This ensures proper voice differentiation: descriptive narration uses the narrator's voice, while the character's spoken words use the character's designated voice.

  **When splitting is NOT needed (third-person quotes in podcast/documentary/news):**
  
  In podcasts, documentaries, or news reports, quoted speech is typically presented in third-person narrative style - the speaker's words are being reported, not performed. Keep these as one segment with the narrator's voice and remove the speaker's name at the beginning:
  
  - `"Welcome to our show." → narrator voice, remove the speaker's name (like "The host said:") at the beginning
  - `"According to experts, 'This technology represents a significant breakthrough.'" → keep as one segment (narrator voice)
  - `"Scientists noted, 'The experimental results exceeded our expectations.'" → keep as one segment (narrator voice)
- **If the split is missing**: Go back to Step 2.1 and ensure dialogue portions are separated from narration with appropriate role labels.

**Create segments.json:**
After completing all 4 sub-steps, save the final `segments.json` to `<cwd>/audio/segments.json`.


### Step 2.5: Generate Preview for User Confirmation (Highly Recommended)

**For multi-voice content (audiobooks, dramas, etc.), always generate a preview first.**

This saves time and prevents waste when voice selections need adjustment.

**How to generate a preview:**
1. Create a smaller segments file with 10-20 representative segments (include all characters)
2. Generate the preview audio
3. Ask user to listen and confirm voice choices

**Preview segments.json example:**
```json
[
  {"text": "Narration opening...", "role": "narrator", "voice_id": "...", "emotion": ""},
  {"text": "Male character speaks...", "role": "male_character", "voice_id": "...", "emotion": ""},
  {"text": "Female character speaks...", "role": "female_character", "voice_id": "...", "emotion": ""},
  {"text": "More dialogue...", "role": "...", "voice_id": "...", "emotion": ""}
]
```

**Preview command:**
```bash
python mmvoice.py generate segments_preview.json -o preview.mp3
```

**When user confirms preview:**
- Use the same voice selections for the full segments.json
- No need to re-select voices

---

### Step 3: Present plan to user for confirmation

Before proceeding to validation and generation, present the segmentation plan to the user and wait for confirmation:

**Present to the user:**
- **Roles identified**: List all characters/speakers in the text
- **Voice assignments**: Show which voice_id is assigned to each role (include voice characteristics from voice_catalog.md)
- **Model being used**: Explain why this model was selected
- **Language**: Confirm the primary language of the content
- **Emotion approach**: Auto-matched (speech-2.8) or manual tags (older models)


**Example confirmation message:**
```
I've analyzed the text and created a segmentation plan:

**Roles and Voices:**
- Narrator: male-qn-jingying (deep, authoritative, suitable for storytelling)
- Protagonist: female-shaonv (bright, energetic, youthful)
- Antagonist: male-qn-qingse (cool, menacing)

**Model:** speech-2.8-hd (recommended - automatic emotion matching)
**Language:** Chinese
**Segments:** 8 segments total

Please review and confirm:
1. ⚠️ **Gender Verification**: Do the voice genders match the character genders?
   - [Narrator: Male ✓] [Protagonist: Female ✓] [Antagonist: Male ✓]
2. ⚠️ **Language Verification**: Do the voice languages match the content language?
   - [All voices: Chinese ✓]
3. Are the voice assignments appropriate for each character (age, personality)?
4. Should any segments be combined or split differently?
5. Any other changes you'd like to make?

**After generation:**
- I'll generate a preview first for you to review
- Only after you confirm the audio quality will I clean up temporary files
- If not satisfied, I'll re-generate and we iterate until you're happy

Reply "confirm" to proceed, or let me know what to adjust.
```

**Wait for user response:**
- If user confirms → Proceed to Step 4 (validate)
- If user suggests changes → Update `segments.json` and present the plan again for confirmation


### Step 4: Validate segments.json (model, emotion, voice_id validation)

Before generating audio, validate the segments file:

```bash
# Default: speech-2.8-hd (auto emotion matching)
python mmvoice.py validate <cwd>/audio/segments.json

# Specify model for context-specific validation
python mmvoice.py validate <cwd>/audio/segments.json --model speech-2.6-hd

# Validate voice_ids against available voices (slower, requires API call)
python mmvoice.py validate <cwd>/audio/segments.json --validate-voices

# Combined options (recommended)
python mmvoice.py validate <cwd>/audio/segments.json --model speech-2.6-hd --validate-voices

# Use `--verbose` to see segment details
python mmvoice.py validate <cwd>/audio/segments.json --model speech-2.6-hd --validate-voices --verbose

```

**Emotion Validation checks:**

| Model | Emotion Validation |
|-------|-------------------|
| **speech-2.8-hd/turbo** | Emotion can be empty (auto emotion matching) |
| **speech-2.6-hd/turbo** | All 9 emotions supported |
| **Older models** | happy, sad, angry, fearful, disgusted, surprised, calm (7 emotions) |

**Voice ID validation:**
**With `--validate-voices`:**
- Calls API once to get all available voices
- Validates each voice_id against the list
- Shows errors for invalid voice_ids (blocks validation)


### Step 5: Generate and merge audio

Generate audio for all segments and merge into final output.

**File placement (default behavior if user doesn't specify):**

```
<cwd>/                      # Claude's current working directory
└── audio/                  # Created automatically
    ├── tmp/                # Intermediate segment files
    │   ├── segment_0000.mp3
    │   ├── segment_0001.mp3
    │   └── ...
    └── <custom_audio_name>.mp3             # Final merged audio, name can be customized
```

Where `<cwd>` is Claude's current working directory (where commands are executed).

- If `-o` is not specified, output goes to `<cwd>/audio/output.mp3`
- Intermediate files go to `<cwd>/audio/tmp/`
- After user confirms the final audio, ask whether to delete `<cwd>/audio/tmp/`

**Basic usage:**
```bash
# Default: speech-2.8-hd, output to <cwd>/audio/output.mp3
python mmvoice.py generate <cwd>/audio/segments.json

# Specify output path
python mmvoice.py generate <cwd>/audio/segments.json -o <cwd>/audio/<custom_audio_name>.mp3

# Specify model if needed
python mmvoice.py generate <cwd>/audio/segments.json --model speech-2.6-hd
```

**Skip existing segments (for rate limit retries):**
```bash
# Only generate segments that don't exist yet - skips already-generated files
python mmvoice.py generate <cwd>/audio/segments.json --skip-existing
```

**Error handling:**
- If a segment fails, the script reports which segment and why
- Use `--continue-on-error` to generate remaining segments despite failures
- Use `--skip-existing` to skip already successfully generated segments (recommended for retries after rate limit)
- The script automatically uses fallback merging if FFmpeg filter_complex fails

### Step 6: Confirm and cleanup

**⚠️ CRITICAL: Never delete temp files until user confirms!**

After generation completes, you MUST follow this exact sequence:

**Step 6.1: Report generation result to user**
```
✓ Audio saved to: <output_path>
  Generated: X/Y segments
  Intermediate files in: <cwd>/audio/tmp/
```

**Step 6.2: Ask user to confirm audio quality**
Ask the user to listen to the audio and confirm:
1. Is the audio quality satisfactory?
2. Are all voices appropriate?
3. Any adjustments needed?

**Step 6.3: Wait for user response**

**Step 6.4: Only after user confirms, offer cleanup**
```
After confirming audio quality, temporary files can be deleted with:
rm -rf <cwd>/audio/tmp/
```

**NEVER execute rm -rf on temp files without explicit user confirmation!**

If user is NOT satisfied:
- Do NOT delete temp files
- Discuss what needs to be adjusted
- Re-generate affected segments if needed
- Ask for confirmation again


## Other Usage

Use the following when the task involves **voice creation**, **single-voice TTS** (sync/async), or **audio processing** instead of the main segment-based workflow. Each subsection gives CLI commands, script paths, and the reference doc to open for details.

### Voice creation (clone / design / list)

- **Purpose:** Create custom voices from audio (clone) or from a text description (design); list system and custom voices.
- **CLI (entry point: `mmvoice.py`):**
  ```bash
  python mmvoice.py clone AUDIO_FILE --voice-id VOICE_ID   # Clone from 10s–5min audio
  python mmvoice.py design "DESCRIPTION" --voice-id ID      # Design from text
  python mmvoice.py list-voices                             # List all voices
  ```
- **Scripts:** `scripts/voice_clone.py` (clone), `scripts/voice_design.py` (design), `scripts/voice_management.py` (list/manage).
- **Documentation:** **reference/voice-guide.md** — cloning (quick + high-quality + step-by-step), design workflow, management.

### Text-to-speech (sync / async)

- **Purpose:** Single-voice TTS: sync for short text (≤10k chars), async for long text (up to 1M chars); optional streaming.
- **CLI:**
  ```bash
  python mmvoice.py tts "TEXT" -o OUTPUT.mp3 [-v VOICE_ID] [--model MODEL]
  ```
- **Scripts:** `scripts/sync_tts.py` (HTTP/WebSocket sync), `scripts/async_tts.py` (async task + poll).
- **Documentation:** **reference/tts-guide.md** — sync TTS, async TTS, streaming, segment-based production.

### Audio processing (merge / convert / normalize)

- **Purpose:** Merge files (with optional crossfade), convert format, normalize loudness, trim.
- **CLI:**
  ```bash
  python mmvoice.py merge FILE1 [FILE2 ...] -o OUTPUT [--crossfade MS]
  python mmvoice.py convert INPUT -o OUTPUT [--format FORMAT]
  ```
- **Script:** `scripts/audio_processing.py` (merge, convert, normalize, trim).
- **Documentation:** **reference/audio-guide.md** — format conversion, merging (filter_complex + concat demuxer fallback), normalization, trimming, optimization.

### Segment-based TTS (main workflow)

- **CLI:** `validate` and `generate` as in Steps 4–5 above.
- **Script:** `scripts/segment_tts.py`.
- **Documentation:** **reference/cli-guide.md**, **reference/api_documentation.md**.

---

## Reference documents (on-demand)

Open these when you need concrete usage, parameters, or troubleshooting. Paths are relative to the skill root.

| Document | Content for the Agent |
|----------|------------------------|
| **reference/cli-guide.md** | All CLI commands (`validate`, `generate`, `tts`, `clone`, `design`, `list-voices`, `merge`, `convert`, `check-env`) with options and examples. Use for correct CLI invocation. |
| **reference/getting-started.md** | Environment setup (venv, `pip install`, FFmpeg), `MINIMAX_VOICE_API_KEY`, basic synthesis test. Use for first-time setup or “env not working”. |
| **reference/tts-guide.md** | Sync TTS (short text), async TTS (long text), streaming TTS, multi-segment production. Use for sync/async/streaming logic and parameters. |
| **reference/voice-guide.md** | Voice cloning (quick, high-quality with prompt audio, step-by-step), voice design, voice management. Use for custom voice creation flows. |
| **reference/audio-guide.md** | Format conversion, merging (including crossfade and fallback), normalization, trimming, optimization. Use for merge/convert/normalize behavior and options. |
| **reference/script-examples.md** | Copy-paste runnable examples for sync TTS, async TTS, segment-based TTS, audio processing, voice clone/design/management. Use for quick Python snippets. |
| **reference/troubleshooting.md** | Environment (API key, FFmpeg), API errors, segment-based TTS, audio, voice. Use when an error message or unexpected behavior appears. |
| **reference/api_documentation.md** | Full API reference: config, sync/async TTS, emotion parameter, segment-based TTS, voice clone/design/management, audio processing, common parameters, error handling. Use for exact function signatures and parameter details. |
| **reference/voice_catalog.md** | System voices list (male/female/beta), selection guide, voice parameters, custom voices, voice IDs. Use to choose or look up `voice_id`. |


## Important notes

### Requirements
- **Python**: 3.8 or higher
- **API Key**: `MINIMAX_VOICE_API_KEY` environment variable must be set
- **FFmpeg**: Required for audio processing (merge, convert, normalize)
  - Install: `brew install ffmpeg` (macOS) or `sudo apt install ffmpeg` (Ubuntu)

### Limits and constraints
- **Text length**: Sync TTS ≤10,000 chars; async TTS ≤1,000,000 chars
- **Voice cloning**: Audio must be 10s–5min duration, ≤20MB, formats: mp3/wav/m4a
- **Voice expiration**: Custom voices (cloned/designed) expire after 7 days if not used with TTS

### Special features
- **Pause insertion**: Use `<#x#>` in text where x = pause duration in seconds (0.01–99.99)
  - Example: `"Hello<#1.5#>world"` creates 1.5s pause between words
- **Supported emotions**: happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper
  - speech-2.8: automatic matching; speech-2.6: all 9; older models: first 7

### Troubleshooting
- Run `python check_environment.py` to diagnose setup issues
- See [troubleshooting.md](reference/troubleshooting.md) for common problems and solutions
- Check [getting-started.md](reference/getting-started.md) for detailed setup instructions
