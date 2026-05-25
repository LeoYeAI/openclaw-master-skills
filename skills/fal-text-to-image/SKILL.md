---
name: fal-text-to-image
description: Generate, remix, and edit images using fal.ai's AI models. Supports text-to-image generation, image-to-image remixing, and targeted inpainting/editing.
---

# fal.ai Image Generation & Editing Skill

Professional AI-powered image workflows using fal.ai's state-of-the-art models including FLUX, Recraft V3, Imagen4, and more.

## Three Modes of Operation

### 1. Text-to-Image (fal-text-to-image)
Generate images from scratch using text prompts

### 2. Image Remix (fal-image-remix)
Transform existing images while preserving composition

### 3. Image Edit (fal-image-edit)
Targeted inpainting and masked editing

## When to Use This Skill

Trigger when user:
- Requests image generation from text descriptions
- Wants to transform/remix existing images with AI
- Needs to edit specific regions of images (inpainting)
- Wants to create images with specific styles (vector, realistic, typography)
- Needs high-resolution professional images (up to 2K)
- Wants to use a reference image for style transfer
- Mentions specific models like FLUX, Recraft, or Imagen
- Asks for logo, poster, or brand-style image generation
- Needs object removal or targeted modifications

## Quick Start

### Text-to-Image: Generate from Scratch
```bash
# Basic generation
uv run python fal-text-to-image "A cyberpunk city at sunset with neon lights"

# With specific model
uv run python fal-text-to-image -m flux-pro/v1.1-ultra "Professional headshot"

# With style reference
uv run python fal-text-to-image -i reference.jpg "Mountain landscape" -m flux-2/lora/edit
```

### Image Remix: Transform Existing Images
```bash
# Transform style while preserving composition
uv run python fal-image-remix input.jpg "Transform into oil painting"

# With strength control (0.0=original, 1.0=full transformation)
uv run python fal-image-remix photo.jpg "Anime style character" --strength 0.6

# Premium quality remix
uv run python fal-image-remix -m flux-1.1-pro image.jpg "Professional portrait"
```

### Image Edit: Targeted Modifications
```bash
# Edit with mask image (white=edit area, black=preserve)
uv run python fal-image-edit input.jpg mask.png "Replace with flowers"

# Auto-generate mask from text
uv run python fal-image-edit input.jpg --mask-prompt "sky" "Make it sunset"

# Remove objects
uv run python fal-image-edit photo.jpg mask.png "Remove object" --strength 1.0

# General editing (no mask)
uv run python fal-image-edit photo.jpg "Enhance lighting and colors"
```

## Model Selection Guide

The script intelligently selects the best model based on task context:

### **flux-pro/v1.1-ultra** (Default for High-Res)
- **Best for**: Professional photography, high-resolution outputs (up to 2K)
- **Strengths**: Photo realism, professional quality
- **Use when**: User needs publication-ready images
- **Endpoint**: `fal-ai/flux-pro/v1.1-ultra`

### **recraft/v3/text-to-image** (SOTA Quality)
- **Best for**: Typography, vector art, brand-style images, long text
- **Strengths**: Industry-leading benchmark scores, precise text rendering
- **Use when**: Creating logos, posters, or text-heavy designs
- **Endpoint**: `fal-ai/recraft/v3/text-to-image`

### **flux-2** (Best Balance)
- **Best for**: General-purpose image generation
- **Strengths**: Enhanced realism, crisp text, native editing
- **Use when**: Standard image generation needs
- **Endpoint**: `fal-ai/flux-2`

### **flux-2/lora** (Custom Styles)
- **Best for**: Domain-specific styles, fine-tuned variations
- **Strengths**: Custom style adaptation
- **Use when**: User wants specific artistic styles
- **Endpoint**: `fal-ai/flux-2/lora`

### **flux-2/lora/edit** (Style Transfer)
- **Best for**: Image-to-image editing with style references
- **Strengths**: Specialized style transfer
- **Use when**: User provides reference image with `-i` flag
- **Endpoint**: `fal-ai/flux-2/lora/edit`

