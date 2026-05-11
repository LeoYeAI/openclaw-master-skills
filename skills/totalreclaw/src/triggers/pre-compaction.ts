/**
 * TotalReclaw Skill - Pre-Compaction Hook
 *
 * This hook runs BEFORE context compaction occurs.
 * It performs comprehensive extraction of the conversation history.
 *
 * Flow:
 * 1. Full extraction of last 20 turns
 * 2. Comprehensive deduplication against existing memories
 * 3. Graph consolidation (merge entities and relations)
 * 4. Batch upload to server
 * 5. Return PreCompactionResult with stats
 *
 * This hook is more thorough than agent-end and runs less frequently.
 */

import type { TotalReclaw } from '@totalreclaw/client';
import type {
  PreCompactionResult,
  OpenClawContext,
  TotalReclawSkillConfig,
  ExtractedFact,
  Entity,
  Relation,
} from '../types';
import {
  FactExtractor,
  createFactExtractor,
  FactDeduplicator,
  createDeduplicator,
  mergeFacts,
  type LLMClient,
  type VectorStoreClient,
  type ExistingFact,
} from '../extraction';
import { debugLog } from '../debug';

// ============================================================================
// Types
// ============================================================================

/**
 * Options for the pre-compaction hook
 */
export interface PreCompactionOptions {
  /** TotalReclaw client instance */
  client: TotalReclaw;
  /** Skill configuration */
  config: TotalReclawSkillConfig;
  /** LLM client for extraction */
  llmClient: LLMClient;
  /** Vector store client for deduplication (optional) */
  vectorStoreClient?: VectorStoreClient;
  /** Custom fact extractor (optional) */
  extractor?: FactExtractor;
  /** Number of turns to analyze (default: 20) */
  analysisWindow?: number;
  /** Whether to enable debug logging */
  debug?: boolean;
  /** Whether to perform graph consolidation */
  consolidateGraph?: boolean;
}

/**
 * Internal extraction result
 */
interface InternalExtractionResult {
  factsExtracted: number;
  factsStored: number;
  duplicatesSkipped: number;
  updatesPerformed: number;
  deletionsPerformed: number;
  processingTimeMs: number;
  graphStats?: GraphConsolidationStats;
}

/**
 * Graph consolidation statistics
 */
interface GraphConsolidationStats {
  entitiesMerged: number;
  relationsMerged: number;
  uniqueEntities: number;
  uniqueRelations: number;
}

// ============================================================================
// Main Hook Function
// ============================================================================

/**
 * Execute the pre-compaction hook
 *
 * This performs comprehensive extraction and storage before context compaction.
 *
 * @param context - OpenClaw context containing user message and history
 * @param options - Hook options including client and configuration
 * @returns PreCompactionResult with extraction and storage stats
 *
 * @example
 * ```typescript
 * const result = await preCompaction(context, {
 *   client: openMemoryClient,
 *   config: skillConfig,
 *   llmClient: myLLMClient,
 * });
 *
 * console.log(`Extracted ${result.factsExtracted} facts, stored ${result.factsStored}`);
 * ```
 */
export async function preCompaction(
  context: OpenClawContext,
  options: PreCompactionOptions
): Promise<PreCompactionResult> {
  const startTime = Date.now();

  if (options.debug) {
    debugLog(true, `Pre-compaction hook started`);
    debugLog(true, `Analyzing ${context.history.length} turns`);
  }

  try {
    // Run comprehensive extraction
    const result = await runComprehensiveExtraction(context, options);

    if (options.debug) {
      debugLog(true, `Pre-compaction completed in ${result.processingTimeMs}ms`);
      debugLog(true, `  Extracted: ${result.factsExtracted}`);
      debugLog(true, `  Stored: ${result.factsStored}`);
      debugLog(true, `  Skipped: ${result.duplicatesSkipped}`);
      if (result.graphStats) {
        debugLog(true, `  Entities: ${result.graphStats.uniqueEntities}`);
        debugLog(true, `  Relations: ${result.graphStats.uniqueRelations}`);
      }
    }

    return {
      factsExtracted: result.factsExtracted,
      factsStored: result.factsStored,
      duplicatesSkipped: result.duplicatesSkipped,
      processingTimeMs: result.processingTimeMs,
    };
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Unknown error';
    console.error('[TotalReclaw] preCompaction hook failed:', errorMsg);

    return {
      factsExtracted: 0,
      factsStored: 0,
      duplicatesSkipped: 0,
      processingTimeMs: Date.now() - startTime,
    };
  }
}

