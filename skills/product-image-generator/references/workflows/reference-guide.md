# Reference Image Guide

## Overview

Reference images help maintain visual consistency and style accuracy across generated product images.

## Types of Reference Images

### 1. User-Provided Reference

**Purpose**: Match existing brand style or competitor standards

**Sources**:
- Brand guideline images
- Previous product shoots
- Competitor product images
- Mood board images
- Style inspiration images

**Usage**:
```bash
/product-image-generator product.md --ref brand-style.png
/product-image-generator product.md --ref style-ref.png --ref competitor.jpg
```

### 2. Internal Reference Chain

**Purpose**: Ensure consistency within a generated image series

**How it works**:
1. Generate hero image (Image 1) without reference
2. Use Image 1 as reference for all subsequent images (2, 3, ...N)

**Automatic**: Applied by default when no user reference provided

## Reference Image Best Practices

### Ideal Reference Images

| Quality | Description |
|---------|-------------|
| **High resolution** | Clear details, no blur |
| **Similar lighting** | Matches desired output |
| **Relevant composition** | Similar framing/angles |
| **Consistent style** | Matches brand aesthetic |

### What Reference Images Control

- **Lighting style** - Soft vs hard, direction, intensity
- **Color grading** - Warm vs cool, saturation levels
- **Background treatment** - Pure white, gradient, contextual
- **Shadow handling** - Minimal vs dramatic
- **Overall mood** - Professional, lifestyle, luxury, etc.

### What Reference Images Don't Control

- **Product shape** - Your actual product geometry
- **Product color** - Unless specified in prompt
- **Platform requirements** - Size, background rules

## Using Reference Images by Platform

### Amazon

```bash
# Reference for additional images only (main must be pure white)
/product-image-generator product.md \
  --ref style-guide.png \
  --platform amazon
```

**Note**: Main image must still comply with pure white background requirement.

### Shopify

```bash
# Full creative freedom with style reference
/product-image-generator product.md \
  --ref brand-aesthetic.png \
  --platform shopify
```

### Taobao/JD

```bash
# Reference for infographic style
/product-image-generator product.md \
  --ref competitor-success.jpg \
  --platform taobao
```

## Multiple Reference Images

When using multiple references:

```bash
/product-image-generator product.md \
  --ref lighting-style.png \
  --ref color-grading.png \
  --ref composition-example.png
```

**Priority order**:
1. First reference (`--ref` #1) - Primary style anchor
2. Second reference - Secondary influence
3. Third reference - Tertiary influence

## Reference Image in Prompts

Reference images are integrated into prompts as:

```
Style reference: [reference image path]
Match the lighting, color grading, and overall aesthetic of the reference.
Maintain similar shadow treatment and background style.
```

## Troubleshooting

### Reference Not Having Desired Effect

**Solutions**:
1. Use clearer, higher quality reference
2. Be more specific in prompt about what to match
3. Try single reference instead of multiple

### Style Inconsistency Across Images

**Solutions**:
1. Ensure internal reference chain is active
2. Use same session ID for all generations
3. Check that reference image is being applied

### Reference Too Dominant

**Solutions**:
1. Use reference with lighter weighting in prompt
2. Specify "subtle influence" in prompt
3. Choose reference closer to desired output

## Example Workflows

### Workflow A: Brand Consistency

```
1. Gather existing brand images (3-5)
2. Select best representative as --ref
3. Generate new product images
4. Verify brand consistency
```

### Workflow B: Competitor Analysis

```
1. Save competitor product images
2. Use as --ref for similar quality
3. Differentiate with unique prompt elements
4. Maintain category standards
```

### Workflow C: Series Generation

```
1. No user reference provided
2. Image 1 establishes style
3. Images 2-N reference Image 1
4. Consistent series output
```

## File Organization

Reference images should be stored in:

```
product-images/{product-slug}/
├── references/
│   ├── user-provided/
│   │   └── brand-style.png
│   └── generated/
│       └── 01-hero-slug.png (used as internal ref)
├── source-article.md
└── ...
```
