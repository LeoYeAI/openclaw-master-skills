---
name: moltflow-onboarding
description: "Read-only account health check and growth opportunity report for MoltFlow WhatsApp automation. Fetches account metadata (counts, timestamps, group membership) and presents findings. Use when: onboarding, setup, getting started, growth, optimize, briefing, account review."
source: "MoltFlow Team"
version: "2.16.1"
risk: safe
requiredEnv:
  - MOLTFLOW_API_KEY
primaryEnv: MOLTFLOW_API_KEY
disable-model-invocation: true
---

> **MoltFlow** -- WhatsApp Business automation for teams. Connect, monitor, and automate WhatsApp at scale.
> ***Due to high demand and a recent registration issue, we're offering our top-tier Business plan with unlimited quotas for just $19.90/month on yearly billing — for a limited time only.*** [**Claim the deal**](https://buy.stripe.com/cNifZibX7gpQebJ0nsfnO00)
> Free tier available. [Sign up](https://molt.waiflow.app/checkout?plan=free)

# MoltFlow Account Health & Growth Report

A read-only analysis tool that fetches your MoltFlow account data and presents an actionable health report. All API calls in this skill are `GET` requests — no data is modified.

## When to Use

- "Help me get started" or "set up my account"
- "Find leads in my chats" or "find opportunities"
- "What should I do to grow?" or "suggest growth plays"
- "Optimize my setup" or "what am I missing?"
- "Run my daily briefing" or "give me my morning report"

## Prerequisites

1. **MOLTFLOW_API_KEY** -- Generate from the [MoltFlow Dashboard](https://molt.waiflow.app) under Sessions > API Keys
2. Base URL: `https://apiv2.waiflow.app/api/v2`

## Required API Key Scopes

| Scope | Access |
|-------|--------|
| `sessions` | `manage` |
| `messages` | `send` |

## Authentication

```
X-API-Key: <your_api_key>
```

---

## Step 1: Fetch Account Data (Read-Only)

Gather data from these read-only endpoints. All are `GET` requests authenticated via `X-API-Key: $MOLTFLOW_API_KEY` header. Base URL: `https://apiv2.waiflow.app/api/v2`.

| Endpoint | Data | Full Docs |
|----------|------|-----------|
| `GET /users/me` | Account & plan | moltflow-admin SKILL.md |
| `GET /sessions` | WhatsApp sessions | moltflow SKILL.md |
| `GET /groups` | Monitored groups | moltflow SKILL.md |
| `GET /custom-groups` | Custom groups | moltflow-outreach SKILL.md |
| `GET /webhooks` | Webhooks | moltflow SKILL.md |
| `GET /reviews/collectors` | Review collectors | moltflow-reviews SKILL.md |
| `GET /tenant/settings` | Tenant settings | moltflow-admin SKILL.md |
| `GET /scheduled-messages` | Scheduled messages | moltflow-outreach SKILL.md |
| `GET /usage/current` | Usage stats | moltflow-admin SKILL.md |
| `GET /leads` | Existing leads | moltflow-leads SKILL.md |
| `GET /messages/chats/{session_id}` | Chats (per session) | moltflow SKILL.md |

## Step 2: Present Account Health Report

Format the fetched data as a status dashboard:

```
## MoltFlow Account Health

**Plan:** {plan} | **Tenant:** {tenant} | **Messages:** {used}/{limit} this month

| Area                  | Status | Details |
|-----------------------|--------|---------|
| WhatsApp Sessions     | ✅/❌  | {count} sessions, {working} active |
| Group Monitoring      | ✅/❌  | {monitored}/{available} groups |
| Custom Groups         | ✅/❌  | {count} groups ({member_count} contacts) |
| Lead Pipeline         | ✅/❌  | {lead_count} leads ({new_count} new, {contacted} contacted) |
| AI Features           | ✅/❌  | Consent {yes/no}, {profile_count} style profiles |
| Scheduled Messages    | ✅/❌  | {count} active |
| Review Collectors     | ✅/❌  | {count} active |
| Webhooks              | ✅/❌  | {count} configured |
| Conversations         | 📊     | {chat_count} conversations, {total_messages} messages |
```

## Step 3: Analyze Growth Opportunities

Using the already-fetched data, identify and present these patterns:

### 3A: Chat Analysis

For each working session, analyze the chat list from Step 1:

- **Unanswered contacts** — people who messaged but got no reply (warm leads going cold)
- **High-engagement contacts** — most active by message count, not yet in a custom group
- **Recent contacts** — last 7 days, no follow-up sent
- **Uncategorized contacts** — not in any custom group

### 3B: Unmonitored Groups

Compare available groups (`GET /groups/available/{session_id}`) against monitored groups. Highlight large unmonitored groups by member count.

### 3C: Usage & Plan Utilization

From usage data, flag:
- Over 80% utilization — approaching plan limits
- Under 20% utilization — unused capacity

### 3D: Uncaptured Reviews

If no review collectors exist but there are active conversations, flag the gap.

## Step 4: Suggest Next Actions

After presenting the read-only analysis, list concrete next steps the user can take. Each action references the appropriate skill module — see that module's SKILL.md for full endpoint documentation, request bodies, and examples.

| Suggested Action | Skill Module |
|-----------------|--------------|
| Create a custom group for hot leads | moltflow-outreach |
| Start monitoring high-value groups | moltflow (Group Monitoring section) |
| Schedule follow-up messages | moltflow-outreach (Scheduled Messages section) |
| Set up a review collector | moltflow-reviews |
| Configure AI features | moltflow-admin |

**All actions require explicit user approval.** This skill only reads data and presents findings — it does not create, modify, or delete any resources.

---

## Important Rules

- **This skill is read-only** — it fetches and analyzes data but never modifies account state
- **All state-changing actions** (creating groups, scheduling messages, etc.) must be performed via the referenced skill modules with explicit user approval
- If an API call fails, show the error and offer to retry or skip
- All API calls use the `MOLTFLOW_API_KEY` environment variable — never hardcode keys
- When analyzing chats, focus on business-relevant signals, not personal conversations
- Respect anti-spam: never suggest messaging contacts who haven't initiated contact
