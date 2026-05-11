import { readConfig, requirePrivateKey, getDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { FOMO3D_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"

export async function exit(_args: string[]) {
  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const diamond = getDiamondAddress(config)
  const account = walletClient.account!.address

  // 检查暂停
  const isPaused = await publicClient.readContract({
    address: diamond, abi: FOMO3D_ABI, functionName: "isPaused",
  }) as boolean
  if (isPaused) fatal("Game is paused")

  // 检查玩家状态
  const playerInfo = await publicClient.readContract({
    address: diamond, abi: FOMO3D_ABI, functionName: "getPlayerInfo", args: [account],
  }) as readonly [bigint, bigint, number, bigint, boolean]

  if (playerInfo[3] === 0n) fatal("You have no shares")
  if (playerInfo[4]) fatal("Already exited this round")

  log("Exiting game...")
  const hash = await walletClient.writeContract({
    address: diamond,
    abi: FOMO3D_ABI,
    functionName: "exitGame",
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
    shares: playerInfo[3].toString(),
  }, (d) => {
    log(`\nExit ${d.status === "success" ? "successful" : "failed"}!`)
    log(`Shares exited: ${d.shares}`)
    log(`Block: ${d.blockNumber}`)
    log("")
  })
}
