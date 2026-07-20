[English](user-story.en.md) | [中文](user-story.md)

# A Real OpenClaw User's Experience

## 2 AM — Your Telegram Group Explodes

Friday night. You're about to sleep. Your phone starts buzzing nonstop — strangers in a Telegram group are spamming your AI bot with nonsense.

You check the config: `requireMention: false`.

That means the bot responds to *every single message* in any group it's in. Your API credits are draining at dozens of requests per minute.

You scramble to fix the config and restart Gateway. But you know this misconfiguration has been there for weeks — nobody noticed until now.

## Next Morning — Context Overflow

You wake up and find the bot has started "forgetting" — it can't recall anything from a few turns ago.

You check the session: `contextTokens` is set to 272,000, but the model's actual `contextWindow` is only 200,000. The extra 72k tokens were never used, but they threw off the compaction timing.

This number was left over from a model swap last month. You don't even remember changing it.

## Then Gateway Goes Down

Afternoon. The bot stops responding entirely.

`ps aux | grep openclaw` — two Gateway processes running simultaneously, fighting over the same port. Probably a leftover from the last manual restart.

You kill the extra process, restart Gateway. But wait — the logs are full of `Skipping skill path that resolves outside its configured root.` errors, repeating every 30 minutes. What's that about?

You start digging through docs, searching GitHub Issues, checking config files one by one...

**Two hours later. You've fixed three problems, but have no idea what else is lurking.**

---

## Then I Installed oc-doctor

```
/oc-doctor
```

One command. 60 seconds later:

```
# OpenClaw Doctor Report

## Summary
- Version: 2026.3.7 (update available: 2026.3.8)
- Gateway: running (port 18789)
- Overall Health: NEEDS ATTENTION

## Findings

### [CRITICAL] Telegram requireMention is false
- Bot responds to every message in groups
- Fix: set requireMention to true in channel config

### [WARNING] 3 Telegram sessions on wrong model
- Using deepseek/chat, config default is claude-sonnet-4
- Fix: openclaw sessions update --model ...

### [WARNING] Compaction missing reserveTokensFloor
- No buffer reserved — context may overflow before compaction triggers
- Fix: set reserveTokensFloor: 20000

### [WARNING] Browser cache 282 MB
- Fix: rm -rf ~/.openclaw/browser/*

### [INFO] System instructions using 2.6% of context
- BOOTSTRAP.md still present (588 tokens reclaimable)
- HEARTBEAT.md is empty template (67 tokens reclaimable)

...12 findings total
```

It doesn't just tell you what's wrong — **it tells you why it matters, how bad it is, and exactly how to fix it.**

Then it asks:

> "Would you like me to fix these? I can batch-fix all WARNING-level and below. CRITICAL issues will be confirmed individually."

You say "fix all".

30 seconds later:
- Telegram requireMention set to true
- Drifted session models realigned
- Compaction config patched with reserve buffer
- Browser cache cleared
- BOOTSTRAP.md archived, empty HEARTBEAT.md replaced with a practical heartbeat checklist

**What used to take two hours of manual troubleshooting — done in 2 minutes.**

---

## It Found Problems I Never Knew About

The most surprising part was the things I thought were fine:

- **12 disabled cron jobs** sitting in config — I'd forgotten they existed
- **HEARTBEAT.md was a hollow shell** — AGENTS.md said "read HEARTBEAT.md", but the file had only a title and no content, so the agent's heartbeat was doing nothing
- **Plaintext API keys in models.json** — it's a local file, but what if you accidentally `git init` someday?
- **4 .bak backup files** quietly taking up space, left over from debugging weeks ago

None of these are emergencies. But over time they become performance degradation, wasted tokens, and security risks.

## Now I Run It Weekly

```
/oc-doctor
```

Like a health check for OpenClaw. Most weeks the report says "healthy". Occasionally a WARNING pops up — fixed on the spot.

No more 2 AM wake-up calls from Telegram.

---

**Install in one line:**

```bash
npx skills add bryant24hao/oc-doctor -g -y
```
