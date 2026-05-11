---
name: google-search
description: Search the web using Google Custom Search Engine (PSE). Use this when you need live information, documentation, or to research topics and the built-in web_search is unavailable.
---

# Google Search Skill

This skill allows OpenClaw agents to perform web searches via Google's Custom Search API (PSE).

## Setup

1.  **Google Cloud Console:** Create a project and enable the "Custom Search API".
2.  **API Key:** Generate an API Key.
3.  **Search Engine ID (CX):** Create a Programmable Search Engine at [cse.google.com](https://cse.google.com/cse/all), and get your CX ID.
4.  **Environment:** Store your credentials in a `.env` file in your workspace:
    ```
    GOOGLE_API_KEY=your_key_here
    GOOGLE_CSE_ID=your_cx_id_here
    ```

## Workflow
... (rest of file)

## Example Usage

```bash
GOOGLE_API_KEY=xxx GOOGLE_CSE_ID=yyy python3 skills/google-search/scripts/search.py "OpenClaw documentation"
```
