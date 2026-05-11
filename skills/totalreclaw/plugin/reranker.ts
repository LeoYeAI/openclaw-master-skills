/**
 * TotalReclaw Plugin - Client-Side Re-Ranker
 *
 * Replaces the naive `textScore` word-overlap scorer with a proper ranking
 * pipeline:
 *   1. Okapi BM25 — term frequency / inverse document frequency
 *   2. Cosine similarity — between query and fact embeddings
 *   3. Importance — normalized importance score (0-1)
 *   4. Recency — time-decay with 1-week half-life
 *   5. Weighted RRF (Reciprocal Rank Fusion) — combines all ranking lists
 *   6. MMR (Maximal Marginal Relevance) — promotes diversity in results
 *
 * All functions are pure TypeScript with zero external dependencies (except
 * porter-stemmer for morphological normalization). This module runs
 * CLIENT-SIDE after decrypting candidates from the server.
 */

import { stemmer } from 'porter-stemmer';

// ---------------------------------------------------------------------------
// Tokenization
// ---------------------------------------------------------------------------

/**
 * Tokenize a text string for BM25 scoring.
 *
 * Matches the tokenization rules used for blind indices in crypto.ts:
 *   1. Lowercase
 *   2. Remove punctuation (keep Unicode letters, numbers, whitespace)
 *   3. Split on whitespace
 *   4. Filter tokens shorter than 2 characters
 *
 * Optionally removes common English stop words (enabled by default) to
 * improve BM25 signal — stop words have low IDF and add noise.
 */
const STOP_WORDS = new Set([
  'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'do', 'for',
  'from', 'had', 'has', 'have', 'he', 'her', 'him', 'his', 'how', 'if',
  'in', 'into', 'is', 'it', 'its', 'me', 'my', 'no', 'not', 'of', 'on',
  'or', 'our', 'out', 'she', 'so', 'than', 'that', 'the', 'their', 'them',
  'then', 'there', 'these', 'they', 'this', 'to', 'up', 'us', 'was', 'we',
  'were', 'what', 'when', 'where', 'which', 'who', 'whom', 'why', 'will',
  'with', 'you', 'your',
]);

export function tokenize(text: string, removeStopWords: boolean = true): string[] {
  let tokens = text
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, ' ')
    .split(/\s+/)
    .filter((t) => t.length >= 2);

  if (removeStopWords) {
    tokens = tokens.filter((t) => !STOP_WORDS.has(t));
  }

  // Stem each token for morphological normalization.
  // This ensures BM25 matches "gaming" with "games" (both stem to "game").
  return tokens.map((t) => stemmer(t));
}

// ---------------------------------------------------------------------------
// BM25 Scoring (Okapi BM25)
// ---------------------------------------------------------------------------

/**
 * Compute the Okapi BM25 score for a single document against a query.
 *
 * Formula:
 *   score = SUM_i IDF(qi) * (f(qi, D) * (k1 + 1)) / (f(qi, D) + k1 * (1 - b + b * |D| / avgdl))
 *
 * where:
 *   IDF(qi) = ln((N - n(qi) + 0.5) / (n(qi) + 0.5) + 1)
 *   f(qi, D) = frequency of term qi in document D
 *   |D| = length of document D (in tokens)
 *   avgdl = average document length across the corpus
 *   N = total number of documents
 *   n(qi) = number of documents containing term qi
 *
 * @param queryTerms  - Tokenized query terms
 * @param docTerms    - Tokenized document terms
 * @param avgDocLen   - Average document length (in tokens) across the candidate corpus
 * @param docCount    - Total number of documents in the candidate corpus
 * @param termDocFreqs - Map from term to number of documents containing that term
 * @param k1          - BM25 k1 parameter (default 1.2)
 * @param b           - BM25 b parameter (default 0.75)
 */
export function bm25Score(
  queryTerms: string[],
  docTerms: string[],
  avgDocLen: number,
  docCount: number,
  termDocFreqs: Map<string, number>,
  k1: number = 1.2,
  b: number = 0.75,
): number {
  if (docTerms.length === 0 || avgDocLen === 0 || docCount === 0) return 0;

  // Count term frequencies in this document.
  const docTf = new Map<string, number>();
  for (const term of docTerms) {
    docTf.set(term, (docTf.get(term) ?? 0) + 1);
  }

  const docLen = docTerms.length;
  let score = 0;

  for (const qi of queryTerms) {
    const freq = docTf.get(qi) ?? 0;
    if (freq === 0) continue;

    const nqi = termDocFreqs.get(qi) ?? 0;

    // IDF with Robertson-Walker floor: ln((N - n + 0.5) / (n + 0.5) + 1)
    // The +1 inside ln ensures IDF is always >= 0 even when n > N/2.
    const idf = Math.log((docCount - nqi + 0.5) / (nqi + 0.5) + 1);

    // TF saturation with length normalization.
    const tfNorm = (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * docLen / avgDocLen));

    score += idf * tfNorm;
  }

  return score;
}

