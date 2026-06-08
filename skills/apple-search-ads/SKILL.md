---
name: Apple Search Ads
slug: apple-search-ads
version: 1.0.0
homepage: https://clawic.com/skills/apple-search-ads
description: Create, optimize, and scale Apple Search Ads campaigns with API automation, attribution integration, and bid strategy recommendations.
metadata: {"clawdbot":{"emoji":"🍎","requires":{"bins":["curl","jq"],"env":["ASA_CLIENT_ID","ASA_TEAM_ID","ASA_KEY_ID","ASA_ORG_ID","ASA_PRIVATE_KEY_FILE"]},"os":["linux","darwin"]}}
---

# Apple Search Ads 🍎

Complete toolkit for Apple Search Ads: Campaign Management API v5, attribution integration (AdServices + SKAdNetwork), bid optimization, and strategic recommendations.

## What's New in v1.0.0

- Full Campaign Management API v5 coverage
- iOS app integration (AdServices framework)
- SKAdNetwork 4.0 support
- Automated reporting scripts
- Bid optimization strategies
- Multi-country campaign patterns

## Contents

1. [Setup](#setup)
2. [When to Use](#when-to-use)
3. [Architecture](#architecture)
4. [API Essentials](#api-essentials)
5. [Campaign Structure](#campaign-structure)
6. [Keywords & Bidding](#keywords--bidding)
7. [Attribution Integration](#attribution-integration)
8. [Reports & Analytics](#reports--analytics)
9. [Strategy Playbook](#strategy-playbook)
10. [Scripts & Automation](#scripts--automation)
11. [Common Traps](#common-traps)

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User needs to run Apple Search Ads for iOS apps. Agent handles campaign creation, bid optimization, attribution tracking, performance analysis, and strategic recommendations.

## Architecture

Memory lives in `~/apple-search-ads/`. See `memory-template.md` for structure.

```
~/apple-search-ads/
├── memory.md          # Active campaigns, preferences, learnings
├── credentials.md     # OAuth config (NEVER commit real secrets)
├── campaigns/         # Campaign-specific notes and performance
│   └── {app-id}/
├── reports/           # Generated reports
└── scripts/           # Custom automation
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| API endpoints | `api-reference.md` |
| iOS integration | `ios-integration.md` |
| Strategy guide | `strategy.md` |
| Script library | `scripts.md` |

## API Essentials

### Authentication (OAuth 2.0)

Apple Ads API uses OAuth with client credentials. Generate credentials at:
https://app.searchads.apple.com/cm/app/settings/apicertificates

```bash
# 1. Generate client secret (JWT signed with private key)
# Header
{
  "alg": "ES256",
  "kid": "{KEY_ID}"
}
# Payload
{
  "sub": "{CLIENT_ID}",
  "aud": "https://appleid.apple.com",
  "iat": {CURRENT_TIMESTAMP},
  "exp": {TIMESTAMP_+180_DAYS},
  "iss": "{TEAM_ID}"
}

# 2. Exchange for access token
curl -X POST "https://appleid.apple.com/auth/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id={CLIENT_ID}" \
  -d "client_secret={CLIENT_SECRET}" \
  -d "scope=searchadsorg"

# Response contains access_token (valid 1 hour)
```

### Base URL & Headers

```
Base URL: https://api.searchads.apple.com/api/v5
Headers:
  Authorization: Bearer {ACCESS_TOKEN}
  X-AP-Context: orgId={ORG_ID}
  Content-Type: application/json
```

### Core Endpoints

| Resource | Method | Endpoint |
|----------|--------|----------|
| **Apps** | | |
| Search apps | POST | `/search/apps` |
| App eligibility | GET | `/apps/{adamId}/eligibilities` |
| **Campaigns** | | |
| List campaigns | GET | `/campaigns` |
| Create campaign | POST | `/campaigns` |
| Update campaign | PUT | `/campaigns/{id}` |
| Delete campaign | DELETE | `/campaigns/{id}` |
| **Ad Groups** | | |
| List ad groups | GET | `/campaigns/{id}/adgroups` |
| Create ad group | POST | `/campaigns/{id}/adgroups` |
| **Keywords** | | |
| List keywords | GET | `/campaigns/{cId}/adgroups/{agId}/targetingkeywords` |
| Add keywords | POST | `/campaigns/{cId}/adgroups/{agId}/targetingkeywords/bulk` |
| **Reports** | | |
| Campaign report | POST | `/reports/campaigns` |
| Ad group report | POST | `/reports/campaigns/{id}/adgroups` |
| Keyword report | POST | `/reports/campaigns/{cId}/adgroups/{agId}/keywords` |
| Search term report | POST | `/reports/campaigns/{cId}/searchterms` |
| Impression share | POST | `/reports/campaigns/{id}/impressionshare` |

## Campaign Structure

### Hierarchy

```
Organization (orgId)
└── Campaign (Search Results / Search Tab / Today Tab)
    ├── Budget & Schedule
    ├── Countries/Regions
    └── Ad Groups
        ├── Keywords (targeting + negative)
        ├── Audience (age, gender, device, etc.)
        ├── Creatives (default or Custom Product Pages)
        └── Bid settings
```

### Campaign Types

| Type | Placement | Best For |
|------|-----------|----------|
| **Search Results** | Top of search results | High-intent users, brand defense |
| **Search Tab** | Suggested apps before search | Discovery, broad reach |
| **Today Tab** | Today tab featured | Brand awareness, launches |

### Campaign Object

```json
{
  "name": "MyApp - US - Brand",
  "adamId": 123456789,
  "countriesOrRegions": ["US"],
  "budgetAmount": {"amount": "1000", "currency": "USD"},
  "dailyBudgetAmount": {"amount": "50", "currency": "USD"},
  "supplySources": ["APPSTORE_SEARCH_RESULTS"],
  "billingEvent": "TAPS",
  "status": "ENABLED",
  "startTime": "2026-01-01T00:00:00.000",
  "endTime": null
}
```

### Ad Group Object

```json
{
  "name": "Brand Keywords",
  "campaignId": 123456,
  "defaultBidAmount": {"amount": "1.50", "currency": "USD"},
  "cpaGoal": {"amount": "5.00", "currency": "USD"},
  "startTime": "2026-01-01T00:00:00.000",
  "targetingDimensions": {
    "age": {"included": [{"minAge": 18}]},
    "gender": {"included": ["M", "F"]},
    "deviceClass": {"included": ["IPHONE", "IPAD"]},
    "daypart": {"userTime": {"included": [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]}},
    "adminArea": null,
    "locality": null,
    "appDownloaders": {"included": [], "excluded": []}
  },
  "automatedKeywordsOptIn": false,
  "status": "ENABLED"
}
```

## Keywords & Bidding

### Match Types

| Type | Behavior | Use Case |
|------|----------|----------|
| **Exact** | Query = keyword exactly | Brand terms, proven converters |
| **Broad** | Synonyms, related terms | Discovery, expansion |
| **Search Match** | Auto-matched by Apple | New apps, keyword research |

### Keyword Object

```json
{
  "text": "meditation app",
  "matchType": "EXACT",
  "bidAmount": {"amount": "2.00", "currency": "USD"},
  "status": "ACTIVE"
}
```

### Bid Strategy Rules

1. **Brand keywords** → Bid high (defend your brand)
2. **Competitor keywords** → Test carefully, monitor CPA
3. **Generic keywords** → Start low, increase for winners
4. **Discovery (Search Match)** → Low bids, mine for keywords
5. **Negative keywords** → Essential to reduce waste

### Bid Optimization Loop

```
Week 1: Set baseline bids (industry avg or $1-2)
        ↓
Week 2: Review search term report
        - High converts, low bid → raise bid 20-30%
        - Low converts, high spend → lower bid or pause
        - Irrelevant terms → add as negative
        ↓
Week 3+: Repeat. Target CPA within 20% of goal.
```

## Attribution Integration

### AdServices Framework (iOS 14.3+)

Modern attribution without user tracking. Integrates directly in iOS app.

```swift
import AdServices

func trackAttribution() async {
    do {
        // 1. Get attribution token from device
        let token = try AAAttribution.attributionToken()
        
        // 2. Send to Apple's attribution API
        var request = URLRequest(url: URL(string: "https://api-adservices.apple.com/api/v1/")!)
        request.httpMethod = "POST"
        request.setValue("text/plain", forHTTPHeaderField: "Content-Type")
        request.httpBody = token.data(using: .utf8)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        let attribution = try JSONDecoder().decode(Attribution.self, from: data)
        
        // 3. attribution contains: campaignId, adGroupId, keywordId, etc.
        // Send to your analytics backend
        
    } catch {
        // Not from Apple Search Ads or error
    }
}

struct Attribution: Codable {
    let attribution: Bool
    let orgId: Int?
    let campaignId: Int?
    let adGroupId: Int?
    let keywordId: Int?
    let creativeSetId: Int?
    let conversionType: String?
    let clickDate: String?
}
```

### SKAdNetwork 4.0

Privacy-focused attribution for installs. Apple aggregates data, no user-level tracking.

```swift
// In your app delegate
import StoreKit

func application(_ application: UIApplication, 
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    // Register for attribution
    SKAdNetwork.updatePostbackConversionValue(0) { error in
        // Initial registration
    }
    return true
}

// When user completes valuable action (purchase, signup, etc.)
func trackConversion(value: Int) {
    // value 0-63, represents conversion value
    SKAdNetwork.updatePostbackConversionValue(value) { error in
        if error == nil {
            // Updated successfully
        }
    }
}
```

### SKAdNetwork Conversion Value Strategy

| Value | Meaning | Example |
|-------|---------|---------|
| 0 | Install only | App opened |
| 1-10 | Engagement tier | Sessions, time in app |
| 11-30 | Feature usage | Key feature activated |
| 31-50 | Monetization signal | Trial started, content viewed |
| 51-63 | Revenue tier | Purchase completed |

### MMP Integration (AppsFlyer, Adjust, etc.)

If using an MMP, they handle AdServices and SKAdNetwork. Follow their SDK docs. Key integration points:

1. Initialize MMP SDK before any tracking
2. Configure SKAdNetwork conversion values in MMP dashboard
3. Link Apple Search Ads account in MMP for cost data
4. Use MMP's deeplink handling for attribution

## Reports & Analytics

### Campaign Report Request

```json
{
  "startTime": "2026-01-01",
  "endTime": "2026-01-31",
  "timeZone": "UTC",
  "granularity": "DAILY",
  "selector": {
    "orderBy": [{"field": "localSpend", "sortOrder": "DESCENDING"}],
    "pagination": {"offset": 0, "limit": 100}
  },
  "returnRowTotals": true,
  "returnGrandTotals": true
}
```

### Key Metrics

| Metric | Description | Good Range |
|--------|-------------|------------|
| **TTR** | Tap-through rate | 5-10%+ |
| **CVR** | Conversion rate (installs/taps) | 30-60% |
| **CPA** | Cost per acquisition | < LTV/3 |
| **CPT** | Cost per tap | $0.50-3.00 (varies) |
| **ROAS** | Return on ad spend | > 100% |
| **Impression Share** | % of eligible impressions won | Track trend |

### Search Term Report

Critical for optimization. Shows actual queries that triggered your ads.

```json
// POST /reports/campaigns/{campaignId}/searchterms
{
  "startTime": "2026-01-01",
  "endTime": "2026-01-31",
  "selector": {
    "conditions": [
      {"field": "impressions", "operator": "GREATER_THAN", "values": ["10"]}
    ],
    "orderBy": [{"field": "impressions", "sortOrder": "DESCENDING"}],
    "pagination": {"offset": 0, "limit": 1000}
  }
}
```

**Weekly ritual:**
1. Pull search term report
2. High impressions + high CVR → Add as exact keyword
3. High impressions + low CVR → Add as negative
4. Irrelevant terms → Negative immediately

## Strategy Playbook

### Campaign Structure (Recommended)

```
Campaign: [App] - [Country] - Brand
  └── Ad Group: Brand Exact
      └── Keywords: app name, brand terms (exact match)

Campaign: [App] - [Country] - Category
  └── Ad Group: Category - Exact
      └── Keywords: category terms (exact match)
  └── Ad Group: Category - Discovery
      └── Search Match enabled, low bid

Campaign: [App] - [Country] - Competitor
  └── Ad Group: Competitor Names
      └── Keywords: competitor app names (exact match)
```

### Budget Allocation

| Stage | Brand | Category | Competitor | Discovery |
|-------|-------|----------|------------|-----------|
| Launch | 40% | 40% | 10% | 10% |
| Growth | 20% | 50% | 20% | 10% |
| Scale | 10% | 60% | 25% | 5% |

### Multi-Country Expansion

1. **Start:** US, UK, Canada, Australia (English)
2. **Expand:** Germany, France, Japan, South Korea (localize)
3. **Test:** Brazil, Mexico, India (high volume, lower CPT)

**Localization checklist:**
- [ ] App Store listing translated
- [ ] Custom Product Pages per country
- [ ] Keywords researched per language
- [ ] Separate campaigns per country (easier optimization)

### Custom Product Pages (CPP)

Create variations of your App Store page for different audiences.

```json
// Get available CPPs
// GET /apps/{adamId}/customproductpages

// Create ad using CPP
{
  "name": "Fitness Ad - Summer Campaign",
  "adGroupId": 12345,
  "creativeType": "CUSTOM_PRODUCT_PAGE",
  "productPageId": "cpp-uuid-here"
}
```

**Best practices:**
- Create CPP for each major keyword theme
- Test: Control (default) vs CPP
- Rotate seasonally (holidays, events)

## Scripts & Automation

See `scripts.md` for complete script library. Key scripts:

### Get Access Token

```bash
#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
# Environment variables accessed: ASA_CLIENT_ID, ASA_TEAM_ID, ASA_KEY_ID, ASA_PRIVATE_KEY
# External endpoints called: https://appleid.apple.com/auth/oauth2/token (only)
# Local files read: none
# Local files written: none

# Requires: openssl, jq

CLIENT_ID="${ASA_CLIENT_ID}"
TEAM_ID="${ASA_TEAM_ID}"
KEY_ID="${ASA_KEY_ID}"
PRIVATE_KEY="${ASA_PRIVATE_KEY}"  # PEM format

# Create JWT header
HEADER=$(echo -n '{"alg":"ES256","kid":"'$KEY_ID'"}' | base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')

# Create JWT payload
NOW=$(date +%s)
EXP=$((NOW + 15552000))  # 180 days
PAYLOAD=$(echo -n '{"sub":"'$CLIENT_ID'","aud":"https://appleid.apple.com","iat":'$NOW',"exp":'$EXP',"iss":"'$TEAM_ID'"}' | base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')

# Sign with private key
SIGNATURE=$(echo -n "$HEADER.$PAYLOAD" | openssl dgst -sha256 -sign <(echo "$PRIVATE_KEY") | base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n')

CLIENT_SECRET="$HEADER.$PAYLOAD.$SIGNATURE"

# Exchange for access token
curl -s -X POST "https://appleid.apple.com/auth/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET&scope=searchadsorg" \
  | jq -r '.access_token'
```

### Daily Performance Report

```bash
#!/usr/bin/env bash
set -euo pipefail

# SECURITY MANIFEST:
# Environment variables accessed: ASA_ACCESS_TOKEN, ASA_ORG_ID
# External endpoints called: https://api.searchads.apple.com/api/v5/reports/campaigns (only)
# Local files read: none
# Local files written: stdout (report data)

ACCESS_TOKEN="${ASA_ACCESS_TOKEN}"
ORG_ID="${ASA_ORG_ID}"

TODAY=$(date -u +%Y-%m-%d)
YESTERDAY=$(date -u -v-1d +%Y-%m-%d 2>/dev/null || date -u -d "yesterday" +%Y-%m-%d)

curl -s -X POST "https://api.searchads.apple.com/api/v5/reports/campaigns" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "X-AP-Context: orgId=$ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "startTime": "'$YESTERDAY'",
    "endTime": "'$TODAY'",
    "granularity": "DAILY",
    "selector": {
      "orderBy": [{"field": "localSpend", "sortOrder": "DESCENDING"}]
    },
    "returnRowTotals": true,
    "returnGrandTotals": true
  }' | jq '.data.reportingDataResponse.row[] | {
    campaign: .metadata.campaignName,
    spend: .total.localSpend.amount,
    impressions: .total.impressions,
    taps: .total.taps,
    installs: .total.installs,
    cpa: (if .total.installs > 0 then (.total.localSpend.amount | tonumber) / .total.installs else "N/A" end)
  }'
```

## Core Rules

### 1. Separate Campaigns by Intent
Brand, category, competitor, and discovery keywords in separate campaigns. Mixing makes optimization impossible.

### 2. Start Exact, Expand Broad
Begin with exact match keywords you're confident about. Use Search Match and broad only for discovery with low bids.

### 3. Mine Search Terms Weekly
The search term report is gold. Review weekly, add winners as exact, add losers as negatives.

### 4. Defend Your Brand
Competitors WILL bid on your brand name. Always have a brand campaign with high bids to protect your real estate.

### 5. Track Attribution Properly
Implement AdServices for iOS 14.3+. Without attribution, you're optimizing blind.

### 6. One Country Per Campaign
Mixing countries makes bid optimization nearly impossible. Create separate campaigns per country/region.

### 7. Budget to CPA, Not Spend
Set CPA goals, not just budgets. If CPA is 2x target, pause and investigate before spending more.

## Common Traps

- **Mixing match types in one ad group** → Can't tell what's working. Separate exact, broad, search match.
- **No negative keywords** → Wasting budget on irrelevant searches. Review search terms weekly.
- **Ignoring Search Tab/Today Tab** → Lower intent but cheaper. Good for discovery.
- **Same bid across all keywords** → Brand keywords worth more than generic. Bid accordingly.
- **No attribution integration** → Flying blind. Implement AdServices or MMP.
- **Launching without App Store optimization** → Low conversion rate. Fix ASO first.
- **Bidding on competitors without testing** → Often unprofitable. Test small first.
- **Forgetting timezone in reports** → Data misalignment. Always use UTC or explicit timezone.
- **Not using Custom Product Pages** → Missing easy wins. Create themed pages.
- **Scaling too fast** → CPA spikes when scaling. Increase budget 20-30% at a time.

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| `https://appleid.apple.com/auth/oauth2/token` | Client credentials (JWT) | Get access token |
| `https://api.searchads.apple.com/api/v5/*` | Campaign/keyword data | Campaign management |
| `https://api-adservices.apple.com/api/v1/` | Attribution token | Attribution data |

No other data is sent externally.

## Security & Privacy

**Data that leaves your machine:**
- Campaign configurations sent to Apple Ads API
- Attribution tokens sent to Apple (from iOS app)

**Data that stays local:**
- Credentials in `~/apple-search-ads/credentials.md`
- Reports and analysis
- Strategy notes

**This skill does NOT:**
- Store API secrets in plain text (use environment variables)
- Access user-level data (attribution is aggregated)
- Make requests to undeclared endpoints

## Trust

By using this skill, data is sent to Apple's Search Ads API and AdServices.
Only install if you trust Apple with your advertising data.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `app-store-connect` — manage apps and releases
- `aso` — App Store Optimization
- `analytics` — track metrics and KPIs
- `ios` — iOS development patterns

## Feedback

- If useful: `clawhub star apple-search-ads`
- Stay updated: `clawhub sync`
