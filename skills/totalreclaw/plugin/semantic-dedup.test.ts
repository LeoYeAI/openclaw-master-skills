/**
 * Unit tests for semantic near-duplicate detection (T330).
 *
 * Run with: npx tsx semantic-dedup.test.ts
 *
 * Uses TAP-style output (no test framework dependency).
 */

import { deduplicateBatch, getSemanticDedupThreshold } from './semantic-dedup.js';
import { cosineSimilarity } from './reranker.js';
import type { ExtractedFact } from './extractor.js';

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

// Mock logger that collects log calls
function createMockLogger() {
  const logs: { level: string; args: unknown[] }[] = [];
  return {
    logger: {
      info: (...args: unknown[]) => logs.push({ level: 'info', args }),
      warn: (...args: unknown[]) => logs.push({ level: 'warn', args }),
      error: (...args: unknown[]) => logs.push({ level: 'error', args }),
    },
    logs,
  };
}

// Helper: create an ExtractedFact
function makeFact(text: string, type: ExtractedFact['type'] = 'fact', importance = 5): ExtractedFact {
  return { text, type, importance };
}

// ---------------------------------------------------------------------------
// getSemanticDedupThreshold tests
// ---------------------------------------------------------------------------

console.log('# getSemanticDedupThreshold');

{
  // Default threshold should be 0.9 (no env var set)
  const orig = process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  delete process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  assertClose(getSemanticDedupThreshold(), 0.9, 1e-10, 'default threshold is 0.9');
  if (orig !== undefined) process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = orig;
}

{
  // Custom threshold via env var
  const orig = process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = '0.85';
  assertClose(getSemanticDedupThreshold(), 0.85, 1e-10, 'custom threshold 0.85 from env');
  if (orig !== undefined) {
    process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = orig;
  } else {
    delete process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  }
}

{
  // Invalid env var falls back to default
  const orig = process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = 'not-a-number';
  assertClose(getSemanticDedupThreshold(), 0.9, 1e-10, 'invalid env var falls back to 0.9');
  if (orig !== undefined) {
    process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = orig;
  } else {
    delete process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  }
}

{
  // Out-of-range env var (>1) falls back to default
  const orig = process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = '1.5';
  assertClose(getSemanticDedupThreshold(), 0.9, 1e-10, 'threshold > 1 falls back to 0.9');
  if (orig !== undefined) {
    process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = orig;
  } else {
    delete process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  }
}

{
  // Negative env var falls back to default
  const orig = process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = '-0.5';
  assertClose(getSemanticDedupThreshold(), 0.9, 1e-10, 'negative threshold falls back to 0.9');
  if (orig !== undefined) {
    process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = orig;
  } else {
    delete process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  }
}

// ---------------------------------------------------------------------------
// deduplicateBatch tests
// ---------------------------------------------------------------------------

console.log('# deduplicateBatch');

// Ensure default threshold for remaining tests
delete process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;

{
  // Empty batch returns empty
  const { logger } = createMockLogger();
  const result = deduplicateBatch([], new Map(), logger);
  assert(result.length === 0, 'empty batch returns empty array');
}

{
  // Single fact is always kept
  const { logger } = createMockLogger();
  const facts = [makeFact('I love hiking')];
  const embeddings = new Map([['I love hiking', [1, 0, 0]]]);
  const result = deduplicateBatch(facts, embeddings, logger);
  assert(result.length === 1, 'single fact is always kept');
  assert(result[0].text === 'I love hiking', 'single fact text preserved');
}

{
  // Two identical facts (cosine = 1.0) -- second is removed
  const { logger, logs } = createMockLogger();
  const facts = [
    makeFact('I love hiking'),
    makeFact('I really enjoy hiking in the mountains'),
  ];
  // Use parallel embeddings (cosine = 1.0) to simulate semantic duplicates
  const embeddings = new Map<string, number[]>([
    ['I love hiking', [1, 0, 0]],
    ['I really enjoy hiking in the mountains', [1, 0, 0]],
  ]);
  const result = deduplicateBatch(facts, embeddings, logger);
  assert(result.length === 1, 'identical embeddings: only one fact kept');
  assert(result[0].text === 'I love hiking', 'first fact is the one kept');
  // Should have logged the dedup
  const dedupLogs = logs.filter(l => l.level === 'info' && String(l.args[0]).includes('Semantic dedup: skipping'));
  assert(dedupLogs.length === 1, 'dedup event was logged');
}