// ---------------------------------------------------------------------------
// Cosine Similarity
// ---------------------------------------------------------------------------

/**
 * Compute cosine similarity between two vectors.
 *
 * Returns dot(a, b) / (||a|| * ||b||).
 * Returns 0 if either vector has zero magnitude (avoids division by zero).
 */
export function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length === 0 || b.length === 0) return 0;

  const len = Math.min(a.length, b.length);
  let dot = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < len; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  if (denom === 0) return 0;

  return dot / denom;
}

// ---------------------------------------------------------------------------
// Reciprocal Rank Fusion (RRF)
// ---------------------------------------------------------------------------

export interface RankedItem {
  id: string;
  score: number;
}

/**
 * Fuse multiple ranking lists using Reciprocal Rank Fusion.
 *
 * For each document d appearing in any ranking list:
 *   rrfScore(d) = SUM_i 1 / (k + rank_i(d))
 *
 * where rank_i(d) is the 1-based rank of document d in the i-th list.
 * Documents not present in a list are not penalized (they simply receive
 * no contribution from that list).
 *
 * @param rankings - Array of ranking lists, each sorted by score descending.
 *                   Each item has an `id` and a `score`.
 * @param k        - RRF smoothing constant (default 60, per the original paper).
 * @returns        - Fused ranking sorted by RRF score descending.
 */
export function rrfFuse(
  rankings: RankedItem[][],
  k: number = 60,
): RankedItem[] {
  const fusedScores = new Map<string, number>();

  for (const ranking of rankings) {
    for (let rank = 0; rank < ranking.length; rank++) {
      const item = ranking[rank];
      const contribution = 1 / (k + rank + 1); // rank is 0-based, formula uses 1-based
      fusedScores.set(item.id, (fusedScores.get(item.id) ?? 0) + contribution);
    }
  }

  const fused: RankedItem[] = [];
  for (const [id, score] of fusedScores) {
    fused.push({ id, score });
  }

  fused.sort((a, b) => b.score - a.score);
  return fused;
}

// ---------------------------------------------------------------------------
// Weighted Reciprocal Rank Fusion
// ---------------------------------------------------------------------------

/**
 * Fuse multiple ranking lists using Weighted Reciprocal Rank Fusion.
 *
 * Like standard RRF, but each ranking list's contribution is multiplied by
 * its weight, allowing callers to emphasize or de-emphasize specific signals.
 *
 * @param rankings - Array of ranking lists, each sorted by score descending.
 * @param weights  - Weight for each ranking list (same length as rankings).
 * @param k        - RRF smoothing constant (default 60).
 * @returns        - Fused ranking sorted by weighted RRF score descending.
 */
export function weightedRrfFuse(
  rankings: RankedItem[][],
  weights: number[],
  k: number = 60,
): RankedItem[] {
  const fusedScores = new Map<string, number>();

  for (let r = 0; r < rankings.length; r++) {
    const w = weights[r] ?? 1;
    for (let rank = 0; rank < rankings[r].length; rank++) {
      const item = rankings[r][rank];
      const contribution = w * (1 / (k + rank + 1));
      fusedScores.set(item.id, (fusedScores.get(item.id) ?? 0) + contribution);
    }
  }

  const fused: RankedItem[] = [];
  for (const [id, score] of fusedScores) {
    fused.push({ id, score });
  }

  fused.sort((a, b) => b.score - a.score);
  return fused;
}

// ---------------------------------------------------------------------------
// Ranking Weights & Interfaces
// ---------------------------------------------------------------------------

export interface RankingWeights {
  bm25: number;
  cosine: number;
  importance: number;
  recency: number;
}

export const DEFAULT_WEIGHTS: RankingWeights = {
  bm25: 0.25,
  cosine: 0.25,
  importance: 0.25,
  recency: 0.25,
};

// ---------------------------------------------------------------------------
// Query Intent Detection (T326)
// ---------------------------------------------------------------------------

/** The detected intent of a user query. */
export type QueryIntent = 'factual' | 'temporal' | 'semantic';

const TEMPORAL_KEYWORDS = /\b(yesterday|today|last\s+week|last\s+month|recently|recent|latest|ago|when|this\s+week|this\s+month|earlier|before|after|since|during|tonight|morning|afternoon)\b/i;

const FACTUAL_PATTERNS = /^(what|who|where|which|how\s+many|how\s+much|is\s+|are\s+|does\s+|do\s+|did\s+|was\s+|were\s+)\b/i;

