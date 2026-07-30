import { z } from "zod";
import { EvmAddress, validateInput } from "../security/input-gate.js";
import { getAgentAddress } from "../wallet/mpc.js";
import { getAgentRecord } from "../registry/erc8004.js";
import { fetchAgentReputation } from "../registry/reputation.js";
import { getHireSummary } from "../analytics/store.js";

const GenerateAgentCardSchema = z.object({
  agent_id: EvmAddress.optional(),
  include_markdown: z.boolean().optional().default(true),
});

export async function generate_agent_card(rawInput: unknown) {
  const input = validateInput(GenerateAgentCardSchema, rawInput);
  const agentId = (input.agent_id as `0x${string}` | undefined) ?? (await getAgentAddress());
  const [record, rep, analytics] = await Promise.all([
    getAgentRecord(agentId),
    fetchAgentReputation(agentId),
    getHireSummary(30),
  ]);

  const card = {
    version: "1.0",
    agent_id: agentId,
    owner: record.owner,
    active: record.active,
    capabilities: record.capabilities,
    min_rate_usdc: Number(record.minRateAtomicUSDC) / 1_000_000,
    reputation: {
      score: rep.score,
      on_chain_score: rep.onChainScore,
      flags: rep.flags,
    },
    analytics_30d: {
      total_hires: analytics.total_hires,
      success_rate: analytics.success_rate,
      total_spent_usdc: analytics.total_spent_usdc,
    },
  };

  const markdown = [
    `# SafeLink Agent Card`,
    ``,
    `- Agent ID: \`${card.agent_id}\``,
    `- Active: \`${card.active}\``,
    `- Reputation: \`${card.reputation.score}/100\``,
    `- Min Rate: \`${card.min_rate_usdc} USDC\``,
    `- Capabilities: ${card.capabilities.join(", ") || "none"}`,
    ``,
    `## 30d Activity`,
    `- Total hires: ${card.analytics_30d.total_hires}`,
    `- Success rate: ${(card.analytics_30d.success_rate * 100).toFixed(2)}%`,
    `- Total spend: ${card.analytics_30d.total_spent_usdc} USDC`,
  ].join("\n");

  return {
    card_json: card,
    ...(input.include_markdown ? { card_markdown: markdown } : {}),
  };
}

