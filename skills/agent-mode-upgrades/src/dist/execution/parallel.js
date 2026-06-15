/**
 * Parallel Tool Execution
 *
 * Execute independent tools concurrently for speed improvements.
 */
// ============================================================================
// Tool Classification
// ============================================================================
/**
 * Tools that are known to be read-only (no side effects)
 */
const READ_ONLY_TOOLS = new Set([
    "Read",
    "web_search",
    "web_fetch",
    "image",
    "session_status",
    "sessions_list",
    "sessions_history",
    "agents_list",
    "cron", // cron:list, cron:status
    "nodes", // nodes:status
]);
/**
 * Tools that have side effects and should run sequentially
 */
const SIDE_EFFECT_TOOLS = new Set([
    "Write",
    "Edit",
    "exec",
    "message",
    "browser",
    "cron", // cron:add, cron:remove
    "gateway",
    "sessions_send",
    "sessions_spawn",
    "tts",
]);
/**
 * Check if a tool is read-only (no side effects)
 */
export function isReadOnlyTool(tool) {
    // Direct match
    if (READ_ONLY_TOOLS.has(tool.name))
        return true;
    // Check action parameter for tools with mixed behavior
    const action = tool.arguments.action;
    if (tool.name === "cron" && action) {
        return ["status", "list", "runs"].includes(action);
    }
    if (tool.name === "nodes" && action) {
        return ["status", "describe"].includes(action);
    }
    if (tool.name === "browser" && action) {
        return ["status", "snapshot", "screenshot", "tabs"].includes(action);
    }
    // exec with read-only commands
    if (tool.name === "exec") {
        const cmd = tool.arguments.command;
        if (cmd && isReadOnlyCommand(cmd))
            return true;
    }
    return false;
}
/**
 * Check if an exec command is read-only
 */
function isReadOnlyCommand(cmd) {
    const readOnlyPatterns = [
        /^(ls|cat|head|tail|grep|find|which|echo|pwd|date|whoami|hostname|uname)\b/,
        /^git\s+(status|log|diff|show|branch|remote|tag)\b/,
        /^(npm|yarn|pnpm)\s+(list|outdated|info|view|show)\b/,
        /^docker\s+(ps|images|logs|inspect)\b/,
        /^kubectl\s+(get|describe|logs)\b/,
        /^(file|stat|wc|du|df)\b/,
    ];
    const trimmed = cmd.trim();
    return readOnlyPatterns.some((p) => p.test(trimmed));
}
/**
 * Check if a tool has side effects
 */
export function hasSideEffects(tool) {
    if (isReadOnlyTool(tool))
        return false;
    if (SIDE_EFFECT_TOOLS.has(tool.name))
        return true;
    // Default: assume side effects for safety
    return true;
}
/**
 * Extract file path from tool arguments
 */
function extractFilePath(tool) {
    const path = tool.arguments.path;
    const filePath = tool.arguments.file_path;
    return path ?? filePath ?? null;
}
/**
 * Check for file path conflicts between tools
 */
function hasFileConflict(a, b) {
    const aPath = extractFilePath(a);
    const bPath = extractFilePath(b);
    if (!aPath || !bPath)
        return false;
    // Same file = dependency
    if (aPath === bPath)
        return true;
    // One is parent of other
    if (aPath.startsWith(bPath + "/") || bPath.startsWith(aPath + "/")) {
        return true;
    }
    return false;
}
/**
 * Check if tool B references output from tool A
 */
function referencesOutput(toolB, toolA) {
    const argsStr = JSON.stringify(toolB.arguments);
    // Check for explicit references
    if (argsStr.includes(`{{${toolA.id}}}`))
        return true;
    if (argsStr.includes(`result_of_${toolA.name}`))
        return true;
    return false;
}
/**
 * Find dependencies for a tool
 */
function findDependencies(tool, previousTools) {
    const deps = [];
    for (const prev of previousTools) {
        // Check output reference
        if (referencesOutput(tool, prev)) {
            deps.push(prev.id);
            continue;
        }
        // Check file conflicts
        if (hasFileConflict(tool, prev)) {
            deps.push(prev.id);
            continue;
        }
        // Write after read on same file
        if ((tool.name === "Write" || tool.name === "Edit") &&
            prev.name === "Read" &&
            extractFilePath(tool) === extractFilePath(prev)) {
            deps.push(prev.id);
        }
    }
    return deps;
}
// ============================================================================
// Tool Classification
// ============================================================================
/**
 * Classify tool calls into parallel and sequential groups
 */
