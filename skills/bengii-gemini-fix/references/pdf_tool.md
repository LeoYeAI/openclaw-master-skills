# OpenClaw PDF Tool Reference

## Overview

First-class PDF analysis tool with native Anthropic and Google PDF provider support, plus extraction fallback for non-native models. Added in v2026.3.2.

## Availability

Model resolution order:
1. `agents.defaults.pdfModel`
2. Fallback to `agents.defaults.imageModel`
3. Best-effort provider defaults based on available auth

## Input Reference

| Parameter | Type | Description |
|---|---|---|
| `pdf` | string | Single PDF path or URL |
| `pdfs` | string[] | Multiple PDF paths/URLs (up to 10 total) |
| `prompt` | string | Analysis prompt (default: "Analyze this PDF document.") |
| `pages` | string | Page filter like `1-5` or `1,3,7-9` |
| `model` | string | Optional model override (`provider/model`) |
| `maxBytesMb` | number | Per-PDF size cap in MB |

Notes:
- `pdf` and `pdfs` are merged and deduplicated before loading
- `pages` is parsed as 1-based page numbers, deduped, sorted, and clamped to max pages
- `maxBytesMb` defaults to `agents.defaults.pdfMaxBytesMb` or `10`

## Supported PDF References

- Local file path (including `~` expansion)
- `file://` URL
- `http://` and `https://` URL
- Other URI schemes (e.g. `ftp://`) rejected with `unsupported_pdf_reference`
- In sandbox mode, remote `http(s)` URLs are rejected
- With workspace-only file policy, local paths outside allowed roots are rejected

## Execution Modes

### Native Provider Mode

Supported providers: `anthropic`, `google`

- Sends raw PDF bytes directly to the provider API
- `pages` is **not supported** in native mode (returns error if set)
- Best quality and most efficient

### Extraction Fallback Mode

For all other models:

1. Extract text from selected pages (up to `agents.defaults.pdfMaxPages`, default 20)
2. If extracted text length < 200 chars, render pages to PNG images
3. Send extracted content + prompt to selected model

Notes:
- Page image extraction uses a pixel budget of 4,000,000
- If target model doesn't support image input and no extractable text → error
- Requires `pdfjs-dist` (and `@napi-rs/canvas` for image rendering)

## Config

```json5
{
  agents: {
    defaults: {
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5-mini"],
      },
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
    },
  },
}
```

## Output Details

Response in `content[0].text` with `details` object:

| Field | Description |
|---|---|
| `model` | Resolved model ref (`provider/model`) |
| `native` | `true` for native provider mode, `false` for fallback |
| `attempts` | Fallback attempts that failed before success |

- Single PDF input: `details.pdf`
- Multiple PDF inputs: `details.pdfs[]` with pdf entries
- Sandbox path rewrite metadata: `rewrittenFrom` (when applicable)

## Error Behavior

| Error | Condition |
|---|---|
| `pdf required: provide a path or URL` | No PDF input provided |
| `details.error = "too_many_pdfs"` | More than 10 PDFs |
| `details.error = "unsupported_pdf_reference"` | Unsupported URI scheme |
| `pages is not supported with native PDF providers` | `pages` used in native mode |

## Examples

```json
// Single PDF analysis
{ "pdf": "/tmp/report.pdf", "prompt": "Summarize this report in 5 bullets" }

// Compare multiple PDFs
{ "pdfs": ["/tmp/q1.pdf", "/tmp/q2.pdf"], "prompt": "Compare risks and timeline changes" }

// Page-specific extraction with model override
{ "pdf": "https://example.com/report.pdf", "pages": "1-3,7", "model": "openai/gpt-5-mini", "prompt": "Extract only customer-impacting incidents" }
```
