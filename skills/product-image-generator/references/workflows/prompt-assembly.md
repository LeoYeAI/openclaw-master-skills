# Prompt Assembly Guide

## Prompt Structure

```
[Style descriptor], [subject description], [background], [lighting],
[mood/atmosphere], [technical specs], [platform requirements]
```

## Component Breakdown

### 1. Style Descriptor

Based on selected style preset:

| Style | Keywords |
|-------|----------|
| minimal | "Professional product photography, clean commercial" |
| premium | "Premium product photography, sophisticated elegant" |
| lifestyle | "Lifestyle product photography, natural authentic" |
| bold | "Bold product photography, high energy vibrant" |
| soft | "Soft product photography, gentle calming" |
| tech | "Tech product photography, futuristic sleek" |
| natural | "Natural product photography, organic earthy" |
| luxury | "Luxury product photography, dramatic exclusive" |

### 2. Subject Description

Describe the product clearly:

```
A [product category] with [key features], [color], [material],
[notable design elements], positioned at [angle]
```

### 3. Background

Based on scene type:

| Scene | Background Description |
|-------|----------------------|
| studio | "Pure white background RGB(255,255,255)" |
| lifestyle | "[Specific environment] background" |
| contextual | "Staged [setting] with subtle props" |
| exploded | "Technical white background with component layout" |
| comparison | "Split background for comparison" |
| infographic | "Clean background suitable for text overlay" |

### 4. Lighting

Based on style:

| Style | Lighting Description |
|-------|---------------------|
| minimal | "Soft even studio lighting, minimal shadows" |
| premium | "Dramatic side lighting, defined contours" |
| lifestyle | "Natural ambient lighting, warm inviting" |
| bold | "Hard dramatic lighting, strong shadows" |
| soft | "Diffused gentle lighting, minimal shadows" |
| tech | "Precision LED lighting, cool accents" |
| natural | "Natural daylight simulation, soft shadows" |
| luxury | "Sculpted dramatic lighting, deep shadows" |

### 5. Mood/Atmosphere

Emotional quality:

- Professional, clean, trustworthy
- Sophisticated, elegant, exclusive
- Warm, inviting, relatable
- Energetic, exciting, dynamic
- Calming, gentle, nurturing
- Futuristic, innovative, cutting-edge
- Authentic, wholesome, natural
- Dramatic, luxurious, premium

### 6. Technical Specs

Always include:

```
High resolution, sharp focus, professional quality,
e-commerce ready, commercial photography standards
```

### 7. Platform Requirements

For Amazon main image:

```
Amazon compliant, pure white background,
product fills 85% of frame, no text or logos
```

## Full Prompt Examples

### Minimal + Studio + Amazon

```
Professional product photography, [product name] with [features],
pure white background RGB(255,255,255), soft even studio lighting,
minimal contact shadows, clean commercial look, neutral color grading,
sharp focus on product, Amazon main image compliant, product fills
85% of frame, high resolution, e-commerce ready
```

### Lifestyle + Warm + Shopify

```
Lifestyle product photography, [product name] in use,
[specific environment setting], natural ambient lighting,
warm inviting mood, relatable lifestyle imagery, authentic
usage scenario, soft natural shadows, high resolution,
Shopify store quality
```

### Tech + Infographic

```
Tech product photography, [product name], dark gradient
background, precision LED lighting with blue accents,
futuristic mood, sleek modern composition, feature callouts
ready, high contrast, sharp details, tech commercial quality
```

## Negative Prompts

Add to avoid common issues:

```
No blur, no distortion, no artifacts, no text (for main images),
no watermarks (unless specified), no props (for studio shots),
no people (unless lifestyle specified)
```

## Reference Image Chain

For visual consistency across multiple images:

1. **Image 1 (Hero)**: Generate without reference
2. **Images 2+**: Add `--ref [path-to-image-1.png]`

## Prompt Templates by Image Type

### Hero Shot Template

```
[Style] product photography, [product] on [background],
[lighting setup], [mood], hero composition, [platform requirements],
high resolution, commercial quality
```

### Detail Shot Template

```
[Style] macro photography, close-up of [specific feature],
[background], [lighting for detail], sharp focus on [area],
high detail, commercial quality
```

### Lifestyle Template

```
Lifestyle photography, [product] in [environment],
natural usage scenario, [specific action], [lighting],
authentic mood, aspirational lifestyle, commercial quality
```

### Infographic Template

```
[Style] product photography, [product] on [background],
clean composition suitable for text overlay, [lighting],
professional quality, infographic base image
```

## Language Considerations

For Chinese language prompts:

```
专业产品摄影，[产品名称]，[背景描述]，[灯光设置]，
[风格关键词]，高分辨率，商业品质，电商平台适用
```

## Iteration Strategy

If first result isn't perfect:

1. Add more specific product details
2. Clarify lighting direction
3. Specify exact background color
4. Add negative prompts
5. Adjust style keywords
