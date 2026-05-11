import { readConfig, requirePrivateKey, getDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { FOMO3D_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"

export async function endRound(_args: string[]) {
  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const diamond = getDiamondAddress(config)

  // 检查倒计时
  const countdown = await publicClient.readContract({
    address: diamond, abi: FOMO3D_ABI, functionName: "getCountdownRemaining",
  }) as bigint

  if (countdown > 0n) {
    fatal(`Round not expired yet. ${countdown} seconds remaining.`)
  }

  log("Ending round and distributing prizes...")
  const hash = await walletClient.writeContract({
    address: diamond,
    abi: FOMO3D_ABI,
    functionName: "endRoundAndDistribute",
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
  }, (d) => {
    log(`\nEnd round ${d.status === "success" ? "successful" : "failed"}!`)
    log(`Block: ${d.blockNumber}`)
    log("")
  })
}
