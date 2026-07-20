# AdCP Task Reference

Complete API reference for all AdCP Media Buy Protocol tasks.

**Official AdCP Documentation**: https://docs.adcontextprotocol.org  
**Media Buy Task Reference**: https://docs.adcontextprotocol.org/docs/media-buy/task-reference/  
**Complete Documentation Index**: https://docs.adcontextprotocol.org/llms.txt

This document provides detailed reference for implementing AdCP tasks. For the official specification and latest updates, always refer to the [official AdCP documentation](https://docs.adcontextprotocol.org).

## Table of Contents

1. [get_adcp_capabilities](#get_adcp_capabilities)
2. [get_products](#get_products)
3. [list_creative_formats](#list_creative_formats)
4. [create_media_buy](#create_media_buy)
5. [update_media_buy](#update_media_buy)
6. [sync_creatives](#sync_creatives)
7. [list_creatives](#list_creatives)
8. [get_media_buy_delivery](#get_media_buy_delivery)

---

## get_adcp_capabilities

**Purpose**: Discover agent capabilities, portfolio, and supported features. **Always start here** when working with a new agent.

**Response Time**: ~1 second

**Authentication**: Not required (public endpoint)

### Request Schema

```typescript
{} // No parameters required
```

### Response Schema

```typescript
{
  adcp: {
    major_versions: string[];           // Supported AdCP versions (e.g., ["3"])
    implementation_version: string;     // Agent implementation version
    agent_name: string;                 // Human-readable agent name
    agent_url: string;                  // Agent base URL
  };
  
  supported_protocols: string[];        // ["media_buy", "signals", "governance", etc.]
  
  media_buy?: {
    portfolio: {
      publishers: string[];             // Publisher domains (e.g., ["nytimes.com"])
      primary_channels: string[];       // Main channels (e.g., ["display", "video"])
      primary_countries: string[];      // Main markets (e.g., ["US", "CA"])
    };
    
    execution: {
      geo_targeting: {
        supported_types: string[];      // ["dma", "zip", "state", "country"]
        coverage: string[];             // Geographic coverage codes
      };
      
      axe_integrations?: {              // Real-time execution capabilities
        brand_safety: boolean;
        frequency_capping: boolean;
        dynamic_audience: boolean;
      };
    };
    
    supported_channels: string[];       // All supported channels
    supported_format_types: string[];   // Creative format types
    supports_guaranteed: boolean;       // Supports guaranteed inventory
    supports_non_guaranteed: boolean;   // Supports programmatic inventory
  };
  
  signals?: {
    signal_types: string[];             // Supported signal types
  };
  
  governance?: {
    property_lists: boolean;            // Property list support
    content_standards: boolean;         // Content standards support
  };
  
  sponsored_intelligence?: {
    offering_types: string[];           // SI offering types
  };
}
```

### Example Request

```javascript
const capabilities = await agent.getAdcpCapabilities({});

console.log(capabilities.media_buy.portfolio);
// {
//   publishers: ["nytimes.com", "washingtonpost.com"],
//   primary_channels: ["display", "video", "native"],
//   primary_countries: ["US", "CA", "GB"]
// }

console.log(capabilities.media_buy.execution.geo_targeting);
// {
//   supported_types: ["dma", "state", "country"],
//   coverage: ["US", "CA"]
// }
```

### Use Cases

- **Initial discovery**: Understand agent capabilities before making requests
- **Feature detection**: Check if specific features are supported
- **Portfolio matching**: Verify agent covers your target markets
- **Format validation**: Confirm creative format support

---

## get_products

**Purpose**: Discover advertising inventory using natural language briefs.

**Response Time**: ~60 seconds (involves AI/LLM processing)

**Authentication**: Optional (limited results without auth, full catalog with auth)

### Request Schema

```typescript
{
  brief: string;                        // Natural language campaign description
  
  brand_manifest: {                     // Brand context
    url?: string;                       // Brand URL (agent fetches info)
    name?: string;                      // Brand name
    tagline?: string;                   // Brand tagline
    colors?: {                          // Brand colors
      primary?: string;
      secondary?: string;
    };
    logo?: {
      url?: string;
    };
    // ... additional brand fields
  };
  
  filters?: {
    channels?: string[];                // Filter by channel (e.g., ["display", "video"])
    budget_range?: {
      min?: number;
      max?: number;
    };
    delivery_type?: string;             // "guaranteed" | "non-guaranteed"
    format_types?: string[];            // Filter by format type
    start_date?: string;                // ISO 8601 date
    end_date?: string;                  // ISO 8601 date
  };
}
```

### Response Schema

```typescript
{
  products: Array<{
    product_id: string;                 // Unique product identifier
    name: string;                       // Human-readable product name
    description: string;                // Product description
    
    channels: string[];                 // Supported channels
    delivery_type: string;              // "guaranteed" | "non-guaranteed"
    
    pricing_options: Array<{
      pricing_option_id: string;        // Use in create_media_buy
      pricing_model: string;            // "cpm", "cpm-auction", "flat-fee", etc.
      price?: number;                   // Base price (for fixed pricing)
      floor?: number;                   // Minimum bid (for auction)
      currency: string;                 // "USD", "EUR", etc.
    }>;
    
    format_ids: Array<{                 // Supported creative formats
      agent_url: string;
      id: string;
    }>;
    
    targeting?: {                       // Available targeting options
      geo?: {
        supported_types: string[];
        available_codes: string[];
      };
      demographics?: {
        age_ranges: boolean;
        genders: boolean;
        income_brackets: boolean;
      };
      behavioral?: {
        interests: string[];
        purchase_intent: string[];
      };
      contextual?: {
        keywords: boolean;
        categories: string[];
      };
    };
    
    inventory_estimate?: {              // Estimated reach
      min_impressions?: number;
      max_impressions?: number;
      audience_size?: number;
    };
    
    requirements?: {                    // Product requirements
      min_budget?: number;
      min_duration_days?: number;
      creative_review_required?: boolean;
      brand_safety_review?: boolean;
    };
  }>;
  
  total_count: number;                  // Total matching products
  has_more: boolean;                    // More results available
}
```

### Example Requests

**Basic product discovery**:
```javascript
const result = await agent.getProducts({
  brief: 'Premium video inventory for luxury automotive brand',
  brand_manifest: {
    url: 'https://lexus.com'
  }
});

result.products.forEach(product => {
  console.log(`${product.name}: ${product.description}`);
  console.log(`Channels: ${product.channels.join(', ')}`);
  console.log(`Pricing: ${JSON.stringify(product.pricing_options)}`);
});
```

**Filtered discovery**:
```javascript
const result = await agent.getProducts({
  brief: 'Tech startup brand awareness campaign targeting developers',
  brand_manifest: {
    name: 'Acme Corp',
    url: 'https://acme.com',
    tagline: 'Building the future of cloud infrastructure'
  },
  filters: {
    channels: ['display', 'video'],
    budget_range: { min: 10000, max: 50000 },
    delivery_type: 'guaranteed',
    start_date: '2026-02-01',
    end_date: '2026-03-31'
  }
});
```

### Brief Writing Best Practices

Write detailed, specific briefs for better matches:

**Good briefs**:
- "Premium video inventory for luxury automotive brand targeting high-income professionals aged 35-54 in major metros. Focus on brand awareness with completion rates above 70%."
- "Display and native advertising for DTC fashion brand launching spring collection. Target women 25-40 interested in sustainable fashion. Need viewability above 80%."
- "Connected TV campaign for streaming service targeting cord-cutters and millennials. Geographic focus on top 20 DMAs. Minimum 30-second completion required."

**Avoid vague briefs**:
- "video ads"
- "need advertising"
- "display campaign"

Include in briefs:
1. **Channel preferences** (display, video, CTV, audio, etc.)
2. **Target audience** (demographics, interests, behaviors)
3. **Campaign goals** (awareness, consideration, conversion)
4. **Geographic focus** (markets, regions, DMAs)
5. **Performance expectations** (completion rates, viewability, etc.)

---

## list_creative_formats

**Purpose**: View supported creative format specifications.

**Response Time**: ~1 second

**Authentication**: Not required (public endpoint)

### Request Schema

```typescript
{
  format_types?: string[];              // Filter to specific types (e.g., ["video", "display"])
  channels?: string[];                  // Filter by channel
  limit?: number;                       // Max results to return
}
```

### Response Schema

```typescript
{
  formats: Array<{
    format_id: {
      agent_url: string;                // Creative agent URL
      id: string;                       // Format identifier
    };
    
    name: string;                       // Human-readable name
    description?: string;               // Format description
    
    format_type: string;                // "video", "display", "audio", etc.
    channels: string[];                 // Applicable channels
    
    specifications: {
      // For display/image formats
      width?: number;
      height?: number;
      max_file_size_kb?: number;
      aspect_ratio?: string;
      
      // For video formats
      duration_ms?: number;
      min_duration_ms?: number;
      max_duration_ms?: number;
      video_codec?: string[];
      audio_codec?: string[];
      
      // For audio formats
      audio_duration_ms?: number;
      audio_bitrate_kbps?: number;
      
      // Common specs
      supported_mime_types?: string[];
      max_bitrate_kbps?: number;
    };
    
    asset_schema: {                     // Required assets structure
      [key: string]: {
        type: string;                   // "video", "image", "html", etc.
        required: boolean;
        description?: string;
      };
    };
  }>;
  
  total_count: number;
}
```

### Example Request

```javascript
const formats = await agent.listCreativeFormats({
  format_types: ['video', 'display']
});

formats.formats.forEach(format => {
  console.log(`${format.name} (${format.format_id.id})`);
  console.log(`Specs: ${JSON.stringify(format.specifications)}`);
  console.log(`Assets: ${Object.keys(format.asset_schema).join(', ')}`);
});
```

### Standard Format IDs

Common IAB standard formats from `https://creative.adcontextprotocol.org`:

**Display**:
- `display_300x250` - Medium Rectangle
- `display_728x90` - Leaderboard
- `display_160x600` - Wide Skyscraper
- `display_300x600` - Half Page
- `display_970x250` - Billboard

**Video**:
- `video_standard_15s` - 15 second pre-roll
- `video_standard_30s` - 30 second pre-roll
- `video_standard_60s` - 60 second mid-roll

**Native**:
- `native_standard` - Standard native ad unit

---

## create_media_buy

**Purpose**: Create an advertising campaign from selected products.

**Response Time**: Minutes to days (may require human approval)

**Authentication**: Required

### Request Schema

```typescript
{
  buyer_ref: string;                    // Your unique campaign identifier
  
  brand_manifest: {                     // Brand context (URL or inline)
    url?: string;
    name?: string;
    // ... full brand manifest fields
  };
  
  packages: Array<{
    buyer_ref: string;                  // Your unique package identifier
    product_id: string;                 // From get_products response
    pricing_option_id: string;          // From product's pricing_options
    
    budget: number;                     // Package budget in dollars
    bid_price?: number;                 // Required for auction pricing
    
    targeting_overlay?: {               // Additional targeting constraints
      geo?: {
        included?: string[];            // DMA/region codes to include
        excluded?: string[];            // DMA/region codes to exclude
      };
      demographics?: {
        age_ranges?: Array<{
          min?: number;
          max?: number;
        }>;
        genders?: string[];             // ["M", "F", "O"]
        income_brackets?: string[];
      };
      behavioral?: {
        interests?: string[];
        purchase_intent?: string[];
      };
      contextual?: {
        keywords?: string[];
        categories?: string[];          // IAB categories
      };
    };
    
    creative_ids?: string[];            // Assign existing creatives
    creatives?: Array<{                 // Inline creative definitions
      creative_id: string;
      format_id: {
        agent_url: string;
        id: string;
      };
      assets: object;                   // Format-specific assets
    }>;
    
    frequency_cap?: {
      impressions: number;
      time_unit: string;                // "hour", "day", "week"
      time_count: number;
    };
  }>;
  
  start_time: {
    type: "asap" | "scheduled";
    datetime?: string;                  // ISO 8601 (if scheduled)
  };
  
  end_time: string;                     // ISO 8601 datetime
  
  optimization_goal?: string;           // "impressions", "clicks", "conversions"
  pacing?: string;                      // "even", "asap"
}
```

### Response Schema

```typescript
{
  media_buy_id: string;                 // Created campaign identifier
  status: string;                       // "pending", "active", "rejected", etc.
  
  packages: Array<{
    package_id: string;                 // Created package identifier
    buyer_ref: string;                  // Your package reference
    status: string;
  }>;
  
  created_at: string;                   // ISO 8601 timestamp
  
  // If status is "pending"
  task_id?: string;                     // For tracking approval status
  approval_url?: string;                // Human approval URL (if required)
  estimated_approval_time_hours?: number;
  
  // If status is "rejected"
  rejection_reasons?: Array<{
    field?: string;
    message: string;
    code: string;
  }>;
}
```

### Example Requests

**Basic campaign creation**:
```javascript
const campaign = await agent.createMediaBuy({
  buyer_ref: 'campaign-2026-q1-tech-launch',
  brand_manifest: {
    url: 'https://startup.com'
  },
  packages: [
    {
      buyer_ref: 'pkg-display-001',
      product_id: 'premium_display',
      pricing_option_id: 'cpm-standard',
      budget: 10000
    }
  ],
  start_time: { type: 'asap' },
  end_time: '2026-03-31T23:59:59Z'
});

console.log(`Campaign ID: ${campaign.media_buy_id}`);
console.log(`Status: ${campaign.status}`);

if (campaign.status === 'pending') {
  console.log(`Approval required. Task ID: ${campaign.task_id}`);
}
```

**Campaign with targeting and creatives**:
```javascript
const campaign = await agent.createMediaBuy({
  buyer_ref: 'campaign-luxury-auto-q1',
  brand_manifest: {
    url: 'https://lexus.com',
    name: 'Lexus'
  },
  packages: [
    {
      buyer_ref: 'pkg-video-premium',
      product_id: 'premium_video_30s',
      pricing_option_id: 'cpm-auction',
      budget: 50000,
      bid_price: 25.00,
      
      targeting_overlay: {
        geo: {
          included: ['US-CA', 'US-NY', 'US-FL'],
          excluded: []
        },
        demographics: {
          age_ranges: [{ min: 35, max: 54 }],
          genders: ['M', 'F'],
          income_brackets: ['100k+']
        },
        behavioral: {
          interests: ['luxury_automotive', 'technology'],
          purchase_intent: ['automotive']
        }
      },
      
      creatives: [
        {
          creative_id: 'lexus_es_30s_v1',
          format_id: {
            agent_url: 'https://creative.adcontextprotocol.org',
            id: 'video_standard_30s'
          },
          assets: {
            video: {
              url: 'https://cdn.lexus.com/ads/es_30s.mp4',
              width: 1920,
              height: 1080,
              duration_ms: 30000
            }
          }
        }
      ],
      
      frequency_cap: {
        impressions: 3,
        time_unit: 'day',
        time_count: 1
      }
    }
  ],
  start_time: {
    type: 'scheduled',
    datetime: '2026-02-01T00:00:00Z'
  },
  end_time: '2026-03-31T23:59:59Z',
  optimization_goal: 'impressions',
  pacing: 'even'
});
```

### Important Notes

1. **Status handling**: Always check `status` field. `pending` means awaiting approval.
2. **Buyer references**: Use descriptive, unique values for tracking
3. **Targeting is additive**: Your overlay + product targeting = final targeting
4. **Creative validation**: Ensure creatives match format requirements
5. **Budget minimums**: Check product `requirements.min_budget`
6. **Auction pricing**: Must include `bid_price` for auction pricing models

---

## update_media_buy

**Purpose**: Modify an existing campaign (budget, targeting, status, etc.).

**Response Time**: Minutes to days (may require human approval)

**Authentication**: Required

### Request Schema

```typescript
{
  media_buy_id: string;                 // Campaign to update
  
  updates: {
    status?: string;                    // "active", "paused", "cancelled"
    
    budget_change?: number;             // Add/subtract from total budget
    end_time?: string;                  // Extend/shorten campaign
    
    targeting?: {                       // Update targeting (replaces existing)
      geo?: object;
      demographics?: object;
      behavioral?: object;
      contextual?: object;
    };
    
    optimization_goal?: string;         // Change optimization
    pacing?: string;                    // Change pacing strategy
    
    package_updates?: Array<{
      package_id: string;
      budget_change?: number;
      status?: string;
      targeting_overlay?: object;
      creative_ids?: string[];          // Reassign creatives
    }>;
  };
}
```

### Response Schema

```typescript
{
  media_buy_id: string;
  status: string;                       // Current campaign status
  
  updated_at: string;                   // ISO 8601 timestamp
  
  // If update requires approval
  task_id?: string;
  approval_url?: string;
  
  // If update was rejected
  rejection_reasons?: Array<{
    field?: string;
    message: string;
    code: string;
  }>;
}
```

### Example Requests

**Pause campaign**:
```javascript
await agent.updateMediaBuy({
  media_buy_id: 'mb_abc123',
  updates: {
    status: 'paused'
  }
});
```

**Increase budget**:
```javascript
await agent.updateMediaBuy({
  media_buy_id: 'mb_abc123',
  updates: {
    budget_change: 5000  // Add $5000 to campaign
  }
});
```

**Extend campaign and update targeting**:
```javascript
await agent.updateMediaBuy({
  media_buy_id: 'mb_abc123',
  updates: {
    end_time: '2026-04-30T23:59:59Z',
    targeting: {
      geo: {
        included: ['US-CA', 'US-NY', 'US-TX']  // Add Texas
      }
    }
  }
});
```

**Update specific package**:
```javascript
await agent.updateMediaBuy({
  media_buy_id: 'mb_abc123',
  updates: {
    package_updates: [
      {
        package_id: 'pkg_xyz789',
        budget_change: 2500,
        creative_ids: ['creative_001', 'creative_002']  // Swap creatives
      }
    ]
  }
});
```

---

## sync_creatives

**Purpose**: Upload and synchronize creative assets with the agent.

**Response Time**: Minutes to days (may require review/approval)

**Authentication**: Required

### Request Schema

```typescript
{
  creatives: Array<{
    creative_id: string;                // Your unique creative identifier
    name: string;                       // Human-readable name
    
    format_id: {
      agent_url: string;
      id: string;
    };
    
    assets: {                           // Format-specific asset structure
      video?: {
        url: string;
        width: number;
        height: number;
        duration_ms: number;
        mime_type?: string;
      };
      image?: {
        url: string;
        width: number;
        height: number;
        mime_type?: string;
      };
      html?: {
        content: string;
        width: number;
        height: number;
      };
      // ... other asset types
    };
    
    click_through_url?: string;
    tracking_pixels?: string[];
    
    status?: string;                    // "active", "archived"
  }>;
  
  assignments?: {                       // Map creative_id to package IDs
    [creative_id: string]: string[];
  };
  
  dry_run?: boolean;                    // Preview changes without applying
  delete_missing?: boolean;             // Archive creatives not in this sync
}
```

### Response Schema

```typescript
{
  synced_creatives: Array<{
    creative_id: string;
    status: string;                     // "synced", "pending_review", "rejected"
    
    // If pending review
    task_id?: string;
    review_url?: string;
    
    // If rejected
    rejection_reasons?: Array<{
      field?: string;
      message: string;
      code: string;
    }>;
  }>;
  
  assignments_updated: boolean;
  deleted_creatives?: string[];         // IDs of archived creatives
}
```

### Example Requests

**Upload video creative**:
```javascript
await agent.syncCreatives({
  creatives: [
    {
      creative_id: 'brand_hero_30s',
      name: 'Brand Hero Video 30s',
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
      click_through_url: 'https://brand.com/products',
      tracking_pixels: [
        'https://analytics.brand.com/pixel?id=123'
      ]
    }
  ]
});
```

**Upload and assign to packages**:
```javascript
await agent.syncCreatives({
  creatives: [
    {
      creative_id: 'display_300x250_v1',
      name: 'Display Banner 300x250',
      format_id: {
        agent_url: 'https://creative.adcontextprotocol.org',
        id: 'display_300x250'
      },
      assets: {
        image: {
          url: 'https://cdn.brand.com/banner.jpg',
          width: 300,
          height: 250,
          mime_type: 'image/jpeg'
        }
      }
    },
    {
      creative_id: 'display_728x90_v1',
      name: 'Display Leaderboard 728x90',
      format_id: {
        agent_url: 'https://creative.adcontextprotocol.org',
        id: 'display_728x90'
      },
      assets: {
        image: {
          url: 'https://cdn.brand.com/leaderboard.jpg',
          width: 728,
          height: 90,
          mime_type: 'image/jpeg'
        }
      }
    }
  ],
  assignments: {
    'display_300x250_v1': ['pkg-001', 'pkg-002'],
    'display_728x90_v1': ['pkg-001']
  }
});
```

**Dry run to preview changes**:
```javascript
const preview = await agent.syncCreatives({
  creatives: [...],
  assignments: {...},
  dry_run: true  // Preview without applying
});

console.log(`Would sync ${preview.synced_creatives.length} creatives`);
```

---

## list_creatives

**Purpose**: Query the creative library with filtering and search.

**Response Time**: ~1 second

**Authentication**: Required

### Request Schema

```typescript
{
  filters?: {
    status?: string[];                  // ["active", "archived"]
    format_types?: string[];            // ["video", "display"]
    creative_ids?: string[];            // Specific IDs to fetch
    search?: string;                    // Text search in name/description
  };
  
  sort_by?: string;                     // "created_at", "name", "updated_at"
  sort_order?: string;                  // "asc", "desc"
  
  limit?: number;                       // Max results (default 50)
  offset?: number;                      // Pagination offset
}
```

### Response Schema

```typescript
{
  creatives: Array<{
    creative_id: string;
    name: string;
    status: string;
    
    format_id: {
      agent_url: string;
      id: string;
    };
    
    format_type: string;                // "video", "display", etc.
    
    thumbnail_url?: string;             // Preview thumbnail
    
    created_at: string;                 // ISO 8601
    updated_at: string;
    
    assigned_packages?: string[];       // Package IDs using this creative
    
    performance_summary?: {             // Aggregate performance
      impressions: number;
      clicks: number;
      ctr: number;
    };
  }>;
  
  total_count: number;
  has_more: boolean;
}
```

### Example Requests

**List all active video creatives**:
```javascript
const result = await agent.listCreatives({
  filters: {
    status: ['active'],
    format_types: ['video']
  },
  sort_by: 'created_at',
  sort_order: 'desc',
  limit: 20
});

result.creatives.forEach(creative => {
  console.log(`${creative.name} (${creative.creative_id})`);
  console.log(`  Format: ${creative.format_id.id}`);
  console.log(`  Packages: ${creative.assigned_packages?.length || 0}`);
});
```

**Search by name**:
```javascript
const result = await agent.listCreatives({
  filters: {
    search: 'holiday campaign'
  }
});
```

**Paginate through all creatives**:
```javascript
let offset = 0;
const limit = 50;
let hasMore = true;

while (hasMore) {
  const result = await agent.listCreatives({
    limit,
    offset
  });
  
  // Process result.creatives
  
  hasMore = result.has_more;
  offset += limit;
}
```

---

## get_media_buy_delivery

**Purpose**: Retrieve performance metrics and delivery data for a campaign.

**Response Time**: ~60 seconds (data aggregation required)

**Authentication**: Required

### Request Schema

```typescript
{
  media_buy_id: string;                 // Campaign to query
  
  granularity?: string;                 // "hourly", "daily", "total"
  
  date_range?: {
    start: string;                      // YYYY-MM-DD
    end: string;                        // YYYY-MM-DD
  };
  
  dimensions?: string[];                // ["package", "creative", "geo", "device"]
  
  metrics?: string[];                   // Specific metrics to fetch
}
```

### Response Schema

```typescript
{
  media_buy_id: string;
  status: string;                       // Campaign status
  
  delivery: {
    impressions: number;
    clicks?: number;
    conversions?: number;
    
    spend: number;                      // Amount spent
    budget: number;                     // Total budget
    
    cpm?: number;                       // Cost per thousand
    cpc?: number;                       // Cost per click
    ctr?: number;                       // Click-through rate
    
    completion_rate?: number;           // Video completion rate
    viewability_rate?: number;          // Viewability percentage
    
    start_time: string;                 // ISO 8601
    end_time: string;
  };
  
  by_package?: Array<{
    package_id: string;
    buyer_ref: string;
    impressions: number;
    spend: number;
    // ... other metrics
  }>;
  
  by_creative?: Array<{
    creative_id: string;
    impressions: number;
    clicks?: number;
    ctr?: number;
    // ... other metrics
  }>;
  
  by_geo?: Array<{
    geo_code: string;                   // DMA/region code
    impressions: number;
    spend: number;
  }>;
  
  timeseries?: Array<{
    timestamp: string;                  // ISO 8601
    impressions: number;
    spend: number;
    // ... other metrics
  }>;
  
  pacing: {
    days_elapsed: number;
    days_total: number;
    percent_complete: number;
    
    spend_pacing: number;               // % of budget spent
    impression_pacing: number;          // % of impressions delivered
  };
}
```

### Example Requests

**Get overall campaign performance**:
```javascript
const delivery = await agent.getMediaBuyDelivery({
  media_buy_id: 'mb_abc123'
});

console.log(`Campaign Status: ${delivery.status}`);
console.log(`Impressions: ${delivery.delivery.impressions.toLocaleString()}`);
console.log(`Spend: $${delivery.delivery.spend.toLocaleString()}`);
console.log(`CPM: $${delivery.delivery.cpm?.toFixed(2)}`);
console.log(`Budget pacing: ${(delivery.pacing.spend_pacing * 100).toFixed(1)}%`);
```

**Get daily breakdown**:
```javascript
const delivery = await agent.getMediaBuyDelivery({
  media_buy_id: 'mb_abc123',
  granularity: 'daily',
  date_range: {
    start: '2026-01-01',
    end: '2026-01-31'
  }
});

delivery.timeseries?.forEach(day => {
  console.log(`${day.timestamp}: ${day.impressions} imps, $${day.spend}`);
});
```

**Get performance by package and creative**:
```javascript
const delivery = await agent.getMediaBuyDelivery({
  media_buy_id: 'mb_abc123',
  dimensions: ['package', 'creative']
});

console.log('Performance by Package:');
delivery.by_package?.forEach(pkg => {
  console.log(`  ${pkg.buyer_ref}: ${pkg.impressions} imps, $${pkg.spend}`);
});

console.log('\nPerformance by Creative:');
delivery.by_creative?.forEach(creative => {
  console.log(`  ${creative.creative_id}: CTR ${(creative.ctr * 100).toFixed(2)}%`);
});
```

**Monitor campaign pacing**:
```javascript
const delivery = await agent.getMediaBuyDelivery({
  media_buy_id: 'mb_abc123'
});

const pacing = delivery.pacing;
console.log(`Days ${pacing.days_elapsed} of ${pacing.days_total}`);
console.log(`Campaign ${(pacing.percent_complete * 100).toFixed(1)}% complete`);
console.log(`Budget ${(pacing.spend_pacing * 100).toFixed(1)}% spent`);
console.log(`Impressions ${(pacing.impression_pacing * 100).toFixed(1)}% delivered`);

// Alert if underpacing
if (pacing.spend_pacing < pacing.percent_complete - 0.1) {
  console.warn('⚠️ Campaign is underpacing - consider budget increase');
}
```

---

## Common Patterns

### Pattern 1: Campaign Health Check

```javascript
async function checkCampaignHealth(mediaBuyId) {
  const delivery = await agent.getMediaBuyDelivery({
    media_buy_id: mediaBuyId
  });
  
  const issues = [];
  
  // Check pacing
  const pacingDiff = delivery.pacing.spend_pacing - delivery.pacing.percent_complete;
  if (Math.abs(pacingDiff) > 0.15) {
    issues.push({
      type: 'pacing',
      severity: 'warning',
      message: `Campaign pacing off by ${(pacingDiff * 100).toFixed(1)}%`
    });
  }
  
  // Check performance
  if (delivery.delivery.ctr && delivery.delivery.ctr < 0.001) {
    issues.push({
      type: 'performance',
      severity: 'warning',
      message: `Low CTR: ${(delivery.delivery.ctr * 100).toFixed(3)}%`
    });
  }
  
  // Check viewability
  if (delivery.delivery.viewability_rate && delivery.delivery.viewability_rate < 0.7) {
    issues.push({
      type: 'quality',
      severity: 'error',
      message: `Low viewability: ${(delivery.delivery.viewability_rate * 100).toFixed(1)}%`
    });
  }
  
  return {
    status: delivery.status,
    health: issues.length === 0 ? 'healthy' : 'needs_attention',
    issues
  };
}
```

### Pattern 2: Budget Optimization

```javascript
async function optimizeBudgetAllocation(mediaBuyId) {
  const delivery = await agent.getMediaBuyDelivery({
    media_buy_id: mediaBuyId,
    dimensions: ['package']
  });
  
  // Rank packages by performance
  const ranked = delivery.by_package
    ?.map(pkg => ({
      ...pkg,
      efficiency: pkg.impressions / pkg.spend
    }))
    .sort((a, b) => b.efficiency - a.efficiency);
  
  console.log('Top performing packages:');
  ranked?.slice(0, 3).forEach((pkg, i) => {
    console.log(`${i + 1}. ${pkg.buyer_ref}: ${pkg.efficiency.toFixed(0)} imps/$`);
  });
  
  // Suggest reallocation
  const topPackage = ranked?.[0];
  const bottomPackage = ranked?.[ranked.length - 1];
  
  if (topPackage && bottomPackage) {
    const efficiencyDiff = topPackage.efficiency / bottomPackage.efficiency;
    if (efficiencyDiff > 2) {
      console.log(`\n💡 Consider reallocating budget from ${bottomPackage.buyer_ref} to ${topPackage.buyer_ref}`);
    }
  }
}
```

### Pattern 3: Creative A/B Testing

```javascript
async function analyzeCreativePerformance(mediaBuyId) {
  const delivery = await agent.getMediaBuyDelivery({
    media_buy_id: mediaBuyId,
    dimensions: ['creative']
  });
  
  if (!delivery.by_creative || delivery.by_creative.length < 2) {
    console.log('Need at least 2 creatives for comparison');
    return;
  }
  
  // Find winner
  const winner = delivery.by_creative.reduce((best, current) => {
    const currentScore = (current.ctr || 0) * (current.completion_rate || 1);
    const bestScore = (best.ctr || 0) * (best.completion_rate || 1);
    return currentScore > bestScore ? current : best;
  });
  
  console.log(`🏆 Winner: ${winner.creative_id}`);
  console.log(`   CTR: ${(winner.ctr * 100).toFixed(2)}%`);
  console.log(`   Completion: ${(winner.completion_rate * 100).toFixed(1)}%`);
  
  // Show all results
  console.log('\nAll creatives:');
  delivery.by_creative
    .sort((a, b) => (b.ctr || 0) - (a.ctr || 0))
    .forEach(creative => {
      const isWinner = creative.creative_id === winner.creative_id;
      console.log(`${isWinner ? '  🏆' : '    '} ${creative.creative_id}: CTR ${(creative.ctr * 100).toFixed(2)}%`);
    });
}
```

---

## Response Time Summary

| Task | Response Time | Reason |
| ------------------------ | --------------- | ----------------------------------------- |
| `get_adcp_capabilities` | ~1s | Simple database lookup |
| `list_creative_formats` | ~1s | Simple database lookup |
| `list_creatives` | ~1s | Simple database query |
| `get_products` | ~60s | AI/LLM processing for brief matching |
| `get_media_buy_delivery` | ~60s | Data aggregation and metric calculation |
| `create_media_buy` | Minutes-Days | May require human approval |
| `update_media_buy` | Minutes-Days | May require human approval |
| `sync_creatives` | Minutes-Days | Creative review and validation |

Always design for asynchronous operations and provide appropriate user feedback during processing.
