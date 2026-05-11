# ProductClank Agent API - Code Examples

Practical code examples for common use cases when creating Communiply campaigns via the ProductClank Agent API.

---

## Table of Contents

1. [Basic Campaign Creation](#basic-campaign-creation)
2. [Full 2-Step Flow (Create + Generate Posts)](#full-2-step-flow)
3. [Advanced Campaign with Custom Guidelines](#advanced-campaign-with-custom-guidelines)
4. [Competitor Intercept Campaign](#competitor-intercept-campaign)
5. [Product Launch Campaign](#product-launch-campaign)
6. [Adding Delegators](#adding-delegators)
7. [Trusted Agent with caller_user_id](#trusted-agent-with-caller_user_id)
8. [Error Handling & Retry Logic](#error-handling--retry-logic)
9. [TypeScript Types](#typescript-types)

---

## Basic Campaign Creation

The simplest way to create a campaign.

```typescript
async function createBasicCampaign() {
  try {
    const response = await fetch(
      "https://app.productclank.com/api/v1/agents/campaigns",
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          product_id: "your-product-uuid",
          title: "Launch Week Campaign",
          keywords: ["productivity tools", "task management", "team collaboration"],
          search_context: "People discussing productivity tools and team collaboration challenges",
        }),
      }
    );

    const result = await response.json();

    if (result.success) {
      console.log(`✅ Campaign created: ${result.campaign.campaign_number}`);
      console.log(`📊 Dashboard: ${result.campaign.url}`);
      console.log(`💰 Credits used: ${result.credits.credits_used}, remaining: ${result.credits.credits_remaining}`);
      console.log(`🔗 Next step: ${result.next_step.endpoint}`);
      return result.campaign;
    } else {
      console.error(`❌ Error: ${result.error} - ${result.message}`);
      throw new Error(result.message);
    }
  } catch (error) {
    console.error("Failed to create campaign:", error);
    throw error;
  }
}
```

**Environment Variables:**
```bash
PRODUCTCLANK_API_KEY=pck_live_...
```

---

## Full 2-Step Flow

Create a campaign and then generate posts (the complete flow).

```typescript
async function createCampaignAndGeneratePosts() {
  const API_KEY = process.env.PRODUCTCLANK_API_KEY;
  const headers = {
    "Authorization": `Bearer ${API_KEY}`,
    "Content-Type": "application/json",
  };

  // Step 1: Create campaign (10 credits)
  console.log("📋 Step 1: Creating campaign...");
  const campaignResponse = await fetch(
    "https://app.productclank.com/api/v1/agents/campaigns",
    {
      method: "POST",
      headers,
      body: JSON.stringify({
        product_id: "your-product-uuid",
        title: "AI Tools Campaign",
        keywords: ["AI tools", "automation", "workflow"],
        search_context: "People discussing AI tools and workflow automation",
        mention_accounts: ["@yourproduct"],
        reply_style_tags: ["friendly", "helpful"],
        reply_length: "short",
        min_follower_count: 500,
        max_post_age_days: 7,
      }),
    }
  );

  const campaignResult = await campaignResponse.json();

  if (!campaignResult.success) {
    console.error(`❌ Campaign creation failed: ${campaignResult.message}`);
    return;
  }

  console.log(`✅ Campaign created: ${campaignResult.campaign.campaign_number}`);
  console.log(`📊 URL: ${campaignResult.campaign.url}`);
  console.log(`💰 Credits: ${campaignResult.credits.credits_used} used, ${campaignResult.credits.credits_remaining} remaining`);

  // Step 2: Generate posts (12 credits/post)
  console.log("\n📝 Step 2: Generating posts...");
  const postsResponse = await fetch(
    `https://app.productclank.com/api/v1/agents/campaigns/${campaignResult.campaign.id}/generate-posts`,
    {
      method: "POST",
      headers,
      body: JSON.stringify({}),
    }
  );

  const postsResult = await postsResponse.json();

  if (postsResult.success) {
    console.log(`✅ Generated ${postsResult.posts_created} posts`);
    console.log(`💰 Credits used for posts: ${postsResult.credits_used}`);
    console.log(`💰 Credits remaining: ${postsResult.credits_remaining}`);
  } else {
    console.error(`❌ Post generation failed: ${postsResult.message}`);
  }

  return { campaign: campaignResult, posts: postsResult };
}
```

---

## Advanced Campaign with Custom Guidelines

Highly customized campaign with specific filters and reply instructions.

```typescript
async function createAdvancedCampaign() {
  const response = await fetch(
    "https://app.productclank.com/api/v1/agents/campaigns",
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        product_id: "your-product-uuid",
        title: "Enterprise Security Product Launch",

        // Discovery settings
        keywords: [
          "enterprise security",
          "SOC2 compliance",
          "data protection",
          "GDPR compliance",
          "security audit"
        ],
        search_context: "CISOs and security teams discussing compliance challenges, data protection requirements, and security audit preparation",

        // Reply customization
        mention_accounts: ["@yourproduct", "@cto_handle"],
        reply_style_tags: ["professional", "technical", "authoritative"],
        reply_style_account: "@briankrebs",
        reply_length: "medium",

        // Custom AI instructions
        reply_guidelines: `
You are a security engineer who has used our product for 2+ years.

**Focus on:**
- Our SOC2 Type II certification
- Automated compliance workflows (saves 20+ hours/month)
- Real-time security monitoring
- Excellent documentation and support

**Avoid:**
- Overselling or making promises
- Directly comparing to competitors
- Discussing pricing (direct them to sales)
- Mentioning unreleased features

**Mention @yourproduct naturally when relevant.**
**Include our website (https://yourproduct.com) only if it adds value.**

Tone: Professional, helpful, technically accurate. Never salesy.
        `.trim(),

        // Quality filters
        min_follower_count: 2000,
        min_engagement_count: 10,
        max_post_age_days: 3,
        require_verified: false,
      }),
    }
  );

  const result = await response.json();

  if (result.success) {
    console.log(`
✅ Advanced Campaign Created

📋 Details:
   - Title: ${result.campaign.title}
   - Campaign #: ${result.campaign.campaign_number}
   - Credits used: ${result.credits.credits_used}

🎯 Targeting:
   - 5 keywords (enterprise security space)
   - Accounts with 2000+ followers
   - Posts with 10+ engagement
   - Last 3 days only

📊 View Dashboard:
   ${result.campaign.url}

🔗 Next: Generate posts via ${result.next_step.endpoint}
    `);

    return result.campaign;
  } else {
    throw new Error(result.message);
  }
}
```

---

## Competitor Intercept Campaign

Target conversations mentioning competitors.

```typescript
async function createCompetitorInterceptCampaign() {
  const response = await fetch(
    "https://app.productclank.com/api/v1/agents/campaigns",
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        product_id: "your-product-uuid",
        title: "Competitor Intercept - Alternatives Campaign",

        keywords: [
          "Competitor1 alternative",
          "switching from Competitor2",
          "better than Competitor3",
          "Competitor4 pricing too high",
          "looking for Competitor5 replacement"
        ],

        search_context: "People actively looking for alternatives to our competitors, frustrated with pricing, features, or support",

        mention_accounts: ["@yourproduct"],
        reply_style_tags: ["helpful", "empathetic", "solution-oriented"],
        reply_length: "short",

        reply_guidelines: `
Reply as a user who recently switched from [competitor] to our product.

**Share your experience:**
- What frustrated you about [competitor]
- What made you switch to us
- Specific features/benefits you love now

**Be authentic:**
- Don't bash competitors
- Share genuine experience
- Offer to help if they have questions

**Example tone:**
"I was in the same boat last month. Switched to @yourproduct and haven't looked back. Their [feature] alone saved me hours/week. Happy to share my migration process if helpful!"

Keep it conversational, not salesy.
        `.trim(),

        min_follower_count: 500,
        max_post_age_days: 2,
      }),
    }
  );

  return response.json();
}
```

---

## Product Launch Campaign

Coordinated campaign for product launch week.

```typescript
async function createLaunchWeekCampaign() {
  // Step 1: Create campaign
  const response = await fetch(
    "https://app.productclank.com/api/v1/agents/campaigns",
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        product_id: "your-product-uuid",
        title: "Launch Week 2026 - Community Amplification",

        keywords: [
          "new AI tools",
          "product launch",
          "Show HN",
          "Product Hunt",
          "indie hacker tools",
          "startup tools 2026"
        ],

        search_context: "People discussing new product launches, sharing cool tools they found, and looking for recommendations in the AI/productivity space",

        mention_accounts: ["@yourproduct", "@founder"],
        reply_style_tags: ["excited", "friendly", "genuine"],
        reply_length: "mixed",

        reply_guidelines: `
You're an early beta user who's been using the product for 3 months.

**Launch week focus:**
- Share what you've built with it
- Mention it launched today/this week
- Highlight 1-2 unique features
- Offer to answer questions

**Example angles:**
- "Just saw @yourproduct launched today! Been using the beta for months..."
- "This reminds me of @yourproduct which just launched. They solve this exact problem by..."
- "Perfect timing - @yourproduct literally just released a feature for this yesterday..."

**Include launch link:** https://yourproduct.com/launch

Be genuinely enthusiastic but not pushy. Share real value.
        `.trim(),

        min_follower_count: 200,
        max_post_age_days: 1,
      }),
    }
  );

  const result = await response.json();

  if (result.success) {
    // Step 2: Generate posts
    const postsResult = await fetch(
      `https://app.productclank.com/api/v1/agents/campaigns/${result.campaign.id}/generate-posts`,
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      }
    ).then(r => r.json());

    console.log(`
🚀 LAUNCH WEEK CAMPAIGN LIVE!

Campaign: ${result.campaign.campaign_number}
Credits used: ${result.credits.credits_used} (creation) + ${postsResult.credits_used || 0} (posts)
Dashboard: ${result.campaign.url}

🎯 Targeting fresh conversations about:
   - New AI tools
   - Product launches
   - Show HN / Product Hunt
   - Startup tools

📝 Posts generated: ${postsResult.posts_created || 0}

✅ Community is now discovering and amplifying your launch!
    `);

    return result.campaign;
  } else {
    throw new Error(result.message);
  }
}
```

---

## Adding Delegators

Add a user as a delegator so they can manage the campaign in the webapp.

```typescript
async function addDelegator(campaignId: string, userId: string) {
  const response = await fetch(
    `https://app.productclank.com/api/v1/agents/campaigns/${campaignId}/delegates`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: userId,
      }),
    }
  );

  const result = await response.json();

  if (result.success) {
    if (result.already_delegator) {
      console.log(`ℹ️ User ${userId} is already a delegator for this campaign`);
    } else {
      console.log(`✅ User ${userId} added as delegator for campaign ${campaignId}`);
    }
  } else {
    console.error(`❌ Failed to add delegator: ${result.message}`);
  }

  return result;
}

