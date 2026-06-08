---
name: product-image-generator
description: Generates professional product images for e-commerce platforms (Amazon, Shopify, eBay, etc.). Supports 8 visual styles and 6 scene types optimized for different product categories. Use when user mentions "商品图", "product images", "Amazon listing", "电商图片", or needs e-commerce product photography.
metadata:
  version: 1.0.0
---

# E-commerce Product Image Generator

Create professional product images optimized for e-commerce platforms with platform-specific requirements and multiple visual styles.

## Usage

```bash
# Auto-select style based on product
/product-image-generator product-description.md

# Specify style
/product-image-generator product.md --style minimal

# Specify platform (auto-adjusts image requirements)
/product-image-generator product.md --platform amazon

# Specify scene type
/product-image-generator product.md --scene studio

# Combine options
/product-image-generator product.md --style premium --platform shopify --scene lifestyle

# Direct input
/product-image-generator
[paste product description]

# Direct input with options
/product-image-generator --style minimal --scene studio
[paste product description]

# With reference image (for style consistency)
/product-image-generator product.md --ref brand-style.png

# Multiple reference images
/product-image-generator product.md --ref style.png --ref competitor.jpg
```

## Options

| Option | Description |
|--------|-------------|
| `--style <name>` | Visual style (see Style Gallery) |
| `--scene <type>` | Scene type (see Scene Gallery) |
| `--platform <name>` | E-commerce platform (auto-adjusts requirements) |
| `--ref <path>` | Reference image(s) for style consistency |

## Three Dimensions

| Dimension | Controls | Options |
|-----------|----------|---------|
| **Style** | Visual aesthetics: mood, color treatment | minimal, premium, lifestyle, bold, soft, tech, natural, luxury |
| **Scene** | Background and context | studio, lifestyle, contextual, exploded, comparison, infographic |
| **Platform** | Technical requirements | amazon, shopify, ebay, etsy, taobao, jd, pinduoduo |

Style × Scene × Platform can be freely combined. Example: `--style premium --scene lifestyle --platform amazon` creates a high-end lifestyle shot meeting Amazon's image requirements.

## Style Gallery

| Style | Description | Best For |
|-------|-------------|----------|
| `minimal` (Default) | Clean, white background, focus on product | Electronics, accessories, professional products |
| `premium` | Sophisticated, elegant lighting, subtle shadows | Luxury goods, jewelry, high-end cosmetics |
| `lifestyle` | Product in natural use context | Home goods, fashion, outdoor products |
| `bold` | High contrast, vibrant, attention-grabbing | Sports products, gaming, youth-oriented items |
| `soft` | Gentle lighting, pastel tones, warm | Baby products, skincare, wellness items |
| `tech` | Futuristic, sleek, modern | Electronics, gadgets, software, AI products |
| `natural` | Organic, eco-friendly, earthy tones | Sustainable products, food, natural cosmetics |
| `luxury` | Gold accents, dramatic lighting, rich colors | Premium brands, jewelry, high-end fashion |

Detailed style definitions: `references/presets/<style>.md`

## Scene Gallery

| Scene | Description | Image Count |
|-------|-------------|-------------|
| `studio` (Default) | Pure white/gradient background, professional studio lighting | 1-3 images |
| `lifestyle` | Product in real-life usage scenario | 2-5 images |
| `contextual` | Product in environment, staged setting | 2-4 images |
| `exploded` | Component breakdown, features highlighted | 3-6 images |
| `comparison` | Before/after, product vs alternatives | 2-4 images |
| `infographic` | Features, specs, benefits with text overlays | 2-5 images |

Detailed scene definitions: `references/elements/scene-guide.md`

## Platform Requirements

| Platform | Main Image | Additional Images | Notes |
|----------|------------|-------------------|-------|
| `amazon` | 1000x1000+, pure white | Up to 9 images | Main image must be on pure white background |
| `shopify` | 1024x1024+ recommended | Unlimited | Flexible, but 1:1 or 4:3 recommended |
| `ebay` | 500x500+ minimum | Up to 12 free | White background preferred |
| `etsy` | 760x760+ | Up to 10 images | Lifestyle shots perform well |
| `taobao` | 800x800+ | Up to 15 images | Infographic style popular |
| `jd` | 800x800+ | Up to 15 images | Clean, professional style |
| `pinduoduo` | 750x750+ | Up to 10 images | Value-focused presentation |

Platform-specific guidelines: `references/platforms/<platform>.md`

## Auto Selection

