import { readConfig, getPredictionDiamondAddress } from "../lib/config.js"
import { getPublicClient } from "../lib/client.js"
import { PREDICTION_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

const MARKET_STATUS = ["Active", "Closed", "Resolved"] as const
const SIDE_NAMES = ["Yes", "No", "Draw"] as const
const SETTLEMENT_TYPE = ["Oracle", "Optimistic"] as const

// 查看市场详情
export async function predMarket(args: string[]) {
  const idStr = getFlagValue(args, "--id")
  if (!idStr) fatal("Missing --id <marketId>. Usage: fomo3d pred market --id 1")

  const marketId = BigInt(idStr)
  const config = readConfig()
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const diamond = getPredictionDiamondAddress(config)

  const market = await publicClient.readContract({
    address: diamond, abi: PREDICTION_ABI, functionName: "getMarketInfo", args: [marketId],
  }) as {
    marketId: bigint; contentHash: string; creator: string; endTime: bigint;
    status: number; outcome: number; prizePool: bigint;
    totalYesShares: bigint; totalNoShares: bigint; totalDrawShares: bigint;
    totalShares: bigint; totalBets: bigint; totalBetAmount: bigint;
    totalDividendsDistributed: bigint; settlementType: number; drawEnabled: boolean;
    title: string; metadataURI: string
  }

  const now = Math.floor(Date.now() / 1000)
  const endTime = Number(market.endTime)
  const remaining = Math.max(0, endTime - now)

  const data = {
    marketId: Number(market.marketId),
    title: market.title,
    creator: market.creator,
    status: MARKET_STATUS[market.status] ?? "Unknown",
    outcome: market.status === 2 ? SIDE_NAMES[market.outcome] ?? "Unknown" : null,
    settlementType: SETTLEMENT_TYPE[market.settlementType] ?? "Unknown",
    drawEnabled: market.drawEnabled,
    endTime,
    timeRemaining: remaining,
    prizePool: market.prizePool.toString(),
    totalYesShares: market.totalYesShares.toString(),
    totalNoShares: market.totalNoShares.toString(),
    totalDrawShares: market.totalDrawShares.toString(),
    totalShares: market.totalShares.toString(),
    totalBets: Number(market.totalBets),
    totalBetAmount: market.totalBetAmount.toString(),
    totalDividendsDistributed: market.totalDividendsDistributed.toString(),
    metadataURI: market.metadataURI || null,
  }

  output(data, (d) => {
    log(`\n=== Market #${d.marketId} ===`)
    log(`Title:       ${d.title || "(no title)"}`)
    log(`Creator:     ${d.creator}`)
    log(`Status:      ${d.status}${d.outcome ? ` → ${d.outcome}` : ""}`)
    log(`Settlement:  ${d.settlementType}`)
    log(`Draw:        ${d.drawEnabled ? "Enabled" : "Disabled"}`)
    log(`Time Left:   ${d.timeRemaining > 0 ? `${d.timeRemaining}s` : "Ended"}`)
    log(`Prize Pool:  ${d.prizePool}`)
    log(`Yes Shares:  ${d.totalYesShares}`)
    log(`No Shares:   ${d.totalNoShares}`)
    if (d.drawEnabled) log(`Draw Shares: ${d.totalDrawShares}`)
    log(`Total Bets:  ${d.totalBets} (${d.totalBetAmount} tokens)`)
    log("")
  })
}
