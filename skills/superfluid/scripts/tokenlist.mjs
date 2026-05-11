#!/usr/bin/env node
// Superfluid Token List Resolver
// Self-contained — no npm install required. Uses @superfluid-finance/tokenlist
// package for token data.
//
// Usage:
//   bunx -p @superfluid-finance/tokenlist bun tokenlist.mjs by-address <address>
//   bunx -p @superfluid-finance/tokenlist bun tokenlist.mjs by-chain <chain-id> [--super|--underlying]
//   bunx -p @superfluid-finance/tokenlist bun tokenlist.mjs by-symbol <symbol> [--chain-id <chain-id>]
//   bunx -p @superfluid-finance/tokenlist bun tokenlist.mjs super-token <chain-id> <symbol-or-address>
//   bunx -p @superfluid-finance/tokenlist bun tokenlist.mjs stats
//
// Output: JSON to stdout. Errors to stderr.

import { extendedSuperTokenList } from "@superfluid-finance/tokenlist";

const tokens = extendedSuperTokenList.tokens;

function isSuperToken(t) { return t.tags?.includes("supertoken"); }
function isUnderlying(t) { return t.tags?.includes("underlying"); }

function tokenSummary(t) {
  const r = { chainId: t.chainId, address: t.address, name: t.name, symbol: t.symbol, decimals: t.decimals, tags: t.tags || [] };
  if (t.extensions?.superTokenInfo) r.superTokenInfo = t.extensions.superTokenInfo;
  return r;
}

const out = o => console.log(JSON.stringify(o, null, 2));
const [command, ...args] = process.argv.slice(2);

switch (command) {
  case "by-address": {
    if (!args[0]) { console.error("Usage: tokenlist.mjs by-address <address>"); process.exit(1); }
    const addr = args[0].toLowerCase();
    const matches = tokens.filter(t => t.address.toLowerCase() === addr);
    if (!matches.length) { console.error(`No token found with address ${args[0]}`); process.exit(1); }
    out(matches.map(tokenSummary));
    break;
  }

  case "by-chain": {
    if (!args[0]) { console.error("Usage: tokenlist.mjs by-chain <chain-id> [--super|--underlying]"); process.exit(1); }
    const chainId = Number(args[0]);
    if (isNaN(chainId)) { console.error("Error: chain-id must be a number"); process.exit(1); }
    let matches = tokens.filter(t => t.chainId === chainId);
    if (args[1] === "--super") matches = matches.filter(isSuperToken);
    else if (args[1] === "--underlying") matches = matches.filter(isUnderlying);
    if (!matches.length) { console.error(`No tokens found on chain ${chainId}${args[1] ? ` with filter ${args[1]}` : ""}`); process.exit(1); }
    out(matches.map(tokenSummary));
    break;
  }

  case "by-symbol": {
    if (!args[0]) { console.error("Usage: tokenlist.mjs by-symbol <symbol> [--chain-id <id>]"); process.exit(1); }
    const sym = args[0].toLowerCase();
    let matches = tokens.filter(t => t.symbol.toLowerCase() === sym);
    const ci = args.indexOf("--chain-id");
    if (ci !== -1 && args[ci + 1]) matches = matches.filter(t => t.chainId === Number(args[ci + 1]));
    if (!matches.length) { console.error(`No token found with symbol "${args[0]}"`); process.exit(1); }
    out(matches.map(tokenSummary));
    break;
  }

  case "super-token": {
    if (!args[0] || !args[1]) { console.error("Usage: tokenlist.mjs super-token <chain-id> <symbol-or-address>"); process.exit(1); }
    const chainId = Number(args[0]);
    const query = args[1].toLowerCase();
    if (isNaN(chainId)) { console.error("Error: chain-id must be a number"); process.exit(1); }
    const chainTokens = tokens.filter(t => t.chainId === chainId);
    const st = chainTokens.find(t => isSuperToken(t) && (t.symbol.toLowerCase() === query || t.address.toLowerCase() === query));
    if (!st) { console.error(`No Super Token found on chain ${chainId} matching "${args[1]}"`); process.exit(1); }
    const result = { superToken: tokenSummary(st), underlying: null };
    const ua = st.extensions?.superTokenInfo?.underlyingTokenAddress;
    if (ua) {
      const u = chainTokens.find(t => t.address.toLowerCase() === ua.toLowerCase());
      result.underlying = u ? tokenSummary(u) : { address: ua, note: "Not in token list" };
    }
    out(result);
    break;
  }

  case "stats": {
    const chains = [...new Set(tokens.map(t => t.chainId))].sort((a, b) => a - b);
    out({
      totalTokens: tokens.length,
      superTokens: tokens.filter(isSuperToken).length,
      underlyingTokens: tokens.filter(isUnderlying).length,
      chains: chains.map(id => {
        const ct = tokens.filter(t => t.chainId === id);
        return { chainId: id, total: ct.length, superTokens: ct.filter(isSuperToken).length, underlying: ct.filter(isUnderlying).length };
      }),
    });
    break;
  }

  default:
    console.error(`Superfluid Token List Resolver

Commands:
  by-address <address>                         Find token(s) by contract address
  by-chain <chain-id> [--super|--underlying]   List tokens on a network
  by-symbol <symbol> [--chain-id <id>]         Find token(s) by symbol
  super-token <chain-id> <symbol-or-address>   Find Super Token + its underlying
  stats                                        Summary stats of the token list

Examples:
  bunx -p @superfluid-finance/tokenlist bun tokenlist.mjs by-address 0x4ac8bD1bDaE47beeF2D1c6Aa62229509b962Aa0d
  bunx -p @superfluid-finance/tokenlist bun tokenlist.mjs by-chain 10 --super
  bunx -p @superfluid-finance/tokenlist bun tokenlist.mjs by-symbol USDCx --chain-id 10
  bunx -p @superfluid-finance/tokenlist bun tokenlist.mjs super-token 10 USDCx
  bunx -p @superfluid-finance/tokenlist bun tokenlist.mjs stats`);
    process.exit(command ? 1 : 0);
}
