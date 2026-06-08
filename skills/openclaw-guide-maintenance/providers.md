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

| Provider | Model Format | Auth Method (Env Var) |
|---|---|---|
| Anthropic | `anthropic/claude-*` (e.g. `anthropic/claude-opus-4-6`) | API key or OAuth (`ANTHROPIC_API_KEY`) |
| OpenAI | `openai/gpt-*` (e.g. `openai/gpt-5.4`) | API key or Codex OAuth (`OPENAI_API_KEY`) |
| OpenAI Codex | `openai-codex/*` | Codex OAuth (`OPENAI_API_KEY`) |
| OpenCode Zen | `opencode/*` (e.g. `opencode/claude-opus-4-6`) | API key (`OPENCODE_API_KEY`) |
| Google (Gemini) | `google/*` (e.g. `google/gemini-3.1-pro-preview`) | API key (`GOOGLE_API_KEY`) |
| Google Vertex AI | `google-vertex/*` | GCP credentials |
| Venice AI | `venice/llama-*`, `venice/claude-*` | API key (`VENICE_API_KEY`) |
| Z.AI | `zai/*` (e.g. `zai/glm-5`) | API key (`ZAI_API_KEY`) |
| Vercel AI Gateway | via gateway config | API key (`AI_GATEWAY_API_KEY`) |
| Kilocode | `kilocode/*` | API key (`KILOCODE_API_KEY`) |
| OpenRouter | `openrouter/*` | API key (`OPENROUTER_API_KEY`) |
| MiniMax | `minimax/*` | API key (`MINIMAX_API_KEY`). Includes `MiniMax-M2.5-highspeed` (v2026.3.2) |
| Moonshot AI (Kimi) | `moonshot/*` (e.g. `moonshot/kimi-k2.5`) | API key (`MOONSHOT_API_KEY`) |
| Kimi Coding | `kimi-coding/*` (e.g. `kimi-coding/k2p5`) | API key (`KIMI_API_KEY`) |
| Together AI | `together/*` | API key (`TOGETHER_API_KEY`) |
| Mistral | `mistral/*` | API key (`MISTRAL_API_KEY`) |
| Groq | `groq/*` | API key (`GROQ_API_KEY`) |
| xAI | `xai/*` | API key (`XAI_API_KEY`) |
| GitHub Copilot | `github-copilot/*` | GitHub token (`GH_TOKEN`) |
| Hugging Face | `huggingface/*` | API key (`HF_TOKEN`) |
| NVIDIA | `nvidia/*` | API key (`NVIDIA_API_KEY`) |
| Volcengine | `volcengine/*` | API key (`VOLCANO_ENGINE_API_KEY`) |
| BytePlus | `byteplus/*` | API key (`BYTEPLUS_API_KEY`) |
| Cerebras | `cerebras/*` | API key (`CEREBRAS_API_KEY`) |
| Xiaomi | `xiaomi/*` | API key (`XIAOMI_API_KEY`) |
| Qianfan | `qianfan/*` | API key (`QIANFAN_API_KEY`) |
| GLM | `glm/*` | API key (`GLM_API_KEY`) |
| Qwen | `qwen/*` | OAuth |
| Amazon Bedrock | `bedrock/*` | AWS credentials |
| Cloudflare AI Gateway | via gateway config | API key |
| LiteLLM | via unified gateway | API key |

### Local Providers

| Provider | Notes |
|---|---|
| Ollama | `ollama/*` — local models |
| vLLM | `vllm/*` — local models |
| SGLang | `sglang/*` — local models |

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
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "openai/gpt-5.2": { alias: "GPT" },
        "openai/gpt-5.4": { alias: "GPT-5.4" },
        "google/gemini-3.1-pro-preview": { alias: "Gemini" },
        "moonshot/kimi-k2.5": { alias: "Kimi" },
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
