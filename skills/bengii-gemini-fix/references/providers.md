# OpenClaw Model Providers Reference

## Table of Contents

- [Quick Start](#quick-start)
- [Supported Providers](#supported-providers)
- [CLI Commands](#cli-commands)
- [Configuration](#configuration)
- [Model Fallbacks](#model-fallbacks)
- [Auth Profiles](#auth-profiles)
- [Transcription Providers](#transcription-providers)
- [Local Models](#local-models)

## Quick Start

1. Authenticate with provider (usually via `openclaw onboard` or `openclaw models auth add`)
2. Set default model in config or CLI

```bash
openclaw models set anthropic/claude-sonnet-4-5
```

## Supported Providers

### Highlight: Venice AI (Privacy-Focused)

- Default: `venice/llama-3.3-70b`
- Best overall: `venice/claude-opus-45` (strongest model offered)

Venice AI is highlighted as a recommended provider for privacy-conscious deployments.

### Cloud Providers

| Provider | Model Format | Auth Method |
|---|---|---|
| Anthropic | `anthropic/claude-*` | API key or OAuth |
| OpenAI | `openai/gpt-*` | API key or Codex OAuth |
| Venice AI | `venice/llama-*`, `venice/claude-*` | API key |
| OpenRouter | `openrouter/*` | API key |
| Google (Gemini) | `google/*` | API key |
| Together AI | `together/*` | API key |
| Mistral | `mistral/*` | API key |
| Moonshot AI (Kimi) | `moonshot/*` | API key |
| Amazon Bedrock | `bedrock/*` | AWS credentials |
| Qwen | `qwen/*` | OAuth |
| Hugging Face | `huggingface/*` | API key |
| NVIDIA | `nvidia/*` | API key |
| Cloudflare AI Gateway | via gateway config | API key |
| Vercel AI Gateway | via gateway config | API key |
| LiteLLM | via unified gateway | API key |
| Kilocode | `kilocode/*` | API key |
| Z.AI | `zai/*` | API key |
| Xiaomi | `xiaomi/*` | API key |
| GLM | `glm/*` | API key |
| MiniMax | `minimax/*` | API key | Includes `MiniMax-M2.5-highspeed` (v2026.3.2) |
| Qianfan | `qianfan/*` | API key | |
| OpenCode Zen | `opencode/*` | API key | |

### Local Providers

| Provider | Notes |
|---|---|
| Ollama | `ollama/*` — local models |
| vLLM | `vllm/*` — local models |

## CLI Commands

```bash
# Model management
openclaw models                     # Overview (alias for models status)
openclaw models list --all          # All available models
openclaw models list --local        # Local models only
openclaw models list --provider <p> # Filter by provider
openclaw models status              # Auth/token status
openclaw models status --probe      # Live probe auth profiles
openclaw models set <model>         # Set default primary
openclaw models set-image <model>   # Set default image model
openclaw models scan                # Scan for available models

# Fallbacks
openclaw models fallbacks list
openclaw models fallbacks add <model>
openclaw models fallbacks remove <model>
openclaw models fallbacks clear

# Image fallbacks
openclaw models image-fallbacks list|add|remove|clear

# Aliases
openclaw models aliases list
openclaw models aliases add <alias> <model>
openclaw models aliases remove <alias>

# Auth
openclaw models auth add                  # Interactive auth
openclaw models auth setup-token          # Token setup (default: anthropic)
openclaw models auth paste-token          # Paste existing token
openclaw models auth order get|set|clear  # Auth profile priority
```

## Configuration

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-5",
        fallbacks: ["openai/gpt-5.2"],
      },
      imageModel: {
        primary: "openai/dall-e-3",
      },
      models: {
        "anthropic/claude-sonnet-4-5": { alias: "Sonnet" },
        "openai/gpt-5.2": { alias: "GPT" },
      },
      imageMaxDimensionPx: 1200,    // Default 1200; reduces vision-token usage
    },
  },
}
```

- `agents.defaults.models` defines the model catalog and allowlist for `/model` command
- Model refs use `provider/model` format
- For custom/self-hosted providers, see Configuration Reference → Custom providers

### Prompt Caching

```json5
{
  agents: {
    defaults: {
      params: {
        cacheRetention: 300,    // Cache TTL in seconds
      },
    },
    list: [{
      id: "high-cache",
      params: { cacheRetention: 600 },  // Per-agent override
    }],
  },
}
```

Precedence: Job payload → Per-agent params → Agent defaults → Model defaults

### Thinking Defaults

| Provider | Default |
|---|---|
| Anthropic Claude 4.6 (+ Bedrock) | `adaptive` |
| Other reasoning-capable models | `low` |

Override per-agent: `agents.list[].thinking` or per-request via `/model`.

### OpenAI WebSocket Transport

OpenAI Responses API uses WebSocket-first by default (`transport: "auto"` with SSE fallback):

```json5
{
  agents: {
    defaults: {
      params: {
        openaiWsWarmup: true,   // Optional WS warm-up (default on for openai/*)
      },
    },
  },
}
```

## Model Fallbacks

When primary model fails, Gateway tries fallbacks in order:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["anthropic/claude-sonnet-4-5", "openai/gpt-5.2"],
      },
    },
  },
}
```

## Auth Profiles

Stored at: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`

```bash
# Check token status
openclaw models status --check      # Exit 1=expired/missing, 2=expiring

# Probe live
openclaw models status --probe
openclaw models status --probe-provider anthropic
```

## Transcription Providers

- Deepgram for audio transcription
- Mistral supports voice and memory embeddings (v2026.2.22+)

### Moonshot AI (Kimi)

- Supports `web_search` provider: `provider: "kimi"`
- Native video understanding provider
- Two-step `$web_search` tool flow with citation extraction

## Local Models

### Ollama

```bash
# Install Ollama, then:
openclaw models set ollama/llama3
```

Ollama also supports **memory embeddings** (v2026.3.2):

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "ollama",      // Use Ollama for memory embedding
        // fallback: "ollama",   // Or as fallback only
      },
    },
  },
}
```

### vLLM

```bash
openclaw models set vllm/my-model
```

See provider-specific docs at https://docs.openclaw.ai/providers/<provider>.
