# Usage Examples

Real-world examples for common image generation tasks.

## Basic Examples

### Simple Landscape
```bash
uv run python fal-text-to-image "A serene mountain landscape at sunset with purple clouds"
```

### Portrait
```bash
uv run python fal-text-to-image "Portrait of a young woman with red hair, professional lighting"
```

### Abstract Art
```bash
uv run python fal-text-to-image "Abstract geometric patterns in blue and gold"
```

## Typography & Design

### Logo Design
```bash
uv run python fal-text-to-image \
  -m recraft/v3/text-to-image \
  "Modern tech startup logo with text 'AI Labs', minimalist design, blue and white color scheme"
```

### Poster Design
```bash
uv run python fal-text-to-image \
  -m ideogram/v2 \
  "Movie poster with text 'FUTURE CITY' in bold futuristic font, cyberpunk aesthetic"
```

### Product Label
```bash
uv run python fal-text-to-image \
  -m recraft/v3/text-to-image \
  "Coffee bag label design with text 'Morning Blend', vintage style, brown and cream colors"
```

## Professional Photography

### Corporate Headshot
```bash
uv run python fal-text-to-image \
  -m flux-pro/v1.1-ultra \
  "Professional corporate headshot of business executive, grey background, studio lighting, 50mm lens" \
  -s 2048x2048
```

### Product Photography
```bash
uv run python fal-text-to-image \
  -m flux-pro/v1.1-ultra \
  "Product photography of luxury watch on marble surface, dramatic lighting, commercial quality"
```

### Architectural Photography
```bash
uv run python fal-text-to-image \
  -m flux-pro/v1.1-ultra \
  "Modern architecture exterior, glass and steel building, golden hour lighting, wide angle"
```

## Style Transfer

### Artistic Style Transfer
```bash
uv run python fal-text-to-image \
  -m flux-2/lora/edit \
  -i van_gogh_style.jpg \
  "Cityscape at night with busy streets"
```

### Photo Style Matching
```bash
uv run python fal-text-to-image \
  -m flux-2/lora/edit \
  -i reference_photo.jpg \
  "Portrait of a man in formal attire"
```

## Creative & Artistic

### Fantasy Scene
```bash
uv run python fal-text-to-image \
  -m stable-diffusion-v35-large \
  "Dragon flying over ancient castle, dramatic clouds, fantasy art style, detailed"
```

### Sci-Fi Concept
```bash
uv run python fal-text-to-image \
  -m flux-2 \
  "Futuristic space station orbiting alien planet, cinematic lighting, concept art"
```

### Character Design
```bash
uv run python fal-text-to-image \
  -m stable-diffusion-v35-large \
  "Steampunk inventor character, full body, detailed mechanical accessories, Victorian era"
```

## Technical & Reproducible

### With Specific Seed
```bash
uv run python fal-text-to-image \
  -m flux-2 \
  --seed 42 \
  "Cyberpunk city street with neon signs"
```

### High Guidance
```bash
uv run python fal-text-to-image \
  -m flux-2 \
  --guidance 15.0 \
  "Photorealistic apple on wooden table, studio lighting"
```

### More Inference Steps
```bash
uv run python fal-text-to-image \
  -m stable-diffusion-v35-large \
  --steps 75 \
  "Highly detailed mechanical watch mechanism, macro photography"
```

### Custom Output Name
```bash
uv run python fal-text-to-image \
  -m flux-2 \
  -o company_logo_v1.png \
  "Tech company logo concept"
```

## Batch Generation Scenarios

### Testing Multiple Styles
```bash
# Version 1: Realistic
uv run python fal-text-to-image \
  -m flux-pro/v1.1-ultra \
  --seed 100 \
  -o portrait_realistic.png \
  "Portrait of young woman in garden"

# Version 2: Artistic
uv run python fal-text-to-image \
  -m stable-diffusion-v35-large \
  --seed 100 \
  -o portrait_artistic.png \
  "Portrait of young woman in garden, impressionist style"

# Version 3: Stylized
uv run python fal-text-to-image \
  -m flux-2/lora \
  --seed 100 \
  -o portrait_stylized.png \
  "Portrait of young woman in garden, anime style"
```

### Iterating on Design
```bash
# First iteration
uv run python fal-text-to-image \
  -m recraft/v3/text-to-image \
  --seed 42 \
  -o logo_v1.png \
  "Minimalist tech logo with text 'DataFlow'"

# Refine with same seed, different prompt
uv run python fal-text-to-image \
  -m recraft/v3/text-to-image \
  --seed 42 \
  -o logo_v2.png \
  "Minimalist tech logo with text 'DataFlow', blue gradient, modern sans-serif"

# Different model, same concept
uv run python fal-text-to-image \
  -m ideogram/v2 \
  --seed 42 \
  -o logo_v3.png \
  "Minimalist tech logo with text 'DataFlow', blue gradient, modern sans-serif"
```

## Commercial Use Cases

### E-Commerce Product
```bash
uv run python fal-text-to-image \
  -m bria/text-to-image/3.2 \
  "Product mockup of smartphone on clean white background, commercial photography style"
```

### Marketing Material
```bash
uv run python fal-text-to-image \
  -m flux-pro/v1.1-ultra \
  "Business team collaboration in modern office, diverse group, professional setting" \
  -s landscape_16_9
```

### Social Media Content
```bash
uv run python fal-text-to-image \
  -m flux-2 \
  "Instagram-style photo of healthy breakfast bowl, top-down view, natural lighting" \
  -s square
```

## Workflow Integration

### A/B Testing Visuals
```bash
# Test A: Traditional approach
uv run python fal-text-to-image \
  -m flux-pro/v1.1-ultra \
  --seed 999 \
  -o hero_traditional.png \
  "Professional business setting, corporate meeting"

# Test B: Modern approach
uv run python fal-text-to-image \
  -m flux-pro/v1.1-ultra \
  --seed 999 \
  -o hero_modern.png \
  "Casual collaborative workspace, startup atmosphere"
```

### Reference-Guided Iterations
```bash
# Generate base image
uv run python fal-text-to-image \
  -m flux-2 \
  -o base_concept.png \
  "Modern interior design, minimalist living room"

# Use it as reference for variations
uv run python fal-text-to-image \
  -m flux-2/lora/edit \
  -i outputs/base_concept.png \
  -o variation_1.png \
  "Modern interior with warmer tones and plants"
```

## Tips for Better Results

### Be Specific
```bash
# ❌ Vague
uv run python fal-text-to-image "a car"

# ✅ Specific
uv run python fal-text-to-image \
  "Red sports car on coastal highway, sunset lighting, cinematic angle, 4k quality"
```

### Use Technical Terms
```bash
# ❌ Generic
uv run python fal-text-to-image "nice photo of person"

# ✅ Technical
uv run python fal-text-to-image \
  -m flux-pro/v1.1-ultra \
  "Professional portrait, 85mm lens, f/1.8 aperture, studio lighting, grey backdrop"
```

### Layer Details
```bash
# ✅ Layered description
uv run python fal-text-to-image \
  "Ancient library interior | towering bookshelves | warm candlelight | dust particles in air | mysterious atmosphere | fantasy setting"
```

### Test Across Models
```bash
# Same prompt, different models
PROMPT="Vintage poster design with text 'Grand Hotel', Art Deco style"

uv run python fal-text-to-image -m recraft/v3/text-to-image "$PROMPT" -o test_recraft.png
uv run python fal-text-to-image -m ideogram/v2 "$PROMPT" -o test_ideogram.png
uv run python fal-text-to-image -m stable-diffusion-v35-large "$PROMPT" -o test_sd.png
```
