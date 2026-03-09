#!/usr/bin/env node

/**
 * Citedy Agent — Registration Script
 * Usage: node register.mjs [agent_name]
 *
 * Registers a new agent with Citedy and outputs the approval URL.
 * Requires Node.js 18+ (built-in fetch).
 */

import { hostname } from "os";

const BASE_URL = "https://www.citedy.com";

async function main() {
  const agentName = process.argv[2] || `agent-${hostname()}`;

  console.log(`Registering agent "${agentName}" with Citedy...`);

  const res = await fetch(`${BASE_URL}/api/agent/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ agent_name: agentName }),
  });

  if (!res.ok) {
    const text = await res.text();
    let msg = text;
    try {
      const json = JSON.parse(text);
      msg = json.message || json.error || text;
    } catch {
      /* non-JSON response */
    }
    console.error(`Registration failed (${res.status}): ${msg}`);
    process.exit(1);
  }

  const data = await res.json();

  if (!data.approval_url) {
    console.error("Unexpected response — no approval_url:", data);
    process.exit(1);
  }

  console.log("\nApproval URL (open in browser):");
  console.log(`  ${data.approval_url}`);
  console.log(`\nExpires in: ${data.expires_in || 3600}s`);
  console.log("\nAfter approving, copy the API key and pass it to your agent.");
}

main().catch((err) => {
  console.error("Error:", err.message || err);
  process.exit(1);
});
