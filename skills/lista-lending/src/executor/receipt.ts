import { createPublicClient, http } from "viem";
import { bsc, mainnet, type Chain } from "viem/chains";
import { getRpcUrls } from "../config.js";

const CHAIN_TO_VIEM: Record<string, Chain> = {
  "eip155:56": bsc,
  "eip155:1": mainnet,
};

function parseIntEnv(value: string | undefined, fallback: number): number {
  const parsed = Number.parseInt(value || "", 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

const TX_RECEIPT_TIMEOUT_MS = parseIntEnv(
  process.env.LISTA_TX_RECEIPT_TIMEOUT_MS,
  120000
);
const TX_RECEIPT_POLLING_MS = parseIntEnv(
  process.env.LISTA_TX_RECEIPT_POLLING_MS,
  1500
);
const TX_RECEIPT_CONFIRMATIONS = parseIntEnv(
  process.env.LISTA_TX_RECEIPT_CONFIRMATIONS,
  1
);

export interface ReceiptWaitResult {
  ok: boolean;
  reverted?: boolean;
  rpcUrl?: string;
  blockNumber?: string;
  reason?: string;
  attempts?: Array<{ rpcUrl: string; error: string }>;
}

function isTimeoutErrorMessage(message: string): boolean {
  const lower = message.toLowerCase();
  return (
    lower.includes("timeout") ||
    lower.includes("timed out") ||
    lower.includes("deadline") ||
    lower.includes("aborted")
  );
}

export async function waitForTransactionFinality(
  chain: string,
  txHash: string
): Promise<ReceiptWaitResult> {
  const viemChain = CHAIN_TO_VIEM[chain];
  if (!viemChain) {
    return {
      ok: false,
      reason: "tx_receipt_wait_unsupported_chain",
      attempts: [{ rpcUrl: "n/a", error: `Unsupported chain for receipt wait: ${chain}` }],
    };
  }

  const rpcUrls = getRpcUrls(chain);
  if (rpcUrls.length === 0) {
    return {
      ok: false,
      reason: "tx_receipt_wait_no_rpc_candidates",
      attempts: [{ rpcUrl: "n/a", error: `No RPC candidates configured for ${chain}` }],
    };
  }

  const attempts: Array<{ rpcUrl: string; error: string }> = [];
  let timeoutDetected = false;
  for (const rpcUrl of rpcUrls) {
    const client = createPublicClient({
      chain: viemChain,
      transport: http(rpcUrl, {
        timeout: Math.max(1000, TX_RECEIPT_TIMEOUT_MS),
        retryCount: 1,
        retryDelay: 250,
      }),
    });

    try {
      const receipt = await client.waitForTransactionReceipt({
        hash: txHash as `0x${string}`,
        confirmations: Math.max(1, TX_RECEIPT_CONFIRMATIONS),
        timeout: Math.max(1000, TX_RECEIPT_TIMEOUT_MS),
        pollingInterval: Math.max(250, TX_RECEIPT_POLLING_MS),
      });

      return {
        ok: true,
        reverted: receipt.status === "reverted",
        rpcUrl,
        blockNumber: receipt.blockNumber.toString(),
      };
    } catch (err) {
      const message = (err as Error).message || String(err);
      attempts.push({ rpcUrl, error: message });
      if (isTimeoutErrorMessage(message)) {
        timeoutDetected = true;
      }
    }
  }

  return {
    ok: false,
    reason: timeoutDetected
      ? "tx_submitted_pending_confirmation"
      : "tx_submitted_receipt_unavailable",
    attempts,
  };
}
