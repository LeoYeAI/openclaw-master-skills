---
name: monid
description: How to use the Monid CLI to execute data scraping and collection tasks from social media platforms, e-commerce sites, and search engines. Use this skill when the user needs to scrape data from Twitter/X, Instagram, TikTok, Facebook, LinkedIn, YouTube, Amazon, or Google Maps. This skill provides complete workflow guidance for authentication, task creation, price quotes, and execution monitoring. ALWAYS use this skill when the user mentions scraping, collecting, or extracting data from supported platforms, even if they don't explicitly say "Monid". Use this for queries like "find tweets about X", "scrape Instagram posts", "get Amazon product reviews", or any data collection from the supported platforms.
---

# Monid CLI Skill

Monid is an agentic payment platform CLI that enables secure, pay-per-use data scraping from various platforms. This skill teaches you how to help users accomplish data collection tasks using the Monid CLI.

## Core Concept

Monid follows a **quote-then-execute** workflow:
1. **Create a task** (defines what data to collect)
2. **Get a price quote** (shows cost before execution)
3. **Execute the search** (runs the scraping job)
4. **Monitor and retrieve results** (check status and download data)

## Prerequisites

Before using Monid for data scraping, the user must complete these one-time setup steps:

### 1. Install the Monid CLI

**Quick Install (Recommended)**:
```bash
curl -fsSL https://raw.githubusercontent.com/FeiyouG/monid-client/main/install.sh | bash
```

This downloads and installs the latest stable Monid CLI to `~/.local/bin/monid`.

**Verify installation**:
```bash
monid --version
```

Expected output: `monid v1.0.0` (or later version)

**Supported platforms**: Linux x64, macOS ARM64 (Apple Silicon), Windows x64

**Troubleshooting**:
- If `monid: command not found` after installation, restart your terminal or run `source ~/.bashrc` (or `~/.zshrc` for zsh)
- Ensure `~/.local/bin` is in your PATH
- For Windows or manual installation, download binaries from: https://github.com/FeiyouG/monid-client/releases/latest

### 2. Authenticate with OAuth

```bash
monid auth login
```

**What happens**:
1. CLI starts a local callback server on port 8918
2. Your browser opens to the authentication page
3. Sign in with your credentials (Google, GitHub, etc.)
4. Browser redirects back to the CLI
5. Workspace information is saved to `~/.monid/config.yaml`

**If browser doesn't open**: Copy the URL from the terminal and paste it into your browser manually.

**Verify authentication**:
```bash
monid auth whoami
```

Expected output shows your workspace and user email.

### 3. Generate API Key

```bash
monid keys generate --label main
```

**What happens**:
1. CLI generates an Ed25519 cryptographic key pair
2. Private key is encrypted and stored locally at `~/.monid/keys/`
3. Public key is automatically registered with the backend
4. Key is activated for signing your requests

**Verify key**:
```bash
monid keys list
```

Expected output shows your key marked with `*` (active).

### Setup Complete!

After these three steps, you're ready to execute searches. If the user hasn't completed these steps, guide them through installation, authentication, and key generation first before attempting any searches.

## Supported Capabilities

Monid can ONLY scrape data from these platforms and capabilities. **NEVER suggest capabilities outside this list**:

### X (Twitter)
- **X Tweet Scraper** (`apify#apidojo/tweet-scraper`)
  - Scrape tweets from search terms, profile handles, list URLs, tweet URLs
  - Advanced filters: date range, language, media type, engagement thresholds
  - Best for: Large-scale tweet collection, trend analysis, sentiment analysis

### Instagram
- **Instagram Scraper** (`apify#apify/instagram-scraper`)
  - Scrape posts from usernames, hashtags, locations
  - Returns: post metadata, engagement metrics
  - Best for: General Instagram content collection
  
- **Instagram Profile Scraper** (`apify#apify/instagram-profile-scraper`)
  - Extract profile information and related posts
  - Best for: Influencer analysis, account research
  
- **Instagram API Scraper** (`apify#apify/instagram-api-scraper`)
  - API-style structured data extraction
  - Best for: Programmatic integration pipelines
  
- **Instagram Hashtag Scraper** (`apify#apify/instagram-hashtag-scraper`)
  - Scrape hashtag pages and posts
  - Best for: Trend tracking, campaign monitoring
  
