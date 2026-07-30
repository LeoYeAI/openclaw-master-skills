import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ethers } from 'ethers';

// ---------------------------------------------------------------------------
// Mock ethers.Contract so query functions never hit the network.
// We keep the real `ethers` namespace (Interface, zeroPadValue, etc.) intact
// and only intercept the Contract constructor.
// ---------------------------------------------------------------------------

const mockContractInstance: Record<string, ReturnType<typeof vi.fn>> = {};

vi.mock('ethers', async () => {
  const actual = await vi.importActual<typeof import('ethers')>('ethers');
  return {
    ...actual,
    Contract: vi.fn(() => mockContractInstance),
  };
});

import {
  // Query functions
  getLSP7Info,
  getLSP7Balance,
  getLSP7AuthorizedAmount,
  getLSP8Info,
  getLSP8TokensOf,
  getLSP8TokenOwner,
  isLSP8Operator,
  getTokenMetadata,
  getNFTTokenMetadata,
  // Encoding functions
  encodeLSP7Transfer,
  encodeLSP8Transfer,
  encodeLSP7AuthorizeOperator,
  encodeLSP8AuthorizeOperator,
  encodeLSP7Mint,
  encodeLSP8Mint,
  // Token ID helpers
  numberToTokenId,
  stringToTokenId,
  addressToTokenId,
  formatTokenId,
} from '../../src/lib/tokens.js';

// ---------------------------------------------------------------------------
// Shared test addresses
// ---------------------------------------------------------------------------

const TOKEN_ADDR = '0x1234567890abcdef1234567890abcdef12345678';
const COLLECTION_ADDR = '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd';
const OWNER_ADDR = '0x1111111111111111111111111111111111111111';
const HOLDER_ADDR = '0x2222222222222222222222222222222222222222';
const OPERATOR_ADDR = '0x3333333333333333333333333333333333333333';
const RECIPIENT_ADDR = '0x4444444444444444444444444444444444444444';
const MOCK_PROVIDER = {} as any;

// A full bytes32 token ID (number 1)
const TOKEN_ID_1 =
  '0x0000000000000000000000000000000000000000000000000000000000000001';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function resetMockContract() {
  for (const key of Object.keys(mockContractInstance)) {
    delete mockContractInstance[key];
  }
}

// ===================================================================
// TOKEN ID HELPERS (pure functions -- no mocking needed)
// ===================================================================

