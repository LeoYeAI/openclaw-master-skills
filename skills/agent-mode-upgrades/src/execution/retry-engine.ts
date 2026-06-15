/**
 * Automatic Retry with Alternative Approaches
 * 
 * When a tool fails, diagnoses the error and attempts recovery
 * using alternative strategies before giving up.
 */

import type { ToolCall, ToolResult, LLMCaller } from "../types.js";

// ============================================================================
// Types
// ============================================================================

export interface RetryConfig {
  /** Enable automatic retries */
  enabled: boolean;
  /** Maximum retry attempts per tool call */
  maxAttempts: number;
  /** Delay between retries (ms) */
  retryDelayMs: number;
  /** Use LLM to generate alternative approaches */
  useLLMAlternatives: boolean;
  /** Learn from errors across sessions */
  learnFromErrors: boolean;
}

export interface ErrorDiagnosis {
  category: ErrorCategory;
  isRetryable: boolean;
  suggestedFix: string;
  alternativeApproach?: AlternativeApproach;
}

export interface AlternativeApproach {
  description: string;
  modifiedTool?: ToolCall;
  differentTool?: ToolCall;
}

export interface RetryAttempt {
  attemptNumber: number;
  originalTool: ToolCall;
  usedTool: ToolCall;
  result: ToolResult;
  diagnosis?: ErrorDiagnosis;
  timestamp: number;
}

export interface RetryResult {
  success: boolean;
  finalResult: ToolResult;
  attempts: RetryAttempt[];
  totalAttempts: number;
  recoveryStrategy?: string;
}

export type ErrorCategory =
  | "permission"
  | "not_found"
  | "network"
  | "timeout"
  | "rate_limit"
  | "invalid_input"
  | "resource_busy"
  | "quota_exceeded"
  | "syntax_error"
  | "dependency_missing"
  | "unknown";

// ============================================================================
// Error Patterns
// ============================================================================

const ERROR_PATTERNS: Array<{
  pattern: RegExp;
  category: ErrorCategory;
  retryable: boolean;
  fix: string;
}> = [
  // Permission errors
  { pattern: /permission denied|access denied|EACCES|EPERM/i, category: "permission", retryable: false, fix: "Check file permissions or use sudo" },
  { pattern: /unauthorized|401|forbidden|403/i, category: "permission", retryable: false, fix: "Check authentication credentials" },
  
  // Not found errors
  { pattern: /not found|ENOENT|no such file|does not exist|404/i, category: "not_found", retryable: false, fix: "Verify path exists or create it first" },
  { pattern: /command not found|not recognized/i, category: "not_found", retryable: false, fix: "Install required command or check PATH" },
  
  // Network errors
  { pattern: /network|ECONNREFUSED|ENOTFOUND|ETIMEDOUT|connection refused/i, category: "network", retryable: true, fix: "Check network connectivity and try again" },
  { pattern: /DNS|resolve|lookup failed/i, category: "network", retryable: true, fix: "Check DNS resolution" },
  
  // Timeout errors
  { pattern: /timeout|timed out|deadline exceeded/i, category: "timeout", retryable: true, fix: "Increase timeout or simplify operation" },
  
  // Rate limiting
  { pattern: /rate limit|too many requests|429|throttle/i, category: "rate_limit", retryable: true, fix: "Wait and retry with exponential backoff" },
  { pattern: /quota|limit exceeded|capacity/i, category: "quota_exceeded", retryable: false, fix: "Check quota limits or upgrade plan" },
  
  // Input errors
  { pattern: /invalid|malformed|bad request|400|syntax error/i, category: "invalid_input", retryable: false, fix: "Check input format and parameters" },
  { pattern: /unexpected token|parse error|JSON/i, category: "syntax_error", retryable: false, fix: "Fix syntax in input data" },
  
  // Resource errors
  { pattern: /busy|locked|in use|EBUSY/i, category: "resource_busy", retryable: true, fix: "Wait for resource to become available" },
  { pattern: /no space|disk full|ENOSPC/i, category: "quota_exceeded", retryable: false, fix: "Free up disk space" },
  
  // Dependency errors
  { pattern: /module not found|cannot find|import error|require\(\)/i, category: "dependency_missing", retryable: false, fix: "Install missing dependency" },
];

// ============================================================================
// Alternative Approach Generators
// ============================================================================

