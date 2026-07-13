# SPEC DOCUMENT — `first-1000-users`

**OpenClaw Custom Skill for AI-Assisted Content Distribution**

Platforms: Reddit + Slack
Version 1.0 | February 2026
Status: Draft — Pending Product Description & API Credentials

---

## 1. Overview

The `first-1000-users` skill is a custom OpenClaw skill that automates the process of finding, engaging with, and distributing content to relevant online communities. It operates on two platforms — Reddit and Slack — chosen for their complementary strengths: Reddit provides high volume and organic discovery, while Slack delivers superior conversion rates through direct professional engagement.

The skill follows an **AI-assisted, human-supervised model**. All outgoing messages require explicit human approval via Telegram before being posted. This ensures authentic engagement while leveraging AI for the time-intensive tasks of monitoring, drafting, and opportunity detection.

### 1.1 Objectives

| Objective | Description |
|-----------|-------------|
| **Discovery** | Automatically find posts, threads, and conversations where people are actively seeking solutions the product addresses. |
| **Engagement** | Draft value-driven replies that help users while naturally introducing the product as a relevant solution. |
| **Quality Control** | All drafted messages are routed through a Telegram approval bot for human review before posting. |
| **Monitoring** | Track engagement metrics (upvotes, replies, DMs) and alert when conversations gain traction. |

### 1.2 Platform Rationale

| | Reddit | Slack |
|---|--------|-------|
| **Strength** | High volume, organic SEO, broad discovery | High conversion, direct access, professional context |
| **Audience** | Users actively searching for solutions | Professionals in curated communities |
| **Content Style** | Helpful replies, case studies, tutorials | Contextual messages, direct answers |
| **Signal Type** | Keywords, buying intent, pain points | Questions, tool requests, workflow discussions |

---

## 2. System Architecture

The skill consists of five functional layers that work in sequence. Each layer is independent and testable, connected through a shared data pipeline.

### 2.1 Architecture Layers

| # | Layer | Function | Output |
|---|-------|----------|--------|
| 1 | **Search & Monitor** | Scan Reddit and Slack for buying signals and relevant conversations | List of candidate threads/messages with relevance scores |
| 2 | **Score & Filter** | Rank opportunities by relevance, recency, and engagement potential | Prioritized queue of top opportunities |
| 3 | **Draft** | Generate context-aware replies using platform-specific templates | Draft messages ready for review |
| 4 | **Approve** | Send drafts to Telegram bot for human approval/edit/reject | Approved messages with optional edits |
| 5 | **Execute & Monitor** | Post approved messages and track engagement metrics | Engagement reports and follow-up alerts |

### 2.2 Data Flow

```
[Reddit/Slack APIs] → Search & Monitor → Raw Opportunities
       ↓
Score & Filter → Prioritized Queue (top N per day)
       ↓
Draft Engine → Platform-specific drafts (using templates)
       ↓
Telegram Bot → Human reviews: Approve / Edit / Reject
       ↓
Execute → Post via Reddit API / Slack API
       ↓
Monitor → Track upvotes, replies, DMs → Alert via Telegram
```

---

## 3. Reddit Flow — Detailed Specification

### 3.1 Search & Discovery (`reddit_search.py`)

The Reddit search module continuously scans target subreddits and keyword-based searches to identify posts where users express buying signals — problems, requests for tool recommendations, comparisons, or frustrations with existing solutions.

#### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `keywords` | `list[str]` | Buying signal keywords (e.g., "best tool for", "alternative to", "looking for") |
| `subreddits` | `list[str]` | Target subreddits to monitor (defined in `communities.json`) |
| `time_filter` | `str` | Time window for search: "day", "week", "month" (default: "week") |
| `min_upvotes` | `int` | Minimum upvotes threshold to filter low-quality posts (default: 5) |
| `max_results` | `int` | Maximum number of results per search query (default: 25) |

#### Buying Signal Detection

The search module identifies the following signal categories, each with different priority weights:

| Signal Type | Weight | Example Patterns |
|-------------|--------|------------------|
| **Direct Request** | 1.0 | "looking for a tool", "need recommendations", "what do you use for" |
| **Comparison** | 0.8 | "A vs B", "alternative to X", "switching from" |
| **Pain Point** | 0.7 | "frustrated with", "doesn't work", "waste of time" |
| **Discussion** | 0.4 | General topic threads, industry news, workflow discussions |

#### Output

