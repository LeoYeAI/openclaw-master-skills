/**
 * Agent State Machine
 *
 * Provides observable state transitions for debugging, logging, and dashboards.
 */
// Valid state transitions
const TRANSITIONS = {
    idle: ["planning"],
    planning: ["executing", "error"],
    executing: ["reflecting", "waiting_human", "recovering", "completing"],
    reflecting: ["executing", "replanning", "completing"],
    replanning: ["executing", "error"],
    waiting_human: ["executing", "planning", "completing", "idle"],
    recovering: ["executing", "replanning", "error"],
    completing: ["idle"],
    error: ["idle"],
    complete: ["idle"],
};
export class AgentStateMachine {
    context;
    observers = [];
    config;
    metrics;
    constructor(config) {
        this.config = config;
        this.context = {
            state: "idle",
            previousState: null,
            enteredAt: Date.now(),
            metadata: {},
            history: [],
        };
        this.metrics = new Map();
        // Initialize metrics for all states
        for (const state of Object.keys(TRANSITIONS)) {
            this.metrics.set(state, { count: 0, totalMs: 0 });
        }
    }
    /**
     * Transition to a new state
     */
    transition(to, trigger, metadata) {
        const from = this.context.state;
        // Validate transition
        if (!TRANSITIONS[from].includes(to)) {
            throw new Error(`Invalid transition: ${from} -> ${to}`);
        }
        const now = Date.now();
        const timeInState = now - this.context.enteredAt;
        // Update metrics
        if (this.config.metrics) {
            const stateMetrics = this.metrics.get(from);
            if (stateMetrics) {
                stateMetrics.count += 1;
                stateMetrics.totalMs += timeInState;
            }
        }
        // Record transition
        const transition = {
            from,
            to,
            trigger,
            timestamp: now,
            metadata,
        };
        this.context.history.push(transition);
        this.context.previousState = from;
        this.context.state = to;
        this.context.enteredAt = now;
        this.context.metadata = metadata ?? {};
        // Log transition
        if (this.config.logging) {
            console.log(`[FSM] ${from} -> ${to} (${trigger}) [${timeInState}ms in ${from}]`);
            if (metadata) {
                console.log(`[FSM] metadata:`, JSON.stringify(metadata));
            }
        }
        // Notify observers
        for (const observer of this.observers) {
            try {
                observer.onTransition(transition);
            }
            catch (err) {
                console.error("[FSM] Observer error:", err);
            }
        }
    }
    /**
     * Get current state
     */
    getState() {
        return this.context.state;
    }
    /**
     * Get full state context
     */
    getContext() {
        return { ...this.context, history: [...this.context.history] };
    }
    /**
     * Get transition history
     */
    getHistory() {
        return this.context.history;
    }
    /**
     * Get metrics for all states
     */
    getMetrics() {
        const result = new Map();
        for (const [state, metrics] of this.metrics) {
            result.set(state, {
                count: metrics.count,
                totalMs: metrics.totalMs,
                avgMs: metrics.count > 0 ? metrics.totalMs / metrics.count : 0,
            });
        }
        return result;
    }
    /**
     * Check if a transition is valid
     */
    canTransition(to) {
        return TRANSITIONS[this.context.state].includes(to);
    }
    /**
     * Subscribe to state changes
     */
    subscribe(observer) {
        this.observers.push(observer);
        return () => {
            this.observers = this.observers.filter((o) => o !== observer);
        };
    }
    /**
     * Reset the state machine
     */
    reset() {
        this.context = {
            state: "idle",
            previousState: null,
            enteredAt: Date.now(),
            metadata: {},
            history: [],
        };
        for (const metrics of this.metrics.values()) {
            metrics.count = 0;
            metrics.totalMs = 0;
        }
    }
    /**
     * Serialize state for persistence
     */
    serialize() {
        return JSON.stringify({
            state: this.context.state,
            enteredAt: this.context.enteredAt,
            metadata: this.context.metadata,
            history: this.context.history,
        });
    }
    /**
     * Restore state from persistence
     */
    restore(serialized) {
        try {
            const data = JSON.parse(serialized);
            this.context = {
                state: data.state ?? "idle",
                previousState: null,
                enteredAt: data.enteredAt ?? Date.now(),
                metadata: data.metadata ?? {},
                history: data.history ?? [],
            };
        }
        catch (err) {
            console.error("[FSM] Failed to restore state:", err);
            this.reset();
        }
    }
}
// ============================================================================
// Built-in Observers
// ============================================================================
/**
 * Logging observer - logs all transitions to console
 */
export class LoggingObserver {
    lastTimestamp = Date.now();
    onTransition(transition) {
        const duration = transition.timestamp - this.lastTimestamp;
        console.log(`[${new Date(transition.timestamp).toISOString()}] ` +
            `${transition.from} -> ${transition.to} ` +
            `(${transition.trigger}) ` +
            `[${duration}ms]`);
        this.lastTimestamp = transition.timestamp;
    }
}
/**
 * Metrics observer - collects timing statistics
 */
export class MetricsObserver {
    stateTimers = new Map();
    transitionCounts = new Map();
    stateDurations = new Map();
    onTransition(transition) {
        // Track time in previous state
        const entryTime = this.stateTimers.get(transition.from);
        if (entryTime) {
            const duration = transition.timestamp - entryTime;
            const durations = this.stateDurations.get(transition.from) ?? [];
            durations.push(duration);
            this.stateDurations.set(transition.from, durations);
        }
        // Track entry time for new state
        this.stateTimers.set(transition.to, transition.timestamp);
        // Count transitions
        const key = `${transition.from}->${transition.to}`;
        this.transitionCounts.set(key, (this.transitionCounts.get(key) ?? 0) + 1);
    }
    getStats() {
        const avgDurations = {};
        let totalTransitions = 0;
        for (const [state, durations] of this.stateDurations) {
            if (durations.length > 0) {
                avgDurations[state] = durations.reduce((a, b) => a + b, 0) / durations.length;
            }
        }
        for (const count of this.transitionCounts.values()) {
            totalTransitions += count;
        }
        return {
            transitionCounts: Object.fromEntries(this.transitionCounts),
            avgDurations: avgDurations,
            totalTransitions,
        };
    }
}
/**
 * Broadcast observer - sends state changes via callback
 */
export class BroadcastObserver {
    sessionKey;
    broadcast;
    constructor(sessionKey, broadcast) {
        this.sessionKey = sessionKey;
        this.broadcast = broadcast;
    }
    onTransition(transition) {
        this.broadcast({
            type: "agent_state_change",
            sessionKey: this.sessionKey,
            data: {
                state: transition.to,
                previousState: transition.from,
                trigger: transition.trigger,
                metadata: transition.metadata,
                timestamp: transition.timestamp,
            },
        });
    }
}
//# sourceMappingURL=fsm.js.map