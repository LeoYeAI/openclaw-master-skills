import { z } from "zod";
import { EvmAddress, validateInput } from "../security/input-gate.js";
import { fetchAgentReputation } from "../registry/reputation.js";
import { getConfig } from "../utils/config.js";

const GetReputationSchema = z.object({
  agent_id: EvmAddress,
  threshold: z.number().min(0).max(100).optional(),
});

export async function get_agent_reputation(rawInput: unknown) {
  const input = validateInput(GetReputationSchema, rawInput);
  const rep = await fetchAgentReputation(input.agent_id as `0x${string}`);
  const threshold = input.threshold ?? getConfig().MIN_REPUTATION_SCORE;

  return {
    agent_id: input.agent_id,
    score: rep.score,
    on_chain_score: rep.onChainScore,
    flags: rep.flags,
    active: rep.active,
    capabilities: rep.capabilities,
    min_rate_usdc: rep.minRateUSDC,
    threshold,
    meets_threshold: rep.score >= threshold,
  };
}