{
  // Two dissimilar facts (cosine = 0.0) -- both kept
  const { logger } = createMockLogger();
  const facts = [
    makeFact('I love hiking'),
    makeFact('I work at Google'),
  ];
  const embeddings = new Map<string, number[]>([
    ['I love hiking', [1, 0, 0]],
    ['I work at Google', [0, 1, 0]],
  ]);
  const result = deduplicateBatch(facts, embeddings, logger);
  assert(result.length === 2, 'dissimilar facts: both kept');
}

{
  // Similarity just below threshold (0.89) -- kept; just above (0.91) -- removed
  const { logger: logger1 } = createMockLogger();

  // Construct vectors with specific cosine similarities.
  // cos(a, b) = dot(a, b) / (|a| * |b|)
  // For unit vectors: cos = dot
  // To get cosine = 0.89: a = [1, 0], b = [0.89, sqrt(1-0.89^2)] = [0.89, 0.4560]
  const factsBelowThreshold = [
    makeFact('fact A'),
    makeFact('fact B'),
  ];
  const vecA = [1, 0];
  const vecBBelow = [0.89, Math.sqrt(1 - 0.89 * 0.89)]; // cosine ~ 0.89

  // Verify our vectors produce the expected similarity
  const simBelow = cosineSimilarity(vecA, vecBBelow);
  assertClose(simBelow, 0.89, 0.01, 'test vector cosine ~0.89');

  const embeddingsBelow = new Map<string, number[]>([
    ['fact A', vecA],
    ['fact B', vecBBelow],
  ]);

  const resultBelow = deduplicateBatch(factsBelowThreshold, embeddingsBelow, logger1);
  assert(resultBelow.length === 2, 'cosine ~0.89 (below 0.9 threshold): both facts kept');

  // Now test above threshold
  const { logger: logger2 } = createMockLogger();
  const factsAboveThreshold = [
    makeFact('fact C'),
    makeFact('fact D'),
  ];
  const vecBAbove = [0.91, Math.sqrt(1 - 0.91 * 0.91)]; // cosine ~ 0.91
  const simAbove = cosineSimilarity(vecA, vecBAbove);
  assertClose(simAbove, 0.91, 0.01, 'test vector cosine ~0.91');

  const embeddingsAbove = new Map<string, number[]>([
    ['fact C', vecA],
    ['fact D', vecBAbove],
  ]);
  const resultAbove = deduplicateBatch(factsAboveThreshold, embeddingsAbove, logger2);
  assert(resultAbove.length === 1, 'cosine ~0.91 (above 0.9 threshold): second fact removed');
}

{
  // Facts without embeddings are always kept (fail-open)
  const { logger } = createMockLogger();
  const facts = [
    makeFact('I love hiking'),
    makeFact('I also love hiking a lot'),
    makeFact('No embedding for me'),
  ];
  // Only provide embeddings for the first two (which are near-duplicates)
  const embeddings = new Map<string, number[]>([
    ['I love hiking', [1, 0, 0]],
    ['I also love hiking a lot', [0.99, 0.1, 0]],
  ]);
  // cosine([1,0,0], [0.99,0.1,0]) ~ 0.995 -> duplicate
  const result = deduplicateBatch(facts, embeddings, logger);
  assert(result.length === 2, 'fact without embedding is kept + first fact kept (near-dup removed)');
  assert(result[0].text === 'I love hiking', 'first fact kept');
  assert(result[1].text === 'No embedding for me', 'fact without embedding kept');
}

{
  // Multiple near-duplicates in a batch: only first of each "cluster" kept
  const { logger } = createMockLogger();
  const facts = [
    makeFact('I love hiking'),
    makeFact('I enjoy hiking'),       // near-dup of fact 0
    makeFact('I work at Google'),
    makeFact('I am employed at Google'), // near-dup of fact 2
    makeFact('I have a cat'),
  ];
  const embeddings = new Map<string, number[]>([
    ['I love hiking', [1, 0, 0, 0]],
    ['I enjoy hiking', [0.98, 0.1, 0, 0]],       // cosine ~ 0.995 with hiking cluster
    ['I work at Google', [0, 1, 0, 0]],
    ['I am employed at Google', [0, 0.97, 0.1, 0]], // cosine ~ 0.995 with Google cluster
    ['I have a cat', [0, 0, 0, 1]],
  ]);
  const result = deduplicateBatch(facts, embeddings, logger);
  assert(result.length === 3, 'three clusters produce three facts');
  assert(result[0].text === 'I love hiking', 'hiking cluster: first fact kept');
  assert(result[1].text === 'I work at Google', 'Google cluster: first fact kept');
  assert(result[2].text === 'I have a cat', 'cat fact kept (unique)');
}

