# AI Platforms Deep Dive

Extended reference on how each AI platform handles local business queries and how to optimize for each.

---

## Platform Comparison Overview

| Platform | Data Sources | Update Frequency | Local Pack Display | Tracked by Local Falcon |
|----------|--------------|------------------|-------------------|------------------------|
| Google AI Overviews | GBP, web, reviews, third-party sites | Real-time | Mobile: Embedded / Desktop: Below | ✅ Yes |
| Google AI Mode | GBP, web, reviews, third-party sites | Real-time | Map at end only | ✅ Yes |
| Google Gemini | Training data + live web | Mixed | May redirect to Search/Maps | ✅ Yes |
| ChatGPT | Bing, Foursquare, Yelp, BBB | Real-time web search | Mapbox-powered | ✅ Yes |
| Grok | X/Twitter + web search | Real-time | Varies | ✅ Yes |
| Perplexity | Multi-source web search | Real-time | Inline citations | ❌ Not tracked |

---

## Google AI Overviews (GAIO) - Extended

### Trigger Conditions
- Shows for ~97% of hybrid-intent queries
- Only ~7% of pure local searches
- Google determines when it's "additive" to user experience

### Citation Sources (Research Data)
- **60% from third-party publishers:** Reddit (7.4%), Yelp, Quora, Thumbtack, HomeGuide, industry forums
- **40% from individual business sites:** Direct website content
- **Only 33% from top 10 organic:** Being in traditional top 10 doesn't guarantee AIO citation
- **46% from outside top 50:** Sites you've never heard of may be cited

### Mobile vs Desktop Behavior (CRITICAL)

**Mobile Experience:**
```
┌─────────────────────────────┐
│   AI Overview Response      │
│                             │
│ [Small Map + 3 GBP Listings]│  ← Local Pack INSIDE AI response
│                             │
│   More AI text...           │
└─────────────────────────────┘
│   Traditional results...    │
```

**Desktop Experience:**
```
┌─────────────────────────────┐
│   AI Overview Response      │
│                             │
│   Natural language prose    │  ← Businesses mentioned in text
│   mentioning businesses...  │
│                             │
└─────────────────────────────┘
┌─────────────────────────────┐
│   Traditional Local Pack    │  ← Separate element below
│   [Map + 3 listings]        │
└─────────────────────────────┘
│   Organic results...        │
```

### Optimization Priorities
1. **Google Business Profile:** Primary structured data (32% weight)
2. **Review keywords:** AI extracts themes from review text
3. **Third-party mentions:** Get cited on Reddit, Yelp, Quora, industry sites
4. **NAP consistency:** Must match across all directories
5. **Structured data:** LocalBusiness schema on website

### CTR Impact
- CTR drops 34.5% when AI Overview present
- Users often get answer without clicking
- Strategy: Be IN the AI Overview, not competing below it

---

## Google AI Mode - Extended

### Fundamental Difference
AI Overviews = **Supplement** traditional results
AI Mode = **Replace** traditional results entirely

**If you're not cited in AI Mode, you're invisible.** There are no backup organic results.

### Query Processing
1. User enters query
2. Google issues up to **16 simultaneous searches** (query fan-out)
3. Breaks query into logical sub-questions
4. Searches each sub-query across sources
5. Gemini synthesizes comprehensive answer
6. Much longer/deeper than AI Overviews

### Local Pack Transformation
- Traditional 3-pack visual **disappears entirely**
- Map appears at **end of response** instead
- GBP data still heavily influences the response
- Interactions open GBP panel (if mentioned)

### Unique AI Mode Features
- **Conversational:** Follow-up questions maintain context
- **Multimodal:** Voice input, image/PDF input
- **Agentic:** Can find reservations, check availability, even CALL businesses for pricing
- **Personalized:** Uses search history, Gmail, Photos (if opted in)

### Optimization Strategy
- All GBP optimization from AI Overviews applies
- Content must be clear enough for AI extraction
- Focus on being THE definitive answer for category
- Consider voice-readability (AI may speak answers)

---

## Google Gemini (Standalone) - Extended

### Product Positioning
"Gemini is the brain; AI Mode is its application in Search."

Gemini is Google's full AI assistant platform - not primarily a search tool.

### How It Handles Local Queries
- Can browse web in real-time
- May **redirect** users to Search or Maps for local queries
- Pulls from training data + live browsing
- Less search-focused, more task-oriented

### When Users Get Local Results
- Direct "find me a plumber" → May redirect to Search
- Conversational "what should I look for in a plumber?" → General advice
- Specific "is ABC Plumbing any good?" → May search for reviews/info

### Optimization Approach
- Ensure business info widely cited on authoritative sources
- Focus on being in training data (Wikipedia, major publications)
- Less direct optimization path than Search products
- Brand mentions in content Gemini would index

