#!/usr/bin/env node
// Wallet setup for Precog prediction market scripts.
//
// Usage:
//   node setup.mjs              # check wallet status, show address + balances
//   node setup.mjs --generate   # generate a new wallet, save to ~/.openclaw/.env
//
// Env: PRECOG_RPC_URL (optional)
import { existsSync, readFileSync, appendFileSync, mkdirSync } from "fs";
import { homedir } from "os";
import { join } from "path";
import { fileURLToPath } from "url";
import { generatePrivateKey, privateKeyToAccount } from "viem/accounts";
import { formatEther } from "viem";
import * as client from "./lib/client.mjs";
import { parseArgs } from "./lib/args.mjs";

const ENV_DIR  = join(homedir(), ".openclaw");
const ENV_FILE = join(ENV_DIR, ".env");

export async function main(deps = {}) {
  const _parseArgs = deps.parseArgs ?? parseArgs;
  const a0 = _parseArgs();
  if (a0.network) client.setNetwork(a0.network);

  const { pub, read, tokenBalance, fromRaw } = { ...client, ...deps };
  const {
    existsSync:     _existsSync     = existsSync,
    readFileSync:   _readFileSync   = readFileSync,
    appendFileSync: _appendFileSync = appendFileSync,
    mkdirSync:      _mkdirSync      = mkdirSync,
    envFile:        _envFile        = ENV_FILE,
    envDir:         _envDir         = ENV_DIR,
    getPrivateKey:  _getPrivateKey  = () => process.env.PRIVATE_KEY,
  } = deps;

  const a = a0;

  // ── Generate ────────────────────────────────────────────────────────────────
  if ("generate" in a) {
    const existingKey = _getPrivateKey();
    if (existingKey) {
      console.error(`Wallet already set: ${privateKeyToAccount(existingKey).address}`);
      console.error("Remove PRIVATE_KEY from ~/.openclaw/.env first.");
      return { error: "already_exists" };
    }
    if (_existsSync(_envFile) && _readFileSync(_envFile, "utf8").includes("PRIVATE_KEY=")) {
      console.error("PRIVATE_KEY already exists in ~/.openclaw/.env. Remove it first.");
      return { error: "already_exists" };
    }

    const pk      = generatePrivateKey();
    const account = privateKeyToAccount(pk);
    _mkdirSync(_envDir, { recursive: true });
    _appendFileSync(_envFile, `\nPRIVATE_KEY=${pk}\n`);

    console.log("✓ Wallet created\n");
    console.log(`  Address: ${account.address}\n`);
    console.log("Send to this address before trading:");
    console.log("  • ETH  — for gas");
    console.log(`  • Token  of the market— for buying shares`);
    console.log("\nPrivate key saved to ~/.openclaw/.env (never printed).");
    return { created: true, address: account.address };
  }

  // ── Status ──────────────────────────────────────────────────────────────────
  const pk = _getPrivateKey();
  if (!pk) {
    console.log("No wallet found.\n");
    console.log("  node setup.mjs --generate   create a new wallet");
    console.log("  or add PRIVATE_KEY=0x... to ~/.openclaw/.env");
    return { error: "no_wallet" };
  }

  const account = privateKeyToAccount(pk.startsWith("0x") ? pk : `0x${pk}`);
  console.log(`Wallet: ${account.address}\n`);

  const ethBal = await pub.getBalance({ address: account.address });
  console.log(`  ETH:  ${Number(formatEther(ethBal)).toFixed(6)} ${ethBal === 0n ? "⚠️  needs gas" : "✓"}`);

  let colInfo = null;
  try {
    const [token, , symbol, decimals] = await read("marketCollateralInfo", [0n]);
    const bal = await tokenBalance(token, account.address);
    console.log(`  ${symbol}: ${fromRaw(bal, Number(decimals))} ${bal === 0n ? "(no funds)" : "✓"}`);
    colInfo = { symbol, balance: bal };
  } catch {
    console.log(`  Collateral: (unavailable — check RPC or contract address)`);
  }

  return { address: account.address, ethBalance: ethBal, collateral: colInfo };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(e => { console.error(e.message); process.exit(1); });
}
