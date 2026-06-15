/**
 * Tests for session ID resolution
 * Verifies lookup by ID, label, channel, and combos
 */

const { resolveSessionId } = require('../../lib/capacity');
const path = require('path');

describe('Session ID Resolution', () => {
  const fixtureDir = path.join(__dirname, '../fixtures/session-resolution');

  describe('UUID resolution', () => {
    test('should pass through full UUID unchanged', () => {
      const uuid = '6eff94ac-dde7-4621-acaf-66bb431db822';
      const result = resolveSessionId(uuid, fixtureDir);
      
      expect(result.sessionId).toBe(uuid);
      expect(result.ambiguous).toBe(false);
      expect(result.error).toBeUndefined();
    });

    test('should pass through partial UUID (8+ chars)', () => {
      const shortUuid = '6eff94ac-dde7';
      const result = resolveSessionId(shortUuid, fixtureDir);
      
      expect(result.sessionId).toBe(shortUuid);
      expect(result.ambiguous).toBe(false);
      expect(result.error).toBeUndefined();
    });

    test('should not pass through 8 chars without hyphen (not UUID format)', () => {
      // UUID pattern requires hyphen: /^[0-9a-f]{8}-/
      const notUuid = 'a3b2c1d4';
      const result = resolveSessionId(notUuid, fixtureDir);
      
      // Should try to resolve as label/channel instead
      expect(result.sessionId).toBeNull(); // No match found
      expect(result.error).toContain('No sessions found');
    });
  });

  describe('Label resolution', () => {
    test('should resolve exact label match', () => {
      const result = resolveSessionId('#navi-code-yatta', fixtureDir);
      
      expect(result.sessionId).toBe('6eff94ac-dde7-4621-acaf-66bb431db822');
      expect(result.ambiguous).toBe(false);
      expect(result.matches).toBeDefined();
      expect(result.matches.length).toBe(1);
      expect(result.matches[0].matchType).toBe('exact-label');
    });

    test('should resolve different label', () => {
      const result = resolveSessionId('#general', fixtureDir);
      
      expect(result.sessionId).toBe('a3b2c1d4-ef56-7890-1234-567890abcdef');
      expect(result.ambiguous).toBe(false);
    });

    test('should resolve personal label', () => {
      const result = resolveSessionId('#personal', fixtureDir);
      
      expect(result.sessionId).toBe('c5d6e7f8-9012-3456-7890-abcdef123456');
      expect(result.ambiguous).toBe(false);
    });
  });

  describe('Channel resolution', () => {
    test('should resolve webchat (unique channel)', () => {
      const result = resolveSessionId('webchat', fixtureDir);
      
      expect(result.sessionId).toBe('b4c5d6e7-f890-1234-5678-90abcdef1234');
      expect(result.ambiguous).toBe(false);
      expect(result.matches).toBeDefined();
      expect(result.matches.length).toBe(1);
      expect(result.matches[0].matchType).toBe('channel');
    });

    test('should resolve telegram (unique channel)', () => {
      const result = resolveSessionId('telegram', fixtureDir);
      
      expect(result.sessionId).toBe('c5d6e7f8-9012-3456-7890-abcdef123456');
      expect(result.ambiguous).toBe(false);
    });

    test('should detect ambiguous match for discord (2 sessions)', () => {
      const result = resolveSessionId('discord', fixtureDir);
      
      expect(result.sessionId).toBeNull();
      expect(result.ambiguous).toBe(true);
      expect(result.matches).toBeDefined();
      expect(result.matches.length).toBe(2);
      expect(result.error).toContain('Multiple sessions match');
    });
  });

  describe('Channel/label combo resolution', () => {
    test('should resolve discord/#navi-code-yatta combo', () => {
      const result = resolveSessionId('discord/#navi-code-yatta', fixtureDir);
      
      expect(result.sessionId).toBe('6eff94ac-dde7-4621-acaf-66bb431db822');
      expect(result.ambiguous).toBe(false);
      expect(result.matches).toBeDefined();
      expect(result.matches.length).toBe(1);
    });

    test('should resolve discord/#general combo', () => {
      const result = resolveSessionId('discord/#general', fixtureDir);
      
      expect(result.sessionId).toBe('a3b2c1d4-ef56-7890-1234-567890abcdef');
      expect(result.ambiguous).toBe(false);
    });

    test('should resolve telegram/#personal combo', () => {
      const result = resolveSessionId('telegram/#personal', fixtureDir);
      
      expect(result.sessionId).toBe('c5d6e7f8-9012-3456-7890-abcdef123456');
      expect(result.ambiguous).toBe(false);
    });
  });

  describe('Error cases', () => {
    test('should return error for non-existent label', () => {
      const result = resolveSessionId('#nonexistent', fixtureDir);
      
      expect(result.sessionId).toBeNull();
      expect(result.ambiguous).toBe(false);
      expect(result.error).toContain('No sessions found matching');
    });

    test('should return error for non-existent channel', () => {
      const result = resolveSessionId('slack', fixtureDir);
      
      expect(result.sessionId).toBeNull();
      expect(result.ambiguous).toBe(false);
      expect(result.error).toContain('No sessions found matching');
    });

    test('should return error for non-existent combo', () => {
      const result = resolveSessionId('discord/#nonexistent', fixtureDir);
      
      expect(result.sessionId).toBeNull();
      expect(result.ambiguous).toBe(false);
      expect(result.error).toContain('No sessions found matching');
    });
  });

  describe('Ambiguous match details', () => {
    test('should provide match details for ambiguous discord sessions', () => {
      const result = resolveSessionId('discord', fixtureDir);
      
      expect(result.ambiguous).toBe(true);
      expect(result.matches.length).toBe(2);
      
      // Check first match
      const match1 = result.matches.find(m => m.label === '#navi-code-yatta');
      expect(match1).toBeDefined();
      expect(match1.sessionId).toBe('6eff94ac-dde7-4621-acaf-66bb431db822');
      expect(match1.channel).toBe('discord');
      
      // Check second match
      const match2 = result.matches.find(m => m.label === '#general');
      expect(match2).toBeDefined();
      expect(match2.sessionId).toBe('a3b2c1d4-ef56-7890-1234-567890abcdef');
      expect(match2.channel).toBe('discord');
    });

    test('should provide helpful error message for ambiguous matches', () => {
      const result = resolveSessionId('discord', fixtureDir);
      
      expect(result.error).toBe('Multiple sessions match "discord". Please be more specific.');
    });
  });

  describe('Match type validation', () => {
    test('should return correct match type for exact label', () => {
      const result = resolveSessionId('#navi-code-yatta', fixtureDir);
      
      expect(result.matches[0].matchType).toBe('exact-label');
    });

    test('should return correct match type for channel', () => {
      const result = resolveSessionId('webchat', fixtureDir);
      
      expect(result.matches[0].matchType).toBe('channel');
    });

    test('should return correct match type for combo', () => {
      const result = resolveSessionId('discord/#general', fixtureDir);
      
      expect(result.matches[0].matchType).toBe('combo');
    });
  });

  describe('Edge cases', () => {
    test('should handle empty string', () => {
      const result = resolveSessionId('', fixtureDir);
      
      expect(result.sessionId).toBeNull();
      // Empty string might match multiple sessions in some implementations
      // The important thing is it doesn't return a sessionId
      expect(result.error).toBeDefined();
    });

    test('should handle whitespace-only input', () => {
      const result = resolveSessionId('   ', fixtureDir);
      
      expect(result.sessionId).toBeNull();
      expect(result.error).toContain('No sessions found');
    });

    test('should be case-sensitive for labels', () => {
      const result = resolveSessionId('#NAVI-CODE-YATTA', fixtureDir);
      
      // Should not match (case-sensitive)
      expect(result.sessionId).toBeNull();
      expect(result.error).toContain('No sessions found');
    });

    test('should be case-sensitive for channels', () => {
      const result = resolveSessionId('DISCORD', fixtureDir);
      
      // Should not match (case-sensitive)
      expect(result.sessionId).toBeNull();
      expect(result.error).toContain('No sessions found');
    });
  });
});
