import { encodeAbiParameters, keccak256, encodePacked } from "viem";
import { getConfig } from "../utils/config.js";
import { RegistryError } from "../utils/errors.js";
import { getMPCWalletClient } from "../wallet/mpc.js";
import { getPublicClient } from "../wallet/provider.js";
import { logger } from "../utils/logger.js";
import type { Policy } from "../security/input-gate.js";

// ── ERC-8004 Registry ABI (minimal) ──────────────────────────────────────────

const REGISTRY_ABI = [
  {
    name: "register",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "capabilities", type: "string[]" },
      { name: "minRate", type: "uint256" },
      { name: "policy", type: "bytes" },
    ],
    outputs: [{ name: "agentId", type: "address" }],
  },
  {
    name: "getAgent",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "agentId", type: "address" }],
    outputs: [
      { name: "owner", type: "address" },
      { name: "capabilities", type: "string[]" },
      { name: "minRate", type: "uint256" },
      { name: "reputation", type: "uint256" },
      { name: "registeredAt", type: "uint256" },
      { name: "active", type: "bool" },
    ],
  },
  {
    name: "updateCapabilities",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [{ name: "capabilities", type: "string[]" }],
    outputs: [],
  },
  {
    name: "deactivate",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [],
    outputs: [],
  },
] as const;

// ── Types ─────────────────────────────────────────────────────────────────────

export interface AgentRecord {
  owner: `0x${string}`;
  capabilities: string[];
  minRateAtomicUSDC: bigint;
  reputationScore: number;
  registeredAt: bigint;
  active: boolean;
}

export interface RegisterAgentParams {
  capabilities: string[];
  minRateUSDC: number;
  policy: Policy;
}

// ── Internal helpers ──────────────────────────────────────────────────────────

function getRegistryAddress(): `0x${string}` {
  const config = getConfig();
  if (!config.ERC8004_REGISTRY_ADDRESS) {
    throw new RegistryError(
      "ERC8004_REGISTRY_ADDRESS not set. Run `pnpm deploy:contracts` first."
    );
  }
  return config.ERC8004_REGISTRY_ADDRESS as `0x${string}`;
}

function encodePolicy(policy: Policy): `0x${string}` {
  return encodeAbiParameters(
    [
      { name: "max_task_seconds", type: "uint256" },
      { name: "require_escrow", type: "bool" },
      { name: "max_rate_usdc", type: "uint256" },
      { name: "auto_approve_below_risk", type: "uint256" },
    ],
    [
      BigInt(policy.max_task_seconds),
      policy.require_escrow,
      BigInt(Math.round(policy.max_rate_usdc * 1_000_000)), // to atomic USDC
      BigInt(policy.auto_approve_below_risk),
    ]
  );
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Register this agent in the ERC-8004 on-chain registry.
 * The agent's address (from MPC wallet) is used as the agentId.
 */
export async function registerAgent(
  params: RegisterAgentParams
): Promise<{ agentId: `0x${string}`; txHash: `0x${string}` }> {
  const registryAddress = getRegistryAddress();
  const wallet = await getMPCWalletClient();
  const minRate = BigInt(Math.round(params.minRateUSDC * 1_000_000));
  const policyBytes = encodePolicy(params.policy);

  // Build calldata
  const selector = keccak256(
    encodePacked(["string"], ["register(string[],uint256,bytes)"])
  ).slice(0, 10);

  const encoded = encodeAbiParameters(
    [
      { name: "capabilities", type: "string[]" },
      { name: "minRate", type: "uint256" },
      { name: "policy", type: "bytes" },
    ],
    [params.capabilities, minRate, policyBytes]
  );
  const calldata = `${selector}${encoded.slice(2)}` as `0x${string}`;

  logger.info({
    event: "registry_register",
    capabilities: params.capabilities,
    minRateUSDC: params.minRateUSDC,
  });

  const txHash = await wallet.sendTransaction({
    to: registryAddress,
    data: calldata,
    value: 0n,
  });

  // Wait for confirmation
  const client = getPublicClient();
  await client.waitForTransactionReceipt({ hash: txHash });

  const agentId = wallet.address;
  logger.info({ event: "registry_registered", agentId, txHash });

  return { agentId, txHash };
}

/**
 * Fetch an agent's full record from the registry.
 */
export async function getAgentRecord(
  agentId: `0x${string}`
): Promise<AgentRecord> {
  const client = getPublicClient();
  const registryAddress = getRegistryAddress();

  const result = await client.readContract({
    address: registryAddress,
    abi: REGISTRY_ABI,
    functionName: "getAgent",
    args: [agentId],
  });

  return {
    owner: result[0],
    capabilities: result[1] as string[],
    minRateAtomicUSDC: result[2],
    reputationScore: Number(result[3]),
    registeredAt: result[4],
    active: result[5],
  };
}

/**
 * Check if an address is registered and active in the registry.
 */
export async function isRegisteredAgent(
  agentId: `0x${string}`
): Promise<boolean> {
  try {
    const record = await getAgentRecord(agentId);
    return record.active;
  } catch {
    return false;
  }
}