- **Instagram Post Scraper** (`apify#apify/instagram-post-scraper`)
  - Extract specific posts from URLs
  - Best for: Known post URLs

### TikTok
- **TikTok API Scraper** (`apify#scraptik/tiktok-api`)
  - Flexible scraping across profiles, videos, hashtags, search
  - Best for: Multi-purpose TikTok collection
  
- **TikTok Profile Scraper** (`apify#apidojo/tiktok-profile-scraper`)
  - Scrape creator profiles and metrics
  - Best for: Influencer tracking
  
- **TikTok Scraper** (`apify#apidojo/tiktok-scraper`)
  - Collect videos from profiles, hashtags, keywords, URLs
  - Best for: High-throughput content extraction
  
- **TikTok Post Scraper** (`apify#thenetaji/tiktok-post-scraper`)
  - Extract individual posts by URL
  - Best for: Specific video collection
  
- **TikTok Video Scraper** (`apify#clockworks/tiktok-video-scraper`)
  - Detailed video metadata extraction
  - Best for: Per-video focused extraction

### LinkedIn
- **LinkedIn Post Search** (`apify#harvestapi/linkedin-post-search`)
  - Find posts by keyword queries
  - Best for: Topic monitoring, brand discussions
  
- **LinkedIn Profile Search** (`apify#harvestapi/linkedin-profile-search`)
  - Search people profiles by role, company, location
  - Best for: Lead generation, market mapping
  
- **LinkedIn Job Search** (`apify#powerai/linkedin-job-search-scraper`)
  - Collect job listings from searches
  - Best for: Hiring intelligence, talent mapping
  
- **LinkedIn Company Search** (`apify#powerai/linkedin-company-search-scraper`)
  - Find company pages and organization data
  - Best for: Company prospecting

### YouTube
- **YouTube Scraper** (`apify#streamers/youtube-scraper`)
  - Scrape videos from searches, channels, video URLs
  - Best for: Broad YouTube data collection
  
- **YouTube Comments Scraper** (`apify#streamers/youtube-comments-scraper`)
  - Collect comments and thread metadata
  - Best for: Sentiment analysis, engagement research
  
- **YouTube Scraper (API Dojo)** (`apify#apidojo/youtube-scraper`)
  - High-volume, cost-effective scraping
  - Best for: Scalable YouTube collection
  
- **YouTube Video Transcript** (`apify#starvibe/youtube-video-transcript`)
  - Fetch video transcripts with timing
  - Best for: Summarization, semantic search, NLP

### Facebook
- **Facebook Reviews Scraper** (`apify#apify/facebook-reviews-scraper`)
  - Scrape reviews from Facebook pages
  - Best for: Reputation monitoring
  
- **Facebook Events Scraper** (`apify#apify/facebook-events-scraper`)
  - Extract event listings and metadata
  - Best for: Event intelligence
  
- **Facebook Marketplace Scraper** (`apify#curious_coder/facebook-marketplace`)
  - Scrape marketplace listings
  - Best for: Market monitoring, competitor analysis
  
- **Facebook Pages Scraper** (`apify#apify/facebook-pages-scraper`)
  - Extract page data and content
  - Best for: Page monitoring
  
- **Facebook Groups Scraper** (`apify#apify/facebook-groups-scraper`)
  - Scrape public group posts
  - Best for: Community monitoring
  
- **Facebook Comments Scraper** (`apify#apify/facebook-comments-scraper`)
  - Extract comments from posts/pages
  - Best for: Sentiment analysis
  
- **Facebook Ads Library Scraper** (`apify#curious_coder/facebook-ads-library-scraper`)
  - Scrape ads library data
  - Best for: Competitive research, ad intelligence

### Amazon
- **Amazon Product Scraper** (`apify#delicious_zebu/amazon-product-scraper`)
  - Scrape product details from URLs: pricing, reviews, ratings, availability
  - Best for: Product research, price monitoring
  
- **Amazon Reviews Scraper** (`apify#axesso_data/amazon-reviews-scraper`)
  - Scrape customer reviews and ratings
  - Best for: Review analysis, sentiment research
  
- **Amazon Search Scraper** (`apify#axesso_data/amazon-search-scraper`)
  - Scrape search results with product listings
  - Best for: Market research, competitor analysis

