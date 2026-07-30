import { getPublicClient } from "../wallet/provider.js";

// ── USDC contract addresses ───────────────────────────────────────────────────

export const USDC_ADDRESSES = {
  "base-sepolia": "0x036CbD53842c5426634e7929541eC2318f3dCF7e" as `0x${string}`,
  "base-mainnet": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913" as `0x${string}`,
} as const;

// ── Minimal ERC-20 ABI (only what we need) ───────────────────────────────────

const ERC20_ABI = [
  {
    name: "balanceOf",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "account", type: "address" }],
    outputs: [{ name: "", type: "uint256" }],
  },
  {
    name: "allowance",
    type: "function",
    stateMutability: "view",
    inputs: [
      { name: "owner", type: "address" },
      { name: "spender", type: "address" },
    ],
    outputs: [{ name: "", type: "uint256" }],
  },
  {
    name: "approve",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "spender", type: "address" },
      { name: "amount", type: "uint256" },
    ],
    outputs: [{ name: "", type: "bool" }],
  },
] as const;

/** USDC has 6 decimal places (not 18). */
export const USDC_DECIMALS = 6;

/**
 * Convert a human-readable USDC amount to atomic units (6 decimals).
 * Uses string arithmetic to avoid float precision loss (e.g. 0.1 USDC losing cents).
 */
export function toAtomicUSDC(amountDecimal: number): bigint {
  // toFixed gives exact decimal string, avoiding float arithmetic imprecision.
  const str = amountDecimal.toFixed(USDC_DECIMALS); // e.g. "0.050000"
  const [intPart = "0", fracPart = ""] = str.split(".");
  const paddedFrac = fracPart.padEnd(USDC_DECIMALS, "0").slice(0, USDC_DECIMALS);
  return BigInt(intPart + paddedFrac);
}

/** Convert atomic USDC units to human-readable. */
export function fromAtomicUSDC(amount: bigint): number {
  return Number(amount) / 10 ** USDC_DECIMALS;
}

/** Return the USDC contract address for the current network (based on RPC URL). */
export function getUSDCAddress(baseRpcUrl: string): `0x${string}` {
  return baseRpcUrl.includes("mainnet")
    ? USDC_ADDRESSES["base-mainnet"]
    : USDC_ADDRESSES["base-sepolia"];
}

/** Get USDC balance for an address (in atomic units). */
export async function getUSDCBalance(
  address: `0x${string}`,
  network: "base-sepolia" | "base-mainnet" = "base-sepolia"
): Promise<bigint> {
  const client = getPublicClient();
  const balance = await client.readContract({
    address: USDC_ADDRESSES[network],
    abi: ERC20_ABI,
    functionName: "balanceOf",
    args: [address],
  });
  return balance;
}

/** Get USDC allowance for a spender. */
export async function getUSDCAllowance(
  owner: `0x${string}`,
  spender: `0x${string}`,
  network: "base-sepolia" | "base-mainnet" = "base-sepolia"
): Promise<bigint> {
  const client = getPublicClient();
  const allowance = await client.readContract({
    address: USDC_ADDRESSES[network],
    abi: ERC20_ABI,
    functionName: "allowance",
    args: [owner, spender],
  });
  return allowance;
}

/** Build calldata for ERC-20 approve(spender, amount). */
export function buildApproveCalldata(
  spender: `0x${string}`,
  amount: bigint
): `0x${string}` {
  // approve(address,uint256) selector: 0x095ea7b3
  const selector = "095ea7b3";
  const paddedSpender = spender.slice(2).toLowerCase().padStart(64, "0");
  const paddedAmount = amount.toString(16).padStart(64, "0");
  return `0x${selector}${paddedSpender}${paddedAmount}` as `0x${string}`;
}
