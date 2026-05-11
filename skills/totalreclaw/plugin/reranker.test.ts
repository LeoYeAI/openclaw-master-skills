/**
 * Unit tests for the TotalReclaw re-ranker module.
 *
 * Run with: npx tsx reranker.test.ts
 *
 * Uses TAP-style output (no test framework dependency).
 */

import {
  tokenize,
  bm25Score,
  cosineSimilarity,
  rrfFuse,
  rerank,
  detectQueryIntent,
  DEFAULT_WEIGHTS,
  type RankedItem,
  type RerankerCandidate,
  type RankingWeights,
  type QueryIntent,
} from './reranker.js';

let passed = 0;
let failed = 0;
let testNum = 0;

function assert(condition: boolean, message: string): void {
  testNum++;
  if (condition) {
    passed++;
    console.log(`ok ${testNum} - ${message}`);
  } else {
    failed++;
    console.log(`not ok ${testNum} - ${message}`);
  }
}

function assertClose(actual: number, expected: number, epsilon: number, message: string): void {
  const diff = Math.abs(actual - expected);
  assert(diff < epsilon, `${message} (expected ~${expected}, got ${actual}, diff=${diff})`);
}

// ---------------------------------------------------------------------------
// Tokenization tests
// ---------------------------------------------------------------------------

console.log('# Tokenization');

{
  const tokens = tokenize('Hello World');
  // "hello" and "world" are both NOT stop words, so both are kept
  assert(tokens.length === 2, 'keeps both "hello" and "world" (neither is a stop word)');
  assert(tokens.includes('hello'), '"hello" is kept');
  assert(tokens.includes('world'), '"world" is kept');
}

{
  const tokens = tokenize('The quick brown fox jumps over the lazy dog');
  // "the" (x2), "over" are stop words? "over" is NOT in stop list. "the" IS.
  // After stop word removal: "quick", "brown", "fox", "jumps", "over", "lazy", "dog"
  assert(!tokens.includes('the'), 'removes "the" stop word');
  assert(tokens.includes('quick'), 'keeps "quick"');
  assert(tokens.includes('fox'), 'keeps "fox"');
}

{
  const tokens = tokenize('I am a test!', false);
  // Without stop word removal: "am", "test" ("I" and "a" are < 2 chars)
  assert(tokens.includes('am'), 'keeps short words without stop word removal');
  assert(tokens.includes('test'), 'keeps "test"');
  assert(!tokens.includes('a'), 'filters single-char tokens');
}

{
  const tokens = tokenize('Hello, World! How are you?');
  // Punctuation removed, then stop words: "hello" stays (not a stop word),
  // "world" stays, "how" removed (stop word), "are" removed, "you" removed
  assert(tokens.includes('hello'), 'punctuation removed, "hello" kept');
  assert(tokens.includes('world'), '"world" kept after punctuation removal');
  assert(!tokens.includes('how'), '"how" removed as stop word');
  assert(!tokens.includes('are'), '"are" removed as stop word');
}

{
  const tokens = tokenize('');
  assert(tokens.length === 0, 'empty string returns empty array');
}

// ---------------------------------------------------------------------------
// BM25 tests
// ---------------------------------------------------------------------------

console.log('# BM25 Scoring');

{
  // Simple single-document scenario
  const queryTerms = ['alex', 'works'];
  const docTerms = ['alex', 'works', 'nexus', 'labs'];
  const avgDocLen = 4;
  const docCount = 1;
  const termDocFreqs = new Map<string, number>([
    ['alex', 1], ['works', 1], ['nexus', 1], ['labs', 1],
  ]);

  const score = bm25Score(queryTerms, docTerms, avgDocLen, docCount, termDocFreqs);
  assert(score > 0, `BM25: matching query gets positive score (${score.toFixed(4)})`);
}

