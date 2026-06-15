/**
 * Enhanced Agentic Loop Orchestrator
 *
 * Unified interface that ties together all enhanced loop capabilities:
 * - Persistent plan state
 * - Step completion tracking
 * - Approval gates
 * - Retry with alternatives
 * - Context summarization
 * - Checkpointing
 */
import type { ToolCall, ToolResult, LLMCaller, TaskPlan } from "./types.js";
import { PlanStateManager } from "./state/persistence.js";
import { type ApprovalRequest } from "./execution/approval-gate.js";
import { type Message } from "./context/summarizer.js";
export interface OrchestratorConfig {
    sessionId: string;
    /** Planning configuration */
    planning: {
        enabled: boolean;
        maxPlanSteps: number;
        reflectionAfterTools: boolean;
    };
    /** Approval gate configuration */
    approvalGate: {
        enabled: boolean;
        timeoutMs: number;
        requireApprovalFor: ("low" | "medium" | "high" | "critical")[];
    };
    /** Retry configuration */
    retry: {
        enabled: boolean;
        maxAttempts: number;
        useLLMAlternatives: boolean;
    };
    /** Context management */
    context: {
        enabled: boolean;
        thresholdTokens: number;
        keepRecentMessages: number;
    };
    /** Checkpointing */
    checkpoint: {
        enabled: boolean;
        autoCheckpointInterval: number;
        checkpointOnStepComplete: boolean;
    };
}
export interface OrchestratorCallbacks {
    onPlanCreated?: (plan: TaskPlan) => void;
    onStepStarted?: (stepId: string, stepTitle: string) => void;
    onStepCompleted?: (stepId: string, result: string) => void;
    onStepFailed?: (stepId: string, error: string) => void;
    onApprovalNeeded?: (request: ApprovalRequest) => void;
    onApprovalDecision?: (request: ApprovalRequest) => void;
    onCheckpointCreated?: (checkpointId: string) => void;
    onContextSummarized?: (savedTokens: number) => void;
    onPlanCompleted?: () => void;
}
export interface ToolExecutionResult {
    result: ToolResult;
    wasRetried: boolean;
    retryAttempts: number;
    wasBlocked: boolean;
    blockReason?: string;
    stepCompleted: boolean;
}
export declare class EnhancedLoopOrchestrator {
    private config;
    private callbacks;
    private llmCaller?;
    private stateManager;
    private stepTracker;
    private approvalGate;
    private retryEngine;
    private summarizer;
    private checkpointManager;
    private initialized;
    constructor(config: Partial<OrchestratorConfig> & {
        sessionId: string;
    }, callbacks?: OrchestratorCallbacks, llmCaller?: LLMCaller);
    /**
     * Initialize the orchestrator for a session
     */
    init(): Promise<{
        state: ReturnType<PlanStateManager["get"]>;
        hasIncompleteWork: boolean;
        incompleteWorkDescription?: string;
    }>;
    /**
     * Process a user goal - create plan if needed
     */
    processGoal(goal: string, context?: string): Promise<{
        planCreated: boolean;
        plan?: TaskPlan;
        contextToInject: string;
    }>;
    /**
     * Execute a tool with all enhancements
     */
    executeTool(tool: ToolCall, executor: (t: ToolCall) => Promise<ToolResult>): Promise<ToolExecutionResult>;
    /**
     * Manage context - summarize if needed
     */
    manageContext(messages: Message[]): Promise<{
        messages: Message[];
        summarized: boolean;
        tokensSaved: number;
    }>;
    /**
     * Resume from checkpoint
     */
    resume(checkpointId?: string): Promise<{
        success: boolean;
        contextToInject?: string;
        error?: string;
    }>;
    /**
     * Get current status for display
     */
    getStatus(): {
        hasPlan: boolean;
        progress: {
            completed: number;
            total: number;
            percent: number;
        };
        activeStep: {
            id: string;
            title: string;
        } | null;
        pendingApprovals: ApprovalRequest[];
        context: {
            turnCount: number;
            toolCalls: number;
            errors: number;
        };
    };
    /**
     * Format status as markdown for injection
     */
    formatStatus(): string;
    /**
     * Format plan as a structured block for UI rendering
     * This outputs a special format that webchat can detect and render as collapsible checklist
     */
    formatPlanBlock(): string;
    /**
     * Format plan as human-readable checklist (fallback for non-UI contexts)
     */
    formatPlanChecklist(): string;
    /**
     * Approve a pending tool execution
     */
    approve(requestId: string): boolean;
    /**
     * Deny a pending tool execution
     */
    deny(requestId: string): boolean;
    /**
     * Create manual checkpoint
     */
    checkpoint(description?: string): Promise<string>;
    /**
     * Sync step statuses from the LLM's response plan block.
     * The LLM outputs a :::plan block with step statuses; we parse it after
     * the run and persist those updates so the next turn is accurate.
     */
    syncFromResponse(planData: {
        steps: Array<{
            id: string;
            status: string;
        }>;
    }): {
        stepsCompleted: string[];
        stepsFailed: string[];
    };
    /**
     * Notify the orchestrator of a tool completion (lightweight tracking).
     * Called from the hook's onAgentEvent wrapper when a tool result arrives.
     * Uses a simple heuristic: if a non-error tool matches the active step's
     * expected action, mark the step as complete.
     */
    notifyToolCompletion(toolName: string, isError: boolean): {
        stepCompleted: boolean;
        completedStepId?: string;
        completedStepTitle?: string;
    };
    /**
     * Cleanup resources
     */
    cleanup(): Promise<void>;
    private ensureInitialized;
}
export interface PlanBlockData {
    goal: string;
    completed: number;
    total: number;
    steps: Array<{
        id: string;
        title: string;
        status: "pending" | "active" | "complete" | "failed";
    }>;
}
/**
 * Parse a plan block from text
 */
export declare function parsePlanBlock(text: string): PlanBlockData | null;
/**
 * Check if text contains a plan block
 */
export declare function hasPlanBlock(text: string): boolean;
export declare function createOrchestrator(config: Partial<OrchestratorConfig> & {
    sessionId: string;
}, callbacks?: OrchestratorCallbacks, llmCallerOrConfig?: LLMCaller | {
    apiKey: string;
    model?: string;
}): EnhancedLoopOrchestrator;
//# sourceMappingURL=orchestrator.d.ts.map