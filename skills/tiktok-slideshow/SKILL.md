---
name: tiktok-slideshow
description: >
  Creates TikTok image carousels (slideshows with text overlays on photos) via the ViralBaby API.
  Use when the user wants to: create TikTok slideshows or carousels, find/search for background
  images for social media content, post or upload slideshow content to TikTok, edit slide text,
  or manage image collections for content creation.
  Do NOT use for: general TikTok account management, TikTok analytics or metrics, video editing
  or video creation (this is for photo slideshows only), non-TikTok social media platforms, or
  any task unrelated to creating visual slideshow content for TikTok.
---

# ViralBaby API v1 — TikTok Slideshow Creation

Create image carousels with text overlays for TikTok — search images, build slides, edit text, and upload to TikTok drafts.

Base URL: `https://viralbaby.co`

All endpoints (except auth) require: `Authorization: Bearer $VB_KEY`

**All indices are 1-based** — image indices, slide indices, etc. Slide 1 is the first slide.

---

## Authentication & API Key

**IMPORTANT — check environment variables first, in this order:**

1. **Check `$VB_KEY`** — if set, you already have an API key. Skip straight to using the API.
2. **Check `$VB_PASSWORD`** — if set, you have a saved password. Log in to get a new API key.
3. **If neither exists**, sign up as a new user (see below).

### Sign Up (new user)
```
POST /api/v1/auth
Body: { "email": "user@example.com", "password": "securepassword", "action": "signup" }
Response: { "key": "vb_live_abc123...", "keyId": "uuid", "userId": "user_...", "message": "Account created..." }
```

When signing up, auto-generate a secure password for the user. **Immediately save both** the API key and the password as environment variables so they persist across sessions:
```bash
export VB_KEY="vb_live_..."
export VB_PASSWORD="the-generated-password"
```

### Log In (existing user)
If `$VB_KEY` is missing but `$VB_PASSWORD` is set, log in to get a fresh API key:
```
POST /api/v1/auth
Body: { "email": "user@example.com", "password": "$VB_PASSWORD" }
Response: { "key": "vb_live_abc123...", "keyId": "uuid", "userId": "user_...", "message": "Logged in..." }
```
Then save the new key: `export VB_KEY="vb_live_..."`

The API key is only shown once and cannot be retrieved later. Always save it immediately. Use it as `Authorization: Bearer $VB_KEY` for all other endpoints.

---

## User Preferences

Store and retrieve the user's business context and content style. **Always fetch preferences at the start of a new session before creating any content.**

### Get Preferences
```
GET /api/v1/preferences
Response: {
  "style": { "id": "uuid", "name": "Casual", "content": "8th grade reading level, lowercase, first-person POV..." } | null,
  "product_info": { "id": "uuid", "name": "My Business", "content": "We sell organic skincare products..." } | null
}
```

### Save or Update a Preference
```
PUT /api/v1/preferences
Body: { "type": "style", "name": "My Style", "content": "casual tone, 8th grade reading level..." }
Body: { "type": "product_info", "name": "My Business", "content": "we sell X to Y audience..." }
Response: { "id": "uuid", "type": "style", "name": "...", "content": "..." }
```

Types: `style` (voice/tone/format) or `product_info` (business/product description).

**Workflow:**
1. On first session: `GET /api/v1/preferences` — if both are null, ask the user for their business description and content style, then save with `PUT`
2. On subsequent sessions: fetch silently, use the stored context without asking again
3. User can update preferences anytime by asking (e.g. "update my style to be more professional")

---

## Content Ideation Process

Before creating a slideshow, always think through:

1. **Hook** — what makes someone stop scrolling? Lead with a bold claim, surprising fact, relatable pain point, or "you're doing X wrong" angle
2. **Content** — what does the audience actually need to hear? Use the stored `product_info` for business context
3. **Voice** — use the stored `style` preference for tone and format (reading level, POV, capitalization, etc.)
4. **CTA** — last slide should drive action: follow, save, comment, or visit

Do NOT ask the user to describe their business or style on every session if preferences are already stored.

---

## Image Search

### Search Unsplash
```
POST /api/v1/images/search
Body: { "query": "sunset beach", "per_page": 20, "page": 1, "color": "teal" }
Response: {
  "searchId": "uuid",
  "results": [{
    "index": 1,
    "id": "unsplash-id",
    "description": "A sunset over the ocean",
    "thumbnailUrl": "https://...",
    "url": "https://...",
    "photographer": "John Doe"
  }],
  "total": 500
}
```

