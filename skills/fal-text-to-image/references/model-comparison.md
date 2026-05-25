# fal.ai Text-to-Image Model Comparison

Detailed comparison of available text-to-image models on fal.ai platform.

## Model Benchmarks

### FLUX Series

#### flux-pro/v1.1-ultra
- **Endpoint**: `fal-ai/flux-pro/v1.1-ultra`
- **Resolution**: Up to 2K (2048x2048)
- **Strengths**: Professional-grade image quality, exceptional photo realism
- **Use Cases**: Publication-ready images, professional photography, high-res prints
- **Pricing**: Per megapixel
- **Speed**: Moderate (high quality requires more compute)
- **Best For**: Commercial projects, professional portfolios, marketing materials

#### flux-2-pro
- **Endpoint**: `fal-ai/flux-2-pro`
- **Strengths**: High-quality image manipulation, style transfer, sequential editing
- **Use Cases**: Image editing workflows, style transfer, professional edits
- **Best For**: Iterative editing, professional post-processing

#### flux-2
- **Endpoint**: `fal-ai/flux-2`
- **Strengths**: Enhanced realism, crisp text generation, native editing
- **Use Cases**: General-purpose image generation, balanced quality/speed
- **Pricing**: 100 free requests (expires Dec 25, 2025)
- **Best For**: Everyday image generation, prototyping, experimentation

#### flux-2/lora
- **Endpoint**: `fal-ai/flux-2/lora`
- **Strengths**: Custom style adaptation, fine-tuned model variations
- **Use Cases**: Domain-specific styles, personalized outputs
- **Best For**: Consistent style across generations, brand-specific imagery

#### flux-2/lora/edit
- **Endpoint**: `fal-ai/flux-2/lora/edit`
- **Strengths**: Specialized style transfer, domain-specific modifications
- **Use Cases**: Image-to-image editing with LoRA, style references
- **Best For**: Style-guided transformations, reference-based generation

#### flux/dev
- **Endpoint**: `fal-ai/flux/dev`
- **Parameters**: 12 billion
- **Architecture**: Flow transformer
- **Strengths**: High-quality text-to-image, suitable for commercial use
- **Best For**: Development and testing, personal/commercial projects

#### flux-general
- **Endpoint**: `fal-ai/flux-general`
- **Features**: LoRA, ControlNet, IP-Adapter support
- **Strengths**: Comprehensive control, multiple guidance methods
- **Best For**: Advanced users needing full control over generation

### Recraft V3

- **Endpoint**: `fal-ai/recraft/v3/text-to-image`
- **Benchmark**: SOTA in Hugging Face Text-to-Image Benchmark (Artificial Analysis)
- **Strengths**:
  - Exceptional long text generation
  - Vector art capabilities
  - Brand-style consistency
  - Industry-leading overall quality
- **Use Cases**: Typography design, logos, brand materials, posters
- **Pricing**: $0.04/image ($0.08 for vector styles)
- **Best For**: Professional design work, branding, text-heavy compositions

### Google Imagen4

#### imagen4/preview
- **Endpoint**: `fal-ai/imagen4/preview`
- **Quality**: Google's highest quality model
- **Strengths**: Overall quality, Google's latest research
- **Best For**: Users wanting Google's cutting-edge capabilities

#### imagen4/preview/fast
- **Endpoint**: `fal-ai/imagen4/preview/fast`
- **Quality**: High quality with faster generation
- **Best For**: Quick iterations with Google quality

### Stable Diffusion v3.5 Large

- **Endpoint**: `fal-ai/stable-diffusion-v35-large`
- **Architecture**: Multimodal Diffusion Transformer (MMDiT)
- **Strengths**:
  - Improved image quality
  - Exceptional typography
  - Complex prompt understanding
  - Resource-efficient
- **Best For**: Complex compositions, artistic style control

### Ideogram v2

- **Endpoint**: `fal-ai/ideogram/v2`
- **Strengths**:
  - Exceptional typography handling
  - Realistic outputs
  - Optimized for commercial use
- **Use Cases**: Posters, logos, text-heavy designs
- **Best For**: Projects where text accuracy is critical

### Bria Text-to-Image 3.2

- **Endpoint**: `fal-ai/bria/text-to-image/3.2`
- **Training Data**: Exclusively licensed data
- **Strengths**:
  - Safe for commercial use
  - Excellent text rendering
  - No copyright concerns
- **Best For**: Commercial projects with strict licensing requirements

### HiDream-I1 Series

