import { describe, it, expect } from '@jest/globals';
import { SecretDetector } from '../detector';
import { ModuleConfig } from '../../../types';

describe('SecretDetector', () => {
  const defaultConfig: ModuleConfig = {
    enabled: true
  };

  describe('constructor', () => {
    it('should create an instance with valid config', () => {
      const detector = new SecretDetector(defaultConfig);
      expect(detector).toBeInstanceOf(SecretDetector);
    });

    it('should throw error if config is invalid', () => {
      expect(() => new SecretDetector(null as any)).toThrow();
    });
  });

  describe('scan', () => {
    describe('Anthropic API keys', () => {
      it('should detect Anthropic API key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'sk-ant-api03-' + 'x'.repeat(95);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].module).toBe('secret_detector');
        expect(findings[0].pattern.subcategory).toBe('anthropic_api_key');
        expect(findings[0].severity).toBe('CRITICAL');
      });

      it('should redact the API key in findings', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'sk-ant-api03-' + 'a'.repeat(95);

        const findings = await detector.scan(text);

        expect(findings[0].matchedText).not.toContain('aaaaaaa');
        expect(findings[0].matchedText).toContain('****');
        expect(findings[0].metadata!.redacted).toBe(true);
      });
    });

    describe('OpenAI API keys', () => {
      it('should detect OpenAI API key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'sk-' + 'x'.repeat(48);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'openai_api_key')).toBe(true);
      });

      it('should detect OpenAI key in code', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'const apiKey = "sk-' + 'A'.repeat(48) + '";';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
      });
    });

    describe('GitHub tokens', () => {
      it('should detect GitHub personal access token (ghp_)', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'ghp_' + 'x'.repeat(36);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('github_token');
        expect(findings[0].severity).toBe('CRITICAL');
      });

      it('should detect GitHub OAuth token (gho_)', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'gho_' + 'x'.repeat(36);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'github_oauth')).toBe(true);
      });

      it('should detect GitHub user token (ghu_)', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'ghu_' + 'x'.repeat(36);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'github_token')).toBe(true);
      });
    });

    describe('AWS credentials', () => {
      it('should detect AWS access key ID (AKIA)', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'AKIAIOSFODNN7EXAMPLE';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('aws_access_key');
        expect(findings[0].severity).toBe('CRITICAL');
      });

      it('should detect AWS access key ID (ASIA)', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'ASIATESTACCESSKEYID1';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'aws_access_key')).toBe(true);
      });

      it('should detect AWS secret access key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'aws_secret_key')).toBe(true);
      });
    });

    describe('Google API keys', () => {
      it('should detect Google API key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'AIzaSy' + 'x'.repeat(33);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('google_api_key');
        expect(findings[0].severity).toBe('CRITICAL');
      });

      it('should detect Google OAuth token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'ya29.' + 'x'.repeat(50);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('google_oauth');
      });
    });

    describe('Slack tokens', () => {
      it('should detect Slack bot token (xoxb)', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'xoxb-REDACTED-TEST-TOKEN';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('slack_token');
        expect(findings[0].severity).toBe('CRITICAL');
      });

      it('should detect Slack app token (xoxa)', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'xoxa-REDACTED-TEST-TOKEN-2';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'slack_token')).toBe(true);
      });

      it('should detect Slack webhook URL', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'https://hooks.slack.com/services/TFAKETEST1/BFAKETEST2/FAKE3EXAMPLE4TESTING56789';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'slack_webhook')).toBe(true);
      });
    });

    describe('Stripe API keys', () => {
      it('should detect Stripe live secret key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'sk_live_' + 'x'.repeat(24);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('stripe_api_key');
        expect(findings[0].severity).toBe('CRITICAL');
      });

      it('should detect Stripe test publishable key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'pk_test_' + 'x'.repeat(24);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'stripe_api_key')).toBe(true);
      });
    });

    describe('Other service tokens', () => {
      it('should detect Twilio API key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'SK' + 'x'.repeat(32);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'twilio_api_key')).toBe(true);
      });

      it('should detect SendGrid API key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'SG.' + 'x'.repeat(22) + '.' + 'y'.repeat(43);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'sendgrid_api_key')).toBe(true);
      });

      it('should detect Mailgun API key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'key-' + 'x'.repeat(32);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'mailgun_api_key')).toBe(true);
      });

      it('should detect Discord bot token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'N' + 'x'.repeat(23) + '.' + 'y'.repeat(6) + '.' + 'z'.repeat(27);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'discord_token')).toBe(true);
      });

      it('should detect NPM token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'npm_' + 'x'.repeat(36);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'npm_token')).toBe(true);
      });

      it('should detect GitLab personal access token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'glpat-' + 'x'.repeat(20);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'gitlab_token')).toBe(true);
      });

      it('should detect PyPI token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'pypi-AgEIcHlwaS5vcmc' + 'x'.repeat(50);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'pypi_token')).toBe(true);
      });
    });

    describe('JWT tokens', () => {
      it('should detect JWT token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('jwt_token');
      });

      it('should detect JWT in Authorization header', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.xyz123';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'jwt_token')).toBe(true);
      });
    });

    describe('Private keys', () => {
      it('should detect RSA private key header', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = '-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('private_key');
        expect(findings[0].severity).toBe('CRITICAL');
      });

      it('should detect generic PRIVATE KEY header', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = '-----BEGIN PRIVATE KEY-----';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'private_key')).toBe(true);
      });

      it('should detect EC private key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = '-----BEGIN EC PRIVATE KEY-----';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'private_key')).toBe(true);
      });
    });

    describe('Generic secrets', () => {
      it('should detect generic API key assignment', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'api_key = "abcdefghijklmnopqrstuvwxyz"';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'generic_api_key')).toBe(true);
      });

      it('should detect apiKey with colon', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'apiKey: "super_secret_key_12345678"';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'generic_api_key')).toBe(true);
      });

      it('should detect password assignment', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'password = "MySecretPassword123"';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'generic_password')).toBe(true);
      });
    });

    describe('Multiple secrets in text', () => {
      it('should detect multiple secrets in the same text', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = `
          const openaiKey = "sk-${'x'.repeat(48)}";
          const githubToken = "ghp_${'y'.repeat(36)}";
          const awsKey = "AKIAIOSFODNN7EXAMPLE";
        `;

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(2);
        expect(findings.some(f => f.pattern.subcategory === 'openai_api_key')).toBe(true);
        expect(findings.some(f => f.pattern.subcategory === 'github_token')).toBe(true);
        expect(findings.some(f => f.pattern.subcategory === 'aws_access_key')).toBe(true);
      });

      it('should find all occurrences of the same pattern', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'API_KEY_1="ghp_' + 'a'.repeat(36) + '" API_KEY_2="ghp_' + 'b'.repeat(36) + '"';

        const findings = await detector.scan(text);

        expect(findings.filter(f => f.pattern.subcategory === 'github_token').length).toBeGreaterThanOrEqual(2);
      });
    });

    describe('Safe text', () => {
      it('should return empty array for text without secrets', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'This is a normal string without any API keys or secrets.';

        const findings = await detector.scan(text);

        expect(findings).toEqual([]);
      });

      it('should return empty array for placeholder values', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'api_key = "your-api-key-here"';

        const findings = await detector.scan(text);

        expect(findings).toEqual([]);
      });
    });

    describe('Edge cases and error handling', () => {
      it('should handle empty string', async () => {
        const detector = new SecretDetector(defaultConfig);
        const findings = await detector.scan('');

        expect(findings).toEqual([]);
      });

      it('should throw error for null input', async () => {
        const detector = new SecretDetector(defaultConfig);

        await expect(detector.scan(null as any)).rejects.toThrow();
      });

      it('should throw error for non-string input', async () => {
        const detector = new SecretDetector(defaultConfig);

        await expect(detector.scan(123 as any)).rejects.toThrow();
      });

      it('should handle very long text', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'a'.repeat(10000) + 'ghp_' + 'x'.repeat(36) + 'b'.repeat(10000);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
      });

      it('should handle text with newlines', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'Line 1\nLine 2 with ghp_' + 'x'.repeat(36) + '\nLine 3';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
      });
    });

    describe('Metadata', () => {
      it('should include metadata in findings', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'ghp_' + 'x'.repeat(36);

        const findings = await detector.scan(text);

        expect(findings[0]).toHaveProperty('metadata');
        expect(findings[0].metadata).toBeDefined();
        expect(findings[0].metadata).toHaveProperty('position');
        expect(findings[0].metadata).toHaveProperty('patternId');
        expect(findings[0].metadata).toHaveProperty('secretLength');
        expect(findings[0].metadata).toHaveProperty('redacted');
      });

      it('should include correct position in metadata', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'Some text ghp_' + 'x'.repeat(36) + ' more text';

        const findings = await detector.scan(text);

        expect(findings[0].metadata!.position).toBe(10);
      });

      it('should mark secrets as redacted', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'ghp_' + 'x'.repeat(36);

        const findings = await detector.scan(text);

        expect(findings[0].metadata!.redacted).toBe(true);
      });
    });

    describe('Secret redaction', () => {
      it('should show only partial secret in findings', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'ghp_' + 'x'.repeat(36);

        const findings = await detector.scan(text);

        const matchedText = findings[0].matchedText;
        expect(matchedText).toContain('ghp_');
        expect(matchedText).toContain('****');
        expect(matchedText.length).toBeLessThan(text.length);
      });

      it('should redact short secrets completely', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'password = "short"';

        const findings = await detector.scan(text);

        if (findings.length > 0) {
          expect(findings[0].matchedText).toBe('***REDACTED***');
        }
      });
    });

    describe('New service tokens (expanded)', () => {
      it('should detect Supabase key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'sbp_' + 'a'.repeat(40);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'supabase_key')).toBe(true);
      });

      it('should detect Vercel token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'vc_' + 'x'.repeat(24);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'vercel_token')).toBe(true);
      });

      it('should detect Cloudflare token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'cf_' + 'x'.repeat(40);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'cloudflare_api_token')).toBe(true);
      });

      it('should detect Azure connection string', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=abc123==;EndpointSuffix=core.windows.net';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'azure_connection_string')).toBe(true);
      });

      it('should detect Databricks token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'dapi' + 'a'.repeat(32);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'databricks_token')).toBe(true);
      });

      it('should detect HuggingFace token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'hf_' + 'x'.repeat(34);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'huggingface_token')).toBe(true);
      });

      it('should detect Replicate token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'r8_' + 'x'.repeat(36);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'replicate_token')).toBe(true);
      });

      it('should detect PlanetScale token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'pscale_tkn_' + 'x'.repeat(32);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'planetscale_token')).toBe(true);
      });

      it('should detect Linear API key', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'lin_api_' + 'x'.repeat(32);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'linear_api_key')).toBe(true);
      });

      it('should detect Grafana Cloud token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'glc_' + 'x'.repeat(32);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'grafana_cloud_token')).toBe(true);
      });

      it('should detect HashiCorp Vault token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'hvs.' + 'x'.repeat(24);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'hashicorp_vault_token')).toBe(true);
      });

      it('should detect Doppler token', async () => {
        const detector = new SecretDetector(defaultConfig);
        const text = 'dp.st.' + 'x'.repeat(40);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'doppler_token')).toBe(true);
      });

      it('should not detect disabled Firebase key', async () => {
        const detector = new SecretDetector(defaultConfig);
        // Firebase pattern is disabled but matches Google API key pattern (which is enabled)
        const text = 'AIzaSy' + 'x'.repeat(33);

        const findings = await detector.scan(text);

        // Should be detected by existing google_api_key pattern, not firebase_key
        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'google_api_key')).toBe(true);
        expect(findings.every(f => f.pattern.subcategory !== 'firebase_key')).toBe(true);
      });
    });
  });
});
