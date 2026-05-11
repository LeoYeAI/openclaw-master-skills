# Complete Monid Capabilities Reference

This document provides a comprehensive reference of all supported Monid capabilities. Use this for quick lookup when helping users determine which capability to use.

## Quick Setup Reference

**First-Time Setup** (3-5 minutes):
```bash
# 1. Install CLI
curl -fsSL https://raw.githubusercontent.com/FeiyouG/monid-client/main/install.sh | bash

# 2. Verify
monid --version

# 3. Authenticate (browser opens)
monid auth login

# 4. Generate key
monid keys generate --label main

# 5. Verify setup
monid auth whoami
```

**Check if already set up**:
```bash
monid --version      # Check if installed
monid auth whoami    # Check if authenticated and has active key
```

For detailed setup instructions, see main SKILL.md Prerequisites section.

---

## Quick Reference Table

| Platform | Capability Name | Capability ID | Best Use Case | Est. Cost |
|----------|----------------|---------------|---------------|-----------|
| **X (Twitter)** |
| | X Tweet Scraper | `apify#apidojo/tweet-scraper` | Large-scale tweet collection, search terms, profiles, advanced filters | $0.0004/call |
| **Instagram** |
| | Instagram Scraper | `apify#apify/instagram-scraper` | General Instagram content from usernames, hashtags, locations | $0.0023/call |
| | Instagram Profile Scraper | `apify#apify/instagram-profile-scraper` | Profile-level info, influencer analysis | $0.0023/call |
| | Instagram API Scraper | `apify#apify/instagram-api-scraper` | API-style structured extraction, programmatic pipelines | $0.0020/call |
| | Instagram Hashtag Scraper | `apify#apify/instagram-hashtag-scraper` | Hashtag pages, trend tracking, campaign monitoring | $0.0023/call |
| | Instagram Post Scraper | `apify#apify/instagram-post-scraper` | Direct post URLs, deterministic URL-driven workflows | $0.0023/call |
| **TikTok** |
| | TikTok API Scraper | `apify#scraptik/tiktok-api` | Flexible TikTok collection (profiles, videos, hashtags, search) | $0.0020/call |
| | TikTok Profile Scraper | `apify#apidojo/tiktok-profile-scraper` | Creator profiles, influencer tracking | $0.0003/call |
| | TikTok Scraper | `apify#apidojo/tiktok-scraper` | High-throughput video collection from profiles, hashtags, keywords | $0.0003/call |
| | TikTok Post Scraper | `apify#thenetaji/tiktok-post-scraper` | Individual posts by URL | $0.0015/call |
| | TikTok Video Scraper | `apify#clockworks/tiktok-video-scraper` | Detailed video metadata, per-video extraction | $0.0100/call |
| **LinkedIn** |
| | LinkedIn Post Search | `apify#harvestapi/linkedin-post-search` | Find posts by keywords, topic monitoring | $0.0020/call |
| | LinkedIn Profile Search | `apify#harvestapi/linkedin-profile-search` | Search people by role/company/location, lead generation | $0.1000/call |
| | LinkedIn Job Search | `apify#powerai/linkedin-job-search-scraper` | Job listings, hiring intelligence | $0.0050/call |
| | LinkedIn Company Search | `apify#powerai/linkedin-company-search-scraper` | Company pages, organization data | $0.0050/call |
| **YouTube** |
| | YouTube Scraper | `apify#streamers/youtube-scraper` | Videos from searches, channels, URLs | $0.0030/call |
| | YouTube Comments Scraper | `apify#streamers/youtube-comments-scraper` | Comments and threads, sentiment analysis | $0.0015/call |
| | YouTube Scraper (API Dojo) | `apify#apidojo/youtube-scraper` | High-volume, cost-effective scraping | $0.0005/call |
| | YouTube Video Transcript | `apify#starvibe/youtube-video-transcript` | Video transcripts with timing, NLP workflows | $0.0050/call |
| **Facebook** |
| | Facebook Reviews Scraper | `apify#apify/facebook-reviews-scraper` | Reviews from pages, reputation monitoring | $0.0020/call |
| | Facebook Events Scraper | `apify#apify/facebook-events-scraper` | Event listings, local activity tracking | $0.0100/call |
| | Facebook Marketplace Scraper | `apify#curious_coder/facebook-marketplace` | Marketplace listings, market monitoring | $0.0050/call |
| | Facebook Pages Scraper | `apify#apify/facebook-pages-scraper` | Page data and content, page monitoring | $0.0100/call |
| | Facebook Groups Scraper | `apify#apify/facebook-groups-scraper` | Public group posts, community monitoring | $0.0040/call |
| | Facebook Comments Scraper | `apify#apify/facebook-comments-scraper` | Comments from posts/pages, sentiment analysis | $0.0020/call |
| | Facebook Ads Library Scraper | `apify#curious_coder/facebook-ads-library-scraper` | Ads library data, competitive research | $0.0008/call |
| **Amazon** |
| | Amazon Product Scraper | `apify#delicious_zebu/amazon-product-scraper` | Product details from URLs (price, reviews, ratings) | $0.0010/call |
| | Amazon Reviews Scraper | `apify#axesso_data/amazon-reviews-scraper` | Customer reviews, review analysis | $0.0070/call |
| | Amazon Search Scraper | `apify#axesso_data/amazon-search-scraper` | Search results, product listings | $0.0001/call |
| **Google** |
| | Google Maps Scraper | `apify#damilo/google-maps-scraper` | Businesses by query + location (BOTH REQUIRED) | $0.0030/call |

