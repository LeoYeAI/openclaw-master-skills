import { describe, it, expect } from '@jest/globals';
import { InjectionValidator } from '../validator';
import { ModuleConfig } from '../../../types';

describe('InjectionValidator', () => {
  const defaultConfig: ModuleConfig = {
    enabled: true
  };

  describe('constructor', () => {
    it('should create an instance with valid config', () => {
      const validator = new InjectionValidator(defaultConfig);
      expect(validator).toBeInstanceOf(InjectionValidator);
    });

    it('should throw error if config is invalid', () => {
      expect(() => new InjectionValidator(null as any)).toThrow();
    });
  });

  describe('validate', () => {
    describe('SQL Injection', () => {
      it('should detect UNION SELECT', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = "' UNION SELECT username, password FROM users --";

        const findings = await validator.validate(input);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].module).toBe('injection_validator');
        expect(findings.some(f => f.pattern.subcategory === 'sql_union_select')).toBe(true);
      });

      it('should detect boolean-blind injection', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = "' OR 1=1 --";

        const findings = await validator.validate(input);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'sql_boolean_blind')).toBe(true);
      });

      it('should detect stacked queries', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = "'; DROP TABLE users; --";

        const findings = await validator.validate(input);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'sql_stacked_queries')).toBe(true);
      });

      it('should detect comment-based termination', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = "admin'--";

        const findings = await validator.validate(input);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'sql_comment_based')).toBe(true);
      });
    });

    describe('NoSQL Injection', () => {
      it('should detect MongoDB operators', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = '{"username": {"$ne": ""}}';

        const findings = await validator.validate(input);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'nosql_mongodb_operators')).toBe(true);
      });

      it('should detect $where JavaScript injection', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = '{"$where": "function() { return true; }"}';

        const findings = await validator.validate(input);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'nosql_where')).toBe(true);
      });
    });

    describe('LDAP Injection', () => {
      it('should detect LDAP filter injection', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = '(|(uid=*))';

        const findings = await validator.validate(input);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'ldap_filter')).toBe(true);
      });
    });

    describe('XPath Injection', () => {
      it('should detect XPath injection', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = "' or 1=1 or 'a'='a";

        const findings = await validator.validate(input);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'xpath_injection')).toBe(true);
      });
    });

    describe('SSTI', () => {
      it('should detect Jinja2 SSTI', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = '{{config}}';

        const findings = await validator.validate(input);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'ssti_jinja2')).toBe(true);
      });

      it('should detect Expression Language SSTI', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = '${Runtime.getRuntime().exec("id")}';

        const findings = await validator.validate(input);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'ssti_expression_language')).toBe(true);
      });

      it('should detect Python dunder introspection', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = "''.__class__.__mro__[1].__subclasses__()";

        const findings = await validator.validate(input);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'ssti_python_dunder')).toBe(true);
      });
    });

    describe('Safe inputs', () => {
      it('should return empty array for safe text', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = 'This is a normal search query about databases';

        const findings = await validator.validate(input);

        expect(findings).toEqual([]);
      });

      it('should return empty array for empty string', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const findings = await validator.validate('');

        expect(findings).toEqual([]);
      });
    });

    describe('Error handling', () => {
      it('should throw error for null input', async () => {
        const validator = new InjectionValidator(defaultConfig);

        await expect(validator.validate(null as any)).rejects.toThrow();
      });

      it('should throw error for non-string input', async () => {
        const validator = new InjectionValidator(defaultConfig);

        await expect(validator.validate(123 as any)).rejects.toThrow();
      });
    });

    describe('Metadata', () => {
      it('should include metadata in findings', async () => {
        const validator = new InjectionValidator(defaultConfig);
        const input = "' UNION SELECT * FROM users --";

        const findings = await validator.validate(input);

        expect(findings[0]).toHaveProperty('metadata');
        expect(findings[0].metadata).toBeDefined();
        expect(findings[0].metadata).toHaveProperty('patternId');
        expect(findings[0].metadata).toHaveProperty('category');
      });
    });
  });
});
