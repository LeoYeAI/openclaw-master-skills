---
name: adcp-advertising
displayName: AdCP Advertising
description: Automate advertising campaigns with AI. Create ads, buy media, manage ad budgets, discover ad inventory, run display ads, video ads, CTV campaigns, and optimize ad performance. Perfect for marketing automation, programmatic advertising, media buying, ad management, campaign optimization, creative management, and performance tracking. Launch Facebook ads, Google ads, display advertising, video marketing, and multi-channel campaigns using natural language. Supports ad targeting, audience segmentation, ROI tracking, and automated bidding.
author: AdCP Community
license: MIT
homepage: https://docs.adcontextprotocol.org
repository: https://github.com/edyyy62/openclaw-adcp
category: advertising
subcategory: marketing-automation
type: agent
keywords:
  - advertising
  - ads
  - marketing
  - campaigns
  - adcp
  - programmatic
  - media-buying
  - display-ads
  - video-ads
  - facebook-ads
  - google-ads
  - ctv
  - connected-tv
  - marketing-automation
  - ad-management
  - campaign-optimization
  - targeting
  - roi-tracking
  - performance-marketing
  - retargeting
---

# Ad Context Protocol (AdCP) Advertising Skill

## Overview

**Automate your advertising campaigns with AI.** This skill enables OpenClaw agents to discover ad inventory, launch campaigns, manage creatives, and optimize performance across display, video, CTV, audio, and more - all through natural language commands.

No dashboards. No forms. No ad platform expertise required.

### What You Can Do

- 🎯 **Launch campaigns in minutes** - "Create a $10k display campaign targeting tech professionals in California"
- 🔍 **Discover ad inventory instantly** - "Find premium video placements for luxury brands"
- 🎨 **Upload ads with ease** - "Upload these banner images as creatives"
- 📊 **Track ROI in real-time** - "Show me campaign performance and CTR by creative"
- 🎛️ **Auto-optimize spend** - "Reallocate budget to top-performing packages"
- 🌐 **Target precisely** - Demographics, behaviors, interests, locations, devices, times

### Perfect For

**Marketing teams** running Facebook ads, Google ads, and multi-channel campaigns  
**Media buyers** managing programmatic ad spend across publishers  
**Agencies** automating client campaign management and reporting  
**E-commerce brands** launching product ads and retargeting campaigns  
**Startups** running lean marketing with AI-powered automation

### Why Choose This Skill?

**Skip the learning curve** - No need to master complex ad platforms  
**Save time** - Launch in 5 minutes vs. hours of manual setup  
**Spend smarter** - AI automatically optimizes budgets to top performers  
**Scale faster** - Manage unlimited campaigns through simple commands  
**Test risk-free** - Public test agent included, no setup required

**Official AdCP Repository**: https://github.com/adcontextprotocol/adcp  
**Official AdCP Documentation**: https://docs.adcontextprotocol.org  
**Complete Documentation Index**: https://docs.adcontextprotocol.org/llms.txt

## When to Use This Skill

Trigger this skill when users ask about:

**Campaign Management**
- "Create a display ad campaign"
- "Launch Facebook ads for my product"
- "Set up a $5000 video advertising campaign"
- "Pause my underperforming campaigns"

**Ad Discovery & Media Buying**
- "Find advertising inventory for luxury brands"
- "Show me CTV ad placements in major cities"
- "What display ad options are available?"
- "Buy media for a tech startup"

**Creative Management**
- "Upload these banner images"
- "Which creative is performing best?"
- "Add video ads to my campaign"
- "Manage my ad library"

**Performance & Optimization**
- "How is my campaign performing?"
- "Show me ROI by channel"
- "Optimize my ad spend"
- "Reallocate budget to top performers"
- "Track impressions and click-through rates"

**Targeting & Audiences**
- "Target professionals in California"
- "Set up demographic targeting"
- "Create a retargeting campaign"
- "Target by device type and time of day"

## Quick Start

### Launch Your First Campaign (5 Minutes)

**No setup required.** Use the included test agent to try everything:

**Step 1: Discover what's available**
```
"Show me advertising capabilities"
```
Browse available channels, publishers, and formats.

