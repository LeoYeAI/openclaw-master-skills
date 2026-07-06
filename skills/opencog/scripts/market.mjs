#!/usr/bin/env node
// Show detailed info for a single market.
//
// Usage:
//   node market.mjs --market <id>            # title, category, all outcomes + probabilities
//   node market.mjs --market <id> --criteria # also shows resolution criteria
//
// Env: PRECOG_RPC_URL (optional)
import { fileURLToPath } from "url";
import * as client from "./lib/client.mjs";
import { parseArgs, requireArgs } from "./lib/args.mjs";

export async function main(deps = {}) {
  const _parseArgs = deps.parseArgs ?? parseArgs;
  const a = _parseArgs();
  if (a.network) client.setNetwork(a.network);

  const { multiread, outcomes, pct, status, date } = { ...client, ...deps };
  requireArgs(a, ["market"]);

  const id = Number(a.market);
  const [marketRes, pricesRes, colRes] = await multiread([
    ["markets",              [BigInt(id)]],
    ["marketPrices",         [BigInt(id)]],
    ["marketCollateralInfo", [BigInt(id)]],
  ], { allowFailure: true });

  const market = marketRes.result;
  const [question, resolutionCriteria, , category, outcomesRaw, , , , , endTs] = market;
  const buyPrices = pricesRes.status === "success" ? pricesRes.result[0] : null;
  const token     = colRes.status === "success"    ? colRes.result[2]    : null;

  const rawOuts = outcomes(outcomesRaw);
  const outs = (rawOuts.length === 1 && rawOuts[0].includes(","))
    ? rawOuts[0].split(",").map(s => s.trim()).filter(Boolean)
    : rawOuts;

  const s = status(endTs);

  // ── Header ────────────────────────────────────────────────────────────────
  const catPart = category ? `  ·  ${category}` : "";
  console.log(`\n📊  Market ${id}${catPart}`);
  console.log(`${question}`);

  const tokPart  = token ? `  💰 ${token}` : "";
  const statIcon = s === "active" ? "🟢" : "🔴";
  console.log(`${statIcon} ${s.charAt(0).toUpperCase() + s.slice(1)}  📅 ${date(endTs)}${tokPart}\n`);

  // ── Outcomes ──────────────────────────────────────────────────────────────
  const medals = ["🥇", "🥈", "🥉"];

  // Rank by price descending (if prices available)
  const ranked = outs.map((label, idx) => {
    const price = buyPrices ? Number(buyPrices[idx + 1]) / 1e18 : null;
    return { n: idx + 1, label, price };
  });
  if (buyPrices) ranked.sort((a, b) => b.price - a.price);

  const maxLabel = Math.max(...ranked.map(r => r.label.length));

  for (let i = 0; i < ranked.length; i++) {
    const { n, label, price } = ranked[i];
    const icon   = medals[i] ?? "   ";
    const padded = label.padEnd(maxLabel);
    const pctStr = price !== null ? `  ${(price * 100).toFixed(1)}%` : "";
    console.log(`${icon}  [${n}] ${padded}${pctStr}`);
  }

  // ── Resolution criteria ───────────────────────────────────────────────────
  if ("criteria" in a) {
    if (resolutionCriteria) {
      console.log(`\n📝  Resolution Criteria\n${resolutionCriteria}`);
    } else {
      console.log("\n📝  No resolution criteria on record.");
    }
  }

  console.log("");
  return { id, question, category, resolutionCriteria, outs, status: s };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(e => { console.error(e.message); process.exit(1); });
}
