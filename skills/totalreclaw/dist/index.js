"use strict";
/**
 * TotalReclaw Skill for OpenClaw
 *
 * Zero-knowledge encrypted memory for AI agents using MemOS-inspired
 * lifecycle hooks pattern.
 *
 * @example
 * ```typescript
 * import { TotalReclawSkill } from '@totalreclaw/skill';
 *
 * const skill = new TotalReclawSkill({
 *   serverUrl: 'http://127.0.0.1:8080',
 *   masterPassword: 'my-secure-password',
 * });
 *
 * await skill.init();
 * ```
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateConfig = exports.loadConfig = exports.CrossEncoderReranker = exports.preCompaction = exports.agentEnd = exports.formatMemoriesForContext = exports.beforeAgentStart = exports.EXTRACTION_PROMPTS = exports.FactExtractor = exports.exportTool = exports.forgetTool = exports.recallTool = exports.rememberTool = exports.TotalReclawSkill = void 0;
var totalreclaw_skill_1 = require("./totalreclaw-skill");
Object.defineProperty(exports, "TotalReclawSkill", { enumerable: true, get: function () { return totalreclaw_skill_1.TotalReclawSkill; } });
// Tool implementations
var remember_1 = require("./tools/remember");
Object.defineProperty(exports, "rememberTool", { enumerable: true, get: function () { return remember_1.rememberTool; } });
var recall_1 = require("./tools/recall");
Object.defineProperty(exports, "recallTool", { enumerable: true, get: function () { return recall_1.recallTool; } });
var forget_1 = require("./tools/forget");
Object.defineProperty(exports, "forgetTool", { enumerable: true, get: function () { return forget_1.forgetTool; } });
var export_1 = require("./tools/export");
Object.defineProperty(exports, "exportTool", { enumerable: true, get: function () { return export_1.exportTool; } });
// Extraction
var extractor_1 = require("./extraction/extractor");
Object.defineProperty(exports, "FactExtractor", { enumerable: true, get: function () { return extractor_1.FactExtractor; } });
var prompts_1 = require("./extraction/prompts");
Object.defineProperty(exports, "EXTRACTION_PROMPTS", { enumerable: true, get: function () { return prompts_1.EXTRACTION_PROMPTS; } });
// Triggers / Lifecycle Hooks
var before_agent_start_1 = require("./triggers/before-agent-start");
Object.defineProperty(exports, "beforeAgentStart", { enumerable: true, get: function () { return before_agent_start_1.beforeAgentStart; } });
Object.defineProperty(exports, "formatMemoriesForContext", { enumerable: true, get: function () { return before_agent_start_1.formatMemoriesForContext; } });
var agent_end_1 = require("./triggers/agent-end");
Object.defineProperty(exports, "agentEnd", { enumerable: true, get: function () { return agent_end_1.agentEnd; } });
var pre_compaction_1 = require("./triggers/pre-compaction");
Object.defineProperty(exports, "preCompaction", { enumerable: true, get: function () { return pre_compaction_1.preCompaction; } });
// Reranking
var cross_encoder_1 = require("./reranker/cross-encoder");
Object.defineProperty(exports, "CrossEncoderReranker", { enumerable: true, get: function () { return cross_encoder_1.CrossEncoderReranker; } });
// Config
var config_1 = require("./config");
Object.defineProperty(exports, "loadConfig", { enumerable: true, get: function () { return config_1.loadConfig; } });
Object.defineProperty(exports, "validateConfig", { enumerable: true, get: function () { return config_1.validateConfig; } });
//# sourceMappingURL=index.js.map