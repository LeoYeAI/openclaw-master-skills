/**
 * Cross-Encoder Reranker for TotalReclaw Skill
 *
 * Uses BGE-Reranker-base ONNX model for high-quality semantic reranking
 * of candidate facts returned from server search.
 *
 * Features:
 * - ONNX runtime integration for efficient inference
 * - Model caching for reuse across multiple rerank calls
 * - Graceful fallback to vector scores when model unavailable
 * - Target latency: 30-50ms for 10 documents
 */
import type { Fact, RerankedResult } from '@totalreclaw/client';
/**
 * Configuration for the CrossEncoderReranker
 */
export interface CrossEncoderConfig {
    /** Path to ONNX model file (optional, uses default if not provided) */
    modelPath?: string;
    /** Path to tokenizer vocabulary file (optional) */
    vocabPath?: string;
    /** Maximum sequence length (default: 512) */
    maxSequenceLength?: number;
    /** Enable debug logging */
    debug?: boolean;
}
/**
 * Reranker result with additional cross-encoder score
 */
export interface CrossEncoderResult extends RerankedResult {
    /** Cross-encoder relevance score */
    crossEncoderScore: number;
}
/**
 * Cross-Encoder Reranker using ONNX Runtime
 *
 * Provides high-quality semantic reranking using a cross-encoder model
 * (BGE-Reranker-base) that jointly encodes query-document pairs for
 * accurate relevance scoring.
 *
 * @example
 * ```typescript
 * const reranker = new CrossEncoderReranker();
 * await reranker.load('/path/to/bge-reranker-base.onnx');
 *
 * const results = await reranker.rerank(
 *   'what is my favorite coffee?',
 *   candidates,
 *   8
 * );
 * ```
 */
export declare class CrossEncoderReranker {
    private session;
    private tokenizer;
    private modelPath;
    private isLoaded;
    private config;
    private loadPromise;
    /**
     * Create a new CrossEncoderReranker
     */
    constructor(config?: CrossEncoderConfig);
    /**
     * Load the ONNX model
     *
     * @param modelPath - Path to ONNX model file (optional, uses default if not provided)
     */
    load(modelPath?: string): Promise<void>;
    /**
     * Internal load implementation
     */
    private doLoad;
    /**
     * Find vocabulary file near the model
     */
    private findVocabPath;
    /**
     * Check if the model is loaded and ready
     */
    isReady(): boolean;
    /**
     * Rerank candidates using cross-encoder
     *
     * @param query - Search query
     * @param candidates - Candidate facts from server search
     * @param topK - Number of top results to return
     * @returns Reranked results sorted by relevance
     */
    rerank(query: string, candidates: Fact[], topK?: number): Promise<CrossEncoderResult[]>;
    /**
     * Score query-document pairs in batch
     */
    private scoreBatch;
    /**
     * Internal batch scoring
     */
    private scoreBatchInternal;
    /**
     * Fallback reranking using vector scores
     */
    private fallbackRerank;
    /**
     * Calculate vector similarity score from fact embedding
     *
     * Note: This is a simplified approach. In practice, you would
     * compute cosine similarity with the query embedding.
     */
    private calculateVectorScore;
    /**
     * Sigmoid function for score normalization
     */
    private sigmoid;
    /**
     * Get model load status
     */
    getLoadStatus(): {
        isLoaded: boolean;
        modelPath: string | null;
        hasTokenizer: boolean;
    };
    /**
     * Dispose of the ONNX session
     */
    dispose(): Promise<void>;
}
/**
 * Get the default cross-encoder reranker instance
 *
 * @param config - Optional configuration (only used on first call)
 * @returns CrossEncoderReranker instance
 */
export declare function getCrossEncoderReranker(config?: CrossEncoderConfig): CrossEncoderReranker;
/**
 * Initialize the default reranker with a model
 *
 * @param modelPath - Path to ONNX model
 * @param config - Optional configuration
 */
export declare function initCrossEncoderReranker(modelPath?: string, config?: CrossEncoderConfig): Promise<CrossEncoderReranker>;
/**
 * Quick rerank function using the default reranker
 *
 * @param query - Search query
 * @param candidates - Candidate facts
 * @param topK - Number of results
 * @returns Reranked results
 */
export declare function crossEncoderRerank(query: string, candidates: Fact[], topK?: number): Promise<CrossEncoderResult[]>;
//# sourceMappingURL=cross-encoder.d.ts.map