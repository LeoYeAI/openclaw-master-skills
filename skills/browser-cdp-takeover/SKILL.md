---
name: browser-cdp-takeover
description: Native takeover of the user's running Chrome browser via CDP port 9222 for automation, web scraping, and visual QA without losing session/login states.
---

# Chrome CDP Takeover Skill

This skill explains how to take over the user's currently running Chrome browser natively, rather than spawning a new blank profile, preserving all cookies and login states.

## 1. Prerequisites (User Setup)
The user must be running Chrome version 144+.
The user must manually enable Remote Debugging:
1. Open `chrome://inspect/#remote-debugging` in a new tab.
2. Check the box: **Allow remote debugging for this browser instance**.
Once checked, Chrome exposes the CDP port at `127.0.0.1:9222`.

## 2. Windows-Specific Quirks
- **Avoid Subagent Tools Defaults**: Do not use standard browser subagent tools (`open_browser_url`, browser recording) as the default path, as they may fail or lose context.
- **Preview Fallback**: If standard preview fails, use system browser directly (`cmd.exe /c start "" "<url>"`, `explorer.exe "<url>"`, or Python `os.startfile()`).
- **NPM agent-browser bug**: The `agent-browser` npm CLI tool lacks a compiled Windows binary. Ignore it on Windows.
- **Error Handling**: If an agent framework throws "local chrome mode is only supported on Linux", stop retrying the subagent. Switch to direct CDP connection.

## 3. How to Connect (Python Playwright)
Use the standard Playwright library connected over CDP:
```python
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Connect to the exposed 9222 port
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else None
        
        if page:
            print(f"Connected to active page: {page.url}")
            # Perform actions natively: click, fill, scrape
            print("Title:", await page.title())
        else:
            print("No open pages found.")

if __name__ == "__main__":
    asyncio.run(run())
```

## 4. How to Connect (MCP `chrome-devtools`)
If the `chrome-devtools` MCP server is installed and configured with `"autoConnect": true`, the AI agent can directly use MCP tools (e.g., `mcp_chrome-devtools_list_pages`, `mcp_chrome-devtools_click`, `mcp_chrome-devtools_fill`) to interact with the active browser.

## 5. Typical Use Cases & Experience
**Web Scraping (e.g., Google Scholar)**: 
  - Bypass cookie and PIN issues by reusing the logged-in Chrome state.
  - Access DOM elements directly and inject scripts in the context of the running page.
  - Implement random delays and backoff if CAPTCHAs trigger.

**Visual Validation**: 
  - Taking a screenshot of UI changes on a locally running dev server.

**Data Entry**: 
  - Filling out forms in internal authenticating dashboards (like Notion, JIRA, etc.) without navigating login walls.
