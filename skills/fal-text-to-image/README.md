# fal.ai Image Generation & Editing Skill

Professional AI-powered image workflows: generate, remix, and edit using fal.ai's state-of-the-art models.

## Three Powerful Tools

### 1. Text-to-Image: Generate from Scratch
```bash
uv run python fal-text-to-image "A serene mountain landscape at sunset"
```

### 2. Image Remix: Transform Existing Images
```bash
uv run python fal-image-remix photo.jpg "Transform into oil painting"
```

### 3. Image Edit: Targeted Modifications
```bash
uv run python fal-image-edit photo.jpg mask.png "Replace with flowers"
```

## Quick Start

### Text-to-Image
```bash
# Basic generation (auto-selects best model)
uv run python fal-text-to-image "Cyberpunk city at sunset"

# With specific model
uv run python fal-text-to-image -m flux-pro/v1.1-ultra "Professional portrait"

# With style reference
uv run python fal-text-to-image -i reference.jpg "Artistic landscape"
```

### Image Remix
```bash
# Basic remix (auto-selects model)
uv run python fal-image-remix input.jpg "Anime style character"

# Control transformation strength (0.0=preserve, 1.0=full transformation)
uv run python fal-image-remix photo.jpg "Watercolor painting" --strength 0.6

# Premium quality
uv run python fal-image-remix -m flux-1.1-pro image.jpg "Professional studio portrait"
```

### Image Edit
```bash
# Edit with mask image (white=edit, black=preserve)
uv run python fal-image-edit photo.jpg mask.png "Replace with garden"

# Auto-generate mask from text
uv run python fal-image-edit photo.jpg --mask-prompt "sky" "Make it sunset"

# Remove objects
uv run python fal-image-edit image.jpg mask.png "Remove" --strength 1.0

# General editing (no mask)
uv run python fal-image-edit photo.jpg "Enhance lighting and colors"
```

## Setup

