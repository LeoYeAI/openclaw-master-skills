/**
 * Confidence-Gated Autonomy
 * 
 * Assess confidence before risky actions and escalate when appropriate.
 */

import type {
  ToolCall,
  RiskLevel,
  ConfidenceAssessment,
  GateDecision,
  ExecutionConfig,
  LLMCaller,
} from "../types.js";

// ============================================================================
// Risk Classification
// ============================================================================

/**
 * Tool risk levels
 */
const TOOL_RISK_MAP: Record<string, RiskLevel> = {
  // Low risk - read-only, no side effects
  Read: "low",
  web_search: "low",
  web_fetch: "low",
  image: "low",
  session_status: "low",
  sessions_list: "low",
  sessions_history: "low",
  agents_list: "low",

  // Medium risk - reversible side effects
  Write: "medium",
  Edit: "medium",
  exec: "medium", // Depends on command

  // High risk - may be irreversible
  message: "high", // External communication
  browser: "high", // Can click things
  sessions_send: "high",
  sessions_spawn: "high",

  // Critical - definitely irreversible (extend as needed)
  gateway: "high", // Config changes
};

/**
 * Patterns that elevate exec risk
 */
const DANGEROUS_EXEC_PATTERNS = [
  /rm\s+-rf/i,
  /drop\s+(table|database)/i,
  /delete\s+from/i,
  /truncate/i,
  /format\s+/i,
  /mkfs/i,
  /dd\s+if=/i,
];

const ELEVATED_EXEC_PATTERNS = [
  /git\s+push/i,
  /git\s+force/i,
  /npm\s+publish/i,
  /docker\s+push/i,
  /kubectl\s+delete/i,
  /terraform\s+destroy/i,
  /aws\s+.*delete/i,
];

/**
 * Classify the risk level of a tool call
 */
export function classifyRisk(tool: ToolCall): RiskLevel {
  const baseRisk = TOOL_RISK_MAP[tool.name] ?? "medium";

  // Special handling for exec
  if (tool.name === "exec") {
    const cmd = tool.arguments.command as string | undefined;
    if (cmd) {
      if (DANGEROUS_EXEC_PATTERNS.some((p) => p.test(cmd))) {
        return "critical";
      }
      if (ELEVATED_EXEC_PATTERNS.some((p) => p.test(cmd))) {
        return "high";
      }
    }
  }

  // Special handling for message (external comms)
  if (tool.name === "message") {
    return "high";
  }

  // Browser with action can be risky
  if (tool.name === "browser") {
    const action = tool.arguments.action as string | undefined;
    if (action && ["act", "click", "type", "navigate"].includes(action)) {
      return "high";
    }
  }

  return baseRisk;
}

/**
 * Check if a tool is low risk (can proceed without assessment)
 */
export function isLowRisk(tool: ToolCall): boolean {
  return classifyRisk(tool) === "low";
}

// ============================================================================
// Confidence Thresholds
// ============================================================================

export interface ConfidenceThresholds {
  proceedFreely: number;      // High confidence, just do it
  proceedCautiously: number;  // Create checkpoint, then proceed
  askHuman: number;           // Need human input
  refuse: number;             // Don't do without explicit approval
}

export const DEFAULT_THRESHOLDS: ConfidenceThresholds = {
  proceedFreely: 0.9,
  proceedCautiously: 0.7,
  askHuman: 0.5,
  refuse: 0.3,
};

/**
 * Resolve thresholds from config
 */
export function resolveThresholds(config: ExecutionConfig): ConfidenceThresholds {
  // Use config threshold as the "proceed cautiously" level
  // Derive others from it
  const cautious = config.confidenceThreshold;
  return {
    proceedFreely: Math.min(0.95, cautious + 0.2),
    proceedCautiously: cautious,
    askHuman: Math.max(0.3, cautious - 0.2),
    refuse: Math.max(0.1, cautious - 0.4),
  };
}

// ============================================================================
// Confidence Assessment
// ============================================================================

const ASSESSMENT_PROMPT = `Assess your confidence in the proposed action.

Proposed action: {action}
Arguments: {arguments}
Context: {context}

Consider:
1. How certain are you this is the right approach?
2. What could go wrong?
3. Is this reversible?
4. Do you have enough information?

Rate your confidence (0.0-1.0) and explain briefly.

Output valid JSON:
{
  "confidence": 0.0-1.0,
  "reversible": true|false|"partial",
  "reasoning": "Brief explanation",
  "suggestedQuestion": "Question for human if low confidence (optional)"
}`;

/**
 * Assess confidence in an action (via LLM)
 */
