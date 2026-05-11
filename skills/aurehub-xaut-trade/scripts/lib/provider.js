import { JsonRpcProvider } from 'ethers6';
import { loadConfig } from './config.js';

/**
 * Error codes and patterns that indicate a transient failure worth retrying
 * on another RPC endpoint.
 */
const RETRIABLE_HTTP_STATUSES = new Set([429, 502, 503]);
const RETRIABLE_NODE_CODES = new Set(['ECONNREFUSED', 'ETIMEDOUT', 'ENOTFOUND', 'ECONNRESET']);
const RETRIABLE_MSG_PATTERNS = [
  /rate.?limit/i,
  /too many requests/i,
  /timeout/i,
  /service unavailable/i,
  /bad gateway/i,
  /connection refused/i,
];

function isRetriable(err) {
  if (err.status && RETRIABLE_HTTP_STATUSES.has(err.status)) return true;
  if (err.code && RETRIABLE_NODE_CODES.has(err.code)) return true;
  if (err.message) {
    for (const pattern of RETRIABLE_MSG_PATTERNS) {
      if (pattern.test(err.message)) return true;
    }
  }
  return false;
}

export class FallbackProvider {
  /**
   * @param {string} primaryUrl  - Primary RPC URL (required)
   * @param {string[]} fallbackUrls - Ordered list of fallback URLs
   * @param {number} requestTimeoutMs - Per-request timeout for JSON-RPC calls
   */
  constructor(primaryUrl, fallbackUrls = [], requestTimeoutMs = 12_000) {
    if (!primaryUrl) {
      throw new Error('FallbackProvider requires a primary RPC URL');
    }
    this._primaryUrl = primaryUrl;
    this._fallbackUrls = fallbackUrls;
    this._requestTimeoutMs = requestTimeoutMs;
    // Underlying ethers provider always points at the current primary
    this._ethersProvider = new JsonRpcProvider(primaryUrl);
  }

