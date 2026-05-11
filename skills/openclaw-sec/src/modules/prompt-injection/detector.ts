import { ModuleConfig, Finding, SecurityPattern } from '../../types';
import { promptInjectionPatternsEN } from '../../patterns/prompt-injection';

export class PromptInjectionDetector {
  private config: ModuleConfig;
  private patterns: SecurityPattern[];

  constructor(config: ModuleConfig) {
    if (!config) {
      throw new Error('Configuration is required');
    }

    this.config = config;
    // Load patterns and filter by enabled flag
    this.patterns = promptInjectionPatternsEN.filter(pattern => pattern.enabled);
  }

  async scan(text: string): Promise<Finding[]> {
    // Validate input
    if (text === null || text === undefined) {
      throw new Error('Input text cannot be null or undefined');
    }

    if (typeof text !== 'string') {
      throw new Error('Input must be a string');
    }

    // Return empty array for empty string
    if (text.length === 0) {
      return [];
    }

    const findings: Finding[] = [];

    // Test text against all enabled patterns
    for (const pattern of this.patterns) {
      const regex = pattern.pattern instanceof RegExp
        ? pattern.pattern
        : new RegExp(pattern.pattern, 'i');

      const match = text.match(regex);

      if (match) {
        findings.push({
          module: 'prompt_injection',
          pattern: pattern,
          matchedText: match[0],
          severity: pattern.severity,
          metadata: {
            position: match.index,
            length: match[0].length,
            category: pattern.category,
            subcategory: pattern.subcategory,
            patternId: pattern.id,
            tags: pattern.tags
          }
        });
      }
    }

    return findings;
  }
}
