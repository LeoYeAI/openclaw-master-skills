# Programmatic 四格漫画 (4-Panel Comic Strip) Generation Research

> Research date: March 2026
> Purpose: Generate warm, illustrated 4-panel comic strips from memoir interview transcripts to surprise elderly narrators with visual summaries of their life stories.

---

## Table of Contents

1. [Image Generation APIs Comparison](#1-image-generation-apis-comparison)
2. [Multi-Panel Layout Approaches](#2-multi-panel-layout-approaches)
3. [Prompt Engineering for Consistent Comics](#3-prompt-engineering-for-consistent-comics)
4. [Local / Open-Source Options](#4-local--open-source-options)
5. [Cost Analysis](#5-cost-analysis)
6. [Recommendation](#6-recommendation)

---

## 1. Image Generation APIs Comparison

### OpenAI GPT-Image-1 / GPT-Image-1.5

| Attribute | Details |
|-----------|---------|
| **Models** | GPT-Image-1 (flagship), GPT-Image-1 Mini (budget), GPT-Image-1.5 (latest, Dec 2025) |
| **Pricing (per image)** | **GPT-Image-1**: ~$0.02 (low), ~$0.07 (medium), ~$0.19 (high) for 1024x1024. **GPT-Image-1 Mini**: ~$0.005-$0.052 depending on quality. |
| **Resolutions** | 1024x1024, 1024x1536, 1536x1024 |
| **Comic/illustration quality** | Strong. Can produce cartoon, watercolor, and illustrated styles with good prompt adherence. |
| **Multi-panel native** | No native 4-panel mode, but can generate a single image depicting 4 panels when prompted (inconsistent results). |
| **Chinese text rendering** | POOR. Known limitation acknowledged by OpenAI even in GPT-Image-1.5. Chinese, Arabic, and Hebrew text remain unreliable. |
| **API availability** | Excellent. Standard REST API, well-documented, widely supported. |
| **Verdict** | Best general-purpose option for English comics. Chinese text must be composited separately. |

### Google Imagen 3 / Imagen 4

| Attribute | Details |
|-----------|---------|
| **Models** | Imagen 3 ($0.03/image), Imagen 4 Fast ($0.02/image), Imagen 4 Ultra ($0.06/image) |
| **Comic/illustration quality** | Good range of styles: impressionistic, anime, abstract, hyperrealistic. |
| **Multi-panel native** | No dedicated multi-panel mode. |
| **Chinese text rendering** | Limited information; not a known strength. |
| **API availability** | Via Gemini API and Vertex AI. Straightforward access. |
| **Verdict** | Cost-effective, good quality, but no particular advantage for this use case. |

### Stability AI (Stable Diffusion API)

| Attribute | Details |
|-----------|---------|
| **Models** | Stable Image Ultra (8 credits), SD 3.5 Large (6.5 credits), SD 3.5 Large Turbo (4 credits). 1 credit = $0.01. |
| **Pricing (per image)** | $0.04-$0.08 per image depending on model. |
| **Comic/illustration quality** | Good with proper prompting. Strong community of fine-tuned models for illustration styles. |
| **Multi-panel native** | No. Must composite. |
| **Chinese text rendering** | Poor. Text rendering is a known weakness of Stable Diffusion models. |
| **API availability** | Credit-based REST API. 25 free credits for new users. |
| **Verdict** | Mid-tier option. Better suited as a local/open-source approach (see Section 4). |

### FLUX.1 Kontext (Black Forest Labs)

| Attribute | Details |
|-----------|---------|
| **Models** | Kontext Pro ($0.025-$0.04/image), Kontext Max ($0.05-$0.08/image) |
| **Providers** | fal.ai ($0.04 Pro), FluxAPI.ai ($0.025 Pro, $0.05 Max), Replicate, Together.ai |
| **Comic/illustration quality** | EXCELLENT. Best-in-class for character consistency across panels. Understands comic visual language: panel compositions, expressive poses, dynamic angles. |
| **Multi-panel native** | Not natively, but excels at maintaining character identity across separate generations using reference images. |
| **Chinese text rendering** | Limited. Text rendering improved with Kontext Max but primarily optimized for Latin scripts. |
| **Character consistency** | BEST AVAILABLE. Can process multiple reference images simultaneously. Identity embeddings maintain character fingerprints across generations. |
| **API availability** | Available via multiple providers (fal.ai, Replicate, FluxAPI.ai). |
| **Verdict** | TOP CHOICE for generating consistent characters across 4 separate panels, then compositing. |

### Qwen-Image / Qwen-Image-2.0 (Alibaba)

| Attribute | Details |
|-----------|---------|
| **Models** | Qwen-Image (20B MMDiT), Qwen-Image-2.0 (Feb 2026) |
| **Pricing** | ~$0.025/image (flat rate). Also available via Alibaba Cloud Model Studio. Chinese domestic pricing: ~0.06 RMB/image (~$0.008). |
| **Comic/illustration quality** | EXCELLENT for comics specifically. Qwen-Image-2.0 explicitly supports "consistent character designs across multi-grid comic layouts with dialogue precisely placed in speech bubbles." |
| **Multi-panel native** | YES. Can produce multi-grid comic layouts with dialogue in a single generation. |
| **Chinese text rendering** | BEST IN CLASS. Purpose-built for bilingual Chinese/English typography. Rivals GPT-4o for English text and surpasses all competitors for Chinese text rendering. |
| **Character consistency** | Good within a single multi-panel generation. |
| **API availability** | Via Alibaba Cloud Model Studio / Qwen API platform. Also available through third-party providers. |
| **Verdict** | STRONGEST OPTION for this specific use case. Native multi-panel comic layout + best Chinese text rendering + affordable pricing. |

### ByteDance Seedream 5.0 (Doubao/Jimeng/即梦)

| Attribute | Details |
|-----------|---------|
| **Models** | Seedream 5.0 Lite ($0.035/image), Seedream 4.5 |
| **Comic/illustration quality** | Good general image quality. Not specifically optimized for comics. |
| **Multi-panel native** | No specific multi-panel mode documented. |
| **Chinese text rendering** | Likely decent (Chinese company), but not prominently marketed as a feature. |
| **API availability** | Via Volcengine API, APIYI, and MCP integration available. |
| **Verdict** | Viable budget option but Qwen-Image is stronger for this use case. |

### Midjourney

| Attribute | Details |
|-----------|---------|
| **API availability** | NO public API. Enterprise-only API keys (must apply). Unofficial third-party APIs exist but violate ToS and risk account bans. |
| **Verdict** | NOT RECOMMENDED for programmatic use. No reliable API access. |

---

## 2. Multi-Panel Layout Approaches

### Approach A: Single-Image Generation (Native Multi-Panel)

**Best model: Qwen-Image-2.0**

Qwen-Image-2.0 can generate a complete multi-grid comic layout in a single API call, including:
- 4-panel layout with borders
- Consistent characters across panels
- Dialogue in speech bubbles with accurate Chinese typography
- Story progression across panels

**Pros:**
- Simplest workflow (one API call)
- Built-in character consistency within the generation
- Native Chinese text support

**Cons:**
- Less control over individual panel composition
- Single model dependency
- May need iteration to get the exact layout desired

### Approach B: Generate 4 Panels Separately + Composite

**Best model: FLUX.1 Kontext Pro/Max**

Generate each panel individually using reference images for character consistency, then composite into a single image.

**Workflow:**
1. Generate Panel 1 with detailed character/scene description
2. Use Panel 1 output as reference image for Panels 2-4 (FLUX Kontext's strength)
3. Composite 4 images into a 2x2 or 1x4 grid
4. Overlay text captions/dialogue using Pillow

**Pros:**
- Maximum control over each panel
- Best character consistency (FLUX Kontext)
- Can mix and match: regenerate individual panels
- Full control over text placement and fonts

**Cons:**
- 4x API cost
- More complex pipeline
- Compositing code required

### Approach C: Hybrid (Generate panels, overlay text separately)

Generate the visual panels using any image model, then add Chinese text/captions programmatically. This is the RECOMMENDED approach because:
- No AI model reliably renders Chinese text in images
- Programmatic text gives perfect typography control
- Font choice, size, and placement are fully customizable

### Compositing Tools

**Python Pillow (PIL) -- RECOMMENDED:**
```python
from PIL import Image, ImageDraw, ImageFont

# Create canvas for 2x2 grid
canvas = Image.new('RGB', (1080, 1080), 'white')

# Paste 4 panels (each 520x520 with 20px margins)
panel_size = (520, 520)
positions = [(20, 20), (560, 20), (20, 560), (560, 560)]
for img, pos in zip(panels, positions):
    canvas.paste(img.resize(panel_size), pos)

# Add Chinese text with a CJK font
font = ImageFont.truetype('NotoSansCJK-Regular.ttc', 24)
draw = ImageDraw.Draw(canvas)
draw.text((x, y), "第一格：小时候的回忆", font=font, fill='black')

canvas.save('comic.jpg', quality=85)  # WhatsApp-friendly
```

**Key considerations for Chinese text:**
- Use a CJK-compatible font: Noto Sans CJK, Source Han Sans, SimSun, Microsoft YaHei
- Pillow's `ImageDraw.text()` supports CJK characters natively with proper font
- For speech bubbles: draw ellipse/rounded rect first, then overlay text
- For vertical text (traditional manga style): render character by character

**ImageMagick (alternative):**
- `montage` command for grid layouts
- `convert -annotate` for text overlay
- Good for CLI/shell-based pipelines

**HTML/CSS Canvas (alternative):**
- Use Puppeteer/Playwright to render HTML comic template to image
- Full CSS control over layout, fonts, text wrapping
- More complex but most flexible for sophisticated layouts

---

## 3. Prompt Engineering for Consistent 4-Panel Comics

### Style Keywords for Warm, Memoir-Appropriate Illustrations

```
Primary style descriptors:
- "warm watercolor illustration"
- "soft pastel colors, gentle lighting"
- "Studio Ghibli inspired, hand-painted feel"
- "children's book illustration style"
- "cozy nostalgic illustration, warm tones"
- "gentle ink and wash painting, 水墨淡彩"

Avoid:
- "photorealistic", "hyperrealistic", "cinematic"
- "dark", "dramatic", "horror"
- "3D render", "CGI"
```

### Character Consistency Techniques

**1. Detailed Character Description (Forensic-Level):**
```
"An elderly Chinese grandmother, 75 years old, with short silver-grey
permed hair, round face with warm smile lines, wearing a burgundy
mandarin-collar blouse (旗袍领), gold-rimmed round glasses, small gold
earrings. Gentle, warm expression."
```

**2. Reference Image Approach (FLUX Kontext):**
- Generate one "character sheet" image first
- Use it as reference for all subsequent panel generations
- FLUX Kontext processes reference images to maintain identity embeddings

**3. LoRA Fine-Tuning (Local Models):**
- Train a LoRA on 20-50 images of a consistent character design
- Apply the LoRA when generating each panel
- Most reliable for local/open-source pipelines

### Panel-Specific Prompting (Yonkoma Structure)

The classic 四格漫画 structure follows 起承転結 (ki-sho-ten-ketsu):

| Panel | Japanese | Chinese | Purpose | Prompt Focus |
|-------|----------|---------|---------|-------------|
| 1 | 起 (ki) | 起 | Introduction | Wide/establishing shot, introduce character and setting |
| 2 | 承 (sho) | 承 | Development | Medium shot, show the situation developing |
| 3 | 転 (ten) | 转 | Twist/Turn | Close-up or different angle, the key moment |
| 4 | 結 (ketsu) | 结 | Conclusion | Emotional resolution, the punchline or heartwarming ending |

**Example prompt sequence for a memoir story:**
```
Panel 1: "Warm watercolor illustration of an elderly Chinese grandmother
sitting in a cozy kitchen, telling a story to her grandchild. Soft
morning light through the window. Nostalgic, gentle mood."

Panel 2: "Same grandmother as a young woman in the 1960s, riding a
bicycle through a village road lined with poplar trees. Warm sepia-toned
watercolor style. Joyful expression."

Panel 3: "The young woman meeting a young man at a village market,
both shy and smiling. Cherry blossoms falling. Warm watercolor,
romantic gentle atmosphere."

Panel 4: "Back to present day, the grandmother smiling warmly, holding
an old photograph. Her grandchild hugging her. Golden afternoon light.
Warm, emotional watercolor illustration."
```

---

## 4. Local / Open-Source Options

### FLUX.1 (Open-Weight Models)

- **FLUX.1 Schnell**: Fastest, open-source, good quality. Best for rapid iteration.
- **FLUX.1 Dev**: Higher quality, non-commercial license.
- **Hardware requirements**: 12GB+ VRAM (RTX 3060 minimum, RTX 4090 ideal)
- **Character consistency**: Use FLUX Kontext techniques locally via ComfyUI

### Stable Diffusion XL + ControlNet

**Pipeline:**
1. Use a comic panel template as ControlNet input (line art or segmentation map)
2. Generate each panel with SDXL + illustration-focused LoRA
3. ControlNet ensures consistent composition/layout

**Recommended LoRAs for illustration style:**
- Ghibli-style LoRAs (widely available on CivitAI)
- Watercolor illustration LoRAs
- Children's book illustration LoRAs

### ComfyUI Comic Workflows

**CR Comic Panel Templates Node:**
- Part of ComfyUI_Comfyroll_CustomNodes
- Creates customizable comic page layouts with panel templates
- Handles panel borders, spacing, and arrangement
- Can be combined with any image generation model

**StoryDiffusion Comic_Type Node:**
- Transforms images into comic-style visuals
- Overlays text prompts with specific comic styles
- Designed for narrative-driven comic panels

**Recommended ComfyUI Workflow:**
1. CR Comic Panel Templates (define 2x2 layout)
2. FLUX.1 Schnell or SDXL for each panel
3. Character consistency via reference image or LoRA
4. Composite panels into template
5. Export as single image

### Qwen-Image (Open-Source 20B Model)

- Available on HuggingFace: `Qwen/Qwen-Image`
- 20B parameter MMDiT model
- Best open-source option for Chinese text rendering
- Hardware requirements: Significant (likely 40GB+ VRAM for full model, quantized versions may work on 24GB)

### Hardware Requirements Summary

| Model | Min VRAM | Recommended | Notes |
|-------|----------|-------------|-------|
| FLUX.1 Schnell | 12GB | 24GB | Fast, good quality |
| SDXL + ControlNet | 8GB | 12GB | More mature ecosystem |
| Qwen-Image 20B | 24GB (quantized) | 40GB+ | Best for Chinese text |

---

## 5. Cost Analysis

### Per Comic Strip (4 Panels) -- API-Based

| Approach | Model | Cost per Comic | Notes |
|----------|-------|----------------|-------|
| **Single generation** | Qwen-Image-2.0 | ~$0.025 | One image, native multi-panel |
| **Single generation** | Qwen-Image (China pricing) | ~0.06 RMB (~$0.008) | Cheapest option via Alibaba China |
| **4 separate panels** | GPT-Image-1 Mini (low) | ~$0.02-0.04 | Budget OpenAI option |
| **4 separate panels** | GPT-Image-1 Mini (medium) | ~$0.16 | Good quality/cost balance |
| **4 separate panels** | GPT-Image-1 (medium) | ~$0.28 | Higher quality |
| **4 separate panels** | GPT-Image-1 (high) | ~$0.76 | Premium quality |
| **4 separate panels** | FLUX Kontext Pro (fal.ai) | ~$0.16 | Best character consistency |
| **4 separate panels** | FLUX Kontext Pro (FluxAPI) | ~$0.10 | Cheaper provider |
| **4 separate panels** | Imagen 4 Fast | ~$0.08 | Budget Google option |
| **4 separate panels** | Imagen 3 | ~$0.12 | Standard Google |
| **4 separate panels** | Seedream 5.0 Lite | ~$0.14 | ByteDance option |
| **4 separate panels** | Stability SD 3.5 Turbo | ~$0.16 | Stability API |

### Additional Costs

- **LLM call to convert story to panel prompts**: ~$0.01-0.05 (using GPT-4o-mini or similar)
- **Compositing**: Free (Pillow, local processing)
- **Font rendering**: Free (open-source CJK fonts)
- **Total per comic (recommended approach)**: ~$0.03-0.10

### Volume Estimates

| Volume | Qwen Single-Gen | FLUX 4-Panel | GPT-Image-1 Mini |
|--------|-----------------|--------------|-------------------|
| 100 comics/month | $2.50 | $10-16 | $4-16 |
| 1,000 comics/month | $25 | $100-160 | $40-160 |
| 10,000 comics/month | $250 | $1,000-1,600 | $400-1,600 |

---

## 6. Recommendation

### Best API-Based Approach (Easiest + Best Quality for This Use Case)

**PRIMARY: Qwen-Image-2.0 via Alibaba Cloud Model Studio**

Rationale:
- Only model with native multi-panel comic layout support
- Best-in-class Chinese text rendering (critical for 四格漫画 with Chinese dialogue)
- Cheapest per comic (~$0.025 international, ~$0.008 via China pricing)
- Single API call produces complete comic strip
- Explicitly designed for "consistent character designs across multi-grid comic layouts"

**FALLBACK: FLUX Kontext Pro (4 panels) + Pillow compositing**

Rationale:
- Best character consistency across separate panels
- More control over individual panel composition
- Add Chinese text via Pillow with CJK fonts (bypass AI text rendering limitations)
- Cost: ~$0.10-0.16 per comic

### Best Local Approach (Cheapest + Privacy-Friendly)

**FLUX.1 Schnell + ComfyUI CR Comic Panel Templates**

- Free after hardware cost
- Good illustration quality with proper LoRAs
- Character consistency via reference images
- Add Chinese text via Pillow post-processing
- Requires: GPU with 12GB+ VRAM

### Recommended End-to-End Workflow

```
Story Text (from interview)
    |
    v
[Step 1: LLM - Story to Panel Descriptions]
    Use GPT-4o-mini or Claude to:
    - Extract 4 key moments following 起承转结 structure
    - Generate detailed visual descriptions for each panel
    - Generate caption/dialogue text for each panel
    - Include consistent character description across all panels
    |
    v
[Step 2: Image Generation]
    Option A (Recommended): Qwen-Image-2.0 single call
        - Include full 4-panel comic layout instruction in prompt
        - Include dialogue text in Chinese
        - One API call, one output image

    Option B (Higher quality control): FLUX Kontext Pro x4
        - Generate Panel 1 with full character description
        - Use Panel 1 as reference for Panels 2-4
        - 4 API calls via fal.ai or FluxAPI.ai
    |
    v
[Step 3: Compositing & Text (if Option B)]
    Using Python Pillow:
    - Arrange 4 panels in 2x2 grid (1080x1080 for WhatsApp)
    - Add panel borders (2-3px, soft grey)
    - Add caption text using Noto Sans CJK font
    - Optional: Add speech bubbles with dialogue
    - Add subtle title/date at top
    |
    v
[Step 4: Export]
    - Save as JPEG, quality=85 (WhatsApp-optimized)
    - Target file size: 200-500KB
    - Resolution: 1080x1080 (square, displays well on mobile)
    |
    v
[Step 5: Deliver]
    - Send via WhatsApp API as single image
```

### Quick-Start Implementation Plan

1. **Phase 1 (MVP)**: Use Qwen-Image-2.0 API for single-call comic generation. Fastest to implement, cheapest, best Chinese text support.

2. **Phase 2 (Quality upgrade)**: If Qwen quality is insufficient, switch to FLUX Kontext Pro (4 panels) + Pillow compositing with CJK font overlay.

3. **Phase 3 (Scale optimization)**: If volume grows significantly, explore local FLUX.1 Schnell deployment to eliminate per-image API costs.

### Key Technical Notes

- **WhatsApp image limits**: Max 16MB, but aim for 200-500KB JPEG for fast loading on mobile
- **Square format (1080x1080)**: Displays best in WhatsApp chat without cropping
- **CJK fonts**: Use Google Noto Sans CJK (free, open-source, excellent coverage for Simplified/Traditional Chinese)
- **Speech bubbles**: Draw with Pillow `ImageDraw.rounded_rectangle()` or `ellipse()`, then overlay text
- **Vertical vs horizontal panels**: 2x2 grid recommended for WhatsApp (square); traditional yonkoma is vertical 1x4 but too tall for mobile viewing

---

## Sources

- [OpenAI Image Generation Pricing](https://openai.com/api/pricing/)
- [OpenAI GPT-Image-1 Model Documentation](https://platform.openai.com/docs/models/gpt-image-1)
- [GPT-Image-1 Mini Pricing Guide](https://www.eesel.ai/blog/gpt-image-1-mini-pricing)
- [Google Imagen 3 API Launch](https://news.aibase.com/news/15170)
- [Stability AI API Pricing](https://platform.stability.ai/pricing)
- [FLUX API Pricing (Black Forest Labs)](https://bfl.ai/pricing)
- [FLUX.1 Kontext on fal.ai](https://fal.ai/models/fal-ai/flux-pro/kontext)
- [FLUX.1 Kontext on Together.ai](https://www.together.ai/blog/flux-1-kontext)
- [Qwen-Image on GitHub](https://github.com/QwenLM/Qwen-Image)
- [Qwen-Image-2.0 Benchmarks](https://automatio.ai/models/qwen-image-2-0)
- [Qwen Image Pricing](https://www.qwenimagen.com/price)
- [通义万相 API Documentation](https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference)
- [Seedream 5.0 Lite API Guide](https://help.apiyi.com/en/seedream-5-0-lite-api-guide-cheaper-than-4-5-en.html)
- [Best Open Source Models for Comics and Manga 2026](https://www.siliconflow.com/articles/en/best-open-source-models-for-comics-and-manga)
- [Building an AI Comic Strip Generator with FLUX](https://www.mindstudio.ai/blog/build-ai-comic-strip-generator-flux-veo-3)
- [CR Comic Panel Templates (ComfyUI)](https://comfyai.run/documentation/CR%20Comic%20Panel%20Templates)
- [FLUX.1 for Comics Guide](https://skywork.ai/blog/flux-1-for-comics-my-no-bs-guide-to-turning-ai-hype-into-real-projects/)
- [Midjourney API Status](https://www.myarchitectai.com/blog/midjourney-apis)
- [AI Image Pricing Comparison 2026](https://intuitionlabs.ai/articles/ai-image-generation-pricing-google-openai)
- [Pillow ImageDraw Documentation](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html)
