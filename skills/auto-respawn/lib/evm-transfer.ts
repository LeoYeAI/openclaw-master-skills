/**
 * Transfer native tokens (AI3/tAI3) between EVM addresses on Auto-EVM.
 */

import { ethers } from 'ethers'
import type { NetworkId } from './network.js'
import { tokenSymbol, isMainnet } from './network.js'

export interface EvmTransferResult {
  success: boolean
  transactionHash: string
  blockNumber: number
  blockHash: string
  gasUsed: string
  from: string
  to: string
  amount: string
  network: NetworkId
  symbol: string
  warning?: string
}

/**
 * Send native tokens from an EVM wallet to another EVM address on Auto-EVM.
 *
 * Pre-checks the sender's balance before sending. If insufficient,
 * throws with the available balance so the caller can act.
 */
export async function transferEvmTokens(
  signer: ethers.Wallet,
  to: string,
  amount: string,
  network: NetworkId,
): Promise<EvmTransferResult> {
  const provider = signer.provider
  if (!provider) {
    throw new Error('Signer has no provider — cannot estimate gas or check balance.')
  }

  const amountWei = ethers.parseEther(amount)

  // Pre-check balance (amount + gas estimate for a simple transfer)
  const balance = await provider.getBalance(signer.address)
  const gasEstimate = 21000n // Standard ETH transfer gas
  const feeData = await provider.getFeeData()
  const gasPrice = feeData.gasPrice ?? feeData.maxFeePerGas
  if (gasPrice == null) {
    throw new Error('Unable to determine gas price from network. Please try again.')
  }
  const totalNeeded = amountWei + gasEstimate * gasPrice

  if (balance < totalNeeded) {
    const symbol = tokenSymbol(network)
    throw new Error(
      `Insufficient EVM balance. ` +
        `Sending ${amount} ${symbol} + gas requires ~${ethers.formatEther(totalNeeded)} ${symbol}, ` +
        `but wallet has ${ethers.formatEther(balance)} ${symbol}.`,
    )
  }

  const tx = await signer.sendTransaction({
    to,
    value: amountWei,
  })

  const receipt = await tx.wait()

  if (!receipt) {
    throw new Error('Transaction was sent but no receipt was received.')
  }

  const result: EvmTransferResult = {
    success: receipt.status === 1,
    transactionHash: receipt.hash,
    blockNumber: receipt.blockNumber,
    blockHash: receipt.blockHash,
    gasUsed: receipt.gasUsed.toString(),
    from: await signer.getAddress(),
    to,
    amount,
    network,
    symbol: tokenSymbol(network),
  }

  if (isMainnet(network)) {
    result.warning = 'This was a mainnet transaction on Auto-EVM with real AI3 tokens.'
  }

  return result
}
