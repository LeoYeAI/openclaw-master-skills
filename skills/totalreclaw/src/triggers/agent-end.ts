/**
 * TotalReclaw Skill - Agent End Hook
 *
 * This hook runs AFTER the agent completes its turn.
 * It extracts facts from the recent conversation and stores them.
 *
 * Flow:
 * 1. Check turn counter (only extract every N turns)
 * 2. Extract facts from recent conversation
 * 3. Deduplicate against existing memories
 * 4. Store high-importance facts
 * 5. Return AgentEndResult with stats
 *
 * This hook is ASYNC and does NOT block the user.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import type { TotalReclaw } from '@totalreclaw/client';
import type {
  AgentEndResult,
  OpenClawContext,
  TotalReclawSkillConfig,
  ExtractedFact,
  SkillState,
} from '../types';
import {
  FactExtractor,
  createFactExtractor,
  isExplicitMemoryCommand,
  type LLMClient,
  type VectorStoreClient,
} from '../extraction';
import { debugLog } from '../debug';

const BILLING_CACHE_PATH = path.join(os.homedir(), '.totalreclaw', 'billing-cache.json');

// Hard cap on facts per extraction to prevent LLM over-extraction from dense conversations
const MAX_FACTS_PER_EXTRACTION = 15;

// ============================================================================
// Types
// ============================================================================

/**
 * Options for the agent-end hook
 */
export interface AgentEndOptions {
  /** TotalReclaw client instance */
  client: TotalReclaw;
  /** Skill configuration */
  config: TotalReclawSkillConfig;
  /** Skill state (for turn tracking) */
  state: SkillState;
  /** LLM client for extraction */
  llmClient: LLMClient;
  /** Vector store client for deduplication (optional) */
  vectorStoreClient?: VectorStoreClient;
  /** Custom fact extractor (optional) */
  extractor?: FactExtractor;
  /** Whether to enable debug logging */
  debug?: boolean;
  /** Whether to run asynchronously (don't await completion) */
  async?: boolean;
}

/**
 * Internal extraction result
 */
interface ExtractionResult {
  factsExtracted: number;
  factsStored: number;
  factsSkipped: number;
  processingTimeMs: number;
  quotaExceeded?: boolean;
  quotaMessage?: string;
}

// ============================================================================
// Main Hook Function
// ============================================================================

/**
 * Execute the agent-end hook
 *
 * This extracts facts from the conversation and stores them asynchronously.
 *
 * @param context - OpenClaw context containing user message and history
 * @param options - Hook options including client and configuration
 * @returns AgentEndResult with extraction and storage stats
 *
 * @example
 * ```typescript
 * const result = await agentEnd(context, {
 *   client: openMemoryClient,
 *   config: skillConfig,
 *   state: skillState,
 *   llmClient: myLLMClient,
 * });
 *
 * console.log(`Extracted ${result.factsExtracted} facts, stored ${result.factsStored}`);
 * ```
 */