const ALTERNATIVE_STRATEGIES: Record<ErrorCategory, (tool: ToolCall, error: string) => AlternativeApproach | null> = {
  permission: (tool) => {
    if (tool.name === "exec" && tool.arguments?.command) {
      const cmd = String(tool.arguments.command);
      // Don't suggest sudo for dangerous commands
      if (!/rm\s+-rf|dd\s+if/i.test(cmd)) {
        return {
          description: "Try with elevated permissions",
          modifiedTool: {
            ...tool,
            arguments: { ...tool.arguments, command: `sudo ${cmd}` },
          },
        };
      }
    }
    return null;
  },
  
  not_found: (tool) => {
    if (tool.name === "Read") {
      return {
        description: "Check if path exists first",
        differentTool: {
          id: `alt_${Date.now()}`,
          name: "exec",
          arguments: { command: `ls -la "${tool.arguments?.path || ""}"` },
        },
      };
    }
    if (tool.name === "exec" && tool.arguments?.command) {
      const cmd = String(tool.arguments.command);
      // If command not found, try with full path or package manager
      return {
        description: "Install missing command",
        differentTool: {
          id: `alt_${Date.now()}`,
          name: "exec", 
          arguments: { command: `which ${cmd.split(" ")[0]} || apt-get install -y ${cmd.split(" ")[0]} 2>/dev/null || npm install -g ${cmd.split(" ")[0]}` },
        },
      };
    }
    return null;
  },
  
  network: () => ({
    description: "Retry after brief delay",
    // Same tool, just retry
  }),
  
  timeout: (tool) => {
    if (tool.name === "exec" && tool.arguments) {
      return {
        description: "Retry with increased timeout",
        modifiedTool: {
          ...tool,
          arguments: { ...tool.arguments, timeout: ((tool.arguments.timeout as number) || 30) * 2 },
        },
      };
    }
    return null;
  },
  
  rate_limit: () => ({
    description: "Wait and retry with backoff",
  }),
  
  invalid_input: () => null, // Need human intervention
  
  resource_busy: () => ({
    description: "Wait for resource and retry",
  }),
  
  quota_exceeded: () => null, // Can't automatically fix
  
  syntax_error: () => null, // Need to fix syntax
  
  dependency_missing: (tool) => {
    if (tool.name === "exec") {
      return {
        description: "Install missing dependency first",
        // Would need context to know what to install
      };
    }
    return null;
  },
  
  unknown: () => null,
};

// ============================================================================
// Retry Engine
// ============================================================================

const DEFAULT_CONFIG: RetryConfig = {
  enabled: true,
  maxAttempts: 3,
  retryDelayMs: 1000,
  useLLMAlternatives: false,
  learnFromErrors: true,
};

export class RetryEngine {
  private config: RetryConfig;
  private llmCaller?: LLMCaller;
  private errorHistory: Array<{ tool: string; error: string; solution: string }> = [];

