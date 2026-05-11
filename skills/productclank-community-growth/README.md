# ProductClank Campaigns - Agent Skill

An [Agent Skill](https://agentskills.io) and [CLI tool](https://github.com/covariance-network/communiply-cli) for community-powered engagement on ProductClank.

## What is This?

This is an Agent Skill and CLI that enable community-driven brand advocacy on ProductClank. Two capabilities:

1. **Boost** — Rally your community to engage with a specific tweet (replies, likes, reposts). One API call, instant results.
2. **Discover** — AI agents find relevant conversations on Twitter/X, generate contextual replies, and community members post them.

**ProductClank Communiply** solves the authenticity problem in social media marketing: when your brand promotes itself, people dismiss it as advertising. Communiply enables real people (employees, users, community members) to naturally recommend your brand in relevant conversations—creating authentic word-of-mouth at scale.

## Quick Start

### CLI (Fastest)

```bash
npm install -g @productclank/communiply-cli
communiply auth register MyAgent
communiply boost https://x.com/myproduct/status/123 --action replies \
  --guidelines "Congratulate the team, ask about features"
```

### For AI Agents

This skill is loaded automatically when an agent needs to create Twitter/X marketing campaigns. The agent will:

1. Gather campaign requirements from the user
2. Authenticate with ProductClank API
3. **Boost:** `POST /agents/campaigns/boost` with tweet URL (200-300 credits)
4. **Or Discover:** Create campaign (10 credits) → Generate posts (12 credits/post)
5. Return the campaign dashboard URL for tracking

### For Developers

```bash
export PRODUCTCLANK_API_KEY=pck_live_YOUR_KEY
node scripts/create-campaign.mjs    # Discover flow
node scripts/boost-tweet.mjs        # Boost flow
```

See [SKILL.md](SKILL.md) for complete documentation.

## Directory Structure

```
productclank-campaigns/
├── SKILL.md                    # Main skill documentation (loaded by agents)
├── README.md                   # This file
├── references/
│   ├── API_REFERENCE.md        # Complete API specification
│   └── EXAMPLES.md             # Code examples for common use cases
└── scripts/
    └── create-campaign.mjs     # Helper script for quick campaign creation
```

## Files

### [SKILL.md](SKILL.md)
The main skill file loaded by AI agents. Contains:
- What Communiply is and how it works
- When to use this skill
- Step-by-step instructions for creating campaigns (2-step flow)
- Credit-based billing model
- Campaign delegates management
- Error handling and troubleshooting

### [references/API_REFERENCE.md](references/API_REFERENCE.md)
Complete API specification including:
- Authentication requirements
- All endpoints: campaign creation, post generation, delegates
- Request/response formats
- Credit costs and billing
- Rate limits and error codes

### [references/EXAMPLES.md](references/EXAMPLES.md)
Practical code examples:
- Basic campaign creation with credits
- Advanced campaigns with custom guidelines
- Competitor intercept campaigns
- Product launch campaigns
- Adding delegators
- Error handling and retry logic
- TypeScript types

### [scripts/create-campaign.mjs](scripts/create-campaign.mjs)
Ready-to-use script for creating campaigns with credit-based billing.

## Getting Started

### 1. Register Your Agent

Self-register via the API — no approval needed:

```bash
curl -X POST https://app.productclank.com/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name": "MyAgent"}'
```

Returns your API key instantly (shown once — store securely).

All agents start as **autonomous** (self-funded). To use your existing ProductClank credits instead, link the agent to your account:

```bash
# After registration, generate a linking URL
curl -X POST https://app.productclank.com/api/v1/agents/create-link \
  -H "Authorization: Bearer pck_live_YOUR_KEY"
# → Returns link_url — click it, log in via Privy, and your agent is linked
```

### 2. Get Credits

- New accounts receive **300 free credits** (~$30 value)
- **Autonomous agents:** Top up via USDC on Base (x402) or direct crypto payment
- **Owner-linked agents:** Use the owner's existing balance — top up via the [webapp](https://app.productclank.com) or crypto

### 3. Create Your First Campaign

Using the helper script:

```bash
# Edit the campaignData object in scripts/create-campaign.mjs
# Then run:
node scripts/create-campaign.mjs
```

Or programmatically (2-step flow):

```javascript
// Step 1: Create campaign (10 credits)
const campaignResponse = await fetch(
  "https://app.productclank.com/api/v1/agents/campaigns",
  {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      product_id: "YOUR_PRODUCT_UUID",
      title: "Launch Week Campaign",
      keywords: ["AI tools", "productivity apps"],
      search_context: "People discussing AI productivity tools",
    }),
  }
);

const campaign = await campaignResponse.json();
console.log("Campaign:", campaign.campaign);

// Step 2: Generate posts (12 credits/post)
const postsResponse = await fetch(
  `https://app.productclank.com/api/v1/agents/campaigns/${campaign.campaign.id}/generate-posts`,
  {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  }
);

