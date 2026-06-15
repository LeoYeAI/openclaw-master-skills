/**
 * Confidence-Gated Autonomy
 *
 * Assess confidence before risky actions and escalate when appropriate.
 */
import type { ToolCall, RiskLevel, ConfidenceAssessment, GateDecision, ExecutionConfig, LLMCaller } from "../types.js";
/**
 * Classify the risk level of a tool call
 */
export declare function classifyRisk(tool: ToolCall): RiskLevel;
/**
 * Check if a tool is low risk (can proceed without assessment)
 */
export declare function isLowRisk(tool: ToolCall): boolean;
export interface ConfidenceThresholds {
    proceedFreely: number;
    proceedCautiously: number;
    askHuman: number;
    refuse: number;
}
export declare const DEFAULT_THRESHOLDS: ConfidenceThresholds;
/**
 * Resolve thresholds from config
 */
export declare function resolveThresholds(config: ExecutionConfig): ConfidenceThresholds;
/**
 * Assess confidence in an action (via LLM)
 */
export declare function assessConfidence(tool: ToolCall, context: string, llmCall: LLMCaller): Promise<ConfidenceAssessment>;
/**
 * Quick confidence assessment without LLM (heuristic-based)
 */
export declare function quickAssessConfidence(tool: ToolCall): ConfidenceAssessment;
/**
 * Make a gate decision based on confidence assessment
 */
export declare function makeGateDecision(assessment: ConfidenceAssessment, thresholds: ConfidenceThresholds): GateDecision;
/**
 * Full gate check: assess and decide
 */
export declare function gateAction(tool: ToolCall, context: string, config: ExecutionConfig, llmCall?: LLMCaller): Promise<{
    assessment: ConfidenceAssessment;
    decision: GateDecision;
}>;
export interface Checkpoint {
    id: string;
    timestamp: number;
    tool: ToolCall;
    context: string;
    files?: {
        path: string;
        content: string;
    }[];
}
/**
 * Create a checkpoint before a risky action
 */
export declare function createCheckpoint(tool: ToolCall, context: string, readFile?: (path: string) => Promise<string | null>): Promise<Checkpoint>;
//# sourceMappingURL=confidence-gate.d.ts.map