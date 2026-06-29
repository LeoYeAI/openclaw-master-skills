#!/usr/bin/env node
/**
 * Submit a CEOVault proposal onchain via registerProposal(actions, proposalURI).
 *
 * Prerequisites:
 *   - Agent must be registered (registerAgent)
 *   - Voting must be open (isVotingOpen() == true)
 *   - Agent must not have proposed this epoch (s_hasProposed(epoch, agent) == false)
 *   - Max 10 proposals per epoch
 *
 * Env: MONAD_RPC_URL, AGENT_PRIVATE_KEY
 *
 * Usage:
 *   node submit-proposal.mjs --file proposal.json
 *   node build-proposal.mjs --noop --uri "https://..." | node submit-proposal.mjs --stdin
 *   node submit-proposal.mjs --noop --uri "https://..."
 *   node submit-proposal.mjs --deploy 5000000000 --uri "https://..."
 *
 * Options:
 *   --dry-run    Simulate only, don't broadcast
 *   --file       Read proposal JSON from file
 *   --stdin      Read proposal JSON from stdin
 *   --noop       Build and submit no-op proposal (use with --uri)
 *   --deploy     Build and submit deploy proposal (use with --uri, optional --vault)
 *   --uri        Proposal URI (required for --noop, --deploy)
 */

import { readFile } from "node:fs/promises";
import { encodeFunctionData } from "viem";
import { CEO_VAULT } from "./ceo-config.mjs";
import { createClients, parseArgs, resolveNetwork } from "./common.mjs";
import { buildNoopActions, buildDeployActions, toContractFormat } from "./build-action.mjs";

const CEO_VAULT_ABI = [
  {
    type: "function",
    name: "registerProposal",
    inputs: [
      {
        name: "actions",
        type: "tuple[]",
        components: [
          { name: "target", type: "address" },
          { name: "value", type: "uint256" },
          { name: "data", type: "bytes" },
        ],
      },
      { name: "proposalURI", type: "string" },
    ],
  },
  { type: "function", name: "isVotingOpen", inputs: [], outputs: [{ type: "bool" }], stateMutability: "view" },
  { type: "function", name: "s_currentEpoch", inputs: [], outputs: [{ type: "uint256" }], stateMutability: "view" },
  {
    type: "function",
    name: "s_hasProposed",
    inputs: [
      { name: "", type: "uint256" },
      { name: "", type: "address" },
    ],
    outputs: [{ type: "bool" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "getProposalCount",
    inputs: [{ name: "epoch", type: "uint256" }],
    outputs: [{ type: "uint256" }],
    stateMutability: "view",
  },
];

async function main() {
  const args = parseArgs(process.argv);
  const network = resolveNetwork(args);
  const { walletClient, publicClient, account } = createClients(network);

  const dryRun = !!(args.dryRun ?? args["dry-run"]);

  let proposal;

  if (args.file) {
    const raw = await readFile(args.file, "utf-8");
    proposal = JSON.parse(raw);
  } else if (args.stdin) {
    let input = "";
    for await (const chunk of process.stdin) input += chunk;
    proposal = JSON.parse(input || "{}");
  } else if (args.noop || args.deploy) {
    const uri = args.uri ?? args.proposalUri;
    if (!uri) {
      console.error("--uri required for --noop and --deploy");
      process.exit(1);
    }
    const actions =
      args.noop
        ? buildNoopActions()
        : buildDeployActions(args.deploy, args.vault ?? "MORPHO_USDC_VAULT");
    proposal = {
      actions: toContractFormat(actions).map((a) => ({
        target: a.target,
        value: a.value.toString(),
        data: a.data,
      })),
      proposalURI: uri,
    };
  } else {
    console.error(`Usage:
  node submit-proposal.mjs --file <proposal.json>
  node submit-proposal.mjs --stdin   # read from stdin
  node submit-proposal.mjs --noop --uri <proposalURI>
  node submit-proposal.mjs --deploy <amount> --uri <proposalURI> [--vault MORPHO_USDC_VAULT]

  node build-proposal.mjs --noop --uri "https://..." | node submit-proposal.mjs --stdin

Options: --dry-run (simulate only)`);
    process.exit(1);
  }

  const { actions: rawActions, proposalURI } = proposal;
  if (!rawActions?.length || !proposalURI) {
    console.error("proposal must have actions[] and proposalURI");
    process.exit(1);
  }

  const actions = rawActions.map((a) => ({
    target: a.target,
    value: BigInt(a.value ?? 0),
    data: a.data,
  }));

  // Pre-flight checks
  const [votingOpen, currentEpoch, hasProposed, proposalCount] = await Promise.all([
    publicClient.readContract({
      address: CEO_VAULT,
      abi: CEO_VAULT_ABI,
      functionName: "isVotingOpen",
    }),
    publicClient.readContract({
      address: CEO_VAULT,
      abi: CEO_VAULT_ABI,
      functionName: "s_currentEpoch",
    }),
    publicClient.readContract({
      address: CEO_VAULT,
      abi: CEO_VAULT_ABI,
      functionName: "s_hasProposed",
      args: [currentEpoch, account.address],
    }),
    publicClient.readContract({
      address: CEO_VAULT,
      abi: CEO_VAULT_ABI,
      functionName: "getProposalCount",
      args: [currentEpoch],
    }),
  ]);

  if (!votingOpen) {
    console.error("Voting period is closed. Cannot submit proposal.");
    process.exit(1);
  }
  if (hasProposed) {
    console.error("Agent has already proposed this epoch.");
    process.exit(1);
  }
  if (proposalCount >= 10) {
    console.error("Max proposals per epoch (10) reached.");
    process.exit(1);
  }

  const data = encodeFunctionData({
    abi: CEO_VAULT_ABI,
    functionName: "registerProposal",
    args: [actions, proposalURI],
  });

  if (dryRun) {
    try {
      await publicClient.call({
        account,
        to: CEO_VAULT,
        data,
      });
      console.log(JSON.stringify({ status: "ok", dryRun: true, message: "Simulation succeeded" }, null, 2));
    } catch (err) {
      console.error("Simulation failed:", err.message);
      process.exit(1);
    }
    return;
  }

  const hash = await walletClient.writeContract({
    address: CEO_VAULT,
    abi: CEO_VAULT_ABI,
    functionName: "registerProposal",
    args: [actions, proposalURI],
    account,
  });

  const receipt = await publicClient.waitForTransactionReceipt({ hash });
  const proposalId = proposalCount;

  console.log(
    JSON.stringify(
      {
        status: "ok",
        txHash: hash,
        chainId: network.chainId,
        vault: CEO_VAULT,
        epoch: Number(currentEpoch),
        proposalId,
        proposalURI,
      },
      null,
      2
    )
  );
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