/** Ranking weights tuned for each query intent. */
export const INTENT_WEIGHTS: Record<QueryIntent, RankingWeights> = {
  factual:  { bm25: 0.40, cosine: 0.20, importance: 0.25, recency: 0.15 },
  temporal: { bm25: 0.15, cosine: 0.20, importance: 0.20, recency: 0.45 },
  semantic: { bm25: 0.20, cosine: 0.35, importance: 0.25, recency: 0.20 },
};

/**
 * Classify a query into one of three intent types using lightweight heuristics.
 * Temporal is checked first so "What did we discuss yesterday?" → temporal.
 */
export function detectQueryIntent(query: string): QueryIntent {
  if (TEMPORAL_KEYWORDS.test(query)) return 'temporal';
  if (FACTUAL_PATTERNS.test(query) && query.length < 80) return 'factual';
  return 'semantic';
}

export interface RerankerCandidate {
  id: string;
  text: string;
  embedding?: number[];
  importance?: number;   // 0-1 normalized importance score
  createdAt?: number;    // Unix timestamp (seconds) when fact was created
}

export interface RerankerResult extends RerankerCandidate {
  rrfScore: number;
  cosineSimilarity?: number;
}

// ---------------------------------------------------------------------------
// Recency Scoring
// ---------------------------------------------------------------------------

/**
 * Compute a recency score with a 1-week half-life.
 *
 * Score = 1 / (1 + hours_since_creation / 168)
 *
 * A fact created just now scores ~1.0, one week ago scores 0.5,
 * two weeks ago scores ~0.33, etc.
 *
 * @param createdAt - Unix timestamp in seconds
 * @returns         - Recency score in (0, 1]
 */
function recencyScore(createdAt: number): number {
  const nowSeconds = Date.now() / 1000;
  const hoursSince = (nowSeconds - createdAt) / 3600;
  return 1 / (1 + hoursSince / 168);
}

// ---------------------------------------------------------------------------
// MMR (Maximal Marginal Relevance)
// ---------------------------------------------------------------------------

/**
 * Apply Maximal Marginal Relevance to promote diversity in results.
 *
 * MMR re-orders a ranked list of candidates so that highly similar candidates
 * are spread out. The algorithm greedily selects the candidate that maximizes:
 *
 *   MMR(d) = lambda * relevance(d) - (1 - lambda) * max_sim(d, selected)
 *
 * where:
 *   - relevance(d) = position-based score (1.0 for first, linearly decreasing)
 *   - max_sim(d, selected) = max cosine similarity between d and any already
 *     selected candidate (0 if no embeddings available)
 *
 * @param candidates - Candidates in relevance order (best first)
 * @param lambda     - Trade-off between relevance and diversity (default 0.7)
 * @param topK       - Number of results to return (default 8)
 * @returns          - Re-ordered candidates with diversity
 */
export function applyMMR(
  candidates: RerankerCandidate[],
  lambda: number = 0.7,
  topK: number = 8,
): RerankerCandidate[] {
  if (candidates.length === 0) return [];
  if (candidates.length <= 1) return candidates.slice(0, topK);

  const remaining = candidates.map((c, i) => ({ candidate: c, index: i }));
  const selected: RerankerCandidate[] = [];
  const n = candidates.length;

  while (selected.length < topK && remaining.length > 0) {
    let bestIdx = -1;
    let bestMMR = -Infinity;

    for (let i = 0; i < remaining.length; i++) {
      const { candidate, index } = remaining[i];

      // Relevance: linear decay from 1.0 (first) to near 0 (last)
      const relevance = 1.0 - index / n;

      // Max similarity to any already-selected candidate
      let maxSim = 0;
      if (candidate.embedding && candidate.embedding.length > 0) {
        for (const sel of selected) {
          if (sel.embedding && sel.embedding.length > 0) {
            const sim = cosineSimilarity(candidate.embedding, sel.embedding);
            if (sim > maxSim) maxSim = sim;
          }
        }
      }

      const mmr = lambda * relevance - (1 - lambda) * maxSim;
      if (mmr > bestMMR) {
        bestMMR = mmr;
        bestIdx = i;
      }
    }

    if (bestIdx >= 0) {
      selected.push(remaining[bestIdx].candidate);
      remaining.splice(bestIdx, 1);
    } else {
      break;
    }
  }

  return selected;
}

// ---------------------------------------------------------------------------
// Combined Re-Ranker
// ---------------------------------------------------------------------------

