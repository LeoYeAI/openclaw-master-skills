/**
 * TotalReclaw Skill - Extraction Module
 *
 * Fact extraction, deduplication, and entity/relation extraction
 */

// Main extractor class
export {
  FactExtractor,
  createFactExtractor,
  extractFactsFromText,
  isExplicitMemoryCommand,
  parseExplicitMemoryCommand,
  DEFAULT_EXTRACTOR_CONFIG
} from './extractor';

export type {
  ExtractionTrigger,
  FactExtractorConfig
} from './extractor';

// Deduplication
export {
  FactDeduplicator,
  createDeduplicator,
  areFactsSimilar,
  mergeFacts,
  DEFAULT_DEDUP_CONFIG
} from './dedup';

export type {
  DedupResult,
  ExistingFact,
  LLMClient,
  VectorStoreClient,
  DedupConfig
} from './dedup';

// Prompts
export {
  PRE_COMPACTION_PROMPT,
  POST_TURN_PROMPT,
  EXPLICIT_COMMAND_PROMPT,
  DEDUP_JUDGE_PROMPT,
  CONTRADICTION_DETECTION_PROMPT,
  ENTITY_EXTRACTION_PROMPT,
  EXTRACTION_PROMPTS,
  EXTRACTION_RESPONSE_SCHEMA,
  DEDUP_JUDGE_SCHEMA,
  formatConversationHistory,
  formatExistingMemories,
  generateEntityId,
  validateExtractionResponse
} from './prompts';
