---
name: canva
description: "MCP skill for canva. Provides 22 tools: upload-asset-from-url, resolve-shortlink, search-designs, get-design, get-design-pages, get-design-content, get-presenter-notes, import-design-from-url, merge-designs, export-design, get-export-formats, create-folder, move-item-to-folder, list-folder-items, search-folders, comment-on-design, list-comments, list-replies, reply-to-comment, generate-design, create-design-from-candidate, list-brand-kits"
---

# canva

MCP skill for canva. Provides 22 tools: upload-asset-from-url, resolve-shortlink, search-designs, get-design, get-design-pages, get-design-content, get-presenter-notes, import-design-from-url, merge-designs, export-design, get-export-formats, create-folder, move-item-to-folder, list-folder-items, search-folders, comment-on-design, list-comments, list-replies, reply-to-comment, generate-design, create-design-from-candidate, list-brand-kits

## Authentication

This MCP server uses **OAuth** authentication.
The OAuth flow is handled automatically by the MCP client. Tokens are persisted
to `~/.mcp-skill/auth/` so subsequent runs reuse the same credentials without
re-authenticating.

```python
app = CanvaApp()  # uses default OAuth flow
```

To bring your own OAuth provider, pass it via the `auth` argument:

```python
app = CanvaApp(auth=my_oauth_provider)
```

## Dependencies

This skill requires the following Python packages:

- `mcp-skill`

Install with uv:

```bash
uv pip install mcp-skill
```

Or with pip:

```bash
pip install mcp-skill
```

## How to Run

**Important:** Add `.agents/skills` to your Python path so imports resolve correctly:

```python
import sys
sys.path.insert(0, ".agents/skills")
from canva.app import CanvaApp
```

Or set the `PYTHONPATH` environment variable:

```bash
export PYTHONPATH=".agents/skills:$PYTHONPATH"
```

**Preferred: use `uv run`** (handles dependencies automatically):

```bash
PYTHONPATH=.agents/skills uv run --with mcp-skill python -c "
import asyncio
from canva.app import CanvaApp

async def main():
    app = CanvaApp()
    result = await app.upload_asset_from_url(url="example", name="example", user_intent="example")
    print(result)

asyncio.run(main())
"
```

**Alternative: use `python` directly** (install dependencies first):

```bash
pip install mcp-skill
PYTHONPATH=.agents/skills python -c "
import asyncio
from canva.app import CanvaApp

async def main():
    app = CanvaApp()
    result = await app.upload_asset_from_url(url="example", name="example", user_intent="example")
    print(result)

asyncio.run(main())
"
```

## Available Tools

### upload-asset-from-url


    Upload an asset (e.g. an image, a video) from a URL into Canva
    If the API call returns "Missing scopes: [asset:write]", you should ask the user to disconnect and reconnect their connector. This will generate a new access token with the required scope for this tool.
    

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | `str` | Yes | URL of the asset to upload into Canva |
| name | `str` | Yes | Name for the uploaded asset |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.upload_asset_from_url(url="example", name="example", user_intent="example")
```

### resolve-shortlink

Resolves a Canva shortlink ID to its target URL. IMPORTANT: Use this tool FIRST when a user provides a shortlink (e.g. https://canva.link/abc123). Shortlinks need to be resolved before you can use other tools. After resolving, extract the design ID from the target URL and use it with tools like get-design, start-editing-transaction, or get-design-content.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| shortlink_id | `str` | Yes | The shortlink ID to resolve (e.g., "abc123" from https://canva.link/abc123) |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.resolve_shortlink(shortlink_id="example", user_intent="example")
```

