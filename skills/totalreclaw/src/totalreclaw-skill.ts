/**
 * TotalReclaw Skill - Main Skill Class
 *
 * The primary integration point for TotalReclaw with OpenClaw.
 * Handles lifecycle hooks, tool methods, and state management.
 *
 * @example
 * ```typescript
 * const skill = new TotalReclawSkill({
 *   serverUrl: 'http://127.0.0.1:8080',
 *   masterPassword: 'my-secure-password',
 * });
 *
 * await skill.init();
 *
 * // Before agent starts processing
 * const contextResult = await skill.onBeforeAgentStart(openClawContext);
 *
 * // After agent finishes
 * const endResult = await skill.onAgentEnd(openClawContext);
 * ```
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import {
  TotalReclaw,
  type Fact,
  type RerankedResult,
  type FactMetadata,
  type ExportedData,
  TotalReclawError,
  TotalReclawErrorCode,
  deriveKeys,
} from '@totalreclaw/client';
import type {
  TotalReclawSkillConfig,
  OpenClawContext,
  BeforeAgentStartResult,
  AgentEndResult,
  PreCompactionResult,
  RememberToolParams,
  RecallToolParams,
  ForgetToolParams,
  ExportToolParams,
  SkillState,
  ExtractedFact,
  ExtractionResult,
} from './types';
import { DEFAULT_SKILL_CONFIG } from './types';
import { loadConfig, validateConfig, assertValidConfig } from './config';
import { CrossEncoderReranker, type CrossEncoderResult } from './reranker/cross-encoder';
import {
  FactExtractor,
  createFactExtractor,
  isExplicitMemoryCommand,
  parseExplicitMemoryCommand,
  type ExtractionTrigger,
  type LLMClient,
  type VectorStoreClient,
} from './extraction';
import { debugLog } from './debug';

// ============================================================================
// Types
// ============================================================================

/**
 * Result of skill initialization
 */
export interface InitResult {
  success: boolean;
  isNewUser: boolean;
  userId?: string;
  error?: string;
}

/**
 * Internal options for skill operations
 */
interface SkillOperationOptions {
  /** Skip extraction even if triggered */
  skipExtraction?: boolean;
  /** Force extraction regardless of triggers */
  forceExtraction?: boolean;
  /** Override minimum importance */
  minImportance?: number;
}

// ============================================================================
// LLM Client Adapter
// ============================================================================

/**
 * Adapter to make OpenClaw's LLM available to the extraction module
 */
class OpenClawLLMAdapter implements LLMClient {
  private completeFn: (prompt: { system: string; user: string }) => Promise<string>;

  constructor(completeFn: (prompt: { system: string; user: string }) => Promise<string>) {
    this.completeFn = completeFn;
  }

  async complete(prompt: { system: string; user: string }): Promise<string> {
    return this.completeFn(prompt);
  }
}

// ============================================================================
// Vector Store Adapter
// ============================================================================

/**
 * Adapter to make TotalReclaw client available as a vector store
 */
class TotalReclawVectorStoreAdapter implements VectorStoreClient {
  private client: TotalReclaw;

  constructor(client: TotalReclaw) {
    this.client = client;
  }

  async findSimilar(embedding: number[], k: number): Promise<import('./extraction/dedup').ExistingFact[]> {
    // Note: This is a simplified implementation.
    // In practice, we'd need a server endpoint that supports embedding-based search.
    // For now, we'll return empty and let the deduplicator fall back to text comparison.
    console.warn('Vector-based similarity search not yet implemented in vector store adapter');
    return [];
  }

  async getEmbedding(text: string): Promise<number[]> {
    // The TotalReclaw client handles embedding internally
    // We'll use a hash-based approach for dedup purposes
    return this.createDeterministicEmbedding(text);
  }

