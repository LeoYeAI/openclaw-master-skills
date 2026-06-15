/**
 * Automatic Retry with Alternative Approaches
 *
 * When a tool fails, diagnoses the error and attempts recovery
 * using alternative strategies before giving up.
 */
import type { ToolCall, ToolResult, LLMCaller } from "../types.js";
export interface RetryConfig {
    /** Enable automatic retries */
    enabled: boolean;
    /** Maximum retry attempts per tool call */
    maxAttempts: number;
    /** Delay between retries (ms) */
    retryDelayMs: number;
    /** Use LLM to generate alternative approaches */
    useLLMAlternatives: boolean;
    /** Learn from errors across sessions */
    learnFromErrors: boolean;
}
export interface ErrorDiagnosis {
    category: ErrorCategory;
    isRetryable: boolean;
    suggestedFix: string;
    alternativeApproach?: AlternativeApproach;
}
export interface AlternativeApproach {
    description: string;
    modifiedTool?: ToolCall;
    differentTool?: ToolCall;
}
export interface RetryAttempt {
    attemptNumber: number;
    originalTool: ToolCall;
    usedTool: ToolCall;
    result: ToolResult;
    diagnosis?: ErrorDiagnosis;
    timestamp: number;
}
export interface RetryResult {
    success: boolean;
    finalResult: ToolResult;
    attempts: RetryAttempt[];
    totalAttempts: number;
    recoveryStrategy?: string;
}
export type ErrorCategory = "permission" | "not_found" | "network" | "timeout" | "rate_limit" | "invalid_input" | "resource_busy" | "quota_exceeded" | "syntax_error" | "dependency_missing" | "unknown";
export declare class RetryEngine {
    private config;
    private llmCaller?;
    private errorHistory;
    constructor(config?: Partial<RetryConfig>, llmCaller?: LLMCaller);
    /**
     * Diagnose an error and suggest recovery
     */
    diagnose(tool: ToolCall, error: string): ErrorDiagnosis;
    /**
     * Execute a tool with automatic retry
     */
    executeWithRetry(tool: ToolCall, executor: (t: ToolCall) => Promise<ToolResult>): Promise<RetryResult>;
    /**
     * Generate LLM-powered alternative approach
     */
    generateAlternative(tool: ToolCall, error: string, previousAttempts: RetryAttempt[]): Promise<AlternativeApproach | null>;
    /**
     * Record a successful recovery for future learning
     */
    private recordSuccess;
    private delay;
}
export declare function createRetryEngine(config?: Partial<RetryConfig>, llmCaller?: LLMCaller): RetryEngine;
//# sourceMappingURL=retry-engine.d.ts.map