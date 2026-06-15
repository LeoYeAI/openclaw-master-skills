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
import { createOrchestratorLLMCaller } from "./llm/caller.js";
import { getStateManager } from "./state/persistence.js";
import { createStepTracker } from "./state/step-tracker.js";
import { getApprovalGate } from "./execution/approval-gate.js";
import { createRetryEngine } from "./execution/retry-engine.js";
import { createContextSummarizer } from "./context/summarizer.js";
import { getCheckpointManager } from "./state/checkpoint.js";
import { shouldGeneratePlan, generatePlan } from "./planning/planner.js";
// ============================================================================
// Default Configuration
// ============================================================================
const DEFAULT_CONFIG = {
    planning: {
        enabled: true,
        maxPlanSteps: 7,
        reflectionAfterTools: true,
    },
    approvalGate: {
        enabled: true,
        timeoutMs: 15000,
        requireApprovalFor: ["high", "critical"],
    },
    retry: {
        enabled: true,
        maxAttempts: 3,
        useLLMAlternatives: false,
    },
    context: {
        enabled: true,
        thresholdTokens: 80000,
        keepRecentMessages: 10,
    },
    checkpoint: {
        enabled: true,
        autoCheckpointInterval: 60000,
        checkpointOnStepComplete: true,
    },
};
// ============================================================================
// Orchestrator
// ============================================================================
export class EnhancedLoopOrchestrator {
    config;
    callbacks;
    llmCaller;
    // Sub-systems
    stateManager;
    stepTracker;
    approvalGate;
    retryEngine;
    summarizer;
    checkpointManager;
    initialized = false;
    constructor(config, callbacks = {}, llmCaller) {
        this.config = { ...DEFAULT_CONFIG, ...config };
        this.callbacks = callbacks;
        this.llmCaller = llmCaller;
        // Initialize sub-systems
        this.stateManager = getStateManager();
        this.stepTracker = createStepTracker(this.stateManager, { autoAdvance: true }, llmCaller);
        this.approvalGate = getApprovalGate({
            enabled: this.config.approvalGate.enabled,
            timeoutMs: this.config.approvalGate.timeoutMs,
            requireApprovalFor: this.config.approvalGate.requireApprovalFor,
            onApprovalNeeded: callbacks.onApprovalNeeded,
            onDecision: callbacks.onApprovalDecision,
        });
        this.retryEngine = createRetryEngine({
            enabled: this.config.retry.enabled,
            maxAttempts: this.config.retry.maxAttempts,
            useLLMAlternatives: this.config.retry.useLLMAlternatives,
        }, llmCaller);
        this.summarizer = createContextSummarizer({
            enabled: this.config.context.enabled,
            thresholdTokens: this.config.context.thresholdTokens,
            keepRecentMessages: this.config.context.keepRecentMessages,
        }, llmCaller);
        this.checkpointManager = getCheckpointManager({
            enabled: this.config.checkpoint.enabled,
            autoCheckpointInterval: this.config.checkpoint.autoCheckpointInterval,
            checkpointOnStepComplete: this.config.checkpoint.checkpointOnStepComplete,
        });
    }
    /**
     * Initialize the orchestrator for a session
     */
    async init() {
        // Initialize state
        const state = await this.stateManager.init(this.config.sessionId);
        // Check for incomplete work
        const incomplete = await this.checkpointManager.hasIncompleteWork(this.config.sessionId);
        // Start auto-checkpointing
        if (this.config.checkpoint.enabled) {
            this.checkpointManager.startAutoCheckpoint(this.config.sessionId, () => this.stateManager.getOrNull());
        }
        this.initialized = true;
        return {
            state,
            hasIncompleteWork: incomplete.hasWork,
            incompleteWorkDescription: incomplete.description,
        };
    }
    /**
     * Process a user goal - create plan if needed
     */
    async processGoal(goal, context = "") {
        this.ensureInitialized();
        let contextToInject = "";
        let plan;
        // Check if planning is needed
        if (this.config.planning.enabled) {
            const needsPlan = shouldGeneratePlan(goal, this.stateManager.get().plan, this.config.planning);
            if (needsPlan && this.llmCaller) {
                plan = await generatePlan(goal, context, this.config.planning, this.llmCaller);
                this.stateManager.setPlan(plan);
                this.callbacks.onPlanCreated?.(plan);
                // Create initial checkpoint
                if (this.config.checkpoint.enabled) {
                    const checkpoint = await this.checkpointManager.createCheckpoint(this.stateManager.get(), { trigger: "manual", description: "Plan created" });
                    this.callbacks.onCheckpointCreated?.(checkpoint.id);
                }
            }
        }
        // Build context injection
        const planContext = this.stateManager.formatForContext();
        const summaryContext = this.summarizer.getSummaryContext();
        if (planContext || summaryContext) {
            contextToInject = [summaryContext, planContext].filter(Boolean).join("\n\n");
        }
        return {
            planCreated: !!plan,
            plan,
            contextToInject,
        };
    }
    /**
     * Execute a tool with all enhancements
     */
    async executeTool(tool, executor) {
        this.ensureInitialized();
        const state = this.stateManager.get();
        let wasBlocked = false;
        let blockReason;
        let wasRetried = false;
        let retryAttempts = 0;
        let stepCompleted = false;
        // Track tool call
        this.stateManager.recordToolCall();
        // === APPROVAL GATE ===
        if (this.config.approvalGate.enabled && this.approvalGate.requiresApproval(tool)) {
            const approval = await this.approvalGate.requestApproval(tool);
            if (!approval.proceed) {
                wasBlocked = true;
                blockReason = `Tool blocked: ${approval.decision} - ${approval.request.riskReason}`;
                return {
                    result: { id: tool.id, success: false, error: blockReason },
                    wasRetried: false,
                    retryAttempts: 0,
                    wasBlocked: true,
                    blockReason,
                    stepCompleted: false,
                };
            }
        }
        // === EXECUTE WITH RETRY ===
        let result;
        if (this.config.retry.enabled) {
            const retryResult = await this.retryEngine.executeWithRetry(tool, executor);
            result = retryResult.finalResult;
            wasRetried = retryResult.totalAttempts > 1;
            retryAttempts = retryResult.totalAttempts;
        }
        else {
            result = await executor(tool);
        }
        // === STEP TRACKING ===
        if (state.plan && state.activeStepId) {
            const analysis = await this.stepTracker.analyzeToolResult(tool, result);
            if (analysis.isComplete) {
                stepCompleted = true;
                this.callbacks.onStepCompleted?.(state.activeStepId, analysis.suggestedResult ?? "Completed");
                // Checkpoint on step completion
                if (this.config.checkpoint.checkpointOnStepComplete) {
                    const checkpoint = await this.checkpointManager.createCheckpoint(this.stateManager.get(), { trigger: "auto", description: `Step completed: ${state.activeStepId}` });
                    this.callbacks.onCheckpointCreated?.(checkpoint.id);
                }
                // Check if plan is complete
                if (this.stepTracker.isPlanComplete()) {
                    this.callbacks.onPlanCompleted?.();
                }
            }
        }
        // === ERROR HANDLING ===
        if (!result.success && this.config.checkpoint.enabled) {
            await this.checkpointManager.createCheckpoint(this.stateManager.get(), { trigger: "error", description: `Error: ${result.error?.slice(0, 50)}` });
        }
        return {
            result,
            wasRetried,
            retryAttempts,
            wasBlocked,
            blockReason,
            stepCompleted,
        };
    }
    /**
     * Manage context - summarize if needed
     */
    async manageContext(messages) {
        if (!this.config.context.enabled) {
            return { messages, summarized: false, tokensSaved: 0 };
        }
        const result = await this.summarizer.summarize(messages);
        if (result.summarized) {
            this.callbacks.onContextSummarized?.(result.savedTokens);
            // Get optimized messages
            const optimized = await this.summarizer.optimizeMessages(messages);
            return {
                messages: optimized.messages,
                summarized: true,
                tokensSaved: result.savedTokens,
            };
        }
        return { messages, summarized: false, tokensSaved: 0 };
    }
    /**
     * Resume from checkpoint
     */
    async resume(checkpointId) {
        const result = await this.checkpointManager.restore(this.config.sessionId, checkpointId);
        if (!result.success || !result.checkpoint) {
            return { success: false, error: result.error };
        }
        // Restore state from checkpoint
        if (result.checkpoint.plan) {
            this.stateManager.setPlan(result.checkpoint.plan);
        }
        return {
            success: true,
            contextToInject: result.resumePrompt,
        };
    }
    /**
     * Get current status for display
     */
    getStatus() {
        const state = this.stateManager.getOrNull();
        const progress = this.stateManager.getProgress();
        const activeStep = this.stateManager.getActiveStep();
        const pendingApprovals = this.approvalGate.getPendingRequests();
        return {
            hasPlan: !!state?.plan,
            progress,
            activeStep: activeStep ? { id: activeStep.id, title: activeStep.title } : null,
            pendingApprovals,
            context: {
                turnCount: state?.context.turnCount ?? 0,
                toolCalls: state?.context.totalToolCalls ?? 0,
                errors: state?.context.totalErrors ?? 0,
            },
        };
    }
    /**
     * Format status as markdown for injection
     */
    formatStatus() {
        const status = this.getStatus();
        if (!status.hasPlan) {
            return "";
        }
        const lines = [
            `## Task Progress: ${status.progress.completed}/${status.progress.total} (${status.progress.percent}%)`,
        ];
        if (status.activeStep) {
            lines.push(`**Current Step:** ${status.activeStep.title}`);
        }
        if (status.pendingApprovals.length > 0) {
            lines.push("");
            lines.push("⚠️ **Pending Approvals:**");
            for (const req of status.pendingApprovals) {
                lines.push(`- ${req.tool.name}: ${req.riskReason}`);
            }
        }
        return lines.join("\n");
    }
    /**
     * Format plan as a structured block for UI rendering
     * This outputs a special format that webchat can detect and render as collapsible checklist
     */
    formatPlanBlock() {
        const state = this.stateManager.getOrNull();
        if (!state?.plan)
            return "";
        const progress = this.stateManager.getProgress();
        const steps = state.plan.steps.map(step => ({
            id: step.id,
            title: step.title,
            status: state.completedStepIds.includes(step.id) ? "complete" :
                state.failedStepIds.includes(step.id) ? "failed" :
                    step.id === state.activeStepId ? "active" : "pending",
        }));
        const planData = {
            goal: state.plan.goal,
            completed: progress.completed,
            total: progress.total,
            steps,
        };
        // Output as special block that UI can parse
        return `\n:::plan\n${JSON.stringify(planData, null, 2)}\n:::\n`;
    }
    /**
     * Format plan as human-readable checklist (fallback for non-UI contexts)
     */
    formatPlanChecklist() {
        const state = this.stateManager.getOrNull();
        if (!state?.plan)
            return "";
        const progress = this.stateManager.getProgress();
        const lines = [
            `**${progress.completed} of ${progress.total} Steps Completed**`,
            "",
        ];
        for (const step of state.plan.steps) {
            const isComplete = state.completedStepIds.includes(step.id);
            const isFailed = state.failedStepIds.includes(step.id);
            const isActive = step.id === state.activeStepId;
            const icon = isComplete ? "✅" : isFailed ? "❌" : isActive ? "🔄" : "⬜";
            const title = isComplete ? `~~${step.title}~~` : step.title;
            const suffix = isActive ? " ← current" : "";
            lines.push(`${icon} ${title}${suffix}`);
        }
        return lines.join("\n");
    }
    /**
     * Approve a pending tool execution
     */
    approve(requestId) {
        return this.approvalGate.approve(requestId);
    }
    /**
     * Deny a pending tool execution
     */
    deny(requestId) {
        return this.approvalGate.deny(requestId);
    }
    /**
     * Create manual checkpoint
     */
    async checkpoint(description) {
        const checkpoint = await this.checkpointManager.createCheckpoint(this.stateManager.get(), { trigger: "manual", description });
        return checkpoint.id;
    }
    /**
     * Sync step statuses from the LLM's response plan block.
     * The LLM outputs a :::plan block with step statuses; we parse it after
     * the run and persist those updates so the next turn is accurate.
     */
    syncFromResponse(planData) {
        const state = this.stateManager.getOrNull();
        if (!state?.plan)
            return { stepsCompleted: [], stepsFailed: [] };
        const stepsCompleted = [];
        const stepsFailed = [];
        for (const step of planData.steps) {
            const normalizedStatus = step.status.toLowerCase();
            if (normalizedStatus === "done" || normalizedStatus === "complete") {
                if (!state.completedStepIds.includes(step.id)) {
                    this.stateManager.completeStep(step.id, "Completed");
                    this.callbacks.onStepCompleted?.(step.id, "Completed");
                    stepsCompleted.push(step.id);
                }
            }
            else if (normalizedStatus === "failed") {
                if (!state.failedStepIds.includes(step.id)) {
                    this.stateManager.failStep(step.id, "Failed");
                    this.callbacks.onStepFailed?.(step.id, "Failed");
                    stepsFailed.push(step.id);
                }
            }
        }
        // Check if plan is complete
        if (stepsCompleted.length > 0 && this.stepTracker.isPlanComplete()) {
            this.callbacks.onPlanCompleted?.();
        }
        return { stepsCompleted, stepsFailed };
    }
    /**
     * Notify the orchestrator of a tool completion (lightweight tracking).
     * Called from the hook's onAgentEvent wrapper when a tool result arrives.
     * Uses a simple heuristic: if a non-error tool matches the active step's
     * expected action, mark the step as complete.
     */
    notifyToolCompletion(toolName, isError) {
        if (!this.initialized)
            return { stepCompleted: false };
        const state = this.stateManager.getOrNull();
        if (!state?.plan || !state.activeStepId)
            return { stepCompleted: false };
        this.stateManager.recordToolCall();
        if (isError)
            return { stepCompleted: false };
        const activeStep = this.stateManager.getActiveStep();
        if (!activeStep)
            return { stepCompleted: false };
        // Lightweight heuristic: successful tool that aligns with the step's action
        const toolLower = toolName.toLowerCase();
        const actionLower = (activeStep.action ?? "").toLowerCase();
        const titleLower = (activeStep.title ?? "").toLowerCase();
        const toolActionMap = {
            exec: ["run", "execute", "install", "build", "deploy", "setup", "configure", "test", "start"],
            bash: ["run", "execute", "install", "build", "deploy", "setup", "configure", "test", "start"],
            write: ["write", "create", "save", "add", "generate", "implement"],
            edit: ["edit", "modify", "update", "change", "fix", "refactor"],
            read: ["read", "check", "verify", "inspect", "review", "analyze"],
            web_search: ["search", "find", "research", "look"],
            web_fetch: ["fetch", "get", "download", "retrieve"],
            browser: ["browse", "navigate", "open", "test", "verify"],
            glob: ["find", "search", "locate"],
            grep: ["search", "find"],
            message: ["send", "message", "notify"],
        };
        const keywords = toolActionMap[toolLower] ?? [];
        const matches = keywords.some((kw) => actionLower.includes(kw) || titleLower.includes(kw));
        if (matches) {
            this.stateManager.completeStep(activeStep.id, `Completed via ${toolName}`);
            this.callbacks.onStepCompleted?.(activeStep.id, `Completed via ${toolName}`);
            return {
                stepCompleted: true,
                completedStepId: activeStep.id,
                completedStepTitle: activeStep.title,
            };
        }
        return { stepCompleted: false };
    }
    /**
     * Cleanup resources
     */
    async cleanup() {
        this.checkpointManager.stopAutoCheckpoint();
        await this.stateManager.cleanup();
    }
    // ──────────────────────────────────────────────────────────────────────────
    // Private Methods
    // ──────────────────────────────────────────────────────────────────────────
    ensureInitialized() {
        if (!this.initialized) {
            throw new Error("Orchestrator not initialized. Call init() first.");
        }
    }
}
/**
 * Parse a plan block from text
 */
export function parsePlanBlock(text) {
    const match = text.match(/:::plan\s*([\s\S]*?)\s*:::/);
    if (!match)
        return null;
    try {
        return JSON.parse(match[1]);
    }
    catch {
        return null;
    }
}
/**
 * Check if text contains a plan block
 */
export function hasPlanBlock(text) {
    return /:::plan\s*[\s\S]*?\s*:::/.test(text);
}
// ============================================================================
// Factory
// ============================================================================
export function createOrchestrator(config, callbacks, llmCallerOrConfig) {
    // Accept either a pre-built LLM caller or a config to create one
    let caller;
    if (typeof llmCallerOrConfig === "function") {
        caller = llmCallerOrConfig;
    }
    else {
        caller = createOrchestratorLLMCaller(llmCallerOrConfig);
    }
    return new EnhancedLoopOrchestrator(config, callbacks, caller);
}
//# sourceMappingURL=orchestrator.js.map