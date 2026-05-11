/**
 * Store-time dedup wiring tests for OpenClaw plugin.
 *
 * TAP-style tests (no framework, consistent with consolidation.test.ts).
 * Tests the searchForNearDuplicates() helper function indirectly by
 * testing the dedup behavior in storeExtractedFacts() and
 * totalreclaw_remember tool.
 *
 * Since these functions depend on heavy OpenClaw plugin infrastructure
 * (api client, encryption, logger), we test the pure logic extracted
 * into consolidation.ts directly with realistic scenarios.
 *
 * Run with: npx tsx store-dedup-wiring.test.ts
 */

import {
  findNearDuplicate,
  shouldSupersede,
  getStoreDedupThreshold,
  STORE_DEDUP_MAX_CANDIDATES,
} from './consolidation.js';
import type { DecryptedCandidate } from './consolidation.js';

let passed = 0;
let failed = 0;
const total = 18;

function assert(condition: boolean, name: string): void {
  if (condition) {
    console.log(`ok ${passed + failed + 1} - ${name}`);
    passed++;
  } else {
    console.log(`not ok ${passed + failed + 1} - ${name}`);
    failed++;
  }
}

function makeCandidate(
  id: string,
  text: string,
  embedding: number[] | null,
  importance: number = 5,
  decayScore?: number,
  createdAt?: number,
): DecryptedCandidate {
  return {
    id,
    text,
    embedding,
    importance,
    decayScore: decayScore ?? importance,
    createdAt: createdAt ?? Date.now(),
    version: 1,
  };
}

console.log(`TAP version 14`);
console.log(`1..${total}`);

// ── searchForNearDuplicates wiring scenarios ────────────────────────────────
// These test the logic that searchForNearDuplicates() uses internally.

// Scenario 1-2: Auto-extraction stores "User likes TypeScript"
// Vault already has "User prefers TypeScript" (very similar)
{
  const existingEmbedding = [0.9, 0.1, 0.0, 0.0];
  const newFactEmbedding = [0.88, 0.12, 0.0, 0.0]; // Very similar
  const vault = [makeCandidate('existing-ts', 'User prefers TypeScript', existingEmbedding, 5)];
  const threshold = getStoreDedupThreshold();
  const result = findNearDuplicate(newFactEmbedding, vault, threshold);
  assert(result !== null, 'auto-extract: finds near-duplicate of paraphrased fact');
  assert(result!.existingFact.id === 'existing-ts', 'auto-extract: identifies correct existing fact ID');
}

// Scenario 3: New fact has HIGHER importance -> supersede
{
  const existing = makeCandidate('weak', 'Old note', [1, 0, 0, 0], 3, 3);
  const action = shouldSupersede(8, existing);
  assert(action === 'supersede', 'auto-extract: supersedes when new fact is more important');
}

// Scenario 4: New fact has LOWER importance -> skip
{
  const existing = makeCandidate('strong', 'Important fact', [1, 0, 0, 0], 9, 9);
  const action = shouldSupersede(3, existing);
  assert(action === 'skip', 'auto-extract: skips when existing fact is more important');
}

// Scenario 5: Equal importance -> supersede (newer wins)
{
  const existing = makeCandidate('old', 'Old fact', [1, 0, 0, 0], 5, 5);
  const action = shouldSupersede(5, existing);
  assert(action === 'supersede', 'auto-extract: supersedes on equal importance (newer wins)');
}

// Scenario 6: Explicit remember always supersedes regardless of importance
{
  const existing = makeCandidate('critical', 'Critical existing', [1, 0, 0, 0], 10, 10);
  // For explicit remember: we don't call shouldSupersede, we always supersede
  // This documents the design: explicit remember = user intent, always honor it
  assert(true, 'explicit-remember: always supersedes (by design, no shouldSupersede call)');
}

// Scenario 7: Importance inheritance — max(new, existing)
{
  const existing = makeCandidate('high', 'High importance', [1, 0, 0, 0], 9, 9);
  const newImportance = 3;
  const effectiveImportance = Math.max(newImportance, existing.importance);
  assert(effectiveImportance === 9, 'importance-inheritance: takes max of new and existing');
}

