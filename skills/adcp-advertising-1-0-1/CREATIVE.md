# Creative Asset Management Guide

Complete guide to managing advertising creatives with AdCP.

**Official AdCP Documentation**: https://docs.adcontextprotocol.org  
**Creative Protocol**: https://docs.adcontextprotocol.org/docs/creative/  
**Creative Formats**: https://docs.adcontextprotocol.org/docs/creative/formats

This guide covers creative asset management with AdCP. For the complete creative specification and format details, see the [official AdCP creative documentation](https://docs.adcontextprotocol.org/docs/creative/).

## Overview

AdCP provides a comprehensive creative management system:
- **Format Discovery** - Understand creative requirements
- **Asset Upload** - Sync creatives across platforms
- **Library Management** - Query and organize assets
- **Creative Assignment** - Link creatives to campaigns
- **Performance Tracking** - Monitor creative effectiveness

## Creative Lifecycle

```
1. Discover Formats
   ↓
2. Build/Prepare Assets
   ↓
3. Validate Requirements
   ↓
4. Upload to Agent
   ↓
5. Assign to Campaigns
   ↓
6. Monitor Performance
   ↓
7. Optimize/Replace
```

## Creative Formats

### Standard IAB Formats

AdCP supports standard IAB creative formats via the Standard Creative Agent at `https://creative.adcontextprotocol.org`.

#### Display Formats

| Format ID | Name | Dimensions | Use Case |
|-----------|------|------------|----------|
| `display_300x250` | Medium Rectangle | 300x250 | Most versatile display format |
| `display_728x90` | Leaderboard | 728x90 | Top of page banner |
| `display_160x600` | Wide Skyscraper | 160x600 | Sidebar placement |
| `display_300x600` | Half Page | 300x600 | Premium sidebar |
| `display_970x250` | Billboard | 970x250 | Above-the-fold large format |
| `display_320x50` | Mobile Banner | 320x50 | Mobile web |
| `display_300x50` | Mobile Banner Small | 300x50 | Mobile web |

#### Video Formats

| Format ID | Name | Duration | Use Case |
|-----------|------|----------|----------|
| `video_standard_15s` | Pre-roll 15s | 15 seconds | Short-form video |
| `video_standard_30s` | Pre-roll 30s | 30 seconds | Standard video ad |
| `video_standard_60s` | Mid-roll 60s | 60 seconds | Long-form content |
| `video_outstream_15s` | Outstream 15s | 15 seconds | In-feed video |

#### Native Formats

| Format ID | Name | Use Case |
|-----------|------|----------|
| `native_standard` | Standard Native | Content-style ads |
| `native_in_feed` | In-Feed Native | Social feed ads |

### Discovering Formats

```javascript
// Get all available formats
const formats = await agent.listCreativeFormats({});

// Filter by type
const videoFormats = await agent.listCreativeFormats({
  format_types: ['video']
});

// Filter by channel
const ctvFormats = await agent.listCreativeFormats({
  channels: ['ctv']
});

// Examine format details
videoFormats.formats.forEach(format => {
  console.log(`${format.name}:`);
  console.log(`  Format ID: ${format.format_id.id}`);
  console.log(`  Dimensions: ${format.specifications.width}x${format.specifications.height}`);
  console.log(`  Duration: ${format.specifications.duration_ms}ms`);
  console.log(`  Max size: ${format.specifications.max_file_size_kb}KB`);
  console.log(`  Codecs: ${format.specifications.video_codec?.join(', ')}`);
});
```

## Building Creatives

### Display Creative Structure

```javascript
{
  creative_id: 'display_mrec_v1',
  name: 'Display Banner - Medium Rectangle',
  format_id: {
    agent_url: 'https://creative.adcontextprotocol.org',
    id: 'display_300x250'
  },
  assets: {
    image: {
      url: 'https://cdn.brand.com/banner_300x250.jpg',
      width: 300,
      height: 250,
      mime_type: 'image/jpeg'
    }
  },
  click_through_url: 'https://brand.com/campaign',
  tracking_pixels: [
    'https://analytics.brand.com/impression?id=123',
    'https://analytics.brand.com/click?id=123'
  ],
  status: 'active'
}
```

### Video Creative Structure

```javascript
{
  creative_id: 'video_30s_hero',
  name: 'Hero Video 30s',
  format_id: {
    agent_url: 'https://creative.adcontextprotocol.org',
    id: 'video_standard_30s'
  },
  assets: {
    video: {
      url: 'https://cdn.brand.com/hero_30s.mp4',
      width: 1920,
      height: 1080,
      duration_ms: 30000,
      mime_type: 'video/mp4'
    }
  },
  click_through_url: 'https://brand.com/product',
  tracking_pixels: [
    'https://analytics.brand.com/video_start?id=456',
    'https://analytics.brand.com/video_complete?id=456'
  ]
}
```

### HTML5 Creative Structure

```javascript
{
  creative_id: 'html5_interactive',
  name: 'Interactive HTML5 Ad',
  format_id: {
    agent_url: 'https://creative.adcontextprotocol.org',
    id: 'display_300x250'
  },
  assets: {
    html: {
      content: '<div>...</div>',  // Full HTML content
      width: 300,
      height: 250
    },
    backup_image: {  // Fallback for non-HTML5 support
      url: 'https://cdn.brand.com/backup.jpg',
      width: 300,
      height: 250
    }
  },
  click_through_url: 'https://brand.com/campaign'
}
```

### Native Creative Structure

```javascript
{
  creative_id: 'native_article',
  name: 'Native Article Ad',
  format_id: {
    agent_url: 'https://creative.adcontextprotocol.org',
    id: 'native_standard'
  },
  assets: {
    title: {
      text: 'Discover the Future of Cloud Computing'
    },
    body: {
      text: 'Learn how our platform helps businesses scale faster'
    },
    image: {
      url: 'https://cdn.brand.com/native_image.jpg',
      width: 1200,
      height: 627
    },
    logo: {
      url: 'https://cdn.brand.com/logo.png',
      width: 200,
      height: 200
    },
    cta: {
      text: 'Learn More'
    }
  },
  click_through_url: 'https://brand.com/cloud'
}
```

## Uploading Creatives

### Single Creative Upload

```javascript
const result = await agent.syncCreatives({
  creatives: [
    {
      creative_id: 'display_300x250_v1',
      name: 'Display Banner',
      format_id: {
        agent_url: 'https://creative.adcontextprotocol.org',
        id: 'display_300x250'
      },
      assets: {
        image: {
          url: 'https://cdn.brand.com/banner.jpg',
          width: 300,
          height: 250
        }
      }
    }
  ]
});

console.log(`Creative uploaded: ${result.synced_creatives[0].status}`);
```

### Bulk Upload

```javascript
const creativeLibrary = [
  { id: 'banner_300x250', format: 'display_300x250', url: 'banner_300x250.jpg' },
  { id: 'banner_728x90', format: 'display_728x90', url: 'banner_728x90.jpg' },
  { id: 'banner_160x600', format: 'display_160x600', url: 'banner_160x600.jpg' },
  { id: 'video_15s', format: 'video_standard_15s', url: 'video_15s.mp4', duration: 15000 },
  { id: 'video_30s', format: 'video_standard_30s', url: 'video_30s.mp4', duration: 30000 }
];

const creatives = creativeLibrary.map(item => {
  const isVideo = item.format.includes('video');
  const [width, height] = isVideo ? [1920, 1080] : item.format.match(/\d+x\d+/)[0].split('x').map(Number);
  
  return {
    creative_id: item.id,
    name: `Campaign Creative - ${item.format}`,
    format_id: {
      agent_url: 'https://creative.adcontextprotocol.org',
      id: item.format
    },
    assets: isVideo ? {
      video: {
        url: `https://cdn.brand.com/${item.url}`,
        width,
        height,
        duration_ms: item.duration
      }
    } : {
      image: {
        url: `https://cdn.brand.com/${item.url}`,
        width,
        height
      }
    }
  };
});

