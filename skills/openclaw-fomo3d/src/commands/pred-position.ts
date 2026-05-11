import { readConfig, requirePrivateKey, getPredictionDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { PREDICTION_ABI } from "../lib/contracts.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"
import { isAddress, getAddress, type Address } from "viem"

// 查看玩家在某市场的仓位
export async function predPosition(args: string[]) {
  const idStr = getFlagValue(args, "--id")
  if (!idStr) fatal("Missing --id <marketId>. Usage: fomo3d pred position --id 1")

  const marketId = BigInt(idStr)
  const config = readConfig()
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const diamond = getPredictionDiamondAddress(config)

  // 地址：优先 --address，否则用钱包
  let playerAddress: Address
  const addrStr = getFlagValue(args, "--address")
  if (addrStr) {
    if (!isAddress(addrStr)) fatal(`Invalid address: ${addrStr}`)
    playerAddress = getAddress(addrStr)
  } else {
    const pk = requirePrivateKey(config)
    const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
    playerAddress = walletClient.account!.address
  }

  const position = await publicClient.readContract({
    address: diamond, abi: PREDICTION_ABI, functionName: "getPlayerPosition",
    args: [marketId, playerAddress],
  }) as {
    yesShares: bigint; noShares: bigint; drawShares: bigint;
    pendingYesDividends: bigint; pendingNoDividends: bigint; pendingDrawDividends: bigint;
    estimatedPrizeIfYes: bigint; estimatedPrizeIfNo: bigint; estimatedPrizeIfDraw: bigint;
    exited: boolean; settled: boolean
  }

  const data = {
    marketId: Number(marketId),
    player: playerAddress,
    yesShares: position.yesShares.toString(),
    noShares: position.noShares.toString(),
    drawShares: position.drawShares.toString(),
    pendingYesDividends: position.pendingYesDividends.toString(),
    pendingNoDividends: position.pendingNoDividends.toString(),
    pendingDrawDividends: position.pendingDrawDividends.toString(),
    estimatedPrizeIfYes: position.estimatedPrizeIfYes.toString(),
    estimatedPrizeIfNo: position.estimatedPrizeIfNo.toString(),
    estimatedPrizeIfDraw: position.estimatedPrizeIfDraw.toString(),
    exited: position.exited,
    settled: position.settled,
  }

  output(data, (d) => {
    log(`\n=== Position in Market #${d.marketId} ===`)
    log(`Player:      ${d.player}`)
    log(`Yes Shares:  ${d.yesShares} (div: ${d.pendingYesDividends}, prize: ${d.estimatedPrizeIfYes})`)
    log(`No Shares:   ${d.noShares} (div: ${d.pendingNoDividends}, prize: ${d.estimatedPrizeIfNo})`)
    log(`Draw Shares: ${d.drawShares} (div: ${d.pendingDrawDividends}, prize: ${d.estimatedPrizeIfDraw})`)
    log(`Exited:      ${d.exited}`)
    log(`Settled:     ${d.settled}`)
    log("")
  })
}
