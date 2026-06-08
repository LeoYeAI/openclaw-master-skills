# Watermark Guide

## Configuration

Watermarks are configured in EXTEND.md:

```json
{
  "watermark": {
    "enabled": true,
    "text": "YourBrand",
    "position": "bottom-right"
  }
}
```

## Position Options

| Position | Description |
|----------|-------------|
| `bottom-right` | Bottom right corner (default) |
| `bottom-left` | Bottom left corner |
| `top-right` | Top right corner |
| `top-left` | Top left corner |
| `center` | Center, low opacity |

## Platform Compliance

⚠️ **Important**: Some platforms have restrictions on watermarks:

| Platform | Main Image | Additional Images |
|----------|------------|-------------------|
| Amazon | ❌ Not allowed | ⚠️ Not recommended |
| eBay | ⚠️ Allowed (subtle) | ✅ Allowed |
| Etsy | ✅ Allowed | ✅ Allowed |
| Shopify | ✅ Allowed | ✅ Allowed |
| Taobao | ✅ Allowed | ✅ Allowed |
| JD | ⚠️ Subtle only | ✅ Allowed |
| Pinduoduo | ⚠️ Subtle only | ✅ Allowed |

## Prompt Integration

When watermark is enabled, add to image generation prompts:

```
Include a subtle watermark "[text]" positioned at [position].
The watermark should be legible but not distracting from the main product.
Opacity: 60-80% for additional images, not applicable for main product images.
```

## Best Practices

1. **Keep it subtle** - Watermark should not distract from product
2. **Consistent placement** - Same position across all images
3. **Platform compliance** - Check platform rules before enabling
4. **Brand consistency** - Use same watermark across all product images
