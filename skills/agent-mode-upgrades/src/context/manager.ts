/**
 * Proactive Context Management
 * 
 * Manage context window efficiently with summarization and pruning.
 */

import type {
  TokenBudget,
  WorkingMemory,
  WorkingMemoryEntry,
  ContextConfig,
  AgentMessage,
  LLMCaller,
} from "../types.js";

// ============================================================================
// Token Estimation
// ============================================================================

/**
 * Rough token estimation (4 chars per token average)
 */
export function estimateTokens(text: string): number {
  return Math.ceil(text.length / 4);
}

/**
 * Estimate tokens for messages
 */
export function estimateMessageTokens(messages: AgentMessage[]): number {
  let total = 0;
  for (const msg of messages) {
    if (typeof msg.content === "string") {
      total += estimateTokens(msg.content);
    } else if (Array.isArray(msg.content)) {
      for (const block of msg.content) {
        if (block.text) {
          total += estimateTokens(block.text);
        }
      }
    }
    // Add overhead for role, etc.
    total += 10;
  }
  return total;
}

// ============================================================================
// Token Budget
// ============================================================================

/**
 * Create a token budget
 */
export function createTokenBudget(maxTokens: number): TokenBudget {
  return {
    max: maxTokens,
    used: 0,
    reserved: {
      systemPrompt: 0,
      responseBuffer: Math.floor(maxTokens * 0.2), // Reserve 20% for response
      toolResults: Math.floor(maxTokens * 0.1),    // Reserve 10% for pending tools
    },
  };
}

/**
 * Get available tokens
 */
export function getAvailableTokens(budget: TokenBudget): number {
  const reserved = Object.values(budget.reserved).reduce((a, b) => a + b, 0);
  return Math.max(0, budget.max - budget.used - reserved);
}

/**
 * Check if content fits in budget
 */
export function canFitInBudget(budget: TokenBudget, content: string): boolean {
  const tokens = estimateTokens(content);
  return tokens <= getAvailableTokens(budget);
}

/**
 * Update budget with used tokens
 */
export function updateBudget(budget: TokenBudget, tokens: number): TokenBudget {
  return {
    ...budget,
    used: budget.used + tokens,
  };
}

/**
 * Get budget usage percentage
 */
export function getBudgetUsage(budget: TokenBudget): number {
  return budget.used / budget.max;
}

// ============================================================================
// Working Memory
// ============================================================================

/**
 * Create a working memory store
 */
export function createWorkingMemory(): WorkingMemory {
  const entries = new Map<string, WorkingMemoryEntry>();

  return {
    entries,

    store(id: string, entry: Omit<WorkingMemoryEntry, "id">): void {
      entries.set(id, { id, ...entry });
    },

    retrieve(ids: string[]): string {
      const relevant: WorkingMemoryEntry[] = [];
      for (const id of ids) {
        const entry = entries.get(id);
        if (entry) {
          relevant.push(entry);
        }
      }

      if (relevant.length === 0) return "";

      return relevant
        .sort((a, b) => b.timestamp - a.timestamp)
        .map((e) => `### ${e.id}\n${e.summary}`)
        .join("\n\n");
    },

    search(query: string, limit = 5): WorkingMemoryEntry[] {
      const queryLower = query.toLowerCase();
      const scored: { entry: WorkingMemoryEntry; score: number }[] = [];

      for (const entry of entries.values()) {
        // Simple keyword matching
        const summaryLower = entry.summary.toLowerCase();
        let score = 0;

        for (const word of queryLower.split(/\s+/)) {
          if (summaryLower.includes(word)) {
            score += 1;
          }
        }

        if (score > 0) {
          scored.push({ entry, score });
        }
      }

      return scored
        .sort((a, b) => b.score - a.score)
        .slice(0, limit)
        .map((s) => s.entry);
    },

    prune(maxAgeMs = 30 * 60 * 1000): number {
      const now = Date.now();
      let pruned = 0;

      for (const [id, entry] of entries) {
        if (now - entry.timestamp > maxAgeMs) {
          entries.delete(id);
          pruned++;
        }
      }

      return pruned;
    },
  };
}

// ============================================================================
// Context Summarization
// ============================================================================

const SUMMARIZE_PROMPT = `Summarize the following tool results concisely.
Keep: errors, key findings, file paths created/modified, important values.
Drop: verbose output, duplicate info, formatting noise.

Tool Results:
{results}

Summary (2-3 sentences max):`;

/**
 * Summarize tool results
 */
export async function summarizeToolResults(
  results: { tool: string; result: string }[],
  llmCall: LLMCaller
): Promise<string> {
  const resultsText = results
    .map((r) => `[${r.tool}]\n${r.result}`)
    .join("\n\n");

  const prompt = SUMMARIZE_PROMPT.replace("{results}", resultsText);

  try {
    const response = await llmCall({
      messages: [
        { role: "system", content: "You are summarizing tool results. Be concise." },
        { role: "user", content: prompt },
      ],
      maxTokens: 300,
    });

    return response.content.trim();
  } catch {
    // Fallback: just truncate
    return results.map((r) => `${r.tool}: completed`).join("; ");
  }
}

const WORK_SESSION_PROMPT = `Summarize what was accomplished in this work session.

Tasks completed: {tasks}
Tools used: {tools}
Files affected: {files}

Create a brief summary covering:
1. What was done
2. Key outcomes
3. What's still pending (if any)

Summary:`;

/**
 * Summarize a work session
 */