// Usage: After creating a campaign, add the user who requested it
const campaign = await createBasicCampaign();
await addDelegator(campaign.id, "user-uuid-of-requester");
```

---

## Trusted Agent with caller_user_id

Trusted agents can bill a human user's credits and auto-add them as a delegator.

```typescript
async function createCampaignForUser(userId: string) {
  // Step 1: Create campaign, billing the user's credits
  const response = await fetch(
    "https://app.productclank.com/api/v1/agents/campaigns",
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        product_id: "product-uuid",
        title: "Campaign for User",
        keywords: ["AI tools", "productivity"],
        search_context: "People discussing AI productivity tools",
        // This bills the user's credits AND auto-adds them as a delegator
        caller_user_id: userId,
      }),
    }
  );

  const result = await response.json();

  if (!result.success) {
    if (result.error === "forbidden") {
      console.error("❌ Your agent is not trusted. Contact ProductClank for trusted status.");
    } else if (result.error === "insufficient_credits") {
      console.error(`❌ User doesn't have enough credits. Need ${result.credits_required}, have ${result.credits_available}.`);
    }
    return null;
  }

  console.log(`✅ Campaign created for user ${userId}`);
  console.log(`💰 Credits deducted from user: ${result.credits.credits_used}`);

  // Step 2: Generate posts, also billing the user
  const postsResult = await fetch(
    `https://app.productclank.com/api/v1/agents/campaigns/${result.campaign.id}/generate-posts`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        caller_user_id: userId, // Also bill the user for post generation
      }),
    }
  ).then(r => r.json());

  return { campaign: result, posts: postsResult };
}
```

---

## Error Handling & Retry Logic

Robust error handling with retries.

```typescript
async function createCampaignWithRetry(
  campaignData: CampaignRequest,
  maxRetries = 3
) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`Attempt ${attempt}/${maxRetries}...`);

      const response = await fetch(
        "https://app.productclank.com/api/v1/agents/campaigns",
        {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(campaignData),
        }
      );

      const result = await response.json();

      // Success
      if (result.success) {
        console.log(`✅ Success on attempt ${attempt}`);
        return result.campaign;
      }

      // Handle specific errors (don't retry these)
      switch (result.error) {
        case "rate_limit_exceeded":
          console.error("❌ Rate limit exceeded. Try again tomorrow.");
          throw new Error("RATE_LIMIT");

        case "insufficient_credits":
          console.error(`❌ Insufficient credits. Need ${result.credits_required}, have ${result.credits_available}.`);
          throw new Error("INSUFFICIENT_CREDITS");

        case "unauthorized":
          console.error("❌ Invalid API key");
          throw new Error("UNAUTHORIZED");

        case "forbidden":
          console.error("❌ Forbidden: " + result.message);
          throw new Error("FORBIDDEN");

        case "not_found":
          console.error("❌ Product not found");
          throw new Error("NOT_FOUND");

        case "validation_error":
          console.error(`❌ Validation error: ${result.message}`);
          throw new Error("VALIDATION_ERROR");

        default:
          // Retry on server errors
          console.warn(`⚠️  Attempt ${attempt} failed: ${result.error}`);
          if (attempt === maxRetries) {
            throw new Error(result.message);
          }

          // Exponential backoff
          const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);
          console.log(`⏳ Waiting ${delay}ms before retry...`);
          await new Promise(resolve => setTimeout(resolve, delay));
      }
    } catch (error: any) {
      // Don't retry on known errors
      const noRetryErrors = [
        "RATE_LIMIT", "INSUFFICIENT_CREDITS", "UNAUTHORIZED",
        "FORBIDDEN", "NOT_FOUND", "VALIDATION_ERROR"
      ];
      if (noRetryErrors.includes(error.message)) {
        throw error;
      }

      if (attempt === maxRetries) throw error;

      console.warn(`⚠️  Network error, retrying...`);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}
