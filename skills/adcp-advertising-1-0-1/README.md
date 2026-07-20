# Ad Context Protocol (AdCP) Advertising Skill for OpenClaw

**Launch and optimize advertising campaigns using AI.** Automate media buying, ad creation, campaign management, and performance tracking across display, video, CTV, audio, and more.

**Official AdCP Repository**: [github.com/adcontextprotocol/adcp](https://github.com/adcontextprotocol/adcp)  
**Official AdCP Documentation**: https://docs.adcontextprotocol.org  
**Complete Documentation Index**: https://docs.adcontextprotocol.org/llms.txt

## Overview

Transform how you run advertising campaigns. This skill provides OpenClaw agents with AI-powered advertising automation:

- 🔍 **Discover ad inventory** - Find display ads, video placements, CTV spots using natural language
- 🎯 **Launch campaigns instantly** - Create multi-channel campaigns across display, video, CTV, audio, native, DOOH
- 🎨 **Manage ad creatives** - Upload banners, videos, HTML5 ads and track performance by creative
- 📊 **Monitor ROI in real-time** - Get impressions, clicks, conversions, CPM, CTR, and spend data instantly
- 🎛️ **Auto-optimize performance** - Reallocate budgets, pause underperformers, scale winners automatically
- 🌐 **Target precisely** - Demographics, behaviors, interests, locations, devices, times, and contexts

### Perfect For

**Marketing teams** running Facebook ads, Google ads, programmatic campaigns  
**Media buyers** managing multi-channel ad spend and inventory  
**Agencies** automating client campaign management and reporting  
**E-commerce** launching product ads and retargeting campaigns  
**Startups** running lean marketing with AI-powered ad automation

## Quick Start

### Installation

For ClawHub users:
```bash
# Install via ClawHub
openclaw skills install adcp-advertising
```

For local development:
```bash
# Clone or download this skill to your workspace
cd ~/.openclaw/workspace/skills/
git clone <this-repo> adcp-advertising
```

### Launch Your First Ad Campaign in 5 Minutes

Go from zero to live campaign using just natural language. No forms, no dashboards, no ad platform expertise needed.

**Step 1: Discover what's available** (No login required)
```
"Show me advertising options for my business"
```
Browse inventory across publishers without authentication.

**Step 2: Find your perfect ad placement**
```
"Find display ads for a tech startup, $5000 budget"
```
AI searches inventory and shows matching products with pricing.

**Step 3: Launch your campaign**
```
"Create campaign with Product ID prod_abc123, $5000 budget, 
targeting tech professionals in California"
```
Campaign goes live instantly using the test environment.

**Step 4: Upload your ads**
```
"Upload this banner as a creative"
```
Drop your image, video, or HTML5 ad. Done.

**Step 5: Track performance**
```
"Show campaign performance"
```
Get impressions, clicks, CTR, spend, and pacing in real-time.

**That's it!** Your first campaign is live in the test environment. When ready, switch to production for real ad delivery.

### Moving to Production

Ready for real ad delivery? Switch seamlessly:
1. Find sales agents: `get_adcp_capabilities` on production endpoints
2. Get credentials from their sales team
3. Update agent URL to production
4. Launch campaigns with real budgets

## Why Choose This Skill?

### Say Goodbye to Ad Platform Complexity
- **No more dashboards** - Manage everything through conversation
- **No forms to fill** - Just describe what you want in plain English  
- **No platform learning curve** - AI handles the technical details
- **No manual optimization** - Automated performance management

### Built for Results
- **Launch faster** - 5 minutes from idea to live campaign vs. hours in traditional platforms
- **Spend smarter** - AI-powered optimization reallocates budgets to top performers
- **Scale easier** - Manage unlimited campaigns through simple commands
- **Track better** - Real-time metrics without dashboard switching

### Trusted Technology
- **Open standard** - Built on Ad Context Protocol used by real advertising platforms
- **Production-ready** - Complete error handling, validation, and best practices
- **Well-documented** - 5,600+ lines of guides, examples, and references
- **Test environment included** - Try everything risk-free before going live

## Features

### 🔍 Product Discovery
- Natural language search for advertising inventory
- Filter by channel, budget, format, and date range
- Detailed product information including pricing and targeting options

### 🎯 Campaign Management
- Create campaigns across multiple channels
- Update budgets, targeting, and creative assignments
- Pause/resume campaigns
- Schedule campaigns for future launch

### 🎨 Creative Management
- Support for all standard IAB formats (display, video, native)
- Bulk creative upload
- Creative library management
- Performance tracking by creative

### 📊 Performance Monitoring
- Real-time campaign metrics
- Detailed breakdowns by package, creative, and geography
- Budget pacing alerts
- Daily/hourly granularity

### 🎛️ Optimization
- Automatic budget reallocation based on performance
- A/B testing for creatives
- Targeting optimization recommendations
- Pacing adjustments

## Supported Channels

- **Display**: Banner ads, rich media, HTML5
- **Video**: Pre-roll, mid-roll, outstream
- **CTV**: Connected TV advertising
- **Audio**: Streaming audio, podcast ads
- **Native**: In-feed, content-style ads
- **DOOH**: Digital out-of-home advertising

## Documentation

Comprehensive documentation is included with this skill:

- **[SKILL.md](SKILL.md)** - Main skill guide with quick start and core concepts
- **[REFERENCE.md](REFERENCE.md)** - Complete API reference for all 8 AdCP tasks
- **[EXAMPLES.md](EXAMPLES.md)** - Real-world campaign examples and use cases
- **[PROTOCOLS.md](PROTOCOLS.md)** - MCP vs A2A protocol details
- **[TARGETING.md](TARGETING.md)** - Advanced targeting strategies
- **[CREATIVE.md](CREATIVE.md)** - Creative asset management guide

## Example Workflows

### Launch a Simple Campaign

```
Agent: "I need to run a display campaign for my startup"

System discovers products, shows options

Agent: "Create a campaign with Product 1, $10,000 budget, 
       targeting tech professionals in California"

System creates campaign

Agent: "Upload my 300x250 banner to this campaign"

System uploads creative and assigns to campaign
```

### Monitor and Optimize

```
Agent: "Show me how my video campaign is performing"

System shows metrics: impressions, CTR, spend, pacing

Agent: "Which creative is performing best?"

System analyzes and shows creative performance rankings

Agent: "Shift $5,000 from package B to package A 
       since it's performing better"

System updates budget allocation
```

## Authentication

AdCP uses a tiered authentication model - some operations are public, others require credentials.

### Public Operations (No Auth Required)

These work without any credentials:

- **`get_adcp_capabilities`** - Discover agent capabilities and portfolio
- **`list_creative_formats`** - Browse available ad formats  
- **`get_products`** (limited) - Basic inventory discovery (partial catalog, no pricing)

**Why?** Publishers want potential buyers to explore capabilities before establishing relationships.

### Authenticated Operations (Credentials Required)

Everything else needs authentication:

- **`get_products`** (full) - Complete catalog with pricing and custom products
- **`create_media_buy`** - Create advertising campaigns
- **`update_media_buy`** - Modify existing campaigns
- **`sync_creatives`** - Upload creative assets
- **`list_creatives`** - View your creative library
- **`get_media_buy_delivery`** - Monitor campaign performance
- **`provide_performance_feedback`** - Submit optimization signals

### Authentication Method

AdCP uses **Bearer token authentication**:

```
Authorization: Bearer <your-token>
```

Tokens can be:
- **Opaque tokens**: Server-validated strings
- **JWT tokens**: Self-contained with embedded claims

### Test Agent (Public Credentials)

A public test agent is available with shared credentials for development:

- **Agent URL**: `https://test-agent.adcontextprotocol.org/mcp`
- **Auth Token**: `1v8tAhASaUYYp4odoQ1PnMpdqNaMiTrCRqYo9OJp6IQ`
- **Interactive Testing**: [testing.adcontextprotocol.org](https://testing.adcontextprotocol.org)

This token is **intentionally public** - anyone can use it for testing. It's included in package.json and official AdCP documentation.

### Production Credentials

For real campaigns, you need credentials from each sales agent:

1. **Discover agents**: Use `get_adcp_capabilities` on production endpoints
2. **Contact sales**: Reach out to the agent's sales/partnerships team
3. **Complete onboarding**: Provide business info, sign agreements, configure billing
4. **Receive credentials**: Get your API Bearer token or OAuth credentials
5. **Store securely**: Use environment variables or secret managers (never commit to git)

**Important**: Each sales agent manages credentials independently. You need separate auth for each one you work with.

### Example Configuration

**Test environment:**
```json
{
  "agent_url": "https://test-agent.adcontextprotocol.org/mcp",
  "auth": {
    "type": "bearer",
    "token": "1v8tAhASaUYYp4odoQ1PnMpdqNaMiTrCRqYo9OJp6IQ"
  }
}
```

**Production environment:**
```json
{
  "agent_url": "https://sales-agent.example.com/mcp",
  "auth": {
    "type": "bearer",
    "token": "your-production-token-here"
  }
}
```

For more details, see the [official authentication guide](https://docs.adcontextprotocol.org/docs/building/integration/authentication).

## Key Concepts

### Asynchronous Operations

AdCP is **not a real-time protocol**. Operations may take:
- **~1 second**: Simple lookups (formats, creative lists)
- **~60 seconds**: AI operations (product discovery)
- **Minutes to days**: Operations requiring approval (campaign creation)

Always check the `status` field and handle `pending` states.

### Targeting is Additive

Your targeting overlay + Product targeting = Final targeting

Products already have targeting. Your overlay adds constraints.

### Brand Context Matters

Provide detailed brand manifests for better product matches:

```javascript
{
  brand_manifest: {
    name: 'Acme Corp',
    url: 'https://acme.com',
    tagline: 'Innovation that matters',
    colors: { primary: '#FF4500' }
  }
}
```

## Who Should Use This Skill?

### Marketing Teams
- Launch campaigns faster without learning complex platforms
- Monitor multiple campaigns through conversational queries
- Get instant performance insights and optimization recommendations

### Media Buyers
- Discover inventory across multiple publishers at once
- Compare products and pricing using natural language
- Automate routine optimization tasks

### Agencies
- Manage client campaigns through AI agents
- Scale operations without proportional staff increases
- Standardize workflows across different platforms

### Developers
- Build advertising automation tools
- Integrate ad buying into larger workflows
- Access advertising APIs through natural language

## Common Use Cases

### Launch New Product Campaign
```
Agent: "I need to launch a campaign for our new SaaS product targeting 
        CTOs and tech directors in major US cities, $50,000 budget"

System: Discovers suitable products, creates multi-package campaign, 
        sets up targeting, and uploads provided creatives
```

### Optimize Existing Campaign
```
Agent: "Analyze my video campaign performance and recommend optimizations"

System: Reviews metrics, identifies top performers, suggests budget 
        reallocation, pauses underperforming elements
```

### Multi-Channel Strategy
```
Agent: "Create an omnichannel campaign: display in California, 
        video in major cities, audio during commute hours"

System: Creates coordinated campaign across channels with unified 
        targeting and creative strategy
```

## Requirements

- **OpenClaw**: Compatible with OpenClaw 2026.1.0+
- **Node.js**: 18+ (for JavaScript examples)
- **Python**: 3.9+ (for Python examples)

## Support & Resources

### Official AdCP Resources
- **Official Repository**: https://github.com/adcontextprotocol/adcp
- **Main Documentation**: https://docs.adcontextprotocol.org
- **Complete Index (for AI agents)**: https://docs.adcontextprotocol.org/llms.txt
- **Media Buy Protocol**: https://docs.adcontextprotocol.org/docs/media-buy/
- **Task Reference**: https://docs.adcontextprotocol.org/docs/media-buy/task-reference/
- **Quickstart Guide**: https://docs.adcontextprotocol.org/docs/quickstart
- **Interactive Testing**: https://testing.adcontextprotocol.org

### This Skill Repository
- **Repository**: https://github.com/edyyy62/openclaw-adcp
- **Issues**: https://github.com/edyyy62/openclaw-adcp/issues

### OpenClaw Resources
- **OpenClaw Docs**: https://docs.openclaw.ai
- **ClawHub**: https://www.clawhub.ai/

## License

This skill is provided under the MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please submit issues or pull requests on GitHub.

## Version

**Version**: 1.0.0  
**Last Updated**: January 2026  
**AdCP Version**: 3.x compatible

## Author

Created for the OpenClaw community to enable AI-powered advertising automation.

## Acknowledgments

- Ad Context Protocol team for the comprehensive advertising API
- OpenClaw community for the excellent AI assistant framework
- ClawHub for skill distribution infrastructure