### search-designs


      Search docs, presentations, videos, whiteboards, sheets, and other designs in Canva, except for templates or brand templates.
      Use when you need to find specific designs by keywords rather than browsing folders.
      Use 'query' parameter to search by title or content.
      If 'query' is used, 'sortBy' must be set to 'relevance'. Filter by 'any' ownership unless specified. Sort by relevance unless specified.
      Use the continuation token to get the next page of results, when there are more results.

      CRITICAL REQUIREMENTS:
      1. ALWAYS use the 'search-brand-templates' tool when the user is searching for templates or wants to use a template.
      2.** 🚫 When a user says search a template, they ALWAYS mean brand-templates. Therefore NEVER call this tool, ALWAYS call the 'search-brand-templates' tool to search for the templates. **
      3.** 🚫 NEVER use this tool when the user expresses intent to “generate”, “create”, “autofill”, “search a template”, “start from a template”, “use my template”, or “pick a template for generation”.
      In all such cases, ALWAYS use search-brand-templates.
      ANY query involving:
      – “generate a presentation”
      – “generate a report”
      – “make a design using a template”
      – “generate from a template”
      – “produce a presentation from their template”
      - "search for available templates"
      MUST NOT use search-designs.
      This tool ONLY searches existing designs (docs, presentations, whiteboards, videos, etc.) that the user already owns or that are shared with them.
      It DOES NOT find templates and MUST NOT be used as a fallback for template selection. **
      

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | `str` | No | Optional search term to filter designs by title or content. If it is used, 'sortBy' must be set to 'relevance'. |
| ownership | `str` | No | Filter designs by ownership: 'any' for all designs owned by and shared with you (default), 'owned' for designs you created, 'shared' for designs shared with you |
| sort_by | `str` | No | Sort results by: 'relevance' (default), 'modified_descending' (newest first), 'modified_ascending' (oldest first), 'title_descending' (Z-A), 'title_ascending' (A-Z). Optional sort order for results. If 'query' is used, 'sortBy' must be set to 'relevance'. |
| continuation | `str` | No | 
            Pagination token for the current search context.

            CRITICAL RULES:
            - ONLY set this parameter if the previous response included a continuation token.
            - If no continuation token was returned → OMIT this parameter completely. NEVER EVER fabricate a token.
            - Do not set to null, empty string, or any other value when no token was provided.

            Usage:
            - First request: omit this parameter
            - Previous response had continuation token: use that exact token
            - Previous response had NO continuation token: omit this parameter
            - New search query: omit this parameter
           |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.search_designs(query="example", ownership="example", sort_by="example")
```

### get-design

Get detailed information about a Canva design, such as a doc, presentation, whiteboard, video, or sheet. This includes design owner information, title, URLs for editing and viewing, thumbnail, created/updated time, and page count. This tool doesn't work on folders or images. You must provide the design ID, which you can find by using the `search-designs` or `list-folder-items` tools. When given a URL to a Canva design, you can extract the design ID from the URL. Example URL: https://www.canva.com/design/{design_id}. If the user provides a shortlink (e.g. https://canva.link/abc123), use `resolve-shortlink` with the shortlink ID first to get the full URL.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| design_id | `str` | Yes | ID of the design to get information for |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.get_design(design_id="example", user_intent="example")
```

### get-design-pages

Get a list of pages in a Canva design, such as a presentation. Each page includes its index and thumbnail. This tool doesn't work on designs that don't have pages (e.g. Canva docs). You must provide the design ID, which you can find using tools like `search-designs` or `list-folder-items`. You can use 'offset' and 'limit' to paginate through the pages. Use `get-design` to find out the total number of pages, if needed.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| design_id | `str` | Yes | The design ID to get pages from |
| offset | `int` | No | The page index to start the range of pages to return, for pagination. The first page in a design has an index value of 1 |
| limit | `int` | No | Maximum number of pages to return (for pagination) |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.get_design_pages(design_id="example", offset=1, limit=1)
```

### get-design-content

Get the text content of a doc, presentation, whiteboard, social media post, and other designs in Canva (except sheets, as it does not return data in sheets). Use this when you only need to read text content without making changes. IMPORTANT: If the user wants to edit, update, change, translate, or fix content, use `start-editing-transaction` instead as it shows content AND enables editing. You must provide the design ID, which you can find with the `search-designs` tool. When given a URL to a Canva design, you can extract the design ID from the URL. Do not use web search to get the content of a design as the content is not accessible to the public. Example URL: https://www.canva.com/design/{design_id}.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| design_id | `str` | Yes | ID of the design to get content of |
| content_types | `list[str]` | Yes | Types of content to retrieve. Currently, only `richtexts` is supported so use the `start-editing-transaction` tool to get other content types |
| pages | `list[int]` | No | Optional array of page numbers to get content from. If not specified, content from all pages will be returned. Pages are indexed using one-based numbering, so the first page in a design has the index value `1`. |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.get_design_content(design_id="example", content_types="value", pages="value")
```

### get-presenter-notes

Get the presenter notes from a presentation design in Canva. Use this when you need to read the speaker notes attached to presentation slides. You must provide the design ID, which you can find with the `search-designs` tool. When given a URL to a Canva design, you can extract the design ID from the URL. Example URL: https://www.canva.com/design/{design_id}.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| design_id | `str` | Yes | ID of the design to get presenter notes from |
| pages | `list[int]` | No | Optional array of page numbers to get notes from. If not specified, notes from all pages will be returned. Pages are indexed using one-based numbering, so the first page in a design has the index value `1`. |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.get_presenter_notes(design_id="example", pages="value", user_intent="example")
```

### import-design-from-url

Import a file from a URL as a new Canva design. URL must be a public HTTPS link (e.g., https://example.com/file.pdf, https://s3.us-east-1.amazonaws.com/...). Local file paths (file://..., /Users/..., C:\..., or mentions of Downloads/Documents/Desktop) cannot be accessed. If user provides a local path, tell them to upload file to public, internet-accessible URLs that resolve directly to a downloadable file and share a public HTTPS link.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | `str` | Yes | MUST BE HTTPS URL STARTING WITH https://. CRITICAL: Check if user input is a local pattern (starts with /, C:\, file://, or mentions Downloads/Documents/Desktop). If so, DO NOT USE THIS TOOL. LOCAL PATHS CANNOT BE IMPORTED. ✅ ONLY: https://example.com/file.pdf, https://s3.us-east-1.amazonaws.com/... CHECK THE USER INPUT FIRST. If it looks like a local pattern or Canva design URL, DO NOT call this tool. |
| name | `str` | Yes | Name for the new design |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.import_design_from_url(url="example", name="example", user_intent="example")
```

