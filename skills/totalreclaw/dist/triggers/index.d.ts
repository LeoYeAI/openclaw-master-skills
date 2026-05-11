/**
 * TotalReclaw Skill - Lifecycle Hooks (Triggers)
 *
 * This module exports the three lifecycle hooks for TotalReclaw integration:
 *
 * 1. **beforeAgentStart** - Runs before agent processes message
 *    - Retrieves relevant memories
 *    - Reranks with cross-encoder
 *    - Formats for context injection
 *    - Target: <100ms
 *
 * 2. **agentEnd** - Runs after agent completes turn
 *    - Checks turn counter (every N turns)
 *    - Extracts facts from recent conversation
 *    - Deduplicates against existing
 *    - Stores high-importance facts
 *    - Async - doesn't block user
 *
 * 3. **preCompaction** - Runs before context compaction
 *    - Full extraction of last 20 turns
 *    - Comprehensive deduplication
 *    - Graph consolidation
 *    - Batch upload to server
 */
export { beforeAgentStart, formatMemoriesForContext, type BeforeAgentStartOptions, } from './before-agent-start';
export { agentEnd, type AgentEndOptions, } from './agent-end';
export { preCompaction, type PreCompactionOptions, } from './pre-compaction';
//# sourceMappingURL=index.d.ts.map