### Google
- **Google Maps Scraper** (`apify#damilo/google-maps-scraper`)
  - Scrape businesses, cafes, restaurants, shops by query and location
  - Returns: name, address, phone, website, rating, reviews
  - **REQUIRED**: query (what to search) and location (where)
  - Best for: Local business data, competitor mapping

## Complete Workflow Guide

### Step 1: One-Time Setup

If the user is new to Monid, guide them through complete setup:

```bash
# 1. Install CLI
curl -fsSL https://raw.githubusercontent.com/FeiyouG/monid-client/main/install.sh | bash

# 2. Verify installation
monid --version

# 3. Authenticate via OAuth (browser will open)
monid auth login

# 4. Generate and register API key
monid keys generate --label main

# 5. Verify everything is ready
monid auth whoami
```

If already set up, skip to Step 2.

### Step 2: Understanding Task Creation

A **task** defines:
- **name**: Descriptive task name
- **query**: Natural language description of what to collect
- **output-schema**: JSON schema defining expected output structure

### Step 3: Execute a Search (Simplified Method)

The simplest approach combines task creation, quote, and execution:

```bash
# Quick execution with natural language query
monid search \
  --name "Twitter Sentiment Analysis" \
  --query "Find the most recent tweets related to Elon Musk from the past 7 days" \
  --output-schema '{
    "type": "object",
    "properties": {
      "tweets": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "text": {"type": "string"},
            "author": {"type": "string"},
            "timestamp": {"type": "string"},
            "likes": {"type": "number"},
            "retweets": {"type": "number"}
          }
        }
      }
    }
  }' \
  --wait \
  --output results.json
```

**Flags explained**:
- `--name`: Human-readable task name
- `--query`: Natural language query describing the task
- `--output-schema`: JSON schema (inline JSON or file path)
- `--wait`: Poll until completion (optional: `--wait 300` for 5-min timeout)
- `--output`: Save results to file
- `--yes` or `-y`: Skip price confirmation

### Step 4: Alternative - Create Reusable Tasks

For repeated use, create a task first:

```bash
# Create a reusable task
monid tasks create \
  --title "Elon Musk Twitter Monitor" \
  --description "Track Elon Musk mentions on Twitter" \
  --input-schema '{
    "type": "object",
    "properties": {
      "keywords": {"type": "string"},
      "days": {"type": "number"}
    },
    "required": ["keywords"]
  }' \
  --output-schema '{
    "type": "object",
    "properties": {
      "tweets": {"type": "array"}
    }
  }' \
  --capabilities '[{
    "capabilityId": "apify#apidojo/tweet-scraper",
    "prepareInput": {}
  }]'

# List all tasks
monid tasks list

# Get quote for a task
monid quotes create <task-id> --input '{"keywords": "Elon Musk", "days": 7}'

# Execute with quote
monid search --quote-id <quote-id> --wait --output results.json

# Or execute with task ID directly
monid search --task-id <task-id> --wait --output results.json
```

### Step 5: Monitor Execution

```bash
# Check execution status
monid executions get --execution-id <execution-id>

# Wait for completion and save results
monid executions get --execution-id <execution-id> --wait --output results.json

# List all executions
monid executions list
```

## Common Use Cases with Examples

### Example 0: First-Time User - Complete Setup to First Search

**User request**: "I want to scrape tweets about AI but I've never used Monid before"

**Complete workflow**:
```bash
# Step 1: Install Monid CLI
curl -fsSL https://raw.githubusercontent.com/FeiyouG/monid-client/main/install.sh | bash

# Step 2: Verify installation
monid --version

# Step 3: Authenticate (browser will open)
monid auth login

# Step 4: Generate API key
monid keys generate --label main

# Step 5: Execute your first search
monid search \
  --name "AI Tweets" \
  --query "Find the 50 most recent tweets about artificial intelligence from the past week" \
  --output-schema '{
    "type": "object",
    "properties": {
      "tweets": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "text": {"type": "string"},
            "author": {"type": "string"},
            "created_at": {"type": "string"},
            "likes": {"type": "number"},
            "retweets": {"type": "number"}
          }
        }
      }
    }
  }' \
  --wait \
  --output ai_tweets.json
```

**Estimated time**: 3-5 minutes for complete setup and first search.

### Example 1: Find Recent Tweets

**User request**: "Find the most recent tweets related to Elon Musk"

