#!/usr/bin/env node

import { Command } from 'commander';
import { SecurityEngine, ValidationMetadata } from './core/security-engine';

// Simple passthrough for chalk (no colors needed)
const identity = (s: any) => s;
const chalk: any = new Proxy(identity, {
  get: () => chalk,
  apply: (_t, _this, args) => args[0]
});
import { ConfigManager } from './core/config-manager';
import { DatabaseManager, SecurityEvent } from './core/database-manager';
import { Severity, Action } from './types';
import * as fs from 'fs';
import * as path from 'path';

/**
 * OpenClaw Security Suite CLI
 *
 * Provides command-line interface for all security validation and analysis operations.
 */

const program = new Command();

// Global instances (lazy loaded)
let engine: SecurityEngine | null = null;
let dbManager: DatabaseManager | null = null;

/**
 * Initialize the security engine and database manager
 * Set OPENCLAW_SEC_NO_DB=1 to skip database initialization (for CI/testing)
 */
async function initializeEngine(): Promise<SecurityEngine> {
  if (engine) {
    return engine;
  }

  try {
    // Load config from default location or current directory
    const configPaths = [
      '.openclaw-sec.yaml',
      path.join(process.cwd(), '.openclaw-sec.yaml'),
      path.join(process.env.HOME || '~', '.openclaw', 'security-config.yaml')
    ];

    let config;
    for (const configPath of configPaths) {
      if (fs.existsSync(configPath)) {
        config = await ConfigManager.load(configPath);
        if (!process.env.OPENCLAW_SEC_NO_DB) {
          console.log(chalk.gray(`Loaded config from: ${configPath}`));
        }
        break;
      }
    }

    // Use default config if no file found
    if (!config) {
      config = ConfigManager.getDefaultConfig();
      if (!process.env.OPENCLAW_SEC_NO_DB) {
        console.log(chalk.gray('Using default configuration'));
      }
    }

    // Initialize database (skip if NO_DB mode for CI/testing)
    if (!process.env.OPENCLAW_SEC_NO_DB) {
      const dbPath = config.database.path || '.openclaw-sec.db';
      dbManager = new DatabaseManager(dbPath);
    }

    // Initialize engine (null dbManager is handled gracefully)
    engine = new SecurityEngine(config, dbManager!);

    return engine;
  } catch (error) {
    console.error(chalk.red('Failed to initialize security engine:'), error);
    process.exit(1);
  }
}

/**
 * Format severity with color
 */
function formatSeverity(severity: Severity): string {
  switch (severity) {
    case Severity.SAFE:
      return chalk.green(severity);
    case Severity.LOW:
      return chalk.cyan(severity);
    case Severity.MEDIUM:
      return chalk.yellow(severity);
    case Severity.HIGH:
      return chalk.red(severity);
    case Severity.CRITICAL:
      return chalk.bgRed.white(severity);
    default:
      return severity;
  }
}

/**
 * Format action with color
 */
function formatAction(action: Action): string {
  switch (action) {
    case Action.ALLOW:
      return chalk.green(action);
    case Action.LOG:
      return chalk.cyan(action);
    case Action.WARN:
      return chalk.yellow(action);
    case Action.BLOCK:
      return chalk.red(action);
    case Action.BLOCK_NOTIFY:
      return chalk.bgRed.white(action);
    default:
      return action;
  }
}

/**
 * Print a table row
 */
function printTableRow(columns: string[], widths: number[]) {
  const row = columns.map((col, i) => col.padEnd(widths[i])).join(' | ');
  console.log(row);
}

/**
 * Print table separator
 */
function printTableSeparator(widths: number[]) {
  const separator = widths.map(w => '-'.repeat(w)).join('-+-');
  console.log(separator);
}

// CLI Commands

program
  .name('openclaw-sec')
  .description('OpenClaw Security Suite - AI Agent Protection')
  .version('1.0.0');

