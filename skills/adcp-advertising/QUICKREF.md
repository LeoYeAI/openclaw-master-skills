# AdCP Quick Reference Card

Fast reference for common AdCP operations. Keep this handy when working with advertising campaigns.

**Official AdCP Documentation**: https://docs.adcontextprotocol.org  
**Quick Reference**: https://docs.adcontextprotocol.org/docs/media-buy/quick-reference  
**Complete Index**: https://docs.adcontextprotocol.org/llms.txt

## 🚀 Getting Started (30 seconds)

```javascript
// 1. Check what agent supports
await agent.getAdcpCapabilities({});

// 2. Find products
await agent.getProducts({
  brief: 'Display ads for tech startup',
  brand_manifest: { url: 'https://brand.com' }
});

// 3. Create campaign
await agent.createMediaBuy({
  buyer_ref: 'campaign-001',
  brand_manifest: { url: 'https://brand.com' },
  packages: [{
    buyer_ref: 'pkg-001',
    product_id: 'product_id_from_step_2',
    pricing_option_id: 'pricing_option_from_step_2',
    budget: 10000
  }],
  start_time: { type: 'asap' },
  end_time: '2026-12-31T23:59:59Z'
});
```

## 📋 The 8 Core Tasks

| Task | Purpose | Time | Auth |
|------|---------|------|------|
| `get_adcp_capabilities` | Discover agent features | ~1s | No |
| `get_products` | Find inventory | ~60s | Optional |
| `list_creative_formats` | View format specs | ~1s | No |
| `create_media_buy` | Launch campaign | Min-Days | Yes |
| `update_media_buy` | Modify campaign | Min-Days | Yes |
| `sync_creatives` | Upload assets | Min-Days | Yes |
| `list_creatives` | Query library | ~1s | Yes |
| `get_media_buy_delivery` | Track performance | ~60s | Yes |

## 🎯 Common Workflows

### Launch Campaign
```javascript
1. getAdcpCapabilities()    // Check features
2. getProducts()             // Find inventory
3. listCreativeFormats()     // Check requirements
4. createMediaBuy()          // Launch campaign
5. syncCreatives()           // Upload assets
6. getMediaBuyDelivery()     // Monitor
```

### Optimize Campaign
```javascript
1. getMediaBuyDelivery()     // Get performance
2. Analyze metrics           // Find opportunities
3. updateMediaBuy()          // Adjust budget/targeting
4. syncCreatives()           // Swap creatives (optional)
5. getMediaBuyDelivery()     // Verify improvements
```

## 🔑 Key Concepts

### Status Values
- `completed` - Operation finished
- `pending` - Awaiting approval
- `failed` - Operation failed (check error)

### Brand Manifest
```javascript
// URL reference (recommended)
{ brand_manifest: { url: 'https://brand.com' } }

// Inline (full details)
{
  brand_manifest: {
    name: 'Brand Name',
    url: 'https://brand.com',
    tagline: 'Brand tagline',
    colors: { primary: '#FF0000' }
  }
}
```

### Format ID
```javascript
{
  format_id: {
    agent_url: 'https://creative.adcontextprotocol.org',
    id: 'display_300x250'
  }
}
```

## 🎨 Creative Formats

### Display
- `display_300x250` - Medium Rectangle
- `display_728x90` - Leaderboard
- `display_160x600` - Wide Skyscraper
- `display_300x600` - Half Page

### Video
- `video_standard_15s` - 15 second
- `video_standard_30s` - 30 second
- `video_standard_60s` - 60 second

## 🎯 Targeting

```javascript
targeting_overlay: {
  geo: {
    included: ['US-CA', 'US-NY'],
    excluded: []
  },
  demographics: {
    age_ranges: [{ min: 25, max: 44 }],
    genders: ['M', 'F']
  },
  behavioral: {
    interests: ['technology'],
    purchase_intent: ['software']
  },
  contextual: {
    keywords: ['innovation'],
    categories: ['IAB19']
  }
}
```

## 📊 Performance Metrics

