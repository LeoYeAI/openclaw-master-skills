---
name: ads-creatives
description: >
  AI-powered ad creative image generation using Google Gemini models. Generates
  creative proposals with visual layouts from product information, then produces
  ad images via Gemini image generation. Supports multiple aspect ratios
  (1:1, 9:16, 16:9, etc.). Requires a Google Gemini API key.
  Use when user says "generate ad", "create ad image", "ad creative generation",
  "creatives", "generate creatives", or "ad image".
allowed-tools:
  - Read
  - Bash
  - Glob
---

# AI Ad Creative Image Generation

Generate professional advertising images using Google Gemini models in a 2-step pipeline:
1. **Step 1** — Creative Proposals + Visual Layout (gemini-2.5-flash)
2. **Step 2** — Image Generation (gemini-3.1-flash-image-preview / Nano Banana 2)

## Process

### A. Data Collection

Ask the user for the following inputs:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `product_info` | Yes | Product description text |
| `generate_num` | Yes | Number of ad proposals to generate |
| `language` | Yes | Language for on-image text (default: English) |
| `audience_descriptions` | No | List of target audiences (as context) |
| `requirements` | No | Extra creative requirements (HIGHEST PRIORITY if provided) |
| `input_cta` | No | Specified CTA text (use exactly if provided) |
| `product_image_path` | No | Path to product reference image |
| `aspect_ratio` | No | Image aspect ratio (default: `1:1`). Supported: `1:1`, `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |

### B. Step 1 — Creative Proposals + Visual Layout

**Model:** `gemini-2.5-flash`

Generate N creative proposals with visual layouts in a single API call.

#### Prompt Template

If the user provides a product image, prepend the image block (lines marked with `[IF product_image]`) and include the reference image rules. Otherwise omit those lines.

```
[IF product_image] [Image 1 - Product Reference (preserve exact appearance)]

You are a senior advertising creative director and visual designer.
Generate {generate_num} distinct creative proposals with detailed visual layouts.

[IF product_image] **Reference Image Analysis:**
[IF product_image] - Extract the product’s appearance (shape, colors, packaging, and logo). Ignore any unrelated elements in the image.

**Product Description:**
{product_info}

**Target Audiences:**
{audience_descriptions}

**User Requirements (HIGHEST PRIORITY):**
{requirements}

**Task:**
Create {generate_num} creative proposals. If target audiences are provided, try to cover them while ensuring creative diversity.

For EACH proposal, provide:

1. **audience_name**: Short label (max 5 words) - e.g., "Busy Professionals", "Fitness Enthusiasts"

2. **overlay_text**: Minimal on-image text (max 6 words, can be empty string "")

3. **suggested_cta**: Use "{input_cta}" EXACTLY (or generate appropriate CTA if needed when not provided)

4. **visual_layout**: Detailed visual layout description (200-300 words) with this structure:
   - Creative Concept: [Core idea, storytelling approach, emotional appeal, how it connects product benefits to audience needs]
   - Scene: [Advertising scene - environment, setting, mood, composition]
   - Content: [Product placement, visual elements, props, focal points]
   - Text Elements: [Overlay text placement + CTA placement + optionally 1-2 key selling points if appropriate (keep all text minimal)]
   - Style: [Lighting, color palette, visual atmosphere]
[IF product_image]    Note: PRESERVE exact product appearance from reference image in Content

**Scene Diversity Guidelines:**
- Vary creative angles across all {generate_num} proposals
- Mix product-focused (studio-style) and contextual (real-world usage)
- Avoid device screens unless product IS digital/software

**Critical Rules:**
- Each proposal must have DIFFERENT creative angle
[IF product_image] - visual_layout MUST preserve exact product appearance from reference image

Return ONLY valid JSON array of objects.
```

#### API Call (Step 1)

**Text-only (no product image):**

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"text": "<PROMPT_TEXT_HERE>"}
      ]
    }]
  }'
```