{
  // No overlap
  const queryTerms = ['python', 'programming'];
  const docTerms = ['alex', 'works', 'nexus', 'labs'];
  const avgDocLen = 4;
  const docCount = 1;
  const termDocFreqs = new Map<string, number>([
    ['alex', 1], ['works', 1], ['nexus', 1], ['labs', 1],
  ]);

  const score = bm25Score(queryTerms, docTerms, avgDocLen, docCount, termDocFreqs);
  assert(score === 0, 'BM25: no overlap gives zero score');
}

{
  // Higher TF -> higher score
  const queryTerms = ['test'];
  const doc1Terms = ['test', 'document', 'about', 'testing'];  // test appears 1x
  const doc2Terms = ['test', 'test', 'test', 'document'];       // test appears 3x
  const avgDocLen = 4;
  const docCount = 2;
  const termDocFreqs = new Map<string, number>([['test', 2], ['document', 2], ['about', 1], ['testing', 1]]);

  const score1 = bm25Score(queryTerms, doc1Terms, avgDocLen, docCount, termDocFreqs);
  const score2 = bm25Score(queryTerms, doc2Terms, avgDocLen, docCount, termDocFreqs);
  assert(score2 > score1, `BM25: higher TF gives higher score (${score2.toFixed(4)} > ${score1.toFixed(4)})`);
}

{
  // Rarer terms have higher IDF
  const queryTerms = ['rare'];
  const docTerms = ['rare', 'word'];
  const avgDocLen = 4;
  const docCount = 100;
  const rareFreq = new Map<string, number>([['rare', 1], ['word', 50]]);
  const commonFreq = new Map<string, number>([['rare', 50], ['word', 50]]);

  const scoreRare = bm25Score(queryTerms, docTerms, avgDocLen, docCount, rareFreq);
  const scoreCommon = bm25Score(queryTerms, docTerms, avgDocLen, docCount, commonFreq);
  assert(scoreRare > scoreCommon, `BM25: rare terms score higher (${scoreRare.toFixed(4)} > ${scoreCommon.toFixed(4)})`);
}

{
  // Empty inputs
  assert(bm25Score(['hello'], [], 4, 10, new Map()) === 0, 'BM25: empty doc returns 0');
  assert(bm25Score([], ['hello'], 4, 10, new Map()) === 0, 'BM25: empty query returns 0');
  assert(bm25Score(['hello'], ['hello'], 0, 10, new Map([['hello', 1]])) === 0, 'BM25: avgDocLen=0 returns 0');
}

{
  // Known BM25 computation (manual verification)
  // query = ["test"], doc = ["test", "document"], N=10, n("test")=3, avgdl=5
  // IDF = ln((10 - 3 + 0.5) / (3 + 0.5) + 1) = ln(7.5/3.5 + 1) = ln(3.14286) = 1.14554
  // TF = (1 * (1.2 + 1)) / (1 + 1.2 * (1 - 0.75 + 0.75 * 2/5)) = 2.2 / (1 + 1.2 * 0.55) = 2.2 / 1.66 = 1.32530
  // score = 1.14554 * 1.32530 = 1.51849
  const queryTerms = ['test'];
  const docTerms = ['test', 'document'];
  const score = bm25Score(queryTerms, docTerms, 5, 10, new Map([['test', 3]]));
  assertClose(score, 1.51849, 0.01, 'BM25: known computation matches expected value');
}

// ---------------------------------------------------------------------------
// Cosine similarity tests
// ---------------------------------------------------------------------------

console.log('# Cosine Similarity');

{
  // Parallel vectors -> 1.0
  const a = [1, 2, 3];
  const b = [2, 4, 6];
  assertClose(cosineSimilarity(a, b), 1.0, 1e-10, 'Cosine: parallel vectors = 1.0');
}

{
  // Orthogonal vectors -> 0.0
  const a = [1, 0];
  const b = [0, 1];
  assertClose(cosineSimilarity(a, b), 0.0, 1e-10, 'Cosine: orthogonal vectors = 0.0');
}

{
  // Opposite vectors -> -1.0
  const a = [1, 2, 3];
  const b = [-1, -2, -3];
  assertClose(cosineSimilarity(a, b), -1.0, 1e-10, 'Cosine: opposite vectors = -1.0');
}

