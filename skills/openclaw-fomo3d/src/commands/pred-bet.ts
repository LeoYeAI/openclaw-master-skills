import type { Address } from "viem"
import { readConfig, requirePrivateKey, getPredictionDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { PREDICTION_ABI } from "../lib/contracts.js"
import { ensureAllowance } from "../lib/erc20.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

const SIDE_MAP: Record<string, number> = { yes: 0, no: 1, draw: 2 }

// 在市场中下注
export async function predBet(args: string[]) {
  const idStr = getFlagValue(args, "--id")
  const sideStr = getFlagValue(args, "--side")
  const amountStr = getFlagValue(args, "--amount")

  if (!idStr) fatal("Missing --id <marketId>")
  if (!sideStr) fatal("Missing --side <yes|no|draw>")
  if (!amountStr) fatal("Missing --amount <wei>")

  const side = SIDE_MAP[sideStr.toLowerCase()]
  if (side === undefined) fatal(`Invalid side: ${sideStr}. Must be yes, no, or draw`)

  const marketId = BigInt(idStr)
  const amount = BigInt(amountStr)
  if (amount <= 0n) fatal("Amount must be positive")

  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const diamond = getPredictionDiamondAddress(config)

  // 获取 token 地址
  const predConfig = await publicClient.readContract({
    address: diamond, abi: PREDICTION_ABI, functionName: "getPredictionConfig",
  }) as { token: Address; minBet: bigint; paused: boolean }

  if (predConfig.paused) fatal("Prediction market is paused")
  if (amount < predConfig.minBet) fatal(`Amount below min bet: ${predConfig.minBet}`)

  // 自动 approve
  await ensureAllowance(publicClient, walletClient, predConfig.token, diamond, amount)

  log(`Placing ${sideStr.toUpperCase()} bet of ${amount} on market #${marketId}...`)
  const hash = await walletClient.writeContract({
    address: diamond,
    abi: PREDICTION_ABI,
    functionName: "placeBet",
    args: [marketId, side, amount],
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
    marketId: Number(marketId),
    side: sideStr.toLowerCase(),
    amount: amount.toString(),
  }, (d) => {
    log(`\nBet ${d.status === "success" ? "placed" : "failed"}!`)
    log(`Market: #${d.marketId}`)
    log(`Side: ${d.side.toUpperCase()}`)
    log(`Amount: ${d.amount}`)
    log("")
  })
}
