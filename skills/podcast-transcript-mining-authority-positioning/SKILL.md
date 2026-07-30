---
name: podcast-transcript-mining-authority-positioning
description: "Extract guest appearances, speaking topics, and soundbites from podcast transcripts to build authority portfolios and generate podcast pitch templates. Use when the user needs to identify speaking opportunities, repurpose content, or position themselves as thought leaders."
version: 1.0.0
homepage: https://github.com/ncreighton/empire-skills
metadata:
  {"openclaw":{"requires":{"env":["OPENAI_API_KEY","GOOGLE_SEARCH_API_KEY","SLACK_WEBHOOK_URL"],"bins":["ffmpeg"]},"os":["macos","linux","win32"],"files":["SKILL.md"],"emoji":"🎙️"}}
---

# Podcast Transcript Mining & Authority Positioning

## Overview

This advanced content intelligence skill transforms raw podcast transcripts into strategic assets for thought leadership positioning. Whether you're a solopreneur, consultant, or agency, this skill automatically:

- **Extracts guest appearances** from uploaded transcripts or RSS feeds
- **Identifies speaking topics** and expertise areas mentioned in conversations
- **Harvests quote-worthy soundbites** for social media and content repurposing
- **Maps target audiences** by analyzing which podcasts your ideal customers listen to
- **Generates guest appearance portfolios** showcasing your media presence
- **Creates personalized podcast pitch templates** for outreach campaigns
- **Tracks competitor appearances** to identify untapped speaking opportunities

The skill integrates with **Slack** for notifications, **Google Search** for podcast discovery, **WordPress** for blog syndication of guest posts, and **Zapier** for workflow automation. It uses OpenAI's GPT-4 for semantic analysis and natural language extraction, ensuring intelligent identification of context-relevant content rather than simple keyword matching.

**Why this matters:** Manual transcript review takes 2-4 hours per episode. This skill processes an entire podcast season in minutes, surfacing your best moments and identifying 10-15 qualified podcast outreach targets automatically.

---

## Quick Start

### Example 1: Extract Soundbites from a Single Transcript
```
Upload my podcast transcript (PDF or text file) and extract the 5 most 
quote-worthy moments about digital marketing strategy. Format them as 
social media posts (280 characters) and LinkedIn posts (1,300 characters).
```

### Example 2: Build a Guest Appearance Portfolio
```
I've appeared on 8 podcasts in the last 6 months. Here are the transcript 
links: [list]. Create a professional guest appearance portfolio page in 
Markdown format that I can add to my website. Include episode titles, 
hosts, key topics discussed, and a 2-sentence bio for each appearance.
```

### Example 3: Generate Podcast Pitch Templates
```
Analyze these 3 competitor transcripts and identify 15 podcasts in the 
"B2B SaaS" and "Startup Founder" categories that would be perfect for me 
as a guest. For each podcast, generate a personalized 150-word pitch email 
that references something the host said in a recent episode.
```

### Example 4: Discover Untapped Speaking Opportunities
```
Search for podcasts in my niche (executive coaching, tech founders) that 
have 50K-500K monthly listeners. Identify which ones have never had a guest 
with my background (10+ years in tech, 5 exits). Create a prioritized list 
with contact information and suggested episode angles.
```

### Example 5: Repurpose Content Across Channels
```
Extract all key insights from this podcast transcript and generate:
- 10 LinkedIn carousel slide ideas
- 1 blog post outline (1,500 words)
- 5 Twitter threads (5 tweets each)
- 3 TikTok/Shorts scripts (60 seconds)
- 1 email newsletter edition
```

---

## Capabilities

### 1. Transcript Ingestion & Processing
- **Supported formats:** MP3/WAV audio files (auto-transcribed via Whisper API), PDF transcripts, plain text, Google Docs links, Notion databases
- **Batch processing:** Upload up to 50 transcripts simultaneously
- **RSS feed integration:** Automatically pull and process new episodes from podcast RSS feeds (Apple Podcasts, Spotify, Anchor, Buzzsprout)
- **Speaker identification:** Automatically detect and label host vs. guest speech patterns
- **Timestamp preservation:** Maintain accurate timestamps for easy audio reference

### 2. Soundbite Extraction Engine
- **Semantic analysis:** Uses GPT-4 to identify contextually relevant, quote-worthy moments (not just keyword matches)
- **Customizable extraction criteria:** Extract by topic, sentiment, length, or expertise area
- **Multi-format output:** Social posts, LinkedIn content, email subject lines, blog pull-quotes
- **Source attribution:** Automatically includes episode title, host name, publication date, and audio timestamp
- **Sentiment scoring:** Flag emotional moments (laughs, surprising revelations, passionate declarations) for maximum engagement

### 3. Authority Portfolio Builder
- **Automated portfolio generation:** Creates professional guest appearance pages with:
  - Episode metadata (title, host, publish date, listener count)
  - Topic summaries (auto-generated or custom)
  - Key quotes and moments
  - Episode links and call-to-action buttons
  - Professional headshots and bios
- **Export formats:** HTML, Markdown, WordPress shortcodes, JSON
- **Integration:** Push directly to WordPress sites via REST API
- **Analytics-ready:** Include UTM parameters for tracking guest appearance traffic

