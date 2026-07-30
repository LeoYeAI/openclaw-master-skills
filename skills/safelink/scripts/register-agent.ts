#!/usr/bin/env tsx
/**
 * Register this agent in the ERC-8004 on-chain registry.
 *
 * Usage:
 *   pnpm register
 *   pnpm register --capabilities "code-review,data-analysis,endpoint:https://..."
 *   pnpm register --rate 0.05
 */

import { parseArgs } from "util";
import { readFileSync, writeFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import "dotenv/config";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ENV_FILE = join(__dirname, "..", ".env");

// 鈹€鈹€ CLI args 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

const { values } = parseArgs({
  options: {
    capabilities: { type: "string", short: "c" },
    rate: { type: "string", short: "r" },
    endpoint: { type: "string", short: "e" },
  },
});

// 鈹€鈹€ Defaults 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

const capabilitiesArg = values["capabilities"] ?? "general-assistance";
const rateArg = parseFloat(values["rate"] ?? "0.05");
const endpointArg = values["endpoint"]; // Optional HTTP endpoint for task delivery
const rpcUrl = process.env["BASE_RPC_URL"] ?? "https://sepolia.base.org";
const isMainnet = rpcUrl.includes("mainnet");
const allowedChain = isMainnet ? "base-mainnet" : "base-sepolia";

let capabilities = capabilitiesArg
  .split(",")
  .map((c) => c.trim())
  .filter(Boolean);

if (endpointArg) {
  capabilities.push(`endpoint:${endpointArg}`);
}

console.log("馃 SafeLink 鈥?Register as Service\n");
console.log("   Capabilities:", capabilities.join(", "));
console.log("   Min rate:    ", rateArg, "USDC per operation");
console.log("");

// 鈹€鈹€ Dynamic import to avoid top-level env validation before dotenv loads 鈹€鈹€鈹€鈹€鈹€鈹€

const { safe_register_as_service } = await import("../src/tools/register.js");
const { getMPCWalletClient } = await import("../src/wallet/mpc.js");

// Show wallet address first
const wallet = await getMPCWalletClient();
console.log("馃捈 Agent wallet address:", wallet.address);
console.log("   Save this as your agent ID for other agents to hire you.\n");

// 鈹€鈹€ Register 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

console.log("馃摑 Registering on-chain...");

try {
  const result = await safe_register_as_service({
    capabilities,
    min_rate: rateArg,
    policy: {
      max_task_seconds: 300,
      allowed_chains: [allowedChain],
      require_escrow: true,
      max_rate_usdc: rateArg * 10, // allow up to 10x the min rate
      auto_approve_below_risk: 30,
    },
    confirmed: true, // CLI context 鈥?auto-approve
  });

  console.log("\n鉁?Registered successfully!");
  console.log("   Agent ID:     ", result.agent_id);
  console.log("   Tx hash:      ", result.tx_hash);
  console.log("   Registry:     ", result.registry_address);
  console.log("   Network:      ", result.network);

  // Update .env with agent ID
  if (existsSync(ENV_FILE)) {
    let envContent = readFileSync(ENV_FILE, "utf8");
    const agentIdLine = `AGENT_ID=${result.agent_id}`;
    if (/^AGENT_ID=.*/m.test(envContent)) {
      envContent = envContent.replace(/^AGENT_ID=.*/m, agentIdLine);
    } else {
      envContent += `\n${agentIdLine}`;
    }
    writeFileSync(ENV_FILE, envContent.trim() + "\n");
    console.log("\n   .env updated with AGENT_ID.");
  }

  // Save wallet ID to env (so it's reused on next startup)
  if (existsSync(ENV_FILE)) {
    let envContent = readFileSync(ENV_FILE, "utf8");
    const walletLine = `PRIVY_WALLET_ID=${wallet.walletId}`;
    if (/^PRIVY_WALLET_ID=.*/m.test(envContent)) {
      envContent = envContent.replace(/^PRIVY_WALLET_ID=.*/m, walletLine);
    } else {
      envContent += `\n${walletLine}`;
    }
    writeFileSync(ENV_FILE, envContent.trim() + "\n");
    console.log("   .env updated with PRIVY_WALLET_ID.");
  }

  console.log("\n馃帀 Your agent is live on", result.network, "!");
  console.log("   Share your agent ID with other agents to be hired:");
  console.log("   ", result.agent_id);
  console.log("\n   To accept hire requests, run: pnpm start");
} catch (err) {
  console.error("\n鉂?Registration failed:", err instanceof Error ? err.message : String(err));
  process.exit(1);
}


