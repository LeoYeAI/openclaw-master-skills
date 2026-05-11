# Structured Prompt Guide for Gemini Image Generation

A human-readable reference for crafting optimized image prompts manually.

## The Core Principle

**Specificity beats creativity.** A technically precise prompt with real camera specs, lighting setups, and material descriptions produces better results than a poetically written but vague one.

## Golden Rules

1. **One subject, one focal point** — Don't try to fit everything in
2. **Real equipment names** — "Sony A7IV with 35mm f/1.4" beats "professional camera"
3. **Real film stocks** — "Kodak Portra 400" gives warm skin tones, "CineStill 800T" gives cinematic halation
4. **Real art references** — "Studio Ghibli" or "Makoto Shinkai" for anime, "Dalí" for surreal
5. **Specific colors** — "cadmium yellow and cerulean blue" beats "colorful"
6. **Lighting direction** — "warm key light from left, cool fill from right" beats "good lighting"
7. **Always include negatives** — Tell the model what NOT to do
8. **No text in images** — Gemini renders text poorly, always add "no text" to negatives

## Style Cheat Sheet

### Want photorealism?
→ Add camera + lens + film stock + "8K, photorealistic, RAW photo"

### Want illustration?
→ Add medium + technique + artist reference + "trending on ArtStation"

### Want anime?
→ Add studio reference + line weight + shading style + "anime key visual"

### Want 3D?
→ Add render engine + material type + "raytraced, 8K render"

### Want traditional art?
→ Add paper type + brush type + technique + "visible texture, fine art quality"

## Film Stock Reference

| Film Stock | Look | Best For |
|-----------|------|----------|
| Kodak Portra 400 | Warm, creamy skin tones, soft colors | Portraits, lifestyle |
| Kodak Ektar 100 | Vivid, saturated, fine grain | Landscapes, travel |
| Fujifilm Pro 400H | Cool pastels, muted greens | Fashion, editorial |
| CineStill 800T | Tungsten balanced, halation, cinematic | Night, neon, moody |
| Ilford HP5 | Classic B&W, medium contrast | Drama, street |
| Kodak Tri-X 400 | Gritty B&W, high contrast | Documentary, raw |

## Lens Guide

| Focal Length | Use |
|-------------|-----|
| 24mm f/1.4 | Wide landscapes, environmental portraits, epic scenes |
| 35mm f/1.4 | Street, documentary, "natural eye" feel |
| 50mm f/1.2 | Standard portraits, low light, everyday |
| 85mm f/1.8 | Portrait king, beautiful bokeh, compression |
| 135mm f/2 | Headshots, subject isolation, dreamy background |
| 90mm macro | Product, food, small details |

## Camera Bodies

| Camera | Known For |
|--------|-----------|
| Sony A7IV | All-rounder, great low light |
| Hasselblad X2D | Medium format, insane detail, fashion |
| Canon R5 | Color science, portraits |
| ARRI Alexa 65 | Cinema, Hollywood blockbuster look |
| Leica M11 | Street photography, documentary, character |
