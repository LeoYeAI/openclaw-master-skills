# Focus Modes - Complete Guide

Nimble Search provides 8 specialized focus modes, each optimized with different ranking algorithms, source preferences, and result filtering to match specific query types.

## Mode Selection Decision Tree

```
Is this a programming/technical question?
├─ YES → coding
│
└─ NO → Is this time-sensitive or about current events?
    ├─ YES → news
    │
    └─ NO → Is this academic/scientific?
        ├─ YES → academic
        │
        └─ NO → Is this about products/shopping?
            ├─ YES → shopping
            │
            └─ NO → Is this about social media/community?
                ├─ YES → social
                │
                └─ NO → Is this about a location/place?
                    ├─ YES → location
                    │
                    └─ NO → Is this geographic/regional?
                        ├─ YES → geo
                        │
                        └─ NO → general
```

## Detailed Mode Reference

### 1. General Mode

**Best for:** Broad web searches, informational queries, general knowledge

**Characteristics:**
- Balanced ranking across diverse sources
- Includes websites, blogs, forums, documentation
- No specific source preference
- Good for exploratory searches

**Source Types:**
- General websites
- Blogs and articles
- Wikipedia and knowledge bases
- Documentation sites
- Forums and Q&A sites

**Example Queries:**
- "How does photosynthesis work"
- "History of the Roman Empire"
- "Best practices for remote work"
- "Explanation of blockchain technology"
- "Tips for learning a new language"

**When to Use:**
- Topic overviews
- General information gathering
- Exploratory research
- Multi-domain queries
- Unclear categorization

**Performance:**
- Response Time: Fast (1-2 seconds)
- Result Quality: Balanced
- Source Diversity: High

---

### 2. Coding Mode

**Best for:** Programming questions, technical documentation, code examples

**Characteristics:**
- Prioritizes technical content
- Ranks Stack Overflow, GitHub, dev blogs highly
- Filters for code-related content
- Optimized for technical accuracy

**Source Types:**
- Stack Overflow
- GitHub repositories
- Official documentation
- Dev.to, Medium technical blogs
- API references
- Programming tutorials

**Example Queries:**
- "React Server Components example"
- "How to implement async/await in Python"
- "TypeScript generic constraints tutorial"
- "Best practices for REST API design"
- "Docker compose multi-container setup"
- "JavaScript promise error handling"

**When to Use:**
- Programming questions
- Code examples needed
- Technical documentation
- API usage help
- Framework/library research
- Bug troubleshooting

**Performance:**
- Response Time: Fast (1-2 seconds)
- Result Quality: High for technical content
- Source Diversity: Medium (focused on dev platforms)

**Pro Tips:**
- Include language/framework name in query
- Be specific about version if relevant
- Add "example" or "tutorial" for code samples
- Use "best practices" for architectural guidance

---

### 3. News Mode

**Best for:** Current events, breaking news, recent announcements

**Characteristics:**
- Prioritizes recent content (hours to days old)
- Ranks news sites and publications highly
- Temporal relevance is primary factor
- Filters for journalistic content

**Source Types:**
- News websites (CNN, BBC, Reuters, etc.)
- Tech news (TechCrunch, The Verge, Ars Technica)
- Industry publications
- Press releases
- News aggregators

**Example Queries:**
- "Latest developments in artificial intelligence"
- "Recent quantum computing breakthroughs"
- "Today's stock market analysis"
- "Breaking news about space exploration"
- "Recent changes to privacy regulations"

**When to Use:**
- Current events research
- Breaking news monitoring
- Trending topic analysis
- Recent announcements
- Time-sensitive information
- Market updates

**Performance:**
- Response Time: Medium (2-3 seconds)
- Result Quality: High for recent content
- Recency: Excellent (hours to days)

**Pro Tips:**
- Use date filters for precise timeframes
- Add "latest", "recent", "breaking" to queries
- Specify timeframe (e.g., "last 24 hours")
- Check published dates in results

---

### 4. Academic Mode

**Best for:** Scholarly research, scientific papers, academic resources

**Characteristics:**
- Prioritizes peer-reviewed content
- Ranks academic databases highly
- Filters for scholarly writing
- Emphasizes citations and references

**Source Types:**
- Google Scholar
- ArXiv preprints
- PubMed articles
- University websites
- Research institution publications
- Academic journals

