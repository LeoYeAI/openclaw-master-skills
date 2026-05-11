---
name: coffee-chat
description: |
  Generate a personalized coffee chat playbook for networking conversations. Use when:
  - User wants to prepare for a coffee chat with someone they met on LinkedIn
  - Need to gather intelligence on a professional contact before meeting
  - Creating conversation guides for networking meetings

  Triggers: "coffee chat", "networking prep", "coffee chat prep", "chat playbook", "meeting prep"

  This skill:
  1. Collects target person's name and LinkedIn URL
  2. Researches company and industry
  3. Finds founder/employee backgrounds
  4. Generates a comprehensive coffee chat playbook with detailed research
---

# Coffee Chat Playbook Generator

This skill helps you prepare for professional coffee chats by gathering intelligence on the person and generating personalized conversation guides.

---

## Prerequisites

Before using this skill, set up the following. Only **Apify CLI** is required for X scraping — everything else is optional.

### 1. Apify CLI (required for X/Twitter scraping)

Apify CLI is used to run the tweet scraper actor.

**Install:**
```bash
npm install -g apify-cli
```

**Authenticate:**
```bash
apify login
# Paste your Apify API token when prompted
# Get your token at: https://console.apify.com/account/integrations
```

**Verify:**
```bash
apify info
# Should show your username and token
```

> Free tier includes $5/month of compute credits. Scraping 10 tweets costs ~$0.004, well within free limits.

---

### 2. Notion Integration (optional — for saving playbooks to Notion)

**Create an integration:**
1. Go to https://www.notion.so/my-integrations
2. Click **"New integration"**
3. Give it a name (e.g. "Coffee Chat Skill")
4. Copy the **Internal Integration Token**

**Set the API key:**
```bash
export NOTION_API_KEY="secret_xxxxxxxxxxxxxxxxxxxx"
# Add to your shell profile to persist:
echo 'export NOTION_API_KEY="secret_xxxxxxxxxxxxxxxxxxxx"' >> ~/.zshrc
```

**Share your Notion page with the integration:**
1. Open the Notion page where you want playbooks saved
2. Click **"..."** → **"Add connections"** → select your integration
3. Copy the page ID from the URL:
   - URL: `https://notion.so/My-Page-abc123def456...`
   - Page ID: `abc123def456...` (the part after the last `-`)

**Update `NOTION_PAGE_ID`** in the Notion Push section of this skill.

---

### 3. Web Search & Fetch (required for company and background research)

This skill relies on web search and web fetch to research the target's company, industry, and background in Steps 2 & 3. Your AI agent needs access to these tools.

**If using OpenClaw or Claude Code:**
- Web search and WebFetch are built-in — no setup needed

**If using another agent framework**, make sure it has access to:
- A **search API** (e.g. Brave Search, Serper, Tavily, You.com) for querying company news, funding rounds, founder backgrounds
- A **web fetch / scrape tool** for reading pages (company websites, LinkedIn profiles, news articles)

> Without these tools the agent will fall back to training knowledge only, which may be outdated. Research quality will drop significantly.

---

### 4. Summary of everything you need

| Tool / Variable | Required | Description |
|-----------------|----------|-------------|
| Web search API | **Yes** (for research) | Built-in on OpenClaw/Claude Code; otherwise configure your agent's search plugin |
| Web fetch | **Yes** (for research) | Built-in on OpenClaw/Claude Code; otherwise configure your agent's fetch tool |
| `APIFY_API_TOKEN` | For X scraping | Set automatically by `apify login` |
| `NOTION_API_KEY` | Optional | Your Notion integration token |

---

## Setup (First Time)

Before using this skill, create your profile file at `memory/my-profile.md`:

```markdown
# My Profile

- **Name**: [Your Name]
- **Role**: [Your current role and company]
- **Background**: [Brief career background, e.g. Finance → VC → AI]
- **Location**: [City, Country]
- **LinkedIn**: [Your LinkedIn URL]
- **Interests**: [Topics you care about / want to discuss]
```

