#!/usr/bin/env tsx
/**
 * SafeLink interactive .env setup wizard.
 *
 * Usage: npm run setup
 */

import * as readline from "readline";
import { writeFileSync, existsSync, readFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ENV_FILE = join(__dirname, "..", ".env");
const MAINNET_CONFIRM_PHRASE = "I_UNDERSTAND_MAINNET_RISK";

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const ask = (q: string): Promise<string> => new Promise((r) => rl.question(q, r));

function ok(msg: string) {
  console.log(`  OK: ${msg}`);
}
function warn(msg: string) {
  console.log(`  WARN: ${msg}`);
}
function fail(msg: string) {
  console.log(`  ERROR: ${msg}`);
}
function hr() {
  console.log("  " + "-".repeat(56));
}

async function testRPC(url: string): Promise<boolean> {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jsonrpc: "2.0", method: "eth_chainId", params: [], id: 1 }),
      signal: AbortSignal.timeout(8000),
    });
    const data = (await res.json()) as { result?: string };
    return !!data.result;
  } catch {
    return false;
  }
}

async function testAnthropic(key: string): Promise<boolean> {
  try {
    const res = await fetch("https://api.anthropic.com/v1/models", {
      headers: { "x-api-key": key, "anthropic-version": "2023-06-01" },
      signal: AbortSignal.timeout(8000),
    });
    return res.status === 200;
  } catch {
    return false;
  }
}

async function testOpenAICompatible(baseUrl: string, key: string): Promise<boolean> {
  try {
    const res = await fetch(`${baseUrl.replace(/\/+$/, "")}/models`, {
      headers: { Authorization: `Bearer ${key}` },
      signal: AbortSignal.timeout(8000),
    });
    return res.status >= 200 && res.status < 300;
  } catch {
    return false;
  }
}

async function testPrivy(appId: string, appSecret: string): Promise<boolean> {
  try {
    const res = await fetch(`https://auth.privy.io/api/v1/apps/${appId}`, {
      headers: {
        "privy-app-id": appId,
        Authorization: `Basic ${Buffer.from(`${appId}:${appSecret}`).toString("base64")}`,
      },
      signal: AbortSignal.timeout(8000),
    });
    return res.status === 200;
  } catch {
    return false;
  }
}

let env: Record<string, string> = {};
if (existsSync(ENV_FILE)) {
  const lines = readFileSync(ENV_FILE, "utf8").split("\n");
  for (const line of lines) {
    const eq = line.indexOf("=");
    if (eq > 0 && !line.startsWith("#")) {
      const key = line.slice(0, eq).trim();
      const val = line.slice(eq + 1).trim();
      if (key) env[key] = val;
    }
  }
  console.log("Loaded existing .env. Press Enter to keep existing values.\n");
}

console.log("SafeLink Setup Wizard\n");
console.log("Required: one LLM provider + one wallet provider\n");

hr();
console.log("  Step 1/4: LLM Provider");
hr();
console.log("  [A] Anthropic direct");
console.log("  [B] OpenAI-compatible endpoint (OpenClaw gateway/proxy/etc.)\n");

const llmChoice = (await ask("  Choose [A/b]: ")).trim().toLowerCase();
const useAnthropic = llmChoice !== "b";

