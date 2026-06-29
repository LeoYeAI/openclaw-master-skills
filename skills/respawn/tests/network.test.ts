import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { resolveNetwork, tokenSymbol, isMainnet } from '../lib/network.js'

describe('resolveNetwork', () => {
  const originalEnv = process.env.AUTO_RESPAWN_NETWORK

  beforeEach(() => {
    delete process.env.AUTO_RESPAWN_NETWORK
  })

  // Restore after all tests
  afterEach(() => {
    if (originalEnv !== undefined) {
      process.env.AUTO_RESPAWN_NETWORK = originalEnv
    } else {
      delete process.env.AUTO_RESPAWN_NETWORK
    }
  })

  it('returns chronos when no flag or env is set', () => {
    expect(resolveNetwork()).toBe('chronos')
  })

  it('returns the flag value when provided', () => {
    expect(resolveNetwork('mainnet')).toBe('mainnet')
    expect(resolveNetwork('chronos')).toBe('chronos')
  })

  it('flag takes precedence over env var', () => {
    process.env.AUTO_RESPAWN_NETWORK = 'mainnet'
    expect(resolveNetwork('chronos')).toBe('chronos')
  })

  it('falls back to env var when no flag', () => {
    process.env.AUTO_RESPAWN_NETWORK = 'mainnet'
    expect(resolveNetwork()).toBe('mainnet')
  })

  it('throws on invalid flag value', () => {
    expect(() => resolveNetwork('testnet')).toThrow(/Unknown network/)
  })

  it('throws on invalid env var value', () => {
    process.env.AUTO_RESPAWN_NETWORK = 'invalid'
    expect(() => resolveNetwork()).toThrow(/Unknown AUTO_RESPAWN_NETWORK/)
  })
})

describe('tokenSymbol', () => {
  it('returns tAI3 for chronos', () => {
    expect(tokenSymbol('chronos')).toBe('tAI3')
  })

  it('returns AI3 for mainnet', () => {
    expect(tokenSymbol('mainnet')).toBe('AI3')
  })
})

describe('isMainnet', () => {
  it('returns true for mainnet', () => {
    expect(isMainnet('mainnet')).toBe(true)
  })

  it('returns false for chronos', () => {
    expect(isMainnet('chronos')).toBe(false)
  })
})
