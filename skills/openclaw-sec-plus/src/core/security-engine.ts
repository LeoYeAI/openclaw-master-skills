import { SecurityConfig, ValidationResult, Finding, Severity, Action } from '../types';
import { DatabaseManager, SecurityEvent } from './database-manager';
import { SeverityScorer } from './severity-scorer';
import { ActionEngine } from './action-engine';
import { AsyncQueue } from './async-queue';
import { PromptInjectionDetector } from '../modules/prompt-injection/detector';
import { CommandValidator } from '../modules/command-validator/validator';
import { URLValidator } from '../modules/url-validator/validator';
import { PathValidator } from '../modules/path-validator/validator';
import { SecretDetector } from '../modules/secret-detector/detector';
import { ContentScanner } from '../modules/content-scanner/scanner';
import { InjectionValidator } from '../modules/injection-validator/validator';
import { ExfiltrationDetector } from '../modules/exfiltration-detector/detector';
import { CodeExecutionDetector } from '../modules/code-execution-detector/detector';
import { SerializationDetector } from '../modules/serialization-detector/detector';
import * as crypto from 'crypto';

/**
 * Validation metadata
 */
export interface ValidationMetadata {
  userId: string;
  sessionId: string;
  context?: Record<string, any>;
}

/**
 * SecurityEngine is the main orchestrator that coordinates all detection modules,
 * severity scoring, action determination, and async writes.
 *
 * Architecture:
 * - Runs all 10 detection modules in parallel
 * - Aggregates findings with SeverityScorer
 * - Determines action with ActionEngine
 * - Returns results in ~20-50ms
 * - Queues DB writes and notifications asynchronously
 *
 * @example
 * ```typescript
 * const config = await ConfigManager.load('security-config.yaml');
 * const dbManager = new DatabaseManager('.openclaw-sec.db');
 * const engine = new SecurityEngine(config, dbManager);
 *
 * const result = await engine.validate('User input text', {
 *   userId: 'user-123',
 *   sessionId: 'session-456'
 * });
 *
 * console.log(result.severity); // SAFE, LOW, MEDIUM, HIGH, or CRITICAL
 * console.log(result.action); // allow, log, warn, block, or block_notify
 *
 * await engine.stop(); // Cleanup
 * ```
 */
interface CacheEntry {
  findings: Finding[];
  severity: Severity;
  timestamp: number;
}

export class SecurityEngine {
  private readonly config: SecurityConfig;
  private readonly dbManager: DatabaseManager;
  private readonly severityScorer: SeverityScorer;
  private readonly actionEngine: ActionEngine;
  private readonly writeQueue: AsyncQueue;

  // Validation result cache (LRU)
  private readonly cache: Map<string, CacheEntry> = new Map();
  private readonly cacheSize: number;
  private readonly cacheTtlMs: number;

  // Detection modules
  private readonly promptInjectionDetector: PromptInjectionDetector | null = null;
  private readonly commandValidator: CommandValidator | null = null;
  private readonly urlValidator: URLValidator | null = null;
  private readonly pathValidator: PathValidator | null = null;
  private readonly secretDetector: SecretDetector | null = null;
  private readonly contentScanner: ContentScanner | null = null;
  private readonly injectionValidator: InjectionValidator | null = null;
  private readonly exfiltrationDetector: ExfiltrationDetector | null = null;
  private readonly codeExecutionDetector: CodeExecutionDetector | null = null;
  private readonly serializationDetector: SerializationDetector | null = null;

