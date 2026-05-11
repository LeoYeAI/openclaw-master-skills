import type { Address } from "viem"
import { readConfig, requirePrivateKey, getDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { FOMO3D_ABI } from "../lib/contracts.js"
import { output, log } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

export async function player(args: string[]) {
  const config = readConfig()
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const diamond = getDiamondAddress(config)

  // 确定地址
  let address: Address
  const addrArg = getFlagValue(args, "--address")
  if (addrArg) {
    address = addrArg as Address
  } else {
    const pk = requirePrivateKey(config)
    const wc = getWalletClient(pk, config.network, config.rpcUrl)
    address = wc.account!.address
  }

  const [playerInfo, pendingEarnings, pendingWithdrawal] = await Promise.all([
    publicClient.readContract({
      address: diamond, abi: FOMO3D_ABI, functionName: "getPlayerInfo", args: [address],
    }) as Promise<readonly [bigint, bigint, number, bigint, boolean]>,
    publicClient.readContract({
      address: diamond, abi: FOMO3D_ABI, functionName: "getPlayerPendingEarnings", args: [address],
    }) as Promise<bigint>,
    publicClient.readContract({
      address: diamond, abi: FOMO3D_ABI, functionName: "getPendingWithdrawal", args: [address],
    }) as Promise<bigint>,
  ])

  const data = {
    address,
    network: config.network,
    earningsPerShare: playerInfo[0].toString(),
    accumulatedEarnings: playerInfo[1].toString(),
    roundNumber: Number(playerInfo[2]),
    shares: playerInfo[3].toString(),
    hasExited: playerInfo[4],
    pendingEarnings: pendingEarnings.toString(),
    pendingWithdrawal: pendingWithdrawal.toString(),
  }

  output(data, (d) => {
    log(`\n=== Player Info (${d.network}) ===`)
    log(`Address:     ${d.address}`)
    log(`Round:       #${d.roundNumber}`)
    log(`Shares:      ${d.shares}`)
    log(`Has Exited:  ${d.hasExited}`)
    log(`Pending Earnings:    ${d.pendingEarnings}`)
    log(`Pending Withdrawal:  ${d.pendingWithdrawal}`)
    log("")
  })
}
