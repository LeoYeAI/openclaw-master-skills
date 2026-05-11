import { readConfig, requirePrivateKey, getSlotDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { SLOT_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"

export async function slotClaim(_args: string[]) {
  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const slotDiamond = getSlotDiamondAddress(config)
  const account = walletClient.account!.address

  // 检查分红
  const playerView = await publicClient.readContract({
    address: slotDiamond, abi: SLOT_ABI, functionName: "getPlayerInfo", args: [account],
  }) as { shares: bigint; pendingDividends: bigint; canClaim: boolean }

  if (playerView.shares === 0n) fatal("No shares. Deposit tokens first.")
  if (!playerView.canClaim) fatal("Cannot claim now. You may have a pending spin.")
  if (playerView.pendingDividends === 0n) fatal("No dividends to claim.")

  log(`Claiming dividends: ${playerView.pendingDividends}...`)
  const hash = await walletClient.writeContract({
    address: slotDiamond,
    abi: SLOT_ABI,
    functionName: "claimDividends",
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
    dividends: playerView.pendingDividends.toString(),
  }, (d) => {
    log(`\nClaim ${d.status === "success" ? "successful" : "failed"}!`)
    log(`Dividends: ${d.dividends} (gross, dev fee deducted on-chain)`)
    log(`Block: ${d.blockNumber}`)
    log("")
  })
}
