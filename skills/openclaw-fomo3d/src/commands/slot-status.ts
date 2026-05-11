import { readConfig, getSlotDiamondAddress } from "../lib/config.js"
import { getPublicClient } from "../lib/client.js"
import { SLOT_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"

export async function slotStatus(_args: string[]) {
  const config = readConfig()
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const slotDiamond = getSlotDiamondAddress(config)

  const [slotConfig, isPaused] = await Promise.all([
      publicClient.readContract({ address: slotDiamond, abi: SLOT_ABI, functionName: "getSlotConfig" }),
      publicClient.readContract({ address: slotDiamond, abi: SLOT_ABI, functionName: "isPaused" }),
    ])

    // SlotConfig 是一个 struct，viem 返回对象
    const sc = slotConfig as {
      token: string; minBet: bigint; maxBet: bigint; prizePool: bigint;
      totalShares: bigint; devFeeBps: number; dividendBps: number; vrfFee: bigint;
      totalSpins: bigint; totalBetAmount: bigint; totalWinAmount: bigint;
      totalDividendsDistributed: bigint;
    }

    const data = {
      network: config.network,
      paused: isPaused as boolean,
      token: sc.token,
      minBet: sc.minBet.toString(),
      maxBet: sc.maxBet.toString(),
      prizePool: sc.prizePool.toString(),
      totalShares: sc.totalShares.toString(),
      devFeeBps: Number(sc.devFeeBps),
      dividendBps: Number(sc.dividendBps),
      vrfFee: sc.vrfFee.toString(),
      stats: {
        totalSpins: sc.totalSpins.toString(),
        totalBetAmount: sc.totalBetAmount.toString(),
        totalWinAmount: sc.totalWinAmount.toString(),
        totalDividendsDistributed: sc.totalDividendsDistributed.toString(),
      },
    }

    output(data, (d) => {
      log(`\n=== Slot Machine (${d.network}) ===`)
      log(`Paused:      ${d.paused}`)
      log(`Prize Pool:  ${d.prizePool}`)
      log(`Min Bet:     ${d.minBet}`)
      log(`Max Bet:     ${d.maxBet}`)
      log(`VRF Fee:     ${d.vrfFee} wei`)
      log(`Dividend:    ${d.dividendBps / 100}%`)
      log(`Dev Fee:     ${d.devFeeBps / 100}%`)
      log(`Total Spins: ${d.stats.totalSpins}`)
      log(`Total Bet:   ${d.stats.totalBetAmount}`)
      log(`Total Won:   ${d.stats.totalWinAmount}`)
      log("")
    })
}
