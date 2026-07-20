# AdCP Real-World Examples

Complete, working examples for common advertising scenarios using AdCP.

**Official AdCP Documentation**: https://docs.adcontextprotocol.org  
**Media Buy Protocol**: https://docs.adcontextprotocol.org/docs/media-buy/  
**Task Reference**: https://docs.adcontextprotocol.org/docs/media-buy/task-reference/

These examples demonstrate practical implementations of the Ad Context Protocol. For the complete specification and additional examples, see the [official AdCP documentation](https://docs.adcontextprotocol.org).

## Table of Contents

1. [Quick Start Examples](#quick-start-examples)
2. [Display Advertising Campaigns](#display-advertising-campaigns)
3. [Video Advertising Campaigns](#video-advertising-campaigns)
4. [Multi-Channel Campaigns](#multi-channel-campaigns)
5. [Campaign Optimization](#campaign-optimization)
6. [Creative Management](#creative-management)
7. [Advanced Targeting](#advanced-targeting)
8. [Performance Monitoring](#performance-monitoring)

---

## Quick Start Examples

### Example 1: Minimal Campaign

The simplest possible campaign - discover products and launch immediately.

```javascript
import { testAgent } from '@adcp/client/testing';

async function launchQuickCampaign() {
  // 1. Discover products
  const products = await testAgent.getProducts({
    brief: 'Display advertising for tech startup',
    brand_manifest: { url: 'https://startup.com' }
  });
  
  const firstProduct = products.products[0];
  
  // 2. Create campaign
  const campaign = await testAgent.createMediaBuy({
    buyer_ref: 'quick-campaign-001',
    brand_manifest: { url: 'https://startup.com' },
    packages: [{
      buyer_ref: 'pkg-001',
      product_id: firstProduct.product_id,
      pricing_option_id: firstProduct.pricing_options[0].pricing_option_id,
      budget: 5000
    }],
    start_time: { type: 'asap' },
    end_time: '2026-12-31T23:59:59Z'
  });
  
  console.log(`✅ Campaign created: ${campaign.media_buy_id}`);
}
```

### Example 2: Discover and Review

Explore available products before committing.

```javascript
async function exploreInventory() {
  // Discover products
  const result = await testAgent.getProducts({
    brief: 'Premium video inventory for luxury brand',
    brand_manifest: {
      name: 'Luxury Auto Corp',
      url: 'https://luxuryauto.com'
    },
    filters: {
      channels: ['video', 'ctv'],
      budget_range: { min: 20000, max: 100000 }
    }
  });
  
  console.log(`Found ${result.products.length} matching products:\n`);
  
  result.products.forEach((product, index) => {
    console.log(`${index + 1}. ${product.name}`);
    console.log(`   ${product.description}`);
    console.log(`   Channels: ${product.channels.join(', ')}`);
    console.log(`   Pricing: ${JSON.stringify(product.pricing_options[0])}`);
    
    if (product.inventory_estimate) {
      console.log(`   Estimated reach: ${product.inventory_estimate.min_impressions?.toLocaleString()} - ${product.inventory_estimate.max_impressions?.toLocaleString()} impressions`);
    }
    
    console.log(`   Formats: ${product.format_ids.map(f => f.id).join(', ')}`);
    console.log('');
  });
}
```

---

## Display Advertising Campaigns

### Example 3: Standard Display Campaign

Launch a multi-format display campaign with proper creatives.

```javascript
async function launchDisplayCampaign() {
  // 1. Discover capabilities
  const caps = await testAgent.getAdcpCapabilities({});
  console.log('Agent supports channels:', caps.media_buy.supported_channels);
  
  // 2. Find display products
  const products = await testAgent.getProducts({
    brief: 'Display advertising for e-commerce fashion brand targeting women 25-40',
    brand_manifest: {
      name: 'FashionCo',
      url: 'https://fashionco.com',
      tagline: 'Sustainable fashion for modern women',
      colors: {
        primary: '#E91E63',
        secondary: '#9C27B0'
      }
    },
    filters: {
      channels: ['display'],
      budget_range: { min: 10000, max: 30000 }
    }
  });
  
  const displayProduct = products.products.find(p => 
    p.channels.includes('display') && 
    p.format_ids.some(f => f.id.includes('300x250'))
  );
  
  if (!displayProduct) {
    throw new Error('No suitable display product found');
  }
  
  // 3. Check format requirements
  const formats = await testAgent.listCreativeFormats({
    format_types: ['display']
  });
  
  const requiredFormats = formats.formats.filter(f => 
    displayProduct.format_ids.some(pf => pf.id === f.format_id.id)
  );
  
  console.log('Required creative formats:');
  requiredFormats.forEach(f => {
    console.log(`  - ${f.name}: ${f.specifications.width}x${f.specifications.height}`);
  });
  
  // 4. Create campaign with creatives
  const campaign = await testAgent.createMediaBuy({
    buyer_ref: 'fashionco-spring-2026',
    brand_manifest: {
      name: 'FashionCo',
      url: 'https://fashionco.com'
    },
    packages: [{
      buyer_ref: 'pkg-display-spring',
      product_id: displayProduct.product_id,
      pricing_option_id: displayProduct.pricing_options[0].pricing_option_id,
      budget: 15000,
      
      targeting_overlay: {
        demographics: {
          age_ranges: [{ min: 25, max: 40 }],
          genders: ['F']
        },
        behavioral: {
          interests: ['fashion', 'sustainable_living', 'online_shopping']
        }
      },
      
      creatives: [
        {
          creative_id: 'spring_banner_300x250',
          format_id: {
            agent_url: 'https://creative.adcontextprotocol.org',
            id: 'display_300x250'
          },
          assets: {
            image: {
              url: 'https://cdn.fashionco.com/ads/spring_300x250.jpg',
              width: 300,
              height: 250,
              mime_type: 'image/jpeg'
            }
          },
          click_through_url: 'https://fashionco.com/spring-collection'
        },
        {
          creative_id: 'spring_leaderboard_728x90',
          format_id: {
            agent_url: 'https://creative.adcontextprotocol.org',
            id: 'display_728x90'
          },
          assets: {
            image: {
              url: 'https://cdn.fashionco.com/ads/spring_728x90.jpg',
              width: 728,
              height: 90,
              mime_type: 'image/jpeg'
            }
          },
          click_through_url: 'https://fashionco.com/spring-collection'
        }
      ],
      
      frequency_cap: {
        impressions: 5,
        time_unit: 'day',
        time_count: 1
      }
    }],
    start_time: { type: 'asap' },
    end_time: '2026-04-30T23:59:59Z',
    optimization_goal: 'clicks',
    pacing: 'even'
  });
  
  console.log(`✅ Display campaign created: ${campaign.media_buy_id}`);
  console.log(`   Status: ${campaign.status}`);
  
  if (campaign.status === 'pending') {
    console.log(`   ⏳ Awaiting approval - Task ID: ${campaign.task_id}`);
  }
}
```

### Example 4: Programmatic Display with Real-Time Bidding

Auction-based display campaign with bid optimization.

```javascript
async function launchProgrammaticDisplay() {
  const products = await testAgent.getProducts({
    brief: 'Programmatic display inventory with RTB support',
    brand_manifest: { url: 'https://brand.com' },
    filters: {
      channels: ['display'],
      delivery_type: 'non-guaranteed'
    }
  });
  
  // Find auction-based product
  const auctionProduct = products.products.find(p =>
    p.pricing_options.some(opt => opt.pricing_model === 'cpm-auction')
  );
  
  if (!auctionProduct) {
    throw new Error('No auction product found');
  }
  
  const auctionPricing = auctionProduct.pricing_options.find(
    opt => opt.pricing_model === 'cpm-auction'
  );
  
  // Calculate bid (20% above floor)
  const bidPrice = auctionPricing.floor * 1.2;
  
  const campaign = await testAgent.createMediaBuy({
    buyer_ref: 'programmatic-campaign-001',
    brand_manifest: { url: 'https://brand.com' },
    packages: [{
      buyer_ref: 'pkg-rtb-001',
      product_id: auctionProduct.product_id,
      pricing_option_id: auctionPricing.pricing_option_id,
      budget: 25000,
      bid_price: bidPrice,  // Required for auction
      
      targeting_overlay: {
        geo: {
          included: ['US-CA', 'US-NY', 'US-TX', 'US-FL']
        },
        contextual: {
          keywords: ['technology', 'innovation', 'business'],
          categories: ['IAB19']  // Technology & Computing
        }
      }
    }],
    start_time: { type: 'asap' },
    end_time: '2026-03-31T23:59:59Z',
    optimization_goal: 'impressions'
  });
  
  console.log(`✅ Programmatic campaign created with $${bidPrice.toFixed(2)} CPM bid`);
}
```

---

## Video Advertising Campaigns

### Example 5: Pre-Roll Video Campaign

Standard 30-second pre-roll video campaign.

```javascript
async function launchVideoPreRoll() {
  // 1. Find video products
  const products = await testAgent.getProducts({
    brief: '30-second pre-roll video for streaming services targeting tech enthusiasts',
    brand_manifest: {
      name: 'StreamTech',
      url: 'https://streamtech.com'
    },
    filters: {
      channels: ['video'],
      format_types: ['video']
    }
  });
  
  const videoProduct = products.products.find(p =>
    p.format_ids.some(f => f.id.includes('30s'))
  );
  
  // 2. Create campaign
  const campaign = await testAgent.createMediaBuy({
    buyer_ref: 'streamtech-video-q1-2026',
    brand_manifest: {
      name: 'StreamTech',
      url: 'https://streamtech.com',
      tagline: 'Stream smarter, not harder'
    },
    packages: [{
      buyer_ref: 'pkg-preroll-30s',
      product_id: videoProduct.product_id,
      pricing_option_id: videoProduct.pricing_options[0].pricing_option_id,
      budget: 40000,
      
      targeting_overlay: {
        demographics: {
          age_ranges: [{ min: 18, max: 44 }],
          genders: ['M', 'F']
        },
        behavioral: {
          interests: ['technology', 'streaming', 'entertainment'],
          purchase_intent: ['electronics', 'software']
        }
      },
      
      creatives: [{
        creative_id: 'streamtech_preroll_30s_v1',
        format_id: {
          agent_url: 'https://creative.adcontextprotocol.org',
          id: 'video_standard_30s'
        },
        assets: {
          video: {
            url: 'https://cdn.streamtech.com/ads/preroll_30s_v1.mp4',
            width: 1920,
            height: 1080,
            duration_ms: 30000,
            mime_type: 'video/mp4'
          }
        },
        click_through_url: 'https://streamtech.com/signup',
        tracking_pixels: [
          'https://analytics.streamtech.com/impression',
          'https://analytics.streamtech.com/completion'
        ]
      }],
      
      frequency_cap: {
        impressions: 2,
        time_unit: 'day',
        time_count: 1
      }
    }],
    start_time: {
      type: 'scheduled',
      datetime: '2026-02-01T00:00:00Z'
    },
    end_time: '2026-03-31T23:59:59Z',
    optimization_goal: 'conversions'
  });
  
  console.log(`✅ Video campaign created: ${campaign.media_buy_id}`);
  
  // 3. Monitor completion rates
  setTimeout(async () => {
    const delivery = await testAgent.getMediaBuyDelivery({
      media_buy_id: campaign.media_buy_id
    });
    
    console.log(`\n📊 Video Performance:`);
    console.log(`   Impressions: ${delivery.delivery.impressions.toLocaleString()}`);
    console.log(`   Completion Rate: ${(delivery.delivery.completion_rate * 100).toFixed(1)}%`);
    console.log(`   CPM: $${delivery.delivery.cpm.toFixed(2)}`);
  }, 60000);  // Check after 1 minute
}
```

### Example 6: Connected TV Campaign

CTV campaign targeting cord-cutters and streaming audiences.

```javascript
async function launchCTVCampaign() {
  const products = await testAgent.getProducts({
    brief: 'Connected TV advertising for premium streaming platforms targeting cord-cutters',
    brand_manifest: {
      name: 'Premium Streaming Service',
      url: 'https://premiumstream.com'
    },
    filters: {
      channels: ['ctv'],
      budget_range: { min: 50000, max: 200000 }
    }
  });
  
  const ctvProduct = products.products[0];
  
  const campaign = await testAgent.createMediaBuy({
    buyer_ref: 'ctv-campaign-q1-2026',
    brand_manifest: { url: 'https://premiumstream.com' },
    packages: [{
      buyer_ref: 'pkg-ctv-premium',
      product_id: ctvProduct.product_id,
      pricing_option_id: ctvProduct.pricing_options[0].pricing_option_id,
      budget: 100000,
      
      targeting_overlay: {
        geo: {
          included: [
            'US-NY', 'US-LA', 'US-CHI', 'US-SF', 'US-PHI',  // Top 5 DMAs
            'US-DAL', 'US-DC', 'US-ATL', 'US-BOS', 'US-SEA'  // Top 6-10 DMAs
          ]
        },
        demographics: {
          age_ranges: [{ min: 25, max: 54 }],
          income_brackets: ['75k+']
        },
        behavioral: {
          interests: ['streaming', 'premium_content', 'cord_cutting']
        }
      },
      
      creatives: [{
        creative_id: 'ctv_spot_30s',
        format_id: {
          agent_url: 'https://creative.adcontextprotocol.org',
          id: 'video_standard_30s'
        },
        assets: {
          video: {
            url: 'https://cdn.premiumstream.com/ctv_30s_4k.mp4',
            width: 3840,  // 4K
            height: 2160,
            duration_ms: 30000,
            mime_type: 'video/mp4'
          }
        }
      }],
      
      frequency_cap: {
        impressions: 3,
        time_unit: 'week',
        time_count: 1
      }
    }],
    start_time: { type: 'asap' },
    end_time: '2026-03-31T23:59:59Z',
    optimization_goal: 'impressions',
    pacing: 'even'
  });
  
  console.log(`✅ CTV campaign launched: ${campaign.media_buy_id}`);
  console.log(`   Budget: $${campaign.packages[0].budget.toLocaleString()}`);
  console.log(`   DMAs: 10 major markets`);
}
```

---

## Multi-Channel Campaigns

### Example 7: Integrated Display + Video Campaign

Coordinated campaign across multiple channels.

```javascript
async function launchMultiChannelCampaign() {
  // 1. Discover products across channels
  const products = await testAgent.getProducts({
    brief: 'Multi-channel campaign for tech product launch - display and video',
    brand_manifest: {
      name: 'TechCorp',
      url: 'https://techcorp.com'
    },
    filters: {
      channels: ['display', 'video'],
      budget_range: { min: 50000, max: 150000 }
    }
  });
  
  // 2. Separate products by channel
  const displayProducts = products.products.filter(p => p.channels.includes('display'));
  const videoProducts = products.products.filter(p => p.channels.includes('video'));
  
  // 3. Create integrated campaign with multiple packages
  const campaign = await testAgent.createMediaBuy({
    buyer_ref: 'techcorp-product-launch-2026',
    brand_manifest: {
      name: 'TechCorp',
      url: 'https://techcorp.com',
      tagline: 'Innovation that matters'
    },
    packages: [
      // Display package (40% of budget)
      {
        buyer_ref: 'pkg-display-awareness',
        product_id: displayProducts[0].product_id,
        pricing_option_id: displayProducts[0].pricing_options[0].pricing_option_id,
        budget: 40000,
        
        targeting_overlay: {
          demographics: {
            age_ranges: [{ min: 25, max: 54 }]
          },
          behavioral: {
            interests: ['technology', 'business', 'innovation']
          }
        },
        
        creatives: [
          {
            creative_id: 'display_300x250_launch',
            format_id: {
              agent_url: 'https://creative.adcontextprotocol.org',
              id: 'display_300x250'
            },
            assets: {
              image: {
                url: 'https://cdn.techcorp.com/launch_300x250.jpg',
                width: 300,
                height: 250
              }
            }
          },
          {
            creative_id: 'display_728x90_launch',
            format_id: {
              agent_url: 'https://creative.adcontextprotocol.org',
              id: 'display_728x90'
            },
            assets: {
              image: {
                url: 'https://cdn.techcorp.com/launch_728x90.jpg',
                width: 728,
                height: 90
              }
            }
          }
        ]
      },
      
      // Video package (60% of budget)
      {
        buyer_ref: 'pkg-video-consideration',
        product_id: videoProducts[0].product_id,
        pricing_option_id: videoProducts[0].pricing_options[0].pricing_option_id,
        budget: 60000,
        
        targeting_overlay: {
          demographics: {
            age_ranges: [{ min: 25, max: 54 }]
          },
          behavioral: {
            interests: ['technology', 'business', 'innovation'],
            purchase_intent: ['electronics', 'software']
          }
        },
        
        creatives: [{
          creative_id: 'video_30s_product_demo',
          format_id: {
            agent_url: 'https://creative.adcontextprotocol.org',
            id: 'video_standard_30s'
          },
          assets: {
            video: {
              url: 'https://cdn.techcorp.com/demo_30s.mp4',
              width: 1920,
              height: 1080,
              duration_ms: 30000
            }
          }
        }],
        
        frequency_cap: {
          impressions: 3,
          time_unit: 'week',
          time_count: 1
        }
      }
    ],
    start_time: { type: 'asap' },
    end_time: '2026-06-30T23:59:59Z',
    optimization_goal: 'conversions',
    pacing: 'even'
  });
  
  console.log(`✅ Multi-channel campaign created: ${campaign.media_buy_id}`);
  console.log(`   Display budget: $40,000`);
  console.log(`   Video budget: $60,000`);
  console.log(`   Total: $100,000`);
  
  // 4. Monitor performance by channel
  setTimeout(async () => {
    const delivery = await testAgent.getMediaBuyDelivery({
      media_buy_id: campaign.media_buy_id,
      dimensions: ['package']
    });
    
    console.log('\n📊 Performance by Channel:');
    delivery.by_package?.forEach(pkg => {
      const channel = pkg.buyer_ref.includes('display') ? 'Display' : 'Video';
      console.log(`   ${channel}:`);
      console.log(`     Impressions: ${pkg.impressions.toLocaleString()}`);
      console.log(`     Spend: $${pkg.spend.toLocaleString()}`);
      console.log(`     CPM: $${(pkg.spend / pkg.impressions * 1000).toFixed(2)}`);
    });
  }, 120000);  // Check after 2 minutes
}
```

---

## Campaign Optimization

### Example 8: Dynamic Budget Reallocation

Monitor and optimize budget allocation based on performance.

```javascript
async function optimizeCampaignBudget(mediaBuyId) {
  // 1. Get current performance
  const delivery = await testAgent.getMediaBuyDelivery({
    media_buy_id: mediaBuyId,
    dimensions: ['package']
  });
  
  // 2. Calculate efficiency scores
  const packagePerformance = delivery.by_package?.map(pkg => ({
    package_id: pkg.package_id,
    buyer_ref: pkg.buyer_ref,
    impressions: pkg.impressions,
    spend: pkg.spend,
    clicks: pkg.clicks || 0,
    efficiency: pkg.impressions / pkg.spend,  // Impressions per dollar
    ctr: pkg.clicks / pkg.impressions
  }));
  
  // 3. Rank by efficiency
  packagePerformance?.sort((a, b) => b.efficiency - a.efficiency);
  
  console.log('📊 Package Performance Rankings:');
  packagePerformance?.forEach((pkg, index) => {
    console.log(`${index + 1}. ${pkg.buyer_ref}`);
    console.log(`   Efficiency: ${pkg.efficiency.toFixed(0)} imps/$`);
    console.log(`   CTR: ${(pkg.ctr * 100).toFixed(2)}%`);
  });
  
  // 4. Identify optimization opportunity
  if (packagePerformance && packagePerformance.length >= 2) {
    const best = packagePerformance[0];
    const worst = packagePerformance[packagePerformance.length - 1];
    
    const efficiencyRatio = best.efficiency / worst.efficiency;
    
    if (efficiencyRatio > 2) {
      console.log(`\n💡 Optimization Opportunity:`);
      console.log(`   ${best.buyer_ref} is ${efficiencyRatio.toFixed(1)}x more efficient than ${worst.buyer_ref}`);
      console.log(`   Recommend: Shift $5,000 from ${worst.buyer_ref} to ${best.buyer_ref}`);
      
      // 5. Implement optimization (if approved)
      const shouldOptimize = true;  // Get user approval in real scenario
      
      if (shouldOptimize) {
        await testAgent.updateMediaBuy({
          media_buy_id: mediaBuyId,
          updates: {
            package_updates: [
              {
                package_id: best.package_id,
                budget_change: 5000  // Add $5k
              },
              {
                package_id: worst.package_id,
                budget_change: -5000  // Remove $5k
              }
            ]
          }
        });
        
        console.log('✅ Budget reallocation complete');
      }
    }
  }
}
```

### Example 9: A/B Testing Creatives

Test multiple creative variations and identify winners.

```javascript
async function runCreativeABTest(mediaBuyId) {
  // 1. Upload test variations
  await testAgent.syncCreatives({
    creatives: [
      {
        creative_id: 'variant_a_headline_1',
        name: 'Variant A - Headline 1',
        format_id: {
          agent_url: 'https://creative.adcontextprotocol.org',
          id: 'display_300x250'
        },
        assets: {
          image: {
            url: 'https://cdn.brand.com/test_a.jpg',
            width: 300,
            height: 250
          }
        }
      },
      {
        creative_id: 'variant_b_headline_2',
        name: 'Variant B - Headline 2',
        format_id: {
          agent_url: 'https://creative.adcontextprotocol.org',
          id: 'display_300x250'
        },
        assets: {
          image: {
            url: 'https://cdn.brand.com/test_b.jpg',
            width: 300,
            height: 250
          }
        }
      },
      {
        creative_id: 'variant_c_headline_3',
        name: 'Variant C - Headline 3',
        format_id: {
          agent_url: 'https://creative.adcontextprotocol.org',
          id: 'display_300x250'
        },
        assets: {
          image: {
            url: 'https://cdn.brand.com/test_c.jpg',
            width: 300,
            height: 250
          }
        }
      }
    ],
    assignments: {
      'variant_a_headline_1': ['pkg-001'],
      'variant_b_headline_2': ['pkg-001'],
      'variant_c_headline_3': ['pkg-001']
    }
  });
  
  console.log('✅ A/B test creatives uploaded');
  
  // 2. Wait for sufficient data (check after 24 hours in production)
  console.log('⏳ Collecting performance data...');
  
  // 3. Analyze results
  const delivery = await testAgent.getMediaBuyDelivery({
    media_buy_id: mediaBuyId,
    dimensions: ['creative']
  });
  
  if (!delivery.by_creative || delivery.by_creative.length < 2) {
    console.log('⚠️ Insufficient data for analysis');
    return;
  }
  
  // 4. Calculate statistical significance and find winner
  const results = delivery.by_creative.map(creative => ({
    creative_id: creative.creative_id,
    impressions: creative.impressions,
    clicks: creative.clicks || 0,
    ctr: (creative.clicks || 0) / creative.impressions,
    confidence: creative.impressions > 1000 ? 'high' : 'low'
  }));
  
  results.sort((a, b) => b.ctr - a.ctr);
  
  console.log('\n📊 A/B Test Results:');
  results.forEach((result, index) => {
    const isWinner = index === 0;
    console.log(`${isWinner ? '🏆' : '  '} ${result.creative_id}`);
    console.log(`     CTR: ${(result.ctr * 100).toFixed(3)}%`);
    console.log(`     Impressions: ${result.impressions.toLocaleString()}`);
    console.log(`     Confidence: ${result.confidence}`);
  });
  
  // 5. Implement winner
  const winner = results[0];
  
  if (winner.confidence === 'high') {
    console.log(`\n✅ Winner identified: ${winner.creative_id}`);
    console.log(`   Recommend: Use this creative for remaining campaign`);
    
    // Update campaign to use only winner
    await testAgent.syncCreatives({
      creatives: [],  // No new creatives
      assignments: {
        [winner.creative_id]: ['pkg-001']  // Only winner
      }
    });
    
    console.log('✅ Campaign updated to use winning creative');
  } else {
    console.log('\n⚠️ Need more data before selecting winner');
  }
}
```

---

## Creative Management

### Example 10: Bulk Creative Upload

Upload multiple creative assets efficiently.

```javascript
async function uploadCreativeLibrary() {
  // Prepare creative library
  const creatives = [
    // Display formats
    { id: 'display_mrec', format: 'display_300x250', url: 'banner_300x250.jpg', w: 300, h: 250 },
    { id: 'display_leader', format: 'display_728x90', url: 'banner_728x90.jpg', w: 728, h: 90 },
    { id: 'display_sky', format: 'display_160x600', url: 'banner_160x600.jpg', w: 160, h: 600 },
    
    // Video formats
    { id: 'video_15s', format: 'video_standard_15s', url: 'video_15s.mp4', w: 1920, h: 1080, duration: 15000 },
    { id: 'video_30s', format: 'video_standard_30s', url: 'video_30s.mp4', w: 1920, h: 1080, duration: 30000 }
  ];
  
  // Build creative objects
  const creativeObjects = creatives.map(c => {
    const isVideo = c.format.includes('video');
    
    return {
      creative_id: c.id,
      name: `Campaign Creative - ${c.format}`,
      format_id: {
        agent_url: 'https://creative.adcontextprotocol.org',
        id: c.format
      },
      assets: isVideo ? {
        video: {
          url: `https://cdn.brand.com/${c.url}`,
          width: c.w,
          height: c.h,
          duration_ms: c.duration,
          mime_type: 'video/mp4'
        }
      } : {
        image: {
          url: `https://cdn.brand.com/${c.url}`,
          width: c.w,
          height: c.h,
          mime_type: 'image/jpeg'
        }
      },
      click_through_url: 'https://brand.com/campaign'
    };
  });
  
  // Upload all creatives
  const result = await testAgent.syncCreatives({
    creatives: creativeObjects
  });
  
  console.log(`✅ Uploaded ${result.synced_creatives.length} creatives`);
  
  result.synced_creatives.forEach(creative => {
    console.log(`   ${creative.creative_id}: ${creative.status}`);
  });
}
```

---

## Advanced Targeting

### Example 11: Geo-Fenced Campaign

Target specific geographic regions with precision.

```javascript
async function launchGeoTargetedCampaign() {
  const products = await testAgent.getProducts({
    brief: 'Retail store promotion targeting customers near store locations',
    brand_manifest: { url: 'https://retailchain.com' },
    filters: {
      channels: ['display', 'mobile']
    }
  });
  
  const campaign = await testAgent.createMediaBuy({
    buyer_ref: 'store-promo-geo-q1',
    brand_manifest: { url: 'https://retailchain.com' },
    packages: [{
      buyer_ref: 'pkg-geo-promo',
      product_id: products.products[0].product_id,
      pricing_option_id: products.products[0].pricing_options[0].pricing_option_id,
      budget: 20000,
      
      targeting_overlay: {
        geo: {
          included: [
            'US-10001',  // NYC ZIP
            'US-10002',
            'US-90001',  // LA ZIP
            'US-90002',
            'US-60601',  // Chicago ZIP
            'US-60602'
          ]
        },
        demographics: {
          age_ranges: [{ min: 21, max: 65 }]
        }
      }
    }],
    start_time: { type: 'asap' },
    end_time: '2026-03-31T23:59:59Z'
  });
  
  console.log(`✅ Geo-targeted campaign launched`);
  console.log(`   Targeting 6 ZIP codes across 3 cities`);
}
```

---

## Performance Monitoring

### Example 12: Real-Time Campaign Dashboard

Monitor campaign performance with comprehensive metrics.

```javascript
async function monitorCampaign(mediaBuyId) {
  const delivery = await testAgent.getMediaBuyDelivery({
    media_buy_id: mediaBuyId,
    granularity: 'daily',
    dimensions: ['package', 'creative']
  });
  
  console.log('=' .repeat(60));
  console.log('📊 CAMPAIGN PERFORMANCE DASHBOARD');
  console.log('='.repeat(60));
  
  // Overall metrics
  console.log('\n📈 Overall Performance:');
  console.log(`   Status: ${delivery.status}`);
  console.log(`   Impressions: ${delivery.delivery.impressions.toLocaleString()}`);
  console.log(`   Clicks: ${(delivery.delivery.clicks || 0).toLocaleString()}`);
  console.log(`   CTR: ${((delivery.delivery.ctr || 0) * 100).toFixed(3)}%`);
  console.log(`   Spend: $${delivery.delivery.spend.toLocaleString()}`);
  console.log(`   CPM: $${delivery.delivery.cpm?.toFixed(2)}`);
  
  // Budget pacing
  console.log('\n💰 Budget Pacing:');
  const pacingBar = '█'.repeat(Math.floor(delivery.pacing.spend_pacing * 20));
  console.log(`   ${pacingBar} ${(delivery.pacing.spend_pacing * 100).toFixed(1)}%`);
  console.log(`   Days ${delivery.pacing.days_elapsed} of ${delivery.pacing.days_total}`);
  console.log(`   Campaign ${(delivery.pacing.percent_complete * 100).toFixed(1)}% complete`);
  
  const pacingHealth = Math.abs(delivery.pacing.spend_pacing - delivery.pacing.percent_complete);
  if (pacingHealth < 0.1) {
    console.log(`   ✅ On track`);
  } else if (delivery.pacing.spend_pacing < delivery.pacing.percent_complete) {
    console.log(`   ⚠️ Underpacing by ${(pacingHealth * 100).toFixed(1)}%`);
  } else {
    console.log(`   ⚠️ Overpacing by ${(pacingHealth * 100).toFixed(1)}%`);
  }
  
  // Package performance
  if (delivery.by_package && delivery.by_package.length > 0) {
    console.log('\n📦 Performance by Package:');
    delivery.by_package.forEach(pkg => {
      console.log(`   ${pkg.buyer_ref}:`);
      console.log(`     Impressions: ${pkg.impressions.toLocaleString()}`);
      console.log(`     Spend: $${pkg.spend.toLocaleString()}`);
      console.log(`     CPM: $${((pkg.spend / pkg.impressions) * 1000).toFixed(2)}`);
    });
  }
  
  // Creative performance
  if (delivery.by_creative && delivery.by_creative.length > 0) {
    console.log('\n🎨 Performance by Creative:');
    delivery.by_creative
      .sort((a, b) => (b.ctr || 0) - (a.ctr || 0))
      .forEach(creative => {
        console.log(`   ${creative.creative_id}:`);
        console.log(`     CTR: ${((creative.ctr || 0) * 100).toFixed(3)}%`);
        console.log(`     Impressions: ${creative.impressions.toLocaleString()}`);
      });
  }
  
  // Daily trend
  if (delivery.timeseries && delivery.timeseries.length > 0) {
    console.log('\n📅 Last 7 Days:');
    delivery.timeseries.slice(-7).forEach(day => {
      const date = new Date(day.timestamp).toLocaleDateString();
      console.log(`   ${date}: ${day.impressions.toLocaleString()} imps, $${day.spend.toLocaleString()}`);
    });
  }
  
  console.log('\n' + '='.repeat(60));
}

// Run dashboard every 5 minutes
setInterval(() => {
  monitorCampaign('your-media-buy-id');
}, 300000);
```

This comprehensive example guide provides OpenClaw agents with practical, working code for common advertising scenarios using AdCP. Each example is complete and can be adapted to specific use cases.
