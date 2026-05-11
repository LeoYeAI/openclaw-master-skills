# Local Falcon MCP Workflows

Complete reference for using Local Falcon's MCP server tools for automated local SEO analysis.

---

## MCP Server Overview

**Package:** `@local-falcon/mcp`
**Installation:** `npm install @local-falcon/mcp`
**Documentation:** [docs.localfalcon.com](https://docs.localfalcon.com)

The MCP server wraps Local Falcon's API endpoints with developer-friendly tool names, enabling AI agents to pull real data and perform analysis.

---

## API Fundamentals

**Base URL:** `https://api.localfalcon.com`

**Authentication:** All endpoints require an `api_key` parameter. Manage keys at [localfalcon.com/api/credentials/](https://www.localfalcon.com/api/credentials/)

**Platform Options:** `google`, `apple`, `chatgpt`, `gemini`, `grok`, `aimode`, `gaio` (Google AI Overviews)

---

## Complete Tool Reference

### Account & Location Management

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `viewLocalFalconAccountInformation` | Get account info, credits, subscription status | - |
| `listAllLocalFalconLocations` | List all saved locations in account | `limit`, `next_token` |
| `searchForLocalFalconBusinessLocation` | Search Google/Apple for businesses | `query`, `platform` |
| `saveLocalFalconBusinessLocationToAccount` | Save location for tracking | `place_id`, `platform` |

### Scan Reports

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `listLocalFalconScanReports` | List all scan reports | `place_id`, `keyword`, `platform`, `start_date`, `end_date` |
| `getLocalFalconReport` | Get specific scan report | `report_key` |
| `runLocalFalconScan` | Execute new scan (uses credits) | `place_id`, `keyword`, `grid_size`, `platform`, `ai_analysis` |

### Campaign Management

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `listLocalFalconCampaignReports` | List all campaigns | `limit`, `next_token` |
| `getLocalFalconCampaignReport` | Get specific campaign data | `campaign_key` |
| `createLocalFalconCampaign` | Create new scheduled campaign | `name`, `place_ids`, `keywords`, `schedule` |
| `runLocalFalconCampaign` | Trigger campaign immediately | `campaign_key` |
| `pauseLocalFalconCampaign` | Pause scheduled runs | `campaign_key` |
| `resumeLocalFalconCampaign` | Resume paused campaign | `campaign_key` |
| `reactivateLocalFalconCampaign` | Reactivate after credit issue | `campaign_key` |

### Trend & Competitor Analysis

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `listLocalFalconTrendReports` | List trend reports | `place_id`, `keyword` |
| `getLocalFalconTrendReport` | Get historical trend data | `trend_key` |
| `getLocalFalconCompetitorReports` | List competitor reports | `place_id` |
| `getLocalFalconCompetitorReport` | Get specific competitor analysis | `report_key` |

### Aggregated Reports

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `listLocalFalconLocationReports` | List by location (multi-keyword roll-up) | `limit` |
| `getLocalFalconLocationReport` | Get location aggregate | `location_key` |
| `listLocalFalconKeywordReports` | List by keyword (multi-location roll-up) | `limit` |
| `getLocalFalconKeywordReport` | Get keyword aggregate | `keyword_key` |

### Reviews Analysis

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `listLocalFalconReviewsAnalysisReports` | List reviews analysis reports | `place_id` |
| `getLocalFalconReviewsAnalysisReport` | Get detailed review analysis | `report_key` |

### Falcon Guard (GBP Monitoring)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `listLocalFalconGuardReports` | List monitored locations | `limit` |
| `getLocalFalconGuardReport` | Get specific monitoring report | `place_id` |
| `addLocationsToFalconGuard` | Add locations to monitoring | `place_ids` |
| `pauseFalconGuardProtection` | Pause monitoring | `place_ids` |
| `resumeFalconGuardProtection` | Resume monitoring | `place_ids` |
| `removeFalconGuardProtection` | Remove from monitoring | `place_ids` |

### Auto Scans

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `listLocalFalconAutoScans` | List scheduled recurring scans | `limit` |

---

## AI Analysis Report (CRITICAL)

When running scans via `runLocalFalconScan`, **ALWAYS enable the AI Analysis Report option**.

### What It Provides
- Automated pattern detection
- Competitive diagnosis
- Prioritized recommendations
- Expert-level interpretation of raw metrics

### Implementation
```
WHEN executing runLocalFalconScan:
  - ALWAYS set ai_analysis: true (or equivalent parameter)
  - Default this option to ON unless user explicitly opts out
  - Inform user: "I'm enabling AI Analysis Report for comprehensive insights"
```

### User Communication
> "When we run this scan, I'll enable the AI Analysis Report which gives you automated expert-level insights - pattern detection, competitive diagnosis, and prioritized action items. It's like having a Local SEO consultant analyze your data automatically."

---

## Intelligent Scan Setup (Conversational Approach)

The most common user request is "help me set up a scan." Here's how to do it RIGHT - by gathering context first, not asking generic questions.

### Why This Matters

**DON'T do this:**
```
Agent: "What keywords do you want to track?"
Agent: "What grid size?"
Agent: "What radius?"
```

Users often don't know the answers. These questions without context aren't helpful.

**DO this instead:**
```
Agent: [Uses MCP to pull their business info]
Agent: "I see you're a plumber in Dallas. For plumbers, most customers search
        'plumber near me' or 'emergency plumber'. Want to start with one of those?"
Agent: "Since you're a service area business, we should scan a wider area -
        maybe 10 miles. What's the farthest you'd drive for a job?"
```

### The Right Flow

**Step 1: Pull Context First**
```
listAllLocalFalconLocations → See what they have saved
  ↓
IF saved: Get GBP data (category, address, service areas)
IF not: searchForLocalFalconBusinessLocation → Get Place ID and GBP data
```

**Step 2: Suggest Keywords Based on GBP Category**

| GBP Category | Suggested Keywords |
|--------------|-------------------|
| Plumber | `plumber near me`, `emergency plumber`, `plumbing services` |
| Italian Restaurant | `italian restaurant`, `best pasta near me`, `italian food` |
| HVAC Contractor | `ac repair near me`, `hvac service`, `heating and cooling` |
| Personal Injury Attorney | `personal injury lawyer`, `car accident attorney`, `injury attorney near me` |
| Hair Salon | `hair salon near me`, `haircut`, `best salon` |

**Agent says:** "Your GBP shows you're a [category]. Most customers search for '[primary keyword]' - want to start there, or is there a specific service you want to track?"

**Step 3: Determine Grid Based on Business Type**

| Type | How to Detect | Grid Recommendation |
|------|---------------|---------------------|
| **Storefront** | Has physical address, no service areas | 7x7 or 9x9, 0.5-1mi radius |
| **SAB (Service Area Business)** | Has service areas defined | 13x13+, 3-10mi radius |
| **Hybrid** | Has both address and service areas | Depends - ask about customer behavior |

**Agent says:** "Do customers come to your location, or do you go to them?"

**Step 4: Center Point Logic**

- **Storefronts:** Use business address (automatic)
- **SABs:** Center where customers ARE, not where office is

**Agent says:** "For service businesses, we center the scan where your customers are. Where do you get most of your jobs - any particular neighborhood or part of town?"

**Step 5: Execute with AI Analysis**

```
runLocalFalconScan:
  place_id: [from discovery]
  keyword: [suggested and confirmed]
  platform: google (default) or user's choice
  grid_size: [appropriate for business type]
  grid_distance: [appropriate for service radius]
  ai_analysis: true  ← ALWAYS ENABLE THIS
```

**Agent says:** "Running the scan now with AI Analysis enabled - this will give you expert-level insights automatically."

### Campaign vs Single Scan

**Ask about campaigns when:**
- User has 3+ locations saved
- User mentions "track over time" or "monitor"
- User asks about multiple locations

**Agent says:** "Since you have multiple locations, would you like to set this up as a Campaign? That way it runs automatically on a schedule and you can compare locations."

---

## Standard Workflows

### Workflow 1: Account Health Check

**Purpose:** Quick overview of account status and recent activity

```
1. viewLocalFalconAccountInformation
   → Check credits available, subscription status

2. listAllLocalFalconLocations
   → See all saved locations

3. listLocalFalconCampaignReports
   → Check for active campaigns

4. getLocalFalconCampaignReport (for most recent)
   → Pull latest data for analysis
```

**Output:** Account status summary, location count, campaign health

---

### Workflow 2: New Location Setup & Analysis

**Purpose:** Add new location and run initial visibility scan

```
1. searchForLocalFalconBusinessLocation
   → Search by business name to get Place ID
   → Parameters: query="Business Name City", platform="google"

2. saveLocalFalconBusinessLocationToAccount
   → Save location for ongoing tracking
   → Parameters: place_id from step 1

3. listLocalFalconScanReports
   → Check if any existing scan data
   → Parameters: place_id, limit=5

4. runLocalFalconScan (if no recent scans)
   → Execute initial scan
   → Parameters: place_id, keyword, grid_size, ai_analysis=true
   → ⚠️ ALWAYS enable AI Analysis Report

5. getLocalFalconReport
   → Retrieve and analyze results
   → Parameters: report_key from step 4
```

**Output:** Complete initial visibility assessment with recommendations

---

### Workflow 3: AI Visibility Audit

**Purpose:** Assess visibility across all AI platforms

```
1. listLocalFalconScanReports
   → Find existing AI platform scans
   → Parameters: place_id, platform (cycle through: chatgpt, gemini, grok, aimode, gaio)

2. FOR EACH platform with recent data:
   getLocalFalconReport
   → Pull scan details
   → Extract SAIV score

3. COMPARE across platforms:
   - Which platforms mention the business most?
   - Where are the gaps?
   - Platform-specific patterns?

4. APPLY platform knowledge:
   - ChatGPT weak? → Check Bing Places, Foursquare
   - Grok weak? → Check X/Twitter presence
   - AI Overviews weak? → Check Reddit, Yelp citations
```

**Output:** Cross-platform SAIV comparison with platform-specific recommendations

---

### Workflow 4: Competitive Analysis

**Purpose:** Understand competitive landscape and identify opportunities

```
1. listAllLocalFalconLocations
   → Get target location details

2. getLocalFalconCompetitorReports
   → List available competitor analyses
   → Parameters: place_id

3. getLocalFalconCompetitorReport
   → Pull detailed competitor data
   → Parameters: report_key

4. ANALYZE:
   - Competitor SoLV scores
   - Review counts and ratings
   - Geographic coverage patterns
   - Where competitors are weak

5. IDENTIFY:
   - Opportunity corridors (low competition areas)
   - Review gaps to close
   - Keywords where you can win
```

**Output:** Gap analysis with prioritized actions to improve competitive position

---

### Workflow 5: Trend Analysis

**Purpose:** Track performance changes over time

```
1. listLocalFalconTrendReports
   → Find available trend data
   → Parameters: place_id, keyword

2. getLocalFalconTrendReport
   → Pull historical data
   → Parameters: trend_key

3. ANALYZE:
   - Direction: Improving, declining, or stable?
   - Inflection points: When did changes occur?
   - Correlation: What events match ranking shifts?
   - Seasonality: Predictable patterns?

4. COMPARE:
   - Your trajectory vs. competitors
   - Current position vs. 30/60/90 days ago
```

**Output:** Performance trajectory with forecasting insights

---

### Workflow 6: GBP Health Monitoring

**Purpose:** Check for GBP changes and performance trends

```
1. listLocalFalconGuardReports
   → Check monitored locations

2. getLocalFalconGuardReport
   → Pull specific monitoring data
   → Parameters: place_id

3. CHECK:
   - Any recent GBP edits detected?
   - Performance trends (impressions, calls, directions)
   - Alerts or warnings?

4. IF issues found:
   - Identify what changed
   - Assess impact on visibility
   - Recommend remediation
```

**Output:** GBP health status with alerts and recommended actions

---

### Workflow 7: Multi-Location Brand Analysis

**Purpose:** Enterprise view across all locations

```
1. listAllLocalFalconLocations
   → Get all brand locations

2. listLocalFalconLocationReports
   → See aggregated performance by location

3. listLocalFalconKeywordReports
   → See aggregated performance by keyword

4. ANALYZE:
   - Top performing locations
   - Underperforming locations
   - Consistent issues across locations
   - Keyword opportunities

5. PRIORITIZE:
   - Which locations need immediate attention?
   - Which keywords to focus on?
   - Resource allocation recommendations
```

**Output:** Portfolio overview with location-by-location priorities

---

## Common Parameters

### Pagination
- `limit` - Results per page (1-100, default 10)
- `next_token` - Token from previous response for next page

### Filtering
- `place_id` - Filter by Google/Apple Place ID
- `keyword` - Filter by keyword (loose match)
- `grid_size` - Filter by scan grid size (3, 5, 7, 9, 11, 13, 15, 17, 19, 21)
- `platform` - Filter by platform(s)
- `start_date` / `end_date` - Date range (MM/DD/YYYY format)
- `campaign_key` - Filter scans from specific campaign

### Field Masks (Performance Optimization)
Use `fieldmask` to return only needed fields:
```
fieldmask=report_key,arp,atrp,solv
fieldmask=reports.*.report_key,reports.*.date
```

---

## Error Handling

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid API key | Key missing or expired | Check [credentials page](https://www.localfalcon.com/api/credentials/) |
| Insufficient credits | Account out of credits | Purchase more credits or check subscription |
| Place ID not found | Invalid or unsaved location | Use `searchForLocalFalconBusinessLocation` first |
| Rate limit exceeded | Too many requests | Wait and retry with backoff |

### Best Practices
1. Always check `viewLocalFalconAccountInformation` first for credit availability
2. Use `fieldmask` to reduce response size when possible
3. Cache results when appropriate
4. Handle pagination for large result sets

---

## Integration Tips

### For Claude Code / Cursor Users
- MCP tools appear in your tool list automatically once configured
- Use natural language: "Check my Local Falcon account" → triggers appropriate tools
- Chain workflows together for comprehensive analysis

### For Custom Integrations
- API documentation: [docs.localfalcon.com](https://docs.localfalcon.com)
- Rate limits apply - implement appropriate backoff
- Webhook support available for campaign completions

---

*For questions about MCP integration, contact Local Falcon support or visit [docs.localfalcon.com](https://docs.localfalcon.com).*
