import { describe, it, expect, vi } from 'vitest';
import { getBalance, getAllowance, approve } from '../erc20.js';

function mockProvider(returnValue) {
  return { call: vi.fn().mockResolvedValue(returnValue) };
}

function mockSigner(address = '0x' + '1'.repeat(40)) {
  return {
    getAddress: vi.fn().mockResolvedValue(address),
    sendTransaction: vi.fn().mockResolvedValue({
      hash: '0xabc',
      wait: vi.fn().mockResolvedValue({ status: 1 }),
    }),
    provider: mockProvider('0x' + '0'.repeat(64)),
  };
}

const TOKEN_USDT = { address: '0xdAC17F958D2ee523a2206206994597C13D831ec7', decimals: 6 };
const TOKEN_XAUT = { address: '0x68749665FF8D2d112Fa859AA293F07A622782F38', decimals: 6 };

describe('getBalance', () => {
  it('calls provider.call and formats result with token decimals', async () => {
    // 1000000000 raw / 10^6 = 1000.0
    const raw = '0x' + (1000000000n).toString(16).padStart(64, '0');
    const provider = mockProvider(raw);

    const result = await getBalance(TOKEN_USDT, '0x' + '2'.repeat(40), provider);

    expect(provider.call).toHaveBeenCalledOnce();
    const callArg = provider.call.mock.calls[0][0];
    expect(callArg.to).toBe(TOKEN_USDT.address);
    expect(typeof callArg.data).toBe('string');
    expect(result).toBe('1000.0');
  });

  it('returns "0.0" when balance is zero', async () => {
    const provider = mockProvider('0x' + '0'.repeat(64));
    const result = await getBalance(TOKEN_XAUT, '0x' + '3'.repeat(40), provider);
    expect(result).toBe('0.0');
  });
});

describe('getAllowance', () => {
  it('returns formatted allowance value', async () => {
    // 500000 raw / 10^6 = 0.5
    const raw = '0x' + (500000n).toString(16).padStart(64, '0');
    const provider = mockProvider(raw);
    const owner = '0x' + '2'.repeat(40);
    const spender = '0x' + '3'.repeat(40);

    const result = await getAllowance(TOKEN_USDT, owner, spender, provider);

    expect(provider.call).toHaveBeenCalledOnce();
    const callArg = provider.call.mock.calls[0][0];
    expect(callArg.to).toBe(TOKEN_USDT.address);
    expect(result).toBe('0.5');
  });
});

describe('approve', () => {
  it('sends one transaction when requiresResetApprove is not set', async () => {
    const signer = mockSigner();
    const spender = '0x' + '3'.repeat(40);

    const result = await approve(TOKEN_USDT, spender, '1000', signer);

    expect(signer.sendTransaction).toHaveBeenCalledOnce();
    const txArg = signer.sendTransaction.mock.calls[0][0];
    expect(txArg.to).toBe(TOKEN_USDT.address);
    expect(typeof txArg.data).toBe('string');
    expect(result).toEqual({ hash: '0xabc' });
  });

  it('sends two transactions (reset + approve) when requiresResetApprove is true', async () => {
    const signer = mockSigner();
    const spender = '0x' + '3'.repeat(40);

    const result = await approve(TOKEN_USDT, spender, '1000', signer, { requiresResetApprove: true });

    expect(signer.sendTransaction).toHaveBeenCalledTimes(2);

    // First call: approve(spender, 0)
    const resetTxArg = signer.sendTransaction.mock.calls[0][0];
    expect(resetTxArg.to).toBe(TOKEN_USDT.address);

    // Second call: approve(spender, amount)
    const approveTxArg = signer.sendTransaction.mock.calls[1][0];
    expect(approveTxArg.to).toBe(TOKEN_USDT.address);

    expect(result).toEqual({ hash: '0xabc' });
  });
});