export async function summarizeWorkSession(
  tasks: string[],
  toolsUsed: string[],
  filesAffected: string[],
  llmCall: LLMCaller
): Promise<string> {
  const prompt = WORK_SESSION_PROMPT
    .replace("{tasks}", tasks.join(", ") || "none")
    .replace("{tools}", [...new Set(toolsUsed)].join(", ") || "none")
    .replace("{files}", filesAffected.join(", ") || "none");

  try {
    const response = await llmCall({
      messages: [
        { role: "system", content: "You are summarizing a work session. Be concise." },
        { role: "user", content: prompt },
      ],
      maxTokens: 400,
    });

    return response.content.trim();
  } catch {
    return `Completed ${tasks.length} tasks using ${toolsUsed.length} tools.`;
  }
}

// ============================================================================
// Context Pruning
// ============================================================================

export interface PruneRules {
  keepLastMessages: number;
  keepRecentMs: number;
  alwaysKeepTypes: string[];
  pruneToolResultsAfterMs: number;
  summarizeBeforePrune: boolean;
}

export const DEFAULT_PRUNE_RULES: PruneRules = {
  keepLastMessages: 10,
  keepRecentMs: 300000, // 5 minutes
  alwaysKeepTypes: ["plan", "error", "human_input"],
  pruneToolResultsAfterMs: 60000, // 1 minute
  summarizeBeforePrune: true,
};

interface TaggedMessage extends AgentMessage {
  timestamp?: number;
  type?: string;
}

/**
 * Apply pruning rules to messages
 */
export function applyPruneRules(
  messages: TaggedMessage[],
  rules: PruneRules = DEFAULT_PRUNE_RULES
): { kept: TaggedMessage[]; pruned: TaggedMessage[] } {
  const now = Date.now();
  const kept: TaggedMessage[] = [];
  const pruned: TaggedMessage[] = [];

  for (let i = 0; i < messages.length; i++) {
    const msg = messages[i];
    const age = now - (msg.timestamp ?? now);
    const isRecent = age < rules.keepRecentMs;
    const isLastN = i >= messages.length - rules.keepLastMessages;
    const isProtected = rules.alwaysKeepTypes.includes(msg.type ?? "");

    if (isRecent || isLastN || isProtected) {
      kept.push(msg);
    } else if (
      msg.role === "assistant" &&
      msg.type === "tool_result" &&
      age > rules.pruneToolResultsAfterMs
    ) {
      pruned.push(msg);
    } else {
      kept.push(msg);
    }
  }

  return { kept, pruned };
}

// ============================================================================
// Proactive Context Management
// ============================================================================

/**
 * Check if context management is needed
 */
export function shouldManageContext(
  budget: TokenBudget,
  iterationCount: number,
  config: ContextConfig
): boolean {
  if (!config.proactiveManagement) return false;

  const usage = getBudgetUsage(budget);

  // Trigger at threshold
  if (usage > config.contextThreshold) return true;

  // Trigger at iteration interval
  if (iterationCount > 0 && iterationCount % config.summarizeAfterIterations === 0) {
    return true;
  }

  return false;
}

/**
 * Manage context proactively
 */
export async function manageContext(
  messages: TaggedMessage[],
  budget: TokenBudget,
  workingMemory: WorkingMemory,
  config: ContextConfig,
  llmCall?: LLMCaller
): Promise<{
  messages: TaggedMessage[];
  budget: TokenBudget;
  summarized?: string;
}> {
  // Apply pruning rules
  const { kept, pruned } = applyPruneRules(messages);

  let summarized: string | undefined;

  // Summarize pruned content if configured and LLM available
  if (pruned.length > 0 && DEFAULT_PRUNE_RULES.summarizeBeforePrune && llmCall) {
    const toolResults = pruned
      .filter((m) => m.type === "tool_result")
      .map((m) => ({
        tool: "tool",
        result: typeof m.content === "string" ? m.content : JSON.stringify(m.content),
      }));

    if (toolResults.length > 0) {
      summarized = await summarizeToolResults(toolResults, llmCall);

      // Store summary in working memory
      workingMemory.store(`summary_${Date.now()}`, {
        summary: summarized,
        timestamp: Date.now(),
      });
    }
  }

  // Recalculate budget
  const newUsed = estimateMessageTokens(kept);
  const newBudget: TokenBudget = {
    ...budget,
    used: newUsed,
  };

  // Add summary as system message if significant content was pruned
  if (summarized && pruned.length > 2) {
    kept.push({
      role: "system",
      content: `## Previous Work Summary\n${summarized}`,
      timestamp: Date.now(),
      type: "summary",
    });
  }

  return {
    messages: kept,
    budget: newBudget,
    summarized,
  };
}

// ============================================================================
// Context Injection
// ============================================================================

/**
 * Build context from working memory for a new subtask
 */
export function buildWorkingMemoryContext(
  workingMemory: WorkingMemory,
  dependencyIds: string[]
): string {
  if (dependencyIds.length === 0) return "";

  const context = workingMemory.retrieve(dependencyIds);
  if (!context) return "";

  return `## Context from Previous Work\n${context}`;
}

/**
 * Search working memory for relevant context
 */
export function searchRelevantContext(
  workingMemory: WorkingMemory,
  query: string,
  limit = 3
): string {
  const entries = workingMemory.search(query, limit);
  if (entries.length === 0) return "";

  const context = entries
    .map((e) => `### ${e.id}\n${e.summary}`)
    .join("\n\n");

  return `## Related Context\n${context}`;
}
