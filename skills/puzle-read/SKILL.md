---
name: puzle-read-skill
version: 0.1.0-beta
description: >-
  Connect to Puzle Read — an intelligent reading workbench that helps users turn articles
  and documents into searchable personal knowledge. Save web articles (by URL or pre-fetched
  content), upload documents and files to the user's reading library, and search across
  everything they've read to find relevant insights. Use this skill whenever the user wants
  to: save or read web articles, add documents to their reading library, look up something
  from their reading collection, process PDFs or other files for deeper understanding,
  or build knowledge workflows around their readings. This skill also applies when the user
  wants to: save something for later reading ("read it later", "bookmark this", "save this
  article"), get a summary or analysis of an article or document, upload a file (PDF, image,
  audio, etc.) for processing, or organize their reading collection. Also trigger when you
  see imports of `puzle_reading` or `PuzleReadingClient`, or when the user mentions Puzle.
compatibility: requires python3, requests
---

# Puzle Read Skill

Save web articles, documents and files to your personal reading library powered by Puzle.
AI analyzes the full text and enables semantic search across everything you've read.

## First-time Setup (show this on skill install)

When this skill is first activated, immediately greet the user and guide them through setup:

1. **Check if a token is already configured**:
   ```python
   from puzle_reading import PuzleReadingClient
   if PuzleReadingClient.token_is_configured():
       # Token exists, ready to go
   ```
   If yes, tell the user: "Puzle Read Skill is ready! You can send me any URL, file, or text
   and I'll save it to your reading library. You can also search across everything you've read."

2. **If no token is configured**, walk the user through it:
   - Tell the user: "To get started, I need your Puzle token. Here's how to get it:"
   - Send the `get_token.gif` file (located at `<this-skill-directory>/get_token.gif`) to the
     user as an attachment so they can see the visual guide.
     - In OpenClaw: send via channel as a file attachment
     - In other environments: provide the file path for the user to open
   - Tell the user to open **https://read-web-test.puzle.com.cn**, log in, then follow the
     GIF to copy their token and paste it back.
   - Once received, save it with `PuzleReadingClient.save_token(token)` and confirm.

3. **After setup is complete**, briefly explain what the skill can do:
   - "You can now send me any URL, article, PDF, or text and I'll save it to your Puzle
     reading library. I can also summarize articles, search across your readings, and more.
     Just try sending me a link!"

## Prerequisites

The bundled Client SDK lives at `scripts/puzle_reading.py` relative to this skill directory.
It requires the `requests` library.

```python
import sys
sys.path.insert(0, "<this-skill-directory>/scripts")
from puzle_reading import PuzleReadingClient
```

## Token Management

Token is stored in `~/.config/puzle/config.json` with file permission `0o600` (owner read/write only).
The SDK looks for a token in the following priority order:

1. Constructor argument `PuzleReadingClient(token="...")`
2. Environment variable `PUZLE_TOKEN`
3. Config file `~/.config/puzle/config.json`

### User sends a token directly

If the user sends a token in the conversation (typically a long string starting with `eyJ...`),
**save it immediately**:

```python
PuzleReadingClient.save_token(token)
client = PuzleReadingClient()  # auto-loads from config file
```

After saving, tell the user: "Token saved to `~/.config/puzle/config.json`. You won't need to
provide it again in future sessions."

### User does not have a token

Guide them step by step:

1. Tell the user to open Puzle Read: **https://read-web-test.puzle.com.cn** and log in
2. Send the tutorial GIF to the user as an attachment so they can see how to get the token.
   The GIF is located at `get_token.gif` relative to this skill directory.
   - In OpenClaw: send it via the channel as a file attachment
   - In other environments: provide the file path for the user to open
3. The GIF shows: open browser DevTools → Application → Cookies → copy the JWT token value
4. Ask the user to paste the token back to you

Once received, save it using the steps above.

### Token already configured (most common case)

Once a token has been saved, all subsequent calls work automatically — no need to ask the user again:

```python
client = PuzleReadingClient()  # auto-reads from ~/.config/puzle/config.json
```

You can check beforehand:

```python
if not PuzleReadingClient.token_is_configured():
    # Guide the user to provide a token
    ...
```

### Token expired (401 error)

