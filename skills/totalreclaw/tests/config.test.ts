/**
 * TotalReclaw Skill - Configuration Tests
 *
 * Tests for configuration loading, merging, and validation.
 */

import {
  loadConfig,
  validateConfig,
  assertValidConfig,
  createConfig,
  type ConfigValidationResult,
} from '../src/config';
import type { TotalReclawSkillConfig } from '../src/types';
import { DEFAULT_SKILL_CONFIG } from '../src/types';

// ============================================================================
// Configuration Loading Tests
// ============================================================================

describe('loadConfig', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    // Reset environment for each test
    jest.resetModules();
    process.env = { ...originalEnv };
  });

  afterAll(() => {
    // Restore original environment
    process.env = originalEnv;
  });

  describe('default values', () => {
    it('should return default configuration with no overrides', () => {
      const config = loadConfig();

      expect(config.serverUrl).toBeDefined();
      expect(config.autoExtractEveryTurns).toBeDefined();
      expect(config.minImportanceForAutoStore).toBeDefined();
      expect(config.maxMemoriesInContext).toBeDefined();
      expect(config.forgetThreshold).toBeDefined();
    });

    it('should have correct default values', () => {
      const config = loadConfig();

      expect(config.serverUrl).toBe('http://127.0.0.1:8080');
      expect(config.autoExtractEveryTurns).toBe(3);
      expect(config.minImportanceForAutoStore).toBe(6);
      expect(config.maxMemoriesInContext).toBe(8);
      expect(config.forgetThreshold).toBe(0.3);
    });
  });

  describe('override behavior', () => {
    it('should override defaults with explicit values', () => {
      const config = loadConfig({
        overrides: {
          serverUrl: 'http://custom-server:9000',
          autoExtractEveryTurns: 10,
        },
      });

      expect(config.serverUrl).toBe('http://custom-server:9000');
      expect(config.autoExtractEveryTurns).toBe(10);
      // Other values should remain default
      expect(config.minImportanceForAutoStore).toBe(6);
    });

    it('should override all values', () => {
      const overrides: Partial<TotalReclawSkillConfig> = {
        serverUrl: 'https://secure.example.com',
        autoExtractEveryTurns: 3,
        minImportanceForAutoStore: 8,
        maxMemoriesInContext: 5,
        forgetThreshold: 0.5,
        rerankerModel: 'custom-model',
        masterPassword: 'secure-password',
        userId: 'user-123',
        salt: Buffer.from('salt'),
      };

      const config = loadConfig({ overrides });

      expect(config.serverUrl).toBe('https://secure.example.com');
      expect(config.autoExtractEveryTurns).toBe(3);
      expect(config.minImportanceForAutoStore).toBe(8);
      expect(config.maxMemoriesInContext).toBe(5);
      expect(config.forgetThreshold).toBe(0.5);
      expect(config.rerankerModel).toBe('custom-model');
      expect(config.masterPassword).toBe('secure-password');
      expect(config.userId).toBe('user-123');
      expect(config.salt).toEqual(Buffer.from('salt'));
    });
  });

  describe('OpenClaw config merging', () => {
    it('should merge OpenClaw configuration', () => {
      const openclawConfig = {
        agents: {
          defaults: {
            totalreclaw: {
              serverUrl: 'http://openclaw-memory:8080',
              maxMemoriesInContext: 12,
            },
          },
        },
      };

      const config = loadConfig({ openclawConfig });

      expect(config.serverUrl).toBe('http://openclaw-memory:8080');
      expect(config.maxMemoriesInContext).toBe(12);
    });

    it('should handle missing OpenClaw config gracefully', () => {
      const config = loadConfig({ openclawConfig: undefined });

      expect(config).toBeDefined();
      expect(config.serverUrl).toBe('http://127.0.0.1:8080');
    });

    it('should handle empty OpenClaw config', () => {
      const config = loadConfig({ openclawConfig: {} });

      expect(config).toBeDefined();
    });
  });

  describe('environment variable loading', () => {
    it('should load from TOTALRECLAW_SERVER_URL', () => {
      process.env.TOTALRECLAW_SERVER_URL = 'http://env-server:8888';

      const config = loadConfig();

      expect(config.serverUrl).toBe('http://env-server:8888');

      delete process.env.TOTALRECLAW_SERVER_URL;
    });

    it('should load from TOTALRECLAW_AUTO_EXTRACT_EVERY_TURNS', () => {
      process.env.TOTALRECLAW_AUTO_EXTRACT_EVERY_TURNS = '7';

      const config = loadConfig();

      expect(config.autoExtractEveryTurns).toBe(7);

      delete process.env.TOTALRECLAW_AUTO_EXTRACT_EVERY_TURNS;
    });

    it('should load from TOTALRECLAW_MIN_IMPORTANCE', () => {
      process.env.TOTALRECLAW_MIN_IMPORTANCE = '8';

      const config = loadConfig();

      expect(config.minImportanceForAutoStore).toBe(8);

      delete process.env.TOTALRECLAW_MIN_IMPORTANCE;
    });

    it('should load from TOTALRECLAW_MAX_MEMORIES', () => {
      process.env.TOTALRECLAW_MAX_MEMORIES = '15';

      const config = loadConfig();

      expect(config.maxMemoriesInContext).toBe(15);

      delete process.env.TOTALRECLAW_MAX_MEMORIES;
    });

    it('should load from TOTALRECLAW_FORGET_THRESHOLD', () => {
      process.env.TOTALRECLAW_FORGET_THRESHOLD = '0.5';

      const config = loadConfig();

      expect(config.forgetThreshold).toBe(0.5);

      delete process.env.TOTALRECLAW_FORGET_THRESHOLD;
    });

    it('should load from TOTALRECLAW_RECOVERY_PHRASE', () => {
      process.env.TOTALRECLAW_RECOVERY_PHRASE = 'env-password';

      const config = loadConfig();

      expect(config.masterPassword).toBe('env-password');

      delete process.env.TOTALRECLAW_RECOVERY_PHRASE;
    });

    it('should handle invalid numeric env values', () => {
      process.env.TOTALRECLAW_AUTO_EXTRACT_EVERY_TURNS = 'not-a-number';

      const config = loadConfig();

      // Should fall back to default or skip invalid value
      expect(config.autoExtractEveryTurns).toBeDefined();

      delete process.env.TOTALRECLAW_AUTO_EXTRACT_EVERY_TURNS;
    });

    it('should handle empty env values', () => {
      process.env.TOTALRECLAW_SERVER_URL = '';

      const config = loadConfig();

      // Empty string should be skipped
      expect(config.serverUrl).toBe('http://127.0.0.1:8080');

      delete process.env.TOTALRECLAW_SERVER_URL;
    });
  });

  describe('priority order', () => {
    it('should prioritize explicit overrides over env vars', () => {
      process.env.TOTALRECLAW_SERVER_URL = 'http://env-server';
      const overrides = { serverUrl: 'http://override-server' };

      const config = loadConfig({ overrides });

      expect(config.serverUrl).toBe('http://override-server');

      delete process.env.TOTALRECLAW_SERVER_URL;
    });

    it('should prioritize env vars over OpenClaw config', () => {
      process.env.TOTALRECLAW_SERVER_URL = 'http://env-server';
      const openclawConfig = {
        agents: {
          defaults: {
            totalreclaw: {
              serverUrl: 'http://openclaw-server',
            },
          },
        },
      };

      const config = loadConfig({ openclawConfig });

      expect(config.serverUrl).toBe('http://env-server');

      delete process.env.TOTALRECLAW_SERVER_URL;
    });
  });
});

