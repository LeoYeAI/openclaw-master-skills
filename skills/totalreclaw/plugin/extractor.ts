/**
 * TotalReclaw Plugin - Fact Extractor
 *
 * Uses LLM calls to extract atomic facts from conversation messages.
 * Matches the extraction prompts described in SKILL.md.
 */

import { chatCompletion, resolveLLMConfig } from './llm-client.js';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type ExtractionAction = 'ADD' | 'UPDATE' | 'DELETE' | 'NOOP';

export interface ExtractedFact {
  text: string;
  type: 'fact' | 'preference' | 'decision' | 'episodic' | 'goal' | 'context' | 'summary';
  importance: number; // 1-10
  action: ExtractionAction;
  existingFactId?: string;
}

interface ContentBlock {
  type?: string;
  text?: string;
  thinking?: string;
}

interface ConversationMessage {
  role?: string;
  content?: string | ContentBlock[];
  text?: string;
}

// ---------------------------------------------------------------------------
// Extraction Prompt
// ---------------------------------------------------------------------------

const EXTRACTION_SYSTEM_PROMPT = `You are a memory extraction engine. Analyze the conversation and extract valuable long-term memories.

Rules:
1. Each memory must be a single, self-contained piece of information
2. Focus on user-specific information that would be useful in future conversations
3. Skip generic knowledge, greetings, small talk, and ephemeral task coordination
4. Score importance 1-10 (6+ = worth storing)
5. Only extract memories with importance >= 6

Types:
- fact: Objective information about the user (name, location, job, relationships)
- preference: Likes, dislikes, or preferences ("prefers dark mode", "allergic to peanuts")
- decision: Choices WITH reasoning ("chose PostgreSQL because data is relational and needs ACID")
- episodic: Notable events or experiences ("deployed v1.0 to production on March 15")
- goal: Objectives, targets, or plans ("wants to launch public beta by end of Q1")
- context: Active project/task context ("working on TotalReclaw v1.2, staging on Base Sepolia")
- summary: Key outcome or conclusion from a discussion ("agreed to use phased rollout for migration")

Extraction guidance:
- For decisions: ALWAYS include the reasoning. "Chose X" is weak. "Chose X because Y" is strong.
- For context: Capture what the user is actively working on, including versions, environments, and status.
- For summaries: Only extract when a conversation reaches a clear conclusion or agreement.
- For facts: Prefer specific over vague. "Lives in Lisbon" beats "lives in Europe".
- Decisions and context should be importance >= 7 (they are high-value for future conversations).

Actions (compare against existing memories if provided):
- ADD: New memory, no conflict with existing
- UPDATE: Refines or corrects an existing memory (provide existingFactId)
- DELETE: Contradicts an existing memory -- the old one is now wrong (provide existingFactId)
- NOOP: Already captured or not worth storing

Return a JSON array (no markdown, no code fences):
[{"text": "...", "type": "...", "importance": N, "action": "ADD|UPDATE|DELETE|NOOP", "existingFactId": "..."}, ...]

If nothing is worth extracting, return: []`;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Extract text content from a conversation message (handles various formats).
 *
 * OpenClaw AgentMessage objects use content arrays:
 *   { role: "user", content: [{ type: "text", text: "..." }] }
 *   { role: "assistant", content: [{ type: "text", text: "..." }, { type: "toolCall", ... }] }
 *
 * We also handle the simpler { role, content: "string" } format.
 */
function messageToText(msg: unknown): { role: string; content: string } | null {
  if (!msg || typeof msg !== 'object') return null;

  const m = msg as ConversationMessage;
  const role = m.role ?? 'unknown';

  // Only keep user and assistant messages
  if (role !== 'user' && role !== 'assistant') return null;

  let textContent: string;

  if (typeof m.content === 'string') {
    // Simple string content
    textContent = m.content;
  } else if (Array.isArray(m.content)) {
    // OpenClaw AgentMessage format: array of content blocks
    // Extract text from { type: "text", text: "..." } blocks
    const textParts = (m.content as ContentBlock[])
      .filter((block) => block.type === 'text' && typeof block.text === 'string')
      .map((block) => block.text as string);
    textContent = textParts.join('\n');
  } else if (typeof m.text === 'string') {
    // Fallback: { text: "..." } field
    textContent = m.text;
  } else {
    return null;
  }

  if (textContent.length < 3) return null;

  return { role, content: textContent };
}

