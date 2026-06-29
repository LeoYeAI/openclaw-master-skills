import { describe, it, expect } from 'vitest'
import { parseArgs, validateAmount } from '../lib/cli.js'

describe('parseArgs', () => {
  // Helper: simulate process.argv with node + script prefix
  const argv = (...args: string[]) => ['node', 'auto-respawn.ts', ...args]

  it('extracts a simple command', () => {
    const result = parseArgs(argv('balance', 'my-wallet'))
    expect(result.command).toBe('balance')
    expect(result.positional).toEqual(['my-wallet'])
    expect(result.subcommand).toBeUndefined()
  })

  it('extracts wallet subcommand', () => {
    const result = parseArgs(argv('wallet', 'create', '--name', 'test'))
    expect(result.command).toBe('wallet')
    expect(result.subcommand).toBe('create')
    expect(result.flags.name).toBe('test')
  })

  it('parses key-value flags', () => {
    const result = parseArgs(argv('transfer', '--from', 'alice', '--to', 'bob', '--amount', '1.5'))
    expect(result.flags).toEqual({ from: 'alice', to: 'bob', amount: '1.5' })
  })

  it('parses boolean flags', () => {
    const result = parseArgs(argv('wallet', 'list', '--verbose'))
    expect(result.flags.verbose).toBe('true')
  })

  it('handles mixed flags and positional args', () => {
    const result = parseArgs(argv('gethead', '0xabc', '--network', 'mainnet'))
    expect(result.command).toBe('gethead')
    expect(result.positional).toEqual(['0xabc'])
    expect(result.flags.network).toBe('mainnet')
  })

  it('returns empty command for empty argv', () => {
    const result = parseArgs(argv())
    expect(result.command).toBe('')
    expect(result.positional).toEqual([])
    expect(result.flags).toEqual({})
  })

  it('does not treat non-wallet commands as having subcommands', () => {
    const result = parseArgs(argv('balance', 'my-wallet', '--network', 'chronos'))
    expect(result.command).toBe('balance')
    expect(result.subcommand).toBeUndefined()
    expect(result.positional).toEqual(['my-wallet'])
  })

  it('treats flag-like wallet subcommand as a flag', () => {
    const result = parseArgs(argv('wallet', '--name', 'test'))
    expect(result.command).toBe('wallet')
    expect(result.subcommand).toBeUndefined()
    expect(result.flags.name).toBe('test')
  })

  it('handles consecutive boolean flags', () => {
    const result = parseArgs(argv('test', '--verbose', '--dry-run'))
    expect(result.flags.verbose).toBe('true')
    expect(result.flags['dry-run']).toBe('true')
  })
})

describe('validateAmount', () => {
  it('accepts valid positive amounts', () => {
    expect(() => validateAmount('1')).not.toThrow()
    expect(() => validateAmount('0.5')).not.toThrow()
    expect(() => validateAmount('100.123')).not.toThrow()
  })

  it('rejects zero', () => {
    expect(() => validateAmount('0')).toThrow(/Must be a positive number/)
  })

  it('rejects negative amounts', () => {
    expect(() => validateAmount('-1')).toThrow(/Must be a positive number/)
  })

  it('rejects non-numeric strings', () => {
    expect(() => validateAmount('abc')).toThrow(/Must be a positive number/)
    expect(() => validateAmount('')).toThrow(/Must be a positive number/)
  })

  it('rejects Infinity', () => {
    expect(() => validateAmount('Infinity')).toThrow(/Must be a positive number/)
  })

  it('enforces minimum when provided', () => {
    expect(() => validateAmount('0.5', 1)).toThrow(/below the minimum/)
  })

  it('accepts amounts at the minimum', () => {
    expect(() => validateAmount('1', 1)).not.toThrow()
  })

  it('accepts amounts above the minimum', () => {
    expect(() => validateAmount('2.5', 1)).not.toThrow()
  })
})
