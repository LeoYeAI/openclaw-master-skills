# Preferences Schema

EXTEND.md supports the following options:

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

## Options

### platform
Default platform preference for image generation.
- `amazon` - Pure white background, 1000x1000+
- `shopify` - Flexible, lifestyle-friendly
- `ebay` - White background preferred
- `etsy` - Lifestyle shots encouraged
- `taobao` - Infographic style popular
- `jd` - Clean, professional
- `pinduoduo` - Value-focused

### style
Default visual style preference.
- `minimal` - Clean, white background
- `premium` - Sophisticated, elegant
- `lifestyle` - In-context, natural
- `bold` - High contrast, vibrant
- `soft` - Gentle, warm tones
- `tech` - Futuristic, sleek
- `natural` - Organic, earthy
- `luxury` - Rich, dramatic

### scene
Default scene type preference.
- `studio` - Pure background, professional
- `lifestyle` - Real usage scenarios
- `contextual` - Staged environment
- `exploded` - Component breakdown
- `comparison` - Before/after
- `infographic` - With text overlays

### watermark
Watermark configuration.

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | boolean | Enable or disable watermark |
| `text` | string | Watermark text content |
| `position` | string | Position: bottom-right, bottom-left, top-right, top-left, center |

### language
Language preference for prompts.
- `auto` - Auto-detect from input
- `zh` - Chinese
- `en` - English
