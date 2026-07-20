# Advanced Targeting Strategies

Comprehensive guide to audience targeting with AdCP.

**Official AdCP Documentation**: https://docs.adcontextprotocol.org  
**Targeting Documentation**: https://docs.adcontextprotocol.org/docs/media-buy/advanced-topics/targeting

This guide provides practical targeting strategies for AdCP campaigns. For the complete targeting specification, see the [official AdCP targeting documentation](https://docs.adcontextprotocol.org/docs/media-buy/advanced-topics/targeting).

## Overview

AdCP supports four targeting dimensions:
1. **Geographic** - Location-based targeting
2. **Demographic** - Age, gender, income
3. **Behavioral** - Interests, purchase intent, browsing history
4. **Contextual** - Keywords, content categories, topics

Targeting is **additive**: Product targeting + Your overlay = Final targeting

## Geographic Targeting

### Supported Types

```typescript
geo: {
  included?: string[];   // Locations to target
  excluded?: string[];   // Locations to exclude
}
```

### DMA Codes (Designated Market Areas)

Target specific US media markets:

```javascript
targeting_overlay: {
  geo: {
    included: [
      'US-NY',    // New York
      'US-LA',    // Los Angeles
      'US-CHI',   // Chicago
      'US-PHI',   // Philadelphia
      'US-DAL',   // Dallas-Fort Worth
      'US-SF',    // San Francisco-Oakland-San Jose
      'US-ATL',   // Atlanta
      'US-BOS',   // Boston
      'US-DC',    // Washington DC
      'US-HOU'    // Houston
    ]
  }
}
```

### State Targeting

Target entire US states:

```javascript
targeting_overlay: {
  geo: {
    included: ['US-CA', 'US-NY', 'US-TX', 'US-FL']
  }
}
```

### ZIP Code Targeting

Precise location targeting:

```javascript
targeting_overlay: {
  geo: {
    included: [
      'US-10001',  // Manhattan
      'US-10002',  // Manhattan
      'US-90210',  // Beverly Hills
      'US-94102'   // San Francisco
    ]
  }
}
```

### Country Targeting

International campaigns:

```javascript
targeting_overlay: {
  geo: {
    included: ['US', 'CA', 'GB', 'AU'],  // Multiple countries
    excluded: []
  }
}
```

### Geo Exclusions

Exclude specific locations:

```javascript
targeting_overlay: {
  geo: {
    included: ['US'],           // All US
    excluded: ['US-AK', 'US-HI'] // Exclude Alaska and Hawaii
  }
}
```

### Radius Targeting

Target around specific points (if supported by agent):

```javascript
targeting_overlay: {
  geo: {
    radius: {
      lat: 37.7749,
      lng: -122.4194,
      radius_km: 10,
      type: 'center'
    }
  }
}
```

## Demographic Targeting

### Age Ranges

Target specific age groups:

```javascript
targeting_overlay: {
  demographics: {
    age_ranges: [
      { min: 18, max: 24 },  // Gen Z
      { min: 25, max: 34 }   // Millennials
    ]
  }
}
```

**Common Age Segments**:
- 18-24: Gen Z
- 25-34: Millennials (younger)
- 35-44: Millennials (older)
- 45-54: Gen X
- 55-64: Baby Boomers (younger)
- 65+: Baby Boomers (older) / Silent Generation

### Gender Targeting

```javascript
targeting_overlay: {
  demographics: {
    genders: ['M', 'F', 'O']  // Male, Female, Other
  }
}
```

### Income Brackets

Target by household income:

```javascript
targeting_overlay: {
  demographics: {
    income_brackets: [
      '50k-75k',
      '75k-100k',
      '100k+'
    ]
  }
}
```

**Standard Income Brackets**:
- '0-25k': Low income
- '25k-50k': Lower-middle income
- '50k-75k': Middle income
- '75k-100k': Upper-middle income
- '100k+': High income
- '150k+': Very high income

### Household Composition

Target by family structure (if supported):

```javascript
targeting_overlay: {
  demographics: {
    household: {
      has_children: true,
      household_size: [3, 4, 5]
    }
  }
}
```

## Behavioral Targeting

### Interests

Target users based on interests:

```javascript
targeting_overlay: {
  behavioral: {
    interests: [
      'technology',
      'gaming',
      'travel',
      'fitness',
      'cooking',
      'fashion',
      'automotive',
      'real_estate'
    ]
  }
}
```

**Common Interest Categories**:
- **Technology**: tech_enthusiast, early_adopter, software, hardware
- **Lifestyle**: fitness, wellness, outdoor, travel, luxury
- **Entertainment**: gaming, movies, music, sports
- **Shopping**: fashion, beauty, home_decor, consumer_electronics
- **Finance**: investing, banking, cryptocurrency
- **Business**: entrepreneurship, b2b, professional_services

### Purchase Intent

Target users actively researching products:

```javascript
targeting_overlay: {
  behavioral: {
    purchase_intent: [
      'automotive',
      'consumer_electronics',
      'home_appliances',
      'travel_services',
      'financial_services'
    ]
  }
}
```

**High-Intent Categories**:
- Automotive (car shopping)
- Real estate (home buying)
- Consumer electronics
- Travel services
- Financial products
- Education/courses
- B2B software

### Life Events

Target users experiencing major life changes:

```javascript
targeting_overlay: {
  behavioral: {
    life_events: [
      'new_parent',
      'recently_moved',
      'job_change',
      'wedding',
      'graduation'
    ]
  }
}
```

### Website Visitors

Retarget your website visitors (requires pixel):

```javascript
targeting_overlay: {
  behavioral: {
    retargeting: {
      pixel_id: 'your-pixel-id',
      lookback_days: 30,
      pages_visited: ['/product/*', '/pricing']
    }
  }
}
```

## Contextual Targeting

### Keywords

Target based on page content:

```javascript
targeting_overlay: {
  contextual: {
    keywords: [
      'innovation',
      'technology',
      'artificial intelligence',
      'machine learning',
      'cloud computing'
    ]
  }
}
```

### IAB Categories

Target by standardized content categories:

```javascript
targeting_overlay: {
  contextual: {
    categories: [
      'IAB19',    // Technology & Computing
      'IAB13',    // Personal Finance
      'IAB3',     // Business
      'IAB20',    // Travel
      'IAB1'      // Arts & Entertainment
    ]
  }
}
```

**Common IAB Categories**:
- IAB1: Arts & Entertainment
- IAB2: Automotive
- IAB3: Business
- IAB4: Careers
- IAB5: Education
- IAB6: Family & Parenting
- IAB7: Health & Fitness
- IAB8: Food & Drink
- IAB9: Hobbies & Interests
- IAB10: Home & Garden
- IAB11: Law, Government & Politics
- IAB12: News
- IAB13: Personal Finance
- IAB14: Society
- IAB15: Science
- IAB16: Pets
- IAB17: Sports
- IAB18: Style & Fashion
- IAB19: Technology & Computing
- IAB20: Travel
- IAB21: Real Estate
- IAB22: Shopping
- IAB23: Religion & Spirituality
- IAB24: Uncategorized
- IAB25: Non-Standard Content
- IAB26: Illegal Content

### Content Safety

Exclude sensitive content:

```javascript
targeting_overlay: {
  contextual: {
    exclude_categories: [
      'IAB25-1',  // Profanity
      'IAB25-2',  // Hate Speech
      'IAB25-3',  // Violence
      'IAB25-4',  // Adult Content
      'IAB26'     // Illegal Content
    ]
  }
}
```

### Topic Targeting

Target specific topics or themes:

```javascript
targeting_overlay: {
  contextual: {
    topics: [
      'artificial_intelligence',
      'sustainable_energy',
      'electric_vehicles',
      'remote_work'
    ]
  }
}
```

## Advanced Targeting Strategies

### Strategy 1: Funnel-Based Targeting

Different targeting for awareness vs. conversion:

```javascript
// Awareness stage - broad targeting
const awarenessTargeting = {
  geo: {
    included: ['US']
  },
  demographics: {
    age_ranges: [{ min: 25, max: 54 }]
  },
  contextual: {
    categories: ['IAB19']  // Technology
  }
};

// Consideration stage - interest-based
const considerationTargeting = {
  geo: {
    included: ['US']
  },
  demographics: {
    age_ranges: [{ min: 25, max: 54 }]
  },
  behavioral: {
    interests: ['technology', 'software'],
    purchase_intent: ['software']
  }
};

// Conversion stage - retargeting
const conversionTargeting = {
  behavioral: {
    retargeting: {
      pixel_id: 'your-pixel-id',
      lookback_days: 14,
      pages_visited: ['/product/*', '/pricing']
    }
  }
};
```

### Strategy 2: Multi-Persona Targeting

Create separate packages for different personas:

```javascript
const campaign = await agent.createMediaBuy({
  buyer_ref: 'multi-persona-campaign',
  brand_manifest: { url: 'https://brand.com' },
  packages: [
    // Tech Enthusiast Persona
    {
      buyer_ref: 'pkg-tech-enthusiasts',
      product_id: 'product_001',
      pricing_option_id: 'cpm-standard',
      budget: 15000,
      targeting_overlay: {
        demographics: {
          age_ranges: [{ min: 25, max: 44 }],
          genders: ['M', 'F']
        },
        behavioral: {
          interests: ['technology', 'early_adopter', 'gadgets']
        }
      }
    },
    // Business Professional Persona
    {
      buyer_ref: 'pkg-business-pros',
      product_id: 'product_001',
      pricing_option_id: 'cpm-standard',
      budget: 15000,
      targeting_overlay: {
        demographics: {
          age_ranges: [{ min: 30, max: 54 }],
          income_brackets: ['100k+']
        },
        behavioral: {
          interests: ['business', 'professional_development'],
          purchase_intent: ['b2b_software']
        }
      }
    },
    // Startup Founder Persona
    {
      buyer_ref: 'pkg-founders',
      product_id: 'product_001',
      pricing_option_id: 'cpm-standard',
      budget: 10000,
      targeting_overlay: {
        demographics: {
          age_ranges: [{ min: 25, max: 44 }]
        },
        behavioral: {
          interests: ['entrepreneurship', 'startups', 'venture_capital']
        },
        contextual: {
          keywords: ['startup', 'founder', 'entrepreneur']
        }
      }
    }
  ],
  start_time: { type: 'asap' },
  end_time: '2026-12-31T23:59:59Z'
});
```

### Strategy 3: Geo-Conquesting

Target competitors' locations:

```javascript
targeting_overlay: {
  geo: {
    radius: [
      { lat: 37.7749, lng: -122.4194, radius_km: 2 },  // Competitor Store 1
      { lat: 37.8044, lng: -122.2712, radius_km: 2 },  // Competitor Store 2
      { lat: 37.3382, lng: -121.8863, radius_km: 2 }   // Competitor Store 3
    ]
  },
  behavioral: {
    interests: ['retail_shopping'],
    purchase_intent: ['consumer_electronics']
  }
}
```

### Strategy 4: Dayparting + Geo

Optimize by time and location:

```javascript
// Morning commute in major cities
const morningCommute = {
  geo: {
    included: ['US-NY', 'US-LA', 'US-CHI']
  },
  schedule: {
    hours: [6, 7, 8, 9],  // 6am-10am
    days: [1, 2, 3, 4, 5]  // Weekdays
  }
};

// Evening leisure nationwide
const eveningLeisure = {
  geo: {
    included: ['US']
  },
  schedule: {
    hours: [18, 19, 20, 21],  // 6pm-10pm
    days: [1, 2, 3, 4, 5, 6, 7]  // All week
  }
};
```

### Strategy 5: Lookalike Audiences

Target users similar to your best customers:

```javascript
targeting_overlay: {
  behavioral: {
    lookalike: {
      source_audience_id: 'best-customers',
      similarity: 0.8,  // 80% similarity
      size: 'balanced'  // 'narrow', 'balanced', 'broad'
    }
  }
}
```

## Targeting Validation

### Check Available Targeting

Always verify what targeting is supported:

```javascript
const capabilities = await agent.getAdcpCapabilities({});

console.log('Geo targeting:', capabilities.media_buy.execution.geo_targeting);
console.log('Supported types:', capabilities.media_buy.execution.geo_targeting.supported_types);
```

### Estimate Reach

Check audience size before launching:

```javascript
const products = await agent.getProducts({
  brief: 'Campaign with specific targeting',
  brand_manifest: { url: 'https://brand.com' }
});

products.products.forEach(product => {
  if (product.inventory_estimate) {
    console.log(`${product.name}:`);
    console.log(`  Estimated reach: ${product.inventory_estimate.min_impressions} - ${product.inventory_estimate.max_impressions} impressions`);
    console.log(`  Audience size: ${product.inventory_estimate.audience_size} users`);
  }
});
```

## Best Practices

### 1. Start Broad, Then Narrow

Begin with broader targeting and refine based on performance:

```javascript
// Week 1: Broad
{ age_ranges: [{ min: 25, max: 54 }] }

// Week 2: Based on data, narrow
{ age_ranges: [{ min: 30, max: 44 }] }
```

### 2. Layer Targeting Dimensions

Combine multiple targeting types:

```javascript
targeting_overlay: {
  geo: { included: ['US-CA'] },
  demographics: { age_ranges: [{ min: 25, max: 44 }] },
  behavioral: { interests: ['technology'] },
  contextual: { categories: ['IAB19'] }
}
```

### 3. Test One Dimension at a Time

Isolate targeting variables for testing:

```javascript
// Package A: Geo only
{ geo: { included: ['US-CA'] } }

// Package B: Demo only
{ demographics: { age_ranges: [{ min: 25, max: 44 }] } }

// Package C: Both
{ 
  geo: { included: ['US-CA'] },
  demographics: { age_ranges: [{ min: 25, max: 44 }] }
}
```

### 4. Monitor Performance by Dimension

Analyze delivery by targeting dimension:

```javascript
const delivery = await agent.getMediaBuyDelivery({
  media_buy_id: 'mb_abc123',
  dimensions: ['geo', 'demographics']
});

// See which locations perform best
delivery.by_geo?.forEach(geo => {
  console.log(`${geo.geo_code}: CTR ${(geo.ctr * 100).toFixed(2)}%`);
});
```

### 5. Exclude Underperformers

Use exclusions to improve efficiency:

```javascript
targeting_overlay: {
  geo: {
    included: ['US'],
    excluded: ['US-WY', 'US-VT']  // Exclude low-performing states
  }
}
```

## Summary

Effective targeting requires:
1. **Understanding your audience** - Demographics, interests, behaviors
2. **Product targeting alignment** - Check what products already target
3. **Layering dimensions** - Combine geo, demo, behavioral, contextual
4. **Testing and optimization** - Start broad, refine based on data
5. **Performance monitoring** - Track by dimension and optimize

Use AdCP's flexible targeting system to reach the right audience at the right time with the right message.
