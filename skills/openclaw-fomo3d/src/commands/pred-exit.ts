import { readConfig, requirePrivateKey, getPredictionDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { PREDICTION_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

const SIDE_MAP: Record<string, number> = { yes: 0, no: 1, draw: 2 }

// 退出某个方向，领取累积分红
export async function predExit(args: string[]) {
  const idStr = getFlagValue(args, "--id")
  const sideStr = getFlagValue(args, "--side")

  if (!idStr) fatal("Missing --id <marketId>")
  if (!sideStr) fatal("Missing --side <yes|no|draw>")

  const side = SIDE_MAP[sideStr.toLowerCase()]
  if (side === undefined) fatal(`Invalid side: ${sideStr}. Must be yes, no, or draw`)

  const marketId = BigInt(idStr)
  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const diamond = getPredictionDiamondAddress(config)

  log(`Exiting ${sideStr.toUpperCase()} from market #${marketId}...`)
  const hash = await walletClient.writeContract({
    address: diamond,
    abi: PREDICTION_ABI,
    functionName: "exitMarket",
    args: [marketId, side],
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
  }, (d) => {
    log(`\nExit ${d.status === "success" ? "successful" : "failed"}!`)
    log(`Market: #${d.marketId}, Side: ${d.side.toUpperCase()}`)
    log("")
  })
}