| Product Category | Style | Scene |
|------------------|-------|-------|
| Electronics, gadgets | `tech` or `minimal` | studio + exploded |
| Fashion, accessories | `premium` or `lifestyle` | lifestyle + contextual |
| Beauty, cosmetics | `soft` or `premium` | studio + lifestyle |
| Home, furniture | `lifestyle` or `natural` | contextual + lifestyle |
| Sports, outdoor | `bold` or `lifestyle` | lifestyle + contextual |
| Jewelry, luxury | `luxury` or `premium` | studio + lifestyle |
| Baby, kids | `soft` or `natural` | lifestyle + contextual |
| Food, supplements | `natural` or `minimal` | studio + infographic |
| Tools, hardware | `bold` or `tech` | exploded + infographic |

## Outline Strategies

### Strategy A: Product-Focused (产品聚焦型)

| Aspect | Description |
|--------|-------------|
| **Concept** | Product as hero, clean presentation |
| **Features** | Multiple angles, detail shots, pure backgrounds |
| **Best for** | Electronics, accessories, luxury items |
| **Structure** | Hero shot → Angle variations → Detail close-ups → Scale/context |

### Strategy B: Lifestyle-Focused (场景融入型)

| Aspect | Description |
|--------|-------------|
| **Concept** | Product in natural use environment |
| **Features** | Context-rich, emotional connection, aspirational |
| **Best for** | Home goods, fashion, outdoor products |
| **Structure** | Lifestyle hero → Usage scenario → Benefits in context → Social proof |

### Strategy C: Information-Focused (信息传达型)

| Aspect | Description |
|--------|-------------|
| **Concept** | Features and benefits clearly communicated |
| **Features** | Text overlays, callouts, comparisons |
| **Best for** | Complex products, tools, supplements |
| **Structure** | Hero with key benefit → Feature breakdown → Comparison → Specs/usage |

## File Structure

Each session creates an independent directory named by product slug:

```
product-images/{product-slug}/
├── source-{slug}.{ext}             # Source files (description, reference images)
├── analysis.md                     # Product analysis + positioning
├── outline-strategy-a.md           # Strategy A: Product-focused
├── outline-strategy-b.md           # Strategy B: Lifestyle-focused
├── outline-strategy-c.md           # Strategy C: Information-focused
├── outline.md                      # Final selected/merged outline
├── prompts/
│   ├── 01-hero-[slug].md
│   ├── 02-detail-[slug].md
│   └── ...
├── 01-hero-[slug].png
├── 02-detail-[slug].png
└── NN-infographic-[slug].png
```

**Slug Generation**:
1. Extract product name (2-4 words, kebab-case)
2. Example: "无线蓝牙耳机" → `wireless-earbuds`

**Conflict Resolution**:
If `product-images/{product-slug}/` already exists:
- Append timestamp: `{product-slug}-YYYYMMDD-HHMMSS`

## Workflow

### Progress Checklist

```
Product Image Generation Progress:
- [ ] Step 0: Check preferences (EXTEND.md) ⛔ BLOCKING
- [ ] Step 1: Analyze product → analysis.md
- [ ] Step 2: Confirmation 1 - Product understanding ⚠️ REQUIRED
- [ ] Step 3: Generate 3 outline + style variants
- [ ] Step 4: Confirmation 2 - Outline & style & platform ⚠️ REQUIRED
- [ ] Step 5: Generate images (sequential)
- [ ] Step 6: Completion report
```

### Flow

```
Input → [Step 0: Preferences] ─┬─ Found → Continue
                               │
                               └─ Not found → First-Time Setup ⛔ BLOCKING
                                              │
                                              └─ Complete setup → Save EXTEND.md → Continue
                                                                                      │
        ┌─────────────────────────────────────────────────────────────────────────────┘
        ↓
Analyze → [Confirm 1] → 3 Outlines → [Confirm 2: Outline + Style + Platform] → Generate → Complete
```

### Step 0: Load Preferences (EXTEND.md) ⛔ BLOCKING

**Purpose**: Load user preferences or run first-time setup.

**CRITICAL**: If EXTEND.md not found, MUST complete first-time setup before ANY other steps.

Use Bash to check EXTEND.md existence:

```bash
# Check project-level first
test -f .teamclaw-skills/product-image-generator/EXTEND.md && echo "project"

# Then user-level
test -f "$HOME/.teamclaw-skills/product-image-generator/EXTEND.md" && echo "user"
```

| Result | Action |
|--------|--------|
| Found | Read, parse, display summary → Continue to Step 1 |
| Not found | ⛔ BLOCKING: Run first-time setup → Save EXTEND.md → Step 1 |

**First-Time Setup** (when EXTEND.md not found):

