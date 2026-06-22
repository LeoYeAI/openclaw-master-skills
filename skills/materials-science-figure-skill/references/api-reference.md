# Nanobanana API Reference

## Official Contract

Use the official Gemini `generateContent` API shape and replace the provider-specific values:

- Official base URL: `https://generativelanguage.googleapis.com`
- Third-party base URL: your Google-compatible Gemini endpoint, only when explicitly intended

- Official API key: `GEMINI_API_KEY`
- Third-party API key: the provider key

Optional third-party provider example:

- Zhizengzeng base URL: `https://api.zhizengzeng.com/google`
- Zhizengzeng API key: the user's ZZZ key
- Third-party confirmation: `NANOBANANA_ALLOW_THIRD_PARTY=1` or `--allow-third-party`

## Endpoint Safety

- The generation scripts are designed to fail closed when `NANOBANANA_BASE_URL` or `--base-url` is missing.
- Official Google endpoint is the recommended default: `https://generativelanguage.googleapis.com`
- If you point the scripts to any other hostname, they should require explicit third-party confirmation before sending API keys or user-provided files.

## Route

```http
POST {base_url}/v1beta/models/{model}:generateContent
Content-Type: application/json
X-goog-api-key: {api_key}
```

## Text To Image Request

```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
        }
      ]
    }
  ],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"]
  }
}
```

## Image Editing Request

Use the same route. Put the prompt and each input image into `parts`.

```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "Using the provided image, change only the blue sofa to a vintage brown leather Chesterfield sofa. Keep everything else exactly the same."
        },
        {
          "inlineData": {
            "mimeType": "image/png",
            "data": "<base64>"
          }
        }
      ]
    }
  ],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {
      "aspectRatio": "16:9",
      "imageSize": "2K"
    }
  }
}
```

## Response Parsing

Read outputs from:

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          { "text": "..." },
          {
            "inlineData": {
              "mimeType": "image/png",
              "data": "<base64>"
            }
          }
        ]
      }
    }
  ]
}
```

## Supported Official Options

- `generationConfig.responseModalities`
- `generationConfig.imageConfig.aspectRatio`
- `generationConfig.imageConfig.imageSize`
- `generationConfig.thinkingConfig.thinkingLevel`
- `generationConfig.thinkingConfig.includeThoughts`

## Practical Notes

- `gemini-3.1-flash-image-preview` supports image generation and editing.
- `imageSize` uses official values like `512`, `1K`, `2K`, `4K`.
- `aspectRatio` uses official values like `1:1`, `3:2`, `16:9`, `21:9`.
- For edit workflows, do not invent a separate edit endpoint. Use `generateContent` with prompt plus image inputs.
- Prompt-only helpers such as `build_materials_figure_prompt.py` and `--print-prompt` should remain local-only and not send data to the network.