  /**
   * Creates a new SecurityEngine instance
   *
   * @param config - Security configuration
   * @param dbManager - Database manager
   * @throws Error if config or dbManager is missing
   */
  constructor(config: SecurityConfig, dbManager?: DatabaseManager | null) {
    if (!config) {
      throw new Error('Configuration is required');
    }

    this.config = config;
    this.dbManager = dbManager!;
    this.severityScorer = new SeverityScorer();
    this.actionEngine = new ActionEngine(config, dbManager);
    this.cacheSize = config.cacheSize ?? 1000;
    this.cacheTtlMs = config.cacheTtlMs ?? 5 * 60 * 1000; // 5 minutes

    // Initialize async write queue (skip DB writes if no dbManager)
    this.writeQueue = new AsyncQueue({
      batchSize: 50,
      flushInterval: 100,
      onBatch: async (events: SecurityEvent[]) => {
        if (!this.dbManager) return; // Skip DB writes in NO_DB mode
        try {
          events.forEach(event => {
            this.dbManager.insertEvent(event);
          });
        } catch (error) {
          console.error('Error writing security events to database:', error);
        }
      }
    });

    // Initialize enabled modules
    if (config.modules.prompt_injection?.enabled) {
      this.promptInjectionDetector = new PromptInjectionDetector(config.modules.prompt_injection);
    }
    if (config.modules.command_validator?.enabled) {
      this.commandValidator = new CommandValidator(config.modules.command_validator);
    }
    if (config.modules.url_validator?.enabled) {
      this.urlValidator = new URLValidator(config.modules.url_validator);
    }
    if (config.modules.path_validator?.enabled) {
      this.pathValidator = new PathValidator(config.modules.path_validator);
    }
    if (config.modules.secret_detector?.enabled) {
      this.secretDetector = new SecretDetector(config.modules.secret_detector);
    }
    if (config.modules.content_scanner?.enabled) {
      this.contentScanner = new ContentScanner(config.modules.content_scanner);
    }
    if (config.modules.injection_validator?.enabled) {
      this.injectionValidator = new InjectionValidator(config.modules.injection_validator);
    }
    if (config.modules.exfiltration_detector?.enabled) {
      this.exfiltrationDetector = new ExfiltrationDetector(config.modules.exfiltration_detector);
    }
    if (config.modules.code_execution_detector?.enabled) {
      this.codeExecutionDetector = new CodeExecutionDetector(config.modules.code_execution_detector);
    }
    if (config.modules.serialization_detector?.enabled) {
      this.serializationDetector = new SerializationDetector(config.modules.serialization_detector);
    }
  }

  /**
   * Validate input text against all security modules
   *
   * @param text - Input text to validate
   * @param metadata - Validation metadata (userId, sessionId, etc.)
   * @returns ValidationResult with severity, action, and findings
   * @throws Error if metadata is invalid
   */
  async validate(text: string, metadata: ValidationMetadata): Promise<ValidationResult> {
    // Validate metadata
    if (!metadata.userId || metadata.userId.trim().length === 0) {
      throw new Error('User ID is required in validation metadata');
    }

    if (!metadata.sessionId || metadata.sessionId.trim().length === 0) {
      throw new Error('Session ID is required in validation metadata');
    }

    // Check if security is enabled
    if (!this.config.enabled) {
      return this.createSafeResult(text);
    }

    // Generate fingerprint for cache lookup
    const fingerprint = this.generateFingerprint(text);

    // Check cache
    const cached = this.getCacheEntry(fingerprint);
    if (cached) {
      // Re-run action engine for the current user (action is user-specific)
      const actionResult = await this.actionEngine.determineAction(
        cached.severity,
        metadata.userId
      );

      const result: ValidationResult = {
        severity: cached.severity,
        action: actionResult.action,
        findings: cached.findings,
        fingerprint,
        timestamp: new Date(),
        normalizedText: this.normalizeText(text),
        recommendations: this.generateRecommendations(cached.findings, actionResult.action)
      };

      this.queueDatabaseWrite(result, metadata);
      return result;
    }

    // Compute input entropy before module dispatch
    const entropy = this.calculateEntropy(text);

    // Collect all findings
    let allFindings: Finding[];

    if (this.config.earlyExitOnCritical) {
      // Two-phase execution: run fast modules first
      allFindings = await this.runWithEarlyExit(text);
    } else {
      // Standard parallel execution
      allFindings = await this.runAllModules(text);
    }

    // Inject synthetic entropy finding if entropy is high
    if (entropy > 4.5) {
      allFindings.push({
        module: 'entropy_analysis',
        pattern: {
          id: 'entropy_001',
          category: 'high_entropy',
          pattern: '',
          severity: Severity.MEDIUM,
          language: 'all',
          description: `Input has high Shannon entropy (${entropy.toFixed(2)} bits/char), indicating possible obfuscation`,
          examples: [],
          falsePositiveRisk: 'medium',
          enabled: true,
          tags: ['entropy', 'obfuscation', 'anomaly']
        },
        matchedText: text.substring(0, 50) + (text.length > 50 ? '...' : ''),
        severity: Severity.MEDIUM,
        metadata: {
          entropy: entropy,
          textLength: text.length,
          category: 'high_entropy'
        }
      });
    }

    // Calculate severity
    const severityResult = this.severityScorer.calculateSeverity(allFindings);

    // Store in cache
    this.setCacheEntry(fingerprint, {
      findings: allFindings,
      severity: severityResult.severity,
      timestamp: Date.now()
    });

    // Determine action
    const actionResult = await this.actionEngine.determineAction(
      severityResult.severity,
      metadata.userId
    );

    // Create validation result
    const result: ValidationResult = {
      severity: severityResult.severity,
      action: actionResult.action,
      findings: allFindings,
      fingerprint,
      timestamp: new Date(),
      normalizedText: this.normalizeText(text),
      recommendations: this.generateRecommendations(allFindings, actionResult.action)
    };

    // Queue async database write
    this.queueDatabaseWrite(result, metadata);

    return result;
  }

