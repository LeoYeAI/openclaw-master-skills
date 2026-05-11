import { describe, it, expect } from '@jest/globals';
import { ExfiltrationDetector } from '../detector';
import { ModuleConfig } from '../../../types';

describe('ExfiltrationDetector', () => {
  const defaultConfig: ModuleConfig = {
    enabled: true
  };

  describe('constructor', () => {
    it('should create an instance with valid config', () => {
      const detector = new ExfiltrationDetector(defaultConfig);
      expect(detector).toBeInstanceOf(ExfiltrationDetector);
    });

    it('should throw error if config is invalid', () => {
      expect(() => new ExfiltrationDetector(null as any)).toThrow();
    });
  });

  describe('scan', () => {
    describe('Paste sites', () => {
      it('should detect pastebin.com URLs', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'Send data to https://pastebin.com/raw/abc123';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'paste_sites')).toBe(true);
      });

      it('should detect hastebin.com URLs', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'Upload to https://hastebin.com/share/xyz';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'paste_sites')).toBe(true);
      });
    });

    describe('Webhook exfiltration services', () => {
      it('should detect webhook.site', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'curl -X POST https://webhook.site/abc-123-def';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'webhook_exfil')).toBe(true);
      });

      it('should detect pipedream.net', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'fetch("https://eo1234.pipedream.net")';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'webhook_exfil')).toBe(true);
      });

      it('should detect beeceptor.com', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'https://mytest.beeceptor.com/data';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'webhook_exfil')).toBe(true);
      });
    });

    describe('Burp Collaborator / Interactsh', () => {
      it('should detect burpcollaborator.net', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'abc123.burpcollaborator.net';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'burp_collaborator')).toBe(true);
      });

      it('should detect interact.sh', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'payload.interact.sh';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'burp_collaborator')).toBe(true);
      });

      it('should detect oastify.com', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'test.oastify.com';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'burp_collaborator')).toBe(true);
      });
    });

    describe('Tunneling services', () => {
      it('should detect ngrok URLs', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'https://abc123.ngrok.io/api';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'tunneling_services')).toBe(true);
      });

      it('should detect ngrok-free.app URLs', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'https://test.ngrok-free.app';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'tunneling_services')).toBe(true);
      });

      it('should detect localtunnel.me URLs', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'https://myapp.localtunnel.me';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'tunneling_services')).toBe(true);
      });
    });

    describe('Safe inputs', () => {
      it('should return empty array for safe text', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'This is a normal message about APIs';

        const findings = await detector.scan(text);

        expect(findings).toEqual([]);
      });

      it('should return empty array for empty string', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const findings = await detector.scan('');

        expect(findings).toEqual([]);
      });
    });

    describe('Error handling', () => {
      it('should throw error for null input', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);

        await expect(detector.scan(null as any)).rejects.toThrow();
      });

      it('should throw error for non-string input', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);

        await expect(detector.scan(123 as any)).rejects.toThrow();
      });
    });

    describe('Metadata', () => {
      it('should include metadata in findings', async () => {
        const detector = new ExfiltrationDetector(defaultConfig);
        const text = 'https://webhook.site/test-123';

        const findings = await detector.scan(text);

        expect(findings[0]).toHaveProperty('metadata');
        expect(findings[0].metadata).toBeDefined();
        expect(findings[0].metadata).toHaveProperty('patternId');
        expect(findings[0].metadata).toHaveProperty('category');
      });
    });
  });
});