### 4. Podcast Pitch Generation
- **Personalized templates:** AI-generated pitch emails that reference specific host episodes or recent news
- **Competitor analysis:** Identify gaps where similar guests haven't appeared
- **Subject line A/B variants:** Generate 3 subject line options with predicted open rates
- **Follow-up sequences:** Auto-generate 3-email follow-up templates (7-day, 14-day, 30-day)
- **Bulk outreach prep:** Export all pitches to CSV for email automation tools (Lemlist, Outreach, Mailchimp)

### 5. Audience Intelligence
- **Listener demographic mapping:** Analyze podcast descriptions and guest bios to infer audience composition
- **Niche alignment scoring:** Rate podcasts 1-10 for fit with your target audience
- **Growth tracking:** Monitor listener count trends over time
- **Competitor appearance tracking:** See which podcasts have hosted your competitors
- **Seasonal patterns:** Identify which topics are trending in your industry

### 6. Content Repurposing Automation
- **Multi-channel output:** Generate content tailored for:
  - LinkedIn (carousel slides, articles, native videos)
  - Twitter/X (threads, quote tweets, engagement hooks)
  - TikTok/Reels/Shorts (script outlines with timing)
  - Email newsletters (curated insights, call-to-action variants)
  - Blog posts (long-form articles with SEO optimization)
  - Slack updates (notifications for team members)
- **Brand voice consistency:** Maintain tone and style across all outputs
- **SEO optimization:** Auto-generate meta descriptions, H1/H2 tags, keyword suggestions

---

## Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=sk-...                    # GPT-4 access for semantic analysis
GOOGLE_SEARCH_API_KEY=AIza...            # Podcast discovery and research
SLACK_WEBHOOK_URL=https://hooks.slack... # Notifications and team updates
WHISPER_API_KEY=sk-...                   # Audio transcription (optional, for MP3s)
WORDPRESS_API_KEY=...                    # WordPress integration (optional)
WORDPRESS_SITE_URL=https://yoursite.com  # Your WordPress domain
```

### Optional Configuration
```yaml
# config.yml
extraction:
  min_quote_length: 15  # Minimum words for soundbite
  max_quote_length: 280 # Maximum words for social posts
  sentiment_threshold: 0.7 # 0-1 scale for emotional moments
  
podcast_discovery:
  listener_min: 10000   # Minimum monthly listeners
  listener_max: 1000000 # Maximum monthly listeners
  language: "en"
  
output_formats:
  - linkedin_carousel
  - twitter_thread
  - blog_post
  - email_newsletter
  - slack_message
  
repurposing:
  blog_word_count: 1500
  email_subject_variants: 3
  twitter_thread_length: 5
  tiktok_duration: 60
```

### Setup Instructions

**Step 1: Connect Your Data Sources**
```bash
# Link your podcast RSS feeds
openclaw podcast-mining add-feed https://feeds.example.com/podcast.xml

# Or upload transcripts directly
openclaw podcast-mining upload ./transcripts/
```

**Step 2: Configure Slack Notifications**
```bash
# Get your Slack webhook URL from Slack App settings
# Paste into SLACK_WEBHOOK_URL environment variable
# Test connection:
openclaw podcast-mining test-slack
```

**Step 3: Set Up WordPress Integration (Optional)**
```bash
# Generate WordPress API token in Settings > REST API
openclaw podcast-mining configure-wordpress \
  --site-url https://yoursite.com \
  --api-key YOUR_KEY
```

**Step 4: Customize Extraction Preferences**
```bash
# Edit extraction rules for your niche
openclaw podcast-mining configure \
  --min-quote-length 20 \
  --sentiment-threshold 0.8 \
  --output-formats linkedin_carousel,blog_post
```

---

## Example Outputs

### Output 1: Extracted Soundbites (JSON)
```json
{
  "episode": {
    "title": "From Zero to $10M ARR: Scaling Your SaaS",
    "host": "Sarah Chen",
    "podcast": "The Founder's Journey",
    "publish_date": "2024-01-15",
    "listener_count": 125000,
    "episode_url": "https://example.com/episode-42"
  },
  "soundbites": [
    {
      "quote": "The biggest mistake founders make is optimizing for growth before optimizing for retention. You can't scale a leaky bucket.",
      "timestamp": "18:42",
      "sentiment": 0.92,
      "category": "business_strategy",
      "social_post_280": "The biggest mistake founders make is optimizing for growth before optimizing for retention. You can't scale a leaky bucket. - [Your Name] on The Founder's Journey",
      "linkedin_post": "\"The biggest mistake founders make is optimizing for growth before optimizing for retention. You can't scale a leaky bucket.\"\n\nThis insight from my recent appearance on The Founder's Journey resonates deeply with my experience scaling [Company]. Here's why retention should come first...",
      "blog_pullquote": "The biggest mistake founders make is optimizing for growth before optimizing for retention. You can't scale a leaky bucket."
    }
  ]
}
```

### Output 2: Guest Appearance Portfolio (HTML)
```html
<div class="guest-appearances">
  <h2>Featured Guest Appearances</h2>
  
  <div class="appearance-card">
    <h3>From Zero to $10M ARR: Scaling Your SaaS</h3>
    <p class="podcast-info">
      <strong>Podcast:</strong> The Founder's Journey<br>
      <strong>Host:</strong> Sarah Chen<br>
      <strong>Date:</strong> January 15, 2024<br>
      <strong>Listeners:</strong> 125K/month
    </p>
    <p class="topics">
      <strong>Topics:</strong> SaaS Scaling, Retention Strategy, Founder Mindset
    </p>
    <blockquote>
      "The biggest mistake founders make is optimizing for growth before 
      optimizing for retention."
    </blockquote>
    <a href="[episode-url]" class="listen-btn">Listen Now</a>
  </div>
