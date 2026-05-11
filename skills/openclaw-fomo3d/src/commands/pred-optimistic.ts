import { readConfig, getPredictionDiamondAddress } from "../lib/config.js"
import { getPublicClient } from "../lib/client.js"
import { PREDICTION_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

const SIDE_NAMES = ["Yes", "No", "Draw"] as const

// 查看乐观预言机配置（提议、争议状态）
export async function predOptimistic(args: string[]) {
  const idStr = getFlagValue(args, "--id")
  if (!idStr) fatal("Missing --id <marketId>")

  const marketId = BigInt(idStr)
  const config = readConfig()
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const diamond = getPredictionDiamondAddress(config)

  const optConfig = await publicClient.readContract({
    address: diamond, abi: PREDICTION_ABI, functionName: "getOptimisticConfig", args: [marketId],
  }) as {
    bondAmount: bigint; challengePeriod: bigint; proposer: string;
    proposedOutcome: number; proposalTime: bigint; hasProposal: boolean;
    disputed: boolean; disputer: string; challengeDeadline: bigint
  }

  const now = Math.floor(Date.now() / 1000)
  const deadline = Number(optConfig.challengeDeadline)
  const challengeRemaining = optConfig.hasProposal ? Math.max(0, deadline - now) : 0

  const data = {
    marketId: Number(marketId),
    bondAmount: optConfig.bondAmount.toString(),
    challengePeriod: Number(optConfig.challengePeriod),
    hasProposal: optConfig.hasProposal,
    proposer: optConfig.hasProposal ? optConfig.proposer : null,
    proposedOutcome: optConfig.hasProposal ? SIDE_NAMES[optConfig.proposedOutcome] ?? "Unknown" : null,
    proposalTime: optConfig.hasProposal ? Number(optConfig.proposalTime) : null,
    disputed: optConfig.disputed,
    disputer: optConfig.disputed ? optConfig.disputer : null,
    challengeDeadline: optConfig.hasProposal ? deadline : null,
    challengeRemaining,
    canFinalize: optConfig.hasProposal && !optConfig.disputed && challengeRemaining === 0,
    canDispute: optConfig.hasProposal && !optConfig.disputed && challengeRemaining > 0,
  }

  output(data, (d) => {
    log(`\n=== Optimistic Config for Market #${d.marketId} ===`)
    log(`Bond Amount:      ${d.bondAmount}`)
    log(`Challenge Period: ${d.challengePeriod}s`)
    if (d.hasProposal) {
      log(`Proposer:         ${d.proposer}`)
      log(`Proposed:         ${d.proposedOutcome}`)
      log(`Challenge Left:   ${d.challengeRemaining}s`)
      if (d.disputed) log(`Disputed by:      ${d.disputer}`)
      if (d.canFinalize) log(`Status:           Ready to finalize`)
      if (d.canDispute) log(`Status:           Open for challenge`)
    } else {
      log(`Status:           No proposal yet`)
    }
    log("")
  })
}
