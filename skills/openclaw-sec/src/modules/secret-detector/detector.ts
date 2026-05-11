import { ModuleConfig, Finding, SecurityPattern } from '../../types';
import { secretPatterns } from '../../patterns/secrets/secret-patterns';

export class SecretDetector {
  private config: ModuleConfig;
  private patterns: SecurityPattern[];

  constructor(config: ModuleConfig) {
    if (!config) {
      throw new Error('Configuration is required');
    }

    this.config = config;
    // Load patterns and filter by enabled flag
    this.patterns = secretPatterns.filter(pattern => pattern.enabled);
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

      // Use global flag to find all matches
      const globalRegex = new RegExp(regex.source, regex.flags.includes('g') ? regex.flags : regex.flags + 'g');
      let match;

      while ((match = globalRegex.exec(text)) !== null) {
        // Extract the actual secret value (captured group or full match)
        const secretValue = match[1] || match[0];

        // Redact the secret in matchedText (show only first/last few chars)
        const redactedSecret = this.redactSecret(secretValue);

        findings.push({
          module: 'secret_detector',
          pattern: pattern,
          matchedText: redactedSecret,
          severity: pattern.severity,
          metadata: {
            position: match.index,
            length: match[0].length,
            category: pattern.category,
            subcategory: pattern.subcategory,
            patternId: pattern.id,
            tags: pattern.tags,
            textLength: text.length,
            secretLength: secretValue.length,
            redacted: true
          }
        });
      }
    }

    return findings;
  }

  private redactSecret(secret: string): string {
    if (secret.length <= 8) {
      return '***REDACTED***';
    }

    const visibleChars = 4;
    const start = secret.substring(0, visibleChars);
    const end = secret.substring(secret.length - visibleChars);
    const redactedMiddle = '*'.repeat(Math.min(secret.length - 2 * visibleChars, 20));

    return `${start}${redactedMiddle}${end}`;
  }
}