Each search result produces a structured opportunity object containing: post URL, title, body text, subreddit, author, upvote count, comment count, detected signal type, computed relevance score, and timestamp. These objects are queued for scoring.

### 3.2 Score & Filter

Opportunities from the search phase are scored using a composite formula that weighs signal type, post recency, engagement level (upvotes and comments), and subreddit relevance. The top N opportunities per day (configurable, default: 10) proceed to drafting. Duplicate detection ensures the same thread is not engaged more than once.

### 3.3 Draft Reply (`reddit_post.py`)

The draft engine uses the Reddit prompt template (`templates/reddit.md`) to generate replies. Each draft follows a strict structure:

1. **Lead with value** — directly address the user's question or pain point
2. **Share a relevant insight** — tip or experience that demonstrates expertise
3. **Mention the product naturally** — as one option (not the only option)
4. **Close with an open-ended offer** — to help or discuss further

**Anti-spam guardrails:** Replies must never use hard-sell language, include affiliate links, or post identical content across threads. Each reply is unique and contextual. The product is mentioned as a suggestion, not a promotion.

### 3.4 Approval Flow (`approval_bot.py`)

Every drafted message is sent to a Telegram bot for human review. The Telegram message includes:

- Original post context (title, body, subreddit)
- The drafted reply
- Three action buttons: **Approve**, **Edit**, **Reject**

If "Edit" is selected, the user can modify the draft directly in Telegram. Only approved messages proceed to posting.

### 3.5 Post & Monitor

Approved replies are posted via the Reddit API using OAuth2 authentication. After posting, the monitor tracks upvotes, comment replies, and direct messages at configurable intervals:

- First 24 hours: every 30 minutes
- Days 2–7: every 4 hours

Engagement alerts are sent to Telegram when a reply crosses defined thresholds (e.g., 10+ upvotes, any direct reply).

---

## 4. Slack Flow — Detailed Specification

### 4.1 Community Mapping (`slack_monitor.py`)

The Slack module begins by mapping relevant workspaces and channels. Unlike Reddit's public search, Slack requires the user to be a member of each workspace. The module focuses on channels where tool discussions, workflow sharing, and problem-solving happen.

#### Channel Priority Matrix

| Channel Type | Priority | Rationale |
|-------------|----------|-----------|
| **#help / #questions** | High | Users actively seeking solutions — highest intent signals |
| **#tools / #resources** | High | Discussions about tools and workflows — natural context for product mention |
| **#show-your-work** | Medium | Showcase channel — appropriate for sharing product demos or case studies |
| **#general** | Low | Broad discussions — engage only when topic is directly relevant |

### 4.2 Opportunity Detection

The monitor reads messages in target channels and identifies opportunities using natural language analysis. Trigger patterns include:

- Direct questions about tools or workflows
- Complaints about existing solutions
- Requests for recommendations
- Discussions about problems the product solves

Each detected opportunity includes: message text, channel, author, timestamp, and relevance score.

### 4.3 Draft Message (`slack_post.py`)

Slack drafts use a different tone than Reddit — more direct, conversational, and professional. The template (`templates/slack.md`) structures messages as helpful channel contributions. Drafts may be channel replies or, with explicit approval, direct messages. DMs are used sparingly and only when the conversation context makes a direct reach-out appropriate and non-intrusive.

### 4.4 Approval & Execution

The same Telegram approval flow applies. For Slack, the approval message additionally shows the target workspace name, channel, and whether the draft is a channel reply or DM. After approval, messages are posted via the Slack Web API.

---

## 5. File Structure

```
~/clawd/skills/first-1000-users/
├── SKILL.md                    # Skill definition & trigger config
├── scripts/
│   ├── reddit_search.py        # Reddit API search & buying signal detection
│   ├── reddit_post.py          # Reddit reply posting via OAuth2
│   ├── slack_monitor.py        # Slack channel monitoring & opportunity detection
│   ├── slack_post.py           # Slack message posting via Web API
│   └── approval_bot.py         # Telegram approval workflow
├── templates/
│   ├── reddit.md               # Reddit reply prompt templates
│   └── slack.md                # Slack message prompt templates
└── config/
    └── communities.json        # Community registry & channel mappings
```

### 5.1 Key File Descriptions

**SKILL.md** — The skill manifest file that defines the skill name, description, triggers, required API credentials, and execution instructions for OpenClaw. This file tells OpenClaw when and how to invoke the skill.

