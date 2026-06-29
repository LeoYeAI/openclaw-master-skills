import { ethers } from 'ethers'

export interface AnchorResult {
  success: boolean
  txHash: string | undefined
  blockHash: string | undefined
  cid: string
  evmAddress: string
  network: string
  gasUsed?: string
  warning?: string
}

/**
 * Anchor a CID on-chain by writing it to the MemoryChain contract.
 * Calls updateHead(string cid) — the contract stores the CID string directly.
 *
 * Pre-checks the wallet's EVM balance and estimates gas before sending.
 * If the balance is too low, throws with an actionable hint to run fund-evm.
 */
export async function anchorCid(
  contract: ethers.Contract,
  cid: string,
  evmAddress: string,
  network: string,
): Promise<AnchorResult> {
  const provider = contract.runner?.provider
  if (!provider) {
    throw new Error('Contract has no provider — cannot estimate gas or check balance.')
  }

  // Estimate gas cost before sending
  let estimatedGas: bigint
  try {
    estimatedGas = await contract.updateHead.estimateGas(cid)
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    if (message.includes('insufficient funds') || message.includes('INSUFFICIENT_FUNDS')) {
      throw new Error(
        `Insufficient EVM balance to anchor. ` +
          `Run: fund-evm --from <wallet> --amount 1 --network ${network}`,
        { cause: err },
      )
    }
    throw err
  }

  // Check balance against estimated cost
  const feeData = await provider.getFeeData()
  const gasPrice = feeData.gasPrice ?? feeData.maxFeePerGas
  if (gasPrice == null) {
    throw new Error('Unable to determine gas price from network. Please try again.')
  }
  const estimatedCost = estimatedGas * gasPrice
  const balance = await provider.getBalance(evmAddress)

  if (balance < estimatedCost) {
    const needed = ethers.formatEther(estimatedCost)
    const have = ethers.formatEther(balance)
    throw new Error(
      `Insufficient EVM balance to anchor. ` +
        `Need ~${needed} ${network === 'mainnet' ? 'AI3' : 'tAI3'}, have ${have}. ` +
        `Run: fund-evm --from <wallet> --amount 1 --network ${network}`,
    )
  }

  const tx: ethers.TransactionResponse = await contract.updateHead(cid)
  const receipt = await tx.wait()

  if (!receipt) {
    throw new Error('Anchor transaction was sent but no receipt was received (transaction may have been replaced or dropped).')
  }

  return {
    success: receipt.status === 1,
    txHash: receipt.hash,
    blockHash: receipt.blockHash,
    cid,
    evmAddress,
    network,
    gasUsed: receipt.gasUsed.toString(),
  }
}

export interface GetHeadResult {
  evmAddress: string
  cid: string | undefined
  network: string
}

/**
 * Read the last anchored CID for an EVM address from the MemoryChain contract.
 * Calls getHead(address) — returns the CID string directly, or undefined if none set.
 */
export async function getHeadCid(
  contract: ethers.Contract,
  evmAddress: string,
  network: string,
): Promise<GetHeadResult> {
  let cid: string
  try {
    cid = await contract.getHead(evmAddress)
  } catch (err) {
    // ethers throws BAD_DATA when calling a non-existent contract (returns 0x).
    const message = err instanceof Error ? err.message : String(err)
    if (message.includes('BAD_DATA') || message.includes('could not decode result data')) {
      throw new Error(
        `MemoryChain contract not available on network "${network}". ` +
          'The contract may not be deployed at the configured address.',
        { cause: err },
      )
    }
    throw err
  }

  return {
    evmAddress,
    cid: cid || undefined,
    network,
  }
}
