---
name: google-gemini-media
description: Use the Gemini API (Nano Banana image generation, Veo video, Gemini TTS speech and audio understanding) to deliver end-to-end multimodal media workflows and code templates for "generation + understanding".
license: MIT
---

# Gemini Multimodal Media (Image/Video/Speech) Skill

## 1. Goals and scope

This Skill consolidates six Gemini API capabilities into reusable workflows and implementation templates:

- Image generation (Nano Banana: text-to-image, image editing, multi-turn iteration)
- Image understanding (caption/VQA/classification/comparison, multi-image prompts; supports inline and Files API)
- Video generation (Veo 3.1: text-to-video, aspect ratio/resolution control, reference-image guidance, first/last frames, video extension, native audio)
- Video understanding (upload/inline/YouTube URL; summaries, Q&A, timestamped evidence)
- Speech generation (Gemini native TTS: single-speaker and multi-speaker; controllable style/accent/pace/tone)
- Audio understanding (upload/inline; description, transcription, time-range transcription, token counting)

> Convention: This Skill follows the official Google Gen AI SDK (Node.js/REST) as the main line; currently only Node.js/REST examples are provided. If your project already wraps other languages or frameworks, map this Skill's request structure, model selection, and I/O spec to your wrapper layer.

---

## 2. Quick routing (decide which capability to use)

1) **Do you need to produce images?**
- Need to generate images from scratch or edit based on an image -> use **Nano Banana image generation** (see Section 5)

2) **Do you need to understand images?**
- Need recognition, description, Q&A, comparison, or info extraction -> use **Image understanding** (see Section 6)

3) **Do you need to produce video?**
- Need to generate an 8-second video (optionally with native audio) -> use **Veo 3.1 video generation** (see Section 7)

4) **Do you need to understand video?**
- Need summaries/Q&A/segment extraction with timestamps -> use **Video understanding** (see Section 8)

5) **Do you need to read text aloud?**
- Need controllable narration, podcast/audiobook style, etc. -> use **Speech generation (TTS)** (see Section 9)

6) **Do you need to understand audio?**
- Need audio descriptions, transcription, time-range transcription, token counting -> use **Audio understanding** (see Section 10)

---

## 3. Unified engineering constraints and I/O spec (must read)

### 3.0 Prerequisites (dependencies and tools)

- Node.js 18+ (match your project version)
- Install SDK (example):
```bash
npm install @google/genai
```
- REST examples only need `curl`; if you need to parse image Base64, install `jq` (optional).

### 3.1 Authentication and environment variables

- Put your API key in `GEMINI_API_KEY`
- REST requests use `x-goog-api-key: $GEMINI_API_KEY`

### 3.2 Two file input modes: Inline vs Files API

**Inline (embedded bytes/Base64)**
- Pros: shorter call chain, good for small files.
- Key constraint: total request size (text prompt + system instructions + embedded bytes) typically has a ~20MB ceiling.

**Files API (upload then reference)**
- Pros: good for large files, reusing the same file, or multi-turn conversations.
- Typical flow:
  1. `files.upload(...)` (SDK) or `POST /upload/v1beta/files` (REST resumable)
  2. Use `file_data` / `file_uri` in `generateContent`

> Engineering suggestion: implement `ensure_file_uri()` so that when a file exceeds a threshold (for example 10-15MB warning) or is reused, you automatically route through the Files API.

### 3.3 Unified handling of binary media outputs

- **Images**: usually returned as `inline_data` (Base64) in response parts; in the SDK use `part.as_image()` or decode Base64 and save as PNG/JPG.
- **Speech (TTS)**: usually returns **PCM** bytes (Base64); save as `.pcm` or wrap into `.wav` (commonly 24kHz, 16-bit, mono).
- **Video (Veo)**: long-running async task; poll the operation; download the file (or use the returned URI).

---

## 4. Model selection matrix (choose by scenario)

> Important: model names, versions, limits, and quotas can change over time. Verify against official docs before use. Last updated: 2026-01-22.

