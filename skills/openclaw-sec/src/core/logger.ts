import * as fs from 'fs';
import * as path from 'path';
import { AsyncQueue } from './async-queue';
import { Severity, Action } from '../types';

/**
 * Log levels in order of severity
 */
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

/**
 * Configuration options for Logger
 */
export interface LoggerOptions {
  filePath: string;
  level: LogLevel;
  batchSize?: number;
  flushInterval?: number;
  maxFileSize?: number; // in bytes
  maxRotatedFiles?: number;
}

/**
 * Security event log entry
 */
export interface SecurityEventLog {
  severity: Severity;
  action: Action;
  userId: string;
  module: string;
  fingerprint: string;
  message: string;
  metadata?: Record<string, any>;
}

/**
 * Logger provides structured JSON logging to file with buffered writes,
 * log rotation, and integration with AsyncQueue.
 *
 * Features:
 * - Structured JSON logging
 * - Buffered writes via AsyncQueue
 * - Automatic log rotation by file size
 * - Configurable log levels
 * - Manual flush support
 *
 * @example
 * ```typescript
 * const logger = new Logger({
 *   filePath: '/path/to/logs/security.log',
 *   level: LogLevel.INFO,
 *   maxFileSize: 10 * 1024 * 1024, // 10MB
 *   maxRotatedFiles: 5
 * });
 *
 * logger.info('Application started');
 * logger.logSecurityEvent({
 *   severity: Severity.HIGH,
 *   action: Action.BLOCK,
 *   userId: 'user-123',
 *   module: 'prompt_injection',
 *   fingerprint: 'fp-123',
 *   message: 'Malicious input detected'
 * });
 *
 * await logger.flush();
 * logger.stop();
 * ```
 */
export class Logger {
  private readonly filePath: string;
  private readonly level: LogLevel;
  private readonly maxFileSize: number;
  private readonly maxRotatedFiles: number;
  private readonly queue: AsyncQueue;
  private readonly levelPriority: Record<LogLevel, number> = {
    [LogLevel.DEBUG]: 0,
    [LogLevel.INFO]: 1,
    [LogLevel.WARN]: 2,
    [LogLevel.ERROR]: 3
  };

  /**
   * Creates a new Logger instance
   *
   * @param options - Logger configuration
   * @throws Error if filePath is missing
   */
  constructor(options: LoggerOptions) {
    if (!options.filePath || options.filePath.trim().length === 0) {
      throw new Error('Log file path is required');
    }

    this.filePath = options.filePath;
    this.level = options.level;
    this.maxFileSize = options.maxFileSize ?? 10 * 1024 * 1024; // Default 10MB
    this.maxRotatedFiles = options.maxRotatedFiles ?? 5;

    // Ensure log directory exists
    const logDir = path.dirname(this.filePath);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }

    // Initialize AsyncQueue for buffered writes
    this.queue = new AsyncQueue({
      batchSize: options.batchSize ?? 50,
      flushInterval: options.flushInterval ?? 100,
      onBatch: async (logs: string[]) => {
        await this.writeBatch(logs);
      }
    });
  }

  /**
   * Log a debug message
   */
  debug(message: string, metadata?: Record<string, any>): void {
    this.log(LogLevel.DEBUG, message, metadata);
  }

  /**
   * Log an info message
   */
  info(message: string, metadata?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, metadata);
  }

  /**
   * Log a warning message
   */
  warn(message: string, metadata?: Record<string, any>): void {
    this.log(LogLevel.WARN, message, metadata);
  }

  /**
   * Log an error message
   */
  error(message: string, metadata?: Record<string, any>): void {
    this.log(LogLevel.ERROR, message, metadata);
  }

  /**
   * Log a structured security event
   */
  logSecurityEvent(event: SecurityEventLog): void {
    const logData: Record<string, any> = {
      severity: event.severity,
      action: event.action,
      userId: event.userId,
      module: event.module,
      fingerprint: event.fingerprint
    };

    // Include metadata if provided
    if (event.metadata) {
      logData.metadata = event.metadata;
    }

    this.log(LogLevel.INFO, event.message, logData);
  }

  /**
   * Flush all pending log entries
   */
  async flush(): Promise<void> {
    await this.queue.flush();
  }

  /**
   * Stop the logger and flush remaining logs
   */
  stop(): void {
    // Flush synchronously before stopping
    const remainingSize = this.queue.size();
    if (remainingSize > 0) {
      // Force flush remaining logs
      this.queue.flush().catch(err => {
        console.error('Error flushing logs on stop:', err);
      });
    }
    this.queue.stop();
  }

  /**
   * Log a message at the specified level
   * @private
   */
  private log(level: LogLevel, message: string, metadata?: Record<string, any>): void {
    // Check if this message should be logged based on level
    if (this.levelPriority[level] < this.levelPriority[this.level]) {
      return;
    }

    const logEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      ...metadata
    };

    const logLine = JSON.stringify(logEntry);
    this.queue.enqueue(logLine);
  }

  /**
   * Write a batch of log entries to file
   * @private
   */
  private async writeBatch(logs: string[]): Promise<void> {
    try {
      // Write logs to file
      const content = logs.join('\n') + '\n';
      fs.appendFileSync(this.filePath, content, 'utf8');

      // Check if rotation is needed after write
      await this.rotateIfNeeded();
    } catch (error) {
      // Log to console if file write fails
      console.error('Failed to write logs to file:', error);
    }
  }

  /**
   * Rotate log file if it exceeds max size
   * @private
   */
  private async rotateIfNeeded(): Promise<void> {
    try {
      // Check if file exists and get size
      if (!fs.existsSync(this.filePath)) {
        return;
      }

      const stats = fs.statSync(this.filePath);
      if (stats.size < this.maxFileSize) {
        return;
      }

      // Rotate the log file
      const timestamp = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');
      const rotatedPath = `${this.filePath}.${timestamp}`;

      fs.renameSync(this.filePath, rotatedPath);

      // Clean up old rotated files
      this.cleanupOldRotatedFiles();
    } catch (error) {
      console.error('Error during log rotation:', error);
    }
  }

  /**
   * Remove old rotated files beyond maxRotatedFiles limit
   * @private
   */
  private cleanupOldRotatedFiles(): void {
    try {
      const logDir = path.dirname(this.filePath);
      const logFileName = path.basename(this.filePath);

      // Get all rotated files
      const files = fs.readdirSync(logDir);
      const rotatedFiles = files
        .filter(f => f.startsWith(logFileName + '.'))
        .map(f => ({
          name: f,
          path: path.join(logDir, f),
          mtime: fs.statSync(path.join(logDir, f)).mtime.getTime()
        }))
        .sort((a, b) => b.mtime - a.mtime); // Sort by modification time, newest first

      // Remove old files beyond the limit
      if (rotatedFiles.length > this.maxRotatedFiles) {
        const filesToDelete = rotatedFiles.slice(this.maxRotatedFiles);
        filesToDelete.forEach(file => {
          try {
            fs.unlinkSync(file.path);
          } catch (error) {
            console.error(`Failed to delete old log file ${file.name}:`, error);
          }
        });
      }
    } catch (error) {
      console.error('Error cleaning up old rotated files:', error);
    }
  }
}
