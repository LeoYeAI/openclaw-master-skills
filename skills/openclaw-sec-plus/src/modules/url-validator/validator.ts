import { ModuleConfig, Finding, SecurityPattern } from '../../types';
import { ssrfPatterns } from '../../patterns/runtime-validation/ssrf-patterns';

export class URLValidator {
  private config: ModuleConfig;
  private patterns: SecurityPattern[];

  constructor(config: ModuleConfig) {
    if (!config) {
      throw new Error('Configuration is required');
    }

    this.config = config;
    // Load patterns and filter by enabled flag
    this.patterns = ssrfPatterns.filter(pattern => pattern.enabled);
  }

  async validate(url: string): Promise<Finding[]> {
    // Validate input
    if (url === null || url === undefined) {
      throw new Error('Input URL cannot be null or undefined');
    }

    if (typeof url !== 'string') {
      throw new Error('Input must be a string');
    }

    // Return empty array for empty string
    if (url.length === 0) {
      return [];
    }

    const findings: Finding[] = [];

    // Parse URL to extract components (handle gracefully if malformed)
    let parsedUrl: URL | null = null;
    let protocol = '';
    let hostname = '';
    let port = '';
    let pathname = '';

    try {
      // Try to parse as URL with protocol
      parsedUrl = new URL(url);
      protocol = parsedUrl.protocol;
      hostname = parsedUrl.hostname;
      port = parsedUrl.port;
      pathname = parsedUrl.pathname;
    } catch (error) {
      // If URL parsing fails, try adding protocol and parse again
      try {
        parsedUrl = new URL('http://' + url);
        protocol = '';
        hostname = parsedUrl.hostname;
        port = parsedUrl.port;
        pathname = parsedUrl.pathname;
      } catch (innerError) {
        // If still fails, continue with pattern matching on raw string
        // This handles edge cases and malformed URLs
      }
    }

    // Test URL against all enabled patterns
    for (const pattern of this.patterns) {
      const regex = pattern.pattern instanceof RegExp
        ? pattern.pattern
        : new RegExp(pattern.pattern, 'i');

      const match = url.match(regex);

      if (match) {
        findings.push({
          module: 'url_validator',
          pattern: pattern,
          matchedText: match[0],
          severity: pattern.severity,
          metadata: {
            url: url,
            protocol: protocol,
            hostname: hostname,
            port: port,
            pathname: pathname,
            position: match.index,
            length: match[0].length,
            category: pattern.category,
            subcategory: pattern.subcategory,
            patternId: pattern.id,
            tags: pattern.tags,
            urlLength: url.length
          }
        });
      }
    }

    return findings;
  }
}
