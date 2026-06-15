/**
 * Semantic Error Recovery
 *
 * Diagnose errors and adapt approach instead of simple retry.
 */
import type { ToolCall, ToolResult, ErrorDiagnosis, RecoveryStrategy, ErrorRecoveryConfig, LLMCaller } from "../types.js";
/**
 * Diagnose and get recovery strategy
 */
export declare function diagnoseAndRecover(tool: ToolCall, result: ToolResult, config: ErrorRecoveryConfig, llmCall?: LLMCaller): Promise<ErrorDiagnosis>;
/**
 * Execute tool with recovery attempts
 */
export declare function executeWithRecovery(tool: ToolCall, executor: (tool: ToolCall) => Promise<ToolResult>, config: ErrorRecoveryConfig, llmCall?: LLMCaller): Promise<{
    result: ToolResult;
    diagnosis?: ErrorDiagnosis;
    attempts: number;
}>;
export interface ErrorRecord {
    toolName: string;
    errorPattern: string;
    successfulRecovery: RecoveryStrategy;
    timestamp: number;
}
/**
 * Store for learned error patterns
 */
export declare class ErrorLearningStore {
    private records;
    private maxRecords;
    add(record: ErrorRecord): void;
    find(toolName: string, error: string): RecoveryStrategy | null;
    getRecords(): readonly ErrorRecord[];
    clear(): void;
}
//# sourceMappingURL=error-recovery.d.ts.map