Use AskUserQuestion with ALL questions in ONE call:

1. **Default platform preference**: amazon / shopify / ebay / etsy / taobao / jd / pinduoduo / no preference
2. **Default style preference**: minimal / premium / lifestyle / bold / soft / tech / natural / luxury
3. **Watermark**: Enable / Disable (if enable, specify text and position)
4. **Language**: Chinese / English / Auto-detect

Schema: `references/config/preferences-schema.md`

### Step 1: Analyze Product → `analysis.md`

**Actions**:
1. **Save source content**:
   - If file path provided: use as-is
   - If pasted content: save to `source.md`
   - **Backup rule**: If exists, rename to `source-backup-YYYYMMDD-HHMMSS.md`
2. Read and analyze product information
3. **Product analysis**:
   - Category identification
   - Target audience
   - Key features and selling points
   - Competitive positioning
   - Visual opportunities
4. Detect product language
5. Determine recommended image count and types
6. **Generate clarifying questions** (see Step 2)
7. **Save to `analysis.md`**

### Step 2: Confirmation 1 - Product Understanding ⚠️

**Purpose**: Validate understanding + collect missing info.

**Display summary**:
- Product category identified
- Key features extracted
- Target audience
- Recommended platform match

**Use AskUserQuestion** for:
1. **Primary selling point** (multiSelect: true):
   - Design/aesthetics
   - Functionality/features
   - Price/value
   - Quality/durability
   - Brand/status
   - Innovation/technology
   - Sustainability/eco-friendly
   - Convenience/ease of use

2. **Target customer**:
   - Budget-conscious
   - Quality-focused
   - Luxury/premium
   - Tech-savvy
   - Eco-conscious
   - Family-oriented
   - Professional/business
   - Youth/trend-focused

3. **Main use scenario**:
   - Indoor/home
   - Outdoor
   - Office/work
   - Travel
   - Sports/fitness
   - Social/events
   - Auto

4. **Additional context** (optional)

**After response**: Update `analysis.md` → Step 3

### Step 3: Generate 3 Outline + Style Variants

Create three distinct strategy variants, each with outline structure and visual style recommendation.

| Strategy | Filename | Focus | Recommended Style |
|----------|----------|-------|-------------------|
| A | `outline-strategy-a.md` | Product-focused | minimal, tech |
| B | `outline-strategy-b.md` | Lifestyle-focused | lifestyle, soft, natural |
| C | `outline-strategy-c.md` | Information-focused | bold, infographic-style |

**Outline format** (YAML front matter + content):
```yaml
---
strategy: a  # a, b, or c
name: Product-Focused
style: minimal
style_reason: "Clean presentation highlights product design and build quality"
scene: studio
platform: amazon
image_count: 5
---

## P1 Hero Shot
**Type**: hero
**Purpose**: Main product image, first impression
**Visual**: Product on pure white background, professional lighting
**Platform**: Amazon main image compliant (1000x1000, pure white)

## P2 Angle Variation
**Type**: angle
**Purpose**: Show product from different perspective
**Visual**: 45-degree angle, slight shadow for depth

## P3 Detail Close-up
**Type**: detail
**Purpose**: Highlight key feature or quality detail
**Visual**: Macro shot of texture/material/connection point

...
```

**After response**: Update `analysis.md` → Step 3

### Step 4: Confirmation 2 - Outline & Style & Platform Selection ⚠️

**Purpose**: User chooses strategy, confirms style and platform.

**Display each strategy**:
- Strategy name + image count + recommended style
- Image-by-image summary

**Use AskUserQuestion** with questions:

**Question 1: Outline Strategy**
- Strategy A (Product-focused)
- Strategy B (Lifestyle-focused)
- Strategy C (Information-focused)
- Combine: specify images from each

**Question 2: Visual Style**
- Use strategy's recommended style
- Or select from: minimal / premium / lifestyle / bold / soft / tech / natural / luxury
- Or type custom style description

**Question 3: Platform**
- Use strategy's recommended platform
- Or select: amazon / shopify / ebay / etsy / taobao / jd / pinduoduo
- Custom: specify requirements

**Question 4: Scene Type**
- Use strategy's recommended scene
- Or select: studio / lifestyle / contextual / exploded / comparison / infographic

**After response**:
- Single strategy → copy to `outline.md` with confirmed settings
- Combination → merge specified images
- Update `outline.md` frontmatter with final settings

### Step 5: Generate Images

With confirmed outline + style + scene + platform:

**Visual Consistency — Reference Image Chain**:

1. **Check for user-provided reference images** (`--ref` option)
   - If provided: Use as primary style reference
   - If not provided: Use internal reference chain (see below)

