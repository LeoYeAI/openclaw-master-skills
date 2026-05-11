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
import { TotalReclaw, type RerankedResult } from '@totalreclaw/client';
import type { TotalReclawSkillConfig, OpenClawContext, BeforeAgentStartResult, AgentEndResult, PreCompactionResult, RememberToolParams, RecallToolParams, ForgetToolParams, ExportToolParams, ExtractedFact } from './types';
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
 * Main TotalReclaw Skill Class
 *
 * Integrates TotalReclaw with OpenClaw through lifecycle hooks and tools.
 */
export declare class TotalReclawSkill {
    private config;
    private client;
    private reranker;
    private extractor;
    private state;
    private llmAdapter;
    private vectorStoreAdapter;
    private authKeyHex;
    /**
     * Create a new TotalReclawSkill instance
     *
     * @param config - Skill configuration (partial, will be merged with defaults)
     */
    constructor(config?: Partial<TotalReclawSkillConfig>);
    /**
     * Initialize the skill
     *
     * Must be called before using any other methods.
     * Initializes the TotalReclaw client and loads the reranker model.
     *
     * @param llmCompleteFn - Optional LLM completion function for extraction
     * @returns Initialization result
     */
    init(llmCompleteFn?: (prompt: {
        system: string;
        user: string;
    }) => Promise<string>): Promise<InitResult>;
    /**
     * Set the LLM completion function for extraction
     * Can be called after init() if LLM wasn't available at initialization
     */
    setLLMProvider(completeFn: (prompt: {
        system: string;
        user: string;
    }) => Promise<string>): void;
    /**
     * before_agent_start hook
     *
     * Called before the agent starts processing a user message.
     * Retrieves relevant memories and formats them for context injection.
     *
     * @param context - OpenClaw context
     * @returns Memories to inject into context
     */
    onBeforeAgentStart(context: OpenClawContext): Promise<BeforeAgentStartResult>;
    /**
     * agent_end hook
     *
     * Called after the agent finishes processing.
     * Triggers fact extraction from the conversation.
     *
     * @param context - OpenClaw context
     * @returns Extraction result summary
     */
    onAgentEnd(context: OpenClawContext): Promise<AgentEndResult>;
    /**
     * pre_compaction hook
     *
     * Called before conversation history is compacted.
     * Extracts facts from the full conversation history before it's lost.
     *
     * @param context - OpenClaw context
     * @returns Extraction result summary
     */
    onPreCompaction(context: OpenClawContext): Promise<PreCompactionResult>;
    /**
     * totalreclaw_remember tool
     *
     * Explicitly store a memory.
     *
     * @param params - Tool parameters
     * @returns Confirmation message
     */
    remember(params: RememberToolParams): Promise<string>;
    /**
     * totalreclaw_recall tool
     *
     * Search for relevant memories.
     *
     * @param params - Tool parameters
     * @returns Search results
     */
    recall(params: RecallToolParams): Promise<RerankedResult[]>;
    /**
     * totalreclaw_forget tool
     *
     * Delete a specific memory.
     *
     * @param params - Tool parameters
     */
    forget(params: ForgetToolParams): Promise<void>;
    /**
     * totalreclaw_export tool
     *
     * Export all memories for portability.
     *
     * @param params - Tool parameters
     * @returns Exported data as formatted string
     */
    export(params: ExportToolParams): Promise<string>;
    /**
     * totalreclaw_status tool
     *
     * Check billing/subscription status.
     *
     * @returns Formatted status summary
     */
    status(): Promise<string>;
    /**
     * Get current turn count
     */
    getTurnCount(): number;
    /**
     * Get cached memories from last search
     */
    getCachedMemories(): RerankedResult[];
    /**
     * Check if skill is initialized
     */
    isInitialized(): boolean;
    /**
     * Get the underlying TotalReclaw client
     */
    getClient(): TotalReclaw | null;
    /**
     * Get the current user ID
     */
    getUserId(): string | null;
    /**
     * Get the salt (for credential persistence)
     */
    getSalt(): Buffer | null;
    /**
     * Reset the turn counter
     */
    resetTurnCount(): void;
    /**
     * Clear cached memories
     */
    clearCache(): void;
    /**
     * Get pending extractions
     */
    getPendingExtractions(): ExtractedFact[];
    /**
     * Clear pending extractions
     */
    clearPendingExtractions(): void;
    /**
     * Ensure the skill is initialized
     */
    private ensureInitialized;
    /**
     * Check if extraction should run on this turn
     */
    private shouldExtractOnTurn;
    /**
     * Extract facts using the configured extractor
     */
    private extractFacts;
    /**
     * Store extracted facts
     */
    private storeExtractedFacts;
    /**
     * Store a single fact
     */
    private storeFact;
    /**
     * Get existing memories for deduplication
     */
    private getExistingMemories;
    /**
     * Format memories for context injection
     */
    private formatMemoriesForContext;
    /**
     * Format age of a memory
     */
    private formatAge;
    /**
     * Format exported data as markdown
     */
    private formatExportAsMarkdown;
}
/**
 * Create an TotalReclaw skill instance with default configuration
 */
export declare function createTotalReclawSkill(config?: Partial<TotalReclawSkillConfig>): TotalReclawSkill;
export default TotalReclawSkill;
//# sourceMappingURL=totalreclaw-skill.d.ts.map