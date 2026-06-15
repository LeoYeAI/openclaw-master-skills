/**
 * Context Summarization
 * 
 * Manages context window by summarizing old content when
 * the conversation history grows too long.
 */

import type { LLMCaller } from "../types.js";

// ============================================================================
// Types
// ============================================================================

export interface Message {
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  toolName?: string;
  toolResult?: unknown;
  timestamp?: number;
}

export interface SummarizerConfig {
  /** Enable automatic summarization */
  enabled: boolean;
  /** Target token count after summarization */
  targetTokens: number;
  /** Trigger summarization when exceeding this */
  thresholdTokens: number;
  /** Minimum messages to keep unsummarized */
  keepRecentMessages: number;
  /** Include tool results in summary */
  summarizeToolResults: boolean;
}

export interface SummarizationResult {
  summarized: boolean;
  summary?: string;
  removedMessages: number;
  originalTokens: number;
  finalTokens: number;
  savedTokens: number;
}

export interface ContextState {
  messages: Message[];
  summaries: ContextSummary[];
  totalTokensEstimate: number;
}

export interface ContextSummary {
  id: string;
  createdAt: number;
  messageRange: { from: number; to: number };
  summary: string;
  keyPoints: string[];
  tokensSaved: number;
}

// ============================================================================
// Token Estimation
// ============================================================================

/**
 * Rough token estimation (4 chars ≈ 1 token)
 */
export function estimateTokens(text: string): number {
  return Math.ceil(text.length / 4);
}

export function estimateMessageTokens(message: Message): number {
  let tokens = estimateTokens(message.content);
  tokens += 4; // Role overhead
  if (message.toolName) tokens += estimateTokens(message.toolName) + 2;
  if (message.toolResult) tokens += estimateTokens(JSON.stringify(message.toolResult));
  return tokens;
}

export function estimateTotalTokens(messages: Message[]): number {
  return messages.reduce((sum, m) => sum + estimateMessageTokens(m), 0);
}

// ============================================================================
// Context Summarizer
// ============================================================================

const DEFAULT_CONFIG: SummarizerConfig = {
  enabled: true,
  targetTokens: 50000,
  thresholdTokens: 80000,
  keepRecentMessages: 10,
  summarizeToolResults: true,
};

export class ContextSummarizer {
  private config: SummarizerConfig;
  private llmCaller?: LLMCaller;
  private summaries: ContextSummary[] = [];

