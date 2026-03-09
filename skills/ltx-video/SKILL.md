---
name: ltx-video
description: |
  Generate videos via LTX-2.3 API (ltx.video). Supports text-to-video, image-to-video,
  audio-to-video (lip-sync from audio + image), extend, and retake.
  Use when: generating AI video from text/image/audio, animating a portrait,
  creating lip-sync video from an existing image + audio recording.
---

# LTX-2.3 Video API

## API Reference

**Base URL:** `https://api.ltx.video/v1`  
**Auth:** `Authorization: Bearer <API_KEY>`  
**Response:** MP4 binary (direct download, no polling)

### Endpoints

| Endpoint | Input | Use |
|----------|-------|-----|
| `/v1/text-to-video` | prompt | Generate video from text |
| `/v1/image-to-video` | image_uri + prompt | Animate a still image |
| `/v1/audio-to-video` | audio_uri + image_uri + prompt | Lip-sync video from audio + image |
| `/v1/extend` | video_uri + prompt | Extend a video at start or end |
| `/v1/retake` | video_uri + time range | Regenerate a section of a video |

### Models

| Model | Speed | Quality |
|-------|-------|---------|
| `ltx-2-3-fast` | ~17s | Good (use for tests) |
| `ltx-2-3-pro` | ~30-60s | Best (use for final) |

### Supported Resolutions

- `1920x1080` (landscape 16:9)
- `1080x1920` (portrait 9:16 — native vertical, trained on vertical data)
- `1440x1080`, `4096x2160` (text-to-video only)

**audio-to-video only supports:** `1920x1080` or `1080x1920`

---

## Quick Examples

### Text to Video
```bash
curl -X POST "https://api.ltx.video/v1/text-to-video" \
  -H "Authorization: Bearer $LTX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A man in a navy blue suit sits at a luxury restaurant table...",
    "model": "ltx-2-3-pro",
    "duration": 8,
    "resolution": "1920x1080"
  }' -o output.mp4
```

### Audio to Video (Lip-sync)
```bash
curl -X POST "https://api.ltx.video/v1/audio-to-video" \
  -H "Authorization: Bearer $LTX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_uri": "https://example.com/voice.mp3",
    "image_uri": "https://example.com/portrait.jpg",
    "prompt": "A man speaks directly to camera...",
    "model": "ltx-2-3-pro",
    "resolution": "1920x1080"
  }' -o output.mp4
```

### Python Wrapper
```python
import requests

def ltx_audio_to_video(audio_url, image_url, prompt, api_key,
                        model="ltx-2-3-pro", resolution="1920x1080",
                        output_path="output.mp4"):
    r = requests.post(
        "https://api.ltx.video/v1/audio-to-video",
        headers={"Authorization": f"Bearer {api_key}",
                 "Content-Type": "application/json"},
        json={"audio_uri": audio_url, "image_uri": image_url,
              "prompt": prompt, "model": model, "resolution": resolution},
        timeout=300, stream=True
    )
    if r.status_code != 200:
        raise RuntimeError(f"LTX error {r.status_code}: {r.text}")
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(8192): f.write(chunk)
    return output_path
```

---

## ⚠️ Critical Rules (learned from experience)

### File Hosting
- URLs must be **HTTPS** — HTTP is rejected
- Files must return correct MIME type (not `application/octet-stream`)
- **uguu.se** works: upload with `curl -F "files[]=@file.mp3" https://uguu.se/upload`
- Audio: upload as **MP3** (not WAV) → uguu returns `audio/mpeg` ✅
- **4K images fail** → resize to 1920x1080 before uploading

```bash
# Upload MP3 to uguu.se
AUDIO_URL=$(curl -s -F "files[]=@audio.mp3" "https://uguu.se/upload" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['files'][0]['url'])")

# Upload image
IMAGE_URL=$(curl -s -F "files[]=@portrait.jpg" "https://uguu.se/upload" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['files'][0]['url'])")
```

### Image Size Limit
```bash
# Resize large images before upload
ffmpeg -y -i input_4k.png -vf "scale=1920:1080" output_1080.jpg
```

### Face Consistency
- Avoid prompts where the character **looks down** — breaks face consistency
- Keep head level and gaze forward throughout
- Place objects already in frame instead of having character reach below frame

### Last Frame
- LTX does **not** support first+last frame natively
- Workaround: generate clip A, generate clip B, then use `/v1/extend` to chain them

---

## Prompting Guide (LTX-2.3)

LTX-2.3 has a much stronger text connector. **Specificity wins.**

### 1. Use Verbs, Not Nouns
❌ `"A dramatic portrait of a man standing"`  
✅ `"A man stands on a rooftop. His coat flaps in the wind. He adjusts his collar and steps forward as the camera tracks right."`

### 2. Block the Scene Like a Director
- Specify **left vs right**, **foreground vs background**
- Describe **who moves**, **what moves**, **how they move**, **what the camera does**
- Spatial relationships are now respected

### 3. Describe Audio Explicitly (for text-to-video)
- Name the type of sound: dialogue, ambient, music
- Specify tone and intensity
- Example: `"His voice is clear and warm. Restaurant ambient sound softly in the background."`

### 4. Avoid Static Photo-Like Prompts
- If the prompt reads like a still image → the output behaves like one
- Add wind, motion, breathing, gestures, camera movement

### 5. Describe Texture and Material
- Hair, fabric, surface finish, lighting fall-off
- `"Individual hair strands visible in the backlight"` → now renders correctly

### 6. Portrait (9:16) Native
- `resolution: "1080x1920"` → trained on vertical data
- Frame for vertical intentionally, don't treat as cropped landscape

### 7. Complex Shots Work Now
- Layer multiple actions: `"He picks up the banana, raises it to his ear, and smirks"`
- Combine character performance + environment + camera motion

### Lip-Sync Prompt Template
```
A [description of person] sits/stands [location]. He/she speaks directly 
to camera, lips moving in perfect sync with his/her voice. [Gesture details]. 
Head stays level and gaze remains locked on camera throughout. 
[Environment description softly blurred in background]. 
[Lighting]. [Camera: holds steady at eye level, front-on].
```

---

## ComfyUI Node

Custom nodes for ComfyUI (no manual API calls):

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/PauldeLavallaz/comfyui-ltx-node
```

Nodes: `LTX Text to Video`, `LTX Image to Video`, `LTX Extend Video`  
Category: **LTX Video**

---

## API Key
Paul's key: stored in `~/clawd/.env` as `LTX_API_KEY`  
```
ltxv_RfSU5hdKJb_g5dwbECZWnilE1P8dJzbavz6niP_0LQJ942ARHIVhrBCfebcytEL1efLVx_63S_PJyWTzicrBcWEkOXfCbGTl8JSzlJJk329MwRViEgOoE2KnE9LIA5t6QSFeBy7DLnTIcX0AZNbV9Jv0TuC7qcq2gV33G6ROhUVUDCuN
```