// ============================================================================
// Extraction Logic
// ============================================================================

/**
 * Run comprehensive extraction from conversation history
 */
async function runComprehensiveExtraction(
  context: OpenClawContext,
  options: PreCompactionOptions
): Promise<InternalExtractionResult> {
  const startTime = Date.now();
  const result: InternalExtractionResult = {
    factsExtracted: 0,
    factsStored: 0,
    duplicatesSkipped: 0,
    updatesPerformed: 0,
    deletionsPerformed: 0,
    processingTimeMs: 0,
  };

  const analysisWindow = options.analysisWindow || 20;

  try {
    // Step 1: Get or create fact extractor
    const extractor = options.extractor || createFactExtractor(
      options.llmClient,
      options.vectorStoreClient,
      {
        minImportance: 1, // Accept all importance levels for comprehensive extraction
        preCompactionWindow: analysisWindow,
      }
    );

    // Step 2: Extract facts using pre-compaction trigger
    const extractionResult = await extractor.extractFacts(context, 'pre_compaction');
    result.factsExtracted = extractionResult.facts.length;

    debugLog(!!options.debug, `Raw extraction: ${result.factsExtracted} facts`);

    // Step 3: Get existing memories for deduplication
    const existingMemories = await getExistingMemories(context, options);

    debugLog(!!options.debug, `Found ${existingMemories.length} existing memories for deduplication`);

    // Step 4: Create deduplicator and process facts
    const deduplicator = createDeduplicator(
      options.llmClient,
      options.vectorStoreClient,
      {
        similarityThreshold: 0.85,
        topK: 5,
        useLLMJudge: true,
      }
    );

    // Step 5: Deduplicate extracted facts
    const deduplicatedFacts = await deduplicator.deduplicateFacts(
      extractionResult.facts,
      existingMemories
    );

    // Step 6: Perform graph consolidation if enabled
    if (options.consolidateGraph !== false) {
      const consolidatedFacts = await consolidateGraph(deduplicatedFacts, options);
      result.graphStats = consolidatedFacts.stats;

      debugLog(!!options.debug, `Graph consolidation: ${result.graphStats.entitiesMerged} entities merged`);
    }

    // Step 7: Store facts in batch
    const storageResult = await storeFactsBatch(deduplicatedFacts, options);

    result.factsStored = storageResult.stored;
    result.duplicatesSkipped = storageResult.skipped;
    result.updatesPerformed = storageResult.updates;
    result.deletionsPerformed = storageResult.deletions;

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Unknown error';
    console.error('[TotalReclaw] Comprehensive extraction failed:', errorMsg);
  }

  result.processingTimeMs = Date.now() - startTime;
  return result;
}

/**
 * Get existing memories for deduplication context
 */
async function getExistingMemories(
  context: OpenClawContext,
  options: PreCompactionOptions
): Promise<ExistingFact[]> {
  try {
    // Search for relevant existing memories based on conversation
    const query = buildDeduplicationQuery(context);
    const results = await options.client.recall(query, 50);

    // Convert to ExistingFact format
    return results.map(r => {
      // Extract type from tags if available
      const typeTag = r.fact.metadata?.tags?.find(t =>
        ['fact', 'preference', 'decision', 'episodic', 'goal', 'context', 'summary'].includes(t)
      ) as ExtractedFact['type'] | undefined;
      const type: ExtractedFact['type'] = typeTag || 'fact';

      return {
        id: r.fact.id,
        factText: r.fact.text,
        type: type,
        importance: (r.fact.metadata?.importance || 0.5) * 10, // Convert back to 1-10 scale
        embedding: r.fact.embedding,
        entities: [],
        relations: [],
      };
    });
  } catch (error) {
    console.error('[TotalReclaw] Failed to get existing memories:', error);
    return [];
  }
}

/**
 * Build a query for fetching existing memories
 */
function buildDeduplicationQuery(context: OpenClawContext): string {
  // Use recent conversation as query context
  const recentTurns = context.history.slice(-10);
  return recentTurns
    .map(t => t.content)
    .join(' ')
    .slice(0, 500);
}