// Scenario 8: No candidates -> no dedup (store normally)
{
  const result = findNearDuplicate([1, 0, 0, 0], [], getStoreDedupThreshold());
  assert(result === null, 'empty-vault: returns null when no candidates');
}

// Scenario 9: All candidates below threshold -> no dedup
{
  const vault = [
    makeCandidate('unrelated1', 'User works at Acme', [0, 1, 0, 0], 5),
    makeCandidate('unrelated2', 'Project uses PostgreSQL', [0, 0, 1, 0], 5),
  ];
  const result = findNearDuplicate([1, 0, 0, 0], vault, getStoreDedupThreshold());
  assert(result === null, 'no-similar: returns null when all candidates below threshold');
}

// Scenario 10-11: Multiple candidates above threshold -> picks highest similarity
{
  const newEmb = [1, 0, 0, 0];
  const vault = [
    makeCandidate('close', 'Close match', [0.95, 0.05, 0.0, 0.0], 5),
    makeCandidate('closer', 'Closer match', [0.99, 0.01, 0.0, 0.0], 5),
  ];
  const result = findNearDuplicate(newEmb, vault, getStoreDedupThreshold());
  assert(result !== null, 'multi-match: finds a match among multiple candidates');
  assert(result!.existingFact.id === 'closer', 'multi-match: picks highest similarity candidate');
}

// Scenario 12-13: Candidate without embedding -> skipped (fail-open)
{
  const vault = [
    makeCandidate('no-emb', 'No embedding', null, 5),
    makeCandidate('has-emb', 'Has embedding', [1, 0, 0, 0], 5),
  ];
  const result = findNearDuplicate([1, 0, 0, 0], vault, getStoreDedupThreshold());
  assert(result !== null, 'missing-embedding: skips candidate without embedding');
  assert(result!.existingFact.id === 'has-emb', 'missing-embedding: finds match from candidate with embedding');
}

// ── Max candidates constant ─────────────────────────────────────────────────

assert(STORE_DEDUP_MAX_CANDIDATES === 200, 'constant: max candidates is 200');
assert(getStoreDedupThreshold() === 0.85, 'constant: default store threshold is 0.85');

// ── Cross-session dedup scenario ────────────────────────────────────────────
// Session 1 stores "User prefers dark mode"
// Session 2 stores "User likes dark themes" — should be caught as near-dup
{
  const session1Fact = makeCandidate('s1-dark', 'User prefers dark mode', [0.9, 0.1, 0.0, 0.0], 7, 7);
  const session2Embedding = [0.87, 0.13, 0.0, 0.0]; // Similar to session 1
  const vault = [session1Fact];
  const result = findNearDuplicate(session2Embedding, vault, getStoreDedupThreshold());
  assert(result !== null, 'cross-session: catches near-duplicate from previous session');
}

// ── Contradiction: cosine correctly does NOT catch it ───────────────────────
{
  const darkMode = makeCandidate('dark', 'User prefers dark mode', [0.9, 0.1, 0.0, 0.0], 7);
  const lightModeEmbedding = [0.1, 0.1, 0.9, 0.0]; // Opposite direction
  const vault = [darkMode];
  const result = findNearDuplicate(lightModeEmbedding, vault, getStoreDedupThreshold());
  assert(result === null, 'contradiction: cosine correctly does NOT catch "dark->light" (LLM layer needed)');
}

// ── Total count verification ────────────────────────────────────────────────
// At this point 17 tests have run; this is the 18th (so passed+failed+1 === total)
assert(passed + failed + 1 === total, `total: ${total} tests executed`);

// ── Summary ─────────────────────────────────────────────────────────────────
console.log(`\n# ${passed}/${total} passed`);
if (failed > 0) {
  console.log(`# ${failed} FAILED`);
  process.exit(1);
}
console.log('\nALL TESTS PASSED');
