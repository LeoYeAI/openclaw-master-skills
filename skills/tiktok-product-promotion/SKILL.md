---
name: tiktok-product-promotion
version: 1.0.0
description: Hire TikTok influencers for product reviews, demonstrations, unboxing videos, and conversion-focused promotional content to drive sales and measurable ROI.
homepage: https://www.pinghuman.ai
metadata: {"category":"tiktok_ecommerce","api_base":"https://www.pinghuman.ai/api/v1","platform":"tiktok"}
---

# TikTok Product Promotion Skill

**TikTok Product Promotion** connects AI agents with TikTok influencers who specialize in product reviews, demonstrations, unboxing content, and conversion-driven promotional campaigns. From affiliate marketing to direct product sales, this skill helps you access creators who can turn TikTok views into measurable business results.

## Quick Links

- **Skill File**: [SKILL.md](https://www.pinghuman.ai/skills/tiktok-product-promotion/skill.md)
- **API Base URL**: `https://www.pinghuman.ai/api/v1`
- **Dashboard**: https://www.pinghuman.ai/dashboard

## Why Product Promotion on TikTok?

TikTok has evolved into a powerful e-commerce platform where product recommendations drive real purchasing decisions:
- **High Conversion Rates**: Users trust authentic creator recommendations over traditional ads
- **Shoppable Content**: TikTok Shop integration enables direct in-app purchasing
- **Discovery Shopping**: Users discover and buy products they didn't know they needed
- **Gen Z & Millennial Buyers**: Demographic with high purchasing power and social commerce adoption
- **Measurable ROI**: Track views, clicks, conversions, and revenue directly

**Key Success Factors:**
- Authentic product demonstrations that feel helpful, not salesy
- Clear call-to-action with trackable affiliate links or promo codes
- High-quality visuals showcasing product features and benefits
- Creator's genuine enthusiasm and credibility in product category
- Strategic use of TikTok Shop features and link-in-bio conversions

## Installation

Add TikTok Product Promotion to your AI agent's skill registry:

```bash
# Via skill manager (recommended)
skill-install tiktok-product-promotion

# Or manually add to agent config
echo "tiktok-product-promotion: https://www.pinghuman.ai/skills/tiktok-product-promotion/skill.md" >> ~/.agent/skills.txt
```

## Getting Started

### Step 1: Register Your Agent

Follow the [PingHuman registration guide](https://www.pinghuman.ai/skill.md#getting-started-agent-registration).

### Step 2: Browse Product Promotion Creators

Search for influencers with proven conversion track records:

```bash
curl -X GET "https://www.pinghuman.ai/api/v1/humans?skills=product_review,demonstration,affiliate_marketing&platform=tiktok&sort=conversion_rate" \
  -H "Authorization: Bearer ph_sk_abc123..."
```

**Key Metrics to Look For:**
- **Conversion Rate**: % of viewers who click links or use promo codes
- **Average Sales per Video**: Revenue generated per promotional post
- **Product Niche Expertise**: Beauty, tech, fashion, home goods, etc.
- **Audience Purchasing Power**: Demographics with buying intent
- **TikTok Shop Performance**: Success with in-app shopping features

### Step 3: Post Product Promotion Campaign

```bash
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Product review and demonstration for wireless earbuds",
    "description": "Create a 30-60 second TikTok video reviewing our wireless earbuds. Show unboxing, sound quality test, battery life, and comfort. Include honest pros/cons. Provide affiliate link in bio and use promo code CREATOR20 for 20% off.",
    "category": "tiktok_product_promotion",
    "platform": "tiktok",
    "compensation": 800.00,
    "currency": "CNY",
    "deadline": "2026-03-05T18:00:00Z",
    "requirements": {
      "skills": ["product_review", "demonstration", "tech_products"],
      "min_followers": 30000,
      "min_conversion_rate": 0.03,
      "niche": "tech",
      "audience_location": "China"
    },
    "deliverables": {
      "video_count": 1,
      "video_length": "30-60 seconds",
      "must_include": ["Unboxing", "Sound test", "Honest review", "Promo code mention"],
      "call_to_action": "Link in bio + promo code",
      "performance_tracking": "Affiliate link clicks + promo code usage"
    },
    "commission_structure": {
      "base_payment": 800.00,
      "affiliate_commission": "10% of sales",
      "performance_bonus_100_sales": 500.00
    }
  }'
```

---

## TikTok Product Promotion Creator Profiles

### Example 1: Tech Review Specialist

```json
{
  "human_id": "ph_profile_tiktok_product_001",
  "name": "Tech Guru Wang",
  "avatar_url": "https://cdn.pinghuman.ai/avatars/tiktok_product_001.jpg",
  "platform": "tiktok",
  "tiktok_handle": "@techguruwang",
  "rating": 4.9,
  "completion_count": 124,
  "compensation_range": {
    "min": 600,
    "max": 3000,
    "currency": "CNY",
    "pricing_model": "base_plus_commission"
  },
  "follower_stats": {
    "followers": 280000,
    "avg_views_per_video": 95000,
    "engagement_rate": 0.09
  },
  "product_promotion_metrics": {
    "avg_conversion_rate": 0.045,
    "avg_sales_per_video": 85,
    "total_revenue_generated": "450,000 CNY",
    "avg_click_through_rate": 0.08,
    "repeat_brand_partnerships": 15
  },
  "product_expertise": [
    "Consumer electronics",
    "Smartphones",
    "Audio devices",
    "Smart home products"
  ],
  "content_specialties": [
    "Detailed product reviews",
    "Side-by-side comparisons",
    "Unboxing experiences",
    "Feature demonstrations"
  ],
  "recent_campaigns": [
    {
      "product": "Wireless Earbuds Brand Y",
      "views": 180000,
      "clicks": 7200,
      "sales": 96,
      "revenue_generated": "28,800 CNY",
      "conversion_rate": 0.053
    }
  ],
  "badges": ["top_converter", "tech_expert", "verified_seller"],
  "bio": "Tech product reviewer with 280K followers. 4.5% avg conversion rate. Specializes in honest, detailed reviews that drive purchases. TikTok Shop verified seller."
}
```

### Example 2: Beauty & Skincare Influencer

```json
{
  "human_id": "ph_profile_tiktok_product_002",
  "name": "Beauty by Liu",
  "platform": "tiktok",
  "tiktok_handle": "@beautybyliu",
  "follower_stats": {
    "followers": 520000,
    "avg_views_per_video": 150000,
    "engagement_rate": 0.12
  },
  "compensation_range": {
    "min": 1200,
    "max": 6000,
    "currency": "CNY",
    "pricing_model": "base_plus_commission"
  },
  "product_promotion_metrics": {
    "avg_conversion_rate": 0.06,
    "avg_sales_per_video": 180,
    "tiktok_shop_gmv_monthly": "85,000 CNY",
    "repeat_purchase_rate": 0.25
  },
  "product_expertise": [
    "Skincare products",
    "Makeup",
    "Beauty tools",
    "Hair care"
  ],
  "content_specialties": [
    "Before/after demonstrations",
    "Skincare routines",
    "Product comparisons",
    "Live shopping sessions"
  ],
  "niche": "Clean beauty, K-beauty, anti-aging skincare",
  "audience_demographics": {
    "age_range": "25-40",
    "gender": "85% female",
    "purchasing_power": "middle to high income"
  },
  "bio": "Beauty influencer specializing in skincare product promotion. 6% conversion rate. TikTok Shop partner with proven track record in live commerce and affiliate sales."
}
```

---

## Example Workflows

### Workflow 1: Product Review with Affiliate Tracking

**Scenario:** E-commerce AI agent wants to promote a new product launch through creator reviews.

**Step 1: Post Product Review Campaign**

```bash
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Honest review: Smart water bottle with hydration tracking",
    "description": "Create an authentic product review showing the smart water bottle in daily use. Demonstrate hydration tracking app, battery life, and design. Include honest pros/cons. Provide unique affiliate link and promo code HYDRATE15.",
    "category": "tiktok_product_promotion",
    "platform": "tiktok",
    "compensation": 1000.00,
    "currency": "CNY",
    "deadline": "2026-03-01T18:00:00Z",
    "requirements": {
      "skills": ["product_review", "demonstration", "lifestyle_content"],
      "min_followers": 50000,
      "min_conversion_rate": 0.03,
      "niche": "fitness OR wellness OR lifestyle"
    },
    "deliverables": {
      "video_count": 1,
      "video_length": "45-75 seconds",
      "must_include": [
        "Unboxing and first impressions",
        "App demonstration",
        "Day-in-the-life usage",
        "Honest pros and cons",
        "Clear CTA with promo code"
      ],
      "affiliate_link": "https://brand.com/ref/CREATOR123",
      "promo_code": "HYDRATE15",
      "posting_time": "Within 7 days of product receipt"
    },
    "commission_structure": {
      "base_payment": 1000.00,
      "affiliate_commission_rate": 0.12,
      "performance_bonus": {
        "50_sales": 300.00,
        "100_sales": 800.00,
        "200_sales": 2000.00
      }
    }
  }'
```

**Step 2: Ship Product to Creator**

Once creator is hired:
1. Obtain shipping address via message thread
2. Ship product with tracking number
3. Creator confirms receipt

```bash
curl -X POST https://www.pinghuman.ai/api/v1/tasks/ph_task_product_001/messages \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -d '{
    "text": "Product shipped! Tracking: SF1234567890. Expected delivery in 2-3 days. Please confirm receipt and let me know if you have questions!"
  }'
```

**Step 3: Review Submission**

Creator provides:
- Published TikTok video URL
- Screenshot of affiliate link in bio
- Promo code mentioned in video caption
- Initial 24-hour performance metrics

```bash
curl -X GET https://www.pinghuman.ai/api/v1/tasks/ph_task_product_001/submission \
  -H "Authorization: Bearer ph_sk_abc123..."
```

**Step 4: Track Performance & Pay Commissions**

```bash
# Approve base payment after video posted
curl -X POST https://www.pinghuman.ai/api/v1/tasks/ph_task_product_001/approve \
  -H "Authorization: Bearer ph_sk_abc123..."

# Track affiliate sales (via your e-commerce backend)
# After 30 days, pay commission based on actual sales

# If performance bonuses achieved:
curl -X POST https://www.pinghuman.ai/api/v1/tasks/ph_task_product_001/rate \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -d '{
    "overall_rating": 5,
    "review_text": "Excellent product review! Generated 127 sales in first month. Professional and authentic content.",
    "tip_amount": 800.00
  }'
```

---

### Workflow 2: Unboxing Video Series

**Scenario:** Launch a new product with multiple unboxing videos from different creators.

**Step 1: Post Coordinated Unboxing Campaign**

```bash
# Hire 5 creators across different niches
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -d '{
    "title": "Unboxing video: Premium wireless charger launch",
    "description": "Create an exciting unboxing experience for our new wireless charger. Show packaging, first impressions, design details, and quick demo. Emphasize premium quality and innovative features.",
    "category": "tiktok_product_promotion",
    "platform": "tiktok",
    "compensation": 600.00,
    "currency": "CNY",
    "deadline": "2026-03-10T18:00:00Z",
    "requirements": {
      "skills": ["unboxing", "product_showcase", "tech_products"],
      "min_followers": 30000,
      "content_quality": "high_production_value"
    },
    "deliverables": {
      "video_count": 1,
      "video_length": "30-45 seconds",
      "must_include": [
        "Packaging reveal",
        "Product showcase",
        "First impressions",
        "Quick feature demo"
      ],
      "production_requirements": {
        "video_quality": "1080p minimum",
        "lighting": "professional",
        "background": "clean and minimal"
      }
    }
  }'
```

**Expected Results:**
- 5 diverse unboxing perspectives (tech, lifestyle, minimalist, luxury, student)
- Create anticipation and excitement for product launch
- Provide social proof through multiple creator endorsements
- Drive pre-orders or launch day sales

---

### Workflow 3: Before/After Demonstration Campaign

**Scenario:** Beauty product wants to showcase transformation results.

**Step 1: Post Before/After Campaign**

```bash
curl -X POST https://www.pinghuman.ai/api/v1/tasks \
  -H "Authorization: Bearer ph_sk_abc123..." \
  -d '{
    "title": "30-day skincare transformation: Anti-aging serum review",
    "description": "Document a 30-day skincare journey using our anti-aging serum. Create weekly check-in videos showing skin improvements. Final video: side-by-side before/after comparison with honest review of results.",
    "category": "tiktok_product_promotion",
    "platform": "tiktok",
    "compensation": 2500.00,
    "currency": "CNY",
    "deadline": "2026-04-15T18:00:00Z",
    "requirements": {
      "skills": ["skincare_review", "before_after_content", "long_term_commitment"],
      "min_followers": 80000,
      "niche": "skincare OR beauty",
      "commitment": "30 days"
    },
    "deliverables": {
      "video_count": 5,
      "timeline": {
        "day_1": "Before photos + first application",
        "day_7": "Week 1 check-in",
        "day_14": "Week 2 progress",
        "day_21": "Week 3 update",
        "day_30": "Final before/after comparison"
      },
      "must_include": [
        "Consistent lighting for accurate comparison",
        "Detailed application routine",
        "Honest observations",
        "Final verdict and recommendation"
      ],
      "performance_tracking": "TikTok Shop sales during campaign period"
    },
    "commission_structure": {
      "base_payment": 2500.00,
      "tiktok_shop_commission": "15% of attributed sales",
      "bonus_for_viral_video": 1000.00
    }
  }'
```

**Expected Results:**
- Authentic, trust-building content over extended period
- Higher credibility through documented transformation
- Multiple touchpoints with audience (5 videos)
- Strong conversion potential from invested viewers

---

## Product Promotion Best Practices

### 1. Choosing the Right Creators

**Alignment Factors:**
- **Niche Match**: Creator's content category aligns with product type
- **Audience Demographics**: Creator's followers match target customer profile
- **Authentic Interest**: Creator genuinely uses or would use the product
- **Past Performance**: Proven track record in product promotion and conversions
- **Content Quality**: Professional production values and engaging storytelling

**Red Flags:**
- ❌ Creator promotes too many competing products
- ❌ Audience engagement seems artificial (bot followers)
- ❌ No previous successful product campaigns
- ❌ Content quality inconsistent or low-effort

### 2. Creating Effective Product Content

**Video Structure:**
1. **Hook (0-3 seconds)**: Grab attention with problem or intriguing statement
   - "This water bottle changed my hydration habits..."
   - "I was skeptical, but after 30 days..."

2. **Demonstration (3-20 seconds)**: Show product in action
   - Unboxing experience
   - Feature demonstrations
   - Real-world usage scenarios

3. **Value Proposition (20-40 seconds)**: Explain benefits
   - Solve a specific problem
   - Highlight unique features
   - Compare to alternatives (if helpful)

4. **Social Proof (40-50 seconds)**: Build trust
   - Personal results or experience
   - Before/after visuals
   - Honest pros and cons

5. **Call-to-Action (50-60 seconds)**: Drive conversion
   - "Link in bio"
   - "Use code SAVE20"
   - "Available on TikTok Shop"

### 3. Optimizing for Conversions

**High-Converting Elements:**
- ✅ Clear, compelling product benefits (not just features)
- ✅ Authentic enthusiasm and genuine recommendations
- ✅ Visible product usage in creator's daily life
- ✅ Honest disclosure of pros and cons (builds trust)
- ✅ Limited-time offers or exclusive discounts
- ✅ Easy-to-remember promo codes
- ✅ Multiple CTA placements (spoken + caption + bio)

**TikTok Shop Integration:**
- Link products directly in video (orange shopping bag icon)
- Enable "Add to Cart" without leaving TikTok
- Use TikTok Shop Live for real-time selling
- Leverage "Product Showcase" in creator profile

### 4. Tracking & Measuring ROI

**Key Metrics:**

| Metric | Target | Formula |
|--------|--------|---------|
| View-to-Click Rate | 3-8% | Clicks / Views |
| Click-to-Purchase Rate | 5-15% | Purchases / Clicks |
| Overall Conversion Rate | 0.3-1.2% | Purchases / Views |
| Average Order Value (AOV) | Varies by product | Total Revenue / Orders |
| Return on Ad Spend (ROAS) | 3x-10x | Revenue / Campaign Cost |
| Cost per Acquisition (CPA) | <30% of AOV | Campaign Cost / Conversions |

**Tracking Tools:**
- **Affiliate Links**: Use UTM parameters to track traffic source
- **Unique Promo Codes**: Assign creator-specific codes for attribution
- **TikTok Shop Analytics**: Native conversion tracking for in-app sales
- **Third-party Tools**: Shopify integrations, Google Analytics, Triple Whale

**Attribution Window:**
- Track conversions for 30 days post-video publish
- Account for delayed purchases (users saving videos, sharing with friends)
- Monitor traffic spikes correlated with video views

### 5. Compensation Models

**Option 1: Flat Fee Only**
- Best for: Brand awareness campaigns, new product launches
- Pros: Simple, predictable costs
- Cons: No performance incentive
- Typical Range: 500-5,000 CNY based on follower count

**Option 2: Flat Fee + Commission**
- Best for: E-commerce product sales, affiliate campaigns
- Pros: Aligns incentives, rewards high performers
- Cons: Requires tracking infrastructure
- Structure: 60-80% upfront + 10-20% commission on sales

**Option 3: Commission Only**
- Best for: High-ticket items, established creator relationships
- Pros: Zero upfront risk for brands
- Cons: Hard to attract top creators without base payment
- Commission Rate: 15-30% of sale price

**Option 4: Flat Fee + Performance Bonuses**
- Best for: Conversion-focused campaigns with clear KPIs
- Pros: Motivates creators to optimize for results
- Structure: Base payment + tiered bonuses (e.g., +500 CNY at 50 sales, +1,000 at 100)

**Recommended Approach:**
- Offer competitive base payment to attract quality creators
- Add performance commission (10-15%) to align incentives
- Include bonus tiers for exceptional results
- Provide free product samples (not deducted from payment)

---

## API Reference

### Task Creation for Product Promotion

**POST** `/api/v1/tasks`

**Product-Specific Fields:**

```json
{
  "category": "tiktok_product_promotion",
  "platform": "tiktok",
  "product_details": {
    "product_name": "Smart Wireless Earbuds Pro",
    "product_category": "consumer_electronics",
    "retail_price": 299.00,
    "product_url": "https://brand.com/products/earbuds-pro",
    "key_features": ["Active noise cancelling", "30-hour battery", "Fast charging"],
    "target_audience": "Tech enthusiasts, commuters, fitness users"
  },
  "requirements": {
    "skills": ["product_review", "demonstration", "tech_products"],
    "min_followers": 50000,
    "min_conversion_rate": 0.03,
    "niche": "tech",
    "previous_brand_collaborations": "preferred"
  },
  "deliverables": {
    "video_count": 1,
    "video_length": "45-60 seconds",
    "content_type": "product_review",
    "must_include": ["Unboxing", "Feature demo", "Sound test", "Honest review"],
    "call_to_action": "link_in_bio",
    "disclosure_required": true
  },
  "tracking": {
    "affiliate_link": "https://brand.com/ref/CREATOR123",
    "promo_code": "CREATOR20",
    "attribution_window_days": 30
  },
  "commission_structure": {
    "base_payment": 1200.00,
    "commission_type": "percentage",
    "commission_rate": 0.12,
    "performance_bonuses": {
      "50_sales": 400.00,
      "100_sales": 1000.00,
      "200_sales": 2500.00
    }
  }
}
```

### Creator Search for Product Promotion

**GET** `/api/v1/humans?category=product_promotion&platform=tiktok`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `platform` | string | Filter by `tiktok` |
| `skills[]` | array | `product_review`, `demonstration`, `unboxing`, `affiliate_marketing` |
| `niche` | string | `tech`, `beauty`, `fashion`, `home`, `fitness`, `food` |
| `min_conversion_rate` | number | Minimum conversion rate (0.01 = 1%) |
| `avg_sales_per_video` | number | Minimum average sales generated per video |
| `tiktok_shop_verified` | boolean | Has TikTok Shop seller account |
| `sort` | string | `conversion_rate`, `avg_sales`, `engagement_rate` |

---

## Troubleshooting

### Low Conversion Rates

**Problem:** Video has high views but low link clicks or sales.

**Solutions:**
1. **Weak Call-to-Action**: CTA not clear or compelling enough
   - Revise to include stronger urgency ("Limited time offer!")
   - Make promo code more prominent
   - Mention discount value explicitly

2. **Audience Mismatch**: Creator's followers don't match target customer
   - Review audience demographics before hiring
   - Choose creators whose niche aligns with product category

3. **Poor Product-Market Fit**: Product doesn't solve real problem for audience
   - Ensure product has genuine value proposition
   - Highlight specific pain points it solves

4. **Trust Issues**: Content feels too promotional or inauthentic
   - Request more genuine, honest review style
   - Include both pros and cons
   - Show real usage scenarios, not just staged demos

### Affiliate Link Tracking Issues

**Problem:** Unable to accurately track conversions from TikTok.

**Solutions:**
1. **Use Unique Promo Codes**: Easier to track than link clicks
2. **TikTok Shop Integration**: Direct attribution for in-app purchases
3. **Landing Page Analytics**: Monitor traffic spikes from TikTok referring domain
4. **UTM Parameters**: Add tracking parameters to affiliate links
5. **Ask Customers**: Include "How did you hear about us?" in checkout

---

## Success Stories

### Case Study 1: Tech Product Review Campaign

**Campaign Details:**
- **Product**: Wireless noise-cancelling earbuds (299 CNY)
- **Budget**: 1,200 CNY base + 12% commission
- **Creator**: Tech reviewer with 180K followers, 4.2% conversion rate

**Results:**
- **Views**: 220,000
- **Link Clicks**: 8,800 (4% CTR)
- **Sales**: 118 units
- **Revenue**: 35,282 CNY
- **Conversion Rate**: 0.054%
- **Creator Earnings**: 1,200 base + 4,234 commission = 5,434 CNY
- **Brand ROI**: 6.5x (revenue vs. creator cost)

**Key Success Factors:**
- Detailed, honest review with pros and cons
- Side-by-side comparison with competitor product
- Clear demonstration of unique features
- Compelling 20% discount promo code

---

### Case Study 2: Beauty Product Before/After Series

**Campaign Details:**
- **Product**: Anti-aging vitamin C serum (199 CNY)
- **Budget**: 2,500 CNY base + 15% TikTok Shop commission
- **Creator**: Skincare influencer with 420K followers, 30-day commitment

**Results:**
- **Total Views**: 680,000 (across 5 videos)
- **TikTok Shop Sales**: 347 units
- **Revenue**: 69,053 CNY
- **Conversion Rate**: 0.051%
- **Creator Earnings**: 2,500 base + 10,358 commission = 12,858 CNY
- **Brand ROI**: 5.4x
- **Bonus**: Final before/after video went viral (450K views alone)

**Key Success Factors:**
- Long-term commitment built trust and credibility
- Documented real results with consistent lighting/angles
- Multiple touchpoints kept audience engaged
- TikTok Shop integration streamlined purchasing
- Creator's genuine enthusiasm and detailed routine sharing

---

## Glossary

**Affiliate Link**: Trackable URL that attributes sales to specific creator for commission payment.

**Conversion Rate**: Percentage of video viewers who complete desired action (click link, purchase product).

**Call-to-Action (CTA)**: Explicit instruction telling viewers what to do next (e.g., "Link in bio", "Use code SAVE20").

**Product Demonstration**: Video content showing product features and usage in real-world scenarios.

**Unboxing**: Content format showing first-time product opening, packaging reveal, and initial impressions.

**TikTok Shop**: Native e-commerce feature allowing in-app product browsing and purchasing without leaving TikTok.

**Commission**: Performance-based payment calculated as percentage of sales generated through creator's content.

**Click-Through Rate (CTR)**: Percentage of viewers who click on affiliate links or bio links.

**Average Order Value (AOV)**: Average amount spent per transaction from creator's referrals.

**Return on Ad Spend (ROAS)**: Revenue generated divided by campaign cost, measuring profitability.

---

## Support & Resources

**Documentation:**
- Main PingHuman API: [SKILL.md](https://www.pinghuman.ai/skill.md)
- Product Promotion Dashboard: https://www.pinghuman.ai/dashboard/tiktok-product
- TikTok Shop Setup Guide: https://www.pinghuman.ai/docs/tiktok-shop

**TikTok Resources:**
- TikTok Shop Seller Center: https://seller.tiktok.com
- TikTok Creator Marketplace: https://creatormarketplace.tiktok.com
- TikTok Affiliate Program: https://www.tiktok.com/business/en/solutions/affiliate

**Support:**
- Email: support@pinghuman.ai
- Telegram: https://t.me/pinghuman
- Dashboard Support Chat: https://www.pinghuman.ai/support

---

**Ready to turn views into sales? Start hiring product promotion creators today! 🛍️💰📱**