## Platform-Specific Guidance

### X (Twitter)

**Single Capability**: Tweet Scraper
- **Inputs**: Search terms, profile handles, list URLs, tweet URLs
- **Filters**: Date range, language, media type, engagement thresholds
- **Best for**: Any Twitter scraping task

**Example queries**:
- "Recent tweets about Bitcoin"
- "Tweets from @elonmusk in the last week"
- "Viral tweets with >10k likes about AI"

---

### Instagram

**5 Capabilities** - Choose based on data source:

1. **General scraper**: Use for broad collection (usernames, hashtags, locations)
2. **Profile scraper**: Use when focusing on specific accounts/influencers
3. **API scraper**: Use for programmatic/pipeline integration
4. **Hashtag scraper**: Use specifically for hashtag-based searches
5. **Post scraper**: Use when you have direct post URLs

**Selection guide**:
- Have URLs? → Post Scraper
- Tracking hashtags? → Hashtag Scraper
- Analyzing influencers? → Profile Scraper
- Need API-style data? → API Scraper
- General collection? → Instagram Scraper

---

### TikTok

**5 Capabilities** - Choose based on scope:

1. **API Scraper**: Most flexible, supports profiles/videos/hashtags/search
2. **Profile Scraper**: Best for creator-focused analysis
3. **TikTok Scraper**: High-throughput for profiles/hashtags/keywords
4. **Post Scraper**: Individual posts by URL
5. **Video Scraper**: Detailed per-video metadata

**Selection guide**:
- Need flexibility? → API Scraper
- High volume? → TikTok Scraper
- Specific videos? → Post/Video Scraper
- Creator focus? → Profile Scraper

---

### LinkedIn

**4 Capabilities** - Choose based on entity type:

1. **Post Search**: Find posts by keywords
2. **Profile Search**: Find people (most expensive at $0.10/call)
3. **Job Search**: Find job listings
4. **Company Search**: Find companies

**Note**: Profile Search is 20x more expensive than other LinkedIn scrapers. Only use when specifically searching for people.

---

### YouTube

**4 Capabilities** - Choose based on data type:

1. **YouTube Scraper**: General video/channel scraping
2. **Comments Scraper**: Extract comments and discussions
3. **YouTube Scraper (API Dojo)**: Cost-effective alternative (60% cheaper)
4. **Video Transcript**: Get video transcripts for NLP

**Selection guide**:
- Need transcripts? → Video Transcript
- Need comments? → Comments Scraper
- Cost-sensitive? → API Dojo version
- General collection? → Standard YouTube Scraper

---

### Facebook

**7 Capabilities** - Most granular platform:

1. **Reviews Scraper**: Page reviews
2. **Events Scraper**: Event listings
3. **Marketplace Scraper**: Buy/sell listings
4. **Pages Scraper**: Page content
5. **Groups Scraper**: Public group posts
6. **Comments Scraper**: Comments from posts
7. **Ads Library Scraper**: Public ad campaigns

**Selection guide**: Choose based on exactly what the user wants to scrape (reviews, events, marketplace, pages, groups, comments, or ads).

---

### Amazon

**3 Capabilities** - Choose based on data source:

1. **Product Scraper**: Use with product URLs for details
2. **Reviews Scraper**: Use for customer reviews (most expensive Amazon scraper)
3. **Search Scraper**: Use for search keyword results (cheapest at $0.0001/call)

**Selection guide**:
- Have product URL? → Product Scraper
- Need reviews? → Reviews Scraper
- Keyword search? → Search Scraper

---

### Google

**Single Capability**: Google Maps Scraper
- **REQUIRED inputs**: Both query AND location
- **Returns**: Business name, address, phone, website, rating, reviews
- **Best for**: Local business data, competitor research

**Example queries**:
- "Coffee shops in Seattle"
- "Italian restaurants in New York City"
- "Gyms near downtown Los Angeles"

## Cost Optimization Tips

### Most Expensive Scrapers (>$0.005/call)
- LinkedIn Profile Search ($0.10) - 20x cost premium
- TikTok Video Scraper ($0.01)
- Facebook Events/Pages ($0.01)
- Amazon Reviews ($0.007)