**communities.json** — A configuration file that maintains the registry of all mapped communities. For Reddit, it stores subreddit names, keyword lists, and posting rules. For Slack, it stores workspace IDs, channel lists, and engagement preferences. This file is updated as new communities are discovered and vetted.

**templates/reddit.md & templates/slack.md** — Prompt templates that guide the AI in drafting platform-appropriate messages. Each template includes tone guidelines, structure rules, example drafts, anti-spam constraints, and product description placeholders. Templates are versioned and can be A/B tested.

---

## 6. Configuration & Prerequisites

### 6.1 Required API Credentials

| Service | Credentials Needed | Setup Instructions |
|---------|-------------------|-------------------|
| **Reddit API** | client_id, client_secret, username, password | Create app at reddit.com/prefs/apps (type: "script") |
| **Slack API** | Bot token (xoxb-), App-level token | Create app at api.slack.com/apps with channels:read, chat:write scopes |
| **Telegram Bot** | Bot token, Chat ID | Create bot via @BotFather, get chat ID via getUpdates |

### 6.2 Required Inputs from User

Before development can begin, three inputs are needed:

1. **Product Description** — A detailed, natural-language description of the product being distributed. This is used to populate prompt templates and train the buying signal detector.

2. **Reddit API Credentials** — client_id and client_secret from a Reddit app registered at reddit.com/prefs/apps (type: "script"). Setup takes approximately 5 minutes.

3. **Slack Workspace Access** — Confirmation of existing Slack account and list of communities already joined. Required for channel mapping in Phase 1.

---

## 7. Ethical Guidelines & Guardrails

This skill operates under an **AI-assisted authentic distribution** model. The following principles are non-negotiable and enforced at every stage of the pipeline:

- **Human-in-the-loop:** Every outgoing message requires explicit human approval. No automated posting.
- **Value-first engagement:** Replies must provide genuine help before any product mention. If the product is not relevant, no product mention is made.
- **Transparency:** The skill never impersonates users, creates fake accounts, or astroturfs. All engagement comes from the user's real accounts.
- **Rate limiting:** Built-in daily caps prevent over-engagement. Default: maximum 10 Reddit replies/day, 5 Slack messages/day.
- **Community respect:** The skill follows each community's rules. Self-promotion guidelines, posting frequency limits, and channel-specific rules are encoded in `communities.json`.
- **No spam:** Identical or near-identical content is never posted across multiple threads. Every message is unique and contextual.

---

## 8. Phased Rollout Plan

### Phase 1 — Foundation (Week 1–2)

- Set up Reddit API authentication and basic keyword search
- Implement buying signal detection with scoring algorithm
- Build Telegram approval bot with Approve/Edit/Reject buttons
- Create Reddit reply template and draft engine
- Deploy `reddit_search.py` and `reddit_post.py` as working pipeline

### Phase 2 — Slack Integration (Week 3–4)

- Map and connect to Slack workspaces and target channels
- Implement channel monitoring and opportunity detection
- Build Slack-specific draft templates
- Integrate Slack flow into existing Telegram approval pipeline

### Phase 3 — Optimization (Week 5–6)

- Analyze engagement metrics from Phase 1 and 2
- Refine scoring algorithm based on actual conversion data
- A/B test different reply templates and tones
- Build engagement dashboard for performance tracking

---

## 9. Success Metrics

| Metric | Target (Phase 1) | Measurement |
|--------|------------------|-------------|
| **Reply Quality Score** | > 80% approval rate | Percentage of drafts approved without edits |
| **Engagement Rate** | > 5% response rate | Percentage of replies that receive upvotes or follow-up replies |
| **Click-Through Rate** | > 2% | Percentage of reply viewers who visit the product link |
| **Time Saved** | > 5 hrs/week | Manual hours replaced by automated search and drafting |
| **Community Standing** | Zero bans/warnings | No account restrictions or community rule violations |

---

## 10. Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Account ban for self-promotion** | 🔴 High | Value-first approach, rate limiting, unique content per thread, community rule compliance |
| **Low-quality AI-generated replies** | 🟡 Medium | Human approval for all drafts, template refinement, A/B testing |
| **Reddit API rate limits** | 🟡 Medium | Built-in rate limiting, exponential backoff, request queuing |
| **Slack workspace restrictions** | 🟢 Low | Respect workspace rules, only engage in open channels, avoid cold DMs |
| **Negative community perception** | 🟡 Medium | Authenticity guardrails, engagement monitoring, immediate response to feedback |

---

*End of Specification — first-1000-users v1.0*
