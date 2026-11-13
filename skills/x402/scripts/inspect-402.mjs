#!/usr/bin/env node
// inspect-402.mjs — Probe a URL for x402 payment requirements WITHOUT paying.
//
// Usage:
//   node inspect-402.mjs <url> [--method POST] [--data '{"k":"v"}'] [--header 'K: V']
//
// Prints, for each accepted payment option: network, asset, human-readable
// amount, recipient (payTo), and the facilitator fee payer (Solana). Zero
// dependencies — requires Node 18+ (global fetch).

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") {
  console.log("Usage: node inspect-402.mjs <url> [--method POST] [--data '<body>'] [--header 'K: V']");
  process.exit(args.length === 0 ? 1 : 0);
}

const url = args[0];
let method = "GET";
let body;
const headers = {};
for (let i = 1; i < args.length; i++) {
  if (args[i] === "--method") method = args[++i];
  else if (args[i] === "--data") { body = args[++i]; method = method === "GET" ? "POST" : method; }
  else if (args[i] === "--header") {
    const raw = args[++i] || "";
    const idx = raw.indexOf(":");
    if (idx > -1) headers[raw.slice(0, idx).trim()] = raw.slice(idx + 1).trim();
  }
}
if (body && !Object.keys(headers).some(h => h.toLowerCase() === "content-type")) {
  headers["Content-Type"] = "application/json";
}

// Known assets, for friendly labels + decimals. Everything else defaults to 6.
const ASSETS = {
  EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v: { symbol: "USDC", decimals: 6 }, // Solana
  "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913":  { symbol: "USDC", decimals: 6 }, // Base
};

function describeAsset(asset) {
  const info = ASSETS[asset] || ASSETS[String(asset).toLowerCase()];
  return info || { symbol: "token", decimals: 6 };
}

function humanAmount(baseUnits, decimals) {
  try {
    const n = BigInt(baseUnits);
    const d = BigInt(10) ** BigInt(decimals);
    const whole = n / d;
    const frac = (n % d).toString().padStart(decimals, "0").replace(/0+$/, "");
    return frac ? `${whole}.${frac}` : `${whole}`;
  } catch {
    return String(baseUnits);
  }
}

function printAccepts(accepts) {
  accepts.forEach((a, i) => {
    const asset = describeAsset(a.asset);
    const amount = a.maxAmountRequired ?? a.amount;
    console.log(`\n  [${i}] ${a.scheme || "exact"} on ${a.network}`);
    console.log(`      price:   ${humanAmount(amount, asset.decimals)} ${asset.symbol}  (${amount} base units)`);
    console.log(`      asset:   ${a.asset}`);
    console.log(`      payTo:   ${a.payTo}`);
    if (a.extra?.feePayer) console.log(`      feePayer:${" "}${a.extra.feePayer}  (facilitator pays Solana gas)`);
    if (a.maxTimeoutSeconds) console.log(`      timeout: ${a.maxTimeoutSeconds}s`);
    if (a.description) console.log(`      desc:    ${a.description}`);
  });
}

const res = await fetch(url, { method, body, headers });
console.log(`\n${method} ${url}\n→ HTTP ${res.status} ${res.statusText}`);

if (res.status !== 402) {
  console.log("\nNo payment required (status is not 402). Nothing to inspect.");
  process.exit(0);
}

// x402 requirements can arrive in the JSON body OR a base64 PAYMENT-REQUIRED header.
let parsed = null;
const bodyText = await res.text();
try { parsed = JSON.parse(bodyText); } catch { /* not JSON */ }

const headerVal = res.headers.get("PAYMENT-REQUIRED") || res.headers.get("payment-required");
if (!parsed?.accepts && headerVal) {
  try { parsed = JSON.parse(Buffer.from(headerVal, "base64").toString("utf8")); } catch { /* ignore */ }
}

if (parsed?.accepts?.length) {
  console.log(`\nx402 version: ${parsed.x402Version ?? "(unspecified)"}`);
  console.log(`Payment options (${parsed.accepts.length}):`);
  printAccepts(parsed.accepts);
  console.log(`\nPick an option whose network you hold USDC on, then pay it (see SKILL.md).`);
} else {
  console.log("\nGot 402 but could not find an `accepts` array in the body or PAYMENT-REQUIRED header.");
  console.log("Raw body:\n" + bodyText.slice(0, 2000));
}
