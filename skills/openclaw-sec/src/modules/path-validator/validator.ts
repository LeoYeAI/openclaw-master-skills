import { ModuleConfig, Finding, SecurityPattern } from '../../types';
import { pathTraversalPatterns } from '../../patterns/runtime-validation/path-traversal-patterns';

export class PathValidator {
  private config: ModuleConfig;
  private patterns: SecurityPattern[];

  constructor(config: ModuleConfig) {
    if (!config) {
      throw new Error('Configuration is required');
    }

    this.config = config;
    // Load patterns and filter by enabled flag
    this.patterns = pathTraversalPatterns.filter(pattern => pattern.enabled);
  }

  async validate(path: string): Promise<Finding[]> {
    // Validate input
    if (path === null || path === undefined) {
      throw new Error('Input path cannot be null or undefined');
    }

    if (typeof path !== 'string') {
      throw new Error('Input must be a string');
    }

    // Return empty array for empty string
    if (path.length === 0) {
      return [];
    }

    const findings: Finding[] = [];

    // Normalize path separators for analysis
    const normalizedPath = path.replace(/\\/g, '/');

    // Test path against all enabled patterns
    for (const pattern of this.patterns) {
      const regex = pattern.pattern instanceof RegExp
        ? pattern.pattern
        : new RegExp(pattern.pattern, 'i');

      const match = path.match(regex);

      if (match) {
        findings.push({
          module: 'path_validator',
          pattern: pattern,
          matchedText: match[0],
          severity: pattern.severity,
          metadata: {
            path: path,
            normalizedPath: normalizedPath,
            position: match.index,
            length: match[0].length,
            category: pattern.category,
            subcategory: pattern.subcategory,
            patternId: pattern.id,
            tags: pattern.tags,
            pathLength: path.length,
            isAbsolute: path.startsWith('/') || /^[a-z]:\\/i.test(path),
            hasTraversal: path.includes('../') || path.includes('..\\')
          }
        });
      }
    }

    return findings;
  }
}
