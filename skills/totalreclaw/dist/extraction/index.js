"use strict";
/**
 * TotalReclaw Skill - Extraction Module
 *
 * Fact extraction, deduplication, and entity/relation extraction
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateExtractionResponse = exports.generateEntityId = exports.formatExistingMemories = exports.formatConversationHistory = exports.DEDUP_JUDGE_SCHEMA = exports.EXTRACTION_RESPONSE_SCHEMA = exports.EXTRACTION_PROMPTS = exports.ENTITY_EXTRACTION_PROMPT = exports.CONTRADICTION_DETECTION_PROMPT = exports.DEDUP_JUDGE_PROMPT = exports.EXPLICIT_COMMAND_PROMPT = exports.POST_TURN_PROMPT = exports.PRE_COMPACTION_PROMPT = exports.DEFAULT_DEDUP_CONFIG = exports.mergeFacts = exports.areFactsSimilar = exports.createDeduplicator = exports.FactDeduplicator = exports.DEFAULT_EXTRACTOR_CONFIG = exports.parseExplicitMemoryCommand = exports.isExplicitMemoryCommand = exports.extractFactsFromText = exports.createFactExtractor = exports.FactExtractor = void 0;
// Main extractor class
var extractor_1 = require("./extractor");
Object.defineProperty(exports, "FactExtractor", { enumerable: true, get: function () { return extractor_1.FactExtractor; } });
Object.defineProperty(exports, "createFactExtractor", { enumerable: true, get: function () { return extractor_1.createFactExtractor; } });
Object.defineProperty(exports, "extractFactsFromText", { enumerable: true, get: function () { return extractor_1.extractFactsFromText; } });
Object.defineProperty(exports, "isExplicitMemoryCommand", { enumerable: true, get: function () { return extractor_1.isExplicitMemoryCommand; } });
Object.defineProperty(exports, "parseExplicitMemoryCommand", { enumerable: true, get: function () { return extractor_1.parseExplicitMemoryCommand; } });
Object.defineProperty(exports, "DEFAULT_EXTRACTOR_CONFIG", { enumerable: true, get: function () { return extractor_1.DEFAULT_EXTRACTOR_CONFIG; } });
// Deduplication
var dedup_1 = require("./dedup");
Object.defineProperty(exports, "FactDeduplicator", { enumerable: true, get: function () { return dedup_1.FactDeduplicator; } });
Object.defineProperty(exports, "createDeduplicator", { enumerable: true, get: function () { return dedup_1.createDeduplicator; } });
Object.defineProperty(exports, "areFactsSimilar", { enumerable: true, get: function () { return dedup_1.areFactsSimilar; } });
Object.defineProperty(exports, "mergeFacts", { enumerable: true, get: function () { return dedup_1.mergeFacts; } });
Object.defineProperty(exports, "DEFAULT_DEDUP_CONFIG", { enumerable: true, get: function () { return dedup_1.DEFAULT_DEDUP_CONFIG; } });
// Prompts
var prompts_1 = require("./prompts");
Object.defineProperty(exports, "PRE_COMPACTION_PROMPT", { enumerable: true, get: function () { return prompts_1.PRE_COMPACTION_PROMPT; } });
Object.defineProperty(exports, "POST_TURN_PROMPT", { enumerable: true, get: function () { return prompts_1.POST_TURN_PROMPT; } });
Object.defineProperty(exports, "EXPLICIT_COMMAND_PROMPT", { enumerable: true, get: function () { return prompts_1.EXPLICIT_COMMAND_PROMPT; } });
Object.defineProperty(exports, "DEDUP_JUDGE_PROMPT", { enumerable: true, get: function () { return prompts_1.DEDUP_JUDGE_PROMPT; } });
Object.defineProperty(exports, "CONTRADICTION_DETECTION_PROMPT", { enumerable: true, get: function () { return prompts_1.CONTRADICTION_DETECTION_PROMPT; } });
Object.defineProperty(exports, "ENTITY_EXTRACTION_PROMPT", { enumerable: true, get: function () { return prompts_1.ENTITY_EXTRACTION_PROMPT; } });
Object.defineProperty(exports, "EXTRACTION_PROMPTS", { enumerable: true, get: function () { return prompts_1.EXTRACTION_PROMPTS; } });
Object.defineProperty(exports, "EXTRACTION_RESPONSE_SCHEMA", { enumerable: true, get: function () { return prompts_1.EXTRACTION_RESPONSE_SCHEMA; } });
Object.defineProperty(exports, "DEDUP_JUDGE_SCHEMA", { enumerable: true, get: function () { return prompts_1.DEDUP_JUDGE_SCHEMA; } });
Object.defineProperty(exports, "formatConversationHistory", { enumerable: true, get: function () { return prompts_1.formatConversationHistory; } });
Object.defineProperty(exports, "formatExistingMemories", { enumerable: true, get: function () { return prompts_1.formatExistingMemories; } });
Object.defineProperty(exports, "generateEntityId", { enumerable: true, get: function () { return prompts_1.generateEntityId; } });
Object.defineProperty(exports, "validateExtractionResponse", { enumerable: true, get: function () { return prompts_1.validateExtractionResponse; } });
//# sourceMappingURL=index.js.map