const result = await agent.syncCreatives({ creatives });
console.log(`Uploaded ${result.synced_creatives.length} creatives`);
```

### Upload with Assignments

Link creatives to packages during upload:

```javascript
await agent.syncCreatives({
  creatives: [
    {
      creative_id: 'video_30s_version_a',
      name: 'Video 30s - Version A',
      format_id: {
        agent_url: 'https://creative.adcontextprotocol.org',
        id: 'video_standard_30s'
      },
      assets: { /* ... */ }
    },
    {
      creative_id: 'video_30s_version_b',
      name: 'Video 30s - Version B',
      format_id: {
        agent_url: 'https://creative.adcontextprotocol.org',
        id: 'video_standard_30s'
      },
      assets: { /* ... */ }
    }
  ],
  assignments: {
    'video_30s_version_a': ['pkg-001', 'pkg-002'],  // Assign to multiple packages
    'video_30s_version_b': ['pkg-003']
  }
});
```

## Creative Library Management

### Querying Creatives

```javascript
// List all active creatives
const all = await agent.listCreatives({
  filters: { status: ['active'] }
});

// Filter by format type
const videos = await agent.listCreatives({
  filters: {
    status: ['active'],
    format_types: ['video']
  }
});

// Search by name
const results = await agent.listCreatives({
  filters: {
    search: 'holiday campaign'
  }
});