</div>
```

### Output 3: Podcast Pitch Template
```markdown
Subject: Guest idea: [Your Name] on scaling SaaS retention (The Founder's Journey listener here!)

Hi Sarah,

I've been a long-time listener of The Founder's Journey—your recent episode 
with [Previous Guest] on founder burnout really hit home. I've faced similar 
challenges scaling [Your Company] from $0 to $5M ARR.

I'd love to be a guest and dive into a topic your audience clearly cares about: 
**How to prioritize retention over growth when you're under pressure to scale.**

In my experience:
- Most founders optimize for growth metrics first (which is backwards)
- A 5% improvement in retention compounds to 50%+ revenue impact
- This shift in mindset saved us $2M in acquisition costs

I think your listeners would find this perspective valuable, especially founders 
in the 6-12 month growth stage.

Would you be open to a 45-minute conversation? I'm flexible on timing.

Best,
[Your Name]
[Your Title]
[Your Website]
```

### Output 4: Content Repurposing Bundle (LinkedIn Carousel)
```markdown
# LinkedIn Carousel: "5 Lessons from 8 Podcast Guest Appearances"

Slide 1: "I've appeared on 8 podcasts in 6 months. Here are the 5 biggest 
lessons that surprised me about audience building, positioning, and growth."

Slide 2: "Lesson 1: Your best content isn't what you think it is. The moments 
that got the most engagement were unscripted, vulnerable, and messy—not polished 
talking points."

Slide 3: "Lesson 2: Podcast listeners are HUNGRY for specific, tactical advice. 
Generic frameworks don't work. They want the exact playbook you used."

Slide 4: "Lesson 3: Host chemistry matters more than topic. The best episodes 
were with hosts who challenged me, asked follow-ups, and weren't afraid to 
disagree."

Slide 5: "Lesson 4: Repurposing is non-negotiable. One 45-min episode generated 
12 pieces of content, 50K+ impressions, and 3 qualified leads."

Slide 6: "Lesson 5: Guest appearances compound. Each appearance makes the next 
one easier. Hosts see your previous appearances and trust you more."
```

---

## Tips & Best Practices

### 1. Optimize for Soundbite Quality
- **Focus on specificity:** Extract quotes that include numbers, frameworks, or surprising insights
- **Avoid generic wisdom:** "Success takes hard work" won't perform. "We grew 300% by cutting our feature set in half" will
- **Timestamp everything:** Include the exact moment in the podcast so listeners can jump to that section
- **Test on your audience:** Share extracted soundbites with your email list to see which resonate most

### 2. Build a Strategic Podcast List
- **Start with 50 target podcasts:** Use this skill to identify 50 podcasts with 10K-500K monthly listeners in your niche
- **Tier by difficulty:** Separate "easy wins" (small, growing podcasts) from "stretch goals" (top-tier shows)
- **Track competitor appearances:** See which shows have hosted your competitors and prioritize those
- **Monitor growth trends:** Focus on podcasts with 20%+ monthly growth (you'll reach a bigger audience in 6 months)

### 3. Personalize Every Pitch
- **Reference a specific episode:** "I loved your episode on [Topic] with [Guest]" performs 5x better than generic pitches
- **Mention a specific quote:** "You mentioned that [quote]—I have a framework that builds on that idea"
- **Show you're a real listener:** Mention a recent episode, not one from 2 years ago
- **Lead with their audience, not your credentials:** "Your listeners are asking about X, and I have specific answers"

### 4. Repurpose Strategically
- **Create a content calendar:** Map one podcast appearance to 12+ pieces of content across channels
- **Batch record:** Record your TikTok/Reel scripts all at once after the podcast episode airs
- **Sequence your promotion:** Release blog post first (SEO), then LinkedIn carousel, then Twitter thread, then email
- **Tag the host:** Always mention the host and podcast in your repurposed content (they'll often amplify it)

### 5. Measure What Matters
- **Track traffic from guest appearances:** Use UTM parameters to measure podcast-sourced visitors
- **Monitor lead quality:** Are podcast listeners higher-quality leads than other sources?
- **Measure brand lift:** Track Google search volume for your name after major appearances
- **Calculate ROI:** One guest appearance = 40 hours of sales conversations? That's worth $5K-10K in value

### 6. Scale Your Outreach
- **Use automation tools:** Export pitch templates to Lemlist or Outreach for automated follow-ups
- **Batch your pitching:**