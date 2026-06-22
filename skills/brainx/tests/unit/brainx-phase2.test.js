/**
 * BrainX V5 - Unit Tests for brainx-phase2.js
 * Run with: node --test tests/unit/brainx-phase2.test.js
 */

const { describe, it } = require('node:test');
const assert = require('node:assert');

// Import the module under test
const {
  getPhase2Config,
  shouldScrubForContext,
  scrubTextPII,
  mergeTagsWithMetadata,
  deriveMergePlan
} = require('../../lib/brainx-phase2');

describe('brainx-phase2', () => {
  describe('getPhase2Config', () => {
    it('should return default config when no env vars set', () => {
      const config = getPhase2Config();
      
      assert.strictEqual(typeof config.dedupeSimThreshold, 'number');
      assert.strictEqual(typeof config.dedupeRecentDays, 'number');
      assert.strictEqual(typeof config.piiScrubReplacement, 'string');
      assert.strictEqual(Array.isArray(config.piiScrubAllowlistContexts), true);
    });
  });

  describe('shouldScrubForContext', () => {
    it('should return true for null/undefined context (scrub by default)', () => {
      assert.strictEqual(shouldScrubForContext(null, {}), true);
      assert.strictEqual(shouldScrubForContext(undefined, {}), true);
    });

    it('should return false for allowlisted contexts', () => {
      const config = { piiScrubAllowlistContexts: ['safe', 'public', 'notes'] };
      assert.strictEqual(shouldScrubForContext('safe', config), false);
      assert.strictEqual(shouldScrubForContext('public', config), false);
      assert.strictEqual(shouldScrubForContext('notes', config), false);
    });

    it('should return true for non-allowlisted contexts', () => {
      const config = { piiScrubAllowlistContexts: ['safe', 'public'] };
      assert.strictEqual(shouldScrubForContext('secret', config), true);
      assert.strictEqual(shouldScrubForContext('password-vault', config), true);
    });
  });

  describe('scrubTextPII', () => {
    it('should return text unchanged when disabled', () => {
      const text = 'Contact me at user@example.com or call 123-456-7890';
      const result = scrubTextPII(text, { enabled: false });
      
      assert.strictEqual(result.text, text);
      assert.deepStrictEqual(result.reasons, []);
    });

    it('should detect email addresses when enabled', () => {
      const text = 'Contact me at user@example.com for details';
      const result = scrubTextPII(text, { enabled: true });
      
      assert.strictEqual(result.text.includes('user@example.com'), false);
      assert.strictEqual(result.reasons.includes('email'), true);
    });

    it('should detect phone numbers when enabled', () => {
      const text = 'Call me at 123-456-7890';
      const result = scrubTextPII(text, { enabled: true });
      
      assert.strictEqual(result.text.includes('123-456-7890'), false);
      assert.strictEqual(result.reasons.includes('phone'), true);
    });

    it('should use custom replacement string', () => {
      const text = 'Email: user@example.com';
      const result = scrubTextPII(text, { 
        enabled: true, 
        replacement: '[REDACTED]' 
      });
      
      assert.strictEqual(result.text.includes('[REDACTED]'), true);
    });
  });

  describe('mergeTagsWithMetadata', () => {
    it('should return original tags when no redaction', () => {
      const tags = ['important', 'project'];
      const meta = { redacted: false, reasons: [] };
      const result = mergeTagsWithMetadata(tags, meta);
      
      assert.deepStrictEqual(result, tags);
    });

    it('should add pii:redacted tag when redacted', () => {
      const tags = ['important'];
      const meta = { redacted: true, reasons: ['email'] };
      const result = mergeTagsWithMetadata(tags, meta);
      
      assert.strictEqual(result.includes('pii:redacted'), true);
      assert.strictEqual(result.includes('important'), true);
    });

    it('should preserve input tags as-is when not redacted', () => {
      const tags = ['important', 'project'];
      const meta = { redacted: false, reasons: [] };
      const result = mergeTagsWithMetadata(tags, meta);
      
      assert.deepStrictEqual(result, ['important', 'project']);
    });
  });

  describe('deriveMergePlan', () => {
    const now = new Date();
    
    it('should create new memory when no existing match', () => {
      const existing = null;
      const lifecycle = { 
        recurrence_count: 1, 
        first_seen: now, 
        last_seen: now,
        _now: now
      };
      
      const plan = deriveMergePlan(existing, lifecycle, now);
      
      assert.strictEqual(plan.found, false);
      assert.strictEqual(plan.finalRecurrence, 1);
    });

    it('should merge with existing when pattern matches', () => {
      const existingId = 'mem-123';
      const existing = {
        id: existingId,
        recurrence_count: 3,
        first_seen: new Date(now - 86400000),
        last_seen: new Date(now - 3600000)
      };
      const lifecycle = { 
        recurrence_count: 1, 
        first_seen: now, 
        last_seen: now,
        _now: now
      };
      
      const plan = deriveMergePlan(existing, lifecycle, now);
      
      assert.strictEqual(plan.found, true);
      assert.strictEqual(plan.finalId, existingId);
      assert.strictEqual(plan.finalRecurrence, 4); // 3 + 1
    });
  });
});
