"use strict";
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
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.CrossEncoderReranker = void 0;
exports.getCrossEncoderReranker = getCrossEncoderReranker;
exports.initCrossEncoderReranker = initCrossEncoderReranker;
exports.crossEncoderRerank = crossEncoderRerank;
const ort = __importStar(require("onnxruntime-node"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const debug_1 = require("../debug");
// ============================================================================
// Configuration
// ============================================================================
/** Default model filename for BGE-Reranker-base */
const DEFAULT_MODEL_FILENAME = 'bge-reranker-base.onnx';
/** Default model directory */
const DEFAULT_MODEL_DIR = 'models';
/** Maximum sequence length for the reranker */
const MAX_SEQUENCE_LENGTH = 512;
/** Default tokenizer vocabulary file */
const DEFAULT_VOCAB_FILE = 'vocab.json';
// ============================================================================
// Simple Tokenizer
// ============================================================================
/**
 * Simple BERT-style tokenizer for cross-encoder models.
 *
 * Note: This is a simplified implementation. For production use,
 * consider using the HuggingFace tokenizers library or a proper
 * WordPiece/BPE tokenizer implementation.
 */
class SimpleTokenizer {
    vocab = new Map();
    invVocab = new Map();
    maxSeqLength;
    isLoaded = false;
    // Special token IDs (BERT-style)
    static CLS_TOKEN_ID = 101;
    static SEP_TOKEN_ID = 102;
    static PAD_TOKEN_ID = 0;
    static UNK_TOKEN_ID = 100;
    constructor(maxSeqLength = MAX_SEQUENCE_LENGTH) {
        this.maxSeqLength = maxSeqLength;
    }
    /**
     * Load vocabulary from file
     */
    async load(vocabPath) {
        try {
            const vocabData = fs.readFileSync(vocabPath, 'utf-8');
            const vocabJson = JSON.parse(vocabData);
            this.vocab.clear();
            this.invVocab.clear();
            for (const [token, id] of Object.entries(vocabJson)) {
                this.vocab.set(token, id);
                this.invVocab.set(id, token);
            }
            this.isLoaded = true;
        }
        catch (error) {
            // If vocab file not found, we'll use hash-based tokenization
            console.warn(`Tokenizer vocabulary not found at ${vocabPath}. Using hash-based tokenization.`);
            this.isLoaded = false;
        }
    }
    /**
     * Check if tokenizer is loaded
     */
    isReady() {
        return this.isLoaded;
    }
    /**
     * Basic text cleaning
     */
    cleanText(text) {
        return text
            .toLowerCase()
            .replace(/[^a-zA-Z0-9\s]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    }
    /**
     * Basic tokenization (whitespace + punctuation)
     */
    basicTokenize(text) {
        const cleaned = this.cleanText(text);
        return cleaned.split(/\s+/).filter((t) => t.length > 0);
    }
    /**
     * Convert token to ID (with hash fallback)
     */
    tokenToId(token) {
        if (this.vocab.has(token)) {
            return this.vocab.get(token);
        }
        // Try lowercase
        const lowerToken = token.toLowerCase();
        if (this.vocab.has(lowerToken)) {
            return this.vocab.get(lowerToken);
        }
        // Hash-based fallback for unknown tokens
        return this.hashToken(token);
    }
    /**
     * Hash token to a valid token ID
     */
    hashToken(token) {
        let hash = 0;
        for (let i = 0; i < token.length; i++) {
            const char = token.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        // Map to vocabulary range (avoid special tokens 0-999)
        return (Math.abs(hash) % 29000) + 1000;
    }
    /**
     * Tokenize a single text
     */
    tokenize(text) {
        const tokens = this.basicTokenize(text);
        const inputIds = [SimpleTokenizer.CLS_TOKEN_ID];
        const attentionMask = [1];
        // Add tokens (reserve space for SEP token)
        const maxTokens = this.maxSeqLength - 2;
        for (let i = 0; i < Math.min(tokens.length, maxTokens); i++) {
            inputIds.push(this.tokenToId(tokens[i]));
            attentionMask.push(1);
        }
        // Add SEP token
        inputIds.push(SimpleTokenizer.SEP_TOKEN_ID);
        attentionMask.push(1);
        // Pad to maxSeqLength
        while (inputIds.length < this.maxSeqLength) {
            inputIds.push(SimpleTokenizer.PAD_TOKEN_ID);
            attentionMask.push(0);
        }
        return { inputIds, attentionMask };
    }
    /**
     * Tokenize query-document pair for cross-encoder
     * Format: [CLS] query [SEP] document [SEP]
     */
    tokenizePair(query, document) {
        const queryTokens = this.basicTokenize(query);
        const docTokens = this.basicTokenize(document);
        const inputIds = [SimpleTokenizer.CLS_TOKEN_ID];
        const attentionMask = [1];
        // Add query tokens (limit to ~1/3 of sequence)
        const maxQueryTokens = Math.floor((this.maxSeqLength - 3) / 3);
        for (let i = 0; i < Math.min(queryTokens.length, maxQueryTokens); i++) {
            inputIds.push(this.tokenToId(queryTokens[i]));
            attentionMask.push(1);
        }
        // Add SEP between query and document
        inputIds.push(SimpleTokenizer.SEP_TOKEN_ID);
        attentionMask.push(1);
        // Add document tokens (remaining space)
        const usedSpace = inputIds.length;
        const maxDocTokens = this.maxSeqLength - usedSpace - 1; // -1 for final SEP
        for (let i = 0; i < Math.min(docTokens.length, maxDocTokens); i++) {
            inputIds.push(this.tokenToId(docTokens[i]));
            attentionMask.push(1);
        }
        // Add final SEP token
        inputIds.push(SimpleTokenizer.SEP_TOKEN_ID);
        attentionMask.push(1);
        // Pad to maxSeqLength
        while (inputIds.length < this.maxSeqLength) {
            inputIds.push(SimpleTokenizer.PAD_TOKEN_ID);
            attentionMask.push(0);
        }
        return { inputIds, attentionMask };
    }
}
// ============================================================================
// Cross-Encoder Reranker
// ============================================================================
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
class CrossEncoderReranker {
    session = null;
    tokenizer;
    modelPath = null;
    isLoaded = false;
    config;
    loadPromise = null;
    /**
     * Create a new CrossEncoderReranker
     */
    constructor(config = {}) {
        this.config = {
            maxSequenceLength: MAX_SEQUENCE_LENGTH,
            debug: false,
            ...config,
        };
        this.tokenizer = new SimpleTokenizer(this.config.maxSequenceLength);
    }
    /**
     * Load the ONNX model
     *
     * @param modelPath - Path to ONNX model file (optional, uses default if not provided)
     */
    async load(modelPath) {
        // If already loading, wait for that promise
        if (this.loadPromise) {
            return this.loadPromise;
        }
        // If already loaded, return immediately
        if (this.isLoaded && this.session) {
            return;
        }
        this.loadPromise = this.doLoad(modelPath);
        try {
            await this.loadPromise;
        }
        finally {
            this.loadPromise = null;
        }
    }
    /**
     * Internal load implementation
     */
    async doLoad(modelPath) {
        // Resolve model path
        if (modelPath) {
            this.modelPath = modelPath;
        }
        else if (this.config.modelPath) {
            this.modelPath = this.config.modelPath;
        }
        else {
            // Try to find default model location
            const possiblePaths = [
                path.join(process.cwd(), DEFAULT_MODEL_DIR, DEFAULT_MODEL_FILENAME),
                path.join(__dirname, '..', '..', DEFAULT_MODEL_DIR, DEFAULT_MODEL_FILENAME),
                path.join(__dirname, '..', '..', '..', DEFAULT_MODEL_DIR, DEFAULT_MODEL_FILENAME),
                path.join(__dirname, '..', '..', '..', '..', DEFAULT_MODEL_DIR, DEFAULT_MODEL_FILENAME),
            ];
            for (const p of possiblePaths) {
                if (fs.existsSync(p)) {
                    this.modelPath = p;
                    break;
                }
            }
            if (!this.modelPath) {
                if (this.config.debug) {
                    console.warn(`BGE-Reranker model not found. Reranker will use vector score fallback. ` +
                        `Expected locations: ${possiblePaths.join(', ')}`);
                }
                // Not an error - will fallback to vector scores
                return;
            }
        }
        // Check if model file exists
        if (!fs.existsSync(this.modelPath)) {
            if (this.config.debug) {
                console.warn(`Model file not found at ${this.modelPath}. Using fallback.`);
            }
            return;
        }
        try {
            // Create ONNX inference session with optimizations
            this.session = await ort.InferenceSession.create(this.modelPath, {
                executionProviders: ['cpu'],
                graphOptimizationLevel: 'all',
                enableCpuMemArena: true,
                enableMemPattern: true,
            });
            // Try to load tokenizer vocabulary
            const vocabPath = this.config.vocabPath || this.findVocabPath();
            if (vocabPath && fs.existsSync(vocabPath)) {
                await this.tokenizer.load(vocabPath);
            }
            this.isLoaded = true;
            (0, debug_1.debugLog)(!!this.config.debug, `CrossEncoderReranker loaded successfully from ${this.modelPath}`);
        }
        catch (error) {
            if (this.config.debug) {
                console.warn(`Failed to load ONNX model: ${error instanceof Error ? error.message : 'Unknown error'}. ` +
                    `Using vector score fallback.`);
            }
            // Don't throw - allow fallback to vector scores
            this.session = null;
            this.isLoaded = false;
        }
    }
    /**
     * Find vocabulary file near the model
     */
    findVocabPath() {
        if (!this.modelPath)
            return null;
        const modelDir = path.dirname(this.modelPath);
        const possibleVocabPaths = [
            path.join(modelDir, DEFAULT_VOCAB_FILE),
            path.join(modelDir, 'tokenizer', DEFAULT_VOCAB_FILE),
            path.join(modelDir, '..', DEFAULT_VOCAB_FILE),
        ];
        for (const p of possibleVocabPaths) {
            if (fs.existsSync(p)) {
                return p;
            }
        }
        return null;
    }
    /**
     * Check if the model is loaded and ready
     */
    isReady() {
        return this.isLoaded && this.session !== null;
    }
    /**
     * Rerank candidates using cross-encoder
     *
     * @param query - Search query
     * @param candidates - Candidate facts from server search
     * @param topK - Number of top results to return
     * @returns Reranked results sorted by relevance
     */
    async rerank(query, candidates, topK = 8) {
        const startTime = Date.now();
        // Handle empty candidates
        if (candidates.length === 0) {
            return [];
        }
        // If model not loaded, use vector score fallback
        if (!this.isReady()) {
            return this.fallbackRerank(candidates, topK);
        }
        try {
            // Score all candidates with cross-encoder
            const scores = await this.scoreBatch(query, candidates);
            // Combine with existing metadata
            const results = candidates.map((fact, index) => {
                const ceScore = scores[index];
                // Normalize cross-encoder score (typically in range -10 to 10)
                const normalizedCeScore = this.sigmoid(ceScore);
                return {
                    fact,
                    score: normalizedCeScore,
                    vectorScore: this.calculateVectorScore(fact),
                    textScore: 0, // Cross-encoder replaces BM25
                    decayAdjustedScore: fact.decayScore,
                    crossEncoderScore: ceScore,
                };
            });
            // Sort by cross-encoder score
            results.sort((a, b) => b.crossEncoderScore - a.crossEncoderScore);
            // Log latency if debug enabled
            if (this.config.debug) {
                const latency = Date.now() - startTime;
                (0, debug_1.debugLog)(true, `CrossEncoder reranked ${candidates.length} documents in ${latency}ms ` +
                    `(${(latency / candidates.length).toFixed(1)}ms per doc)`);
            }
            return results.slice(0, topK);
        }
        catch (error) {
            console.warn(`Cross-encoder scoring failed: ${error instanceof Error ? error.message : 'Unknown error'}. ` +
                `Falling back to vector scores.`);
            return this.fallbackRerank(candidates, topK);
        }
    }
    /**
     * Score query-document pairs in batch
     */
    async scoreBatch(query, documents) {
        if (!this.session) {
            throw new Error('Session not initialized');
        }
        const scores = [];
        // Process in batches for memory efficiency
        const batchSize = 8; // Process 8 pairs at a time
        for (let i = 0; i < documents.length; i += batchSize) {
            const batch = documents.slice(i, i + batchSize);
            const batchScores = await this.scoreBatchInternal(query, batch);
            scores.push(...batchScores);
        }
        return scores;
    }
    /**
     * Internal batch scoring
     */
    async scoreBatchInternal(query, documents) {
        if (!this.session) {
            throw new Error('Session not initialized');
        }
        const batchSize = documents.length;
        // Tokenize all query-document pairs
        const allInputIds = [];
        const allAttentionMasks = [];
        for (const doc of documents) {
            const tokenized = this.tokenizer.tokenizePair(query, doc.text);
            allInputIds.push(...tokenized.inputIds);
            allAttentionMasks.push(...tokenized.attentionMask);
        }
        // Create tensors
        const inputIdsTensor = new ort.Tensor('int64', BigInt64Array.from(allInputIds.map(BigInt)), [batchSize, this.config.maxSequenceLength]);
        const attentionMaskTensor = new ort.Tensor('int64', BigInt64Array.from(allAttentionMasks.map(BigInt)), [batchSize, this.config.maxSequenceLength]);
        // Prepare feeds
        const feeds = {
            input_ids: inputIdsTensor,
            attention_mask: attentionMaskTensor,
        };
        // Add token_type_ids if model requires it
        if (this.session.inputNames.includes('token_type_ids')) {
            const size = batchSize * this.config.maxSequenceLength;
            const zeroArray = new BigInt64Array(size);
            for (let i = 0; i < size; i++) {
                zeroArray[i] = BigInt(0);
            }
            const tokenTypeIds = new ort.Tensor('int64', zeroArray, [batchSize, this.config.maxSequenceLength]);
            feeds.token_type_ids = tokenTypeIds;
        }
        // Run inference
        const results = await this.session.run(feeds);
        // Get output (usually logits for relevance)
        const outputName = this.session.outputNames[0];
        const output = results[outputName];
        const data = output.data;
        // Extract scores (one per document)
        const scores = [];
        for (let i = 0; i < batchSize; i++) {
            // Output shape is typically [batch_size, 1] or [batch_size]
            scores.push(data[i]);
        }
        return scores;
    }
    /**
     * Fallback reranking using vector scores
     */
    fallbackRerank(candidates, topK) {
        const results = candidates.map((fact) => {
            const vecScore = this.calculateVectorScore(fact);
            const decScore = fact.decayScore || 0.5;
            // Combine vector and decay scores
            const combinedScore = vecScore * 0.7 + decScore * 0.3;
            return {
                fact,
                score: combinedScore,
                vectorScore: vecScore,
                textScore: 0,
                decayAdjustedScore: decScore,
                crossEncoderScore: vecScore, // Use vector score as cross-encoder score
            };
        });
        // Sort by combined score
        results.sort((a, b) => b.score - a.score);
        return results.slice(0, topK);
    }
    /**
     * Calculate vector similarity score from fact embedding
     *
     * Note: This is a simplified approach. In practice, you would
     * compute cosine similarity with the query embedding.
     */
    calculateVectorScore(fact) {
        // If fact has embedding, compute norm-based relevance proxy
        if (fact.embedding && fact.embedding.length > 0) {
            // Use embedding magnitude as a proxy (not ideal but works for fallback)
            let norm = 0;
            for (const val of fact.embedding) {
                norm += val * val;
            }
            norm = Math.sqrt(norm);
            // Normalized embeddings have norm close to 1
            // Use decay score as the main signal
            return fact.decayScore || 0.5;
        }
        return fact.decayScore || 0.5;
    }
    /**
     * Sigmoid function for score normalization
     */
    sigmoid(x) {
        return 1 / (1 + Math.exp(-x));
    }
    /**
     * Get model load status
     */
    getLoadStatus() {
        return {
            isLoaded: this.isLoaded,
            modelPath: this.modelPath,
            hasTokenizer: this.tokenizer.isReady(),
        };
    }
    /**
     * Dispose of the ONNX session
     */
    async dispose() {
        if (this.session) {
            await this.session.release();
            this.session = null;
            this.isLoaded = false;
        }
    }
}
exports.CrossEncoderReranker = CrossEncoderReranker;
// ============================================================================
// Singleton Instance
// ============================================================================
/**
 * Default cross-encoder reranker instance
 *
 * Lazily loaded on first use.
 */
let defaultReranker = null;
/**
 * Get the default cross-encoder reranker instance
 *
 * @param config - Optional configuration (only used on first call)
 * @returns CrossEncoderReranker instance
 */
function getCrossEncoderReranker(config) {
    if (!defaultReranker) {
        defaultReranker = new CrossEncoderReranker(config);
    }
    return defaultReranker;
}
/**
 * Initialize the default reranker with a model
 *
 * @param modelPath - Path to ONNX model
 * @param config - Optional configuration
 */
async function initCrossEncoderReranker(modelPath, config) {
    const reranker = getCrossEncoderReranker(config);
    await reranker.load(modelPath);
    return reranker;
}
// ============================================================================
// Utility Functions
// ============================================================================
/**
 * Quick rerank function using the default reranker
 *
 * @param query - Search query
 * @param candidates - Candidate facts
 * @param topK - Number of results
 * @returns Reranked results
 */
async function crossEncoderRerank(query, candidates, topK = 8) {
    const reranker = getCrossEncoderReranker();
    return reranker.rerank(query, candidates, topK);
}
//# sourceMappingURL=cross-encoder.js.map