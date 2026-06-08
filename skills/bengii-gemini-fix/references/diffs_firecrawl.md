# OpenClaw Diffs Tool & Firecrawl Integration Reference

## Table of Contents

- [Diffs Tool](#diffs-tool)
- [Firecrawl Integration](#firecrawl-integration)

---

## Diffs Tool

Optional plugin that renders before/after text or unified patches as a gateway-hosted diff view, a PNG image, or both.

### Quick Start

```bash
# Install the plugin
openclaw plugins install @openclaw/diffs
openclaw config set plugins.entries.diffs.enabled true
```

### Enable

```json5
{
  plugins: {
    entries: {
      diffs: { enabled: true },
    },
  },
}
```

### Typical Agent Workflow

1. Agent generates a diff (before/after text or unified patch)
2. Calls the `diffs` tool with the diff content
3. Tool renders the diff as a hosted HTML viewer and/or PNG image
4. Returns URL + optional image block to the agent

### Input Reference

| Parameter | Type | Description |
|---|---|---|
| `before` | string | Original text (for before/after mode) |
| `after` | string | Modified text (for before/after mode) |
| `patch` | string | Unified diff/patch (for patch mode) |
| `filename` | string | Optional filename for display |
| `format` | string | `viewer`, `image`, or `both` (default: `both`) |

### Output

Returns:
- `viewerUrl`: URL to the hosted diff viewer
- `imagePath`: path to rendered PNG (if format includes image)
- `imageBlock`: image content block for the model

### Plugin Defaults

```json5
{
  plugins: {
    entries: {
      diffs: {
        config: {
          format: "both",        // viewer + image
          maxLines: 5000,
          darkMode: true,
        },
      },
    },
  },
}
```

### Security

- Viewer URLs are Gateway-scoped (accessible only via Gateway auth)
- Artifacts are cleaned up based on lifecycle policy
- No external network calls required

### Browser Requirements (Image Mode)

- Image rendering requires a browser (Playwright/Chromium) when generating PNG
- Falls back to viewer-only if browser is unavailable

### Troubleshooting

| Problem | Fix |
|---|---|
| No PNG generated | Check browser availability (`openclaw browser status`) |
| Viewer URL not accessible | Ensure Gateway is running and accessible |
| Large diffs truncated | Increase `maxLines` in plugin config |

---

## Firecrawl Integration

Firecrawl is an optional anti-bot fallback for the `web_fetch` tool. When regular fetching fails (e.g., Cloudflare protection), Firecrawl can bypass these protections.

### Get an API Key

Sign up at https://firecrawl.dev and get an API key.

### Configure

```json5
{
  tools: {
    web: {
      fetch: {
        firecrawl: {
          apiKey: "${FIRECRAWL_API_KEY}",
          // Or use SecretRef
        },
      },
    },
  },
}
```

Or set `FIRECRAWL_API_KEY` environment variable.

### Stealth / Bot Circumvention

Firecrawl offers stealth mode for better anti-bot bypass:

```json5
{
  tools: {
    web: {
      fetch: {
        firecrawl: {
          apiKey: "...",
          stealth: true,    // Enable stealth mode
        },
      },
    },
  },
}
```

### How `web_fetch` Uses Firecrawl

1. Agent calls `web_fetch` with a URL
2. OpenClaw tries the standard fetcher first
3. If the standard fetch fails (anti-bot block, empty content, etc.), it falls back to Firecrawl
4. Firecrawl fetches the page and returns cleaned content
5. Result is returned to the agent

The fallback is automatic — no agent-side changes needed.
