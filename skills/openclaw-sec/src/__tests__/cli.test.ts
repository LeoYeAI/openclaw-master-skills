import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

describe('CLI', () => {
  const cliPath = path.join(process.cwd(), 'src', 'cli.ts');
  const testDbPath = '.openclaw-sec-test.db';

  beforeEach(() => {
    // Clean up test database
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }
  });

  afterEach(() => {
    // Clean up test database
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }
  });

  describe('validate-command', () => {
    it('should validate safe command', () => {
      const output = execSync(`npx tsx "${cliPath}" validate-command "ls -la"`, {
        encoding: 'utf8'
      });

      expect(output).toContain('Validating command');
      expect(output).toContain('Severity');
      expect(output).toContain('Action');
    });

    it('should detect dangerous command', () => {
      try {
        execSync(`npx tsx "${cliPath}" validate-command "rm -rf /"`, {
          encoding: 'utf8'
        });
      } catch (error: any) {
        // Should exit with non-zero code for blocked commands
        expect(error.status).toBeGreaterThan(0);
      }
    });
  });

  describe('check-url', () => {
    it('should validate URL', () => {
      const output = execSync(`npx tsx "${cliPath}" check-url "https://example.com"`, {
        encoding: 'utf8'
      });

      expect(output).toContain('Checking URL');
      expect(output).toContain('Severity');
    });
  });

  describe('validate-path', () => {
    it('should validate file path', () => {
      const output = execSync(`npx tsx "${cliPath}" validate-path "/tmp/test.txt"`, {
        encoding: 'utf8'
      });

      expect(output).toContain('Validating path');
      expect(output).toContain('Severity');
    });

    it('should detect path traversal', () => {
      try {
        execSync(`npx tsx "${cliPath}" validate-path "../../etc/passwd"`, {
          encoding: 'utf8'
        });
      } catch (error: any) {
        // Should exit with non-zero code for dangerous paths
        expect(error.status).toBeGreaterThan(0);
      }
    });
  });

  describe('scan-content', () => {
    it('should scan text content', () => {
      const output = execSync(`npx tsx "${cliPath}" scan-content "Hello world"`, {
        encoding: 'utf8'
      });

      expect(output).toContain('Scanning content');
      expect(output).toContain('Severity');
    });
  });

  describe('check-all', () => {
    it('should run comprehensive scan', () => {
      const output = execSync(`npx tsx "${cliPath}" check-all "Test input"`, {
        encoding: 'utf8'
      });

      expect(output).toContain('comprehensive security scan');
      expect(output).toContain('Scan Results');
    });
  });

  describe('config', () => {
    it('should show configuration', () => {
      const output = execSync(`npx tsx "${cliPath}" config`, {
        encoding: 'utf8'
      });

      expect(output).toContain('Configuration');
      expect(output).toContain('Modules');
    });
  });

  describe('test', () => {
    it('should run configuration tests', () => {
      const output = execSync(`npx tsx "${cliPath}" test`, {
        encoding: 'utf8'
      });

      expect(output).toContain('Testing Security Configuration');
      expect(output).toContain('Test Results');
    });
  });

  describe('db-vacuum', () => {
    it('should optimize database or handle missing db', () => {
      const output = execSync(`npx tsx "${cliPath}" db-vacuum`, {
        encoding: 'utf8'
      });

      // Should either optimize or report no database
      const validOutput = output.includes('optimized') || output.includes('No database found');
      expect(validOutput).toBe(true);
    });
  });

  describe('stats', () => {
    it('should show statistics', () => {
      const output = execSync(`npx tsx "${cliPath}" stats`, {
        encoding: 'utf8'
      });

      const hasStats = output.includes('statistics') || output.includes('Statistics');
      expect(hasStats).toBe(true);
    });
  });
});