#### hidream-i1-full
- **Endpoint**: `fal-ai/hidream-i1-full`
- **Parameters**: 17 billion
- **Quality**: State-of-the-art
- **Speed**: Seconds
- **Best For**: Maximum quality from open-source model

#### hidream-i1-dev
- **Endpoint**: `fal-ai/hidream-i1-dev`
- **Parameters**: 17 billion
- **Balance**: Quality and speed
- **Best For**: Development with high quality

#### hidream-i1-fast
- **Endpoint**: `fal-ai/hidream-i1-fast`
- **Parameters**: 17 billion
- **Steps**: 16 steps
- **Best For**: Rapid iteration and prototyping

## Selection Matrix

| Use Case | Recommended Model | Alternative |
|----------|------------------|-------------|
| Professional Photography | flux-pro/v1.1-ultra | imagen4/preview |
| Typography/Logos | recraft/v3/text-to-image | ideogram/v2 |
| General Purpose | flux-2 | flux/dev |
| Style Transfer | flux-2/lora/edit | flux-2-pro |
| Vector Art | recraft/v3/text-to-image | stable-diffusion-v35-large |
| Commercial Safe | bria/text-to-image/3.2 | flux-pro/v1.1-ultra |
| Fast Iteration | hidream-i1-fast | imagen4/preview/fast |
| Complex Prompts | stable-diffusion-v35-large | recraft/v3/text-to-image |
| Brand Consistency | flux-2/lora | recraft/v3/text-to-image |
| High-Res Outputs | flux-pro/v1.1-ultra | stable-diffusion-v35-large |

## Cost Considerations

### Free Tier Options
- **flux-2**: 100 free requests (expires Dec 25, 2025)
- Best for experimentation and prototyping

### Budget Options
- **flux/dev**: Suitable for personal and commercial use
- **stable-diffusion-v35-large**: Resource-efficient

### Premium Options
- **flux-pro/v1.1-ultra**: Per-megapixel pricing, best quality
- **recraft/v3/text-to-image**: $0.04-0.08 per image

## Performance Characteristics

### Speed Ranking (Fast to Slow)
1. hidream-i1-fast
2. imagen4/preview/fast
3. flux-2
4. flux/dev
5. stable-diffusion-v35-large
6. imagen4/preview
7. flux-pro/v1.1-ultra

### Quality Ranking (Best to Good)
1. flux-pro/v1.1-ultra
2. recraft/v3/text-to-image
3. imagen4/preview
4. hidream-i1-full
5. stable-diffusion-v35-large
6. flux-2
7. ideogram/v2

### Typography Ranking
1. recraft/v3/text-to-image
2. ideogram/v2
3. stable-diffusion-v35-large
4. bria/text-to-image/3.2
5. flux-2

## Advanced Features

### LoRA Support
- flux-2/lora
- flux-2/lora/edit
- flux-general (with LoRA tools)

### ControlNet Support
- flux-general

### IP-Adapter Support
- flux-general

### Editing Capabilities
- flux-2 (native editing)
- flux-2-pro
- flux-2/lora/edit

## Best Practices by Model

### flux-pro/v1.1-ultra
- Use for final production images
- Request specific resolutions up to 2K
- Detailed prompts yield best results
- Monitor costs (per-megapixel pricing)

### recraft/v3/text-to-image
- Specify text content clearly in prompt
- Use for brand consistency across images
- Leverage vector style for scalable outputs
- Ideal for design mockups

### flux-2
- Great starting point for most projects
- Use free tier for experimentation
- Refine prompts before moving to premium models
- Good balance of speed and quality

### flux-2/lora/edit
- Provide high-quality reference images
- Be specific about style elements to transfer
- May require iteration to match reference
- Best with similar composition to reference

### stable-diffusion-v35-large
- Use detailed, complex prompts
- Leverage artistic style keywords
- Good for creative interpretations
- Resource-efficient for batch generation

## Prompt Engineering Tips

### For Typography Models (Recraft, Ideogram)
- Explicitly state text content: "logo with text 'Company Name'"
- Specify font style: "modern sans-serif", "elegant script"
- Mention layout: "centered text", "circular arrangement"

### For Photo-Realistic Models (FLUX Pro, Imagen)
- Include lighting details: "golden hour", "studio lighting"
- Specify camera details: "50mm lens", "shallow depth of field"
- Mention style: "professional headshot", "editorial photography"

### For Style Transfer (LoRA Edit)
- Describe target content clearly
- Reference specific style elements
- May need to iterate on prompt for best match

### General Best Practices
- Be specific and descriptive
- Include desired mood/atmosphere
- Specify composition if important
- Mention any unwanted elements with negative prompts (where supported)
