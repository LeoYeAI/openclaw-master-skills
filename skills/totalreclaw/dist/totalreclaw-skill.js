"use strict";
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
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.TotalReclawSkill = void 0;
exports.createTotalReclawSkill = createTotalReclawSkill;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const client_1 = require("@totalreclaw/client");
const config_1 = require("./config");
const cross_encoder_1 = require("./reranker/cross-encoder");
const extraction_1 = require("./extraction");
const debug_1 = require("./debug");
// ============================================================================
// LLM Client Adapter
// ============================================================================
/**
 * Adapter to make OpenClaw's LLM available to the extraction module
 */
class OpenClawLLMAdapter {
    completeFn;
    constructor(completeFn) {
        this.completeFn = completeFn;
    }
    async complete(prompt) {
        return this.completeFn(prompt);
    }
}
// ============================================================================
// Vector Store Adapter
// ============================================================================
/**
 * Adapter to make TotalReclaw client available as a vector store
 */
class TotalReclawVectorStoreAdapter {
    client;
    constructor(client) {
        this.client = client;
    }
    async findSimilar(embedding, k) {
        // Note: This is a simplified implementation.
        // In practice, we'd need a server endpoint that supports embedding-based search.
        // For now, we'll return empty and let the deduplicator fall back to text comparison.
        console.warn('Vector-based similarity search not yet implemented in vector store adapter');
        return [];
    }
    async getEmbedding(text) {
        // The TotalReclaw client handles embedding internally
        // We'll use a hash-based approach for dedup purposes
        return this.createDeterministicEmbedding(text);
    }
    /**
     * Create a deterministic embedding from text for dedup purposes
     */
    createDeterministicEmbedding(text) {
        // Simple hash-based embedding for dedup comparison
        // Not as accurate as real embeddings but works for similarity comparison
        const dimension = 384;
        const embedding = new Array(dimension).fill(0);
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
function isBillingCacheData(data) {
    if (typeof data !== 'object' || data === null)
        return false;
    const d = data;
    return (typeof d.tier === 'string' &&
        typeof d.free_writes_used === 'number' &&
        typeof d.free_writes_limit === 'number' &&
        typeof d.free_reads_used === 'number' &&
        typeof d.free_reads_limit === 'number' &&
        typeof d.checked_at === 'number');
}
// ============================================================================
// TotalReclawSkill Class
// ============================================================================
/**
 * Main TotalReclaw Skill Class
 *
 * Integrates TotalReclaw with OpenClaw through lifecycle hooks and tools.
 */
class TotalReclawSkill {
    config;
    client = null;
    reranker;
    extractor = null;
    state;
    llmAdapter = null;
    vectorStoreAdapter = null;
    authKeyHex = null;
    /**
     * Create a new TotalReclawSkill instance
     *
     * @param config - Skill configuration (partial, will be merged with defaults)
     */
    constructor(config = {}) {
        // Load and merge configuration
        this.config = (0, config_1.loadConfig)({ overrides: config });
        // Validate configuration
        (0, config_1.assertValidConfig)(this.config);
        // Initialize reranker
        this.reranker = new cross_encoder_1.CrossEncoderReranker({
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
    async init(llmCompleteFn) {
        try {
            // Initialize TotalReclaw client
            this.client = new client_1.TotalReclaw({
                serverUrl: this.config.serverUrl,
            });
            await this.client.init();
            // Check if we have credentials
            let isNewUser = false;
            if (this.config.masterPassword) {
                if (this.config.userId && this.config.salt) {
                    // Login with existing credentials
                    await this.client.login(this.config.userId, this.config.masterPassword, this.config.salt);
                    // Derive auth key hex for billing API calls
                    try {
                        const { authKey } = await (0, client_1.deriveKeys)(this.config.masterPassword, this.config.salt);
                        this.authKeyHex = authKey.toString('hex');
                    }
                    catch (e) {
                        (0, debug_1.debugLog)('Failed to derive auth key for billing:', e);
                    }
                }
                else {
                    // Register new user
                    const userId = await this.client.register(this.config.masterPassword);
                    isNewUser = true;
                    // Derive auth key hex for billing API calls
                    const salt = this.client.getSalt();
                    if (salt) {
                        try {
                            const { authKey } = await (0, client_1.deriveKeys)(this.config.masterPassword, salt);
                            this.authKeyHex = authKey.toString('hex');
                        }
                        catch (e) {
                            (0, debug_1.debugLog)('Failed to derive auth key for billing:', e);
                        }
                    }
                    // Store credentials for future use (caller should persist these)
                    (0, debug_1.debugLog)(`Registered new user: ${userId}`);
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
                this.extractor = (0, extraction_1.createFactExtractor)(this.llmAdapter, this.vectorStoreAdapter, { minImportance: this.config.minImportanceForAutoStore });
            }
            this.state.isInitialized = true;
            return {
                success: true,
                isNewUser,
                userId: this.client.getUserId() ?? undefined,
            };
        }
        catch (error) {
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
    setLLMProvider(completeFn) {
        this.llmAdapter = new OpenClawLLMAdapter(completeFn);
        if (this.client) {
            this.vectorStoreAdapter = new TotalReclawVectorStoreAdapter(this.client);
        }
        this.extractor = (0, extraction_1.createFactExtractor)(this.llmAdapter, this.vectorStoreAdapter ?? undefined, { minImportance: this.config.minImportanceForAutoStore });
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
    async onBeforeAgentStart(context) {
        this.ensureInitialized();
        const startTime = Date.now();
        // Billing cache check
        let billingWarning = '';
        try {
            let needsRefresh = true;
            let billingData = null;
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
                    headers: { 'Authorization': `Bearer ${this.authKeyHex}` }
                });
                if (response.ok) {
                    const parsed = await response.json();
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
        }
        catch (e) {
            (0, debug_1.debugLog)('billing cache check failed:', e);
        }
        try {
            // Search for relevant memories based on user message
            const memories = await this.client.recall(context.userMessage, this.config.maxMemoriesInContext);
            // Re-rank using cross-encoder if available
            let rankedMemories;
            if (this.reranker.isReady() && memories.length > 0) {
                const facts = memories.map(m => m.fact);
                const crossEncoderResults = await this.reranker.rerank(context.userMessage, facts, this.config.maxMemoriesInContext);
                // Map back to RerankedResult format
                rankedMemories = crossEncoderResults.map(ceResult => ({
                    fact: ceResult.fact,
                    score: ceResult.score,
                    vectorScore: ceResult.vectorScore,
                    textScore: ceResult.textScore,
                    decayAdjustedScore: ceResult.decayAdjustedScore,
                }));
            }
            else {
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
        }
        catch (error) {
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
    async onAgentEnd(context) {
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
            const explicitCommand = (0, extraction_1.parseExplicitMemoryCommand)(context.userMessage);
            const trigger = explicitCommand.isMemoryCommand ? 'explicit' : 'post_turn';
            // Extract facts
            const extractionResult = await this.extractFacts(context, trigger);
            // Store extracted facts (with 403 handling)
            let storedCount;
            let quotaExceededMessage = '';
            try {
                storedCount = await this.storeExtractedFacts(extractionResult.facts);
            }
            catch (storeError) {
                // Check for 403 quota exceeded
                const errorMsg = storeError instanceof Error ? storeError.message : String(storeError);
                if (errorMsg.includes('403') || errorMsg.includes('quota') || errorMsg.includes('Quota')) {
                    (0, debug_1.debugLog)('Quota exceeded (403) during agent_end store:', errorMsg);
                    // Invalidate billing cache so next before_agent_start refreshes
                    try {
                        if (fs.existsSync(BILLING_CACHE_PATH)) {
                            fs.unlinkSync(BILLING_CACHE_PATH);
                        }
                    }
                    catch (e) {
                        (0, debug_1.debugLog)('Failed to invalidate billing cache:', e);
                    }
                    quotaExceededMessage = `TotalReclaw quota exceeded. New memories cannot be stored until the quota resets next month or you upgrade your plan.`;
                    return {
                        factsExtracted: extractionResult.facts.length,
                        factsStored: 0,
                        processingTimeMs: Date.now() - startTime,
                        quotaExceeded: true,
                        quotaMessage: quotaExceededMessage,
                    };
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
        }
        catch (error) {
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
    async onPreCompaction(context) {
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
                    await this.client.forget(fact.existingFactId);
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
        }
        catch (error) {
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
    async remember(params) {
        this.ensureInitialized();
        try {
            const metadata = {
                importance: (params.importance ?? this.config.minImportanceForAutoStore) / 10,
                source: 'explicit',
            };
            const factId = await this.client.remember(params.text, metadata);
            return `Memory stored successfully with ID: ${factId}`;
        }
        catch (error) {
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
    async recall(params) {
        this.ensureInitialized();
        try {
            const k = params.k ?? this.config.maxMemoriesInContext;
            const results = await this.client.recall(params.query, k);
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
        }
        catch (error) {
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
    async forget(params) {
        this.ensureInitialized();
        try {
            await this.client.forget(params.factId);
        }
        catch (error) {
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
    async export(params) {
        this.ensureInitialized();
        try {
            const exportedData = await this.client.export();
            if (params.format === 'markdown') {
                return this.formatExportAsMarkdown(exportedData);
            }
            return JSON.stringify(exportedData, null, 2);
        }
        catch (error) {
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
    async status() {
        this.ensureInitialized();
        try {
            const { statusTool } = await Promise.resolve().then(() => __importStar(require('./tools/status')));
            const result = await statusTool(this.config.serverUrl, this.authKeyHex || '');
            if (!result.success) {
                throw new Error(result.error || 'Unknown error');
            }
            return result.formatted || 'No billing information available.';
        }
        catch (error) {
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
    getTurnCount() {
        return this.state.turnCount;
    }
    /**
     * Get cached memories from last search
     */
    getCachedMemories() {
        return [...this.state.cachedMemories];
    }
    /**
     * Check if skill is initialized
     */
    isInitialized() {
        return this.state.isInitialized;
    }
    /**
     * Get the underlying TotalReclaw client
     */
    getClient() {
        return this.client;
    }
    /**
     * Get the current user ID
     */
    getUserId() {
        return this.client?.getUserId() ?? null;
    }
    /**
     * Get the salt (for credential persistence)
     */
    getSalt() {
        return this.client?.getSalt() ?? null;
    }
    /**
     * Reset the turn counter
     */
    resetTurnCount() {
        this.state.turnCount = 0;
    }
    /**
     * Clear cached memories
     */
    clearCache() {
        this.state.cachedMemories = [];
    }
    /**
     * Get pending extractions
     */
    getPendingExtractions() {
        return [...this.state.pendingExtractions];
    }
    /**
     * Clear pending extractions
     */
    clearPendingExtractions() {
        this.state.pendingExtractions = [];
    }
    // ============================================================================
    // Private Methods
    // ============================================================================
    /**
     * Ensure the skill is initialized
     */
    ensureInitialized() {
        if (!this.state.isInitialized || !this.client) {
            throw new client_1.TotalReclawError(client_1.TotalReclawErrorCode.NOT_REGISTERED, 'TotalReclaw skill not initialized. Call init() first.');
        }
    }
    /**
     * Check if extraction should run on this turn
     */
    shouldExtractOnTurn() {
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
    async extractFacts(context, trigger) {
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
    async storeExtractedFacts(facts) {
        let storedCount = 0;
        for (const fact of facts) {
            // Skip NOOP actions
            if (fact.action === 'NOOP') {
                continue;
            }
            // Handle DELETE
            if (fact.action === 'DELETE' && fact.existingFactId) {
                await this.client.forget(fact.existingFactId);
                continue;
            }
            // Handle UPDATE by deleting old and adding new
            if (fact.action === 'UPDATE' && fact.existingFactId) {
                await this.client.forget(fact.existingFactId);
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
    async storeFact(fact) {
        const metadata = {
            importance: fact.importance / 10,
            source: 'extracted',
            tags: [fact.type],
        };
        return this.client.remember(fact.factText, metadata);
    }
    /**
     * Get existing memories for deduplication
     */
    async getExistingMemories() {
        // This would need a server endpoint to fetch all memories
        // For now, return empty array
        return [];
    }
    /**
     * Format memories for context injection
     */
    formatMemoriesForContext(memories) {
        if (memories.length === 0) {
            return '';
        }
        const lines = [
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
    formatAge(date) {
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        if (diffMins < 1)
            return 'just now';
        if (diffMins < 60)
            return `${diffMins} minute${diffMins === 1 ? '' : 's'} ago`;
        if (diffHours < 24)
            return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
        if (diffDays < 7)
            return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;
        return date.toLocaleDateString();
    }
    /**
     * Format exported data as markdown
     */
    formatExportAsMarkdown(data) {
        const lines = [
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
exports.TotalReclawSkill = TotalReclawSkill;
// ============================================================================
// Factory Function
// ============================================================================
/**
 * Create an TotalReclaw skill instance with default configuration
 */
function createTotalReclawSkill(config) {
    return new TotalReclawSkill(config);
}
// ============================================================================
// Default Export
// ============================================================================
exports.default = TotalReclawSkill;
//# sourceMappingURL=totalreclaw-skill.js.map