**Step 2: Find ad inventory**
```
"Find display ads for a tech startup, budget $5000"
```
AI searches and shows matching products with pricing.

**Step 3: Launch campaign**
```
"Create campaign with Product prod_123, $5000 budget, targeting California tech professionals"
```
Campaign goes live instantly.

**Step 4: Upload your ads**
```
"Upload these banner images as creatives"
```
Drop files, get instant creative IDs.

**Step 5: Monitor performance**
```
"Show campaign metrics and ROI"
```
Real-time impressions, clicks, CTR, spend.

### Real-World Usage Examples

**Quick campaign launch:**
```
User: "I need to run display ads for my SaaS product"
Agent: [Discovers products] "Found 5 display packages. Want details?"
User: "Create campaign with Product 1, $10k budget, target CTOs"
Agent: [Creates campaign] "Campaign live! ID: mb_abc123"
```

**Performance optimization:**
```
User: "How are my video ads performing?"
Agent: [Shows metrics] "Package A: 2.3% CTR, Package B: 0.8% CTR"
User: "Move $5k from B to A"
Agent: [Reallocates] "Budget updated. Package A now $15k"
```

**Multi-channel campaign:**
```
User: "Launch omnichannel campaign: display in CA, video in NYC, $50k total"
Agent: [Creates packages] "3 packages created across display and video"
```

## How It Works

### Natural Language Understanding

Speak naturally. The skill understands:
- **Budgets**: "$5000", "five thousand dollars", "5k budget"
- **Locations**: "California", "major US cities", "New York and LA"
- **Audiences**: "tech professionals", "age 25-45", "high income"
- **Goals**: "brand awareness", "drive conversions", "increase sales"

### Progressive Workflow

**1. Discovery Phase**
```
"Find video advertising for luxury brands"
```
↓ Agent searches inventory
↓ Shows matched products with pricing
↓ Explains targeting and formats

**2. Campaign Creation**
```
"Create campaign with Product 1, $25k, target professionals"
```
↓ Agent creates media buy
↓ Sets up targeting overlay
↓ Returns campaign ID and status

**3. Creative Management**
```
"Upload my banner ads"
```
↓ Agent syncs creatives
↓ Assigns to campaign
↓ Returns creative IDs

**4. Monitoring & Optimization**
```
"Show performance"
```
↓ Agent fetches delivery data  
↓ Shows metrics by package/creative  
↓ Suggests optimizations

## Core Operations

### Create Campaign

```javascript
const campaign = await testAgent.createMediaBuy({
  buyer_ref: 'campaign-2026-q1',
  brand_manifest: { url: 'https://acme.com' },
  packages: [{ product_id: 'premium_display', budget: 10000 }]
});
```

### Upload Creatives

```javascript
await testAgent.syncCreatives({
  creatives: [{ 
    buyer_ref: 'banner-300x250',
    url: 'https://cdn.acme.com/banner.jpg'
  }]
});
```

### Monitor Performance

```javascript
const delivery = await testAgent.getMediaBuyDelivery({
  media_buy_id: 'mb_abc123'
});
console.log(`CTR: ${delivery.totals.ctr}%, Spend: $${delivery.totals.spend}`);
```

See [REFERENCE.md](REFERENCE.md) for complete API docs and [EXAMPLES.md](EXAMPLES.md) for detailed workflows.

## Core Concepts

### The 8 Media Buy Tasks