**Example Queries:**
- "Machine learning interpretability methods"
- "Climate change impact on biodiversity"
- "Quantum entanglement research papers"
- "Cognitive behavioral therapy effectiveness studies"
- "Neural network architecture comparisons"

**When to Use:**
- Research paper discovery
- Literature reviews
- Scientific evidence gathering
- Academic citations needed
- Peer-reviewed content required
- Scholarly analysis

**Performance:**
- Response Time: Medium (2-4 seconds)
- Result Quality: Very High (peer-reviewed)
- Source Authority: Excellent

**Pro Tips:**
- Include scientific terminology
- Add research keywords (study, analysis, review)
- Specify field/domain for better results
- Use author names if known
- Include year range for temporal filtering

---

### 5. Shopping Mode

**Best for:** Product searches, price comparisons, e-commerce research

**Characteristics:**
- Prioritizes e-commerce sites
- Includes product specifications
- Filters for shopping-relevant content
- May include pricing information

**Source Types:**
- E-commerce sites (Amazon, eBay, etc.)
- Retailer websites
- Product review sites
- Price comparison tools
- Shopping aggregators

**Example Queries:**
- "Best mechanical keyboards for programming"
- "Affordable noise-canceling headphones"
- "Standing desk reviews and comparisons"
- "Laptop recommendations for video editing"
- "Ergonomic office chair options"

**When to Use:**
- Product research
- Price comparison
- Shopping recommendations
- Product reviews
- Spec comparisons
- Purchase decisions

**Performance:**
- Response Time: Medium (2-3 seconds)
- Result Quality: High for products
- Price Accuracy: Varies by source

**Pro Tips:**
- Include product category
- Add specifications (size, features)
- Use "best", "top", "affordable" for recommendations
- Specify use case for targeted results
- Add "review" for detailed analysis

---

### 6. Social Mode

**Best for:** Social media content, community discussions, trending topics

**Characteristics:**
- Prioritizes social platforms
- Includes real-time content
- Filters for user-generated content
- Captures community sentiment

**Source Types:**
- Twitter/X posts
- Reddit discussions
- LinkedIn content
- YouTube videos
- Facebook posts (public)
- TikTok (where accessible)

**Example Queries:**
- "Twitter reactions to new AI announcement"
- "Reddit discussions about remote work"
- "Social media trends in 2026"
- "Community feedback on latest iPhone"
- "Viral posts about climate action"

**When to Use:**
- Social media monitoring
- Public sentiment analysis
- Trending topic discovery
- Community discussions
- User opinions and reactions
- Viral content research

**Performance:**
- Response Time: Medium (2-4 seconds)
- Result Quality: Variable (user-generated)
- Recency: Excellent (real-time)

**Pro Tips:**
- Include platform name if targeting specific network
- Use hashtags in queries
- Add "trending" for popular content
- Specify topic for focused results
- Check timestamps for recency

---

### 7. Geo Mode

**Best for:** Geographic information, regional data, area-specific queries

**Characteristics:**
- Prioritizes geographic content
- Includes maps and location data
- Filters for regional relevance
- Emphasizes spatial information

**Source Types:**
- Geographic databases
- Government websites
- Regional information sites
- Travel resources
- Local news (for area context)

**Example Queries:**
- "Population density of European cities"
- "Climate patterns in Pacific Northwest"
- "Geographic features of Sahara Desert"
- "Regional economic data for Southeast Asia"
- "Topography of Himalayan mountain range"

**When to Use:**
- Geographic research
- Regional data gathering
- Area comparisons
- Spatial analysis
- Environmental studies
- Demographic research

**Performance:**
- Response Time: Medium (2-3 seconds)
- Result Quality: High for geographic data
- Geographic Accuracy: Excellent

**Pro Tips:**
- Include specific location names
- Add geographic terms (region, area, zone)
- Specify data type (population, climate, etc.)
- Use proper place names
- Add context (urban, rural, coastal, etc.)

---

### 8. Location Mode

**Best for:** Local business searches, place-specific information, nearby services

**Characteristics:**
- Prioritizes local businesses
- Includes address and contact info
- Filters for place-specific content
- Emphasizes proximity and relevance

**Source Types:**
- Google Maps data
- Business directories
- Review platforms (Yelp, TripAdvisor)
- Local websites
- Business listings