```

---

## TypeScript Types

Type definitions for type-safe development.

```typescript
// Campaign Request
interface CampaignRequest {
  product_id: string;
  title: string;
  keywords: string[];
  search_context: string;
  mention_accounts?: string[];
  reply_style_tags?: string[];
  reply_style_account?: string;
  reply_length?: "very-short" | "short" | "medium" | "long" | "mixed";
  reply_guidelines?: string;
  min_follower_count?: number;
  min_engagement_count?: number;
  max_post_age_days?: number;
  require_verified?: boolean;
  caller_user_id?: string; // Trusted agents only
}

// Generate Posts Request
interface GeneratePostsRequest {
  caller_user_id?: string; // Trusted agents only
}

// Add Delegate Request
interface AddDelegateRequest {
  user_id: string;
}

// Campaign Creation Success Response
interface CampaignSuccessResponse {
  success: true;
  campaign: {
    id: string;
    campaign_number: string;
    title: string;
    status: "active";
    created_via: "api";
    creator_agent_id: string;
    is_funded: boolean;
    url: string;
  };
  credits: {
    credits_used: number;
    credits_remaining: number;
    billing_user_id: string;
  };
  next_step: {
    action: "generate_posts";
    endpoint: string;
    description: string;
  };
}

// Generate Posts Success Response
interface GeneratePostsSuccessResponse {
  success: true;
  posts_created: number;
  credits_used: number;
  credits_remaining: number;
  campaign_id: string;
}