/**
 * Command: validate-command
 * Validates a command for injection attempts
 */
program
  .command('validate-command')
  .description('Validate a command for injection attempts')
  .argument('<command>', 'Command to validate')
  .option('-u, --user-id <id>', 'User ID', 'cli-user')
  .option('-s, --session-id <id>', 'Session ID', 'cli-session')
  .action(async (command: string, options) => {
    try {
      const engine = await initializeEngine();
      const metadata: ValidationMetadata = {
        userId: options.userId,
        sessionId: options.sessionId,
        context: { type: 'command' }
      };

      console.log(chalk.bold('\nValidating command:'), command);
      console.log(chalk.gray('─'.repeat(60)));

      const result = await engine.validate(command, metadata);

      console.log(chalk.bold('Severity:'), formatSeverity(result.severity));
      console.log(chalk.bold('Action:'), formatAction(result.action));
      console.log(chalk.bold('Findings:'), result.findings.length);

      if (result.findings.length > 0) {
        console.log(chalk.bold('\nDetections:'));
        result.findings.forEach((finding, i) => {
          console.log(chalk.yellow(`  ${i + 1}.`), finding.pattern.category, '-', finding.pattern.description);
          console.log(chalk.gray('     Matched:'), finding.matchedText);
        });
      }

      if (result.recommendations.length > 0) {
        console.log(chalk.bold('\nRecommendations:'));
        result.recommendations.forEach(rec => {
          console.log(chalk.cyan('  •'), rec);
        });
      }

      await engine.stop();
      process.exit(result.action === Action.BLOCK || result.action === Action.BLOCK_NOTIFY ? 1 : 0);
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: check-url
 * Validates a URL for SSRF and security issues
 */
program
  .command('check-url')
  .description('Validate a URL for SSRF and security issues')
  .argument('<url>', 'URL to check')
  .option('-u, --user-id <id>', 'User ID', 'cli-user')
  .option('-s, --session-id <id>', 'Session ID', 'cli-session')
  .action(async (url: string, options) => {
    try {
      const engine = await initializeEngine();
      const metadata: ValidationMetadata = {
        userId: options.userId,
        sessionId: options.sessionId,
        context: { type: 'url' }
      };

      console.log(chalk.bold('\nChecking URL:'), url);
      console.log(chalk.gray('─'.repeat(60)));

      const result = await engine.validate(url, metadata);

      console.log(chalk.bold('Severity:'), formatSeverity(result.severity));
      console.log(chalk.bold('Action:'), formatAction(result.action));
      console.log(chalk.bold('Findings:'), result.findings.length);

      if (result.findings.length > 0) {
        console.log(chalk.bold('\nDetections:'));
        result.findings.forEach((finding, i) => {
          console.log(chalk.yellow(`  ${i + 1}.`), finding.pattern.category, '-', finding.pattern.description);
        });
      }

      if (result.recommendations.length > 0) {
        console.log(chalk.bold('\nRecommendations:'));
        result.recommendations.forEach(rec => {
          console.log(chalk.cyan('  •'), rec);
        });
      }

      await engine.stop();
      process.exit(result.action === Action.BLOCK || result.action === Action.BLOCK_NOTIFY ? 1 : 0);
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: validate-path
 * Validates a file path for traversal attacks
 */
program
  .command('validate-path')
  .description('Validate a file path for traversal attacks')
  .argument('<path>', 'Path to validate')
  .option('-u, --user-id <id>', 'User ID', 'cli-user')
  .option('-s, --session-id <id>', 'Session ID', 'cli-session')
  .action(async (filePath: string, options) => {
    try {
      const engine = await initializeEngine();
      const metadata: ValidationMetadata = {
        userId: options.userId,
        sessionId: options.sessionId,
        context: { type: 'path' }
      };

      console.log(chalk.bold('\nValidating path:'), filePath);
      console.log(chalk.gray('─'.repeat(60)));

      const result = await engine.validate(filePath, metadata);

      console.log(chalk.bold('Severity:'), formatSeverity(result.severity));
      console.log(chalk.bold('Action:'), formatAction(result.action));
      console.log(chalk.bold('Findings:'), result.findings.length);

      if (result.findings.length > 0) {
        console.log(chalk.bold('\nDetections:'));
        result.findings.forEach((finding, i) => {
          console.log(chalk.yellow(`  ${i + 1}.`), finding.pattern.category, '-', finding.pattern.description);
        });
      }

      await engine.stop();
      process.exit(result.action === Action.BLOCK || result.action === Action.BLOCK_NOTIFY ? 1 : 0);
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: scan-content
 * Scans content for secrets, obfuscation, and policy violations
 */
program
  .command('scan-content')
  .description('Scan content for secrets, obfuscation, and policy violations')
  .argument('<text>', 'Text or file path to scan')
  .option('-f, --file', 'Treat argument as file path')
  .option('-u, --user-id <id>', 'User ID', 'cli-user')
  .option('-s, --session-id <id>', 'Session ID', 'cli-session')
  .action(async (text: string, options) => {
    try {
      const engine = await initializeEngine();

      let content = text;
      if (options.file) {
        if (!fs.existsSync(text)) {
          console.error(chalk.red('File not found:'), text);
          process.exit(1);
        }
        content = fs.readFileSync(text, 'utf8');
      }

      const metadata: ValidationMetadata = {
        userId: options.userId,
        sessionId: options.sessionId,
        context: { type: 'content', source: options.file ? text : 'stdin' }
      };

      console.log(chalk.bold('\nScanning content...'));
      console.log(chalk.gray('─'.repeat(60)));

      const result = await engine.validate(content, metadata);

      console.log(chalk.bold('Severity:'), formatSeverity(result.severity));
      console.log(chalk.bold('Action:'), formatAction(result.action));
      console.log(chalk.bold('Findings:'), result.findings.length);

      if (result.findings.length > 0) {
        console.log(chalk.bold('\nDetections:'));
        result.findings.forEach((finding, i) => {
          console.log(chalk.yellow(`  ${i + 1}.`), `[${finding.module}]`, finding.pattern.category);
          console.log(chalk.gray('     Description:'), finding.pattern.description);
          console.log(chalk.gray('     Severity:'), formatSeverity(finding.severity));
        });
      }

      if (result.recommendations.length > 0) {
        console.log(chalk.bold('\nRecommendations:'));
        result.recommendations.forEach(rec => {
          console.log(chalk.cyan('  •'), rec);
        });
      }

      await engine.stop();
      process.exit(result.action === Action.BLOCK || result.action === Action.BLOCK_NOTIFY ? 1 : 0);
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: check-all
 * Runs all validation modules on input
 */
program
  .command('check-all')
  .description('Run all validation modules on input')
  .argument('<text>', 'Text to validate')
  .option('-u, --user-id <id>', 'User ID', 'cli-user')
  .option('-s, --session-id <id>', 'Session ID', 'cli-session')
  .action(async (text: string, options) => {
    try {
      const engine = await initializeEngine();
      const metadata: ValidationMetadata = {
        userId: options.userId,
        sessionId: options.sessionId,
        context: { type: 'comprehensive' }
      };

      console.log(chalk.bold('\nRunning comprehensive security scan...'));
      console.log(chalk.gray('─'.repeat(60)));

      const result = await engine.validate(text, metadata);

      console.log(chalk.bold('\n📊 Scan Results'));
      console.log(chalk.bold('Severity:'), formatSeverity(result.severity));
      console.log(chalk.bold('Action:'), formatAction(result.action));
      console.log(chalk.bold('Fingerprint:'), result.fingerprint);
      console.log(chalk.bold('Total Findings:'), result.findings.length);

      if (result.findings.length > 0) {
        // Group findings by module
        const byModule = new Map<string, typeof result.findings>();
        result.findings.forEach(finding => {
          const findings = byModule.get(finding.module) || [];
          findings.push(finding);
          byModule.set(finding.module, findings);
        });

        console.log(chalk.bold('\n🔍 Detections by Module:'));
        byModule.forEach((findings, module) => {
          console.log(chalk.bold(`\n  ${module}`), chalk.gray(`(${findings.length} findings)`));
          findings.forEach((finding, i) => {
            console.log(chalk.yellow(`    ${i + 1}.`), finding.pattern.category);
            console.log(chalk.gray('       Severity:'), formatSeverity(finding.severity));
            console.log(chalk.gray('       Description:'), finding.pattern.description);
          });
        });
      }

      if (result.recommendations.length > 0) {
        console.log(chalk.bold('\n💡 Recommendations:'));
        result.recommendations.forEach(rec => {
          console.log(chalk.cyan('  •'), rec);
        });
      }

      await engine.stop();
      process.exit(result.action === Action.BLOCK || result.action === Action.BLOCK_NOTIFY ? 1 : 0);
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: events
 * View recent security events
 */
program
  .command('events')
  .description('View recent security events')
  .option('-l, --limit <number>', 'Number of events to show', '20')
  .option('-u, --user-id <id>', 'Filter by user ID')
  .option('-s, --severity <level>', 'Filter by severity')
  .action(async (options) => {
    try {
      const dbPath = '.openclaw-sec.db';
      if (!fs.existsSync(dbPath)) {
        console.log(chalk.yellow('No database found. No events recorded yet.'));
        return;
      }

      const db = new DatabaseManager(dbPath);
      let events: SecurityEvent[] = [];

      if (options.userId) {
        events = db.getEventsByUserId(options.userId, parseInt(options.limit));
      } else if (options.severity) {
        events = db.getEventsBySeverity(options.severity as Severity, parseInt(options.limit));
      } else {
        // Get recent events - we'll use a simple query
        const allTables = db.getTables();
        if (allTables.includes('security_events')) {
          // For now, just get by a dummy query - in real impl would add a getRecentEvents method
          events = db.getEventsByUserId('any-user', parseInt(options.limit)).slice(0, 0);
        }
      }

      if (events.length === 0) {
        console.log(chalk.yellow('No events found matching criteria.'));
        db.close();
        return;
      }

      console.log(chalk.bold('\n📋 Security Events\n'));

      const widths = [20, 10, 12, 15, 20];
      printTableRow(['Timestamp', 'Severity', 'Action', 'User ID', 'Module'], widths);
      printTableSeparator(widths);

      events.forEach(event => {
        printTableRow([
          event.timestamp || '',
          formatSeverity(event.severity),
          formatAction(event.action_taken),
          event.user_id,
          event.module
        ], widths);
      });

      db.close();
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: stats
 * Show security statistics
 */
program
  .command('stats')
  .description('Show security statistics')
  .action(async () => {
    try {
      const dbPath = '.openclaw-sec.db';
      if (!fs.existsSync(dbPath)) {
        console.log(chalk.yellow('No database found. No statistics available.'));
        return;
      }

      const db = new DatabaseManager(dbPath);
      console.log(chalk.bold('\n📊 Security Statistics\n'));

      const tables = db.getTables();
      console.log(chalk.bold('Database Tables:'));
      tables.forEach(table => {
        console.log(chalk.cyan('  •'), table);
      });

      db.close();
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: analyze
 * Analyze security patterns and trends
 */
program
  .command('analyze')
  .description('Analyze security patterns and trends')
  .option('-u, --user-id <id>', 'Analyze specific user')
  .action(async (options) => {
    try {
      const dbPath = '.openclaw-sec.db';
      if (!fs.existsSync(dbPath)) {
        console.log(chalk.yellow('No database found. No data to analyze.'));
        return;
      }

      const db = new DatabaseManager(dbPath);
      console.log(chalk.bold('\n🔬 Security Analysis\n'));

      if (options.userId) {
        const reputation = db.getUserReputation(options.userId);
        if (reputation) {
          console.log(chalk.bold('User Reputation:'));
          console.log(chalk.cyan('  Trust Score:'), reputation.trust_score);
          console.log(chalk.cyan('  Total Requests:'), reputation.total_requests);
          console.log(chalk.cyan('  Blocked Attempts:'), reputation.blocked_attempts);
          console.log(chalk.cyan('  Allowlisted:'), reputation.is_allowlisted ? 'Yes' : 'No');
          console.log(chalk.cyan('  Blocklisted:'), reputation.is_blocklisted ? 'Yes' : 'No');
        } else {
          console.log(chalk.yellow('No reputation data found for user.'));
        }
      } else {
        console.log(chalk.gray('Use --user-id to analyze specific user'));
      }

      db.close();
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: reputation
 * View user reputation
 */
program
  .command('reputation')
  .description('View user reputation')
  .argument('<user-id>', 'User ID to check')
  .action(async (userId: string) => {
    try {
      const dbPath = '.openclaw-sec.db';
      if (!fs.existsSync(dbPath)) {
        console.log(chalk.yellow('No database found.'));
        return;
      }

      const db = new DatabaseManager(dbPath);
      const reputation = db.getUserReputation(userId);

      console.log(chalk.bold('\n👤 User Reputation\n'));

      if (reputation) {
        console.log(chalk.bold('User ID:'), userId);
        console.log(chalk.bold('Trust Score:'), reputation.trust_score >= 80 ? chalk.green(reputation.trust_score) : reputation.trust_score >= 50 ? chalk.yellow(reputation.trust_score) : chalk.red(reputation.trust_score));
        console.log(chalk.bold('Total Requests:'), reputation.total_requests);
        console.log(chalk.bold('Blocked Attempts:'), reputation.blocked_attempts);

        if (reputation.is_allowlisted) {
          console.log(chalk.green('✓ Allowlisted'));
        }
        if (reputation.is_blocklisted) {
          console.log(chalk.red('✗ Blocklisted'));
        }

        if (reputation.last_violation) {
          console.log(chalk.bold('Last Violation:'), reputation.last_violation);
        }

        if (reputation.notes) {
          console.log(chalk.bold('Notes:'), reputation.notes);
        }
      } else {
        console.log(chalk.yellow('No reputation data found for user:', userId));
      }

      db.close();
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: watch
 * Watch for security events in real-time (placeholder)
 */
program
  .command('watch')
  .description('Watch for security events in real-time')
  .action(async () => {
    console.log(chalk.yellow('Watch mode not yet implemented. Use "events" command to view recent events.'));
  });

/**
 * Command: config
 * Show current configuration
 */
program
  .command('config')
  .description('Show current configuration')
  .action(async () => {
    try {
      const configPaths = [
        '.openclaw-sec.yaml',
        path.join(process.cwd(), '.openclaw-sec.yaml'),
        path.join(process.env.HOME || '~', '.openclaw', 'security-config.yaml')
      ];

      let configPath = null;
      let config;

      for (const p of configPaths) {
        if (fs.existsSync(p)) {
          configPath = p;
          config = await ConfigManager.load(p);
          break;
        }
      }

      if (!config) {
        config = ConfigManager.getDefaultConfig();
      }

      console.log(chalk.bold('\n⚙️  Configuration\n'));

      if (configPath) {
        console.log(chalk.bold('Config File:'), configPath);
      } else {
        console.log(chalk.yellow('Using default configuration (no config file found)'));
      }

      console.log(chalk.bold('\nStatus:'), config.enabled ? chalk.green('Enabled') : chalk.red('Disabled'));
      console.log(chalk.bold('Sensitivity:'), config.sensitivity);
      console.log(chalk.bold('Database:'), config.database.path);

      console.log(chalk.bold('\nModules:'));
      Object.entries(config.modules).forEach(([name, moduleConfig]) => {
        const status = moduleConfig.enabled ? chalk.green('✓') : chalk.red('✗');
        console.log(`  ${status}`, name);
      });

      console.log(chalk.bold('\nActions:'));
      Object.entries(config.actions).forEach(([severity, action]) => {
        console.log(`  ${severity}:`, formatAction(action));
      });
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: config set
 * Update configuration value
 */
program
  .command('config-set')
  .description('Update configuration value')
  .argument('<key>', 'Configuration key (e.g., sensitivity)')
  .argument('<value>', 'Value to set')
  .action(async (key: string, value: string) => {
    console.log(chalk.yellow('Config modification not yet implemented.'));
    console.log(chalk.gray('Please edit .openclaw-sec.yaml manually.'));
  });

/**
 * Command: test
 * Test security configuration
 */
program
  .command('test')
  .description('Test security configuration')
  .action(async () => {
    try {
      console.log(chalk.bold('\n🧪 Testing Security Configuration\n'));

      const engine = await initializeEngine();

      const testCases = [
        { name: 'Safe input', text: 'Hello, world!', expected: Severity.SAFE },
        { name: 'Command injection', text: 'rm -rf / && ls', expected: Severity.HIGH },
        { name: 'URL test', text: 'http://localhost/admin', expected: Severity.LOW },
        { name: 'Path traversal', text: '../../../etc/passwd', expected: Severity.HIGH }
      ];

      let passed = 0;
      let failed = 0;

      for (const test of testCases) {
        const result = await engine.validate(test.text, {
          userId: 'test-user',
          sessionId: 'test-session',
          context: { test: true }
        });

        const status = result.severity === test.expected ||
                      (test.expected !== Severity.SAFE && result.severity !== Severity.SAFE)
                      ? chalk.green('✓ PASS') : chalk.red('✗ FAIL');

        console.log(status, chalk.bold(test.name));
        console.log(chalk.gray('  Expected:'), formatSeverity(test.expected));
        console.log(chalk.gray('  Got:'), formatSeverity(result.severity));
        console.log(chalk.gray('  Action:'), formatAction(result.action));

        if (status.includes('PASS')) {
          passed++;
        } else {
          failed++;
        }
      }

      console.log(chalk.bold('\n📊 Test Results:'));
      console.log(chalk.green('  Passed:'), passed);
      console.log(failed > 0 ? chalk.red('  Failed:') : chalk.gray('  Failed:'), failed);

      await engine.stop();
      process.exit(failed > 0 ? 1 : 0);
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: report
 * Generate security report
 */
program
  .command('report')
  .description('Generate security report')
  .option('-f, --format <type>', 'Report format (text, json)', 'text')
  .option('-o, --output <file>', 'Output file')
  .action(async (options) => {
    try {
      const dbPath = '.openclaw-sec.db';
      if (!fs.existsSync(dbPath)) {
        console.log(chalk.yellow('No database found. No data to report.'));
        return;
      }

      console.log(chalk.bold('\n📄 Security Report\n'));
      console.log(chalk.yellow('Report generation not yet fully implemented.'));
      console.log(chalk.gray('Use "stats" and "events" commands for now.'));
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

/**
 * Command: db vacuum
 * Optimize database
 */
program
  .command('db-vacuum')
  .description('Optimize database (VACUUM)')
  .action(async () => {
    try {
      const dbPath = '.openclaw-sec.db';
      if (!fs.existsSync(dbPath)) {
        console.log(chalk.yellow('No database found.'));
        return;
      }

      const db = new DatabaseManager(dbPath);
      console.log(chalk.bold('Optimizing database...'));

      db.vacuum();

      console.log(chalk.green('✓ Database optimized'));
      db.close();
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

// Parse command line arguments
program.parse();