The token is valid for approximately **7 days**. When you receive `PuzleAPIError(code=401)`:
1. Tell the user their token has expired
2. Ask them to obtain a new token from Puzle
3. Save the new token: `PuzleReadingClient.save_token(new_token)`

### Environment variable method (optional)

Users can also configure via environment variable, which takes precedence over the config file:

```bash
export PUZLE_TOKEN="eyJhbG..."
```

## Two Modes of Use

### Mode A: Save for later ("Read It Later")

When the user just wants to **save** content — no need to wait for processing. Create the reading,
give user the web link, done.

```python
result = client.create_reading_from_url("https://example.com/article")
# result.web_url → "https://read.puzle.com.cn/read/42"
# Tell the user: "Saved! You can view it here: {result.web_url}"
```

Use this mode when:
- "save this" / "bookmark" / "read it later" / "store this link"
- "save all of these" — batch-saving multiple links
- User uploads a file but doesn't ask for any analysis — "just store this PDF"
- User shares a link in passing without asking a question about its content
- "keep it for later"

### Mode B: Analyze now (background processing)

When the user wants to **understand, summarize, or work with** the content, processing takes
30–90 seconds. To avoid blocking the conversation:

1. **Create the reading and immediately give user the web link**
2. **Spawn a background task / subagent** to run `wait_for_reading()` + analysis
3. **When the background task completes**, present the result to the user

```python
# Step 1: Create and immediately respond to user
result = client.create_reading_from_url("https://example.com/article")
# Tell user: "Processing now. You can preview it here: {result.web_url}"

# Step 2: In a background task / subagent, wait and analyze
detail = client.wait_for_reading(result.reading_id, result.resource_type)
content = detail["data"]["content"]
# Generate summary / answer questions based on content

# Step 3: When done, present results to user
```

**Why background processing?** `wait_for_reading()` blocks for 30–90 seconds. Running it in
a subagent or background process keeps the conversation responsive. The user gets the web link
instantly and can start reading there, while the analysis runs in parallel.

Use this mode when:
- "what does this article say" / "summarize this" / "give me a summary"
- "what are the key findings in this PDF" — need to read and analyze
- "compare the viewpoints of these two articles" — need content from multiple readings
- User asks a specific question about the article content
- You need to search across readings afterwards

## When to Use Which Method

### User shares a URL — Decision Chain

When the user gives you a link, **do NOT call `create_reading_from_url()` directly**.
Try the following approaches in order, falling through to the next step only on failure:

```
User sends a URL
  │
  ▼
┌─────────────────────────────────────────────────┐
│ Step 1: Fetch the page yourself                 │
│                                                 │
│ Use WebFetch, browser, or any available tool    │
│ to retrieve the page content.                   │
│                                                 │
│ Success (got meaningful content)?               │
│   → Extract using readability (or use the       │
│     tool's formatted output directly)           │
│   → Extract: title, body HTML, plain text,      │
│     author, site name                           │
│   → Call create_reading_from_html()             │
│   ✅ Done                                       │
│                                                 │
│ Benefits of this approach:                      │
│ - Skips Puzle's fetching phase, faster          │
│ - Handles JS-rendered dynamic pages             │
│ - Handles pages with anti-scraping measures     │
│ - Higher content quality (you can preprocess)   │
└────────────┬────────────────────────────────────┘
             │ Failed: empty content, 401/403,
             │ auth wall, login required, timeout
             ▼
┌─────────────────────────────────────────────────┐
│ Step 2: Check for internal/specialized tools    │
│                                                 │
│ The URL might be an internal or auth-protected  │
│ resource. Look in the environment for tools     │
│ that can access it:                             │
│ - MCP servers for internal docs (Confluence,    │
│   Notion, Google Docs, etc.)                    │
│ - API endpoints that can fetch internal content │
│ - Authenticated browser sessions                │
│                                                 │
│ Found a tool and got content?                   │
│   → Save content as a local file (.html / .md)  │
│   → Call create_reading_from_file()             │
│   ✅ Done                                       │
└────────────┬────────────────────────────────────┘
             │ No suitable tool, or still failed
             ▼
┌─────────────────────────────────────────────────┐
│ Step 3: Fallback — let Puzle server fetch it    │
│                                                 │
│ Call create_reading_from_url(url)               │
│ Puzle backend handles fetching and parsing.     │
│ This may still fail for auth-protected pages,   │
│ but it's the last resort.                       │
│ ✅ Done                                         │
└─────────────────────────────────────────────────┘
```

