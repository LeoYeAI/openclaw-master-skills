/**
 * Query the token balance of an EVM address on Auto-EVM.
 */

import { ethers } from 'ethers'
import type { NetworkId } from './network.js'
import { tokenSymbol } from './network.js'

export interface EvmBalanceResult {
  evmAddress: string
  balance: string
  network: NetworkId
  symbol: string
  hint?: string
}

/**
 * Get the native token balance (AI3/tAI3) of an EVM address on Auto-EVM.
 */
export async function queryEvmBalance(
  provider: ethers.Provider,
  evmAddress: string,
  network: NetworkId,
): Promise<EvmBalanceResult> {
  const balanceWei = await provider.getBalance(evmAddress)
  const result: EvmBalanceResult = {
    evmAddress,
    balance: ethers.formatEther(balanceWei),
    network,
    symbol: tokenSymbol(network),
  }

  if (balanceWei === 0n) {
    result.hint = `No EVM balance. To fund this address, run: fund-evm --from <wallet> --amount 1 --network ${network}`
  }

  return result
}
