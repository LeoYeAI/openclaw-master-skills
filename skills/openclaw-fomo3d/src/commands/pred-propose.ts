import type { Address } from "viem"
import { readConfig, requirePrivateKey, getPredictionDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { PREDICTION_ABI } from "../lib/contracts.js"
import { ensureAllowance } from "../lib/erc20.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

const SIDE_MAP: Record<string, number> = { yes: 0, no: 1, draw: 2 }

// 提议乐观预言机结果（需要质押 bond）
export async function predPropose(args: string[]) {
  const idStr = getFlagValue(args, "--id")
  const outcomeStr = getFlagValue(args, "--outcome")

  if (!idStr) fatal("Missing --id <marketId>")
  if (!outcomeStr) fatal("Missing --outcome <yes|no|draw>")

  const outcome = SIDE_MAP[outcomeStr.toLowerCase()]
  if (outcome === undefined) fatal(`Invalid outcome: ${outcomeStr}. Must be yes, no, or draw`)

  const marketId = BigInt(idStr)
  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const diamond = getPredictionDiamondAddress(config)

  // 获取 bond 金额和 token 地址
  const [optConfig, predConfig] = await Promise.all([
    publicClient.readContract({
      address: diamond, abi: PREDICTION_ABI, functionName: "getOptimisticConfig", args: [marketId],
    }) as Promise<{ bondAmount: bigint }>,
    publicClient.readContract({
      address: diamond, abi: PREDICTION_ABI, functionName: "getPredictionConfig",
    }) as Promise<{ token: Address }>,
  ])

  // 自动 approve bond
  await ensureAllowance(publicClient, walletClient, predConfig.token, diamond, optConfig.bondAmount)

  log(`Proposing ${outcomeStr.toUpperCase()} for market #${marketId} (bond: ${optConfig.bondAmount})...`)
  const hash = await walletClient.writeContract({
    address: diamond,
    abi: PREDICTION_ABI,
    functionName: "proposeOutcome",
    args: [marketId, outcome],
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
    marketId: Number(marketId),
    outcome: outcomeStr.toLowerCase(),
    bondAmount: optConfig.bondAmount.toString(),
  }, (d) => {
    log(`\nProposal ${d.status === "success" ? "submitted" : "failed"}!`)
    log(`Market: #${d.marketId}, Outcome: ${d.outcome.toUpperCase()}, Bond: ${d.bondAmount}`)
    log("")
  })
}
