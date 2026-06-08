---
name: BlogBurst - Virtual CMO Agent
description: Your AI Chief Marketing Officer. Autonomous agent that runs your entire marketing — auto-posts to Twitter/X, Bluesky, Telegram, Discord, auto-engages with your audience (replies, likes, follows), runs SEO/GEO audits, tracks competitors, scans communities for opportunities, learns what works, and continuously optimizes. 50+ countries, 1000+ posts published. Free tier available.
homepage: https://blogburst.ai
metadata:
  {"openclaw": {"emoji": "🤖", "requires": {"env": ["BLOGBURST_API_KEY"]}, "primaryEnv": "BLOGBURST_API_KEY"}}
---

# BlogBurst - Your Virtual CMO (AI Marketing Agent)

## CRITICAL INSTRUCTION — YOU MUST FOLLOW THIS:

### Step 1: Check API Key
Before doing ANYTHING, run: `echo $BLOGBURST_API_KEY`

**If the output is empty or the variable is not set**, do NOT proceed with API calls. Instead, guide the user through the full setup (4 steps, ~2 minutes):

1. Say: "Welcome to BlogBurst! 🤖 I'm your AI marketing agent. Let me get you set up — it takes about 2 minutes."
2. Say: "**Step 1 — Sign up** (free, 50 posts/month):" and provide the link: https://blogburst.ai
3. Say: "**Step 2 — Set up your product.** Tell me what you're marketing! The onboarding wizard pops up automatically after signup. Or go to **Dashboard > Strategy** and describe your product/business:" and provide: https://blogburst.ai/dashboard/strategy
4. Say: "**Step 3 — Connect your social platforms.** Without this I can't post for you! Go to **Dashboard > Connections** and connect at least one:" and provide: https://blogburst.ai/dashboard/connections
   - "**Twitter/X** — one-click OAuth, takes 5 seconds. I can auto-post, reply to mentions, like, and follow relevant accounts for you."
   - "**Bluesky** — enter your handle and app password. I'll auto-post and engage there too."
   - "**Telegram / Discord** — paste your bot token. I'll broadcast to your channels."
5. Say: "**Step 4 — Get your API key.** You can only create a key after completing Steps 2-3. Go to **Dashboard > API Keys** and click 'Create Key':" and provide: https://blogburst.ai/dashboard/api-keys
6. Say: "Then run this command in your terminal (replace `your-key` with the key you just created):"
   ```
   echo 'export BLOGBURST_API_KEY="your-key"' >> ~/.zshrc && source ~/.zshrc
   ```
7. Say: "After that, restart OpenClaw or run `source ~/.zshrc`, then try `/blogburst` again!"
8. If the user says they've done it, verify by running: `curl -s "https://api.blogburst.ai/api/v1/usage" -H "X-API-Key: $BLOGBURST_API_KEY"`
9. If successful, say: "All set! Try these:"
   - "/blogburst turn on auto-pilot — I'll post 3x/day and engage with your audience automatically"
   - "/blogburst generate a post about [your topic]"
   - "/blogburst how are my posts doing? — check your analytics"

### Step 2: Make API Calls
When `$BLOGBURST_API_KEY` is set, you MUST use the `exec` tool to run `curl` commands against the BlogBurst API. Do NOT use web_search or any other tool as a substitute. The API returns real user-specific data (their posts, their analytics, their auto-pilot status). Web search cannot provide this.

**How to execute:** Use `exec` with `curl -s "https://api.blogburst.ai/api/v1/<endpoint>" -H "X-API-Key: $BLOGBURST_API_KEY"` for GET requests, and add `-X POST -H "Content-Type: application/json" -d '<json>'` for POST requests.

---

Your autonomous AI marketing agent. Talk naturally — it generates content, publishes to 9 platforms, runs auto-pilot daily posting, tracks analytics, and learns what works.