if (useAnthropic) {
  env["LLM_PROVIDER"] = "anthropic";
  const key = await ask(`  Anthropic API Key ${env["ANTHROPIC_API_KEY"] ? "(Enter to keep)" : ""}: `);
  if (key.trim()) {
    process.stdout.write("  Testing... ");
    if (await testAnthropic(key.trim())) ok("valid");
    else warn("could not verify Anthropic key");
    env["ANTHROPIC_API_KEY"] = key.trim();
  } else if (!env["ANTHROPIC_API_KEY"]) {
    fail("ANTHROPIC_API_KEY is required for anthropic mode");
    rl.close();
    process.exit(1);
  }
  if (!env["ANTHROPIC_MODEL"]) env["ANTHROPIC_MODEL"] = "claude-haiku-4-5-20251001";
} else {
  env["LLM_PROVIDER"] = "openai_compatible";

  const base = await ask(
    `  LLM Base URL ${env["LLM_BASE_URL"] ? `(Enter to keep: ${env["LLM_BASE_URL"]})` : "(e.g. https://your-gateway/v1)"}: `
  );
  if (base.trim()) env["LLM_BASE_URL"] = base.trim();

  const key = await ask(`  LLM API Key ${env["LLM_API_KEY"] ? "(Enter to keep)" : ""}: `);
  if (key.trim()) env["LLM_API_KEY"] = key.trim();

  const model = await ask(
    `  LLM Model ${env["LLM_MODEL"] ? `(Enter to keep: ${env["LLM_MODEL"]})` : "(default: gpt-4o-mini)"}: `
  );
  if (model.trim()) env["LLM_MODEL"] = model.trim();
  else if (!env["LLM_MODEL"]) env["LLM_MODEL"] = "gpt-4o-mini";

  if (!env["LLM_BASE_URL"] || !env["LLM_API_KEY"]) {
    fail("LLM_BASE_URL and LLM_API_KEY are required for openai_compatible mode");
    rl.close();
    process.exit(1);
  }

  process.stdout.write("  Testing endpoint... ");
  if (await testOpenAICompatible(env["LLM_BASE_URL"], env["LLM_API_KEY"])) ok("reachable");
  else warn("could not verify /models endpoint");
}

hr();
console.log("  Step 2/4: Wallet Provider");
hr();
console.log("  [A] Coinbase AgentKit (recommended)");
console.log("  [B] Privy MPC\n");

const walletChoice = (await ask("  Choose [A/b]: ")).trim().toLowerCase();
const useCoinbase = walletChoice !== "b";

if (useCoinbase) {
  env["WALLET_PROVIDER"] = "coinbase";
  const keyName = await ask(
    `  CDP Key Name ${env["COINBASE_CDP_API_KEY_NAME"] ? "(Enter to keep)" : ""}: `
  );
  if (keyName.trim()) env["COINBASE_CDP_API_KEY_NAME"] = keyName.trim();

  const priv = await ask(
    `  CDP Private Key ${env["COINBASE_CDP_API_KEY_PRIVATE_KEY"] ? "(Enter to keep)" : ""}: `
  );
  if (priv.trim()) env["COINBASE_CDP_API_KEY_PRIVATE_KEY"] = priv.trim();

  if (!env["COINBASE_CDP_API_KEY_NAME"] || !env["COINBASE_CDP_API_KEY_PRIVATE_KEY"]) {
    fail("Coinbase key name and private key are required");
    rl.close();
    process.exit(1);
  }
} else {
  env["WALLET_PROVIDER"] = "privy";
  const appId = await ask(`  Privy App ID ${env["PRIVY_APP_ID"] ? "(Enter to keep)" : ""}: `);
  if (appId.trim()) env["PRIVY_APP_ID"] = appId.trim();

  const secret = await ask(
    `  Privy App Secret ${env["PRIVY_APP_SECRET"] ? "(Enter to keep)" : ""}: `
  );
  if (secret.trim()) env["PRIVY_APP_SECRET"] = secret.trim();

  if (!env["PRIVY_APP_ID"] || !env["PRIVY_APP_SECRET"]) {
    fail("Privy App ID and App Secret are required");
    rl.close();
    process.exit(1);
  }

  process.stdout.write("  Testing Privy credentials... ");
  if (await testPrivy(env["PRIVY_APP_ID"], env["PRIVY_APP_SECRET"])) ok("valid");
  else warn("could not verify Privy credentials");
}

hr();
console.log("  Step 3/4: Base Network + RPC");
hr();
console.log("  [A] Base Sepolia (testnet)");
console.log("  [B] Base Mainnet (real funds)\n");

