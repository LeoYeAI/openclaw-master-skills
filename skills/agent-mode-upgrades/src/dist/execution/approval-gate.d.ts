/**
 * Tool Interception with Timed Approval Gates
 *
 * Intercepts risky tool calls, emits approval requests,
 * and either waits for human response or proceeds after timeout.
 */
import type { ToolCall } from "../types.js";
export type RiskLevel = "low" | "medium" | "high" | "critical";
export type ApprovalDecision = "approved" | "denied" | "timeout" | "pending";
export interface ApprovalRequest {
    id: string;
    tool: ToolCall;
    riskLevel: RiskLevel;
    riskReason: string;
    createdAt: number;
    timeoutMs: number;
    decision: ApprovalDecision;
    decidedAt?: number;
    decidedBy?: "human" | "timeout" | "auto";
}
export interface ApprovalGateConfig {
    /** Enable approval gates */
    enabled: boolean;
    /** Timeout before auto-proceeding (ms) */
    timeoutMs: number;
    /** Risk levels that require approval */
    requireApprovalFor: RiskLevel[];
    /** Auto-approve low-risk operations */
    autoApproveLowRisk: boolean;
    /** Auto-deny critical operations (require explicit approval) */
    autoDenyCritical: boolean;
    /** Callback when approval is needed */
    onApprovalNeeded?: (request: ApprovalRequest) => void;
    /** Callback when decision is made */
    onDecision?: (request: ApprovalRequest) => void;
}
export interface ApprovalResult {
    proceed: boolean;
    decision: ApprovalDecision;
    request: ApprovalRequest;
    waitedMs: number;
}
export declare function classifyToolRisk(tool: ToolCall): {
    level: RiskLevel;
    reason: string;
};
export declare class ApprovalGate {
    private config;
    private pendingRequests;
    private resolvers;
    constructor(config?: Partial<ApprovalGateConfig>);
    /**
     * Check if a tool call requires approval
     */
    requiresApproval(tool: ToolCall): boolean;
    /**
     * Request approval for a tool call
     * Returns a promise that resolves when approved, denied, or timed out
     */
    requestApproval(tool: ToolCall): Promise<ApprovalResult>;
    /**
     * Approve a pending request
     */
    approve(requestId: string): boolean;
    /**
     * Deny a pending request
     */
    deny(requestId: string): boolean;
    /**
     * Get all pending requests
     */
    getPendingRequests(): ApprovalRequest[];
    /**
     * Get a specific request
     */
    getRequest(requestId: string): ApprovalRequest | undefined;
    /**
     * Format pending request for display
     */
    formatPendingRequest(request: ApprovalRequest): string;
    private createRequest;
    private waitForDecision;
    private decide;
}
export declare function getApprovalGate(config?: Partial<ApprovalGateConfig>): ApprovalGate;
export declare function resetApprovalGate(): void;
/**
 * Create a tool execution wrapper that applies approval gates
 */
export declare function withApprovalGate<T>(gate: ApprovalGate, executor: (tool: ToolCall) => Promise<T>): (tool: ToolCall) => Promise<T | {
    blocked: true;
    reason: string;
}>;
//# sourceMappingURL=approval-gate.d.ts.map