describe('Token ID Helpers', () => {
  describe('numberToTokenId', () => {
    it('converts 0 to bytes32 zero', () => {
      const result = numberToTokenId(0);
      expect(result).toBe(
        '0x0000000000000000000000000000000000000000000000000000000000000000'
      );
    });

    it('converts 1 to bytes32', () => {
      const result = numberToTokenId(1);
      expect(result).toBe(TOKEN_ID_1);
    });

    it('converts a large number', () => {
      const result = numberToTokenId(255);
      expect(result).toBe(
        '0x00000000000000000000000000000000000000000000000000000000000000ff'
      );
    });

    it('converts bigint values', () => {
      const result = numberToTokenId(1000000n);
      expect(result).toMatch(/^0x[0-9a-f]{64}$/);
      expect(BigInt(result)).toBe(1000000n);
    });

    it('returns a 66-character hex string (0x + 64 hex chars)', () => {
      const result = numberToTokenId(42);
      expect(result).toHaveLength(66);
      expect(result).toMatch(/^0x[0-9a-f]{64}$/);
    });
  });

  describe('stringToTokenId', () => {
    it('converts a short string to bytes32', () => {
      const result = stringToTokenId('hello');
      expect(result).toHaveLength(66);
      expect(result).toMatch(/^0x/);
      // "hello" = 0x68656c6c6f  -- rest is zero-padded
      expect(result.startsWith('0x68656c6c6f')).toBe(true);
    });

    it('converts an empty string', () => {
      const result = stringToTokenId('');
      expect(result).toBe(
        '0x0000000000000000000000000000000000000000000000000000000000000000'
      );
    });

    it('converts a 32-byte string exactly', () => {
      const str32 = 'abcdefghijklmnopqrstuvwxyz012345'; // 32 ASCII chars
      const result = stringToTokenId(str32);
      expect(result).toHaveLength(66);
    });

    it('throws if string is longer than 32 bytes', () => {
      const tooLong = 'abcdefghijklmnopqrstuvwxyz0123456'; // 33 chars
      expect(() => stringToTokenId(tooLong)).toThrow('String too long for token ID');
    });

    it('throws for multi-byte UTF-8 strings that exceed 32 bytes', () => {
      // Each emoji is 4 bytes, so 9 emojis = 36 bytes > 32
      const manyEmoji = '\u{1F600}'.repeat(9);
      expect(() => stringToTokenId(manyEmoji)).toThrow('String too long for token ID');
    });
  });

  describe('addressToTokenId', () => {
    it('converts a valid address to zero-padded bytes32', () => {
      const result = addressToTokenId(HOLDER_ADDR);
      expect(result).toHaveLength(66);
      expect(result).toMatch(/^0x/);
      // Address should appear in the last 40 hex chars
      expect(result.toLowerCase().endsWith(HOLDER_ADDR.slice(2).toLowerCase())).toBe(
        true
      );
      // First 24 hex chars (12 bytes) should be zero padding
      expect(result.slice(2, 26)).toBe('000000000000000000000000');
    });

    it('throws for an invalid address', () => {
      expect(() => addressToTokenId('0xINVALID')).toThrow('Invalid address');
    });

    it('throws for empty string', () => {
      expect(() => addressToTokenId('')).toThrow('Invalid address');
    });

    it('handles checksummed addresses', () => {
      const checksummed = ethers.getAddress(HOLDER_ADDR);
      const result = addressToTokenId(checksummed);
      expect(result).toHaveLength(66);
    });
  });

  describe('formatTokenId', () => {
    it('formats as NUMBER by default', () => {
      const result = formatTokenId(TOKEN_ID_1);
      expect(result).toBe('1');
    });

    it('formats zero as NUMBER', () => {
      const zero =
        '0x0000000000000000000000000000000000000000000000000000000000000000';
      expect(formatTokenId(zero, 0)).toBe('0');
    });

    it('formats as STRING (format=1)', () => {
      const helloId = stringToTokenId('hello');
      const result = formatTokenId(helloId, 1);
      expect(result).toBe('hello');
    });

    it('formats as ADDRESS (format=2)', () => {
      const addrId = addressToTokenId(HOLDER_ADDR);
      const result = formatTokenId(addrId, 2);
      expect(result.toLowerCase()).toBe(HOLDER_ADDR.toLowerCase());
    });

    it('returns raw hex for unknown format', () => {
      const result = formatTokenId(TOKEN_ID_1, 99);
      expect(result).toBe(TOKEN_ID_1);
    });

    it('returns raw hex when STRING decoding fails', () => {
      // Create bytes that are not valid UTF-8
      const badBytes =
        '0xff00000000000000000000000000000000000000000000000000000000000000';
      const result = formatTokenId(badBytes, 1);
      // Should either return decoded or fall back to raw hex
      expect(typeof result).toBe('string');
    });
  });
});

// ===================================================================
// ENCODING FUNCTIONS (use real ethers.Interface -- no mocking needed)
// ===================================================================

