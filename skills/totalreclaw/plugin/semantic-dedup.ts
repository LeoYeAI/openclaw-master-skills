/**
 * TotalReclaw Plugin - Semantic Near-Duplicate Detection (T330)
 *
 * Provides batch-level deduplication of extracted facts using cosine
 * similarity on their embeddings. Facts within the same extraction batch
 * that are semantically near-duplicates (cosine >= threshold) are reduced
 * to keep only the first occurrence.
 *
 * This module intentionally has minimal dependencies (only reranker for
 * cosineSimilarity and extractor for the ExtractedFact type) so it can
 * be tested without pulling in the full plugin dependency graph.
 */

import { cosineSimilarity } from './reranker.js';
import type { ExtractedFact } from './extractor.js';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

/**
 * Get the cosine similarity threshold for semantic dedup.
 *
 * Configurable via TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD env var.
 * Must be a number in [0, 1]. Falls back to 0.9 if invalid or unset.
 */
export function getSemanticDedupThreshold(): number {
  const envVal = process.env.TOTALRECLAW_SEMANTIC_DEDUP_THRESHOLD;
  if (envVal !== undefined) {
    const parsed = parseFloat(envVal);
    if (!isNaN(parsed) && parsed >= 0 && parsed <= 1) return parsed;
  }
  return 0.9;
}

// ---------------------------------------------------------------------------
// Logger interface (minimal, matches OpenClawPluginApi['logger'])
// ---------------------------------------------------------------------------

interface Logger {
  info(...args: unknown[]): void;
  warn(...args: unknown[]): void;
  error(...args: unknown[]): void;
}

// ---------------------------------------------------------------------------
// Batch deduplication
// ---------------------------------------------------------------------------

/**
 * Deduplicate a batch of extracted facts using cosine similarity on their
 * embeddings. Facts without embeddings are always kept (fail-open).
 *
 * For each fact, compares its embedding against all previously kept facts.
 * If any kept fact has cosine similarity >= threshold, the new fact is
 * considered a near-duplicate and is skipped.
 *
 * @param facts      - Array of extracted facts to deduplicate
 * @param embeddings - Map from fact text to its embedding vector
 * @param logger     - Logger for reporting skipped duplicates
 * @returns          - Deduplicated array (subset of input, preserving order)
 */
export function deduplicateBatch(
  facts: ExtractedFact[],
  embeddings: Map<string, number[]>,
  logger: Logger,
): ExtractedFact[] {
  const threshold = getSemanticDedupThreshold();
  const kept: ExtractedFact[] = [];

  for (const fact of facts) {
    const factEmb = embeddings.get(fact.text);
    if (!factEmb) {
      // No embedding available -- keep the fact (fail-open)
      kept.push(fact);
      continue;
    }

    let isDuplicate = false;
    for (const keptFact of kept) {
      const keptEmb = embeddings.get(keptFact.text);
      if (!keptEmb) continue;

      const similarity = cosineSimilarity(factEmb, keptEmb);
      if (similarity >= threshold) {
        isDuplicate = true;
        logger.info(
          `Semantic dedup: skipping "${fact.text}" (cosine=${similarity.toFixed(3)} >= ${threshold} with "${keptFact.text}")`,
        );
        break;
      }
    }

    if (!isDuplicate) {
      kept.push(fact);
    }
  }

  return kept;
}
