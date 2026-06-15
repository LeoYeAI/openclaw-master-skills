/**
 * Semantic Error Recovery
 *
 * Diagnose errors and adapt approach instead of simple retry.
 */
/**
 * File operation error patterns
 */
const FILE_ERROR_PATTERNS = [
    {
        match: /ENOENT|no such file|file not found/i,
        strategy: (tool, _error) => {
            if (tool.name === "Read") {
                return {
                    type: "alternative_approach",
                    newPlan: `File ${tool.arguments.path} doesn't exist. Check if we need to create it first or use a different path.`,
                };
            }
            if (tool.name === "Edit") {
                return {
                    type: "retry_modified",
                    modifiedArgs: { ...tool.arguments, createIfMissing: true },
                };
            }
            return { type: "escalate", explanation: "File not found" };
        },
    },
    {
        match: /EACCES|permission denied/i,
        strategy: () => ({
            type: "alternative_approach",
            newPlan: "Permission denied. Try with elevated privileges or use a different location.",
        }),
    },
    {
        match: /ENOSPC|no space left/i,
        strategy: () => ({
            type: "escalate",
            explanation: "Disk full. Cannot continue without human intervention.",
        }),
    },
    {
        match: /EEXIST|already exists/i,
        strategy: (tool) => ({
            type: "alternative_approach",
            newPlan: `File/directory ${tool.arguments.path} already exists. Decide whether to overwrite, rename, or skip.`,
        }),
    },
    {
        match: /EISDIR|is a directory/i,
        strategy: () => ({
            type: "alternative_approach",
            newPlan: "Target is a directory, not a file. Adjust the path.",
        }),
    },
];
/**
 * Network error patterns
 */
const NETWORK_ERROR_PATTERNS = [
    {
        match: /ETIMEDOUT|timeout|timed out/i,
        strategy: () => ({
            type: "retry_same",
            delay: 5000,
        }),
    },
    {
        match: /ECONNREFUSED|connection refused/i,
        strategy: (tool) => ({
            type: "alternative_approach",
            newPlan: `Service is not running or refusing connections. Check if it needs to be started.`,
        }),
    },
    {
        match: /ENOTFOUND|getaddrinfo|DNS/i,
        strategy: () => ({
            type: "alternative_approach",
            newPlan: "DNS resolution failed. Check the hostname or network connectivity.",
        }),
    },
    {
        match: /404|not found/i,
        strategy: (tool) => ({
            type: "alternative_approach",
            newPlan: `Resource not found. Verify the URL or search for the correct endpoint.`,
        }),
    },
    {
        match: /401|unauthorized/i,
        strategy: () => ({
            type: "escalate",
            explanation: "Authentication required. Need credentials.",
        }),
    },
    {
        match: /403|forbidden/i,
        strategy: () => ({
            type: "escalate",
            explanation: "Access forbidden. Need different permissions.",
        }),
    },
    {
        match: /429|rate limit|too many requests/i,
        strategy: () => ({
            type: "retry_same",
            delay: 60000, // Wait 1 minute
        }),
    },
    {
        match: /5\d{2}|server error|internal error/i,
        strategy: () => ({
            type: "retry_same",
            delay: 10000,
        }),
    },
];
/**
 * Exec/command error patterns
 */
const EXEC_ERROR_PATTERNS = [
    {
        match: /command not found|not recognized/i,
        strategy: (tool) => {
            const cmd = tool.arguments.command?.split(" ")[0] ?? "command";
            return {
                type: "alternative_approach",
                newPlan: `Command '${cmd}' not installed. Try installing it or use an alternative.`,
            };
        },
    },
    {
        match: /npm ERR!.*ERESOLVE/i,
        strategy: () => ({
            type: "retry_modified",
            modifiedArgs: { command: "npm install --legacy-peer-deps" },
        }),
    },
    {
        match: /git.*conflict/i,
        strategy: () => ({
            type: "escalate",
            explanation: "Git merge conflict requires manual resolution.",
        }),
    },
    {
        match: /git.*diverged/i,
        strategy: () => ({
            type: "alternative_approach",
            newPlan: "Git branches have diverged. Need to decide whether to merge, rebase, or force push.",
        }),
    },
    {
        match: /docker.*no such image/i,
        strategy: () => ({
            type: "alternative_approach",
            newPlan: "Docker image not found. Need to build or pull it first.",
        }),
    },
    {
        match: /syntax error|parse error/i,
        strategy: () => ({
            type: "alternative_approach",
            newPlan: "Syntax error in command or script. Review and fix the syntax.",
        }),
    },
];
/**
 * All error patterns
 */
