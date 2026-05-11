# Provider Comparison & Configuration

## Provider Comparison

| | MeiGen Platform | OpenAI-Compatible | ComfyUI (Local) |
|---|---|---|---|
| **Models** | Nanobanana 2, Seedream 5.0, GPT Image 1.5, etc. | Any model at the endpoint | Any checkpoint on your machine |
| **Reference images** | Native support | Depends on your model/provider | Requires LoadImage node |
| **Concurrency** | Up to 4 parallel | Up to 4 parallel | 1 at a time (GPU constraint) |
| **Latency** | 10-30s typical | Varies by provider | Depends on hardware |
| **Cost** | Token-based credits | Provider billing | Free (your hardware) |
| **Offline** | No | No | Yes |

## Alternative Provider Configuration

Save to `~/.config/meigen/config.json`:

**OpenAI-compatible API (Together AI, Fireworks AI, DeepInfra, etc.):**

```json
{
  "openaiApiKey": "sk-...",
  "openaiBaseUrl": "https://api.together.xyz/v1",
  "openaiModel": "black-forest-labs/FLUX.1-schnell"
}
```

**Local ComfyUI:**

```json
{
  "comfyuiUrl": "http://localhost:8188"
}
```

Import workflows with the `comfyui_workflow` tool (action: `import`). The server auto-detects key nodes (KSampler, CLIPTextEncode, EmptyLatentImage) and fills in prompt, seed, and dimensions at runtime.

Multiple providers can be configured simultaneously. Auto-detection priority: MeiGen > ComfyUI > OpenAI-compatible.

## MeiGen Model Pricing

| Model | Credits | 4K | Best For |
|-------|---------|-----|----------|
| Nanobanana 2 (default) | 5 | Yes | General purpose, high quality |
| Seedream 5.0 Lite | 5 | Yes | Fast, stylized imagery |
| GPT Image 1.5 | 2 | No | Budget-friendly |
| Nanobanana Pro | 10 | Yes | Premium quality |
| Seedream 4.5 | 5 | Yes | Stylized, wide ratio support |
| Midjourney Niji 7 | 15 | No | Anime and illustration |

When no model is specified, the server defaults to Nanobanana 2.

## Prompt Enhancement Styles

`enhance_prompt` supports three style modes:

| Style | Focus | Best For |
|-------|-------|----------|
| `realistic` | Camera lens, aperture, focal length, lighting direction, material textures | Product photos, portraits, architecture |
| `anime` | Key visual composition, character details (eyes, hair, costume), trigger words | Anime illustrations, character design |
| `illustration` | Art medium, color palette, composition direction, brush texture | Concept art, digital painting, watercolor |