{
  // Same vector -> 1.0
  const a = [3, 4];
  assertClose(cosineSimilarity(a, a), 1.0, 1e-10, 'Cosine: vector with itself = 1.0');
}

{
  // Zero vector -> 0.0
  const a = [0, 0, 0];
  const b = [1, 2, 3];
  assertClose(cosineSimilarity(a, b), 0.0, 1e-10, 'Cosine: zero vector = 0.0');
}

{
  // Both zero vectors -> 0.0
  const a = [0, 0];
  const b = [0, 0];
  assertClose(cosineSimilarity(a, b), 0.0, 1e-10, 'Cosine: both zero vectors = 0.0');
}

{
  // Empty vectors -> 0.0
  assertClose(cosineSimilarity([], [1, 2]), 0.0, 1e-10, 'Cosine: empty vector a = 0.0');
  assertClose(cosineSimilarity([1, 2], []), 0.0, 1e-10, 'Cosine: empty vector b = 0.0');
}

{
  // Known cosine: [1,1] and [1,0] -> cos(45 deg) = sqrt(2)/2 ~ 0.7071
  const a = [1, 1];
  const b = [1, 0];
  assertClose(cosineSimilarity(a, b), Math.SQRT2 / 2, 1e-10, 'Cosine: 45-degree angle = sqrt(2)/2');
}

// ---------------------------------------------------------------------------
// RRF tests
// ---------------------------------------------------------------------------

console.log('# Reciprocal Rank Fusion');

{
  // Two rankings, same items, different order
  const ranking1: RankedItem[] = [
    { id: 'A', score: 10 },
    { id: 'B', score: 8 },
    { id: 'C', score: 6 },
  ];
  const ranking2: RankedItem[] = [
    { id: 'C', score: 10 },
    { id: 'A', score: 8 },
    { id: 'B', score: 6 },
  ];

  const fused = rrfFuse([ranking1, ranking2], 60);

  // Expected RRF scores (k=60, 1-based ranks):
  // A: 1/(60+1) + 1/(60+2) = 0.01639 + 0.01613 = 0.03253
  // B: 1/(60+2) + 1/(60+3) = 0.01613 + 0.01587 = 0.03200
  // C: 1/(60+3) + 1/(60+1) = 0.01587 + 0.01639 = 0.03226

  assert(fused.length === 3, 'RRF: all items present');
  assert(fused[0].id === 'A', 'RRF: A ranked first (appears in rank 1 + rank 2)');
  assert(fused[1].id === 'C', 'RRF: C ranked second (appears in rank 3 + rank 1)');
  assert(fused[2].id === 'B', 'RRF: B ranked third');
}

{
  // Items present in only one ranking
  const ranking1: RankedItem[] = [
    { id: 'X', score: 10 },
    { id: 'Y', score: 5 },
  ];
  const ranking2: RankedItem[] = [
    { id: 'Z', score: 10 },
    { id: 'X', score: 5 },
  ];

  const fused = rrfFuse([ranking1, ranking2], 60);

  assert(fused.length === 3, 'RRF: all unique items present (X, Y, Z)');
  // X appears in both rankings -> highest score
  assert(fused[0].id === 'X', 'RRF: X ranked first (in both lists)');
}

{
  // Single ranking -> RRF just orders by that ranking
  const ranking: RankedItem[] = [
    { id: 'A', score: 10 },
    { id: 'B', score: 5 },
  ];

  const fused = rrfFuse([ranking], 60);
  assert(fused[0].id === 'A', 'RRF: single ranking preserves order');
  assert(fused[1].id === 'B', 'RRF: single ranking preserves order (second)');
}

{
  // Empty rankings
  const fused = rrfFuse([], 60);
  assert(fused.length === 0, 'RRF: empty input returns empty');
}