// Add Delegate Success Response
interface AddDelegateSuccessResponse {
  success: true;
  message: string;
  delegator?: {
    user_id: string;
    campaign_id: string;
  };
  already_delegator?: boolean;
}

// Error Response
interface ErrorResponse {
  success: false;
  error:
    | "insufficient_credits"
    | "validation_error"
    | "unauthorized"
    | "forbidden"
    | "not_found"
    | "rate_limit_exceeded"
    | "creation_failed"
    | "internal_error";
  message: string;
  credits_required?: number;
  credits_available?: number;
  shortfall?: number;
  topup_endpoint?: string;
}

type CampaignResponse = CampaignSuccessResponse | ErrorResponse;

// Helper function with types
async function createCampaign(
  data: CampaignRequest
): Promise<CampaignSuccessResponse["campaign"]> {
  const response = await fetch(
    "https://app.productclank.com/api/v1/agents/campaigns",
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }
  );

  const result: CampaignResponse = await response.json();

  if (!result.success) {
    throw new Error(`Campaign creation failed: ${result.message}`);
  }

  return result.campaign;
}
```

---

## Helper Utilities

Useful helper functions.

```typescript
// Validate campaign data before sending
function validateCampaignData(data: Partial<CampaignRequest>): string[] {
  const errors: string[] = [];

  if (!data.product_id?.trim()) {
    errors.push("product_id is required");
  }

  if (!data.title?.trim()) {
    errors.push("title is required");
  }

  if (!data.keywords || data.keywords.length === 0) {
    errors.push("keywords must be a non-empty array");
  }

  if (!data.search_context?.trim()) {
    errors.push("search_context is required");
  }

  return errors;
}

