# X Algorithm Guide (2025-2026)

How the X algorithm distributes content and how to work with it.

---

## How Distribution Works

Every tweet enters a ranking pipeline. The algorithm decides who sees it based on four signal categories:

1. **Engagement velocity** — Speed of interactions in the first 15-30 minutes
2. **Relationship signals** — History of interactions between author and viewer
3. **Content quality** — Predicted engagement based on content features
4. **Interest matching** — Topic alignment via SimClusters (~145K topic groups)

The critical insight: **early, fast engagement matters far more than total engagement**. A tweet with 10 interactions in 5 minutes outranks one with 100 interactions over 24 hours.

---

## Engagement Weight Hierarchy

Not all engagement is equal. Approximate weights:

| Action | Weight | Notes |
|--------|--------|-------|
| Reply | 1x (baseline) | Signals conversation; strongest positive signal |
| Retweet / Quote | ~1x | Signals distribution-worthy content |
| Bookmark | ~1x | Signals high-intent relevance (save-worthy) |
| Like | ~0.5x | Passive; weakest positive signal |
| Profile click | ~24x vs like | Strong interest signal |
| 2+ min dwell time | ~22x vs like | Deep content consumption |
| Mute | ~-74x | Devastating negative signal |
| Block | ~-74x | Devastating negative signal |
| Report | ~-74x | Devastating negative signal |

**Optimization priority**: Create content that generates replies, bookmarks, and extended reading time — not just likes.

---

## Key Algorithm Rules

### 1. The 30-Minute Window

The first 30 minutes after posting determine 80%+ of a tweet's total reach. Tactics to win this window:

- Post when your audience is most active (not when convenient for you)
- "Warm up" before posting by spending 30 min replying to others (signals you're an active user)
- Have your core circle ready to engage early
- Craft hooks that stop the scroll and prompt immediate replies

### 2. External Links Are Penalized

Tweets with external links receive **30-50% fewer impressions**. The algorithm wants users to stay on X.

**Workaround**: Post your insight as a text/image tweet, then add the link in the first reply. Reference "link in reply" or use a bookmark-worthy format.

### 3. Consistency Rewards, Sudden Changes Punish

The algorithm learns your account-specific posting patterns. Sudden behavior changes (e.g., going from 2 tweets/day to 15, or going silent for a week) trigger spam detection and reduce reach.

- Maintain a consistent posting cadence
- Ramp up gradually when increasing frequency
- If you need to go offline, don't disappear entirely — schedule a few posts

### 4. SimClusters and Niche Specificity

X places every account into topic clusters (~145K clusters). Your content reaches people in overlapping clusters first. Staying focused on 2-3 related topics maximizes cluster alignment and reach.

**Anti-pattern**: Posting about random unrelated topics dilutes your cluster placement and confuses the algorithm about who to show your content to.

### 5. Sentiment Analysis

The algorithm runs sentiment analysis on content:

- **Positive, constructive content** gets wider distribution
- **Negative, hostile, or divisive content** is throttled
- Contrarian takes are fine — hostility is not

### 6. Dwell Time

How long users spend reading your content is a ranking signal. Longer-form content (threads, detailed tweets, image carousels) that holds attention gets rewarded.

Tactics to increase dwell time:
- Use line breaks and formatting for readability
- Include images or diagrams that require inspection
- Write threads where each tweet compels reading the next
- Provide enough depth that people pause to think

### 7. Video Gets Priority

Native video (uploaded directly to X) receives approximately **10x the distribution** of text-only posts. Long-form video (2+ minutes) performs best. External video links (YouTube, etc.) are penalized like any other external link.

---

## Algorithm Anti-Patterns

Things that **hurt** your reach:

| Anti-Pattern | Consequence |
|-------------|-------------|
| "Like if you agree" / forced engagement bait | Actively penalized since 2024 |
| Sudden posting frequency changes | Spam detection, reduced reach |
| Excessive external links | 30-50% fewer impressions per link tweet |
| Off-topic content (breaking niche) | Diluted SimCluster placement |
| Negative/hostile tone | Algorithmic throttling |
| Buying followers or engagement | Destroys SimCluster placement, fake accounts get pruned |
| Deleting and reposting tweets | Resets engagement, algorithm sees inconsistency |

---

## Practical Playbook

### Before Every Post

1. Check: is your audience awake and active right now?
2. Spend 15-30 min engaging with others first (warm up the algorithm)
3. Ensure no external links in the main tweet body
4. Craft a hook designed to generate replies, not just likes

### After Every Post

1. Stay active for 30-60 minutes after posting
2. Reply to every comment in the first hour (signals active conversation)
3. Don't post another tweet for 2-3 hours (let this one breathe)

### Weekly Algorithm Hygiene

1. Review which content types generate the most replies vs. likes
2. Double down on reply-generating formats
3. Check if any posts triggered negative signals (low impressions = possible throttle)
4. Ensure posting consistency (no big gaps or spikes)

---

*Algorithm Guide v1.0 — Based on X algorithm analysis and public documentation as of early 2026*