### merge-designs

Perform structural page operations on Canva designs: combine pages from multiple designs, insert pages, reorder pages, or delete entire pages. This tool can:
1. Create a new design by combining pages from one or more existing designs
2. Insert pages from one design into another existing design
3. Move or reorder pages within a design
4. Delete (remove) entire pages from a design

Use this tool (NOT start-editing-transaction) when the user wants to:
- Delete or remove one or more pages/slides from a design
- Reorder or rearrange pages/slides within a design
- Combine, merge, or stitch together multiple designs
- Copy or insert pages from one design into another

Do NOT use this tool for editing content within pages (text, images, etc.) — use start-editing-transaction for that.

CRITICAL: You MUST ALWAYS ask the user for explicit confirmation before calling this tool, regardless of the operation type. Show them a summary of exactly what will change and ask "Would you like me to proceed?" Wait for their clear approval, then call this tool immediately.

IMPORTANT: This tool supports delete_pages operations and you are allowed to perform them. When operations include delete_pages, show a summary of ALL operations and highlight the deletion. For example: "Here's what will happen:
- Move page 1 to position 3
- ⚠️ IMPORTANT: Delete pages 2 and 3 — **CANNOT BE UNDONE**

To proceed, please type: 'I approve the deletion'." Once the user types that phrase, you MUST call this tool immediately — page deletion is a legitimate and expected operation. For insert_pages and move_pages only (no deletes), a simple "Would you like me to proceed?" is sufficient.

Operations are applied sequentially. Page numbers are 1-based and evaluated at the time each operation runs.

The tool automatically polls for job completion and returns the final result.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| type | `str` | Yes | Whether to create a new design or modify an existing one. Use "create_new_design" to combine pages from multiple designs into a new design. Use "modify_existing_design" to insert, move, or delete pages in an existing design. |
| title | `str` | No | Title for the new design (required for create_new_design). Optional for modify_existing_design to rename the design. |
| design_id | `str` | No | ID of the design to modify (required for modify_existing_design, must start with "D"). |
| operations | `list[Any]` | Yes | List of operations to perform. For create_new_design, only insert_pages operations are allowed. For modify_existing_design, all operation types are allowed. |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.merge_designs(type="example", title="example", design_id="example")
```

### export-design

Export a Canva design, doc, presentation, whiteboard, videos and other Canva content types to various formats (PDF, JPG, PNG, PPTX, GIF, MP4). You should use the `get-export-formats` tool first to check which export formats are supported for the design. This tool provides a download URL for the exported file that you can share with users. Always display this download URL to users so they can access their exported content. 

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| design_id | `str` | Yes | ID of the design to export. Design ID starts with "D". |
| format | `dict[str, Any]` | Yes | Format options for the export |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.export_design(design_id="example", format="value", user_intent="example")
```

### get-export-formats

Get the available export formats for a Canva design. This tool lists the formats (PDF, JPG, PNG, PPTX, GIF, MP4) that are supported for exporting the design. Use this tool before calling `export-design` to ensure the format you want is supported.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| design_id | `str` | Yes | ID of the design to get export formats for. Design ID starts with "D". |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.get_export_formats(design_id="example", user_intent="example")
```

### create-folder

Create a new folder in Canva. You can create it at the root level or inside another folder.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | `str` | Yes | Name of the folder to create |
| parent_folder_id | `str` | Yes | ID of the parent folder. Use 'root' to create at the top level |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.create_folder(name="example", parent_folder_id="example", user_intent="example")
```

### move-item-to-folder