// Format campaign URL
function getCampaignDashboardUrl(campaignId: string): string {
  return `https://app.productclank.com/communiply/${campaignId}`;
}
```

---

## Complete End-to-End Example

Full workflow from user input to campaign creation with post generation.

```typescript
async function main() {
  const headers = {
    "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
    "Content-Type": "application/json",
  };

  // 1. Gather campaign requirements (from user input, LLM, etc.)
  const campaignData: CampaignRequest = {
    product_id: "abc-123-def-456",
    title: "AI Agents Launch Week",
    keywords: [
      "AI agents",
      "autonomous agents",
      "agent frameworks",
      "AI automation"
    ],
    search_context: "Developers and founders discussing AI agents, autonomous systems, and agent frameworks",
    mention_accounts: ["@myaiagent", "@founder"],
    reply_style_tags: ["technical", "enthusiastic", "helpful"],
    reply_length: "short",
    min_follower_count: 500,
    max_post_age_days: 3,
  };

  // 2. Validate
  const errors = validateCampaignData(campaignData);
  if (errors.length > 0) {
    throw new Error(`Validation failed: ${errors.join(", ")}`);
  }

  // 3. Create campaign (10 credits)
  console.log("Creating campaign...");
  const campaignResult = await fetch(
    "https://app.productclank.com/api/v1/agents/campaigns",
    { method: "POST", headers, body: JSON.stringify(campaignData) }
  ).then(r => r.json());

  if (!campaignResult.success) {
    throw new Error(`Failed: ${campaignResult.message}`);
  }

  // 4. Generate posts (12 credits/post)
  console.log("Generating posts...");
  const postsResult = await fetch(
    `https://app.productclank.com/api/v1/agents/campaigns/${campaignResult.campaign.id}/generate-posts`,
    { method: "POST", headers, body: JSON.stringify({}) }
  ).then(r => r.json());

  // 5. Return results to user
  console.log(`
✅ Campaign Created Successfully!

📋 Campaign Details:
   - ID: ${campaignResult.campaign.campaign_number}
   - Title: ${campaignResult.campaign.title}
   - Status: ${campaignResult.campaign.status}

💰 Credits:
   - Campaign creation: ${campaignResult.credits.credits_used}
   - Post generation: ${postsResult.credits_used || 0}
   - Remaining: ${postsResult.credits_remaining || campaignResult.credits.credits_remaining}

📝 Posts Generated: ${postsResult.posts_created || 0}

🔗 View Campaign:
   ${getCampaignDashboardUrl(campaignResult.campaign.id)}

🎯 What Happens Next:
   1. Community members browse and claim reply opportunities
   2. They post replies from their personal accounts
   3. You track engagement and ROI in real-time

Your campaign is now live and actively working!
  `);

  return campaignResult.campaign;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Error:", error);
    process.exit(1);
  });
