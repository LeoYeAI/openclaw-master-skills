/**
 * TotalReclaw Plugin - Memory Consolidation & Near-Duplicate Detection
 *
 * Provides cross-session / cross-vault deduplication of stored facts using
 * cosine similarity on their embeddings. Unlike semantic-dedup.ts (which
 * handles within-batch dedup at threshold 0.9), this module handles:
 *
 *   1. Store-time dedup — before writing a new fact, check whether a
 *      near-duplicate already exists in the vault (findNearDuplicate).
 *   2. Supersede logic — when a near-duplicate is found, decide whether
 *      the new fact should replace or be skipped (shouldSupersede).
 *   3. Bulk consolidation — cluster all facts in the vault and identify
 *      groups of near-duplicates for cleanup (clusterFacts).
 *
 * This module intentionally has minimal dependencies (only reranker for
 * cosineSimilarity) so it can be tested without pulling in the full
 * plugin dependency graph.
 */

import { cosineSimilarity } from './reranker.js';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

/**
 * Get the cosine similarity threshold for store-time dedup.
 *
 * Configurable via TOTALRECLAW_STORE_DEDUP_THRESHOLD env var.
 * Must be a number in [0, 1]. Falls back to 0.85 if invalid or unset.
 */
export function getStoreDedupThreshold(): number {
  const envVal = process.env.TOTALRECLAW_STORE_DEDUP_THRESHOLD;
  if (envVal !== undefined) {
    const parsed = parseFloat(envVal);
    if (!isNaN(parsed) && parsed >= 0 && parsed <= 1) return parsed;
  }
  return 0.85;
}

/**
 * Get the cosine similarity threshold for bulk consolidation clustering.
 *
 * Configurable via TOTALRECLAW_CONSOLIDATION_THRESHOLD env var.
 * Must be a number in [0, 1]. Falls back to 0.88 if invalid or unset.
 */
export function getConsolidationThreshold(): number {
  const envVal = process.env.TOTALRECLAW_CONSOLIDATION_THRESHOLD;
  if (envVal !== undefined) {
    const parsed = parseFloat(envVal);
    if (!isNaN(parsed) && parsed >= 0 && parsed <= 1) return parsed;
  }
  return 0.88;
}

/** Maximum candidates to compare against during store-time dedup. */
export const STORE_DEDUP_MAX_CANDIDATES = 200;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** A decrypted fact candidate from the vault, with metadata for ranking. */
export interface DecryptedCandidate {
  id: string;
  text: string;
  embedding: number[] | null;
  importance: number;
  decayScore: number;
  createdAt: number;
  version: number;
}

/** A match result from near-duplicate detection. */
export interface NearDuplicateMatch {
  existingFact: DecryptedCandidate;
  similarity: number;
}

/** A cluster of near-duplicate facts for consolidation. */
export interface ConsolidationCluster {
  representative: DecryptedCandidate;
  duplicates: DecryptedCandidate[];
}

// ---------------------------------------------------------------------------
// Store-time dedup
// ---------------------------------------------------------------------------

/**
 * Find the best near-duplicate match for a new fact among existing candidates.
 *
 * Compares the new fact's embedding against all candidates using cosine
 * similarity. Returns the candidate with the highest similarity above the
 * threshold, or null if no match is found.
 *
 * Candidates without embeddings are skipped (fail-safe).
 *
 * @param newFactEmbedding - Embedding vector for the new fact
 * @param candidates       - Existing facts to compare against
 * @param threshold        - Cosine similarity threshold (e.g. 0.85)
 * @returns                - Best match above threshold, or null
 */
export function findNearDuplicate(
  newFactEmbedding: number[],
  candidates: DecryptedCandidate[],
  threshold: number,
): NearDuplicateMatch | null {
  let bestMatch: NearDuplicateMatch | null = null;

  for (const candidate of candidates) {
    if (!candidate.embedding || candidate.embedding.length === 0) continue;

    const similarity = cosineSimilarity(newFactEmbedding, candidate.embedding);
    if (similarity >= threshold) {
      if (!bestMatch || similarity > bestMatch.similarity) {
        bestMatch = { existingFact: candidate, similarity };
      }
    }
  }

  return bestMatch;
}

// ---------------------------------------------------------------------------
// Supersede logic
// ---------------------------------------------------------------------------

/**
 * Decide whether a new fact should supersede an existing near-duplicate.
 *
 * - Higher importance wins.
 * - Equal importance: new fact supersedes (newer is preferred).
 *
 * @param newImportance - Importance score of the new fact
 * @param existingFact  - The existing near-duplicate candidate
 * @returns             - 'supersede' if new fact should replace, 'skip' otherwise
 */
export function shouldSupersede(
  newImportance: number,
  existingFact: DecryptedCandidate,
): 'supersede' | 'skip' {
  if (newImportance >= existingFact.importance) return 'supersede';
  return 'skip';
}

// ---------------------------------------------------------------------------
// Bulk consolidation
// ---------------------------------------------------------------------------

/**
 * Pick the best representative from a group of near-duplicate facts.
 *
 * Tiebreak order:
 *   1. Highest decayScore
 *   2. Most recent (highest createdAt)
 *   3. Longest text
 */
function pickRepresentative(facts: DecryptedCandidate[]): DecryptedCandidate {
  let best = facts[0];
  for (let i = 1; i < facts.length; i++) {
    const f = facts[i];
    if (
      f.decayScore > best.decayScore ||
      (f.decayScore === best.decayScore && f.createdAt > best.createdAt) ||
      (f.decayScore === best.decayScore && f.createdAt === best.createdAt && f.text.length > best.text.length)
    ) {
      best = f;
    }
  }
  return best;
}

/**
 * Cluster facts by semantic similarity using greedy single-pass clustering.
 *
 * For each fact (in order), assigns it to the first existing cluster whose
 * representative has cosine similarity >= threshold. If no cluster matches,
 * a new cluster is started.
 *
 * Only returns clusters that have duplicates (i.e. more than one member).
 * Facts without embeddings are not clustered.
 *
 * @param facts     - All facts to cluster
 * @param threshold - Cosine similarity threshold (e.g. 0.88)
 * @returns         - Clusters with duplicates (representative + duplicates)
 */
export function clusterFacts(
  facts: DecryptedCandidate[],
  threshold: number,
): ConsolidationCluster[] {
  const clusters: { members: DecryptedCandidate[] }[] = [];

  for (const fact of facts) {
    if (!fact.embedding || fact.embedding.length === 0) continue;

    let assigned = false;
    for (const cluster of clusters) {
      // Compare against the first member's embedding (cluster seed)
      const seed = cluster.members[0];
      if (!seed.embedding) continue;

      const similarity = cosineSimilarity(fact.embedding, seed.embedding);
      if (similarity >= threshold) {
        cluster.members.push(fact);
        assigned = true;
        break;
      }
    }

    if (!assigned) {
      clusters.push({ members: [fact] });
    }
  }

  // Only return clusters with duplicates, pick representative for each
  const result: ConsolidationCluster[] = [];
  for (const cluster of clusters) {
    if (cluster.members.length < 2) continue;

    const representative = pickRepresentative(cluster.members);
    const duplicates = cluster.members.filter((m) => m !== representative);
    result.push({ representative, duplicates });
  }

  return result;
}
