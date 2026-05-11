#!/usr/bin/env node

/**
 * ProductClank Campaign Creation Script
 *
 * A helper script for creating Communiply campaigns via the ProductClank Agent API.
 * Uses credit-based billing (10 credits for campaign creation, 12 credits/post for generation).
 *
 * Usage:
 *   node create-campaign.mjs
 *
 * Environment Variables Required:
 *   PRODUCTCLANK_API_KEY - Your API key (pck_live_*)
 */

// Configuration
const API_BASE_URL = "https://app.productclank.com/api/v1";
const API_KEY = process.env.PRODUCTCLANK_API_KEY;

// Validation
if (!API_KEY) {
  console.error("❌ Error: PRODUCTCLANK_API_KEY environment variable is required");
  console.error("Set it with: export PRODUCTCLANK_API_KEY=pck_live_YOUR_KEY");
  process.exit(1);
}

// Example campaign data - modify this for your use case
const campaignData = {
  product_id: "YOUR_PRODUCT_UUID", // ⚠️ Replace with your product ID
  title: "Example Campaign",
  keywords: [
    "AI tools",
    "productivity apps",
    "automation software"
  ],
  search_context: "People discussing AI productivity tools and automation challenges",
  mention_accounts: ["@productclank"],
  reply_style_tags: ["friendly", "helpful"],
  reply_length: "short",
  min_follower_count: 100,
  max_post_age_days: 7,
};

// Validate campaign data
function validateCampaignData(data) {
  const errors = [];

  if (!data.product_id || data.product_id === "YOUR_PRODUCT_UUID") {
    errors.push("product_id must be set to a valid UUID");
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

// Create campaign
async function createCampaign(data) {
  console.log("📋 Creating campaign...");

  const response = await fetch(`${API_BASE_URL}/agents/campaigns`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return response.json();
}

// Generate posts for campaign
async function generatePosts(campaignId) {
  console.log("📝 Generating posts...");

  const response = await fetch(`${API_BASE_URL}/agents/campaigns/${campaignId}/generate-posts`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  });

  return response.json();
}

// Main execution
async function main() {
  console.log("🚀 ProductClank Campaign Creation Script\n");

  // Validate campaign data
  console.log("✅ Validating campaign data...");
  const errors = validateCampaignData(campaignData);
  if (errors.length > 0) {
    console.error("❌ Validation errors:");
    errors.forEach(err => console.error(`   - ${err}`));
    console.error("\n💡 Edit the campaignData object in this script to fix these errors.");
    process.exit(1);
  }

  // Display campaign details
  console.log("📋 Campaign Details:");
  console.log(`   - Title: ${campaignData.title}`);
  console.log(`   - Keywords: ${campaignData.keywords.join(", ")}`);
  console.log("");

  try {
    // Step 1: Create campaign (10 credits)
    const result = await createCampaign(campaignData);

    if (result.success) {
      console.log("\n✅ Campaign Created Successfully!\n");
      console.log("📋 Campaign Details:");
      console.log(`   - ID: ${result.campaign.campaign_number}`);
      console.log(`   - Title: ${result.campaign.title}`);
      console.log(`   - Status: ${result.campaign.status}`);
      console.log(`   - Funded: ${result.campaign.is_funded ? 'Yes' : 'No'}`);
      console.log("");
      console.log("💰 Credits:");
      console.log(`   - Used: ${result.credits.credits_used}`);
      console.log(`   - Remaining: ${result.credits.credits_remaining}`);
      console.log("");
      console.log("🔗 View Campaign:");
      console.log(`   ${result.campaign.url}`);

      // Step 2: Generate posts (12 credits/post)
      console.log("\n--- Generating Posts ---\n");
      const postsResult = await generatePosts(result.campaign.id);

      if (postsResult.success) {
        console.log(`✅ Generated ${postsResult.posts_created} posts`);
        console.log(`💰 Credits used for posts: ${postsResult.credits_used}`);
        console.log(`💰 Credits remaining: ${postsResult.credits_remaining}`);
      } else {
        console.error(`❌ Post generation failed: ${postsResult.message}`);
      }

      console.log("");
      console.log("🎯 Next Steps:");
      console.log("   1. Community members can claim and execute replies");
      console.log("   2. Track engagement in real-time via dashboard");
      console.log("");
    } else {
      console.error(`\n❌ Campaign Creation Failed\n`);
      console.error(`Error: ${result.error}`);
      console.error(`Message: ${result.message}`);

      if (result.error === "insufficient_credits") {
        console.error("\n💡 Insufficient Credits:");
        console.error(`   Need: ${result.credits_required} credits`);
        console.error(`   Have: ${result.credits_available} credits`);
        console.error(`   Shortfall: ${result.shortfall} credits`);
        console.error("\n   Top up credits via the webapp or the credits/topup API endpoint.");
      } else if (result.error === "rate_limit_exceeded") {
        console.error("\n💡 Rate limit exceeded. Try again tomorrow or contact ProductClank for higher limits.");
      } else if (result.error === "unauthorized") {
        console.error("\n💡 Invalid API key. Verify PRODUCTCLANK_API_KEY is correct.");
      } else if (result.error === "not_found") {
        console.error("\n💡 Product not found. Verify product_id exists on ProductClank.");
        console.error("   Visit: https://app.productclank.com/products");
      }

      process.exit(1);
    }
  } catch (error) {
    console.error("\n❌ Error:", error.message);
    console.error("\nStack trace:");
    console.error(error.stack);
    process.exit(1);
  }
}

// Run script
main().catch(error => {
  console.error("Fatal error:", error);
  process.exit(1);
});
