# Web Tools Reference

Web tools provide search and fetch capabilities for the AI agent. Multiple search providers are supported.

## How It Works

- `web_search`: Sends a query to a search provider and returns results.
- `web_fetch`: Fetches a web page and returns extracted content.

## Choosing a Search Provider

### Auto-Detection

OpenClaw detects the provider from available API keys:
1. Brave Search API (`BRAVE_API_KEY`)
2. Perplexity (via OpenRouter or direct)
3. Gemini (Google Search grounding)
4. Grok (`GROK_API_KEY`)
5. Kimi (`KIMI_API_KEY`)

### Explicit Provider

```json5
{
  tools: {
    web: {
      search: {
        provider: "brave",      // "brave" | "perplexity" | "gemini" | "grok" | "kimi"
        apiKey: "${BRAVE_API_KEY}",
      },
    },
  },
}
```

## Brave Search API

### Getting a Brave API Key

1. Go to [Brave Search API](https://brave.com/search/api/).
2. Create an account and get an API key.
3. Free tier available (limited queries/month).

### Where to Set the Key

```json5
// In ~/.openclaw/openclaw.json
{
  tools: {
    web: {
      search: {
        apiKey: "${BRAVE_API_KEY}",
      },
    },
  },
}
```

Or via environment variable:

```bash
export BRAVE_API_KEY="your-api-key"
```

## Using Perplexity (Direct or via OpenRouter)

### Getting an OpenRouter API Key

1. Go to [OpenRouter](https://openrouter.ai/).
2. Create an account and get an API key.

### Setting Up Perplexity Search

```json5
{
  tools: {
    web: {
      search: {
        provider: "perplexity",
        // Configure via OpenRouter or direct Perplexity API
      },
    },
  },
}
```

### Available Perplexity Models

Check the [OpenRouter](https://openrouter.ai/) model catalog for current Perplexity models.

## Using Gemini (Google Search Grounding)

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Generate an API key.

### Setting Up Gemini Search

```json5
{
  tools: {
    web: {
      search: {
        provider: "gemini",
      },
    },
  },
}
```

Notes:
- Gemini search uses Google Search grounding.
- Requires a valid Gemini API key.

## web_search

### Requirements

- A search API key (Brave, Perplexity, Gemini, Grok, or Kimi).

### Config

```json5
{
  tools: {
    web: {
      search: {
        provider: "brave",
        apiKey: "${BRAVE_API_KEY}",
      },
    },
  },
}
```

### Tool Parameters

| Parameter | Description |
|---|---|
| `query` | Search query string |
| Additional parameters depend on provider |

## web_fetch

### Requirements

- No API key needed (fetches pages directly).
- Optional: `FIRECRAWL_API_KEY` for anti-bot fallback.

### Defaults

| Setting | Default |
|---|---|
| `maxChars` | 50000 |
| `timeoutSeconds` | 30 |
| `cacheTtlMinutes` | 15 |

### Config

```json5
{
  tools: {
    web: {
      fetch: {
        maxChars: 50000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
    },
  },
}
```

### Firecrawl Fallback

Firecrawl is used as an anti-bot fallback for `web_fetch`. When the default Readability extraction fails (e.g. bot-protected pages), the pipeline falls back to Firecrawl for content extraction.

Processing pipeline: Fetch -> Readability extraction -> Firecrawl fallback -> Cache (15 min)

Requires `FIRECRAWL_API_KEY` environment variable.

### Tool Parameters

| Parameter | Description |
|---|---|
| `url` | URL to fetch |
| Additional options for content extraction |
