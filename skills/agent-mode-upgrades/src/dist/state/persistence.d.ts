/**
 * Persistent Plan State
 *
 * Stores and retrieves plan state across conversation turns.
 * State is persisted per-session to allow resumption.
 */
import type { TaskPlan, PlanStep } from "../types.js";
export interface PlanState {
    sessionId: string;
    plan: TaskPlan | null;
    activeStepId: string | null;
    completedStepIds: string[];
    failedStepIds: string[];
    context: {
        turnCount: number;
        totalToolCalls: number;
        totalErrors: number;
        lastActivity: number;
        startedAt: number;
    };
    checkpoints: Checkpoint[];
    metadata: Record<string, unknown>;
}
export interface Checkpoint {
    id: string;
    timestamp: number;
    stepId: string;
    description: string;
    state: Partial<PlanState>;
}
export interface StateManagerConfig {
    stateDir: string;
    autoSaveInterval?: number;
    maxCheckpoints?: number;
}
export declare class PlanStateManager {
    private config;
    private state;
    private dirty;
    private autoSaveTimer;
    constructor(config: StateManagerConfig);
    /**
     * Initialize or load state for a session
     */
    init(sessionId: string): Promise<PlanState>;
    /**
     * Get current state (throws if not initialized)
     */
    get(): PlanState;
    /**
     * Get state if available, null otherwise
     */
    getOrNull(): PlanState | null;
    /**
     * Set the active plan
     */
    setPlan(plan: TaskPlan): void;
    /**
     * Mark a step as complete
     */
    completeStep(stepId: string, result?: string): void;
    /**
     * Mark a step as failed
     */
    failStep(stepId: string, error: string): void;
    /**
     * Record a tool call
     */
    recordToolCall(): void;
    /**
     * Get the current active step
     */
    getActiveStep(): PlanStep | null;
    /**
     * Get plan progress
     */
    getProgress(): {
        completed: number;
        total: number;
        percent: number;
    };
    /**
     * Create a checkpoint
     */
    createCheckpoint(description: string): Checkpoint;
    /**
     * Restore from a checkpoint
     */
    restoreCheckpoint(checkpointId: string): boolean;
    /**
     * Format plan state for context injection
     */
    formatForContext(): string;
    /**
     * Save state to disk
     */
    save(): Promise<void>;
    /**
     * Load state from disk
     */
    load(sessionId: string): Promise<PlanState | null>;
    /**
     * Check if state exists for session
     */
    hasState(sessionId: string): boolean;
    /**
     * Clear state for session
     */
    clear(sessionId?: string): Promise<void>;
    /**
     * Cleanup: stop auto-save and save final state
     */
    cleanup(): Promise<void>;
    private createEmpty;
    private getStatePath;
    private advanceToNextStep;
    private startAutoSave;
    private stopAutoSave;
}
export declare function getStateManager(config?: Partial<StateManagerConfig>): PlanStateManager;
export declare function resetStateManager(): void;
//# sourceMappingURL=persistence.d.ts.map