{
  // Verify RRF scores numerically
  const ranking1: RankedItem[] = [
    { id: 'D1', score: 1 },  // rank 1 -> 1/(60+1)
    { id: 'D2', score: 0.5 },  // rank 2 -> 1/(60+2)
  ];
  const ranking2: RankedItem[] = [
    { id: 'D2', score: 1 },  // rank 1 -> 1/(60+1)
    { id: 'D1', score: 0.5 },  // rank 2 -> 1/(60+2)
  ];

  const fused = rrfFuse([ranking1, ranking2], 60);

  // D1: 1/61 + 1/62 = 0.03252
  // D2: 1/62 + 1/61 = 0.03252
  // Both should have equal score
  assertClose(fused[0].score, fused[1].score, 1e-10, 'RRF: symmetric rankings produce equal scores');
  assertClose(fused[0].score, 1/61 + 1/62, 1e-10, 'RRF: correct numeric score');
}

// ---------------------------------------------------------------------------
// End-to-end rerank tests
// ---------------------------------------------------------------------------

console.log('# Rerank (end-to-end)');

{
  // BM25-only (no embeddings) - should still work
  // Use terms that match exactly to avoid stemming issues (BM25 has no stemmer)
  const candidates: RerankerCandidate[] = [
    { id: '1', text: 'Alex works Nexus Labs senior engineer' },
    { id: '2', text: 'The weather today is sunny and warm' },
    { id: '3', text: 'Bob enjoys hiking in the mountains on weekends' },
  ];

  // Query: "Alex Nexus Labs" -> tokens: ["alex", "nexus", "labs"]
  // Doc 1 matches all 3 terms, Doc 2 and 3 match zero
  const results = rerank('Alex Nexus Labs', [], candidates, 2);

  assert(results.length === 2, 'Rerank: returns topK=2 results');
  assert(results[0].id === '1', 'Rerank: BM25-only ranks matching document first');
}

{
  // Mixed candidates: some with embeddings, some without
  // Embeddings are fabricated such that candidate 2 is semantically closer
  // to the query than candidate 1, even though candidate 1 has better BM25.
  const queryEmb = [1, 0, 0, 0];
  const candidates: RerankerCandidate[] = [
    {
      id: '1',
      text: 'Alex employed Nexus Labs senior engineer',  // good BM25 match for "alex" + "employed"
      embedding: [0, 1, 0, 0],  // orthogonal to query embedding
    },
    {
      id: '2',
      text: 'career position company staff',  // poor BM25 match (no overlapping terms)
      embedding: [0.99, 0.1, 0, 0],  // very close to query embedding
    },
    {
      id: '3',
      text: 'sunny weather forecast today',
      embedding: [0, 0, 0, 1],  // orthogonal
    },
  ];

  const results = rerank('Alex employed somewhere', queryEmb, candidates, 3);
  assert(results.length === 3, 'Rerank: returns all 3 candidates');

  // With RRF fusion, candidate 1 (good BM25) and candidate 2 (good cosine)
  // should be in top 2. The exact order depends on RRF, but both should
  // beat candidate 3 which has neither.
  const topTwoIds = new Set([results[0].id, results[1].id]);
  assert(topTwoIds.has('1'), 'Rerank: BM25-strong candidate in top 2');
  assert(topTwoIds.has('2'), 'Rerank: cosine-strong candidate in top 2');
  assert(results[2].id === '3', 'Rerank: irrelevant candidate ranked last');
}

{
  // Empty candidates
  const results = rerank('test query', [1, 0, 0], [], 5);
  assert(results.length === 0, 'Rerank: empty candidates returns empty');
}

{
  // topK larger than candidates
  const candidates: RerankerCandidate[] = [
    { id: '1', text: 'only candidate' },
  ];
  const results = rerank('only', [], candidates, 10);
  assert(results.length === 1, 'Rerank: returns all candidates when topK > count');
}