const posts = await postsResponse.json();
console.log("Posts generated:", posts.posts_created);
```

## Credit Costs

| Operation | Credits |
|-----------|---------|
| Tweet boost (community replies) | 200 |
| Tweet boost (likes/reposts) | 300 |
| Campaign creation (Discover) | 10 |
| Post generation | 12 per post |
| Reply regeneration | 5 |

New accounts receive **300 free credits**. Additional credits available via the [webapp](https://app.productclank.com/credits).

## Rate Limits

- **Default**: 10 campaigns per day per agent
- **Custom limits**: Contact ProductClank for higher limits

## API Endpoints

### Campaign Management

| Method | Endpoint | Description | Credits |
|--------|----------|-------------|---------|
| POST | `/api/v1/agents/campaigns/boost` | Rally community around a tweet (replies, likes, reposts) | 200-300 |
| POST | `/api/v1/agents/campaigns` | Create a Discover campaign | 10 |
| POST | `/api/v1/agents/campaigns/{id}/generate-posts` | Generate posts for a campaign | 12/post |
| POST | `/api/v1/agents/campaigns/{id}/delegates` | Add a user as campaign delegator | 0 |

### Agent Registration & Linking

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agents/register` | Self-register an agent (no auth required) |
| POST | `/api/v1/agents/create-link` | Generate a linking URL for owner-linking |

### Trusted Agent / Multi-Tenant (Coming Soon)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agents/telegram/create-link` | Generate a linking token for a Telegram user |
| GET | `/api/v1/agents/telegram/lookup` | Look up a user by telegram_id |
| POST | `/api/v1/agents/authorize` | Grant agent authorization to bill a user |
| DELETE | `/api/v1/agents/authorize` | Revoke agent authorization |

**Note:** These endpoints are for multi-tenant trusted agents that bill different users per request. Most agents should use **Autonomous** (self-funded) or **Owner-Linked** (user-funded) registration instead — no linking needed.

## Use Cases

### For Builders & Founders

| Use Case | What You Do | What Happens |
|----------|-------------|--------------|
| **Launch Day Blitz** | Create a campaign targeting launch-related conversations | 50+ community members amplify your Product Hunt/Show HN launch with authentic posts |
| **Growth Campaign with Rewards** | Fund a campaign with credits | Community earns crypto for driving real sign-ups and engagement—60-80% lower CAC than ads |
| **Competitor Intercept** | Target "[Competitor] alternative" keywords | Community naturally recommends your product in competitor threads |
| **Content Amplification** | Boost your tweet with community engagement | Community rallies behind your post with replies (support, questions, congrats), likes, and reposts |
| **Conference Hype** | Target event-related conversations | Community mentions your presence in event threads, driving booth/talk traffic |
| **Hiring Push** | Target tech hiring conversations | Community shares your open roles in relevant "looking for work" threads |

### For AI Agents & Developers

| Use Case | Architecture | Credits |
|----------|-------------|---------|
| **Autonomous Growth Agent** | Cron → trend detection → auto-create campaigns → community executes | Pay-per-campaign |
| **Multi-Product Portfolio** | One agent manages campaigns across multiple `product_id`s | Shared credit balance |
| **Scheduled Campaigns** | Weekly cron creates fresh campaigns with updated keywords | ~250 credits/week |
| **Event-Reactive Campaigns** | Agent detects trending topics → auto-creates relevant campaigns | On-demand |
| **Growth-as-a-Service** | Build an agent that offers campaign management to multiple clients | Per-client billing (coming soon) |

### For Creators & Community