**Tip**: Suggest alternatives when possible:
- For TikTok videos, try TikTok Scraper ($0.0003) first
- For Amazon products, use Product Scraper ($0.001) instead of Reviews if reviews aren't critical

### Most Cost-Effective Scrapers (<$0.001/call)
- Amazon Search ($0.0001) - Cheapest overall
- TikTok Profile/Scraper ($0.0003)
- X Tweet Scraper ($0.0004)
- YouTube API Dojo ($0.0005)

## Common Patterns

### Pattern 1: Social Media Monitoring
**Platforms**: X, Instagram, TikTok, Facebook
**Use case**: Track brand mentions, hashtags, trends
**Recommended scrapers**:
- X Tweet Scraper (search terms)
- Instagram Hashtag Scraper
- TikTok Scraper (keywords)
- Facebook Groups/Pages (if applicable)

### Pattern 2: Influencer Analysis
**Platforms**: Instagram, TikTok, YouTube
**Use case**: Analyze creator metrics, content performance
**Recommended scrapers**:
- Instagram Profile Scraper
- TikTok Profile Scraper
- YouTube Scraper

### Pattern 3: E-commerce Research
**Platforms**: Amazon
**Use case**: Product research, competitor pricing, review analysis
**Recommended scrapers**:
- Amazon Search Scraper (broad research)
- Amazon Product Scraper (specific products)
- Amazon Reviews Scraper (sentiment analysis)

### Pattern 4: B2B Lead Generation
**Platforms**: LinkedIn
**Use case**: Find prospects, companies, jobs
**Recommended scrapers**:
- LinkedIn Profile Search (people - expensive)
- LinkedIn Company Search (organizations)
- LinkedIn Job Search (hiring signals)

### Pattern 5: Local Business Intelligence
**Platforms**: Google Maps
**Use case**: Competitor mapping, local market research
**Recommended scraper**:
- Google Maps Scraper (requires query + location)

### Pattern 6: Content Analysis
**Platforms**: YouTube, TikTok, Instagram
**Use case**: Analyze video/post content, transcripts, comments
**Recommended scrapers**:
- YouTube Video Transcript (for text analysis)
- YouTube Comments Scraper (engagement/sentiment)
- TikTok Video Scraper (detailed metadata)
- Instagram Post Scraper (specific posts)

## Unsupported Platforms

Monid does **NOT** support:
- Reddit
- Pinterest
- Snapchat
- WhatsApp
- Telegram
- Discord
- Twitter Spaces (audio)
- Twitch
- Generic web scraping
- Any platform not explicitly listed above

If a user asks for data from these platforms, inform them that Monid doesn't currently support them.

## Schema Design Tips by Platform

### Social Media Posts (X, Instagram, TikTok, Facebook)
Typical fields:
```json
{
  "posts": [{
    "text": "string",
    "author": "string",
    "timestamp": "string",
    "likes": "number",
    "comments": "number",
    "shares": "number",
    "url": "string",
    "media_urls": ["string"]
  }]
}
```

### Profile/Creator Data
Typical fields:
```json
{
  "profiles": [{
    "username": "string",
    "display_name": "string",
    "bio": "string",
    "followers": "number",
    "following": "number",
    "posts_count": "number",
    "verified": "boolean",
    "profile_url": "string"
  }]
}
```

### E-commerce Products (Amazon)
Typical fields:
```json
{
  "products": [{
    "title": "string",
    "price": "number",
    "currency": "string",
    "rating": "number",
    "review_count": "number",
    "availability": "string",
    "asin": "string",
    "url": "string"
  }]
}
```

### Local Businesses (Google Maps)
Typical fields:
```json
{
  "businesses": [{
    "name": "string",
    "address": "string",
    "phone": "string",
    "website": "string",
    "rating": "number",
    "review_count": "number",
    "categories": ["string"],
    "hours": "string"
  }]
}
```

### Job Listings (LinkedIn)
Typical fields:
```json
{
  "jobs": [{
    "title": "string",
    "company": "string",
    "location": "string",
    "description": "string",
    "posted_date": "string",
    "employment_type": "string",
    "seniority_level": "string",
    "job_url": "string"
  }]
}
```

## Rate Limits and Best Practices

### General Guidelines
1. **Start small**: Test with 10-50 items before scaling
2. **Add delays**: For large jobs, expect longer execution times
3. **Batch requests**: Don't make hundreds of individual calls; use single calls with larger limits
4. **Respect platforms**: Monid automatically handles rate limiting, but be reasonable with requests

### Recommended Limits
- **Social media posts**: 50-500 per request
- **Profiles**: 10-100 per request
- **Products**: 20-200 per request
- **Job listings**: 50-500 per request
- **Local businesses**: 20-200 per request

Larger requests may timeout or fail. When in doubt, use smaller limits and make multiple requests if needed.
