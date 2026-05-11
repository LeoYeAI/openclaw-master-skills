import { readConfig, getDiamondAddress } from "../lib/config.js"
import { getPublicClient } from "../lib/client.js"
import { FOMO3D_ABI } from "../lib/contracts.js"
import { output, log } from "../lib/output.js"

const ROUND_STATUS = ["NotStarted", "Active", "Ended"] as const

export async function status(_args: string[]) {
  const config = readConfig()
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const diamond = getDiamondAddress(config)

  const [currentRound, countdown, pools, isPaused, sharePrice] = await Promise.all([
    publicClient.readContract({ address: diamond, abi: FOMO3D_ABI, functionName: "getCurrentRoundNumber" }),
    publicClient.readContract({ address: diamond, abi: FOMO3D_ABI, functionName: "getCountdownRemaining" }),
    publicClient.readContract({ address: diamond, abi: FOMO3D_ABI, functionName: "getPools" }),
    publicClient.readContract({ address: diamond, abi: FOMO3D_ABI, functionName: "isPaused" }),
    publicClient.readContract({ address: diamond, abi: FOMO3D_ABI, functionName: "getSharePrice" }),
  ])

  const roundNumber = Number(currentRound)
  const roundInfo = await publicClient.readContract({
    address: diamond,
    abi: FOMO3D_ABI,
    functionName: "getRoundInfo",
    args: [roundNumber],
  }) as readonly [number, boolean, bigint, bigint, bigint, bigint, bigint, bigint]

  const lastBuyers = await publicClient.readContract({
    address: diamond,
    abi: FOMO3D_ABI,
    functionName: "getLastBuyers",
    args: [roundNumber],
  }) as readonly `0x${string}`[]

  const [poolPending, poolNextRound, trackedBalance, contractBalance] = pools as readonly [bigint, bigint, bigint, bigint]
  const zeroAddr = "0x0000000000000000000000000000000000000000"

  const data = {
    network: config.network,
    paused: isPaused as boolean,
    currentRound: roundNumber,
    roundStatus: ROUND_STATUS[roundInfo[0]] ?? "Unknown",
    isPrizePaid: roundInfo[1],
    startTime: Number(roundInfo[2]),
    endTime: Number(roundInfo[3]),
    totalShares: roundInfo[4].toString(),
    earningsPerShare: roundInfo[5].toString(),
    grandPrizePool: roundInfo[6].toString(),
    dividendPool: roundInfo[7].toString(),
    countdownRemaining: Number(countdown),
    sharePrice: (sharePrice as bigint).toString(),
    pools: {
      pendingPool: poolPending.toString(),
      nextRoundCarryover: poolNextRound.toString(),
      trackedBalance: trackedBalance.toString(),
      contractBalance: contractBalance.toString(),
    },
    lastBuyers: (lastBuyers as string[]).filter(a => a !== zeroAddr),
  }

  output(data, (d) => {
    log(`\n=== Fomo3D Status (${d.network}) ===`)
    log(`Round:       #${d.currentRound} (${d.roundStatus})`)
    log(`Paused:      ${d.paused}`)
    log(`Countdown:   ${d.countdownRemaining}s`)
    log(`Grand Prize: ${d.grandPrizePool}`)
    log(`Dividends:   ${d.dividendPool}`)
    log(`Share Price: ${d.sharePrice}`)
    log(`Shares:      ${d.totalShares}`)
    if (d.lastBuyers.length > 0) {
      log(`Last Buyers: ${d.lastBuyers.join(", ")}`)
    }
    log("")
  })
}
