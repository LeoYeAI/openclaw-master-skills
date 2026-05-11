import { ModuleConfig, Finding, SecurityPattern } from '../../types';
import { obfuscationPatterns } from '../../patterns/obfuscation/obfuscation-patterns';

export class ContentScanner {
  private config: ModuleConfig;
  private patterns: SecurityPattern[];

  constructor(config: ModuleConfig) {
    if (!config) {
      throw new Error('Configuration is required');
    }

    this.config = config;
    // Load patterns and filter by enabled flag
    this.patterns = obfuscationPatterns.filter(pattern => pattern.enabled);
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
        // Extract the matched text
        const matchedText = match[0];

        // Truncate very long matches for readability
        const displayText = matchedText.length > 100
          ? matchedText.substring(0, 100) + '...'
          : matchedText;

        findings.push({
          module: 'content_scanner',
          pattern: pattern,
          matchedText: displayText,
          severity: pattern.severity,
          metadata: {
            position: match.index,
            length: match[0].length,
            category: pattern.category,
            subcategory: pattern.subcategory,
            patternId: pattern.id,
            tags: pattern.tags,
            textLength: text.length,
            truncated: matchedText.length > 100,
            // Add specific metadata based on pattern type
            encodingType: pattern.subcategory ? this.detectEncodingType(pattern.subcategory) : undefined,
            hasInvisibleChars: this.hasInvisibleCharacters(matchedText)
          }
        });
      }
    }

    return findings;
  }

  private detectEncodingType(subcategory: string): string | undefined {
    const encodingMap: Record<string, string> = {
      'base64_encoded': 'base64',
      'hex_encoded': 'hexadecimal',
      'unicode_escape': 'unicode',
      'url_encoding_excessive': 'url',
      'html_entities': 'html',
      'double_encoding': 'double-url',
      'excessive_escaping': 'hex-escape',
      'octal_escaping': 'octal'
    };
    return encodingMap[subcategory];
  }

  private hasInvisibleCharacters(text: string): boolean {
    // Check for zero-width and invisible Unicode characters
    const invisibleChars = /[\u200B-\u200F\u202A-\u202E\u2060-\u206F\uFEFF]/;
    return invisibleChars.test(text);
  }
}
