import { ActionEngine } from '../action-engine';
import { DatabaseManager, UserReputation } from '../database-manager';
import { Severity, Action, SecurityConfig } from '../../types';
import * as fs from 'fs';
import * as path from 'path';

describe('ActionEngine', () => {
  let dbManager: DatabaseManager;
  let dbPath: string;

  beforeEach(() => {
    // Create temp database for testing
    dbPath = path.join(__dirname, `test-action-engine-${Date.now()}.db`);
    dbManager = new DatabaseManager(dbPath);
  });

  afterEach(() => {
    dbManager.close();
    if (fs.existsSync(dbPath)) {
      fs.unlinkSync(dbPath);
    }
  });

  const createMockConfig = (overrides?: Partial<SecurityConfig>): SecurityConfig => ({
    enabled: true,
    sensitivity: 'medium',
    owner_ids: ['owner-1', 'owner-2'],
    modules: {
      prompt_injection: { enabled: true },
      command_validator: { enabled: true },
      url_validator: { enabled: true },
      path_validator: { enabled: true },
      secret_detector: { enabled: true },
      content_scanner: { enabled: true },
      injection_validator: { enabled: true },
      exfiltration_detector: { enabled: true },
      code_execution_detector: { enabled: true },
      serialization_detector: { enabled: true }
    },
    actions: {
      [Severity.SAFE]: Action.ALLOW,
      [Severity.LOW]: Action.LOG,
      [Severity.MEDIUM]: Action.WARN,
      [Severity.HIGH]: Action.BLOCK,
      [Severity.CRITICAL]: Action.BLOCK_NOTIFY
    },
    rate_limit: {
      enabled: true,
      max_requests_per_minute: 30,
      lockout_threshold: 5
    },
    notifications: {
      enabled: false,
      channels: {},
      severity_threshold: Severity.HIGH
    },
    logging: {
      enabled: true,
      level: 'info',
      file: '~/.openclaw/logs/security-events.log',
      rotation: 'daily',
      retention_days: 90
    },
    database: {
      path: '.openclaw-sec.db',
      analytics_enabled: true,
      retention_days: 365
    },
    ...overrides
  });

  describe('constructor', () => {
    it('should create instance successfully', () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);
      expect(engine).toBeInstanceOf(ActionEngine);
    });

    it('should throw error if config is null', () => {
      expect(() => new ActionEngine(null as any, dbManager)).toThrow('Configuration is required');
    });

    it('should accept null dbManager for NO_DB mode', () => {
      const config = createMockConfig();
      expect(() => new ActionEngine(config, null as any)).not.toThrow();
    });
  });

  describe('determineAction', () => {
    it('should return ALLOW for SAFE severity', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      const result = await engine.determineAction(Severity.SAFE, 'user-123');

      expect(result.action).toBe(Action.ALLOW);
      expect(result.reasoning).toContain('SAFE');
    });

    it('should return LOG for LOW severity', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      const result = await engine.determineAction(Severity.LOW, 'user-123');

      expect(result.action).toBe(Action.LOG);
      expect(result.reasoning).toContain('LOW');
    });

    it('should return WARN for MEDIUM severity', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      const result = await engine.determineAction(Severity.MEDIUM, 'user-123');

      expect(result.action).toBe(Action.WARN);
      expect(result.reasoning).toContain('MEDIUM');
    });

    it('should return BLOCK for HIGH severity', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      const result = await engine.determineAction(Severity.HIGH, 'user-123');

      expect(result.action).toBe(Action.BLOCK);
      expect(result.reasoning).toContain('HIGH');
    });

    it('should return BLOCK_NOTIFY for CRITICAL severity', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      const result = await engine.determineAction(Severity.CRITICAL, 'user-123');

      expect(result.action).toBe(Action.BLOCK_NOTIFY);
      expect(result.reasoning).toContain('CRITICAL');
    });

    it('should apply custom action overrides from config', async () => {
      const config = createMockConfig({
        actions: {
          [Severity.SAFE]: Action.ALLOW,
          [Severity.LOW]: Action.WARN, // Override: normally LOG
          [Severity.MEDIUM]: Action.BLOCK, // Override: normally WARN
          [Severity.HIGH]: Action.BLOCK_NOTIFY, // Override: normally BLOCK
          [Severity.CRITICAL]: Action.BLOCK_NOTIFY
        }
      });
      const engine = new ActionEngine(config, dbManager);

      const lowResult = await engine.determineAction(Severity.LOW, 'user-123');
      expect(lowResult.action).toBe(Action.WARN);

      const mediumResult = await engine.determineAction(Severity.MEDIUM, 'user-123');
      expect(mediumResult.action).toBe(Action.BLOCK);
    });

    it('should throw error for invalid severity', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      await expect(engine.determineAction('INVALID' as any, 'user-123')).rejects.toThrow('Invalid severity');
    });

    it('should throw error for null userId', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      await expect(engine.determineAction(Severity.LOW, null as any)).rejects.toThrow('User ID is required');
    });

    it('should throw error for empty userId', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      await expect(engine.determineAction(Severity.LOW, '')).rejects.toThrow('User ID is required');
    });
  });

  describe('reputation-based decisions', () => {
    it('should allow owner users even for high severity', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      const result = await engine.determineAction(Severity.HIGH, 'owner-1');

      expect(result.action).toBe(Action.ALLOW);
      expect(result.reasoning).toContain('owner');
      expect(result.bypassReason).toBe('owner');
    });

    it('should allow allowlisted users for non-critical severities', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      // Add user to allowlist
      dbManager.upsertUserReputation({
        user_id: 'trusted-user',
        trust_score: 100,
        total_requests: 0,
        blocked_attempts: 0,
        is_allowlisted: 1,
        is_blocklisted: 0
      });

      const result = await engine.determineAction(Severity.HIGH, 'trusted-user');

      expect(result.action).toBe(Action.ALLOW);
      expect(result.reasoning).toContain('allowlisted');
      expect(result.bypassReason).toBe('allowlisted');
    });

    it('should not allow allowlisted users for critical severity', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      // Add user to allowlist
      dbManager.upsertUserReputation({
        user_id: 'trusted-user',
        trust_score: 100,
        total_requests: 0,
        blocked_attempts: 0,
        is_allowlisted: 1,
        is_blocklisted: 0
      });

      const result = await engine.determineAction(Severity.CRITICAL, 'trusted-user');

      expect(result.action).toBe(Action.BLOCK_NOTIFY);
      expect(result.bypassReason).toBeUndefined();
    });

    it('should always block blocklisted users', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      // Add user to blocklist
      dbManager.upsertUserReputation({
        user_id: 'bad-user',
        trust_score: 0,
        total_requests: 0,
        blocked_attempts: 10,
        is_allowlisted: 0,
        is_blocklisted: 1
      });

      const safeResult = await engine.determineAction(Severity.SAFE, 'bad-user');
      expect(safeResult.action).toBe(Action.BLOCK);
      expect(safeResult.reasoning).toContain('blocklisted');

      const lowResult = await engine.determineAction(Severity.LOW, 'bad-user');
      expect(lowResult.action).toBe(Action.BLOCK);
    });

    it('should upgrade action for users with low trust score', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      // User with low trust score
      dbManager.upsertUserReputation({
        user_id: 'suspicious-user',
        trust_score: 15, // Below 20 threshold
        total_requests: 100,
        blocked_attempts: 25,
        is_allowlisted: 0,
        is_blocklisted: 0
      });

      const lowResult = await engine.determineAction(Severity.LOW, 'suspicious-user');
      expect(lowResult.action).toBe(Action.WARN); // Upgraded from LOG
      expect(lowResult.reasoning).toContain('low trust score');
    });

    it('should not upgrade CRITICAL severity', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      // User with low trust score
      dbManager.upsertUserReputation({
        user_id: 'suspicious-user',
        trust_score: 10,
        total_requests: 100,
        blocked_attempts: 50,
        is_allowlisted: 0,
        is_blocklisted: 0
      });

      const result = await engine.determineAction(Severity.CRITICAL, 'suspicious-user');
      expect(result.action).toBe(Action.BLOCK_NOTIFY); // Cannot upgrade beyond BLOCK_NOTIFY
    });
  });

  describe('edge cases', () => {
    it('should handle user with no reputation record', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      const result = await engine.determineAction(Severity.MEDIUM, 'new-user');

      expect(result.action).toBe(Action.WARN);
      expect(result.reasoning).toContain('MEDIUM');
    });

    it('should handle missing actions in config gracefully', async () => {
      const config = createMockConfig();
      // Remove actions config
      delete (config as any).actions;

      const engine = new ActionEngine(config, dbManager);

      // Should use default mappings
      const result = await engine.determineAction(Severity.HIGH, 'user-123');
      expect(result.action).toBe(Action.BLOCK);
    });

    it('should handle database errors gracefully', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      // Close database to trigger error
      dbManager.close();

      // Should not throw, should use default behavior
      await expect(engine.determineAction(Severity.MEDIUM, 'user-123')).resolves.toBeDefined();
    });
  });

  describe('reasoning generation', () => {
    it('should include severity in reasoning', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      const result = await engine.determineAction(Severity.HIGH, 'user-123');

      expect(result.reasoning).toContain('HIGH');
      expect(result.reasoning.toLowerCase()).toContain('block');
    });

    it('should include trust score in reasoning when applicable', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      dbManager.upsertUserReputation({
        user_id: 'user-123',
        trust_score: 15,
        total_requests: 100,
        blocked_attempts: 25,
        is_allowlisted: 0,
        is_blocklisted: 0
      });

      const result = await engine.determineAction(Severity.LOW, 'user-123');

      expect(result.reasoning).toContain('trust score');
    });

    it('should provide clear reasoning for all decision factors', async () => {
      const config = createMockConfig();
      const engine = new ActionEngine(config, dbManager);

      const result = await engine.determineAction(Severity.MEDIUM, 'user-123');

      expect(result.reasoning).toBeTruthy();
      expect(result.reasoning.length).toBeGreaterThan(10);
      expect(result.action).toBeDefined();
    });
  });
});