### **imagen4/preview** (Google Quality)
- **Best for**: High-quality general images
- **Strengths**: Google's highest quality model
- **Use when**: User specifically requests Imagen or Google models
- **Endpoint**: `fal-ai/imagen4/preview`

### **stable-diffusion-v35-large** (Typography & Style)
- **Best for**: Complex prompts, typography, style control
- **Strengths**: Advanced prompt understanding, resource efficiency
- **Use when**: Complex multi-element compositions
- **Endpoint**: `fal-ai/stable-diffusion-v35-large`

### **ideogram/v2** (Typography Specialist)
- **Best for**: Posters, logos, text-heavy designs
- **Strengths**: Exceptional typography, realistic outputs
- **Use when**: Text accuracy is critical
- **Endpoint**: `fal-ai/ideogram/v2`

### **bria/text-to-image/3.2** (Commercial Safe)
- **Best for**: Commercial projects requiring licensed training data
- **Strengths**: Safe for commercial use, excellent text rendering
- **Use when**: Legal/licensing concerns matter
- **Endpoint**: `fal-ai/bria/text-to-image/3.2`

## Command-Line Interface

```bash
uv run python fal-text-to-image [OPTIONS] PROMPT

Arguments:
  PROMPT                    Text description of the image to generate

Options:
  -m, --model TEXT         Model to use (see model list above)
  -i, --image TEXT         Path or URL to reference image for style transfer
  -o, --output TEXT        Output filename (default: generated_image.png)
  -s, --size TEXT          Image size (e.g., "1024x1024", "landscape_16_9")
  --seed INTEGER           Random seed for reproducibility
  --steps INTEGER          Number of inference steps (model-dependent)
  --guidance FLOAT         Guidance scale (higher = more prompt adherence)
  --help                   Show this message and exit
```

## Authentication Setup

Before first use, set your fal.ai API key:

```bash
export FAL_KEY="your-api-key-here"
```

Or create a `.env` file in the skill directory:
```env
FAL_KEY=your-api-key-here
```

Get your API key from: https://fal.ai/dashboard/keys

## Advanced Examples

### High-Resolution Professional Photo
```bash
uv run python fal-text-to-image \
  -m flux-pro/v1.1-ultra \
  "Professional headshot of a business executive in modern office" \
  -s 2048x2048
```

### Logo/Typography Design
```bash
uv run python fal-text-to-image \
  -m recraft/v3/text-to-image \
  "Modern tech startup logo with text 'AI Labs' in minimalist style"
```

### Style Transfer from Reference
```bash
uv run python fal-text-to-image \
  -m flux-2/lora/edit \
  -i artistic_style.jpg \
  "Portrait of a woman in a garden"
```

### Reproducible Generation
```bash
uv run python fal-text-to-image \
  -m flux-2 \
  --seed 42 \
  "Futuristic cityscape with flying cars"
```

## Model Selection Logic

The script automatically selects the best model when `-m` is not specified:

1. **If `-i` provided**: Uses `flux-2/lora/edit` for style transfer
2. **If prompt contains typography keywords** (logo, text, poster, sign): Uses `recraft/v3/text-to-image`
3. **If prompt suggests high-res needs** (professional, portrait, headshot): Uses `flux-pro/v1.1-ultra`
4. **If prompt mentions vector/brand**: Uses `recraft/v3/text-to-image`
5. **Default**: Uses `flux-2` for general purpose

## Output Format

Generated images are saved with metadata:
- Filename includes timestamp and model name
- EXIF data stores prompt, model, and parameters
- Console displays generation time and cost estimate

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `FAL_KEY not set` | Export FAL_KEY environment variable or create .env file |
| `Model not found` | Check model name against supported list |
| `Image reference fails` | Ensure image path/URL is accessible |
| `Generation timeout` | Some models take longer; wait or try faster model |
| `Rate limit error` | Check fal.ai dashboard for usage limits |

## Cost Optimization

- **Free tier**: FLUX.2 offers 100 free requests (expires Dec 25, 2025)
- **Pay per use**: FLUX Pro charges per megapixel
- **Budget option**: Use `flux-2` or `stable-diffusion-v35-large` for general use
- **Premium**: Use `flux-pro/v1.1-ultra` only when high-res is required

