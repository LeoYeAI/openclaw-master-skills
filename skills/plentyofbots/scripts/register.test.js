import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { registerBot } from './register.js';

// Mock fetch for testing
let originalFetch;
let mockFetchImpl;

function mockFetch(impl) {
  mockFetchImpl = impl;
}

function createMockResponse(status, body, ok = null) {
  return {
    ok: ok !== null ? ok : status >= 200 && status < 300,
    status,
    json: async () => body,
    text: async () => JSON.stringify(body),
  };
}

describe('register', () => {
  beforeEach(() => {
    originalFetch = globalThis.fetch;
    globalThis.fetch = async (...args) => mockFetchImpl(...args);
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    mockFetchImpl = null;
  });

  it('sends correct POST body to /bots/register', async () => {
    let capturedUrl;
    let capturedBody;

    mockFetch(async (url, opts) => {
      capturedUrl = url;
      capturedBody = JSON.parse(opts.body);
      return createMockResponse(201, {
        claimUrl: 'https://plentyofbots.ai/claim?token=abc',
        expiresAt: '2025-01-01T12:00:00.000Z',
        bot: { profile: { id: 'test-uuid' } },
      });
    });

    await registerBot({
      handle: 'test_bot',
      displayName: 'Test Bot',
      bio: 'A test bot',
      publicKey: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
    }, 'https://example.com/api');

    assert.equal(capturedUrl, 'https://example.com/api/bots/register');
    assert.equal(capturedBody.handle, 'test_bot');
    assert.equal(capturedBody.displayName, 'Test Bot');
    assert.equal(capturedBody.bio, 'A test bot');
    assert.equal(capturedBody.publicKey, 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=');
  });

  it('parses claim URL and bot profile ID from response', async () => {
    mockFetch(async () => createMockResponse(201, {
      claimUrl: 'https://plentyofbots.ai/claim?token=xyz',
      expiresAt: '2025-06-15T10:00:00.000Z',
      bot: { profile: { id: 'uuid-123-456' } },
    }));

    const result = await registerBot({
      handle: 'my_bot',
      displayName: 'My Bot',
      publicKey: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
    });

    assert.equal(result.claimUrl, 'https://plentyofbots.ai/claim?token=xyz');
    assert.equal(result.botProfileId, 'uuid-123-456');
    assert.equal(result.expiresAt, '2025-06-15T10:00:00.000Z');
  });

  it('handles 409 Conflict (handle already taken)', async () => {
    mockFetch(async () => createMockResponse(409, { error: 'Handle already taken' }));

    await assert.rejects(
      () => registerBot({
        handle: 'taken_bot',
        displayName: 'Taken Bot',
        publicKey: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
      }),
      (err) => {
        assert.ok(err.message.includes('already taken'));
        assert.ok(err.message.includes('409'));
        return true;
      },
    );
  });

  it('handles 429 Too Many Requests (rate limited)', async () => {
    mockFetch(async () => createMockResponse(429, { error: 'Rate limited' }));

    await assert.rejects(
      () => registerBot({
        handle: 'spam_bot',
        displayName: 'Spam Bot',
        publicKey: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
      }),
      (err) => {
        assert.ok(err.message.includes('Rate limited'));
        assert.ok(err.message.includes('429'));
        return true;
      },
    );
  });

  it('handles network errors gracefully', async () => {
    mockFetch(async () => {
      throw new Error('ECONNREFUSED');
    });

    await assert.rejects(
      () => registerBot({
        handle: 'net_bot',
        displayName: 'Net Bot',
        publicKey: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
      }),
      (err) => {
        assert.ok(err.message.includes('Network error'));
        return true;
      },
    );
  });

  it('handles invalid JSON response', async () => {
    mockFetch(async () => ({
      ok: true,
      status: 201,
      json: async () => { throw new Error('invalid json'); },
      text: async () => 'not json',
    }));

    await assert.rejects(
      () => registerBot({
        handle: 'json_bot',
        displayName: 'JSON Bot',
        publicKey: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
      }),
      (err) => {
        assert.ok(err.message.includes('Invalid JSON'));
        return true;
      },
    );
  });

  it('handles unexpected response format (missing claimUrl)', async () => {
    mockFetch(async () => createMockResponse(201, {
      bot: { profile: { id: 'uuid' } },
      // missing claimUrl
    }));

    await assert.rejects(
      () => registerBot({
        handle: 'bad_resp_bot',
        displayName: 'Bad Resp Bot',
        publicKey: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
      }),
      (err) => {
        assert.ok(err.message.includes('Unexpected response'));
        return true;
      },
    );
  });

  it('validates required fields', async () => {
    await assert.rejects(
      () => registerBot({ displayName: 'Bot', publicKey: 'key' }),
      (err) => {
        assert.ok(err.message.includes('handle'));
        return true;
      },
    );

    await assert.rejects(
      () => registerBot({ handle: 'bot', publicKey: 'key' }),
      (err) => {
        assert.ok(err.message.includes('displayName'));
        return true;
      },
    );

    await assert.rejects(
      () => registerBot({ handle: 'bot', displayName: 'Bot' }),
      (err) => {
        assert.ok(err.message.includes('publicKey'));
        return true;
      },
    );
  });

  it('passes extension fields through to the API', async () => {
    let capturedBody;

    mockFetch(async (url, opts) => {
      capturedBody = JSON.parse(opts.body);
      return createMockResponse(201, {
        claimUrl: 'https://plentyofbots.ai/claim?token=abc',
        expiresAt: '2025-01-01T12:00:00.000Z',
        bot: { profile: { id: 'test-uuid' } },
      });
    });

    await registerBot({
      handle: 'ext_bot',
      displayName: 'Extension Bot',
      publicKey: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
      personalityArchetype: 'comedian',
      vibe: 'playful',
      backstory: 'Born in the cloud',
    });

    assert.equal(capturedBody.personalityArchetype, 'comedian');
    assert.equal(capturedBody.vibe, 'playful');
    assert.equal(capturedBody.backstory, 'Born in the cloud');
  });

  it('handles 500 server errors', async () => {
    mockFetch(async () => createMockResponse(500, { error: 'Internal Server Error' }));

    await assert.rejects(
      () => registerBot({
        handle: 'err_bot',
        displayName: 'Error Bot',
        publicKey: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
      }),
      (err) => {
        assert.ok(err.message.includes('500'));
        return true;
      },
    );
  });

  it('uses default API base when none provided', async () => {
    let capturedUrl;

    mockFetch(async (url) => {
      capturedUrl = url;
      return createMockResponse(201, {
        claimUrl: 'https://plentyofbots.ai/claim?token=abc',
        expiresAt: '2025-01-01T12:00:00.000Z',
        bot: { profile: { id: 'uuid' } },
      });
    });

    await registerBot({
      handle: 'default_bot',
      displayName: 'Default Bot',
      publicKey: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
    });

    assert.equal(capturedUrl, 'https://plentyofbots.ai/api/bots/register');
  });
});
