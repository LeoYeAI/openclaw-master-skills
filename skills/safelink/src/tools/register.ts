import { z } from "zod";
import {
  validateInput,
  USDCRate,
  PolicySchema,
  type Policy,
} from "../security/input-gate.js";
import { createTempSession, destroySession } from "../security/session.js";
import { simulateTx } from "../security/simulation.js";
import { scoreRisk } from "../security/risk-scorer.js";
import { requireApproval, ApprovalRequiredError } from "../security/approval.js";
import { registerAgent } from "../registry/erc8004.js";
import { getAgentAddress } from "../wallet/mpc.js";
import { getConfig } from "../utils/config.js";
import { logger } from "../utils/logger.js";
import { toError } from "../utils/errors.js";

// ── Input schema ──────────────────────────────────────────────────────────────

const RegisterSchema = z.object({
  capabilities: z
    .array(z.string().min(1).max(50))
    .min(1, "At least one capability required")
    .max(20, "Maximum 20 capabilities"),
  min_rate: USDCRate.describe("Minimum USDC rate per operation"),
  policy: PolicySchema.optional(),
  confirmed: z.boolean().optional().default(false),
});

export type RegisterInput = z.infer<typeof RegisterSchema>;

// ── Output type ───────────────────────────────────────────────────────────────

export interface RegisterResult {
  agent_id: `0x${string}`;
  tx_hash: `0x${string}`;
  capabilities: string[];
  min_rate_usdc: number;
  registry_address: `0x${string}`;
  network: string;
}

// ── Tool handler ──────────────────────────────────────────────────────────────

export async function safe_register_as_service(
  rawInput: unknown
): Promise<RegisterResult> {
  const input = validateInput(RegisterSchema, rawInput);
  const config = getConfig();
  const policy = (input.policy ?? PolicySchema.parse({})) as Policy;

  const session = createTempSession({ tool: "safe_register_as_service" });

  try {
    logger.info({
      event: "register_start",
      capabilities: input.capabilities,
      min_rate: input.min_rate,
    });

    const agentAddress = await getAgentAddress();
    const registryAddress = config.ERC8004_REGISTRY_ADDRESS;

    if (!registryAddress) {
      throw new Error(
        "ERC8004_REGISTRY_ADDRESS not configured. Run `pnpm deploy:contracts` first."
      );
    }

    // Build actual register() calldata so simulation faithfully models the real tx
    const { encodeAbiParameters, keccak256, encodePacked } = await import("viem");
    const minRate = BigInt(Math.round(input.min_rate * 1_000_000));
    const registerSelector = keccak256(
      encodePacked(["string"], ["register(string[],uint256,bytes)"])
    ).slice(0, 10);
    const registerEncoded = encodeAbiParameters(
      [
        { name: "capabilities", type: "string[]" },
        { name: "minRate", type: "uint256" },
        { name: "policy", type: "bytes" },
      ],
      [input.capabilities, minRate, "0x" as `0x${string}`]
    );
    const registerCalldata = `${registerSelector}${registerEncoded.slice(2)}` as `0x${string}`;

    const simulation = await simulateTx({
      to: registryAddress as `0x${string}`,
      data: registerCalldata,
      value: 0n,
    });

    const { score, flags } = await scoreRisk(simulation);

    if (score >= config.RISK_APPROVAL_THRESHOLD && !input.confirmed) {
      throw new ApprovalRequiredError({
        action: `Register agent ${agentAddress} to ERC-8004 registry`,
        details: simulation,
        riskScore: score,
        riskFlags: flags,
      });
    }

    const { agentId, txHash } = await registerAgent({
      capabilities: input.capabilities,
      minRateUSDC: input.min_rate,
      policy,
    });

    logger.info({ event: "register_complete", agentId, txHash });

    return {
      agent_id: agentId,
      tx_hash: txHash,
      capabilities: input.capabilities,
      min_rate_usdc: input.min_rate,
      registry_address: registryAddress as `0x${string}`,
      network: config.BASE_RPC_URL.includes("sepolia") ? "base-sepolia" : "base-mainnet",
    };
  } finally {
    await destroySession(session.id);
  }
}