AdCP provides 8 standardized tasks for the complete advertising lifecycle. Learn more in the [Media Buy Protocol documentation](https://docs.adcontextprotocol.org/docs/media-buy/).

1. **get_adcp_capabilities** - Discover agent features and portfolio (~1s)
2. **get_products** - Find inventory using natural language (~60s)
3. **list_creative_formats** - View creative specifications (~1s)
4. **create_media_buy** - Launch campaigns (minutes-days, may require approval)
5. **update_media_buy** - Modify campaigns (minutes-days)
6. **sync_creatives** - Upload creative assets (minutes-days)
7. **list_creatives** - Query creative library (~1s)
8. **get_media_buy_delivery** - Track performance (~60s)

**Complete task reference**: https://docs.adcontextprotocol.org/docs/media-buy/task-reference/

### Brand Manifest

Brand context can be provided two ways:

**URL reference** (recommended - agent fetches brand info):
```json
{
  "brand_manifest": {
    "url": "https://brand.com"
  }
}
```

**Inline manifest** (full brand details):
```json
{
  "brand_manifest": {
    "name": "Brand Name",
    "url": "https://brand.com",
    "tagline": "Brand tagline",
    "colors": { "primary": "#FF0000" },
    "logo": { "url": "https://cdn.brand.com/logo.png" }
  }
}
```

### Pricing Models

Products support various pricing models:
- **CPM** (Cost Per Mille/Thousand) - Fixed price per 1000 impressions
- **CPM-Auction** - Bid-based pricing for impressions
- **CPCV** (Cost Per Completed View) - Video completions
- **Flat-Fee** - Fixed campaign cost
- **CPP** (Cost Per Point) - Percentage of audience reached

For auction pricing, include `bid_price` in your package.

### Asynchronous Operations

AdCP is **not a real-time protocol**. Operations may take:
- **~1 second** - Simple lookups (formats, creative lists)
- **~60 seconds** - AI/inference operations (product discovery)
- **Minutes to days** - Operations requiring human approval (campaign creation)

Always check the `status` field in responses:
- `completed` - Operation finished successfully
- `pending` - Awaiting approval or processing
- `failed` - Operation failed (check error details)

### Targeting Capabilities

Apply targeting overlays to campaigns:
```javascript
{
  targeting_overlay: {
    geo: {
      included: ['US-CA', 'US-NY'],  // DMA codes or regions
      excluded: ['US-TX']
    },
    demographics: {
      age_ranges: [{ min: 25, max: 44 }],
      genders: ['M', 'F']
    },
    behavioral: {
      interests: ['technology', 'gaming'],
      purchase_intent: ['consumer_electronics']
    },
    contextual: {
      keywords: ['innovation', 'design'],
      categories: ['IAB19'] // Technology & Computing
    }
  }
}
```

## Common Workflows

### Workflow 1: Campaign Discovery to Launch

```javascript
// 1. Discover capabilities
const caps = await agent.getAdcpCapabilities({});

// 2. Find products
const products = await agent.getProducts({
  brief: 'Q1 2026 brand awareness campaign for tech startup',
  brand_manifest: { url: 'https://startup.com' },
  filters: { channels: ['display', 'video'] }
});

// 3. Check creative formats
const formats = await agent.listCreativeFormats({
  format_types: ['display', 'video']
});

// 4. Create campaign
const campaign = await agent.createMediaBuy({
  buyer_ref: 'q1-2026-awareness',
  brand_manifest: { url: 'https://startup.com' },
  packages: [
    {
      buyer_ref: 'pkg-001',
      product_id: products.products[0].product_id,
      pricing_option_id: 'cpm-standard',
      budget: 15000
    }
  ],
  start_time: { type: 'asap' },
  end_time: '2026-03-31T23:59:59Z'
});

// 5. Upload creatives
await agent.syncCreatives({
  creatives: [...], // Your creative assets
  assignments: {
    'creative_001': ['pkg-001']
  }
});

// 6. Monitor performance
const delivery = await agent.getMediaBuyDelivery({
  media_buy_id: campaign.media_buy_id
});
```

### Workflow 2: Update Running Campaign

```javascript
// Pause, adjust budget, and resume campaign
await agent.updateMediaBuy({
  media_buy_id: 'mb_abc123',
  updates: {
    status: 'paused',
    budget_change: 5000, // Add $5000
    end_time: '2026-04-30T23:59:59Z'
  }
});

// Resume after adjustments
await agent.updateMediaBuy({
  media_buy_id: 'mb_abc123',
  updates: { status: 'active' }
});
```

**More workflow examples**: See [EXAMPLES.md](EXAMPLES.md) for complete campaign scenarios including creative management, multi-channel campaigns, and optimization workflows.

## Test Agent

For development and testing, use the public test agent:

**Agent URL**: `https://test-agent.adcontextprotocol.org/mcp`  
**Auth Token**: `1v8tAhASaUYYp4odoQ1PnMpdqNaMiTrCRqYo9OJp6IQ`

```javascript
import { testAgent } from '@adcp/client/testing';

// No authentication needed for test agent
const result = await testAgent.getProducts({
  brief: 'Test campaign',
  brand_manifest: { url: 'https://example.com' }
});
```

Interactive testing available at: **[testing.adcontextprotocol.org](https://testing.adcontextprotocol.org)**

## Error Handling

Common error patterns:

**400 Bad Request** - Invalid parameters:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "budget must be greater than 0",
    "field": "packages[0].budget"
  }
}
```

**401 Unauthorized** - Missing or invalid auth:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid authentication token"
  }
}
```

