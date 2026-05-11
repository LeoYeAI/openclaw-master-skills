# Browser Skill

## Description

This skill provides the ability to render modern, JavaScript-heavy web pages and extract their clean, text-based content. I created this tool to overcome the limitations of simple HTTP clients like `curl`, which only fetch raw HTML and often fail to capture dynamically generated information. This allows me to accurately read and understand web content as a human would see it in a browser.

## Dependencies

- `puppeteer`

## Usage Example

The skill is executed via a Node.js script from the workspace root:

```bash
node skills/browser/index.js read https://example.com
```
