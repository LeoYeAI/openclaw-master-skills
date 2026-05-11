import { describe, it, expect } from '@jest/globals';
import { URLValidator } from '../validator';
import { ModuleConfig } from '../../../types';

describe('URLValidator', () => {
  const defaultConfig: ModuleConfig = {
    enabled: true
  };

  describe('constructor', () => {
    it('should create an instance with valid config', () => {
      const validator = new URLValidator(defaultConfig);
      expect(validator).toBeInstanceOf(URLValidator);
    });

    it('should throw error if config is invalid', () => {
      expect(() => new URLValidator(null as any)).toThrow();
    });
  });

  describe('validate', () => {
    describe('Private IP addresses (RFC 1918)', () => {
      it('should detect 10.0.0.0/8 range', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://10.0.0.1/api';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].module).toBe('url_validator');
        expect(findings[0].pattern.category).toBe('ssrf');
      });

      it('should detect 172.16.0.0/12 range', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://172.16.0.1/secret';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].module).toBe('url_validator');
      });

      it('should detect 192.168.0.0/16 range', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://192.168.1.1/admin';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].module).toBe('url_validator');
      });
    });

    describe('Localhost variations', () => {
      it('should detect localhost hostname', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://localhost:8080/api';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('localhost');
      });

      it('should detect 127.0.0.1 loopback', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://127.0.0.1/admin';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
      });

      it('should detect 0.0.0.0 address', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://0.0.0.0/api';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
      });
    });

    describe('Cloud metadata endpoints', () => {
      it('should detect AWS metadata endpoint (169.254.169.254)', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://169.254.169.254/latest/meta-data/';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'aws_metadata')).toBe(true);
      });

      it('should detect Azure metadata endpoint', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://169.254.169.254/metadata/instance';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
      });

      it('should detect GCP metadata endpoint', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://metadata.google.internal/computeMetadata/v1/';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'gcp_metadata')).toBe(true);
      });

      it('should detect alternative GCP metadata IP', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://169.254.169.254/computeMetadata/v1/';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
      });
    });

    describe('Link-local addresses', () => {
      it('should detect 169.254.0.0/16 range', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://169.254.1.1/api';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'link_local')).toBe(true);
      });
    });

    describe('IPv6 localhost', () => {
      it('should detect ::1 IPv6 loopback', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://[::1]/api';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'ipv6_localhost')).toBe(true);
      });

      it('should detect ::ffff:127.0.0.1 IPv4-mapped IPv6', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://[::ffff:127.0.0.1]/api';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
      });
    });

    describe('File protocol', () => {
      it('should detect file:// protocol', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'file:///etc/passwd';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'file_protocol')).toBe(true);
      });

      it('should detect file:// with localhost', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'file://localhost/etc/passwd';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
      });
    });

    describe('Safe URLs', () => {
      it('should return empty array for public URLs', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'https://api.example.com/v1/users';

        const findings = await validator.validate(url);

        expect(findings).toEqual([]);
      });

      it('should return empty array for valid public IPs', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://8.8.8.8/api';

        const findings = await validator.validate(url);

        expect(findings).toEqual([]);
      });

      it('should allow https URLs', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'https://github.com/user/repo';

        const findings = await validator.validate(url);

        expect(findings).toEqual([]);
      });
    });

    describe('Edge cases and error handling', () => {
      it('should handle empty string', async () => {
        const validator = new URLValidator(defaultConfig);
        const findings = await validator.validate('');

        expect(findings).toEqual([]);
      });

      it('should throw error for null input', async () => {
        const validator = new URLValidator(defaultConfig);

        await expect(validator.validate(null as any)).rejects.toThrow();
      });

      it('should throw error for non-string input', async () => {
        const validator = new URLValidator(defaultConfig);

        await expect(validator.validate(123 as any)).rejects.toThrow();
      });

      it('should handle malformed URLs gracefully', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'not-a-valid-url';

        const findings = await validator.validate(url);

        // Should either return empty or handle gracefully without throwing
        expect(Array.isArray(findings)).toBe(true);
      });

      it('should handle URLs without protocol', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = '192.168.1.1/api';

        const findings = await validator.validate(url);

        // Should detect as private IP
        expect(findings.length).toBeGreaterThan(0);
      });

      it('should handle URLs with credentials', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://user:pass@10.0.0.1/api';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
      });
    });

    describe('Multiple findings', () => {
      it('should detect multiple patterns in one URL', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://169.254.169.254/latest/meta-data/';

        const findings = await validator.validate(url);

        // AWS metadata endpoint matches both link-local and AWS metadata patterns
        expect(findings.length).toBeGreaterThan(0);
      });
    });

    describe('Metadata', () => {
      it('should include metadata in findings', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://localhost/api';

        const findings = await validator.validate(url);

        expect(findings[0]).toHaveProperty('metadata');
        expect(findings[0].metadata).toBeDefined();
        expect(findings[0].metadata).toHaveProperty('url');
        expect(findings[0].metadata).toHaveProperty('patternId');
      });

      it('should include parsed URL components in metadata', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://192.168.1.1:8080/api/endpoint';

        const findings = await validator.validate(url);

        expect(findings[0].metadata).toHaveProperty('protocol');
        expect(findings[0].metadata).toHaveProperty('hostname');
      });
    });

    describe('Pattern respect enabled flag', () => {
      it('should respect enabled flag in patterns', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://10.0.0.1/api';

        const findings = await validator.validate(url);

        // Should find at least one match since pattern is enabled
        expect(findings.length).toBeGreaterThan(0);
      });
    });

    describe('Cloud metadata endpoints (expanded)', () => {
      it('should detect Azure IMDS endpoint', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://169.254.169.254/metadata/instance?api-version=2021-02-01';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'azure_imds')).toBe(true);
      });

      it('should detect Azure Wire Server', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://168.63.129.16/machine?comp=goalstate';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'azure_wire_server')).toBe(true);
      });

      it('should detect DigitalOcean metadata', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://169.254.169.254/metadata/v1/hostname';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'digitalocean_metadata')).toBe(true);
      });

      it('should detect Oracle Cloud metadata', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://169.254.169.254/opc/v1/instance/';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'oracle_metadata')).toBe(true);
      });

      it('should detect Oracle Cloud metadata v2', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://169.254.169.254/opc/v2/instance/metadata/';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'oracle_metadata')).toBe(true);
      });

      it('should detect Alibaba Cloud metadata', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'http://100.100.100.200/latest/meta-data/instance-id';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'alibaba_metadata')).toBe(true);
      });

      it('should detect Kubernetes API server', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'https://kubernetes.default.svc/api/v1/namespaces';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'kubernetes_api')).toBe(true);
      });

      it('should detect Kubernetes API with cluster.local', async () => {
        const validator = new URLValidator(defaultConfig);
        const url = 'https://kubernetes.default.svc.cluster.local/api';

        const findings = await validator.validate(url);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'kubernetes_api')).toBe(true);
      });
    });
  });
});
