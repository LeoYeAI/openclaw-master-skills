import { readConfig, requirePrivateKey, getDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { FOMO3D_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"

export async function settle(_args: string[]) {
  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const diamond = getDiamondAddress(config)
  const account = walletClient.account!.address

  // 检查是否有待结算
  const [pendingEarnings, pendingWithdrawal] = await Promise.all([
    publicClient.readContract({
      address: diamond, abi: FOMO3D_ABI, functionName: "getPlayerPendingEarnings", args: [account],
    }) as Promise<bigint>,
    publicClient.readContract({
      address: diamond, abi: FOMO3D_ABI, functionName: "getPendingWithdrawal", args: [account],
    }) as Promise<bigint>,
  ])

  if (pendingEarnings === 0n && pendingWithdrawal === 0n) {
    fatal("Nothing to settle. No pending earnings or withdrawal.")
  }

  log(`Settling... (earnings: ${pendingEarnings}, withdrawal: ${pendingWithdrawal})`)
  const hash = await walletClient.writeContract({
    address: diamond,
    abi: FOMO3D_ABI,
    functionName: "settleUnexited",
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
    pendingEarnings: pendingEarnings.toString(),
    pendingWithdrawal: pendingWithdrawal.toString(),
  }, (d) => {
    log(`\nSettle ${d.status === "success" ? "successful" : "failed"}!`)
    log(`Earnings settled: ${d.pendingEarnings}`)
    log(`Withdrawal claimed: ${d.pendingWithdrawal}`)
    log(`Block: ${d.blockNumber}`)
    log("")
  })
}
