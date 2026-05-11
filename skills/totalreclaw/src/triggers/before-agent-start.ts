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

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import type { TotalReclaw } from '@totalreclaw/client';
import type { RerankedResult, Fact } from '@totalreclaw/client';
import type {
  BeforeAgentStartResult,
  OpenClawContext,
  TotalReclawSkillConfig,
} from '../types';
import { CrossEncoderReranker, getCrossEncoderReranker } from '../reranker/cross-encoder';
import { debugLog } from '../debug';

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

/**
 * Options for the before-agent-start hook
 */
export interface BeforeAgentStartOptions {
  /** TotalReclaw client instance */
  client: TotalReclaw;
  /** Skill configuration */
  config: TotalReclawSkillConfig;
  /** Cross-encoder reranker instance (optional, will create if not provided) */
  reranker?: CrossEncoderReranker;
  /** Custom context formatter (optional) */
  contextFormatter?: (memories: RerankedResult[]) => string;
  /** Whether to enable debug logging */
  debug?: boolean;
  /** Hex-encoded auth key for billing API calls (optional) */
  authKeyHex?: string;
}

/**
 * Internal metrics for performance tracking
 */
interface HookMetrics {
  searchLatencyMs: number;
  rerankLatencyMs: number;
  formatLatencyMs: number;
  totalLatencyMs: number;
  candidatesRetrieved: number;
  memoriesReturned: number;
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
export function formatMemoriesForContext(memories: RerankedResult[]): string {
  if (memories.length === 0) {
    return '';
  }

  const lines: string[] = [
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
function getMemoryType(fact: Fact): string {
  // Check tags for type information
  if (fact.metadata?.tags && fact.metadata.tags.length > 0) {
    const typeTag = fact.metadata.tags.find(t =>
      ['fact', 'preference', 'decision', 'episodic', 'goal', 'context', 'summary'].includes(t)
    );
    if (typeTag) return typeTag;
  }
  return 'fact';
}

/**
 * Get a visual indicator for memory type
 */
function getTypeIndicator(type: string): string {
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
function getImportanceBar(score: number): string {
  const filled = Math.round(score * 5);
  const empty = 5 - filled;
  return '█'.repeat(filled) + '░'.repeat(empty);
}

/**
 * Escape XML special characters
 */
function escapeXml(text: string): string {
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
export async function beforeAgentStart(
  context: OpenClawContext,
  options: BeforeAgentStartOptions
): Promise<BeforeAgentStartResult> {
  const startTime = Date.now();
  const metrics: HookMetrics = {
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
    let billingData: BillingCacheData | null = null;

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
        headers: { 'Authorization': `Bearer ${options.authKeyHex}`, 'X-TotalReclaw-Client': 'openclaw-plugin' }
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
    debugLog(!!options.debug, 'billing cache check failed:', e);
  }

  try {
    // Step 1: Build search query from user message and recent context
    const searchQuery = buildSearchQuery(context);

    debugLog(!!options.debug, `Searching for: "${searchQuery}"`);

    // Step 2: Retrieve candidate memories from TotalReclaw
    const searchStart = Date.now();
    const candidates = await options.client.recall(
      searchQuery,
      options.config.maxMemoriesInContext * 3 // Get more candidates for reranking
    );
    metrics.searchLatencyMs = Date.now() - searchStart;
    metrics.candidatesRetrieved = candidates.length;

    debugLog(!!options.debug, `Retrieved ${candidates.length} candidates in ${metrics.searchLatencyMs}ms`);

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
    const reranker = options.reranker || getCrossEncoderReranker();

    // Ensure reranker is loaded
    if (!reranker.isReady()) {
      await reranker.load(options.config.rerankerModel);
    }

    // Extract facts from reranked results for cross-encoder
    const candidateFacts: Fact[] = candidates.map(r => r.fact);

    // Rerank using cross-encoder
    const rerankedResults = await reranker.rerank(
      searchQuery,
      candidateFacts,
      options.config.maxMemoriesInContext
    );
    metrics.rerankLatencyMs = Date.now() - rerankStart;

    debugLog(!!options.debug, `Reranked in ${metrics.rerankLatencyMs}ms`);

    // Convert CrossEncoderResult back to RerankedResult format
    const memories: RerankedResult[] = rerankedResults.map(result => ({
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
      debugLog(true, `Hook completed in ${metrics.totalLatencyMs}ms`);
      debugLog(true, `  Search: ${metrics.searchLatencyMs}ms`);
      debugLog(true, `  Rerank: ${metrics.rerankLatencyMs}ms`);
      debugLog(true, `  Format: ${metrics.formatLatencyMs}ms`);
    }

    return {
      memories,
      contextString,
      latencyMs: metrics.totalLatencyMs,
    };
  } catch (error) {
    debugLog(!!options.debug, 'beforeAgentStart recall/rerank failed:', error);

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
function buildSearchQuery(context: OpenClawContext): string {
  const parts: string[] = [];

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

export default beforeAgentStart;
