/**
 * HTTP client for ClawSend relay server.
 */

import * as crypto from './crypto.js';

// Default relay URL
export const DEFAULT_RELAY = 'https://clawsend-relay-production.up.railway.app';

// Request timeout (ms)
const DEFAULT_TIMEOUT = 30000;

export class ClientError extends Error {
  constructor(message, statusCode = null, response = null) {
    super(message);
    this.name = 'ClientError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

export class AuthenticationError extends ClientError {
  constructor(message, statusCode = null, response = null) {
    super(message, statusCode, response);
    this.name = 'AuthenticationError';
  }
}

export class ServerError extends ClientError {
  constructor(message, statusCode = null, response = null) {
    super(message, statusCode, response);
    this.name = 'ServerError';
  }
}

export class NetworkError extends ClientError {
  constructor(message) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class RelayClient {
  constructor(vault, serverUrl = null, timeout = DEFAULT_TIMEOUT) {
    this.vault = vault;
    this.serverUrl = (serverUrl || DEFAULT_RELAY).replace(/\/+$/, '');
    this.timeout = timeout;
  }

  _url(endpoint) {
    return `${this.serverUrl}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
  }

  async _handleResponse(response) {
    let data;
    try {
      data = await response.json();
    } catch {
      data = { error: response.statusText || 'Unknown error' };
    }

    if (response.status === 401 || response.status === 403) {
      throw new AuthenticationError(data.error || 'Authentication failed', response.status, data);
    } else if (response.status >= 400) {
      throw new ServerError(data.error || `Server error: ${response.status}`, response.status, data);
    }

    return data;
  }

  async _request(method, endpoint, { json = null, sign = false } = {}) {
    const url = this._url(endpoint);
    const headers = { 'Content-Type': 'application/json' };

    if (sign && json) {
      const signature = this.vault.sign(json);
      headers['X-Signature'] = signature;
      headers['X-Vault-ID'] = this.vault.vaultId;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers,
        body: json ? JSON.stringify(json) : undefined,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return await this._handleResponse(response);
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        throw new NetworkError('Request timed out');
      }
      if (err instanceof ClientError) {
        throw err;
      }
      throw new NetworkError(`Request failed: ${err.message}`);
    }
  }

  async get(endpoint) {
    return this._request('GET', endpoint);
  }

  async post(endpoint, data = null, sign = false) {
    return this._request('POST', endpoint, { json: data, sign });
  }

  // =========================================================================
  // API Methods
  // =========================================================================

  async health() {
    return this.get('/health');
  }

  async getChallenge() {
    return this.post('/register/challenge', {
      vault_id: this.vault.vaultId,
      signing_public_key: this.vault.signingPublicKeyB64,
      encryption_public_key: this.vault.encryptionPublicKeyB64,
    });
  }

  async register(challenge, signature, alias = null) {
    const data = {
      vault_id: this.vault.vaultId,
      signing_public_key: this.vault.signingPublicKeyB64,
      encryption_public_key: this.vault.encryptionPublicKeyB64,
      challenge,
      challenge_signature: signature,
    };
    if (alias) {
      data.alias = alias;
    }
    return this.post('/register', data);
  }

  async sendMessage(message, signature, encryptedPayload = null) {
    const data = {
      message,
      signature,
    };
    if (encryptedPayload) {
      data.encrypted_payload = encryptedPayload;
    }
    return this.post('/send', data, true);
  }

  async receive(limit = 50) {
    return this.get(`/receive/${this.vault.vaultId}?limit=${limit}`);
  }

  async acknowledge(messageId) {
    return this.post(`/ack/${messageId}`, { vault_id: this.vault.vaultId }, true);
  }

  async listAgents(limit = 100) {
    return this.get(`/agents?limit=${limit}`);
  }

  async resolveAlias(alias) {
    return this.get(`/resolve/${alias}`);
  }

  async setAlias(alias) {
    return this.post('/alias', { vault_id: this.vault.vaultId, alias }, true);
  }
}

// =========================================================================
// Output Helpers
// =========================================================================

export function outputJson(data) {
  console.log(JSON.stringify(data, null, 2));
}

export function outputError(message, code = 'error') {
  console.error(JSON.stringify({ error: message, code }, null, 2));
}

export function outputHuman(message) {
  console.error(message);
}
