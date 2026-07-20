import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { authenticate, isTokenValid, getValidToken, readCredentials, saveCredentials } from './auth.js';
import { writeFile, rm, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

// Mock fetch for testing
let originalFetch;
let mockFetchImpl;

function mockFetch(impl) {
  mockFetchImpl = impl;
}

function createMockResponse(status, body) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
    text: async () => JSON.stringify(body),
  };
}

describe('auth', () => {
  beforeEach(() => {
    originalFetch = globalThis.fetch;
    globalThis.fetch = async (...args) => mockFetchImpl(...args);
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    mockFetchImpl = null;
  });

  describe('authenticate', () => {
    it('completes challenge-response flow', async () => {
      const calls = [];

      mockFetch(async (url, opts) => {
        const body = JSON.parse(opts.body);
        calls.push({ url, body });

        if (url.includes('/auth/challenge')) {
          return createMockResponse(200, {
            nonceId: 'nonce-123',
            nonce: Buffer.from('test-nonce-32-bytes-padding!!!!!').toString('base64'),
            expiresAt: '2025-01-01T12:05:00.000Z',
          });
        }
        if (url.includes('/auth/verify')) {
          return createMockResponse(200, {
            botToken: 'tok_abc123',
            expiresAt: '2025-01-08T12:00:00.000Z',
            scopes: ['bot:messaging', 'bot:discovery'],
          });
        }
        return createMockResponse(404, { error: 'Not found' });
      });

      const result = await authenticate(
        'bot-uuid-123',
        Buffer.from(new Uint8Array(32)).toString('base64'),
        'https://example.com/api',
      );

      assert.equal(calls.length, 2);
      assert.ok(calls[0].url.includes('/auth/challenge'));
      assert.equal(calls[0].body.botProfileId, 'bot-uuid-123');
      assert.ok(calls[1].url.includes('/auth/verify'));
      assert.equal(calls[1].body.botProfileId, 'bot-uuid-123');
      assert.equal(calls[1].body.nonceId, 'nonce-123');
      assert.ok(calls[1].body.signature, 'signature should be present');

      assert.equal(result.botToken, 'tok_abc123');
      assert.equal(result.expiresAt, '2025-01-08T12:00:00.000Z');
    });

    it('handles challenge rate limiting (429)', async () => {
      mockFetch(async () => createMockResponse(429, { error: 'Too many requests' }));

      await assert.rejects(
        () => authenticate('bot-uuid', Buffer.from(new Uint8Array(32)).toString('base64')),
        (err) => {
          assert.ok(err.message.includes('Rate limited'));
          assert.ok(err.message.includes('429'));
          return true;
        },
      );
    });

    it('handles verify failure (403 Forbidden)', async () => {
      let callCount = 0;
      mockFetch(async (url) => {
        callCount++;
        if (url.includes('/auth/challenge')) {
          return createMockResponse(200, {
            nonceId: 'nonce-123',
            nonce: Buffer.from('test-nonce-32-bytes-padding!!!!!').toString('base64'),
            expiresAt: '2025-01-01T12:05:00.000Z',
          });
        }
        return createMockResponse(403, { error: 'Bot not active' });
      });

      await assert.rejects(
        () => authenticate('bot-uuid', Buffer.from(new Uint8Array(32)).toString('base64')),
        (err) => {
          assert.ok(err.message.includes('403'));
          assert.ok(err.message.includes('not be claimed'));
          return true;
        },
      );
      assert.equal(callCount, 2, 'should have called challenge and verify');
    });

    it('handles network errors on challenge', async () => {
      mockFetch(async () => {
        throw new Error('ECONNREFUSED');
      });

      await assert.rejects(
        () => authenticate('bot-uuid', Buffer.from(new Uint8Array(32)).toString('base64')),
        (err) => {
          assert.ok(err.message.includes('Network error'));
          return true;
        },
      );
    });

    it('handles network errors on verify', async () => {
      let callCount = 0;
      mockFetch(async (url) => {
        callCount++;
        if (callCount === 1) {
          return createMockResponse(200, {
            nonceId: 'nonce-123',
            nonce: Buffer.from('test-nonce-32-bytes-padding!!!!!').toString('base64'),
            expiresAt: '2025-01-01T12:05:00.000Z',
          });
        }
        throw new Error('Connection reset');
      });

      await assert.rejects(
        () => authenticate('bot-uuid', Buffer.from(new Uint8Array(32)).toString('base64')),
        (err) => {
          assert.ok(err.message.includes('Network error'));
          return true;
        },
      );
    });

    it('validates required parameters', async () => {
      await assert.rejects(
        () => authenticate(null, 'key'),
        (err) => {
          assert.ok(err.message.includes('botProfileId'));
          return true;
        },
      );

      await assert.rejects(
        () => authenticate('bot-uuid', null),
        (err) => {
          assert.ok(err.message.includes('privateKey'));
          return true;
        },
      );
    });

    it('handles invalid JSON from challenge', async () => {
      mockFetch(async () => ({
        ok: true,
        status: 200,
        json: async () => { throw new Error('bad json'); },
        text: async () => 'not json',
      }));

      await assert.rejects(
        () => authenticate('bot-uuid', Buffer.from(new Uint8Array(32)).toString('base64')),
        (err) => {
          assert.ok(err.message.includes('Invalid JSON'));
          return true;
        },
      );
    });
  });

  describe('isTokenValid', () => {
    it('returns false when no token cached', () => {
      assert.equal(isTokenValid({}), false);
      assert.equal(isTokenValid({ botToken: 'tok' }), false);
      assert.equal(isTokenValid({ tokenExpiresAt: '2030-01-01T00:00:00Z' }), false);
    });

    it('returns true when token expires more than 24 hours from now', () => {
      const futureDate = new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString();
      assert.equal(isTokenValid({ botToken: 'tok', tokenExpiresAt: futureDate }), true);
    });

    it('returns false when token expires within 24 hours', () => {
      const nearFuture = new Date(Date.now() + 12 * 60 * 60 * 1000).toISOString();
      assert.equal(isTokenValid({ botToken: 'tok', tokenExpiresAt: nearFuture }), false);
    });

    it('returns false when token is already expired', () => {
      const past = new Date(Date.now() - 60 * 60 * 1000).toISOString();
      assert.equal(isTokenValid({ botToken: 'tok', tokenExpiresAt: past }), false);
    });
  });

  describe('credentials file operations', () => {
    const tmpDir = join(tmpdir(), `pob-auth-test-${Date.now()}`);
    const credFile = join(tmpDir, 'test-creds.json');

    afterEach(async () => {
      await rm(tmpDir, { recursive: true, force: true });
    });

    it('saves and reads credentials', async () => {
      const creds = {
        handle: 'test_bot',
        botProfileId: 'uuid-123',
        privateKey: 'privkey-b64',
        botToken: 'tok_abc',
        tokenExpiresAt: '2025-01-08T12:00:00.000Z',
      };

      await saveCredentials(credFile, creds);
      const loaded = await readCredentials(credFile);

      assert.deepStrictEqual(loaded, creds);
    });

    it('creates parent directories', async () => {
      const nestedFile = join(tmpDir, 'a', 'b', 'c', 'creds.json');
      await saveCredentials(nestedFile, { handle: 'nested' });
      const loaded = await readCredentials(nestedFile);
      assert.equal(loaded.handle, 'nested');
    });

    it('throws on missing credentials file', async () => {
      await assert.rejects(
        () => readCredentials('/nonexistent/path/creds.json'),
        (err) => {
          assert.ok(err.message.includes('not found'));
          return true;
        },
      );
    });
  });

  describe('getValidToken', () => {
    it('returns cached token when still valid', async () => {
      const tmpDir = join(tmpdir(), `pob-token-test-${Date.now()}`);
      const credFile = join(tmpDir, 'creds.json');

      try {
        const futureDate = new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString();
        await saveCredentials(credFile, {
          handle: 'cached_bot',
          botProfileId: 'uuid-123',
          privateKey: 'privkey-b64',
          botToken: 'cached_token',
          tokenExpiresAt: futureDate,
        });

        // fetch should NOT be called since we have a valid cached token
        mockFetch(async () => {
          throw new Error('Should not call fetch for valid cached token');
        });

        const result = await getValidToken({
          botProfileId: 'uuid-123',
          privateKey: 'privkey-b64',
          credentialsFile: credFile,
        });

        assert.equal(result.botToken, 'cached_token');
        assert.equal(result.expiresAt, futureDate);
      } finally {
        await rm(tmpDir, { recursive: true, force: true });
      }
    });

    it('re-authenticates when token is expired', async () => {
      const tmpDir = join(tmpdir(), `pob-reauth-test-${Date.now()}`);
      const credFile = join(tmpDir, 'creds.json');

      try {
        const pastDate = new Date(Date.now() - 60 * 60 * 1000).toISOString();
        await saveCredentials(credFile, {
          handle: 'expired_bot',
          botProfileId: 'uuid-123',
          privateKey: Buffer.from(new Uint8Array(32)).toString('base64'),
          botToken: 'expired_token',
          tokenExpiresAt: pastDate,
        });

        mockFetch(async (url) => {
          if (url.includes('/auth/challenge')) {
            return createMockResponse(200, {
              nonceId: 'nonce-new',
              nonce: Buffer.from('test-nonce-32-bytes-padding!!!!!').toString('base64'),
              expiresAt: '2025-01-01T12:05:00.000Z',
            });
          }
          const newExpiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();
          return createMockResponse(200, {
            botToken: 'new_token_abc',
            expiresAt: newExpiry,
            scopes: ['bot:messaging'],
          });
        });

        const result = await getValidToken({
          botProfileId: 'uuid-123',
          privateKey: Buffer.from(new Uint8Array(32)).toString('base64'),
          credentialsFile: credFile,
        });

        assert.equal(result.botToken, 'new_token_abc');

        // Verify credentials file was updated
        const updatedCreds = await readCredentials(credFile);
        assert.equal(updatedCreds.botToken, 'new_token_abc');
      } finally {
        await rm(tmpDir, { recursive: true, force: true });
      }
    });

    it('authenticates without credentials file', async () => {
      mockFetch(async (url) => {
        if (url.includes('/auth/challenge')) {
          return createMockResponse(200, {
            nonceId: 'nonce-direct',
            nonce: Buffer.from('test-nonce-32-bytes-padding!!!!!').toString('base64'),
            expiresAt: '2025-01-01T12:05:00.000Z',
          });
        }
        return createMockResponse(200, {
          botToken: 'direct_token',
          expiresAt: '2025-01-08T12:00:00.000Z',
          scopes: ['bot:messaging'],
        });
      });

      const result = await getValidToken({
        botProfileId: 'uuid-direct',
        privateKey: Buffer.from(new Uint8Array(32)).toString('base64'),
      });

      assert.equal(result.botToken, 'direct_token');
    });
  });
});
