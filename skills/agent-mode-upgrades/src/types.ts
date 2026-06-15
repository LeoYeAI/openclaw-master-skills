/**
 * Core types for the Enhanced Agentic Loop
 */

// ============================================================================
// Configuration Types
// ============================================================================

export interface EnhancedLoopConfig {
  enabled: boolean;
  planning: PlanningConfig;
  execution: ExecutionConfig;
  context: ContextConfig;
  errorRecovery: ErrorRecoveryConfig;
  stateMachine: StateMachineConfig;
}

export interface PlanningConfig {
  enabled: boolean;
  reflectionAfterTools: boolean;
  maxPlanSteps: number;
}

export interface ExecutionConfig {
  parallelTools: boolean;
  maxConcurrentTools: number;
  confidenceGates: boolean;
  confidenceThreshold: number;
}

export interface ContextConfig {
  proactiveManagement: boolean;
  summarizeAfterIterations: number;
  contextThreshold: number;
}

export interface ErrorRecoveryConfig {
  enabled: boolean;
  maxAttempts: number;
  learnFromErrors: boolean;
}

export interface StateMachineConfig {
  enabled: boolean;
  logging: boolean;
  metrics: boolean;
}

// ============================================================================
// Task Types
// ============================================================================

export type TaskStatus =
  | "pending"
  | "in_progress"
  | "blocked"
  | "complete"
  | "failed"
  | "skipped";

export interface Task {
  id: string;
  parentId: string | null;
  title: string;
  description: string;
  status: TaskStatus;
  priority: number;
  createdAt: number;
  updatedAt: number;
  subtasks: Task[];
  dependencies: string[];
  result?: TaskResult;
  metadata: Record<string, unknown>;
}

export interface TaskResult {
  success: boolean;
  summary: string;
  artifacts?: string[];
  error?: string;
}

export interface TaskStack {
  tasks: Task[];
  activeTaskId: string | null;
}

// ============================================================================
// Plan Types
// ============================================================================

export interface PlanStep {
  id: string;
  title: string;
  action: string;
  dependencies: string[];
  successCriteria: string;
  complexity: "low" | "medium" | "high";
  status: TaskStatus;
  result?: string;
}

export interface TaskPlan {
  id: string;
  goal: string;
  steps: PlanStep[];
  assumptions: string[];
  createdAt: number;
  status: "active" | "completed" | "abandoned";
}

export interface ReflectionResult {
  actionSucceeded: boolean | "partial";
  onTrack: boolean;
  decision: "continue" | "replan" | "escalate";
  reason?: string;
}

// ============================================================================
// Tool Execution Types
// ============================================================================

export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

export interface ToolResult {
  id: string;
  success: boolean;
  output?: unknown;
  error?: string;
  needsReplan?: boolean;
  needsHuman?: boolean;
  skipped?: boolean;
  reason?: string;
}

export interface ClassifiedTools {
  parallel: ToolCall[];
  sequential: ToolCall[];
  dependencyGraph: Map<string, string[]>;
}

// ============================================================================
// Confidence Types
// ============================================================================

export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface ConfidenceAssessment {
  confidence: number;
  reversible: boolean | "partial";
  reasoning: string;
  suggestedQuestion?: string;
}

export interface GateDecision {
  proceed: boolean;
  checkpoint?: boolean;
  waitForHuman?: boolean;
  refused?: boolean;
  question?: string;
  options?: string[];
  reason?: string;
}

// ============================================================================
// Error Recovery Types
// ============================================================================

export type RecoveryStrategy =
  | { type: "alternative_approach"; newPlan: string }
  | { type: "retry_modified"; modifiedArgs: Record<string, unknown> }
  | { type: "skip_and_continue"; reason: string }
  | { type: "escalate"; explanation: string }
  | { type: "retry_same"; delay?: number };

export interface ErrorDiagnosis {
  cause: string;
  recoverable: boolean | "maybe";
  strategy: RecoveryStrategy;
}

// ============================================================================
// State Machine Types
// ============================================================================

export type AgentState =
  | "idle"
  | "planning"
  | "executing"
  | "reflecting"
  | "waiting_human"
  | "replanning"
  | "recovering"
  | "completing"
  | "error"
  | "complete";

export interface StateTransition {
  from: AgentState;
  to: AgentState;
  trigger: string;
  timestamp: number;
  metadata?: Record<string, unknown>;
}

export interface StateContext {
  state: AgentState;
  previousState: AgentState | null;
  enteredAt: number;
  metadata: Record<string, unknown>;
  history: StateTransition[];
}

export interface StateObserver {
  onTransition(transition: StateTransition): void;
}

// ============================================================================
// Context Management Types
// ============================================================================

export interface TokenBudget {
  max: number;
  used: number;
  reserved: {
    systemPrompt: number;
    responseBuffer: number;
    toolResults: number;
  };
}

export interface WorkingMemoryEntry {
  id: string;
  summary: string;
  artifacts?: string[];
  timestamp: number;
  relevance?: number;
}

export interface WorkingMemory {
  entries: Map<string, WorkingMemoryEntry>;
  store(id: string, entry: Omit<WorkingMemoryEntry, "id">): void;
  retrieve(ids: string[]): string;
  search(query: string, limit?: number): WorkingMemoryEntry[];
  prune(maxAge?: number): number;
}

// ============================================================================
// Enhanced Loop Types
// ============================================================================

export interface EnhancedLoopState {
  config: EnhancedLoopConfig;
  taskStack: TaskStack;
  currentPlan: TaskPlan | null;
  workingMemory: WorkingMemory;
  stateContext: StateContext;
  tokenBudget: TokenBudget;
  iterationCount: number;
}

export interface EnhancedLoopCallbacks {
  onStateChange?: (transition: StateTransition) => void;
  onPlanGenerated?: (plan: TaskPlan) => void;
  onReflection?: (result: ReflectionResult) => void;
  onConfidenceGate?: (decision: GateDecision, action: ToolCall) => void;
  onErrorRecovery?: (diagnosis: ErrorDiagnosis, tool: ToolCall) => void;
  onHumanInputRequired?: (question: string, options?: string[]) => Promise<string>;
}

// ============================================================================
// Integration Types (matches OpenClaw's existing types)
// ============================================================================

export interface AgentMessage {
  role: "user" | "assistant" | "system";
  content: string | ContentBlock[];
}

export interface ContentBlock {
  type: string;
  text?: string;
  data?: string;
  [key: string]: unknown;
}

export interface LLMCallOptions {
  messages: AgentMessage[];
  tools?: ToolDefinition[];
  systemPrompt?: string;
  maxTokens?: number;
}

export interface ToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, unknown>;
}

export type LLMCaller = (options: LLMCallOptions) => Promise<{
  content: string;
  toolCalls?: ToolCall[];
  usage?: { inputTokens: number; outputTokens: number };
}>;

export type ToolExecutor = (toolCall: ToolCall) => Promise<ToolResult>;
