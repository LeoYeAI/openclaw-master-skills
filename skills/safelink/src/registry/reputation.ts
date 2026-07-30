import { getAgentRecord } from "./erc8004.js";
import { ReputationError } from "../utils/errors.js";
import { getConfig } from "../utils/config.js";
import { logger } from "../utils/logger.js";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ReputationResult {
  /** 0–100. Lower is worse. */
  score: number;
  /** Human-readable reasons for a low score. */
  flags: string[];
  /** Raw on-chain reputation value. */
  onChainScore: number;
  /** Whether the agent is active in the registry. */
  active: boolean;
  capabilities: string[];
  minRateUSDC: number;
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Fetch and evaluate the reputation of a target agent.
 * Combines on-chain registry data with optional off-chain signals.
 */
export async function fetchAgentReputation(
  agentId: `0x${string}`
): Promise<ReputationResult> {
  logger.debug({ event: "reputation_check", agentId });

  let record;
  try {
    record = await getAgentRecord(agentId);
  } catch (err) {
    throw new ReputationError(
      agentId,
      0,
      getConfig().MIN_REPUTATION_SCORE
    );
  }

  const flags: string[] = [];
  let score = record.reputationScore;

  // Apply deductions for observable bad signals
  if (!record.active) {
    flags.push("AGENT_INACTIVE");
    score = 0;
  }

  if (record.capabilities.length === 0) {
    flags.push("NO_CAPABILITIES_DECLARED");
    score = Math.max(0, score - 20);
  }

  // New agent (registered < 7 days ago) gets a trust penalty
  const registeredDaysAgo =
    (Date.now() / 1000 - Number(record.registeredAt)) / 86400;
  if (registeredDaysAgo < 7) {
    flags.push("NEW_AGENT");
    score = Math.max(0, score - 15);
  }

  // Clamp to 0–100
  score = Math.min(100, Math.max(0, score));

  logger.info({
    event: "reputation_result",
    agentId,
    score,
    flags,
    registeredDaysAgo: Math.round(registeredDaysAgo),
  });

  return {
    score,
    flags,
    onChainScore: record.reputationScore,
    active: record.active,
    capabilities: record.capabilities,
    minRateUSDC: Number(record.minRateAtomicUSDC) / 1_000_000,
  };
}

/**
 * Assert that an agent meets the minimum reputation threshold.
 * Throws ReputationError if not.
 */
export async function assertReputation(
  agentId: `0x${string}`,
  threshold?: number
): Promise<ReputationResult> {
  const config = getConfig();
  const minScore = threshold ?? config.MIN_REPUTATION_SCORE;
  const result = await fetchAgentReputation(agentId);

  if (result.score < minScore) {
    throw new ReputationError(agentId, result.score, minScore);
  }

  return result;
}
