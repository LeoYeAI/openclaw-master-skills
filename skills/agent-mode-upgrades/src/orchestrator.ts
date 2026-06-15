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

import type { ToolCall, ToolResult, LLMCaller, TaskPlan, PlanStep } from "./types.js";
import { createOrchestratorLLMCaller } from "./llm/caller.js";
import { PlanStateManager, getStateManager } from "./state/persistence.js";
import { StepTracker, createStepTracker } from "./state/step-tracker.js";
import { ApprovalGate, getApprovalGate, type ApprovalRequest } from "./execution/approval-gate.js";
import { RetryEngine, createRetryEngine } from "./execution/retry-engine.js";
import { ContextSummarizer, createContextSummarizer, type Message } from "./context/summarizer.js";
import { CheckpointManager, getCheckpointManager } from "./state/checkpoint.js";
import { shouldGeneratePlan, generatePlan } from "./planning/planner.js";

// ============================================================================
// Types
// ============================================================================

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

// ============================================================================
// Default Configuration
// ============================================================================

const DEFAULT_CONFIG: Omit<OrchestratorConfig, "sessionId"> = {
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
  private config: OrchestratorConfig;
  private callbacks: OrchestratorCallbacks;
  private llmCaller?: LLMCaller;
  
  // Sub-systems
  private stateManager: PlanStateManager;
  private stepTracker: StepTracker;
  private approvalGate: ApprovalGate;
  private retryEngine: RetryEngine;
  private summarizer: ContextSummarizer;
  private checkpointManager: CheckpointManager;
  
  private initialized: boolean = false;

  constructor(
    config: Partial<OrchestratorConfig> & { sessionId: string },
    callbacks: OrchestratorCallbacks = {},
    llmCaller?: LLMCaller
  ) {
    this.config = { ...DEFAULT_CONFIG, ...config } as OrchestratorConfig;
    this.callbacks = callbacks;
    this.llmCaller = llmCaller;

    // Initialize sub-systems
    this.stateManager = getStateManager();
    this.stepTracker = createStepTracker(
      this.stateManager,
      { autoAdvance: true },
      llmCaller
    );
    this.approvalGate = getApprovalGate({
      enabled: this.config.approvalGate.enabled,
      timeoutMs: this.config.approvalGate.timeoutMs,
      requireApprovalFor: this.config.approvalGate.requireApprovalFor,
      onApprovalNeeded: callbacks.onApprovalNeeded,
      onDecision: callbacks.onApprovalDecision,
    });
    this.retryEngine = createRetryEngine(
      {
        enabled: this.config.retry.enabled,
        maxAttempts: this.config.retry.maxAttempts,
        useLLMAlternatives: this.config.retry.useLLMAlternatives,
      },
      llmCaller
    );
    this.summarizer = createContextSummarizer(
      {
        enabled: this.config.context.enabled,
        thresholdTokens: this.config.context.thresholdTokens,
        keepRecentMessages: this.config.context.keepRecentMessages,
      },
      llmCaller
    );
    this.checkpointManager = getCheckpointManager({
      enabled: this.config.checkpoint.enabled,
      autoCheckpointInterval: this.config.checkpoint.autoCheckpointInterval,
      checkpointOnStepComplete: this.config.checkpoint.checkpointOnStepComplete,
    });
  }

  /**
   * Initialize the orchestrator for a session
   */
  async init(): Promise<{
    state: ReturnType<PlanStateManager["get"]>;
    hasIncompleteWork: boolean;
    incompleteWorkDescription?: string;
  }> {
    // Initialize state
    const state = await this.stateManager.init(this.config.sessionId);
    
    // Check for incomplete work
    const incomplete = await this.checkpointManager.hasIncompleteWork(this.config.sessionId);
    
    // Start auto-checkpointing
    if (this.config.checkpoint.enabled) {
      this.checkpointManager.startAutoCheckpoint(
        this.config.sessionId,
        () => this.stateManager.getOrNull()
      );
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
  async processGoal(goal: string, context: string = ""): Promise<{
    planCreated: boolean;
    plan?: TaskPlan;
    contextToInject: string;
  }> {
    this.ensureInitialized();

    let contextToInject = "";
    let plan: TaskPlan | undefined;

    // Check if planning is needed
    if (this.config.planning.enabled) {
      const needsPlan = shouldGeneratePlan(goal, this.stateManager.get().plan, this.config.planning);
      
      if (needsPlan && this.llmCaller) {
        plan = await generatePlan(goal, context, this.config.planning, this.llmCaller);
        this.stateManager.setPlan(plan);
        this.callbacks.onPlanCreated?.(plan);
        
        // Create initial checkpoint
        if (this.config.checkpoint.enabled) {
          const checkpoint = await this.checkpointManager.createCheckpoint(
            this.stateManager.get(),
            { trigger: "manual", description: "Plan created" }
          );
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
  async executeTool(
    tool: ToolCall,
    executor: (t: ToolCall) => Promise<ToolResult>
  ): Promise<ToolExecutionResult> {
    this.ensureInitialized();
    
    const state = this.stateManager.get();
    let wasBlocked = false;
    let blockReason: string | undefined;
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
    let result: ToolResult;
    
    if (this.config.retry.enabled) {
      const retryResult = await this.retryEngine.executeWithRetry(tool, executor);
      result = retryResult.finalResult;
      wasRetried = retryResult.totalAttempts > 1;
      retryAttempts = retryResult.totalAttempts;
    } else {
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
          const checkpoint = await this.checkpointManager.createCheckpoint(
            this.stateManager.get(),
            { trigger: "auto", description: `Step completed: ${state.activeStepId}` }
          );
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
      await this.checkpointManager.createCheckpoint(
        this.stateManager.get(),
        { trigger: "error", description: `Error: ${result.error?.slice(0, 50)}` }
      );
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
  async manageContext(messages: Message[]): Promise<{
    messages: Message[];
    summarized: boolean;
    tokensSaved: number;
  }> {
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
  async resume(checkpointId?: string): Promise<{
    success: boolean;
    contextToInject?: string;
    error?: string;
  }> {
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
  getStatus(): {
    hasPlan: boolean;
    progress: { completed: number; total: number; percent: number };
    activeStep: { id: string; title: string } | null;
    pendingApprovals: ApprovalRequest[];
    context: { turnCount: number; toolCalls: number; errors: number };
  } {
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
  formatStatus(): string {
    const status = this.getStatus();
    
    if (!status.hasPlan) {
      return "";
    }

    const lines: string[] = [
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
  formatPlanBlock(): string {
    const state = this.stateManager.getOrNull();
    if (!state?.plan) return "";

    const progress = this.stateManager.getProgress();
    const steps = state.plan.steps.map(step => ({
      id: step.id,
      title: step.title,
      status: state.completedStepIds.includes(step.id) ? "complete" as const :
              state.failedStepIds.includes(step.id) ? "failed" as const :
              step.id === state.activeStepId ? "active" as const : "pending" as const,
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
  formatPlanChecklist(): string {
    const state = this.stateManager.getOrNull();
    if (!state?.plan) return "";

    const progress = this.stateManager.getProgress();
    const lines: string[] = [
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
  approve(requestId: string): boolean {
    return this.approvalGate.approve(requestId);
  }

  /**
   * Deny a pending tool execution
   */
  deny(requestId: string): boolean {
    return this.approvalGate.deny(requestId);
  }

  /**
   * Create manual checkpoint
   */
  async checkpoint(description?: string): Promise<string> {
    const checkpoint = await this.checkpointManager.createCheckpoint(
      this.stateManager.get(),
      { trigger: "manual", description }
    );
    return checkpoint.id;
  }

  /**
   * Sync step statuses from the LLM's response plan block.
   * The LLM outputs a :::plan block with step statuses; we parse it after
   * the run and persist those updates so the next turn is accurate.
   */
  syncFromResponse(planData: {
    steps: Array<{ id: string; status: string }>;
  }): { stepsCompleted: string[]; stepsFailed: string[] } {
    const state = this.stateManager.getOrNull();
    if (!state?.plan) return { stepsCompleted: [], stepsFailed: [] };

    const stepsCompleted: string[] = [];
    const stepsFailed: string[] = [];

    for (const step of planData.steps) {
      const normalizedStatus = step.status.toLowerCase();
      if (normalizedStatus === "done" || normalizedStatus === "complete") {
        if (!state.completedStepIds.includes(step.id)) {
          this.stateManager.completeStep(step.id, "Completed");
          this.callbacks.onStepCompleted?.(step.id, "Completed");
          stepsCompleted.push(step.id);
        }
      } else if (normalizedStatus === "failed") {
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
  notifyToolCompletion(toolName: string, isError: boolean): {
    stepCompleted: boolean;
    completedStepId?: string;
    completedStepTitle?: string;
  } {
    if (!this.initialized) return { stepCompleted: false };
    const state = this.stateManager.getOrNull();
    if (!state?.plan || !state.activeStepId) return { stepCompleted: false };

    this.stateManager.recordToolCall();
    if (isError) return { stepCompleted: false };

    const activeStep = this.stateManager.getActiveStep();
    if (!activeStep) return { stepCompleted: false };

    // Lightweight heuristic: successful tool that aligns with the step's action
    const toolLower = toolName.toLowerCase();
    const actionLower = (activeStep.action ?? "").toLowerCase();
    const titleLower = (activeStep.title ?? "").toLowerCase();

    const toolActionMap: Record<string, string[]> = {
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
    const matches = keywords.some(
      (kw) => actionLower.includes(kw) || titleLower.includes(kw),
    );

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
  async cleanup(): Promise<void> {
    this.checkpointManager.stopAutoCheckpoint();
    await this.stateManager.cleanup();
  }

  // ──────────────────────────────────────────────────────────────────────────
  // Private Methods
  // ──────────────────────────────────────────────────────────────────────────

  private ensureInitialized(): void {
    if (!this.initialized) {
      throw new Error("Orchestrator not initialized. Call init() first.");
    }
  }
}

// ============================================================================
// Plan Block Types (for UI rendering)
// ============================================================================

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
export function parsePlanBlock(text: string): PlanBlockData | null {
  const match = text.match(/:::plan\s*([\s\S]*?)\s*:::/);
  if (!match) return null;
  
  try {
    return JSON.parse(match[1]) as PlanBlockData;
  } catch {
    return null;
  }
}

/**
 * Check if text contains a plan block
 */
export function hasPlanBlock(text: string): boolean {
  return /:::plan\s*[\s\S]*?\s*:::/.test(text);
}

// ============================================================================
// Factory
// ============================================================================

export function createOrchestrator(
  config: Partial<OrchestratorConfig> & { sessionId: string },
  callbacks?: OrchestratorCallbacks,
  llmCallerOrConfig?: LLMCaller | { apiKey: string; model?: string }
): EnhancedLoopOrchestrator {
  // Accept either a pre-built LLM caller or a config to create one
  let caller: LLMCaller;
  if (typeof llmCallerOrConfig === "function") {
    caller = llmCallerOrConfig;
  } else {
    caller = createOrchestratorLLMCaller(llmCallerOrConfig);
  }
  return new EnhancedLoopOrchestrator(config, callbacks, caller);
}
