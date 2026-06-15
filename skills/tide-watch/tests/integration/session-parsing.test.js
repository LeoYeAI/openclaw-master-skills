const path = require('path');
const {
  parseSession,
  loadSessionRegistry
} = require('../../lib/capacity');

const fixturesDir = path.join(__dirname, '..', 'fixtures');

describe('parseSession', () => {
  test('should parse session JSONL file', () => {
    const sessionPath = path.join(fixturesDir, 'test-session.jsonl');
    const session = parseSession(sessionPath);

    expect(session).toBeDefined();
    expect(session.sessionId).toBe('test-session-123');
    expect(session.tokensUsed).toBe(6000);
    expect(session.tokensMax).toBe(200000);
    expect(session.percentage).toBeCloseTo(3.0, 1);
    expect(session.messageCount).toBe(7);
    expect(session.model).toBe('claude-sonnet-4-5');
  });

  test('should handle session with registry metadata', () => {
    const sessionPath = path.join(fixturesDir, 'test-session.jsonl');
    const registry = loadSessionRegistry(fixturesDir);
    const session = parseSession(sessionPath, registry);

    expect(session).toBeDefined();
    expect(session.sessionId).toBe('test-session-123');
    expect(session.channel).toBe('discord');
    expect(session.label).toBe('#test-channel');
  });

  test('should return null for non-existent file', () => {
    const sessionPath = path.join(fixturesDir, 'non-existent.jsonl');
    const session = parseSession(sessionPath);

    expect(session).toBeNull();
  });
});

describe('loadSessionRegistry', () => {
  test('should load sessions.json registry', () => {
    const registry = loadSessionRegistry(fixturesDir);

    expect(registry).toBeDefined();
    expect(registry['test-session-123']).toBeDefined();
    expect(registry['test-session-123'].channel).toBe('discord');
    expect(registry['test-session-123'].label).toBe('#test-channel');
  });

  test('should load webchat session from registry', () => {
    const registry = loadSessionRegistry(fixturesDir);

    expect(registry['test-session-456']).toBeDefined();
    expect(registry['test-session-456'].channel).toBe('webchat');
    expect(registry['test-session-456'].label).toBeNull();
  });

  test('should return empty object for non-existent registry', () => {
    const registry = loadSessionRegistry('/non-existent-path');

    expect(registry).toEqual({});
  });
});