{
  // Custom threshold via env var
  const orig = process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = '0.5';

  const { logger } = createMockLogger();
  const facts = [
    makeFact('fact X'),
    makeFact('fact Y'),
  ];
  // cosine([1, 0], [0.6, 0.8]) = 0.6 -> above 0.5 threshold -> deduped
  const embeddings = new Map<string, number[]>([
    ['fact X', [1, 0]],
    ['fact Y', [0.6, 0.8]],
  ]);
  const result = deduplicateBatch(facts, embeddings, logger);
  assert(result.length === 1, 'custom threshold 0.5: cosine 0.6 triggers dedup');

  if (orig !== undefined) {
    process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = orig;
  } else {
    delete process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  }
}

{
  // Threshold = 0 means everything except exact self is a duplicate
  const orig = process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = '0';

  const { logger } = createMockLogger();
  const facts = [
    makeFact('fact A'),
    makeFact('fact B'),
  ];
  // Any non-negative cosine triggers dedup. With non-zero non-orthogonal vectors,
  // cosine will be > 0.
  const embeddings = new Map<string, number[]>([
    ['fact A', [1, 0]],
    ['fact B', [0.01, 0.99]], // cosine ~ 0.01 (very small but > 0)
  ]);
  const result = deduplicateBatch(facts, embeddings, logger);
  assert(result.length === 1, 'threshold 0: even tiny similarity triggers dedup');

  if (orig !== undefined) {
    process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = orig;
  } else {
    delete process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  }
}

{
  // Threshold = 1.0 means only exact duplicates (cosine = 1.0) are removed
  const orig = process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = '1.0';

  const { logger } = createMockLogger();
  const facts = [
    makeFact('fact A'),
    makeFact('fact B'),
    makeFact('fact C'),
  ];
  const embeddings = new Map<string, number[]>([
    ['fact A', [1, 0, 0]],
    ['fact B', [0.999, 0.04, 0]], // cosine ~ 0.999, very close but not 1.0
    ['fact C', [1, 0, 0]],        // exact duplicate embedding of A
  ]);
  const result = deduplicateBatch(facts, embeddings, logger);
  assert(result.length === 2, 'threshold 1.0: only exact cosine=1.0 removed');
  assert(result[0].text === 'fact A', 'fact A kept');
  assert(result[1].text === 'fact B', 'fact B kept (cosine < 1.0)');

  if (orig !== undefined) {
    process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD = orig;
  } else {
    delete process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  }
}

{
  // Empty embedding map -- all facts kept (fail-open)
  const { logger } = createMockLogger();
  const facts = [
    makeFact('fact 1'),
    makeFact('fact 2'),
    makeFact('fact 3'),
  ];
  const result = deduplicateBatch(facts, new Map(), logger);
  assert(result.length === 3, 'empty embedding map: all facts kept');
}

{
  // Order preservation: deduplication preserves insertion order
  const { logger } = createMockLogger();
  const facts = [
    makeFact('unique 1'),
    makeFact('duplicate of 1'),
    makeFact('unique 2'),
    makeFact('duplicate of 2'),
    makeFact('unique 3'),
  ];
  const embeddings = new Map<string, number[]>([
    ['unique 1', [1, 0, 0]],
    ['duplicate of 1', [1, 0, 0]],    // exact dup of unique 1
    ['unique 2', [0, 1, 0]],
    ['duplicate of 2', [0, 1, 0]],    // exact dup of unique 2
    ['unique 3', [0, 0, 1]],
  ]);
  const result = deduplicateBatch(facts, embeddings, logger);
  assert(result.length === 3, 'order preservation: 3 unique facts kept');
  assert(result[0].text === 'unique 1', 'order: first is unique 1');
  assert(result[1].text === 'unique 2', 'order: second is unique 2');
  assert(result[2].text === 'unique 3', 'order: third is unique 3');
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
