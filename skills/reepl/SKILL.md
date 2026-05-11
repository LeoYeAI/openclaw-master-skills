---
name: LinkedIn Content Creation Skill by Reepl
description: Manage your LinkedIn presence with Reepl -- create drafts, publish and schedule posts, manage contacts and collections, generate AI images, create carousels, post to Twitter/X, and maintain your voice profile. Requires a Reepl account (reepl.io).
homepage: https://reepl.io
metadata: {"openclaw":{"requires":{"env":["REEPL_MCP_KEY"]},"primaryEnv":"REEPL_MCP_KEY"}}
---

# LinkedIn Content Creation via Reepl

Full LinkedIn content management through Reepl's MCP integration. Write posts in your authentic voice, schedule content, manage drafts, generate AI images, create carousels, post to Twitter/X, browse your saved content library, and maintain contacts -- all from your AI assistant.

## Prerequisites

1. **Reepl account** -- sign up at [reepl.io](https://reepl.io)
2. **MCP connection** -- connect your account via OAuth (see Setup below)
3. **Gemini API key** (optional) -- required only for AI image generation, link at [Settings > AI Models](https://app.reepl.io/settings/ai-models-api)

## Setup

```
# 1. Visit the OAuth page to connect your Reepl account
https://mcp.reepl.io/oauth/authorize

# 2. Log in with your Reepl credentials (Google or email)

# 3. Copy the API key shown after authorization

# 4. Configure the MCP server endpoint
https://mcp.reepl.io/mcp?key=YOUR_API_KEY
```

If you receive authentication errors at any point, re-authenticate at the URL above.

---

## Available Tools (31 total)

| Tool | Purpose |
|------|---------|
| `create_draft` | Save a new LinkedIn post draft |
| `get_drafts` | List and search your drafts |
| `update_draft` | Edit an existing draft |
| `delete_draft` | Remove a draft |
| `publish_to_linkedin` | Publish a post to LinkedIn immediately |
| `schedule_post` | Queue a post for future publishing |
| `update_scheduled_post` | Change time, content, or settings of a scheduled post |
| `delete_scheduled_post` | Cancel and delete a scheduled post |
| `publish_now` | Immediately publish a scheduled post |
| `schedule_draft` | Schedule an existing draft for publishing |
| `get_published_posts` | View your published LinkedIn posts |
| `get_scheduled_posts` | View your scheduled post queue |
| `add_comment_to_post` | Add a comment to a published post |
| `get_user_profile` | Get your Reepl account info |
| `get_voice_profile` | Read your voice profile (writing style patterns) |
| `update_voice_profile` | Update voice profile with learned patterns |
| `get_contacts` | Browse saved LinkedIn contacts |
| `get_lists` | Browse your contact lists |
| `get_list_contacts` | Get contacts in a specific list |
| `add_contact_to_list` | Add a contact to a list |
| `get_collections` | Browse your saved post collections |
| `get_saved_posts` | Read posts from a specific collection |
| `get_templates` | Browse your post templates and ideas |
| `generate_image` | Generate an AI image for a post (requires Gemini API key) |
| `generate_carousel_content` | Generate AI slide content for a carousel |
| `list_carousel_drafts` | List your saved carousel drafts |
| `get_carousel_draft` | Fetch a specific carousel draft |
| `create_carousel_draft` | Save a new carousel draft |
| `update_carousel_draft` | Edit an existing carousel draft |
| `delete_carousel_draft` | Delete a carousel draft |
| `twitter_create_post` | Create or schedule a Twitter/X post or thread |

---

## Content Rules

All LinkedIn content MUST be plain text. Never use markdown formatting like **bold**, *italic*, or # headings. LinkedIn does not render markdown -- it will appear literally in the feed, looking AI-generated. Use line breaks, spacing, and natural punctuation for structure instead.

LinkedIn posts have a 3,000 character limit.

---

## Tool Reference

### 1. Create Draft

Save a post idea for later editing or publishing.

```json
{
  "content": "Just wrapped up a deep dive into how AI is reshaping B2B sales.\n\nHere are 3 things I learned...",
  "title": "AI in B2B Sales",
  "mediaUrls": ["https://example.com/image.jpg"]
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | Post text (plain text only) |
| `title` | No | Draft title for organization |
| `mediaUrls` | No | Array of image URLs to attach |

### 2. Get Drafts

List and search your saved drafts.

```json
{
  "search": "AI sales",
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `limit` | No | Number of drafts to return (default: 20) |
| `search` | No | Filter drafts by keyword |

### 3. Update Draft

Edit an existing draft's content, title, or images.

```json
{
  "draft_id": "abc-123",
  "content": "Updated post content here...",
  "title": "New Title"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `draft_id` | Yes | ID of the draft to update |
| `content` | No | Updated post text |
| `title` | No | Updated title |
| `mediaUrls` | No | Updated image URLs (replaces existing) |

### 4. Delete Draft

```json
{
  "draft_id": "abc-123"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `draft_id` | Yes | ID of the draft to delete |

---

### 5. Publish to LinkedIn

Publish a post to LinkedIn immediately. This action is irreversible -- always confirm with the user before calling.

```json
{
  "content": "Excited to share that we just hit 10,000 users on Reepl!\n\nBuilding in public has been one of the best decisions we made.\n\nHere's what I'd tell founders who are hesitant to share their journey...",
  "visibility": "PUBLIC"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | Post text (plain text only, max 3000 chars) |
| `mediaUrls` | No | Array of image URLs to include |
| `visibility` | No | `PUBLIC` (default) or `CONNECTIONS` |

### 6. Schedule Post

Queue a post for future publishing. Times are rounded to 15-minute intervals.

```json
{
  "content": "Monday motivation: the best time to start was yesterday. The second best time is now.",
  "scheduledFor": "2026-02-17T08:00:00Z",
  "visibility": "PUBLIC"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | Post text (plain text only, max 3000 chars) |
| `scheduledFor` | Yes | ISO 8601 timestamp (e.g. `2026-02-17T08:00:00Z`) |
| `mediaUrls` | No | Array of image URLs |
| `visibility` | No | `PUBLIC` (default) or `CONNECTIONS` |

**Scheduling tips:**
- Ask the user for their preferred time rather than picking one yourself.
- If they want suggestions, recommend varied slots: early morning (7-8 AM), lunch (12-1 PM), or end of day (5-6 PM) in their timezone.
- Avoid scheduling all posts at the same time -- spread them for better engagement.

### 7. Update Scheduled Post

Change the time, content, visibility, or images on a post that's already scheduled.

```json
{
  "post_id": "post-456",
  "scheduledFor": "2026-02-18T12:30:00Z",
  "content": "Updated content for the scheduled post..."
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `post_id` | Yes | ID of the scheduled post |
| `scheduledFor` | No | New ISO 8601 timestamp |
| `content` | No | Updated post text |
| `visibility` | No | Updated visibility |
| `mediaUrls` | No | Updated image URLs (replaces existing) |

### 8. Delete Scheduled Post

Cancel and remove a scheduled post. Only works on posts with status `scheduled`, `failed`, or `pending_approval`. Published posts cannot be deleted this way.

```json
{
  "post_id": "post-456"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `post_id` | Yes | ID of the scheduled post to delete |

### 9. Publish Now

Immediately queue a scheduled post for publishing by rescheduling it to now. The post will be picked up by the scheduler within a few minutes. Only works on scheduled posts.

```json
{
  "post_id": "post-456"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `post_id` | Yes | ID of the scheduled post to publish immediately |

### 10. Schedule Draft

Schedule an existing draft for LinkedIn publishing. Fetches the draft content and creates a new scheduled post. The original draft remains as a draft.

```json
{
  "draft_id": "abc-123",
  "scheduledFor": "2026-02-17T08:00:00Z"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `draft_id` | Yes | ID of the draft to schedule (use `get_drafts` to find IDs) |
| `scheduledFor` | Yes | ISO 8601 timestamp for when to publish |

---

### 11. Get Published Posts

View the user's published LinkedIn posts. Supports keyword search and pagination.

```json
{
  "limit": 10,
  "search": "AI"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `limit` | No | Number of posts to return (default: 20) |
| `search` | No | Filter posts by keyword (case-insensitive content search) |
| `nextToken` | No | Cursor for pagination -- use the `nextToken` from a previous response |

### 12. Get Scheduled Posts

View posts currently queued for future publishing. Supports status filtering, keyword search, and pagination.

```json
{
  "limit": 10,
  "status": "scheduled"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `limit` | No | Number of posts to return (default: 20) |
| `status` | No | Filter by status: `scheduled` (default), `failed`, `pending_approval`, `changes_requested` |
| `search` | No | Filter posts by keyword (case-insensitive content search) |
| `nextToken` | No | Cursor for pagination -- use the `nextToken` from a previous response |

### 13. Add Comment to Post

Add a comment to a published LinkedIn post. Some post types (reshares, restricted posts) may reject comments -- this is a LinkedIn limitation.

```json
{
  "post_id": "post-456",
  "comment_text": "Great insights! This resonates with what I've seen in enterprise sales."
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `post_id` | Yes | The `postId` of the published post (from `get_published_posts`) |
| `comment_text` | Yes | Comment text (plain text only, max 1250 characters) |

---

### 14. Get User Profile

Returns the user's name, email, and LinkedIn URL. No parameters required.

### 15. Get Voice Profile

Read the user's voice profile -- writing style patterns learned from their published posts. No parameters required.

Returns:
- `userInstructions` -- guidelines the user has set (topics to avoid/emphasize, brand keywords, custom rules, writing samples)
- `generatedProfile` -- LLM-learned patterns (tone dimensions, vocabulary preferences, hook styles, structure patterns, anti-patterns)
- `allowAutoUpdate` -- whether the generated profile can be updated automatically
- `isActive` -- whether the voice profile is active

**Always read the voice profile before generating content.** This is the key to writing posts that sound like the user, not like an AI.

### 16. Update Voice Profile

Update the voice profile with newly learned patterns after analyzing the user's posts.

```json
{
  "generatedProfile": {
    "schema_version": "1.0",
    "tone": { "primary": "conversational-authoritative" },
    "vocabulary": { "signature_phrases": ["here's the thing", "let me break this down"] },
    "structure": { "hook_patterns": [{ "type": "bold-statement" }, { "type": "question" }] },
    "anti_patterns": { "never_do": ["use corporate jargon", "start with 'I'm excited to announce'"] }
  }
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `allowAutoUpdate` | No | Only change if user explicitly requests |
| `isActive` | No | Toggle voice profile on/off |
| `userInstructions` | No | User-controlled guidelines -- only modify if user explicitly asks |
| `generatedProfile` | No | LLM-learned patterns from analyzing posts |

**Important:** Before updating `generatedProfile`, always check that `allowAutoUpdate` is `true`. If the user has locked their profile, do not update it.

---

### 17. Get Contacts

Browse saved LinkedIn contacts and profiles. Supports pagination.

```json
{
  "search": "product manager",
  "limit": 20
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `limit` | No | Number of contacts (default: 20) |
| `search` | No | Filter by name, headline, or keyword |
| `nextToken` | No | Cursor for pagination -- use the `nextToken` from a previous response |

### 18. Get Lists

Browse the user's contact lists (curated groups of contacts).

```json
{
  "search": "leads",
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `search` | No | Filter lists by name |
| `limit` | No | Number of lists (default: 20) |

### 19. Get List Contacts

Get all contacts in a specific contact list. Use `get_lists` to find list IDs.

```json
{
  "list_id": "list-123",
  "limit": 20
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `list_id` | Yes | The ID of the list to fetch contacts from |
| `limit` | No | Number of contacts (default: 20) |
| `nextToken` | No | Cursor for pagination -- use the `nextToken` from a previous response |

### 20. Add Contact to List

Add an existing contact to a contact list. Use `get_contacts` to find profile IDs and `get_lists` to find list IDs.

```json
{
  "profile_id": "profile-abc",
  "list_id": "list-123"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `profile_id` | Yes | The `profileID` of the contact to add |
| `list_id` | Yes | The ID of the list to add the contact to |

---

### 21. Get Collections

Browse saved post collections (groups of bookmarked LinkedIn posts).

```json
{
  "search": "inspiration",
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `search` | No | Filter collections by name |
| `limit` | No | Number of collections (default: 20) |

### 22. Get Saved Posts

Read posts from a specific collection. Use `get_collections` first to find the collection ID.

```json
{
  "collectionID": "col-789",
  "search": "storytelling",
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `collectionID` | Yes | The collection to fetch from |
| `limit` | No | Number of posts (default: 20) |
| `search` | No | Filter posts by keyword |

### 23. Get Templates

Browse post templates and content ideas saved in the user's library.

```json
{
  "search": "product launch",
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `limit` | No | Number of templates (default: 20) |
| `search` | No | Filter by keyword |
| `catalogID` | No | Filter by specific catalog |

---

### 24. Generate Image

Generate an AI image for a LinkedIn post using Google Gemini. Requires the user to have linked their Gemini API key in [Reepl settings](https://app.reepl.io/settings/ai-models-api).

```json
{
  "style": "infographic",
  "postContent": "3 ways AI is changing B2B sales in 2026..."
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `style` | Yes | Image style (see table below) |
| `postContent` | No | Post content for context |
| `customPrompt` | If style is `custom` | Your own image prompt |

**Available styles:**

| Style | Output |
|-------|--------|
| `infographic` | Professional data visuals and charts |
| `minimal-illustration` | Clean line art illustrations |
| `bold-text` | Typography and quote cards |
| `screenshot-social-proof` | Mockup screenshots |
| `comic-storyboard` | Comic-style panels |
| `realistic-portrait` | Photorealistic scenes |
| `diagram-flowchart` | Diagrams and process flows |
| `custom` | Your own prompt (requires `customPrompt`) |

**Always show the generated image to the user for approval before publishing.** Pass the returned URL as `mediaUrls` when calling `publish_to_linkedin` or `schedule_post`.

---

### 25. Generate Carousel Content

Generate AI slide content for a LinkedIn carousel. Supports plain text topics, YouTube URLs, and article URLs. Returns slide headlines and body text to pass into `create_carousel_draft`.

Note: the API adds a hook slide and CTA slide automatically, so the actual slide count will be `number_of_slides + 2`.

```json
{
  "topic": "remote work productivity tips",
  "number_of_slides": 5
}
```

```json
{
  "url": "https://youtube.com/watch?v=...",
  "number_of_slides": 6
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `topic` | No | Topic or subject for the carousel (use for plain text topics) |
| `url` | No | YouTube or article URL to extract content from |
| `number_of_slides` | No | Number of content slides to generate (1-10, default: 5) |

### 26. List Carousel Drafts

List the user's carousel drafts saved in Reepl.

```json
{
  "search": "productivity",
  "limit": 10
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `search` | No | Filter drafts by title |
| `limit` | No | Number of drafts to return (default: 20) |

### 27. Get Carousel Draft

Fetch a single carousel draft by ID, including all slide content, theme, and styling.

```json
{
  "draft_id": "carousel-abc"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `draft_id` | Yes | The draft ID (use `list_carousel_drafts` to find IDs) |

### 28. Create Carousel Draft

Save a new carousel draft in Reepl. Pass slides from `generate_carousel_content` or write your own. If no theme or colors are specified, your saved brand kit styling is applied automatically.

```json
{
  "title": "5 Remote Work Tips",
  "slides": [
    { "headline": "Stop working from the couch", "body": "Your brain associates spaces with activities. Create a dedicated workspace." },
    { "headline": "Time-block your deep work", "body": "90-minute focus blocks beat 8 hours of fragmented attention every time." }
  ],
  "theme": "3"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `title` | Yes | Title for this carousel draft |
| `slides` | Yes | Array of slides, each with a `headline` (required) and optional `body` |
| `theme` | No | Theme preset ID (`'1'` through `'22'`). Leave unset to use brand kit default |
| `title_font_size` | No | Font size for slide titles: `lg`, `md` (default), or `sm` |
| `body_font_size` | No | Font size for slide body text: `lg`, `md` (default), or `sm` |

### 29. Update Carousel Draft

Update an existing carousel draft. Only provide the fields you want to change -- unspecified fields are left as-is. Note: providing `slides` replaces ALL slides in the carousel.

```json
{
  "draft_id": "carousel-abc",
  "title": "Updated Title",
  "slides": [
    { "headline": "New headline", "body": "New body text" }
  ]
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `draft_id` | Yes | The ID of the draft to update |
| `title` | No | New title |
| `slides` | No | Replacement slides (replaces ALL existing slides) |
| `theme` | No | New theme preset ID (`'1'` through `'22'`) |
| `title_font_size` | No | `lg`, `md`, or `sm` |
| `body_font_size` | No | `lg`, `md`, or `sm` |

### 30. Delete Carousel Draft

Permanently delete a carousel draft. This cannot be undone.

```json
{
  "draft_id": "carousel-abc"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `draft_id` | Yes | The ID of the carousel draft to delete |

---

### 31. Twitter/X: Create Post

Create or schedule a Twitter/X post or thread. Requires a Twitter account connected in Reepl Settings > Integrations and an active Premium subscription.

For a single tweet, pass an array with one item. For a thread, pass multiple items in order.

```json
{
  "threadTweets": [
    { "index": 0, "text": "I spent 6 months studying how top creators grow on LinkedIn. Here's what actually works (thread):" },
    { "index": 1, "text": "1/ Consistency beats virality. Posting 3x/week for 6 months outperforms a single viral post every time." },
    { "index": 2, "text": "2/ Comments matter more than posts. Thoughtful replies on big accounts drive more followers than original posts." }
  ],
  "scheduledFor": "2026-03-15T14:00:00Z"
}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `threadTweets` | Yes | Array of tweet objects with `index` (0-based position) and `text` (max 280 chars each) |
| `scheduledFor` | No | ISO 8601 timestamp. If omitted, post is saved as a draft (status: pending) |
| `linkedPostId` | No | The `postId` of a LinkedIn post this thread was cross-posted from |

---

## Common Patterns

### Pattern 1: Write a Post in the User's Voice

```
1. get_voice_profile          -- read their writing style
2. Ask user for topic          -- what do they want to write about?
3. Write draft (plain text!)   -- match their tone, hooks, vocabulary
4. Show draft, get feedback    -- iterate until they're happy
5. create_draft OR publish     -- save or go live
```

### Pattern 2: Schedule a Week of Content

```
1. get_voice_profile           -- read writing style
2. get_templates               -- browse content ideas
3. get_saved_posts             -- browse inspiration from collections
4. Write 3-5 posts             -- vary topics, hooks, formats
5. schedule_post (x5)          -- spread across Mon-Fri at varied times
```

### Pattern 3: Repurpose Saved Content

```
1. get_collections             -- find the right collection
2. get_saved_posts             -- browse posts in it
3. Pick a post, rewrite it     -- new angle, user's voice
4. create_draft or publish     -- save or go live
```

### Pattern 4: Post with AI-Generated Image

```
1. Write the post content first
2. generate_image              -- use post content as context
3. Show the image to user      -- get approval
4. publish_to_linkedin         -- pass image URL in mediaUrls
```

### Pattern 5: Analyze and Update Voice Profile

```
1. get_published_posts         -- fetch recent posts (limit: 20)
2. Analyze patterns            -- tone, hooks, vocabulary, structure
3. get_voice_profile           -- check if allowAutoUpdate is true
4. update_voice_profile        -- save learned patterns to generatedProfile
```

### Pattern 6: Create a LinkedIn Carousel

```
1. Read carousel_guidelines prompt  -- understand content and styling rules
2. generate_carousel_content        -- provide topic or URL
3. Review slides with user          -- adjust if needed
4. create_carousel_draft            -- save with brand kit styling
5. Share the deep link              -- user fine-tunes in Reepl editor
6. update_carousel_draft            -- apply any requested edits
```

### Pattern 7: Cross-Post to Twitter/X

```
1. Write or retrieve the LinkedIn post content
2. Adapt for Twitter format           -- split into 280-char chunks for threads
3. twitter_create_post                -- schedule or save as draft
4. Pass linkedPostId if cross-posting -- links the Twitter thread to the LinkedIn post
```

### Pattern 8: Schedule a Draft

```
1. get_drafts                  -- find the draft to publish
2. Ask user for preferred time -- or suggest morning/lunch/evening slots
3. schedule_draft              -- pass draft_id and scheduledFor
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `Session expired or invalid` | OAuth token expired | Re-authenticate at https://mcp.reepl.io/oauth/authorize |
| `Content exceeds 3000 character limit` | Post too long | Shorten the content |
| `draft_id is required` | Missing draft ID | Call `get_drafts` first to find the ID |
| `collectionID is required` | Missing collection ID | Call `get_collections` first to find the ID |
| `GEMINI_NOT_LINKED` | No Gemini API key | User must link key at https://app.reepl.io/settings/ai-models-api |
| `Rate limit exceeded` | Too many requests | Wait a moment and retry |
| `Resource not found` | Invalid ID | The draft/post/collection may have been deleted |
| `Couldn't comment on this post` | Reshare or restricted post | LinkedIn limitation, not a bug -- try a different post |

---

## Best Practices

1. **Always read the voice profile first.** Before writing any content, call `get_voice_profile` to understand the user's writing style. Posts should sound like them, not like an AI.
2. **Plain text only.** Never use markdown in post content. No `**bold**`, no `*italic*`, no `# headings`. LinkedIn renders these literally.
3. **Confirm before publishing.** Always show the final content and get explicit confirmation before calling `publish_to_linkedin`, `schedule_post`, or `publish_now`. These affect the user's real LinkedIn profile.
4. **Vary scheduling times.** Don't default to 9 AM for every post. Ask the user, or suggest varied slots across mornings, lunch, and end of day.
5. **Never fabricate data.** Don't invent engagement metrics, analytics, or post performance numbers. Only report what the API returns.
6. **Respect voice profile locks.** If `allowAutoUpdate` is false, do not modify `generatedProfile`. The user has intentionally locked their voice profile.
7. **Use the library.** Before writing from scratch, check templates and saved posts for inspiration. The user has curated these for a reason.
8. **Read carousel guidelines before creating carousels.** Call the `carousel_guidelines` prompt to understand content rules and the slide structure before generating or saving carousel content.

---

## See Also

- [Reepl](https://reepl.io) -- AI-powered LinkedIn content management platform
- [Reepl Help Center](https://help.reepl.io) -- Documentation and guides
- [MCP Setup Guide](https://mcp.reepl.io) -- Connect your Reepl account to Claude
- [Reepl Chrome Extension](https://chromewebstore.google.com/detail/reepl/geomampobbapgnflneaofdplfomdkejn) -- AI writing assistant for LinkedIn
