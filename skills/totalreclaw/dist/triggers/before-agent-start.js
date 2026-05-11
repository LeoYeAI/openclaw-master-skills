"use strict";
/**
 * TotalReclaw Skill - Before Agent Start Hook
 *
 * This hook runs BEFORE the agent processes the user's message.
 * It retrieves relevant memories and injects them into the context.
 *
 * Flow:
 * 1. Retrieve relevant memories using TotalReclaw client
 * 2. Rerank with cross-encoder for high-quality results
 * 3. Format memories for context injection
 * 4. Return BeforeAgentStartResult with memories and contextString
 *
 * Target latency: <100ms total
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
exports.formatMemoriesForContext = formatMemoriesForContext;
exports.beforeAgentStart = beforeAgentStart;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const cross_encoder_1 = require("../reranker/cross-encoder");
const debug_1 = require("../debug");
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
// Default Context Formatter
// ============================================================================
/**
 * Format retrieved memories into a context string for injection
 *
 * This format is designed to be:
 * - Clear to the LLM about what these memories represent
 * - Easy to parse visually
 * - Compact to minimize token usage
 */
function formatMemoriesForContext(memories) {
    if (memories.length === 0) {
        return '';
    }
    const lines = [
        '<memory_context>',
        '  <description>Relevant memories about the user retrieved from long-term storage</description>',
        '  <memories>',
    ];
    for (let i = 0; i < memories.length; i++) {
        const memory = memories[i];
        const fact = memory.fact;
        // Format each memory with type and importance indicators
        const memoryType = getMemoryType(fact);
        const typeEmoji = getTypeIndicator(memoryType);
        const importanceBar = getImportanceBar(memory.score);
        lines.push(`    <memory rank="${i + 1}" score="${memory.score.toFixed(2)}">`);
        lines.push(`      <type>${memoryType}</type>`);
        lines.push(`      <importance>${importanceBar}</importance>`);
        lines.push(`      <content>${typeEmoji} ${escapeXml(fact.text)}</content>`);
        lines.push(`    </memory>`);
    }
    lines.push('  </memories>');
    lines.push('</memory_context>');
    return lines.join('\n');
}
/**
 * Get memory type from fact metadata
 */
function getMemoryType(fact) {
    // Check tags for type information
    if (fact.metadata?.tags && fact.metadata.tags.length > 0) {
        const typeTag = fact.metadata.tags.find(t => ['fact', 'preference', 'decision', 'episodic', 'goal'].includes(t));
        if (typeTag)
            return typeTag;
    }
    return 'fact';
}
/**
 * Get a visual indicator for memory type
 */
function getTypeIndicator(type) {
    switch (type) {
        case 'preference':
            return '[PREF]';
        case 'decision':
            return '[DEC]';
        case 'goal':
            return '[GOAL]';
        case 'episodic':
            return '[EPIS]';
        default:
            return '[FACT]';
    }
}
/**
 * Get a visual importance bar
 */
function getImportanceBar(score) {
    const filled = Math.round(score * 5);
    const empty = 5 - filled;
    return '█'.repeat(filled) + '░'.repeat(empty);
}
/**
 * Escape XML special characters
 */
function escapeXml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');
}
// ============================================================================
// Main Hook Function
// ============================================================================
/**
 * Execute the before-agent-start hook
 *
 * This retrieves relevant memories and prepares them for context injection.
 *
 * @param context - OpenClaw context containing user message and history
 * @param options - Hook options including client and configuration
 * @returns BeforeAgentStartResult with memories and formatted context string
 *
 * @example
 * ```typescript
 * const result = await beforeAgentStart(context, {
 *   client: openMemoryClient,
 *   config: skillConfig,
 * });
 *
 * // Inject result.contextString into the agent's context
 * console.log(`Retrieved ${result.memories.length} memories in ${result.latencyMs}ms`);
 * ```
 */
