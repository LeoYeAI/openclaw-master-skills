import { ModuleConfig, Finding, SecurityPattern } from '../../types';
import { injectionPatterns } from '../../patterns/runtime-validation/injection-patterns';

export class InjectionValidator {
  private config: ModuleConfig;
  private patterns: SecurityPattern[];

  constructor(config: ModuleConfig) {
    if (!config) {
      throw new Error('Configuration is required');
    }

    this.config = config;
    // Load patterns and filter by enabled flag
    this.patterns = injectionPatterns.filter(pattern => pattern.enabled);
  }

  async validate(input: string): Promise<Finding[]> {
    // Validate input
    if (input === null || input === undefined) {
      throw new Error('Input cannot be null or undefined');
    }

    if (typeof input !== 'string') {
      throw new Error('Input must be a string');
    }

    // Return empty array for empty string
    if (input.length === 0) {
      return [];
    }

    const findings: Finding[] = [];

    // Test input against all enabled patterns
    for (const pattern of this.patterns) {
      const regex = pattern.pattern instanceof RegExp
        ? pattern.pattern
        : new RegExp(pattern.pattern, 'i');

      const match = input.match(regex);

      if (match) {
        findings.push({
          module: 'injection_validator',
          pattern: pattern,
          matchedText: match[0],
          severity: pattern.severity,
          metadata: {
            position: match.index,
            length: match[0].length,
            category: pattern.category,
            subcategory: pattern.subcategory,
            patternId: pattern.id,
            tags: pattern.tags,
            inputLength: input.length
          }
        });
      }
    }

    return findings;
  }
}
