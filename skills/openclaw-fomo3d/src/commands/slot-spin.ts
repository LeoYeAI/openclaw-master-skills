import type { Address } from "viem"
import { readConfig, requirePrivateKey, getSlotDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { SLOT_ABI, VRF_FEE_FALLBACK } from "../lib/contracts.js"
import { ensureAllowance } from "../lib/erc20.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

export async function slotSpin(args: string[]) {
  const betStr = getFlagValue(args, "--bet")
  if (!betStr) fatal("Missing --bet <amount>. Usage: fomo3d slot spin --bet 1000000000000000000")

  const betAmount = BigInt(betStr)
  if (betAmount <= 0n) fatal("Bet amount must be positive")

  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const slotDiamond = getSlotDiamondAddress(config)

  // 获取配置
  const slotConfig = await publicClient.readContract({
    address: slotDiamond, abi: SLOT_ABI, functionName: "getSlotConfig",
  }) as { token: Address; minBet: bigint; maxBet: bigint; vrfFee: bigint }

  if (betAmount < slotConfig.minBet) fatal(`Bet too small. Min: ${slotConfig.minBet}`)
  if (betAmount > slotConfig.maxBet) fatal(`Bet too large. Max: ${slotConfig.maxBet}`)

  // 自动 approve
  await ensureAllowance(publicClient, walletClient, slotConfig.token, slotDiamond, betAmount)

  // spin（payable，附带 VRF 费用）
  const vrfFee = slotConfig.vrfFee > 0n ? slotConfig.vrfFee : VRF_FEE_FALLBACK
  log(`Spinning with bet ${betAmount}, VRF fee ${vrfFee}...`)

  const hash = await walletClient.writeContract({
    address: slotDiamond,
    abi: SLOT_ABI,
    functionName: "spin",
    args: [betAmount],
    value: vrfFee,
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
    betAmount: betAmount.toString(),
    vrfFee: vrfFee.toString(),
    note: "Spin requested. VRF callback pending (1-3 blocks). Check result with 'fomo3d slot status' or player info.",
  }, (d) => {
    log(`\nSpin ${d.status === "success" ? "requested" : "failed"}!`)
    log(`Bet: ${d.betAmount}`)
    log(d.note)
    log("")
  })
}
