# How to Schedule Social Media Posts with AI Using PostFast and OpenClaw

Managing social media across multiple platforms is a time sink. You open the scheduler, pick your accounts, write your caption, upload your media, set the time, and repeat for every platform. Now multiply that by every post, every week. It adds up fast.

What if you could just tell your AI assistant what to post and when, and it handled the rest?

That's exactly what the PostFast skill for OpenClaw enables. Schedule posts to TikTok, Instagram, Facebook, X, YouTube, LinkedIn, Threads, Bluesky, and Pinterest through natural conversation. No interface switching, no clicking through menus. Just say what you want and your AI does it.

## What You'll Learn

- What OpenClaw is and why it matters for marketers
- How the PostFast skill works
- How to install and configure it in minutes
- Real-world examples of AI-powered social media scheduling
- Why this approach beats the traditional workflow

## What is OpenClaw?

[OpenClaw](https://openclaw.ai) is an open-source AI personal assistant with over 157,000 GitHub stars. It runs on your own device and connects to the messaging platforms you already use — WhatsApp, Telegram, Slack, Discord, and more.

What makes OpenClaw powerful for marketers is its skill system. Skills are plugins that teach the assistant how to use specific tools and APIs. The [ClawHub marketplace](https://clawhub.ai) hosts hundreds of community-built skills, and PostFast is now one of them.

Think of it as having a personal social media manager that lives in your terminal (or your chat app) and never sleeps.

## The PostFast Skill for OpenClaw

The PostFast skill connects your OpenClaw assistant directly to the [PostFast API](https://postfa.st/docs). Once installed, you can manage your entire social media workflow through conversational commands.

### What It Can Do

With the PostFast skill installed, your AI assistant can:

- **Schedule posts** to any of the 9 supported platforms
- **Upload media** — images, videos, carousels, and documents
- **Cross-post** the same content to multiple platforms simultaneously
- **List your connected accounts** and see what's scheduled
- **Delete scheduled posts** you've changed your mind about
- **Handle platform-specific settings** like TikTok privacy controls, Instagram Reels vs Stories, YouTube Shorts, Pinterest board selection, and more

The skill knows the full PostFast API, including the multi-step media upload workflow. You don't need to think about signed URLs or S3 uploads. Just tell it what to post and where.

### Why PostFast vs Other Social Media Skills?

There are a few social media scheduling skills on ClawHub already. Here's why PostFast stands out:

- **No self-hosting required.** Competitors like Mixpost and Postiz require you to run your own server infrastructure. PostFast is SaaS — sign up, get an API key, and you're done in 60 seconds.

- **Deep platform controls.** PostFast exposes platform-specific settings that other tools don't: TikTok duet/stitch toggles, Instagram collaborators, YouTube playlist integration, Pinterest board targeting, and LinkedIn document posts.

- **9 platforms, one API.** TikTok, Instagram, Facebook, X (Twitter), YouTube, LinkedIn, Threads, Bluesky, and Pinterest. All from a single, unified API.

- **Battle-tested API.** PostFast's API supports the full content lifecycle: upload media, schedule posts, manage accounts, and clean up. It's the same API that powers the [PostFast web app](https://app.postfa.st).

## How to Install the PostFast Skill

Getting started takes about two minutes.

### Prerequisites

- A working [OpenClaw](https://openclaw.ai) installation
- The [ClawHub CLI](https://docs.openclaw.ai/tools/clawhub) installed (`npm i -g clawhub`)
- A [PostFast account](https://app.postfa.st/register) (free 7-day trial available)

### Step 1: Install the Skill

Open your terminal and run:

```bash
clawhub install postfast
```

That's it. The skill is downloaded and ready.

### Step 2: Get Your API Key

1. Log in to [PostFast](https://app.postfa.st)
2. Go to **Workspace Settings**
3. Click **Generate API Key**
4. Copy the key

### Step 3: Configure OpenClaw

Add your API key to your OpenClaw configuration. You can either set it as an environment variable:

```bash
export POSTFAST_API_KEY="your-api-key-here"
```

Or add it to your `openclaw.json` config:

```json
{
  "skills": {
    "entries": {
      "postfast": {
        "enabled": true,
        "apiKey": "your-api-key-here"
      }
    }
  }
}
```

### Step 4: Verify the Connection

Start a new OpenClaw session and ask:

> "Show me my connected social media accounts"

If everything is configured correctly, your assistant will list all the social accounts connected to your PostFast workspace.

## Real-World Usage Examples

Here's where things get exciting. Instead of navigating interfaces, you just talk.

### Quick Post Scheduling

> "Schedule a post to my LinkedIn for tomorrow at 9am: We just hit 1,000 customers! Here's what we learned along the way. Thread below 👇 #startup #milestone"

Your assistant calls the PostFast API, creates the post, and confirms the schedule. Done.

### Cross-Platform Publishing

> "Post this to Instagram as a Reel, TikTok, and YouTube Shorts at 3pm today: Quick tip — batch your content creation into one session per week. You'll save 5+ hours. Trust me."

The skill handles the platform-specific settings automatically: `instagramPublishType: "REEL"`, `youtubeIsShort: true`, and the right TikTok defaults. One message, three platforms.

### Media Uploads

> "Upload this image and schedule it as a Pinterest pin to my 'Marketing Tips' board with a link to postfa.st/blog"

The assistant handles the full 3-step flow behind the scenes: gets a signed upload URL, uploads your image, and creates the pin with the right board ID and destination link.

### Content Calendar Check

> "What do I have scheduled for this week?"

Get a quick overview of your upcoming posts without opening any dashboard.

### TikTok with Specific Controls

> "Schedule a TikTok video for Friday at 6pm. Set it to public, disable duets, enable stitches, and mark it as branded content."

The skill knows every TikTok API parameter and maps your natural language to the right controls.

### LinkedIn Document Post

> "Upload this PDF and post it to LinkedIn with the title 'Q1 Marketing Playbook' and the caption: Our complete Q1 strategy in 12 slides. Save this for later."

Document posts on LinkedIn display as swipeable carousels and consistently outperform regular image posts for educational content.

## How It Works Under the Hood

For the technically curious, here's what happens when you tell your AI to schedule a post:

1. **Account lookup** — The skill calls `GET /social-media/my-social-accounts` to find the right account ID for the platform you mentioned.

2. **Media upload** (if needed) — Requests a signed upload URL via `POST /file/get-signed-upload-urls`, uploads your file directly to storage, and captures the media key.

3. **Post creation** — Calls `POST /social-posts` with your content, media keys, schedule time, target account, and any platform-specific controls.

4. **Confirmation** — Reports back the scheduled post ID and details.

The entire PostFast API is documented in the skill's reference files, so your AI assistant always knows the right endpoints, parameters, and constraints for every platform.

## Security and Privacy

Your PostFast API key stays on your machine. OpenClaw runs locally, and the skill communicates directly with the PostFast API over HTTPS. No data passes through ClawHub or any intermediary.

A few best practices:

- **Use workspace-scoped API keys.** Each PostFast API key is tied to a single workspace, limiting access to only the accounts in that workspace.
- **Review the skill before enabling it.** The PostFast skill is open source and published by the PostFast team. You can inspect every line of the SKILL.md and reference files.
- **Rotate keys periodically.** You can regenerate your API key in PostFast Workspace Settings at any time.

## Getting Started

Ready to schedule social media posts with AI?

1. **[Sign up for PostFast](https://app.postfa.st/register?source=blog-openclaw)** — Free 7-day trial, no credit card required
2. **[Install OpenClaw](https://openclaw.ai)** — Open-source AI assistant
3. **Install the skill:** `clawhub install postfast`
4. **Start posting** — Just tell your AI what to schedule

Stop switching between tabs. Start telling your AI what to post.

---

*PostFast is a social media scheduling tool that helps creators, brands, and agencies publish content across 9 platforms from one dashboard. [Learn more about our features](https://postfa.st/features) or [explore the API](https://postfa.st/docs).*
