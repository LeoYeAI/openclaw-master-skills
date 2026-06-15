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
export { EnhancedLoopOrchestrator, createOrchestrator, parsePlanBlock, hasPlanBlock, type OrchestratorConfig, type OrchestratorCallbacks, type ToolExecutionResult, type PlanBlockData, } from "./orchestrator.js";
export { LLMCaller as SkillLLMCaller, createLLMCaller, getLLMCaller, createOrchestratorLLMCaller, type LLMCallerConfig, type LLMCallOptions, type LLMResponse, } from "./llm/caller.js";
export { EnhancedAgentLoop, createEnhancedLoop, DEFAULT_CONFIG, } from "./enhanced-loop.js";
export { PlanStateManager, getStateManager, resetStateManager, type PlanState, type Checkpoint, type StateManagerConfig, } from "./state/persistence.js";
export { StepTracker, createStepTracker, type StepTrackerConfig, type CompletionAnalysis, } from "./state/step-tracker.js";
export { CheckpointManager, getCheckpointManager, resetCheckpointManager, type CheckpointData, type CheckpointConfig, type RestoreResult, } from "./state/checkpoint.js";
export { ApprovalGate, getApprovalGate, resetApprovalGate, classifyToolRisk, withApprovalGate, type ApprovalGateConfig, type ApprovalRequest, type ApprovalResult, type RiskLevel, type ApprovalDecision, } from "./execution/approval-gate.js";
export { RetryEngine, createRetryEngine, type RetryConfig, type ErrorDiagnosis, type AlternativeApproach, type RetryAttempt, type RetryResult, type ErrorCategory, } from "./execution/retry-engine.js";
export { ContextSummarizer, createContextSummarizer, estimateTokens, estimateMessageTokens, estimateTotalTokens, type SummarizerConfig, type SummarizationResult, type Message, type ContextSummary, } from "./context/summarizer.js";
export { createTokenBudget, createWorkingMemory, shouldManageContext, manageContext, buildWorkingMemoryContext, } from "./context/manager.js";
export { shouldGeneratePlan, generatePlan, reflect, replan, completeStep, failStep, getNextStep, formatPlanForContext, } from "./planning/planner.js";
export { createTaskStack, createTask, findTask, flattenTasks, updateTaskStatus, hasPendingDependencies, getNextTask, getActiveTask, setActiveTask, handleInterruption, buildTaskContextPrompt, serializeTaskStack, restoreTaskStack, calculateProgress, getTaskStats, } from "./tasks/task-stack.js";
export { AgentStateMachine, LoggingObserver, MetricsObserver, BroadcastObserver, } from "./state-machine/fsm.js";
export { isReadOnlyTool, hasSideEffects, classifyToolDependencies, executeToolCalls, executeWithMetrics, } from "./execution/parallel.js";
export { classifyRisk, isLowRisk, assessConfidence, quickAssessConfidence, makeGateDecision, gateAction, createCheckpoint as createConfidenceCheckpoint, resolveThresholds, DEFAULT_THRESHOLDS, } from "./execution/confidence-gate.js";
export { diagnoseAndRecover, executeWithRecovery, ErrorLearningStore, } from "./execution/error-recovery.js";
export type { TaskPlan, PlanStep, TaskStack, Task, TaskStatus, ReflectionResult, ToolCall, ToolResult, LLMCaller, PlanningConfig, EnhancedLoopConfig, EnhancedLoopState, } from "./types.js";
export declare const VERSION = "0.2.0";
//# sourceMappingURL=index.d.ts.map