const ALL_ERROR_PATTERNS = [
    ...FILE_ERROR_PATTERNS,
    ...NETWORK_ERROR_PATTERNS,
    ...EXEC_ERROR_PATTERNS,
];
/**
 * Try to match error against known patterns
 */
function matchErrorPattern(tool, error) {
    for (const pattern of ALL_ERROR_PATTERNS) {
        if (pattern.match.test(error)) {
            return pattern.strategy(tool, error);
        }
    }
    return null;
}
// ============================================================================
// LLM-Based Diagnosis
// ============================================================================
const DIAGNOSIS_PROMPT = `A tool call failed. Diagnose the cause and suggest recovery.

Tool: {toolName}
Arguments: {arguments}
Error: {error}

Analyze:
1. What likely caused this error?
2. Is this recoverable?
3. What alternative approaches could work?
4. Should we skip this and continue, or is it blocking?

Output valid JSON:
{
  "cause": "Brief diagnosis",
  "recoverable": true|false|"maybe",
  "strategy": "alternative_approach"|"retry_modified"|"skip_and_continue"|"escalate"|"retry_same",
  "alternative": "If alternative_approach, describe the new approach",
  "modifiedArgs": {},  // If retry_modified, the new arguments
  "skipReason": "If skip_and_continue, explain why it's safe",
  "escalateExplanation": "If escalate, explain why human needed",
  "retryDelay": 0  // If retry_same, delay in ms
}`;
/**
 * Diagnose error using LLM
 */
async function llmDiagnose(tool, error, llmCall) {
    const prompt = DIAGNOSIS_PROMPT
        .replace("{toolName}", tool.name)
        .replace("{arguments}", JSON.stringify(tool.arguments, null, 2))
        .replace("{error}", error);
    try {
        const response = await llmCall({
            messages: [
                { role: "system", content: "You are diagnosing tool errors. Output valid JSON only." },
                { role: "user", content: prompt },
            ],
            maxTokens: 500,
        });
        const parsed = parseJsonFromResponse(response.content);
        if (!parsed) {
            return defaultDiagnosis(error);
        }
        const strategy = parseStrategy(parsed);
        return {
            cause: String(parsed.cause ?? "Unknown cause"),
            recoverable: parsed.recoverable ?? "maybe",
            strategy,
        };
    }
    catch {
        return defaultDiagnosis(error);
    }
}
function parseStrategy(parsed) {
    switch (parsed.strategy) {
        case "alternative_approach":
            return {
                type: "alternative_approach",
                newPlan: parsed.alternative ?? "Try a different approach",
            };
        case "retry_modified":
            return {
                type: "retry_modified",
                modifiedArgs: parsed.modifiedArgs ?? {},
            };
        case "skip_and_continue":
            return {
                type: "skip_and_continue",
                reason: parsed.skipReason ?? "Error is non-blocking",
            };
        case "escalate":
            return {
                type: "escalate",
                explanation: parsed.escalateExplanation ?? "Human intervention needed",
            };
        case "retry_same":
        default:
            return {
                type: "retry_same",
                delay: parsed.retryDelay ?? 1000,
            };
    }
}
function defaultDiagnosis(error) {
    return {
        cause: error,
        recoverable: "maybe",
        strategy: { type: "escalate", explanation: error },
    };
}
// ============================================================================
// Main Recovery Function
// ============================================================================
/**
 * Diagnose and get recovery strategy
 */
export async function diagnoseAndRecover(tool, result, config, llmCall) {
    if (!config.enabled) {
        return {
            cause: result.error ?? "Unknown error",
            recoverable: false,
            strategy: { type: "escalate", explanation: result.error ?? "Error recovery disabled" },
        };
    }
    const error = result.error ?? "Unknown error";
    // First, try pattern matching (fast)
    const patternStrategy = matchErrorPattern(tool, error);
    if (patternStrategy) {
        return {
            cause: error,
            recoverable: patternStrategy.type !== "escalate",
            strategy: patternStrategy,
        };
    }
    // Then, try LLM diagnosis (if available)
    if (llmCall) {
        return llmDiagnose(tool, error, llmCall);
    }
    // Fallback
    return defaultDiagnosis(error);
}
// ============================================================================
// Recovery Execution
// ============================================================================
/**
 * Execute tool with recovery attempts
 */