### 4.1 Image generation (Nano Banana)
- **gemini-2.5-flash-image**: optimized for speed/throughput; good for frequent, low-latency generation/editing.
- **gemini-3-pro-image-preview**: stronger instruction following and high-fidelity text rendering; better for professional assets and complex edits.

### 4.2 General image/video/audio understanding
- Docs use `gemini-3-flash-preview` for image, video, and audio understanding (choose stronger models as needed for quality/cost).

### 4.3 Video generation (Veo)
- Example model: `veo-3.1-generate-preview` (generates 8-second video and can natively generate audio).

### 4.4 Speech generation (TTS)
- Example model: `gemini-2.5-flash-preview-tts` (native TTS, currently in preview).

---

## 5. Image generation (Nano Banana)

### 5.1 Text-to-Image

**SDK (Node.js) minimal template**
```js
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const response = await ai.models.generateContent({
  model: "gemini-2.5-flash-image",
  contents:
    "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme",
});

const parts = response.candidates?.[0]?.content?.parts ?? [];
for (const part of parts) {
  if (part.text) console.log(part.text);
  if (part.inlineData?.data) {
    fs.writeFileSync("out.png", Buffer.from(part.inlineData.data, "base64"));
  }
}
```

**REST (with imageConfig) minimal template**
```bash
curl -s -X POST   "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"   -H "x-goog-api-key: $GEMINI_API_KEY"   -H "Content-Type: application/json"   -d '{
    "contents":[{"parts":[{"text":"Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"}]}],
    "generationConfig": {"imageConfig": {"aspectRatio":"16:9"}}
  }'
```

**REST image parsing (Base64 decode)**
```bash
curl -s -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"A minimal studio product shot of a nano banana"}]}]}' \
  | jq -r '.candidates[0].content.parts[] | select(.inline_data) | .inline_data.data' \
  | base64 --decode > out.png

# macOS can use: base64 -D > out.png
```

### 5.2 Text-and-Image-to-Image

Use case: given an image, **add/remove/modify elements**, change style, color grading, etc.

**SDK (Node.js) minimal template**
```js
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const prompt =
  "Add a nano banana on the table, keep lighting consistent, cinematic tone.";
const imageBase64 = fs.readFileSync("input.png").toString("base64");

const response = await ai.models.generateContent({
  model: "gemini-2.5-flash-image",
  contents: [
    { text: prompt },
    { inlineData: { mimeType: "image/png", data: imageBase64 } },
  ],
});

const parts = response.candidates?.[0]?.content?.parts ?? [];
for (const part of parts) {
  if (part.inlineData?.data) {
    fs.writeFileSync("edited.png", Buffer.from(part.inlineData.data, "base64"));
  }
}
```

### 5.3 Multi-turn image iteration (Multi-turn editing)

Best practice: use chat for continuous iteration (for example: generate first, then "only edit a specific region/element", then "make variants in the same style").  
To output mixed "text + image" results, set `response_modalities` to `["TEXT", "IMAGE"]`.

### 5.4 ImageConfig

You can set in `generationConfig.imageConfig` or the SDK config:
- `aspectRatio`: e.g. `16:9`, `1:1`.
- `imageSize`: e.g. `2K`, `4K` (higher resolution is usually slower/more expensive and model support can vary).

---

## 6. Image understanding (Image Understanding)

### 6.1 Two ways to provide input images

- **Inline image data**: suitable for small files (total request size < 20MB).
- **Files API upload**: better for large files or reuse across multiple requests.

### 6.2 Inline images (Node.js) minimal template
```js
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const imageBase64 = fs.readFileSync("image.jpg").toString("base64");

const response = await ai.models.generateContent({
  model: "gemini-3-flash-preview",
  contents: [
    { inlineData: { mimeType: "image/jpeg", data: imageBase64 } },
    { text: "Caption this image, and list any visible brands." },
  ],
});

console.log(response.text);
```

### 6.3 Upload and reference with Files API (Node.js) minimal template
```js
import { GoogleGenAI, createPartFromUri, createUserContent } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
const uploaded = await ai.files.upload({ file: "image.jpg" });

const response = await ai.models.generateContent({
  model: "gemini-3-flash-preview",
  contents: createUserContent([
    createPartFromUri(uploaded.uri, uploaded.mimeType),
    "Caption this image.",
  ]),
});

console.log(response.text);
```