1. Get your API key from [fal.ai dashboard](https://fal.ai/dashboard/keys)

2. Set environment variable:
```bash
export FAL_KEY="your-api-key-here"
```

Or create `.env` file:
```env
FAL_KEY=your-api-key-here
```

3. Run (uv handles dependencies automatically):
```bash
# Text-to-image
uv run python fal-text-to-image "Your prompt here"

# Image remix
uv run python fal-image-remix input.jpg "Your transformation prompt"

# Image edit
uv run python fal-image-edit input.jpg mask.png "Your edit prompt"
```

## Features

### Text-to-Image
- **Intelligent Model Selection**: Auto-selects best model based on prompt analysis
- **13+ Model Options**: FLUX, Recraft V3, Imagen4, Stable Diffusion, and more
- **Style Transfer**: Use reference images with `-i` flag
- **High-Resolution**: Up to 2K outputs with flux-pro/v1.1-ultra
- **Reproducible**: Use `--seed` for consistent results

### Image Remix
- **Style Transformation**: Convert photos to paintings, illustrations, or any artistic style
- **Strength Control**: Adjust transformation intensity (0.0-1.0)
- **Composition Preservation**: Maintains original image structure while applying new styles
- **Multiple Models**: Optimized for different remix types (artistic, realistic, vector)

### Image Edit
- **Targeted Editing**: Modify specific regions using mask images
- **Auto-Masking**: Generate masks from text prompts (`--mask-prompt`)
- **Object Removal**: Seamlessly remove unwanted objects
- **Inpainting**: Fill and complete image regions
- **General Editing**: Overall image adjustments without masks

### All Tools
- **Metadata Embedding**: Stores prompt and generation parameters in image EXIF
- **Progress Tracking**: Real-time queue position and generation status
- **Error Handling**: Clear error messages and validation

## Available Models

See [SKILL.md](SKILL.md) for complete model documentation.

### Text-to-Image Top Picks
- **flux-pro/v1.1-ultra**: Professional high-res (up to 2K)
- **recraft/v3/text-to-image**: SOTA quality, excellent typography
- **flux-2**: Best balance (100 free requests)
- **ideogram/v2**: Typography specialist

### Image Remix Top Picks
- **flux-2/dev**: General remixing (free, fast)
- **flux-1.1-pro**: Premium quality transformations
- **recraft/v3**: Vector/illustration style
- **stable-diffusion-v35**: Artistic styles

### Image Edit Top Picks
- **flux-2/fill**: Seamless inpainting (default)
- **flux-pro-v11/fill**: Premium quality inpainting
- **flux-2/redux**: General editing (no mask)
- **stable-diffusion-v35/inpainting**: Artistic edits

## Usage Examples

### Text-to-Image

#### Typography & Logos
```bash
uv run python fal-text-to-image \
  -m recraft/v3/text-to-image \
  "Modern tech logo with text 'AI Labs' in minimalist blue design"
```

#### Professional Photography
```bash
uv run python fal-text-to-image \
  -m flux-pro/v1.1-ultra \
  "Professional headshot of business executive, studio lighting, grey background"
```

#### Reproducible Generation
```bash
uv run python fal-text-to-image \
  -m flux-2 \
  --seed 42 \
  "Cyberpunk cityscape with neon lights"
```

### Image Remix

#### Style Transfer
```bash
# Subtle artistic style
uv run python fal-image-remix photo.jpg "Oil painting style" --strength 0.4

# Strong anime transformation
uv run python fal-image-remix portrait.jpg "Anime character" --strength 0.9

# Vector conversion
uv run python fal-image-remix -m recraft/v3 logo.png "Clean vector illustration"
```

### Image Edit

#### Object Removal
```bash
# Remove with mask
uv run python fal-image-edit photo.jpg object_mask.png "Remove completely" --strength 1.0
```

#### Region Replacement
```bash
# With mask image
uv run python fal-image-edit room.jpg region_mask.png "Add modern sofa"

# With auto-generated mask
uv run python fal-image-edit landscape.jpg --mask-prompt "sky" "Golden hour sunset"
```

#### General Enhancement
```bash
uv run python fal-image-edit -m flux-2/redux photo.jpg "Enhance lighting and saturation"
```

## Workflow Pipeline

Combine all three tools for complete image workflows:

```bash
# 1. Generate base image
uv run python fal-text-to-image "Modern office space" -o base.png

# 2. Apply artistic style
uv run python fal-image-remix base.png "Cyberpunk aesthetic" -o styled.png

# 3. Edit specific details
uv run python fal-image-edit styled.png --mask-prompt "desk" "Add holographic display"
```

## Command-Line Options

### fal-text-to-image
```
Arguments:
  PROMPT                    Text description of image

Options:
  -m, --model TEXT         Model selection
  -i, --image TEXT         Reference image for style transfer
  -o, --output TEXT        Output filename
  -s, --size TEXT          Image size (1024x1024, landscape_16_9, etc.)
  --seed INTEGER           Random seed
  --steps INTEGER          Inference steps
  --guidance FLOAT         Guidance scale
  --help                   Show help
```

### fal-image-remix
```
Arguments:
  INPUT_IMAGE              Path or URL to source image
  PROMPT                   How to transform the image

Options:
  -m, --model TEXT         Model selection
  -o, --output TEXT        Output filename
  -s, --strength FLOAT     Transformation strength 0.0-1.0 (default: 0.75)
  --guidance FLOAT         Guidance scale (default: 7.5)
  --seed INTEGER           Random seed
  --steps INTEGER          Inference steps
  --help                   Show help
```

### fal-image-edit
```
Arguments:
  INPUT_IMAGE              Path or URL to source image
  MASK_IMAGE               Path or URL to mask (white=edit, black=preserve) [optional]
  PROMPT                   How to edit the masked region

Options:
  -m, --model TEXT         Model selection
  -o, --output TEXT        Output filename
  --mask-prompt TEXT       Generate mask from text (no mask image needed)
  -s, --strength FLOAT     Edit strength 0.0-1.0 (default: 0.95)
  --guidance FLOAT         Guidance scale (default: 7.5)
  --seed INTEGER           Random seed
  --steps INTEGER          Inference steps
  --help                   Show help
```

## Output

All tools save images to `outputs/` directory with:
- Timestamp in filename
- Model name in filename
- Embedded metadata (prompt, model, parameters)
- Console display of generation time and image URL

## Cost Management

- **Free Tier**: flux-2/dev offers 100 free requests (until Dec 25, 2025)
- **Budget**: Use flux-2/dev or stable-diffusion models
- **Premium**: flux-pro models charged per megapixel
- **Design**: recraft/v3 at $0.04/image ($0.08 for vector)

Monitor usage at [fal.ai dashboard](https://fal.ai/dashboard)

## File Structure

```
fal-text-to-image/
├── SKILL.md                    # Full documentation
├── README.md                   # This file
├── fal-text-to-image           # Text-to-image generation script
├── fal-image-remix             # Image-to-image remixing script
├── fal-image-edit              # Image editing/inpainting script
├── pyproject.toml              # Dependencies
├── .env.example                # Environment template
├── .gitignore
├── references/
│   └── model-comparison.md     # Detailed model comparison
└── outputs/                    # Generated images (created on first run)
```

## Troubleshooting

| Issue | Solution | Tool |
|-------|----------|------|
| `FAL_KEY not set` | Export FAL_KEY or create .env file | All |
| `Model not found` | Check model name in SKILL.md | All |
| `Image upload fails` | Check file exists and is readable | Remix, Edit |
| `Mask not working` | Verify mask is grayscale PNG (white=edit) | Edit |
| `Transformation too strong` | Reduce --strength value | Remix, Edit |
| `Generation timeout` | Try faster model or wait longer | All |

## Resources

- [fal.ai Documentation](https://docs.fal.ai/)
- [Model Playground](https://fal.ai/explore/search)
- [API Keys](https://fal.ai/dashboard/keys)
- [Pricing](https://fal.ai/pricing)
- [Full Skill Documentation](SKILL.md)

## Dependencies

Managed automatically by `uv`:
- fal-client
- python-dotenv
- pillow
- click
- requests

## License

This skill is part of the Claude Code skills ecosystem.
