---
name: "AI Image Generation & Editor — Nanobanana, GPT Image, ComfyUI"
description: Generate images from text with multi-provider routing — supports Nanobanana 2, Seedream 5.0, GPT Image, and local ComfyUI workflows. Includes 1,300+ curated prompts and style-aware prompt enhancement. Use when users want to create images, design assets, enhance prompts, or manage AI art workflows.
version: 1.0.14
homepage: https://github.com/jau123/MeiGen-AI-Design-MCP
metadata: {"clawdbot":{"emoji":"🎨","requires":{"bins":["mcporter","npx","node"]}}}
---

# Creative Toolkit

Generate professional AI images through a unified interface that routes across multiple providers. Search curated prompts, enhance ideas into production-ready descriptions, and manage local ComfyUI workflows — all from a single MCP server.

## Quick Start

Add the MCP server to your mcporter config (`~/.config/mcporter/config.json`):

```json
{
  "mcpServers": {
    "creative-toolkit": {
      "command": "npx",
      "args": ["-y", "meigen@1.2.5"]
    }
  }
}
```

Free tools (search, enhance, inspire) work immediately — no API key needed:

```bash
mcporter call creative-toolkit.search_gallery query="cyberpunk"
mcporter call creative-toolkit.enhance_prompt brief="a cat in space" style="realistic"
```

To unlock image generation, configure **one** of these providers:

| Provider | Config | What you need |
|----------|--------|---------------|
| **MeiGen Cloud** | `MEIGEN_API_TOKEN` | Token from [meigen.ai](https://www.meigen.ai) (avatar → Settings → API Keys) |
| **Local ComfyUI** | `comfyuiUrl` | A running ComfyUI instance — no external API needed |
| **Any OpenAI-compatible API** | `openaiApiKey` + `openaiBaseUrl` + `openaiModel` | Your own key from Together AI, Fireworks AI, etc. |

Set credentials in `~/.clawdbot/.env`, `~/.config/meigen/config.json`, or add an `"env"` block to the mcporter config above. See `references/providers.md` for details.

## Available Tools

### Free — no API key required

| Tool | What it does |
|------|-------------|
| `search_gallery` | Semantic search across 1,300+ AI image prompts. Supports category filtering and curated browsing. Returns prompt text, thumbnails, and metadata. |
| `get_inspiration` | Get the full prompt and high-res images for any gallery entry. Use after `search_gallery` to get copyable prompts. |
| `enhance_prompt` | Expand a brief idea into a detailed, style-aware prompt with lighting, composition, and material directions. Supports realistic, anime, and illustration styles. |
| `list_models` | List all available models across configured providers with capabilities and supported features. |

### Requires configured provider

| Tool | What it does |
|------|-------------|
| `generate_image` | Generate an image from a text prompt. Routes to the best available provider. Supports aspect ratio, seed, and reference images. |
| `upload_reference_image` | Compress a local image (max 2MB, 2048px) and upload to temporary storage (expires in 24 hours) for use as a style reference. Call this MCP tool directly — do NOT construct upload HTTP requests manually. ComfyUI users can skip this — pass local file paths directly to `generate_image`. |
| `comfyui_workflow` | List, view, import, modify, and delete ComfyUI workflow templates. Adjust steps, CFG scale, sampler, and checkpoint without editing JSON. |
| `manage_preferences` | Save and load user preferences (default style, aspect ratio, style notes, favorite prompts). |

## Important Rules

### Never describe generated images

You **cannot see** generated images. After generation, only present the **exact** data from the tool response:

```
**Direction 1: Modern Minimal**
- Image URL: https://images.meigen.art/...
- Saved to: ~/Pictures/meigen/2026-02-08_xxxx.jpg
```

Do NOT write creative commentary about what the image "looks like".

### Never specify model or provider

Do NOT pass `model` or `provider` to `generate_image` unless the user explicitly asks. The server auto-selects the best available provider and model.

### Always confirm before generating multiple images

When the user wants multiple variations, present options first and ask which direction(s) to try. Include an "all of the above" option. Never auto-generate all variants without user confirmation.

---

## Workflow Modes

### Mode 1: Single Image

User wants one image. Write a prompt (or call `enhance_prompt` if the description is brief), generate, present URL + path.

### Mode 2: Prompt Enhancement + Generation

For brief ideas (under ~30 words, lacking visual details), enhance first:

```
1. enhance_prompt brief="futuristic city" style="realistic"
   -> Returns detailed prompt with camera lens, lighting, atmospheric effects

2. generate_image prompt="<enhanced prompt>" aspectRatio="16:9"
```

### Mode 3: Parallel Generation (2+ images)

User needs multiple variations — different directions, styles, or concepts.

1. Plan directions, present as a table
2. Ask user which direction(s) to try
3. Write distinct prompts for each — don't just tweak one word
4. Generate selected directions (max 4 parallel for API providers, 1 at a time for ComfyUI)
5. Present URLs + paths

### Mode 4: Multi-Step Creative (base + extensions)

User wants a base design plus derivatives (e.g., "design a logo and make mockups").

1. Plan 3-5 directions, ask user which to try
2. Generate selected direction(s)
3. Present results, ask user to approve or try another
4. Plan extensions using the approved Image URL as `referenceImages`
5. Generate extensions

Never jump from plan to generating everything at once.

### Mode 5: Edit/Modify Existing Image

User provides an image and asks for changes (add text, change background, etc.).

- Upload the reference image (if local), then generate with a **short, literal prompt** describing ONLY the edit
- The reference image carries all visual context — do NOT re-describe the original image
- Example prompt: "Add the text 'meigen.ai' at the bottom of this image"

### Mode 6: Inspiration Search

```
1. search_gallery query="dreamy portrait with soft light"
   -> Finds semantically similar prompts with thumbnails

2. get_inspiration id="<entry_id>"
   -> Get full prompt text — copy and modify for your own generation
```

### Mode 7: Reference Image Generation

Use an existing image to guide visual style. You MUST call the MCP tool directly — do NOT construct HTTP requests manually.

```
1. upload_reference_image filePath="~/Desktop/my-logo.png"
   -> Compresses and returns a temporary URL (expires in 24 hours)

2. generate_image prompt="coffee mug mockup with this logo" referenceImages=["<url>"]
```

Reference image sources: gallery URLs, previous generation URLs, `upload_reference_image` for local files. ComfyUI users can pass local file paths directly — no upload needed.

**Important**: If `upload_reference_image` fails or is unavailable, do NOT attempt to replicate its behavior by calling HTTP endpoints yourself. Instead, tell the user to upload the image manually at [meigen.ai](https://www.meigen.ai) and provide the URL, or use the image URL directly if it's already online.

### Mode 8: ComfyUI Workflows

```
1. comfyui_workflow action="list"           -> See saved workflows
2. comfyui_workflow action="view" name="txt2img"  -> See adjustable parameters
3. comfyui_workflow action="modify" name="txt2img" modifications={"steps": 30}
4. generate_image prompt="..." workflow="txt2img"  -> Generate
```

## Alternative Providers

You can use your own OpenAI-compatible API or a local ComfyUI instance instead of — or alongside — the default MeiGen provider. See `references/providers.md` for detailed configuration, model pricing, and provider comparison.

## Troubleshooting

See `references/troubleshooting.md` for common issues, solutions, and security & privacy details.