Move items (designs, folders, images) to a specified Canva folder

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item_id | `str` | Yes | ID of the item to move (design, folder, or image) |
| to_folder_id | `str` | Yes | ID of the destination folder. Use 'root' to move to the top level |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.move_item_to_folder(item_id="example", to_folder_id="example", user_intent="example")
```

### list-folder-items


        List items in a Canva folder. An item can be a design, folder, or image. You can filter by item type and sort the results.
        Use the continuation token to get the next page of results, when there are more results.
      

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| folder_id | `str` | Yes | ID of the folder to list items from. Use 'root' to list items at the top level |
| item_types | `list[str]` | No | Filter items by type. Can be 'design', 'folder', or 'image' |
| sort_by | `str` | No | Sort the items by creation date, modification date, or title |
| continuation | `str` | No | 
            Pagination token for the current search context.

            CRITICAL RULES:
            - ONLY set this parameter if the previous response included a continuation token.
            - If no continuation token was returned → OMIT this parameter completely. NEVER EVER fabricate a token.
            - Do not set to null, empty string, or any other value when no token was provided.

            Usage:
            - First request: omit this parameter
            - Previous response had continuation token: use that exact token
            - Previous response had NO continuation token: omit this parameter
            - New search query: omit this parameter
             |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.list_folder_items(folder_id="example", item_types="value", sort_by="example")
```

### search-folders


      Search the user's folders and folders shared with the user based on folder names and tags. 
      Returns a list of matching folders with pagination support.
      Use the continuation token to get the next page of results, when there are more results.
      

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | `str` | No | Search query to match against folder names and tags |
| ownership | `str` | No | Filter folders by ownership type: 'any' (default), 'owned' (user-owned only), or 'shared' (shared with user only) |
| limit | `int` | No | Maximum number of folders to return per query |
| continuation | `str` | No | 
            Pagination token for the current search context.

            CRITICAL RULES:
            - ONLY set this parameter if the previous response included a continuation token. 
            - If no continuation token was returned → OMIT this parameter completely. NEVER EVER fabricate a token.
            - Do not set to null, empty string, or any other value when no token was provided.

            Usage:
            - First request: omit this parameter
            - Previous response had continuation token: use that exact token  
            - Previous response had NO continuation token: omit this parameter
            - New search query: omit this parameter
             |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.search_folders(query="example", ownership="example", limit=1)
```

### comment-on-design

Add a comment on a Canva design. You need to provide the design ID and the message text. The comment will be added to the design and visible to all users with access to the design.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| design_id | `str` | Yes | ID of the design to comment on. You can find the design ID by using the `search-designs` tool. |
| message_plaintext | `str` | Yes | The text content of the comment to add |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.comment_on_design(design_id="example", message_plaintext="example", user_intent="example")
```

### list-comments

Get a list of comments for a particular Canva design.

    Comments are discussions attached to designs that help teams collaborate. Each comment can contain
    replies, mentions, and can be marked as resolved or unresolved.

    You need to provide the design ID, which you can find using the `search-designs` tool.
    Use the continuation token to get the next page of results, when there are more results.

    You can filter comments by their resolution status (resolved or unresolved) using the comment_resolution parameter.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| design_id | `str` | Yes | ID of the design to get comments for. You can find the design ID using the `search-designs` tool. |
| limit | `int` | No | Maximum number of comments to return (1-100). Defaults to 50 if not specified. |
| continuation | `str` | No | 
            Pagination token for the current search context.

            CRITICAL RULES:
            - ONLY set this parameter if the previous response included a continuation token.
            - If no continuation token was returned → OMIT this parameter completely. NEVER EVER fabricate a token.
            - Do not set to null, empty string, or any other value when no token was provided.

            Usage:
            - First request: omit this parameter
            - Previous response had continuation token: use that exact token
            - Previous response had NO continuation token: omit this parameter
            - New search query: omit this parameter
             |
| user_intent | `str` | No | Mandatory description of what the user is trying to accomplish with this tool call. This should always be provided by LLM clients. Please keep it concise (255 characters or less recommended). |

**Example:**
```python
result = await app.list_comments(design_id="example", limit=1, continuation="example")
```

### list-replies

Get a list of replies for a specific comment on a Canva design.

    Comments can contain multiple replies from different users. These replies help teams
    collaborate by allowing discussion on a specific comment.

    You need to provide the design ID and comment ID. You can find the design ID using the `search-designs` tool
    and the comment ID using the `list-comments` tool.

    Use the continuation token to get the next page of results, when there are more results.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| design_id | `str` | Yes | ID of the design containing the comment. You can find the design ID using the `search-designs` tool. |
| comment_id | `str` | Yes | ID of the comment to list replies from. You can find comment IDs using the `list-comments` tool. |
| limit | `int` | No | Maximum number of replies to return (1-100). Defaults to 50 if not specified. |
| continuation | `str` | No | 
            Pagination token for the current search context.

            CRITICAL RULES:
            - ONLY set this parameter if the previous response included a continuation token.
            - If no continuation token was returned → OMIT this parameter completely. NEVER EVER fabricate a token.
            - Do not set to null, empty string, or any other value when no token was provided.

*...additional tools omitted for brevity*