## Image Remix: Model Selection Guide

Available models for image-to-image remixing:

### **flux-2/dev** (Default, Free)
- **Best for**: General remixing, style transfer, fast iteration
- **Strengths**: Balanced quality/speed, 100 free requests
- **Use when**: Standard remixing needs
- **Endpoint**: `fal-ai/flux/dev/image-to-image`

### **flux-pro** (Premium Quality)
- **Best for**: Professional remixing, high-quality outputs
- **Strengths**: Superior quality, realistic transformations
- **Use when**: Professional or publication-ready remixes
- **Endpoint**: `fal-ai/flux-pro`

### **flux-1.1-pro** (Ultra Premium)
- **Best for**: Highest quality remixing with maximum detail
- **Strengths**: Ultra-high quality, exceptional detail preservation
- **Use when**: Premium projects requiring best possible output
- **Endpoint**: `fal-ai/flux-pro/v1.1`

### **recraft/v3** (Vector/Illustration)
- **Best for**: Vector style, brand imagery, illustration remixing
- **Strengths**: Clean vector outputs, brand-style transformations
- **Use when**: Converting to illustration or vector style
- **Endpoint**: `fal-ai/recraft/v3/text-to-image`

### **stable-diffusion-v35** (Artistic)
- **Best for**: Artistic styles, painting effects, creative remixing
- **Strengths**: Strong artistic style application
- **Use when**: Artistic or stylized transformations
- **Endpoint**: `fal-ai/stable-diffusion-v35-large`

## Image Remix: Command-Line Interface

```bash
uv run python fal-image-remix [OPTIONS] INPUT_IMAGE PROMPT

Arguments:
  INPUT_IMAGE               Path or URL to source image
  PROMPT                    How to transform the image

Options:
  -m, --model TEXT         Model to use (auto-selected if not specified)
  -o, --output TEXT        Output filename (default: remixed_TIMESTAMP.png)
  -s, --strength FLOAT     Transformation strength 0.0-1.0 (default: 0.75)
                           0.0 = preserve original, 1.0 = full transformation
  --guidance FLOAT         Guidance scale (default: 7.5)
  --seed INTEGER           Random seed for reproducibility
  --steps INTEGER          Number of inference steps
  --help                   Show help
```

### Remix Strength Guide

The `--strength` parameter controls transformation intensity:

| Strength | Effect | Use Case |
|----------|--------|----------|
| 0.3-0.5 | Subtle changes | Minor color adjustments, lighting tweaks |
| 0.5-0.7 | Moderate changes | Style hints while preserving details |
| 0.7-0.85 | Strong changes | Clear style transfer, significant transformation |
| 0.85-1.0 | Maximum changes | Complete style overhaul, dramatic transformation |

### Remix Examples

```bash
# Subtle artistic style (low strength)
uv run python fal-image-remix photo.jpg "Oil painting style" --strength 0.4

# Balanced transformation (default)
uv run python fal-image-remix input.jpg "Cyberpunk neon aesthetic"

# Strong transformation (high strength)
uv run python fal-image-remix portrait.jpg "Anime character" --strength 0.9

# Vector conversion
uv run python fal-image-remix -m recraft/v3 logo.png "Clean vector illustration"

# Premium quality remix
uv run python fal-image-remix -m flux-1.1-pro photo.jpg "Professional studio portrait"
```

## Image Edit: Model Selection Guide

Available models for targeted editing and inpainting:

### **flux-2/redux** (General Editing)
- **Best for**: General image editing without masks
- **Strengths**: Fast, balanced, good for overall adjustments
- **Use when**: No specific region targeting needed
- **Endpoint**: `fal-ai/flux-2/redux`

### **flux-2/fill** (Inpainting, Default)
- **Best for**: Masked region editing, object removal, filling
- **Strengths**: Seamless inpainting, natural blending
- **Use when**: Editing specific masked regions
- **Endpoint**: `fal-ai/flux-2/fill`