**Example Queries:**
- "Italian restaurants in downtown Seattle"
- "Yoga studios near Central Park"
- "Bookstores in San Francisco Bay Area"
- "Coffee shops with WiFi in Austin"
- "Hiking trails near Denver"

**When to Use:**
- Local business discovery
- Place recommendations
- Nearby services
- Location-specific info
- Business contact details
- Review aggregation

**Performance:**
- Response Time: Medium (2-4 seconds)
- Result Quality: High for local content
- Location Accuracy: Excellent

**Pro Tips:**
- Include specific location (city, neighborhood)
- Add business type or category
- Use "near", "in", "around" for location context
- Specify features (WiFi, parking, outdoor seating)
- Add "reviews" for ratings and feedback

---

## Mode Comparison Table

| Mode | Best Use Case | Speed | Source Focus | Recency Weight | Depth |
|------|--------------|-------|--------------|----------------|-------|
| general | Broad searches | Fast | Diverse | Medium | Medium |
| coding | Programming | Fast | Dev platforms | Low | High |
| news | Current events | Medium | News sites | Very High | Medium |
| academic | Research | Medium | Scholarly | Low | Very High |
| shopping | Products | Medium | E-commerce | Medium | Medium |
| social | Social media | Medium | Social platforms | Very High | Low |
| geo | Geographic data | Medium | Geographic | Low | High |
| location | Local business | Medium | Business listings | Medium | Medium |

## Combining Focus Modes

For complex research tasks, consider sequential searches with different focus modes:

**Example: Comprehensive AI Framework Research**

1. **coding** - "AI agent frameworks comparison" → Technical details
2. **news** - "recent AI agent framework releases" → Latest developments
3. **academic** - "autonomous agent architecture research" → Theoretical foundations
4. **social** - "developer opinions on AI frameworks" → Community feedback

**Example: Product Research**

1. **shopping** - "4K monitors for programming" → Product options
2. **coding** - "optimal monitor setup for developers" → Technical requirements
3. **social** - "Reddit recommendations for programming monitors" → User experiences

## Advanced Tips

### Mode-Specific Query Optimization

**For coding mode:**
- Include framework/library versions
- Add error messages for debugging
- Use technical jargon freely
- Specify programming language

**For news mode:**
- Add temporal keywords (today, recent, latest)
- Include industry/sector for focused results
- Use headline-style phrasing
- Specify geographic region if relevant

**For academic mode:**
- Use precise scientific terminology
- Include methodology keywords (meta-analysis, RCT, etc.)
- Add author names if known
- Specify publication timeframe

**For shopping mode:**
- Include budget constraints (affordable, premium)
- Add use case (for gaming, for travel, etc.)
- Specify key features
- Use comparison keywords (vs, versus, compared to)

### When Multiple Modes Apply

If a query could fit multiple modes:

1. **Start with the most specific mode** (e.g., coding over general)
2. **Consider your primary need** (code example → coding; recent news → news)
3. **Try both modes** if results are unsatisfactory
4. **Use general mode** only as fallback

### Testing and Iteration

- **Test focus mode impact**: Run same query with different modes
- **Compare result quality**: Evaluate relevance and usefulness
- **Adjust based on results**: Switch modes if needed
- **Document patterns**: Note which modes work best for your use cases

## Mode-Specific Limitations

**General Mode**
- May lack depth in specialized topics
- Diverse results can dilute relevance
- Less optimized for any specific domain

**Coding Mode**
- May miss non-technical context
- Limited for theoretical computer science
- Best for practical programming, not algorithms research

**News Mode**
- Historical events get low relevance
- Academic papers ranked lower
- Optimized for recency over depth

**Academic Mode**
- Slower than other modes
- May be too formal for practical guides
- Limited access to paywalled content

**Shopping Mode**
- Affiliate content may dominate
- Price info may be outdated
- Review authenticity varies

**Social Mode**
- Content quality highly variable
- May include misinformation
- Context often missing
- Temporal context critical

**Geo Mode**
- Less relevant for local businesses
- May be too broad for specific places
- Better for regions than addresses

**Location Mode**
- Requires location context
- Business info may be outdated
- Limited to public listings
- Reviews may not be current

## Conclusion

Choosing the right focus mode is crucial for search quality. When in doubt:

1. Start with the most specific relevant mode
2. Use general mode as a fallback
3. Try 2-3 modes for important research
4. Document what works for your use cases

The investment in choosing the right focus mode pays dividends in result relevance and research efficiency.