export async function agentEnd(
  context: OpenClawContext,
  options: AgentEndOptions
): Promise<AgentEndResult> {
  const startTime = Date.now();

  // Update turn counter
  options.state.turnCount++;

  debugLog(!!options.debug, `Agent end hook - Turn ${options.state.turnCount}`);

  try {
    // Step 1: Check if we should extract this turn
    const shouldExtract = shouldExtractThisTurn(context, options);

    if (!shouldExtract) {
      debugLog(!!options.debug, `Skipping extraction this turn`);

      return {
        factsExtracted: 0,
        factsStored: 0,
        processingTimeMs: Date.now() - startTime,
      };
    }

    // Step 2: Run extraction (can be async)
    if (options.async) {
      // Fire and forget - don't await
      runExtractionAsync(context, options).catch(error => {
        console.error('[TotalReclaw] Async extraction failed:', error);
      });

      return {
        factsExtracted: 0, // Will be updated asynchronously
        factsStored: 0,
        processingTimeMs: Date.now() - startTime,
      };
    }

    // Step 3: Run extraction synchronously
    const result = await runExtraction(context, options);

    // Propagate quota exceeded info
    if (result.quotaExceeded) {
      return {
        factsExtracted: result.factsExtracted,
        factsStored: result.factsStored,
        processingTimeMs: Date.now() - startTime,
        quotaExceeded: true,
        quotaMessage: result.quotaMessage,
      };
    }

    return {
      factsExtracted: result.factsExtracted,
      factsStored: result.factsStored,
      processingTimeMs: Date.now() - startTime,
    };
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Unknown error';
    console.error('[TotalReclaw] agentEnd hook failed:', errorMsg);

    return {
      factsExtracted: 0,
      factsStored: 0,
      processingTimeMs: Date.now() - startTime,
    };
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Determine if we should extract facts this turn
 */
function shouldExtractThisTurn(
  context: OpenClawContext,
  options: AgentEndOptions
): boolean {
  const { config, state } = options;

  // Always extract for explicit memory commands
  if (isExplicitMemoryCommand(context.userMessage)) {
    debugLog(!!options.debug, `Explicit memory command detected`);
    return true;
  }

  // Check if turn counter matches extraction interval
  if (state.turnCount % config.autoExtractEveryTurns === 0) {
    return true;
  }

  // Check if we have pending extractions
  if (state.pendingExtractions.length > 0) {
    return true;
  }

  return false;
}

/**
 * Run extraction asynchronously (fire and forget)
 */
async function runExtractionAsync(
  context: OpenClawContext,
  options: AgentEndOptions
): Promise<void> {
  const result = await runExtraction(context, options);

  debugLog(!!options.debug,
    `Async extraction completed: ${result.factsExtracted} extracted, ` +
    `${result.factsStored} stored, ${result.factsSkipped} skipped`
  );
}

/**
 * Run the actual extraction and storage
 */
async function runExtraction(
  context: OpenClawContext,
  options: AgentEndOptions
): Promise<ExtractionResult> {
  const result: ExtractionResult = {
    factsExtracted: 0,
    factsStored: 0,
    factsSkipped: 0,
    processingTimeMs: 0,
  };

  const startTime = Date.now();

  try {
    // Get or create fact extractor
    const extractor = options.extractor || createFactExtractor(
      options.llmClient,
      options.vectorStoreClient,
      {
        minImportance: options.config.minImportanceForAutoStore,
        postTurnWindow: 3, // Last 3 turns
      }
    );

    // Determine extraction trigger
    const trigger = isExplicitMemoryCommand(context.userMessage) ? 'explicit' : 'post_turn';

    // Extract facts from conversation
    const extractionResult = await extractor.extractFacts(context, trigger);
    result.factsExtracted = extractionResult.facts.length;

    // Cap extracted facts to prevent over-extraction from dense conversations
    const factsToProcess = extractionResult.facts.slice(0, MAX_FACTS_PER_EXTRACTION);
    if (extractionResult.facts.length > MAX_FACTS_PER_EXTRACTION) {
      debugLog(!!options.debug, `Capped extraction from ${extractionResult.facts.length} to ${MAX_FACTS_PER_EXTRACTION} facts`);
    }

    debugLog(!!options.debug, `Extracted ${result.factsExtracted} facts in ${extractionResult.processingTimeMs}ms`);

    // Filter and store facts
    for (const fact of factsToProcess) {
      // Skip NOOP facts
      if (fact.action === 'NOOP') {
        result.factsSkipped++;
        continue;
      }

      // Skip low importance facts (unless explicit command)
      if (trigger !== 'explicit' && fact.importance < options.config.minImportanceForAutoStore) {
        result.factsSkipped++;
        continue;
      }

      // Store the fact
      try {
        await storeFact(fact, options);
        result.factsStored++;

        debugLog(!!options.debug, `Stored fact: "${fact.factText}" (importance: ${fact.importance})`);
      } catch (storeError) {
        const storeErrorMsg = storeError instanceof Error ? storeError.message : String(storeError);

        // Check for 403 quota exceeded
        if (storeErrorMsg.includes('403') || storeErrorMsg.includes('quota') || storeErrorMsg.includes('Quota')) {
          debugLog(!!options.debug, `Quota exceeded (403) during store: ${storeErrorMsg}`);

          // Invalidate billing cache so next before_agent_start refreshes
          try {
            if (fs.existsSync(BILLING_CACHE_PATH)) {
              fs.unlinkSync(BILLING_CACHE_PATH);
            }
          } catch (e) {
            debugLog(!!options.debug, 'Failed to invalidate billing cache:', e);
          }

          result.quotaExceeded = true;
          result.quotaMessage = 'TotalReclaw quota exceeded. New memories cannot be stored until the quota resets next month or you upgrade your plan.';
          // Stop trying to store more facts
          break;
        }

        console.error(`[TotalReclaw] Failed to store fact:`, storeError);
        result.factsSkipped++;
      }
    }

    // Update state
    options.state.lastExtraction = new Date();
    options.state.pendingExtractions = [];
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Unknown error';
    console.error('[TotalReclaw] Extraction failed:', errorMsg);
  }

  result.processingTimeMs = Date.now() - startTime;
  return result;
}

/**
 * Store a single fact in TotalReclaw
 */
async function storeFact(
  fact: ExtractedFact,
  options: AgentEndOptions
): Promise<void> {
  const { client, config } = options;

  switch (fact.action) {
    case 'ADD':
      // Store new fact
      await client.remember(fact.factText, {
        importance: fact.importance / 10, // Normalize to 0-1
        source: 'extracted',
        tags: [fact.type],
      });
      break;

    case 'UPDATE':
      // Delete old and add new (simple update strategy)
      if (fact.existingFactId) {
        try {
          await client.forget(fact.existingFactId);
        } catch {
          // Ignore if old fact doesn't exist
        }
      }
      await client.remember(fact.factText, {
        importance: fact.importance / 10,
        source: 'extracted',
        tags: [fact.type],
      });
      break;

    case 'DELETE':
      // Delete existing fact
      if (fact.existingFactId) {
        await client.forget(fact.existingFactId);
      }
      break;

    case 'NOOP':
    default:
      // Do nothing
      break;
  }
}

// ============================================================================
// Exports
// ============================================================================

export default agentEnd;
