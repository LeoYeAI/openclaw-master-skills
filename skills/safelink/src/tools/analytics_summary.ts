import { z } from "zod";
import { validateInput } from "../security/input-gate.js";
import { getHireSummary } from "../analytics/store.js";

const AgentAnalyticsSummarySchema = z.object({
  period_days: z.number().int().min(1).max(365).optional().default(7),
});

export async function agent_analytics_summary(rawInput: unknown) {
  const input = validateInput(AgentAnalyticsSummarySchema, rawInput);
  const summary = await getHireSummary(input.period_days);

  const markdown = [
    `# SafeLink Weekly Analytics`,
    ``,
    `- Period: ${summary.period_days} days`,
    `- Total hires: ${summary.total_hires}`,
    `- Completed: ${summary.completed}`,
    `- Refunded: ${summary.refunded}`,
    `- Failed: ${summary.failed}`,
    `- Success rate: ${(summary.success_rate * 100).toFixed(2)}%`,
    `- Total spend: ${summary.total_spent_usdc} USDC`,
    `- Avg spend per hire: ${summary.avg_spent_usdc} USDC`,
    ``,
    `## Top Targets`,
    ...summary.top_targets.map((t) => `- ${t.target_id}: ${t.count}`),
  ].join("\n");

  return {
    summary,
    markdown,
  };
}

