/**
 * Enhanced Agentic Loop for OpenClaw
 *
 * A comprehensive upgrade to the agent loop with:
 * - Persistent plan state across conversation turns
 * - Automatic step completion detection
 * - Tool interception with timed approval gates
 * - Automatic retry with alternative approaches
 * - Context summarization when history grows long
 * - Checkpoint/restore for long-running tasks
 *
 * @module @openclaw/enhanced-loop
 */
// ============================================================================
// Main Orchestrator (recommended entry point)
// ============================================================================
export { EnhancedLoopOrchestrator, createOrchestrator, parsePlanBlock, hasPlanBlock, } from "./orchestrator.js";
// ============================================================================
// LLM Caller
// ============================================================================
export { LLMCaller as SkillLLMCaller, createLLMCaller, getLLMCaller, createOrchestratorLLMCaller, } from "./llm/caller.js";
// ============================================================================
// Legacy Enhanced Loop (backward compatibility)
// ============================================================================
export { EnhancedAgentLoop, createEnhancedLoop, DEFAULT_CONFIG, } from "./enhanced-loop.js";
// ============================================================================
// State Management
// ============================================================================
export { PlanStateManager, getStateManager, resetStateManager, } from "./state/persistence.js";
export { StepTracker, createStepTracker, } from "./state/step-tracker.js";
export { CheckpointManager, getCheckpointManager, resetCheckpointManager, } from "./state/checkpoint.js";
// ============================================================================
// Execution
// ============================================================================
export { ApprovalGate, getApprovalGate, resetApprovalGate, classifyToolRisk, withApprovalGate, } from "./execution/approval-gate.js";
export { RetryEngine, createRetryEngine, } from "./execution/retry-engine.js";
// ============================================================================
// Context Management
// ============================================================================
export { ContextSummarizer, createContextSummarizer, estimateTokens, estimateMessageTokens, estimateTotalTokens, } from "./context/summarizer.js";
// Legacy exports from context/manager
export { createTokenBudget, createWorkingMemory, shouldManageContext, manageContext, buildWorkingMemoryContext, } from "./context/manager.js";
// ============================================================================
// Planning
// ============================================================================
export { shouldGeneratePlan, generatePlan, reflect, replan, completeStep, failStep, getNextStep, formatPlanForContext, } from "./planning/planner.js";
// ============================================================================
// Tasks
// ============================================================================
export { createTaskStack, createTask, findTask, flattenTasks, updateTaskStatus, hasPendingDependencies, getNextTask, getActiveTask, setActiveTask, handleInterruption, buildTaskContextPrompt, serializeTaskStack, restoreTaskStack, calculateProgress, getTaskStats, } from "./tasks/task-stack.js";
// ============================================================================
// State Machine
// ============================================================================
export { AgentStateMachine, LoggingObserver, MetricsObserver, BroadcastObserver, } from "./state-machine/fsm.js";
// ============================================================================
// Parallel Execution
// ============================================================================
export { isReadOnlyTool, hasSideEffects, classifyToolDependencies, executeToolCalls, executeWithMetrics, } from "./execution/parallel.js";
// ============================================================================
// Confidence Gates (legacy)
// ============================================================================
export { classifyRisk, isLowRisk, assessConfidence, quickAssessConfidence, makeGateDecision, gateAction, createCheckpoint as createConfidenceCheckpoint, resolveThresholds, DEFAULT_THRESHOLDS, } from "./execution/confidence-gate.js";
// ============================================================================
// Error Recovery (legacy)
// ============================================================================
export { diagnoseAndRecover, executeWithRecovery, ErrorLearningStore, } from "./execution/error-recovery.js";
// ============================================================================
// Version
// ============================================================================
export const VERSION = "0.2.0";
//# sourceMappingURL=index.js.map