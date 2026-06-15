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

export {
  EnhancedLoopOrchestrator,
  createOrchestrator,
  parsePlanBlock,
  hasPlanBlock,
  type OrchestratorConfig,
  type OrchestratorCallbacks,
  type ToolExecutionResult,
  type PlanBlockData,
} from "./orchestrator.js";

// ============================================================================
// LLM Caller
// ============================================================================

export {
  LLMCaller as SkillLLMCaller,
  createLLMCaller,
  getLLMCaller,
  createOrchestratorLLMCaller,
  type LLMCallerConfig,
  type LLMCallOptions,
  type LLMResponse,
} from "./llm/caller.js";

// ============================================================================
// Legacy Enhanced Loop (backward compatibility)
// ============================================================================

export {
  EnhancedAgentLoop,
  createEnhancedLoop,
  DEFAULT_CONFIG,
} from "./enhanced-loop.js";

// ============================================================================
// State Management
// ============================================================================

export {
  PlanStateManager,
  getStateManager,
  resetStateManager,
  type PlanState,
  type Checkpoint,
  type StateManagerConfig,
} from "./state/persistence.js";

export {
  StepTracker,
  createStepTracker,
  type StepTrackerConfig,
  type CompletionAnalysis,
} from "./state/step-tracker.js";

export {
  CheckpointManager,
  getCheckpointManager,
  resetCheckpointManager,
  type CheckpointData,
  type CheckpointConfig,
  type RestoreResult,
} from "./state/checkpoint.js";

// ============================================================================
// Execution
// ============================================================================

export {
  ApprovalGate,
  getApprovalGate,
  resetApprovalGate,
  classifyToolRisk,
  withApprovalGate,
  type ApprovalGateConfig,
  type ApprovalRequest,
  type ApprovalResult,
  type RiskLevel,
  type ApprovalDecision,
} from "./execution/approval-gate.js";

export {
  RetryEngine,
  createRetryEngine,
  type RetryConfig,
  type ErrorDiagnosis,
  type AlternativeApproach,
  type RetryAttempt,
  type RetryResult,
  type ErrorCategory,
} from "./execution/retry-engine.js";

// ============================================================================
// Context Management
// ============================================================================

export {
  ContextSummarizer,
  createContextSummarizer,
  estimateTokens,
  estimateMessageTokens,
  estimateTotalTokens,
  type SummarizerConfig,
  type SummarizationResult,
  type Message,
  type ContextSummary,
} from "./context/summarizer.js";

// Legacy exports from context/manager
export {
  createTokenBudget,
  createWorkingMemory,
  shouldManageContext,
  manageContext,
  buildWorkingMemoryContext,
} from "./context/manager.js";

// ============================================================================
// Planning
// ============================================================================

export {
  shouldGeneratePlan,
  generatePlan,
  reflect,
  replan,
  completeStep,
  failStep,
  getNextStep,
  formatPlanForContext,
} from "./planning/planner.js";

// ============================================================================
// Tasks
// ============================================================================

export {
  createTaskStack,
  createTask,
  findTask,
  flattenTasks,
  updateTaskStatus,
  hasPendingDependencies,
  getNextTask,
  getActiveTask,
  setActiveTask,
  handleInterruption,
  buildTaskContextPrompt,
  serializeTaskStack,
  restoreTaskStack,
  calculateProgress,
  getTaskStats,
} from "./tasks/task-stack.js";

// ============================================================================
// State Machine
// ============================================================================

export {
  AgentStateMachine,
  LoggingObserver,
  MetricsObserver,
  BroadcastObserver,
} from "./state-machine/fsm.js";

// ============================================================================
// Parallel Execution
// ============================================================================

export {
  isReadOnlyTool,
  hasSideEffects,
  classifyToolDependencies,
  executeToolCalls,
  executeWithMetrics,
} from "./execution/parallel.js";

// ============================================================================
// Confidence Gates (legacy)
// ============================================================================

export {
  classifyRisk,
  isLowRisk,
  assessConfidence,
  quickAssessConfidence,
  makeGateDecision,
  gateAction,
  createCheckpoint as createConfidenceCheckpoint,
  resolveThresholds,
  DEFAULT_THRESHOLDS,
} from "./execution/confidence-gate.js";

// ============================================================================
// Error Recovery (legacy)
// ============================================================================

export {
  diagnoseAndRecover,
  executeWithRecovery,
  ErrorLearningStore,
} from "./execution/error-recovery.js";

// ============================================================================
// Types
// ============================================================================

export type {
  TaskPlan,
  PlanStep,
  TaskStack,
  Task,
  TaskStatus,
  ReflectionResult,
  ToolCall,
  ToolResult,
  LLMCaller,
  PlanningConfig,
  EnhancedLoopConfig,
  EnhancedLoopState,
} from "./types.js";

// ============================================================================
// Version
// ============================================================================

export const VERSION = "0.2.0";