async function beforeAgentStart(context, options) {
    const startTime = Date.now();
    const metrics = {
        searchLatencyMs: 0,
        rerankLatencyMs: 0,
        formatLatencyMs: 0,
        totalLatencyMs: 0,
        candidatesRetrieved: 0,
        memoriesReturned: 0,
    };
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
        if (needsRefresh && options.authKeyHex) {
            // Make API call to refresh cache
            const serverUrl = options.config.serverUrl.replace(/\/+$/, '');
            const response = await fetch(`${serverUrl}/v1/billing/status`, {
                headers: { 'Authorization': `Bearer ${options.authKeyHex}` }
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
        (0, debug_1.debugLog)(!!options.debug, 'billing cache check failed:', e);
    }
    try {
        // Step 1: Build search query from user message and recent context
        const searchQuery = buildSearchQuery(context);
        (0, debug_1.debugLog)(!!options.debug, `Searching for: "${searchQuery}"`);
        // Step 2: Retrieve candidate memories from TotalReclaw
        const searchStart = Date.now();
        const candidates = await options.client.recall(searchQuery, options.config.maxMemoriesInContext * 3 // Get more candidates for reranking
        );
        metrics.searchLatencyMs = Date.now() - searchStart;
        metrics.candidatesRetrieved = candidates.length;
        (0, debug_1.debugLog)(!!options.debug, `Retrieved ${candidates.length} candidates in ${metrics.searchLatencyMs}ms`);
        // If no candidates, return empty result early
        if (candidates.length === 0) {
            return {
                memories: [],
                contextString: '',
                latencyMs: Date.now() - startTime,
            };
        }
        // Step 3: Rerank with cross-encoder for high-quality results
        const rerankStart = Date.now();
        const reranker = options.reranker || (0, cross_encoder_1.getCrossEncoderReranker)();
        // Ensure reranker is loaded
        if (!reranker.isReady()) {
            await reranker.load(options.config.rerankerModel);
        }
        // Extract facts from reranked results for cross-encoder
        const candidateFacts = candidates.map(r => r.fact);
        // Rerank using cross-encoder
        const rerankedResults = await reranker.rerank(searchQuery, candidateFacts, options.config.maxMemoriesInContext);
        metrics.rerankLatencyMs = Date.now() - rerankStart;
        (0, debug_1.debugLog)(!!options.debug, `Reranked in ${metrics.rerankLatencyMs}ms`);
        // Convert CrossEncoderResult back to RerankedResult format
        const memories = rerankedResults.map(result => ({
            fact: result.fact,
            score: result.score,
            vectorScore: result.vectorScore,
            textScore: result.textScore,
            decayAdjustedScore: result.decayAdjustedScore,
        }));
        // Step 4: Format memories for context injection
        const formatStart = Date.now();
        const formatter = options.contextFormatter || formatMemoriesForContext;
        const contextString = formatter(memories) + billingWarning;
        metrics.formatLatencyMs = Date.now() - formatStart;
        metrics.memoriesReturned = memories.length;
        // Calculate total latency
        metrics.totalLatencyMs = Date.now() - startTime;
        if (options.debug) {
            (0, debug_1.debugLog)(true, `Hook completed in ${metrics.totalLatencyMs}ms`);
            (0, debug_1.debugLog)(true, `  Search: ${metrics.searchLatencyMs}ms`);
            (0, debug_1.debugLog)(true, `  Rerank: ${metrics.rerankLatencyMs}ms`);
            (0, debug_1.debugLog)(true, `  Format: ${metrics.formatLatencyMs}ms`);
        }
        return {
            memories,
            contextString,
            latencyMs: metrics.totalLatencyMs,
        };
    }
    catch (error) {
        (0, debug_1.debugLog)(!!options.debug, 'beforeAgentStart recall/rerank failed:', error);
        // Provide a helpful hint for authentication failures
        const errorMsg = error instanceof Error ? error.message : String(error);
        const isAuthFailure = errorMsg.includes('401') || errorMsg.includes('UNAUTHORIZED') || errorMsg.includes('AUTH_FAILED');
        const authHint = isAuthFailure
            ? '\n\nTotalReclaw authentication failed. If using a recovery phrase, check that all 12 words are in the correct order and spelled correctly.'
            : '';
        // Return empty result on error (still include billing warning if available)
        return {
            memories: [],
            contextString: billingWarning + authHint,
            latencyMs: Date.now() - startTime,
        };
    }
}
// ============================================================================
// Helper Functions
// ============================================================================
/**
 * Build a search query from the OpenClaw context
 *
 * Combines:
 * - Current user message (primary signal)
 * - Recent conversation history (context signal)
 */
function buildSearchQuery(context) {
    const parts = [];
    // Add current user message (most important)
    if (context.userMessage) {
        parts.push(context.userMessage);
    }
    // Add recent conversation history for context
    // Limit to last 2 turns to keep query focused
    const recentHistory = context.history.slice(-2);
    for (const turn of recentHistory) {
        // Only add if not too long
        if (turn.content.length < 200) {
            parts.push(turn.content);
        }
    }
    // Join with newlines and truncate to reasonable length
    const query = parts.join('\n').slice(0, 500);
    return query;
}
// ============================================================================
// Exports
// ============================================================================
exports.default = beforeAgentStart;
//# sourceMappingURL=before-agent-start.js.map