### 6.4 Multi-image prompts

Append multiple images as multiple `Part` entries in the same `contents`; you can mix uploaded references and inline bytes.

---

## 7. Video generation (Veo 3.1)

### 7.1 Core features (must know)
- Generates **8-second** high-fidelity video, optionally 720p / 1080p / 4k, and supports native audio generation (dialogue, ambience, SFX).
- Supports:
  - Aspect ratio (16:9 / 9:16)
  - Video extension (extend a generated video; typically limited to 720p)
  - First/last frame control (frame-specific)
  - Up to 3 reference images (image-based direction)

### 7.2 SDK (Node.js) minimal template: async polling + download
```js
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const prompt =
  "A cinematic shot of a cat astronaut walking on the moon. Include subtle wind ambience.";
let operation = await ai.models.generateVideos({
  model: "veo-3.1-generate-preview",
  prompt,
  config: { resolution: "1080p" },
});

while (!operation.done) {
  await new Promise((resolve) => setTimeout(resolve, 10_000));
  operation = await ai.operations.getVideosOperation({ operation });
}

const video = operation.response?.generatedVideos?.[0]?.video;
if (!video) throw new Error("No video returned");
await ai.files.download({ file: video, downloadPath: "out.mp4" });
```

### 7.3 REST minimal template: predictLongRunning + poll + download

Key point: Veo REST uses `:predictLongRunning` to return an operation name, then poll `GET /v1beta/{operation_name}`; once done, download from the video URI in the response.

### 7.4 Common controls (recommend a unified wrapper)

- `aspectRatio`: `"16:9"` or `"9:16"`
- `resolution`: `"720p" | "1080p" | "4k"` (higher resolutions are usually slower/more expensive)
- When writing prompts: put dialogue in quotes; explicitly call out SFX and ambience; use cinematography language (camera position, movement, composition, lens effects, mood).
- Negative constraints: if the API supports a negative prompt field, use it; otherwise list elements you do not want to see.

### 7.5 Important limits (engineering fallback needed)

- Latency can vary from seconds to minutes; implement timeouts and retries.
- Generated videos are only retained on the server for a limited time (download promptly).
- Outputs include a SynthID watermark.

**Polling fallback (with timeout/backoff) pseudocode**
```js
const deadline = Date.now() + 300_000; // 5 min
let sleepMs = 2000;
while (!operation.done && Date.now() < deadline) {
  await new Promise((resolve) => setTimeout(resolve, sleepMs));
  sleepMs = Math.min(Math.floor(sleepMs * 1.5), 15_000);
  operation = await ai.operations.getVideosOperation({ operation });
}
if (!operation.done) throw new Error("video generation timed out");
```

---

## 8. Video understanding (Video Understanding)

### 8.1 Video input options
- **Files API upload**: recommended when file > 100MB, video length > ~1 minute, or you need reuse.
- **Inline video data**: for smaller files.
- **Direct YouTube URL**: can analyze public videos.

### 8.2 Files API (Node.js) minimal template
```js
import { GoogleGenAI, createPartFromUri, createUserContent } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
const uploaded = await ai.files.upload({ file: "sample.mp4" });

const response = await ai.models.generateContent({
  model: "gemini-3-flash-preview",
  contents: createUserContent([
    createPartFromUri(uploaded.uri, uploaded.mimeType),
    "Summarize this video. Provide timestamps for key events.",
  ]),
});

console.log(response.text);
```

### 8.3 Timestamp prompting strategy
- Ask for segmented bullets with "(mm:ss)" timestamps.
- Require "evidence with specific time ranges" and include downstream structured extraction (JSON) in the same prompt if needed.

---

## 9. Speech generation (Text-to-Speech, TTS)

### 9.1 Positioning
- Native TTS: for "precise reading + controllable style" (podcasts, audiobooks, ad voiceover, etc.).
- Distinguish from the Live API: Live API is more interactive and non-structured audio/multimodal conversation; TTS is focused on controlled narration.

