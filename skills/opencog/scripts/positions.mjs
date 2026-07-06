#!/usr/bin/env node
// Show share positions for a wallet in a Precog prediction market.
//
// Usage:
//   node positions.mjs --market <id>
//
// Env: PRIVATE_KEY (required), PRECOG_RPC_URL (optional)
import { fileURLToPath } from "url";
import * as client from "./lib/client.mjs";
import { parseArgs, requireArgs } from "./lib/args.mjs";

export async function main(deps = {}) {
  const _parseArgs   = deps.parseArgs   ?? parseArgs;
  const _requireArgs = deps.requireArgs ?? requireArgs;
  const a = _parseArgs();
  if (a.network) client.setNetwork(a.network);

  const { multiread, getWallet, outcomes, fromRaw, pct } = { ...client, ...deps };
  _requireArgs(a, ["market"]);

  const marketId = BigInt(a.market);
  const { account } = getWallet();

  const [marketRes, colRes, accountRes, pricesRes] = await multiread([
    ["markets",              [marketId]],
    ["marketCollateralInfo", [marketId]],
    ["marketAccountInfo",    [marketId, account.address]],
    ["marketPrices",         [marketId]],
  ], { allowFailure: true });

  if (marketRes.status  === "failure") throw new Error("Failed to load market");
  if (colRes.status     === "failure") throw new Error("Failed to load collateral info");
  if (accountRes.status === "failure") throw new Error("Failed to load account info");

  const [question, , , , outcomesRaw]                         = marketRes.result;
  const [, , colSymbol, colDecimals]                          = colRes.result;
  const [totalBuys, totalSells, deposited, withdrawn, redeemed, balances] = accountRes.result;
  const buyPrices = pricesRes.status === "success" ? pricesRes.result[0] : null;

  const dec  = Number(colDecimals);
  const outs = outcomes(outcomesRaw);

  const netCost = deposited - withdrawn - redeemed;

  // ── Header ────────────────────────────────────────────────────────────────
  console.log(`\n💼  Market ${a.market}`);
  console.log(`${question}\n`);
  console.log(`👛  ${account.address}`);
  console.log(`💵  Net cost  ${fromRaw(netCost < 0n ? 0n : netCost, dec)} ${colSymbol}  ·  📥 ${totalBuys} buys  📤 ${totalSells} sells\n`);

  // ── Shares ────────────────────────────────────────────────────────────────
  const medals = ["🥇", "🥈", "🥉"];
  const held = [];

  for (let i = 1; i < balances.length; i++) {
    if (balances[i] === 0n) continue;
    const label       = outs[i - 1] ?? `Outcome ${i}`;
    const sharesHuman = parseFloat((Number(balances[i]) / 1e18).toFixed(4));
    const priceStr    = buyPrices ? `  ·  ${pct(buyPrices[i])}%` : "";
    held.push({ outcome: i, label, shares: sharesHuman, priceStr });
  }

  if (held.length === 0) {
    console.log("🎯  No shares held in this market.\n");
  } else {
    console.log("🎯  Shares held");
    const maxLabel = Math.max(...held.map(h => h.label.length));
    held.forEach((h, idx) => {
      const icon   = medals[idx] ?? "   ";
      const padded = h.label.padEnd(maxLabel);
      console.log(`${icon}  [${h.outcome}] ${padded}   ${h.shares} shares${h.priceStr}`);
    });
    console.log("");
  }

  return { netCost, totalBuys, totalSells, held };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(e => { console.error(e.message); process.exit(1); });
}
