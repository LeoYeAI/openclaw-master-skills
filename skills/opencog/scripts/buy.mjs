#!/usr/bin/env node
// Buy outcome shares in a Precog prediction market.
// Always run quote.mjs first to confirm cost with the user.
//
// Usage:
//   node buy.mjs --market <id> --outcome <n> --shares <amount> --max <usdc>
//
// --max is the maximum USDC to spend (e.g. 40 for $40). Slippage defaults to 1%.
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

  const { multiread, write, getWallet, ensureApproval, outcomes, toFP64, toRaw, MASTER_ADDRESS } =
    { ...client, ...deps };
  _requireArgs(a, ["market", "outcome", "shares", "max"]);

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
  const [colToken, , colSymbol, colDecimals] = colRes;
  const market = marketRes;
  const dec    = Number(colDecimals);
  const maxRaw = toRaw((parseFloat(a.max) * (1 + slippage / 100)).toFixed(dec), dec);

  // ── Market info & guard ───────────────────────────────────────────────────
  const [question, , , , outcomesRaw, , , , , endTs] = market;

  if (Date.now() / 1000 > Number(endTs)) {
    console.error("Market has ended.");
    process.exit(1);
  }

  const outs  = outcomes(outcomesRaw);
  const label = outs[outcome - 1] ?? `Outcome ${outcome}`;

  console.log(`\nBuying ${a.shares} shares of [${label}] on market ${a.market}`);
  console.log(`Max spend: ${a.max} ${colSymbol} (+${slippage}% slippage)`);
  console.log(`Wallet: ${account.address}\n`);

  // ── Approve token spend and execute buy ───────────────────────────────────
  await ensureApproval(wallet, account, colToken, MASTER_ADDRESS, maxRaw);
  await write(wallet, account, "marketBuy", [marketId, BigInt(outcome), sharesFP, maxRaw]);

  console.log(`\n✓ Bought ${a.shares} shares of ${label} on market ${a.market}`);
  return { label, shares: a.shares, market: a.market };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(e => { console.error(e.message); process.exit(1); });
}
