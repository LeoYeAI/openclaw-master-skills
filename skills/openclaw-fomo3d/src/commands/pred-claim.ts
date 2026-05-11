import { readConfig, requirePrivateKey, getPredictionDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { PREDICTION_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

// 市场结算后领取奖金
export async function predClaim(args: string[]) {
  const idStr = getFlagValue(args, "--id")
  if (!idStr) fatal("Missing --id <marketId>. Usage: fomo3d pred claim --id 1")

  const marketId = BigInt(idStr)
  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const diamond = getPredictionDiamondAddress(config)

  log(`Claiming settlement for market #${marketId}...`)
  const hash = await walletClient.writeContract({
    address: diamond,
    abi: PREDICTION_ABI,
    functionName: "claimSettlement",
    args: [marketId],
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
    marketId: Number(marketId),
  }, (d) => {
    log(`\nClaim ${d.status === "success" ? "successful" : "failed"}!`)
    log(`Market: #${d.marketId}`)
    log("")
  })
}
