import { readConfig, requirePrivateKey, getSlotDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { SLOT_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"

export async function slotCancel(_args: string[]) {
  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const slotDiamond = getSlotDiamondAddress(config)
  const account = walletClient.account!.address

  // 检查是否有 pending spin
  const playerView = await publicClient.readContract({
    address: slotDiamond, abi: SLOT_ABI, functionName: "getPlayerInfo", args: [account],
  }) as { pendingRequestId: bigint }

  if (!playerView.pendingRequestId || playerView.pendingRequestId === 0n) {
    fatal("No pending spin to cancel.")
  }

  log("Cancelling timed-out spin...")
  const hash = await walletClient.writeContract({
    address: slotDiamond,
    abi: SLOT_ABI,
    functionName: "cancelSpin",
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
  }, (d) => {
    log(`\nCancel ${d.status === "success" ? "successful" : "failed"}!`)
    log(`Block: ${d.blockNumber}`)
    log("")
  })
}
