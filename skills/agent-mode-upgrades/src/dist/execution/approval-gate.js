/**
 * Tool Interception with Timed Approval Gates
 *
 * Intercepts risky tool calls, emits approval requests,
 * and either waits for human response or proceeds after timeout.
 */
// ============================================================================
// Risk Classification
// ============================================================================
const TOOL_RISK_LEVELS = {
    // Low risk - read-only
    Read: "low",
    web_search: "low",
    web_fetch: "low",
    image: "low",
    session_status: "low",
    sessions_list: "low",
    sessions_history: "low",
    agents_list: "low",
    // Medium risk - local side effects
    Write: "medium",
    Edit: "medium",
    exec: "medium", // Elevated based on command
    // High risk - external effects
    message: "high",
    browser: "high",
    sessions_send: "high",
    sessions_spawn: "high",
    cron: "high",
    // Critical - system changes
    gateway: "critical",
};
const DANGEROUS_PATTERNS = [
    { pattern: /rm\s+-rf/i, level: "critical", reason: "Recursive delete" },
    { pattern: /drop\s+(table|database)/i, level: "critical", reason: "Database drop" },
    { pattern: /truncate/i, level: "critical", reason: "Data truncation" },
    { pattern: /mkfs|format/i, level: "critical", reason: "Disk format" },
    { pattern: /dd\s+if=/i, level: "critical", reason: "Direct disk write" },
    { pattern: /:(){ :|:& };:/i, level: "critical", reason: "Fork bomb" },
    { pattern: />\s*\/dev\/(sda|hda|nvme)/i, level: "critical", reason: "Direct device write" },
    { pattern: /chmod\s+777/i, level: "high", reason: "Insecure permissions" },
    { pattern: /curl.*\|\s*(bash|sh)/i, level: "high", reason: "Piped script execution" },
    { pattern: /git\s+push.*--force/i, level: "high", reason: "Force push" },
    { pattern: /npm\s+publish/i, level: "high", reason: "Package publish" },
    { pattern: /docker\s+push/i, level: "high", reason: "Image publish" },
    { pattern: /kubectl\s+delete/i, level: "high", reason: "K8s resource deletion" },
    { pattern: /terraform\s+destroy/i, level: "high", reason: "Infrastructure destroy" },
];
export function classifyToolRisk(tool) {
    const baseLevel = TOOL_RISK_LEVELS[tool.name] ?? "medium";
    let level = baseLevel;
    let reason = `Tool type: ${tool.name}`;
    // Special handling for exec
    if (tool.name === "exec" && tool.arguments?.command) {
        const cmd = String(tool.arguments.command);
        for (const { pattern, level: patternLevel, reason: patternReason } of DANGEROUS_PATTERNS) {
            if (pattern.test(cmd)) {
                // Upgrade to more dangerous level
                if (riskOrdinal(patternLevel) > riskOrdinal(level)) {
                    level = patternLevel;
                    reason = patternReason;
                }
            }
        }
    }
    // Browser actions
    if (tool.name === "browser" && tool.arguments?.action) {
        const action = String(tool.arguments.action);
        if (["act", "click", "type"].includes(action)) {
            level = "high";
            reason = `Browser interaction: ${action}`;
        }
    }
    // Message sending
    if (tool.name === "message" && tool.arguments?.action === "send") {
        level = "high";
        reason = "External message";
    }
    return { level, reason };
}
function riskOrdinal(level) {
    return { low: 0, medium: 1, high: 2, critical: 3 }[level];
}
// ============================================================================
// Approval Gate
// ============================================================================
const DEFAULT_CONFIG = {
    enabled: true,
    timeoutMs: 10000, // 10 seconds
    requireApprovalFor: ["high", "critical"],
    autoApproveLowRisk: true,
    autoDenyCritical: false,
};
export class ApprovalGate {
    config;
    pendingRequests = new Map();
    resolvers = new Map();
    constructor(config = {}) {
        this.config = { ...DEFAULT_CONFIG, ...config };
    }
    /**
     * Check if a tool call requires approval
     */
    requiresApproval(tool) {
        if (!this.config.enabled)
            return false;
        const { level } = classifyToolRisk(tool);
        return this.config.requireApprovalFor.includes(level);
    }
    /**
     * Request approval for a tool call
     * Returns a promise that resolves when approved, denied, or timed out
     */
    async requestApproval(tool) {
        const { level, reason } = classifyToolRisk(tool);
        const startTime = Date.now();
        // Auto-approve low risk
        if (this.config.autoApproveLowRisk && level === "low") {
            return {
                proceed: true,
                decision: "approved",
                request: this.createRequest(tool, level, reason, "approved"),
                waitedMs: 0,
            };
        }
        // Auto-deny critical if configured
        if (this.config.autoDenyCritical && level === "critical") {
            const request = this.createRequest(tool, level, reason, "denied");
            request.decidedBy = "auto";
            return {
                proceed: false,
                decision: "denied",
                request,
                waitedMs: 0,
            };
        }
        // Create pending request
        const request = this.createRequest(tool, level, reason, "pending");
        this.pendingRequests.set(request.id, request);
        // Notify listeners
        this.config.onApprovalNeeded?.(request);
        // Wait for decision or timeout
        const decision = await this.waitForDecision(request);
        const waitedMs = Date.now() - startTime;
        // Update request
        request.decision = decision;
        request.decidedAt = Date.now();
        request.decidedBy = decision === "timeout" ? "timeout" : "human";
        // Cleanup
        this.pendingRequests.delete(request.id);
        this.resolvers.delete(request.id);
        // Notify listeners
        this.config.onDecision?.(request);
        return {
            proceed: decision === "approved" || decision === "timeout",
            decision,
            request,
            waitedMs,
        };
    }
    /**
     * Approve a pending request
     */
    approve(requestId) {
        return this.decide(requestId, "approved");
    }
    /**
     * Deny a pending request
     */
    deny(requestId) {
        return this.decide(requestId, "denied");
    }
    /**
     * Get all pending requests
     */
    getPendingRequests() {
        return Array.from(this.pendingRequests.values());
    }
    /**
     * Get a specific request
     */
    getRequest(requestId) {
        return this.pendingRequests.get(requestId);
    }
    /**
     * Format pending request for display
     */
    formatPendingRequest(request) {
        const timeLeft = Math.max(0, request.timeoutMs - (Date.now() - request.createdAt));
        const timeLeftSec = Math.round(timeLeft / 1000);
        return `
⚠️ **Approval Required**

**Tool:** ${request.tool.name}
**Risk:** ${request.riskLevel.toUpperCase()} - ${request.riskReason}
**Arguments:** \`${JSON.stringify(request.tool.arguments)}\`

⏱️ Auto-proceeding in ${timeLeftSec}s unless denied.

Reply with:
- \`/approve ${request.id.slice(-6)}\` to approve
- \`/deny ${request.id.slice(-6)}\` to deny
`.trim();
    }
    // ──────────────────────────────────────────────────────────────────────────
    // Private Methods
    // ──────────────────────────────────────────────────────────────────────────
    createRequest(tool, riskLevel, riskReason, decision) {
        return {
            id: `apr_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
            tool,
            riskLevel,
            riskReason,
            createdAt: Date.now(),
            timeoutMs: this.config.timeoutMs,
            decision,
        };
    }
    waitForDecision(request) {
        return new Promise((resolve) => {
            // Store resolver for external decisions
            this.resolvers.set(request.id, resolve);
            // Set timeout
            setTimeout(() => {
                if (this.pendingRequests.has(request.id)) {
                    resolve("timeout");
                }
            }, this.config.timeoutMs);
        });
    }
    decide(requestId, decision) {
        const resolver = this.resolvers.get(requestId);
        if (!resolver)
            return false;
        resolver(decision);
        return true;
    }
}
// ============================================================================
// Factory
// ============================================================================
let defaultGate = null;
export function getApprovalGate(config) {
    if (!defaultGate) {
        defaultGate = new ApprovalGate(config);
    }
    return defaultGate;
}
export function resetApprovalGate() {
    defaultGate = null;
}
// ============================================================================
// Middleware Helper
// ============================================================================
/**
 * Create a tool execution wrapper that applies approval gates
 */
export function withApprovalGate(gate, executor) {
    return async (tool) => {
        if (!gate.requiresApproval(tool)) {
            return executor(tool);
        }
        const result = await gate.requestApproval(tool);
        if (!result.proceed) {
            return {
                blocked: true,
                reason: `Tool blocked: ${result.decision} (${result.request.riskReason})`,
            };
        }
        return executor(tool);
    };
}
//# sourceMappingURL=approval-gate.js.map