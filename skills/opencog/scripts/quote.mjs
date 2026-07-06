#!/usr/bin/env node
// Quote the cost to buy or sell outcome shares in a Precog market.
// Always run before buy or sell — show the output to the user and confirm.
//
// Usage:
//   node quote.mjs --market <id> --outcome <n> --shares <amount> [--buy | --sell]
//   node quote.mjs --market <id> --outcome <n> --cost <usdc>     [--buy | --sell]
//   node quote.mjs --market <id> --outcome <n> --price <0.0-1.0> [--buy | --sell]
//
// IMPORTANT — choosing the right flag:
//   User says "buy N shares"                      → --shares N
//   User says "spend $X" / "for $X" / "budget $X" → --cost X
//   User says "reach X%" / "move to X%" /
//             "push to X%" / "target X%"           → --price 0.X   ← DO NOT guess shares manually
//   User says "use all my balance" / "all in"      → --all         ← reads wallet balance automatically
//
// --outcome is 1-based (1 = first outcome, usually YES).
// --buy / --sell show only that side. Omit both to show buy and sell.
// Env: PRECOG_RPC_URL (optional)
import { fileURLToPath } from "url";
import * as client from "./lib/client.mjs";
import { parseArgs, requireArgs } from "./lib/args.mjs";
import { LSLMSR, marketSharesFromCost, marketPriceAfterTrade, getFuturePriceAfterTrade } from "./lib/helper.mjs";

