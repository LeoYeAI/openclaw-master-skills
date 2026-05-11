import Database from 'better-sqlite3';
import { Severity, Action } from '../types';

export class DatabaseError extends Error {
  constructor(message: string, public readonly cause?: unknown) {
    super(message);
    this.name = 'DatabaseError';
    if (cause instanceof Error) {
      this.stack = `${this.stack}\nCaused by: ${cause.stack}`;
    }
  }
}

export interface SecurityEvent {
  id?: number;
  timestamp?: string;
  event_type: string;
  severity: Severity;
  action_taken: Action;
  user_id: string;
  session_id: string;
  input_text: string;
  patterns_matched: string;
  fingerprint: string;
  module: string;
  metadata: string;
}

export interface RateLimit {
  user_id: string;
  request_count: number;
  window_start: string;
  lockout_until?: string;
  failed_attempts: number;
}

export interface UserReputation {
  user_id: string;
  trust_score: number;
  total_requests: number;
  blocked_attempts: number;
  last_violation?: string;
  is_allowlisted: number;
  is_blocklisted: number;
  notes?: string;
}

export interface AttackPattern {
  id?: number;
  pattern: string;
  category: string;
  severity: Severity;
  language: string;
  times_matched: number;
  last_matched?: string;
  is_custom: number;
  enabled: number;
}

export interface NotificationLog {
  id?: number;
  timestamp?: string;
  channel: string;
  severity: Severity;
  message: string;
  delivery_status: string;
  event_id: number;
}

export class DatabaseManager {
  private db: Database.Database;
  private isClosed: boolean = false;

  constructor(dbPath: string) {
    try {
      this.db = new Database(dbPath);
      // Enable foreign key constraints before initializing schema
      this.db.pragma('foreign_keys = ON');
      this.initializeSchema();
    } catch (error) {
      throw new DatabaseError('Failed to initialize database', error);
    }
  }

  private ensureNotClosed(): void {
    if (this.isClosed) {
      throw new DatabaseError('Database connection is closed');
    }
  }

  private validateSeverity(severity: Severity): void {
    const validSeverities = Object.values(Severity);
    if (!validSeverities.includes(severity)) {
      throw new DatabaseError(`Invalid severity: ${severity}. Must be one of: ${validSeverities.join(', ')}`);
    }
  }

  private validateAction(action: Action): void {
    const validActions = Object.values(Action);
    if (!validActions.includes(action)) {
      throw new DatabaseError(`Invalid action: ${action}. Must be one of: ${validActions.join(', ')}`);
    }
  }

  private validatePositiveInteger(value: number, fieldName: string): void {
    if (!Number.isInteger(value) || value < 0) {
      throw new DatabaseError(`${fieldName} must be a positive integer, got: ${value}`);
    }
  }

  private validateRequiredString(value: string, fieldName: string): void {
    if (typeof value !== 'string' || value.trim().length === 0) {
      throw new DatabaseError(`${fieldName} is required and must be a non-empty string`);
    }
  }