// Get specific creatives
const specific = await agent.listCreatives({
  filters: {
    creative_ids: ['creative_001', 'creative_002', 'creative_003']
  }
});
```

### Pagination

```javascript
async function getAllCreatives() {
  const allCreatives = [];
  let offset = 0;
  const limit = 50;
  let hasMore = true;
  
  while (hasMore) {
    const result = await agent.listCreatives({
      limit,
      offset,
      sort_by: 'created_at',
      sort_order: 'desc'
    });
    
    allCreatives.push(...result.creatives);
    hasMore = result.has_more;
    offset += limit;
  }
  
  return allCreatives;
}
```

### Organizing Creatives

Use naming conventions for easy management:

```javascript
// Format: [campaign]-[format]-[variant]-[version]
const namingExamples = [
  'q1-launch-display-300x250-hero-v1',
  'q1-launch-display-728x90-hero-v1',
  'q1-launch-video-30s-product-v2',
  'holiday-sale-display-300x250-promo-v1'
];

// Query by campaign
const q1Creatives = await agent.listCreatives({
  filters: { search: 'q1-launch' }
});
```

## Creative Assignment

### Assigning During Campaign Creation

```javascript
const campaign = await agent.createMediaBuy({
  buyer_ref: 'campaign-001',
  brand_manifest: { url: 'https://brand.com' },
  packages: [{
    buyer_ref: 'pkg-001',
    product_id: 'product_001',
    pricing_option_id: 'cpm-standard',
    budget: 10000,
    
    // Option 1: Inline creatives
    creatives: [
      {
        creative_id: 'inline_creative_001',
        format_id: { /* ... */ },
        assets: { /* ... */ }
      }
    ],
    
    // Option 2: Reference existing creatives
    creative_ids: ['existing_creative_001', 'existing_creative_002']
  }],
  start_time: { type: 'asap' },
  end_time: '2026-12-31T23:59:59Z'
});
```

### Updating Assignments

```javascript
// Reassign creatives after upload
await agent.syncCreatives({
  creatives: [],  // No new creatives
  assignments: {
    'creative_001': ['pkg-001', 'pkg-002'],
    'creative_002': ['pkg-003']
  }
});

