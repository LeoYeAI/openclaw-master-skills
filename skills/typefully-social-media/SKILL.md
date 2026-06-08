---
name: typefully
description: >
  Create, schedule, and manage social media posts via Typefully. ALWAYS use this
  skill when asked to draft, schedule, post, or check tweets, posts, threads, or
  social media content for Twitter/X, LinkedIn, Threads, Bluesky, or Mastodon.
last-updated: 2026-02-10
allowed-tools: Bash(./scripts/typefully.js:*)
---

# Typefully Skill

Create, schedule, and publish social media content across multiple platforms using [Typefully](https://typefully.com).

> **Freshness check**: If more than 30 days have passed since the `last-updated` date above, inform the user that this skill may be outdated and point them to the update options below.

## Keeping This Skill Updated

**Source**: [github.com/typefully/agent-skills](https://github.com/typefully/agent-skills)
**API docs**: [typefully.com/docs/api](https://typefully.com/docs/api)

Update methods by installation type:

| Installation | How to update |
|--------------|---------------|
| CLI (`npx skills`) | `npx skills update` |
| Claude Code plugin | `/plugin update typefully@typefully-skills` |
| Cursor | Remote rules auto-sync from GitHub |
| Manual | Pull latest from repo or re-copy `skills/typefully/` |

API changes ship independently—updating the skill ensures you have the latest commands and workflows.

## Setup

Before using this skill, ensure:

1. **API Key**: Run the setup command to configure your API key securely
   - Get your key at https://typefully.com/?settings=api
   - Run: `<skill-path>/scripts/typefully.js setup` (where `<skill-path>` is the directory containing this SKILL.md)
   - Or set environment variable: `export TYPEFULLY_API_KEY=your_key`

2. **Requirements**: Node.js 18+ (for built-in fetch API). No other dependencies needed.

**Config priority** (highest to lowest):
1. `TYPEFULLY_API_KEY` environment variable
2. `./.typefully/config.json` (project-local, in user's working directory)
3. `~/.config/typefully/config.json` (user-global)

### Handling "API key not found" errors

**CRITICAL**: When you receive an "API key not found" error from the CLI:

1. **Tell the user to run the setup command** - The setup is interactive and requires user input, so you cannot run it on their behalf. Recommend they run it themselves, using the correct path based on where this skill was loaded:
   ```bash
   <skill-path>/scripts/typefully.js setup
   ```

2. **Stop and wait** - After telling the user to run setup, **do not continue with the task**. You cannot create drafts, upload media, or perform any API operations without a valid API key. Wait for the user to complete setup and confirm before proceeding.

3. **DO NOT** attempt any of the following:
   - Searching for API keys in macOS Keychain, `.env` files, or other locations
   - Grepping through config files or directories
   - Looking in the user's Trash or other system folders
   - Constructing complex shell commands to find credentials
   - Drafting content or preparing posts before setup is complete

The setup command will interactively guide the user through configuration. Trust the CLI's error messages and follow their instructions.

> **Note for agents**: All script paths in this document (e.g., `./scripts/typefully.js`) are relative to the skill directory where this SKILL.md file is located. Resolve them accordingly based on where the skill is installed.

## Social Sets

The Typefully API uses the term "social set" to refer to what users commonly call an "account". A social set contains the connected social media platforms (X, LinkedIn, Threads, etc.) for a single identity.

**The CLI supports a default social set** - once configured, most commands work without specifying the social_set_id.

**You can pass the social set either way**:
- Positional: `drafts:list 123`
- Flag: `drafts:list --social-set-id 123` (also supports `--social_set_id`)

When determining which social set to use:

1. **Check for a configured default first** - Run `config:show` to see if a default is already set:
   ```bash
   ./scripts/typefully.js config:show
   ```
   If `default_social_set` is configured, the CLI uses it automatically when you omit the social_set_id.

2. **Check project context** - Look for configuration in project files like `CLAUDE.md` or `AGENTS.md`:

   ```markdown
   ## Typefully
   Default social set ID: 12345
   ```

3. **Single social set shortcut** - If the user only has one social set and no default is configured, use it automatically

4. **Multiple social sets, no default** - Ask the user which to use, then **offer to save their choice as the default**:
   ```bash
   ./scripts/typefully.js config:set-default
   ```
   This command lists available social sets and saves the choice to the config file.

5. **Reuse previously resolved social set** - If determined earlier in the session, use it without asking again

## Common Actions

| User says... | Action |
|--------------|--------|
| "Draft a tweet about X" | `drafts:create --text "..."` (uses default social set) |
| "Post this to LinkedIn" | `drafts:create --platform linkedin --text "..."` |
| "Post to X and LinkedIn" (same content) | `drafts:create --platform x,linkedin --text "..."` |
| "X thread + LinkedIn post" (different content) | Create one draft, then `drafts:update` to add platform (see [Publishing to Multiple Platforms](#publishing-to-multiple-platforms)) |
| "What's scheduled?" | `drafts:list --status scheduled` |
| "Show my recent posts" | `drafts:list --status published` |
| "Schedule this for tomorrow" | `drafts:create ... --schedule "2025-01-21T09:00:00Z"` |
| "Post this now" | `drafts:create ... --schedule now` or `drafts:publish <draft_id> --use-default` |
| "Add notes/ideas to the draft" | `drafts:create ... --scratchpad "Your notes here"` |
| "Check available tags" | `tags:list` |

## Workflow

Follow this workflow when creating posts:

1. **Check if a default social set is configured**:
   ```bash
   ./scripts/typefully.js config:show
   ```
   If `default_social_set` shows an ID, skip to step 3.

2. **If no default, list social sets** to find available options:
   ```bash
   ./scripts/typefully.js social-sets:list
   ```
   If multiple exist, ask the user which to use and offer to set it as default:
   ```bash
   ./scripts/typefully.js config:set-default
   ```

3. **Create drafts** (social_set_id is optional if default is configured):
   ```bash
   ./scripts/typefully.js drafts:create --text "Your post"
   ```
   Note: If `--platform` is omitted, the first connected platform is auto-selected.

   **For multi-platform posts**: See [Publishing to Multiple Platforms](#publishing-to-multiple-platforms) — always use a single draft, even when content differs per platform.

4. **Schedule or publish** as needed

## Working with Tags

Tags help organize drafts within Typefully. **Always check existing tags before creating new ones**:

1. **List existing tags first**:
   ```bash
   ./scripts/typefully.js tags:list
   ```

2. **Use existing tags when available** - if a tag with the desired name already exists, use it directly when creating drafts:
   ```bash
   ./scripts/typefully.js drafts:create --text "..." --tags existing-tag-name
   ```

3. **Only create new tags if needed** - if the tag doesn't exist, create it:
   ```bash
   ./scripts/typefully.js tags:create --name "New Tag"
   ```

**Important**: Tags are scoped to each social set. A tag created for one social set won't appear in another.

## Publishing to Multiple Platforms

If a single draft needs to be created for different platforms, you need to make sure to create **a single draft** and not multiple drafts.

When the content is the same across platforms, create a single draft with multiple platforms:

```bash
# Specific platforms
./scripts/typefully.js drafts:create --platform x,linkedin --text "Big announcement!"

# All connected platforms
./scripts/typefully.js drafts:create --all --text "Posting everywhere!"
```

**IMPORTANT**: When content should be tailored (e.g., X thread with a LinkedIn post version), **still use a single draft** — create with one platform first, then update to add the other:

```bash
# 1. Create draft with the primary platform first
./scripts/typefully.js drafts:create --platform linkedin --text "Excited to share our new feature..."
# Returns: { "id": "draft-123", ... }

# 2. Update the same draft to add another platform with different content
./scripts/typefully.js drafts:update draft-123 --platform x --text "🧵 Thread time!

---

Here's what we shipped and why it matters..." --use-default
```

So make sure to NEVER create multiple drafts unless the user explicitly wants separate drafts for each platform.

## Commands Reference

### User & Social Sets

| Command | Description |
|---------|-------------|
| `me:get` | Get authenticated user info |
| `social-sets:list` | List all social sets you can access |
| `social-sets:get <id>` | Get social set details including connected platforms |

### Drafts

All drafts commands support an optional `[social_set_id]` - if omitted, the configured default is used.
**Safety note**: For commands that take `[social_set_id] <draft_id>`, if you pass only a single argument (the draft_id) while a default social set is configured, you must add `--use-default` to confirm intent.

| Command | Description |
|---------|-------------|
| `drafts:list [social_set_id]` | List drafts (add `--status scheduled` to filter, `--sort` to order) |
| `drafts:get [social_set_id] <draft_id>` | Get a specific draft with full content (single-arg requires `--use-default` if a default is configured) |
| `drafts:create [social_set_id] --text "..."` | Create a new draft (auto-selects platform) |
| `drafts:create [social_set_id] --platform x --text "..."` | Create a draft for specific platform(s) |
| `drafts:create [social_set_id] --all --text "..."` | Create a draft for all connected platforms |
| `drafts:create [social_set_id] --file <path>` | Create draft from file content |
| `drafts:create ... --media <media_ids>` | Create draft with attached media |
| `drafts:create ... --reply-to <url>` | Reply to an existing X post |
| `drafts:create ... --community <id>` | Post to an X community |
| `drafts:create ... --share` | Generate a public share URL for the draft |
| `drafts:create ... --scratchpad "..."` | Add internal notes/scratchpad to the draft |
| `drafts:update [social_set_id] <draft_id> --text "..."` | Update an existing draft (single-arg requires `--use-default` if a default is configured) |
| `drafts:update [social_set_id] <draft_id> --tags "tag1,tag2"` | Update tags on an existing draft (content unchanged) |
| `drafts:update ... --share` | Generate a public share URL for the draft |
| `drafts:update ... --scratchpad "..."` | Update internal notes/scratchpad |
| `drafts:update [social_set_id] <draft_id> --append --text "..."` | Append to existing thread |

### Scheduling & Publishing

**Safety note**: These commands require `--use-default` when using the default social set with a single argument (to prevent accidental operations from ambiguous syntax).

| Command | Description |
|---------|-------------|
| `drafts:delete <social_set_id> <draft_id>` | Delete a draft (explicit IDs) |
| `drafts:delete <draft_id> --use-default` | Delete using default social set |
| `drafts:schedule <social_set_id> <draft_id> --time next-free-slot` | Schedule to next available slot |
| `drafts:schedule <draft_id> --time next-free-slot --use-default` | Schedule using default social set |
| `drafts:publish <social_set_id> <draft_id>` | Publish immediately |
| `drafts:publish <draft_id> --use-default` | Publish using default social set |

### Tags

| Command | Description |
|---------|-------------|
| `tags:list [social_set_id]` | List all tags |
| `tags:create [social_set_id] --name "Tag Name"` | Create a new tag |

### Media

| Command | Description |
|---------|-------------|
| `media:upload [social_set_id] <file_path>` | Upload media, wait for processing, return ready media_id |
| `media:upload ... --no-wait` | Upload and return immediately (use media:status to poll) |
| `media:upload ... --timeout <seconds>` | Set custom timeout (default: 60) |
| `media:status [social_set_id] <media_id>` | Check media upload status |

### Setup & Configuration

| Command | Description |
|---------|-------------|
| `setup` | Interactive setup - prompts for API key, storage location, and default social set |
| `setup --key <key> --location <global\|local>` | Non-interactive setup for scripts/CI (auto-selects default if only one social set) |
| `setup --key <key> --default-social-set <id>` | Non-interactive setup with explicit default social set |
| `setup --key <key> --no-default` | Non-interactive setup, skip default social set selection |
| `config:show` | Show current config, API key source, and default social set |
| `config:set-default [social_set_id]` | Set default social set (interactive if ID omitted) |

## Examples

### Set up default social set
```bash
# Check current config
./scripts/typefully.js config:show

# Set default (interactive - lists available social sets)
./scripts/typefully.js config:set-default

# Set default (non-interactive)
./scripts/typefully.js config:set-default 123 --location global
```

### Create a tweet (using default social set)
```bash
./scripts/typefully.js drafts:create --text "Hello, world!"
```

### Create a tweet with explicit social_set_id
```bash
./scripts/typefully.js drafts:create 123 --text "Hello, world!"
```

### Create a cross-platform post (specific platforms)
```bash
./scripts/typefully.js drafts:create --platform x,linkedin,threads --text "Big announcement!"
```

### Create a post on all connected platforms
```bash
./scripts/typefully.js drafts:create --all --text "Posting everywhere!"
```

### Create and schedule for next slot
```bash
./scripts/typefully.js drafts:create --text "Scheduled post" --schedule next-free-slot
```

### Create with tags
```bash
./scripts/typefully.js drafts:create --text "Marketing post" --tags marketing,product
```

### List scheduled posts sorted by date
```bash
./scripts/typefully.js drafts:list --status scheduled --sort scheduled_date
```

### Reply to a tweet
```bash
./scripts/typefully.js drafts:create --platform x --text "Great thread!" --reply-to "https://x.com/user/status/123456"
```

### Post to an X community
```bash
./scripts/typefully.js drafts:create --platform x --text "Community update" --community 1493446837214187523
```

### Create draft with share URL
```bash
./scripts/typefully.js drafts:create --text "Check this out" --share
```

### Create draft with scratchpad notes
```bash
./scripts/typefully.js drafts:create --text "Launching next week!" --scratchpad "Draft for product launch. Coordinate with marketing team before publishing."
```

### Upload media and create post with it
```bash
# Single command handles upload + polling - returns when ready!
./scripts/typefully.js media:upload ./image.jpg
# Returns: {"media_id": "abc-123-def", "status": "ready", "message": "Media uploaded and ready to use"}

# Create post with the media attached
./scripts/typefully.js drafts:create --text "Check out this image!" --media abc-123-def
```

### Upload multiple media files
```bash
# Upload each file (each waits for processing)
./scripts/typefully.js media:upload ./photo1.jpg  # Returns media_id: id1
./scripts/typefully.js media:upload ./photo2.jpg  # Returns media_id: id2

# Create post with multiple media (comma-separated)
./scripts/typefully.js drafts:create --text "Photo dump!" --media id1,id2
```

### Add media to an existing draft
```bash
# Upload media
./scripts/typefully.js media:upload ./new-image.jpg  # Returns media_id: xyz

# Update draft with media (456 is the draft_id)
./scripts/typefully.js drafts:update 456 --text "Updated post with image" --media xyz --use-default
```

### Setup (interactive)
```bash
./scripts/typefully.js setup
```

### Setup (non-interactive, for scripts/CI)
```bash
# Auto-selects default social set if only one exists
./scripts/typefully.js setup --key typ_xxx --location global

# With explicit default social set
./scripts/typefully.js setup --key typ_xxx --location global --default-social-set 123

# Skip default social set selection entirely
./scripts/typefully.js setup --key typ_xxx --no-default
```

## Platform Names

Use these exact names for the `--platform` option:
- `x` - X (formerly Twitter)
- `linkedin` - LinkedIn
- `threads` - Threads
- `bluesky` - Bluesky
- `mastodon` - Mastodon

## Draft URLs

Typefully draft URLs contain the social set and draft IDs:
```
https://typefully.com/?a=<social_set_id>&d=<draft_id>
```

Example: `https://typefully.com/?a=12345&d=67890`
- `a=12345` → social_set_id
- `d=67890` → draft_id

## Draft Scratchpad

**When the user explictly asked to add notes, ideas, or anything else in the draft scratchpad, use the `--scratchpad` flag—do NOT write to local files!**

The `--scratchpad` option attaches internal notes directly to the Typefully draft. These notes:
- Are visible in the Typefully UI alongside the draft
- Stay attached to the draft permanently
- Are private and never published to social media
- Are perfect for storing thread expansion ideas, research notes, context, etc.

```bash
# CORRECT: Notes attached to the draft in Typefully
./scripts/typefully.js drafts:create 123 --text "My post" --scratchpad "Ideas for expanding: 1) Add stats 2) Include quote"

# WRONG: Do NOT write notes to local files when the user wants them in Typefully
# Writing to /tmp/scratchpad/ or any local file is NOT the same thing
```

## Automation Guidelines

When automating posts, especially on X, follow these rules to keep accounts in good standing:

- **No duplicate content** across multiple accounts
- **No unsolicited automated replies** - only reply when explicitly requested by the user
- **No trending manipulation** - don't mass-post about trending topics
- **No fake engagement** - don't automate likes, reposts, or follows
- **Respect rate limits** - the API has rate limits, don't spam requests
- **Drafts are private** - content stays private until published or explicitly shared

When in doubt, create drafts for user review rather than publishing directly.

**Publishing confirmation**: Unless the user explicitly asks to "publish now" or "post immediately", always confirm before publishing. Creating a draft is safe; publishing is irreversible and goes public instantly.

## Tips

- **Smart platform default**: If `--platform` is omitted, the first connected platform is auto-selected
- **All platforms**: Use `--all` to post to all connected platforms at once
- **Character limits**: X (280), LinkedIn (3000), Threads (500), Bluesky (300), Mastodon (500)
- **Thread creation**: Use `---` on its own line to split into multiple posts (thread)
- **Scheduling**: Use `next-free-slot` to let Typefully pick the optimal time
- **Cross-posting**: List multiple platforms separated by commas: `--platform x,linkedin`
- **Draft titles**: Use `--title` for internal organization (not posted to social media)
- **Draft scratchpad**: Use `--scratchpad` to attach notes to the draft in Typefully (NOT local files!) - perfect for thread ideas, research, context
- **Read from file**: Use `--file ./post.txt` instead of `--text` to read content from a file
- **Sorting drafts**: Use `--sort` with values like `created_at`, `-created_at`, `scheduled_date`, etc.