export async function executeWithRecovery(tool, executor, config, llmCall) {
    let attempts = 0;
    let currentTool = tool;
    const tried = new Set();
    while (attempts < config.maxAttempts) {
        attempts++;
        const callSignature = JSON.stringify(currentTool);
        // Prevent infinite loops
        if (tried.has(callSignature)) {
            return {
                result: {
                    id: tool.id,
                    success: false,
                    error: "Recovery loop detected",
                },
                attempts,
            };
        }
        tried.add(callSignature);
        try {
            const result = await executor(currentTool);
            if (result.success) {
                return { result, attempts };
            }
            // Tool returned an error result
            const diagnosis = await diagnoseAndRecover(currentTool, result, config, llmCall);
            switch (diagnosis.strategy.type) {
                case "retry_same":
                    if (diagnosis.strategy.delay) {
                        await sleep(diagnosis.strategy.delay);
                    }
                    // currentTool stays the same
                    break;
                case "retry_modified":
                    currentTool = {
                        ...currentTool,
                        arguments: { ...currentTool.arguments, ...diagnosis.strategy.modifiedArgs },
                    };
                    break;
                case "alternative_approach":
                    // Can't execute alternative here, return for replanning
                    return {
                        result: {
                            id: tool.id,
                            success: false,
                            error: result.error,
                            needsReplan: true,
                            reason: diagnosis.strategy.newPlan,
                        },
                        diagnosis,
                        attempts,
                    };
                case "skip_and_continue":
                    return {
                        result: {
                            id: tool.id,
                            success: false,
                            skipped: true,
                            reason: diagnosis.strategy.reason,
                        },
                        diagnosis,
                        attempts,
                    };
                case "escalate":
                    return {
                        result: {
                            id: tool.id,
                            success: false,
                            error: result.error,
                            needsHuman: true,
                            reason: diagnosis.strategy.explanation,
                        },
                        diagnosis,
                        attempts,
                    };
            }
        }
        catch (err) {
            // Unexpected exception
            const error = err instanceof Error ? err.message : String(err);
            const result = {
                id: tool.id,
                success: false,
                error,
            };
            if (attempts >= config.maxAttempts) {
                return { result, attempts };
            }
            const diagnosis = await diagnoseAndRecover(currentTool, result, config, llmCall);
            if (diagnosis.strategy.type === "escalate") {
                return { result, diagnosis, attempts };
            }
            // Apply non-escalate strategy and continue
            if (diagnosis.strategy.type === "retry_modified") {
                currentTool = {
                    ...currentTool,
                    arguments: { ...currentTool.arguments, ...diagnosis.strategy.modifiedArgs },
                };
            }
        }
    }
    return {
        result: {
            id: tool.id,
            success: false,
            error: `Failed after ${config.maxAttempts} recovery attempts`,
        },
        attempts,
    };
}
/**
 * Store for learned error patterns
 */
export class ErrorLearningStore {
    records = [];
    maxRecords = 100;
    add(record) {
        this.records.push(record);
        if (this.records.length > this.maxRecords) {
            this.records.shift();
        }
    }
    find(toolName, error) {
        // Find most recent matching record
        for (let i = this.records.length - 1; i >= 0; i--) {
            const record = this.records[i];
            if (record.toolName === toolName &&
                error.toLowerCase().includes(record.errorPattern.toLowerCase())) {
                return record.successfulRecovery;
            }
        }
        return null;
    }
    getRecords() {
        return this.records;
    }
    clear() {
        this.records = [];
    }
}
// ============================================================================
// Utilities
// ============================================================================
function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
function parseJsonFromResponse(content) {
    try {
        return JSON.parse(content);
    }
    catch {
        const match = content.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
        if (match) {
            try {
                return JSON.parse(match[1]);
            }
            catch {
                return null;
            }
        }
        return null;
    }
}
//# sourceMappingURL=error-recovery.js.map