// Or update via campaign
await agent.updateMediaBuy({
  media_buy_id: 'mb_abc123',
  updates: {
    package_updates: [{
      package_id: 'pkg-001',
      creative_ids: ['new_creative_001', 'new_creative_002']
    }]
  }
});
```

## Creative Validation

### Pre-Upload Validation

```javascript
async function validateCreative(creative, formatSpec) {
  const errors = [];
  
  // Check dimensions
  if (creative.assets.image) {
    if (creative.assets.image.width !== formatSpec.specifications.width) {
      errors.push(`Width mismatch: ${creative.assets.image.width} vs ${formatSpec.specifications.width}`);
    }
    if (creative.assets.image.height !== formatSpec.specifications.height) {
      errors.push(`Height mismatch: ${creative.assets.image.height} vs ${formatSpec.specifications.height}`);
    }
  }
  
  // Check video duration
  if (creative.assets.video) {
    const duration = creative.assets.video.duration_ms;
    if (formatSpec.specifications.min_duration_ms && duration < formatSpec.specifications.min_duration_ms) {
      errors.push(`Video too short: ${duration}ms < ${formatSpec.specifications.min_duration_ms}ms`);
    }
    if (formatSpec.specifications.max_duration_ms && duration > formatSpec.specifications.max_duration_ms) {
      errors.push(`Video too long: ${duration}ms > ${formatSpec.specifications.max_duration_ms}ms`);
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

// Usage
const formats = await agent.listCreativeFormats({});
const format = formats.formats.find(f => f.format_id.id === 'display_300x250');
const validation = await validateCreative(myCreative, format);

if (!validation.valid) {
  console.error('Validation errors:', validation.errors);
}
```

### Dry Run Testing

```javascript
// Test upload without committing
const preview = await agent.syncCreatives({
  creatives: [myCreative],
  dry_run: true
});

console.log('Preview results:');
preview.synced_creatives.forEach(result => {
  console.log(`${result.creative_id}: ${result.status}`);
  if (result.rejection_reasons) {
    console.log('  Reasons:', result.rejection_reasons);
  }
});
```

## Performance Tracking

### Creative Performance Analysis

```javascript
async function analyzeCreativePerformance(mediaBuyId) {
  const delivery = await agent.getMediaBuyDelivery({
    media_buy_id: mediaBuyId,
    dimensions: ['creative']
  });
  
  if (!delivery.by_creative) {
    console.log('No creative performance data available');
    return;
  }
  
  // Calculate efficiency scores
  const performance = delivery.by_creative.map(creative => ({
    creative_id: creative.creative_id,
    impressions: creative.impressions,
    clicks: creative.clicks || 0,
    ctr: (creative.clicks || 0) / creative.impressions,
    cpm: (creative.spend / creative.impressions) * 1000,
    efficiency_score: ((creative.clicks || 0) / creative.impressions) * (creative.impressions / creative.spend)
  }));
  
  // Rank by efficiency
  performance.sort((a, b) => b.efficiency_score - a.efficiency_score);
  
  console.log('Creative Performance Rankings:');
  performance.forEach((p, index) => {
    console.log(`${index + 1}. ${p.creative_id}`);
    console.log(`   CTR: ${(p.ctr * 100).toFixed(3)}%`);
    console.log(`   CPM: $${p.cpm.toFixed(2)}`);
    console.log(`   Efficiency: ${p.efficiency_score.toFixed(2)}`);
  });
  
  return performance;
}
```

### Creative Rotation Optimization

```javascript
async function optimizeCreativeRotation(mediaBuyId) {
  const performance = await analyzeCreativePerformance(mediaBuyId);
  
  // Find top 3 performers
  const topCreatives = performance.slice(0, 3).map(p => p.creative_id);
  
  console.log(`\nOptimizing to use top performers: ${topCreatives.join(', ')}`);
  
  // Update campaign to use only top performers
  await agent.updateMediaBuy({
    media_buy_id: mediaBuyId,
    updates: {
      package_updates: [{
        package_id: 'pkg-001',
        creative_ids: topCreatives
      }]
    }
  });
  
  console.log('✅ Creative rotation optimized');
}
```

## Best Practices

### 1. Maintain Creative Library

Organize creatives systematically:

```javascript
// Use consistent naming
const naming = {
  pattern: '[campaign]-[format]-[message]-[version]',
  examples: [
    'spring-2026-display-300x250-sale-v1',
    'spring-2026-video-30s-product-v1'
  ]
};

// Track creative metadata
const creativeMetadata = {
  creative_id: 'spring-2026-display-300x250-sale-v1',
  campaign: 'spring-2026',
  format: 'display-300x250',
  message: 'sale',
  version: 'v1',
  created_date: '2026-01-15',
  designer: 'John Doe'
};
```

### 2. Version Control

Track creative versions:

```javascript
// Use version suffixes
const versions = [
  'banner-300x250-hero-v1',  // Original
  'banner-300x250-hero-v2',  // Headline changed
  'banner-300x250-hero-v3'   // CTA updated
];

// Document changes
const versionLog = {
  'v1': 'Initial version',
  'v2': 'Updated headline for clarity',
  'v3': 'Strengthened call-to-action'
};
```

### 3. Test Multiple Variations

Always A/B test creatives:

```javascript
// Upload test variations
const variations = ['variant_a', 'variant_b', 'variant_c'];

await agent.syncCreatives({
  creatives: variations.map(v => ({
    creative_id: `test-${v}`,
    name: `Test - ${v}`,
    format_id: { /* ... */ },
    assets: { /* ... */ }
  })),
  assignments: {
    'test-variant_a': ['pkg-001'],
    'test-variant_b': ['pkg-001'],
    'test-variant_c': ['pkg-001']
  }
});
```

### 4. Archive Old Creatives

Keep library clean:

```javascript
// Archive outdated creatives
await agent.syncCreatives({
  creatives: [{
    creative_id: 'old_creative',
    status: 'archived'
  }]
});

// Query only active
const active = await agent.listCreatives({
  filters: { status: ['active'] }
});
```

### 5. Monitor File Sizes

Optimize creative file sizes:

```javascript
// Check format requirements
const format = await agent.listCreativeFormats({
  format_types: ['display']
});

format.formats.forEach(f => {
  console.log(`${f.name}: Max ${f.specifications.max_file_size_kb}KB`);
});

// Optimize before upload
// - Compress images (use tools like TinyPNG, ImageOptim)
// - Optimize videos (H.264, proper bitrate)
// - Minify HTML/CSS/JS for HTML5 ads
```

## Summary

Effective creative management requires:

1. **Understanding format requirements** - Check specifications before building
2. **Systematic organization** - Use consistent naming and metadata
3. **Validation before upload** - Check dimensions, file sizes, durations
4. **Performance tracking** - Monitor CTR, completion rates, efficiency
5. **Continuous optimization** - Test variations, optimize based on data

AdCP's creative management system provides the tools needed to deliver high-quality advertising at scale.
