---
name: first-time-setup
description: First-time setup and default model selection flow for baoyu-image-gen
---

# First-Time Setup

## Overview

Triggered when:
1. No EXTEND.md found → full setup (provider + model + preferences)
2. EXTEND.md found but `default_model.[provider]` is null → model selection only

## Setup Flow

```
No EXTEND.md found          EXTEND.md found, model null
        │                            │
        ▼                            ▼
┌─────────────────────┐    ┌──────────────────────┐
│ AskUserQuestion     │    │ AskUserQuestion      │
│ (full setup)        │    │ (model only)         │
└─────────────────────┘    └──────────────────────┘
        │                            │
        ▼                            ▼
┌─────────────────────┐    ┌──────────────────────┐
│ Create EXTEND.md    │    │ Update EXTEND.md     │
└─────────────────────┘    └──────────────────────┘
        │                            │
        ▼                            ▼
    Continue                     Continue
```

## Flow 1: No EXTEND.md (Full Setup)

**Language**: Use user's input language or saved language preference.

Use AskUserQuestion with ALL questions in ONE call:

### Question 1: Default Provider

```yaml
header: "Provider"
question: "Default image generation provider?"
options:
  - label: "Google (Recommended)"
    description: "Gemini multimodal - high quality, reference images, flexible sizes"
  - label: "OpenAI"
    description: "GPT Image - consistent quality, reliable output"
  - label: "OpenRouter"
    description: "Router for Gemini/FLUX/OpenAI-compatible image models"
  - label: "DashScope"
    description: "Alibaba Cloud - Qwen-Image, strong Chinese/English text rendering"
  - label: "Replicate"
    description: "Community models - nano-banana-pro, flexible model selection"
```

### Question 2: Default Google Model

Only show if user selected Google or auto-detect (no explicit provider).

```yaml
header: "Google Model"
question: "Default Google image generation model?"
options:
  - label: "gemini-3-pro-image-preview (Recommended)"
    description: "Highest quality, best for production use"
  - label: "gemini-3.1-flash-image-preview"
    description: "Fast generation, good quality, lower cost"
  - label: "gemini-3-flash-preview"
    description: "Fast generation, balanced quality and speed"
```

### Question 2b: Default OpenRouter Model

Only show if user selected OpenRouter.

```yaml
header: "OpenRouter Model"
question: "Default OpenRouter image generation model?"
options:
  - label: "google/gemini-3.1-flash-image-preview (Recommended)"
    description: "Best general-purpose OpenRouter image model with reference-image workflows"
  - label: "google/gemini-2.5-flash-image-preview"
    description: "Fast Gemini preview model on OpenRouter"
  - label: "black-forest-labs/flux.2-pro"
    description: "Strong text-to-image quality through OpenRouter"
```

### Question 3: Default Quality

```yaml
header: "Quality"
question: "Default image quality?"
options:
  - label: "2k (Recommended)"
    description: "2048px - covers, illustrations, infographics"
  - label: "normal"
    description: "1024px - quick previews, drafts"
```

### Question 4: Save Location

```yaml
header: "Save"
question: "Where to save preferences?"
options:
  - label: "Project (Recommended)"
    description: ".baoyu-skills/ (this project only)"
  - label: "User"
    description: "~/.baoyu-skills/ (all projects)"
```

### Save Locations

| Choice | Path | Scope |
|--------|------|-------|
| Project | `.baoyu-skills/baoyu-image-gen/EXTEND.md` | Current project |
| User | `$HOME/.baoyu-skills/baoyu-image-gen/EXTEND.md` | All projects |

### EXTEND.md Template

```yaml
---
version: 1
default_provider: [selected provider or null]
default_quality: [selected quality]
default_aspect_ratio: null
default_image_size: null
default_model:
  google: [selected google model or null]
  openai: null
  openrouter: [selected openrouter model or null]
  dashscope: null
  replicate: null
---
```

## Flow 2: EXTEND.md Exists, Model Null

When EXTEND.md exists but `default_model.[current_provider]` is null, ask ONLY the model question for the current provider.

### Google Model Selection

```yaml
header: "Google Model"
question: "Choose a default Google image generation model?"
options:
  - label: "gemini-3-pro-image-preview (Recommended)"
    description: "Highest quality, best for production use"
  - label: "gemini-3.1-flash-image-preview"
    description: "Fast generation, good quality, lower cost"
  - label: "gemini-3-flash-preview"
    description: "Fast generation, balanced quality and speed"
```

### OpenAI Model Selection

```yaml
header: "OpenAI Model"
question: "Choose a default OpenAI image generation model?"
options:
  - label: "gpt-image-1.5 (Recommended)"
    description: "Latest GPT Image model, high quality"
  - label: "gpt-image-1"
    description: "Previous generation GPT Image model"
```

### OpenRouter Model Selection

```yaml
header: "OpenRouter Model"
question: "Choose a default OpenRouter image generation model?"
options:
  - label: "google/gemini-3.1-flash-image-preview (Recommended)"
    description: "Recommended for image output and reference-image edits"
  - label: "google/gemini-2.5-flash-image-preview"
    description: "Fast preview-oriented image generation"
  - label: "black-forest-labs/flux.2-pro"
    description: "High-quality text-to-image through OpenRouter"
```

### DashScope Model Selection

```yaml
header: "DashScope Model"
question: "Choose a default DashScope image generation model?"
options:
  - label: "qwen-image-2.0-pro (Recommended)"
    description: "Best DashScope model for text rendering and custom sizes"
  - label: "qwen-image-2.0"
    description: "Faster 2.0 variant with flexible output size"
  - label: "qwen-image-max"
    description: "Legacy Qwen model with five fixed output sizes"
  - label: "qwen-image-plus"
    description: "Legacy Qwen model, same current capability as qwen-image"
  - label: "z-image-turbo"
    description: "Legacy DashScope model for compatibility"
  - label: "z-image-ultra"
    description: "Legacy DashScope model, higher quality but slower"
```

Notes for DashScope setup:

- Prefer `qwen-image-2.0-pro` when the user needs custom `--size`, uncommon ratios like `21:9`, or strong Chinese/English text rendering.
- `qwen-image-max` / `qwen-image-plus` / `qwen-image` only support five fixed sizes: `1664*928`, `1472*1104`, `1328*1328`, `1104*1472`, `928*1664`.
- In `baoyu-image-gen`, `quality` is a compatibility preset. It is not a native DashScope parameter.

### Replicate Model Selection

```yaml
header: "Replicate Model"
question: "Choose a default Replicate image generation model?"
options:
  - label: "google/nano-banana-pro (Recommended)"
    description: "Google's fast image model on Replicate"
  - label: "google/nano-banana"
    description: "Google's base image model on Replicate"
```

### Update EXTEND.md

After user selects a model:

1. Read existing EXTEND.md
2. If `default_model:` section exists → update the provider-specific key
3. If `default_model:` section missing → add the full section:

```yaml
default_model:
  google: [value or null]
  openai: [value or null]
  openrouter: [value or null]
  dashscope: [value or null]
  replicate: [value or null]
```

Only set the selected provider's model; leave others as their current value or null.

## After Setup

1. Create directory if needed
2. Write/update EXTEND.md with frontmatter
3. Confirm: "Preferences saved to [path]"
4. Continue with image generation
