# Event / Invitation Reference

## When to Use This Template

- User asks for an event page, invitation, meetup listing, conference agenda, or RSVP page
- Keywords: event, invitation, meetup, conference, workshop, webinar, agenda, RSVP, save the date
- Output is promoting or organizing a gathering (physical or virtual)
- User wants a shareable link for an event with date, location, and schedule

---

## Structure Template

```markdown
![{Event banner}]({banner_image_url})

# {Event Name}

**{Tagline — what attendees will get out of this event}**

---

## 📅 Details

| | |
|---|---|
| **Date** | {Day, Month DD, YYYY} |
| **Time** | {HH:MM – HH:MM timezone} |
| **Location** | {Venue name, Address} |
| **Format** | {In-person / Virtual / Hybrid} |
| **Cost** | {Free / $XX / Donations welcome} |

---

## About This Event

{2-3 paragraphs: What is this event? Who is it for? What will attendees learn, experience, or gain? Why should they attend?}

---

## 📋 Schedule

| Time | Session | Speaker |
|------|---------|---------|
| {HH:MM} | {Session title} | {Speaker name} |
| {HH:MM} | {Session title} | {Speaker name} |
| {HH:MM} | {Break / Networking} | — |
| {HH:MM} | {Session title} | {Speaker name} |
| {HH:MM} | {Closing / Social} | — |

---

## 🎤 Speakers

### {Speaker Name}
**{Title, Company}**
{1-2 sentences: relevant expertise and what they'll be speaking about.}

### {Speaker Name}
**{Title, Company}**
{1-2 sentences.}

---

## 📍 Venue

**{Venue Name}**
{Full address}

{Directions, parking info, or virtual meeting link.}

---

## 🎟 Register

**[Register here]({registration_url})**

{Or: "RSVP by replying to this page" / "Spots limited — first come, first served" / "Free — just show up"}

---

*Organized by {organizer}. Questions? Contact {email}.*
```

---

## Styling Guidelines

- **Date and location immediately visible** — Use the key-value table at the top. These are the two things every visitor looks for first.
- **Banner image**: Full-width markdown image at the very top if available. Sets the mood.
- **Schedule as a table** — Time, Session, Speaker columns. Include breaks and networking slots.
- **Speaker bios: 1-2 sentences max** — Name, title, company, and what they'll talk about. No life stories.
- **Registration CTA is prominent** — Use bold link, H2 section header, and add urgency if applicable ("Only 30 spots")
- **Emoji section headers** — 📅 📋 🎤 📍 🎟 help with visual scanning on event pages

---

## Chart Recommendations

Charts are **rarely used** in event pages. One exception:

**Schedule timeline bar chart** (for multi-day or long events):
```
```markdown-ui-widget
chart-bar
title: Conference Day 1 — Session Duration (min)
Session,Duration
"Opening Keynote",45
"Workshop A",90
"Lunch Break",60
"Panel Discussion",60
"Lightning Talks",30
"Networking Social",90
```
```

In general, tables are better than charts for event schedules.

---

## Professional Tips

1. **Date + location in the first 5 seconds** — If a visitor can't immediately find when and where, they'll leave
2. **Clear registration action** — One button or link. Don't make people search for how to sign up.
3. **Schedule with times** — "Afternoon session" is useless. "14:00–15:30" lets people plan their day.
4. **Speaker bios: 1-2 sentences** — Focus on why this person is qualified to speak on this topic. Not their full CV.
5. **Include practical details** — Parking, transit, Wi-Fi, what to bring, dress code. These reduce friction.
6. **Add urgency if real** — "Limited to 50 spots" or "Early bird ends March 20" drives action. But never fake scarcity.
7. **Virtual event details** — For online events, specify the platform (Zoom, Google Meet), whether it will be recorded, and time zone clearly.

---

## Example

```markdown
![Tech Meetup Banner](https://events.example.com/banners/devtalks-march.jpg)

# DevTalks Bucharest — March Edition

**An evening of lightning talks on AI agents, local-first software, and developer tooling**

---

## 📅 Details

| | |
|---|---|
| **Date** | Thursday, March 27, 2026 |
| **Time** | 18:30 – 21:30 EET |
| **Location** | TechHub Bucharest, Str. Splaiul Independenței 319 |
| **Format** | In-person (no livestream) |
| **Cost** | Free |

---

## About This Event

DevTalks March is back with three speakers covering the hottest topics in developer tooling. Whether you're building AI agents, exploring local-first architecture, or optimizing your dev workflow — there's something for you.

This is an informal, community-driven event. Come for the talks, stay for the pizza and conversations. All experience levels welcome.

---

## 📋 Schedule

| Time | Session | Speaker |
|------|---------|---------|
| 18:30 | Doors open + networking | — |
| 19:00 | Building AI Agents That Actually Work | Ana Popescu |
| 19:25 | Local-First: Why Your App Should Work Offline | Mihai Ionescu |
| 19:50 | Break + pizza | — |
| 20:10 | Developer Tooling in 2026: What's Changed | Cristina Dumitrescu |
| 20:35 | Open Q&A + panel | All speakers |
| 21:00 | Networking + drinks | — |

---

## 🎤 Speakers

### Ana Popescu
**AI Engineer, OpenClaw**
Building production AI agent systems for the past 2 years. Will share real-world patterns for agent orchestration and failure handling.

### Mihai Ionescu
**Staff Engineer, Linear**
Works on Linear's sync engine. Will demo a local-first architecture that handles conflicts gracefully.

### Cristina Dumitrescu
**DevRel Lead, Vercel**
Previously at GitHub. Will survey the developer tooling landscape and highlight underrated tools for 2026.

---

## 📍 Venue

**TechHub Bucharest**
Splaiul Independenței 319, Sector 6, Bucharest

Metro: Politehnica station (M3), 5-minute walk. Parking available at Mall Plaza România across the street.

---

## 🎟 Register

**[RSVP on Meetup](https://meetup.com/devtalks-buc/march-2026)**

Limited to 80 spots. Registration closes March 26 or when full.

---

*Organized by DevTalks Bucharest Community. Questions? Contact events@devtalks.ro*
```
