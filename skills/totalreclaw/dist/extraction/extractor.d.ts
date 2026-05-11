/**
 * TotalReclaw Skill - Fact Extractor
 *
 * Main extraction module that:
 * 1. Extracts facts from conversation context
 * 2. Deduplicates against existing memories
 * 3. Scores importance
 * 4. Extracts entities and relations
 */
import type { ExtractedFact, ExtractionResult, OpenClawContext, Entity, Relation } from '../types';
import { FactDeduplicator, createDeduplicator, type ExistingFact, type LLMClient, type VectorStoreClient, type DedupConfig } from './dedup';
/**
 * Extraction trigger type
 */
export type ExtractionTrigger = 'pre_compaction' | 'post_turn' | 'explicit';
/**
 * Configuration for the fact extractor
 */
export interface FactExtractorConfig {
    /** Model to use for extraction (e.g., "claude-3-5-haiku") */
    extractionModel?: string;
    /** Temperature for extraction */
    extractionTemperature?: number;
    /** Minimum importance to include in results */
    minImportance?: number;
    /** Whether to auto-deduplicate */
    autoDeduplicate?: boolean;
    /** Number of turns to include in post-turn extraction */
    postTurnWindow?: number;
    /** Number of turns to include in pre-compaction extraction */
    preCompactionWindow?: number;
    /** Deduplication configuration */
    dedupConfig?: Partial<DedupConfig>;
}
/**
 * Default extraction configuration
 */
export declare const DEFAULT_EXTRACTOR_CONFIG: Required<Omit<FactExtractorConfig, 'dedupConfig'>> & {
    dedupConfig: Partial<DedupConfig>;
};
/**
 * Main fact extraction class
 */
export declare class FactExtractor {
    private config;
    private llmClient;
    private vectorStore;
    private deduplicator;
    constructor(llmClient: LLMClient, vectorStore?: VectorStoreClient, config?: Partial<FactExtractorConfig>);
    /**
     * Extract facts from OpenClaw context
     */
    extractFacts(context: OpenClawContext, trigger?: ExtractionTrigger): Promise<ExtractionResult>;
    /**
     * Deduplicate extracted facts against existing memories
     */
    deduplicateAgainstExisting(facts: ExtractedFact[], existingFacts: ExistingFact[]): Promise<ExtractedFact[]>;
    /**
     * Score importance of a fact (1-10 scale)
     * Can be used to re-score or validate LLM scores
     */
    scoreImportance(fact: ExtractedFact): number;
    /**
     * Extract entities from text (standalone entity extraction)
     */
    extractEntities(text: string): Promise<Entity[]>;
    /**
     * Extract relations from a fact
     */
    extractRelations(fact: ExtractedFact): Promise<Relation[]>;
    /**
     * Select the appropriate prompt based on trigger type
     */
    private selectPrompt;
    /**
     * Build pre-compaction extraction prompt
     */
    private buildPreCompactionPrompt;
    /**
     * Build post-turn extraction prompt
     */
    private buildPostTurnPrompt;
    /**
     * Build explicit command extraction prompt
     */
    private buildExplicitPrompt;
    /**
     * Parse and validate LLM extraction response
     */
    private parseExtractionResponse;
    /**
     * Validate a single extracted fact
     */
    private validateFact;
    /**
     * Post-process a fact (normalize entities, etc.)
     */
    private postProcessFact;
}
/**
 * Create a fact extractor with default configuration
 */
export declare function createFactExtractor(llmClient: LLMClient, vectorStore?: VectorStoreClient, config?: Partial<FactExtractorConfig>): FactExtractor;
/**
 * Quick extraction function for simple use cases
 */
export declare function extractFactsFromText(text: string, llmClient: LLMClient, options?: {
    type?: ExtractedFact['type'];
    importance?: number;
}): Promise<ExtractedFact[]>;
/**
 * Detect if a message is an explicit memory command
 */
export declare function isExplicitMemoryCommand(message: string): boolean;
/**
 * Parse an explicit memory command to extract the core content
 */
export declare function parseExplicitMemoryCommand(message: string): {
    isMemoryCommand: boolean;
    commandType: 'remember' | 'forget' | 'update';
    content: string;
};
export { FactDeduplicator, createDeduplicator };
export type { ExistingFact, LLMClient, VectorStoreClient, DedupConfig };
//# sourceMappingURL=extractor.d.ts.map