export async function assessConfidence(
  tool: ToolCall,
  context: string,
  llmCall: LLMCaller
): Promise<ConfidenceAssessment> {
  const prompt = ASSESSMENT_PROMPT
    .replace("{action}", tool.name)
    .replace("{arguments}", JSON.stringify(tool.arguments, null, 2))
    .replace("{context}", context);

  try {
    const response = await llmCall({
      messages: [
        { role: "system", content: "You are assessing action confidence. Output valid JSON only." },
        { role: "user", content: prompt },
      ],
      maxTokens: 300,
    });

    const parsed = parseJsonFromResponse(response.content);

    if (!parsed) {
      return defaultAssessment(tool);
    }

    return {
      confidence: clamp(Number(parsed.confidence) || 0.5, 0, 1),
      reversible: (parsed.reversible as boolean | "partial") ?? false,
      reasoning: String(parsed.reasoning ?? "No reasoning provided"),
      suggestedQuestion: parsed.suggestedQuestion as string | undefined,
    };
  } catch {
    return defaultAssessment(tool);
  }
}

/**
 * Quick confidence assessment without LLM (heuristic-based)
 */
export function quickAssessConfidence(tool: ToolCall): ConfidenceAssessment {
  const risk = classifyRisk(tool);

  const confidenceByRisk: Record<RiskLevel, number> = {
    low: 0.95,
    medium: 0.75,
    high: 0.55,
    critical: 0.3,
  };

  const reversibleByRisk: Record<RiskLevel, boolean | "partial"> = {
    low: true,
    medium: true,
    high: "partial",
    critical: false,
  };

  return {
    confidence: confidenceByRisk[risk],
    reversible: reversibleByRisk[risk],
    reasoning: `Risk level: ${risk}`,
  };
}

function defaultAssessment(tool: ToolCall): ConfidenceAssessment {
  const risk = classifyRisk(tool);
  return {
    confidence: risk === "low" ? 0.9 : risk === "medium" ? 0.7 : 0.5,
    reversible: risk !== "critical",
    reasoning: "Default assessment based on tool type",
  };
}

// ============================================================================
// Gate Decision
// ============================================================================

/**
 * Make a gate decision based on confidence assessment
 */
export function makeGateDecision(
  assessment: ConfidenceAssessment,
  thresholds: ConfidenceThresholds
): GateDecision {
  if (assessment.confidence >= thresholds.proceedFreely) {
    return { proceed: true, checkpoint: false };
  }

  if (assessment.confidence >= thresholds.proceedCautiously) {
    return {
      proceed: true,
      checkpoint: true,
      reason: assessment.reasoning,
    };
  }

  if (assessment.confidence >= thresholds.askHuman) {
    return {
      proceed: false,
      waitForHuman: true,
      question: assessment.suggestedQuestion ?? 
        `Confidence is ${(assessment.confidence * 100).toFixed(0)}%. Should I proceed?`,
      options: ["Yes, proceed", "No, cancel", "Modify approach"],
    };
  }

  return {
    proceed: false,
    refused: true,
    reason: `Confidence too low (${(assessment.confidence * 100).toFixed(0)}%): ${assessment.reasoning}`,
  };
}

/**
 * Full gate check: assess and decide
 */
export async function gateAction(
  tool: ToolCall,
  context: string,
  config: ExecutionConfig,
  llmCall?: LLMCaller
): Promise<{ assessment: ConfidenceAssessment; decision: GateDecision }> {
  if (!config.confidenceGates) {
    // Gates disabled, always proceed
    return {
      assessment: { confidence: 1, reversible: true, reasoning: "Gates disabled" },
      decision: { proceed: true, checkpoint: false },
    };
  }

  // Skip assessment for low-risk tools
  if (isLowRisk(tool)) {
    const assessment = quickAssessConfidence(tool);
    return {
      assessment,
      decision: { proceed: true, checkpoint: false },
    };
  }

  // Full assessment
  const assessment = llmCall
    ? await assessConfidence(tool, context, llmCall)
    : quickAssessConfidence(tool);

  const thresholds = resolveThresholds(config);
  const decision = makeGateDecision(assessment, thresholds);

  return { assessment, decision };
}

// ============================================================================
// Checkpointing
// ============================================================================

export interface Checkpoint {
  id: string;
  timestamp: number;
  tool: ToolCall;
  context: string;
  files?: { path: string; content: string }[];
}

/**
 * Create a checkpoint before a risky action
 */
export async function createCheckpoint(
  tool: ToolCall,
  context: string,
  readFile?: (path: string) => Promise<string | null>
): Promise<Checkpoint> {
  const checkpoint: Checkpoint = {
    id: `ckpt_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
    timestamp: Date.now(),
    tool,
    context,
  };

  // For file operations, snapshot the file
  if (readFile && (tool.name === "Write" || tool.name === "Edit")) {
    const path = tool.arguments.path as string | undefined;
    if (path) {
      try {
        const content = await readFile(path);
        if (content !== null) {
          checkpoint.files = [{ path, content }];
        }
      } catch {
        // File doesn't exist, no snapshot needed
      }
    }
  }

  return checkpoint;
}

// ============================================================================
// Utilities
// ============================================================================

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function parseJsonFromResponse(content: string): Record<string, unknown> | null {
  try {
    return JSON.parse(content);
  } catch {
    const match = content.match(/```(?:json)?\s*([\s\S]*?)\s*```/);
    if (match) {
      try {
        return JSON.parse(match[1]);
      } catch {
        return null;
      }
    }
    return null;
  }
}
