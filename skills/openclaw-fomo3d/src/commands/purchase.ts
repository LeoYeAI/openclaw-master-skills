import type { Address } from "viem"
import { readConfig, requirePrivateKey, getDiamondAddress } from "../lib/config.js"
import { getPublicClient, getWalletClient } from "../lib/client.js"
import { FOMO3D_ABI } from "../lib/contracts.js"
import { ensureAllowance } from "../lib/erc20.js"
import { output, log, fatal } from "../lib/output.js"
import { getFlagValue } from "../lib/args.js"

export async function purchase(args: string[]) {
  const sharesStr = getFlagValue(args, "--shares")
  if (!sharesStr) fatal("Missing --shares <amount>. Usage: fomo3d purchase --shares 10")

  const shareAmount = BigInt(sharesStr)
  if (shareAmount <= 0n) fatal("Share amount must be positive")

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

  // 检查 pendingWithdrawals
  const pendingWithdrawal = await publicClient.readContract({
    address: diamond, abi: FOMO3D_ABI, functionName: "getPendingWithdrawal", args: [account],
  }) as bigint
  if (pendingWithdrawal > 0n) {
    fatal(`Pending withdrawal: ${pendingWithdrawal}. Run 'fomo3d settle' first.`)
  }

  // 获取 token 地址和 share 价格
  const [gameConfig, sharePrice] = await Promise.all([
    publicClient.readContract({ address: diamond, abi: FOMO3D_ABI, functionName: "getConfig" }) as Promise<[Address, ...unknown[]]>,
    publicClient.readContract({ address: diamond, abi: FOMO3D_ABI, functionName: "getSharePrice" }) as Promise<bigint>,
  ])
  const tokenAddress = gameConfig[0]
  const requiredTokens = shareAmount * sharePrice

  // 自动 approve
  await ensureAllowance(publicClient, walletClient, tokenAddress, diamond, requiredTokens)

  // 购买
  log(`Purchasing ${shareAmount} shares (cost: ${requiredTokens} tokens)...`)
  const hash = await walletClient.writeContract({
    address: diamond,
    abi: FOMO3D_ABI,
    functionName: "purchase",
    args: [shareAmount],
    chain: walletClient.chain,
  })

  log(`Transaction: ${hash}`)
  const receipt = await publicClient.waitForTransactionReceipt({ hash })

  output({
    txHash: hash,
    blockNumber: Number(receipt.blockNumber),
    status: receipt.status,
    sharesAmount: shareAmount.toString(),
    tokensCost: requiredTokens.toString(),
  }, (d) => {
    log(`\nPurchase ${d.status === "success" ? "successful" : "failed"}!`)
    log(`Shares: ${d.sharesAmount}`)
    log(`Tokens spent: ${d.tokensCost}`)
    log(`Block: ${d.blockNumber}`)
    log("")
  })
}
