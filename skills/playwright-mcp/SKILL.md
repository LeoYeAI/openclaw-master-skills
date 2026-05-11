---
name: playwright-mcp
description: Browser automation via Playwright MCP server. Navigate websites, click elements, fill forms, extract data, take screenshots, and perform full browser automation workflows.
metadata: {"openclaw":{"emoji":"🎭","os":["linux","darwin","win32"],"requires":{"bins":["playwright-mcp","npx"]},"install":[{"id":"npm-playwright-mcp","kind":"npm","package":"@playwright/mcp","bins":["playwright-mcp"],"label":"Install Playwright MCP"}]}}
---

# Playwright MCP Skill

Browser automation powered by Playwright MCP server. Control Chrome, Firefox, or WebKit programmatically.

## Installation

```bash
npm install -g @playwright/mcp
# Or
npx @playwright/mcp
```

Install browsers (first time):
```bash
npx playwright install chromium
```

## Quick Start

### Start MCP Server (STDIO mode)
```bash
npx @playwright/mcp
```

### Start with Options
```bash
# Headless mode
npx @playwright/mcp --headless

# Specific browser
npx @playwright/mcp --browser firefox

# With viewport
npx @playwright/mcp --viewport-size 1280x720

# Ignore HTTPS errors
npx @playwright/mcp --ignore-https-errors
```

## Common Use Cases

### 1. Navigate and Extract Data
```python
# MCP tools available:
# - browser_navigate: Open URL
# - browser_click: Click element
# - browser_type: Type text
# - browser_select_option: Select dropdown
# - browser_get_text: Extract text content
# - browser_evaluate: Run JavaScript
# - browser_snapshot: Get page structure
# - browser_close: Close browser
```

### 2. Form Interaction
```
1. browser_navigate to form URL
2. browser_type into input fields
3. browser_click to submit
4. browser_get_text to verify result
```

### 3. Data Extraction
```
1. browser_navigate to page
2. browser_evaluate to run extraction script
3. Parse returned JSON data
```

## MCP Tools Reference

| Tool | Description |
|------|-------------|
| `browser_navigate` | Navigate to URL |
| `browser_click` | Click element by selector |
| `browser_type` | Type text into input |
| `browser_select_option` | Select dropdown option |
| `browser_get_text` | Get text content |
| `browser_evaluate` | Execute JavaScript |
| `browser_snapshot` | Get accessible page snapshot |
| `browser_close` | Close browser context |
| `browser_choose_file` | Upload file |
| `browser_press` | Press keyboard key |

## Configuration Options

```bash
# Security
--allowed-hosts example.com,api.example.com
--blocked-origins malicious.com
--ignore-https-errors

# Browser settings
--browser chromium|firefox|webkit
--headless
--viewport-size 1920x1080
--user-agent "Custom Agent"

# Timeouts
--timeout-action 10000      # Action timeout (ms)
--timeout-navigation 30000  # Navigation timeout (ms)

# Output
--output-dir ./playwright-output
--save-trace
--save-video 1280x720
```

## Examples

### Login to Website
```
browser_navigate: { url: "https://example.com/login" }
browser_type: { selector: "#username", text: "user" }
browser_type: { selector: "#password", text: "pass" }
browser_click: { selector: "#submit" }
browser_get_text: { selector: ".welcome-message" }
```

### Extract Table Data
```
browser_navigate: { url: "https://example.com/data" }
browser_evaluate: { 
  script: "() => { return Array.from(document.querySelectorAll('table tr')).map(r => r.textContent); }" 
}
```

### Screenshot
```
browser_navigate: { url: "https://example.com" }
browser_evaluate: { script: "() => { document.body.style.zoom = 1; return true; }" }
# Screenshot saved via --output-dir or returned in response
```

## Security Notes

- By default restricts file system access to workspace root
- Host validation prevents navigation to untrusted domains
- Sandboxing enabled by default (use `--no-sandbox` with caution)
- Service workers blocked by default

## Troubleshooting

```bash
# Update browsers
npx playwright install chromium

# Debug mode
npx @playwright/mcp --headless=false --output-mode=stdout

# Check installation
playwright-mcp --version
```

## Links

- [Playwright Docs](https://playwright.dev)
- [MCP Protocol](https://modelcontextprotocol.io)
- [NPM Package](https://www.npmjs.com/package/@playwright/mcp)
