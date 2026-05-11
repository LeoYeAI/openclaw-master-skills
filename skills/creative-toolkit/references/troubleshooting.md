# Troubleshooting

## Common Issues

**"No image generation providers configured"**
-> Set `MEIGEN_API_TOKEN` or configure an alternative provider in `~/.config/meigen/config.json`

**Timeout during generation**
-> Image generation typically takes 10-30 seconds. During high demand, it may take longer. The server polls with a 5-minute timeout.

**ComfyUI connection refused**
-> Ensure ComfyUI is running and accessible at the configured URL. Test with: `curl <url>/system_stats`

**"Model not found"**
-> Run `list_models` to see available models for your configured providers.

**Reference image rejected**
-> Reference images require accessible URLs. Use `upload_reference_image` to prepare local files first. ComfyUI users can pass local file paths directly.

**Upload returns "Not found" or path error (e.g. `/upload/reference`)**
-> You must call the `upload_reference_image` MCP tool directly — do NOT construct HTTP requests to upload endpoints yourself. The tool handles compression, presigning, and uploading internally. If the tool is unavailable, ask the user to upload the image manually at [meigen.ai](https://www.meigen.ai) and provide the URL.

**Reference image URL expired**
-> URLs from `upload_reference_image` expire after 24 hours. Re-upload the image if the URL is no longer accessible.

## Security & Privacy

**Pinned package**: This skill runs as an MCP server via `npx meigen@1.2.5` (pinned version, not floating). The package is published on [npmjs.com](https://www.npmjs.com/package/meigen) with full source code at [GitHub](https://github.com/jau123/MeiGen-AI-Design-MCP). No code is obfuscated or minified beyond standard TypeScript compilation.

**Reference images**: The `upload_reference_image` tool compresses a user-specified image (max 2MB, 2048px) for use as a style reference in generation. This is always user-initiated and requires explicit invocation — no files are accessed automatically. Uploaded images expire after 24 hours. ComfyUI users can skip uploading entirely by passing local file paths directly to `generate_image`.

**API tokens**: `MEIGEN_API_TOKEN` is stored locally in environment variables or `~/.config/meigen/config.json` with `chmod 600` permissions. Tokens are only sent to the configured provider's API endpoint and never logged or transmitted elsewhere.

**No telemetry**: The MCP server does not collect analytics, usage data, or send any information to third parties beyond the configured image generation provider.
