# fal.ai Image Tools Quick Reference

## Three Tools at a Glance

| Tool | Purpose | Basic Usage |
|------|---------|-------------|
| **fal-text-to-image** | Generate from scratch | `uv run python fal-text-to-image "prompt"` |
| **fal-image-remix** | Transform existing images | `uv run python fal-image-remix input.jpg "style"` |
| **fal-image-edit** | Edit specific regions | `uv run python fal-image-edit input.jpg mask.png "edit"` |

## Common Workflows

### Generate → Remix → Edit
```bash
# 1. Create base
uv run python fal-text-to-image "office space" -o base.png

# 2. Apply style
uv run python fal-image-remix base.png "cyberpunk" -o styled.png

# 3. Fine-tune
uv run python fal-image-edit styled.png --mask-prompt "desk" "add hologram"
```

### Quick Iterations
```bash
# Generate with seed
uv run python fal-text-to-image "landscape" --seed 42 -o v1.png

# Remix same seed
uv run python fal-image-remix v1.png "oil painting" --seed 42 -o v2.png
```

## Key Parameters

### Strength Values
| Range | Text-to-Image | Image Remix | Image Edit |
|-------|---------------|-------------|------------|
| N/A | N/A | 0.3-0.5: Subtle | 0.5-0.7: Minor edits |
| N/A | N/A | 0.5-0.7: Moderate | 0.7-0.9: Clear edits |
| N/A | N/A | 0.7-0.85: Strong | 0.9-1.0: Full replacement |
| N/A | N/A | 0.85-1.0: Maximum | N/A |

### Model Selection Shortcuts

**Text-to-Image:**
- Typography/logos → `recraft/v3/text-to-image`
- Professional photos → `flux-pro/v1.1-ultra`
- General/fast/free → `flux-2`

**Image Remix:**
- General/free → `flux-2/dev`
- Premium quality → `flux-1.1-pro`
- Artistic styles → `stable-diffusion-v35`
- Vector/illustration → `recraft/v3`

**Image Edit:**
- Inpainting → `flux-2/fill` (default)
- Premium inpainting → `flux-pro-v11/fill`
- General edits (no mask) → `flux-2/redux`
- Artistic edits → `stable-diffusion-v35/inpainting`

## Common Flags

| Flag | Purpose | Example |
|------|---------|---------|
| `-m MODEL` | Specify model | `-m flux-pro/v1.1-ultra` |
| `-o FILE` | Output path | `-o result.png` |
| `--seed N` | Reproducibility | `--seed 42` |
| `-s N` (text-to-image) | Image size | `-s 1024x1024` |
| `-s N` (remix/edit) | Strength | `-s 0.8` |
| `--guidance N` | Prompt adherence | `--guidance 7.5` |
| `--steps N` | Inference steps | `--steps 50` |
| `--mask-prompt TEXT` | Auto-mask (edit only) | `--mask-prompt "sky"` |

## Troubleshooting Quick Fixes

| Problem | Fix |
|---------|-----|
| Too much transformation | Reduce `--strength` |
| Not enough change | Increase `--strength` |
| Wrong style | Try different model with `-m` |
| Mask not precise | Use manual mask instead of `--mask-prompt` |
| Low quality | Use premium model (flux-pro, flux-1.1-pro) |
| Too slow | Use faster model (flux-2/dev, flux-2) |
| Cost concerns | Use flux-2/dev (100 free requests) |

## Mask Creation Tips (for Image Edit)

**In image editor:**
1. Open source image
2. Create new layer
3. Paint white on areas to edit
4. Paint black on areas to preserve
5. Save as PNG

**Quick mask from prompt:**
```bash
# No mask file needed
uv run python fal-image-edit input.jpg --mask-prompt "object to edit" "change description"
```

## Cost Optimization

| Need | Model Choice | Why |
|------|--------------|-----|
| Learning/testing | `flux-2/dev` | 100 free requests |
| Production quality | `flux-1.1-pro` or `flux-pro-v11` | Best quality |
| Typography | `recraft/v3` | $0.04/image, excellent text |
| Batch processing | `flux-2` or `stable-diffusion-v35` | Lower cost |

## Setup Reminder

```bash
# Set API key (do once)
export FAL_KEY="your-api-key-here"

# Or create .env file in skill directory
echo "FAL_KEY=your-api-key-here" > .env
```

Get API key: https://fal.ai/dashboard/keys

---

**Full documentation:** See SKILL.md for complete details
**Getting started:** See README.md for setup and examples