const networkChoice = (await ask("  Choose [A/b]: ")).trim().toLowerCase();
const defaultRpc = networkChoice === "b" ? "https://mainnet.base.org" : "https://sepolia.base.org";

const rpc = await ask(
  `  RPC URL ${env["BASE_RPC_URL"] ? `(Enter to keep: ${env["BASE_RPC_URL"]})` : `(Enter for default: ${defaultRpc})`}: `
);
if (rpc.trim()) env["BASE_RPC_URL"] = rpc.trim();
else if (!env["BASE_RPC_URL"]) env["BASE_RPC_URL"] = defaultRpc;

process.stdout.write("  Testing RPC... ");
if (await testRPC(env["BASE_RPC_URL"])) ok("connected");
else warn("RPC check failed; verify URL/provider");

if (env["BASE_RPC_URL"].includes("mainnet")) {
  console.log("");
  warn("Base Mainnet selected. Real funds may be used.");
  const confirm = await ask(`  Type ${MAINNET_CONFIRM_PHRASE} to continue: `);
  if (confirm.trim() !== MAINNET_CONFIRM_PHRASE) {
    fail("Mainnet confirmation mismatch. Aborting setup.");
    rl.close();
    process.exit(1);
  }
  env["MAINNET_ENABLED"] = "true";
  env["MAINNET_CONFIRM_TEXT"] = MAINNET_CONFIRM_PHRASE;
} else {
  env["MAINNET_ENABLED"] = "false";
  env["MAINNET_CONFIRM_TEXT"] = "";
}

hr();
console.log("  Step 4/4: Optional");
hr();

const tenderlyKey = await ask("  Tenderly Access Key (optional): ");
if (tenderlyKey.trim()) {
  env["TENDERLY_ACCESS_KEY"] = tenderlyKey.trim();
  const account = await ask("  Tenderly Account ID: ");
  if (account.trim()) env["TENDERLY_ACCOUNT_ID"] = account.trim();
  const slug = await ask("  Tenderly Project Slug [SafeLink]: ");
  env["TENDERLY_PROJECT_SLUG"] = slug.trim() || "SafeLink";
}

env["X402_FACILITATOR_URL"] = env["X402_FACILITATOR_URL"] || "https://x402.org/facilitator";
const redisUrl = await ask(
  `  Redis URL (optional, recommended for multi-instance replay protection) ${env["REDIS_URL"] ? `(Enter to keep: ${env["REDIS_URL"]})` : ""}: `
);
if (redisUrl.trim()) env["REDIS_URL"] = redisUrl.trim();

if (env["REDIS_URL"]) {
  const redisPrefix = await ask(
    `  Redis key prefix ${env["REDIS_PREFIX"] ? `(Enter to keep: ${env["REDIS_PREFIX"]})` : "[SafeLink]"}: `
  );
  env["REDIS_PREFIX"] = redisPrefix.trim() || env["REDIS_PREFIX"] || "SafeLink";
}

const agentName = await ask("  Agent name [my-SafeLink]: ");
env["AGENT_NAME"] = agentName.trim() || env["AGENT_NAME"] || "my-SafeLink";

const envLines = Object.entries(env)
  .filter(([k]) => k && !k.startsWith("#"))
  .map(([k, v]) => `${k}=${v}`);

writeFileSync(ENV_FILE, envLines.join("\n") + "\n");
ok(`.env written (${envLines.length} variables)`);

console.log("\nNext steps:");
if (env["BASE_RPC_URL"].includes("mainnet")) {
  console.log("  1. npm run deploy:contracts  (Base Mainnet, real gas)");
} else {
  console.log("  1. npm run deploy:contracts  (Base Sepolia)");
  console.log("     faucet: https://faucet.base.org");
}
console.log("  2. npm run register");
console.log("  3. npm start\n");

rl.close();