**404 Not Found** - Invalid ID reference:
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Product not found",
    "resource": "product_id: premium_video_30s"
  }
}
```

Always check for errors before processing responses:
```javascript
if (result.error) {
  console.error(`Error: ${result.error.message}`);
  return;
}
```

## Best Practices

### 1. Always Start with Capabilities

Call `get_adcp_capabilities` first to understand what the agent supports before making other requests.

### 2. Use Clear Buyer References

Use descriptive `buyer_ref` values for tracking:
- Good: `'campaign-2026-q1-tech-launch'`
- Avoid: `'c1'`, `'test'`, `'abc'`

### 3. Handle Async Operations

Check `status` field and implement polling for pending operations:
```javascript
let status = 'pending';
while (status === 'pending') {
  await sleep(5000); // Wait 5 seconds
  const update = await agent.getMediaBuyDelivery({
    media_buy_id: campaign.media_buy_id
  });
  status = update.status;
}
```

### 4. Write Detailed Briefs

Better briefs lead to better product matches:
- Good: `'Premium video inventory for luxury automotive brand targeting high-income professionals aged 35-54 in major metros. Focus on brand awareness with completion rates above 70%.'`
- Avoid: `'video ads'`, `'need advertising'`

### 5. Validate Creative Formats

Always check `list_creative_formats` to ensure your creatives meet requirements before uploading.

### 6. Monitor Budget Pacing

Regularly check delivery metrics to ensure campaigns are pacing properly:
```javascript
const delivery = await agent.getMediaBuyDelivery({
  media_buy_id: campaign.media_buy_id
});

const pacing = delivery.delivery.spend / delivery.delivery.budget;
console.log(`Budget pacing: ${(pacing * 100).toFixed(1)}%`);
```

## Additional Resources

### Official AdCP Documentation
- **Main Documentation**: https://docs.adcontextprotocol.org
- **Complete Index**: https://docs.adcontextprotocol.org/llms.txt
- **Media Buy Protocol**: https://docs.adcontextprotocol.org/docs/media-buy/
- **Quick Reference**: https://docs.adcontextprotocol.org/docs/media-buy/quick-reference
- **Task Reference**: https://docs.adcontextprotocol.org/docs/media-buy/task-reference/
- **Quickstart Guide**: https://docs.adcontextprotocol.org/docs/quickstart

### This Skill's Documentation
- [REFERENCE.md](REFERENCE.md) - Complete API reference and schemas
- [EXAMPLES.md](EXAMPLES.md) - Real-world campaign examples
- [PROTOCOLS.md](PROTOCOLS.md) - MCP vs A2A protocol details
- [TARGETING.md](TARGETING.md) - Advanced targeting strategies
- [CREATIVE.md](CREATIVE.md) - Creative asset management guide

## Key Reminders

1. **AdCP is asynchronous** - Operations may take minutes to days
2. **Human approval may be required** - Check for `pending` status
3. **Start with capabilities** - Always call `get_adcp_capabilities` first
4. **Brand context matters** - Provide detailed brand manifests for better results
5. **Targeting is additive** - Product targeting + your overlay = final targeting
6. **Creative formats are strict** - Always validate against format specifications
7. **Monitor performance** - Regular delivery checks ensure campaign success

## Support

For help with AdCP:
- Official Repository: https://github.com/adcontextprotocol/adcp
- Documentation: https://docs.adcontextprotocol.org
- Interactive Testing: https://testing.adcontextprotocol.org
- Complete API Docs: https://docs.adcontextprotocol.org/llms.txt
