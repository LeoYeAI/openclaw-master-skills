#!/usr/bin/env node
/**
 * Build a full CEOVault proposal (actions + proposalURI) for registerProposal.
 *
 * Reads actions from:
 *   - --file <path>  JSON file with array of action specs
 *   - --stdin        JSON from stdin
 *   - --noop         Use no-op actions (approve 0)
 *   - --deploy <amount> [vault]  Deploy USDC to yield vault
 *
 * Output: JSON with { actions, proposalURI, proposalHash } for submit-proposal.mjs
 *
 * Usage:
 *   node build-proposal.mjs --noop --uri "https://example.com/proposal-1"
 *   node build-proposal.mjs --deploy 5000000000 --uri "ipfs://Qm..."
 *   node build-proposal.mjs --file proposal.json --uri "https://..."
 *   echo '[{"type":"approve","token":"USDC","spender":"MORPHO_USDC_VAULT","amount":"0"}]' | node build-proposal.mjs --stdin --uri "https://..."
 */

import { keccak256, encodeAbiParameters, parseAbiParameters } from "viem";
import { readFile } from "node:fs/promises";
import { buildAction, buildNoopActions, buildDeployActions, toContractFormat } from "./build-action.mjs";

const ACTION_ABI = parseAbiParameters("(address target, uint256 value, bytes data)[]");

/**
 * Compute proposalHash = keccak256(abi.encode(actions))
 * Must match at execution time.
 */
export function computeProposalHash(actions) {
  const encoded = encodeAbiParameters(ACTION_ABI, [actions]);
  return keccak256(encoded);
}

/**
 * Build proposal from action specs.
 * @param {Array<object>} specs - Array of action specs for buildAction
 * @param {string} proposalURI - Off-chain URI
 * @returns {{ actions, proposalURI, proposalHash }}
 */
export function buildProposal(specs, proposalURI) {
  const actions = specs.map((s) => buildAction(s));
  const formatted = toContractFormat(actions);
  const proposalHash = computeProposalHash(formatted);
  return { actions: formatted, proposalURI, proposalHash };
}

async function main() {
  const args = parseArgs(process.argv);
  const uri = args.uri ?? args.proposalUri ?? "https://moltiverse.xyz/proposal";

  let actions;

  if (args.noop) {
    actions = buildNoopActions();
  } else if (args.deploy) {
    const amount = args.deploy;
    const vault = args.vault ?? "MORPHO_USDC_VAULT";
    actions = buildDeployActions(amount, vault);
  } else if (args.file) {
    const raw = await readFile(args.file, "utf-8");
    const specs = JSON.parse(raw);
    if (!Array.isArray(specs)) throw new Error("File must contain JSON array of action specs");
    actions = specs.map((s) => buildAction(s));
  } else if (args.stdin) {
    let input = "";
    for await (const chunk of process.stdin) input += chunk;
    const specs = JSON.parse(input || "[]");
    actions = Array.isArray(specs) ? specs.map((s) => buildAction(s)) : [buildAction(specs)];
  } else {
    console.error(`Usage:
  node build-proposal.mjs --noop --uri <proposalURI>
  node build-proposal.mjs --deploy <amount> [--vault MORPHO_USDC_VAULT] --uri <proposalURI>
  node build-proposal.mjs --file <path> --uri <proposalURI>
  node build-proposal.mjs --stdin --uri <proposalURI>

Required: --uri (or --proposalUri) with off-chain proposal description URL`);
    process.exit(1);
  }

  const formatted = toContractFormat(actions);
  const proposalHash = computeProposalHash(formatted);

  const out = {
    actions: formatted.map((a) => ({
      target: a.target,
      value: a.value.toString(),
      data: a.data,
    })),
    proposalURI: uri,
    proposalHash,
  };

  console.log(JSON.stringify(out, null, 2));
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const t = argv[i];
    if (t.startsWith("--")) {
      const k = t.slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      const next = argv[i + 1];
      args[k] = next && !next.startsWith("--") ? next : true;
      if (next && !next.startsWith("--")) i++;
    }
  }
  return args;
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
