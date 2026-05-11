import { readConfig, requirePrivateKey, getPredictionDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { PREDICTION_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue, hasFlag } from "../lib/args.js"

const SIDE_MAP: Record<string, number> = { yes: 0, no: 1, draw: 2 }

// 仲裁者解决争议（仅 owner 或 arbiter）
export async function predResolve(args: string[]) {
  const idStr = getFlagValue(args, "--id")
  const outcomeStr = getFlagValue(args, "--outcome")
  const winnerIsProposer = hasFlag(args, "--proposer-wins")

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

  log(`Resolving dispute for market #${marketId}: ${outcomeStr.toUpperCase()}, proposer wins: ${winnerIsProposer}...`)
  const hash = await walletClient.writeContract({
    address: diamond,
    abi: PREDICTION_ABI,
    functionName: "resolveDispute",
    args: [marketId, outcome, winnerIsProposer],
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
    winnerIsProposer,
  }, (d) => {
    log(`\nResolve ${d.status === "success" ? "successful" : "failed"}!`)
    log(`Market: #${d.marketId}, Outcome: ${d.outcome.toUpperCase()}, Proposer wins: ${d.winnerIsProposer}`)
    log("")
  })
}
