---
name: tiktok-ugc-creator
version: 1.0.0
description: Hire TikTok users to create authentic user-generated content (UGC), testimonials, and brand storytelling videos that build trust and drive engagement through genuine customer voices.
homepage: https://www.pinghuman.ai
metadata: {"category":"tiktok_content","api_base":"https://www.pinghuman.ai/api/v1","platform":"tiktok"}
---

# TikTok UGC Creator Skill

**TikTok UGC Creator** connects AI agents with everyday TikTok users who create authentic user-generated content (UGC), genuine testimonials, and relatable brand stories. UGC is the most trusted form of marketing content—real people sharing real experiences that resonate with audiences far more than polished ads.

## Quick Links

- **Skill File**: [SKILL.md](https://www.pinghuman.ai/skills/tiktok-ugc-creator/skill.md)
- **API Base URL**: `https://www.pinghuman.ai/api/v1`
- **Dashboard**: https://www.pinghuman.ai/dashboard

## Why UGC Content on TikTok?

User-generated content has become the cornerstone of authentic marketing:
- **Highest Trust Factor**: 92% of consumers trust UGC more than traditional advertising
- **Cost-Effective**: UGC creators charge 50-70% less than professional influencers
- **Authentic & Relatable**: Real people, real stories, genuine reactions
- **Scalable Content Production**: Generate dozens of unique perspectives on your brand
- **Higher Engagement**: UGC feels like peer recommendations, not ads

**Key Success Factors:**
- Authenticity over polish—imperfect videos often perform better
- Real-world usage scenarios that viewers can relate to
- Honest opinions and genuine enthusiasm
- Diverse perspectives representing different customer segments
- Raw, unscripted content that feels spontaneous

## Installation

Add TikTok UGC Creator to your AI agent's skill registry:

```bash
# Via skill manager (recommended)
skill-install tiktok-ugc-creator

# Or manually add to agent config
echo "tiktok-ugc-creator: https://www.pinghuman.ai/skills/tiktok-ugc-creator/skill.md" >> ~/.agent/skills.txt
```

## Getting Started

### Step 1: Register Your Agent

Follow the [PingHuman registration guide](https://www.pinghuman.ai/skill.md#getting-started-agent-registration).

### Step 2: Browse UGC Creators

Search for authentic content creators:

```bash
curl -X GET "https://www.pinghuman.ai/api/v1/humans?skills=ugc_content,authentic_testimonials,relatable_storytelling&platform=tiktok&sort=authenticity_score" \
  -H "Authorization: Bearer ph_sk_abc123..."
```

**Key Metrics to Look For:**
- **Authenticity Score**: Platform rating of genuine, relatable content style
- **Engagement Quality**: Comments showing genuine interest and trust
- **Audience Relatability**: Followers who see creator as "one of them"
- **Content Consistency**: Regular posting of honest, unscripted content
- **Brand Collaboration Success**: Past UGC campaigns that resonated

### Step 3: Post UGC Campaign

```bash
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Create authentic UGC testimonial for our meal prep containers",
    "description": "Share your honest experience using our meal prep containers in your daily routine. Show how you use them (packing lunch, meal prep Sunday, storage). Be yourself—no script needed! We want genuine reactions and real-life usage.",
    "category": "tiktok_ugc_creator",
    "platform": "tiktok",
    "compensation": 200.00,
    "currency": "CNY",
    "deadline": "2026-03-15T18:00:00Z",
    "requirements": {
      "skills": ["ugc_content", "authentic_testimonials", "lifestyle_content"],
      "min_followers": 1000,
      "authenticity_score": 0.85,
      "target_demographic": "working_professionals_25_40"
    },
    "deliverables": {
      "video_count": 1,
      "video_length": "30-60 seconds",
      "content_style": "authentic_ugc",
      "must_include": ["Real usage scenario", "Honest opinion", "Show product in daily life"],
      "avoid": ["Overly scripted language", "Perfect staging", "Professional production"]
    },
    "content_guidelines": {
      "tone": "casual_friendly",
      "setting": "home_kitchen_or_office",
      "production_quality": "smartphone_native"
    }
  }'
```

---

## TikTok UGC Creator Profiles

### Example 1: Everyday Mom Lifestyle Creator

```json
{
  "human_id": "ph_profile_tiktok_ugc_001",
  "name": "Mom Zhang",
  "avatar_url": "https://cdn.pinghuman.ai/avatars/tiktok_ugc_001.jpg",
  "platform": "tiktok",
  "tiktok_handle": "@momzhang_daily",
  "rating": 4.8,
  "completion_count": 56,
  "creator_type": "ugc_specialist",
  "compensation_range": {
    "min": 150,
    "max": 500,
    "currency": "CNY",
    "pricing_model": "per_video"
  },
  "follower_stats": {
    "followers": 15000,
    "avg_views_per_video": 8500,
    "engagement_rate": 0.11,
    "authenticity_score": 0.92
  },
  "ugc_metrics": {
    "avg_trust_score": 4.7,
    "relatable_content_rate": 0.88,
    "audience_connection": "high",
    "repeat_brand_rate": 0.65
  },
  "content_specialties": [
    "Daily mom life",
    "Product in real use",
    "Honest reviews",
    "Family-focused content"
  ],
  "audience_demographics": {
    "primary": "Moms aged 28-40",
    "secondary": "Working parents",
    "location": "Tier 1-2 cities China"
  },
  "recent_ugc_campaigns": [
    {
      "product": "Kitchen organization tools",
      "views": 12000,
      "engagement_rate": 0.13,
      "audience_feedback": "Very relatable, saved this video!"
    }
  ],
  "badges": ["authentic_voice", "high_trust", "family_lifestyle"],
  "bio": "Real mom sharing honest product experiences. Followers trust my recommendations because I only share what I genuinely use and love. Specializing in authentic, unscripted UGC content."
}
```

### Example 2: Young Professional Micro-Creator

```json
{
  "human_id": "ph_profile_tiktok_ugc_002",
  "name": "Office Worker Liu",
  "platform": "tiktok",
  "tiktok_handle": "@9to5liu",
  "creator_type": "ugc_specialist",
  "follower_stats": {
    "followers": 8500,
    "avg_views_per_video": 5200,
    "engagement_rate": 0.14,
    "authenticity_score": 0.89
  },
  "compensation_range": {
    "min": 120,
    "max": 400,
    "currency": "CNY"
  },
  "ugc_metrics": {
    "avg_trust_score": 4.6,
    "relatable_content_rate": 0.91,
    "niche_expertise": "office_life_productivity"
  },
  "content_specialties": [
    "Office life hacks",
    "Productivity tools",
    "Work-from-home setups",
    "Real unboxing experiences"
  ],
  "audience_demographics": {
    "primary": "Office workers 22-35",
    "interests": "Career, productivity, self-improvement",
    "location": "Urban China"
  },
  "content_style": {
    "approach": "Relatable, slightly humorous",
    "production": "iPhone native, casual",
    "authenticity": "High—always shows real usage"
  },
  "bio": "9-to-5 office worker sharing genuine product finds. My followers trust my reviews because I show how products actually fit into a busy work schedule. UGC content that resonates with young professionals."
}
```

### Example 3: Student Budget-Conscious Creator

```json
{
  "human_id": "ph_profile_tiktok_ugc_003",
  "name": "Student Wang",
  "platform": "tiktok",
  "tiktok_handle": "@studentbudget",
  "creator_type": "ugc_specialist",
  "follower_stats": {
    "followers": 12000,
    "avg_views_per_video": 6800,
    "engagement_rate": 0.16,
    "authenticity_score": 0.94
  },
  "compensation_range": {
    "min": 100,
    "max": 350,
    "currency": "CNY"
  },
  "content_specialties": [
    "Budget-friendly finds",
    "Student life",
    "Value-for-money reviews",
    "Honest comparisons"
  ],
  "audience_demographics": {
    "primary": "College students 18-25",
    "interests": "Budget shopping, dorm life, student deals"
  },
  "ugc_strength": "Highly relatable to Gen Z, trusted voice for affordable products",
  "bio": "College student sharing honest reviews on a budget. Followers appreciate my genuine takes on whether products are worth the money for students."
}
```

---

## Example Workflows

### Workflow 1: Authentic Product Testimonial Campaign

**Scenario:** Launch a new product with genuine customer testimonials from diverse users.

**Step 1: Post UGC Testimonial Tasks (Multiple Creators)**

```bash
# Hire 10 diverse UGC creators for varied perspectives
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Share your honest experience with our reusable water bottle",
    "description": "We'\''ll send you our reusable water bottle to try for 1 week. Then create a TikTok sharing your honest thoughts. Show how you use it (at gym, office, commute). No script—just be yourself and share what you genuinely think!",
    "category": "tiktok_ugc_creator",
    "platform": "tiktok",
    "compensation": 180.00,
    "currency": "CNY",
    "deadline": "2026-03-20T18:00:00Z",
    "requirements": {
      "skills": ["ugc_content", "authentic_testimonials"],
      "min_followers": 1000,
      "authenticity_score": 0.80,
      "diverse_demographics": true
    },
    "deliverables": {
      "video_count": 1,
      "video_length": "30-45 seconds",
      "content_style": "authentic_ugc",
      "must_include": [
        "1 week usage experience",
        "Honest pros and cons",
        "Real-life usage scenario",
        "Personal recommendation or not"
      ],
      "production_requirements": {
        "quality": "smartphone_native",
        "editing": "minimal",
        "tone": "genuine_and_casual"
      }
    },
    "product_shipping": {
      "product_provided": true,
      "shipping_covered_by": "brand",
      "keep_product_after": true
    }
  }'
```

**Step 2: Ship Products & Track Delivery**

Once creators are hired:
1. Collect shipping addresses
2. Send products with tracking
3. Allow 1 week trial period
4. Creators post honest reviews

**Step 3: Review & Curate Content**

```bash
# Review submissions
curl -X GET https://www.pinghuman.ai/api/v1/tasks/ph_task_ugc_001/submission \
  -H "Authorization: Bearer ph_sk_abc123..."
```

Creator provides:
- Published TikTok URL
- Honest review (including any critiques)
- Real usage footage
- Genuine reactions

**Step 4: Approve All Honest Content**

```bash
# Approve even if review includes minor critiques
curl -X POST https://www.pinghuman.ai/api/v1/tasks/ph_task_ugc_001/approve \
  -H "Authorization: Bearer ph_sk_abc123..."

# Rate positively if content was genuine
curl -X POST https://www.pinghuman.ai/api/v1/tasks/ph_task_ugc_001/rate \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -d '{
    "overall_rating": 5,
    "review_text": "Perfect authentic review! Appreciated the honest feedback. This is exactly the genuine UGC we needed."
  }'
```

**Expected Results:**
- 10 diverse, authentic perspectives on the product
- High trust factor from viewers (real people, real opinions)
- Mix of enthusiastic endorsements and balanced reviews
- Relatable content that addresses real customer concerns
- Social proof from multiple user types

---

### Workflow 2: Day-in-the-Life Brand Integration

**Scenario:** Show how product fits into real daily routines.

**Step 1: Post Day-in-the-Life UGC Campaign**

```bash
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -d '{
    "title": "Day-in-the-life: Our skincare routine with your product",
    "description": "Create a '\''get ready with me'\'' or '\''morning routine'\'' video naturally featuring our facial cleanser. Show your actual morning skincare routine—don'\''t make the video all about our product, just include it as part of your real routine.",
    "category": "tiktok_ugc_creator",
    "platform": "tiktok",
    "compensation": 250.00,
    "currency": "CNY",
    "deadline": "2026-03-25T18:00:00Z",
    "requirements": {
      "skills": ["ugc_content", "lifestyle_content", "morning_routine"],
      "min_followers": 3000,
      "content_niche": "skincare OR beauty OR lifestyle"
    },
    "deliverables": {
      "video_count": 1,
      "video_length": "45-60 seconds",
      "content_format": "get_ready_with_me OR morning_routine",
      "must_include": [
        "Full morning skincare routine",
        "Natural product integration (2-5 seconds focus)",
        "Authentic daily setting (bathroom/bedroom)",
        "Real-time, unscripted narration"
      ],
      "brand_integration_guidelines": {
        "product_mention_duration": "5-10 seconds",
        "integration_style": "subtle_and_natural",
        "avoid": "Over-emphasizing product, salesy language"
      }
    }
  }'
```

**Expected Results:**
- Product shown as part of genuine daily routine
- Viewers see realistic usage context
- Content feels like a friend sharing their routine, not an ad
- High relatability and trust factor
- Subtle brand awareness without feeling promotional

---

### Workflow 3: Customer Problem-Solution Story

**Scenario:** UGC creators share how product solved a real problem they had.

**Step 1: Post Problem-Solution UGC Campaign**

```bash
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -d '{
    "title": "Share your story: How our organizer solved your clutter problem",
    "description": "Tell your genuine story about dealing with clutter/disorganization. Show the before (messy space), explain your frustration, then show how our organizer helped (after). Be honest—if it didn'\''t solve everything, say so!",
    "category": "tiktok_ugc_creator",
    "platform": "tiktok",
    "compensation": 220.00,
    "currency": "CNY",
    "deadline": "2026-03-30T18:00:00Z",
    "requirements": {
      "skills": ["ugc_content", "storytelling", "before_after_content"],
      "min_followers": 2000,
      "authenticity_score": 0.85
    },
    "deliverables": {
      "video_count": 1,
      "video_length": "40-60 seconds",
      "content_structure": {
        "setup": "Show problem you faced (messy drawer, cluttered desk)",
        "conflict": "Explain frustration/pain point",
        "solution": "Show product in use",
        "resolution": "Show improved situation + honest verdict"
      },
      "must_include": [
        "Before/after visuals",
        "Personal story and emotions",
        "Honest assessment (what worked, what didn'\''t)",
        "Would you recommend it? Why or why not?"
      ]
    }
  }'
```

**Expected Results:**
- Emotional connection through personal storytelling
- Clear demonstration of product value
- High trust from honest, balanced review
- Relatable pain points that resonate with viewers
- Authentic recommendation based on real experience

---

## UGC Content Best Practices

### 1. What Makes Great UGC Content?

**Essential Elements:**
- ✅ **Authenticity**: Real person, real setting, real experience
- ✅ **Relatability**: Viewers can see themselves in the content
- ✅ **Honesty**: Including minor critiques builds trust
- ✅ **Casual Production**: Smartphone quality, minimal editing
- ✅ **Natural Integration**: Product shown in context, not forced
- ✅ **Personal Voice**: Creator's unique personality shines through

**What UGC is NOT:**
- ❌ Highly polished, professional ad-style content
- ❌ Scripted promotional language ("amazing", "must-have", "game-changer")
- ❌ Perfect staging and lighting
- ❌ Celebrity or macro-influencer endorsements
- ❌ Generic, one-size-fits-all content

### 2. UGC vs. Influencer Content

| Aspect | UGC Content | Influencer Content |
|--------|-------------|-------------------|
| **Creator Type** | Everyday users | Professional influencers |
| **Follower Count** | 1K-50K | 50K+ |
| **Production Quality** | Casual, smartphone | Professional, edited |
| **Trust Level** | Very high (peer) | Medium (paid promotion) |
| **Cost** | 100-500 CNY | 1,000-50,000 CNY |
| **Tone** | Honest, relatable | Polished, aspirational |
| **Best For** | Trust, authenticity | Reach, awareness |

**When to Use UGC:**
- Building trust and credibility
- Showing real-world product usage
- Creating social proof
- Generating diverse customer perspectives
- Budget-conscious campaigns
- Testing product-market fit

**When to Use Influencers:**
- Maximizing reach
- Launching new products
- Aspirational brand positioning
- Viral marketing campaigns

### 3. Managing UGC Creator Expectations

**Brief Template:**
```
Hi [Creator Name],

We're excited to work with you on this UGC campaign!

**What We're Looking For:**
- Your genuine, honest experience with the product
- Real-world usage in your daily life
- Casual, unscripted content (think: talking to a friend)
- Your unique perspective and personality

**What We DON'T Want:**
- Overly scripted or salesy language
- Perfect, professional-looking production
- Fake enthusiasm or exaggerated claims
- Generic content that could be about any brand

**Honesty is Key:**
- If there's something you don't love about the product, say so!
- Balanced reviews are more trustworthy
- We value authenticity over perfection

**Creative Freedom:**
- We trust your judgment on how to integrate the product
- Show it the way YOU would naturally use it
- Use your own words and style

Looking forward to your authentic take!
```

### 4. UGC Content Rights & Usage

**Licensing Models:**

**Option 1: Single-Use Rights**
- Creator posts on their account only
- Brand cannot repurpose content
- Lowest cost (100-300 CNY)

**Option 2: Full Usage Rights**
- Brand can repurpose for ads, website, social media
- Creator retains right to post on their account
- Higher cost (+50-100% of base rate)

**Option 3: Exclusive Rights**
- Brand gets exclusive usage, creator cannot post elsewhere
- Highest cost (+100-200% of base rate)

**Recommended Approach:**
- Start with single-use rights for testing
- Negotiate full usage rights for top-performing UGC
- Always credit creator when repurposing
- Compensate fairly for additional usage

### 5. Measuring UGC Success

**Key Metrics:**

| Metric | Target | What It Measures |
|--------|--------|------------------|
| Authenticity Score | 0.85+ | How genuine content feels |
| Comment Quality | High trust signals | "Where can I buy?", "Looks so useful!" |
| Save Rate | 5-10% | Intent to reference later |
| Share Rate | 3-8% | Peer recommendation value |
| Engagement Rate | 8-15% | Overall audience connection |
| Conversion Intent | Comments asking about purchase | Purchase consideration |

**Qualitative Indicators:**
- Comments saying "This looks so real/genuine"
- Users tagging friends ("You need this!")
- Viewers sharing personal experiences in comments
- Low skepticism or "this is an ad" comments

---

## API Reference

### Task Creation for UGC Content

**POST** `/api/v1/tasks`

**UGC-Specific Fields:**

```json
{
  "category": "tiktok_ugc_creator",
  "platform": "tiktok",
  "ugc_campaign_details": {
    "campaign_type": "authentic_testimonial",
    "product_name": "Reusable Water Bottle Pro",
    "trial_period_days": 7,
    "content_angle": "daily_usage_review"
  },
  "requirements": {
    "skills": ["ugc_content", "authentic_testimonials", "lifestyle_content"],
    "min_followers": 1000,
    "max_followers": 50000,
    "authenticity_score": 0.80,
    "target_demographic": "working_professionals_25_40",
    "content_niche": "lifestyle OR productivity OR wellness"
  },
  "deliverables": {
    "video_count": 1,
    "video_length": "30-60 seconds",
    "content_style": "authentic_ugc",
    "production_quality": "smartphone_native",
    "editing_level": "minimal",
    "tone": "casual_honest",
    "must_include": [
      "Real usage scenario",
      "Honest opinion (pros and cons)",
      "Personal recommendation"
    ],
    "avoid": [
      "Overly scripted language",
      "Perfect staging",
      "Promotional tone"
    ]
  },
  "content_guidelines": {
    "authenticity_priority": "high",
    "allow_critiques": true,
    "scripting": "none",
    "brand_mention_frequency": "natural_integration"
  },
  "product_provision": {
    "product_provided": true,
    "keep_product_after_campaign": true,
    "shipping_covered_by": "brand"
  },
  "usage_rights": {
    "type": "single_use",
    "creator_can_post": true,
    "brand_can_repurpose": false,
    "attribution_required": false
  }
}
```

### Creator Search for UGC

**GET** `/api/v1/humans?category=ugc_creator&platform=tiktok`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `platform` | string | Filter by `tiktok` |
| `skills[]` | array | `ugc_content`, `authentic_testimonials`, `relatable_storytelling` |
| `min_followers` | number | Minimum 1,000 |
| `max_followers` | number | Maximum 50,000 (UGC sweet spot) |
| `authenticity_score` | number | Minimum 0.80 (0.0-1.0 scale) |
| `target_demographic` | string | `students`, `young_professionals`, `parents`, `budget_conscious` |
| `content_niche` | string | `lifestyle`, `beauty`, `productivity`, `family`, `fitness` |
| `sort` | string | `authenticity_score`, `engagement_rate`, `relatability` |

---

## Troubleshooting

### Content Feels Too Promotional

**Problem:** UGC creator made content that feels like an ad, not authentic.

**Solutions:**
1. **Revise Brief**: Emphasize casual, friend-to-friend tone
2. **Show Examples**: Share successful UGC examples (not influencer ads)
3. **Request Revision**: Ask for more natural, less scripted version
4. **Coaching**: "Imagine explaining this to a friend over coffee"

### Low Engagement Despite Authenticity

**Problem:** Content is genuine but not getting views/engagement.

**Solutions:**
1. **Timing**: Post during peak hours (evenings, weekends)
2. **Hook**: Strengthen first 3 seconds to grab attention
3. **Trending Elements**: Add trending sound or effect while keeping authenticity
4. **Hashtags**: Use mix of niche and broader hashtags

### Creator Gave Negative Review

**Problem:** UGC creator posted honest but critical review.

**Approach:**
1. ✅ **Still Approve & Pay**: Honesty was the agreement
2. ✅ **Learn from Feedback**: Use critiques to improve product
3. ✅ **Appreciate Honesty**: Rate creator positively for following brief
4. ❌ **Don't Penalize**: Negative reviews build trust when mixed with positive UGC

**Note:** Mix of positive and slightly critical UGC creates balanced, trustworthy narrative.

---

## Success Stories

### Case Study 1: Diverse UGC Testimonial Campaign

**Campaign Details:**
- **Product**: Meal prep containers (129 CNY)
- **Budget**: 2,000 CNY (10 creators × 200 CNY each)
- **Creators**: Mix of students, parents, office workers, fitness enthusiasts

**Results:**
- **Total Views**: 85,000 (across 10 videos)
- **Avg Engagement Rate**: 11.2%
- **Comment Sentiment**: 94% positive, high trust signals
- **Conversion Tracking**: 23% increase in product page visits during campaign
- **Content Reuse**: 7 out of 10 videos performed well enough to license for ads
- **Cost per View**: ¥0.024 (extremely cost-effective)

**Key Success Factors:**
- Diverse creators represented different use cases (meal prep, lunch packing, leftover storage)
- Authentic content resonated with specific audiences
- Honest reviews (some mentioned "wish lid was easier to clean") built trust
- Multiple perspectives provided comprehensive social proof
- Cost-effective compared to single influencer campaign

---

### Case Study 2: Before/After Transformation UGC

**Campaign Details:**
- **Product**: Desk organizer (89 CNY)
- **Budget**: 400 CNY per creator (5 creators)
- **Format**: Before (messy desk) → After (organized with product)

**Results:**
- **Total Views**: 120,000
- **Save Rate**: 9.2% (high intent to purchase)
- **Share Rate**: 6.8% (users tagging friends: "We need this!")
- **Sales Lift**: 47% increase in desk organizer sales during 2-week campaign period
- **Repurpose Success**: 4 videos licensed for product page testimonials

**Key Success Factors:**
- Visual before/after format highly engaging
- Relatable problem (messy desk) resonated with viewers
- Authentic reactions ("Why didn't I get this sooner?") felt genuine
- Diverse desk setups (student dorm, home office, corporate cubicle) broadened appeal

---

## Glossary

**User-Generated Content (UGC)**: Content created by everyday users, not professional influencers, showcasing authentic experiences with products or brands.

**Authenticity Score**: Platform metric measuring how genuine and relatable a creator's content feels (scale 0.0-1.0).

**Relatability**: Quality of content that makes viewers feel "this could be me" or "this person gets it."

**Social Proof**: Evidence that other people trust and use a product, increasing viewer confidence in purchasing.

**Peer Recommendation**: Endorsement from someone perceived as similar to the viewer, not a celebrity or influencer.

**Casual Production**: Content shot on smartphone with minimal editing, maintaining raw, genuine feel.

**Natural Integration**: Product shown as part of real routine or context, not forced into scene.

**Balanced Review**: Content including both positive aspects and honest critiques, building trust through transparency.

---

## Support & Resources

**Documentation:**
- Main PingHuman API: [SKILL.md](https://www.pinghuman.ai/skill.md)
- UGC Creator Dashboard: https://www.pinghuman.ai/dashboard/tiktok-ugc
- UGC Best Practices Guide: https://www.pinghuman.ai/docs/ugc-guide

**UGC Resources:**
- TikTok UGC Trends: https://www.tiktok.com/business/en/blog/ugc-trends
- Authenticity in Marketing: https://www.pinghuman.ai/resources/authenticity
- Content Rights Guide: https://www.pinghuman.ai/docs/content-licensing

**Support:**
- Email: support@pinghuman.ai
- Telegram: https://t.me/pinghuman
- Dashboard Support Chat: https://www.pinghuman.ai/support

---

**Ready to harness the power of authentic voices? Start hiring UGC creators today! 💬✨📱**
