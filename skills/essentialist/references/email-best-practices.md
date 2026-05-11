# Cold Email Best Practices

Reference guide for the Essentialist email outreach platform. Use this knowledge when creating campaigns, writing templates, and advising users.

## Subject Line Formulas

### What Works
- **Question format**: "Quick question about {{company}}" (35-50% open rates)
- **Relevance hook**: "Noticed {{company}} isn't ranking for [keyword]"
- **Mutual connection**: "{{referral_name}} suggested I reach out"
- **Brevity**: 4-7 words outperform longer subjects
- **Personalization**: Including company name boosts opens 22%

### What to Avoid
- ALL CAPS or excessive punctuation (!!!)
- Spam trigger words: "free", "guarantee", "act now", "limited time"
- Misleading subjects (RE: or FWD: without actual thread)
- Generic subjects: "Following up", "Quick question"
- Emojis in subject (reduces deliverability on some providers)

## Email Body Structure

### The Problem-Solution-CTA Framework

```
Hi {{first_name}},

[1 sentence: specific observation about their company/industry]

[1-2 sentences: the problem this creates]

[1-2 sentences: how you solve it, with proof point]

[1 sentence: clear, low-commitment CTA]

Best,
[Name]
```

### Key Rules
- **Under 80 words** — longer emails get lower reply rates
- **ONE call-to-action** — multiple CTAs confuse and reduce response
- **No attachments** — triggers spam filters
- **Plain text style** — even in HTML, keep it looking like a personal email
- **No images in first email** — images trigger spam filters on cold email
- **Mobile-friendly** — 60%+ of emails opened on mobile

### Call-to-Action Examples (Low Commitment)
- "Worth a quick chat?"
- "Mind if I send over a brief case study?"
- "Would it be helpful if I shared how we did this for [similar company]?"
- "Is this something you're thinking about right now?"

Avoid high-commitment CTAs like "Schedule a demo" or "Sign up for a trial" in cold outreach.

## Personalization Strategies

### Available Merge Tags
- `{{first_name}}` — Contact first name
- `{{last_name}}` — Contact last name
- `{{email}}` — Contact email
- `{{company}}` — From custom_fields
- Any custom field: `{{field_name}}`

### Levels of Personalization
1. **Basic**: First name + company name
2. **Research-based**: Reference specific company detail (website, recent news)
3. **Trigger-based**: Reference specific event (job posting, funding round, product launch)

Higher personalization = higher reply rates but lower volume. For cold outreach at scale, Level 1-2 is the sweet spot.

## Sequence Design

### Optimal Length: 3-5 Emails

| Email | Timing | Purpose | Expected Performance |
|-------|--------|---------|---------------------|
| 1. Cold Intro | Day 0 | Hook + value prop | 15-25% open, 2-5% reply |
| 2. Follow-up | Day 3 | Different angle + social proof | 10-20% open, 1-3% reply |
| 3. Value add | Day 7 | Share resource/insight | 10-15% open, 1-2% reply |
| 4. Break-up | Day 12 | Last chance, create urgency | 12-18% open, 1-3% reply |

### Sequence Flow
- Each email should stand alone (don't assume they read previous ones)
- Vary the angle — don't just repeat the same pitch
- The "break-up" email often gets highest reply rate due to loss aversion
- After 4-5 emails with no response, stop. More emails = spam complaints.

### Timing Rules
- **Between emails**: 3-5 days minimum
- **Send window**: Weekdays only, 8am-5pm recipient timezone
- **Best days**: Tuesday, Wednesday, Thursday
- **Worst days**: Monday (inbox overwhelm), Friday (weekend mindset)
- **Never**: weekends, holidays, late night

## Domain Warming Deep Dive

### Why Warming Matters
New domains have no reputation. ISPs (Gmail, Outlook, Yahoo) treat unknown senders as suspicious. Warming builds trust gradually.

### Warming Schedule

| Week | Daily Volume | Notes |
|------|-------------|-------|
| 1 | 10-20 | Send to known contacts or warming targets |
| 2 | 20-40 | Mix warming + real outreach |
| 3 | 40-80 | Increase real outreach proportion |
| 4 | 80-150 | Near full capacity |
| 5-6 | 150-300 | Full capacity, monitor bounce rate |

### Warming Best Practices
- Never skip warming on a new domain
- If you pause sending for 2+ weeks, re-warm at 50% of previous volume
- Monitor bounce rate daily during warming — if > 3%, slow down
- Warming emails should have real engagement (opens, clicks, replies)
- The Essentialist warming system handles this automatically via rescue routine

### Volume Ramp Rule
**Never increase daily volume by more than 20% in a single day.**

Example: If sending 50/day, max next day is 60. Not 100.

## Deliverability

### DNS Requirements (SPF, DKIM, DMARC)
- **SPF**: Authorize Mailgun to send on behalf of your domain
- **DKIM**: Enable email signature verification
- **DMARC**: Set policy (start with `p=none`, move to `p=quarantine`)
- All three must be configured before sending at volume

### Deliverability Monitoring
- **Bounce rate > 3%**: Warning — slow down, clean list
- **Bounce rate > 5%**: Critical — pause sending immediately
- **Spam complaint rate > 0.1%**: Review email content and targeting
- **Open rate < 10%**: Subject lines need improvement or list quality is poor

### List Hygiene
- Verify emails before importing (use verification endpoint)
- Remove bounced contacts immediately (system does this automatically)
- Remove contacts who haven't engaged after full sequence
- Re-verify lists older than 3 months

## When to Stop a Campaign

### Positive Signals (Keep Going)
- Open rate > 20%
- Reply rate > 2%
- Getting interested/question replies
- Low bounce rate (< 2%)

### Warning Signals (Adjust)
- Open rate 10-20% — improve subject lines
- Reply rate 1-2% — improve body copy or targeting
- Bounce rate 2-5% — clean list, slow down

### Stop Signals (Pause Immediately)
- Bounce rate > 5%
- Spam complaints
- Open rate < 5% (likely going to spam)
- 80%+ not_interested replies
- Domain blacklisted

## Industry Benchmarks

| Metric | Average | Good | Excellent |
|--------|---------|------|-----------|
| Open Rate | 15-25% | 25-35% | 35%+ |
| Reply Rate | 1-3% | 3-5% | 5%+ |
| Click Rate | 2-5% | 5-8% | 8%+ |
| Bounce Rate | 2-4% | < 2% | < 1% |
| Interested Rate | 0.5-1% | 1-2% | 2%+ |

These vary by industry:
- **Tech/SaaS**: Higher open rates, lower reply rates
- **Professional Services**: Moderate opens, higher reply rates
- **Agency/Marketing**: Lower opens (inbox fatigue), moderate replies
- **Local Business**: Highest reply rates when personalized
