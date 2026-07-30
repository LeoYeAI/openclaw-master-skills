/**
 * Comprehensive unit tests for src/lib/relay.ts
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ethers, Wallet } from 'ethers';

// ---- Mock ethers.Contract at the module level ----
// We keep everything real except Contract, which we replace with a factory
// that returns whatever mockContractInstance is set to at call time.
let mockContractInstance: Record<string, any> = {};

vi.mock('ethers', async (importOriginal) => {
  const actual = await importOriginal<typeof import('ethers')>();
  return {
    ...actual,
    Contract: vi.fn((..._args: any[]) => mockContractInstance),
  };
});

// Import after vi.mock so the mock is in place
import {
  signRelayCall,
  getNonce,
  createValidityTimestamps,
  executeViaRelayer,
  executeRelayCallDirect,
  encodeExecutePayload,
  encodeExecuteBatchPayload,
  encodeSetDataPayload,
  encodeSetDataBatchPayload,
  checkRelayQuota,
  executeViaRelay,
  setDataViaRelay,
} from '../../src/lib/relay.js';

// Known private key for deterministic testing (Hardhat account #0)
const TEST_PRIVATE_KEY = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80';
const TEST_ADDRESS = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266';
const FAKE_KEY_MANAGER = '0x1234567890abcdef1234567890abcdef12345678';
const FAKE_UP_ADDRESS = '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd';

// ==================== createValidityTimestamps ====================

describe('createValidityTimestamps', () => {
  let dateNowSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    // Fix Date.now() to 1_700_000_000_000 ms => 1_700_000_000 seconds
    dateNowSpy = vi.spyOn(Date, 'now').mockReturnValue(1_700_000_000_000);
  });

  afterEach(() => {
    dateNowSpy.mockRestore();
  });

  it('should pack start and end times into a single uint256 with defaults', () => {
    const result = createValidityTimestamps();
    const now = 1_700_000_000;
    const expectedStart = BigInt(now);
    const expectedEnd = BigInt(now + 3600);

    const mask128 = (1n << 128n) - 1n;
    expect(result >> 128n).toBe(expectedStart);
    expect(result & mask128).toBe(expectedEnd);
  });

  it('should apply startOffset correctly', () => {
    const result = createValidityTimestamps(60, 3600);
    const now = 1_700_000_000;

    const mask128 = (1n << 128n) - 1n;
    expect(result >> 128n).toBe(BigInt(now + 60));
    expect(result & mask128).toBe(BigInt(now + 60 + 3600));
  });

  it('should apply custom duration correctly', () => {
    const result = createValidityTimestamps(0, 7200);
    const now = 1_700_000_000;

    const mask128 = (1n << 128n) - 1n;
    expect(result >> 128n).toBe(BigInt(now));
    expect(result & mask128).toBe(BigInt(now + 7200));
  });

  it('should return a bigint', () => {
    const result = createValidityTimestamps();
    expect(typeof result).toBe('bigint');
  });

  it('should handle both startOffset and duration together', () => {
    const result = createValidityTimestamps(300, 1800);
    const now = 1_700_000_000;
    const mask128 = (1n << 128n) - 1n;

    expect(result >> 128n).toBe(BigInt(now + 300));
    expect(result & mask128).toBe(BigInt(now + 300 + 1800));
  });

  it('should produce a non-zero value', () => {
    const result = createValidityTimestamps();
    expect(result).toBeGreaterThan(0n);
  });
});

// ==================== encodeExecutePayload ====================

describe('encodeExecutePayload', () => {
  it('should return a hex string', () => {
    const payload = encodeExecutePayload({
      operationType: 0,
      target: '0x0000000000000000000000000000000000000001',
      value: 0n,
      data: '0x',
    });

    expect(payload).toMatch(/^0x[0-9a-f]+$/i);
  });

  it('should start with the correct selector for execute(uint256,address,uint256,bytes)', () => {
    const iface = new ethers.Interface([
      'function execute(uint256 operationType, address target, uint256 value, bytes data) payable returns (bytes)',
    ]);
    const expectedSelector = iface.getFunction('execute')!.selector;

    const payload = encodeExecutePayload({
      operationType: 0,
      target: '0x0000000000000000000000000000000000000001',
      value: 0n,
      data: '0x',
    });

    expect(payload.slice(0, 10)).toBe(expectedSelector);
  });

  it('should encode non-zero value and data correctly', () => {
    const payload = encodeExecutePayload({
      operationType: 0,
      target: '0x0000000000000000000000000000000000000001',
      value: 1000000000000000000n,
      data: '0xdeadbeef',
    });

    expect(payload).toMatch(/^0x[0-9a-f]+$/i);
    // Selector (4 bytes = 8 hex chars) + encoded params
    expect(payload.length).toBeGreaterThan(10);
  });

  it('should encode different operation types producing different payloads', () => {
    const callPayload = encodeExecutePayload({
      operationType: 0,
      target: '0x0000000000000000000000000000000000000001',
      value: 0n,
      data: '0x',
    });

    const staticCallPayload = encodeExecutePayload({
      operationType: 3,
      target: '0x0000000000000000000000000000000000000001',
      value: 0n,
      data: '0x',
    });

    // Same selector, different encoded operationType
    expect(callPayload.slice(0, 10)).toBe(staticCallPayload.slice(0, 10));
    expect(callPayload).not.toBe(staticCallPayload);
  });

  it('should be deterministic for same inputs', () => {
    const params = {
      operationType: 0,
      target: '0x0000000000000000000000000000000000000001',
      value: 0n,
      data: '0xdeadbeef',
    };
    expect(encodeExecutePayload(params)).toBe(encodeExecutePayload(params));
  });
});

// ==================== encodeExecuteBatchPayload ====================

describe('encodeExecuteBatchPayload', () => {
  it('should return a hex string', () => {
    const payload = encodeExecuteBatchPayload([
      {
        operationType: 0,
        target: '0x0000000000000000000000000000000000000001',
        value: 0n,
        data: '0x',
      },
    ]);

    expect(payload).toMatch(/^0x[0-9a-f]+$/i);
  });

  it('should start with the correct selector for executeBatch', () => {
    const iface = new ethers.Interface([
      'function executeBatch(uint256[] operationTypes, address[] targets, uint256[] values, bytes[] datas) payable returns (bytes[])',
    ]);
    const expectedSelector = iface.getFunction('executeBatch')!.selector;

    const payload = encodeExecuteBatchPayload([
      {
        operationType: 0,
        target: '0x0000000000000000000000000000000000000001',
        value: 0n,
        data: '0x',
      },
      {
        operationType: 0,
        target: '0x0000000000000000000000000000000000000002',
        value: 100n,
        data: '0xabcd',
      },
    ]);

    expect(payload.slice(0, 10)).toBe(expectedSelector);
  });

  it('should encode multiple operations producing a longer payload', () => {
    const singlePayload = encodeExecuteBatchPayload([
      {
        operationType: 0,
        target: '0x0000000000000000000000000000000000000001',
        value: 0n,
        data: '0x',
      },
    ]);

    const doublePayload = encodeExecuteBatchPayload([
      {
        operationType: 0,
        target: '0x0000000000000000000000000000000000000001',
        value: 0n,
        data: '0x',
      },
      {
        operationType: 0,
        target: '0x0000000000000000000000000000000000000002',
        value: 0n,
        data: '0x',
      },
    ]);

    expect(doublePayload.length).toBeGreaterThan(singlePayload.length);
  });
});

// ==================== encodeSetDataPayload ====================

describe('encodeSetDataPayload', () => {
  const dataKey = '0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5';
  const dataValue = '0xdeadbeef';

  it('should return a hex string', () => {
    const payload = encodeSetDataPayload(dataKey, dataValue);
    expect(payload).toMatch(/^0x[0-9a-f]+$/i);
  });

  it('should start with the correct selector for setData(bytes32,bytes)', () => {
    const iface = new ethers.Interface([
      'function setData(bytes32 dataKey, bytes dataValue) payable',
    ]);
    const expectedSelector = iface.getFunction('setData')!.selector;

    const payload = encodeSetDataPayload(dataKey, dataValue);
    expect(payload.slice(0, 10)).toBe(expectedSelector);
  });

  it('should produce different payloads for different data keys', () => {
    const key1 = '0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5';
    const key2 = '0x0000000000000000000000000000000000000000000000000000000000000001';

    const payload1 = encodeSetDataPayload(key1, dataValue);
    const payload2 = encodeSetDataPayload(key2, dataValue);

    expect(payload1).not.toBe(payload2);
  });

  it('should produce different payloads for different data values', () => {
    const payload1 = encodeSetDataPayload(dataKey, '0xaa');
    const payload2 = encodeSetDataPayload(dataKey, '0xbb');

    expect(payload1).not.toBe(payload2);
  });
});

// ==================== encodeSetDataBatchPayload ====================

describe('encodeSetDataBatchPayload', () => {
  const keys = [
    '0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5',
    '0x0000000000000000000000000000000000000000000000000000000000000001',
  ];
  const values = ['0xaabb', '0xccdd'];

  it('should return a hex string', () => {
    const payload = encodeSetDataBatchPayload(keys, values);
    expect(payload).toMatch(/^0x[0-9a-f]+$/i);
  });

  it('should start with the correct selector for setDataBatch(bytes32[],bytes[])', () => {
    const iface = new ethers.Interface([
      'function setDataBatch(bytes32[] dataKeys, bytes[] dataValues) payable',
    ]);
    const expectedSelector = iface.getFunction('setDataBatch')!.selector;

    const payload = encodeSetDataBatchPayload(keys, values);
    expect(payload.slice(0, 10)).toBe(expectedSelector);
  });

  it('should produce longer payloads for more items', () => {
    const singlePayload = encodeSetDataBatchPayload([keys[0]], [values[0]]);
    const doublePayload = encodeSetDataBatchPayload(keys, values);

    expect(doublePayload.length).toBeGreaterThan(singlePayload.length);
  });
});

// ==================== signRelayCall ====================

describe('signRelayCall', () => {
  let wallet: Wallet;

  beforeEach(() => {
    wallet = new Wallet(TEST_PRIVATE_KEY);
  });

  it('should return a valid 65-byte hex signature', async () => {
    const params = {
      keyManagerAddress: FAKE_KEY_MANAGER,
      payload: '0xdeadbeef',
      nonce: 0n,
      validityTimestamps: 0n,
      value: 0n,
    };

    const signature = await signRelayCall(wallet, params, 42);

    expect(signature).toMatch(/^0x[0-9a-f]+$/i);
    // EIP-191 signatures are 65 bytes = 130 hex chars + '0x' prefix
    expect(signature.length).toBe(132);
  });

  it('should produce different signatures for different payloads', async () => {
    const base = {
      keyManagerAddress: FAKE_KEY_MANAGER,
      nonce: 0n,
      validityTimestamps: 0n,
    };

    const sig1 = await signRelayCall(wallet, { ...base, payload: '0xdeadbeef' }, 42);
    const sig2 = await signRelayCall(wallet, { ...base, payload: '0xcafebabe' }, 42);

    expect(sig1).not.toBe(sig2);
  });

  it('should produce different signatures for different nonces', async () => {
    const base = {
      keyManagerAddress: FAKE_KEY_MANAGER,
      payload: '0xdeadbeef',
      validityTimestamps: 0n,
    };

    const sig1 = await signRelayCall(wallet, { ...base, nonce: 0n }, 42);
    const sig2 = await signRelayCall(wallet, { ...base, nonce: 1n }, 42);

    expect(sig1).not.toBe(sig2);
  });

  it('should produce different signatures for different chain IDs', async () => {
    const params = {
      keyManagerAddress: FAKE_KEY_MANAGER,
      payload: '0xdeadbeef',
      nonce: 0n,
      validityTimestamps: 0n,
    };

    const sig1 = await signRelayCall(wallet, params, 42);
    const sig2 = await signRelayCall(wallet, params, 4201);

    expect(sig1).not.toBe(sig2);
  });

  it('should be deterministic for the same inputs', async () => {
    const params = {
      keyManagerAddress: FAKE_KEY_MANAGER,
      payload: '0xdeadbeef',
      nonce: 0n,
      validityTimestamps: 0n,
    };

    const sig1 = await signRelayCall(wallet, params, 42);
    const sig2 = await signRelayCall(wallet, params, 42);

    expect(sig1).toBe(sig2);
  });

  it('should treat missing value as 0', async () => {
    const paramsWithValue = {
      keyManagerAddress: FAKE_KEY_MANAGER,
      payload: '0xdeadbeef',
      nonce: 0n,
      validityTimestamps: 0n,
      value: 0n,
    };

    const paramsWithoutValue = {
      keyManagerAddress: FAKE_KEY_MANAGER,
      payload: '0xdeadbeef',
      nonce: 0n,
      validityTimestamps: 0n,
    };

    const sig1 = await signRelayCall(wallet, paramsWithValue, 42);
    const sig2 = await signRelayCall(wallet, paramsWithoutValue, 42);

    expect(sig1).toBe(sig2);
  });

  it('should produce different signatures for different validity timestamps', async () => {
    const base = {
      keyManagerAddress: FAKE_KEY_MANAGER,
      payload: '0xdeadbeef',
      nonce: 0n,
    };

    const sig1 = await signRelayCall(wallet, { ...base, validityTimestamps: 0n }, 42);
    const sig2 = await signRelayCall(wallet, { ...base, validityTimestamps: 999n }, 42);

    expect(sig1).not.toBe(sig2);
  });
});

// ==================== getNonce ====================

describe('getNonce', () => {
  beforeEach(() => {
    mockContractInstance = {};
  });

  it('should call keyManager.getNonce with correct arguments and return result', async () => {
    const mockGetNonce = vi.fn().mockResolvedValue(5n);
    mockContractInstance = { getNonce: mockGetNonce };

    const result = await getNonce(
      FAKE_KEY_MANAGER,
      TEST_ADDRESS,
      0,
      {} as any
    );

    expect(mockGetNonce).toHaveBeenCalledWith(TEST_ADDRESS, 0);
    expect(result).toBe(5n);
  });

  it('should pass the channelId through to the contract call', async () => {
    const mockGetNonce = vi.fn().mockResolvedValue(10n);
    mockContractInstance = { getNonce: mockGetNonce };

    await getNonce(FAKE_KEY_MANAGER, TEST_ADDRESS, 5, {} as any);

    expect(mockGetNonce).toHaveBeenCalledWith(TEST_ADDRESS, 5);
  });

  it('should default channelId to 0', async () => {
    const mockGetNonce = vi.fn().mockResolvedValue(0n);
    mockContractInstance = { getNonce: mockGetNonce };

    // channelId has a default value of 0 in the function signature
    await getNonce(FAKE_KEY_MANAGER, TEST_ADDRESS, undefined as any, {} as any);

    expect(mockGetNonce).toHaveBeenCalledWith(TEST_ADDRESS, 0);
  });
});

// ==================== executeViaRelayer ====================

describe('executeViaRelayer', () => {
  let fetchSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchSpy = vi.fn();
    vi.stubGlobal('fetch', fetchSpy);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('should POST to the relayer and return success result', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          transactionHash: '0xabc123',
          returnData: '0x',
        }),
    });

    const result = await executeViaRelayer(
      'https://relayer.lukso.network',
      FAKE_KEY_MANAGER,
      '0xsignature',
      1n,
      100n,
      '0xpayload',
      0n
    );

    expect(result).toEqual({
      transactionHash: '0xabc123',
      success: true,
      returnData: '0x',
    });

    expect(fetchSpy).toHaveBeenCalledWith(
      'https://relayer.lukso.network/execute',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyManagerAddress: FAKE_KEY_MANAGER,
          signature: '0xsignature',
          nonce: '1',
          validityTimestamps: '100',
          payload: '0xpayload',
          value: '0',
        }),
      }
    );
  });

  it('should handle response without returnData', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          transactionHash: '0xnoreturndata',
        }),
    });

    const result = await executeViaRelayer(
      'https://relayer.lukso.network',
      FAKE_KEY_MANAGER,
      '0xsig',
      0n,
      0n,
      '0xdata'
    );

    expect(result.success).toBe(true);
    expect(result.transactionHash).toBe('0xnoreturndata');
    expect(result.returnData).toBeUndefined();
  });

  it('should throw UniversalProfileError on non-OK response', async () => {
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: () => Promise.resolve({ message: 'Invalid nonce' }),
    });

    await expect(
      executeViaRelayer(
        'https://relayer.lukso.network',
        FAKE_KEY_MANAGER,
        '0xsig',
        0n,
        0n,
        '0xdata'
      )
    ).rejects.toThrow('Relayer error: Bad Request');
  });

  it('should include status and error data in thrown error details', async () => {
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 429,
      statusText: 'Too Many Requests',
      json: () => Promise.resolve({ message: 'Rate limited' }),
    });

    try {
      await executeViaRelayer(
        'https://relayer.lukso.network',
        FAKE_KEY_MANAGER,
        '0xsig',
        0n,
        0n,
        '0xdata'
      );
      expect.fail('Should have thrown');
    } catch (err: any) {
      expect(err.code).toBe('UP_RELAY_FAILED');
      expect(err.details?.status).toBe(429);
      expect(err.details?.error).toEqual({ message: 'Rate limited' });
    }
  });

  it('should handle non-OK response with non-JSON body gracefully', async () => {
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      json: () => Promise.reject(new Error('not json')),
    });

    await expect(
      executeViaRelayer(
        'https://relayer.lukso.network',
        FAKE_KEY_MANAGER,
        '0xsig',
        0n,
        0n,
        '0xdata'
      )
    ).rejects.toThrow('Relayer error');
  });

  it('should wrap network errors in UniversalProfileError', async () => {
    fetchSpy.mockRejectedValue(new TypeError('Failed to fetch'));

    try {
      await executeViaRelayer(
        'https://relayer.lukso.network',
        FAKE_KEY_MANAGER,
        '0xsig',
        0n,
        0n,
        '0xdata'
      );
      expect.fail('Should have thrown');
    } catch (err: any) {
      expect(err.name).toBe('UniversalProfileError');
      expect(err.code).toBe('UP_RELAY_FAILED');
      expect(err.message).toContain('Failed to fetch');
    }
  });

  it('should default value to 0n when not provided', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ transactionHash: '0x123' }),
    });

    await executeViaRelayer(
      'https://relayer.lukso.network',
      FAKE_KEY_MANAGER,
      '0xsig',
      0n,
      0n,
      '0xdata'
    );

    const body = JSON.parse(fetchSpy.mock.calls[0][1].body);
    expect(body.value).toBe('0');
  });

  it('should serialize bigint nonce and validityTimestamps as strings', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ transactionHash: '0xok' }),
    });

    await executeViaRelayer(
      'https://relayer.lukso.network',
      FAKE_KEY_MANAGER,
      '0xsig',
      42n,
      999n,
      '0xdata',
      100n
    );

    const body = JSON.parse(fetchSpy.mock.calls[0][1].body);
    expect(body.nonce).toBe('42');
    expect(body.validityTimestamps).toBe('999');
    expect(body.value).toBe('100');
  });
});

// ==================== executeRelayCallDirect ====================

describe('executeRelayCallDirect', () => {
  let wallet: Wallet;

  beforeEach(() => {
    wallet = new Wallet(TEST_PRIVATE_KEY);
    mockContractInstance = {};
  });

  it('should call contract executeRelayCall and return success on receipt', async () => {
    const mockWait = vi.fn().mockResolvedValue({
      status: 1,
      hash: '0xtxhash123',
    });
    const mockExecuteRelayCall = vi.fn().mockResolvedValue({
      hash: '0xtxhash123',
      wait: mockWait,
    });
    mockContractInstance = { executeRelayCall: mockExecuteRelayCall };

    const result = await executeRelayCallDirect(
      FAKE_KEY_MANAGER,
      '0xsig',
      1n,
      100n,
      '0xpayload',
      wallet,
      0n
    );

    expect(result.success).toBe(true);
    expect(result.transactionHash).toBe('0xtxhash123');
    expect(mockExecuteRelayCall).toHaveBeenCalledWith(
      '0xsig',
      1n,
      100n,
      '0xpayload',
      { value: 0n }
    );
  });

  it('should throw UniversalProfileError when receipt status is not 1', async () => {
    const mockWait = vi.fn().mockResolvedValue({
      status: 0,
      hash: '0xfailedhash',
    });
    mockContractInstance = {
      executeRelayCall: vi.fn().mockResolvedValue({
        hash: '0xfailedhash',
        wait: mockWait,
      }),
    };

    try {
      await executeRelayCallDirect(
        FAKE_KEY_MANAGER,
        '0xsig',
        1n,
        100n,
        '0xpayload',
        wallet
      );
      expect.fail('Should have thrown');
    } catch (err: any) {
      expect(err.name).toBe('UniversalProfileError');
      expect(err.code).toBe('UP_RELAY_FAILED');
      expect(err.message).toContain('Relay call transaction failed');
    }
  });

  it('should throw UniversalProfileError when receipt is null', async () => {
    const mockWait = vi.fn().mockResolvedValue(null);
    mockContractInstance = {
      executeRelayCall: vi.fn().mockResolvedValue({
        hash: '0xnullreceipt',
        wait: mockWait,
      }),
    };

    try {
      await executeRelayCallDirect(
        FAKE_KEY_MANAGER,
        '0xsig',
        1n,
        100n,
        '0xpayload',
        wallet
      );
      expect.fail('Should have thrown');
    } catch (err: any) {
      expect(err.name).toBe('UniversalProfileError');
      expect(err.code).toBe('UP_RELAY_FAILED');
    }
  });

  it('should wrap unexpected errors in UniversalProfileError', async () => {
    mockContractInstance = {
      executeRelayCall: vi.fn().mockRejectedValue(new Error('network timeout')),
    };

    try {
      await executeRelayCallDirect(
        FAKE_KEY_MANAGER,
        '0xsig',
        1n,
        100n,
        '0xpayload',
        wallet
      );
      expect.fail('Should have thrown');
    } catch (err: any) {
      expect(err.name).toBe('UniversalProfileError');
      expect(err.code).toBe('UP_RELAY_FAILED');
      expect(err.message).toContain('network timeout');
    }
  });

  it('should default value to 0n when not provided', async () => {
    const mockExecuteRelayCall = vi.fn().mockResolvedValue({
      hash: '0xdefault_value',
      wait: vi.fn().mockResolvedValue({ status: 1, hash: '0xdefault_value' }),
    });
    mockContractInstance = { executeRelayCall: mockExecuteRelayCall };

    await executeRelayCallDirect(
      FAKE_KEY_MANAGER,
      '0xsig',
      0n,
      0n,
      '0xdata',
      wallet
    );

    expect(mockExecuteRelayCall).toHaveBeenCalledWith(
      '0xsig',
      0n,
      0n,
      '0xdata',
      { value: 0n }
    );
  });

  it('should not re-wrap UniversalProfileError thrown internally', async () => {
    // When the receipt check throws a UniversalProfileError, it should
    // propagate unchanged (not be double-wrapped)
    const mockWait = vi.fn().mockResolvedValue({ status: 0, hash: '0xfail' });
    mockContractInstance = {
      executeRelayCall: vi.fn().mockResolvedValue({
        hash: '0xfail',
        wait: mockWait,
      }),
    };

    try {
      await executeRelayCallDirect(
        FAKE_KEY_MANAGER,
        '0xsig',
        0n,
        0n,
        '0xdata',
        wallet
      );
      expect.fail('Should have thrown');
    } catch (err: any) {
      // Should be the original error, not wrapped
      expect(err.message).toBe('Relay call transaction failed');
      expect(err.code).toBe('UP_RELAY_FAILED');
    }
  });
});

// ==================== checkRelayQuota ====================

describe('checkRelayQuota', () => {
  let fetchSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchSpy = vi.fn();
    vi.stubGlobal('fetch', fetchSpy);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('should return quota data on success', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          remaining: 8,
          total: 10,
          resetsAt: '2025-01-01T00:00:00Z',
        }),
    });

    const result = await checkRelayQuota(
      'https://relayer.lukso.network',
      FAKE_UP_ADDRESS
    );

    expect(result.remaining).toBe(8);
    expect(result.total).toBe(10);
    expect(result.resetsAt).toBeInstanceOf(Date);
    expect(result.resetsAt!.toISOString()).toBe('2025-01-01T00:00:00.000Z');
  });

  it('should call fetch with the correct quota URL', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ remaining: 1, total: 5 }),
    });

    await checkRelayQuota('https://relayer.lukso.network', FAKE_UP_ADDRESS);

    expect(fetchSpy).toHaveBeenCalledWith(
      `https://relayer.lukso.network/quota/${FAKE_UP_ADDRESS}`
    );
  });

  it('should return null resetsAt when not provided in response', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          remaining: 5,
          total: 10,
        }),
    });

    const result = await checkRelayQuota(
      'https://relayer.lukso.network',
      FAKE_UP_ADDRESS
    );

    expect(result.remaining).toBe(5);
    expect(result.total).toBe(10);
    expect(result.resetsAt).toBeNull();
  });

  it('should return -1/-1/null on non-OK response (e.g. 404)', async () => {
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 404,
    });

    const result = await checkRelayQuota(
      'https://relayer.lukso.network',
      FAKE_UP_ADDRESS
    );

    expect(result.remaining).toBe(-1);
    expect(result.total).toBe(-1);
    expect(result.resetsAt).toBeNull();
  });

  it('should return -1/-1/null on network failure', async () => {
    fetchSpy.mockRejectedValue(new TypeError('Failed to fetch'));

    const result = await checkRelayQuota(
      'https://relayer.lukso.network',
      FAKE_UP_ADDRESS
    );

    expect(result.remaining).toBe(-1);
    expect(result.total).toBe(-1);
    expect(result.resetsAt).toBeNull();
  });

  it('should default remaining and total to 0 when missing from response', async () => {
    fetchSpy.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    });

    const result = await checkRelayQuota(
      'https://relayer.lukso.network',
      FAKE_UP_ADDRESS
    );

    expect(result.remaining).toBe(0);
    expect(result.total).toBe(0);
    expect(result.resetsAt).toBeNull();
  });

  it('should return -1/-1/null on 500 server error', async () => {
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 500,
    });

    const result = await checkRelayQuota(
      'https://relayer.lukso.network',
      FAKE_UP_ADDRESS
    );

    expect(result).toEqual({ remaining: -1, total: -1, resetsAt: null });
  });
});

// ==================== executeViaRelay (high-level orchestrator) ====================

describe('executeViaRelay', () => {
  let fetchSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchSpy = vi.fn();
    vi.stubGlobal('fetch', fetchSpy);
    mockContractInstance = {};
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('should use relayer when relayerUrl is provided and useDirect is false', async () => {
    const mockProvider = {
      getNetwork: vi.fn().mockResolvedValue({ chainId: 42n }),
    };
    const wallet = new Wallet(TEST_PRIVATE_KEY, mockProvider as any);

    mockContractInstance = { getNonce: vi.fn().mockResolvedValue(0n) };

    fetchSpy.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          transactionHash: '0xrelayed123',
          returnData: '0x',
        }),
    });

    const result = await executeViaRelay(
      wallet,
      FAKE_UP_ADDRESS,
      FAKE_KEY_MANAGER,
      {
        operationType: 0,
        target: '0x0000000000000000000000000000000000000001',
        value: 0n,
        data: '0x',
      },
      { relayerUrl: 'https://relayer.lukso.network' }
    );

    expect(result.success).toBe(true);
    expect(result.transactionHash).toBe('0xrelayed123');
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(fetchSpy.mock.calls[0][0]).toBe(
      'https://relayer.lukso.network/execute'
    );
  });

  it('should fall back to direct when no relayerUrl is provided', async () => {
    const mockProvider = {
      getNetwork: vi.fn().mockResolvedValue({ chainId: 42n }),
    };
    const wallet = new Wallet(TEST_PRIVATE_KEY, mockProvider as any);

    const mockWait = vi.fn().mockResolvedValue({
      status: 1,
      hash: '0xdirecthash',
    });
    mockContractInstance = {
      getNonce: vi.fn().mockResolvedValue(0n),
      executeRelayCall: vi.fn().mockResolvedValue({
        hash: '0xdirecthash',
        wait: mockWait,
      }),
    };

    const result = await executeViaRelay(
      wallet,
      FAKE_UP_ADDRESS,
      FAKE_KEY_MANAGER,
      {
        operationType: 0,
        target: '0x0000000000000000000000000000000000000001',
        value: 0n,
        data: '0x',
      }
    );

    expect(result.success).toBe(true);
    expect(result.transactionHash).toBe('0xdirecthash');
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('should use direct when useDirect is true even if relayerUrl is provided', async () => {
    const mockProvider = {
      getNetwork: vi.fn().mockResolvedValue({ chainId: 42n }),
    };
    const wallet = new Wallet(TEST_PRIVATE_KEY, mockProvider as any);

    const mockWait = vi.fn().mockResolvedValue({
      status: 1,
      hash: '0xforced_direct',
    });
    mockContractInstance = {
      getNonce: vi.fn().mockResolvedValue(0n),
      executeRelayCall: vi.fn().mockResolvedValue({
        hash: '0xforced_direct',
        wait: mockWait,
      }),
    };

    const result = await executeViaRelay(
      wallet,
      FAKE_UP_ADDRESS,
      FAKE_KEY_MANAGER,
      {
        operationType: 0,
        target: '0x0000000000000000000000000000000000000001',
        value: 0n,
        data: '0x',
      },
      {
        relayerUrl: 'https://relayer.lukso.network',
        useDirect: true,
      }
    );

    expect(result.success).toBe(true);
    expect(result.transactionHash).toBe('0xforced_direct');
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('should pass the encoded execute payload to the relayer', async () => {
    const mockProvider = {
      getNetwork: vi.fn().mockResolvedValue({ chainId: 42n }),
    };
    const wallet = new Wallet(TEST_PRIVATE_KEY, mockProvider as any);

    mockContractInstance = { getNonce: vi.fn().mockResolvedValue(0n) };

    fetchSpy.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ transactionHash: '0xcheck_payload' }),
    });

    const target = '0x0000000000000000000000000000000000000001';
    await executeViaRelay(
      wallet,
      FAKE_UP_ADDRESS,
      FAKE_KEY_MANAGER,
      {
        operationType: 0,
        target,
        value: 0n,
        data: '0xdeadbeef',
      },
      { relayerUrl: 'https://relayer.lukso.network' }
    );

    const body = JSON.parse(fetchSpy.mock.calls[0][1].body);
    // The payload should be an encoded execute call
    const iface = new ethers.Interface([
      'function execute(uint256 operationType, address target, uint256 value, bytes data) payable returns (bytes)',
    ]);
    const expectedSelector = iface.getFunction('execute')!.selector;
    expect(body.payload.slice(0, 10)).toBe(expectedSelector);
  });
});

// ==================== setDataViaRelay (high-level orchestrator) ====================

describe('setDataViaRelay', () => {
  let fetchSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchSpy = vi.fn();
    vi.stubGlobal('fetch', fetchSpy);
    mockContractInstance = {};
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('should relay setData via relayer when relayerUrl is provided', async () => {
    const mockProvider = {
      getNetwork: vi.fn().mockResolvedValue({ chainId: 42n }),
    };
    const wallet = new Wallet(TEST_PRIVATE_KEY, mockProvider as any);

    mockContractInstance = { getNonce: vi.fn().mockResolvedValue(3n) };

    fetchSpy.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          transactionHash: '0xsetdata_relayed',
        }),
    });

    const dataKey =
      '0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5';
    const dataValue = '0xdeadbeef';

    const result = await setDataViaRelay(
      wallet,
      FAKE_UP_ADDRESS,
      FAKE_KEY_MANAGER,
      dataKey,
      dataValue,
      { relayerUrl: 'https://relayer.lukso.network' }
    );

    expect(result.success).toBe(true);
    expect(result.transactionHash).toBe('0xsetdata_relayed');

    // Verify fetch was called with the relayer URL
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const [url, options] = fetchSpy.mock.calls[0];
    expect(url).toBe('https://relayer.lukso.network/execute');
    expect(options.method).toBe('POST');

    // Verify the body contains the setData payload with correct selector
    const body = JSON.parse(options.body);
    expect(body.keyManagerAddress).toBe(FAKE_KEY_MANAGER);
    expect(body.nonce).toBe('3');
    const iface = new ethers.Interface([
      'function setData(bytes32 dataKey, bytes dataValue) payable',
    ]);
    const expectedSelector = iface.getFunction('setData')!.selector;
    expect(body.payload.slice(0, 10)).toBe(expectedSelector);
  });

  it('should use direct execution when no relayerUrl is provided', async () => {
    const mockProvider = {
      getNetwork: vi.fn().mockResolvedValue({ chainId: 4201n }),
    };
    const wallet = new Wallet(TEST_PRIVATE_KEY, mockProvider as any);

    const mockWait = vi.fn().mockResolvedValue({
      status: 1,
      hash: '0xsetdata_direct',
    });
    mockContractInstance = {
      getNonce: vi.fn().mockResolvedValue(0n),
      executeRelayCall: vi.fn().mockResolvedValue({
        hash: '0xsetdata_direct',
        wait: mockWait,
      }),
    };

    const result = await setDataViaRelay(
      wallet,
      FAKE_UP_ADDRESS,
      FAKE_KEY_MANAGER,
      '0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5',
      '0xaabbccdd'
    );

    expect(result.success).toBe(true);
    expect(result.transactionHash).toBe('0xsetdata_direct');
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it('should respect custom validityDuration option', async () => {
    const dateNowSpy = vi.spyOn(Date, 'now').mockReturnValue(1_700_000_000_000);

    const mockProvider = {
      getNetwork: vi.fn().mockResolvedValue({ chainId: 42n }),
    };
    const wallet = new Wallet(TEST_PRIVATE_KEY, mockProvider as any);

    mockContractInstance = { getNonce: vi.fn().mockResolvedValue(0n) };

    fetchSpy.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({ transactionHash: '0xcustom_validity' }),
    });

    await setDataViaRelay(
      wallet,
      FAKE_UP_ADDRESS,
      FAKE_KEY_MANAGER,
      '0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5',
      '0xaa',
      { relayerUrl: 'https://relayer.lukso.network', validityDuration: 7200 }
    );

    // Verify the validityTimestamps encodes the custom 7200s duration
    const body = JSON.parse(fetchSpy.mock.calls[0][1].body);
    const vt = BigInt(body.validityTimestamps);
    const mask128 = (1n << 128n) - 1n;
    const now = 1_700_000_000;
    expect(vt >> 128n).toBe(BigInt(now));
    expect(vt & mask128).toBe(BigInt(now + 7200));

    dateNowSpy.mockRestore();
  });

  it('should use direct when useDirect is true', async () => {
    const mockProvider = {
      getNetwork: vi.fn().mockResolvedValue({ chainId: 42n }),
    };
    const wallet = new Wallet(TEST_PRIVATE_KEY, mockProvider as any);

    const mockWait = vi.fn().mockResolvedValue({
      status: 1,
      hash: '0xsetdata_forced_direct',
    });
    mockContractInstance = {
      getNonce: vi.fn().mockResolvedValue(0n),
      executeRelayCall: vi.fn().mockResolvedValue({
        hash: '0xsetdata_forced_direct',
        wait: mockWait,
      }),
    };

    const result = await setDataViaRelay(
      wallet,
      FAKE_UP_ADDRESS,
      FAKE_KEY_MANAGER,
      '0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5',
      '0xaa',
      {
        relayerUrl: 'https://relayer.lukso.network',
        useDirect: true,
      }
    );

    expect(result.success).toBe(true);
    expect(result.transactionHash).toBe('0xsetdata_forced_direct');
    expect(fetchSpy).not.toHaveBeenCalled();
  });
});