---

## ChatGPT - Extended

### Critical Architecture Insight
**ChatGPT does NOT access Google at all.**

This is the most misunderstood aspect of ChatGPT local optimization. Businesses optimized only for Google may be invisible to ChatGPT.

### Data Source Hierarchy

| Source | Function | Priority |
|--------|----------|----------|
| **Bing Places for Business** | Primary structured local data | Claim immediately |
| **Foursquare** | major source of name, address, photos, ratings | Critical |
| **Mapbox** | Powers visual map output | Indirect |
| **Yelp** | Trusted review source | High |
| **BBB** | Trust/verification signal | High |
| **TripAdvisor** | Especially for hospitality | High |
| **Editorial Lists** | Eater, Time Out, local "best of" | Very influential |

### How Bing Integration Works
1. ChatGPT runs Bing search in real-time
2. Scans top 20-30 web results
3. Selects content based on **its own criteria** (not Bing's rankings)
4. Uses Bing for 92% of live web searches
5. Small overlap between Bing rankings and what ChatGPT actually cites

### Optimization Checklist
- [ ] Claim Bing Places for Business
- [ ] Claim/update Foursquare listing (name, hours, photos, categories)
- [ ] Keep Yelp profile active with responses
- [ ] BBB accreditation if applicable
- [ ] TripAdvisor for restaurants/hotels
- [ ] Pursue editorial "best of" list features
- [ ] NAP consistency across ALL directories (not just Google ecosystem)

---

## Grok - Extended

### Unique Data Access
Grok has exclusive real-time access to X/Twitter public posts. No other major LLM has this.

### How It Processes Queries
1. Analyzes query intent
2. Decides: search X posts AND/OR web search
3. If X: Analyzes relevant posts, trends, sentiment
4. If web: Standard search synthesis
5. Often combines both for local queries

### X/Twitter Data Influence
- Your tweets become part of potential answers
- Customer mentions of your business matter
- Local community engagement signals relevance
- Real-time sentiment affects recommendations
- Trending local topics can trigger visibility

### Potential Issues
- X data can be messy, inaccurate, or biased
- Grok may pick up and repeat misinformation
- Negative viral tweets can impact recommendations
- Less structured than traditional business directories

### Optimization Strategy
1. **Active X presence:** Regular posts about your business, industry, community
2. **Community engagement:** Reply to local conversations, retweet relevant content
3. **Customer encouragement:** Ask satisfied customers to mention you on X
4. **Brand monitoring:** Track mentions, respond to both positive and negative
5. **Standard web presence:** Grok also searches web, so traditional optimization still matters

### Industries Where X Matters Most
- Restaurants/bars (heavy X/Twitter user base)
- Entertainment venues
- News-adjacent businesses
- Tech-forward brands
- Anything targeting younger demographics

---

## Perplexity AI - Extended (Awareness Only)

**Note:** Local Falcon does not currently track Perplexity. Included for strategic awareness.

### How It Differs
- "Answer engine" vs. "chat assistant"
- Shows **exactly** which sources it cites (numbered inline)
- Users can click directly to source
- Smaller, more selective index than Google
- Heavily favors established, high-authority content

### What Gets Cited
- Wikipedia and government sites
- Expert blogs and industry publications
- Reddit threads and YouTube transcripts
- Original research and comprehensive guides
- Well-structured how-to content
- Niche forums with expert discussions

### What Gets Skipped
- Thin content (< 500 words on a topic)
- Promotional/sales-focused material
- Outdated information
- Paywalled content
- Low-authority domains

### Optimization Approach
1. NAP consistency across directories (foundational)
2. Active profiles on Google Business, Yelp, industry directories
3. Customer reviews on Google, Trustpilot, G2
4. Presence on Reddit, relevant forums, YouTube
5. Comprehensive, well-structured content (expert guides)
6. Original research in your industry

---

## Cross-Platform Strategy Summary

### Must-Do for All Platforms
1. **NAP Consistency:** Name, Address, Phone must match everywhere
2. **Claim all profiles:** GBP, Bing Places, Foursquare, Yelp, BBB, TripAdvisor
3. **Active review management:** Generate reviews, respond to all
4. **Structured data:** LocalBusiness schema on website

### Platform-Specific Priorities

| If optimizing for... | Focus on... |
|---------------------|-------------|
| Google AI Overviews | GBP, reviews with keywords, Reddit/Yelp mentions |
| Google AI Mode | Same as above + voice-readable content |
| ChatGPT | Bing Places, Foursquare (critical), editorial lists |
| Grok | X/Twitter presence, community engagement, brand monitoring |
| Perplexity | Expert content, Reddit presence, comprehensive guides |

---

*For tracking your SAIV across these platforms, use Local Falcon's AI Visibility scans.*