### **flux-pro-v11/fill** (Premium Inpainting)
- **Best for**: Professional inpainting with highest quality
- **Strengths**: Superior quality, professional results
- **Use when**: Premium quality inpainting required
- **Endpoint**: `fal-ai/flux-pro-v11/fill`

### **stable-diffusion-v35/inpainting** (Artistic Inpainting)
- **Best for**: Artistic edits, creative inpainting
- **Strengths**: Strong artistic control, detailed generation
- **Use when**: Artistic or stylized edits
- **Endpoint**: `fal-ai/stable-diffusion-v35-large/inpainting`

### **ideogram/v2/edit** (Realistic Editing)
- **Best for**: Realistic modifications, precise edits
- **Strengths**: High realism, precise control
- **Use when**: Realistic edits required
- **Endpoint**: `fal-ai/ideogram/v2/edit`

### **recraft/v3/svg** (Vector Editing)
- **Best for**: Vector style edits, clean illustrations
- **Strengths**: Clean vector outputs, illustration style
- **Use when**: Vector or illustration edits
- **Endpoint**: `fal-ai/recraft/v3/svg`

## Image Edit: Command-Line Interface

```bash
uv run python fal-image-edit [OPTIONS] INPUT_IMAGE [MASK_IMAGE] PROMPT

Arguments:
  INPUT_IMAGE               Path or URL to source image
  MASK_IMAGE                Path or URL to mask (white=edit, black=preserve) [optional]
  PROMPT                    How to edit the masked region

Options:
  -m, --model TEXT         Model to use (auto-selected if not specified)
  -o, --output TEXT        Output filename (default: edited_TIMESTAMP.png)
  --mask-prompt TEXT       Generate mask from text (no mask image needed)
  -s, --strength FLOAT     Edit strength 0.0-1.0 (default: 0.95)
  --guidance FLOAT         Guidance scale (default: 7.5)
  --seed INTEGER           Random seed for reproducibility
  --steps INTEGER          Number of inference steps
  --help                   Show help
```

### Edit Strength Guide

The `--strength` parameter controls edit intensity:

| Strength | Effect | Use Case |
|----------|--------|----------|
| 0.5-0.7 | Subtle edits | Minor touch-ups, color adjustments |
| 0.7-0.9 | Moderate edits | Clear modifications while blending naturally |
| 0.9-1.0 | Strong edits | Complete replacement, object removal |

### Creating Mask Images

Mask images define edit regions:
- **White (255)**: Areas to edit/modify
- **Black (0)**: Areas to preserve unchanged
- **Gray**: Partial blending (proportional to brightness)

Create masks using:
- Image editors (GIMP, Photoshop, Krita)
- Paint tools (select and fill with white/black)
- Text-based prompts (`--mask-prompt` flag)

### Edit Examples

```bash
# Edit with mask image
uv run python fal-image-edit photo.jpg mask.png "Replace with beautiful garden"

# Auto-generate mask from text
uv run python fal-image-edit landscape.jpg --mask-prompt "sky" "Make it sunset with clouds"

# Remove objects
uv run python fal-image-edit photo.jpg object_mask.png "Remove completely" --strength 1.0

# Seamless object insertion
uv run python fal-image-edit room.jpg region_mask.png "Add modern sofa" --strength 0.85

# General editing (no mask)
uv run python fal-image-edit -m flux-2/redux photo.jpg "Enhance lighting and saturation"

# Premium quality inpainting
uv run python fal-image-edit -m flux-pro-v11/fill image.jpg mask.png "Professional portrait background"

# Artistic modification
uv run python fal-image-edit -m stable-diffusion-v35/inpainting photo.jpg mask.png "Van Gogh style"
```

## File Structure

```
fal-text-to-image/
├── SKILL.md                    # This file
├── README.md                   # Quick reference
├── pyproject.toml              # Dependencies (uv)
├── fal-text-to-image           # Text-to-image generation script
├── fal-image-remix             # Image-to-image remixing script
├── fal-image-edit              # Image editing/inpainting script
├── references/
│   └── model-comparison.md     # Detailed model benchmarks
└── outputs/                    # Generated images (created on first run)
```

## Dependencies