**Solution** (assumes Monid is already installed and authenticated):
```bash
monid search \
  --name "Elon Musk Tweets" \
  --query "Find the 50 most recent tweets mentioning 'Elon Musk' from the past 3 days" \
  --output-schema '{
    "type": "object",
    "properties": {
      "tweets": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "text": {"type": "string"},
            "author": {"type": "string"},
            "created_at": {"type": "string"},
            "likes": {"type": "number"},
            "retweets": {"type": "number"},
            "url": {"type": "string"}
          }
        }
      }
    }
  }' \
  --wait \
  --output elon_tweets.json
```

### Example 2: Instagram Hashtag Analysis

**User request**: "Get Instagram posts with hashtag #ai"

**Solution**:
```bash
monid search \
  --name "AI Hashtag Instagram" \
  --query "Scrape the top 100 Instagram posts with hashtag #ai, including engagement metrics" \
  --output-schema '{
    "type": "object",
    "properties": {
      "posts": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "caption": {"type": "string"},
            "author": {"type": "string"},
            "likes": {"type": "number"},
            "comments": {"type": "number"},
            "timestamp": {"type": "string"},
            "image_url": {"type": "string"}
          }
        }
      }
    }
  }' \
  --wait \
  --output ai_instagram.json
```

### Example 3: Amazon Product Research

**User request**: "Get reviews for a specific Amazon product"

**Solution**:
```bash
monid search \
  --name "Product Reviews" \
  --query "Scrape all customer reviews for the Amazon product at URL https://amazon.com/dp/B0123456, including ratings, review text, and reviewer names" \
  --output-schema '{
    "type": "object",
    "properties": {
      "reviews": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "rating": {"type": "number"},
            "title": {"type": "string"},
            "text": {"type": "string"},
            "reviewer": {"type": "string"},
            "date": {"type": "string"},
            "verified_purchase": {"type": "boolean"}
          }
        }
      }
    }
  }' \
  --wait \
  --output product_reviews.json
```

### Example 4: LinkedIn Job Search

**User request**: "Find machine learning jobs in San Francisco"

**Solution**:
```bash
monid search \
  --name "ML Jobs SF" \
  --query "Find machine learning engineer job postings in San Francisco area on LinkedIn from the past 2 weeks" \
  --output-schema '{
    "type": "object",
    "properties": {
      "jobs": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "title": {"type": "string"},
            "company": {"type": "string"},
            "location": {"type": "string"},
            "description": {"type": "string"},
            "posted_date": {"type": "string"},
            "job_url": {"type": "string"}
          }
        }
      }
    }
  }' \
  --wait \
  --output ml_jobs.json
```

### Example 5: Google Maps Business Search

**User request**: "Find coffee shops in Seattle"

**Solution**:
```bash
monid search \
  --name "Seattle Coffee Shops" \
  --query "Find all coffee shops in Seattle with ratings, reviews, and contact information" \
  --output-schema '{
    "type": "object",
    "properties": {
      "businesses": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "address": {"type": "string"},
            "phone": {"type": "string"},
            "website": {"type": "string"},
            "rating": {"type": "number"},
            "review_count": {"type": "number"}
          }
        }
      }
    }
  }' \
  --wait \
  --output seattle_coffee.json
```

## Output Schema Guidelines

A good output schema:
1. **Defines structure clearly**: Use nested objects and arrays appropriately
2. **Matches data type**: Use correct JSON schema types (string, number, boolean, array, object)
3. **Is realistic**: Don't expect data that the scraper can't provide
4. **Uses descriptive property names**: Clear, snake_case or camelCase names

**Example schema template**:
```json
{
  "type": "object",
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "field1": {"type": "string"},
          "field2": {"type": "number"},
          "nested_object": {
            "type": "object",
            "properties": {
              "sub_field": {"type": "string"}
            }
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "total_count": {"type": "number"},
        "scraped_at": {"type": "string"}
      }
    }
  }
}
```

## Important Constraints and Limitations

### Platform Limitations
- **Rate limiting**: Platforms may have rate limits; Monid handles retries automatically
- **Authentication**: Some data requires platform login (handled by scrapers where possible)
- **Public data only**: Can only access publicly available data
- **Real-time limits**: Data freshness depends on platform and scraper performance

### Query Limitations
- **Be specific**: Vague queries may produce unexpected results
- **Use realistic limits**: Request reasonable amounts (e.g., "top 100" not "all tweets ever")
- **Include timeframes**: Specify date ranges when relevant
- **Provide context**: Include keywords, hashtags, URLs, or usernames as needed

