---
name: Playwright (Automation + MCP + Scraper)
slug: playwright
version: 1.0.2
homepage: https://playwright.dev
description: Browser automation and web scraping with Playwright. Forms, screenshots, data extraction. Works standalone or via MCP. Testing included.
changelog: Rewritten with MCP integration and scraping focus. Now covers standalone use and MCP server setup.
---

## When to Use

Use this skill when you need to:
- **Scrape a website** (static or JavaScript-rendered)
- **Automate form filling** (login, checkout, data entry)
- **Test a web application** (E2E tests, visual regression)
- **Take screenshots or PDFs** of web pages
- **Extract data** from tables, lists, or dynamic content

## Decision Matrix

| Scenario | Method | Speed |
|----------|--------|-------|
| Static HTML | `web_fetch` tool | ⚡ Fastest |
| JavaScript-rendered | Playwright direct | 🚀 Fast |
| AI agent automation | MCP server | 🤖 Integrated |
| E2E testing | @playwright/test | ✅ Full framework |

## Quick Reference

| Task | File |
|------|------|
| E2E testing patterns | `testing.md` |
| CI/CD integration | `ci-cd.md` |
| Debugging failures | `debugging.md` |
| Web scraping patterns | `scraping.md` |
| Selector strategies | `selectors.md` |

## Core Rules

1. **Never use `waitForTimeout()`** - always wait for specific conditions (element, URL, network)
2. **Always close the browser** - call `browser.close()` to prevent memory leaks
3. **Prefer role selectors** - `getByRole()` survives UI changes better than CSS
4. **Handle dynamic content** - use `waitFor()` before interacting with elements
5. **Persist auth state** - use `storageState` to save and reuse login sessions

## Quick Start - Common Tasks

### Scrape a Page
```javascript
const { chromium } = require('playwright');
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto('https://example.com');
const text = await page.locator('body').textContent();
await browser.close();
```

### Fill a Form and Submit
```javascript
await page.goto('https://example.com/login');
await page.getByLabel('Email').fill('user@example.com');
await page.getByLabel('Password').fill('secret');
await page.getByRole('button', { name: 'Sign in' }).click();
await page.waitForURL('**/dashboard');
```

### Take a Screenshot
```javascript
await page.goto('https://example.com');
await page.screenshot({ path: 'screenshot.png', fullPage: true });
```

### Extract Table Data
```javascript
const rows = await page.locator('table tr').all();
const data = [];
for (const row of rows) {
  const cells = await row.locator('td').allTextContents();
  data.push(cells);
}
```

## Selector Priority

| Priority | Method | Example |
|----------|--------|---------|
| 1 | `getByRole()` | `getByRole('button', { name: 'Submit' })` |
| 2 | `getByLabel()` | `getByLabel('Email')` |
| 3 | `getByPlaceholder()` | `getByPlaceholder('Search...')` |
| 4 | `getByTestId()` | `getByTestId('submit-btn')` |
| 5 | `locator()` | `locator('.class')` - last resort |

## Common Traps

| Trap | Fix |
|------|-----|
| Element not found | Add `await locator.waitFor()` before interacting |
| Flaky clicks | Use `click({ force: true })` or wait for `state: 'visible'` |
| Timeout in CI | Increase timeout, check viewport size matches local |
| Auth lost between tests | Use `storageState` to persist cookies |
| SPA never reaches networkidle | Wait for specific DOM element instead |
| 403 Forbidden | Check if site blocks headless; try `headless: false` |
| Blank page after load | Increase wait time or use `waitUntil: 'networkidle'` |

## Handling Sessions

```javascript
// Save session after login
await page.context().storageState({ path: 'auth.json' });

// Reuse session in new context
const context = await browser.newContext({ storageState: 'auth.json' });
```

## MCP Integration

For AI agents using Model Context Protocol:

```bash
npm install -g @playwright/mcp
npx @playwright/mcp --headless
```

### MCP Tools Reference

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

### MCP Server Options

```bash
--headless              # Run without UI
--browser chromium      # chromium|firefox|webkit
--viewport-size 1920x1080
--timeout-action 10000  # Action timeout (ms)
--timeout-navigation 30000
--allowed-hosts example.com,api.example.com
--save-trace            # Save trace for debugging
--save-video 1280x720   # Record video
```

## Installation

```bash
npm init playwright@latest
# Or add to existing project
npm install -D @playwright/test
npx playwright install chromium
```

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `puppeteer` - Alternative browser automation (Chrome-focused)
- `scrape` - General web scraping patterns and strategies
- `web` - Web development fundamentals and HTTP handling

## Feedback

- If useful: `clawhub star playwright`
- Stay updated: `clawhub sync`