  private initializeSchema(): void {
    // Security Events Table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS security_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        action_taken TEXT NOT NULL,
        user_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        input_text TEXT NOT NULL,
        patterns_matched TEXT NOT NULL,
        fingerprint TEXT NOT NULL,
        module TEXT NOT NULL,
        metadata TEXT DEFAULT '{}'
      );
    `);

    // Create indexes for security_events
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_events_timestamp ON security_events(timestamp);
      CREATE INDEX IF NOT EXISTS idx_events_user_id ON security_events(user_id);
      CREATE INDEX IF NOT EXISTS idx_events_severity ON security_events(severity);
      CREATE INDEX IF NOT EXISTS idx_events_fingerprint ON security_events(fingerprint);
    `);

    // Rate Limits Table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS rate_limits (
        user_id TEXT PRIMARY KEY,
        request_count INTEGER DEFAULT 0,
        window_start DATETIME NOT NULL,
        lockout_until DATETIME,
        failed_attempts INTEGER DEFAULT 0
      );
    `);

    // Create indexes for rate_limits
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_rate_limits_window_start ON rate_limits(window_start);
    `);

    // User Reputation Table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS user_reputation (
        user_id TEXT PRIMARY KEY,
        trust_score REAL DEFAULT 100.0,
        total_requests INTEGER DEFAULT 0,
        blocked_attempts INTEGER DEFAULT 0,
        last_violation DATETIME,
        is_allowlisted INTEGER DEFAULT 0,
        is_blocklisted INTEGER DEFAULT 0,
        notes TEXT
      );
    `);

    // Create indexes for user_reputation
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_reputation_trust_score ON user_reputation(trust_score);
    `);

    // Attack Patterns Table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS attack_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        language TEXT NOT NULL,
        times_matched INTEGER DEFAULT 0,
        last_matched DATETIME,
        is_custom INTEGER DEFAULT 0,
        enabled INTEGER DEFAULT 1
      );
    `);

    // Create indexes for attack_patterns
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_patterns_pattern ON attack_patterns(pattern);
      CREATE INDEX IF NOT EXISTS idx_patterns_category ON attack_patterns(category);
      CREATE INDEX IF NOT EXISTS idx_patterns_severity ON attack_patterns(severity);
    `);

    // Notifications Log Table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS notifications_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        channel TEXT NOT NULL,
        severity TEXT NOT NULL,
        message TEXT NOT NULL,
        delivery_status TEXT NOT NULL,
        event_id INTEGER NOT NULL,
        FOREIGN KEY (event_id) REFERENCES security_events(id)
      );
    `);

    // Create indexes for notifications_log
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_notifications_event_id ON notifications_log(event_id);
      CREATE INDEX IF NOT EXISTS idx_notifications_timestamp ON notifications_log(timestamp);
      CREATE INDEX IF NOT EXISTS idx_notifications_delivery_status ON notifications_log(delivery_status);
    `);
  }

  public getTables(): string[] {
    this.ensureNotClosed();
    try {
      const stmt = this.db.prepare(`
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
      `);
      const results = stmt.all() as Array<{ name: string }>;
      return results.map(row => row.name);
    } catch (error) {
      throw new DatabaseError('Failed to get tables', error);
    }
  }

  // Security Events Methods
  public insertEvent(event: SecurityEvent): number {
    this.ensureNotClosed();

    // Validate required fields
    this.validateRequiredString(event.event_type, 'event_type');
    this.validateSeverity(event.severity);
    this.validateAction(event.action_taken);
    this.validateRequiredString(event.user_id, 'user_id');
    this.validateRequiredString(event.session_id, 'session_id');
    this.validateRequiredString(event.input_text, 'input_text');
    this.validateRequiredString(event.patterns_matched, 'patterns_matched');
    this.validateRequiredString(event.fingerprint, 'fingerprint');
    this.validateRequiredString(event.module, 'module');
    this.validateRequiredString(event.metadata, 'metadata');

    try {
      const stmt = this.db.prepare(`
        INSERT INTO security_events (
          event_type, severity, action_taken, user_id, session_id,
          input_text, patterns_matched, fingerprint, module, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      const result = stmt.run(
        event.event_type,
        event.severity,
        event.action_taken,
        event.user_id,
        event.session_id,
        event.input_text,
        event.patterns_matched,
        event.fingerprint,
        event.module,
        event.metadata
      );

      return result.lastInsertRowid as number;
    } catch (error) {
      throw new DatabaseError('Failed to insert security event', error);
    }
  }

  public getEventById(id: number): SecurityEvent | undefined {
    this.ensureNotClosed();
    this.validatePositiveInteger(id, 'id');

    try {
      const stmt = this.db.prepare('SELECT * FROM security_events WHERE id = ?');
      return stmt.get(id) as SecurityEvent | undefined;
    } catch (error) {
      throw new DatabaseError(`Failed to get event by id ${id}`, error);
    }
  }

  public getEventsByUserId(userId: string, limit: number = 100): SecurityEvent[] {
    this.ensureNotClosed();
    this.validateRequiredString(userId, 'userId');
    this.validatePositiveInteger(limit, 'limit');

    try {
      const stmt = this.db.prepare(`
        SELECT * FROM security_events
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
      `);
      return stmt.all(userId, limit) as SecurityEvent[];
    } catch (error) {
      throw new DatabaseError(`Failed to get events for user ${userId}`, error);
    }
  }

  public getEventsBySeverity(severity: Severity, limit: number = 100): SecurityEvent[] {
    this.ensureNotClosed();
    this.validateSeverity(severity);
    this.validatePositiveInteger(limit, 'limit');

    try {
      const stmt = this.db.prepare(`
        SELECT * FROM security_events
        WHERE severity = ?
        ORDER BY timestamp DESC
        LIMIT ?
      `);
      return stmt.all(severity, limit) as SecurityEvent[];
    } catch (error) {
      throw new DatabaseError(`Failed to get events by severity ${severity}`, error);
    }
  }

  // Rate Limits Methods
  public upsertRateLimit(rateLimit: RateLimit): void {
    this.ensureNotClosed();
    this.validateRequiredString(rateLimit.user_id, 'user_id');
    this.validatePositiveInteger(rateLimit.request_count, 'request_count');
    this.validateRequiredString(rateLimit.window_start, 'window_start');
    this.validatePositiveInteger(rateLimit.failed_attempts, 'failed_attempts');

    try {
      const stmt = this.db.prepare(`
        INSERT INTO rate_limits (user_id, request_count, window_start, lockout_until, failed_attempts)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
          request_count = excluded.request_count,
          window_start = excluded.window_start,
          lockout_until = excluded.lockout_until,
          failed_attempts = excluded.failed_attempts
      `);

      stmt.run(
        rateLimit.user_id,
        rateLimit.request_count,
        rateLimit.window_start,
        rateLimit.lockout_until,
        rateLimit.failed_attempts
      );
    } catch (error) {
      throw new DatabaseError(`Failed to upsert rate limit for user ${rateLimit.user_id}`, error);
    }
  }

  public getRateLimitByUserId(userId: string): RateLimit | undefined {
    this.ensureNotClosed();
    this.validateRequiredString(userId, 'userId');

    try {
      const stmt = this.db.prepare('SELECT * FROM rate_limits WHERE user_id = ?');
      return stmt.get(userId) as RateLimit | undefined;
    } catch (error) {
      throw new DatabaseError(`Failed to get rate limit for user ${userId}`, error);
    }
  }

  // User Reputation Methods
  public upsertUserReputation(reputation: UserReputation): void {
    this.ensureNotClosed();
    this.validateRequiredString(reputation.user_id, 'user_id');

    if (typeof reputation.trust_score !== 'number' || reputation.trust_score < 0) {
      throw new DatabaseError(`trust_score must be a non-negative number, got: ${reputation.trust_score}`);
    }

    this.validatePositiveInteger(reputation.total_requests, 'total_requests');
    this.validatePositiveInteger(reputation.blocked_attempts, 'blocked_attempts');

    if (reputation.is_allowlisted !== 0 && reputation.is_allowlisted !== 1) {
      throw new DatabaseError(`is_allowlisted must be 0 or 1, got: ${reputation.is_allowlisted}`);
    }

    if (reputation.is_blocklisted !== 0 && reputation.is_blocklisted !== 1) {
      throw new DatabaseError(`is_blocklisted must be 0 or 1, got: ${reputation.is_blocklisted}`);
    }

    try {
      const stmt = this.db.prepare(`
        INSERT INTO user_reputation (
          user_id, trust_score, total_requests, blocked_attempts, last_violation, is_allowlisted, is_blocklisted, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
          trust_score = excluded.trust_score,
          total_requests = excluded.total_requests,
          blocked_attempts = excluded.blocked_attempts,
          last_violation = excluded.last_violation,
          is_allowlisted = excluded.is_allowlisted,
          is_blocklisted = excluded.is_blocklisted,
          notes = excluded.notes
      `);

      stmt.run(
        reputation.user_id,
        reputation.trust_score,
        reputation.total_requests,
        reputation.blocked_attempts,
        reputation.last_violation,
        reputation.is_allowlisted,
        reputation.is_blocklisted,
        reputation.notes
      );
    } catch (error) {
      throw new DatabaseError(`Failed to upsert user reputation for user ${reputation.user_id}`, error);
    }
  }

  public getUserReputation(userId: string): UserReputation | undefined {
    this.ensureNotClosed();
    this.validateRequiredString(userId, 'userId');

    try {
      const stmt = this.db.prepare('SELECT * FROM user_reputation WHERE user_id = ?');
      return stmt.get(userId) as UserReputation | undefined;
    } catch (error) {
      throw new DatabaseError(`Failed to get user reputation for user ${userId}`, error);
    }
  }

  // Attack Patterns Methods
  public upsertAttackPattern(pattern: AttackPattern): number {
    this.ensureNotClosed();
    this.validateRequiredString(pattern.pattern, 'pattern');
    this.validateRequiredString(pattern.category, 'category');
    this.validateSeverity(pattern.severity);
    this.validateRequiredString(pattern.language, 'language');
    this.validatePositiveInteger(pattern.times_matched, 'times_matched');

    if (pattern.is_custom !== 0 && pattern.is_custom !== 1) {
      throw new DatabaseError(`is_custom must be 0 or 1, got: ${pattern.is_custom}`);
    }

    if (pattern.enabled !== 0 && pattern.enabled !== 1) {
      throw new DatabaseError(`enabled must be 0 or 1, got: ${pattern.enabled}`);
    }

    try {
      const stmt = this.db.prepare(`
        INSERT INTO attack_patterns (
          pattern, category, severity, language, times_matched, last_matched, is_custom, enabled
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(pattern) DO UPDATE SET
          category = excluded.category,
          severity = excluded.severity,
          language = excluded.language,
          times_matched = excluded.times_matched,
          last_matched = excluded.last_matched,
          is_custom = excluded.is_custom,
          enabled = excluded.enabled
      `);

      const result = stmt.run(
        pattern.pattern,
        pattern.category,
        pattern.severity,
        pattern.language,
        pattern.times_matched,
        pattern.last_matched,
        pattern.is_custom,
        pattern.enabled
      );

      return result.lastInsertRowid as number;
    } catch (error) {
      throw new DatabaseError(`Failed to upsert attack pattern: ${pattern.pattern}`, error);
    }
  }

  public getAttackPatternByPattern(pattern: string): AttackPattern | undefined {
    this.ensureNotClosed();
    this.validateRequiredString(pattern, 'pattern');

    try {
      const stmt = this.db.prepare('SELECT * FROM attack_patterns WHERE pattern = ?');
      return stmt.get(pattern) as AttackPattern | undefined;
    } catch (error) {
      throw new DatabaseError(`Failed to get attack pattern: ${pattern}`, error);
    }
  }

  public getAttackPatternsByCategory(category: string, limit: number = 100): AttackPattern[] {
    this.ensureNotClosed();
    this.validateRequiredString(category, 'category');
    this.validatePositiveInteger(limit, 'limit');

    try {
      const stmt = this.db.prepare(`
        SELECT * FROM attack_patterns
        WHERE category = ?
        ORDER BY times_matched DESC
        LIMIT ?
      `);
      return stmt.all(category, limit) as AttackPattern[];
    } catch (error) {
      throw new DatabaseError(`Failed to get attack patterns by category ${category}`, error);
    }
  }

  // Notifications Log Methods
  public insertNotificationLog(log: NotificationLog): number {
    this.ensureNotClosed();
    this.validateRequiredString(log.channel, 'channel');
    this.validateSeverity(log.severity);
    this.validateRequiredString(log.message, 'message');
    this.validateRequiredString(log.delivery_status, 'delivery_status');
    this.validatePositiveInteger(log.event_id, 'event_id');

    try {
      const stmt = this.db.prepare(`
        INSERT INTO notifications_log (
          channel, severity, message, delivery_status, event_id
        ) VALUES (?, ?, ?, ?, ?)
      `);

      const result = stmt.run(
        log.channel,
        log.severity,
        log.message,
        log.delivery_status,
        log.event_id
      );

      return result.lastInsertRowid as number;
    } catch (error) {
      throw new DatabaseError(`Failed to insert notification log for event ${log.event_id}`, error);
    }
  }

  public getNotificationLogsByEventId(eventId: number): NotificationLog[] {
    this.ensureNotClosed();
    this.validatePositiveInteger(eventId, 'eventId');

    try {
      const stmt = this.db.prepare('SELECT * FROM notifications_log WHERE event_id = ? ORDER BY timestamp DESC');
      return stmt.all(eventId) as NotificationLog[];
    } catch (error) {
      throw new DatabaseError(`Failed to get notification logs for event ${eventId}`, error);
    }
  }

  // Utility Methods
  public close(): void {
    if (this.isClosed) {
      return; // Already closed, no-op
    }

    try {
      this.db.close();
      this.isClosed = true;
    } catch (error) {
      throw new DatabaseError('Failed to close database connection', error);
    }
  }

  public vacuum(): void {
    this.ensureNotClosed();

    try {
      this.db.exec('VACUUM');
    } catch (error) {
      throw new DatabaseError('Failed to vacuum database', error);
    }
  }

  public deleteOldEvents(daysToKeep: number): number {
    this.ensureNotClosed();

    // Validate that daysToKeep is a positive integer to prevent SQL injection
    if (!Number.isInteger(daysToKeep) || daysToKeep < 0) {
      throw new DatabaseError(`daysToKeep must be a positive integer, got: ${daysToKeep}`);
    }

    try {
      const stmt = this.db.prepare(`
        DELETE FROM security_events
        WHERE timestamp < datetime('now', '-' || ? || ' days')
      `);
      const result = stmt.run(daysToKeep);
      return result.changes;
    } catch (error) {
      throw new DatabaseError(`Failed to delete events older than ${daysToKeep} days`, error);
    }
  }
}