Also configure integrations (optional):
- **Notion**: Set `NOTION_API_KEY` env var and update `NOTION_PAGE_ID` in the Notion Push section below
- **Apify**: Set `APIFY_API_TOKEN` env var for LinkedIn scraping (free tier available)

---

## Workflow

### Step 1: Collect Information

Ask the user for:
1. **Target person's name** (required)
2. **Target's LinkedIn profile URL** (optional but recommended)
3. **Target's company name** (required for research)
4. **Target's X (Twitter) username** (optional, e.g. `@elonmusk` or just `elonmusk`) — used for scraping recent posts
5. **Context of the meeting** (optional - how you met, goal)

Load your profile from `memory/my-profile.md` for comparison.

### Step 2: Research Target's Company

For each target, do comprehensive company research:

1. **Web search** for company info:
   - Funding news
   - Product/feature launches
   - Team / founders

2. **X (Twitter) search** for company account:
   - Recent posts
   - Product demos
   - Engagement with community

3. **News search** for recent coverage:
   - Funding announcements
   - Product launches
   - Competitor/industry analysis

### Step 3: Research Target's Background

1. **Find LinkedIn profile** via web search
2. **Scrape LinkedIn posts** (if available via Apify)
3. **Scrape X (Twitter) posts** — if user provided an X username, run:

```bash
apify call apidojo/tweet-scraper --input '{
  "searchTerms": ["from:USERNAME"],
  "maxTweets": 10,
  "sort": "Latest"
}' --output-dataset --silent
```

Replace `USERNAME` with the target's X handle (without `@`).

- Parse the dataset output and extract: tweet text, date, likes, retweets, replies
- If `APIFY_API_TOKEN` is not set or scraping fails, fall back to web search for recent X posts
- Skip this step silently if no X username was provided

4. **Gather background info**:
   - Previous work experience
   - Education
   - Notable projects/achievements
   - Recent posts/topics (from both LinkedIn and X)

### Step 4: Generate Comprehensive Playbook

Follow the **Full Playbook Template** below with ALL sections:
- Target Profile Summary
- Company & Industry Research (detailed)
- Founder Deep Dive (for startup targets)
- Recent Content & Posts
- Profile Comparison
- 8 Questions
- 4 Talking Points
- Communication Tips
- Pre-Chat Checklist

### Step 5: Save & Push to Notion (optional)

1. **Save locally**: `memory/coffee-chat-{target-slug}-{YYYY-MM-DD}.md`
2. **Push to Notion**: Append to your configured Notion page (if `NOTION_API_KEY` is set)

---

## Full Playbook Template

