/**
 * Checkpoint/Restore System
 *
 * Enables saving and restoring agent state for long-running tasks.
 * Supports automatic checkpointing at intervals and on significant events.
 */
import type { TaskPlan } from "../types.js";
import type { PlanState } from "./persistence.js";
import type { Message } from "../context/summarizer.js";
export interface CheckpointData {
    id: string;
    version: number;
    timestamp: number;
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
    recentMessages?: Message[];
    conversationSummary?: string;
    metadata: {
        description?: string;
        trigger?: "manual" | "auto" | "interval" | "error";
        stepAtCheckpoint?: string;
    };
}
export interface CheckpointConfig {
    /** Enable checkpointing */
    enabled: boolean;
    /** Directory for checkpoint files */
    checkpointDir: string;
    /** Auto-checkpoint interval (ms), 0 to disable */
    autoCheckpointInterval: number;
    /** Max checkpoints to keep per session */
    maxCheckpointsPerSession: number;
    /** Checkpoint on step completion */
    checkpointOnStepComplete: boolean;
    /** Checkpoint on errors */
    checkpointOnError: boolean;
}
export interface RestoreResult {
    success: boolean;
    checkpoint?: CheckpointData;
    error?: string;
    resumePrompt?: string;
}
export declare class CheckpointManager {
    private config;
    private autoCheckpointTimer;
    private lastCheckpoint;
    constructor(config?: Partial<CheckpointConfig>);
    /**
     * Create a checkpoint from current state
     */
    createCheckpoint(state: PlanState, options?: {
        description?: string;
        trigger?: CheckpointData["metadata"]["trigger"];
        recentMessages?: Message[];
        conversationSummary?: string;
    }): Promise<CheckpointData>;
    /**
     * Restore from a checkpoint
     */
    restore(sessionId: string, checkpointId?: string): Promise<RestoreResult>;
    /**
     * List available checkpoints for a session
     */
    listCheckpoints(sessionId: string): Promise<CheckpointData[]>;
    /**
     * Get the latest checkpoint for a session
     */
    getLatestCheckpoint(sessionId: string): Promise<CheckpointData | null>;
    /**
     * Check if a session has incomplete work to resume
     */
    hasIncompleteWork(sessionId: string): Promise<{
        hasWork: boolean;
        checkpoint?: CheckpointData;
        description?: string;
    }>;
    /**
     * Start auto-checkpointing
     */
    startAutoCheckpoint(sessionId: string, getState: () => PlanState | null): void;
    /**
     * Stop auto-checkpointing
     */
    stopAutoCheckpoint(): void;
    /**
     * Delete a checkpoint
     */
    deleteCheckpoint(sessionId: string, checkpointId: string): Promise<boolean>;
    /**
     * Format checkpoint for display
     */
    formatCheckpoint(checkpoint: CheckpointData): string;
    /**
     * Format resume offer for user
     */
    formatResumeOffer(checkpoint: CheckpointData): string;
    private generateCheckpointId;
    private getSessionDir;
    private saveCheckpoint;
    private loadCheckpoint;
    private cleanupOldCheckpoints;
    private generateResumePrompt;
}
export declare function getCheckpointManager(config?: Partial<CheckpointConfig>): CheckpointManager;
export declare function resetCheckpointManager(): void;
//# sourceMappingURL=checkpoint.d.ts.map