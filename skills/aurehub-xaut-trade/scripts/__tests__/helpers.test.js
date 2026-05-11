import { describe, it, expect } from 'vitest';
import { computeNonceComponents, resolveExpiry, checkPrecision } from '../helpers.js';

// --- computeNonceComponents ---
// Permit2 invalidateUnorderedNonces(wordPos, mask):
//   wordPos = nonce >> 8n   (which 256-bit word)
//   mask    = 1n << (nonce & 0xFFn)  (which bit within the word)

describe('computeNonceComponents', () => {
  it('nonce 0 → wordPos 0, mask 1', () => {
    const { wordPos, mask } = computeNonceComponents(0n);
    expect(wordPos).toBe(0n);
    expect(mask).toBe(1n);
  });

  it('nonce 1 → wordPos 0, mask 2', () => {
    const { wordPos, mask } = computeNonceComponents(1n);
    expect(wordPos).toBe(0n);
    expect(mask).toBe(2n);
  });

  it('nonce 255 → wordPos 0, mask 2^255', () => {
    const { wordPos, mask } = computeNonceComponents(255n);
    expect(wordPos).toBe(0n);
    expect(mask).toBe(2n ** 255n);
  });

  it('nonce 256 → wordPos 1, mask 1', () => {
    const { wordPos, mask } = computeNonceComponents(256n);
    expect(wordPos).toBe(1n);
    expect(mask).toBe(1n);
  });

  it('nonce 257 → wordPos 1, mask 2', () => {
    const { wordPos, mask } = computeNonceComponents(257n);
    expect(wordPos).toBe(1n);
    expect(mask).toBe(2n);
  });
});

// --- resolveExpiry ---

describe('resolveExpiry', () => {
  const limits = { defaultSeconds: 86400, minSeconds: 300, maxSeconds: 2592000 };

  it('null → default', () => {
    expect(resolveExpiry(null, limits)).toBe(86400);
  });

  it('undefined → default', () => {
    expect(resolveExpiry(undefined, limits)).toBe(86400);
  });

  it('value within range → unchanged', () => {
    expect(resolveExpiry(3600, limits)).toBe(3600);
  });

  it('below min → clamped to min', () => {
    expect(resolveExpiry(60, limits)).toBe(300);
  });

  it('above max → clamped to max', () => {
    expect(resolveExpiry(9999999, limits)).toBe(2592000);
  });

  it('exactly min → allowed', () => {
    expect(resolveExpiry(300, limits)).toBe(300);
  });

  it('exactly max → allowed', () => {
    expect(resolveExpiry(2592000, limits)).toBe(2592000);
  });
});

// --- checkPrecision ---

describe('checkPrecision', () => {
  it('integer → valid', () => {
    expect(checkPrecision('1000000', 6)).toBe(true);
  });

  it('exactly 6 decimals → valid', () => {
    expect(checkPrecision('0.000001', 6)).toBe(true);
  });

  it('7 decimals → invalid', () => {
    expect(checkPrecision('0.0000001', 6)).toBe(false);
  });

  it('no dot → valid', () => {
    expect(checkPrecision('42', 6)).toBe(true);
  });

  it('5 decimals → valid', () => {
    expect(checkPrecision('1.12345', 6)).toBe(true);
  });

  it('boundary: maxDecimals=0 integer → valid', () => {
    expect(checkPrecision('5', 0)).toBe(true);
  });
});
