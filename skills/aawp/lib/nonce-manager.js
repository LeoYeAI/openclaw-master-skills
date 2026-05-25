'use strict';

/**
 * NonceManager — local pending nonce tracking to prevent concurrent tx nonce conflicts.
 * Singleton module.
 */
class NonceManager {
  constructor() {
    this._pending = {};  // key: "chainId:walletAddr" → { base, offset }
    this._locks = {};    // simple mutex per key
  }

  _key(walletAddr, chainId) {
    return `${chainId}:${walletAddr.toLowerCase()}`;
  }

  /**
   * Get next nonce (on-chain nonce + local pending offset).
   * @param {object} provider - ethers JsonRpcProvider
   * @param {string} walletAddr - AAWP wallet address
   * @param {number} chainId
   * @param {object} walletContract - ethers Contract with nonce() method
   * @returns {Promise<number>}
   */
  async getNonce(provider, walletAddr, chainId, walletContract) {
    const k = this._key(walletAddr, chainId);

    // Simple lock: wait if another call is in progress
    while (this._locks[k]) {
      await new Promise(r => setTimeout(r, 50));
    }
    this._locks[k] = true;

    try {
      if (!this._pending[k]) {
        // First call: sync from chain
        const onChainNonce = walletContract
          ? Number(await walletContract.nonce())
          : 0;
        this._pending[k] = { base: onChainNonce, offset: 0 };
      }

      const nonce = this._pending[k].base + this._pending[k].offset;
      this._pending[k].offset++;
      return nonce;
    } finally {
      this._locks[k] = false;
    }
  }

  /**
   * Confirm a tx completed (success or failure). Decrements pending offset.
   */
  confirm(walletAddr, chainId) {
    const k = this._key(walletAddr, chainId);
    if (this._pending[k] && this._pending[k].offset > 0) {
      this._pending[k].base++;
      this._pending[k].offset--;
    }
  }

  /**
   * Reset — force re-sync from chain on next getNonce call.
   */
  reset(walletAddr, chainId) {
    const k = this._key(walletAddr, chainId);
    delete this._pending[k];
  }
}

module.exports = new NonceManager();