### 9.2 Single-speaker TTS (Node.js) minimal template
```js
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const response = await ai.models.generateContent({
  model: "gemini-2.5-flash-preview-tts",
  contents: [{ parts: [{ text: "Say cheerfully: Have a wonderful day!" }] }],
  config: {
    responseModalities: ["AUDIO"],
    speechConfig: {
      voiceConfig: {
        prebuiltVoiceConfig: { voiceName: "Kore" },
      },
    },
  },
});

const data =
  response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data ?? "";
if (!data) throw new Error("No audio returned");
fs.writeFileSync("out.pcm", Buffer.from(data, "base64"));
```

### 9.3 Multi-speaker TTS (max 2 speakers)
Requirements:
- Use `multiSpeakerVoiceConfig`
- Each speaker name must match the dialogue labels in the prompt (e.g., Joe/Jane).

### 9.4 Voice options and language
- `voice_name` supports 30 prebuilt voices (for example Zephyr, Puck, Charon, Kore, etc.).
- The model can auto-detect input language and supports 24 languages (see docs for the list).

### 9.5 "Director notes" (strongly recommended for high-quality voice)
Provide controllable directions for style, pace, accent, etc., but avoid over-constraining.

---

## 10. Audio understanding (Audio Understanding)

### 10.1 Typical tasks
- Describe audio content (including non-speech like birds, alarms, etc.)
- Generate transcripts
- Transcribe specific time ranges
- Count tokens (for cost estimates/segmentation)

### 10.2 Files API (Node.js) minimal template
```js
import { GoogleGenAI, createPartFromUri, createUserContent } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
const uploaded = await ai.files.upload({ file: "sample.mp3" });

const response = await ai.models.generateContent({
  model: "gemini-3-flash-preview",
  contents: createUserContent([
    "Describe this audio clip.",
    createPartFromUri(uploaded.uri, uploaded.mimeType),
  ]),
});

console.log(response.text);
```

### 10.3 Key limits and engineering tips
- Supports common formats: WAV/MP3/AIFF/AAC/OGG/FLAC.
- Audio tokenization: about 32 tokens/second (about 1920 tokens per minute; values may change).
- Total audio length per prompt is capped at 9.5 hours; multi-channel audio is downmixed; audio is resampled (see docs for exact parameters).
- If total request size exceeds 20MB, you must use the Files API.

---

## 11. End-to-end examples (composition)

### Example A: Image generation -> validation via understanding
1) Generate product images with Nano Banana (require negative space, consistent lighting).
2) Use image understanding for self-check: verify text clarity, brand spelling, and unsafe elements.
3) If not satisfied, feed the generated image into text+image editing and iterate.

### Example B: Video generation -> video understanding -> narration script
1) Generate an 8-second shot with Veo (include dialogue or SFX).
2) Download and save (respect retention window).
3) Upload video to video understanding to produce a storyboard + timestamps + narration copy (then feed to TTS).

### Example C: Audio understanding -> time-range transcription -> TTS redub
1) Upload meeting audio and transcribe full content.
2) Transcribe or summarize specific time ranges.
3) Use TTS to generate a "broadcast" version of the summary.

---

## 12. Compliance and risk (must follow)

- Ensure you have the necessary rights to upload images/video/audio; do not generate infringing, deceptive, harassing, or harmful content.
- Generated images and videos include SynthID watermarking; videos may also have regional/person-based generation constraints.
- Production systems must implement timeouts, retries, failure fallbacks, and human review/post-processing for generated content.

---

## 13. Quick reference (Checklist)

- [ ] Pick the right model: image generation (Flash Image / Pro Image Preview), video generation (Veo 3.1), TTS (Gemini 2.5 TTS), understanding (Gemini Flash/Pro).
- [ ] Pick the right input mode: inline for small files; Files API for large/reuse.
- [ ] Parse binary outputs correctly: image/audio via inline_data decode; video via operation polling + download.
- [ ] For video generation: set aspectRatio / resolution, and download promptly (avoid expiration).
- [ ] For TTS: set response_modalities=["AUDIO"]; max 2 speakers; speaker names must match prompt.
- [ ] For audio understanding: countTokens when needed; segment long audio or use Files API.
