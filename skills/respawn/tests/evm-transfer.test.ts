import { describe, it, expect, vi } from 'vitest'
import { ethers } from 'ethers'
import { transferEvmTokens } from '../lib/evm-transfer.js'

/**
 * EVM transfer pre-check tests.
 *
 * Mocks the ethers Wallet/Provider to test the balance pre-check logic,
 * gas price handling, error messages, and result formatting — without
 * hitting a real RPC endpoint.
 */

const TEST_TO = '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'
const TEST_FROM = '0x1234567890123456789012345678901234567890'

/**
 * Build a mock ethers.Wallet with a mock provider.
 * Override individual provider methods as needed per test.
 */
function createMockSigner(overrides: {
  balance?: bigint
  gasPrice?: bigint | null
  maxFeePerGas?: bigint | null
  sendTransaction?: () => Promise<unknown>
} = {}) {
  const balance = overrides.balance ?? 10_000_000_000_000_000_000n // 10 AI3 default
  const gasPrice = overrides.gasPrice !== undefined ? overrides.gasPrice : 1_000_000_000n // 1 gwei default
  const maxFeePerGas = overrides.maxFeePerGas !== undefined ? overrides.maxFeePerGas : null

  const mockProvider = {
    getBalance: vi.fn().mockResolvedValue(balance),
    getFeeData: vi.fn().mockResolvedValue({
      gasPrice,
      maxFeePerGas,
      maxPriorityFeePerGas: null,
    }),
  }

  const mockSigner = {
    address: TEST_FROM,
    provider: mockProvider,
    getAddress: vi.fn().mockResolvedValue(TEST_FROM),
    sendTransaction: overrides.sendTransaction ?? vi.fn().mockResolvedValue({
      wait: vi.fn().mockResolvedValue({
        status: 1,
        hash: '0xabcdef1234567890',
        blockNumber: 42,
        blockHash: '0xblockhash',
        gasUsed: 21000n,
      }),
    }),
  } as unknown as ethers.Wallet

  return mockSigner
}

describe('transferEvmTokens', () => {
  it('throws when signer has no provider', async () => {
    const signerNoProvider = { provider: null } as unknown as ethers.Wallet

    await expect(transferEvmTokens(signerNoProvider, TEST_TO, '1', 'chronos'))
      .rejects.toThrow(/Signer has no provider/)
  })

  it('throws on insufficient balance with detailed error message', async () => {
    // Balance of 0.5 AI3, trying to send 1 AI3
    const signer = createMockSigner({
      balance: 500_000_000_000_000_000n, // 0.5 AI3
    })

    await expect(transferEvmTokens(signer, TEST_TO, '1', 'chronos'))
      .rejects.toThrow(/Insufficient EVM balance/)
  })

  it('insufficient balance error includes amounts and symbol', async () => {
    const signer = createMockSigner({
      balance: 500_000_000_000_000_000n, // 0.5 AI3
    })

    try {
      await transferEvmTokens(signer, TEST_TO, '1', 'chronos')
      expect.unreachable('should have thrown')
    } catch (err) {
      const msg = (err as Error).message
      expect(msg).toContain('tAI3')       // correct symbol for chronos
      expect(msg).toContain('1')           // amount attempted
      expect(msg).toContain('0.5')         // available balance
    }
  })

  it('insufficient balance error uses mainnet symbol', async () => {
    const signer = createMockSigner({
      balance: 500_000_000_000_000_000n,
    })

    await expect(transferEvmTokens(signer, TEST_TO, '1', 'mainnet'))
      .rejects.toThrow(/AI3/)
  })

  it('throws when gas price is unavailable', async () => {
    const signer = createMockSigner({
      gasPrice: null,
      maxFeePerGas: null,
    })

    await expect(transferEvmTokens(signer, TEST_TO, '1', 'chronos'))
      .rejects.toThrow(/Unable to determine gas price/)
  })

  it('falls back to maxFeePerGas when gasPrice is null', async () => {
    // gasPrice null, maxFeePerGas available — should not throw gas price error
    // but will fail on balance check if balance is too low
    const signer = createMockSigner({
      balance: 10_000_000_000_000_000_000n, // 10 AI3
      gasPrice: null,
      maxFeePerGas: 1_000_000_000n, // 1 gwei
    })

    const result = await transferEvmTokens(signer, TEST_TO, '1', 'chronos')
    expect(result.success).toBe(true)
  })

  it('succeeds and returns correct result shape', async () => {
    const signer = createMockSigner()

    const result = await transferEvmTokens(signer, TEST_TO, '2.5', 'chronos')

    expect(result.success).toBe(true)
    expect(result.transactionHash).toBe('0xabcdef1234567890')
    expect(result.blockNumber).toBe(42)
    expect(result.from).toBe(TEST_FROM)
    expect(result.to).toBe(TEST_TO)
    expect(result.amount).toBe('2.5')
    expect(result.symbol).toBe('tAI3')
    expect(result.network).toBe('chronos')
    expect(result.warning).toBeUndefined()
  })

  it('includes mainnet warning', async () => {
    const signer = createMockSigner()

    const result = await transferEvmTokens(signer, TEST_TO, '1', 'mainnet')

    expect(result.warning).toContain('mainnet')
    expect(result.warning).toContain('real AI3')
  })

  it('no warning on chronos', async () => {
    const signer = createMockSigner()

    const result = await transferEvmTokens(signer, TEST_TO, '1', 'chronos')

    expect(result.warning).toBeUndefined()
  })

  it('throws when receipt is null', async () => {
    const signer = createMockSigner({
      sendTransaction: vi.fn().mockResolvedValue({
        wait: vi.fn().mockResolvedValue(null),
      }),
    })

    await expect(transferEvmTokens(signer, TEST_TO, '1', 'chronos'))
      .rejects.toThrow(/no receipt/)
  })
})