Save `searchId` — needed for collection creation and the preview page URL.

**`color` parameter** (optional) — filter results by dominant color. Best values for dark slideshow backgrounds:
- `teal` — moody, atmospheric (works great for most topics)
- `black` — very dark, high drama
- `blue` — cool, calm, professional
- Omit for no filter (broadest results)

Results are automatically diversified across photographers — no two consecutive photos from the same person.

**Image selection modes:**

**Auto mode** (AI picks, no human review):
- Search with a `color` filter matching the content mood
- Use descriptions to reason about background suitability: prefer images described as landscapes, architecture, abstract, nature, or atmospheric scenes — avoid portraits, close-up faces, and busy text-heavy scenes
- Pick 8–12 images from across the result indices (not just the first few)

**Preview mode** (human picks):
- After searching, share the preview URL: `https://viralbaby.co/preview/search/{searchId}`
- Tell the user: "Here are the search results — tell me which numbers you want to use (e.g. '1, 3, 5, 8')"
- Wait for their response, then use those indices to create the collection

---

## Collections

### List Collections
```
GET /api/v1/collections
Response: [{ "id": "uuid", "name": "Beach Vibes", "imageCount": 12, "coverImageUrl": "..." }]
```

### Create Empty Collection
```
POST /api/v1/collections
Body: { "name": "Beach Vibes", "description": "Sunset and ocean photos" }
Response: { "id": "uuid", "name": "Beach Vibes" }
```

### Create Collection from Search Results
```
POST /api/v1/collections/from-search
Body: { "name": "Beach Vibes", "searchId": "uuid", "imageIndices": [1, 4, 6, 8] }
Response: { "collection": { "id": "uuid", "name": "Beach Vibes" }, "stats": { "total": 4, "successful": 4, "failed": 0 } }
```
This downloads the selected search result images to permanent storage. Maximum 30 images per request.

### Get Collection Details
```
GET /api/v1/collections/{id}
Response: { "id": "uuid", "name": "...", "imageCount": 12, "images": [{ "id": "uuid", "url": "https://..." }] }
```

### Delete Collection
```
DELETE /api/v1/collections/{id}
Response: { "success": true }
```

---

## Slideshows

### List Slideshows
```
GET /api/v1/slideshows
GET /api/v1/slideshows?status=draft
Response: [{ "id": "uuid", "title": "...", "status": "draft", "slideCount": 5, "previewUrl": "https://viralbaby.co/preview/uuid" }]
```

### Create Slideshow
Each slide is a background image with text overlays. Maximum 30 slides per slideshow.

Each slide can get its image from three sources (in priority order):
1. `imageUrl` — direct URL to any image
2. `searchId` + `imageIndex` — reference a previous search result by 1-based index
3. `collectionId` — random image from a collection

Text element options:
- `text` (required) — the text content
- `type` (required) — `"title"` (larger, bolder) or `"subtitle"` (smaller)
- `fontSize` (optional) — font size in px, defaults to 16 for title, 14 for subtitle. For better readability on TikTok, consider using 18–20 for titles.
- Text is always white with black outline. Long text auto-wraps to fit within the slide.
- Text positioning is automatic: single elements center vertically, title + subtitle position at 40%/60% for clear separation.

```
POST /api/v1/slideshows
Body: {
  "title": "5 Morning Routine Tips",
  "aspectRatio": "3:4",
  "slides": [
    {
      "imageUrl": "https://example.com/photo.jpg",
      "textElements": [{ "text": "Your morning routine is broken", "type": "title" }]
    },
    {
      "searchId": "uuid",
      "imageIndex": 3,  // 1-indexed
      "textElements": [{ "text": "Here's why", "type": "title", "fontSize": 18 }]
    },
    {
      "collectionId": "uuid",
      "textElements": [
        { "text": "Tip #1: Wake up early", "type": "title" },
        { "text": "Even 30 minutes makes a difference", "type": "subtitle" }
      ]
    }
  ]
}
Response: {
  "id": "uuid",
  "title": "5 Morning Routine Tips",
  "previewUrl": "https://viralbaby.co/preview/uuid",
  "slides": [{ "id": "slide-...", "imageUrl": "...", "textElements": [...] }],
  "status": "draft"
}
```

Aspect ratios: `3:4` (default, best for TikTok), `1:1`, `9:16`, `4:5`

