/**
 * Chat summary paragraph injection — from src/agents/pi-embedded-runner/compact.ts
 *
 * This snippet shows how the conversation summary instruction is injected
 * into the upstream compaction LLM call via customInstructions.
 */

// Inject chat summary paragraph instruction before the structured sections.
const chatSummaryInstruction =
  `Before the ## Goal section, add a ## Conversation Summary section with a short paragraph (3-6 sentences) ` +
  `that describes the overall topic(s) of the conversation, the flow of discussion, key turns and transitions, ` +
  `and how the conversation progressed. This gives a human-readable narrative overview before the structured details. ` +
  `Write it in past tense as a natural summary of what was discussed.`;
const effectiveInstructions = params.customInstructions
  ? `${chatSummaryInstruction}\n\n${params.customInstructions}`
  : chatSummaryInstruction;
const result = await compactWithSafetyTimeout(() =>
  session.compact(effectiveInstructions),
);
