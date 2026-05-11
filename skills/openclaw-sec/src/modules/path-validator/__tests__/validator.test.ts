import { describe, it, expect } from '@jest/globals';
import { PathValidator } from '../validator';
import { ModuleConfig } from '../../../types';

describe('PathValidator', () => {
  const defaultConfig: ModuleConfig = {
    enabled: true
  };

  describe('constructor', () => {
    it('should create an instance with valid config', () => {
      const validator = new PathValidator(defaultConfig);
      expect(validator).toBeInstanceOf(PathValidator);
    });

    it('should throw error if config is invalid', () => {
      expect(() => new PathValidator(null as any)).toThrow();
    });
  });

  describe('validate', () => {
    describe('Path traversal patterns', () => {
      it('should detect ../ pattern', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '../etc/passwd';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].module).toBe('path_validator');
        expect(findings[0].pattern.category).toBe('path_traversal');
      });

      it('should detect ..\\ pattern (Windows)', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '..\\windows\\system32';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('dot_dot_slash');
      });

      it('should detect multiple traversal sequences', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '../../../../../../etc/passwd';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
      });

      it('should detect traversal in middle of path', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = 'files/../../secret.txt';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
      });
    });

    describe('URL-encoded traversal', () => {
      it('should detect %2e%2e%2f pattern', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '%2e%2e%2fetc%2fpasswd';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'encoded_dot_dot_slash')).toBe(true);
      });

      it('should detect mixed encoded traversal', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '..%2f..%2fetc%2fpasswd';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
      });

      it('should detect double-encoded traversal', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '%252e%252e%252f';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'double_encoded')).toBe(true);
      });
    });

    describe('Sensitive Unix files', () => {
      it('should detect /etc/passwd access attempt', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/etc/passwd';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'unix_passwd')).toBe(true);
        expect(findings.some(f => f.severity === 'CRITICAL')).toBe(true);
      });

      it('should detect /etc/shadow access attempt', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '../../etc/shadow';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'unix_passwd')).toBe(true);
      });
    });

    describe('SSH keys', () => {
      it('should detect id_rsa access attempt', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '.ssh/id_rsa';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'ssh_keys')).toBe(true);
        expect(findings.some(f => f.severity === 'CRITICAL')).toBe(true);
      });

      it('should detect id_ed25519 access attempt', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/home/user/.ssh/id_ed25519';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'ssh_keys')).toBe(true);
      });

      it('should detect authorized_keys access attempt', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '../.ssh/authorized_keys';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'ssh_keys')).toBe(true);
      });
    });

    describe('Windows sensitive files', () => {
      it('should detect Windows SAM database access', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = 'C:\\windows\\system32\\config\\sam';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'windows_sam')).toBe(true);
        expect(findings.some(f => f.severity === 'CRITICAL')).toBe(true);
      });

      it('should detect forward slash variant', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/windows/system32/config/system';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'windows_sam')).toBe(true);
      });
    });

    describe('Environment and configuration files', () => {
      it('should detect .env file access', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '.env';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'environment_files')).toBe(true);
      });

      it('should detect .env.local variant', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '../.env.production';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'environment_files')).toBe(true);
      });

      it('should detect .git/config access', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '.git/config';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'environment_files')).toBe(true);
      });
    });

    describe('Cloud credentials', () => {
      it('should detect AWS credentials access', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '.aws/credentials';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'aws_credentials')).toBe(true);
        expect(findings.some(f => f.severity === 'CRITICAL')).toBe(true);
      });

      it('should detect AWS config access', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/home/user/.aws/config';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'aws_credentials')).toBe(true);
      });
    });

    describe('Container secrets', () => {
      it('should detect Docker secrets access', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/run/secrets/db_password';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'docker_secrets')).toBe(true);
        expect(findings.some(f => f.severity === 'CRITICAL')).toBe(true);
      });

      it('should detect Kubernetes service account token', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/var/run/secrets/kubernetes.io/serviceaccount/token';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'docker_secrets')).toBe(true);
      });
    });

    describe('Backup and temporary files', () => {
      it('should detect .bak file extension', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = 'config.php.bak';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'backup_files')).toBe(true);
      });

      it('should detect .backup extension', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = 'database.sql.backup';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'backup_files')).toBe(true);
      });

      it('should detect tilde backup files', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = 'important~';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'backup_files')).toBe(true);
      });
    });

    describe('Log files', () => {
      it('should detect /var/log/ access', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/var/log/apache2/access.log';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'log_files')).toBe(true);
      });

      it('should detect .log extension', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = 'application.log';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'log_files')).toBe(true);
      });
    });

    describe('/proc filesystem', () => {
      it('should detect /proc/self/environ access', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/proc/self/environ';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'proc_filesystem')).toBe(true);
      });

      it('should detect /proc/self/cmdline access', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/proc/self/cmdline';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'proc_filesystem')).toBe(true);
      });

      it('should detect /proc/PID/environ access', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/proc/1/environ';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'proc_filesystem')).toBe(true);
      });
    });

    describe('Null byte injection', () => {
      it('should detect null byte in path', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = 'file.txt%00.jpg';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'null_byte')).toBe(true);
      });

      it('should detect null byte with traversal', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '../../../etc/passwd%00';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'null_byte')).toBe(true);
      });
    });

    describe('Absolute paths', () => {
      it('should detect absolute Unix paths', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/etc/hosts';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'absolute_unix_paths')).toBe(true);
      });

      it('should detect absolute Windows paths', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = 'C:\\windows\\win.ini';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'windows_absolute_paths')).toBe(true);
      });
    });

    describe('Safe paths', () => {
      it('should return empty array for safe relative path', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = 'files/document.pdf';

        const findings = await validator.validate(path);

        expect(findings).toEqual([]);
      });

      it('should return empty array for safe filename', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = 'report.txt';

        const findings = await validator.validate(path);

        expect(findings).toEqual([]);
      });

      it('should return empty array for safe subdirectory', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = 'data/uploads/image.png';

        const findings = await validator.validate(path);

        expect(findings).toEqual([]);
      });
    });

    describe('Edge cases and error handling', () => {
      it('should handle empty string', async () => {
        const validator = new PathValidator(defaultConfig);
        const findings = await validator.validate('');

        expect(findings).toEqual([]);
      });

      it('should throw error for null input', async () => {
        const validator = new PathValidator(defaultConfig);

        await expect(validator.validate(null as any)).rejects.toThrow();
      });

      it('should throw error for non-string input', async () => {
        const validator = new PathValidator(defaultConfig);

        await expect(validator.validate(123 as any)).rejects.toThrow();
      });

      it('should handle paths with spaces', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '../my documents/secret.txt';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
      });

      it('should handle mixed separators', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '..\\../mixed/separators';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
      });
    });

    describe('Multiple findings', () => {
      it('should detect multiple patterns in one path', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '../../../etc/passwd';

        const findings = await validator.validate(path);

        // Should match both traversal and passwd patterns
        expect(findings.length).toBeGreaterThan(0);
      });

      it('should detect traversal with SSH key access', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '../../.ssh/id_rsa';

        const findings = await validator.validate(path);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'dot_dot_slash')).toBe(true);
        expect(findings.some(f => f.pattern.subcategory === 'ssh_keys')).toBe(true);
      });
    });

    describe('Metadata', () => {
      it('should include metadata in findings', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '../etc/passwd';

        const findings = await validator.validate(path);

        expect(findings[0]).toHaveProperty('metadata');
        expect(findings[0].metadata).toBeDefined();
        expect(findings[0].metadata).toHaveProperty('path');
        expect(findings[0].metadata).toHaveProperty('normalizedPath');
        expect(findings[0].metadata).toHaveProperty('patternId');
      });

      it('should include path analysis in metadata', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '../secret.txt';

        const findings = await validator.validate(path);

        expect(findings[0].metadata).toHaveProperty('isAbsolute');
        expect(findings[0].metadata).toHaveProperty('hasTraversal');
        expect(findings[0].metadata!.hasTraversal).toBe(true);
      });

      it('should detect absolute path in metadata', async () => {
        const validator = new PathValidator(defaultConfig);
        const path = '/etc/passwd';

        const findings = await validator.validate(path);

        expect(findings[0].metadata!.isAbsolute).toBe(true);
      });
    });
  });
});