**With product image (multimodal):**

First convert image to base64:
```bash
IMAGE_BASE64=$(base64 -i "${product_image_path}")
MIME_TYPE="image/png"  # or image/jpeg based on file extension
```

Then include in API call:
```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"inline_data": {"mime_type": "'"${MIME_TYPE}"'", "data": "'"${IMAGE_BASE64}"'"}},
        {"text": "<PROMPT_TEXT_HERE>"}
      ]
    }]
  }'
```

#### JSON Parsing Note

**Parser priority:** Try `python3` first, fall back to `jq` if python3 is unavailable.

Detect available parser at the start:
```bash
if command -v python3 &>/dev/null; then
  JSON_PARSER="python3"
elif command -v jq &>/dev/null; then
  JSON_PARSER="jq"
else
  echo "Error: Neither python3 nor jq is installed. Please install one of them."
  exit 1
fi
```

All response parsing below shows **both** variants. Use whichever `$JSON_PARSER` detected.

#### Response Parsing (Step 1)

The response JSON contains the generated text at `candidates[0].content.parts[0].text`.

**python3 variant:**
```bash
# Extract response text from API response
RESPONSE_TEXT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['candidates'][0]['content']['parts'][0]['text'])")

# Strip markdown code fences if present, then parse as JSON and save
echo "$RESPONSE_TEXT" | python3 -c "
import sys,json,re
text = sys.stdin.read().strip()
text = re.sub(r'^```json\s*', '', text)
text = re.sub(r'\s*```$', '', text)
proposals = json.loads(text)
print(json.dumps(proposals, indent=2))
" > creative-proposals.json

# Read back for iteration
PROPOSALS_JSON=$(cat creative-proposals.json)

# Get number of proposals
NUM_PROPOSALS=$(echo "$PROPOSALS_JSON" | python3 -c "import sys,json; print(len(json.loads(sys.stdin.read())))")

# Extract fields for proposal index $i (0-based):
VISUAL_LAYOUT=$(echo "$PROPOSALS_JSON" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())[$i]['visual_layout'])")
AUDIENCE_NAME=$(echo "$PROPOSALS_JSON" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())[$i]['audience_name'])")
```

**jq variant (fallback):**
```bash
# Extract response text from API response
RESPONSE_TEXT=$(echo "$RESPONSE" | jq -r '.candidates[0].content.parts[0].text')

# Strip markdown code fences if present, then parse as JSON and save
echo "$RESPONSE_TEXT" | sed 's/^```json[[:space:]]*//' | sed 's/[[:space:]]*```$//' | jq '.' > creative-proposals.json

# Read back for iteration
PROPOSALS_JSON=$(cat creative-proposals.json)

# Get number of proposals
NUM_PROPOSALS=$(echo "$PROPOSALS_JSON" | jq 'length')

# Extract fields for proposal index $i (0-based):
VISUAL_LAYOUT=$(echo "$PROPOSALS_JSON" | jq -r ".[$i].visual_layout")
AUDIENCE_NAME=$(echo "$PROPOSALS_JSON" | jq -r ".[$i].audience_name")
```

### C. Step 2 — Image Generation

**Model:** `gemini-3.1-flash-image-preview` (Nano Banana 2)

For each proposal from Step 1, generate an ad image using the `visual_layout`.

**Supported aspect ratios:** `1:1` (default), `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`
**Supported resolutions:** `512px`, `1K`, `2K`, `4K` (default)

#### Prompt Template

```
Generate a NEW {aspect_ratio} image: You are an expert advertising creative designer.

Create a professional advertising image.

**Reference Image Rules:**
- MUST Preserve EXACT product appearance from Product Reference (shape, colors, logo, packaging)
- Create an ORIGINAL ad scene, NOT a copy of reference

