---
name: contextui-exchange
description: Interact with the ContextUI Exchange marketplace — browse, search, and download workflows, publish your own (free or paid), post comments, like listings, manage your uploads, and check download history. Use when working with the ContextUI Exchange API, MCP server, or marketplace operations. Admin users can also review, approve/reject submissions, and send feedback to creators.
---

# ContextUI Exchange

The Exchange is ContextUI's marketplace for workflows. Browse, download, publish, comment, like, and manage workflows via REST API or MCP.

## Setup

### API Key

Generate an API key at [contextui.ai](https://contextui.ai) → Account → API Keys.

Set as environment variable:

```bash
export CONTEXTUI_API_KEY="ctxk_your_key_here"
```

All requests require the key in the Authorization header:

```
Authorization: Bearer ctxk_your_key_here
```

### MCP Server (Optional)

Connect your agent to the Exchange via MCP:

```json
{
  "mcpServers": {
    "contextui-exchange": {
      "command": "node",
      "args": ["/path/to/mcp-server/index.js"],
      "env": {
        "CONTEXTUI_API_KEY": "ctxk_your_key_here",
        "CONTEXTUI_API_URL": "https://contextui.ai"
      }
    }
  }
}
```

## REST API

**Base URL:** `https://contextui.ai/.netlify/functions/`

### Browse & Search

```bash
# Search workflows
curl -H "Authorization: Bearer $CONTEXTUI_API_KEY" \
  "https://contextui.ai/.netlify/functions/marketplace?search=video"

# Filter by category
curl -H "Authorization: Bearer $CONTEXTUI_API_KEY" \
  "https://contextui.ai/.netlify/functions/marketplace?category=gen_ai"

# Get specific workflow details
curl -H "Authorization: Bearer $CONTEXTUI_API_KEY" \
  "https://contextui.ai/.netlify/functions/marketplace?id=<UUID>"
```

**Categories:** `gen_ai`, `developer_tools`, `creative_tools`, `productivity`, `games`, `data_tools`, `file_utilities`, `image_processing`, `video_processing`, `llm`

### Download

```bash
curl -H "Authorization: Bearer $CONTEXTUI_API_KEY" \
  "https://contextui.ai/.netlify/functions/marketplace-download?id=<UUID>"
```

Returns presigned S3 download URLs. Requires an active account.

### Comments

```bash
# Get comments
curl -H "Authorization: Bearer $CONTEXTUI_API_KEY" \
  "https://contextui.ai/.netlify/functions/marketplace-comments?listingId=<UUID>"

# Post a comment
curl -X POST -H "Authorization: Bearer $CONTEXTUI_API_KEY" -H "Content-Type: application/json" \
  -d '{"listingId":"<UUID>","body":"Great workflow!"}' \
  "https://contextui.ai/.netlify/functions/marketplace-comments"
```

### Likes

```bash
curl -X POST -H "Authorization: Bearer $CONTEXTUI_API_KEY" -H "Content-Type: application/json" \
  -d '{"listingId":"<UUID>"}' \
  "https://contextui.ai/.netlify/functions/marketplace-like"
```

Toggles like on/off.

### Your Workflows & Downloads

```bash
# List workflows you've published
curl -H "Authorization: Bearer $CONTEXTUI_API_KEY" \
  "https://contextui.ai/.netlify/functions/marketplace-my-workflows"

# List workflows you've downloaded
curl -H "Authorization: Bearer $CONTEXTUI_API_KEY" \
  "https://contextui.ai/.netlify/functions/marketplace-my-downloads"
```

## Publishing Workflows (Programmatic Upload)

Publishing is a 2-step process: init (get presigned S3 URLs) → upload files to S3 → complete (create listing in DB).

### Step 1: Initialize Upload

```bash
curl -X POST -H "Authorization: Bearer $CONTEXTUI_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "metadata": { "title": "My Workflow" },
    "files": [
      { "name": "MyWorkflowWindow.tsx", "size": 12345, "type": "workflow" },
      { "name": "my_server.py", "size": 6789, "type": "workflow" },
      { "name": "thumbnail.png", "size": 50000, "type": "image" }
    ],
    "listingId": "<optional-UUID-for-updates>"
  }' \
  "https://contextui.ai/.netlify/functions/marketplace-upload-init"
```

**File types:** `workflow` (code files), `image` (thumbnails/screenshots, max 5MB), `video` (max 50MB)

**Blocked extensions:** `.exe`, `.msi`, `.dmg`, `.pkg`, `.app`, `.deb`, `.rpm`, `.appimage`, `.apk`, `.ipa`

**Total size limit:** 100MB

Returns `{ listingId, uploadUrls: [{ name, uploadUrl }] }` — use the presigned URLs to PUT files directly to S3.

### Step 2: Upload Files to S3

For each file, PUT directly to the presigned URL:

```bash
curl -X PUT -H "Content-Type: application/octet-stream" \
  --data-binary @MyWorkflowWindow.tsx \
  "<presigned-upload-url>"
```

### Step 3: Complete Upload

```bash
curl -X POST -H "Authorization: Bearer $CONTEXTUI_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "listingId": "<UUID-from-step-1>",
    "title": "My Workflow",
    "description": "What it does...",
    "category": "developer_tools",
    "tags": ["coding", "productivity"],
    "thumbnailUrl": "marketplace/workflows/<UUID>/media/thumbnail.png",
    "screenshotUrls": [],
    "videoUrl": null,
    "workflowFiles": [
      { "name": "MyWorkflowWindow.tsx", "path": "MyWorkflowWindow.tsx", "size": 12345 },
      { "name": "my_server.py", "path": "my_server.py", "size": 6789 }
    ],
    "fileSizeBytes": 19134,
    "priceCents": 0,
    "changelog": "Initial release",
    "contextUiVersionMin": null,
    "creatorDisplayName": "Your Name"
  }' \
  "https://contextui.ai/.netlify/functions/marketplace-upload-complete"
```

**Required fields:** `listingId`, `title`, `category`, `thumbnailUrl`

New uploads go to `review_status: pending`. Updates with new files also reset to pending review.

### Updating an Existing Listing

Pass the existing `listingId` in both init and complete steps. The system creates a new version automatically if workflow files changed. Metadata-only updates don't require re-review.

## Web App Listings

For cloud-hosted web apps (no downloadable workflow files):

```bash
# Initialize web app listing
curl -X POST -H "Authorization: Bearer $CONTEXTUI_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "title": "My Web App",
    "description": "...",
    "category": "data_tools",
    "appUrl": "https://myapp.example.com",
    "thumbnailFile": { "name": "thumb.png", "size": 50000 },
    "pricingModel": "free"
  }' \
  "https://contextui.ai/.netlify/functions/marketplace-webapp-upload"
```

Then complete with:

```bash
curl -X POST -H "Authorization: Bearer $CONTEXTUI_API_KEY" -H "Content-Type: application/json" \
  -d '{ "listingId": "<UUID>", ... }' \
  "https://contextui.ai/.netlify/functions/marketplace-webapp-complete"
```

## Deleting Listings

Owners can delete their own listings. Two-stage: soft-delete first, then optional hard-delete.

```bash
# Soft-delete (hides from Exchange, recoverable)
curl -X POST -H "Authorization: Bearer $CONTEXTUI_API_KEY" -H "Content-Type: application/json" \
  -d '{"listingId":"<UUID>"}' \
  "https://contextui.ai/.netlify/functions/marketplace-delete"

# Hard-delete (permanent, removes S3 files — only works on already soft-deleted listings)
curl -X POST -H "Authorization: Bearer $CONTEXTUI_API_KEY" -H "Content-Type: application/json" \
  -d '{"listingId":"<UUID>","hardDelete":true}' \
  "https://contextui.ai/.netlify/functions/marketplace-delete"
```

## Publishing Guidelines

**Required files for a workflow:**
- `*Window.tsx` — main React component
- `*.meta.json` — icon and color metadata
- `description.txt` — what it does (first line = summary)

**Optional:** Python FastAPI server, `requirements.txt`, `README.md`, screenshots

**Good listings have:**
- Clear description with features and use cases
- Screenshot(s) showing the workflow in action
- Clean code — no dev artifacts (`PLAN.md`, `test.html`, `package-lock.json`, logs)
- Reasonable file size — avoid shipping large data files

**Pricing:** Free or set `priceCents` (minimum applies). 70% goes to creator, 30% to platform.

## Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `marketplace?search=query&category=cat` | Browse/search workflows |
| GET | `marketplace?id=UUID` | Get workflow details |
| GET | `marketplace-comments?listingId=UUID` | Get comments |
| POST | `marketplace-comments` | Post a comment |
| GET | `marketplace-download?id=UUID` | Get download URLs |
| POST | `marketplace-like` | Toggle like |
| GET | `marketplace-my-downloads` | Your downloads |
| GET | `marketplace-my-workflows` | Your workflows |
| POST | `marketplace-upload-init` | Initialize upload (get presigned S3 URLs) |
| POST | `marketplace-upload-complete` | Complete upload (create/update listing) |
| POST | `marketplace-webapp-upload` | Initialize web app listing |
| POST | `marketplace-webapp-complete` | Complete web app listing |
| POST | `marketplace-delete` | Delete your listing (soft or hard) |
