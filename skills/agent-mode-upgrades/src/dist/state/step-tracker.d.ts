/**
 * Automatic Step Completion Detection
 *
 * Analyzes tool results to determine if plan steps are complete.
 * Uses heuristics and optional LLM verification.
 */
import type { PlanStep, ToolCall, ToolResult, LLMCaller } from "../types.js";
import type { PlanStateManager } from "./persistence.js";
export interface StepTrackerConfig {
    /** Use LLM to verify completion (more accurate but costs tokens) */
    useLLMVerification: boolean;
    /** Confidence threshold for heuristic-only detection (0-1) */
    heuristicThreshold: number;
    /** Auto-advance to next step on completion */
    autoAdvance: boolean;
    /** Keywords that indicate failure */
    failureKeywords: string[];
    /** Keywords that indicate success */
    successKeywords: string[];
}
export interface CompletionAnalysis {
    isComplete: boolean;
    confidence: number;
    reason: string;
    suggestedResult?: string;
}
export declare class StepTracker {
    private config;
    private stateManager;
    private llmCaller?;
    constructor(stateManager: PlanStateManager, config?: Partial<StepTrackerConfig>, llmCaller?: LLMCaller);
    /**
     * Analyze a tool result to determine if current step is complete
     */
    analyzeToolResult(tool: ToolCall, result: ToolResult): Promise<CompletionAnalysis>;
    /**
     * Manually mark step complete (for explicit completion)
     */
    markComplete(stepId?: string, result?: string): void;
    /**
     * Manually mark step failed
     */
    markFailed(stepId?: string, error?: string): void;
    /**
     * Check if plan is complete
     */
    isPlanComplete(): boolean;
    /**
     * Get completion status summary
     */
    getStatus(): {
        hasActivePlan: boolean;
        activeStep: PlanStep | null;
        progress: {
            completed: number;
            total: number;
            percent: number;
        };
        isComplete: boolean;
    };
    private heuristicAnalysis;
    private llmVerification;
    private toolMatchesStepAction;
    private resultToText;
    private summarizeResult;
}
export declare function createStepTracker(stateManager: PlanStateManager, config?: Partial<StepTrackerConfig>, llmCaller?: LLMCaller): StepTracker;
//# sourceMappingURL=step-tracker.d.ts.map