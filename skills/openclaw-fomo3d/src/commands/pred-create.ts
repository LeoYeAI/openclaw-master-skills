import type { Address } from "viem"
import { decodeEventLog } from "viem"
import { readConfig, requirePrivateKey, getPredictionDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { PREDICTION_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue, hasFlag } from "../lib/args.js"

// 创建乐观预言机市场
export async function predCreate(args: string[]) {
  const title = getFlagValue(args, "--title")
  const endTimeStr = getFlagValue(args, "--end-time")
  const bondStr = getFlagValue(args, "--bond")
  const challengeStr = getFlagValue(args, "--challenge-period")
  const drawEnabled = hasFlag(args, "--draw")

  if (!title) fatal("Missing --title <string>")
  if (!endTimeStr) fatal("Missing --end-time <unix_timestamp>")
  if (!bondStr) fatal("Missing --bond <amount_in_wei>")
  if (!challengeStr) fatal("Missing --challenge-period <seconds>")

  const endTime = BigInt(endTimeStr)
  const bondAmount = BigInt(bondStr)
  const challengePeriod = BigInt(challengeStr)

  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const diamond = getPredictionDiamondAddress(config)

  log(`Creating optimistic market: "${title}"...`)
  const hash = await walletClient.writeContract({
    address: diamond,
    abi: PREDICTION_ABI,
    functionName: "createOptimisticMarket",
    args: [title, endTime, bondAmount, challengePeriod, drawEnabled],
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  // 从事件中解码 marketId
  let newMarketId: number | null = null
  for (const receiptLog of receipt.logs) {
    try {
      const decoded = decodeEventLog({
        abi: PREDICTION_ABI,
        data: receiptLog.data,
        topics: receiptLog.topics,
      })
      if (decoded.eventName === "OptimisticMarketCreated") {
        newMarketId = Number((decoded.args as { marketId: bigint }).marketId)
      }
    } catch {
      // 跳过无法解码的事件
    }
  }

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
    marketId: newMarketId,
    title,
    endTime: Number(endTime),
    bondAmount: bondAmount.toString(),
    challengePeriod: Number(challengePeriod),
    drawEnabled,
  }, (d) => {
    log(`\nMarket ${d.status === "success" ? "created" : "failed"}!`)
    if (d.marketId !== null) log(`Market ID: #${d.marketId}`)
    log(`Title: ${d.title}`)
    log(`End Time: ${new Date(d.endTime * 1000).toISOString()}`)
    log(`Bond: ${d.bondAmount}`)
    log(`Challenge Period: ${d.challengePeriod}s`)
    log(`Draw: ${d.drawEnabled ? "Enabled" : "Disabled"}`)
    log("")
  })
}