/**
 * Re-rank decrypted candidates using BM25 + Cosine + Importance + Recency
 * with Weighted RRF fusion and MMR diversity.
 *
 * Pipeline:
 *   1. Tokenize query and all candidate texts
 *   2. Build corpus statistics (term document frequencies, average doc length)
 *   3. Score each candidate with BM25
 *   4. Score each candidate with cosine similarity (if embedding available)
 *   5. Score each candidate by importance
 *   6. Score each candidate by recency
 *   7. Fuse all 4 rankings with weighted RRF
 *   8. Apply MMR for diversity
 *   9. Return top-k candidates sorted by fused score
 *
 * Backward compatibility:
 *   - Candidates without embeddings get cosine score = 0 and are excluded
 *     from the cosine ranking list. They can still rank well via other signals.
 *   - If NO candidates have embeddings, cosine ranking is omitted.
 *   - Candidates without importance get neutral score (0.5).
 *   - Candidates without createdAt get neutral recency score (0.5).
 *   - topK defaults to 8, weights default to equal (0.25 each).
 *
 * @param query          - The user's search query (plaintext)
 * @param queryEmbedding - Embedding vector for the query
 * @param candidates     - Decrypted candidates with text and optional embeddings
 * @param topK           - Number of results to return (default 8)
 * @param weights        - Optional partial ranking weights (merged with defaults)
 * @returns              - Top-k candidates sorted by fused score, with scores attached
 */
export function rerank(
  query: string,
  queryEmbedding: number[],
  candidates: RerankerCandidate[],
  topK: number = 8,
  weights?: Partial<RankingWeights>,
): RerankerResult[] {
  if (candidates.length === 0) return [];

  // Merge caller weights with defaults
  const w: RankingWeights = { ...DEFAULT_WEIGHTS, ...weights };

  // --- Step 1: Tokenize ---
  const queryTerms = tokenize(query);
  const candidateTerms = candidates.map((c) => tokenize(c.text));

  // --- Step 2: Corpus statistics ---
  const docCount = candidates.length;
  let totalDocLen = 0;

  // Count how many documents contain each term.
  const termDocFreqs = new Map<string, number>();
  for (const terms of candidateTerms) {
    totalDocLen += terms.length;
    const uniqueTerms = new Set(terms);
    for (const term of uniqueTerms) {
      termDocFreqs.set(term, (termDocFreqs.get(term) ?? 0) + 1);
    }
  }

  const avgDocLen = docCount > 0 ? totalDocLen / docCount : 0;

  // --- Step 3: BM25 scores ---
  const bm25Ranking: RankedItem[] = [];
  for (let i = 0; i < candidates.length; i++) {
    const score = bm25Score(queryTerms, candidateTerms[i], avgDocLen, docCount, termDocFreqs);
    bm25Ranking.push({ id: candidates[i].id, score });
  }
  bm25Ranking.sort((a, b) => b.score - a.score);

  // --- Step 4: Cosine similarity scores ---
  const cosineScores = new Map<string, number>();
  const cosineRanking: RankedItem[] = [];
  for (const candidate of candidates) {
    if (candidate.embedding && candidate.embedding.length > 0) {
      const score = cosineSimilarity(queryEmbedding, candidate.embedding);
      cosineScores.set(candidate.id, score);
      cosineRanking.push({ id: candidate.id, score });
    }
  }
  cosineRanking.sort((a, b) => b.score - a.score);

  // --- Step 5: Importance ranking ---
  const importanceRanking: RankedItem[] = candidates.map((c) => ({
    id: c.id,
    score: c.importance ?? 0.5,
  }));
  importanceRanking.sort((a, b) => b.score - a.score);

  // --- Step 6: Recency ranking ---
  const recencyRanking: RankedItem[] = candidates.map((c) => ({
    id: c.id,
    score: c.createdAt != null ? recencyScore(c.createdAt) : 0.5,
  }));
  recencyRanking.sort((a, b) => b.score - a.score);

  // --- Step 7: Weighted RRF fusion ---
  const rankings: RankedItem[][] = [bm25Ranking];
  const rankWeights: number[] = [w.bm25];

  if (cosineRanking.length > 0) {
    rankings.push(cosineRanking);
    rankWeights.push(w.cosine);
  }

  rankings.push(importanceRanking);
  rankWeights.push(w.importance);

  rankings.push(recencyRanking);
  rankWeights.push(w.recency);

  const fused = weightedRrfFuse(rankings, rankWeights);

  // --- Step 8: Build result objects with scores ---
  const candidateMap = new Map<string, RerankerCandidate>();
  for (const c of candidates) {
    candidateMap.set(c.id, c);
  }

  const rrfResults: RerankerResult[] = [];
  for (const item of fused) {
    const candidate = candidateMap.get(item.id);
    if (candidate) {
      rrfResults.push({
        ...candidate,
        rrfScore: item.score,
        cosineSimilarity: cosineScores.get(item.id),
      });
    }
  }

  // --- Step 9: Apply MMR for diversity, then return top-k ---
  const mmrResults = applyMMR(rrfResults, 0.7, topK);

  // Preserve rrfScore and cosineSimilarity through MMR
  return mmrResults as RerankerResult[];
}