  constructor(config: Partial<SummarizerConfig> = {}, llmCaller?: LLMCaller) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.llmCaller = llmCaller;
  }

  /**
   * Check if summarization is needed
   */
  needsSummarization(messages: Message[]): boolean {
    if (!this.config.enabled) return false;
    const totalTokens = estimateTotalTokens(messages);
    return totalTokens > this.config.thresholdTokens;
  }

  /**
   * Summarize older messages to reduce context size
   */
  async summarize(messages: Message[]): Promise<SummarizationResult> {
    const originalTokens = estimateTotalTokens(messages);
    
    if (!this.needsSummarization(messages)) {
      return {
        summarized: false,
        removedMessages: 0,
        originalTokens,
        finalTokens: originalTokens,
        savedTokens: 0,
      };
    }

    // Determine how many messages to summarize
    const keepCount = Math.max(this.config.keepRecentMessages, 3);
    const recentMessages = messages.slice(-keepCount);
    const olderMessages = messages.slice(0, -keepCount);

    if (olderMessages.length < 3) {
      // Not enough to summarize meaningfully
      return {
        summarized: false,
        removedMessages: 0,
        originalTokens,
        finalTokens: originalTokens,
        savedTokens: 0,
      };
    }

    // Generate summary
    const summary = await this.generateSummary(olderMessages);
    
    // Create summary record
    const summaryRecord: ContextSummary = {
      id: `sum_${Date.now()}`,
      createdAt: Date.now(),
      messageRange: { from: 0, to: olderMessages.length - 1 },
      summary: summary.text,
      keyPoints: summary.keyPoints,
      tokensSaved: estimateTotalTokens(olderMessages) - estimateTokens(summary.text),
    };
    
    this.summaries.push(summaryRecord);

    const finalTokens = estimateTokens(summary.text) + estimateTotalTokens(recentMessages);

    return {
      summarized: true,
      summary: summary.text,
      removedMessages: olderMessages.length,
      originalTokens,
      finalTokens,
      savedTokens: originalTokens - finalTokens,
    };
  }

  /**
   * Get summary to inject as context
   */
  getSummaryContext(): string {
    if (this.summaries.length === 0) return "";

    const latest = this.summaries[this.summaries.length - 1];
    return `
## Previous Conversation Summary

${latest.summary}

### Key Points
${latest.keyPoints.map(p => `- ${p}`).join("\n")}

_This summarizes ${latest.messageRange.to - latest.messageRange.from + 1} earlier messages._
`.trim();
  }

  /**
   * Condense tool results to save tokens
   */
  condenseToolResult(result: unknown, maxTokens: number = 500): string {
    const str = typeof result === "string" ? result : JSON.stringify(result, null, 2);
    const tokens = estimateTokens(str);
    
    if (tokens <= maxTokens) return str;

    // Truncate intelligently
    const lines = str.split("\n");
    let condensed = "";
    let currentTokens = 0;
    
    for (const line of lines) {
      const lineTokens = estimateTokens(line);
      if (currentTokens + lineTokens > maxTokens - 50) {
        condensed += "\n... [truncated] ...";
        break;
      }
      condensed += (condensed ? "\n" : "") + line;
      currentTokens += lineTokens;
    }

    return condensed;
  }

  /**
   * Build optimized message array with summarization
   */
  async optimizeMessages(messages: Message[]): Promise<{
    messages: Message[];
    summaryInjected: boolean;
  }> {
    if (!this.needsSummarization(messages)) {
      return { messages, summaryInjected: false };
    }

    const result = await this.summarize(messages);
    
    if (!result.summarized || !result.summary) {
      return { messages, summaryInjected: false };
    }

    // Create new message array with summary + recent messages
    const keepCount = this.config.keepRecentMessages;
    const recentMessages = messages.slice(-keepCount);
    
    const summaryMessage: Message = {
      role: "system",
      content: `[Context Summary]\n${result.summary}`,
      timestamp: Date.now(),
    };

    return {
      messages: [summaryMessage, ...recentMessages],
      summaryInjected: true,
    };
  }

  // ──────────────────────────────────────────────────────────────────────────
  // Private Methods
  // ──────────────────────────────────────────────────────────────────────────

  private async generateSummary(messages: Message[]): Promise<{
    text: string;
    keyPoints: string[];
  }> {
    if (this.llmCaller) {
      return this.llmGenerateSummary(messages);
    }
    return this.heuristicSummary(messages);
  }

  private async llmGenerateSummary(messages: Message[]): Promise<{
    text: string;
    keyPoints: string[];
  }> {
    const conversationText = messages.map(m => {
      let content = `[${m.role}]: ${m.content.slice(0, 500)}`;
      if (m.toolName) content += ` (tool: ${m.toolName})`;
      return content;
    }).join("\n\n");

    const prompt = `Summarize this conversation concisely, preserving key decisions, results, and context needed for continuation.

Conversation:
${conversationText.slice(0, 8000)}

Respond in JSON:
{
  "summary": "2-3 paragraph summary",
  "keyPoints": ["point 1", "point 2", ...]
}`;

    try {
      const response = await this.llmCaller!({
        messages: [
          { role: "system", content: "You summarize conversations. Output valid JSON." },
          { role: "user", content: prompt },
        ],
        maxTokens: 800,
      });

      const parsed = JSON.parse(response.content);
      return {
        text: parsed.summary || "Conversation summary unavailable.",
        keyPoints: parsed.keyPoints || [],
      };
    } catch {
      return this.heuristicSummary(messages);
    }
  }

  private heuristicSummary(messages: Message[]): {
    text: string;
    keyPoints: string[];
  } {
    // Extract key information heuristically
    const userMessages = messages.filter(m => m.role === "user");
    const toolCalls = messages.filter(m => m.role === "tool" || m.toolName);
    const decisions = messages.filter(m => 
      m.content.toLowerCase().includes("decided") ||
      m.content.toLowerCase().includes("will ") ||
      m.content.toLowerCase().includes("let's ")
    );

    const keyPoints: string[] = [];
    
    // First user message often contains the goal
    if (userMessages[0]) {
      keyPoints.push(`Initial request: ${userMessages[0].content.slice(0, 100)}...`);
    }

    // Note tool usage
    if (toolCalls.length > 0) {
      const toolNames = [...new Set(toolCalls.map(t => t.toolName).filter(Boolean))];
      keyPoints.push(`Tools used: ${toolNames.join(", ")}`);
    }

    // Extract decisions
    decisions.slice(0, 3).forEach(d => {
      const snippet = d.content.slice(0, 80);
      keyPoints.push(snippet + (d.content.length > 80 ? "..." : ""));
    });

    const summary = `This conversation covered ${messages.length} exchanges. ` +
      `The user made ${userMessages.length} requests. ` +
      `${toolCalls.length} tool operations were performed. ` +
      `Key context has been preserved below.`;

    return { text: summary, keyPoints };
  }
}

// ============================================================================
// Factory
// ============================================================================

export function createContextSummarizer(
  config?: Partial<SummarizerConfig>,
  llmCaller?: LLMCaller
): ContextSummarizer {
  return new ContextSummarizer(config, llmCaller);
}