  /**
   * Run all detection modules in parallel (standard mode)
   * @private
   */
  private async runAllModules(text: string): Promise<Finding[]> {
    const detectionPromises: Promise<Finding[]>[] = [];

    if (this.promptInjectionDetector) {
      detectionPromises.push(this.promptInjectionDetector.scan(text).catch(() => []));
    }
    if (this.commandValidator) {
      detectionPromises.push(this.commandValidator.validate(text).catch(() => []));
    }
    if (this.urlValidator) {
      detectionPromises.push(this.urlValidator.validate(text).catch(() => []));
    }
    if (this.pathValidator) {
      detectionPromises.push(this.pathValidator.validate(text).catch(() => []));
    }
    if (this.secretDetector) {
      detectionPromises.push(this.secretDetector.scan(text).catch(() => []));
    }
    if (this.contentScanner) {
      detectionPromises.push(this.contentScanner.scan(text).catch(() => []));
    }
    if (this.injectionValidator) {
      detectionPromises.push(this.injectionValidator.validate(text).catch(() => []));
    }
    if (this.exfiltrationDetector) {
      detectionPromises.push(this.exfiltrationDetector.scan(text).catch(() => []));
    }
    if (this.codeExecutionDetector) {
      detectionPromises.push(this.codeExecutionDetector.scan(text).catch(() => []));
    }
    if (this.serializationDetector) {
      detectionPromises.push(this.serializationDetector.scan(text).catch(() => []));
    }

    const results = await Promise.all(detectionPromises);
    return results.flat();
  }

  /**
   * Two-phase execution with early exit on CRITICAL findings
   * Phase 1: Run fast modules (command, path, injection validators)
   * Phase 2: If no CRITICAL found, run remaining modules
   * @private
   */
  private async runWithEarlyExit(text: string): Promise<Finding[]> {
    // Phase 1: Fast regex-only modules
    const fastPromises: Promise<Finding[]>[] = [];

    if (this.commandValidator) {
      fastPromises.push(this.commandValidator.validate(text).catch(() => []));
    }
    if (this.pathValidator) {
      fastPromises.push(this.pathValidator.validate(text).catch(() => []));
    }
    if (this.injectionValidator) {
      fastPromises.push(this.injectionValidator.validate(text).catch(() => []));
    }

    const fastResults = await Promise.all(fastPromises);
    const fastFindings = fastResults.flat();

    // Check for CRITICAL
    const hasCritical = fastFindings.some(f => f.severity === Severity.CRITICAL);
    if (hasCritical) {
      return fastFindings;
    }

    // Phase 2: Run remaining modules
    const slowPromises: Promise<Finding[]>[] = [];

    if (this.promptInjectionDetector) {
      slowPromises.push(this.promptInjectionDetector.scan(text).catch(() => []));
    }
    if (this.urlValidator) {
      slowPromises.push(this.urlValidator.validate(text).catch(() => []));
    }
    if (this.secretDetector) {
      slowPromises.push(this.secretDetector.scan(text).catch(() => []));
    }
    if (this.contentScanner) {
      slowPromises.push(this.contentScanner.scan(text).catch(() => []));
    }
    if (this.exfiltrationDetector) {
      slowPromises.push(this.exfiltrationDetector.scan(text).catch(() => []));
    }
    if (this.codeExecutionDetector) {
      slowPromises.push(this.codeExecutionDetector.scan(text).catch(() => []));
    }
    if (this.serializationDetector) {
      slowPromises.push(this.serializationDetector.scan(text).catch(() => []));
    }

    const slowResults = await Promise.all(slowPromises);
    return [...fastFindings, ...slowResults.flat()];
  }

  /**
   * Stop the security engine and flush pending writes
   */
  async stop(): Promise<void> {
    await this.writeQueue.flush();
    this.writeQueue.stop();
  }

  /**
   * Create a safe result for clean input
   * @private
   */
  private createSafeResult(text: string): ValidationResult {
    return {
      severity: Severity.SAFE,
      action: Action.ALLOW,
      findings: [],
      fingerprint: this.generateFingerprint(text),
      timestamp: new Date(),
      normalizedText: this.normalizeText(text),
      recommendations: []
    };
  }

  /**
   * Generate a fingerprint for the input text
   * @private
   */
  private generateFingerprint(text: string): string {
    const normalized = this.normalizeText(text);
    return crypto.createHash('sha256').update(normalized).digest('hex').substring(0, 16);
  }

  /**
   * Normalize text for fingerprinting
   * @private
   */
  private normalizeText(text: string): string {
    return text.toLowerCase().replace(/\s+/g, ' ').trim();
  }

