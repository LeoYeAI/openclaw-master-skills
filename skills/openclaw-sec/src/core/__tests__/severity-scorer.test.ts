import { SeverityScorer } from '../severity-scorer';
import { Severity, Finding, SecurityPattern } from '../../types';

describe('SeverityScorer', () => {
  const createMockPattern = (severity: Severity): SecurityPattern => ({
    id: 'test-pattern',
    category: 'test',
    pattern: /test/,
    severity,
    language: 'en',
    description: 'Test pattern',
    examples: [],
    falsePositiveRisk: 'low',
    enabled: true,
    tags: []
  });

  const createMockFinding = (module: string, severity: Severity): Finding => ({
    module,
    pattern: createMockPattern(severity),
    matchedText: 'test',
    severity
  });

  describe('constructor', () => {
    it('should create instance successfully', () => {
      const scorer = new SeverityScorer();
      expect(scorer).toBeInstanceOf(SeverityScorer);
    });
  });

  describe('calculateSeverity', () => {
    it('should return SAFE for empty findings', () => {
      const scorer = new SeverityScorer();
      const result = scorer.calculateSeverity([]);

      expect(result.severity).toBe(Severity.SAFE);
      expect(result.reasoning).toContain('No security findings detected');
      expect(result.findingCount).toBe(0);
      expect(result.modulesConcerned).toEqual([]);
    });

    it('should return highest severity when multiple findings exist', () => {
      const scorer = new SeverityScorer();
      const findings: Finding[] = [
        createMockFinding('prompt_injection', Severity.LOW),
        createMockFinding('command_validator', Severity.CRITICAL),
        createMockFinding('url_validator', Severity.MEDIUM)
      ];

      const result = scorer.calculateSeverity(findings);

      expect(result.severity).toBe(Severity.CRITICAL);
      expect(result.reasoning).toContain('CRITICAL');
      expect(result.findingCount).toBe(3);
      expect(result.modulesConcerned).toContain('command_validator');
    });

    it('should handle single finding', () => {
      const scorer = new SeverityScorer();
      const findings: Finding[] = [
        createMockFinding('prompt_injection', Severity.HIGH)
      ];

      const result = scorer.calculateSeverity(findings);

      expect(result.severity).toBe(Severity.HIGH);
      expect(result.findingCount).toBe(1);
      expect(result.modulesConcerned).toEqual(['prompt_injection']);
    });

    it('should identify all concerned modules', () => {
      const scorer = new SeverityScorer();
      const findings: Finding[] = [
        createMockFinding('prompt_injection', Severity.LOW),
        createMockFinding('command_validator', Severity.MEDIUM),
        createMockFinding('url_validator', Severity.LOW),
        createMockFinding('command_validator', Severity.HIGH) // duplicate module
      ];

      const result = scorer.calculateSeverity(findings);

      expect(result.modulesConcerned).toHaveLength(3);
      expect(result.modulesConcerned).toContain('prompt_injection');
      expect(result.modulesConcerned).toContain('command_validator');
      expect(result.modulesConcerned).toContain('url_validator');
    });

    it('should correctly order severity levels (CRITICAL > HIGH > MEDIUM > LOW > SAFE)', () => {
      const scorer = new SeverityScorer();

      const testCases = [
        { findings: [Severity.LOW, Severity.MEDIUM], expected: Severity.MEDIUM },
        { findings: [Severity.MEDIUM, Severity.HIGH], expected: Severity.HIGH },
        { findings: [Severity.HIGH, Severity.CRITICAL], expected: Severity.CRITICAL },
        { findings: [Severity.LOW, Severity.HIGH, Severity.MEDIUM], expected: Severity.HIGH }
      ];

      testCases.forEach(({ findings, expected }) => {
        const mockFindings = findings.map((sev, idx) =>
          createMockFinding(`module_${idx}`, sev)
        );
        const result = scorer.calculateSeverity(mockFindings);
        expect(result.severity).toBe(expected);
      });
    });

    it('should provide detailed reasoning for multiple modules', () => {
      const scorer = new SeverityScorer();
      const findings: Finding[] = [
        createMockFinding('prompt_injection', Severity.HIGH),
        createMockFinding('command_validator', Severity.MEDIUM)
      ];

      const result = scorer.calculateSeverity(findings);

      expect(result.reasoning).toContain('HIGH');
      expect(result.reasoning).toContain('2 findings');
      expect(result.reasoning).toContain('2 modules');
    });

    it('should handle all severity levels correctly', () => {
      const scorer = new SeverityScorer();
      const severities = [Severity.SAFE, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL];

      severities.forEach(severity => {
        const findings: Finding[] = [createMockFinding('test_module', severity)];
        const result = scorer.calculateSeverity(findings);
        expect(result.severity).toBe(severity);
      });
    });

    it('should include severity breakdown in metadata', () => {
      const scorer = new SeverityScorer();
      const findings: Finding[] = [
        createMockFinding('module1', Severity.LOW),
        createMockFinding('module2', Severity.LOW),
        createMockFinding('module3', Severity.HIGH),
        createMockFinding('module4', Severity.CRITICAL)
      ];

      const result = scorer.calculateSeverity(findings);

      expect(result.severityBreakdown).toBeDefined();
      expect(result.severityBreakdown![Severity.LOW]).toBe(2);
      expect(result.severityBreakdown![Severity.HIGH]).toBe(1);
      expect(result.severityBreakdown![Severity.CRITICAL]).toBe(1);
    });

    it('should throw error for null findings', () => {
      const scorer = new SeverityScorer();
      expect(() => scorer.calculateSeverity(null as any)).toThrow('Findings must be an array');
    });

    it('should throw error for undefined findings', () => {
      const scorer = new SeverityScorer();
      expect(() => scorer.calculateSeverity(undefined as any)).toThrow('Findings must be an array');
    });

    it('should throw error for non-array findings', () => {
      const scorer = new SeverityScorer();
      expect(() => scorer.calculateSeverity('invalid' as any)).toThrow('Findings must be an array');
    });
  });

  describe('edge cases', () => {
    it('should handle findings with metadata', () => {
      const scorer = new SeverityScorer();
      const finding: Finding = {
        ...createMockFinding('test_module', Severity.MEDIUM),
        metadata: { customField: 'value', position: 10 }
      };

      const result = scorer.calculateSeverity([finding]);

      expect(result.severity).toBe(Severity.MEDIUM);
      expect(result.findingCount).toBe(1);
    });

    it('should handle multiple findings from same module', () => {
      const scorer = new SeverityScorer();
      const findings: Finding[] = [
        createMockFinding('prompt_injection', Severity.LOW),
        createMockFinding('prompt_injection', Severity.MEDIUM),
        createMockFinding('prompt_injection', Severity.HIGH)
      ];

      const result = scorer.calculateSeverity(findings);

      expect(result.severity).toBe(Severity.HIGH);
      expect(result.findingCount).toBe(3);
      expect(result.modulesConcerned).toEqual(['prompt_injection']);
    });

    it('should handle large number of findings', () => {
      const scorer = new SeverityScorer();
      const findings: Finding[] = Array(1000).fill(null).map((_, idx) =>
        createMockFinding(`module_${idx % 6}`, Severity.LOW)
      );

      const result = scorer.calculateSeverity(findings);

      expect(result.severity).toBe(Severity.LOW);
      expect(result.findingCount).toBe(1000);
      expect(result.modulesConcerned.length).toBeLessThanOrEqual(6);
    });
  });

  describe('severity ordering', () => {
    it('should use correct severity weight hierarchy', () => {
      const scorer = new SeverityScorer();

      // Test all combinations to ensure proper ordering
      const allSeverities = [Severity.SAFE, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL];

      for (let i = 0; i < allSeverities.length; i++) {
        for (let j = i + 1; j < allSeverities.length; j++) {
          const findings = [
            createMockFinding('module1', allSeverities[i]),
            createMockFinding('module2', allSeverities[j])
          ];
          const result = scorer.calculateSeverity(findings);

          // Higher index should always win
          expect(result.severity).toBe(allSeverities[j]);
        }
      }
    });
  });
});