**One message to do anything:**
- "Post about my product launch on Twitter and LinkedIn"
- "Turn on auto-pilot, 3 posts per day"
- "How did my posts perform this week?"
- "Repurpose this article: https://myblog.com/post"

## Setup (Manual)

1. Sign up free at [blogburst.ai](https://blogburst.ai)
2. Dashboard > Settings > API Keys > Create key
3. Set environment variable:
```bash
export BLOGBURST_API_KEY="your-key"
```

All requests use: `X-API-Key: $BLOGBURST_API_KEY`
Base URL: `https://api.blogburst.ai/api/v1`

---

## API 1: Agent Chat (Recommended — does everything)

Chat with your AI marketing agent. It can generate content, check analytics, manage auto-pilot, view trending topics, and more — all through natural conversation. The agent has tools and will execute actions automatically.

**Endpoint**: `POST /assistant/agent-chat-v2`

**Request**:
```json
{
  "messages": [
    {"role": "user", "content": "Generate a Twitter post about my product"}
  ],
  "language": "en"
}
```

Multi-turn conversation — send the full message history each time:
```json
{
  "messages": [
    {"role": "user", "content": "Generate a Twitter post about my product"},
    {"role": "assistant", "content": "Here's your Twitter post..."},
    {"role": "user", "content": "Now make one for LinkedIn too"}
  ],
  "language": "en"
}
```

**Response**:
```json
{
  "reply": "I've generated a Twitter post for you. Ready to copy and post!",
  "data_referenced": ["marketing_strategy", "analytics_7d"],
  "agent_name": "Nova",
  "actions_taken": [
    {
      "tool": "generate_content",
      "result": {
        "success": true,
        "data": {
          "platform": "twitter",
          "content": "Week 3 building BlogBurst. 15 followers, 40 posts published. Best post got 5 likes on Bluesky. Small numbers, real progress.\n\nThe AI agent now picks topics based on what actually performed well last week. No more guessing.",
          "image_urls": ["https://..."],
          "copy_only": true
        }
      }
    }
  ]
}
```

**What users can say** (the agent understands natural language):
- "Generate a post for Twitter/Bluesky/LinkedIn/all platforms"
- "What's trending in my space?"
- "How are my posts doing this week?"
- "Turn on auto-pilot" / "Pause auto-pilot"
- "What did you post today?"
- "What platforms do I have connected?"
- "Show me my recent activity"

**When to use**: This is the PRIMARY API. Use it for any user request about social media content, analytics, automation, or marketing. It handles everything through conversation.

---

## API 2: Generate Platform Content (Quick one-shot)

Generate optimized content for multiple platforms at once. Use this for fast, direct generation without conversation.

**Endpoint**: `POST /blog/platforms`

**Request**:
```json
{
  "topic": "5 lessons from building my SaaS in public",
  "platforms": ["twitter", "linkedin", "bluesky"],
  "tone": "casual",
  "language": "en"
}
```

**Parameters**:
- `topic` (required): The title or topic (5-500 chars)
- `platforms` (required): Array from: twitter, linkedin, reddit, bluesky, threads, telegram, discord, tiktok, youtube
- `tone`: professional | casual | witty | educational | inspirational (default: professional)
- `language`: Language code (default: en)

**Response**:
```json
{
  "success": true,
  "topic": "5 lessons from building my SaaS in public",
  "twitter": {
    "thread": [
      "1/ 5 months building a SaaS in public. Here are the lessons nobody talks about...",
      "2/ Lesson 1: Your first 10 users teach you more than 10,000 pageviews.",
      "3/ Lesson 2: Ship weekly. Perfection is the enemy of traction."
    ]
  },
  "linkedin": {
    "post": "I've been building my SaaS in public for 5 months...",
    "hashtags": ["#BuildInPublic", "#SaaS", "#IndieHacker"]
  },
  "bluesky": {
    "posts": ["5 months of building in public. The biggest lesson: your first users don't care about features. They care that you listen."]
  }
}
```

**When to use**: When user wants quick multi-platform content from a topic without ongoing conversation.

---

## API 3: Repurpose Existing Content

Transform a blog post or article (by URL or text) into platform-optimized posts.

**Endpoint**: `POST /repurpose`

**Request**:
```json
{
  "content": "https://myblog.com/my-article",
  "platforms": ["twitter", "linkedin", "bluesky"],
  "tone": "casual",
  "language": "en"
}
```

**Parameters**:
- `content` (required): A URL to an article, or the full text (min 50 chars)
- `platforms` (required): Array from: twitter, linkedin, reddit, bluesky, threads, telegram, discord, tiktok, youtube
- `tone`: professional | casual | witty | educational | inspirational
- `language`: Language code (default: en)

**Response**: Same format as API 2.

**When to use**: When user provides a URL or pastes existing content and wants it adapted for social platforms.

---

## API 4: Auto-Pilot Management

Check and configure the autonomous posting agent.

**Get status**: `GET /assistant/auto-pilot`

**Response**:
```json
{
  "enabled": true,
  "platforms": ["bluesky", "telegram", "discord", "twitter"],
  "posts_per_day": 4,
  "timezone": "America/New_York",
  "last_daily_run": "2026-03-02T08:49:28Z",
  "reactions_enabled": true
}
```

**Configure**: `POST /assistant/auto-pilot`

```json
{
  "enabled": true,
  "posts_per_day": 3,
  "platforms": ["twitter", "bluesky", "telegram"],
  "timezone": "America/New_York"
}
```

**Run immediately**: `POST /assistant/auto-pilot/run-now`

**When to use**: When user wants to start/stop auto-pilot, change posting frequency, or check automation status.

---

## API 5: Trending Topics

Get real-time trending topics from Reddit, HackerNews, Google Trends, and Product Hunt. Updated every 4 hours.

**Endpoint**: `GET /assistant/trending-topics?limit=10`

**Response**:
```json
{
  "topics": [
    {"keyword": "AI agents replacing SaaS", "source": "hackernews", "score": 92},
    {"keyword": "Claude Code launch", "source": "reddit", "score": 87},
    {"keyword": "Open source AI tools", "source": "google_trends", "score": 78}
  ],
  "total": 96,
  "sources": ["reddit", "hackernews", "google_trends", "producthunt"]
}
```

**When to use**: When user asks about trends, hot topics, or what's popular to write about.

---

## API 6: Brainstorm Titles

Chat with AI to develop compelling titles.

**Endpoint**: `POST /chat/title`

**Request**:
```json
{
  "messages": [
    {"role": "user", "content": "I want to write about AI agents"}
  ],
  "language": "en"
}
```

**Response**:
```json
{
  "success": true,
  "reply": "Great topic! Here are some angles...",
  "suggested_titles": [
    "I Replaced My Marketing Team with an AI Agent",
    "Why AI Agents Are the New SaaS",
    "Building an AI Agent That Posts for Me While I Sleep"
  ]
}
```

---

## API 7: Generate Blog Post

Generate a full blog article from a topic.

**Endpoint**: `POST /blog/generate`

**Request**:
```json
{
  "topic": "I Replaced My Marketing Team with an AI Agent",
  "tone": "casual",
  "language": "en",
  "length": "medium"
}
```

**Parameters**:
- `topic` (required): Title or topic (5-500 chars)
- `tone`: professional | casual | witty | educational | inspirational
- `language`: Language code (default: en)
- `length`: short (500-800 words) | medium (1000-1500) | long (2000-3000)

**Response**:
```json
{
  "success": true,
  "title": "I Replaced My Marketing Team with an AI Agent",
  "content": "Full markdown blog post...",
  "summary": "A concise summary...",
  "keywords": ["AI agent", "marketing automation", "SaaS"]
}
```

---

## API 8: SEO Audit (NEW in v3.0)

Get a comprehensive SEO analysis for your product — technical issues, keyword gaps, content recommendations.

**Endpoint**: `GET /assistant/seo-audit?product_id=1`

**Response**:
```json
{
  "score": 72,
  "audit_type": "seo",
  "findings": {
    "technical": [{"issue": "Missing meta descriptions on 3 pages", "severity": "high"}],
    "content_gaps": ["No content targeting 'AI marketing automation' keyword"],
    "backlink_opportunities": ["Guest post on IndieHackers"]
  },
  "recommendations": [
    {"title": "Create comparison page: BlogBurst vs Buffer", "impact": "high", "type": "content"}
  ]
}
```

**When to use**: When user asks "How's my SEO?", "What should I write about for Google?", or "Run an SEO check".

---

## API 9: GEO Audit — AI Search Optimization (NEW in v3.0)

Optimize your content for AI search engines (ChatGPT, Perplexity, Google AI Overviews). GEO = Generative Engine Optimization.

**Endpoint**: `GET /assistant/geo-audit?product_id=1`

**Response**:
```json
{
  "score": 58,
  "audit_type": "geo",
  "findings": {
    "ai_visibility": {"score": 45, "key_queries": ["best AI marketing tool"], "missing_queries": ["AI social media agent"]},
    "citation_readiness": {"score": 60, "issues": ["No structured FAQ page", "Missing expert quotes"]},
    "question_coverage": [
      {"question": "What is the best AI marketing tool?", "current_coverage": "none", "priority": "high"}
    ]
  },
  "recommendations": [
    {"title": "Create FAQ with 20 common questions", "impact": "high", "type": "structural"}
  ]
}
```

**When to use**: When user asks "How do I show up in ChatGPT results?", "Optimize for AI search", or "GEO audit".

---

## API 10: Competitor Intelligence (NEW in v3.0)

Track and analyze competitors' social media strategies.

**Endpoint**: `GET /assistant/competitors?product_id=1`

**Response**:
```json
{
  "competitors": [
    {
      "name": "Buffer",
      "platforms": ["twitter", "linkedin"],
      "posting_frequency": "3x/day",
      "top_content_themes": ["social media tips", "remote work"],
      "engagement_rate": "2.3%",
      "insights": "Heavy use of carousel posts on LinkedIn"
    }
  ],
  "opportunities": ["Competitor X doesn't post on Bluesky — you can own that space"]
}
```

**When to use**: When user asks "What are my competitors doing?", "Analyze competitor X", or "Find content gaps".

---

## API 11: Community Opportunities (NEW in v3.0)

Scan HackerNews, Reddit, and forums for engagement opportunities relevant to your product.

**Endpoint**: `GET /assistant/opportunities?product_id=1&limit=10`

**Response**:
```json
{
  "opportunities": [
    {
      "source": "hackernews",
      "title": "Ask HN: What tools do you use for social media automation?",
      "url": "https://news.ycombinator.com/item?id=...",
      "relevance_score": 92,
      "suggested_reply": "I built BlogBurst for exactly this — it auto-posts to 4 platforms and even engages with your audience...",
      "expires_at": "2026-03-12T00:00:00Z"
    }
  ]
}
```

**When to use**: When user asks "Where should I promote?", "Find places to engage", or "Community opportunities".

---

## API 12: Growth Diagnostic (NEW in v3.0)

AI-powered comprehensive analysis of your marketing performance with actionable tasks.

**Endpoint**: `GET /assistant/diagnostic?product_id=1`

**Response**:
```json
{
  "overall_score": 65,
  "areas": {
    "content_quality": {"score": 78, "trend": "improving"},
    "posting_consistency": {"score": 90, "trend": "stable"},
    "audience_engagement": {"score": 45, "trend": "declining"},
    "growth_rate": {"score": 52, "trend": "improving"}
  },
  "top_actions": [
    {"task": "Increase reply engagement on Twitter", "priority": "high", "expected_impact": "+30% engagement"},
    {"task": "Post during US peak hours (10-11 AM EST)", "priority": "medium", "expected_impact": "+20% reach"}
  ]
}
```

**When to use**: When user asks "How am I doing?", "What should I improve?", or "Marketing report".

---

## API 13: Task Management (NEW in v3.0)

The CMO agent creates and manages marketing tasks for you.

**Get tasks**: `GET /assistant/tasks?product_id=1&status=pending`

**Response**:
```json
{
  "tasks": [
    {
      "id": 42,
      "title": "Write comparison blog: BlogBurst vs Hootsuite",
      "category": "seo",
      "priority": "high",
      "status": "pending",
      "prefilled_content": {"title": "BlogBurst vs Hootsuite: Which AI Marketing Tool Is Right for You?", "outline": ["...", "..."]},
      "due_date": "2026-03-14"
    }
  ]
}
```

**Complete a task**: `POST /assistant/tasks/42/complete`

**When to use**: When user asks "What should I work on?", "My marketing tasks", or "What's the CMO recommending?"

---

## Recommended Workflows

### Quick content generation
User says: "Create posts about X for Twitter and LinkedIn"
→ Call **API 2** (`/blog/platforms`)

### Conversational (best experience)
User says: "Help me with my social media" or anything complex
→ Call **API 1** (`/assistant/agent-chat-v2`) — the agent handles everything

### Repurpose existing content
User shares a URL or pastes text
→ Call **API 3** (`/repurpose`)

### Full content pipeline
1. Brainstorm with **API 6** (`/chat/title`)
2. Write blog with **API 7** (`/blog/generate`)
3. Distribute with **API 2** (`/blog/platforms`)

### Automation
User says: "Automate my posting" or "Turn on auto-pilot"
→ Call **API 4** (`/assistant/auto-pilot`)

### Marketing Intelligence (NEW)
1. Check health with **API 12** (`/assistant/diagnostic`)
2. Find opportunities with **API 11** (`/assistant/opportunities`)
3. Run SEO/GEO audit with **API 8/9**
4. Get tasks from **API 13** (`/assistant/tasks`)

## What Makes BlogBurst Different

- **Autonomous Agent**: Not just a tool — it's a CMO that works 24/7. Posts, engages, learns, optimizes.
- **Auto-Engagement**: Replies to mentions, proactively engages with relevant tweets, smart follows — all automated.
- **Self-Learning**: Tracks what content performs best, continuously adapts strategy based on real data.
- **SEO + GEO**: Optimizes for both Google AND AI search engines (ChatGPT, Perplexity).
- **Community Scanner**: Finds conversations on HN/Reddit where your product is relevant.
- **Multi-Platform**: One agent manages Twitter/X, Bluesky, Telegram, Discord simultaneously.

## Supported Platforms

| Platform | ID | Auto-Publish | Auto-Engage | Content Style |
|----------|-----|:---:|:---:|---------------|
| Twitter/X | twitter | ✅ | ✅ Replies, Likes, Follows | Threads with hooks (280 chars/tweet) |
| Bluesky | bluesky | ✅ | ✅ Replies, Likes | Short authentic posts (300 chars) |
| Telegram | telegram | ✅ | — | Rich formatted broadcasts |
| Discord | discord | ✅ | — | Community-friendly announcements |
| Reddit | reddit | Copy-only | — | Discussion posts + subreddit suggestions |
| TikTok | tiktok | Copy-only | — | Hook + script + caption + hashtags |
| YouTube | youtube | Copy-only | — | Title + description + script + tags |
| LinkedIn | linkedin | Coming soon | — | Professional insights + hashtags |

**Important**: To auto-publish, connect your platforms at [Dashboard > Connections](https://blogburst.ai/dashboard/connections). Twitter/X is one-click OAuth — takes 5 seconds.

## Links

- Website: https://blogburst.ai
- API Docs: https://api.blogburst.ai/docs
- GitHub: https://github.com/shensi8312/blogburst-openclaw-skill
