#!/usr/bin/env node
/* eslint-disable no-console */

// Cross-platform prerequisite checker for auto trading.
// - Works on Linux/macOS/Windows (Node.js required).
// - MUST NOT print secret values.

const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const requiredKeys = [
  "HYPERLIQUID_WALLET_ADDRESS",
  "BLOCKBEATS_API_KEY",
];

function getEnvPath() {
  const baseStateDir = process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), ".openclaw");
  const stateDir = path.join(baseStateDir, ".1m-trade");
  return path.join(stateDir, ".env");
}

function trim(s) {
  return (s ?? "").trim();
}

function stripSurroundingQuotes(s) {
  const v = trim(s);
  if (v.length >= 2) {
    const first = v[0];
    const last = v[v.length - 1];
    if ((first === `"` && last === `"`) || (first === `'` && last === `'`)) {
      return v.slice(1, -1);
    }
  }
  return v;
}

function readDotenvValue(fileContent, key) {
  // Supports:
  //   KEY=value
  //   export KEY=value
  // Ignores comments/blank lines.
  // "Last assignment wins".
  let value = "";
  const lines = fileContent.split(/\r?\n/);
  for (const raw of lines) {
    let line = trim(raw);
    if (!line || line.startsWith("#")) continue;

    if (line.startsWith("export ")) {
      line = trim(line.slice("export ".length));
    }

    if (!line.startsWith(`${key}=`)) continue;
    value = stripSurroundingQuotes(line.slice(`${key}=`.length));
  }
  return value;
}

function hasCommand(cmd) {
  const probe = process.platform === "win32" ? "where" : "which";
  const out = spawnSync(probe, [cmd], { stdio: "pipe" });
  return out.status === 0;
}

function main() {
  const missingBins = [];
  if (!hasCommand("node")) missingBins.push("node");
  if (!hasCommand("hl1m")) missingBins.push("hl1m");
  if (!hasCommand("openclaw")) missingBins.push("openclaw");
  if (!hasCommand("curl")) missingBins.push("curl");

  if (missingBins.length > 0) {
    console.error("❌ Auto-trading cannot be enabled: required binaries are missing.");
    console.error(`   Missing: ${missingBins.join(" ")}`);
    console.error("");
    if (missingBins.includes("hl1m")) {
      console.error("Next step (1m-trade CLI):");
      console.error("- Install pipx if needed: `python3 -m pip install --user pipx`");
      console.error("- Install CLI: `pipx install 1m-trade`");
      console.error("- Verify: `hl1m --help`");
      console.error("");
    }
    if (missingBins.includes("openclaw")) {
      console.error("Next step (OpenClaw CLI):");
      console.error("- Install/enable `openclaw` CLI and ensure it is in PATH.");
      console.error("- Verify: `openclaw --help`");
      console.error("");
    }
    if (missingBins.includes("curl")) {
      console.error("Next step (curl):");
      console.error("- Install curl and ensure it is in PATH.");
      console.error("");
    }
    console.error("After fixing missing binaries, re-run: `node auto_check.js`");
    process.exit(1);
  }

  const envPath = getEnvPath();

  let content = "";
  if (fs.existsSync(envPath) && fs.statSync(envPath).isFile()) {
    content = fs.readFileSync(envPath, "utf8");
  }

  const missing = [];
  for (const k of requiredKeys) {
    const v = readDotenvValue(content, k);
    if (!v) missing.push(k);
  }

  // Encrypted private key is required; plaintext key must not be used.
  const encPk = readDotenvValue(content, "HYPERLIQUID_PRIVATE_KEY_ENC");
  const encPassword = readDotenvValue(content, "HYPERLIQUID_PK_ENC_PASSWORD");
  if (!encPk) missing.push("HYPERLIQUID_PRIVATE_KEY_ENC");
  if (!encPassword) missing.push("HYPERLIQUID_PK_ENC_PASSWORD");

  const plainPk = readDotenvValue(content, "HYPERLIQUID_PRIVATE_KEY");
  if (plainPk) {
    console.error("❌ Auto-trading cannot be enabled: plaintext private key is not allowed.");
    console.error("   Found: HYPERLIQUID_PRIVATE_KEY");
    console.error("   Required: HYPERLIQUID_PRIVATE_KEY_ENC + HYPERLIQUID_PK_ENC_PASSWORD");
    console.error("");
    console.error("Next step:");
    console.error("- Remove `HYPERLIQUID_PRIVATE_KEY` from the .env file.");
    console.error("- Keep only encrypted key fields and wallet address.");
    process.exit(1);
  }

  if (missing.length > 0) {
    console.error("❌ Auto-trading cannot be enabled: required .env values are missing or empty.");
    console.error(`   Missing: ${missing.join(" ")}`);
    console.error("");

    const missingSet = new Set(missing);
    const missingBlockbeats = missingSet.has("BLOCKBEATS_API_KEY");
    const missingHlPk = missingSet.has("HYPERLIQUID_PRIVATE_KEY_ENC") || missingSet.has("HYPERLIQUID_PK_ENC_PASSWORD");
    const missingHlAddr = missingSet.has("HYPERLIQUID_WALLET_ADDRESS");

    if (missingBlockbeats) {
      console.error("Next step (BlockBeats API key):");
      console.error("- Follow the instructions in `skills/1m-trade-news/SKILL.md` → \"Get an API key\" to fetch and write `BLOCKBEATS_API_KEY` into the same .env file.");
      console.error("- Do NOT paste API keys into chat.");
      console.error("");
    }

    if (missingHlPk || missingHlAddr) {
      console.error("Next step (Hyperliquid wallet):");
      console.error("- Create/manage wallet in the browser: https://www.1m-trade.com");
      console.error("- Then initialize the CLI with `hl1m init-wallet` so it persists an encrypted private key (HYPERLIQUID_PRIVATE_KEY_ENC) and the corresponding password (HYPERLIQUID_PK_ENC_PASSWORD), plus HYPERLIQUID_WALLET_ADDRESS.");
      console.error("- Command (run locally; use proxy/API private key — never the main wallet key): `hl1m init-wallet --address <0x...> --pri_key <0x...>`");
      console.error("- Do NOT paste private keys into chat.");
      console.error("");
    }

    console.error("After fixing the missing values, re-run: `node auto_check.js`");
    process.exit(1);
  }

  console.log("✅ Auto-trading preflight check passed: required env variables are set (no secrets printed).");
  process.exit(0);
}

main();

