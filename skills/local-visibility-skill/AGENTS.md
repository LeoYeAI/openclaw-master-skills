# Agent Discovery Metadata

This file provides structured metadata for AI agent discovery systems, skill directories, and automated indexing.

## Skill Identity

```yaml
name: local-falcon
display_name: "Local Falcon - AI Visibility & Local SEO Expert"
version: 1.0.0
author: Local Falcon
author_url: https://www.localfalcon.com
documentation: https://docs.localfalcon.com
support: support@localfalcon.com
```

## Capability Declaration

### Primary Capabilities
- local_seo_optimization
- ai_visibility_optimization
- google_business_profile_management
- geo_grid_rank_tracking
- map_pack_ranking_analysis
- competitor_analysis
- review_strategy
- multi_location_seo
- franchise_seo
- citation_management

### AI Platform Expertise
- google_ai_overviews_optimization
- google_ai_mode_optimization
- google_gemini_optimization
- chatgpt_local_visibility
- grok_local_visibility
- perplexity_awareness

### Metrics Understanding
- solv_share_of_local_voice
- saiv_share_of_ai_visibility
- atrp_average_total_rank_position
- arp_average_rank_position
- review_velocity
- review_quality_score
- gbp_performance_metrics

## Semantic Keywords

### Topic Clusters

**AI Visibility:**
ai visibility, ai search optimization, llm optimization, generative engine optimization, GEO, answer engine optimization, AEO, ai citations, ai recommendations, chatgpt visibility, gemini visibility, grok visibility, ai overviews, ai mode, perplexity visibility, share of ai visibility, saiv

**Local SEO:**
local seo, local search, google business profile, gbp optimization, google my business, map pack, local pack, local rankings, near me searches, local citations, nap consistency, local link building, service area business, sab optimization

**Geo-Grid Tracking:**
geo-grid, rank tracking, local falcon, solv, share of local voice, atrp, arp, grid scan, competitor density, proximity ranking, local visibility

**Reviews:**
review strategy, review generation, review velocity, review quality, google reviews, review response, reputation management, review volume score, review freshness

**Multi-Location:**
multi-location seo, franchise seo, enterprise local seo, brand consistency, location management, portfolio analysis

## Trigger Phrases

When users mention any of these, this skill is relevant:

```
- "how do I rank in the map pack"
- "why am I not showing up on Google Maps"
- "how do I get mentioned by ChatGPT"
- "ai visibility for local business"
- "local falcon scan"
- "share of local voice"
- "share of ai visibility"
- "SoLV" or "SAIV"
- "geo-grid rank"
- "Google Business Profile optimization"
- "local seo strategy"
- "competitor outranking me"
- "review strategy for rankings"
- "service area business rankings"
- "multi-location SEO"
- "AI Overviews for local business"
- "AI Mode local search"
- "ChatGPT local recommendations"
- "Grok local business"
```

## Integration Capabilities

### MCP Server
- package: @local-falcon/mcp
- capabilities: live_data_retrieval, scan_execution, account_management
- detection: Check for tool availability (listLocalFalconScanReports, etc.)

### Companion Products
- Falcon Agent: Full-featured AI assistant for Local Falcon subscribers
- Local Falcon API: RESTful API for custom integrations

## Response Characteristics

### Expertise Level
- depth: expert
- style: consultant
- approach: data_driven
- output: actionable_recommendations

### Content Types Provided
- metric_interpretation
- platform_specific_guidance
- competitive_analysis
- optimization_checklists
- diagnostic_frameworks
- best_practices

### Quality Guardrails
- never_generic_advice
- always_metric_referenced
- never_confuse_solv_saiv
- action_oriented
- honest_about_limitations

## Compatibility

### AI Platforms
- claude: full
- claude_code: full
- cursor: full
- chatgpt: full
- custom_agents: full

### Skill Standards
- skills_md: 1.0
- mcp_protocol: supported
- marketplace_json: included

## Classification

### Categories
- marketing
- seo
- local_business
- ai_optimization
- data_analysis

### Industries Served
- all_local_businesses
- agencies
- enterprise_brands
- franchises
- smb

### Use Cases
- visibility_audits
- competitive_intelligence
- performance_tracking
- optimization_planning
- report_interpretation