```

---

---

## Growth Campaign with Rewards

Run a paid growth campaign where community members earn rewards for amplifying your launch.

```typescript
async function createGrowthRewardsCampaign() {
  const headers = {
    "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
    "Content-Type": "application/json",
  };

  // Step 1: Create a growth campaign targeting launch conversations
  const campaignResult = await fetch(
    "https://app.productclank.com/api/v1/agents/campaigns",
    {
      method: "POST",
      headers,
      body: JSON.stringify({
        product_id: "your-product-uuid",
        title: "Launch Week Growth — Earn Rewards for Amplifying",
        keywords: [
          "new productivity tools 2026",
          "best project management app",
          "team collaboration tools",
          "workflow automation startup"
        ],
        search_context: "Founders, PMs, and developers actively looking for new productivity and project management solutions",
        mention_accounts: ["@yourproduct"],
        reply_style_tags: ["enthusiastic", "helpful", "genuine"],
        reply_length: "short",
        reply_guidelines: `
You're a user who's been using the product for a few weeks during beta.

Share what you love:
- How it saved you time on X
- A specific feature that surprised you
- Why you'd recommend it

Keep it natural — you're helping someone, not selling.
Include @yourproduct when relevant.
        `.trim(),
        min_follower_count: 300,
        max_post_age_days: 5,
      }),
    }
  ).then(r => r.json());

  if (!campaignResult.success) {
    throw new Error(campaignResult.message);
  }

  // Step 2: Generate posts — community members will claim these
  // and earn crypto rewards for posting verified replies
  const postsResult = await fetch(
    `https://app.productclank.com/api/v1/agents/campaigns/${campaignResult.campaign.id}/generate-posts`,
    { method: "POST", headers, body: JSON.stringify({}) }
  ).then(r => r.json());

  console.log(`
🚀 Growth Rewards Campaign Live!

Campaign: ${campaignResult.campaign.campaign_number}
Dashboard: ${campaignResult.campaign.url}
Posts generated: ${postsResult.posts_created || 0}

💰 How it works for community:
   1. Members browse ${postsResult.posts_created || 0} reply opportunities
   2. They claim a reply, customize it, post from their account
   3. Submit proof (tweet URL)
   4. Earn crypto rewards after verification

📊 Your cost: ${campaignResult.credits.credits_used + (postsResult.credits_used || 0)} credits
   (~60-80% cheaper than running Twitter ads for the same reach)
  `);

  return campaignResult.campaign;
}
```

---

## Autonomous Growth Agent (Cron-Based)

Build an agent that runs weekly campaigns automatically — detecting trends and creating fresh campaigns.

```typescript
// This runs on a cron schedule (e.g., every Monday at 9am)
async function weeklyGrowthCampaign() {
  const headers = {
    "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
    "Content-Type": "application/json",
  };

  // 1. Check credit balance before proceeding
  const balanceRes = await fetch(
    "https://app.productclank.com/api/v1/agents/credits/balance",
    { headers }
  ).then(r => r.json());

  if (balanceRes.balance < 300) {
    console.log(`⚠️ Low credits (${balanceRes.balance}). Skipping this week.`);
    // Optionally: notify team, auto-topup, etc.
    return;
  }

  // 2. Dynamic keywords based on current week's trends
  // (You'd replace this with your own trend detection logic)
  const weekNumber = Math.ceil(
    (Date.now() - new Date("2026-01-01").getTime()) / (7 * 24 * 60 * 60 * 1000)
  );

  const campaignResult = await fetch(
    "https://app.productclank.com/api/v1/agents/campaigns",
    {
      method: "POST",
      headers,
      body: JSON.stringify({
        product_id: "your-product-uuid",
        title: `Weekly Growth Push — Week ${weekNumber}`,
        keywords: [
          "need a better tool for",
          "any recommendations for",
          "what do you use for",
          "looking for a solution to"
        ],
        search_context: "People actively seeking tool recommendations in our category",
        reply_style_tags: ["helpful", "concise"],
        reply_length: "short",
        min_follower_count: 200,
        max_post_age_days: 3,
      }),
    }
  ).then(r => r.json());

  if (!campaignResult.success) return;

  // 3. Generate posts
  await fetch(
    `https://app.productclank.com/api/v1/agents/campaigns/${campaignResult.campaign.id}/generate-posts`,
    { method: "POST", headers, body: JSON.stringify({}) }
  );

  console.log(`✅ Week ${weekNumber} campaign created: ${campaignResult.campaign.url}`);
}
```

---

## Tweet Boost — Rally Community Around Your Post

Get your community to engage with your tweet — replies showing support, asking questions, congratulating, plus likes and reposts.

```typescript
async function boostTweet(
  tweetUrl: string,
  actionType: "replies" | "likes" | "repost",
  options?: { tweetText?: string; tweetAuthor?: string; guidelines?: string }
) {
  const creditCost = actionType === "replies" ? 200 : 300;

  const result = await fetch(
    "https://app.productclank.com/api/v1/agents/campaigns/boost",
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        product_id: "your-product-uuid",
        tweet_url: tweetUrl,
        action_type: actionType,
        // For reply boosts — tell the community how to engage
        ...(actionType === "replies" && {
          reply_guidelines: options?.guidelines ||
            "Show genuine excitement. Ask thoughtful questions about the features or congratulate the team. Keep it authentic.",
        }),
        // Optional: pass tweet text to skip server-side fetch (useful when Twitter API is down)
        ...(options?.tweetText && { tweet_text: options.tweetText }),
        ...(options?.tweetAuthor && { tweet_author: options.tweetAuthor }),
      }),
    }
  ).then(r => r.json());

  if (result.success) {
    const actions = actionType === "replies" ? "10 community replies" : actionType === "likes" ? "30 likes" : "10 reposts";
    console.log(`
Boost created!

Tweet: ${tweetUrl}
Action: ${actions} from real community members
Cost: ${creditCost} credits
Dashboard: ${result.campaign.url}
    `);
  }

  return result;
}

