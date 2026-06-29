import { describe, it, expect, vi } from 'vitest'
import { queryEvmBalance } from '../lib/evm-balance.js'
import { ethers } from 'ethers'

/**
 * EVM balance tests.
 *
 * Mocks ethers.Provider.getBalance() to avoid needing a real RPC connection.
 * Tests formatting, zero-balance hints, and network labelling.
 */

function createMockProvider(balanceWei: bigint) {
  return {
    getBalance: vi.fn().mockResolvedValue(balanceWei),
  } as unknown as ethers.Provider
}

const TEST_EVM_ADDRESS = '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'

describe('queryEvmBalance', () => {
  it('formats wei balance to ether string', async () => {
    // 2.5 ETH/AI3 in wei
    const provider = createMockProvider(2_500_000_000_000_000_000n)
    const result = await queryEvmBalance(provider, TEST_EVM_ADDRESS, 'chronos')

    expect(result.balance).toBe('2.5')
    expect(result.evmAddress).toBe(TEST_EVM_ADDRESS)
    expect(result.symbol).toBe('tAI3')
    expect(result.network).toBe('chronos')
    expect(result.hint).toBeUndefined()
  })

  it('includes hint when balance is zero', async () => {
    const provider = createMockProvider(0n)
    const result = await queryEvmBalance(provider, TEST_EVM_ADDRESS, 'chronos')

    expect(result.balance).toBe('0.0')
    expect(result.hint).toContain('No EVM balance')
    expect(result.hint).toContain('fund-evm')
    expect(result.hint).toContain('chronos')
  })

  it('uses correct symbol for mainnet', async () => {
    const provider = createMockProvider(1_000_000_000_000_000_000n)
    const result = await queryEvmBalance(provider, TEST_EVM_ADDRESS, 'mainnet')

    expect(result.symbol).toBe('AI3')
    expect(result.network).toBe('mainnet')
  })

  it('hint includes correct network name', async () => {
    const providerChronos = createMockProvider(0n)
    const chronos = await queryEvmBalance(providerChronos, TEST_EVM_ADDRESS, 'chronos')
    expect(chronos.hint).toContain('--network chronos')

    const providerMainnet = createMockProvider(0n)
    const mainnet = await queryEvmBalance(providerMainnet, TEST_EVM_ADDRESS, 'mainnet')
    expect(mainnet.hint).toContain('--network mainnet')
  })

  it('formats large balances correctly', async () => {
    // 1,000,000 AI3
    const provider = createMockProvider(1_000_000_000_000_000_000_000_000n)
    const result = await queryEvmBalance(provider, TEST_EVM_ADDRESS, 'chronos')

    expect(result.balance).toBe('1000000.0')
  })

  it('formats small balances correctly', async () => {
    // 0.001 AI3 = 10^15 wei
    const provider = createMockProvider(1_000_000_000_000_000n)
    const result = await queryEvmBalance(provider, TEST_EVM_ADDRESS, 'chronos')

    expect(result.balance).toBe('0.001')
  })

  it('no hint when balance is non-zero', async () => {
    const provider = createMockProvider(1n) // smallest positive balance
    const result = await queryEvmBalance(provider, TEST_EVM_ADDRESS, 'chronos')

    expect(result.hint).toBeUndefined()
  })

  it('calls provider.getBalance with the correct address', async () => {
    const provider = createMockProvider(0n)
    await queryEvmBalance(provider, TEST_EVM_ADDRESS, 'chronos')

    expect(provider.getBalance).toHaveBeenCalledWith(TEST_EVM_ADDRESS)
  })
})
