# Infographic Modes & Parameters

## mode (Scenario Type)

| mode | Description | Required Parameters |
|------|-------------|-------------------|
| `article` | Convert a topic or long-form text into an infographic. `--article` can carry either user-provided long-form text or complete content expanded/planned by the Agent based on a topic | `--article` |
| `reference` | Generate an infographic based on a reference image | `--reference-type` + `--reference-image-urls` |

> Note: The script layer still supports `--mode topic --topic` for compatibility, but the skill no longer recommends it. All text-based infographic requests should use `article`.

## reference_type (Reference Image Sub-scenarios)

Only used when `mode=reference`.

| reference_type | Description | Required Parameters | Typical Scenario |
|---------------|-------------|-------------------|-----------------|
| `sketch` | Sketch/hand-drawn to infographic | `--reference-image-urls` | User uploads hand-drawn image, whiteboard photo |
| `style_transfer` | Mimic reference image style | `--reference-image-urls` + (`--reference-topic` or `--reference-article`) | User uploads existing infographic as style reference |
| `product_embed` | Embed product/character into infographic | `--reference-image-urls` + `--reference-article` | User uploads product/character image with selling points/description; differs from style_transfer (style_transfer uses the reference as a style sample, product_embed uses the reference as the product/character to embed into the scene) |
| `content_rewrite` | Rewrite text content in reference image | `--reference-image-urls` + (`--reference-article` or `--reference-topic`) | User uploads infographic, only replacing text |

> Note: In reference mode, if the caller mistakenly puts content in `--article`, the script will auto-map it to `--reference-article`. However, callers should pass `--reference-article` directly.

## child_reference_type (Batch Mode Sub-task Strategy)

Only effective when `count >= 2`.

| child_reference_type | Description | Use Case |
|---------------------|-------------|----------|
| `style_transfer` (default) | Each image generated independently, roughly consistent style but layout may vary | Series with diverse content |
| `content_rewrite` | Strictly maintains base image layout and style, only replaces text content | Coherent paginated series |

## action (Retry Actions)

| action | Description | Requires `--last-task-id` |
|--------|-------------|--------------------------|
| `repeat_last_task` | Regenerate (same content and style) | Yes |
| `switch_style` | Retry with different style (same content) | Yes |
| `switch_content` | Retry with different content (same style) | Yes |
| `switch_all` | Change both content and style | Yes |

### Retry Rules for Reference Image Mode

- Text mode (article/topic) retry: pass `--action` + `--last-task-id` + `--article`
- Reference image mode retry: also requires `--mode reference` + `--reference-type` + `--reference-image-urls`
- `action=switch_content`: must pass `--article` as new content
- `action=switch_style`: must pass `--article` to preserve original content context
- `reference_type=content_rewrite` / `style_transfer` with `action=switch_style`: executor will downgrade to `switch_all` (style comes from reference image)

## Other Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--style-hint` | Style keywords (max 10 chars), e.g. "minimalist", "cyberpunk" | None |
| `--aspect-ratio` | Image ratio: `3:4` / `4:3` / `1:1` / `16:9` / `9:16` | `3:4` |
| `--locale` | Text language: `zh-CN` / `en-US` / `ja-JP` etc. | `zh-CN` |
| `--count` | Generation count, 1-10, >=2 triggers batch mode | `1` |
| `--template-id` | Specify template ID, skip auto-matching | None |
| `--article-summary` | Article summary (optional for mode=article) | None |