```markdown
# ☕ Coffee Chat Playbook: [Target Company/Name]

**Date:** [YYYY-MM-DD]
**Status:** Researched

---

## 📋 Target Profile Summary

### Basic Info
- **Target**: [Name] (Founder/CEO/PM at [Company])
- **LinkedIn**: [URL]
- **Location**: [City, Country]
- **Connection**: [How you met]

### Background
- [Previous career/experience]
- [Notable projects or achievements]
- [Education]

### Recent Posts / Topics
- [Topic 1 from LinkedIn/X]
- [Topic 2]
- [Topic 3]

---

## 🏢 Company & Industry Research

### Company Overview
- **Company Name**: [Name]
- **Founded**: [Year]
- **Location**: [HQ location]
- **Funding**: [Amount] ([Investors]) - [Date]
- **Team**: [Size/distribution if known]
- **X/Website**: [Links]

### Product
- [Product description]
- [Key features]
- [Target users]

### Industry Landscape
- **Market**: [Brief description of market]
- **Competitors**: [List key competitors]
- **Trends**: [Industry trends]
- **Challenges**: [Key challenges]
- **Opportunities**: [Opportunities]

### Investors (if applicable)
- **Investor 1**: [Background]
- **Investor 2**: [Background]

---

## 👥 Founder Deep Dive (for startups)

### [Founder 1 Name] ([Title])
- **Background**: [e.g., Documentary filmmaker, Ex-Google, etc.]
- **Work history**: [Notable companies/clients]
- **Notable achievements**: [e.g., Founded X, Award Y]
- **Philosophy/Interests**: [From posts]

### [Founder 2 Name] ([Title])
- [Same structure]

---

## 📱 Recent Content & Posts

### LinkedIn Posts
- [Post 1: topic and key message]
- [Post 2]
- [Post 3]

### X (Twitter) Posts — Last 10
> Scraped via apidojo/tweet-scraper. If X username not provided, use web search results.

| # | Date | Tweet | Likes | RT | Replies |
|---|------|-------|-------|----|---------|
| 1 | [YYYY-MM-DD] | [Full tweet text] | [n] | [n] | [n] |
| 2 | [YYYY-MM-DD] | [Full tweet text] | [n] | [n] | [n] |
| 3 | [YYYY-MM-DD] | [Full tweet text] | [n] | [n] | [n] |
| ... | | | | | |

**Key themes from X posts:**
- [Theme 1: what they talk about most]
- [Theme 2: opinions/stances]
- [Theme 3: recent interests or announcements]

**Engagement pattern**: [High/Medium/Low — what type of content gets most engagement]

---

## 🔍 Profile Comparison (You vs Target)

### Your Profile
- **Role**: [Load from memory/my-profile.md]
- **Background**: [Load from memory/my-profile.md]
- **Location**: [Load from memory/my-profile.md]

### Common Ground
- [Common industry or domain]
- [Similar career transition experience]
- [Shared interests]

### Conversation Starters (Based on Research)
1. "[Based on their product launch] I saw [product] launched - what was the inspiration?"
2. "[Based on their background] As someone who transitioned from [old career] to [new career], what surprised you most?"
3. "[Based on their philosophy] Your focus on [X] resonates with me because..."
4. "[Based on investors] How did you approach raising from [Investor]?"
5. "[Based on team] With your distributed team across [locations], how do you manage collaboration?"

---

## 💬 Questions to Ask (8 total)

### 👤 Personal (3)
1. [Question based on their background - e.g., "What prompted your transition from X to Y?"]
2. [Question based on their location/move - e.g., "What's it like building a US company from [location]?"]
3. [Question based on their interests - e.g., "I saw you worked on [project] - what was that experience like?"]

### 💼 Work-Related (3)
4. [Question about their product - e.g., "How is [Company] different from competitors?"]
5. [Question about challenges - e.g., "What's been the biggest challenge building [Company]?"]
6. [Question about team/culture - e.g., "How do you think about team building as a founder?"]

### 🌐 Industry (2)
7. [Question about industry trends - e.g., "Where do you see the industry heading in 2-3 years?"]
8. [Question about advice - e.g., "What advice would you give to someone in my role?"]

---

## 🗣️ Your Talking Points (4)

1. **Your background**: [Load from memory/my-profile.md]
2. **What you admire**: [Something specific from their profile/posts]
3. **Your work**: [Current role and what you're building]
4. **Curiosity**: [Something specific you want to learn from them]

---

## 🧭 Communication Principles & In-Chat Guide

### ☕ The COFFEE Framework (30-min structure)

Use this as your session blueprint. Every great coffee chat has a shape.

| Time | Phase | What to do |
|------|-------|------------|
| 0–5 min | **C — Connect** | Start human. Share who you are briefly. Ask about them first. |
| 5–10 min | **O — Offer Proof** + **F — Frame** | Optionally show a 60-sec artifact (1-pager, analysis, teardown) that proves you've done homework. Then frame the agenda: *"I have a few questions — happy to go wherever is useful for you too."* |
| 10–25 min | **F — Focused Questions** | Ask 2–3 non-Googleable questions. Listen 70%, talk 30%. Follow their thread. |
| 25–30 min | **E — End on Time** | Start wrapping at min 25. Don't let it run over. |
| Closing | **E — Extend Help** | Before you leave: *"Is there anything I can help with from my end?"* |

> **Litmus test for every question:** If the answer is fully on Google or their LinkedIn, don't ask it. Ask things only *they* can answer.

---

### The Golden Rule: 70/30

> **They talk 70%, you talk 30%.** Your job is to draw them out, not to impress them.

- Ask open-ended questions, then listen fully before responding
- Don't fill silence — let them think
- Put your phone away. Be fully present

---

### 🤝 Nonverbal Signals (Don't Overlook These)

| Signal | What to do |
|--------|-----------|
| Eye contact | Maintain natural eye contact — shows you're engaged |
| Nodding | Nod slowly to signal you're following and interested |
| Smile | Warm, genuine smiles — not forced |
| Body posture | Lean slightly forward, open body language, no crossed arms |
| Hands | Keep visible, use to emphasize points naturally |
| Phone | Face-down or away — checking it kills rapport instantly |

---

### 🎭 Identify Their Networker Persona

Read the room in the first 2-3 minutes. Adjust your style accordingly.

#### 🔵 Practicalist
> Fact-driven, problem-solver, sticks to the point, values time efficiency

**Signs**: Gets straight to business, asks direct questions, gives concise answers

**Your technique**:
- Be clear on your intention upfront ("I'm here to learn about X")
- Skip small talk, lead with substance
- Give them space to respond — don't ramble
- Use data and specifics, not vague observations

**Sample opener**: *"I wanted to connect because [specific reason]. I have a few focused questions — hope that works for you."*

---

#### 🟡 Conversationalist
> Personable, relationship-focused, loves stories, open to tangents

**Signs**: Asks personal questions, shares stories, warm and expressive

**Your technique**:
- Power on small talk — ask about their weekend, their city, their journey
- Match their warmth and storytelling style
- Pay close attention to body language — they're reading yours too
- Let conversations flow naturally, don't over-structure

**Sample opener**: *"I loved your post about [X] — it really resonated with me. How did that come about?"*

---

#### 🔴 Dominator
> Dominates the conversation, tends to be the one asking questions, high-status energy

**Signs**: Asks lots of questions, steers topics, rarely pauses for your input

**Your technique**:
- Listen to their questions — they reveal what they care about
- Be more assertive: when there's a natural pause, jump in with your question
- Use bridging phrases: *"That's a great point — it makes me curious about..."*
- Don't wait to be invited — politely redirect to your agenda

**Sample opener**: *"Before I forget — I actually had a specific question I was hoping to get your take on..."*

---

### 💬 Question Bank (70/30 Principle)

Design questions to keep them talking. Follow up on their answers before moving to the next question.

> **How to use this bank:**
> - Pick 2-3 **Core Questions** per section — these are your main agenda
> - Use **Follow-Up Questions** only if time allows and the topic naturally opens up
> - Use **Transition Phrases** to move between topics without abrupt cuts

---

#### 🔓 Warm-Up (first 5 min — build comfort)

**Core:**
- *"How's your week going? Anything exciting on your plate right now?"*
- *"How did you end up in [city/role]? Was it planned or did it just happen?"*

**Follow-up (if they open up):**
- *"What do you enjoy most about being based in [city]?"*
- *"Was there a specific moment that made you decide to make the move?"*

**Transition into background:** *"That's really interesting — I'd love to hear more about your path to where you are now..."*

---

#### 🧬 Background & Journey (understand their path)

**Core:**
- *"What drew you to [industry/role] originally?"*
- *"What's been the most unexpected part of your journey so far?"*
- *"If you could start all over again, would you change your career path in any way?"* *(UB)*

**Follow-up (if time allows):**
- *"If you could go back and tell your younger self one thing, what would it be?"*
- *"Was there a specific decision that really changed the trajectory of things?"*
- *"How long does it typically take for people to rise to more senior levels in this field?"* *(UB)*

**Transition into work:** *"It sounds like you've built a really intentional path. I'm curious how that shapes how you think about [Company] today..."*

---

#### 🏢 Work & Company (go deeper on what they do)

**Core:**
- *"What does a great day at work look like for you right now?"*
- *"What's the hardest problem [Company] is working through?"*
- *"What parts of your job do you find most challenging — and most enjoyable?"* *(UB)*

**Follow-up (if they go deep):**
- *"How has the team's approach evolved as you've scaled?"*
- *"What's something people on the outside misunderstand about what you're building?"*
- *"How would you describe the culture — what kind of person thrives here?"* *(UB)*
- *"Why do people typically leave this company or field?"* *(UB)*

**Transition into industry:** *"Given everything you're seeing up close at [Company], I'd love your take on where the broader space is going..."*

---

#### 🌐 Industry & Trends (show intellectual curiosity)

**Core:**
- *"Where do you think [industry] is heading in the next 2-3 years?"*
- *"What's a trend you're watching that most people aren't paying attention to yet?"*
- *"What are the biggest challenges facing this industry right now?"* *(MIT)*

**Follow-up (if time allows):**
- *"Who do you think is doing the most interesting work in this space right now?"*
- *"Is there a bet you're making that feels contrarian to the mainstream view?"*
- *"Is the field growing — are there good opportunities for newcomers?"* *(UB)*
- *"What developments on the horizon could affect opportunities in this space?"* *(UB)*

**Transition into closing:** *"This has been really eye-opening — before we wrap up, I wanted to make sure I ask..."*

---

#### 🤝 Relationship-Building & Closing (make it mutual)

**Core:**
- *"Is there anything I can help with from my end — introductions, resources, anything?"*
- *"Would it be okay to keep in touch? I'd love to follow your journey."*
- *"Are there any questions I should have asked but didn't?"* *(MIT — always ask this)*

**Follow-up:**
- *"Who else do you think I should be talking to in this space? Would it be okay to use your name?"* *(UB)*
- *"What resources — books, podcasts, communities — would you recommend I look into?"* *(MIT)*

---

#### ⚡ Persona-Specific Follow-Ups
- **Practicalist**: *"How do you measure success on that?"* / *"What's the ROI you're seeing?"*
- **Conversationalist**: *"Tell me more about that — how did it feel?"* / *"What was the moment you knew?"*
- **Dominator**: *"You mentioned [X] — I've been thinking about that a lot. Can I ask your take on [Y]?"*

---

#### 🏛️ Consulting / Finance / High-Prestige Firm (use when target works at MBB, Big 4, investment bank, etc.)

These questions are sharper and more direct — suited for time-pressed, high-status professionals who respect preparation.

**About their firm & culture:**
- *"What surprised you most about [Firm] that you only discovered after joining?"*
- *"How would you describe someone who truly excels here — what separates them from the rest?"*
- *"What do you see as [Firm]'s biggest opportunity and biggest challenge right now?"*
- *"How would you compare [Firm] to others you've worked with or considered?"*

**About their career path:**
- *"What underrated skill do you think accelerated your growth here?"*
- *"What surprised you most moving from individual contributor to managing others?"*
- *"Looking back, what do you wish you'd known before entering this field?"*

**Situational / behavioral (if they're senior and the vibe allows):**
- *"Tell me about a time you had to persuade someone to change their mind when the stakes were high — how did you approach it?"*
- *"Describe a moment when you had to make a call with limited information. What did you do?"*
- *"What's a professional risk you took that paid off — and one that didn't?"*

**About breaking in (if you're exploring the field):**
- *"How do most people at your level enter this field — what paths tend to work?"*
- *"Considering my background, how well do you think I'd fit into this type of role?"* *(UB)*
- *"What would you recommend I do in the next 6 months to be a stronger candidate?"*
- *"Are there specific companies or teams within the industry you'd suggest I look at?"*

> **Tone note for consulting/finance targets:** Be crisp. Lead with your agenda. They appreciate directness and hate meandering. Show you've done the homework — reference their work, their firm's recent deals or reports, their public writing.

---

### 🔍 Finding Common Ground (TLDR)

Before the chat, scan their LinkedIn/X for:
- **Shared experiences**: same industry, career pivot, city, university
- **Shared interests**: topics they post about repeatedly
- **Shared values**: how they talk about their work and people

Use these to open genuine threads — not forced flattery. One real connection beats five generic questions.

---

### ✨ Value-Added Mindset

Go in with a giving mentality, not just a taking one:
- Bring a relevant article, resource, or intro to offer
- Share a genuine observation about their work: *"I noticed [X] — have you considered [Y]?"*
- Follow up within 24hrs: summarize 1-2 things you learned and mention what you'll do next

---

## ⚠️ Communication Tips

- **Tone**: Warm, curious, show genuine interest in their journey
- **Attitude**: Be authentic, appreciate their unique background
- **Address**: First names
- **Time Zone**: [Check time zone difference if remote]

---

## ✅ Pre-Chat Checklist

- [ ] Review company website and product
- [ ] Check recent LinkedIn/X posts
- [ ] Prepare 30-sec self introduction
- [ ] Set up calendar invite (consider time zones)
- [ ] Have questions ready
- [ ] Have pen and paper for notes
```