// Community replies with support and questions
await boostTweet(
  "https://x.com/myproduct/status/123456789",
  "replies",
  {
    tweetText: "We just shipped v2.0! New API with 10x faster response times.",
    tweetAuthor: "myproduct",
    guidelines: "Congratulate the team, ask about the new API features, show excitement",
  }
);

// Community likes
await boostTweet("https://x.com/myproduct/status/123456789", "likes");

// Community reposts
await boostTweet("https://x.com/myproduct/status/123456789", "repost");
```

**Also available via CLI:**
```bash
# Install: npm install -g @productclank/communiply-cli

# Community replies with guidelines
communiply boost https://x.com/myproduct/status/123 --action replies \
  --guidelines "Congratulate the team, ask about new features" \
  --tweet-text "We just shipped v2.0!"

# Likes
communiply boost https://x.com/myproduct/status/123 --action likes

# Reposts
communiply boost https://x.com/myproduct/status/123 --action reposts
```

---

## Multi-Product Growth Agency

Manage campaigns for multiple clients from a single agent.

```typescript
interface ClientProduct {
  productId: string;
  name: string;
  keywords: string[];
  searchContext: string;
  teamUserId?: string; // Add as delegator
}

async function createCampaignsForPortfolio(clients: ClientProduct[]) {
  const headers = {
    "Authorization": `Bearer ${process.env.PRODUCTCLANK_API_KEY}`,
    "Content-Type": "application/json",
  };

  const results = [];

  for (const client of clients) {
    // Create campaign for each client product
    const campaignResult = await fetch(
      "https://app.productclank.com/api/v1/agents/campaigns",
      {
        method: "POST",
        headers,
        body: JSON.stringify({
          product_id: client.productId,
          title: `${client.name} — Weekly Outreach`,
          keywords: client.keywords,
          search_context: client.searchContext,
          reply_style_tags: ["professional", "helpful"],
          reply_length: "short",
          min_follower_count: 500,
          max_post_age_days: 7,
        }),
      }
    ).then(r => r.json());

    if (!campaignResult.success) {
      console.error(`❌ ${client.name}: ${campaignResult.message}`);
      continue;
    }

    // Generate posts
    await fetch(
      `https://app.productclank.com/api/v1/agents/campaigns/${campaignResult.campaign.id}/generate-posts`,
      { method: "POST", headers, body: JSON.stringify({}) }
    );

    // Add client's team as delegator so they can manage it
    if (client.teamUserId) {
      await fetch(
        `https://app.productclank.com/api/v1/agents/campaigns/${campaignResult.campaign.id}/delegates`,
        {
          method: "POST",
          headers,
          body: JSON.stringify({ user_id: client.teamUserId }),
        }
      );
    }

    console.log(`✅ ${client.name}: ${campaignResult.campaign.url}`);
    results.push({ client: client.name, campaign: campaignResult.campaign });
  }

  return results;
}

// Usage
await createCampaignsForPortfolio([
  {
    productId: "uuid-1",
    name: "DeFi Protocol",
    keywords: ["DeFi yield", "staking rewards", "liquidity pools"],
    searchContext: "Crypto users looking for DeFi yield opportunities",
    teamUserId: "user-uuid-1",
  },
  {
    productId: "uuid-2",
    name: "Dev Tools Startup",
    keywords: ["developer tools", "API management", "backend framework"],
    searchContext: "Developers discussing backend frameworks and API tooling",
    teamUserId: "user-uuid-2",
  },
]);
```

---

For more examples and use cases, see:
- [SKILL.md](../SKILL.md) - Main skill documentation
- [API_REFERENCE.md](./API_REFERENCE.md) - Complete API reference
- [scripts/create-campaign.mjs](../scripts/create-campaign.mjs) - Ready-to-use script
