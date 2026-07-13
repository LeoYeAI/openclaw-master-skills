import { balance } from '@autonomys/auto-consensus'
import { shannonsToAi3 } from '@autonomys/auto-utils'
import type { ApiPromise } from '@polkadot/api'
import { type NetworkId, tokenSymbol } from './network.js'
import { normalizeAddress } from './address.js'

export interface BalanceResult {
  address: string
  free: string
  reserved: string
  frozen: string
  total: string
  network: NetworkId
  symbol: string
}

function formatShannons(shannons: bigint): string {
  const ai3 = shannonsToAi3(shannons)
  return ai3.toString()
}

export async function queryBalance(
  api: ApiPromise,
  addr: string,
  network: NetworkId,
): Promise<BalanceResult> {
  const normalized = normalizeAddress(addr)
  const bal = await balance(api, normalized)

  const free = bal.free
  const reserved = bal.reserved
  const frozen = bal.frozen
  const total = free + reserved

  return {
    address: normalized,
    free: formatShannons(free),
    reserved: formatShannons(reserved),
    frozen: formatShannons(frozen),
    total: formatShannons(total),
    network,
    symbol: tokenSymbol(network),
  }
}
