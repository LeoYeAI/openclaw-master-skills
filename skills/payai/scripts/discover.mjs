#!/usr/bin/env node
// discover.mjs — Browse the PayAI Bazaar: live x402 paid resources you can call.
//
// Usage:
//   node discover.mjs [--network <name>] [--query <text>] [--limit <n>] [--json]
//
// Examples:
//   node discover.mjs                     # recent resources
//   node discover.mjs --network solana    # only resources payable on Solana
//   node discover.mjs --query weather     # match resource URL / description
//
// Zero dependencies — requires Node 18+ (global fetch).

const FACILITATOR = process.env.PAYAI_FACILITATOR || "https://facilitator.payai.network";

const args = process.argv.slice(2);
let network, query, limit = 25, asJson = false;
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--network") network = (args[++i] || "").toLowerCase();
  else if (args[i] === "--query") query = (args[++i] || "").toLowerCase();
  else if (args[i] === "--limit") limit = Number(args[++i]) || 25;
  else if (args[i] === "--json") asJson = true;
  else if (args[i] === "-h" || args[i] === "--help") {
    console.log("Usage: node discover.mjs [--network <name>] [--query <text>] [--limit <n>] [--json]");
    process.exit(0);
  }
}

const ASSETS = {
  EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v: { symbol: "USDC", decimals: 6 },
  "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913":  { symbol: "USDC", decimals: 6 },
};
const assetInfo = a => ASSETS[a] || ASSETS[String(a).toLowerCase()] || { symbol: "token", decimals: 6 };

function human(baseUnits, decimals) {
  try {
    const n = BigInt(baseUnits), d = BigInt(10) ** BigInt(decimals);
    const frac = (n % d).toString().padStart(decimals, "0").replace(/0+$/, "");
    return frac ? `${n / d}.${frac}` : `${n / d}`;
  } catch { return String(baseUnits); }
}

const res = await fetch(`${FACILITATOR}/discovery/resources?limit=${Math.max(limit * 3, 50)}`);
if (!res.ok) {
  console.error(`Failed to reach Bazaar: HTTP ${res.status} ${res.statusText}`);
  process.exit(1);
}
const data = await res.json();
let items = data.items || [];

if (network) items = items.filter(it => (it.accepts || []).some(a => String(a.network).toLowerCase().includes(network)));
if (query)   items = items.filter(it => JSON.stringify(it).toLowerCase().includes(query));
items = items.slice(0, limit);

if (asJson) { console.log(JSON.stringify(items, null, 2)); process.exit(0); }

console.log(`\nPayAI Bazaar — ${items.length} resource(s)  (facilitator: ${FACILITATOR})`);
if (network) console.log(`filter: network~="${network}"`);
if (query)   console.log(`filter: query~="${query}"`);

for (const it of items) {
  const opts = (it.accepts || []).map(a => {
    const info = assetInfo(a.asset);
    const amt = a.maxAmountRequired ?? a.amount;
    return `${human(amt, info.decimals)} ${info.symbol} on ${a.network}`;
  });
  console.log(`\n• ${it.method || "GET"} ${it.resource}`);
  if (it.accepts?.[0]?.description) console.log(`  ${it.accepts[0].description}`);
  console.log(`  pay: ${opts.join("  |  ") || "(no accepts listed)"}`);
  if (it.accepts?.[0]?.payTo) console.log(`  payTo: ${it.accepts[0].payTo}`);
}

console.log(`\nTo call + pay one of these, use the companion \`x402\` skill.`);