{
  // Backward compatibility: candidates without embeddings
  // Even when queryEmbedding is provided, candidates without embeddings
  // should still be ranked by BM25 only.
  const queryEmb = [1, 0, 0];
  const candidates: RerankerCandidate[] = [
    { id: 'v1', text: 'Alex works at Nexus Labs' },  // no embedding (v1 fact)
    { id: 'v2', text: 'Alex works at Nexus Labs', embedding: [0.9, 0.1, 0] },  // has embedding
  ];

  const results = rerank('Alex Nexus Labs', queryEmb, candidates, 2);
  assert(results.length === 2, 'Rerank: backward compat - both v1 and v2 facts returned');
  // v2 should rank higher because it benefits from both BM25 and cosine
  assert(results[0].id === 'v2', 'Rerank: v2 fact with embedding ranks above v1 (benefits from cosine + BM25)');
}

// ---------------------------------------------------------------------------
// RerankResult.cosineSimilarity tests
// ---------------------------------------------------------------------------

console.log('# RerankResult cosine similarity field');

{
  // Results with embeddings should have cosineSimilarity set
  const queryEmb = [1, 0, 0];
  const candidates: RerankerCandidate[] = [
    { id: 'a', text: 'first document', embedding: [0.9, 0.1, 0] },
    { id: 'b', text: 'second document', embedding: [0, 1, 0] },
  ];

  const results = rerank('first document', queryEmb, candidates, 2);
  assert(results.length === 2, 'RerankResult: returns 2 results');
  const resultA = results.find(r => r.id === 'a');
  const resultB = results.find(r => r.id === 'b');
  assert(resultA !== undefined, 'RerankResult: result a exists');
  assert(resultB !== undefined, 'RerankResult: result b exists');
  assert(resultA!.cosineSimilarity !== undefined, 'RerankResult: a has cosineSimilarity');
  assert(resultB!.cosineSimilarity !== undefined, 'RerankResult: b has cosineSimilarity');
  assert(resultA!.cosineSimilarity! > resultB!.cosineSimilarity!, 'RerankResult: a has higher cosine similarity than b');
}

{
  // Results without embeddings should have cosineSimilarity undefined
  const candidates: RerankerCandidate[] = [
    { id: 'no-emb', text: 'a document without embedding' },
  ];

  const results = rerank('document', [], candidates, 1);
  assert(results.length === 1, 'RerankResult: returns 1 result without embedding');
  assert(results[0].cosineSimilarity === undefined, 'RerankResult: no embedding -> cosineSimilarity is undefined');
}

// ---------------------------------------------------------------------------
// Weighted reranking tests
// ---------------------------------------------------------------------------

console.log('# Weighted Reranking');

{
  // Recency-heavy weights should promote newer facts
  const now = Math.floor(Date.now() / 1000);
  const candidates: RerankerCandidate[] = [
    { id: 'old', text: 'meeting notes from project kickoff', createdAt: now - 30 * 24 * 60 * 60, importance: 0.5 },
    { id: 'new', text: 'meeting notes from project update', createdAt: now - 1 * 60 * 60, importance: 0.5 },
  ];

  const temporalWeights: RankingWeights = { bm25: 0.15, cosine: 0.20, importance: 0.20, recency: 0.45 };
  const results = rerank('meeting notes', [], candidates, 2, temporalWeights);

  assert(results.length === 2, 'Weighted: returns both candidates');
  assert(results[0].id === 'new', 'Weighted: temporal weights promote newer fact to top');
}

{
  // Importance-heavy weights should promote high-importance facts
  const now = Math.floor(Date.now() / 1000);
  const candidates: RerankerCandidate[] = [
    { id: 'low-imp', text: 'Alex mentioned liking coffee', importance: 0.2, createdAt: now - 3600 },
    { id: 'high-imp', text: 'Alex mentioned liking tea', importance: 0.9, createdAt: now - 3600 },
  ];

  const importanceWeights: RankingWeights = { bm25: 0.10, cosine: 0.10, importance: 0.70, recency: 0.10 };
  const results = rerank('Alex likes', [], candidates, 2, importanceWeights);

  assert(results.length === 2, 'Weighted: returns both candidates with importance weights');
  assert(results[0].id === 'high-imp', 'Weighted: importance-heavy weights promote high-importance fact');
}

