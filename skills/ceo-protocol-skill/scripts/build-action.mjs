#!/usr/bin/env node
/**
 * Build CEOVault Action structs for proposals.
 *
 * CEOVault validates actions at proposal time and execution time:
 * 1. value must be 0 (no native MON)
 * 2. USDC/$CEO: only approve(spender, amount); spender must be whitelisted
 * 3. Yield vaults: only deposit/mint/withdraw/redeem with receiver/owner = CEOVault
 * 4. Other whitelisted targets: any calldata
 *
 * Usage:
 *   node build-action.mjs approve USDC MORPHO_USDC_VAULT 5000000000
 *   node build-action.mjs deposit MORPHO_USDC_VAULT 5000000000
 *   node build-action.mjs noop
 *   node build-action.mjs --from-json '{"type":"approve","token":"USDC","spender":"MORPHO_USDC_VAULT","amount":"5000000000"}'
 *
 * Output: JSON array of Action objects { target, value, data } (value always 0)
 */

import { encodeFunctionData, parseAbi } from "viem";
import {
  CEO_VAULT,
  USDC,
  CEO_TOKEN,
  MORPHO_USDC_VAULT,
  WHITELISTED_TARGETS,
} from "./ceo-config.mjs";

const ERC20_ABI = parseAbi([
  "function approve(address spender, uint256 amount) returns (bool)",
]);

const ERC4626_ABI = parseAbi([
  "function deposit(uint256 assets, address receiver) returns (uint256)",
  "function mint(uint256 shares, address receiver) returns (uint256)",
  "function withdraw(uint256 assets, address receiver, address owner) returns (uint256)",
  "function redeem(uint256 shares, address receiver, address owner) returns (uint256)",
]);

const TARGET_MAP = {
  USDC,
  CEO_TOKEN,
  MORPHO_USDC_VAULT,
  ...WHITELISTED_TARGETS,
};

/**
 * Build a single Action for CEOVault.
 * @param {object} spec - { type, token?, target?, spender?, amount?, shares?, data? }
 * @returns {{ target: string, value: bigint, data: string }}
 */
export function buildAction(spec) {
  const { type } = spec;
  const value = 0n;

  switch (type) {
    case "approve": {
      const token = resolveAddress(spec.token);
      const spender = resolveAddress(spec.spender);
      const amount = BigInt(spec.amount ?? 0);
      const data = encodeFunctionData({
        abi: ERC20_ABI,
        functionName: "approve",
        args: [spender, amount],
      });
      return { target: token, value, data };
    }

    case "deposit": {
      const vault = resolveAddress(spec.target ?? spec.vault);
      const assets = BigInt(spec.amount ?? spec.assets ?? 0);
      const data = encodeFunctionData({
        abi: ERC4626_ABI,
        functionName: "deposit",
        args: [assets, CEO_VAULT],
      });
      return { target: vault, value, data };
    }

    case "mint": {
      const vault = resolveAddress(spec.target ?? spec.vault);
      const shares = BigInt(spec.shares ?? 0);
      const data = encodeFunctionData({
        abi: ERC4626_ABI,
        functionName: "mint",
        args: [shares, CEO_VAULT],
      });
      return { target: vault, value, data };
    }

    case "withdraw": {
      const vault = resolveAddress(spec.target ?? spec.vault);
      const assets = BigInt(spec.amount ?? spec.assets ?? 0);
      const data = encodeFunctionData({
        abi: ERC4626_ABI,
        functionName: "withdraw",
        args: [assets, CEO_VAULT, CEO_VAULT],
      });
      return { target: vault, value, data };
    }

    case "redeem": {
      const vault = resolveAddress(spec.target ?? spec.vault);
      const shares = BigInt(spec.shares ?? 0);
      const data = encodeFunctionData({
        abi: ERC4626_ABI,
        functionName: "redeem",
        args: [shares, CEO_VAULT, CEO_VAULT],
      });
      return { target: vault, value, data };
    }

    case "custom":
    case "adapter": {
      const target = resolveAddress(spec.target);
      const data = spec.data?.startsWith("0x")
        ? spec.data
        : `0x${Buffer.from(spec.data, "hex").toString("hex")}`;
      return { target, value, data };
    }

    default:
      throw new Error(`Unknown action type: ${type}`);
  }
}