Managed via `uv`:
- `fal-client`: Official fal.ai Python SDK
- `python-dotenv`: Environment variable management
- `pillow`: Image handling and EXIF metadata
- `click`: CLI interface

## Best Practices

### General
1. **Model Selection**: Let scripts auto-select unless you have specific needs
2. **Prompt Engineering**: Be specific and descriptive for better outputs
3. **Cost Awareness**: Monitor usage on fal.ai dashboard
4. **Reproducibility**: Use `--seed` for consistent results during iteration

### Text-to-Image
1. **Reference Images**: Use high-quality references for best style transfer results
2. **Size Selection**: Match aspect ratio to intended use (square, landscape, portrait)
3. **Model Choice**: Use recraft/v3 for typography, flux-pro for professional photography

### Image Remix
1. **Strength Tuning**: Start with default (0.75), adjust based on desired transformation
2. **Source Quality**: Higher quality source images produce better remixes
3. **Iteration**: Use --seed to iterate on same generation with different prompts
4. **Balance**: Lower strength preserves more detail, higher creates more dramatic changes

### Image Edit
1. **Mask Quality**: Clean, well-defined masks produce better results
2. **Mask Creation**: Use image editors for precise control, --mask-prompt for quick tests
3. **Blending**: Use gray tones in masks for smooth transitions
4. **Edit Strength**: Use 0.95+ for object removal, 0.7-0.9 for modifications
5. **Test First**: Try --mask-prompt before creating detailed masks
6. **Multiple Edits**: Edit in stages rather than all at once for complex modifications

## Resources

- fal.ai Documentation: https://docs.fal.ai/
- Model Playground: https://fal.ai/explore/search
- API Keys: https://fal.ai/dashboard/keys
- Pricing: https://fal.ai/pricing

## Workflow Examples

### Complete Image Creation Pipeline

```bash
# 1. Generate base image
uv run python fal-text-to-image -m flux-2 "Modern office space, minimalist" -o base.png

# 2. Remix to different style
uv run python fal-image-remix base.png "Cyberpunk aesthetic with neon" -o styled.png

# 3. Edit specific region
uv run python fal-image-edit styled.png --mask-prompt "desk" "Add holographic display"
```

### Iterative Refinement

```bash
# Generate with seed for reproducibility
uv run python fal-text-to-image "Mountain landscape" --seed 42 -o v1.png

# Remix with same seed, different style
uv run python fal-image-remix v1.png "Oil painting style" --seed 42 -o v2.png

# Fine-tune with editing
uv run python fal-image-edit v2.png --mask-prompt "sky" "Golden hour lighting" --seed 42
```

### Object Removal and Replacement

```bash
# 1. Remove unwanted object
uv run python fal-image-edit photo.jpg object_mask.png "Remove" --strength 1.0 -o removed.png

# 2. Fill with new content
uv run python fal-image-edit removed.png region_mask.png "Beautiful flowers" --strength 0.9
```

## Troubleshooting

| Problem | Solution | Tool |
|---------|----------|------|
| `FAL_KEY not set` | Export FAL_KEY or create .env file | All |
| `Model not found` | Check model name in documentation | All |
| `Image upload fails` | Check file exists and is readable | Remix, Edit |
| `Mask not working` | Verify mask is grayscale PNG (white=edit) | Edit |
| `Transformation too strong` | Reduce --strength value | Remix, Edit |
| `Transformation too weak` | Increase --strength value | Remix, Edit |
| `Mask-prompt not precise` | Create manual mask in image editor | Edit |
| `Generation timeout` | Try faster model or wait longer | All |
| `Rate limit error` | Check fal.ai dashboard usage limits | All |

## Limitations

### General
- Requires active fal.ai API key
- Subject to fal.ai rate limits and quotas
- Internet connection required
- Some models have usage costs (check pricing)

### Text-to-Image
- Image reference features limited to specific models
- Typography quality varies by model

### Image Remix
- Source image quality affects output quality
- Extreme strength values may introduce artifacts
- Some styles work better with specific models

### Image Edit
- Mask quality critical for seamless results
- Auto-generated masks (--mask-prompt) less precise than manual masks
- Complex edits may require multiple passes
- Some models don't support all editing features