  /**
   * Create a deterministic embedding from text for dedup purposes
   */
  private createDeterministicEmbedding(text: string): number[] {
    // Simple hash-based embedding for dedup comparison
    // Not as accurate as real embeddings but works for similarity comparison
    const dimension = 1024;
    const embedding: number[] = new Array(dimension).fill(0);

    const words = text.toLowerCase().split(/\s+/).filter(w => w.length > 2);

    for (const word of words) {
      // Hash each word to multiple dimensions
      let hash = 0;
      for (let i = 0; i < word.length; i++) {
        const char = word.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
      }

      // Spread the hash across several dimensions
      for (let i = 0; i < 5; i++) {
        const idx = Math.abs(hash + i * 73) % dimension;
        embedding[idx] += 0.2;
      }
    }

    // Normalize
    let norm = 0;
    for (const val of embedding) {
      norm += val * val;
    }
    norm = Math.sqrt(norm);

    if (norm > 0) {
      for (let i = 0; i < embedding.length; i++) {
        embedding[i] /= norm;
      }
    }

    return embedding;
  }
}

// ============================================================================
// Billing Constants
// ============================================================================

const BILLING_CACHE_PATH = path.join(os.homedir(), '.totalreclaw', 'billing-cache.json');
const CACHE_MAX_AGE_MS = 12 * 60 * 60 * 1000; // 12 hours
const QUOTA_WARNING_THRESHOLD = 0.8; // 80%

interface BillingCacheData {
  tier: string;
  free_writes_used: number;
  free_writes_limit: number;
  free_reads_used: number;
  free_reads_limit: number;
  checked_at: number;
}

function isBillingCacheData(data: unknown): data is BillingCacheData {
  if (typeof data !== 'object' || data === null) return false;
  const d = data as Record<string, unknown>;
  return (
    typeof d.tier === 'string' &&
    typeof d.free_writes_used === 'number' &&
    typeof d.free_writes_limit === 'number' &&
    typeof d.free_reads_used === 'number' &&
    typeof d.free_reads_limit === 'number' &&
    typeof d.checked_at === 'number'
  );
}

// ============================================================================
// TotalReclawSkill Class
// ============================================================================

/**
 * Main TotalReclaw Skill Class
 *
 * Integrates TotalReclaw with OpenClaw through lifecycle hooks and tools.
 */
export class TotalReclawSkill {
  private config: TotalReclawSkillConfig;
  private client: TotalReclaw | null = null;
  private reranker: CrossEncoderReranker;
  private extractor: FactExtractor | null = null;
  private state: SkillState;
  private llmAdapter: OpenClawLLMAdapter | null = null;
  private vectorStoreAdapter: TotalReclawVectorStoreAdapter | null = null;
  private authKeyHex: string | null = null;

  /**
   * Create a new TotalReclawSkill instance
   *
   * @param config - Skill configuration (partial, will be merged with defaults)
   */
  constructor(config: Partial<TotalReclawSkillConfig> = {}) {
    // Load and merge configuration
    this.config = loadConfig({ overrides: config });

    // Validate configuration
    assertValidConfig(this.config);

    // Initialize reranker
    this.reranker = new CrossEncoderReranker({
      modelPath: this.config.rerankerModel,
      debug: false,
    });

    // Initialize state
    this.state = {
      turnCount: 0,
      lastExtraction: null,
      cachedMemories: [],
      isInitialized: false,
      pendingExtractions: [],
    };
  }

  // ============================================================================
  // Initialization
  // ============================================================================