function resolveAddress(key) {
  if (typeof key !== "string") throw new Error("Address key must be string");
  const addr = TARGET_MAP[key] ?? (key.startsWith("0x") ? key : null);
  if (!addr) throw new Error(`Unknown address key: ${key}`);
  return addr;
}

/**
 * Build no-op proposal (approve 0 to a yield vault). Useful for "do nothing" epochs.
 */
export function buildNoopActions() {
  return [
    buildAction({
      type: "approve",
      token: "USDC",
      spender: "MORPHO_USDC_VAULT",
      amount: 0,
    }),
  ];
}

/**
 * Build deploy-to-yield actions: approve USDC to vault, then deposit.
 * @param {string|number|bigint} amount - USDC amount (6 decimals)
 * @param {string} [yieldVault] - Yield vault key (default MORPHO_USDC_VAULT)
 */
export function buildDeployActions(amount, yieldVault = "MORPHO_USDC_VAULT") {
  const amt = BigInt(amount);
  return [
    buildAction({
      type: "approve",
      token: "USDC",
      spender: yieldVault,
      amount: amt,
    }),
    buildAction({
      type: "deposit",
      target: yieldVault,
      amount: amt,
    }),
  ];
}

/**
 * Convert actions to format suitable for viem/contract call.
 * CEOVault expects { target, value, data } with value as bigint.
 */
export function toContractFormat(actions) {
  return actions.map((a) => ({
    target: a.target,
    value: BigInt(a.value ?? 0),
    data: typeof a.data === "string" ? a.data : `0x${a.data.toString("hex")}`,
  }));
}

// ── CLI ──

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const t = argv[i];
    if (t === "--from-json" && argv[i + 1]) {
      return { fromJson: argv[i + 1] };
    }
    if (t.startsWith("--")) {
      const k = t.slice(2);
      args[k] = argv[i + 1] ?? true;
      if (argv[i + 1]) i++;
      continue;
    }
    if (!args._) args._ = [];
    args._.push(t);
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv);

  let actions;

  if (args.fromJson) {
    const spec = JSON.parse(args.fromJson);
    actions = Array.isArray(spec) ? spec.map((s) => buildAction(s)) : [buildAction(spec)];
  } else {
    const [cmd, ...rest] = args._ ?? [];

    if (cmd === "noop") {
      actions = buildNoopActions();
    } else if (cmd === "deploy") {
      const amount = rest[0] ?? "0";
      const vault = rest[1] ?? "MORPHO_USDC_VAULT";
      actions = buildDeployActions(amount, vault);
    } else if (cmd === "approve") {
      const [token, spender, amount] = rest;
      actions = [buildAction({ type: "approve", token, spender, amount: amount ?? 0 })];
    } else if (cmd === "deposit") {
      const [vault, amount] = rest;
      actions = [buildAction({ type: "deposit", target: vault, amount: amount ?? 0 })];
    } else if (cmd === "withdraw") {
      const [vault, amount] = rest;
      actions = [buildAction({ type: "withdraw", target: vault, amount: amount ?? 0 })];
    } else if (cmd === "redeem") {
      const [vault, shares] = rest;
      actions = [buildAction({ type: "redeem", target: vault, shares: shares ?? 0 })];
    } else {
      console.error(`Usage:
  node build-action.mjs noop
  node build-action.mjs deploy <amount> [yieldVault]
  node build-action.mjs approve <token> <spender> <amount>
  node build-action.mjs deposit <yieldVault> <amount>
  node build-action.mjs withdraw <yieldVault> <amount>
  node build-action.mjs redeem <yieldVault> <shares>
  node build-action.mjs --from-json '<JSON>'

Examples:
  node build-action.mjs noop
  node build-action.mjs deploy 5000000000
  node build-action.mjs approve USDC MORPHO_USDC_VAULT 5000000000
  node build-action.mjs deposit MORPHO_USDC_VAULT 5000000000`);
      process.exit(1);
    }
  }

  const formatted = toContractFormat(actions);
  console.log(JSON.stringify(formatted, (_, v) => (typeof v === "bigint" ? v.toString() : v), 2));
}

// Only run CLI when executed directly (not when imported)
if (process.argv[1]?.includes("build-action.mjs")) {
  main().catch((err) => {
    console.error(err.message);
    process.exit(1);
  });
}