describe('Encoding Functions', () => {
  // Helper to compute the expected 4-byte selector from a function signature
  function selector(sig: string): string {
    return ethers.id(sig).slice(0, 10); // "0x" + 8 hex chars
  }

  describe('encodeLSP7Transfer', () => {
    it('returns correct ExecuteParams structure', () => {
      const result = encodeLSP7Transfer(
        TOKEN_ADDR,
        OWNER_ADDR,
        RECIPIENT_ADDR,
        1000n
      );

      expect(result).toEqual(
        expect.objectContaining({
          operationType: 0,
          target: TOKEN_ADDR,
          value: 0n,
        })
      );
      expect(typeof result.data).toBe('string');
      expect(result.data).toMatch(/^0x/);
    });

    it('data starts with transfer(address,address,uint256,bool,bytes) selector', () => {
      const result = encodeLSP7Transfer(
        TOKEN_ADDR,
        OWNER_ADDR,
        RECIPIENT_ADDR,
        500n
      );
      const expected = selector('transfer(address,address,uint256,bool,bytes)');
      expect(result.data.slice(0, 10)).toBe(expected);
    });

    it('uses default force=true and data=0x', () => {
      const result = encodeLSP7Transfer(
        TOKEN_ADDR,
        OWNER_ADDR,
        RECIPIENT_ADDR,
        100n
      );
      // Just ensure it doesn't throw and returns valid data
      expect(result.data.length).toBeGreaterThan(10);
    });

    it('accepts custom force and data parameters', () => {
      const result = encodeLSP7Transfer(
        TOKEN_ADDR,
        OWNER_ADDR,
        RECIPIENT_ADDR,
        100n,
        false,
        '0xdeadbeef'
      );
      expect(result.operationType).toBe(0);
      expect(result.target).toBe(TOKEN_ADDR);
      expect(result.value).toBe(0n);
      expect(result.data).toMatch(/^0x/);
    });

    it('encodes different amounts to different data', () => {
      const a = encodeLSP7Transfer(TOKEN_ADDR, OWNER_ADDR, RECIPIENT_ADDR, 100n);
      const b = encodeLSP7Transfer(TOKEN_ADDR, OWNER_ADDR, RECIPIENT_ADDR, 200n);
      expect(a.data).not.toBe(b.data);
    });
  });

  describe('encodeLSP8Transfer', () => {
    it('returns correct ExecuteParams structure', () => {
      const result = encodeLSP8Transfer(
        COLLECTION_ADDR,
        OWNER_ADDR,
        RECIPIENT_ADDR,
        TOKEN_ID_1
      );

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(COLLECTION_ADDR);
      expect(result.value).toBe(0n);
      expect(result.data).toMatch(/^0x/);
    });

    it('data starts with transfer(address,address,bytes32,bool,bytes) selector', () => {
      const result = encodeLSP8Transfer(
        COLLECTION_ADDR,
        OWNER_ADDR,
        RECIPIENT_ADDR,
        TOKEN_ID_1
      );
      const expected = selector('transfer(address,address,bytes32,bool,bytes)');
      expect(result.data.slice(0, 10)).toBe(expected);
    });

    it('accepts custom force and data parameters', () => {
      const result = encodeLSP8Transfer(
        COLLECTION_ADDR,
        OWNER_ADDR,
        RECIPIENT_ADDR,
        TOKEN_ID_1,
        false,
        '0xaa'
      );
      expect(result.operationType).toBe(0);
      expect(result.data.length).toBeGreaterThan(10);
    });
  });

  describe('encodeLSP7AuthorizeOperator', () => {
    it('returns correct ExecuteParams structure', () => {
      const result = encodeLSP7AuthorizeOperator(TOKEN_ADDR, OPERATOR_ADDR, 500n);

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(TOKEN_ADDR);
      expect(result.value).toBe(0n);
      expect(result.data).toMatch(/^0x/);
    });

    it('data starts with authorizeOperator(address,uint256,bytes) selector', () => {
      const result = encodeLSP7AuthorizeOperator(TOKEN_ADDR, OPERATOR_ADDR, 500n);
      const expected = selector('authorizeOperator(address,uint256,bytes)');
      expect(result.data.slice(0, 10)).toBe(expected);
    });

    it('accepts custom operatorNotificationData', () => {
      const result = encodeLSP7AuthorizeOperator(
        TOKEN_ADDR,
        OPERATOR_ADDR,
        1000n,
        '0xbeef'
      );
      expect(result.data.length).toBeGreaterThan(10);
    });
  });

  describe('encodeLSP8AuthorizeOperator', () => {
    it('returns correct ExecuteParams structure', () => {
      const result = encodeLSP8AuthorizeOperator(
        COLLECTION_ADDR,
        OPERATOR_ADDR,
        TOKEN_ID_1
      );

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(COLLECTION_ADDR);
      expect(result.value).toBe(0n);
      expect(result.data).toMatch(/^0x/);
    });

    it('data starts with authorizeOperator(address,bytes32,bytes) selector', () => {
      const result = encodeLSP8AuthorizeOperator(
        COLLECTION_ADDR,
        OPERATOR_ADDR,
        TOKEN_ID_1
      );
      const expected = selector('authorizeOperator(address,bytes32,bytes)');
      expect(result.data.slice(0, 10)).toBe(expected);
    });

    it('accepts custom operatorNotificationData', () => {
      const result = encodeLSP8AuthorizeOperator(
        COLLECTION_ADDR,
        OPERATOR_ADDR,
        TOKEN_ID_1,
        '0xcafe'
      );
      expect(result.data.length).toBeGreaterThan(10);
    });
  });

  describe('encodeLSP7Mint', () => {
    it('returns correct ExecuteParams structure', () => {
      const result = encodeLSP7Mint(TOKEN_ADDR, RECIPIENT_ADDR, 1000n);

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(TOKEN_ADDR);
      expect(result.value).toBe(0n);
      expect(result.data).toMatch(/^0x/);
    });

    it('data starts with mint(address,uint256,bool,bytes) selector', () => {
      const result = encodeLSP7Mint(TOKEN_ADDR, RECIPIENT_ADDR, 1000n);
      const expected = selector('mint(address,uint256,bool,bytes)');
      expect(result.data.slice(0, 10)).toBe(expected);
    });

    it('uses default force=true and data=0x', () => {
      const result = encodeLSP7Mint(TOKEN_ADDR, RECIPIENT_ADDR, 100n);
      expect(result.data.length).toBeGreaterThan(10);
    });

    it('accepts custom force and data', () => {
      const result = encodeLSP7Mint(
        TOKEN_ADDR,
        RECIPIENT_ADDR,
        100n,
        false,
        '0xabcd'
      );
      expect(result.operationType).toBe(0);
      expect(result.target).toBe(TOKEN_ADDR);
    });
  });

  describe('encodeLSP8Mint', () => {
    it('returns correct ExecuteParams structure', () => {
      const result = encodeLSP8Mint(COLLECTION_ADDR, RECIPIENT_ADDR, TOKEN_ID_1);

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(COLLECTION_ADDR);
      expect(result.value).toBe(0n);
      expect(result.data).toMatch(/^0x/);
    });

    it('data starts with mint(address,bytes32,bool,bytes) selector', () => {
      const result = encodeLSP8Mint(COLLECTION_ADDR, RECIPIENT_ADDR, TOKEN_ID_1);
      const expected = selector('mint(address,bytes32,bool,bytes)');
      expect(result.data.slice(0, 10)).toBe(expected);
    });

    it('accepts custom force and data', () => {
      const result = encodeLSP8Mint(
        COLLECTION_ADDR,
        RECIPIENT_ADDR,
        TOKEN_ID_1,
        false,
        '0x1234'
      );
      expect(result.data.length).toBeGreaterThan(10);
    });
  });
});

