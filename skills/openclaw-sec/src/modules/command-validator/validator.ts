import { ModuleConfig, Finding, SecurityPattern } from '../../types';
import { commandInjectionPatterns } from '../../patterns/runtime-validation/command-injection';

export class CommandValidator {
  private config: ModuleConfig;
  private patterns: SecurityPattern[];

  constructor(config: ModuleConfig) {
    if (!config) {
      throw new Error('Configuration is required');
    }

    this.config = config;
    // Load patterns and filter by enabled flag
    this.patterns = commandInjectionPatterns.filter(pattern => pattern.enabled);
  }

  async validate(command: string): Promise<Finding[]> {
    // Validate input
    if (command === null || command === undefined) {
      throw new Error('Input command cannot be null or undefined');
    }

    if (typeof command !== 'string') {
      throw new Error('Input must be a string');
    }

    // Return empty array for empty string
    if (command.length === 0) {
      return [];
    }

    const findings: Finding[] = [];

    // Test command against all enabled patterns
    for (const pattern of this.patterns) {
      const regex = pattern.pattern instanceof RegExp
        ? pattern.pattern
        : new RegExp(pattern.pattern, 'i');

      const match = command.match(regex);

      if (match) {
        findings.push({
          module: 'command_validator',
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
            commandLength: command.length
          }
        });
      }
    }

    return findings;
  }
}