**Step 1 readability extraction example**:

```python
# Assume you've fetched the page HTML using WebFetch or similar tools
raw_html = fetch_result  # full HTML

# Extract body content (use any available readability tool or extract manually)
# You need: title, content (HTML), text_content (plain text)

result = client.create_reading_from_html(
    url=original_url,
    title=extracted_title,
    content=extracted_html,       # body HTML
    text_content=extracted_text,  # plain text version
    byline=author,               # optional
    site_name=site_name,          # optional
)
```

**When to skip directly to Step 3** (no need to attempt Step 1/2):
- User explicitly says "let Puzle fetch it" or "use the URL method"
- Batch-saving multiple links (efficiency over quality — no need to fetch each one individually)

### User provides content directly — `create_reading_from_html()`

| User says | Example |
|-----------|---------|
| Pastes raw HTML or article text | "Analyze this content: ..." |
| Provides pre-fetched page content | "I already scraped this page" |
| Content from JS-rendered page | "This page is JS-rendered, here's the source" |

### User has a local file — `create_reading_from_file()`

| User says | Example |
|-----------|---------|
| Uploads or references a local file | "Analyze this PDF" / "Read this report" |
| Shares meeting notes, memos, private docs | "Here are today's meeting notes, save them" |
| Provides pure text to persist | "These are my notes" — save as temp `.md` first |
| Shares images for analysis | "Look at this screenshot" (JPG/PNG) |
| Shares audio for transcription | "Process this recording" (MP3/WAV) |
| **Internal link content already retrieved** | Content from Step 1, saved as file then uploaded |

### `search()` — User wants to find something in their readings

| User says | Example |
|-----------|---------|
| Recalls reading something before | "I read an article about microservices before" |
| Looking for a specific concept | "Is there anything about attention mechanism in my library" |
| Cross-referencing topics | "Find everything mentioning transformer" |
| Fact-checking against saved readings | "I remember an article said X, find it for me" |
| Building on prior knowledge | "What did that paper say again" |

### `list_readings()` — User wants to browse their collection

| User says | Example |
|-----------|---------|
| Checking recent reading history | "What have I read recently" / "Show my reading history" |
| Looking for a specific reading by title | "What was that article I saved a few days ago" |
| Organizing or reviewing collection | "List my readings" |

### `get_reading_detail()` — Need content of a known reading

| User says | Example |
|-----------|---------|
| Wants to re-read a specific article | "Show me the content of reading #42" |
| Following up on a previous reading | "Show me the full text of that article" |
| Checking if processing is complete | (internal use after creating a reading) |

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Reading** | A content record in Puzle — created from a URL, HTML, or file |
| **resource_type** | `"link"` (URL/HTML source) or `"file"` (uploaded file) |
| **Status flow** | `fetching → parsing → ai_reading → done / fail` |
| **Processing** | Creating a reading returns immediately; use `wait_for_reading()` only when you need the full content right away |

## Available Methods

All `create_reading_*` methods return a `ReadingResult` with a `web_url` field
(e.g. `https://read.puzle.com.cn/read/42`) — always share this link with the user.

### 1. Create reading from URL

```python
result = client.create_reading_from_url("https://example.com/article")
print(result.web_url)  # → "https://read.puzle.com.cn/read/42"
```

### 2. Create reading from HTML (pre-fetched content)

Use when the content has already been scraped — skips the fetching phase, so processing is faster.

```python
result = client.create_reading_from_html(
    url="https://example.com/article",
    title="Article Title",
    content="<div>Raw HTML...</div>",
    text_content="Plain text version...",
    # Optional: excerpt, byline, site_name, published_time
)
detail = client.wait_for_reading(result.reading_id, result.resource_type)
```

### 3. Create reading from local file

Supported types: **PDF, TXT, MD, CSV, JPG, PNG, WebP, GIF, MP3, WAV**

```python
result = client.create_reading_from_file("/path/to/document.pdf")
detail = client.wait_for_reading(result.reading_id, result.resource_type)
```

