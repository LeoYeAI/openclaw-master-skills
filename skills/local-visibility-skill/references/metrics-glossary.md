# Local Falcon Metrics Glossary

Complete reference for all metrics used in Local Falcon reports and analysis.

---

## Map-Based Metrics

### ATRP (Average Total Rank Position)
- **Definition:** Average ranking across ALL grid points in the scan
- **Range:** 1-20+ (lower is better)
- **Use Case:** Primary metric for overall visibility health
- **Interpretation:**
  - 1-3: Excellent (dominating the area)
  - 4-7: Good (competitive but room to improve)
  - 8-12: Moderate (appearing but often below fold)
  - 13+: Poor (rarely seen by searchers)

### ARP (Average Rank Position)
- **Definition:** Average rank only for grid points WHERE the business appears
- **Difference from ATRP:** Excludes points where business doesn't show at all
- **Use Case:** Understanding ranking quality when you DO show up
- **Insight:** If ARP is much better than ATRP, you rank well where you appear but have coverage gaps

### SoLV (Share of Local Voice)
- **Definition:** Percentage of pins in top 3 positions on Google Maps or Apple Maps
- **Range:** 0-100%
- **Use Case:** Standard map pack analysis ONLY (not AI platforms)
- **CRITICAL:** NEVER confuse with SAIV - this is maps-only
- **Benchmarks:** Varies significantly by market competitiveness

### Competition SoLV
- **Definition:** Count of competitors with any SoLV score higher than 0.00
- **Use Case:** Assessing market saturation and competitive difficulty
- **Note:** High Competition SoLV doesn't mean equal distribution - one competitor may dominate

### Max SoLV
- **Definition:** Highest SoLV score achieved by any business in the report
- **Use Case:** Establishing ceiling for visibility potential in this market
- **Caution:** Don't assume it's easily achievable - top performer may have structural advantages (location, age, reviews)

### Opportunity SoLV
- **Definition:** Gap between your SoLV and Max SoLV (Max SoLV − Your SoLV)
- **Use Case:** Quantifying realistic growth potential
- **Note:** Some gaps may be constrained by proximity - not all opportunity is capturable

### SoLV Distance
- **Definition:** Distance from business to grid points where it ranks 1-3
- **Use Case:** Understanding geographic reach of top rankings
- **Insight:** Varies by keyword competitiveness and business type

### Average SoLV Distance
- **Definition:** Average distance across all top-3 ranking grid points
- **Use Case:** Benchmarking geographic reach against competitors
- **Best Practice:** Compare with SoLV percentage for full picture

### Found In
- **Definition:** Count of grid points where business appears in results
- **Use Case:** Measuring geographic coverage
- **Warning:** High "Found In" with poor ATRP is worse than lower "Found In" with good ATRP

### Total Competitors
- **Definition:** Unique businesses appearing anywhere in results (excluding your business)
- **Use Case:** Understanding total market density
- **Note:** Different from Competition SoLV (which is top-3 only)

### Distance from Data Point
- **Definition:** Distance between business and a specific grid point
- **Use Case:** Analyzing proximity influence at specific locations
- **Insight:** Identical distances can produce different rankings due to other factors

### Distance from Center Point
- **Definition:** Distance between business and center-most grid point
- **Use Case:** Establishing baseline proximity context
- **Note:** Center point is based on scan setup, not necessarily the commercial center

---

## AI Visibility Metrics

### SAIV (Share of AI Visibility)
- **Definition:** Percentage of AI results that mention the business
- **Platforms:** ChatGPT, Google AI Overviews, Gemini, AI Mode, Grok
- **Range:** 0-100%
- **CRITICAL:** NEVER confuse with SoLV - this is AI-only, completely separate measurement
- **Interpretation:** What % of times someone asks an AI about your category/area does it mention you?

---

## Review Metrics

### Review Volume Score (RVS)
- **Definition:** Composite metric evaluating quantitative strength of review profile
- **Components:** Total count, velocity, distribution over time
- **Use Case:** Assessing review acquisition health

### Review Velocity
- **Definition:** Average reviews received per month over last 90 days
- **Use Case:** Diagnosing recent review momentum
- **Why It Matters:** Google weighs recent reviews more heavily

### Total Reviews
- **Definition:** Cumulative count of all Google reviews
- **Use Case:** Understanding established authority
- **Context:** Compare against local competitors, not national averages

### Review Quality Score (RQS)
- **Definition:** Composite of rating distribution, response engagement, recency
- **Use Case:** Assessing reputation management beyond just quantity
- **Components:**
  - Star rating distribution
  - Owner response rate
  - Response timeliness
  - Review freshness

### Review Freshness
- **Definition:** Recency-weighted score based on when reviews were received
- **Use Case:** Identifying stale review profiles
- **Risk:** A business with 500 reviews but none in 6 months may be declining

### Rating
- **Definition:** Average star rating (1.0-5.0)
- **Use Case:** Quick reputation snapshot
- **Note:** 4.0-4.5 often performs better than 5.0 (authenticity perception)

### Unresponded to Reviews
- **Definition:** Count of reviews without owner response
- **Use Case:** Identifying engagement gaps
- **Best Practice:** Respond to ALL reviews (positive and negative)

### Reviews by Local Guides
- **Definition:** Reviews from Google Local Guide program members
- **Use Case:** Assessing credibility signals
- **Why It Matters:** Local Guide reviews may carry more weight

### Reviews with Photos
- **Definition:** Reviews that include customer-uploaded photos
- **Use Case:** Visual social proof assessment
- **Why It Matters:** Photo reviews demonstrate authentic customer experiences

---

## GBP Performance Metrics (via Falcon Guard with Google oAuth)

### Impressions
- **Definition:** Number of times your GBP was viewed
- **Sources:** Search results, Maps, Discovery
- **Use Case:** Visibility trend tracking

### Calls
- **Definition:** Clicks on the call button in your GBP
- **Use Case:** Direct lead measurement
- **Note:** Only tracks clicks, not completed calls

### Website Clicks
- **Definition:** Clicks on the website URL in your GBP
- **Use Case:** Traffic referral measurement

### Directions
- **Definition:** Navigation/directions requests from your GBP
- **Use Case:** Foot traffic intent measurement
- **Insight:** High directions + low visits may indicate location confusion

---

## Metric Relationships

### ATRP vs ARP
- **If ARP << ATRP:** You rank well where you appear but have major coverage gaps
- **If ARP ≈ ATRP:** Consistent performance (good or bad) across the grid

### SoLV vs Found In
- **High SoLV, Low Found In:** Dominating a small area
- **Low SoLV, High Found In:** Wide coverage but not in top 3

### SAIV vs SoLV
- **High SoLV, Low SAIV:** Strong on maps, weak on AI platforms (citation gap)
- **High SAIV, Low SoLV:** AI mentions you but map rankings need work
- **Both High:** Comprehensive visibility
- **Both Low:** Significant optimization opportunity

---

*For personalized metric analysis, connect the Local Falcon MCP server or use Falcon Agent.*