// ============================================================================
// Graph Consolidation
// ============================================================================

/**
 * Consolidate graph by merging duplicate entities and relations
 */
async function consolidateGraph(
  facts: ExtractedFact[],
  options: PreCompactionOptions
): Promise<{ facts: ExtractedFact[]; stats: GraphConsolidationStats }> {
  const stats: GraphConsolidationStats = {
    entitiesMerged: 0,
    relationsMerged: 0,
    uniqueEntities: 0,
    uniqueRelations: 0,
  };

  // Collect all entities and relations
  const entityMap = new Map<string, Entity>();
  const relationSet = new Set<string>();
  const consolidatedRelations: Relation[] = [];

  for (const fact of facts) {
    // Consolidate entities
    for (const entity of fact.entities) {
      const key = `${entity.name.toLowerCase()}-${entity.type}`;
      if (!entityMap.has(key)) {
        entityMap.set(key, entity);
      } else {
        stats.entitiesMerged++;
      }
    }

    // Consolidate relations
    for (const relation of fact.relations) {
      const key = `${relation.subjectId}-${relation.predicate}-${relation.objectId}`;
      if (!relationSet.has(key)) {
        relationSet.add(key);
        consolidatedRelations.push(relation);
      } else {
        stats.relationsMerged++;
      }
    }
  }

  stats.uniqueEntities = entityMap.size;
  stats.uniqueRelations = consolidatedRelations.length;

  // Update facts with consolidated entities and relations
  const consolidatedFacts = facts.map(fact => ({
    ...fact,
    entities: fact.entities.map(e => {
      const key = `${e.name.toLowerCase()}-${e.type}`;
      return entityMap.get(key) || e;
    }),
  }));

  return { facts: consolidatedFacts, stats };
}

// ============================================================================
// Batch Storage
// ============================================================================

/**
 * Store facts in batch for efficiency
 */
async function storeFactsBatch(
  facts: ExtractedFact[],
  options: PreCompactionOptions
): Promise<{
  stored: number;
  skipped: number;
  updates: number;
  deletions: number;
}> {
  const result = {
    stored: 0,
    skipped: 0,
    updates: 0,
    deletions: 0,
  };

  // Process facts in parallel batches for efficiency
  const batchSize = 5;
  const batches: ExtractedFact[][] = [];

  for (let i = 0; i < facts.length; i += batchSize) {
    batches.push(facts.slice(i, i + batchSize));
  }

  for (const batch of batches) {
    const promises = batch.map(fact => storeFactWithResult(fact, options));
    const results = await Promise.allSettled(promises);

    for (const r of results) {
      if (r.status === 'fulfilled') {
        switch (r.value.action) {
          case 'ADD':
            result.stored++;
            break;
          case 'UPDATE':
            result.updates++;
            result.stored++;
            break;
          case 'DELETE':
            result.deletions++;
            break;
          case 'NOOP':
            result.skipped++;
            break;
        }
      } else {
        result.skipped++;
      }
    }
  }

  return result;
}

/**
 * Store a single fact and return the action taken
 */
async function storeFactWithResult(
  fact: ExtractedFact,
  options: PreCompactionOptions
): Promise<{ action: string; factId?: string }> {
  const { client } = options;

  switch (fact.action) {
    case 'ADD':
      const factId = await client.remember(fact.factText, {
        importance: fact.importance / 10,
        source: 'pre_compaction',
        tags: [fact.type],
      });
      return { action: 'ADD', factId };

    case 'UPDATE':
      // Delete old and add new
      if (fact.existingFactId) {
        try {
          await client.forget(fact.existingFactId);
        } catch {
          // Ignore if old fact doesn't exist
        }
      }
      const updateId = await client.remember(fact.factText, {
        importance: fact.importance / 10,
        source: 'pre_compaction',
        tags: [fact.type],
      });
      return { action: 'UPDATE', factId: updateId };

    case 'DELETE':
      if (fact.existingFactId) {
        await client.forget(fact.existingFactId);
      }
      return { action: 'DELETE' };

    case 'NOOP':
    default:
      return { action: 'NOOP' };
  }
}

// ============================================================================
// Exports
// ============================================================================

export default preCompaction;
