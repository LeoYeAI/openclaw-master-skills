import { type Address, maxUint256 } from "viem"
import type { PublicClient, WalletClient } from "viem"
import { ERC20_ABI } from "./contracts.js"
import { log } from "./output.js"

export async function ensureAllowance(
  publicClient: PublicClient,
  walletClient: WalletClient,
  tokenAddress: Address,
  spenderAddress: Address,
  requiredAmount: bigint,
): Promise<void> {
  const owner = walletClient.account!.address

  const allowance = await publicClient.readContract({
    address: tokenAddress,
    abi: ERC20_ABI,
    functionName: "allowance",
    args: [owner, spenderAddress],
  })

  if (allowance >= requiredAmount) {
    log(`Allowance sufficient: ${allowance}`)
    return
  }

  log(`Approving token spend...`)
  const hash = await walletClient.writeContract({
    address: tokenAddress,
    abi: ERC20_ABI,
    functionName: "approve",
    args: [spenderAddress, maxUint256],
    account: walletClient.account!,
    chain: walletClient.chain,
  })

  log(`Approve tx: ${hash}`)
  await publicClient.waitForTransactionReceipt({ hash })
  log("Approve confirmed")
}

export async function getTokenBalance(
  publicClient: PublicClient,
  tokenAddress: Address,
  owner: Address,
): Promise<bigint> {
  return await publicClient.readContract({
    address: tokenAddress,
    abi: ERC20_ABI,
    functionName: "balanceOf",
    args: [owner],
  })
}
