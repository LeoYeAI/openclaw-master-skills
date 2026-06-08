# First-Time Setup

When EXTEND.md is not found, run first-time setup with AskUserQuestion.

## Questions (Single Call)

### Question 1: Default Platform

**Header**: Platform

**Options**:
- `amazon` - Largest marketplace, strict image requirements
- `shopify` - Flexible, brand-focused stores
- `ebay` - Auction and fixed price, global reach
- `etsy` - Handmade and vintage, lifestyle focus
- `taobao` - China's largest C2C platform
- `jd` - China's premium B2C platform
- `pinduoduo` - China's value-focused platform
- `no preference` - Generic e-commerce settings

### Question 2: Default Style

**Header**: Visual Style

**Options**:
- `minimal` - Clean, white background, product-focused
- `premium` - Sophisticated, elegant lighting
- `lifestyle` - Product in natural use context
- `bold` - High contrast, vibrant colors
- `soft` - Gentle lighting, warm tones
- `tech` - Futuristic, sleek, modern
- `natural` - Organic, eco-friendly aesthetic
- `luxury` - Rich colors, dramatic lighting

### Question 3: Watermark

**Header**: Watermark

**Options**:
- `Enable` - Add brand watermark to images
- `Disable` - No watermark (Recommended for Amazon)

If enabled, follow up with text and position questions.

### Question 4: Language

**Header**: Language

**Options**:
- `Chinese` - Generate prompts in Chinese
- `English` - Generate prompts in English
- `Auto-detect` - Match input language (Recommended)

## Saving Preferences

After user selection, save to EXTEND.md:

**Project-level**: `.teamclaw-skills/product-image-generator/EXTEND.md`

**User-level**: `$HOME/.teamclaw-skills/product-image-generator/EXTEND.md`

## Example EXTEND.md

```json
{
  "platform": "amazon",
  "style": "minimal",
  "scene": "studio",
  "watermark": {
    "enabled": false,
    "text": "",
    "position": "bottom-right"
  },
  "language": "auto"
}
```

## Display After Setup

Show confirmation:

```
Preferences saved to [location]:
- Platform: [selected]
- Style: [selected]
- Watermark: [enabled/disabled]
- Language: [selected]

Starting product analysis...
```
