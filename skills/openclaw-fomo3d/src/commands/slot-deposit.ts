import type { Address } from "viem"
import { readConfig, requirePrivateKey, getSlotDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { SLOT_ABI } from "../lib/contracts.js"
import { ensureAllowance } from "../lib/erc20.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

export async function slotDeposit(args: string[]) {
  const amountStr = getFlagValue(args, "--amount")
  if (!amountStr) fatal("Missing --amount <n>. Usage: fomo3d slot deposit --amount 1000000000000000000")

  const amount = BigInt(amountStr)
  if (amount <= 0n) fatal("Amount must be positive")

  const config = readConfig()
  const pk = requirePrivateKey(config)
  const publicClient = getPublicClient(config.network, config.rpcUrl)
  const walletClient = getWalletClient(pk, config.network, config.rpcUrl)
  const slotDiamond = getSlotDiamondAddress(config)

  // 获取 token 地址
  const slotConfig = await publicClient.readContract({
    address: slotDiamond, abi: SLOT_ABI, functionName: "getSlotConfig",
  }) as { token: Address }

  // 自动 approve
  await ensureAllowance(publicClient, walletClient, slotConfig.token, slotDiamond, amount)

  log(`Depositing ${amount} tokens to prize pool...`)
  log("WARNING: Deposited tokens are permanently locked. You earn dividends from shares.")

  const hash = await walletClient.writeContract({
    address: slotDiamond,
    abi: SLOT_ABI,
    functionName: "deposit",
    args: [amount],
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
    amount: amount.toString(),
    warning: "Tokens permanently locked. You earn dividend shares.",
  }, (d) => {
    log(`\nDeposit ${d.status === "success" ? "successful" : "failed"}!`)
    log(`Amount: ${d.amount}`)
    log(`Block: ${d.blockNumber}`)
    log("")
  })
}