---

## Notion Push (Optional)

Requires `NOTION_API_KEY` environment variable and your target page ID.

```bash
# Set your Notion page ID here
NOTION_PAGE_ID="YOUR_NOTION_PAGE_ID"
NOTION_KEY="${NOTION_API_KEY}"

curl -s -X PATCH "https://api.notion.com/v1/blocks/${NOTION_PAGE_ID}/children" \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "☕ Coffee Chat Playbook: [Target]"}}]}},
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Date: [YYYY-MM-DD]"}}]}},
      {"object": "block", "type": "divider", "divider": {}},
      {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "📋 Target Profile Summary"}}]}},
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "[Basic info, background, recent topics]"}}]}},
      {"object": "block", "type": "divider", "divider": {}},
      {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "🏢 Company & Industry Research"}}]}},
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "[Funding, location, team, product, industry landscape]"}}]}},
      {"object": "block", "type": "divider", "divider": {}},
      {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "👥 Founder Deep Dive"}}]}},
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "[Background, work history, achievements, philosophy]"}}]}},
      {"object": "block", "type": "divider", "divider": {}},
      {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "📱 Recent Content & Posts"}}]}},
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "[LinkedIn posts + X activity]"}}]}},
      {"object": "block", "type": "divider", "divider": {}},
      {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "🔍 You vs Target"}}]}},
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "[Common ground and conversation starters]"}}]}},
      {"object": "block", "type": "divider", "divider": {}},
      {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "💬 Questions (8)"}}]}},
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "[8 questions: 3 personal, 3 work, 2 industry]"}}]}},
      {"object": "block", "type": "divider", "divider": {}},
      {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "🗣️ Talking Points (4)"}}]}},
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "[4 talking points]"}}]}},
      {"object": "block", "type": "divider", "divider": {}},
      {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "⚠️ Tips & ✅ Checklist"}}]}},
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "[Communication tips and pre-chat checklist]"}}]}}
    ]
  }'
```

---

## Quality Standards

1. **Always include Company & Industry Research** - funding, product, competitors, trends
2. **Always include Founder Deep Dive** - for startup targets, research each founder's background
3. **Always include Recent Content** - LinkedIn posts + X activity
4. **Always compare profiles** - find common ground between you and the target
5. **Generate exactly 8 questions** - 3 personal, 3 work, 2 industry
6. **Generate exactly 4 talking points** - show you've done homework
7. **Save locally** - always save to `memory/coffee-chat-{target-slug}-{YYYY-MM-DD}.md`
8. **Push to Notion** - if `NOTION_API_KEY` is configured
9. **Make questions specific** - based on their background, posts, company news

---

## Known Limitations

### LinkedIn Scraping
- LinkedIn company scrapers often return wrong data
- LinkedIn profile scrapers may fail on free Apify tier
- **Workaround**: Use web search for company/founder info, check X for recent posts

### Profile Cache
- Located at: `memory/my-profile.md`
- If missing, ask the user to provide their background before proceeding

### Notion
- Requires `NOTION_API_KEY` environment variable
- Set your page ID in the Notion Push section above
- Notion API version: `2022-06-28`
