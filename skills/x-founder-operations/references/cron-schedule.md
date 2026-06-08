# Cron Schedule

Automated task schedule for daily X operations. Configure based on your timezone and target audience.

---

## Timezone Configuration

Calculate your posting windows based on:
- **Your timezone**: Set in [profile config](../config/profile.example.json)
- **Target audience timezone**: Usually US East (ET) or US West (PT) for tech/founder accounts
- **Peak windows**: 09:00-12:00 and 17:00-20:00 in target audience timezone

### Timezone Mapping Example

For an operator in Asia (UTC+8) targeting US audiences:

| Your Local | US East (ET) | US West (PT) | Activity |
|-----------|-------------|-------------|----------|
| 01:00 | 12:00 | 09:00 | US lunch / West morning — **Window A** |
| 08:00 | 19:00 | 16:00 | US evening / West afternoon |
| 09:00 | 20:00 | 17:00 | US prime time — **Window B** |
| 22:00 | 09:00 | 06:00 | US East morning (West too early) |

For an operator in US East (ET):

| Your Local | US East (ET) | US West (PT) | Activity |
|-----------|-------------|-------------|----------|
| 09:00 | 09:00 | 06:00 | East morning — **Window A** |
| 12:00 | 12:00 | 09:00 | East lunch / West morning |
| 17:00 | 17:00 | 14:00 | East end-of-day — **Window B** |
| 20:00 | 20:00 | 17:00 | Evening engagement |

---

## Daily Task Schedule

### Task 1: Morning Scan

**When**: 30 minutes before Window A
**Duration**: 15 min (automated) + 15 min (manual review)

**Automated actions**:
1. Fetch trending topics in your niche keywords
2. Scan core circle accounts for recent high-engagement posts
3. Check overnight mentions, replies, and DMs
4. Generate "Morning Briefing" report

**Keywords to monitor** (configure per account):
- Your product name
- Your industry terms (e.g., "AI Agent", "developer tools")
- Competitor names
- Trending hashtags in your space

**Report format**:
```
Morning Briefing — [Date]

Trending Topics:
- [Topic 1]: [Brief context]
- [Topic 2]: [Brief context]

Core Circle Activity:
- @account posted about [topic] — engagement opportunity
- @account's tweet getting traction — reply candidate

Overnight Mentions:
- [List of mentions requiring response]

Suggested Actions:
1. Reply to @account's post about [topic]
2. Post about [trending topic] — draft angle: [suggestion]
3. Respond to mention from @account
```

### Task 2: Posting Reminder — Window A

**When**: Start of Window A
**Duration**: 5 min reminder

**Actions**:
1. Remind to post (or confirm scheduled post went live)
2. Provide content recommendation based on:
   - Today's content calendar theme
   - Morning scan results
   - Content mix ratio compliance

**Content recommendation format**:
```
Window A Posting Reminder

Today's Theme: [from content calendar]
Recommended Angle: [specific suggestion]
Content Pillar: [which pillar this serves]
Product Integration: [Tier 1/2/3 recommendation]

Content Mix Status (this week):
- Value: [actual]% / [target]%
- Opinion: [actual]% / [target]%
- Story: [actual]% / [target]%
- Engagement: [actual]% / [target]%
```

### Task 3: Midday Content Collection

**When**: Between Window A and Window B
**Duration**: 15 min (automated)

**Automated actions**:
1. Scan for new trending topics since morning
2. Check performance of Window A post (early metrics)
3. Identify engagement opportunities (new posts from core circle)
4. Update content recommendations for Window B

### Task 4: Posting Reminder — Window B

**When**: Start of Window B
**Duration**: 5 min reminder

Same format as Task 2, updated with midday scan results.

### Task 5: Engagement Follow-up

**When**: 30 minutes after Window B
**Duration**: 15 min (automated analysis)

**Actions**:
1. Collect metrics for today's posts
2. Identify high-quality replies worth responding to
3. Check for quote tweet opportunities
4. Generate engagement recommendations

**Engagement criteria**:
- Replies from accounts in your core circle (always respond)
- Thoughtful replies that add value (respond with depth)
- Questions about your domain (reply with expertise)
- Mentions by larger accounts (respond promptly)

### Task 6: Mentions Check

**When**: 1 hour after Window B
**Duration**: 10 min (automated)

**Actions**:
1. Check all mentions since last scan
2. Categorize: needs reply, acknowledge, skip
3. Flag high-priority mentions (from target accounts, investors, media)
4. Generate mention report

### Task 7: Evening Review

**When**: End of day (your timezone)
**Duration**: 10 min (automated) + 10 min (manual reflection)

**Automated actions**:
1. Collect final metrics for all posts today
2. Compare against daily targets from goals config
3. Calculate content mix compliance
4. Generate daily performance summary

**Manual actions** (using [daily review template](../templates/daily-review.md)):
1. Record what worked and what didn't
2. Identify one thing to try differently tomorrow
3. Draft tomorrow's content ideas
4. Update evolution state if any significant learnings

---

## Weekly Tasks

### Sunday Evening: Weekly Performance Review

**When**: Sunday evening (your timezone)
**Duration**: 30 min (automated analysis) + 15 min (manual review)

**Automated actions**:
1. Run full analytics for the week
2. Calculate week-over-week trends
3. Identify top 3 and bottom 3 performing posts
4. Generate content mix analysis
5. Produce competitor activity summary

**Manual actions** (using [weekly review template](../templates/weekly-review.md)):
1. Review automated report
2. Decide next week's A/B test
3. Adjust content calendar if needed
4. Update watchlist and core circle

---

## Monthly Tasks

### End of Month: Monthly Strategy Review

**When**: Last day of month
**Duration**: 30 min (automated) + 30 min (manual)

**Actions**:
1. Run full monthly analytics
2. Compare against monthly targets from goals config
3. Run competitor analysis framework
4. Update strategy parameters in evolution state
5. Refresh content calendar themes
6. Profile audit (bio, pinned tweet, header)

---

## Task Dependencies

```
Morning Scan
    ↓
Window A Posting Reminder (uses scan results)
    ↓
Midday Content Collection
    ↓
Window B Posting Reminder (uses midday scan)
    ↓
Engagement Follow-up (uses today's post data)
    ↓
Mentions Check
    ↓
Evening Review (uses all day's data)
```

---

## Error Handling

### If API Fails
1. Retry with exponential backoff (3 attempts max)
2. Log error in validation report
3. Report failure to user with clear error description
4. NEVER proceed with fabricated data

### If Data Anomaly Detected
1. Flag immediately in report
2. Cross-check with alternative sources
3. Exclude suspicious data from analysis
4. Alert user to investigate

### If Cron Job Missed
1. Run the missed task as soon as possible
2. Adjust subsequent tasks if they depend on the missed one
3. Note the gap in daily review
4. Check if the miss was a system issue or a configuration problem

---

## Validation Principles (Non-Negotiable)

These principles apply to ALL automated tasks:

1. **NEVER fabricate data** — If API fails, report failure honestly
2. **Mark missing data as null** — Never substitute 0 or estimates
3. **Cross-validate** — When possible, verify data from multiple sources
4. **Flag anomalies** — Don't silently ignore suspicious data
5. **Log everything** — All task executions and their outcomes should be traceable

---

*Cron Schedule v1.0*
