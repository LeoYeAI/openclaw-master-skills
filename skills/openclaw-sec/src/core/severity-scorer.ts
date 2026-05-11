import { Severity, Finding } from '../types';

/**
 * Result of severity calculation
 */
export interface SeverityResult {
  severity: Severity;
  reasoning: string;
  findingCount: number;
  modulesConcerned: string[];
  severityBreakdown?: Record<Severity, number>;
}

/**
 * SeverityScorer aggregates findings from all detection modules and calculates
 * the final severity level.
 *
 * Strategy: Highest severity wins (most conservative approach)
 *
 * @example
 * ```typescript
 * const scorer = new SeverityScorer();
 * const result = scorer.calculateSeverity(findings);
 * console.log(result.severity); // CRITICAL
 * console.log(result.reasoning); // "Overall severity: CRITICAL (3 findings across 2 modules)"
 * ```
 */
export class SeverityScorer {
  private readonly severityWeight: Record<Severity, number> = {
    [Severity.SAFE]: 0,
    [Severity.LOW]: 1,
    [Severity.MEDIUM]: 2,
    [Severity.HIGH]: 3,
    [Severity.CRITICAL]: 4
  };

  /**
   * Calculate the overall severity from multiple findings
   *
   * @param findings - Array of findings from detection modules
   * @returns SeverityResult with calculated severity and analysis
   * @throws Error if findings is not an array
   */
  calculateSeverity(findings: Finding[]): SeverityResult {
    // Validate input
    if (!Array.isArray(findings)) {
      throw new Error('Findings must be an array');
    }

    // Handle empty findings
    if (findings.length === 0) {
      return {
        severity: Severity.SAFE,
        reasoning: 'No security findings detected. Input appears safe.',
        findingCount: 0,
        modulesConcerned: [],
        severityBreakdown: {
          [Severity.SAFE]: 0,
          [Severity.LOW]: 0,
          [Severity.MEDIUM]: 0,
          [Severity.HIGH]: 0,
          [Severity.CRITICAL]: 0
        }
      };
    }

    // Calculate highest severity (most conservative approach)
    let highestSeverity = Severity.SAFE;
    let highestWeight = 0;

    // Track modules and severity breakdown
    const moduleSet = new Set<string>();
    const severityBreakdown: Record<Severity, number> = {
      [Severity.SAFE]: 0,
      [Severity.LOW]: 0,
      [Severity.MEDIUM]: 0,
      [Severity.HIGH]: 0,
      [Severity.CRITICAL]: 0
    };

    for (const finding of findings) {
      const weight = this.severityWeight[finding.severity];

      // Update severity breakdown
      severityBreakdown[finding.severity]++;

      // Track module
      moduleSet.add(finding.module);

      // Update highest severity
      if (weight > highestWeight) {
        highestWeight = weight;
        highestSeverity = finding.severity;
      }
    }

    const modulesConcerned = Array.from(moduleSet);

    // Build reasoning
    const reasoning = this.buildReasoning(
      highestSeverity,
      findings.length,
      modulesConcerned.length,
      severityBreakdown
    );

    return {
      severity: highestSeverity,
      reasoning,
      findingCount: findings.length,
      modulesConcerned,
      severityBreakdown
    };
  }

  /**
   * Build a human-readable reasoning string
   * @private
   */
  private buildReasoning(
    severity: Severity,
    findingCount: number,
    moduleCount: number,
    breakdown: Record<Severity, number>
  ): string {
    const parts: string[] = [];

    // Main severity statement
    parts.push(`Overall severity: ${severity}`);

    // Finding and module counts
    const findingText = findingCount === 1 ? '1 finding' : `${findingCount} findings`;
    const moduleText = moduleCount === 1 ? '1 module' : `${moduleCount} modules`;
    parts.push(`(${findingText} across ${moduleText})`);

    // Add breakdown for multiple findings
    if (findingCount > 1) {
      const breakdownParts: string[] = [];
      if (breakdown[Severity.CRITICAL] > 0) {
        breakdownParts.push(`${breakdown[Severity.CRITICAL]} CRITICAL`);
      }
      if (breakdown[Severity.HIGH] > 0) {
        breakdownParts.push(`${breakdown[Severity.HIGH]} HIGH`);
      }
      if (breakdown[Severity.MEDIUM] > 0) {
        breakdownParts.push(`${breakdown[Severity.MEDIUM]} MEDIUM`);
      }
      if (breakdown[Severity.LOW] > 0) {
        breakdownParts.push(`${breakdown[Severity.LOW]} LOW`);
      }

      if (breakdownParts.length > 0) {
        parts.push(`- Breakdown: ${breakdownParts.join(', ')}`);
      }
    }

    return parts.join(' ');
  }
}
