/**
 * Parallel Tool Execution
 *
 * Execute independent tools concurrently for speed improvements.
 */
import type { ToolCall, ToolResult, ClassifiedTools, ExecutionConfig, ToolExecutor } from "../types.js";
/**
 * Check if a tool is read-only (no side effects)
 */
export declare function isReadOnlyTool(tool: ToolCall): boolean;
/**
 * Check if a tool has side effects
 */
export declare function hasSideEffects(tool: ToolCall): boolean;
/**
 * Classify tool calls into parallel and sequential groups
 */
export declare function classifyToolDependencies(toolCalls: ToolCall[], config: ExecutionConfig): ClassifiedTools;
/**
 * Execute tools with parallelism where possible
 */
export declare function executeToolCalls(toolCalls: ToolCall[], executor: ToolExecutor, config: ExecutionConfig): Promise<Map<string, ToolResult>>;
export interface ExecutionMetrics {
    totalTools: number;
    parallelBatches: number;
    sequentialTools: number;
    wallTimeMs: number;
    sumToolTimeMs: number;
    speedup: number;
}
/**
 * Execute tools and return metrics
 */
export declare function executeWithMetrics(toolCalls: ToolCall[], executor: ToolExecutor, config: ExecutionConfig): Promise<{
    results: Map<string, ToolResult>;
    metrics: ExecutionMetrics;
}>;
//# sourceMappingURL=parallel.d.ts.map