export async function main(deps = {}) {
  const _parseArgs   = deps.parseArgs   ?? parseArgs;
  const _requireArgs = deps.requireArgs ?? requireArgs;
  // ── Args ──────────────────────────────────────────────────────────────────
  const a = _parseArgs();
  if (a.network) client.setNetwork(a.network);

  const { multiread, outcomes, pct, toFP64, fromFP64, fromRaw, tokenBalance, getWallet } = { ...client, ...deps };
  _requireArgs(a, ["market", "outcome"]);

  if (!("shares" in a) && !("cost" in a) && !("price" in a) && !("all" in a)) {
    throw new Error("Provide one of: --shares <n>, --cost <usdc>, --price <0.0-1.0>, --all");
  }

  const showBuy  = !("sell" in a);
  const showSell = !("buy"  in a);

  const marketId = BigInt(a.market);
  const outcome  = parseInt(a.outcome);

  // ── Batch 1: market info, collateral, setup, shares, prices ──────────────
  const [marketRes, colRes, setupRes, sharesRes, pricesRes] = await multiread([
    ["markets",              [marketId]],
    ["marketCollateralInfo", [marketId]],
    ["marketSetupInfo",      [marketId]],
    ["marketSharesInfo",     [marketId]],
    ["marketPrices",         [marketId]],
  ], { allowFailure: true });

  if (marketRes.status  === "failure") throw new Error("Failed to load market");
  if (colRes.status     === "failure") throw new Error("Failed to load collateral info");
  if (setupRes.status   === "failure") throw new Error("Failed to load market setup info");
  if (sharesRes.status  === "failure") throw new Error("Failed to load market shares info");

  const [question, , , , outcomesRaw]  = marketRes.result;
  const [colToken, , colSymbol, colDecimals] = colRes.result;
  const [, alphaFP, , sellFeeFP]       = setupRes.result;
  const [, sharesBalancesFP]           = sharesRes.result;

  const rawOuts = outcomes(outcomesRaw);
  const outcomeList = (rawOuts.length === 1 && rawOuts[0].includes(","))
    ? rawOuts[0].split(",").map(s => s.trim()).filter(Boolean)
    : rawOuts;
  const label = outcomeList[outcome - 1] ?? `Outcome ${outcome}`;

  const alpha    = fromFP64(alphaFP);
  const sellFee  = fromFP64(sellFeeFP);
  const sharesArr = sharesBalancesFP.map(fp => fromFP64(fp)); // keep 1-indexed

  // ── Resolve share count from flag ─────────────────────────────────────────
  let sharesNum;

  if ("all" in a) {
    const { account } = getWallet();
    const balRaw  = await tokenBalance(colToken, account.address);
    const balance = Number(balRaw) / 10 ** Number(colDecimals);
    console.log(`  💰  Wallet balance : ${balance.toFixed(4)} ${colSymbol}`);
    sharesNum = Math.floor(marketSharesFromCost(sharesArr, alpha, outcome, balance));
  } else if ("cost" in a) {
    sharesNum = Math.floor(marketSharesFromCost(sharesArr, alpha, outcome, parseFloat(a.cost)));
  } else if ("price" in a) {
    const outcomesBalances = {};
    for (let j = 0; j < outcomeList.length; j++) {
      outcomesBalances[outcomeList[j]] = sharesArr[j + 1];
    }
    const lslmsr   = LSLMSR.fromState(outcomesBalances, alpha);
    lslmsr.sellFee = sellFee;
    sharesNum = Math.floor(lslmsr.maxSharesFromPrice(label, parseFloat(a.price)));
  } else {
    sharesNum = parseFloat(a.shares);
  }

  if (sharesNum <= 0) {
    console.log("\n❌  Not enough for even 1 share.\n");
    return null;
  }

  // ── Batch 2: on-chain price quotes ────────────────────────────────────────
  const sharesFP  = toFP64(sharesNum);
  const [buyCostFP, sellRetFP] = await multiread([
    ["marketBuyPrice",  [marketId, BigInt(outcome), sharesFP]],
    ["marketSellPrice", [marketId, BigInt(outcome), sharesFP]],
  ]);
  const buyCost   = fromFP64(BigInt(buyCostFP));
  const sellRet   = fromFP64(BigInt(sellRetFP));
  const perShare  = buyCost / sharesNum;

  // ── Local price simulation (future probability after trade) ───────────────
  const futureBuyPrice  = marketPriceAfterTrade(sharesArr, alpha, outcome, sharesNum);
  const futureSellPrice = getFuturePriceAfterTrade(sharesArr, alpha, outcome, -sharesNum);
  const maxReturn       = sharesNum;
  const buyProfit       = maxReturn - buyCost;
  const sellPerShare    = sellRet / sharesNum;

  let prob = "N/A";
  if (pricesRes.status === "success") {
    prob = pct(pricesRes.result[0][outcome]) + "%";
  }

  // ── Output ────────────────────────────────────────────────────────────────
  const hr = "─".repeat(57);

  console.log(`\n📋  Quote — Market ${a.market}: ${question}`);
  console.log(hr);
  console.log(`  🎯  Outcome      : ${label}`);
  console.log(`  🔢  Shares       : ${sharesNum}`);
  console.log(`  📊  Current prob : ${prob}`);

  if (showBuy) {
    console.log(`\n  🛒  Buy ${sharesNum} shares`);
    console.log(`       💵  Cost           : ~${buyCost.toFixed(4)} ${colSymbol}`);
    console.log(`       📏  Price / share  : ${perShare.toFixed(4)} ${colSymbol}`);
    console.log(`       📈  Prob after buy : ${pct(futureBuyPrice)}%  (market moves up ↑)`);
    console.log(`       🏆  Max return     : ${maxReturn.toFixed(4)} ${colSymbol}   (+${buyProfit.toFixed(4)} profit if "${label}" wins)`);
    console.log(`\n  ⚡  Suggested --max for buy  : ${(buyCost * 1.01).toFixed(4)}`);
  }

  if (showSell) {
    console.log(`\n  💸  Sell ${sharesNum} shares`);
    console.log(`       💵  Return         : ~${sellRet.toFixed(4)} ${colSymbol}`);
    console.log(`       📏  Price / share  : ${sellPerShare.toFixed(4)} ${colSymbol}`);
    console.log(`       📉  Prob after sell: ${pct(futureSellPrice)}%  (market moves down ↓)`);
    console.log(`\n  ⚡  Suggested --min for sell : ${(sellRet * 0.99).toFixed(4)}`);
  }

  console.log(`─── Paste ALL lines above verbatim to the user before asking to confirm ───`);
  console.log("");

  return { label, shares: sharesNum, buyCost, sellRet, perShare, prob,
           futureBuyPrice, futureSellPrice, maxReturn, buyProfit, sellPerShare,
           suggestedMax: buyCost * 1.01, suggestedMin: sellRet * 0.99 };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(e => { console.error(e.message); process.exit(1); });
}
