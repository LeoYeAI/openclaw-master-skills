/**
 * Enhanced Agentic Loop
 *
 * Main orchestrator that wraps the core runner with advanced capabilities:
 * - Planning and reflection
 * - Parallel tool execution
 * - Confidence-gated autonomy
 * - Semantic error recovery
 * - Proactive context management
 * - Observable state machine
 */
import type { EnhancedLoopConfig, EnhancedLoopState, EnhancedLoopCallbacks, ToolCall, ToolResult, LLMCaller, ToolExecutor } from "./types.js";
import { AgentStateMachine } from "./state-machine/fsm.js";
export declare const DEFAULT_CONFIG: EnhancedLoopConfig;
export declare class EnhancedAgentLoop {
    private config;
    private state;
    private stateMachine;
    private errorStore;
    private callbacks;
    constructor(config?: Partial<EnhancedLoopConfig>, callbacks?: EnhancedLoopCallbacks);
    /**
     * Get current configuration
     */
    getConfig(): EnhancedLoopConfig;
    /**
     * Update configuration
     */
    updateConfig(update: Partial<EnhancedLoopConfig>): void;
    /**
     * Get current state
     */
    getState(): Readonly<EnhancedLoopState>;
    /**
     * Run the enhanced loop
     */
    run(userGoal: string, context: string, llmCall: LLMCaller, toolExecutor: ToolExecutor, options?: {
        maxTokens?: number;
        maxIterations?: number;
        abortSignal?: AbortSignal;
    }): Promise<{
        success: boolean;
        result?: string;
        error?: string;
        metrics: {
            iterations: number;
            toolsExecuted: number;
            planGenerated: boolean;
            replans: number;
            humanEscalations: number;
        };
    }>;
    /**
     * Execute tool calls with enhanced features
     */
    executeTools(toolCalls: ToolCall[], executor: ToolExecutor, context: string, llmCall?: LLMCaller): Promise<Map<string, ToolResult>>;
    /**
     * Execute tools in parallel where possible
     */
    executeToolsParallel(toolCalls: ToolCall[], executor: ToolExecutor): Promise<{
        results: Map<string, ToolResult>;
        metrics?: unknown;
    }>;
    /**
     * Reset the loop state
     */
    reset(): void;
    /**
     * Get state machine metrics
     */
    getMetrics(): ReturnType<AgentStateMachine["getMetrics"]>;
    /**
     * Get state machine history
     */
    getHistory(): ReturnType<AgentStateMachine["getHistory"]>;
}
/**
 * Create an enhanced agent loop
 */
export declare function createEnhancedLoop(config?: Partial<EnhancedLoopConfig>, callbacks?: EnhancedLoopCallbacks): EnhancedAgentLoop;
//# sourceMappingURL=enhanced-loop.d.ts.map