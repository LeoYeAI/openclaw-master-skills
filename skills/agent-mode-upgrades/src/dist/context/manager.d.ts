/**
 * Proactive Context Management
 *
 * Manage context window efficiently with summarization and pruning.
 */
import type { TokenBudget, WorkingMemory, ContextConfig, AgentMessage, LLMCaller } from "../types.js";
/**
 * Rough token estimation (4 chars per token average)
 */
export declare function estimateTokens(text: string): number;
/**
 * Estimate tokens for messages
 */
export declare function estimateMessageTokens(messages: AgentMessage[]): number;
/**
 * Create a token budget
 */
export declare function createTokenBudget(maxTokens: number): TokenBudget;
/**
 * Get available tokens
 */
export declare function getAvailableTokens(budget: TokenBudget): number;
/**
 * Check if content fits in budget
 */
export declare function canFitInBudget(budget: TokenBudget, content: string): boolean;
/**
 * Update budget with used tokens
 */
export declare function updateBudget(budget: TokenBudget, tokens: number): TokenBudget;
/**
 * Get budget usage percentage
 */
export declare function getBudgetUsage(budget: TokenBudget): number;
/**
 * Create a working memory store
 */
export declare function createWorkingMemory(): WorkingMemory;
/**
 * Summarize tool results
 */
export declare function summarizeToolResults(results: {
    tool: string;
    result: string;
}[], llmCall: LLMCaller): Promise<string>;
/**
 * Summarize a work session
 */
export declare function summarizeWorkSession(tasks: string[], toolsUsed: string[], filesAffected: string[], llmCall: LLMCaller): Promise<string>;
export interface PruneRules {
    keepLastMessages: number;
    keepRecentMs: number;
    alwaysKeepTypes: string[];
    pruneToolResultsAfterMs: number;
    summarizeBeforePrune: boolean;
}
export declare const DEFAULT_PRUNE_RULES: PruneRules;
interface TaggedMessage extends AgentMessage {
    timestamp?: number;
    type?: string;
}
/**
 * Apply pruning rules to messages
 */
export declare function applyPruneRules(messages: TaggedMessage[], rules?: PruneRules): {
    kept: TaggedMessage[];
    pruned: TaggedMessage[];
};
/**
 * Check if context management is needed
 */
export declare function shouldManageContext(budget: TokenBudget, iterationCount: number, config: ContextConfig): boolean;
/**
 * Manage context proactively
 */
export declare function manageContext(messages: TaggedMessage[], budget: TokenBudget, workingMemory: WorkingMemory, config: ContextConfig, llmCall?: LLMCaller): Promise<{
    messages: TaggedMessage[];
    budget: TokenBudget;
    summarized?: string;
}>;
/**
 * Build context from working memory for a new subtask
 */
export declare function buildWorkingMemoryContext(workingMemory: WorkingMemory, dependencyIds: string[]): string;
/**
 * Search working memory for relevant context
 */
export declare function searchRelevantContext(workingMemory: WorkingMemory, query: string, limit?: number): string;
export {};
//# sourceMappingURL=manager.d.ts.map