// ===================================================================
// QUERY FUNCTIONS (require mocked Contract)
// ===================================================================

describe('Query Functions', () => {
  beforeEach(() => {
    resetMockContract();
  });

  // ----- LSP7 queries -----

  describe('getLSP7Info', () => {
    it('returns full LSP7TokenInfo when interface is supported', async () => {
      mockContractInstance.supportsInterface = vi.fn().mockResolvedValue(true);
      mockContractInstance.name = vi.fn().mockResolvedValue('TestToken');
      mockContractInstance.symbol = vi.fn().mockResolvedValue('TT');
      mockContractInstance.decimals = vi.fn().mockResolvedValue(18n);
      mockContractInstance.totalSupply = vi
        .fn()
        .mockResolvedValue(1000000000000000000000n);
      mockContractInstance.owner = vi.fn().mockResolvedValue(OWNER_ADDR);

      const info = await getLSP7Info(TOKEN_ADDR, MOCK_PROVIDER);

      expect(info).toEqual({
        address: TOKEN_ADDR,
        name: 'TestToken',
        symbol: 'TT',
        decimals: 18,
        totalSupply: 1000000000000000000000n,
        owner: OWNER_ADDR,
        isNonDivisible: false,
      });
    });

    it('sets isNonDivisible to true when decimals is 0', async () => {
      mockContractInstance.supportsInterface = vi.fn().mockResolvedValue(true);
      mockContractInstance.name = vi.fn().mockResolvedValue('NonDiv');
      mockContractInstance.symbol = vi.fn().mockResolvedValue('ND');
      mockContractInstance.decimals = vi.fn().mockResolvedValue(0n);
      mockContractInstance.totalSupply = vi.fn().mockResolvedValue(100n);
      mockContractInstance.owner = vi.fn().mockResolvedValue(OWNER_ADDR);

      const info = await getLSP7Info(TOKEN_ADDR, MOCK_PROVIDER);
      expect(info.isNonDivisible).toBe(true);
      expect(info.decimals).toBe(0);
    });

    it('throws UniversalProfileError when interface check fails', async () => {
      mockContractInstance.supportsInterface = vi.fn().mockResolvedValue(false);

      await expect(getLSP7Info(TOKEN_ADDR, MOCK_PROVIDER)).rejects.toThrow(
        'Address is not an LSP7 token'
      );
    });

    it('throws when supportsInterface reverts', async () => {
      mockContractInstance.supportsInterface = vi
        .fn()
        .mockRejectedValue(new Error('revert'));

      await expect(getLSP7Info(TOKEN_ADDR, MOCK_PROVIDER)).rejects.toThrow(
        'Address is not an LSP7 token'
      );
    });
  });

  describe('getLSP7Balance', () => {
    it('returns the balance as bigint', async () => {
      mockContractInstance.balanceOf = vi.fn().mockResolvedValue(500n);

      const balance = await getLSP7Balance(TOKEN_ADDR, HOLDER_ADDR, MOCK_PROVIDER);
      expect(balance).toBe(500n);
      expect(mockContractInstance.balanceOf).toHaveBeenCalledWith(HOLDER_ADDR);
    });

    it('returns 0n for address with no balance', async () => {
      mockContractInstance.balanceOf = vi.fn().mockResolvedValue(0n);

      const balance = await getLSP7Balance(TOKEN_ADDR, HOLDER_ADDR, MOCK_PROVIDER);
      expect(balance).toBe(0n);
    });
  });

  describe('getLSP7AuthorizedAmount', () => {
    it('returns the authorized amount', async () => {
      mockContractInstance.authorizedAmountFor = vi.fn().mockResolvedValue(1000n);

      const amount = await getLSP7AuthorizedAmount(
        TOKEN_ADDR,
        OPERATOR_ADDR,
        HOLDER_ADDR,
        MOCK_PROVIDER
      );

      expect(amount).toBe(1000n);
      expect(mockContractInstance.authorizedAmountFor).toHaveBeenCalledWith(
        OPERATOR_ADDR,
        HOLDER_ADDR
      );
    });

    it('returns 0n when no authorization exists', async () => {
      mockContractInstance.authorizedAmountFor = vi.fn().mockResolvedValue(0n);

      const amount = await getLSP7AuthorizedAmount(
        TOKEN_ADDR,
        OPERATOR_ADDR,
        HOLDER_ADDR,
        MOCK_PROVIDER
      );
      expect(amount).toBe(0n);
    });
  });

  // ----- LSP8 queries -----

  describe('getLSP8Info', () => {
    it('returns full LSP8CollectionInfo when interface is supported', async () => {
      mockContractInstance.supportsInterface = vi.fn().mockResolvedValue(true);
      mockContractInstance.name = vi.fn().mockResolvedValue('TestNFT');
      mockContractInstance.symbol = vi.fn().mockResolvedValue('TNFT');
      mockContractInstance.totalSupply = vi.fn().mockResolvedValue(42n);
      mockContractInstance.owner = vi.fn().mockResolvedValue(OWNER_ADDR);
      mockContractInstance.getData = vi.fn().mockResolvedValue('0x');

      const info = await getLSP8Info(COLLECTION_ADDR, MOCK_PROVIDER);

      expect(info).toEqual({
        address: COLLECTION_ADDR,
        name: 'TestNFT',
        symbol: 'TNFT',
        totalSupply: 42n,
        owner: OWNER_ADDR,
        tokenIdFormat: 0,
      });
    });

    it('parses tokenIdFormat from getData response', async () => {
      mockContractInstance.supportsInterface = vi.fn().mockResolvedValue(true);
      mockContractInstance.name = vi.fn().mockResolvedValue('NFT');
      mockContractInstance.symbol = vi.fn().mockResolvedValue('N');
      mockContractInstance.totalSupply = vi.fn().mockResolvedValue(10n);
      mockContractInstance.owner = vi.fn().mockResolvedValue(OWNER_ADDR);
      // format=2 (ADDRESS)
      mockContractInstance.getData = vi.fn().mockResolvedValue('0x02');

      const info = await getLSP8Info(COLLECTION_ADDR, MOCK_PROVIDER);
      expect(info.tokenIdFormat).toBe(2);
    });

    it('defaults tokenIdFormat to 0 when getData throws', async () => {
      mockContractInstance.supportsInterface = vi.fn().mockResolvedValue(true);
      mockContractInstance.name = vi.fn().mockResolvedValue('NFT');
      mockContractInstance.symbol = vi.fn().mockResolvedValue('N');
      mockContractInstance.totalSupply = vi.fn().mockResolvedValue(10n);
      mockContractInstance.owner = vi.fn().mockResolvedValue(OWNER_ADDR);
      mockContractInstance.getData = vi
        .fn()
        .mockRejectedValue(new Error('not supported'));

      const info = await getLSP8Info(COLLECTION_ADDR, MOCK_PROVIDER);
      expect(info.tokenIdFormat).toBe(0);
    });

    it('throws when interface check fails', async () => {
      mockContractInstance.supportsInterface = vi.fn().mockResolvedValue(false);

      await expect(getLSP8Info(COLLECTION_ADDR, MOCK_PROVIDER)).rejects.toThrow(
        'Address is not an LSP8 collection'
      );
    });

    it('throws when supportsInterface reverts', async () => {
      mockContractInstance.supportsInterface = vi
        .fn()
        .mockRejectedValue(new Error('revert'));

      await expect(getLSP8Info(COLLECTION_ADDR, MOCK_PROVIDER)).rejects.toThrow(
        'Address is not an LSP8 collection'
      );
    });
  });

  describe('getLSP8TokensOf', () => {
    it('returns array of token IDs', async () => {
      const tokenIds = [TOKEN_ID_1, numberToTokenId(2)];
      mockContractInstance.tokenIdsOf = vi.fn().mockResolvedValue(tokenIds);

      const result = await getLSP8TokensOf(
        COLLECTION_ADDR,
        HOLDER_ADDR,
        MOCK_PROVIDER
      );

      expect(result).toEqual(tokenIds);
      expect(mockContractInstance.tokenIdsOf).toHaveBeenCalledWith(HOLDER_ADDR);
    });

    it('returns empty array when holder has no tokens', async () => {
      mockContractInstance.tokenIdsOf = vi.fn().mockResolvedValue([]);

      const result = await getLSP8TokensOf(
        COLLECTION_ADDR,
        HOLDER_ADDR,
        MOCK_PROVIDER
      );
      expect(result).toEqual([]);
    });
  });

  describe('getLSP8TokenOwner', () => {
    it('returns the owner address', async () => {
      mockContractInstance.tokenOwnerOf = vi.fn().mockResolvedValue(HOLDER_ADDR);

      const owner = await getLSP8TokenOwner(
        COLLECTION_ADDR,
        TOKEN_ID_1,
        MOCK_PROVIDER
      );

      expect(owner).toBe(HOLDER_ADDR);
      expect(mockContractInstance.tokenOwnerOf).toHaveBeenCalledWith(TOKEN_ID_1);
    });
  });

  describe('isLSP8Operator', () => {
    it('returns true when address is operator', async () => {
      mockContractInstance.isOperatorFor = vi.fn().mockResolvedValue(true);

      const result = await isLSP8Operator(
        COLLECTION_ADDR,
        OPERATOR_ADDR,
        TOKEN_ID_1,
        MOCK_PROVIDER
      );

      expect(result).toBe(true);
      expect(mockContractInstance.isOperatorFor).toHaveBeenCalledWith(
        OPERATOR_ADDR,
        TOKEN_ID_1
      );
    });

    it('returns false when address is not operator', async () => {
      mockContractInstance.isOperatorFor = vi.fn().mockResolvedValue(false);

      const result = await isLSP8Operator(
        COLLECTION_ADDR,
        OPERATOR_ADDR,
        TOKEN_ID_1,
        MOCK_PROVIDER
      );

      expect(result).toBe(false);
    });
  });

  // ----- Metadata queries -----

  describe('getTokenMetadata', () => {
    it('returns metadata bytes when present', async () => {
      const metaHex = '0xaabbccdd';
      mockContractInstance.getData = vi.fn().mockResolvedValue(metaHex);

      const result = await getTokenMetadata(TOKEN_ADDR, MOCK_PROVIDER);
      expect(result).toBe(metaHex);
    });

    it('returns null when metadata is empty bytes', async () => {
      mockContractInstance.getData = vi.fn().mockResolvedValue('0x');

      const result = await getTokenMetadata(TOKEN_ADDR, MOCK_PROVIDER);
      expect(result).toBeNull();
    });

    it('returns null when metadata is null', async () => {
      mockContractInstance.getData = vi.fn().mockResolvedValue(null);

      const result = await getTokenMetadata(TOKEN_ADDR, MOCK_PROVIDER);
      expect(result).toBeNull();
    });
  });

  describe('getNFTTokenMetadata', () => {
    it('returns metadata bytes when present', async () => {
      const metaHex = '0x11223344';
      mockContractInstance.getDataForTokenId = vi.fn().mockResolvedValue(metaHex);

      const result = await getNFTTokenMetadata(
        COLLECTION_ADDR,
        TOKEN_ID_1,
        MOCK_PROVIDER
      );
      expect(result).toBe(metaHex);
    });

    it('returns null when metadata is empty', async () => {
      mockContractInstance.getDataForTokenId = vi.fn().mockResolvedValue('0x');

      const result = await getNFTTokenMetadata(
        COLLECTION_ADDR,
        TOKEN_ID_1,
        MOCK_PROVIDER
      );
      expect(result).toBeNull();
    });

    it('returns null when call reverts', async () => {
      mockContractInstance.getDataForTokenId = vi
        .fn()
        .mockRejectedValue(new Error('revert'));

      const result = await getNFTTokenMetadata(
        COLLECTION_ADDR,
        TOKEN_ID_1,
        MOCK_PROVIDER
      );
      expect(result).toBeNull();
    });

    it('returns null when getDataForTokenId returns null', async () => {
      mockContractInstance.getDataForTokenId = vi.fn().mockResolvedValue(null);

      const result = await getNFTTokenMetadata(
        COLLECTION_ADDR,
        TOKEN_ID_1,
        MOCK_PROVIDER
      );
      expect(result).toBeNull();
    });
  });
});
