import { describe, it, expect } from 'vitest'
import { isConsensusAddress, isEvmAddress, normalizeAddress, normalizeEvmAddress } from '../lib/address.js'

// Known valid addresses for testing
const VALID_EVM = '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'
const VALID_EVM_LOWER = '0xd8da6bf26964af9d7eed9e03e53415d37aa96045'

// Derived from test mnemonic "test test test test test test test test test test test junk"
const VALID_SU_ADDRESS = 'sufmoyKii8Se1QaUz8wQSN9YBypcNtpi2d6XKPkpCxr3kZC5m'
const VALID_5_ADDRESS = '5GmS1wtCfR4tK5SSgnZbVT4kYw5W8NmxmijcsxCQE6oLW6A8'

describe('isConsensusAddress', () => {
  it('accepts valid su... address', () => {
    expect(isConsensusAddress(VALID_SU_ADDRESS)).toBe(true)
  })

  it('accepts valid 5... address', () => {
    expect(isConsensusAddress(VALID_5_ADDRESS)).toBe(true)
  })

  it('rejects EVM addresses', () => {
    expect(isConsensusAddress(VALID_EVM)).toBe(false)
  })

  it('rejects empty string', () => {
    expect(isConsensusAddress('')).toBe(false)
  })

  it('rejects random strings', () => {
    expect(isConsensusAddress('hello')).toBe(false)
  })
})

describe('isEvmAddress', () => {
  it('accepts valid checksummed EVM address', () => {
    expect(isEvmAddress(VALID_EVM)).toBe(true)
  })

  it('accepts valid lowercase EVM address', () => {
    expect(isEvmAddress(VALID_EVM_LOWER)).toBe(true)
  })

  it('rejects addresses without 0x prefix', () => {
    // Must require 0x prefix to stay consistent with normalizeEvmAddress
    expect(isEvmAddress('d8dA6BF26964aF9D7eEd9e03E53415D37aA96045')).toBe(false)
  })

  it('rejects too-short addresses', () => {
    expect(isEvmAddress('0x1234')).toBe(false)
  })

  it('rejects empty string', () => {
    expect(isEvmAddress('')).toBe(false)
  })

  it('rejects consensus addresses', () => {
    expect(isEvmAddress('su1234567890')).toBe(false)
  })
})

describe('normalizeAddress', () => {
  it('passes through a valid su... address', () => {
    const result = normalizeAddress(VALID_SU_ADDRESS)
    expect(result).toBe(VALID_SU_ADDRESS)
  })

  it('converts a 5... address to su... format', () => {
    const result = normalizeAddress(VALID_5_ADDRESS)
    expect(result).toMatch(/^su/)
    // Both formats represent the same public key, so normalising the 5... address
    // should produce the same su... address
    expect(result).toBe(VALID_SU_ADDRESS)
  })

  it('throws on EVM addresses', () => {
    expect(() => normalizeAddress(VALID_EVM)).toThrow(/Invalid address prefix/)
  })

  it('throws on random strings', () => {
    expect(() => normalizeAddress('hello')).toThrow(/Invalid address prefix/)
  })

  it('throws on address with valid prefix but invalid encoding', () => {
    expect(() => normalizeAddress('su00000000000000000000')).toThrow(/Could not decode/)
  })
})

describe('normalizeEvmAddress', () => {
  it('checksums a valid lowercase address', () => {
    const result = normalizeEvmAddress(VALID_EVM_LOWER)
    expect(result).toBe(VALID_EVM)
  })

  it('passes through an already-checksummed address', () => {
    const result = normalizeEvmAddress(VALID_EVM)
    expect(result).toBe(VALID_EVM)
  })

  it('throws on missing 0x prefix', () => {
    expect(() => normalizeEvmAddress('d8dA6BF26964aF9D7eEd9e03E53415D37aA96045'))
      .toThrow(/Expected an address starting with 0x/)
  })

  it('throws on invalid hex', () => {
    expect(() => normalizeEvmAddress('0xZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ'))
      .toThrow(/Not a valid Ethereum address/)
  })
})
