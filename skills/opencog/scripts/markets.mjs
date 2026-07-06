#!/usr/bin/env node
// List Precog prediction markets.
//
// Usage:
//   node markets.mjs           # active markets only, with predictions
//   node markets.mjs --all     # all markets (titles only, no prices)
//
// Env: PRECOG_RPC_URL (optional)
import { fileURLToPath } from "url";
import * as client from "./lib/client.mjs";
import { parseArgs } from "./lib/args.mjs";

export async function main(deps = {}) {
  const _parseArgs = deps.parseArgs ?? parseArgs;
  const a = _parseArgs();
  if (a.network) client.setNetwork(a.network);

  const { read, multiread, outcomes, pct, status, date } = { ...client, ...deps };
  const total = await read("createdMarkets");
  if (total === 0n) { console.log("No markets found."); return []; }

  const showAll = "all" in a;
  const result  = [];

  // Batch fetch all markets in one call
  const marketResults = await multiread(
    Array.from({ length: Number(total) }, (_, i) => ["markets", [BigInt(i)]])
  );

  // ── --all: list every market with status, no prices ───────────────────────
  if (showAll) {
    console.log(`\nAll Markets (${total})\n`);
    for (let i = 0; i < marketResults.length; i++) {
      const [question, , , , , , , , , endTs] = marketResults[i];
      const s = status(endTs);
      console.log(`  [${i}]  ${question}  [${s}]`);
      result.push({ id: i, question, status: s });
    }
  } else {
    // ── Default: active markets with leading prediction and token ─────────────
    const activeIds = [];
    for (let i = 0; i < marketResults.length; i++) {
      if (status(marketResults[i][9]) === "active") activeIds.push(i);
    }

    if (activeIds.length === 0) {
      console.log("\nNo active markets.\n");
      return result;
    }

    // Batch fetch prices + collateral for all active markets in one call
    const priceAndColResults = await multiread([
      ...activeIds.map(i => ["marketPrices",         [BigInt(i)]]),
      ...activeIds.map(i => ["marketCollateralInfo",  [BigInt(i)]]),
    ], { allowFailure: true });

    const pricesArr = priceAndColResults.slice(0, activeIds.length);
    const colArr    = priceAndColResults.slice(activeIds.length);

    const active = [];
    for (let j = 0; j < activeIds.length; j++) {
      const id     = activeIds[j];
      const market = marketResults[id];
      const [question, , , , outcomesRaw, , , , , endTs] = market;

      const rawOuts = outcomes(outcomesRaw);
      const outs = (rawOuts.length === 1 && rawOuts[0].includes(","))
        ? rawOuts[0].split(",").map(s => s.trim()).filter(Boolean)
        : rawOuts;

      let prediction = null;
      const prRes = pricesArr[j];
      if (prRes.status === "success") {
        const buyPrices = prRes.result[0];
        let bestIdx = 1;
        for (let k = 2; k <= outs.length; k++) {
          if (buyPrices[k] > buyPrices[bestIdx]) bestIdx = k;
        }
        prediction = { label: outs[bestIdx - 1], pct: pct(buyPrices[bestIdx]) };
      }

      let token = null;
      const coRes = colArr[j];
      if (coRes.status === "success") {
        token = coRes.result[2];
      }

      active.push({ id, question, endTs, outs, prediction, token });
    }

    console.log(`\nActive Markets (${active.length})\n`);
    for (const m of active) {
      const tok = m.token ? `  💰 ${m.token}` : "";
      console.log(`[${m.id}] ${m.question}`);
      if (m.prediction) {
        console.log(`    📈 ${m.prediction.label}  ${m.prediction.pct}%${tok}  📅 ${date(m.endTs)}`);
      } else {
        console.log(`    📅 ${date(m.endTs)}`);
      }
      console.log("");
      result.push(m);
    }
  }

  if (showAll) console.log("");
  return result;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(e => { console.error(e.message); process.exit(1); });
}
