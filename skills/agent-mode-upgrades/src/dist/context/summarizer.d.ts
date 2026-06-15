/**
 * Context Summarization
 *
 * Manages context window by summarizing old content when
 * the conversation history grows too long.
 */
import type { LLMCaller } from "../types.js";
export interface Message {
    role: "user" | "assistant" | "system" | "tool";
    content: string;
    toolName?: string;
    toolResult?: unknown;
    timestamp?: number;
}
export interface SummarizerConfig {
    /** Enable automatic summarization */
    enabled: boolean;
    /** Target token count after summarization */
    targetTokens: number;
    /** Trigger summarization when exceeding this */
    thresholdTokens: number;
    /** Minimum messages to keep unsummarized */
    keepRecentMessages: number;
    /** Include tool results in summary */
    summarizeToolResults: boolean;
}
export interface SummarizationResult {
    summarized: boolean;
    summary?: string;
    removedMessages: number;
    originalTokens: number;
    finalTokens: number;
    savedTokens: number;
}
export interface ContextState {
    messages: Message[];
    summaries: ContextSummary[];
    totalTokensEstimate: number;
}
export interface ContextSummary {
    id: string;
    createdAt: number;
    messageRange: {
        from: number;
        to: number;
    };
    summary: string;
    keyPoints: string[];
    tokensSaved: number;
}
/**
 * Rough token estimation (4 chars ≈ 1 token)
 */
export declare function estimateTokens(text: string): number;
export declare function estimateMessageTokens(message: Message): number;
export declare function estimateTotalTokens(messages: Message[]): number;
export declare class ContextSummarizer {
    private config;
    private llmCaller?;
    private summaries;
    constructor(config?: Partial<SummarizerConfig>, llmCaller?: LLMCaller);
    /**
     * Check if summarization is needed
     */
    needsSummarization(messages: Message[]): boolean;
    /**
     * Summarize older messages to reduce context size
     */
    summarize(messages: Message[]): Promise<SummarizationResult>;
    /**
     * Get summary to inject as context
     */
    getSummaryContext(): string;
    /**
     * Condense tool results to save tokens
     */
    condenseToolResult(result: unknown, maxTokens?: number): string;
    /**
     * Build optimized message array with summarization
     */
    optimizeMessages(messages: Message[]): Promise<{
        messages: Message[];
        summaryInjected: boolean;
    }>;
    private generateSummary;
    private llmGenerateSummary;
    private heuristicSummary;
}
export declare function createContextSummarizer(config?: Partial<SummarizerConfig>, llmCaller?: LLMCaller): ContextSummarizer;
//# sourceMappingURL=summarizer.d.ts.map