| Use Case | How It Works |
|----------|-------------|
| **Earn While You Tweet** | Browse campaigns, claim reply opportunities, post from your account, earn crypto rewards |
| **Build Your Reputation** | Grow your Believer Score through verified participations |
| **Get Credits** | Earn credits by participating in campaigns, use them to run your own |

## How Communiply Works

1. **Create Campaign** — Define keywords, target audience, and reply style (10 credits)
2. **Generate Posts** — AI discovers relevant conversations and creates contextual replies (12 credits/post)
3. **Community Amplifies** — Real people post from personal accounts, creating authentic third-party recommendations
4. **Tracks Results** — Real-time analytics on engagement, reach, and ROI

## Why It Works

| When You Promote Yourself ❌ | When Others Recommend You ✅ |
|------------------------------|------------------------------|
| Responses scream "advertisement" | Real users = authentic credibility |
| People dismiss automatically | 10x more trustworthy |
| Zero credibility in competitive conversations | Natural presence everywhere |
| Limited reach—only your followers | Unlimited reach—wherever conversations happen |

## Support & Resources

- **API Documentation**: [app.productclank.com/api/v1/docs](https://app.productclank.com/api/v1/docs)
- **Campaign Dashboard**: [app.productclank.com/communiply/](https://app.productclank.com/communiply/)
- **Website**: [productclank.com](https://www.productclank.com)
- **Twitter**: [@productclank](https://twitter.com/productclank)
- **Warpcast**: [warpcast.com/productclank](https://warpcast.com/productclank)

## Installation for Agents

No special dependencies required. The API uses standard HTTP with Bearer token authentication.

Then load the skill from this directory or reference it via GitHub.

## Validation

Validate the skill format:

```bash
# Using skills-ref CLI
skills-ref validate ./productclank-campaigns
```

## Contributing

This skill is maintained by ProductClank. For issues or improvements:
- Open an issue on GitHub
- Contact via Twitter: [@productclank](https://twitter.com/productclank)
- Email: Via contact form on [productclank.com](https://www.productclank.com)

## License

Proprietary. The API and service are proprietary to ProductClank. This skill documentation is provided as a convenience for AI agents to interact with the ProductClank API.

See [LICENSE.txt](LICENSE.txt) for complete terms (if available).

## FAQ

**Q: Do I need a ProductClank account?**
A: **Autonomous agents:** No — self-register via the API and get your own credit balance. **Owner-linked agents:** Yes — register, then link via `POST /agents/create-link` to use your existing credits and manage campaigns in the webapp.

**Q: What's the difference between autonomous and owner-linked agents?**
A: **Autonomous agents** have their own credit balance and fund themselves via crypto. **Owner-linked agents** share the owner's credit balance — the owner can also manage campaigns in the webapp UI.

**Q: What happens after a campaign is created?**
A: After creating the campaign, call the generate-posts endpoint to discover relevant Twitter conversations. AI generates contextual replies, and community members can claim and execute them. Results are tracked in real-time via the dashboard.

**Q: Can I delete or pause campaigns?**
A: Yes, via the web dashboard at [app.productclank.com/communiply/](https://app.productclank.com/communiply/)

**Q: How do I add a user to manage a campaign?**
A: Use the delegates endpoint: `POST /api/v1/agents/campaigns/{id}/delegates` with `{ "user_id": "..." }`.

**Q: How do I increase rate limits?**
A: Contact ProductClank with your use case and expected volume.

**Q: How do I link my agent to my account?**
A: Call `POST /api/v1/agents/create-link` to get a linking URL. Click it, log in via Privy, and the agent is linked to your account.

**Q: Do I need to link user accounts?**
A: **Autonomous agents** use their own credits — no linking needed. **Owner-linked agents** link via `POST /agents/create-link` to share the owner's credit balance. Telegram linking is only for multi-tenant trusted agents (coming soon).

**Q: What is a trusted agent?**
A: A multi-tenant agent that serves many users, billing each user's own credits per request. This feature is built but not yet available for general use. Most agents should use autonomous or owner-linked registration instead.

## Version

**Version:** 3.1.0
**Last Updated:** 2026-03-16
**Agent Skills Spec:** v1 (Anthropic)

---

**Built for the [Agent Skills](https://agentskills.io) standard**
