import { address as encodeAddress, decode } from '@autonomys/auto-utils'
import { ethers } from 'ethers'

/**
 * Non-throwing check: is this string a valid consensus-layer address?
 */
export function isConsensusAddress(input: string): boolean {
  if (!input.startsWith('su') && !input.startsWith('5')) return false
  try {
    decode(input)
    return true
  } catch {
    return false
  }
}

/**
 * Non-throwing check: is this string a valid EVM address?
 * Requires the 0x prefix to stay consistent with normalizeEvmAddress.
 */
export function isEvmAddress(input: string): boolean {
  return input.startsWith('0x') && ethers.isAddress(input)
}

/**
 * Validate and normalise a consensus-layer address.
 *
 * Accepted formats:
 *   - su...  (Autonomys SS58 prefix 6094) — passed through
 *   - 5...   (Substrate generic prefix 42) — converted to su...
 *
 * Anything else is rejected with a clear error message.
 */
export function normalizeAddress(input: string): string {
  // Quick prefix check before we attempt decoding
  if (!input.startsWith('su') && !input.startsWith('5')) {
    throw new Error(
      `Invalid address prefix: "${input.slice(0, 6)}…". ` +
        'Expected an Autonomys address (su…) or a Substrate address (5…).',
    )
  }

  // Attempt to decode → re-encode at Autonomys prefix 6094
  let publicKey: Uint8Array
  try {
    publicKey = decode(input)
  } catch {
    throw new Error(
      `Invalid address: "${input}". Could not decode as a valid SS58 address.`,
    )
  }

  // Re-encode with Autonomys prefix (6094 is the default in auto-utils)
  const normalized = encodeAddress(publicKey)

  return normalized
}

/**
 * Validate and normalise an EVM address.
 *
 * Accepted format: 0x... (42-character hex string)
 * Returns the checksummed EVM address.
 */
export function normalizeEvmAddress(input: string): string {
  if (!input.startsWith('0x')) {
    throw new Error(
      `Invalid EVM address: "${input.slice(0, 10)}…". Expected an address starting with 0x.`,
    )
  }

  try {
    return ethers.getAddress(input) // Returns checksummed address
  } catch {
    throw new Error(
      `Invalid EVM address: "${input}". Not a valid Ethereum address.`,
    )
  }
}
