# Operations Methodology

The core operating system for X account operations. Built on a Plan-Do-Check-Act (PDCA) closed loop that runs at daily, weekly, monthly, and quarterly cadences.

---

## Philosophy

X operations is not "post and hope." It is a disciplined system where every action generates data, every data point informs the next action, and the strategy continuously evolves based on empirical results.

```
Plan → Do → Check → Act → (repeat, but smarter)
```

The goal is to find YOUR optimal operating formula — the specific combination of content types, posting times, engagement tactics, and voice that maximizes results for your unique account, audience, and objectives.

---

## Daily Loop

### Morning Phase: Plan + Warm Up (30-45 min)

**1. Scan & Collect (15 min)**
- Check overnight activity: mentions, replies, DMs
- Scan core circle watchlist for engagement opportunities
- Review trending topics in your niche (X search, industry feeds)
- Check competitor accounts for content inspiration
- Note any breaking news or hot topics relevant to your space

**2. Plan Today's Content (10 min)**
- Select today's content theme from [content calendar](../config/content-calendar.example.json)
- Choose 2-3 tweet ideas (mix of value, opinion, story, or engagement — see [content strategy](content-strategy.md))
- If thread day: finalize thread draft (should be prepared day before)
- Identify 1-2 product integration opportunities (see [product integration](product-integration.md))
- Check if any scheduled posts need adjustment based on breaking news

**3. Warm Up the Algorithm (15-20 min)**
- Reply to 10-15 accounts from your core circle (2-10x your follower count)
- Focus on accounts that posted in the last 30-60 minutes (early replies get more visibility)
- Every reply must add value: data, a different perspective, a genuine question, or a personal story
- This is not optional — it directly impacts the reach of your subsequent posts

### Execution Phase: Create + Post + Engage (throughout the day)

**4. Post Content (2-3 posts spaced 2-3 hours apart)**
- Post at your configured optimal windows (see [cron schedule](cron-schedule.md))
- Stay active for 30-60 minutes after each post
- Reply to every comment in the first hour
- No external links in main tweet body (links go in first reply)

**5. Active Engagement (15-20 min, 2-3 times during the day)**
- Check for new mentions and reply to high-quality ones
- Engage with your core circle's new posts
- Look for real-time opportunities (trending topics, viral discussions)
- Post in relevant X Communities (2-3x per week)

### Evening Phase: Check + Reflect (15-20 min)

**6. Daily Performance Check**
- Collect metrics for today's posts (impressions, engagement rate, replies, bookmarks)
- Compare against your baseline metrics from [goals](../config/goals.example.json)
- Note which content type performed best/worst today
- Record any anomalies or surprises

**7. Quick Reflection (5 min)**
Use the [daily review template](../templates/daily-review.md):
- What worked today? (content, timing, engagement)
- What didn't work? Why?
- One thing to try differently tomorrow
- Any insight worth saving to evolution state

**8. Plan Tomorrow**
- Draft tomorrow's content (especially if tomorrow is a thread day)
- Identify tomorrow's engagement targets from watchlist
- Queue any scheduled posts

---

## Weekly Loop (Sunday evening, ~45 min)

Use the [weekly review template](../templates/weekly-review.md):

### 1. Performance Analysis (20 min)
- Run analytics for the week (use `scripts/analytics_reporter.py`)
- Calculate: total tweets, total impressions, avg engagement rate, best/worst performing
- Compare week-over-week trends
- Identify top 3 and bottom 3 tweets — analyze WHY each performed as it did

### 2. Content Audit (10 min)
- Review content mix ratio: were you hitting 40% value / 25% opinion / 25% story / 10% engagement?
- Track which content pillars are overrepresented or underrepresented
- Assess thread performance (if any posted this week)
- Check product integration frequency — too much? too little?

### 3. Engagement Review (10 min)
- Review core circle engagement — did you reply to enough accounts? Quality of replies?
- Check relationship development — any accounts moving from cold to warm?
- Review DM conversations — any new connections worth nurturing?
- Community engagement — participation in X Communities and Spaces

### 4. Next Week Planning (5 min)
- Set next week's content calendar (adjust themes based on learnings)
- Identify any scheduled events, launches, or trending topics to capitalize on
- Set one specific A/B test for next week (see A/B Testing section below)
- Update watchlist if needed (add/remove accounts)

---

## Monthly Loop (end of month, ~1 hour)

Use the [monthly review template](../templates/monthly-review.md):

