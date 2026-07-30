import { createPublicClient, http, type TransactionRequest } from "viem";
import { baseSepolia, base } from "viem/chains";
import { getConfig } from "../utils/config.js";
import { logger } from "../utils/logger.js";
import { SimulationError } from "../utils/errors.js";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ApprovalEvent {
  owner: `0x${string}`;
  spender: `0x${string}`;
  amount: bigint;
  token: `0x${string}`;
}

export interface DelegateCall {
  from: `0x${string}`;
  to: `0x${string}`;
  targetIsEOA: boolean;
}

export interface EventLog {
  address: `0x${string}`;
  topic0: `0x${string}`;
  data: `0x${string}`;
}

export interface SimulationReport {
  success: boolean;
  revertReason?: string;
  gasEstimate: bigint;
  /** Address called by the tx */
  to: `0x${string}`;
  /** State changes (balance diffs, storage diffs) */
  stateDiff: Record<string, unknown>;
  /** ERC-20 approval events decoded from logs */
  approvals: ApprovalEvent[];
  /** DELEGATECALL entries in the call trace */
  delegateCalls: DelegateCall[];
  /** Raw decoded event logs */
  eventLogs: EventLog[];
  /** Opcodes seen in the call trace (for SELFDESTRUCT detection) */
  opcodes: string[];
  /**
   * True when only viem eth_call was used (Tenderly unavailable).
   * All trace-based patterns (SELFDESTRUCT, DELEGATECALL, approvals, events) are BLIND.
   * Risk scorer enforces a minimum floor score when this flag is set.
   */
  viemFallback?: boolean;
  /** Raw Tenderly or viem response */
  raw: unknown;
}

// ── Tenderly simulation ───────────────────────────────────────────────────────

async function simulateWithTenderly(
  tx: TransactionRequest & { to: `0x${string}` }
): Promise<SimulationReport> {
  const config = getConfig();
  if (!config.TENDERLY_ACCESS_KEY || !config.TENDERLY_ACCOUNT_ID) {
    throw new Error("Tenderly credentials not configured");
  }

  const url = `https://api.tenderly.co/api/v1/account/${config.TENDERLY_ACCOUNT_ID}/project/${config.TENDERLY_PROJECT_SLUG}/simulate`;

  const isMainnet = config.BASE_RPC_URL.includes("mainnet");
  const body = {
    network_id: isMainnet ? "8453" : "84532", // Base mainnet or Base Sepolia
    from: tx.from ?? "0x0000000000000000000000000000000000000001",
    to: tx.to,
    input: tx.data ?? "0x",
    value: tx.value?.toString() ?? "0",
    gas: 2_000_000,
    save: false,
    save_if_fails: false,
    simulation_type: "full",
  };

  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Access-Key": config.TENDERLY_ACCESS_KEY,
    },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(15_000), // 15s — don't block tx pipeline
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new SimulationError(`Tenderly API error ${resp.status}: ${text}`);
  }

  const data = (await resp.json()) as {
    transaction: {
      status: boolean;
      error_message?: string;
      gas_used: number;
      call_trace?: { calls?: unknown[]; opcodes?: string[] };
    };
    contracts?: unknown[];
    logs?: Array<{ name: string; inputs: unknown[]; raw: { address: string; topics: string[]; data: string } }>;
  };

  const tx_result = data.transaction;

  // Extract approval events (ERC-20 Approval topic)
  const APPROVAL_TOPIC = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925";
  const approvals: ApprovalEvent[] = [];
  const eventLogs: EventLog[] = [];

  for (const log of data.logs ?? []) {
    const raw = log.raw;
    const topic0 = raw.topics[0] as `0x${string}` | undefined;
    if (!topic0) continue;

    eventLogs.push({
      address: raw.address as `0x${string}`,
      topic0,
      data: raw.data as `0x${string}`,
    });

    if (topic0 === APPROVAL_TOPIC && raw.topics.length === 3) {
      approvals.push({
        owner: `0x${raw.topics[1]?.slice(26)}` as `0x${string}`,
        spender: `0x${raw.topics[2]?.slice(26)}` as `0x${string}`,
        amount: BigInt(raw.data),
        token: raw.address as `0x${string}`,
      });
    }
  }

  return {
    success: tx_result.status,
    ...(tx_result.error_message !== undefined ? { revertReason: tx_result.error_message } : {}),
    gasEstimate: BigInt(tx_result.gas_used),
    to: tx.to,
    stateDiff: {},
    approvals,
    delegateCalls: [],
    eventLogs,
    opcodes: tx_result.call_trace?.opcodes ?? [],
    raw: data,
  };
}

// ── viem fallback simulation ──────────────────────────────────────────────────

async function simulateWithViem(
  tx: TransactionRequest & { to: `0x${string}` }
): Promise<SimulationReport> {
  const config = getConfig();
  const isMainnet = config.BASE_RPC_URL.includes("mainnet");
  const client = createPublicClient({
    chain: isMainnet ? base : baseSepolia,
    transport: http(config.BASE_RPC_URL),
  });

  try {
    const result = await client.call({
      to: tx.to,
      data: tx.data,
      value: tx.value,
    });

    // Estimate gas separately
    const gasEstimate = await client.estimateGas({
      to: tx.to,
      data: tx.data,
      value: tx.value,
    });

    return {
      success: true,
      gasEstimate,
      to: tx.to,
      stateDiff: {},
      approvals: [],
      delegateCalls: [],
      eventLogs: [],
      opcodes: [],
      viemFallback: true, // CRIT-03: flag so risk-scorer applies floor score
      raw: { returnData: result.data },
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      success: false,
      revertReason: message,
      gasEstimate: 0n,
      to: tx.to,
      stateDiff: {},
      approvals: [],
      delegateCalls: [],
      eventLogs: [],
      opcodes: [],
      viemFallback: true,
      raw: { error: message },
    };
  }
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Simulate a transaction off-chain before any signing occurs.
 * Prefers Tenderly (richer trace) → falls back to viem eth_call.
 */
export async function simulateTx(
  tx: TransactionRequest & { to: `0x${string}` }
): Promise<SimulationReport> {
  const config = getConfig();

  logger.debug({ event: "simulation_start", to: tx.to });

  if (config.TENDERLY_ACCESS_KEY && config.TENDERLY_ACCOUNT_ID) {
    try {
      const report = await simulateWithTenderly(tx);
      logger.debug({ event: "simulation_complete", provider: "tenderly", success: report.success });
      return report;
    } catch (err) {
      logger.warn({
        event: "tenderly_fallback",
        reason: err instanceof Error ? err.message : String(err),
      });
    }
  }

  // Fallback to viem
  const report = await simulateWithViem(tx);
  logger.debug({ event: "simulation_complete", provider: "viem", success: report.success });
  return report;
}
