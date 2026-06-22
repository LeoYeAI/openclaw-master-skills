---
name: awesome-free-llm-apis
description: Reference guide for permanent free-tier LLM APIs with rate limits, model lists, and OpenAI-compatible integration patterns.
triggers:
  - free LLM API
  - free AI API key
  - free GPT API
  - no cost LLM endpoint
  - free tier language model API
  - which LLM has a free API
  - free inference API
  - open source LLM free API
---

# Awesome Free LLM APIs

> Skill by [ara.so](https://ara.so) — Daily 2026 Skills collection.

A curated list of LLM providers offering **permanent free tiers** for text inference — no trial credits, no expiry. All endpoints listed are OpenAI SDK-compatible unless noted.

---

## Provider Overview

### Provider APIs (trained/fine-tuned by the company)

| Provider | Notable Models | Rate Limits | Region |
|---|---|---|---|
| [Cohere](https://dashboard.cohere.com/api-keys) | Command A, Command R+, Aya Expanse 32B | 20 RPM, 1K req/mo | 🇺🇸 |
| [Google Gemini](https://aistudio.google.com/app/apikey) | Gemini 2.5 Pro, Flash, Flash-Lite | 5–15 RPM, 100–1K RPD | 🇺🇸 (not EU/UK/CH) |
| [Mistral AI](https://console.mistral.ai/api-keys) | Mistral Large 3, Small 3.1, Ministral 8B | 1 req/s, 1B tok/mo | 🇪🇺 |
| [Zhipu AI](https://open.bigmodel.cn/usercenter/apikeys) | GLM-4.7-Flash, GLM-4.5-Flash, GLM-4.6V-Flash | Undocumented | 🇨🇳 |

### Inference Providers (host open-weight models)

| Provider | Notable Models | Rate Limits | Region |
|---|---|---|---|
| [Cerebras](https://cloud.cerebras.ai/) | Llama 3.3 70B, Qwen3 235B, GPT-OSS-120B | 30 RPM, 14,400 RPD | 🇺🇸 |
| [Cloudflare Workers AI](https://dash.cloudflare.com/profile/api-tokens) | Llama 3.3 70B, Qwen QwQ 32B | 10K neurons/day | 🇺🇸 |
| [GitHub Models](https://github.com/marketplace/models) | GPT-4o, Llama 3.3 70B, DeepSeek-R1 | 10–15 RPM, 50–150 RPD | 🇺🇸 |
| [Groq](https://console.groq.com/keys) | Llama 3.3 70B, Llama 4 Scout, Kimi K2 | 30 RPM, 1K RPD | 🇺🇸 |
| [Hugging Face](https://huggingface.co/settings/tokens) | Llama 3.3 70B, Qwen2.5 72B, Mistral 7B | $0.10/mo free credits | 🇺🇸 |
| [Kluster AI](https://platform.kluster.ai/apikeys) | DeepSeek-R1, Llama 4 Maverick, Qwen3-235B | Undocumented | 🇺🇸 |
| [LLM7.io](https://token.llm7.io) | DeepSeek R1, Flash-Lite, Qwen2.5 Coder | 30 RPM (120 with token) | 🇬🇧 |
| [NVIDIA NIM](https://build.nvidia.com/explore/discover) | Llama 3.3 70B, Mistral Large, Qwen3 235B | 40 RPM | 🇺🇸 |
| [Ollama Cloud](https://ollama.com/settings/keys) | DeepSeek-V3.2, Qwen3.5, Kimi-K2.5 | 1 concurrent, light usage | 🇺🇸 |
| [OpenRouter](https://openrouter.ai/keys) | DeepSeek R1, Llama 3.3 70B, GPT-OSS-120B | 20 RPM, 50 RPD (1K with $10+) | 🇺🇸 |

---

## Getting API Keys

Each provider has its own key management page:

```bash
# Store keys as environment variables — never hardcode them
export GROQ_API_KEY="your_groq_key"
export GEMINI_API_KEY="your_gemini_key"
export OPENROUTER_API_KEY="your_openrouter_key"
export MISTRAL_API_KEY="your_mistral_key"
export COHERE_API_KEY="your_cohere_key"
export CEREBRAS_API_KEY="your_cerebras_key"
export GITHUB_TOKEN="your_github_pat"
export HF_TOKEN="your_huggingface_token"
export NVIDIA_API_KEY="your_nvidia_key"
export CLOUDFLARE_API_TOKEN="your_cf_token"
export CLOUDFLARE_ACCOUNT_ID="your_cf_account_id"
```

---

## OpenAI SDK Integration

All providers (except Ollama Cloud) are OpenAI SDK-compatible — just swap the `base_url` and `api_key`.

### Python

```python
from openai import OpenAI

# ── Groq ──────────────────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],
)
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)

# ── Google Gemini ─────────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"],
)
response = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=[{"role": "user", "content": "Explain quantum entanglement."}],
)

# ── Mistral AI ────────────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://api.mistral.ai/v1",
    api_key=os.environ["MISTRAL_API_KEY"],
)
response = client.chat.completions.create(
    model="mistral-small-latest",
    messages=[{"role": "user", "content": "Write a haiku about code."}],
)

# ── OpenRouter ────────────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
response = client.chat.completions.create(
    model="deepseek/deepseek-r1",          # free model on OpenRouter
    messages=[{"role": "user", "content": "What is 2+2?"}],
    extra_headers={
        "HTTP-Referer": "https://yourapp.com",   # optional but recommended
        "X-Title": "My App",
    },
)

# ── Cerebras ──────────────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.environ["CEREBRAS_API_KEY"],
)
response = client.chat.completions.create(
    model="llama-3.3-70b",
    messages=[{"role": "user", "content": "Tell me a joke."}],
)

# ── NVIDIA NIM ────────────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ["NVIDIA_API_KEY"],
)
response = client.chat.completions.create(
    model="meta/llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": "Summarize this text."}],
)

# ── GitHub Models ─────────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Draft an email."}],
)

# ── Cohere (OpenAI-compatible endpoint) ───────────────────────────────────────
client = OpenAI(
    base_url="https://api.cohere.com/compatibility/v1",
    api_key=os.environ["COHERE_API_KEY"],
)
response = client.chat.completions.create(
    model="command-a-03-2025",
    messages=[{"role": "user", "content": "Translate to French: Hello world"}],
)
```

### JavaScript / TypeScript

```typescript
import OpenAI from "openai";

// ── Groq ──────────────────────────────────────────────────────────────────────
const groq = new OpenAI({
  baseURL: "https://api.groq.com/openai/v1",
  apiKey: process.env.GROQ_API_KEY,
});

const completion = await groq.chat.completions.create({
  model: "llama-3.3-70b-versatile",
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(completion.choices[0].message.content);

// ── OpenRouter with free model router ────────────────────────────────────────
const openrouter = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.OPENROUTER_API_KEY,
  defaultHeaders: {
    "HTTP-Referer": "https://yourapp.com",
    "X-Title": "My App",
  },
});

// Use the free models router — automatically picks an available free model
const freeCompletion = await openrouter.chat.completions.create({
  model: "openrouter/free",
  messages: [{ role: "user", content: "What is the capital of France?" }],
});

// ── Mistral ───────────────────────────────────────────────────────────────────
const mistral = new OpenAI({
  baseURL: "https://api.mistral.ai/v1",
  apiKey: process.env.MISTRAL_API_KEY,
});

const mistralCompletion = await mistral.chat.completions.create({
  model: "mistral-small-latest",
  messages: [{ role: "user", content: "Explain async/await in JavaScript." }],
});
```

---

## Cloudflare Workers AI

Cloudflare uses a slightly different auth pattern:

```python
import requests, os

ACCOUNT_ID = os.environ["CLOUDFLARE_ACCOUNT_ID"]
API_TOKEN  = os.environ["CLOUDFLARE_API_TOKEN"]

response = requests.post(
    f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/"
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    headers={"Authorization": f"Bearer {API_TOKEN}"},
    json={"messages": [{"role": "user", "content": "What is Cloudflare Workers?"}]},
)
result = response.json()
print(result["result"]["response"])
```

```typescript
// Cloudflare Workers runtime (inside a Worker)
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const ai = new Ai(env.AI);
    const response = await ai.run("@cf/meta/llama-3.3-70b-instruct-fp8-fast", {
      messages: [{ role: "user", content: "Hello from Workers AI!" }],
    });
    return Response.json(response);
  },
};
```

---

## Ollama Cloud (Non-OpenAI API)

Ollama Cloud uses the Ollama API format, **not** the OpenAI format:

```python
import requests, os

response = requests.post(
    "https://ollama.com/api/chat",
    headers={"Authorization": f"Bearer {os.environ['OLLAMA_API_KEY']}"},
    json={
        "model": "deepseek-v3.2",
        "messages": [{"role": "user", "content": "What is 2 + 2?"}],
        "stream": False,
    },
)
print(response.json()["message"]["content"])
```

```python
# Using the ollama Python client
import ollama, os

client = ollama.Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {os.environ['OLLAMA_API_KEY']}"},
)
response = client.chat(
    model="qwen3.5",
    messages=[{"role": "user", "content": "Write a poem about the sea."}],
)
print(response["message"]["content"])
```

---

## Hugging Face Inference API

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://router.huggingface.co/novita/v3/openai",
    api_key=os.environ["HF_TOKEN"],
)

response = client.chat.completions.create(
    model="meta-llama/llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": "Summarize the theory of relativity."}],
    max_tokens=512,
)
print(response.choices[0].message.content)
```

---

## Streaming Responses

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"],
)

with client.chat.completions.stream(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Write a short story about a robot."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

```typescript
const stream = await groq.chat.completions.create({
  model: "llama-3.3-70b-versatile",
  messages: [{ role: "user", content: "Write a haiku." }],
  stream: true,
});

for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content ?? "");
}
```

---

## Provider Fallback Pattern

Cycle through providers when rate limits are hit:

```python
from openai import OpenAI, RateLimitError
import os

PROVIDERS = [
    {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": os.environ.get("GROQ_API_KEY"),
        "model": "llama-3.3-70b-versatile",
    },
    {
        "name": "Cerebras",
        "base_url": "https://api.cerebras.ai/v1",
        "api_key": os.environ.get("CEREBRAS_API_KEY"),
        "model": "llama-3.3-70b",
    },
    {
        "name": "Mistral",
        "base_url": "https://api.mistral.ai/v1",
        "api_key": os.environ.get("MISTRAL_API_KEY"),
        "model": "mistral-small-latest",
    },
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": os.environ.get("OPENROUTER_API_KEY"),
        "model": "openrouter/free",
    },
]

def chat_with_fallback(messages: list[dict], **kwargs) -> str:
    for provider in PROVIDERS:
        if not provider["api_key"]:
            continue
        try:
            client = OpenAI(
                base_url=provider["base_url"],
                api_key=provider["api_key"],
            )
            response = client.chat.completions.create(
                model=provider["model"],
                messages=messages,
                **kwargs,
            )
            return response.choices[0].message.content
        except RateLimitError:
            print(f"Rate limited on {provider['name']}, trying next...")
            continue
        except Exception as e:
            print(f"Error on {provider['name']}: {e}, trying next...")
            continue
    raise RuntimeError("All providers exhausted.")

# Usage
answer = chat_with_fallback(
    messages=[{"role": "user", "content": "What is the speed of light?"}]
)
print(answer)
```

---

## OpenRouter Free Models Router

OpenRouter provides a special router that automatically selects available free models:

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

# Use the free router — picks from 29+ free models automatically
response = client.chat.completions.create(
    model="openrouter/free",
    messages=[{"role": "user", "content": "Explain recursion."}],
)

# Or use model fallbacks for priority ordering
response = client.chat.completions.create(
    model="deepseek/deepseek-r1",
    messages=[{"role": "user", "content": "Explain recursion."}],
    extra_body={
        "route": "fallback",
        "models": [
            "deepseek/deepseek-r1",
            "meta-llama/llama-3.3-70b-instruct:free",
            "openrouter/free",
        ],
    },
)
```

---

## LangChain Integration

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os

# Works with any OpenAI-compatible provider
llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.environ["GROQ_API_KEY"],
    temperature=0.7,
)

response = llm.invoke([HumanMessage(content="What are the SOLID principles?")])
print(response.content)

# Gemini via LangChain
gemini = ChatOpenAI(
    model="gemini-2.0-flash",
    openai_api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
    openai_api_key=os.environ["GEMINI_API_KEY"],
)
```

---

## Rate Limit Reference

| Provider | RPM | RPD | Notes |
|---|---|---|---|
| Groq | 30 | 1,000 | 14,400 RPD for Llama 3.1 8B only |
| Cerebras | 30 | 14,400 | — |
| Gemini Flash | 15 | 1,500 | Not in EU/UK/CH |
| Gemini 2.5 Pro | 5 | 25 | Not in EU/UK/CH |
| GitHub Models | 10–15 | 50–150 | Varies by model tier |
| OpenRouter (free) | 20 | 50 | 1K RPD after $10+ purchase |
| Mistral | 1 req/s | — | 1B tokens/month cap |
| NVIDIA NIM | 40 | — | — |
| Cloudflare Workers AI | — | — | 10K neurons/day |
| Cohere | 20 | — | 1K requests/month |

---

## Common Troubleshooting

**`AuthenticationError`**
- Double-check the env var is set: `echo $GROQ_API_KEY`
- Ensure the key is for the correct provider
- Some providers (GitHub Models) require a classic PAT, not a fine-grained token

**`RateLimitError`**
- Implement exponential backoff or use the fallback pattern above
- Switch to a provider with higher limits (Cerebras: 14,400 RPD)
- For Groq, use `llama-3.1-8b-instant` for the 14,400 RPD limit

**`Model not found`**
- Check the exact model ID on the provider's docs/dashboard
- OpenRouter free models have `:free` suffix: `meta-llama/llama-3.3-70b-instruct:free`
- Cloudflare models use `@cf/` prefix: `@cf/meta/llama-3.3-70b-instruct-fp8-fast`

**Gemini free tier unavailable**
- The free tier is not available in EU, UK, or Switzerland
- Use a VPN or switch to a different provider like Groq or Mistral

**Ollama Cloud not working with OpenAI SDK**
- Ollama Cloud uses its own API format — use the `ollama` Python package or raw HTTP

**OpenRouter 50 RPD limit**
- Make a one-time $10 credit purchase to unlock 1,000 RPD for free models permanently
- Alternatively, use `openrouter/free` router to distribute across all free models

---

## Choosing the Right Provider

```
Need highest RPD?         → Cerebras (14,400 RPD)
Need smartest free model? → Gemini 2.5 Pro (if not in EU/UK/CH)
Need EU-hosted?           → Mistral AI (France)
Need most model variety?  → OpenRouter (29+ free models) or Cloudflare (48+ models)
Need fastest inference?   → Groq (purpose-built inference chips)
Need reasoning model?     → DeepSeek-R1 on Groq/OpenRouter/Kluster AI
Need vision?              → Gemini Flash, Llama 4 Scout (Groq), GLM-4.6V-Flash (Zhipu)
No rate limit concern?    → Cloudflare (10K neurons/day, compute-based)
```