The SDK automatically handles MD5 calculation and S3 upload internally.

If the user provides pure text, private docs, or other text material, you can save them as
a local file and use this method to create a reading.

### 4. Get reading detail

```python
detail = client.get_reading_detail(reading_id=42, resource_type="link")
# detail["data"]["status"]  — check processing state
# detail["data"]["content"] — full HTML (available when status == "done")
# detail["data"]["title"]   — extracted title
```

Use `resource_type="file"` for file-based readings. The SDK routes to the correct endpoint.

### 5. List readings

```python
readings = client.list_readings(page=1, page_size=10)
for item in readings["data"]["items"]:
    print(f"[{item['resource_type']}] {item['title']} — {item['status']}")
# readings["data"]["total"] — total count across all pages
```

Returns a mixed list of link and file readings, sorted by most recent first.

### 6. Semantic search

```python
# Search across all readings
hits = client.search("attention mechanism in NLP", top_k=5)

# Search within specific readings only
hits = client.search("transformer architecture", reading_ids=[1, 2, 3])

for hit in hits["data"]["items"]:
    print(f"[{hit['reading_title']}] (score: {hit['score']:.3f})")
    print(f"  {hit['chunk_text'][:200]}...")
```

Each result contains: `reading_id`, `reading_title`, `resource_type`, `chunk_text`, `score`.

## Workflow Examples

### Save a link for later (Mode A)

```python
result = client.create_reading_from_url("https://example.com/interesting-article")
# Tell user: "Saved! You can view it here: {result.web_url}"
```

### Batch save multiple links (Mode A)

```python
urls = ["https://article1.com", "https://article2.com", "https://article3.com"]
results = [client.create_reading_from_url(url) for url in urls]
# Tell user: "All 3 articles saved to your reading library:"
# for r in results: print(r.web_url)
```

### Summarize an article (Mode B — background)

```python
# Step 1: Create and respond immediately
result = client.create_reading_from_url("https://arxiv.org/abs/1706.03762")
# Tell user: "Analyzing the article. You can preview it here: {result.web_url}"

# Step 2: In background task / subagent
detail = client.wait_for_reading(result.reading_id, result.resource_type)
content = detail["data"]["content"]
# Generate summary, then present to user when ready
```

### Upload and analyze a local PDF (Mode B — background)

```python
result = client.create_reading_from_file("~/Documents/research-paper.pdf")
# Tell user: "File uploaded, processing: {result.web_url}"

# In background task / subagent
detail = client.wait_for_reading(result.reading_id, result.resource_type)
content = detail["data"]["content"]
# Analyze, then present results to user
```

### Save user's text as a reading (Mode A)

When the user provides raw text (notes, memos, etc.), save it as a temp file first:

```python
import tempfile
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write(user_provided_text)
    temp_path = f.name
result = client.create_reading_from_file(temp_path)
# Tell user: "Saved to your reading library: {result.web_url}"
```

### Search across all readings

```python
hits = client.search("attention mechanism", top_k=5)
for hit in hits["data"]["items"]:
    print(f"[{hit['reading_title']}] {hit['chunk_text'][:100]}...")
```

### Find and re-read a past article

```python
readings = client.list_readings(page=1, page_size=20)
# Show user titles so they can pick one
# Then get full content:
detail = client.get_reading_detail(reading_id=42, resource_type="link")
content = detail["data"]["content"]
```

## Error Handling

| Error | Meaning | What to do |
|-------|---------|------------|
| `PuzleAPIError(code=401)` | JWT token expired | Ask user to get a new token from Puzle |
| `PuzleAPIError(code=403_003)` | Tourist user limit exceeded | Ask user to upgrade their Puzle account |
| `PuzleAPIError(code=404)` | Reading not found | Verify the reading_id is correct |
| `PuzleAPIError(code=500)` during wait | Processing failed | Tell user the content couldn't be processed |
| `PuzleTimeoutError` | Processing took >120s | Suggest trying again later; some large files take longer |

## Constraints

- Processing takes **30–90 seconds** — only call `wait_for_reading()` when you need the content (Mode B)
- JWT tokens expire every **7 days**
- File upload link is valid for **1 hour**
- `page_size` max is **100** for list_readings