export function classifyToolDependencies(toolCalls, config) {
    if (!config.parallelTools) {
        // All sequential if parallel disabled
        return {
            parallel: [],
            sequential: toolCalls,
            dependencyGraph: new Map(),
        };
    }
    const graph = new Map();
    const sequential = [];
    const parallel = [];
    for (let i = 0; i < toolCalls.length; i++) {
        const tool = toolCalls[i];
        const previousTools = toolCalls.slice(0, i);
        const deps = findDependencies(tool, previousTools);
        if (deps.length > 0) {
            graph.set(tool.id, deps);
            sequential.push(tool);
        }
        else if (hasSideEffects(tool)) {
            // Side-effecting tools run sequentially for safety
            sequential.push(tool);
        }
        else {
            parallel.push(tool);
        }
    }
    return { parallel, sequential, dependencyGraph: graph };
}
// ============================================================================
// Parallel Execution
// ============================================================================
/**
 * Execute tools with parallelism where possible
 */
export async function executeToolCalls(toolCalls, executor, config) {
    const { parallel, sequential, dependencyGraph } = classifyToolDependencies(toolCalls, config);
    const results = new Map();
    // Execute parallel tools concurrently (with limit)
    if (parallel.length > 0) {
        const parallelResults = await executeParallelWithLimit(parallel, executor, config.maxConcurrentTools);
        for (const [id, result] of parallelResults) {
            results.set(id, result);
        }
    }
    // Execute sequential tools in dependency order
    const executed = new Set();
    while (executed.size < sequential.length) {
        // Find tools whose dependencies are satisfied
        const ready = sequential.filter((tool) => {
            if (executed.has(tool.id))
                return false;
            const deps = dependencyGraph.get(tool.id) ?? [];
            return deps.every((d) => results.has(d) || executed.has(d));
        });
        if (ready.length === 0 && executed.size < sequential.length) {
            // Circular dependency - execute remaining sequentially
            console.warn("[parallel] Circular dependency detected, falling back to sequential");
            for (const tool of sequential) {
                if (!executed.has(tool.id)) {
                    const result = await executor(tool);
                    results.set(tool.id, result);
                    executed.add(tool.id);
                }
            }
            break;
        }
        // Execute ready tools (could parallelize within this batch too)
        for (const tool of ready) {
            const result = await executor(tool);
            results.set(tool.id, result);
            executed.add(tool.id);
        }
    }
    return results;
}
/**
 * Execute tools in parallel with concurrency limit
 */
async function executeParallelWithLimit(tools, executor, limit) {
    const results = new Map();
    // Process in batches
    for (let i = 0; i < tools.length; i += limit) {
        const batch = tools.slice(i, i + limit);
        const batchResults = await Promise.allSettled(batch.map(async (tool) => {
            const result = await executor(tool);
            return { id: tool.id, result };
        }));
        for (const settled of batchResults) {
            if (settled.status === "fulfilled") {
                results.set(settled.value.id, settled.value.result);
            }
            else {
                // Find the tool that failed
                const tool = batch[batchResults.indexOf(settled)];
                results.set(tool.id, {
                    id: tool.id,
                    success: false,
                    error: settled.reason?.message ?? "Unknown error",
                });
            }
        }
    }
    return results;
}
/**
 * Execute tools and return metrics
 */
export async function executeWithMetrics(toolCalls, executor, config) {
    const startTime = Date.now();
    let sumToolTimeMs = 0;
    const timedExecutor = async (tool) => {
        const toolStart = Date.now();
        const result = await executor(tool);
        sumToolTimeMs += Date.now() - toolStart;
        return result;
    };
    const { parallel, sequential } = classifyToolDependencies(toolCalls, config);
    const results = await executeToolCalls(toolCalls, timedExecutor, config);
    const wallTimeMs = Date.now() - startTime;
    const parallelBatches = Math.ceil(parallel.length / config.maxConcurrentTools);
    const metrics = {
        totalTools: toolCalls.length,
        parallelBatches,
        sequentialTools: sequential.length,
        wallTimeMs,
        sumToolTimeMs,
        speedup: sumToolTimeMs > 0 ? sumToolTimeMs / wallTimeMs : 1,
    };
    return { results, metrics };
}
//# sourceMappingURL=parallel.js.map