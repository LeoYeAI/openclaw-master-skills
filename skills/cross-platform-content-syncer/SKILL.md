---
name: cross-platform-content-syncer
description: "Publish content once, distribute everywhere—sync WordPress, Substack, Medium, and LinkedIn automatically. Use when the user needs multi-channel publishing, content distribution, or unified editorial workflows."
version: 1.0.0
homepage: https://github.com/ncreighton/empire-skills
metadata:
  {
    "openclaw": {
      "requires": {
        "env": [
          "WORDPRESS_API_KEY",
          "WORDPRESS_SITE_URL",
          "SUBSTACK_API_KEY",
          "MEDIUM_API_TOKEN",
          "LINKEDIN_ACCESS_TOKEN",
          "SLACK_WEBHOOK_URL"
        ],
        "bins": ["curl", "jq"]
      },
      "os": ["macos", "linux", "win32"],
      "files": ["SKILL.md"],
      "emoji": "🔄"
    }
  }
---

## Overview

The **Cross-Platform Content Syncer** eliminates manual republishing across your content ecosystem. Write once in your primary platform (WordPress, Substack, Medium, or LinkedIn), and automatically sync to all others with intelligent formatting, SEO optimization, and platform-specific metadata.

This skill is built for:
- **Content creators** managing multiple audiences across platforms
- **Marketing teams** distributing thought leadership at scale
- **Newsletter publishers** expanding reach without duplicate work
- **B2B companies** maintaining consistent messaging across channels

### Why It Matters

Content distribution typically requires 4-5 manual steps per platform (copy, reformat, add metadata, preview, publish). This skill automates that workflow, saving 30-45 minutes per article while ensuring consistency and SEO best practices.

**Supported Integrations:**
- WordPress (REST API v2)
- Substack (Email + Web)
- Medium (Partner Program API)
- LinkedIn (Content Distribution API)
- Slack (notifications)
- Google Drive (backup)

---

## Quick Start

Try these prompts immediately:

### Example 1: Sync a WordPress post to all platforms
```
Sync my latest WordPress article "10 AI Tools for Content Creators" to Substack, 
Medium, and LinkedIn. Add LinkedIn hashtags, optimize for Medium's audience, 
and notify me on Slack when complete.
```

### Example 2: Schedule content across platforms with delays
```
I have a blog post ready. Publish to Substack first (immediately), then Medium 
(24 hours later), then LinkedIn (48 hours later). Add platform-specific CTAs 
and track engagement metrics.
```

### Example 3: Batch sync multiple articles
```
Sync my last 5 published WordPress articles to Medium. Skip articles published 
before January 2024. Preserve all images, add author bio, and create a Google 
Sheet tracking which articles synced where.
```

### Example 4: Sync with content transformation
```
Take my Substack newsletter draft, convert it to a LinkedIn article (add 
professional formatting), a Medium post (add SEO keywords), and a WordPress 
blog post (add related posts). Include platform-specific metadata.
```

---

## Capabilities

### 1. **Multi-Platform Publishing**
- **WordPress**: Direct REST API publishing with featured images, categories, tags, and SEO metadata
- **Substack**: Email distribution + web archive with subscriber list segmentation
- **Medium**: Partner program publishing with canonical URLs and publication selection
- **LinkedIn**: Article publishing with formatting, hashtags, and engagement tracking

### 2. **Intelligent Content Transformation**
- Auto-convert formatting (Markdown → HTML → Platform-specific)
- Preserve and optimize images across platforms
- Generate platform-specific headlines and descriptions
- Add platform-appropriate CTAs (Subscribe, Follow, Read More)
- Maintain internal link structure with redirects