### Get Slideshow
```
GET /api/v1/slideshows/{id}
Response: { "id": "uuid", "title": "...", "slides": [...], "status": "draft", "previewUrl": "..." }
```

### Update Slideshow
Use this to edit slides — change text, reorder, add/remove slides, update title, etc.

```
PUT /api/v1/slideshows/{id}
Body: { "title": "New Title", "slides": [...], "status": "ready_to_publish" }
Response: { "id": "uuid", "title": "New Title", ... }
```

**How to edit slides:**
1. `GET /api/v1/slideshows/{id}` — fetch current slideshow with all slides
2. Modify the `slides` array as needed (change text, reorder, add/remove)
3. `PUT /api/v1/slideshows/{id}` with the updated `slides` array

Each slide in the array has this structure:
```json
{
  "id": "slide-uuid",
  "imageUrl": "https://cdn.viralbaby.co/...",
  "aspectRatio": "3:4",
  "textElements": [
    { "text": "Your hook text here", "type": "title", "fontSize": 16 },
    { "text": "Supporting subtitle", "type": "subtitle", "fontSize": 14 }
  ]
}
```

Keep existing `id` and `imageUrl` when editing text — only change what you need.

### Delete Slideshow
```
DELETE /api/v1/slideshows/{id}
Response: { "success": true }
```

### Render Slides (Server-Side)
Renders slides as JPEG images with text overlaid on background images. Returns S3 URLs.

```
POST /api/v1/slideshows/{id}/render
Body: { "slideIndices": [1, 3] }   // optional (1-indexed), defaults to all slides
Response: { "renderedSlides": [{ "index": 1, "url": "https://s3.../rendered-slide.jpg" }] }
```

---

## TikTok Integration

### Connect TikTok Account
Returns a one-time OAuth URL. Open it in any browser — no dashboard login required.

```
GET /api/v1/tiktok/connect
Response: {
  "authUrl": "https://www.tiktok.com/v2/auth/authorize/?...",
  "message": "Open this URL in any browser to connect your TikTok account."
}
```

Give the `authUrl` to the user to open in their browser. They will complete TikTok's OAuth flow and see a success page when done. This only needs to be done once.

### Check Connection Status
```
GET /api/v1/tiktok/status
Response: { "connected": true, "tokenExpired": false, "user": { "display_name": "..." } }
// or
Response: { "connected": false, "message": "TikTok not connected..." }
```

### Upload to TikTok Drafts
Renders all slides server-side and uploads to the user's **TikTok drafts** (not published directly). The user must open the TikTok app to review and publish from their drafts.

```
POST /api/v1/tiktok/upload
Body: {
  "slideshowId": "uuid",
  "title": "5 Morning Routine Tips",
  "description": "I used to wake up exhausted every single day. Hitting snooze 5 times, scrolling my phone before my feet even touched the floor...\n\nThen I made 3 small changes and everything shifted. These aren't complicated hacks — they're simple habits anyone can start tomorrow.\n\nSave this for your morning tomorrow 👇",
  "hashtags": ["morningroutine", "productivity", "tips"]
}
Response: { "success": true, "publishId": "tiktok-publish-id", "renderedSlides": 5 }
```

- `title` — short title for the TikTok post
- `description` — caption text, up to 4000 characters. **Write long, detailed descriptions** — longer captions tend to perform better on TikTok. Include storytelling, context, call-to-action, and relatable hooks. Aim for 500–2000 characters minimum, not just 1-2 sentences.
- `hashtags` — array of up to 5 hashtags (with or without `#` prefix, auto-added). Appended to the description.

After a successful upload, tell the user: "Your slideshow has been uploaded to your TikTok drafts. Open the TikTok app to review and publish it."

---

## Complete Workflow Example

Here's how to create and upload a slideshow end-to-end:

```
0. Check credentials (in order):
   a. If $VB_KEY is set → skip to step 1
   b. If $VB_PASSWORD is set → POST /api/v1/auth { "email": "...", "password": "$VB_PASSWORD" } → export VB_KEY="vb_live_..."
   c. Otherwise → POST /api/v1/auth { "email": "...", "password": "<auto-generate>", "action": "signup" } → export VB_KEY="vb_live_..." && export VB_PASSWORD="..."

0b. Fetch preferences
   GET /api/v1/preferences
   → If style or product_info is null, ask user and save with PUT /api/v1/preferences
   → Use stored context for all content decisions going forward

1. Search for images
   POST /api/v1/images/search  { "query": "morning routine aesthetic" }
   → save searchId

2. Create a collection from search results
   POST /api/v1/collections/from-search  { "name": "Morning Routine", "searchId": "...", "imageIndices": [1, 3, 6, 9, 12] }
   → save collectionId

3. Create the slideshow (one slide per element in the array, up to 30 slides)
   POST /api/v1/slideshows  {
     "title": "5 Morning Routine Tips",
     "aspectRatio": "3:4",
     "slides": [
       { "collectionId": "...", "textElements": [{ "text": "Your morning routine is broken", "type": "title" }] },
       { "collectionId": "...", "textElements": [{ "text": "Tip #1: Wake up at the same time", "type": "title" }, { "text": "Consistency beats motivation", "type": "subtitle" }] },
       { "collectionId": "...", "textElements": [{ "text": "Tip #2: No phone for 30 min", "type": "title" }] },
       { "collectionId": "...", "textElements": [{ "text": "Tip #3: Move your body", "type": "title" }] },
       { "collectionId": "...", "textElements": [{ "text": "Follow for more tips", "type": "title" }] }
     ]
   }
   → save slideshowId, get previewUrl

4. (Optional) Edit slides
   GET /api/v1/slideshows/{id}  → get current slides
   Modify text/elements as needed, then:
   PUT /api/v1/slideshows/{id}  { "slides": [...updated slides...] }

5. Preview the slideshow
   Share previewUrl with the user so they can verify in their browser

6. Connect TikTok (first time only)
   GET /api/v1/tiktok/connect  → give authUrl to user to open in browser → complete OAuth
   GET /api/v1/tiktok/status   → verify connected: true

7. Upload to TikTok drafts
   POST /api/v1/tiktok/upload  { "slideshowId": "...", "title": "5 Morning Routine Tips", "description": "I used to wake up and immediately reach for my phone...\n\n(write a long, detailed caption — 500-2000+ chars)", "hashtags": ["morningroutine", "productivity"] }
   → Tell user to open TikTok app to review and publish from drafts
```

---

## Billing

Free tier: 5 TikTok uploads. Pro: $49 one-time payment, unlimited uploads.

The upload endpoint (`POST /api/v1/tiktok/upload`) is the only gated endpoint. All other endpoints (search, collections, slideshows, editing) are free and unlimited.

### Check Billing Status
```
GET /api/v1/billing
Authorization: Bearer $VB_KEY
Response: {
  "plan": "free",
  "uploadCount": 3,
  "limit": 5,
  "upgradeUrl": "https://viralbaby.co/checkout?userId=user_xxx"
}
```

### Handling 402 (Upload Limit Reached)
When the free upload limit is exhausted, `POST /api/v1/tiktok/upload` returns:
```
HTTP 402
{
  "error": "Free upload limit reached. Upgrade to Pro for unlimited uploads.",
  "plan": "free",
  "uploadCount": 5,
  "limit": 5,
  "upgradeUrl": "https://viralbaby.co/checkout?userId=user_xxx"
}
```

When you receive a 402:
1. Tell the user they've used all 5 free uploads
2. Share the `upgradeUrl` so they can upgrade to Pro ($49 one-time)
3. After payment, uploads work immediately — no action needed from the user

### Pro Plan
After upgrading, `GET /api/v1/billing` returns:
```json
{ "plan": "pro", "uploadCount": 5, "limit": "unlimited" }
```

---

## Feedback & Error Reporting

If you encounter an error from the API, or if the user shares feedback about ViralBaby, report it:

```
POST /api/v1/feedback
Body: { "type": "error", "message": "POST /api/v1/tiktok/upload returned 500: Internal server error. Slideshow ID: abc123" }
Body: { "type": "feedback", "message": "User says: would love to be able to change font styles" }
```

- `type` — `"error"` for API errors/bugs, `"feedback"` for user suggestions (defaults to `"feedback"`)
- `message` — free-form text. For errors, include the endpoint, status code, error message, and any relevant IDs. For feedback, include the user's words.

Report errors automatically when an API call fails unexpectedly (5xx, or repeated 4xx that shouldn't happen). Don't report 401/402 — those are expected.

---

## Error Responses

All errors follow this format:
```json
{ "error": "Human-readable error message" }
```

Common status codes:
- `400` — Bad request (missing/invalid parameters)
- `401` — Invalid or missing API key
- `402` — Free upload limit reached (includes `upgradeUrl`)
- `404` — Resource not found
- `500` — Server error
