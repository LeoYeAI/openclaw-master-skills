/**
 * Automatic Step Completion Detection
 *
 * Analyzes tool results to determine if plan steps are complete.
 * Uses heuristics and optional LLM verification.
 */
const DEFAULT_CONFIG = {
    useLLMVerification: false,
    heuristicThreshold: 0.7,
    autoAdvance: true,
    failureKeywords: [
        "error", "failed", "failure", "exception", "cannot", "unable",
        "denied", "permission", "not found", "timeout", "refused"
    ],
    successKeywords: [
        "success", "complete", "created", "done", "finished", "wrote",
        "saved", "built", "deployed", "installed", "configured"
    ],
};
// ============================================================================
// Step Tracker
// ============================================================================
export class StepTracker {
    config;
    stateManager;
    llmCaller;
    constructor(stateManager, config = {}, llmCaller) {
        this.stateManager = stateManager;
        this.config = { ...DEFAULT_CONFIG, ...config };
        this.llmCaller = llmCaller;
    }
    /**
     * Analyze a tool result to determine if current step is complete
     */
    async analyzeToolResult(tool, result) {
        const state = this.stateManager.getOrNull();
        const activeStep = state ? this.stateManager.getActiveStep() : null;
        if (!activeStep) {
            return {
                isComplete: false,
                confidence: 1.0,
                reason: "No active step to track",
            };
        }
        // First, do heuristic analysis
        const heuristic = this.heuristicAnalysis(activeStep, tool, result);
        // If confident enough or LLM verification disabled, return heuristic
        if (heuristic.confidence >= this.config.heuristicThreshold || !this.config.useLLMVerification) {
            if (heuristic.isComplete && this.config.autoAdvance) {
                this.stateManager.completeStep(activeStep.id, heuristic.suggestedResult);
            }
            return heuristic;
        }
        // Use LLM for verification if available
        if (this.llmCaller) {
            const llmAnalysis = await this.llmVerification(activeStep, tool, result, heuristic);
            if (llmAnalysis.isComplete && this.config.autoAdvance) {
                this.stateManager.completeStep(activeStep.id, llmAnalysis.suggestedResult);
            }
            return llmAnalysis;
        }
        return heuristic;
    }
    /**
     * Manually mark step complete (for explicit completion)
     */
    markComplete(stepId, result) {
        const state = this.stateManager.getOrNull();
        if (!state?.plan)
            return;
        const id = stepId ?? state.activeStepId;
        if (id) {
            this.stateManager.completeStep(id, result);
        }
    }
    /**
     * Manually mark step failed
     */
    markFailed(stepId, error) {
        const state = this.stateManager.getOrNull();
        if (!state?.plan)
            return;
        const id = stepId ?? state.activeStepId;
        if (id) {
            this.stateManager.failStep(id, error ?? "Step failed");
        }
    }
    /**
     * Check if plan is complete
     */
    isPlanComplete() {
        const state = this.stateManager.getOrNull();
        if (!state?.plan)
            return false;
        return state.plan.steps.every(s => s.status === "complete" || s.status === "skipped");
    }
    /**
     * Get completion status summary
     */
    getStatus() {
        const state = this.stateManager.getOrNull();
        return {
            hasActivePlan: !!state?.plan,
            activeStep: this.stateManager.getActiveStep(),
            progress: this.stateManager.getProgress(),
            isComplete: this.isPlanComplete(),
        };
    }
    // ──────────────────────────────────────────────────────────────────────────
    // Private Methods
    // ──────────────────────────────────────────────────────────────────────────
    heuristicAnalysis(step, tool, result) {
        const resultText = this.resultToText(result);
        const lowerResult = resultText.toLowerCase();
        const lowerAction = step.action.toLowerCase();
        const lowerCriteria = step.successCriteria.toLowerCase();
        // Check for explicit failure
        const hasFailure = this.config.failureKeywords.some(kw => lowerResult.includes(kw) && !lowerResult.includes(`no ${kw}`));
        if (hasFailure && result.error) {
            return {
                isComplete: false,
                confidence: 0.9,
                reason: `Tool returned error: ${result.error.slice(0, 100)}`,
            };
        }
        // Check for explicit success keywords
        const successCount = this.config.successKeywords.filter(kw => lowerResult.includes(kw)).length;
        // Check if tool matches expected action
        const toolMatchesAction = this.toolMatchesStepAction(tool.name, lowerAction);
        // Check if result mentions success criteria keywords
        const criteriaWords = lowerCriteria.split(/\s+/).filter(w => w.length > 3);
        const criteriaMatches = criteriaWords.filter(w => lowerResult.includes(w)).length;
        const criteriaMatchRatio = criteriaWords.length > 0
            ? criteriaMatches / criteriaWords.length
            : 0;
        // Calculate confidence
        let confidence = 0;
        let reasons = [];
        if (result.success) {
            confidence += 0.4;
            reasons.push("Tool succeeded");
        }
        if (successCount > 0) {
            confidence += Math.min(0.2, successCount * 0.1);
            reasons.push(`Found ${successCount} success indicators`);
        }
        if (toolMatchesAction) {
            confidence += 0.2;
            reasons.push("Tool matches expected action");
        }
        if (criteriaMatchRatio > 0.3) {
            confidence += 0.2 * criteriaMatchRatio;
            reasons.push(`Success criteria ${Math.round(criteriaMatchRatio * 100)}% matched`);
        }
        const isComplete = confidence >= this.config.heuristicThreshold && result.success;
        return {
            isComplete,
            confidence,
            reason: reasons.join("; ") || "Insufficient indicators",
            suggestedResult: isComplete ? this.summarizeResult(resultText) : undefined,
        };
    }
    async llmVerification(step, tool, result, heuristic) {
        if (!this.llmCaller)
            return heuristic;
        const prompt = `Analyze if this plan step is complete based on the tool result.

Step: ${step.title}
Action: ${step.action}
Success Criteria: ${step.successCriteria}

Tool Used: ${tool.name}
Tool Arguments: ${JSON.stringify(tool.arguments)}
Tool Result: ${this.resultToText(result).slice(0, 1000)}

Heuristic Analysis: ${heuristic.reason} (confidence: ${heuristic.confidence})

Answer in JSON:
{
  "isComplete": true/false,
  "confidence": 0.0-1.0,
  "reason": "Brief explanation",
  "suggestedResult": "One-line summary if complete"
}`;
        try {
            const response = await this.llmCaller({
                messages: [
                    { role: "system", content: "You analyze task completion. Output valid JSON only." },
                    { role: "user", content: prompt },
                ],
                maxTokens: 200,
            });
            const parsed = JSON.parse(response.content);
            return {
                isComplete: parsed.isComplete ?? heuristic.isComplete,
                confidence: parsed.confidence ?? heuristic.confidence,
                reason: parsed.reason ?? heuristic.reason,
                suggestedResult: parsed.suggestedResult,
            };
        }
        catch {
            return heuristic;
        }
    }
    toolMatchesStepAction(toolName, action) {
        const toolActionMap = {
            exec: ["run", "execute", "install", "build", "deploy", "create", "setup", "configure"],
            Write: ["write", "create", "save", "add", "generate"],
            Edit: ["edit", "modify", "update", "change", "fix"],
            Read: ["read", "check", "verify", "inspect", "look"],
            web_search: ["search", "find", "research", "look up"],
            web_fetch: ["fetch", "get", "download", "retrieve"],
            browser: ["browse", "navigate", "open", "click", "interact"],
            message: ["send", "message", "notify", "email", "communicate"],
        };
        const keywords = toolActionMap[toolName] ?? [];
        return keywords.some(kw => action.includes(kw));
    }
    resultToText(result) {
        if (result.error)
            return `Error: ${result.error}`;
        if (typeof result.output === "string")
            return result.output;
        if (result.output)
            return JSON.stringify(result.output);
        return result.success ? "Success (no output)" : "Failed (no details)";
    }
    summarizeResult(text) {
        // Take first meaningful line or truncate
        const lines = text.split("\n").filter(l => l.trim().length > 0);
        const firstLine = lines[0] ?? "Completed";
        return firstLine.length > 100 ? firstLine.slice(0, 97) + "..." : firstLine;
    }
}
// ============================================================================
// Factory
// ============================================================================
export function createStepTracker(stateManager, config, llmCaller) {
    return new StepTracker(stateManager, config, llmCaller);
}
//# sourceMappingURL=step-tracker.js.map