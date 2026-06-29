import { transfer } from '@autonomys/auto-consensus'
import { signAndSendTx, ai3ToShannons, address as formatAddress } from '@autonomys/auto-utils'
import type { ApiPromise } from '@polkadot/api'
import type { KeyringPair } from '@polkadot/keyring/types'
import { type NetworkId, tokenSymbol, isMainnet } from './network.js'
import { normalizeAddress } from './address.js'

export interface TransferResult {
  success: boolean
  txHash: string | undefined
  blockHash: string | undefined
  from: string
  to: string
  amount: string
  network: NetworkId
  symbol: string
  warning?: string
}

export async function transferTokens(
  api: ApiPromise,
  sender: KeyringPair,
  to: string,
  amount: string,
  network: NetworkId,
): Promise<TransferResult> {
  const normalizedTo = normalizeAddress(to)
  const shannons = ai3ToShannons(amount)
  const tx = transfer(api, normalizedTo, shannons)

  // Use default event check (system.ExtrinsicSuccess) rather than
  // events.transfer which requires all four sub-events and can fail
  // on some runtime configurations.
  const result = await signAndSendTx(sender, tx)

  // The SDK's detectTxSuccess has a bug (forEach return doesn't propagate)
  // so result.success is always false. If signAndSendTx resolved without
  // throwing, the tx landed in a block — that's success.
  const transferResult: TransferResult = {
    success: !!(result.txHash && result.blockHash),
    txHash: result.txHash,
    blockHash: result.blockHash,
    from: formatAddress(sender.address),
    to: normalizedTo,
    amount,
    network,
    symbol: tokenSymbol(network),
  }

  if (isMainnet(network)) {
    transferResult.warning = 'This was a mainnet transaction with real AI3 tokens.'
  }

  return transferResult
}
