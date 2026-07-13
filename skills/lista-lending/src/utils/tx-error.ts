import type { StepParam } from "@lista-dao/moolah-lending-sdk";
import type { TxResult } from "../types.js";

interface WalletConnectResponse {
  status?: string;
  txHash?: string;
  error?: string;
  reason?: string;
  revertReason?: string;
}

interface ExecSyncErrorLike {
  message?: string;
  stdout?: string | Buffer;
  stderr?: string | Buffer;
  output?: Array<string | Buffer | null | undefined>;
}

function toText(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value;
  if (value instanceof Buffer) return value.toString("utf-8");
  return String(value);
}

function parseJsonLines(text: string): WalletConnectResponse[] {
  const responses: WalletConnectResponse[] = [];
  for (const raw of text.split("\n")) {
    const line = raw.trim();
    if (!line.startsWith("{") || !line.endsWith("}")) continue;
    try {
      responses.push(JSON.parse(line) as WalletConnectResponse);
    } catch {
      // Ignore non-JSON lines.
    }
  }
  return responses;
}

function extractWalletConnectResponses(err: unknown): WalletConnectResponse[] {
  const e = err as ExecSyncErrorLike;
  const chunks = [
    toText(e.stdout),
    toText(e.stderr),
    ...(Array.isArray(e.output) ? e.output.map((item) => toText(item)) : []),
  ].filter(Boolean);

  const responses: WalletConnectResponse[] = [];
  for (const chunk of chunks) {
    responses.push(...parseJsonLines(chunk));
  }
  return responses;
}

function extractRevertReason(value: string): string {
  const normalize = (reason: string): string => {
    const cleaned = reason.replace(/\.$/, "").trim();
    const hexSuffix = cleaned.match(/^(.*?):\s*0x[0-9a-fA-F]+$/);
    if (hexSuffix?.[1]) {
      return hexSuffix[1].trim();
    }
    return cleaned;
  };

  const withReasonMatch = value.match(/with reason:\s*([^\n]+)/i);
  if (withReasonMatch?.[1]) {
    return normalize(withReasonMatch[1]);
  }
  const revertedMatch = value.match(/execution reverted:?\s*([^\n]+)/i);
  if (revertedMatch?.[1]) {
    return normalize(revertedMatch[1]);
  }
  return normalize(value);
}

export function mapWalletConnectResponse(
  response: WalletConnectResponse,
  step: StepParam["step"],
  explorerUrl?: string
): TxResult {
  if (response.status === "sent") {
    if (!response.txHash) {
      return {
        status: "error",
        reason: "wallet_connect_missing_tx_hash",
        step,
      };
    }
    return {
      status: "sent",
      txHash: response.txHash,
      explorer: explorerUrl,
      step,
    };
  }

  if (response.status === "rejected") {
    return {
      status: "rejected",
      reason: "user_rejected",
      step,
    };
  }

  return {
    status: "error",
    reason: response.error || "Unknown error",
    step,
  };
}

export function mapExecutionError(
  err: unknown,
  step: StepParam["step"]
): TxResult {
  const responses = extractWalletConnectResponses(err);
  const simulationFailed = responses.find((r) => r.status === "simulation_failed");
  if (simulationFailed) {
    const rawReason =
      simulationFailed.revertReason ||
      simulationFailed.error ||
      simulationFailed.reason ||
      "Transaction simulation failed";
    return {
      status: "reverted",
      reason: extractRevertReason(rawReason),
      step,
    };
  }

  const rejected = responses.find((r) => r.status === "rejected");
  if (rejected) {
    return {
      status: "rejected",
      reason: "user_rejected",
      step,
    };
  }

  const message = (err as Error)?.message || String(err);

  // Check for user rejection
  if (message.includes("User rejected") || message.includes("rejected")) {
    return {
      status: "rejected",
      reason: "user_rejected",
      step,
    };
  }

  // Check for contract revert
  if (message.includes("revert") || message.includes("execution reverted")) {
    const revertMatch = message.match(/reason="([^"]+)"/);
    return {
      status: "reverted",
      reason: revertMatch ? revertMatch[1] : "Contract execution reverted",
      step,
    };
  }

  // Check for insufficient funds
  if (message.includes("insufficient funds")) {
    return {
      status: "error",
      reason: "insufficient_balance",
      step,
    };
  }

  return {
    status: "error",
    reason: message,
    step,
  };
}
