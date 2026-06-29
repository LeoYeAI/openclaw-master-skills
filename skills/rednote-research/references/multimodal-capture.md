# RedNote Multimodal Capture Patterns

Use this file when the task involves screenshots, image posts, videos, gifs, subtitles, audio clips, or partial pages where the visible snippet is weaker than the underlying media signal.

## 1) Goal

Convert fragile public-web media evidence into inspectable notes without pretending to have more access than you do.

Priorities:
1. preserve what is directly visible
2. separate OCR/transcript output from interpretation
3. capture recovery paths when search snippets are partial
4. log each claim with evidence strength and modality

## 2) Observation ladder

Work from the most direct material available.

1. **Original media file or user-provided screenshot/video/audio**
2. **Fetched page with visible caption, alt text, surrounding text, or embedded metadata**
3. **Search snippet or cached preview**
4. **Secondary discussion about the media**

Do not collapse these levels together. A caption about a video is not the same as direct video inspection.

## 3) Image / screenshot workflow

For screenshots, posters, menus, notices, chat logs, or image-heavy posts:

### Capture
- note source URL and visible page title
- preserve visible date, username, location, and caption text if any
- describe image count and obvious layout if visible
- if text inside the image matters, treat OCR output as extracted evidence, not as guaranteed ground truth

### Extract
Break the image into layers:
- **Visible text:** exact words, numbers, prices, names, dates, hashtags, watermarks
- **Visual context:** scene, product, place, document type, UI layout, whether it looks cropped or edited
- **Confidence note:** clear / partially legible / low-resolution / occluded

### Analyze
Ask:
- is the key claim actually inside the image, or only in the caption/snippet?
- is the screenshot complete or selectively cropped?
- do visual details support or weaken the claim?
- is there a document number, store name, map pin, date, or interface cue that enables follow-up verification?

### Safe wording
- "The screenshot appears to show..."
- "The visible text suggests..."
- "I can read X with medium confidence; the lower section is cut off."

## 4) Video / gif workflow

Use when a post or search result points to a clip, reel, vlog, surveillance excerpt, or reaction video.

### Capture
Log:
- caption/title text
- visible duration if shown
- source URL
- visible upload date
- whether audio, subtitles, or comments are available from the public-web surface

### Extract in channels
- **Frames:** key scenes, objects, people, locations, documents, gestures, on-screen overlays
- **On-screen text:** subtitles, location stickers, date overlays, product names, prices
- **Narrative sequence:** what happens first / next / last
- **Edit cues:** cuts, zooms, reaction overlays, stitched repost indicators, meme captions

### Analysis questions
- does the clip itself show the claimed event, or only a reaction to it?
- are subtitles consistent with what is visible?
- does the clip appear heavily edited or excerpted?
- what would need actual frame extraction to verify more confidently?

### If only snippet-level access exists
Do not claim full clip analysis. Say:
- "Public-web access shows the caption/snippet, but not enough of the clip to verify the full sequence."
- "This looks like a video-led discussion, but I would need the file or extracted frames to analyze the clip itself."

## 5) Audio / ASR workflow

Use when the topic relies on voice notes, spoken explanations, livestream audio, or subtitle-less clips.

### Capture
- identify whether audio is directly available, indirectly referenced, or absent
- record speaker labels only when explicit
- preserve surrounding metadata: date, caption, URL, claimed context

### Extract
Separate:
- **Direct transcript** — exact spoken words if a transcript or subtitle exists
- **ASR-derived text** — machine-readable approximation from audio, if obtained
- **Interpretation** — meaning, tone, accusation, explanation, promise, denial

### Reliability notes
Lower confidence when:
- speaker overlap is strong
- background noise is heavy
- clip is very short
- the uploaded audio appears edited or spliced
- quote summaries differ from available transcript

### Safe wording
- "If the subtitle line is accurate, the speaker is claiming..."
- "I do not have enough direct audio access to verify tone or exact wording."
- "The available evidence is transcript-level, not waveform-level."

## 6) Partial-page fallback strategies

When the landing page is weak, inaccessible, or only partly indexed, recover carefully:

1. capture the search snippet verbatim enough to preserve the claim
2. search the exact title/caption phrase in quotes
3. search distinctive names, prices, dates, hashtags, or subtitle fragments
4. search for reposts, mirrors, or discussions quoting the same line
5. look for non-RedNote corroboration using the same entities or phrases
6. mark whether each recovered source is original, relay, or commentary

Good recovery targets:
- exact subtitle phrase
- menu price or product name
- notice title + date
- unique complaint wording
- hashtag + location

## 7) Evidence packaging for multimodal tasks

For each evidence item, log:
- modality: image / screenshot / video / gif / audio / mixed / text-page
- access level: direct file / fetched page / snippet / secondary relay
- extracted text: visible text or transcript fragment
- visual or audio summary
- claim supported
- confidence
- missing piece

## 8) Common traps

Avoid these mistakes:
- treating OCR text as perfectly accurate
- assuming subtitles are faithful to speech
- inferring full comment sentiment from one snippet
- calling a reposted clip "first-hand evidence"
- confusing popularity with verification
- ignoring crop/edit signs in screenshots or videos

## 9) Decision rule

If media matters to the conclusion, but you only have snippet-level access, keep the final answer provisional and say what direct media artifact would most improve confidence.
