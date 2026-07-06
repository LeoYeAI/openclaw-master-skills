#!/usr/bin/env node
// Sell outcome shares in a Precog prediction market.
// Always run quote.mjs first to confirm return with the user.
//
// Usage:
//   node sell.mjs --market <id> --outcome <n> --shares <amount> --min <usdc>
//
// --min is the minimum USDC to accept (e.g. 38 for $38). Slippage defaults to 1%.
// Env: PRIVATE_KEY (required), PRECOG_RPC_URL (optional)
import { fileURLToPath } from "url";
import * as client from "./lib/client.mjs";
import { parseArgs, requireArgs } from "./lib/args.mjs";

export async function main(deps = {}) {
  const _parseArgs   = deps.parseArgs   ?? parseArgs;
  const _requireArgs = deps.requireArgs ?? requireArgs;
  // ── Args ──────────────────────────────────────────────────────────────────
  const a = _parseArgs();
  if (a.network) client.setNetwork(a.network);

  const { multiread, write, getWallet, outcomes, toFP64, toRaw } = { ...client, ...deps };
  _requireArgs(a, ["market", "outcome", "shares", "min"]);

  const marketId = BigInt(a.market);
  const outcome  = parseInt(a.outcome);
  const sharesFP = toFP64(a.shares);
  const slippage = parseFloat(a.slippage ?? "1");

  // ── Account & collateral ──────────────────────────────────────────────────
  const { account, wallet } = getWallet();

  const [colRes, marketRes] = await multiread([
    ["marketCollateralInfo", [marketId]],
    ["markets",              [marketId]],
  ]);
  const [, , colSymbol, colDecimals] = colRes;
  const dec    = Number(colDecimals);
  const minRaw = toRaw((parseFloat(a.min) * (1 - slippage / 100)).toFixed(dec), dec);

  // ── Market outcome label ──────────────────────────────────────────────────
  const [, , , , outcomesRaw] = marketRes;
  const outs  = outcomes(outcomesRaw);
  const label = outs[outcome - 1] ?? `Outcome ${outcome}`;

  console.log(`\nSelling ${a.shares} shares of [${label}] on market ${a.market}`);
  console.log(`Min receive: ${a.min} ${colSymbol} (-${slippage}% slippage)`);
  console.log(`Wallet: ${account.address}\n`);

  // ── Execute sell ──────────────────────────────────────────────────────────
  await write(wallet, account, "marketSell", [marketId, BigInt(outcome), sharesFP, minRaw]);

  console.log(`\n✓ Sold ${a.shares} shares of ${label} on market ${a.market}`);
  return { label, shares: a.shares, market: a.market };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(e => { console.error(e.message); process.exit(1); });
}
