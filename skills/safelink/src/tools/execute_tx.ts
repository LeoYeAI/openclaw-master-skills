import { z } from "zod";
import { validateInput, stripPII } from "../security/input-gate.js";
import { simulateTx } from "../security/simulation.js";
import { scoreRisk } from "../security/risk-scorer.js";
import { ApprovalRequiredError } from "../security/approval.js";
import { createTempSession, destroySession } from "../security/session.js";
import { getMPCWalletClient } from "../wallet/mpc.js";
import { getConfig } from "../utils/config.js";
import { logger } from "../utils/logger.js";

const TxOverrideSchema = z.object({
  to: z.string().regex(/^0x[a-fA-F0-9]{40}$/, "tx.to must be a valid EVM address"),
  data: z.string().regex(/^0x([a-fA-F0-9]{2})*$/, "tx.data must be hex calldata").default("0x"),
  value_wei: z.string().regex(/^\d+$/, "tx.value_wei must be a decimal integer").default("0"),
});

const ExecuteTxSchema = z.object({
  intent_description: z
    .string()
    .min(5, "Intent must be at least 5 characters")
    .max(1000, "Intent too long (max 1000 chars)")
    .transform(stripPII)
    .optional()
    .describe(
      "Plain-English transaction intent. NEVER include private keys, seed phrases, or personal data."
    ),
  tx: TxOverrideSchema
    .optional()
    .describe("Deterministic transaction params. Preferred for production flows."),
  confirmed: z.boolean().optional().default(false),
}).refine((v) => Boolean(v.tx || v.intent_description), {
  message: "Either `tx` or `intent_description` is required",
});

export type ExecuteTxInput = z.infer<typeof ExecuteTxSchema>;

export interface ExecuteTxResult {
  tx_hash: `0x${string}` | null;
  simulation_report: {
    success: boolean;
    revert_reason?: string;
    gas_estimate: string;
  };
  risk_score: number;
  risk_flags: string[];
  status: "broadcast" | "blocked" | "rejected_by_user" | "simulation_failed";
}

interface ParsedTx {
  to: `0x${string}`;
  data: `0x${string}`;
  value: bigint;
}

function parseEthToWei(value: string): bigint {
  const normalized = value.trim();
  if (!/^\d+(\.\d+)?$/.test(normalized)) {
    throw new Error(`Invalid ETH amount: ${value}`);
  }

  const [wholeRaw, fraction = ""] = normalized.split(".");
  const whole = wholeRaw ?? "0";
  if (fraction.length > 18) {
    throw new Error("ETH amount supports up to 18 decimal places");
  }

  const weiWhole = BigInt(whole) * 10n ** 18n;
  const weiFraction = BigInt((fraction + "0".repeat(18)).slice(0, 18));
  return weiWhole + weiFraction;
}

function intentToTransaction(intent: string): ParsedTx {
  const hasTransferVerb = /\b(send|transfer|pay|anchor)\b/i.test(intent);
  if (!hasTransferVerb) {
    throw new Error(
      "Unsupported intent format. Provide `tx` params for deterministic execution."
    );
  }

  const addressMatch = intent.match(/0x[a-fA-F0-9]{40}/);
  const amountMatch = intent.match(/(\d+(?:\.\d+)?)\s*eth/i);
  const amountRaw = amountMatch?.[1] ?? "0";

  return {
    to: (addressMatch?.[0] ?? "0x0000000000000000000000000000000000000000") as `0x${string}`,
    data: "0x",
    value: amountMatch ? parseEthToWei(amountRaw) : 0n,
  };
}

function txInputToTransaction(
  tx: { to: string; data?: string | undefined; value_wei?: string | undefined }
): ParsedTx {
  return {
    to: tx.to as `0x${string}`,
    data: (tx.data ?? "0x") as `0x${string}`,
    value: BigInt(tx.value_wei ?? "0"),
  };
}

export async function safe_execute_tx(rawInput: unknown): Promise<ExecuteTxResult> {
  const input = validateInput(ExecuteTxSchema, rawInput);
  const config = getConfig();
  const session = createTempSession({ tool: "safe_execute_tx" });

  try {
    logger.info({ event: "execute_tx_start", intent: input.intent_description ?? "[tx-override]" });

    const parsedTx = input.tx
      ? txInputToTransaction(input.tx)
      : intentToTransaction(input.intent_description ?? "");

    const simulation = await simulateTx(parsedTx);

    const simulationSummary = {
      success: simulation.success,
      ...(simulation.revertReason !== undefined ? { revert_reason: simulation.revertReason } : {}),
      gas_estimate: simulation.gasEstimate.toString(),
    };

    if (!simulation.success) {
      logger.warn({
        event: "simulation_failed",
        reason: simulation.revertReason,
        intent: input.intent_description ?? "[tx-override]",
      });
      return {
        tx_hash: null,
        simulation_report: simulationSummary,
        risk_score: 100,
        risk_flags: ["SIMULATION_FAILED"],
        status: "simulation_failed",
      };
    }

    const { score, flags, details } = await scoreRisk(simulation);

    logger.info({ event: "risk_scored", score, flags });

    if (score >= config.RISK_APPROVAL_THRESHOLD && !input.confirmed) {
      throw new ApprovalRequiredError({
        action: `Execute transaction: ${input.intent_description ?? "[tx-override]"}`,
        details: simulation,
        riskScore: score,
        riskFlags: flags,
        riskDetails: details,
      });
    } else if (score >= 30 && score < config.RISK_APPROVAL_THRESHOLD) {
      logger.warn({
        event: "medium_risk_auto_proceed",
        score,
        flags,
        intent: input.intent_description ?? "[tx-override]",
      });
    }

    const wallet = await getMPCWalletClient();
    const txHash = await wallet.sendTransaction({
      to: parsedTx.to,
      data: parsedTx.data,
      value: parsedTx.value,
      gas: simulation.gasEstimate > 0n ? simulation.gasEstimate : undefined,
    });

    logger.info({ event: "tx_broadcast", hash: txHash, score });

    return {
      tx_hash: txHash,
      simulation_report: simulationSummary,
      risk_score: score,
      risk_flags: flags,
      status: "broadcast",
    };
  } finally {
    await destroySession(session.id);
  }
}