### 3. **SEO & Metadata Management**
- Auto-generate meta descriptions for each platform
- Add relevant hashtags (#content, #marketing, #ai)
- Create canonical URLs to prevent duplicate content penalties
- Optimize keyword density per platform algorithm
- Generate Open Graph tags for social sharing

### 4. **Scheduling & Workflow**
- Publish immediately or schedule for specific dates/times
- Stagger publication across platforms (e.g., 24-48 hour delays)
- Create content calendars visible in Slack
- Queue management with priority levels
- Automatic retry on failed syncs (with exponential backoff)

### 5. **Analytics & Tracking**
- Track views, engagement, and clicks per platform
- Generate weekly performance reports
- Identify top-performing platforms for your content
- Monitor comment/response threads across platforms
- Export metrics to Google Sheets or Data Studio

### 6. **Content Backup & Version Control**
- Auto-backup all synced content to Google Drive
- Maintain version history (rollback capability)
- Archive original + synced versions
- Compare formatting across platforms

---

## Configuration

### Required Environment Variables

Set these in your `.env` file or ClawHub secrets:

```bash
# WordPress
WORDPRESS_SITE_URL="https://yourblog.com"
WORDPRESS_API_KEY="your-application-password"

# Substack
SUBSTACK_API_KEY="sk_live_xxxxxxxxxxxx"

# Medium
MEDIUM_API_TOKEN="your-medium-integration-token"

# LinkedIn
LINKEDIN_ACCESS_TOKEN="your-oauth-access-token"
LINKEDIN_ORGANIZATION_ID="12345678"

# Slack (optional, for notifications)
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Google Drive (optional, for backups)
GOOGLE_DRIVE_FOLDER_ID="your-folder-id"
GOOGLE_SERVICE_ACCOUNT_JSON="path/to/service-account.json"
```

### Configuration Options

```yaml
sync_config:
  source_platform: "wordpress"  # wordpress, substack, medium, linkedin
  target_platforms: ["substack", "medium", "linkedin"]
  
  # Scheduling
  publish_immediately: false
  schedule_delays:
    substack: 0  # hours
    medium: 24
    linkedin: 48
  
  # Content transformation
  preserve_formatting: true
  add_platform_ctc: true
  generate_seo_metadata: true
  
  # Notifications
  notify_slack: true
  notify_email: "your@email.com"
  
  # Analytics
  track_engagement: true
  report_frequency: "weekly"
```

---

## Example Outputs

### Output 1: Sync Confirmation
```
✅ Cross-Platform Sync Complete

Article: "10 AI Tools for Content Creators"
Source: WordPress (ID: 1247)
Synced: 3/3 platforms

Platform         Status    URL                              Published
─────────────────────────────────────────────────────────────────────
Substack         ✓         substack.com/@yourname/ai-tools 2024-01-15
Medium           ✓         medium.com/@yourname/ai-tools   2024-01-16
LinkedIn         ✓         linkedin.com/feed/update/...    2024-01-17

Next Steps:
→ View analytics dashboard: https://clawhub.app/sync/1247
→ Share LinkedIn post: https://linkedin.com/feed/update/...
→ Check Slack for engagement updates
```

### Output 2: Weekly Engagement Report
```
📊 Weekly Content Performance (Jan 8-14, 2024)

Top Performer: "AI Tools" article
├─ WordPress: 3,240 views | 127 comments
├─ Medium: 1,850 views | 43 claps
├─ LinkedIn: 4,120 impressions | 89 reactions
└─ Substack: 2,310 opens | 340 clicks

Platform Insights:
• LinkedIn: Best for B2B thought leadership (+15% engagement vs. last week)
• Medium: Growing audience in tech category (+8% followers)
• Substack: Highest click-through rate (14.7%)

Recommendations:
→ Increase LinkedIn publishing frequency (2x/week)
→ Add more technical depth for Medium audience
→ Segment Substack content by subscriber interest
```

### Output 3: Content Transformation Example
```
Original WordPress Post:
─────────────────────────
Title: "10 AI Tools for Content Creators"
Length: 2,100 words
Images: 5
Format: Blog post with sections and code blocks

Transformed for Medium:
─────────────────────────
Title: "10 AI Tools That Changed How I Create Content" (optimized for engagement)
Length: 2,050 words (trimmed for Medium's preferred length)
Images: 5 (auto-optimized for mobile)
Format: Article with pull quotes and highlighted sections
Canonical URL: https://yourblog.com/ai-tools

Transformed for LinkedIn:
─────────────────────────
Title: "10 AI Tools Every Content Creator Should Know in 2024" (keyword-optimized)
Length: 850 words (summarized for LinkedIn)
Images: 3 (best-performing visuals)
Format: Article with professional formatting
Hashtags: #AI #ContentCreation #ProductivityTools #MarketingTech
CTA: "What's your favorite AI tool? Drop it in the comments."

Transformed for Substack:
─────────────────────────
Title: "10 AI Tools I'm Using This Month (+ Free Alternatives)" (curiosity-driven)
Length: 2,100 words (full version for email)
Images: 5 (full resolution for email clients)
Format: Newsletter with personal narrative
CTA: "Share this with a creator friend who needs this."
```

---

## Tips & Best Practices

### 1. **Choose the Right Source Platform**
- **WordPress**: Best for long-form, SEO-focused content
- **Substack**: Best for newsletter-first audiences
- **Medium**: Best for technical/niche content
- **LinkedIn**: Best for industry insights and thought leadership

**Pro tip**: Use WordPress as your primary source—it has the most flexibility and SEO power.

### 2. **Optimize for Each Platform's Algorithm**
- **LinkedIn**: Use 3-5 industry hashtags, ask engagement questions, publish Tuesday-Thursday 8am-10am
- **Medium**: Add 5-7 topic tags, use compelling first paragraph, aim for 1,500-2,000 words
- **Substack**: Personalize subject lines, include one clear CTA, send at consistent day/time
- **WordPress**: Use target keywords in title and first 100 words, add internal links, optimize images

### 3. **Stagger Publication Timing**
Don't publish to all platforms simultaneously. Stagger by 24-48 hours:
- Day 1: WordPress (primary, builds SEO authority)
- Day 2: Substack (builds email subscriber engagement)
- Day 3: Medium (captures search traffic)
- Day 4: LinkedIn (maximizes professional reach)

This prevents algorithmic penalties for duplicate content and maximizes visibility across platforms.

### 4. **Use Platform-Specific CTAs**
- **WordPress**: "Subscribe to my newsletter" (convert to email list)
- **Substack**: "Share this with a colleague" (grow subscriber base)
- **Medium**: "Follow for more insights" (build Medium following)
- **LinkedIn**: "What's your take?" (drive engagement)

### 5. **Monitor Platform-Specific Metrics**
Track what matters on each platform:
- WordPress: Traffic, bounce rate, time on page, conversions
- Substack: Open rate, click rate, subscriber growth
- Medium: Claps, reading time, follower growth
- LinkedIn: Impressions, engagement rate, profile visits

### 6. **Batch Your Content**
Sync content in batches (weekly or monthly) rather than one-off articles. This reduces API calls, improves efficiency, and allows for better scheduling.

### 7. **Maintain Canonical URLs**
Always set WordPress as the canonical source. This tells search engines which version is the "original," preserving SEO value.

---

## Safety & Guardrails

### What This Skill Will NOT Do

- **No unauthorized republishing**: Requires explicit user confirmation before syncing
- **No plagiarism**: Does not copy content from other creators without attribution
- **No spam distribution**: Respects platform ToS (no artificial engagement boosting)
- **No data scraping**: Does not collect reader data beyond what platforms provide via API
- **No content modification without consent**: Preserves original message (only formats for platform)
- **No cross-posting without canonical URLs**: Always maintains canonical source to avoid SEO penalties

### Limitations & Boundaries

1. **Platform API Rate Limits**
   - WordPress: 10 requests/second
   - Substack: 100 requests/hour
   - Medium: 50 requests/hour
   - LinkedIn: 100 requests/day
   - Skill will queue excess requests and retry automatically

2. **Content Type Restrictions**
   - Video content: Links only (platforms don't support direct video uploads via API)
   - Paywalled content: Cannot sync to free platforms (respects Medium's Partner Program rules)
   - Sensitive content: Requires manual review before syncing

3. **Image Handling**
   - Max 50MB per image
   - Supported formats: JPG, PNG, WebP, GIF
   - Skill auto-optimizes for each platform's requirements

4. **Authentication**
   - Tokens expire and must be refreshed manually (set calendar reminders)
   - Multi-factor authentication required for all platforms
   - API keys stored in encrypted vault (never logged or exposed)

5. **Content Approval**
   - Drafts must be explicitly published (no auto-publish from drafts)
   - Scheduled content requires 15-minute review window before publish
   - Bulk syncs limited to 50 articles per batch

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: "Authentication Failed - Invalid Token"
**Cause**: API token expired or incorrect credentials
**Solution**:
1. Verify token in ClawHub secrets dashboard
2. Regenerate token on the platform (Settings → API/Integrations)
3. Update WORDPRESS_API_KEY, MEDIUM_API_TOKEN, etc. in `.env`
4. Test connection: `curl -H "Authorization: Bearer YOUR_TOKEN" https://api.platform.com/me`
5. Retry sync

#### Issue 2: "Rate Limit Exceeded"
**Cause**: Too many requests to platform API
**Solution**:
1. Skill automatically queues requests—no action needed for single articles
2. For bulk syncs: Reduce batch size from 50 to 25 articles
3. Increase delay between platform syncs (e.g., 48-72 hours instead of 24)
4. Check platform API status: `https://status.medium.com`, `https://status.substack.com`

#### Issue 3: "Images Not Syncing"
**Cause**: Image URL broken, unsupported format, or file size exceeds limit
**Solution**:
1. Verify image URLs are publicly accessible (not behind login)
2. Check image format (JPG, PNG, WebP, GIF only)
3. Compress images if >5MB: Use `ImageOptim` (Mac) or `TinyPNG` (web)
4. Re-upload images to WordPress and retry sync
5. View sync logs: `clawhub logs cross-platform-content-syncer --tail 50`

#### Issue 4: "Formatting Broken on Medium/LinkedIn"
**Cause**: HTML conversion error or unsupported formatting
**Solution**:
1. Check source content for complex HTML (tables, nested lists, iframes)
2. Simplify formatting: Use bold/italic only, avoid custom CSS
3. Test sync with simpler article first
4. Enable "preserve_formatting: false" to auto-clean HTML
5. Contact support with screenshot: `support@clawhub.app`

#### Issue 5: "Slack Notifications Not Arriving"
**Cause**: Invalid webhook URL or Slack workspace permissions
**Solution**:
1. Verify SLACK_WEBHOOK_URL in `.env` (should start with `https://hooks.slack.com`)
2. Check Slack app permissions: Settings → Manage Apps → ClawHub → Permissions
3. Test webhook manually:
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test message"}' \
     YOUR_WEBHOOK_URL
   ```
4. Regenerate webhook if needed: Slack → Integrations → Incoming Webhooks
5. Verify notify_slack: true in config

### FAQ

**Q: Can I sync to only some platforms, not all?**
A: Yes. In config, set `target_platforms: ["medium", "linkedin"]` to sync only to those.

**Q: What happens if one platform fails—do the others still sync?**
A: Yes. Skill syncs to each platform independently. If Medium fails, WordPress/Substack/LinkedIn still publish. Retry failed platforms automatically after