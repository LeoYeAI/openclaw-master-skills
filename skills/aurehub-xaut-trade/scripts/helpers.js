/**
 * Compute Permit2 invalidateUnorderedNonces arguments from a UniswapX nonce.
 * @param {bigint} nonce
 * @returns {{ wordPos: bigint, mask: bigint }}
 */
function computeNonceComponents(nonce) {
  const wordPos = nonce >> 8n;
  const mask = 1n << (nonce & 0xFFn);
  return { wordPos, mask };
}

/**
 * Resolve expiry seconds with clamping. Returns default if input is null/undefined.
 * @param {number|null|undefined} inputSeconds
 * @param {{ defaultSeconds: number, minSeconds: number, maxSeconds: number }} limits
 * @returns {number}
 */
function resolveExpiry(inputSeconds, limits) {
  if (inputSeconds == null) return limits.defaultSeconds;
  return Math.max(limits.minSeconds, Math.min(limits.maxSeconds, inputSeconds));
}

/**
 * Check that an amount string does not exceed maxDecimals decimal places.
 * @param {string} amount - must be a decimal string (not scientific notation)
 * @param {number} maxDecimals
 * @returns {boolean}
 */
function checkPrecision(amount, maxDecimals) {
  const s = String(amount);
  const dotIndex = s.indexOf('.');
  if (dotIndex === -1) return true;
  return s.length - dotIndex - 1 <= maxDecimals;
}

export { computeNonceComponents, resolveExpiry, checkPrecision };
