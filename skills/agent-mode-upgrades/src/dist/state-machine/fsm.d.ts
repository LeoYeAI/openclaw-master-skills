/**
 * Agent State Machine
 *
 * Provides observable state transitions for debugging, logging, and dashboards.
 */
import type { AgentState, StateContext, StateObserver, StateTransition, StateMachineConfig } from "../types.js";
export declare class AgentStateMachine {
    private context;
    private observers;
    private config;
    private metrics;
    constructor(config: StateMachineConfig);
    /**
     * Transition to a new state
     */
    transition(to: AgentState, trigger: string, metadata?: Record<string, unknown>): void;
    /**
     * Get current state
     */
    getState(): AgentState;
    /**
     * Get full state context
     */
    getContext(): Readonly<StateContext>;
    /**
     * Get transition history
     */
    getHistory(): readonly StateTransition[];
    /**
     * Get metrics for all states
     */
    getMetrics(): Map<AgentState, {
        count: number;
        totalMs: number;
        avgMs: number;
    }>;
    /**
     * Check if a transition is valid
     */
    canTransition(to: AgentState): boolean;
    /**
     * Subscribe to state changes
     */
    subscribe(observer: StateObserver): () => void;
    /**
     * Reset the state machine
     */
    reset(): void;
    /**
     * Serialize state for persistence
     */
    serialize(): string;
    /**
     * Restore state from persistence
     */
    restore(serialized: string): void;
}
/**
 * Logging observer - logs all transitions to console
 */
export declare class LoggingObserver implements StateObserver {
    private lastTimestamp;
    onTransition(transition: StateTransition): void;
}
/**
 * Metrics observer - collects timing statistics
 */
export declare class MetricsObserver implements StateObserver {
    private stateTimers;
    private transitionCounts;
    private stateDurations;
    onTransition(transition: StateTransition): void;
    getStats(): {
        transitionCounts: Record<string, number>;
        avgDurations: Record<AgentState, number>;
        totalTransitions: number;
    };
}
/**
 * Broadcast observer - sends state changes via callback
 */
export declare class BroadcastObserver implements StateObserver {
    private sessionKey;
    private broadcast;
    constructor(sessionKey: string, broadcast: (data: unknown) => void);
    onTransition(transition: StateTransition): void;
}
//# sourceMappingURL=fsm.d.ts.map