  /**
   * Send a single JSON-RPC request to `url`. Override in tests to avoid
   * real network calls.
   *
   * @param {string} url
   * @param {string} method
   * @param {any[]} params
   * @returns {Promise<any>}
   */
  async _rawSend(url, method, params) {
    const body = JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method,
      params,
    });

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this._requestTimeoutMs);
    let response;
    try {
      response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        signal: controller.signal,
      });
    } catch (err) {
      if (err?.name === 'AbortError') {
        const timeoutErr = new Error(`RPC request timeout after ${this._requestTimeoutMs}ms`);
        timeoutErr.code = 'ETIMEDOUT';
        throw timeoutErr;
      }
      throw err;
    } finally {
      clearTimeout(timer);
    }

    if (!response.ok) {
      const err = new Error(`HTTP ${response.status}: ${response.statusText}`);
      err.status = response.status;
      throw err;
    }

    const json = await response.json();
    if (json.error) {
      const err = new Error(json.error.message ?? 'RPC error');
      err.code = json.error.code;
      throw err;
    }

    return json.result;
  }

  /**
   * Try the primary URL first; on retriable errors try each fallback in order.
   * Session-sticky: the first URL that succeeds becomes the new primary.
   *
   * @param {string} method
   * @param {any[]} params
   * @returns {Promise<any>}
   */
  async _sendWithFallback(method, params) {
    const urls = [this._primaryUrl, ...this._fallbackUrls];
    const errors = [];

    for (let i = 0; i < urls.length; i++) {
      const url = urls[i];
      try {
        const result = await this._rawSend(url, method, params);

        // Session-sticky: promote successful fallback to primary
        if (i > 0) {
          const oldPrimary = this._primaryUrl;
          this._primaryUrl = url;
          this._fallbackUrls = [
            oldPrimary,
            ...urls.slice(1, i),
            ...urls.slice(i + 1),
          ];
          this._ethersProvider = new JsonRpcProvider(this._primaryUrl);
        }

        return result;
      } catch (err) {
        if (!isRetriable(err) || i === urls.length - 1) {
          // Non-retriable: throw immediately without trying fallbacks
          if (!isRetriable(err)) throw err;
        }
        errors.push({ url, error: err });
      }
    }

    // All URLs failed — redact API keys from URLs before logging
    const redact = (u) => { try { const o = new URL(u); return `${o.protocol}//${o.host}${o.pathname.replace(/\/[^/]{20,}$/, '/***')}`; } catch { return '[invalid url]'; } };
    const summary = errors
      .map(({ url, error }) => `${redact(url)}: ${error.message}`)
      .join('; ');
    throw new Error(`All RPC endpoints failed — ${summary}`);
  }

  /**
   * Generic JSON-RPC send.
   */
  async send(method, params) {
    return this._sendWithFallback(method, params);
  }

  /**
   * eth_call — routes through fallback path.
   */
  async call(tx) {
    return this._sendWithFallback('eth_call', [tx, 'latest']);
  }

  /**
   * eth_blockNumber — routes through fallback path.
   */
  async getBlockNumber() {
    return this._sendWithFallback('eth_blockNumber', []);
  }

  /**
   * eth_getBalance — routes through fallback path.
   */
  async getBalance(address) {
    return this._sendWithFallback('eth_getBalance', [address, 'latest']);
  }

  /**
   * Return the underlying ethers JsonRpcProvider (e.g. for Wallet.connect()).
   * Always reflects the current primary URL (updated after fallback switches).
   */
  getEthersProvider() {
    return this._ethersProvider;
  }

  /**
   * Wait for a transaction receipt with fallback support.
   * When the current provider's waitForTransaction fails with a retriable
   * error, try each fallback URL's provider instead.
   *
   * @param {string} txHash
   * @param {number} [confirmations=1]
   * @param {number} [timeoutMs=300000]
   * @returns {Promise<import('ethers6').TransactionReceipt|null>}
   */
  async waitForTransaction(txHash, confirmations = 1, timeoutMs = 300000) {
    const urls = [this._primaryUrl, ...this._fallbackUrls];

    // Race all URLs in parallel — whichever returns the receipt first wins.
    // This prevents a slow/lagging primary RPC from blocking confirmation
    // detection when faster fallback nodes already have the receipt indexed.
    const providers = urls.map(url => {
      const p = new JsonRpcProvider(url);
      p.pollingInterval = 1000;
      return p;
    });

    // Do NOT pass timeoutMs to individual providers — ethers6 creates an internal
    // setTimeout for the timeout that destroy() cannot cancel, which would hold
    // the event loop for the full duration. Manage the overall timeout ourselves.
    const racePromises = providers.map((provider, i) =>
      provider.waitForTransaction(txHash, confirmations)
        .then(receipt => ({ receipt, index: i }))
    );

    let result;
    let timer;
    try {
      result = await Promise.race([
        Promise.any(racePromises),
        new Promise((_, reject) => {
          timer = setTimeout(() => reject(new Error(
            `waitForTransaction timeout after ${timeoutMs / 1000}s`
          )), timeoutMs);
        }),
      ]);
    } finally {
      clearTimeout(timer);
      // Destroy all providers to stop their polling loops and free the event loop.
      providers.forEach(p => p.destroy());
    }

    const { receipt, index } = result;

    // Promote the winning URL to primary if it was a fallback
    if (index > 0) {
      const oldPrimary = this._primaryUrl;
      this._primaryUrl = urls[index];
      this._fallbackUrls = [
        oldPrimary,
        ...urls.slice(1, index),
        ...urls.slice(index + 1),
      ];
      this._ethersProvider = new JsonRpcProvider(this._primaryUrl);
    }

    return receipt;
  }
}

/**
 * Build a FallbackProvider from an env object.
 *
 * @param {Record<string, string>} env
 * @returns {FallbackProvider}
 */
export function createProvider(env) {
  let effectiveEnv = env;
  if (!effectiveEnv?.ETH_RPC_URL) {
    // Fallback: load from ~/.aurehub/.env when env vars are not exported
    try {
      const cfg = loadConfig();
      effectiveEnv = { ...cfg.env, ...effectiveEnv };
    } catch (_) {
      // ignore — will throw below if still missing
    }
  }

  const primaryUrl = effectiveEnv.ETH_RPC_URL;
  if (!primaryUrl) {
    throw new Error(
      'ETH_RPC_URL is required in env to create a provider'
    );
  }

  const fallbackUrls = effectiveEnv.ETH_RPC_URL_FALLBACK
    ? effectiveEnv.ETH_RPC_URL_FALLBACK.split(',').map((u) => u.trim()).filter(Boolean)
    : [];

  return new FallbackProvider(primaryUrl, fallbackUrls);
}
