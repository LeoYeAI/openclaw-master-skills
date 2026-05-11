/**
 * TotalReclaw Skill - Deduplication Logic
 *
 * Handles detection of duplicate facts using:
 * 1. Vector similarity for initial candidate retrieval
 * 2. LLM judge for final ADD/UPDATE/DELETE decision
 * 3. Contradiction handling for conflicting facts
 */
import type { ExtractedFact, Entity, Relation, ExtractionAction } from '../types';
/**
 * Result from deduplication check
 */
export interface DedupResult {
    /** The determined action */
    action: ExtractionAction;
    /** ID of existing fact if UPDATE or DELETE */
    existingFactId?: string;
    /** Confidence in the decision */
    confidence: number;
    /** Reasoning for the decision */
    reasoning: string;
}
/**
 * Existing fact from memory store
 */
export interface ExistingFact {
    id: string;
    factText: string;
    type: ExtractedFact['type'];
    importance: number;
    embedding?: number[];
    entities?: Entity[];
    relations?: Relation[];
}
/**
 * LLM client interface (to be implemented by consumer)
 */
export interface LLMClient {
    complete(prompt: {
        system: string;
        user: string;
    }): Promise<string>;
}
/**
 * Vector store client interface (to be implemented by consumer)
 */
export interface VectorStoreClient {
    /**
     * Find similar facts by embedding
     */
    findSimilar(embedding: number[], k: number): Promise<ExistingFact[]>;
    /**
     * Get embedding for text
     */
    getEmbedding(text: string): Promise<number[]>;
}
/**
 * Configuration for deduplication
 */
export interface DedupConfig {
    /** Similarity threshold for considering facts as duplicates (0-1) */
    similarityThreshold: number;
    /** Number of similar facts to retrieve for comparison */
    topK: number;
    /** Whether to use LLM judge for final decision */
    useLLMJudge: boolean;
    /** Minimum confidence to override default ADD decision */
    minConfidenceForOverride: number;
}
/**
 * Default deduplication configuration
 */
export declare const DEFAULT_DEDUP_CONFIG: DedupConfig;
/**
 * Fact deduplicator that uses vector similarity + LLM judge
 */
export declare class FactDeduplicator {
    private config;
    private llmClient;
    private vectorStore;
    constructor(config?: Partial<DedupConfig>, llmClient?: LLMClient, vectorStore?: VectorStoreClient);
    /**
     * Check if a fact should be ADD/UPDATE/DELETE/NOOP
     */
    checkDuplication(fact: ExtractedFact): Promise<DedupResult>;
    /**
     * Deduplicate multiple facts against existing memories
     */
    deduplicateFacts(facts: ExtractedFact[], existingFacts: ExistingFact[]): Promise<ExtractedFact[]>;
    /**
     * Find similar facts from a list of existing facts
     */
    private findSimilarFacts;
    /**
     * Use LLM to judge ADD vs UPDATE vs DELETE
     */
    private llmJudgeDedup;
    /**
     * Heuristic-based deduplication (no LLM)
     */
    private heuristicDedup;
    /**
     * Text-based deduplication when no vector store is available
     */
    private textBasedDedup;
    /**
     * Detect if two facts are likely contradictions
     */
    detectContradiction(factA: string, factB: string): Promise<{
        isContradiction: boolean;
        type: string;
        reasoning: string;
    }>;
    /**
     * Use LLM for contradiction detection
     */
    private llmContradictionDetection;
    /**
     * Calculate cosine similarity between two vectors
     */
    private calculateCosineSimilarity;
    /**
     * Calculate text similarity using Jaccard similarity on words
     */
    private textSimilarity;
    /**
     * Quick check if two facts are likely contradictions
     */
    private isLikelyContradiction;
    /**
     * Detailed contradiction detection
     */
    private isLikelyContradictionDetailed;
    /**
     * Format a fact for the LLM judge
     */
    private formatFactForJudge;
    /**
     * Validate and normalize action
     */
    private validateAction;
}
/**
 * Create a deduplicator with default configuration
 */
export declare function createDeduplicator(llmClient?: LLMClient, vectorStore?: VectorStoreClient, config?: Partial<DedupConfig>): FactDeduplicator;
/**
 * Quick check if two fact texts are semantically similar
 */
export declare function areFactsSimilar(factA: string, factB: string, vectorStore?: VectorStoreClient): Promise<boolean>;
/**
 * Merge two facts (for UPDATE operations)
 */
export declare function mergeFacts(existing: ExistingFact, update: ExtractedFact): ExtractedFact;
//# sourceMappingURL=dedup.d.ts.map