  /**
   * Initialize the skill
   *
   * Must be called before using any other methods.
   * Initializes the TotalReclaw client and loads the reranker model.
   *
   * @param llmCompleteFn - Optional LLM completion function for extraction
   * @returns Initialization result
   */
  async init(llmCompleteFn?: (prompt: { system: string; user: string }) => Promise<string>): Promise<InitResult> {
    try {
      // Initialize TotalReclaw client
      this.client = new TotalReclaw({
        serverUrl: this.config.serverUrl,
      });

      await this.client.init();

      // Check if we have credentials
      let isNewUser = false;

      if (this.config.masterPassword) {
        if (this.config.userId && this.config.salt) {
          // Login with existing credentials
          await this.client.login(
            this.config.userId,
            this.config.masterPassword,
            this.config.salt
          );

          // Derive auth key hex for billing API calls
          try {
            const { authKey } = await deriveKeys(this.config.masterPassword, this.config.salt);
            this.authKeyHex = authKey.toString('hex');
          } catch (e) {
            debugLog('Failed to derive auth key for billing:', e);
          }
        } else {
          // Register new user
          const userId = await this.client.register(this.config.masterPassword);
          isNewUser = true;

          // Derive auth key hex for billing API calls
          const salt = this.client.getSalt();
          if (salt) {
            try {
              const { authKey } = await deriveKeys(this.config.masterPassword, salt);
              this.authKeyHex = authKey.toString('hex');
            } catch (e) {
              debugLog('Failed to derive auth key for billing:', e);
            }
          }

          // Store credentials for future use (caller should persist these)
          debugLog(`Registered new user: ${userId}`);
        }
      }

      // Initialize reranker (async, non-blocking)
      this.reranker.load(this.config.rerankerModel).catch(err => {
        console.warn('[TotalReclaw] Failed to load reranker model, using fallback:', err);
      });

      // Set up LLM adapter if provided
      if (llmCompleteFn) {
        this.llmAdapter = new OpenClawLLMAdapter(llmCompleteFn);
        this.vectorStoreAdapter = new TotalReclawVectorStoreAdapter(this.client);
        this.extractor = createFactExtractor(
          this.llmAdapter,
          this.vectorStoreAdapter,
          { minImportance: this.config.minImportanceForAutoStore }
        );
      }

      this.state.isInitialized = true;

      return {
        success: true,
        isNewUser,
        userId: this.client.getUserId() ?? undefined,
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      console.error('[TotalReclaw] Initialization failed:', message);

      return {
        success: false,
        isNewUser: false,
        error: message,
      };
    }
  }

  /**
   * Set the LLM completion function for extraction
   * Can be called after init() if LLM wasn't available at initialization
   */
  setLLMProvider(completeFn: (prompt: { system: string; user: string }) => Promise<string>): void {
    this.llmAdapter = new OpenClawLLMAdapter(completeFn);

    if (this.client) {
      this.vectorStoreAdapter = new TotalReclawVectorStoreAdapter(this.client);
    }

    this.extractor = createFactExtractor(
      this.llmAdapter,
      this.vectorStoreAdapter ?? undefined,
      { minImportance: this.config.minImportanceForAutoStore }
    );
  }

  // ============================================================================
  // Lifecycle Hooks
  // ============================================================================

  /**
   * before_agent_start hook
   *
   * Called before the agent starts processing a user message.
   * Retrieves relevant memories and formats them for context injection.
   *
   * @param context - OpenClaw context
   * @returns Memories to inject into context
   */
  async onBeforeAgentStart(context: OpenClawContext): Promise<BeforeAgentStartResult> {
    this.ensureInitialized();
    const startTime = Date.now();

    // Billing cache check
    let billingWarning = '';
    try {
      let needsRefresh = true;
      let billingData: BillingCacheData | null = null;

      if (fs.existsSync(BILLING_CACHE_PATH)) {
        const cached = JSON.parse(fs.readFileSync(BILLING_CACHE_PATH, 'utf-8'));
        if (Date.now() - cached.timestamp < CACHE_MAX_AGE_MS && isBillingCacheData(cached.data)) {
          needsRefresh = false;
          billingData = cached.data;
        }
      }

      if (needsRefresh && this.authKeyHex) {
        // Make API call to refresh cache
        const serverUrl = this.config.serverUrl.replace(/\/+$/, '');
        const response = await fetch(`${serverUrl}/v1/billing/status`, {
          headers: { 'Authorization': `Bearer ${this.authKeyHex}`, 'X-TotalReclaw-Client': 'openclaw-plugin' }
        });
        if (response.ok) {
          const parsed: unknown = await response.json();
          if (isBillingCacheData(parsed)) {
            billingData = parsed;
            fs.mkdirSync(path.dirname(BILLING_CACHE_PATH), { recursive: true });
            fs.writeFileSync(BILLING_CACHE_PATH, JSON.stringify({ timestamp: Date.now(), data: billingData }));
          }
        }
      }

      if (billingData && billingData.free_writes_limit > 0) {
        const usageRatio = billingData.free_writes_used / billingData.free_writes_limit;
        if (usageRatio >= QUOTA_WARNING_THRESHOLD) {
          billingWarning = `\n\n⚠️ TotalReclaw quota warning: ${billingData.free_writes_used}/${billingData.free_writes_limit} writes used this month (${Math.round(usageRatio * 100)}%). ` +
            (billingData.upgrade_url ? `Upgrade: ${billingData.upgrade_url}` : 'Resets next month.');
        }
      }
    } catch (e) {
      debugLog('billing cache check failed:', e);
    }

    try {
      // Search for relevant memories based on user message
      const memories = await this.client!.recall(
        context.userMessage,
        this.config.maxMemoriesInContext
      );

      // Re-rank using cross-encoder if available
      let rankedMemories: RerankedResult[];
      if (this.reranker.isReady() && memories.length > 0) {
        const facts = memories.map(m => m.fact);
        const crossEncoderResults = await this.reranker.rerank(
          context.userMessage,
          facts,
          this.config.maxMemoriesInContext
        );

        // Map back to RerankedResult format
        rankedMemories = crossEncoderResults.map(ceResult => ({
          fact: ceResult.fact,
          score: ceResult.score,
          vectorScore: ceResult.vectorScore,
          textScore: ceResult.textScore,
          decayAdjustedScore: ceResult.decayAdjustedScore,
        }));
      } else {
        rankedMemories = memories;
      }

      // Update cache
      this.state.cachedMemories = rankedMemories;

      // Format context string and append billing warning
      const contextString = this.formatMemoriesForContext(rankedMemories) + billingWarning;

      return {
        memories: rankedMemories,
        contextString,
        latencyMs: Date.now() - startTime,
      };
    } catch (error) {
      console.error('[TotalReclaw] onBeforeAgentStart failed:', error);

      // Return empty result on error (still include billing warning if available)
      return {
        memories: [],
        contextString: billingWarning,
        latencyMs: Date.now() - startTime,
      };
    }
  }

  /**
   * agent_end hook
   *
   * Called after the agent finishes processing.
   * Triggers fact extraction from the conversation.
   *
   * @param context - OpenClaw context
   * @returns Extraction result summary
   */
  async onAgentEnd(context: OpenClawContext): Promise<AgentEndResult> {
    this.ensureInitialized();
    const startTime = Date.now();

    try {
      // Increment turn counter
      this.state.turnCount++;

      // Check if extraction should run
      const shouldExtract = this.shouldExtractOnTurn();

      if (!shouldExtract) {
        return {
          factsExtracted: 0,
          factsStored: 0,
          processingTimeMs: Date.now() - startTime,
        };
      }

      // Check for explicit memory command
      const explicitCommand = parseExplicitMemoryCommand(context.userMessage);
      const trigger: ExtractionTrigger = explicitCommand.isMemoryCommand ? 'explicit' : 'post_turn';

      // Extract facts
      const extractionResult = await this.extractFacts(context, trigger);

      // Store extracted facts (with 403 handling)
      let storedCount: number;
      let quotaExceededMessage = '';
      try {
        storedCount = await this.storeExtractedFacts(extractionResult.facts);
      } catch (storeError) {
        // Check for 403 quota exceeded
        const errorMsg = storeError instanceof Error ? storeError.message : String(storeError);
        if (errorMsg.includes('403') || errorMsg.includes('quota') || errorMsg.includes('Quota')) {
          debugLog('Quota exceeded (403) during agent_end store:', errorMsg);

          // Invalidate billing cache so next before_agent_start refreshes
          try {
            if (fs.existsSync(BILLING_CACHE_PATH)) {
              fs.unlinkSync(BILLING_CACHE_PATH);
            }
          } catch (e) {
            debugLog('Failed to invalidate billing cache:', e);
          }

          quotaExceededMessage = `TotalReclaw quota exceeded. New memories cannot be stored until the quota resets next month or you upgrade your plan.`;

          return {
            factsExtracted: extractionResult.facts.length,
            factsStored: 0,
            processingTimeMs: Date.now() - startTime,
            quotaExceeded: true,
            quotaMessage: quotaExceededMessage,
          } as AgentEndResult;
        }
        // Re-throw non-quota errors
        throw storeError;
      }

      // Update last extraction timestamp
      this.state.lastExtraction = new Date();

      return {
        factsExtracted: extractionResult.facts.length,
        factsStored: storedCount,
        processingTimeMs: Date.now() - startTime,
      };
    } catch (error) {
      console.error('[TotalReclaw] onAgentEnd failed:', error);

      return {
        factsExtracted: 0,
        factsStored: 0,
        processingTimeMs: Date.now() - startTime,
      };
    }
  }

  /**
   * pre_compaction hook
   *
   * Called before conversation history is compacted.
   * Extracts facts from the full conversation history before it's lost.
   *
   * @param context - OpenClaw context
   * @returns Extraction result summary
   */
  async onPreCompaction(context: OpenClawContext): Promise<PreCompactionResult> {
    this.ensureInitialized();
    const startTime = Date.now();

    try {
      // Extract facts from full conversation history
      const extractionResult = await this.extractFacts(context, 'pre_compaction');

      // Get existing memories for deduplication
      const existingMemories = await this.getExistingMemories();

      // Deduplicate and store
      let duplicatesSkipped = 0;
      let factsStored = 0;

      for (const fact of extractionResult.facts) {
        if (fact.action === 'NOOP') {
          duplicatesSkipped++;
          continue;
        }

        if (fact.action === 'DELETE' && fact.existingFactId) {
          await this.client!.forget(fact.existingFactId);
          continue;
        }

        if (fact.importance >= this.config.minImportanceForAutoStore) {
          await this.storeFact(fact);
          factsStored++;
        }
      }

      // Update last extraction timestamp
      this.state.lastExtraction = new Date();

      return {
        factsExtracted: extractionResult.facts.length,
        factsStored,
        duplicatesSkipped,
        processingTimeMs: Date.now() - startTime,
      };
    } catch (error) {
      console.error('[TotalReclaw] onPreCompaction failed:', error);

      return {
        factsExtracted: 0,
        factsStored: 0,
        duplicatesSkipped: 0,
        processingTimeMs: Date.now() - startTime,
      };
    }
  }

  // ============================================================================
  // Tool Methods
  // ============================================================================

  /**
   * totalreclaw_remember tool
   *
   * Explicitly store a memory.
   *
   * @param params - Tool parameters
   * @returns Confirmation message
   */
  async remember(params: RememberToolParams): Promise<string> {
    this.ensureInitialized();

    try {
      const metadata: FactMetadata = {
        importance: (params.importance ?? this.config.minImportanceForAutoStore) / 10,
        source: 'explicit',
      };

      const factId = await this.client!.remember(params.text, metadata);

      return `Memory stored successfully with ID: ${factId}`;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Failed to store memory: ${message}`);
    }
  }

  /**
   * totalreclaw_recall tool
   *
   * Search for relevant memories.
   *
   * @param params - Tool parameters
   * @returns Search results
   */
  async recall(params: RecallToolParams): Promise<RerankedResult[]> {
    this.ensureInitialized();

    try {
      const k = params.k ?? this.config.maxMemoriesInContext;
      const results = await this.client!.recall(params.query, k);

      // Re-rank if reranker is ready
      if (this.reranker.isReady() && results.length > 0) {
        const facts = results.map(r => r.fact);
        const crossEncoderResults = await this.reranker.rerank(params.query, facts, k);

        return crossEncoderResults.map(ceResult => ({
          fact: ceResult.fact,
          score: ceResult.score,
          vectorScore: ceResult.vectorScore,
          textScore: ceResult.textScore,
          decayAdjustedScore: ceResult.decayAdjustedScore,
        }));
      }

      return results;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Failed to recall memories: ${message}`);
    }
  }