  constructor(config: Partial<RetryConfig> = {}, llmCaller?: LLMCaller) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.llmCaller = llmCaller;
  }

  /**
   * Diagnose an error and suggest recovery
   */
  diagnose(tool: ToolCall, error: string): ErrorDiagnosis {
    // Match against known patterns
    for (const { pattern, category, retryable, fix } of ERROR_PATTERNS) {
      if (pattern.test(error)) {
        const altGenerator = ALTERNATIVE_STRATEGIES[category];
        const alternative = altGenerator?.(tool, error) ?? undefined;
        
        return {
          category,
          isRetryable: retryable,
          suggestedFix: fix,
          alternativeApproach: alternative,
        };
      }
    }

    // Check error history for learned solutions
    const historicalMatch = this.errorHistory.find(h => 
      h.tool === tool.name && error.includes(h.error.slice(0, 50))
    );
    
    if (historicalMatch) {
      return {
        category: "unknown",
        isRetryable: true,
        suggestedFix: `Previously resolved: ${historicalMatch.solution}`,
      };
    }

    return {
      category: "unknown",
      isRetryable: false,
      suggestedFix: "Unknown error - may require manual intervention",
    };
  }

  /**
   * Execute a tool with automatic retry
   */
  async executeWithRetry(
    tool: ToolCall,
    executor: (t: ToolCall) => Promise<ToolResult>
  ): Promise<RetryResult> {
    const attempts: RetryAttempt[] = [];
    let currentTool = tool;
    let attempt = 0;

    while (attempt < this.config.maxAttempts) {
      attempt++;
      
      const result = await executor(currentTool);
      
      const attemptRecord: RetryAttempt = {
        attemptNumber: attempt,
        originalTool: tool,
        usedTool: currentTool,
        result,
        timestamp: Date.now(),
      };

      if (result.success) {
        attempts.push(attemptRecord);
        
        // Learn from successful retry
        if (attempt > 1 && this.config.learnFromErrors) {
          this.recordSuccess(tool, currentTool, attempts[0].result.error || "");
        }
        
        return {
          success: true,
          finalResult: result,
          attempts,
          totalAttempts: attempt,
          recoveryStrategy: attempt > 1 ? "retry_succeeded" : undefined,
        };
      }

      // Diagnose the error
      const diagnosis = this.diagnose(currentTool, result.error || "Unknown error");
      attemptRecord.diagnosis = diagnosis;
      attempts.push(attemptRecord);

      // If not retryable or last attempt, give up
      if (!diagnosis.isRetryable || attempt >= this.config.maxAttempts) {
        return {
          success: false,
          finalResult: result,
          attempts,
          totalAttempts: attempt,
        };
      }

      // Try alternative approach if available
      if (diagnosis.alternativeApproach?.modifiedTool) {
        currentTool = diagnosis.alternativeApproach.modifiedTool;
      } else if (diagnosis.alternativeApproach?.differentTool) {
        // For different tool, we'd need to handle separately
        // For now, just retry same tool
      }

      // Wait before retry
      await this.delay(this.config.retryDelayMs * attempt); // Exponential-ish backoff
    }

    return {
      success: false,
      finalResult: attempts[attempts.length - 1]?.result ?? { success: false, error: "Max attempts reached" },
      attempts,
      totalAttempts: attempt,
    };
  }

  /**
   * Generate LLM-powered alternative approach
   */
  async generateAlternative(
    tool: ToolCall,
    error: string,
    previousAttempts: RetryAttempt[]
  ): Promise<AlternativeApproach | null> {
    if (!this.llmCaller || !this.config.useLLMAlternatives) {
      return null;
    }

    const prompt = `A tool call failed. Suggest an alternative approach.

Tool: ${tool.name}
Arguments: ${JSON.stringify(tool.arguments)}
Error: ${error}

Previous attempts: ${previousAttempts.length}

Suggest either:
1. Modified arguments for the same tool
2. A different tool to achieve the same goal
3. Preparatory steps needed first

Answer in JSON:
{
  "description": "What to try",
  "approach": "modify_args" | "different_tool" | "prep_step",
  "tool": "tool_name",
  "arguments": { ... }
}`;

    try {
      const response = await this.llmCaller({
        messages: [
          { role: "system", content: "You help fix failed tool calls. Output valid JSON only." },
          { role: "user", content: prompt },
        ],
        maxTokens: 300,
      });

      const parsed = JSON.parse(response.content);
      
      if (parsed.approach === "modify_args") {
        return {
          description: parsed.description,
          modifiedTool: { id: tool.id, name: tool.name, arguments: parsed.arguments },
        };
      } else if (parsed.approach === "different_tool") {
        return {
          description: parsed.description,
          differentTool: { id: `alt_${Date.now()}`, name: parsed.tool, arguments: parsed.arguments },
        };
      }
      
      return { description: parsed.description };
    } catch {
      return null;
    }
  }

  /**
   * Record a successful recovery for future learning
   */
  private recordSuccess(originalTool: ToolCall, successfulTool: ToolCall, error: string): void {
    const solution = originalTool === successfulTool 
      ? "Retry succeeded"
      : `Modified: ${JSON.stringify(successfulTool.arguments)}`;
    
    this.errorHistory.push({
      tool: originalTool.name,
      error: error.slice(0, 100),
      solution,
    });

    // Keep history bounded
    if (this.errorHistory.length > 100) {
      this.errorHistory = this.errorHistory.slice(-50);
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// ============================================================================
// Factory
// ============================================================================

export function createRetryEngine(
  config?: Partial<RetryConfig>,
  llmCaller?: LLMCaller
): RetryEngine {
  return new RetryEngine(config, llmCaller);
}