### 1. Goal Progress Evaluation
- Compare current metrics against monthly targets from goals config
- Calculate: follower growth %, engagement rate trend, impressions trend
- Assess business metrics: website referrals, leads, mentions by target accounts
- Decide: on track, ahead, or behind?

### 2. Strategy Assessment
- Which content pillars drove the most growth this month?
- Which posting times consistently performed best?
- Which engagement tactics produced the strongest relationship signals?
- Is your persona/voice resonating? (check reply quality and tone of incoming engagement)

### 3. Competitor Check
- Run competitor analysis framework (see [competitor framework](competitor-framework.md))
- Note any strategy shifts from benchmark accounts
- Identify new tactics worth testing

### 4. Strategy Adjustments
- Adjust content mix ratios based on performance data
- Refine posting schedule if data shows better windows
- Update goals if significantly ahead or behind
- Add new A/B tests for next month

### 5. Evolution State Update
- Update `.evolution/strategy-state.json` with current best-performing parameters
- Document key learnings in `.evolution/reflections.json`
- Update profile (bio, pinned tweet, header) if positioning has evolved

---

## Quarterly Loop (end of quarter, ~2 hours)

### 1. Major Strategy Review
- Review 3-month growth trajectory against original goals
- Assess whether primary objective is still correct (brand vs. leads vs. fundraising)
- Evaluate if target audience definition needs refinement
- Compare your account growth rate against industry benchmarks (see [growth benchmarks](growth-benchmarks.md))

### 2. Persona Evolution
- Has your voice naturally evolved? Does the profile still match?
- Are there new personality anchors or running themes that emerged?
- Update `config/profile.json` with evolved voice and persona attributes

### 3. Goal Reset
- Set new quarterly goals based on current trajectory
- Adjust growth stage if you've crossed a threshold (e.g., early -> growth)
- Recalibrate KPI targets

### 4. Skill Update
- Document any new tactics or frameworks discovered
- Update reference documents with new learnings
- Archive outdated strategies

---

## A/B Testing Protocol

Systematic testing is the engine of continuous improvement. Run one test per week.

### Test Design
- **Variable**: Change ONE thing at a time (posting time, content format, hook style, CTA approach)
- **Control**: Keep everything else the same
- **Sample size**: Test for at least 5-7 posts before drawing conclusions
- **Metric**: Define the success metric before starting (engagement rate, reply count, impressions)

### Test Categories

| Category | Example Tests |
|----------|--------------|
| Timing | Morning vs. evening posts for same content type |
| Format | Text-only vs. text+image for same insight |
| Hook style | Question hook vs. bold claim vs. story hook |
| Thread length | 5-tweet vs. 10-tweet threads |
| CTA approach | Soft CTA vs. direct CTA vs. no CTA |
| Content pillar | Technical depth vs. builder's journey for same topic |
| Product mention | Subtle background vs. contextual reference |

### Results Tracking

After each test cycle:
1. Record results in weekly review
2. If significant: adopt the winning variant as new default
3. If inconclusive: extend the test or note as neutral
4. Update evolution state with confirmed learnings

---

## Posting Frequency by Growth Stage

Research-backed guidelines (adjust based on your capacity and A/B test results):

| Growth Stage | Daily Tweets | Daily Replies | Weekly Threads | Space between Posts |
|-------------|-------------|---------------|----------------|-------------------|
| Early (0-1K) | 3-5 | 10-15 | 1 | 2-3 hours |
| Growth (1K-10K) | 5-10 | 15-20 | 1-2 | 2-3 hours |
| Established (10K-50K) | 10-15 | 20-30 | 2 | 1-2 hours |
| Authority (50K+) | 5-10 | 10-15 | 1-2 | 2-3 hours |

Note: Authority accounts can post less because each post has massive organic reach. Early accounts need more volume to find what works and build relationship signals.

---

## Content Mix Ratios

Target ratio (adjust based on A/B testing):

| Content Type | Target % | Purpose |
|-------------|----------|---------|
| Value tweets | 40% | Tips, insights, how-tos, tutorials — builds authority |
| Opinion tweets | 25% | Contrarian takes, hot takes, predictions — builds thought leadership |
| Story tweets | 25% | Personal experiences, build-in-public, lessons — builds connection |
| Engagement tweets | 10% | Questions, polls, "which do you prefer?" — builds community |

**Promotional content cap**: No more than 20% of total posts should be directly promotional (Tier 3 in [product integration](product-integration.md)). Product mentions through Tier 1 (background) and Tier 2 (contextual) don't count toward this cap.

---

*Methodology v1.0*