```javascript
const delivery = await agent.getMediaBuyDelivery({
  media_buy_id: 'mb_abc123',
  granularity: 'daily',
  dimensions: ['package', 'creative']
});

console.log(delivery.delivery.impressions);  // Total impressions
console.log(delivery.delivery.clicks);       // Total clicks
console.log(delivery.delivery.ctr);          // Click-through rate
console.log(delivery.delivery.spend);        // Amount spent
console.log(delivery.delivery.cpm);          // Cost per thousand
console.log(delivery.pacing.spend_pacing);   // Budget pacing %
```

## 🛠️ Common Operations

### Pause Campaign
```javascript
await agent.updateMediaBuy({
  media_buy_id: 'mb_abc123',
  updates: { status: 'paused' }
});
```

### Increase Budget
```javascript
await agent.updateMediaBuy({
  media_buy_id: 'mb_abc123',
  updates: { budget_change: 5000 }
});
```

### Swap Creatives
```javascript
await agent.syncCreatives({
  creatives: [],
  assignments: {
    'new_creative': ['pkg-001'],
    'old_creative': []
  }
});
```

### Check Pacing
```javascript
const delivery = await agent.getMediaBuyDelivery({
  media_buy_id: 'mb_abc123'
});

const pacing = delivery.pacing.spend_pacing;
const timeProgress = delivery.pacing.percent_complete;

if (Math.abs(pacing - timeProgress) > 0.15) {
  console.log('⚠️ Campaign pacing is off');
}
```

## 🧪 Test Agent

**Quick test without setup:**

```javascript
import { testAgent } from '@adcp/client/testing';

const result = await testAgent.getProducts({
  brief: 'Test campaign',
  brand_manifest: { url: 'https://example.com' }
});
```

**Credentials:**
- URL: `https://test-agent.adcontextprotocol.org/mcp`
- Token: `1v8tAhASaUYYp4odoQ1PnMpdqNaMiTrCRqYo9OJp6IQ`
- Testing: [testing.adcontextprotocol.org](https://testing.adcontextprotocol.org)

## ⚠️ Common Errors

### 400 Bad Request
```javascript
// Missing required field
{ error: { code: 'VALIDATION_ERROR', message: 'budget required' } }
```

### 401 Unauthorized
```javascript
// Invalid/missing auth token
{ error: { code: 'UNAUTHORIZED', message: 'Invalid token' } }
```

### 404 Not Found
```javascript
// Invalid ID reference
{ error: { code: 'NOT_FOUND', message: 'Product not found' } }
```

## 💡 Pro Tips

1. **Always start with capabilities** - Know what the agent supports
2. **Check status** - Handle `pending` operations properly
3. **Write detailed briefs** - Better briefs = better product matches
4. **Validate formats** - Check creative specs before upload
5. **Monitor pacing** - Regular delivery checks prevent issues
6. **Test creatives** - A/B test everything
7. **Start broad** - Narrow targeting based on data

## 📚 Documentation

### Official AdCP Documentation
- **Main Docs**: https://docs.adcontextprotocol.org
- **Complete Index (AI agents)**: https://docs.adcontextprotocol.org/llms.txt
- **Media Buy Protocol**: https://docs.adcontextprotocol.org/docs/media-buy/
- **Task Reference**: https://docs.adcontextprotocol.org/docs/media-buy/task-reference/
- **Quick Reference**: https://docs.adcontextprotocol.org/docs/media-buy/quick-reference

### This Skill's Documentation
- **Full Docs**: [SKILL.md](SKILL.md)
- **API Reference**: [REFERENCE.md](REFERENCE.md)
- **Examples**: [EXAMPLES.md](EXAMPLES.md)
- **Protocols**: [PROTOCOLS.md](PROTOCOLS.md)
- **Targeting**: [TARGETING.md](TARGETING.md)
- **Creatives**: [CREATIVE.md](CREATIVE.md)

## 🆘 Quick Help

**Need help?**
- **Official Docs**: https://docs.adcontextprotocol.org
- **Interactive Testing**: https://testing.adcontextprotocol.org
- **Complete API (AI agents)**: https://docs.adcontextprotocol.org/llms.txt

---

**Print this card** or keep it open in a tab for quick reference while working with AdCP!
