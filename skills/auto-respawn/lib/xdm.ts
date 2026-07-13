/**
 * Cross-domain messaging (XDM): move tokens between consensus and Auto-EVM.
 *
 * Consensus → EVM: uses `transporterTransfer` via substrate RPC + signAndSendTx
 * EVM → Consensus: uses `transferToConsensus` via the EVM precompile at 0x0800
 */

import { transporterTransfer, transferToConsensus } from '@autonomys/auto-xdm'
import { signAndSendTx, ai3ToShannons, address as formatAddress } from '@autonomys/auto-utils'
import type { ApiPromise } from '@polkadot/api'
import type { KeyringPair } from '@polkadot/keyring/types'
import type { ethers } from 'ethers'
import type { NetworkId } from './network.js'
import { tokenSymbol, isMainnet } from './network.js'
import { AUTO_EVM_DOMAIN_ID } from './evm.js'

export interface FundEvmResult {
  success: boolean
  txHash: string | undefined
  blockHash: string | undefined
  from: string
  toEvmAddress: string
  amount: string
  network: NetworkId
  symbol: string
  warning?: string
}

/**
 * Transfer tokens from the consensus layer to an EVM address on Auto-EVM.
 *
 * Uses the Autonomys transporter (XDM) to bridge tokens across domains.
 * The sender signs a consensus-layer extrinsic that credits the EVM address.
 */
export async function fundEvm(
  api: ApiPromise,
  sender: KeyringPair,
  evmAddress: string,
  amount: string,
  network: NetworkId,
): Promise<FundEvmResult> {
  const shannons = ai3ToShannons(amount)

  const tx = transporterTransfer(
    api,
    { domainId: AUTO_EVM_DOMAIN_ID },
    { accountId20: evmAddress },
    shannons,
  )

  const result = await signAndSendTx(sender, tx)

  const fundResult: FundEvmResult = {
    success: !!(result.txHash && result.blockHash),
    txHash: result.txHash,
    blockHash: result.blockHash,
    from: formatAddress(sender.address),
    toEvmAddress: evmAddress,
    amount,
    network,
    symbol: tokenSymbol(network),
  }

  if (isMainnet(network)) {
    fundResult.warning = 'This was a mainnet transaction with real AI3 tokens.'
  }

  return fundResult
}

export interface WithdrawResult {
  success: boolean
  transactionHash: string
  blockNumber: number
  blockHash: string
  gasUsed: string
  fromEvmAddress: string
  toConsensusAddress: string
  amount: string
  network: NetworkId
  symbol: string
  warning?: string
}

/**
 * Transfer tokens from Auto-EVM back to a consensus address.
 *
 * Uses the transporter precompile at 0x0800 on Auto-EVM.
 * The sender signs an EVM transaction that debits the EVM address
 * and credits the consensus address.
 */
export async function withdrawToConsensus(
  signer: ethers.Wallet,
  consensusAddress: string,
  amount: string,
  network: NetworkId,
): Promise<WithdrawResult> {
  // Convert human-readable amount (AI3) to wei (1 AI3 = 10^18 wei, same as Shannon)
  const amountWei = BigInt(ai3ToShannons(amount).toString())

  const result = await transferToConsensus(signer, consensusAddress, amountWei)

  const withdrawResult: WithdrawResult = {
    success: result.success,
    transactionHash: result.transactionHash,
    blockNumber: result.blockNumber,
    blockHash: result.blockHash,
    gasUsed: result.gasUsed.toString(),
    fromEvmAddress: await signer.getAddress(),
    toConsensusAddress: consensusAddress,
    amount,
    network,
    symbol: tokenSymbol(network),
  }

  if (isMainnet(network)) {
    withdrawResult.warning = 'This was a mainnet transaction with real AI3 tokens.'
  }

  return withdrawResult
}
