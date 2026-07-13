import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { deriveEvmKey, getMemoryChainAddress } from '../lib/evm.js'
import { ethers } from 'ethers'

// Well-known test mnemonic (DO NOT use for real funds)
const TEST_MNEMONIC = 'test test test test test test test test test test test junk'

describe('deriveEvmKey', () => {
  it('returns a valid EVM address', () => {
    const result = deriveEvmKey(TEST_MNEMONIC)
    expect(ethers.isAddress(result.address)).toBe(true)
  })

  it('returns a valid private key', () => {
    const result = deriveEvmKey(TEST_MNEMONIC)
    expect(result.privateKey).toMatch(/^0x[0-9a-f]{64}$/i)
  })

  it('is deterministic — same mnemonic always produces same keys', () => {
    const a = deriveEvmKey(TEST_MNEMONIC)
    const b = deriveEvmKey(TEST_MNEMONIC)
    expect(a.address).toBe(b.address)
    expect(a.privateKey).toBe(b.privateKey)
  })

  it('different mnemonics produce different keys', () => {
    const other = 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about'
    const a = deriveEvmKey(TEST_MNEMONIC)
    const b = deriveEvmKey(other)
    expect(a.address).not.toBe(b.address)
  })

  it('derived private key corresponds to the derived address', () => {
    const result = deriveEvmKey(TEST_MNEMONIC)
    const wallet = new ethers.Wallet(result.privateKey)
    expect(wallet.address).toBe(result.address)
  })
})

describe('getMemoryChainAddress', () => {
  const originalEnv = process.env.AUTO_RESPAWN_CONTRACT_ADDRESS

  beforeEach(() => {
    delete process.env.AUTO_RESPAWN_CONTRACT_ADDRESS
  })

  afterEach(() => {
    if (originalEnv !== undefined) {
      process.env.AUTO_RESPAWN_CONTRACT_ADDRESS = originalEnv
    } else {
      delete process.env.AUTO_RESPAWN_CONTRACT_ADDRESS
    }
  })

  it('returns mainnet contract address', () => {
    const addr = getMemoryChainAddress('mainnet')
    expect(addr).toBe('0x51DAedAFfFf631820a4650a773096A69cB199A3c')
  })

  it('returns chronos contract address', () => {
    const addr = getMemoryChainAddress('chronos')
    expect(addr).toBe('0x5fa47C8F3B519deF692BD9C87179d69a6f4EBf11')
  })

  it('env var overrides default addresses', () => {
    process.env.AUTO_RESPAWN_CONTRACT_ADDRESS = '0x1234567890123456789012345678901234567890'
    expect(getMemoryChainAddress('mainnet')).toBe('0x1234567890123456789012345678901234567890')
    expect(getMemoryChainAddress('chronos')).toBe('0x1234567890123456789012345678901234567890')
  })
})
