/**
 * Persistent Plan State
 *
 * Stores and retrieves plan state across conversation turns.
 * State is persisted per-session to allow resumption.
 */
import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
// ============================================================================
// State Manager
// ============================================================================
export class PlanStateManager {
    config;
    state = null;
    dirty = false;
    autoSaveTimer = null;
    constructor(config) {
        this.config = {
            autoSaveInterval: 5000,
            maxCheckpoints: 10,
            ...config,
        };
    }
    /**
     * Initialize or load state for a session
     */
    async init(sessionId) {
        const existing = await this.load(sessionId);
        if (existing) {
            this.state = existing;
            this.state.context.turnCount++;
            this.state.context.lastActivity = Date.now();
        }
        else {
            this.state = this.createEmpty(sessionId);
        }
        this.dirty = true;
        this.startAutoSave();
        return this.state;
    }
    /**
     * Get current state (throws if not initialized)
     */
    get() {
        if (!this.state) {
            throw new Error("State not initialized. Call init() first.");
        }
        return this.state;
    }
    /**
     * Get state if available, null otherwise
     */
    getOrNull() {
        return this.state;
    }
    /**
     * Set the active plan
     */
    setPlan(plan) {
        if (!this.state)
            throw new Error("State not initialized");
        this.state.plan = plan;
        this.state.activeStepId = plan.steps[0]?.id ?? null;
        this.state.completedStepIds = [];
        this.state.failedStepIds = [];
        this.dirty = true;
    }
    /**
     * Mark a step as complete
     */
    completeStep(stepId, result) {
        if (!this.state?.plan)
            return;
        // Update step status
        const step = this.state.plan.steps.find(s => s.id === stepId);
        if (step) {
            step.status = "complete";
            if (result)
                step.result = result;
        }
        // Track completion
        if (!this.state.completedStepIds.includes(stepId)) {
            this.state.completedStepIds.push(stepId);
        }
        // Advance to next step
        this.advanceToNextStep();
        this.dirty = true;
    }
    /**
     * Mark a step as failed
     */
    failStep(stepId, error) {
        if (!this.state?.plan)
            return;
        const step = this.state.plan.steps.find(s => s.id === stepId);
        if (step) {
            step.status = "failed";
            step.result = error;
        }
        if (!this.state.failedStepIds.includes(stepId)) {
            this.state.failedStepIds.push(stepId);
        }
        this.state.context.totalErrors++;
        this.dirty = true;
    }
    /**
     * Record a tool call
     */
    recordToolCall() {
        if (!this.state)
            return;
        this.state.context.totalToolCalls++;
        this.state.context.lastActivity = Date.now();
        this.dirty = true;
    }
    /**
     * Get the current active step
     */
    getActiveStep() {
        if (!this.state?.plan || !this.state.activeStepId)
            return null;
        return this.state.plan.steps.find(s => s.id === this.state.activeStepId) ?? null;
    }
    /**
     * Get plan progress
     */
    getProgress() {
        if (!this.state?.plan) {
            return { completed: 0, total: 0, percent: 0 };
        }
        const total = this.state.plan.steps.length;
        const completed = this.state.completedStepIds.length;
        return {
            completed,
            total,
            percent: total > 0 ? Math.round((completed / total) * 100) : 0,
        };
    }
    /**
     * Create a checkpoint
     */
    createCheckpoint(description) {
        if (!this.state)
            throw new Error("State not initialized");
        const checkpoint = {
            id: `ckpt_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
            timestamp: Date.now(),
            stepId: this.state.activeStepId ?? "none",
            description,
            state: {
                plan: this.state.plan ? { ...this.state.plan } : null,
                activeStepId: this.state.activeStepId,
                completedStepIds: [...this.state.completedStepIds],
                context: { ...this.state.context },
            },
        };
        this.state.checkpoints.push(checkpoint);
        // Trim old checkpoints
        const max = this.config.maxCheckpoints ?? 10;
        if (this.state.checkpoints.length > max) {
            this.state.checkpoints = this.state.checkpoints.slice(-max);
        }
        this.dirty = true;
        return checkpoint;
    }
    /**
     * Restore from a checkpoint
     */
    restoreCheckpoint(checkpointId) {
        if (!this.state)
            return false;
        const checkpoint = this.state.checkpoints.find(c => c.id === checkpointId);
        if (!checkpoint?.state)
            return false;
        // Restore state from checkpoint
        if (checkpoint.state.plan) {
            this.state.plan = checkpoint.state.plan;
        }
        if (checkpoint.state.activeStepId !== undefined) {
            this.state.activeStepId = checkpoint.state.activeStepId;
        }
        if (checkpoint.state.completedStepIds) {
            this.state.completedStepIds = checkpoint.state.completedStepIds;
        }
        if (checkpoint.state.context) {
            this.state.context = { ...this.state.context, ...checkpoint.state.context };
        }
        this.dirty = true;
        return true;
    }
    /**
     * Format plan state for context injection
     */
    formatForContext() {
        if (!this.state?.plan)
            return "";
        const progress = this.getProgress();
        const lines = [
            "## Current Plan State",
            "",
            `**Goal:** ${this.state.plan.goal}`,
            `**Progress:** ${progress.completed}/${progress.total} steps (${progress.percent}%)`,
            "",
            "### Steps",
        ];
        for (const step of this.state.plan.steps) {
            const isActive = step.id === this.state.activeStepId;
            const icon = step.status === "complete" ? "✅" :
                step.status === "failed" ? "❌" :
                    step.status === "in_progress" ? "🔄" :
                        isActive ? "👉" : "⬜";
            lines.push(`${icon} **${step.title}**${isActive ? " ← current" : ""}`);
            if (step.result && step.status !== "pending") {
                lines.push(`   _${step.result}_`);
            }
        }
        if (this.state.checkpoints.length > 0) {
            const latest = this.state.checkpoints[this.state.checkpoints.length - 1];
            lines.push("");
            lines.push(`_Last checkpoint: ${latest.description} (${new Date(latest.timestamp).toLocaleTimeString()})_`);
        }
        return lines.join("\n");
    }
    /**
     * Save state to disk
     */
    async save() {
        if (!this.state || !this.dirty)
            return;
        await fs.mkdir(this.config.stateDir, { recursive: true });
        const filePath = this.getStatePath(this.state.sessionId);
        await fs.writeFile(filePath, JSON.stringify(this.state, null, 2));
        this.dirty = false;
    }
    /**
     * Load state from disk
     */
    async load(sessionId) {
        const filePath = this.getStatePath(sessionId);
        try {
            const content = await fs.readFile(filePath, "utf-8");
            return JSON.parse(content);
        }
        catch {
            return null;
        }
    }
    /**
     * Check if state exists for session
     */
    hasState(sessionId) {
        return fsSync.existsSync(this.getStatePath(sessionId));
    }
    /**
     * Clear state for session
     */
    async clear(sessionId) {
        const id = sessionId ?? this.state?.sessionId;
        if (!id)
            return;
        const filePath = this.getStatePath(id);
        try {
            await fs.unlink(filePath);
        }
        catch {
            // Ignore if doesn't exist
        }
        if (this.state?.sessionId === id) {
            this.state = null;
            this.dirty = false;
        }
    }
    /**
     * Cleanup: stop auto-save and save final state
     */
    async cleanup() {
        this.stopAutoSave();
        await this.save();
    }
    // ──────────────────────────────────────────────────────────────────────────
    // Private Methods
    // ──────────────────────────────────────────────────────────────────────────
    createEmpty(sessionId) {
        return {
            sessionId,
            plan: null,
            activeStepId: null,
            completedStepIds: [],
            failedStepIds: [],
            context: {
                turnCount: 1,
                totalToolCalls: 0,
                totalErrors: 0,
                lastActivity: Date.now(),
                startedAt: Date.now(),
            },
            checkpoints: [],
            metadata: {},
        };
    }
    getStatePath(sessionId) {
        // Sanitize session ID for filesystem
        const safeId = sessionId.replace(/[^a-zA-Z0-9_-]/g, "_");
        return path.join(this.config.stateDir, `${safeId}.json`);
    }
    advanceToNextStep() {
        if (!this.state?.plan)
            return;
        // Find next pending step with satisfied dependencies
        for (const step of this.state.plan.steps) {
            if (step.status !== "pending")
                continue;
            const depsComplete = step.dependencies.every(depId => this.state.completedStepIds.includes(depId));
            if (depsComplete) {
                this.state.activeStepId = step.id;
                step.status = "in_progress";
                return;
            }
        }
        // No more steps - plan complete
        this.state.activeStepId = null;
        if (this.state.plan) {
            this.state.plan.status = "completed";
        }
    }
    startAutoSave() {
        if (this.config.autoSaveInterval && this.config.autoSaveInterval > 0) {
            this.autoSaveTimer = setInterval(() => {
                this.save().catch(console.error);
            }, this.config.autoSaveInterval);
        }
    }
    stopAutoSave() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
    }
}
// ============================================================================
// Factory
// ============================================================================
let defaultManager = null;
export function getStateManager(config) {
    if (!defaultManager) {
        const home = process.env.HOME || process.env.USERPROFILE || "/tmp";
        defaultManager = new PlanStateManager({
            stateDir: path.join(home, ".openclaw", "agent-state"),
            ...config,
        });
    }
    return defaultManager;
}
export function resetStateManager() {
    defaultManager = null;
}
//# sourceMappingURL=persistence.js.map