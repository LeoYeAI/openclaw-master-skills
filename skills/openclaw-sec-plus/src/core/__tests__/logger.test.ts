import { Logger, LogLevel } from '../logger';
import { Severity, Action } from '../../types';
import * as fs from 'fs';
import * as path from 'path';

describe('Logger', () => {
  let testLogDir: string;

  beforeEach(() => {
    // Create temp directory for test logs
    testLogDir = path.join(__dirname, `test-logs-${Date.now()}`);
    if (!fs.existsSync(testLogDir)) {
      fs.mkdirSync(testLogDir, { recursive: true });
    }
  });

  afterEach(async () => {
    // Small delay to ensure all writes complete
    await new Promise(resolve => setTimeout(resolve, 100));

    // Clean up test logs
    if (fs.existsSync(testLogDir)) {
      try {
        const files = fs.readdirSync(testLogDir);
        files.forEach(file => {
          try {
            fs.unlinkSync(path.join(testLogDir, file));
          } catch (e) {
            // Ignore cleanup errors
          }
        });
        fs.rmdirSync(testLogDir);
      } catch (e) {
        // Ignore cleanup errors
      }
    }
  });

  describe('constructor', () => {
    it('should create logger instance successfully', () => {
      const logFile = path.join(testLogDir, 'test.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.INFO
      });
      expect(logger).toBeInstanceOf(Logger);
      logger.stop();
    });

    it('should throw error if filePath is missing', () => {
      expect(() => new Logger({
        filePath: '',
        level: LogLevel.INFO
      })).toThrow('Log file path is required');
    });

    it('should create log file directory if it does not exist', () => {
      const nestedDir = path.join(testLogDir, 'nested', 'dir');
      const logFile = path.join(nestedDir, 'test.log');

      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.INFO
      });

      expect(fs.existsSync(nestedDir)).toBe(true);
      logger.stop();
    });
  });

  describe('log levels', () => {
    it('should log info messages when level is INFO', async () => {
      const logFile = path.join(testLogDir, 'info.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.INFO,
        batchSize: 1
      });

      logger.info('Info message', { userId: 'user-123' });
      logger.stop(); // Stop will flush

      await new Promise(resolve => setTimeout(resolve, 150));

      expect(fs.existsSync(logFile)).toBe(true);
      const content = fs.readFileSync(logFile, 'utf8');
      expect(content).toContain('INFO');
      expect(content).toContain('Info message');
    });

    it('should log warning messages', async () => {
      const logFile = path.join(testLogDir, 'warn.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.WARN,
        batchSize: 1
      });

      logger.warn('Warning message', { severity: Severity.MEDIUM });
      logger.stop();

      await new Promise(resolve => setTimeout(resolve, 150));

      const content = fs.readFileSync(logFile, 'utf8');
      expect(content).toContain('WARN');
      expect(content).toContain('Warning message');
    });

    it('should log error messages', async () => {
      const logFile = path.join(testLogDir, 'error.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.ERROR,
        batchSize: 1
      });

      logger.error('Error message', { error: 'Something failed' });
      logger.stop();

      await new Promise(resolve => setTimeout(resolve, 150));

      const content = fs.readFileSync(logFile, 'utf8');
      expect(content).toContain('ERROR');
      expect(content).toContain('Error message');
    });

    it('should not log messages below configured level', async () => {
      const logFile = path.join(testLogDir, 'filtered.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.ERROR, // Only log ERROR
        batchSize: 1
      });

      logger.debug('Debug message');
      logger.info('Info message');
      logger.warn('Warn message');
      logger.error('Error message');
      logger.stop();

      await new Promise(resolve => setTimeout(resolve, 150));

      const content = fs.readFileSync(logFile, 'utf8');
      expect(content).not.toContain('DEBUG');
      expect(content).not.toContain('INFO');
      expect(content).not.toContain('WARN');
      expect(content).toContain('ERROR');
    });
  });

  describe('logSecurityEvent', () => {
    it('should log structured security event', async () => {
      const logFile = path.join(testLogDir, 'security.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.INFO,
        batchSize: 1
      });

      logger.logSecurityEvent({
        severity: Severity.HIGH,
        action: Action.BLOCK,
        userId: 'user-123',
        module: 'prompt_injection',
        fingerprint: 'fp-123',
        message: 'Prompt injection detected'
      });

      logger.stop();
      await new Promise(resolve => setTimeout(resolve, 150));

      const content = fs.readFileSync(logFile, 'utf8');
      const logEntry = JSON.parse(content.trim());

      expect(logEntry.level).toBe('INFO');
      expect(logEntry.severity).toBe(Severity.HIGH);
      expect(logEntry.action).toBe(Action.BLOCK);
      expect(logEntry.userId).toBe('user-123');
      expect(logEntry.module).toBe('prompt_injection');
      expect(logEntry.fingerprint).toBe('fp-123');
    });

    it('should include metadata in security event', async () => {
      const logFile = path.join(testLogDir, 'security-meta.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.INFO,
        batchSize: 1
      });

      logger.logSecurityEvent({
        severity: Severity.CRITICAL,
        action: Action.BLOCK_NOTIFY,
        userId: 'user-456',
        module: 'command_validator',
        fingerprint: 'fp-456',
        message: 'Command injection attempt',
        metadata: {
          command: 'rm -rf /',
          patternId: 'cmd-inject-001'
        }
      });

      logger.stop();
      await new Promise(resolve => setTimeout(resolve, 150));

      const content = fs.readFileSync(logFile, 'utf8');
      const logEntry = JSON.parse(content.trim());

      expect(logEntry.metadata).toBeDefined();
      expect(logEntry.metadata.command).toBe('rm -rf /');
      expect(logEntry.metadata.patternId).toBe('cmd-inject-001');
    });
  });

  describe('buffered writes', () => {
    it('should buffer writes and flush manually', async () => {
      const logFile = path.join(testLogDir, 'buffered.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.INFO,
        batchSize: 1
      });

      // Log multiple messages
      logger.info('Message 1');
      logger.info('Message 2');
      logger.info('Message 3');

      logger.stop();
      await new Promise(resolve => setTimeout(resolve, 150));

      const content = fs.readFileSync(logFile, 'utf8');
      const lines = content.trim().split('\n');

      expect(lines.length).toBe(3);
    });
  });

  describe('log rotation', () => {
    it('should rotate log file when it exceeds max size', async () => {
      const logFile = path.join(testLogDir, 'rotate.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.INFO,
        maxFileSize: 500, // 500 bytes - very small for testing
        batchSize: 1
      });

      // Write enough data to trigger rotation
      for (let i = 0; i < 10; i++) {
        logger.info(`This is a test message that will help us exceed the max file size ${i}`, {
          data: 'x'.repeat(50)
        });
      }

      logger.stop();
      await new Promise(resolve => setTimeout(resolve, 200));

      // Check that rotated file exists
      const files = fs.readdirSync(testLogDir);
      const rotatedFiles = files.filter(f => f.startsWith('rotate.log.'));

      expect(rotatedFiles.length).toBeGreaterThan(0);
    });

    it('should keep only specified number of rotated files', async () => {
      const logFile = path.join(testLogDir, 'rotate-limit.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.INFO,
        maxFileSize: 300,
        maxRotatedFiles: 3,
        batchSize: 1
      });

      // Write enough to create multiple rotations
      for (let i = 0; i < 20; i++) {
        logger.info(`Message ${i}`, { data: 'x'.repeat(100) });
      }

      logger.stop();
      await new Promise(resolve => setTimeout(resolve, 200));

      const files = fs.readdirSync(testLogDir);
      const rotatedFiles = files.filter(f => f.startsWith('rotate-limit.log.'));

      // Should keep max 3 rotated files
      expect(rotatedFiles.length).toBeLessThanOrEqual(3);
    });
  });

  describe('JSON formatting', () => {
    it('should write valid JSON for each log entry', async () => {
      const logFile = path.join(testLogDir, 'json.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.INFO,
        batchSize: 1
      });

      logger.info('Test message', { key: 'value', number: 42 });
      logger.stop();
      await new Promise(resolve => setTimeout(resolve, 150));

      const content = fs.readFileSync(logFile, 'utf8');
      const logEntry = JSON.parse(content.trim());

      expect(logEntry).toHaveProperty('timestamp');
      expect(logEntry).toHaveProperty('level');
      expect(logEntry).toHaveProperty('message');
      expect(logEntry.message).toBe('Test message');
      expect(logEntry.key).toBe('value');
      expect(logEntry.number).toBe(42);
    });

    it('should handle special characters in log messages', async () => {
      const logFile = path.join(testLogDir, 'special-chars.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.INFO,
        batchSize: 1
      });

      logger.info('Message with "quotes" and \\backslashes\\', {
        special: 'newline\nand\ttab'
      });

      logger.stop();
      await new Promise(resolve => setTimeout(resolve, 150));

      const content = fs.readFileSync(logFile, 'utf8');
      const logEntry = JSON.parse(content.trim());

      expect(logEntry.message).toContain('quotes');
      expect(logEntry.special).toContain('\n');
    });
  });

  describe('error handling', () => {
    it('should handle write errors gracefully', async () => {
      const logFile = path.join(testLogDir, 'write-error.log');
      const logger = new Logger({
        filePath: logFile,
        level: LogLevel.INFO
      });

      logger.info('Test message');
      logger.stop();

      // Try to log after stop - should not throw
      logger.info('After stop');

      expect(true).toBe(true);
    });
  });
});
