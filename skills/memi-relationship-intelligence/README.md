# Relationship Intelligence

A comprehensive personal CRM and relationship intelligence skill for [OpenClaw](https://openclaw.ai). It gets smarter about your relationships the more you use it.

## Install

```bash
clawhub install memi-relationship-intelligence
```

## What It Does

Tell your agent about the people in your life and it remembers everything — names, companies, how you met, what they like, important dates, promises you've made, and how they're all connected.

The more you use it, the sharper it gets. It learns your relationship patterns, detects what kinds of connections matter most to you, figures out your natural communication rhythms, and evolves its understanding of your social world over time.

### Save contacts naturally

> "met sarah at the google mixer, she's a PM there"
>
> *oh nice — saved Sarah, PM at Google. the mixer downtown?*

### Track commitments

> "I told Jake I'd send him that article about AI infrastructure"
>
> *noted — I'll remind you about that*

### Look up anyone

> "what do I know about Sarah?"
>
> *Sarah Chen — PM at Google, met at the mixer downtown. You mentioned she's into rock climbing and you promised to send her that podcast episode.*

### Morning briefs

> *hey — you told Jake you'd send that article 3 days ago. Also, Sarah's birthday is next week and she's into craft beer. You've got a call with David at 2pm — last time you talked he mentioned moving to Austin.*

### Cooling detection (gets smarter over time)

Early on:
> "who should I catch up with?"
>
> *been a minute since you mentioned Jake — he'd probably love to hear from you.*

After learning your patterns:
> *you usually catch up with your Sequoia contacts monthly — been about 6 weeks since you mentioned David. Also, you met 4 people at the Austin conference 2 weeks ago and haven't followed up with any of them.*

### Network intelligence

> "who do I know at Stripe?"
>
> *you know Jake directly — engineer there. And Sarah's old college roommate David just joined their platform team, so she could probably intro you.*

## How It Learns

The skill builds a persistent model of your relationship world that evolves with every interaction:

- **Relationship archetypes** — Instead of fixed categories, it discovers what types of relationships YOU have. A VC might have "portfolio founders" and "LP contacts." A student might have "study group" and "club friends." These emerge from your data, not from presets.
- **Communication rhythms** — Learns how often you naturally engage with different types of contacts. Uses this for smarter cooling detection — a close friend going quiet for 2 weeks is noteworthy; an industry acquaintance going quiet for 2 months is normal.
- **Network patterns** — Notices meta-patterns in how you build and maintain relationships. "You tend to meet people at conferences and follow up within a week." Uses these for proactive suggestions.
- **Self-correction** — When you correct it or ignore suggestions, it updates its model. If you consistently ignore cooling alerts for networking contacts, it adjusts the threshold. Your behavior teaches it what matters to you.

## Features

- Contact extraction from natural language with 3-strategy deduplication
- Structured notes, preferences (likes/dislikes/dietary/gift ideas), and important dates
- Commitment tracking with automatic promise detection
- Relationship scoring with cooling/cold detection (invisible to user — no scores or metrics ever shown)
- Relationship graph between contacts with warm introduction path finding
- Communication style analysis per contact
- Morning briefs with overdue commitments, upcoming dates, cooling contacts, and pattern-based suggestions
- Pre-meeting context briefs via Google Calendar (requires gog)
- Post-meeting follow-up prompts
- Email signal extraction via Gmail (requires gog)
- Contact enrichment from Google Contacts (requires gog)
- Follow-up message drafting matched to your tone and the contact's style
- Conversation import from pasted text
- Photo/business card/LinkedIn screenshot scanning
- Reminders (one-time and recurring)
- Emergent relationship archetypes with per-archetype cooling thresholds
- Cross-contact pattern matching and network cluster detection

## Requirements

- `sqlite3` (required) — data stored locally at `~/.local/share/memi-ri/memi.db`
- `gog` (optional) — Google Calendar, Gmail, and Contacts integration

## Privacy

Everything is local. Your contacts, notes, relationship data, and learned patterns live in a SQLite file on your machine. Google integration (via gog) uses your own OAuth credentials. No data leaves your machine except to the LLM provider you've configured in OpenClaw.

## License

MIT-0
