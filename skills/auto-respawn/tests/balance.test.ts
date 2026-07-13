import { describe, it, expect, vi } from 'vitest'
import type { BalanceResult } from '../lib/balance.js'

/**
 * Balance formatting tests.
 *
 * Mocks the @autonomys/auto-consensus `balance()` function to avoid
 * needing a real RPC connection. Tests that queryBalance correctly
 * normalises addresses, formats shannons → AI3, and labels the network.
 */

// Mock the consensus balance call — returns raw bigint values
vi.mock('@autonomys/auto-consensus', () => ({
  balance: vi.fn(),
}))

// We need to import after mocking
const { balance: mockBalance } = await import('@autonomys/auto-consensus')
const { queryBalance } = await import('../lib/balance.js')

// A valid su... address derived from the well-known test mnemonic
// "test test test test test test test test test test test junk"
const TEST_ADDRESS = 'sufmoyKii8Se1QaUz8wQSN9YBypcNtpi2d6XKPkpCxr3kZC5m'

describe('queryBalance', () => {
  it('formats shannons to AI3 correctly for non-zero balances', async () => {
    vi.mocked(mockBalance).mockResolvedValue({
      free: 1_500_000_000_000_000_000n,   // 1.5 AI3
      reserved: 500_000_000_000_000_000n,  // 0.5 AI3
      frozen: 0n,
      flags: 0n,
    })

    // Create a minimal mock API object — queryBalance only passes it through to balance()
    const mockApi = {} as Parameters<typeof queryBalance>[0]

    const result: BalanceResult = await queryBalance(mockApi, TEST_ADDRESS, 'chronos')

    expect(result.free).toBe('1.5')
    expect(result.reserved).toBe('0.5')
    expect(result.frozen).toBe('0')
    expect(result.total).toBe('2')
    expect(result.symbol).toBe('tAI3')
    expect(result.network).toBe('chronos')
  })

  it('handles zero balances', async () => {
    vi.mocked(mockBalance).mockResolvedValue({
      free: 0n,
      reserved: 0n,
      frozen: 0n,
      flags: 0n,
    })

    const mockApi = {} as Parameters<typeof queryBalance>[0]
    const result = await queryBalance(mockApi, TEST_ADDRESS, 'mainnet')

    expect(result.free).toBe('0')
    expect(result.reserved).toBe('0')
    expect(result.total).toBe('0')
    expect(result.symbol).toBe('AI3')
    expect(result.network).toBe('mainnet')
  })

  it('formats large balances without precision loss', async () => {
    // 1,000,000 AI3
    vi.mocked(mockBalance).mockResolvedValue({
      free: 1_000_000_000_000_000_000_000_000n,
      reserved: 0n,
      frozen: 0n,
      flags: 0n,
    })

    const mockApi = {} as Parameters<typeof queryBalance>[0]
    const result = await queryBalance(mockApi, TEST_ADDRESS, 'chronos')

    expect(result.free).toBe('1000000')
    expect(result.total).toBe('1000000')
  })

  it('formats fractional balances', async () => {
    // 0.000000000000000001 AI3 (1 shannon)
    vi.mocked(mockBalance).mockResolvedValue({
      free: 1n,
      reserved: 0n,
      frozen: 0n,
      flags: 0n,
    })

    const mockApi = {} as Parameters<typeof queryBalance>[0]
    const result = await queryBalance(mockApi, TEST_ADDRESS, 'chronos')

    // shannonsToAi3 should handle the smallest unit
    expect(Number(result.free)).toBeGreaterThan(0)
    expect(Number(result.free)).toBeLessThan(0.001)
  })

  it('uses correct symbol per network', async () => {
    vi.mocked(mockBalance).mockResolvedValue({ free: 0n, reserved: 0n, frozen: 0n, flags: 0n })

    const mockApi = {} as Parameters<typeof queryBalance>[0]

    const chronos = await queryBalance(mockApi, TEST_ADDRESS, 'chronos')
    expect(chronos.symbol).toBe('tAI3')

    const mainnet = await queryBalance(mockApi, TEST_ADDRESS, 'mainnet')
    expect(mainnet.symbol).toBe('AI3')
  })

  it('normalises the address in the result', async () => {
    vi.mocked(mockBalance).mockResolvedValue({ free: 0n, reserved: 0n, frozen: 0n, flags: 0n })

    const mockApi = {} as Parameters<typeof queryBalance>[0]
    const result = await queryBalance(mockApi, TEST_ADDRESS, 'chronos')

    // The returned address should be a valid su... address
    expect(result.address).toMatch(/^su/)
  })

  it('passes the normalised address to the SDK balance call', async () => {
    vi.mocked(mockBalance).mockResolvedValue({ free: 0n, reserved: 0n, frozen: 0n, flags: 0n })

    const mockApi = {} as Parameters<typeof queryBalance>[0]
    await queryBalance(mockApi, TEST_ADDRESS, 'chronos')

    expect(mockBalance).toHaveBeenCalledWith(mockApi, expect.stringMatching(/^su/))
  })
})