{
  // BM25-heavy weights (factual) should promote exact term matches
  const candidates: RerankerCandidate[] = [
    { id: 'exact', text: "Alex's email is alex@example.com" },
    { id: 'vague', text: 'Someone once mentioned contact information for reaching out' },
  ];

  const factualWeights: RankingWeights = { bm25: 0.40, cosine: 0.20, importance: 0.25, recency: 0.15 };
  const results = rerank("What is Alex's email?", [], candidates, 2, factualWeights);

  assert(results[0].id === 'exact', 'Weighted: factual weights promote exact term match (BM25-heavy)');
}

{
  // Default weights should work the same as no weights
  const candidates: RerankerCandidate[] = [
    { id: '1', text: 'Alex works Nexus Labs senior engineer' },
    { id: '2', text: 'The weather today is sunny and warm' },
  ];

  const withDefaults = rerank('Alex Nexus Labs', [], candidates, 2, DEFAULT_WEIGHTS);
  const withoutWeights = rerank('Alex Nexus Labs', [], candidates, 2);

  assert(withDefaults[0].id === withoutWeights[0].id, 'Weighted: default weights match no-weights behavior');
}

// ---------------------------------------------------------------------------
// Query Intent Detection tests
// ---------------------------------------------------------------------------

console.log('# Query Intent Detection');

{
  // Factual queries
  const factualQueries = [
    "What's Alex's email?",
    "Who is the project lead?",
    "Where does Sarah live?",
    "How many people are on the team?",
    "Is the project using TypeScript?",
    "Does Alex work at Nexus?",
  ];

  for (const q of factualQueries) {
    const intent = detectQueryIntent(q);
    assert(intent === 'factual', `Intent: "${q}" => factual (got ${intent})`);
  }
}

{
  // Temporal queries
  const temporalQueries = [
    "What did we discuss yesterday?",
    "What happened last week?",
    "Any recent updates?",
    "What was mentioned earlier today?",
    "Tell me what changed since Monday",
    "What did Alex say this morning?",
  ];

  for (const q of temporalQueries) {
    const intent = detectQueryIntent(q);
    assert(intent === 'temporal', `Intent: "${q}" => temporal (got ${intent})`);
  }
}

{
  // Semantic queries (default)
  const semanticQueries = [
    "Tell me about Alex's work preferences",
    "Explain the project architecture",
    "Summarize the project architecture and its main design decisions and tradeoffs that were discussed",
    "Alex personality traits and communication style",
  ];

  for (const q of semanticQueries) {
    const intent = detectQueryIntent(q);
    assert(intent === 'semantic', `Intent: "${q}" => semantic (got ${intent})`);
  }
}

{
  // Temporal overrides factual: "What did we discuss yesterday?" has both
  // factual pattern ("What") and temporal keyword ("yesterday")
  const intent = detectQueryIntent("What did we discuss yesterday?");
  assert(intent === 'temporal', 'Intent: temporal overrides factual when both match');
}

{
  // Long factual-pattern queries fall through to semantic (>80 chars)
  const longQuery = "What are all the different design patterns and architectural decisions that were discussed in the project?";
  const intent = detectQueryIntent(longQuery);
  assert(intent === 'semantic', `Intent: long factual-pattern query => semantic (got ${intent})`);
}

{
  // "What do you know about X?" is factual (starts with "what", under 80 chars)
  const intent = detectQueryIntent("What do you know about hiking?");
  assert(intent === 'factual', `Intent: "What do you know about..." => factual (got ${intent})`);
}

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------

console.log(`\n1..${testNum}`);
console.log(`# pass: ${passed}`);
console.log(`# fail: ${failed}`);

if (failed > 0) {
  console.log('\nFAILED');
  process.exit(1);
} else {
  console.log('\nALL TESTS PASSED');
  process.exit(0);
}