2. **Internal Reference Chain** (when no user ref provided):
   - **Generate image 1 (hero) FIRST** — without `--ref`
   - **Use image 1 as `--ref` for ALL remaining images** (2, 3, ..., N)

**For each image**:
1. Save prompt to `prompts/NN-{type}-[slug].md`
   - **Backup rule**: If exists, rename to `prompts/NN-{type}-[slug]-backup-YYYYMMDD-HHMMSS.md`
   - Include reference image paths in prompt
2. Generate image:
   - **With user ref**: `--ref <user-reference.png>` for all images
   - **Image 1 (no user ref)**: Generate without `--ref` (establishes visual anchor)
   - **Images 2+ (no user ref)**: Generate with `--ref <image-01-path>`
   - **Backup rule**: If image exists, rename with timestamp
3. Report progress after each generation

**Reference Image Best Practices**:

| Reference Type | Usage | Effect |
|----------------|-------|--------|
| Style reference | Brand guideline images | Maintains brand consistency |
| Competitor reference | Similar product images | Matches category standards |
| Internal chain (image 1) | First generated image | Ensures series consistency |

**Platform Compliance**:
- Apply platform-specific requirements automatically
- Amazon: Pure white background for main image
- Size adjustments based on platform

**Session Management**:
Use consistent session ID for all images in the set: `product-{slug}-{timestamp}`

### Step 6: Completion Report

```
Product Image Set Complete!

Product: [product name]
Strategy: [A/B/C/Combined]
Style: [style name]
Scene: [scene type]
Platform: [platform] (requirements applied)
Location: [directory path]
Images: N total

✓ analysis.md
✓ outline-strategy-a.md
✓ outline-strategy-b.md
✓ outline-strategy-c.md
✓ outline.md (selected: [strategy])

Files:
- 01-hero-[slug].png ✓ Main image ([platform] compliant)
- 02-angle-[slug].png ✓ Angle variation
- 03-detail-[slug].png ✓ Detail shot
...
```

## Image Modification

| Action | Steps |
|--------|-------|
| **Edit** | Update prompt file FIRST → Regenerate with same session ID |
| **Add** | Specify position → Create prompt → Generate → Renumber files |
| **Delete** | Remove files → Renumber subsequent → Update outline |

## Platform-Specific Guidelines

### Amazon
- Main image: Pure white background (RGB 255,255,255)
- Minimum 1000x1000 pixels for zoom feature
- Product must fill 85%+ of frame
- No text, logos, or watermarks on main image
- Additional images: lifestyle, infographic, comparison allowed

### Shopify
- Recommended 1024x1024 or 4:3 aspect ratio
- More flexible styling
- Lifestyle images perform well
- Consistent style across all product images

### eBay
- Minimum 500x500 pixels
- White background preferred but not required
- Up to 12 free images per listing

## Content Breakdown Principles

1. **Hero Image (Image 1)**: Main product shot, platform-compliant
2. **Angle Variations**: Show product from multiple perspectives
3. **Detail Shots**: Highlight quality, features, materials
4. **Lifestyle/Context**: Product in use, emotional connection
5. **Infographic**: Features, specs, benefits with callouts
6. **Comparison**: Before/after, vs alternatives
7. **Social Proof**: Reviews, testimonials (if applicable)

## References

Detailed templates in `references/` directory:

**Elements**:
- `elements/scene-guide.md` - Scene types and compositions
- `elements/lighting.md` - Lighting setups and moods
- `elements/composition.md` - Framing and composition rules

**Presets**:
- `presets/<style>.md` - Style definitions and prompts

**Workflows**:
- `workflows/analysis-framework.md` - Product analysis
- `workflows/outline-template.md` - Outline templates
- `workflows/prompt-assembly.md` - Prompt assembly

**Platforms**:
- `platforms/amazon.md` - Amazon requirements
- `platforms/shopify.md` - Shopify requirements
- `platforms/ebay.md` - eBay requirements
- `platforms/etsy.md` - Etsy requirements
- `platforms/taobao.md` - Taobao requirements
- `platforms/jd.md` - JD.com requirements
- `platforms/pinduoduo.md` - Pinduoduo requirements

**Config**:
- `config/preferences-schema.md` - EXTEND.md schema
- `config/watermark-guide.md` - Watermark configuration

## Notes

- Auto-retry once on failure
- Platform requirements auto-applied
- Two confirmation points required (Steps 2 & 4)
- Reference image chain ensures visual consistency

## Extension Support

Custom configurations via EXTEND.md. See **Step 0** for paths.
