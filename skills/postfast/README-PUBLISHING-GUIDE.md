# PostFast OpenClaw Skill — Publishing Guide

## What's in this folder

```
postfast/
├── SKILL.md                           # The actual skill (this is what gets published)
├── references/
│   ├── api-reference.md               # Full API endpoint docs
│   └── platform-controls.md           # All platform-specific settings
├── blog-post-openclaw-skill.md        # Blog post draft for postfa.st
└── README-PUBLISHING-GUIDE.md         # This file (don't publish this)
```

---

## Step 1: Test the Skill (YOU ARE HERE)

The skill is now installed at `skills/postfast/` and configured with your API key.
Start a new session (`/new`) and test these prompts:

1. "Show me my connected social media accounts"
2. "What posts do I have scheduled?"
3. "Schedule a test post to Facebook for next Monday at 10am: Testing PostFast + OpenClaw integration!"
4. "Delete that scheduled post"

If everything works → move to Step 2.

---

## Step 2: Publish to ClawHub

No GitHub repo needed — ClawHub publishes directly from a local folder.

**On your machine:**

1. **Install ClawHub CLI:**
   ```bash
   npm i -g clawhub
   ```

2. **Login** (requires GitHub account, at least 1 week old):
   ```bash
   clawhub login
   ```
   This opens a browser for GitHub OAuth.

3. **Unzip and publish:**
   ```bash
   unzip postfast-skill-v1.0.0.zip
   cd postfast-clean

   clawhub publish . \
     --slug postfast \
     --name "PostFast" \
     --version 1.0.0 \
     --changelog "Initial release: schedule posts to 9 platforms via PostFast API" \
     --tags latest
   ```

4. **Verify it's live:**
   ```bash
   clawhub search "postfast"
   ```

---

## Step 3: Publish the Blog Post

1. Take the `blog-post-openclaw-skill.md` file
2. Adapt it to your blog CMS format (whatever postfa.st uses)
3. **Create a featured image** — suggestions:
   - PostFast logo + OpenClaw 🦞 logo side by side
   - Use Canva: clean background, both logos, "Schedule Posts with AI" subtitle
   - Dimensions: 1200×630 (standard OG image)
4. **SEO metadata:**
   - **Title:** "How to Schedule Social Media Posts with AI Using PostFast and OpenClaw"
   - **Description:** "Use the PostFast skill for OpenClaw to schedule posts to TikTok, Instagram, Facebook, X, YouTube, LinkedIn, Threads, Bluesky, and Pinterest with natural language commands."
   - **Slug:** `/blog/openclaw-skill` or `/blog/schedule-posts-with-ai-openclaw`
   - **Keywords:** schedule social media posts AI, OpenClaw social media, PostFast OpenClaw skill, AI social media scheduling
5. Publish it

---

## Step 4: Promote

1. **OpenClaw Discord** (https://discord.com/invite/clawd):
   - Post in #showcase or #skills channel
   - Brief message: "Just published a PostFast skill for scheduling social media to 9 platforms — `clawhub install postfast`. No self-hosting needed, SaaS API."

2. **X / Twitter:**
   - "Just shipped a PostFast skill for @OpenClaw 🦞 — schedule posts to TikTok, Instagram, YouTube, LinkedIn & more with AI. No self-hosting needed. `clawhub install postfast`"

3. **Reddit** (r/selfhosted, r/sideproject, r/SaaS):
   - Share the blog post link

4. **Update PostFast homepage:**
   - Consider adding "OpenClaw Integration" to the integrations section (alongside Canva)

---

## How Users Install & Use the Skill

This is what you tell users in docs/blog/README:

### Installation

```bash
# Install the ClawHub CLI (if not already)
npm i -g clawhub

# Install the PostFast skill
clawhub install postfast
```

### Configuration

Get your API key from PostFast → Workspace Settings → Generate API Key.

**Option A** — Environment variable:
```bash
export POSTFAST_API_KEY="your-api-key"
```

**Option B** — OpenClaw config (`~/.openclaw/openclaw.json`):
```json
{
  "skills": {
    "entries": {
      "postfast": {
        "enabled": true,
        "apiKey": "your-api-key"
      }
    }
  }
}
```

Start a new OpenClaw session to pick up the skill.

### Usage Examples

Just talk to your AI assistant:

- "Show me my social media accounts"
- "Schedule a TikTok video for tomorrow at 3pm with duets disabled"
- "Post this image to Instagram as a Reel and Facebook at the same time"
- "What's scheduled for this week?"
- "Pin this to my Recipes board on Pinterest with a link to my blog"
- "Delete my last scheduled post"

---

## Future Updates

To publish a new version:
```bash
clawhub publish ./postfast-openclaw-skill \
  --slug postfast \
  --version 1.1.0 \
  --changelog "Added XYZ" \
  --tags latest
```

Users update with:
```bash
clawhub update postfast
```
