"use strict";
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
Object.defineProperty(exports, "__esModule", { value: true });
exports.preCompaction = exports.agentEnd = exports.formatMemoriesForContext = exports.beforeAgentStart = void 0;
// Before Agent Start Hook
var before_agent_start_1 = require("./before-agent-start");
Object.defineProperty(exports, "beforeAgentStart", { enumerable: true, get: function () { return before_agent_start_1.beforeAgentStart; } });
Object.defineProperty(exports, "formatMemoriesForContext", { enumerable: true, get: function () { return before_agent_start_1.formatMemoriesForContext; } });
// Agent End Hook
var agent_end_1 = require("./agent-end");
Object.defineProperty(exports, "agentEnd", { enumerable: true, get: function () { return agent_end_1.agentEnd; } });
// Pre-Compaction Hook
var pre_compaction_1 = require("./pre-compaction");
Object.defineProperty(exports, "preCompaction", { enumerable: true, get: function () { return pre_compaction_1.preCompaction; } });
//# sourceMappingURL=index.js.map