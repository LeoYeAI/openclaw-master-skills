import type { SimulationReport } from "./simulation.js";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface RiskResult {
  /** 0 = no risk, 100 = maximum risk. */
  score: number;
  flags: string[];
  details: Record<string, string>;
}

interface RiskPattern {
  id: string;
  weight: number;
  description: string;
  check: (sim: SimulationReport) => boolean;
}

// ── Known bad addresses ────────────────────────────────────────────────────────
// In production, refresh this list from Chainalysis / TRM Labs / OFAC SDN API.

const BLACKLISTED_ADDRESSES = new Set<string>([
  // Example sanctioned addresses (replace with real OFAC/Chainalysis feed)
  "0x7f268357a8c2552623316e2562d90e642bb538e5", // OpenSea hack
  "0x098b716b8aaf21512996dc57eb0615e2383e2f96", // Tornado Cash deployer
  "0xd882cfc20f52f2599d84b8e8d58c7fb62cfe344b",
  "0x901bb9583b24d97e995513c6778dc6888ab6870e",
]);

const OWNERSHIP_TRANSFERRED_TOPIC =
  "0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0" as const;

const UPGRADE_TOPIC =
  "0xbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b" as const;

// ── Risk patterns ─────────────────────────────────────────────────────────────

const RISK_PATTERNS: RiskPattern[] = [
  {
    id: "UNLIMITED_APPROVAL",
    weight: 40,
    description: "ERC-20 unlimited token approval detected (amount = MaxUint256)",
    check: (sim) => {
      const MAX = BigInt(2 ** 256) - 1n;
      return sim.approvals.some((a) => a.amount === MAX);
    },
  },
  {
    id: "BLACKLISTED_ADDRESS",
    weight: 60,
    description: "Transaction target is on OFAC/community sanction blacklist",
    check: (sim) => BLACKLISTED_ADDRESSES.has(sim.to.toLowerCase()),
  },
  {
    id: "OWNERSHIP_TRANSFER",
    weight: 50,
    description: "Contract ownership transfer detected in event logs",
    check: (sim) =>
      sim.eventLogs.some((e) => e.topic0 === OWNERSHIP_TRANSFERRED_TOPIC),
  },
  {
    id: "CONTRACT_UPGRADE",
    weight: 45,
    description: "Proxy/contract upgrade event detected",
    check: (sim) =>
      sim.eventLogs.some((e) => e.topic0 === UPGRADE_TOPIC),
  },
  {
    id: "SELF_DESTRUCT",
    weight: 80,
    description: "SELFDESTRUCT opcode present in call trace",
    check: (sim) =>
      sim.opcodes.some(
        (op) => op === "SELFDESTRUCT" || op === "SUICIDE"
      ),
  },
  {
    id: "DELEGATECALL_TO_EOA",
    weight: 70,
    description: "DELEGATECALL targeting an externally-owned account",
    check: (sim) => sim.delegateCalls.some((d) => d.targetIsEOA),
  },
  {
    id: "HIGH_GAS",
    weight: 15,
    description: "Unusually high gas estimate (> 500k) — possible complex re-entrant logic",
    check: (sim) => sim.gasEstimate > 500_000n,
  },
  {
    id: "ZERO_VALUE_LARGE_CALLDATA",
    weight: 20,
    description: "Zero-value tx with large calldata — possible phishing or sweep transaction",
    check: (sim) =>
      sim.eventLogs.length === 0 &&
      sim.approvals.length > 0 &&
      sim.approvals.some((a) => a.amount > 1_000_000n), // > 1 USDC
  },
];

// ── Scorer ────────────────────────────────────────────────────────────────────

// Minimum score when only viem eth_call was available (trace patterns are blind).
const VIEM_FALLBACK_FLOOR = 50;

export async function scoreRisk(sim: SimulationReport): Promise<RiskResult> {
  // If simulation failed outright, treat as maximum risk
  if (!sim.success) {
    return {
      score: 100,
      flags: ["SIMULATION_FAILED"],
      details: {
        SIMULATION_FAILED: sim.revertReason ?? "Transaction reverted without reason",
      },
    };
  }

  // CRIT-03: viem fallback strips all trace-based detection.
  // Enforce floor score so user cannot auto-proceed without acknowledgment.
  if (sim.viemFallback) {
    return {
      score: VIEM_FALLBACK_FLOOR,
      flags: ["VIEM_FALLBACK_LIMITED_TRACE"],
      details: {
        VIEM_FALLBACK_LIMITED_TRACE:
          "Tenderly unavailable — SELFDESTRUCT, DELEGATECALL_TO_EOA, UNLIMITED_APPROVAL, " +
          "OWNERSHIP_TRANSFER and CONTRACT_UPGRADE patterns cannot be detected. " +
          "Set TENDERLY_ACCESS_KEY for full trace analysis. " +
          `Floor score ${VIEM_FALLBACK_FLOOR}/100 applied. Confirm manually before proceeding.`,
      },
    };
  }

  const triggeredFlags: string[] = [];
  const details: Record<string, string> = {};
  let score = 0;

  for (const pattern of RISK_PATTERNS) {
    if (pattern.check(sim)) {
      triggeredFlags.push(pattern.id);
      details[pattern.id] = pattern.description;
      score = Math.min(100, score + pattern.weight);
    }
  }

  return { score, flags: triggeredFlags, details };
}

/** Convenience: is this score auto-approvable (below threshold)? */
export function isAutoApprovable(score: number, threshold = 30): boolean {
  return score < threshold;
}

/** Convenience: does this score require human approval? */
export function requiresApproval(score: number, threshold = 70): boolean {
  return score >= threshold;
}
