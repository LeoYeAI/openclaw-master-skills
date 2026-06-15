/**
 * Checkpoint/Restore System
 *
 * Enables saving and restoring agent state for long-running tasks.
 * Supports automatic checkpointing at intervals and on significant events.
 */
import fs from "node:fs/promises";
import path from "node:path";
// ============================================================================
// Checkpoint Manager
// ============================================================================
const DEFAULT_CONFIG = {
    enabled: true,
    checkpointDir: "", // Set in constructor
    autoCheckpointInterval: 60000, // 1 minute
    maxCheckpointsPerSession: 5,
    checkpointOnStepComplete: true,
    checkpointOnError: true,
};
const CHECKPOINT_VERSION = 1;
export class CheckpointManager {
    config;
    autoCheckpointTimer = null;
    lastCheckpoint = null;
    constructor(config = {}) {
        const home = process.env.HOME || process.env.USERPROFILE || "/tmp";
        this.config = {
            ...DEFAULT_CONFIG,
            checkpointDir: path.join(home, ".openclaw", "checkpoints"),
            ...config,
        };
    }
    /**
     * Create a checkpoint from current state
     */
    async createCheckpoint(state, options = {}) {
        const checkpoint = {
            id: this.generateCheckpointId(),
            version: CHECKPOINT_VERSION,
            timestamp: Date.now(),
            sessionId: state.sessionId,
            plan: state.plan,
            activeStepId: state.activeStepId,
            completedStepIds: [...state.completedStepIds],
            failedStepIds: [...state.failedStepIds],
            context: { ...state.context },
            recentMessages: options.recentMessages,
            conversationSummary: options.conversationSummary,
            metadata: {
                description: options.description,
                trigger: options.trigger ?? "manual",
                stepAtCheckpoint: state.activeStepId ?? undefined,
            },
        };
        await this.saveCheckpoint(checkpoint);
        this.lastCheckpoint = checkpoint;
        // Cleanup old checkpoints
        await this.cleanupOldCheckpoints(state.sessionId);
        return checkpoint;
    }
    /**
     * Restore from a checkpoint
     */
    async restore(sessionId, checkpointId) {
        try {
            // Find checkpoint
            let checkpoint = null;
            if (checkpointId) {
                checkpoint = await this.loadCheckpoint(sessionId, checkpointId);
            }
            else {
                // Get most recent
                checkpoint = await this.getLatestCheckpoint(sessionId);
            }
            if (!checkpoint) {
                return {
                    success: false,
                    error: "No checkpoint found",
                };
            }
            // Generate resume prompt
            const resumePrompt = this.generateResumePrompt(checkpoint);
            return {
                success: true,
                checkpoint,
                resumePrompt,
            };
        }
        catch (err) {
            return {
                success: false,
                error: `Failed to restore: ${err}`,
            };
        }
    }
    /**
     * List available checkpoints for a session
     */
    async listCheckpoints(sessionId) {
        const sessionDir = this.getSessionDir(sessionId);
        try {
            const files = await fs.readdir(sessionDir);
            const checkpoints = [];
            for (const file of files) {
                if (!file.endsWith(".json"))
                    continue;
                try {
                    const content = await fs.readFile(path.join(sessionDir, file), "utf-8");
                    checkpoints.push(JSON.parse(content));
                }
                catch {
                    // Skip invalid files
                }
            }
            // Sort by timestamp descending
            return checkpoints.sort((a, b) => b.timestamp - a.timestamp);
        }
        catch {
            return [];
        }
    }
    /**
     * Get the latest checkpoint for a session
     */
    async getLatestCheckpoint(sessionId) {
        const checkpoints = await this.listCheckpoints(sessionId);
        return checkpoints[0] ?? null;
    }
    /**
     * Check if a session has incomplete work to resume
     */
    async hasIncompleteWork(sessionId) {
        const checkpoint = await this.getLatestCheckpoint(sessionId);
        if (!checkpoint?.plan) {
            return { hasWork: false };
        }
        // Check if plan is incomplete
        const totalSteps = checkpoint.plan.steps.length;
        const completedSteps = checkpoint.completedStepIds.length;
        const isIncomplete = completedSteps < totalSteps &&
            checkpoint.plan.status !== "completed" &&
            checkpoint.plan.status !== "abandoned";
        if (!isIncomplete) {
            return { hasWork: false };
        }
        // Calculate time since checkpoint
        const hoursSince = (Date.now() - checkpoint.timestamp) / (1000 * 60 * 60);
        return {
            hasWork: true,
            checkpoint,
            description: `Incomplete task: "${checkpoint.plan.goal}" (${completedSteps}/${totalSteps} steps, paused ${hoursSince.toFixed(1)}h ago)`,
        };
    }
    /**
     * Start auto-checkpointing
     */
    startAutoCheckpoint(sessionId, getState) {
        if (!this.config.enabled || this.config.autoCheckpointInterval <= 0)
            return;
        this.stopAutoCheckpoint();
        this.autoCheckpointTimer = setInterval(async () => {
            const state = getState();
            if (state?.plan && state.activeStepId) {
                await this.createCheckpoint(state, {
                    trigger: "interval",
                    description: "Auto-checkpoint",
                });
            }
        }, this.config.autoCheckpointInterval);
    }
    /**
     * Stop auto-checkpointing
     */
    stopAutoCheckpoint() {
        if (this.autoCheckpointTimer) {
            clearInterval(this.autoCheckpointTimer);
            this.autoCheckpointTimer = null;
        }
    }
    /**
     * Delete a checkpoint
     */
    async deleteCheckpoint(sessionId, checkpointId) {
        const filePath = path.join(this.getSessionDir(sessionId), `${checkpointId}.json`);
        try {
            await fs.unlink(filePath);
            return true;
        }
        catch {
            return false;
        }
    }
    /**
     * Format checkpoint for display
     */
    formatCheckpoint(checkpoint) {
        const date = new Date(checkpoint.timestamp).toLocaleString();
        const progress = checkpoint.plan
            ? `${checkpoint.completedStepIds.length}/${checkpoint.plan.steps.length} steps`
            : "No plan";
        return `
📍 **Checkpoint: ${checkpoint.id.slice(-8)}**
- **Created:** ${date}
- **Progress:** ${progress}
- **Trigger:** ${checkpoint.metadata.trigger}
${checkpoint.metadata.description ? `- **Note:** ${checkpoint.metadata.description}` : ""}
${checkpoint.plan ? `- **Goal:** ${checkpoint.plan.goal}` : ""}
`.trim();
    }
    /**
     * Format resume offer for user
     */
    formatResumeOffer(checkpoint) {
        const hoursSince = (Date.now() - checkpoint.timestamp) / (1000 * 60 * 60);
        const timeAgo = hoursSince < 1
            ? `${Math.round(hoursSince * 60)} minutes`
            : `${hoursSince.toFixed(1)} hours`;
        return `
🔄 **Incomplete Task Found**

You have an unfinished task from ${timeAgo} ago:

**Goal:** ${checkpoint.plan?.goal ?? "Unknown"}
**Progress:** ${checkpoint.completedStepIds.length}/${checkpoint.plan?.steps.length ?? 0} steps completed
**Paused at:** ${checkpoint.metadata.stepAtCheckpoint ?? "Unknown step"}

Would you like to:
- **Resume** - Continue from where you left off
- **Start fresh** - Begin a new task (checkpoint will be kept)
- **Discard** - Delete the checkpoint and start fresh

Reply with your choice.
`.trim();
    }
    // ──────────────────────────────────────────────────────────────────────────
    // Private Methods
    // ──────────────────────────────────────────────────────────────────────────
    generateCheckpointId() {
        return `ckpt_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    }
    getSessionDir(sessionId) {
        const safeId = sessionId.replace(/[^a-zA-Z0-9_-]/g, "_");
        return path.join(this.config.checkpointDir, safeId);
    }
    async saveCheckpoint(checkpoint) {
        const sessionDir = this.getSessionDir(checkpoint.sessionId);
        await fs.mkdir(sessionDir, { recursive: true });
        const filePath = path.join(sessionDir, `${checkpoint.id}.json`);
        await fs.writeFile(filePath, JSON.stringify(checkpoint, null, 2));
    }
    async loadCheckpoint(sessionId, checkpointId) {
        const filePath = path.join(this.getSessionDir(sessionId), `${checkpointId}.json`);
        try {
            const content = await fs.readFile(filePath, "utf-8");
            return JSON.parse(content);
        }
        catch {
            return null;
        }
    }
    async cleanupOldCheckpoints(sessionId) {
        const checkpoints = await this.listCheckpoints(sessionId);
        const max = this.config.maxCheckpointsPerSession;
        if (checkpoints.length <= max)
            return;
        // Delete oldest checkpoints beyond limit
        const toDelete = checkpoints.slice(max);
        for (const checkpoint of toDelete) {
            await this.deleteCheckpoint(sessionId, checkpoint.id);
        }
    }
    generateResumePrompt(checkpoint) {
        const lines = [
            "## Resuming from Checkpoint",
            "",
        ];
        if (checkpoint.conversationSummary) {
            lines.push("### Previous Context");
            lines.push(checkpoint.conversationSummary);
            lines.push("");
        }
        if (checkpoint.plan) {
            lines.push("### Plan Status");
            lines.push(`**Goal:** ${checkpoint.plan.goal}`);
            lines.push("");
            for (const step of checkpoint.plan.steps) {
                const isActive = step.id === checkpoint.activeStepId;
                const icon = checkpoint.completedStepIds.includes(step.id) ? "✅" :
                    checkpoint.failedStepIds.includes(step.id) ? "❌" :
                        isActive ? "👉" : "⬜";
                lines.push(`${icon} ${step.title}${isActive ? " ← resume here" : ""}`);
            }
            lines.push("");
        }
        lines.push("Continue executing the plan from the current step.");
        return lines.join("\n");
    }
}
// ============================================================================
// Factory
// ============================================================================
let defaultManager = null;
export function getCheckpointManager(config) {
    if (!defaultManager) {
        defaultManager = new CheckpointManager(config);
    }
    return defaultManager;
}
export function resetCheckpointManager() {
    defaultManager?.stopAutoCheckpoint();
    defaultManager = null;
}
//# sourceMappingURL=checkpoint.js.map