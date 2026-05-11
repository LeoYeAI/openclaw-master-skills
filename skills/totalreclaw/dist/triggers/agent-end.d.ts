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
import type { TotalReclaw } from '@totalreclaw/client';
import type { AgentEndResult, OpenClawContext, TotalReclawSkillConfig, SkillState } from '../types';
import { FactExtractor, type LLMClient, type VectorStoreClient } from '../extraction';
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
export declare function agentEnd(context: OpenClawContext, options: AgentEndOptions): Promise<AgentEndResult>;
export default agentEnd;
//# sourceMappingURL=agent-end.d.ts.map