  /**
   * Calculate Shannon entropy of input text (bits per character)
   * @private
   */
  private calculateEntropy(text: string): number {
    if (text.length === 0) return 0;

    const freq = new Map<string, number>();
    for (const char of text) {
      freq.set(char, (freq.get(char) || 0) + 1);
    }

    let entropy = 0;
    const len = text.length;
    for (const count of freq.values()) {
      const p = count / len;
      if (p > 0) {
        entropy -= p * Math.log2(p);
      }
    }

    return entropy;
  }

  /**
   * Get a cache entry if it exists and is not expired
   * @private
   */
  private getCacheEntry(fingerprint: string): CacheEntry | null {
    const entry = this.cache.get(fingerprint);
    if (!entry) return null;

    // Check TTL
    if (Date.now() - entry.timestamp > this.cacheTtlMs) {
      this.cache.delete(fingerprint);
      return null;
    }

    return entry;
  }

  /**
   * Set a cache entry, evicting oldest if at capacity
   * @private
   */
  private setCacheEntry(fingerprint: string, entry: CacheEntry): void {
    // Evict oldest entry if at capacity
    if (this.cache.size >= this.cacheSize && !this.cache.has(fingerprint)) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey !== undefined) {
        this.cache.delete(firstKey);
      }
    }

    this.cache.set(fingerprint, entry);
  }

  /**
   * Generate actionable recommendations based on findings
   * @private
   */
  private generateRecommendations(findings: Finding[], action: Action): string[] {
    const recommendations: string[] = [];

    if (findings.length === 0) {
      return recommendations;
    }

    // Group findings by module
    const moduleGroups = new Map<string, Finding[]>();
    findings.forEach(finding => {
      const existing = moduleGroups.get(finding.module) || [];
      existing.push(finding);
      moduleGroups.set(finding.module, existing);
    });

    // Generate recommendations per module
    moduleGroups.forEach((moduleFindings, module) => {
      switch (module) {
        case 'prompt_injection':
          recommendations.push('Review input for potential prompt injection attempts');
          recommendations.push('Consider implementing input sanitization');
          break;
        case 'command_validator':
          recommendations.push('Validate and sanitize any system commands');
          recommendations.push('Use parameterized commands instead of string concatenation');
          break;
        case 'url_validator':
          recommendations.push('Validate and whitelist allowed URL patterns');
          recommendations.push('Implement URL parsing and domain verification');
          break;
        case 'path_validator':
          recommendations.push('Validate file paths against allowed directories');
          recommendations.push('Use path normalization to prevent traversal attacks');
          break;
        case 'secret_detector':
          recommendations.push('Remove any exposed secrets or credentials');
          recommendations.push('Rotate compromised credentials immediately');
          break;
        case 'content_scanner':
          recommendations.push('Review content for policy violations');
          recommendations.push('Implement content filtering or moderation');
          break;
        case 'injection_validator':
          recommendations.push('Sanitize inputs to prevent injection attacks');
          recommendations.push('Use parameterized queries and prepared statements');
          break;
        case 'exfiltration_detector':
          recommendations.push('Review outbound connections for data exfiltration attempts');
          recommendations.push('Implement egress filtering and data loss prevention');
          break;
        case 'code_execution_detector':
          recommendations.push('Review input for code execution attempts');
          recommendations.push('Restrict dynamic code evaluation and sandboxing');
          break;
        case 'serialization_detector':
          recommendations.push('Avoid deserializing untrusted data');
          recommendations.push('Use safe deserialization methods with type allowlists');
          break;
      }
    });

    // Add action-specific recommendations
    if (action === Action.BLOCK || action === Action.BLOCK_NOTIFY) {
      recommendations.push('This request has been blocked due to security concerns');
      recommendations.push('Contact security team if you believe this is a false positive');
    }

    // Deduplicate recommendations
    return Array.from(new Set(recommendations));
  }

  /**
   * Queue database write for async processing
   * @private
   */
  private queueDatabaseWrite(result: ValidationResult, metadata: ValidationMetadata): void {
    try {
      const normalizedText = result.normalizedText || '-';
      const event: SecurityEvent = {
        event_type: 'validation',
        severity: result.severity,
        action_taken: result.action,
        user_id: metadata.userId,
        session_id: metadata.sessionId,
        input_text: normalizedText,
        patterns_matched: JSON.stringify(
          result.findings.map(f => ({
            module: f.module,
            patternId: f.pattern.id,
            severity: f.severity
          }))
        ),
        fingerprint: result.fingerprint,
        module: result.findings.length > 0 ? result.findings[0].module : 'none',
        metadata: JSON.stringify({
          findingCount: result.findings.length,
          modulesConcerned: Array.from(new Set(result.findings.map(f => f.module))),
          context: metadata.context
        })
      };

      this.writeQueue.enqueue(event);
    } catch (error) {
      console.error('Error queuing database write:', error);
    }
  }
}