// ============================================================================
// Configuration Validation Tests
// ============================================================================

describe('validateConfig', () => {
  describe('valid configurations', () => {
    it('should validate default configuration', () => {
      const config = loadConfig();
      const result = validateConfig(config);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should validate configuration with all valid values', () => {
      const config: TotalReclawSkillConfig = {
        serverUrl: 'https://secure.example.com',
        autoExtractEveryTurns: 5,
        minImportanceForAutoStore: 7,
        maxMemoriesInContext: 10,
        forgetThreshold: 0.3,
        rerankerModel: 'BAAI/bge-reranker-base',
        masterPassword: 'secure-password',
        userId: 'user-123',
        salt: Buffer.from('salt'),
      };

      const result = validateConfig(config);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe('serverUrl validation', () => {
    it('should reject invalid URLs', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, serverUrl: 'not-a-url' };
      const result = validateConfig(config);

      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.field === 'serverUrl')).toBe(true);
    });

    it('should reject non-HTTP URLs', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, serverUrl: 'ftp://server.com' };
      const result = validateConfig(config);

      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.field === 'serverUrl')).toBe(true);
    });

    it('should accept HTTP URLs', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, serverUrl: 'http://localhost:8080' };
      const result = validateConfig(config);

      expect(result.valid).toBe(true);
    });

    it('should accept HTTPS URLs', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, serverUrl: 'https://secure.example.com' };
      const result = validateConfig(config);

      expect(result.valid).toBe(true);
    });

    it('should warn about HTTP in production', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, serverUrl: 'http://insecure.com' };
      const result = validateConfig(config);

      expect(result.warnings.some(w => w.field === 'serverUrl')).toBe(true);
    });
  });

  describe('autoExtractEveryTurns validation', () => {
    it('should reject values below 1', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, autoExtractEveryTurns: 0 };
      const result = validateConfig(config);

      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.field === 'autoExtractEveryTurns')).toBe(true);
    });

    it('should reject values above 100', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, autoExtractEveryTurns: 101 };
      const result = validateConfig(config);

      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.field === 'autoExtractEveryTurns')).toBe(true);
    });

    it('should accept valid values', () => {
      for (const value of [1, 5, 10, 50, 100]) {
        const config = { ...DEFAULT_SKILL_CONFIG, autoExtractEveryTurns: value };
        const result = validateConfig(config);

        expect(result.valid).toBe(true);
      }
    });
  });

  describe('minImportanceForAutoStore validation', () => {
    it('should reject values below 1', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, minImportanceForAutoStore: 0 };
      const result = validateConfig(config);

      expect(result.valid).toBe(false);
    });

    it('should reject values above 10', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, minImportanceForAutoStore: 11 };
      const result = validateConfig(config);

      expect(result.valid).toBe(false);
    });

    it('should accept valid values', () => {
      for (const value of [1, 5, 10]) {
        const config = { ...DEFAULT_SKILL_CONFIG, minImportanceForAutoStore: value };
        const result = validateConfig(config);

        expect(result.valid).toBe(true);
      }
    });
  });

  describe('maxMemoriesInContext validation', () => {
    it('should reject values below 1', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, maxMemoriesInContext: 0 };
      const result = validateConfig(config);

      expect(result.valid).toBe(false);
    });

    it('should reject values above 50', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, maxMemoriesInContext: 51 };
      const result = validateConfig(config);

      expect(result.valid).toBe(false);
    });

    it('should warn about high values', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, maxMemoriesInContext: 25 };
      const result = validateConfig(config);

      expect(result.warnings.some(w => w.field === 'maxMemoriesInContext')).toBe(true);
    });
  });

  describe('forgetThreshold validation', () => {
    it('should reject negative values', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, forgetThreshold: -0.1 };
      const result = validateConfig(config);

      expect(result.valid).toBe(false);
    });

    it('should reject values above 1', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, forgetThreshold: 1.1 };
      const result = validateConfig(config);

      expect(result.valid).toBe(false);
    });

    it('should warn about very low threshold', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, forgetThreshold: 0.05 };
      const result = validateConfig(config);

      expect(result.warnings.some(w => w.message.includes('bloat'))).toBe(true);
    });

    it('should warn about very high threshold', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, forgetThreshold: 0.9 };
      const result = validateConfig(config);

      expect(result.warnings.some(w => w.message.includes('loss'))).toBe(true);
    });
  });

  describe('optional fields validation', () => {
    it('should allow undefined rerankerModel', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, rerankerModel: undefined };
      const result = validateConfig(config);

      expect(result.valid).toBe(true);
    });

    it('should allow undefined masterPassword', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, masterPassword: undefined };
      const result = validateConfig(config);

      expect(result.valid).toBe(true);
    });

    it('should warn about short masterPassword', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, masterPassword: 'short' };
      const result = validateConfig(config);

      expect(result.warnings.some(w => w.field === 'masterPassword')).toBe(true);
    });

    it('should allow Buffer salt', () => {
      const config = { ...DEFAULT_SKILL_CONFIG, salt: Buffer.from('salt') };
      const result = validateConfig(config);

      expect(result.valid).toBe(true);
    });
  });
});

