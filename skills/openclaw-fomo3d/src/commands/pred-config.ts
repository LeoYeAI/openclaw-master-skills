import { readConfig, getPredictionDiamondAddress } from "../lib/config.js"
import { getPublicClient } from "../lib/client.js"
import { PREDICTION_ABI } from "../lib/contracts.js"
import { output, log } from "../lib/output.js"

// 预测市场全局配置
export async function predConfig(_args: string[]) {
  const config = readConfig()
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const diamond = getPredictionDiamondAddress(config)

  const predConfig = await publicClient.readContract({
    address: diamond, abi: PREDICTION_ABI, functionName: "getPredictionConfig",
  }) as {
    token: string; minBet: bigint; devFeeBps: number; creatorFeeBps: number;
    dividendBps: number; nextMarketId: bigint; paused: boolean; minDuration: bigint
  }

  const data = {
    network: config.network,
    diamond,
    token: predConfig.token,
    minBet: predConfig.minBet.toString(),
    devFeeBps: Number(predConfig.devFeeBps),
    creatorFeeBps: Number(predConfig.creatorFeeBps),
    dividendBps: Number(predConfig.dividendBps),
    nextMarketId: Number(predConfig.nextMarketId),
    totalMarkets: Math.max(0, Number(predConfig.nextMarketId) - 1),
    paused: predConfig.paused,
    minDuration: Number(predConfig.minDuration),
  }

  output(data, (d) => {
    log(`\n=== Prediction Market Config (${d.network}) ===`)
    log(`Diamond:      ${d.diamond}`)
    log(`Token:        ${d.token}`)
    log(`Paused:       ${d.paused}`)
    log(`Min Bet:      ${d.minBet}`)
    log(`Dev Fee:      ${d.devFeeBps / 100}%`)
    log(`Creator Fee:  ${d.creatorFeeBps / 100}%`)
    log(`Dividend:     ${d.dividendBps / 100}%`)
    log(`Total Markets: ${d.totalMarkets}`)
    log(`Min Duration: ${d.minDuration}s`)
    log("")
  })
}
