/**
 * Enhanced Agentic Loop
 *
 * Main orchestrator that wraps the core runner with advanced capabilities:
 * - Planning and reflection
 * - Parallel tool execution
 * - Confidence-gated autonomy
 * - Semantic error recovery
 * - Proactive context management
 * - Observable state machine
 */
import { AgentStateMachine, LoggingObserver, MetricsObserver } from "./state-machine/fsm.js";
import { createTaskStack, createTask, updateTaskStatus, getActiveTask, setActiveTask, } from "./tasks/task-stack.js";
import { shouldGeneratePlan, generatePlan, reflect, replan, completeStep, getNextStep, formatPlanForContext, } from "./planning/planner.js";
import { executeWithMetrics, } from "./execution/parallel.js";
import { gateAction, createCheckpoint, } from "./execution/confidence-gate.js";
import { executeWithRecovery, ErrorLearningStore, } from "./execution/error-recovery.js";
import { createTokenBudget, createWorkingMemory, shouldManageContext, } from "./context/manager.js";
// ============================================================================
// Default Configuration
// ============================================================================
export const DEFAULT_CONFIG = {
    enabled: false,
    planning: {
        enabled: true,
        reflectionAfterTools: true,
        maxPlanSteps: 7,
    },
    execution: {
        parallelTools: true,
        maxConcurrentTools: 5,
        confidenceGates: true,
        confidenceThreshold: 0.7,
    },
    context: {
        proactiveManagement: true,
        summarizeAfterIterations: 5,
        contextThreshold: 0.7,
    },
    errorRecovery: {
        enabled: true,
        maxAttempts: 3,
        learnFromErrors: true,
    },
    stateMachine: {
        enabled: true,
        logging: true,
        metrics: false,
    },
};
// ============================================================================
// Enhanced Loop Class
// ============================================================================
export class EnhancedAgentLoop {
    config;
    state;
    stateMachine;
    errorStore;
    callbacks;
    constructor(config = {}, callbacks = {}) {
        this.config = { ...DEFAULT_CONFIG, ...config };
        this.callbacks = callbacks;
        this.stateMachine = new AgentStateMachine(this.config.stateMachine);
        this.errorStore = new ErrorLearningStore();
        // Initialize state
        this.state = {
            config: this.config,
            taskStack: createTaskStack(),
            currentPlan: null,
            workingMemory: createWorkingMemory(),
            stateContext: this.stateMachine.getContext(),
            tokenBudget: createTokenBudget(128000), // Default, will be updated
            iterationCount: 0,
        };
        // Set up observers
        if (this.config.stateMachine.enabled) {
            if (this.config.stateMachine.logging) {
                this.stateMachine.subscribe(new LoggingObserver());
            }
            if (this.config.stateMachine.metrics) {
                this.stateMachine.subscribe(new MetricsObserver());
            }
            if (callbacks.onStateChange) {
                this.stateMachine.subscribe({ onTransition: callbacks.onStateChange });
            }
        }
    }
    /**
     * Get current configuration
     */
    getConfig() {
        return { ...this.config };
    }
    /**
     * Update configuration
     */
    updateConfig(update) {
        this.config = { ...this.config, ...update };
        this.state.config = this.config;
    }
    /**
     * Get current state
     */
    getState() {
        return {
            ...this.state,
            stateContext: this.stateMachine.getContext(),
        };
    }
    /**
     * Run the enhanced loop
     */
    async run(userGoal, context, llmCall, toolExecutor, options = {}) {
        const maxIterations = options.maxIterations ?? 50;
        this.state.tokenBudget = createTokenBudget(options.maxTokens ?? 128000);
        this.state.iterationCount = 0;
        let toolsExecuted = 0;
        let replans = 0;
        let humanEscalations = 0;
        let planGenerated = false;
        try {
            // ─────────────────────────────────────────────────────────────────────
            // PLANNING PHASE
            // ─────────────────────────────────────────────────────────────────────
            this.stateMachine.transition("planning", "user_input", { goal: userGoal });
            if (shouldGeneratePlan(userGoal, this.state.currentPlan, this.config.planning)) {
                this.state.currentPlan = await generatePlan(userGoal, context, this.config.planning, llmCall);
                planGenerated = true;
                if (this.callbacks.onPlanGenerated) {
                    this.callbacks.onPlanGenerated(this.state.currentPlan);
                }
                // Create task from plan
                const rootTask = createTask(this.state.taskStack, {
                    title: this.state.currentPlan.goal,
                    description: formatPlanForContext(this.state.currentPlan),
                    priority: 10,
                });
                setActiveTask(this.state.taskStack, rootTask.id);
            }
            this.stateMachine.transition("executing", "plan_ready");
            // ─────────────────────────────────────────────────────────────────────
            // MAIN LOOP
            // ─────────────────────────────────────────────────────────────────────
            while (this.state.iterationCount < maxIterations) {
                if (options.abortSignal?.aborted) {
                    throw new Error("Aborted");
                }
                this.state.iterationCount++;
                // Check context management
                if (shouldManageContext(this.state.tokenBudget, this.state.iterationCount, this.config.context)) {
                    // Would need actual messages here - simplified for now
                    console.log("[enhanced-loop] Context management triggered");
                }
                // Get next step from plan
                const nextStep = this.state.currentPlan ? getNextStep(this.state.currentPlan) : null;
                if (!nextStep && this.state.currentPlan) {
                    // Plan complete
                    this.stateMachine.transition("completing", "all_done");
                    break;
                }
                // ─────────────────────────────────────────────────────────────────────
                // TOOL EXECUTION PHASE
                // ─────────────────────────────────────────────────────────────────────
                // This is where we'd integrate with the actual LLM to get tool calls
                // For now, we provide hooks for the caller to use
                // Note: In real integration, we'd call the LLM here and get tool calls
                // The caller would pass in a function that returns tool calls from the LLM
                // For demonstration, assume we have a tool call to execute
                // In real usage, this would come from the LLM response
                // ─────────────────────────────────────────────────────────────────────
                // REFLECTION PHASE
                // ─────────────────────────────────────────────────────────────────────
                if (this.config.planning.reflectionAfterTools && this.state.currentPlan) {
                    this.stateMachine.transition("reflecting", "tool_complete");
                    // Simplified - would have actual tool call and result here
                    const mockToolCall = { id: "mock", name: "mock", arguments: {} };
                    const mockResult = { id: "mock", success: true };
                    const reflection = await reflect(this.state.currentPlan, mockToolCall, mockResult, this.config.planning, llmCall);
                    if (this.callbacks.onReflection) {
                        this.callbacks.onReflection(reflection);
                    }
                    if (reflection.decision === "replan") {
                        this.stateMachine.transition("replanning", "need_replan", {
                            reason: reflection.reason,
                        });
                        this.state.currentPlan = await replan(this.state.currentPlan, reflection.reason ?? "Reflection indicated replanning needed", this.config.planning, llmCall);
                        replans++;
                        this.stateMachine.transition("executing", "plan_revised");
                    }
                    else if (reflection.decision === "escalate") {
                        humanEscalations++;
                        if (this.callbacks.onHumanInputRequired) {
                            this.stateMachine.transition("waiting_human", "low_confidence", {
                                reason: reflection.reason,
                            });
                            await this.callbacks.onHumanInputRequired(reflection.reason ?? "Human input needed");
                            this.stateMachine.transition("executing", "human_responded");
                        }
                        else {
                            // No human callback, treat as complete
                            this.stateMachine.transition("completing", "escalate_no_handler");
                            break;
                        }
                    }
                    else {
                        // Continue
                        this.stateMachine.transition("executing", "on_track");
                    }
                }
                // Mark step complete if we have a plan
                if (nextStep && this.state.currentPlan) {
                    this.state.currentPlan = completeStep(this.state.currentPlan, nextStep.id, "Completed");
                }
                // Simple iteration limit for this demo
                // In real usage, the loop would continue until the LLM signals completion
                if (this.state.iterationCount >= 3) {
                    break;
                }
            }
            // ─────────────────────────────────────────────────────────────────────
            // COMPLETION
            // ─────────────────────────────────────────────────────────────────────
            this.stateMachine.transition("completing", "loop_done");
            // Update task status
            const activeTask = getActiveTask(this.state.taskStack);
            if (activeTask) {
                updateTaskStatus(this.state.taskStack, activeTask.id, "complete", {
                    success: true,
                    summary: "Task completed",
                });
            }
            this.stateMachine.transition("idle", "response_sent");
            return {
                success: true,
                result: "Enhanced loop completed",
                metrics: {
                    iterations: this.state.iterationCount,
                    toolsExecuted,
                    planGenerated,
                    replans,
                    humanEscalations,
                },
            };
        }
        catch (err) {
            const error = err instanceof Error ? err.message : String(err);
            this.stateMachine.transition("error", "unrecoverable", { error });
            // Update task status
            const activeTask = getActiveTask(this.state.taskStack);
            if (activeTask) {
                updateTaskStatus(this.state.taskStack, activeTask.id, "failed", {
                    success: false,
                    summary: error,
                    error,
                });
            }
            this.stateMachine.transition("idle", "error_reported");
            return {
                success: false,
                error,
                metrics: {
                    iterations: this.state.iterationCount,
                    toolsExecuted,
                    planGenerated,
                    replans,
                    humanEscalations,
                },
            };
        }
    }
    /**
     * Execute tool calls with enhanced features
     */
    async executeTools(toolCalls, executor, context, llmCall) {
        const results = new Map();
        for (const tool of toolCalls) {
            // ─────────────────────────────────────────────────────────────────────
            // CONFIDENCE GATE
            // ─────────────────────────────────────────────────────────────────────
            if (this.config.execution.confidenceGates) {
                const { assessment, decision } = await gateAction(tool, context, this.config.execution, llmCall);
                if (this.callbacks.onConfidenceGate) {
                    this.callbacks.onConfidenceGate(decision, tool);
                }
                if (decision.checkpoint) {
                    await createCheckpoint(tool, context);
                }
                if (decision.waitForHuman) {
                    if (this.callbacks.onHumanInputRequired) {
                        const response = await this.callbacks.onHumanInputRequired(decision.question ?? "Should I proceed?", decision.options);
                        if (response.toLowerCase().includes("no") || response.toLowerCase().includes("cancel")) {
                            results.set(tool.id, {
                                id: tool.id,
                                success: false,
                                skipped: true,
                                reason: "Cancelled by user",
                            });
                            continue;
                        }
                    }
                }
                if (decision.refused) {
                    results.set(tool.id, {
                        id: tool.id,
                        success: false,
                        error: decision.reason ?? "Action refused due to low confidence",
                    });
                    continue;
                }
            }
            // ─────────────────────────────────────────────────────────────────────
            // EXECUTE WITH RECOVERY
            // ─────────────────────────────────────────────────────────────────────
            if (this.config.errorRecovery.enabled) {
                const { result, diagnosis, attempts } = await executeWithRecovery(tool, executor, this.config.errorRecovery, llmCall);
                if (diagnosis && this.callbacks.onErrorRecovery) {
                    this.callbacks.onErrorRecovery(diagnosis, tool);
                }
                // Learn from successful recovery
                if (this.config.errorRecovery.learnFromErrors &&
                    diagnosis &&
                    result.success &&
                    attempts > 1) {
                    this.errorStore.add({
                        toolName: tool.name,
                        errorPattern: diagnosis.cause,
                        successfulRecovery: diagnosis.strategy,
                        timestamp: Date.now(),
                    });
                }
                results.set(tool.id, result);
            }
            else {
                // Simple execution
                const result = await executor(tool);
                results.set(tool.id, result);
            }
        }
        return results;
    }
    /**
     * Execute tools in parallel where possible
     */
    async executeToolsParallel(toolCalls, executor) {
        if (!this.config.execution.parallelTools) {
            // Sequential execution
            const results = new Map();
            for (const tool of toolCalls) {
                const result = await executor(tool);
                results.set(tool.id, result);
            }
            return { results };
        }
        // Parallel execution with metrics
        return executeWithMetrics(toolCalls, executor, this.config.execution);
    }
    /**
     * Reset the loop state
     */
    reset() {
        this.stateMachine.reset();
        this.state = {
            config: this.config,
            taskStack: createTaskStack(),
            currentPlan: null,
            workingMemory: createWorkingMemory(),
            stateContext: this.stateMachine.getContext(),
            tokenBudget: createTokenBudget(128000),
            iterationCount: 0,
        };
    }
    /**
     * Get state machine metrics
     */
    getMetrics() {
        return this.stateMachine.getMetrics();
    }
    /**
     * Get state machine history
     */
    getHistory() {
        return this.stateMachine.getHistory();
    }
}
// ============================================================================
// Factory Function
// ============================================================================
/**
 * Create an enhanced agent loop
 */
export function createEnhancedLoop(config, callbacks) {
    return new EnhancedAgentLoop(config, callbacks);
}
//# sourceMappingURL=enhanced-loop.js.map