  /**
   * totalreclaw_forget tool
   *
   * Delete a specific memory.
   *
   * @param params - Tool parameters
   */
  async forget(params: ForgetToolParams): Promise<void> {
    this.ensureInitialized();

    try {
      await this.client!.forget(params.factId);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Failed to forget memory: ${message}`);
    }
  }

  /**
   * totalreclaw_export tool
   *
   * Export all memories for portability.
   *
   * @param params - Tool parameters
   * @returns Exported data as formatted string
   */
  async export(params: ExportToolParams): Promise<string> {
    this.ensureInitialized();

    try {
      const exportedData = await this.client!.export();

      if (params.format === 'markdown') {
        return this.formatExportAsMarkdown(exportedData);
      }

      return JSON.stringify(exportedData, null, 2);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Failed to export memories: ${message}`);
    }
  }

  /**
   * totalreclaw_status tool
   *
   * Check billing/subscription status.
   *
   * @returns Formatted status summary
   */
  async status(): Promise<string> {
    this.ensureInitialized();

    try {
      const { statusTool } = await import('./tools/status');
      const result = await statusTool(this.config.serverUrl, this.authKeyHex || '');

      if (!result.success) {
        throw new Error(result.error || 'Unknown error');
      }

      return result.formatted || 'No billing information available.';
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      throw new Error(`Failed to fetch billing status: ${message}`);
    }
  }

  // ============================================================================
  // State Management
  // ============================================================================

  /**
   * Get current turn count
   */
  getTurnCount(): number {
    return this.state.turnCount;
  }

  /**
   * Get cached memories from last search
   */
  getCachedMemories(): RerankedResult[] {
    return [...this.state.cachedMemories];
  }

  /**
   * Check if skill is initialized
   */
  isInitialized(): boolean {
    return this.state.isInitialized;
  }

  /**
   * Get the underlying TotalReclaw client
   */
  getClient(): TotalReclaw | null {
    return this.client;
  }

  /**
   * Get the current user ID
   */
  getUserId(): string | null {
    return this.client?.getUserId() ?? null;
  }

  /**
   * Get the salt (for credential persistence)
   */
  getSalt(): Buffer | null {
    return this.client?.getSalt() ?? null;
  }

  /**
   * Reset the turn counter
   */
  resetTurnCount(): void {
    this.state.turnCount = 0;
  }

  /**
   * Clear cached memories
   */
  clearCache(): void {
    this.state.cachedMemories = [];
  }

  /**
   * Get pending extractions
   */
  getPendingExtractions(): ExtractedFact[] {
    return [...this.state.pendingExtractions];
  }

  /**
   * Clear pending extractions
   */
  clearPendingExtractions(): void {
    this.state.pendingExtractions = [];
  }

  // ============================================================================
  // Private Methods
  // ============================================================================

  /**
   * Ensure the skill is initialized
   */
  private ensureInitialized(): void {
    if (!this.state.isInitialized || !this.client) {
      throw new TotalReclawError(
        TotalReclawErrorCode.NOT_REGISTERED,
        'TotalReclaw skill not initialized. Call init() first.'
      );
    }
  }

  /**
   * Check if extraction should run on this turn
   */
  private shouldExtractOnTurn(): boolean {
    // Extract if we've hit the turn interval
    if (this.state.turnCount % this.config.autoExtractEveryTurns === 0) {
      return true;
    }

    // Always extract on turn 1
    if (this.state.turnCount === 1) {
      return true;
    }

    return false;
  }

  /**
   * Extract facts using the configured extractor
   */
  private async extractFacts(
    context: OpenClawContext,
    trigger: ExtractionTrigger
  ): Promise<ExtractionResult> {
    if (!this.extractor) {
      console.warn('[TotalReclaw] No extractor configured, skipping fact extraction');
      return {
        facts: [],
        rawResponse: '',
        processingTimeMs: 0,
      };
    }

    return this.extractor.extractFacts(context, trigger);
  }

  /**
   * Store extracted facts
   */
  private async storeExtractedFacts(facts: ExtractedFact[]): Promise<number> {
    let storedCount = 0;

    for (const fact of facts) {
      // Skip NOOP actions
      if (fact.action === 'NOOP') {
        continue;
      }

      // Handle DELETE
      if (fact.action === 'DELETE' && fact.existingFactId) {
        await this.client!.forget(fact.existingFactId);
        continue;
      }

      // Handle UPDATE by deleting old and adding new
      if (fact.action === 'UPDATE' && fact.existingFactId) {
        await this.client!.forget(fact.existingFactId);
      }

      // Check importance threshold
      if (fact.importance < this.config.minImportanceForAutoStore) {
        continue;
      }

      // Store the fact
      await this.storeFact(fact);
      storedCount++;
    }

    return storedCount;
  }

  /**
   * Store a single fact
   */
  private async storeFact(fact: ExtractedFact): Promise<string> {
    const metadata: FactMetadata = {
      importance: fact.importance / 10,
      source: 'extracted',
      tags: [fact.type],
    };

    return this.client!.remember(fact.factText, metadata);
  }

  /**
   * Get existing memories for deduplication
   */
  private async getExistingMemories(): Promise<import('./extraction/dedup').ExistingFact[]> {
    // This would need a server endpoint to fetch all memories
    // For now, return empty array
    return [];
  }

  /**
   * Format memories for context injection
   */
  private formatMemoriesForContext(memories: RerankedResult[]): string {
    if (memories.length === 0) {
      return '';
    }

    const lines: string[] = [
      '## Relevant Memories',
      '',
      'Here are some relevant memories from previous conversations:',
      '',
    ];

    for (let i = 0; i < memories.length; i++) {
      const memory = memories[i];
      const importance = Math.round((memory.fact.metadata.importance ?? 0.5) * 10);
      const age = this.formatAge(memory.fact.createdAt);

      lines.push(`${i + 1}. ${memory.fact.text}`);
      lines.push(`   (importance: ${importance}/10, ${age})`);
      lines.push('');
    }

    return lines.join('\n');
  }

  /**
   * Format age of a memory
   */
  private formatAge(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins === 1 ? '' : 's'} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;

    return date.toLocaleDateString();
  }

  /**
   * Format exported data as markdown
   */
  private formatExportAsMarkdown(data: ExportedData): string {
    const lines: string[] = [
      '# TotalReclaw Export',
      '',
      `**Exported at:** ${data.exportedAt.toISOString()}`,
      `**Version:** ${data.version}`,
      '',
      '## Configuration',
      '',
      '```json',
      JSON.stringify(data.lshConfig, null, 2),
      '```',
      '',
      '## Key Parameters',
      '',
      `- Salt: ${data.keyParams.salt.toString('base64')}`,
      `- Memory Cost: ${data.keyParams.memoryCost}`,
      `- Time Cost: ${data.keyParams.timeCost}`,
      `- Parallelism: ${data.keyParams.parallelism}`,
      '',
      '## Memories',
      '',
      `Total memories: ${data.facts.length}`,
      '',
      '_Note: Full memory export requires server support._',
      '',
    ];

    return lines.join('\n');
  }
}

// ============================================================================
// Factory Function
// ============================================================================

/**
 * Create an TotalReclaw skill instance with default configuration
 */
export function createTotalReclawSkill(
  config?: Partial<TotalReclawSkillConfig>
): TotalReclawSkill {
  return new TotalReclawSkill(config);
}

// ============================================================================
// Default Export
// ============================================================================

export default TotalReclawSkill;
