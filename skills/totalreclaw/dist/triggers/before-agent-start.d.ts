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
import type { TotalReclaw } from '@totalreclaw/client';
import type { RerankedResult } from '@totalreclaw/client';
import type { BeforeAgentStartResult, OpenClawContext, TotalReclawSkillConfig } from '../types';
import { CrossEncoderReranker } from '../reranker/cross-encoder';
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
 * Format retrieved memories into a context string for injection
 *
 * This format is designed to be:
 * - Clear to the LLM about what these memories represent
 * - Easy to parse visually
 * - Compact to minimize token usage
 */
export declare function formatMemoriesForContext(memories: RerankedResult[]): string;
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
export declare function beforeAgentStart(context: OpenClawContext, options: BeforeAgentStartOptions): Promise<BeforeAgentStartResult>;
export default beforeAgentStart;
//# sourceMappingURL=before-agent-start.d.ts.map