import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';
import { ConfigManager } from '../config-manager';
import type { SecurityConfig } from '../../types';

describe('ConfigManager', () => {
  const testConfigDir = path.join(__dirname, 'test-configs');
  const testConfigPath = path.join(testConfigDir, 'test-config.yaml');

  beforeEach(() => {
    // Create test directory
    if (!fs.existsSync(testConfigDir)) {
      fs.mkdirSync(testConfigDir, { recursive: true });
    }
  });

  afterEach(() => {
    // Clean up test files
    if (fs.existsSync(testConfigPath)) {
      fs.unlinkSync(testConfigPath);
    }
    if (fs.existsSync(testConfigDir)) {
      fs.rmdirSync(testConfigDir);
    }
  });

  describe('getDefaultConfig', () => {
    it('should return default configuration', () => {
      const config = ConfigManager.getDefaultConfig();

      expect(config).toHaveProperty('enabled');
      expect(config).toHaveProperty('database');
      expect(config).toHaveProperty('modules');
      expect(config.database.path).toBe('.openclaw-sec.db');
      expect(config.sensitivity).toBe('medium');
    });
  });

  describe('load', () => {
    it('should return default config when file does not exist', async () => {
      const config = await ConfigManager.load('nonexistent.yaml');
      const defaultConfig = ConfigManager.getDefaultConfig();

      expect(config).toEqual(defaultConfig);
    });

    it('should load and merge config from YAML file', async () => {
      const userConfig = `
openclaw_security:
  database:
    path: custom.db
  sensitivity: strict
  modules:
    prompt_injection:
      enabled: true
      sensitivity: paranoid
`;
      fs.writeFileSync(testConfigPath, userConfig);

      const config = await ConfigManager.load(testConfigPath);

      expect(config.database.path).toBe('custom.db');
      expect(config.sensitivity).toBe('strict');
      expect(config.modules.prompt_injection.sensitivity).toBe('paranoid');
    });

    it('should merge user config with defaults', async () => {
      const userConfig = `
openclaw_security:
  database:
    path: custom.db
`;
      fs.writeFileSync(testConfigPath, userConfig);

      const config = await ConfigManager.load(testConfigPath);

      expect(config.database.path).toBe('custom.db');
      expect(config).toHaveProperty('modules');
      expect(config).toHaveProperty('actions');
    });

    it('should handle invalid YAML gracefully', async () => {
      const invalidYaml = `
openclaw_security:
  database:
    path: [invalid: yaml
`;
      fs.writeFileSync(testConfigPath, invalidYaml);

      await expect(ConfigManager.load(testConfigPath)).rejects.toThrow();
    });

    it('should validate sensitivity levels', async () => {
      const invalidConfig = `
openclaw_security:
  sensitivity: invalid_level
`;
      fs.writeFileSync(testConfigPath, invalidConfig);

      await expect(ConfigManager.load(testConfigPath)).rejects.toThrow('Invalid sensitivity level');
    });

    it('should validate actions', async () => {
      const invalidConfig = `
openclaw_security:
  actions:
    HIGH: invalid_action
`;
      fs.writeFileSync(testConfigPath, invalidConfig);

      await expect(ConfigManager.load(testConfigPath)).rejects.toThrow('Invalid action');
    });
  });

  describe('deepMerge', () => {
    it('should merge nested objects', () => {
      const target = {
        a: { b: 1, c: 2 },
        d: 3
      };
      const source = {
        a: { b: 10, e: 4 },
        f: 5
      };

      const result = ConfigManager.deepMerge(target, source);

      expect(result).toEqual({
        a: { b: 10, c: 2, e: 4 },
        d: 3,
        f: 5
      });
    });

    it('should replace arrays instead of merging', () => {
      const target = {
        rules: [{ pattern: 'old' }]
      };
      const source = {
        rules: [{ pattern: 'new' }]
      };

      const result = ConfigManager.deepMerge(target, source);

      expect(result.rules).toEqual([{ pattern: 'new' }]);
    });
  });

  describe('validateConfig', () => {
    it('should accept valid config', () => {
      const validConfig = ConfigManager.getDefaultConfig();
      expect(() => ConfigManager.validateConfig(validConfig)).not.toThrow();
    });

    it('should reject invalid sensitivity level', () => {
      const invalidConfig: any = {
        sensitivity: 'invalid',
        actions: {},
        modules: {}
      };

      expect(() => ConfigManager.validateConfig(invalidConfig)).toThrow('Invalid sensitivity level');
    });

    it('should reject invalid action', () => {
      const defaultConfig = ConfigManager.getDefaultConfig();
      const invalidConfig: any = {
        ...defaultConfig,
        actions: {
          HIGH: 'invalid_action'
        }
      };

      expect(() => ConfigManager.validateConfig(invalidConfig)).toThrow('Invalid action');
    });
  });
});