### What Monid CANNOT Do
- ❌ Scrape platforms not in the supported list
- ❌ Access private accounts or authenticated content (unless user provides credentials)
- ❌ Bypass platform rate limits or ToS restrictions
- ❌ Guarantee 100% data completeness (platforms may block or limit scrapers)
- ❌ Real-time streaming (it's batch-based scraping)

## Pricing and Cost Management

- **Quote first**: Always get a quote before execution to show user the cost
- **Costs vary**: Different scrapers have different per-call costs
- **Wait for confirmation**: Use `--yes` flag only when user explicitly agrees to cost
- **Monitor spending**: Users can view usage in the dashboard

**Example with cost confirmation**:
```bash
# Get quote first
monid search \
  --name "Test Search" \
  --query "..." \
  --output-schema '...'
# CLI will show price and ask for confirmation
# Press 'y' to proceed or 'n' to cancel
```

## Troubleshooting

### "Authentication expired"
**Solution**: `monid auth login`

### "No active key"
**Solution**: `monid keys generate --label main` then `monid keys activate main`

### "Task not found" or "Quote expired"
**Solution**: Quotes expire after 1 hour. Create a new quote or execute immediately with `--wait`

### "Execution failed"
**Possible causes**:
- Invalid query (too vague or requesting unavailable data)
- Platform blocked the scraper (temporary, retry later)
- Invalid output schema (doesn't match actual data structure)

**Solution**: Check execution details with `monid executions get --execution-id <id>` for error messages

### "Invalid JSON schema"
**Solution**: Validate JSON syntax, ensure proper structure, use online JSON schema validators

## Best Practices

1. **Start with small tests**: Test with small data requests (e.g., "top 10") before scaling up
2. **Use descriptive names**: Name tasks clearly for future reference
3. **Save results immediately**: Always use `--output` to avoid losing data
4. **Check prices first**: Review quotes before confirming execution
5. **Reuse tasks**: Create reusable tasks for repeated workflows
6. **Monitor executions**: Use `--wait` for immediate results, or check status later
7. **Structure queries well**: Be specific about what you want, include filters (date, location, keywords)
8. **Design realistic schemas**: Match schema to actual data structure scrapers provide

## Workflow Decision Tree

When a user asks for data collection:

1. **Is the platform supported?**
   - NO → Inform user Monid doesn't support that platform
   - YES → Continue

2. **Is Monid CLI installed?**
   - Don't know → Ask user to run `monid --version`
   - NO → Guide through installation: `curl -fsSL https://raw.githubusercontent.com/FeiyouG/monid-client/main/install.sh | bash`
   - YES → Continue

3. **Is user authenticated?**
   - Don't know → Ask user to run `monid auth whoami`
   - NO → Guide through authentication:
     1. `monid auth login` (browser opens for OAuth)
     2. `monid keys generate --label main`
     3. Verify with `monid auth whoami`
   - YES → Continue

4. **Is this a one-time or repeated task?**
   - One-time → Use `monid search --name --query --output-schema`
   - Repeated → Create task with `monid tasks create`, then reference with `--task-id`

5. **Execute with appropriate flags**:
   - Add `--wait` for immediate results
   - Add `--output` to save results
   - Add `--yes` if user pre-approved cost

6. **Monitor and deliver**:
   - If using `--wait`, results appear automatically
   - If not, guide user to check status with `monid executions get`

## Summary

Monid enables agents and LLMs to help users collect data from social media, e-commerce, and search platforms through a simple CLI workflow:

1. **Install CLI** (one-time): `curl -fsSL https://raw.githubusercontent.com/FeiyouG/monid-client/main/install.sh | bash`
2. **Authenticate** (one-time): `monid auth login` + `monid keys generate --label main`
3. **Execute searches**: Use natural language queries with structured output schemas
4. **Monitor results**: Track execution status and download data
5. **Stay within bounds**: Only use supported capabilities, be specific in queries

When helping users, always:
- Check if CLI is installed (ask for `monid --version`)
- Verify the platform is supported
- Guide through installation and authentication if needed
- Craft specific, detailed queries
- Design realistic output schemas
- Show costs before execution
- Save results to files

**Remember**: Monid is for **supported platforms only**. Never suggest capabilities outside the explicitly listed ones in this skill.