/**
 * Truncate messages to fit within a token budget (rough estimate: 4 chars per token).
 */
function truncateMessages(messages: Array<{ role: string; content: string }>, maxChars: number): string {
  const lines: string[] = [];
  let totalChars = 0;

  for (const msg of messages) {
    const line = `[${msg.role}]: ${msg.content}`;
    if (totalChars + line.length > maxChars) break;
    lines.push(line);
    totalChars += line.length;
  }

  return lines.join('\n\n');
}

/**
 * Parse the LLM response into structured facts.
 */
function parseFactsResponse(response: string): ExtractedFact[] {
  // Strip markdown code fences if present
  let cleaned = response.trim();
  if (cleaned.startsWith('```')) {
    cleaned = cleaned.replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '').trim();
  }

  try {
    const parsed = JSON.parse(cleaned);
    if (!Array.isArray(parsed)) return [];

    return parsed
      .filter(
        (f: unknown) =>
          f &&
          typeof f === 'object' &&
          typeof (f as ExtractedFact).text === 'string' &&
          (f as ExtractedFact).text.length >= 5,
      )
      .map((f: unknown) => {
        const fact = f as Record<string, unknown>;
        const validActions: ExtractionAction[] = ['ADD', 'UPDATE', 'DELETE', 'NOOP'];
        const action = validActions.includes(String(fact.action) as ExtractionAction)
          ? (String(fact.action) as ExtractionAction)
          : 'ADD'; // Default to ADD for backward compatibility
        return {
          text: String(fact.text).slice(0, 512),
          type: (['fact', 'preference', 'decision', 'episodic', 'goal', 'context', 'summary'].includes(String(fact.type))
            ? String(fact.type)
            : 'fact') as ExtractedFact['type'],
          importance: Math.max(1, Math.min(10, Number(fact.importance) || 5)),
          action,
          existingFactId: typeof fact.existingFactId === 'string' ? fact.existingFactId : undefined,
        };
      })
      .filter((f) => f.importance >= 6 || f.action === 'DELETE'); // DELETE actions pass regardless of importance
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// Main extraction function
// ---------------------------------------------------------------------------

/**
 * Extract facts from a list of conversation messages using LLM.
 *
 * @param rawMessages - The messages array from the hook event (unknown[])
 * @param mode - 'turn' for agent_end (recent only), 'full' for compaction/reset
 * @param existingMemories - Optional list of existing memories for dedup context
 * @returns Array of extracted facts, or empty array on failure.
 */
export async function extractFacts(
  rawMessages: unknown[],
  mode: 'turn' | 'full',
  existingMemories?: Array<{ id: string; text: string }>,
): Promise<ExtractedFact[]> {
  const config = resolveLLMConfig();
  if (!config) return []; // No LLM available

  // Parse messages
  const parsed = rawMessages
    .map(messageToText)
    .filter((m): m is { role: string; content: string } => m !== null);

  if (parsed.length === 0) return [];

  // For 'turn' mode, only look at last 6 messages (3 turns)
  // For 'full' mode, use all messages but truncate to fit token budget
  const relevantMessages = mode === 'turn' ? parsed.slice(-6) : parsed;

  // Truncate to ~3000 tokens worth of text
  const conversationText = truncateMessages(relevantMessages, 12_000);

  if (conversationText.length < 20) return [];

  // Build existing memories context if available
  let memoriesContext = '';
  if (existingMemories && existingMemories.length > 0) {
    const memoriesStr = existingMemories
      .map((m) => `[ID: ${m.id}] ${m.text}`)
      .join('\n');
    memoriesContext = `\n\nExisting memories (use these for dedup — classify as UPDATE/DELETE/NOOP if they conflict or overlap):\n${memoriesStr}`;
  }

  const userPrompt =
    mode === 'turn'
      ? `Extract important facts from these recent conversation turns:\n\n${conversationText}${memoriesContext}`
      : `Extract ALL valuable long-term memories from this conversation before it is lost:\n\n${conversationText}${memoriesContext}`;

  try {
    const response = await chatCompletion(config, [
      { role: 'system', content: EXTRACTION_SYSTEM_PROMPT },
      { role: 'user', content: userPrompt },
    ]);

    if (!response) return [];

    return parseFactsResponse(response);
  } catch {
    return []; // Fail silently -- hooks must never break the agent
  }
}