**Core Rules:**
1. TEXT - Include text as specified in Visual Layout. Keep text SHORT and CONCISE. Use LARGE, BOLD, high-contrast text
2. NATURAL LOOK - Realistic lighting, authentic expressions
3. CLEAN COMPOSITION - Clear focal point, balanced layout, 2-4 colors max
4. ASPECT RATIO - MUST be {aspect_ratio}
5. TEXT LANGUAGE - All on-image text (headlines, selling points, overlay text, CTA) MUST be written in {language}. Do NOT mix languages.

**Visual Layout:**
{visual_layout}

**Additional Requirements:**
{requirements}

Based on the above information, generate an advertising image that meets all requirements.

IMPORTANT: The output image MUST be {aspect_ratio}. Do not use any other aspect ratio.
```

#### API Call (Step 2)

**IMPORTANT:** Send all N image generation requests **in parallel** (concurrent Bash calls) to maximize speed. Do NOT wait for one image to finish before starting the next.

**Without product image:**
```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"text": "<PROMPT_TEXT_HERE>"}
      ]
    }],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {
        "aspectRatio": "'"${ASPECT_RATIO}"'"
      }
    }
  }'
```

**With product image (multimodal):**
```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"inline_data": {"mime_type": "'"${MIME_TYPE}"'", "data": "'"${IMAGE_BASE64}"'"}},
        {"text": "Product reference image (preserve exact appearance):\n\n<PROMPT_TEXT_HERE>"}
      ]
    }],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {
        "aspectRatio": "'"${ASPECT_RATIO}"'"
      }
    }
  }'
```

> **Important:** The `aspectRatio` MUST be inside `imageConfig`, not directly in `generationConfig`. Default is `1:1` if user does not specify.

#### Response Parsing (Step 2)

The image response contains base64 data in `inlineData`:

**python3 variant:**
```bash
# Extract base64 image data from response
IMAGE_DATA=$(echo "$RESPONSE" | python3 -c "
import sys,json
data = json.loads(sys.stdin.read())
for part in data['candidates'][0]['content']['parts']:
    if 'inlineData' in part:
        print(part['inlineData']['data'])
        break
")

# Decode and save as PNG
echo "$IMAGE_DATA" | base64 -d > "ad-${AUDIENCE_NAME_SLUG}-${i}.png"
```

**jq variant (fallback):**
```bash
# Extract base64 image data from response
IMAGE_DATA=$(echo "$RESPONSE" | jq -r '.candidates[0].content.parts[] | select(.inlineData) | .inlineData.data')

# Decode and save as PNG
echo "$IMAGE_DATA" | base64 -d > "ad-${AUDIENCE_NAME_SLUG}-${i}.png"
```

Create a filename-safe slug from audience_name:
```bash
AUDIENCE_NAME_SLUG=$(echo "$AUDIENCE_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')
```

### D. Error Handling

Check for API errors in the response:

**python3:**
```bash
echo "$RESPONSE" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); e=d.get('error',{}); print(e.get('message','')) if e else None"
```

**jq (fallback):**
```bash
echo "$RESPONSE" | jq -r '.error.message // empty'
```

- Common errors: invalid API key (401), quota exceeded (429), content filtered (400)
- If image generation fails for a proposal, log the error and continue with the next proposal

### E. Output

After all images are generated:

1. Save all proposals to `creative-proposals.json`
2. Save each generated image as `ad-{audience-slug}-{index}.png`
3. Present a summary to the user:
   - Number of proposals generated
   - Number of images successfully created
   - List of saved files with proposal details (audience, category, CTA)

## Data Flow

```
product_info + audiences + requirements + cta + product image (optional)
        |
        v
  gemini-2.5-flash: Step 1 --> N x Creative Proposal (with visual_layout)
        |
        v (for each proposal)
  gemini-3.1-flash-image-preview: Step 2 --> ad image (base64 --> PNG)
        |
        v
  Output: creative-proposals.json + ad-*.png files
```