// ============================================================================
// assertValidConfig Tests
// ============================================================================

describe('assertValidConfig', () => {
  it('should not throw for valid config', () => {
    const config = loadConfig();

    expect(() => assertValidConfig(config)).not.toThrow();
  });

  it('should throw for invalid config', () => {
    const config = { ...DEFAULT_SKILL_CONFIG, serverUrl: 'invalid' };

    expect(() => assertValidConfig(config)).toThrow('Invalid TotalReclaw configuration');
  });

  it('should include all errors in message', () => {
    const config = {
      ...DEFAULT_SKILL_CONFIG,
      serverUrl: 'invalid',
      autoExtractEveryTurns: 0,
      forgetThreshold: 2,
    };

    expect(() => assertValidConfig(config)).toThrow();
  });
});

// ============================================================================
// createConfig Tests
// ============================================================================

describe('createConfig', () => {
  it('should create and validate configuration', () => {
    const config = createConfig();

    expect(config).toBeDefined();
    expect(config.serverUrl).toBeDefined();
  });

  it('should merge partial configuration', () => {
    const config = createConfig({
      serverUrl: 'http://custom:9000',
    });

    expect(config.serverUrl).toBe('http://custom:9000');
    expect(config.autoExtractEveryTurns).toBe(3); // Default
  });

  it('should throw for invalid configuration', () => {
    expect(() => createConfig({ serverUrl: 'invalid' })).toThrow();
  });

  it('should accept options', () => {
    const config = createConfig(
      { serverUrl: 'https://example.com' },
      { openclawConfig: {} }
    );

    expect(config.serverUrl).toBe('https://example.com');
  });
});

// ============================================================================
// Type Safety Tests
// ============================================================================

describe('Type Safety', () => {
  it('should accept valid TotalReclawSkillConfig', () => {
    const config: TotalReclawSkillConfig = {
      serverUrl: 'http://localhost:8080',
      autoExtractEveryTurns: 5,
      minImportanceForAutoStore: 6,
      maxMemoriesInContext: 8,
      forgetThreshold: 0.3,
    };

    const result = validateConfig(config);

    expect(result.valid).toBe(true);
  });

  it('should handle numeric coercion', () => {
    // Environment variables are always strings
    process.env.TOTALRECLAW_AUTO_EXTRACT_EVERY_TURNS = '5';

    const config = loadConfig();

    expect(typeof config.autoExtractEveryTurns).toBe('number');

    delete process.env.TOTALRECLAW_AUTO_EXTRACT_EVERY_TURNS;
  });
});
