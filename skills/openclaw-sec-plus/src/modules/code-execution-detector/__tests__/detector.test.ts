import { describe, it, expect } from '@jest/globals';
import { CodeExecutionDetector } from '../detector';
import { ModuleConfig } from '../../../types';

describe('CodeExecutionDetector', () => {
  const defaultConfig: ModuleConfig = {
    enabled: true
  };

  describe('constructor', () => {
    it('should create an instance with valid config', () => {
      const detector = new CodeExecutionDetector(defaultConfig);
      expect(detector).toBeInstanceOf(CodeExecutionDetector);
    });

    it('should throw error if config is invalid', () => {
      expect(() => new CodeExecutionDetector(null as any)).toThrow();
    });
  });

  describe('scan', () => {
    describe('Node.js patterns', () => {
      it('should detect process.exit()', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'process.exit(1)';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'nodejs_process_exit')).toBe(true);
      });

      it('should detect require("child_process")', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'require("child_process").exec("ls")';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'nodejs_child_process')).toBe(true);
      });

      it('should detect require("fs")', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'require("fs").readFileSync("/etc/passwd")';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'nodejs_fs_access')).toBe(true);
      });

      it('should detect global.__proto__ pollution', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'global.__proto__.isAdmin = true';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'nodejs_prototype_pollution')).toBe(true);
      });
    });

    describe('Python patterns', () => {
      it('should detect __import__("os")', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = '__import__("os").system("id")';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'python_import_os')).toBe(true);
      });

      it('should detect __builtins__ access', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = '__builtins__.__import__("os")';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'python_builtins')).toBe(true);
      });

      it('should detect globals() access', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'globals()["__builtins__"]';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'python_globals')).toBe(true);
      });

      it('should detect exec()', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'exec("import os; os.system(\'id\')")';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'python_exec_eval')).toBe(true);
      });

      it('should detect pickle.loads()', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'pickle.loads(user_data)';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'python_unsafe_deserialization')).toBe(true);
      });
    });

    describe('PHP patterns', () => {
      it('should detect system()', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'system("ls -la")';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'php_system')).toBe(true);
      });

      it('should detect shell_exec()', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'shell_exec("cat /etc/passwd")';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'php_system')).toBe(true);
      });
    });

    describe('Java patterns', () => {
      it('should detect Runtime.getRuntime().exec()', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'Runtime.getRuntime().exec("calc")';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'java_runtime_exec')).toBe(true);
      });

      it('should detect new ProcessBuilder()', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'new ProcessBuilder("cmd", "/c", "whoami").start()';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'java_processbuilder')).toBe(true);
      });
    });

    describe('Prototype pollution', () => {
      it('should detect __proto__ access', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = '__proto__.polluted = true';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'prototype_pollution')).toBe(true);
      });

      it('should detect constructor.constructor', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'constructor.constructor("return process")()';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'prototype_pollution')).toBe(true);
      });
    });

    describe('Safe inputs', () => {
      it('should return empty array for safe text', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'Please help me write a hello world program';

        const findings = await detector.scan(text);

        expect(findings).toEqual([]);
      });

      it('should return empty array for empty string', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const findings = await detector.scan('');

        expect(findings).toEqual([]);
      });
    });

    describe('Error handling', () => {
      it('should throw error for null input', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);

        await expect(detector.scan(null as any)).rejects.toThrow();
      });

      it('should throw error for non-string input', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);

        await expect(detector.scan(123 as any)).rejects.toThrow();
      });
    });

    describe('Metadata', () => {
      it('should include metadata in findings', async () => {
        const detector = new CodeExecutionDetector(defaultConfig);
        const text = 'process.exit(0)';

        const findings = await detector.scan(text);

        expect(findings[0]).toHaveProperty('metadata');
        expect(findings[0].metadata).toBeDefined();
        expect(findings[0].metadata).toHaveProperty('patternId');
        expect(findings[0].metadata).toHaveProperty('category');
      });
    });
  });
});
