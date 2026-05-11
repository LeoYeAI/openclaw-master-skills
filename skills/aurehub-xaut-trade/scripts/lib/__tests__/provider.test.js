import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { FallbackProvider, createProvider } from '../provider.js';

describe('FallbackProvider', () => {
  it('uses primary URL by default', async () => {
    const provider = new FallbackProvider('https://primary.example.com');
    provider._rawSend = vi.fn().mockResolvedValue('0x1');

    const result = await provider.send('eth_blockNumber', []);

    expect(result).toBe('0x1');
    expect(provider._rawSend).toHaveBeenCalledWith(
      'https://primary.example.com',
      'eth_blockNumber',
      []
    );
  });

  it('throws when no primary URL is provided', () => {
    expect(() => new FallbackProvider()).toThrow(/primary/i);
    expect(() => new FallbackProvider('')).toThrow(/primary/i);
  });

  it('falls back on retriable error codes (429, 502, 503)', async () => {
    const provider = new FallbackProvider('https://primary.example.com', [
      'https://fallback1.example.com',
    ]);

    let callCount = 0;
    provider._rawSend = vi.fn().mockImplementation(async (url) => {
      callCount++;
      if (url === 'https://primary.example.com') {
        const err = new Error('Too Many Requests');
        err.status = 429;
        throw err;
      }
      return '0x2';
    });

    const result = await provider.send('eth_blockNumber', []);

    expect(result).toBe('0x2');
    expect(provider._rawSend).toHaveBeenCalledTimes(2);
    expect(provider._rawSend).toHaveBeenNthCalledWith(
      1,
      'https://primary.example.com',
      'eth_blockNumber',
      []
    );
    expect(provider._rawSend).toHaveBeenNthCalledWith(
      2,
      'https://fallback1.example.com',
      'eth_blockNumber',
      []
    );
  });

  it('is session-sticky: after fallback success, primary URL updates', async () => {
    const provider = new FallbackProvider('https://primary.example.com', [
      'https://fallback1.example.com',
    ]);

    provider._rawSend = vi.fn().mockImplementation(async (url) => {
      if (url === 'https://primary.example.com') {
        const err = new Error('Service Unavailable');
        err.status = 503;
        throw err;
      }
      return '0x3';
    });

    // First call triggers fallback
    await provider.send('eth_blockNumber', []);

    // Reset mock to track next call
    provider._rawSend.mockClear();
    provider._rawSend.mockResolvedValue('0x4');

    // Second call should use the new primary (fallback1)
    await provider.send('eth_blockNumber', []);

    expect(provider._rawSend).toHaveBeenCalledWith(
      'https://fallback1.example.com',
      'eth_blockNumber',
      []
    );
  });

  it('throws after all URLs are exhausted', async () => {
    const provider = new FallbackProvider('https://primary.example.com', [
      'https://fallback1.example.com',
      'https://fallback2.example.com',
    ]);

    provider._rawSend = vi.fn().mockImplementation(async (url) => {
      const err = new Error('Bad Gateway');
      err.status = 502;
      throw err;
    });

    await expect(provider.send('eth_blockNumber', [])).rejects.toThrow();
  });

  it('call() routes through _sendWithFallback with eth_call', async () => {
    const provider = new FallbackProvider('https://primary.example.com');
    provider._rawSend = vi.fn().mockResolvedValue('0xresult');

    const tx = { to: '0xabc', data: '0x1234' };
    const result = await provider.call(tx);

    expect(result).toBe('0xresult');
    expect(provider._rawSend).toHaveBeenCalledWith(
      'https://primary.example.com',
      'eth_call',
      [tx, 'latest']
    );
  });

  it('getBalance() routes through _sendWithFallback with eth_getBalance', async () => {
    const provider = new FallbackProvider('https://primary.example.com');
    provider._rawSend = vi.fn().mockResolvedValue('0xde0b6b3a7640000');

    const address = '0xabcdef1234567890abcdef1234567890abcdef12';
    const result = await provider.getBalance(address);

    expect(result).toBe('0xde0b6b3a7640000');
    expect(provider._rawSend).toHaveBeenCalledWith(
      'https://primary.example.com',
      'eth_getBalance',
      [address, 'latest']
    );
  });

  it('getBlockNumber() routes through _sendWithFallback', async () => {
    const provider = new FallbackProvider('https://primary.example.com');
    provider._rawSend = vi.fn().mockResolvedValue('0x10d4f');

    const result = await provider.getBlockNumber();

    expect(result).toBe('0x10d4f');
    expect(provider._rawSend).toHaveBeenCalledWith(
      'https://primary.example.com',
      'eth_blockNumber',
      []
    );
  });

  it('falls back on timeout and connection-refused errors', async () => {
    const provider = new FallbackProvider('https://primary.example.com', [
      'https://fallback1.example.com',
    ]);

    provider._rawSend = vi.fn().mockImplementation(async (url) => {
      if (url === 'https://primary.example.com') {
        const err = new Error('Connection refused');
        err.code = 'ECONNREFUSED';
        throw err;
      }
      return '0x5';
    });

    const result = await provider.send('eth_blockNumber', []);
    expect(result).toBe('0x5');
  });

  it('times out individual RPC requests and retries fallback', async () => {
    const provider = new FallbackProvider(
      'https://primary.example.com',
      ['https://fallback1.example.com'],
      5
    );

    provider._rawSend = vi.fn().mockImplementation(async (url) => {
      if (url === 'https://primary.example.com') {
        const err = new Error('RPC request timeout after 5ms');
        err.code = 'ETIMEDOUT';
        throw err;
      }
      return '0x6';
    });

    const result = await provider.send('eth_blockNumber', []);
    expect(result).toBe('0x6');
    expect(provider._rawSend).toHaveBeenCalledTimes(2);
  });

  it('does not fall back on non-retriable errors', async () => {
    const provider = new FallbackProvider('https://primary.example.com', [
      'https://fallback1.example.com',
    ]);

    provider._rawSend = vi.fn().mockImplementation(async () => {
      const err = new Error('Invalid params');
      err.code = -32602;
      throw err;
    });

    await expect(provider.send('eth_call', [{}])).rejects.toThrow('Invalid params');
    // Should only have tried primary, not fallback
    expect(provider._rawSend).toHaveBeenCalledTimes(1);
  });

  it('getEthersProvider() returns underlying JsonRpcProvider', () => {
    const provider = new FallbackProvider('https://primary.example.com');
    const ethersProvider = provider.getEthersProvider();
    // Should be an object with expected ethers Provider interface
    expect(ethersProvider).toBeDefined();
    expect(typeof ethersProvider.getBlockNumber).toBe('function');
  });
});

describe('createProvider', () => {
  it('creates provider from env with primary and fallbacks', () => {
    const env = {
      ETH_RPC_URL: 'https://primary.example.com',
      ETH_RPC_URL_FALLBACK: 'https://fb1.example.com,https://fb2.example.com',
    };

    const provider = createProvider(env);
    expect(provider).toBeInstanceOf(FallbackProvider);
  });

  it('creates provider with only primary when no fallback env set', () => {
    const env = { ETH_RPC_URL: 'https://primary.example.com' };
    const provider = createProvider(env);
    expect(provider).toBeInstanceOf(FallbackProvider);
  });

  it('throws when ETH_RPC_URL is missing from env', () => {
    const originalHome = process.env.HOME;
    process.env.HOME = mkdtempSync(join(tmpdir(), 'xaut-provider-test-'));
    try {
      expect(() => createProvider({})).toThrow(/ETH_RPC_URL/i);
    } finally {
      process.env.HOME = originalHome;
    }
  });
});
