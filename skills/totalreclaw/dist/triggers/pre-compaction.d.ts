/**
 * TotalReclaw Skill - Pre-Compaction Hook
 *
 * This hook runs BEFORE context compaction occurs.
 * It performs comprehensive extraction of the conversation history.
 *
 * Flow:
 * 1. Full extraction of last 20 turns
 * 2. Comprehensive deduplication against existing memories
 * 3. Graph consolidation (merge entities and relations)
 * 4. Batch upload to server
 * 5. Return PreCompactionResult with stats
 *
 * This hook is more thorough than agent-end and runs less frequently.
 */
import type { TotalReclaw } from '@totalreclaw/client';
import type { PreCompactionResult, OpenClawContext, TotalReclawSkillConfig } from '../types';
import { FactExtractor, type LLMClient, type VectorStoreClient } from '../extraction';
/**
 * Options for the pre-compaction hook
 */
export interface PreCompactionOptions {
    /** TotalReclaw client instance */
    client: TotalReclaw;
    /** Skill configuration */
    config: TotalReclawSkillConfig;
    /** LLM client for extraction */
    llmClient: LLMClient;
    /** Vector store client for deduplication (optional) */
    vectorStoreClient?: VectorStoreClient;
    /** Custom fact extractor (optional) */
    extractor?: FactExtractor;
    /** Number of turns to analyze (default: 20) */
    analysisWindow?: number;
    /** Whether to enable debug logging */
    debug?: boolean;
    /** Whether to perform graph consolidation */
    consolidateGraph?: boolean;
}
/**
 * Execute the pre-compaction hook
 *
 * This performs comprehensive extraction and storage before context compaction.
 *
 * @param context - OpenClaw context containing user message and history
 * @param options - Hook options including client and configuration
 * @returns PreCompactionResult with extraction and storage stats
 *
 * @example
 * ```typescript
 * const result = await preCompaction(context, {
 *   client: openMemoryClient,
 *   config: skillConfig,
 *   llmClient: myLLMClient,
 * });
 *
 * console.log(`Extracted ${result.factsExtracted} facts, stored ${result.factsStored}`);
 * ```
 */
export declare function preCompaction(context: OpenClawContext, options: PreCompactionOptions): Promise<PreCompactionResult>;
export default preCompaction;
//# sourceMappingURL=pre-compaction.d.ts.map