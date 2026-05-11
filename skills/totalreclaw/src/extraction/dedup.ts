/**
 * TotalReclaw Skill - Deduplication Logic
 *
 * Handles detection of duplicate facts using:
 * 1. Vector similarity for initial candidate retrieval
 * 2. LLM judge for final ADD/UPDATE/DELETE decision
 * 3. Contradiction handling for conflicting facts
 */

import type { ExtractedFact, Entity, Relation, ExtractionAction } from '../types';
import {
  DEDUP_JUDGE_PROMPT,
  CONTRADICTION_DETECTION_PROMPT,
  formatExistingMemories,
  validateExtractionResponse
} from './prompts';

// ============================================================================
// Types
// ============================================================================

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
  complete(prompt: { system: string; user: string }): Promise<string>;
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
export const DEFAULT_DEDUP_CONFIG: DedupConfig = {
  similarityThreshold: 0.85,
  topK: 5,
  useLLMJudge: true,
  minConfidenceForOverride: 0.7
};

// ============================================================================
// Deduplication Class
// ============================================================================

/**
 * Fact deduplicator that uses vector similarity + LLM judge
 */
export class FactDeduplicator {
  private config: DedupConfig;
  private llmClient: LLMClient | null;
  private vectorStore: VectorStoreClient | null;

  constructor(
    config: Partial<DedupConfig> = {},
    llmClient?: LLMClient,
    vectorStore?: VectorStoreClient
  ) {
    this.config = { ...DEFAULT_DEDUP_CONFIG, ...config };
    this.llmClient = llmClient || null;
    this.vectorStore = vectorStore || null;
  }

  /**
   * Check if a fact should be ADD/UPDATE/DELETE/NOOP
   */
  async checkDuplication(fact: ExtractedFact): Promise<DedupResult> {
    // If no vector store, use simple text-based comparison
    if (!this.vectorStore) {
      return this.textBasedDedup(fact);
    }

    // Get embedding for the fact
    const embedding = await this.vectorStore.getEmbedding(fact.factText);

    // Find similar existing facts
    const similarFacts = await this.vectorStore.findSimilar(embedding, this.config.topK);

    // Filter by similarity threshold
    const candidates = similarFacts.filter(f =>
      this.calculateCosineSimilarity(embedding, f.embedding || []) >= this.config.similarityThreshold
    );

    // No similar facts found - ADD
    if (candidates.length === 0) {
      return {
        action: 'ADD',
        confidence: 0.95,
        reasoning: 'No similar existing facts found'
      };
    }

    // Use LLM judge if available and enabled
    if (this.config.useLLMJudge && this.llmClient) {
      return this.llmJudgeDedup(fact, candidates);
    }

    // Fall back to heuristic-based decision
    return this.heuristicDedup(fact, candidates);
  }

  /**
   * Deduplicate multiple facts against existing memories
   */
  async deduplicateFacts(
    facts: ExtractedFact[],
    existingFacts: ExistingFact[]
  ): Promise<ExtractedFact[]> {
    const results: ExtractedFact[] = [];

    for (const fact of facts) {
      // Find similar existing facts
      const candidates = await this.findSimilarFacts(fact, existingFacts);

      if (candidates.length === 0) {
        // No similar facts - keep as ADD
        results.push({ ...fact, action: fact.action || 'ADD' });
        continue;
      }

      // Determine action using LLM judge or heuristics
      const dedupResult = await this.checkDuplication(fact);

      // Apply the dedup result
      results.push({
        ...fact,
        action: dedupResult.action,
        existingFactId: dedupResult.existingFactId,
        confidence: Math.min(fact.confidence, dedupResult.confidence)
      });
    }

    return results;
  }

  /**
   * Find similar facts from a list of existing facts
   */
  private async findSimilarFacts(
    fact: ExtractedFact,
    existingFacts: ExistingFact[]
  ): Promise<ExistingFact[]> {
    if (!this.vectorStore) {
      // Text-based similarity
      return existingFacts.filter(ef =>
        this.textSimilarity(fact.factText, ef.factText) >= this.config.similarityThreshold
      );
    }

    const embedding = await this.vectorStore.getEmbedding(fact.factText);

    return existingFacts.filter(ef => {
      if (!ef.embedding) return false;
      return this.calculateCosineSimilarity(embedding, ef.embedding) >= this.config.similarityThreshold;
    });
  }

  /**
   * Use LLM to judge ADD vs UPDATE vs DELETE
   */
  private async llmJudgeDedup(fact: ExtractedFact, candidates: ExistingFact[]): Promise<DedupResult> {
    if (!this.llmClient) {
      return this.heuristicDedup(fact, candidates);
    }

    const prompt = DEDUP_JUDGE_PROMPT.format({
      newFact: this.formatFactForJudge(fact),
      existingFacts: candidates.map((c, i) =>
        `[${i + 1}] ID: ${c.id}\n    Type: ${c.type}\n    Importance: ${c.importance}\n    Fact: ${c.factText}`
      ).join('\n\n')
    });

    try {
      const response = await this.llmClient.complete(prompt);
      const parsed = JSON.parse(response);

      return {
        action: this.validateAction(parsed.decision),
        existingFactId: parsed.existingFactId,
        confidence: Math.max(0, Math.min(1, parsed.confidence || 0.8)),
        reasoning: parsed.reasoning || 'LLM judge decision'
      };
    } catch (error) {
      console.error('LLM judge failed, falling back to heuristics:', error);
      return this.heuristicDedup(fact, candidates);
    }
  }

  /**
   * Heuristic-based deduplication (no LLM)
   */
  private heuristicDedup(fact: ExtractedFact, candidates: ExistingFact[]): DedupResult {
    // Check for near-exact match
    for (const candidate of candidates) {
      const similarity = this.textSimilarity(fact.factText, candidate.factText);

      // Very high similarity - likely duplicate
      if (similarity >= 0.95) {
        return {
          action: 'NOOP',
          existingFactId: candidate.id,
          confidence: 0.9,
          reasoning: `Near-exact match with existing fact (similarity: ${similarity.toFixed(2)})`
        };
      }

      // Check for contradiction
      if (this.isLikelyContradiction(fact.factText, candidate.factText)) {
        return {
          action: 'DELETE',
          existingFactId: candidate.id,
          confidence: 0.7,
          reasoning: 'Likely contradiction with existing fact'
        };
      }
    }

    // Check for refinement/update
    const bestMatch = candidates[0];
    if (bestMatch && this.textSimilarity(fact.factText, bestMatch.factText) >= 0.7) {
      return {
        action: 'UPDATE',
        existingFactId: bestMatch.id,
        confidence: 0.7,
        reasoning: 'Likely update/refinement of existing fact'
      };
    }

    // Default to ADD
    return {
      action: 'ADD',
      confidence: 0.8,
      reasoning: 'No sufficient similarity to existing facts'
    };
  }

  /**
   * Text-based deduplication when no vector store is available
   */
  private textBasedDedup(fact: ExtractedFact): DedupResult {
    // Without vector store or LLM, we rely on the fact's own action
    // and do simple text comparison
    return {
      action: fact.action || 'ADD',
      confidence: 0.6,
      reasoning: 'Text-based deduplication (no vector store available)'
    };
  }

  /**
   * Detect if two facts are likely contradictions
   */
  async detectContradiction(
    factA: string,
    factB: string
  ): Promise<{ isContradiction: boolean; type: string; reasoning: string }> {
    // Heuristic contradiction detection
    const heuristicsResult = this.isLikelyContradictionDetailed(factA, factB);

    // If LLM is available, use it for more accurate detection
    if (this.llmClient && heuristicsResult.confidence < 0.8) {
      return this.llmContradictionDetection(factA, factB);
    }

    return heuristicsResult;
  }

  /**
   * Use LLM for contradiction detection
   */
  private async llmContradictionDetection(
    factA: string,
    factB: string
  ): Promise<{ isContradiction: boolean; type: string; reasoning: string }> {
    if (!this.llmClient) {
      return { isContradiction: false, type: 'none', reasoning: 'No LLM available' };
    }

    const prompt = CONTRADICTION_DETECTION_PROMPT.format({
      factA,
      factB
    });

    try {
      const response = await this.llmClient.complete(prompt);
      const parsed = JSON.parse(response);

      return {
        isContradiction: parsed.isContradiction || false,
        type: parsed.contradictionType || 'none',
        reasoning: parsed.reasoning || 'LLM detection'
      };
    } catch (error) {
      console.error('LLM contradiction detection failed:', error);
      return { isContradiction: false, type: 'none', reasoning: 'LLM error' };
    }
  }

  // ============================================================================
  // Utility Methods
  // ============================================================================

  /**
   * Calculate cosine similarity between two vectors
   */
  private calculateCosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length || a.length === 0) return 0;

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    if (normA === 0 || normB === 0) return 0;

    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }

  /**
   * Calculate text similarity using Jaccard similarity on words
   */
  private textSimilarity(a: string, b: string): number {
    const wordsA = new Set(a.toLowerCase().split(/\s+/).filter(w => w.length > 2));
    const wordsB = new Set(b.toLowerCase().split(/\s+/).filter(w => w.length > 2));

    if (wordsA.size === 0 || wordsB.size === 0) return 0;

    const intersection = new Set(Array.from(wordsA).filter(x => wordsB.has(x)));
    const union = new Set([...Array.from(wordsA), ...Array.from(wordsB)]);

    return intersection.size / union.size;
  }

  /**
   * Quick check if two facts are likely contradictions
   */
  private isLikelyContradiction(a: string, b: string): boolean {
    const contradictionPatterns = [
      /\b(?:not|never|don't|doesn't|won't|can't)\b.*\b(?:like|prefer|use|want|need)\b/i,
      /\b(?:hate|dislike|avoid)\b.*\b(?:vs|instead of|rather than)\b/i
    ];

    // Check if one fact negates keywords in the other
    const aLower = a.toLowerCase();
    const bLower = b.toLowerCase();

    for (const pattern of contradictionPatterns) {
      if ((pattern.test(a) && !pattern.test(b)) || (pattern.test(b) && !pattern.test(a))) {
        // Check if they share significant content
        const similarity = this.textSimilarity(a, b);
        if (similarity >= 0.3) {
          return true;
        }
      }
    }

    return false;
  }

  /**
   * Detailed contradiction detection
   */
  private isLikelyContradictionDetailed(
    a: string,
    b: string
  ): { isContradiction: boolean; type: string; reasoning: string; confidence: number } {
    const aLower = a.toLowerCase();
    const bLower = b.toLowerCase();

    // Direct negation patterns
    const negationWords = ['not', 'never', "don't", "doesn't", "won't", "can't", 'no'];
    const hasNegationA = negationWords.some(w => aLower.includes(` ${w} `) || aLower.startsWith(`${w} `));
    const hasNegationB = negationWords.some(w => bLower.includes(` ${w} `) || bLower.startsWith(`${w} `));

    if (hasNegationA !== hasNegationB) {
      const similarity = this.textSimilarity(a, b);
      if (similarity >= 0.4) {
        return {
          isContradiction: true,
          type: 'direct_negation',
          reasoning: 'One fact contains negation while the other does not, with significant content overlap',
          confidence: 0.7
        };
      }
    }

    // Mutually exclusive value patterns
    const valuePatterns = [
      { pattern: /\b(?:uses?|prefers?|likes?)\s+(\w+)/i, type: 'mutually_exclusive' }
    ];

    // Check for temporal replacement keywords
    const temporalKeywords = ['now', 'currently', 'formerly', 'used to', 'previously', 'moved to', 'switched to'];
    const hasTemporalA = temporalKeywords.some(k => aLower.includes(k));
    const hasTemporalB = temporalKeywords.some(k => bLower.includes(k));

    if (hasTemporalA || hasTemporalB) {
      const similarity = this.textSimilarity(a, b);
      if (similarity >= 0.3) {
        return {
          isContradiction: true,
          type: 'temporal_replacement',
          reasoning: 'Temporal keywords suggest state change',
          confidence: 0.6
        };
      }
    }

    return {
      isContradiction: false,
      type: 'none',
      reasoning: 'No contradiction patterns detected',
      confidence: 0.5
    };
  }

  /**
   * Format a fact for the LLM judge
   */
  private formatFactForJudge(fact: ExtractedFact): string {
    const parts = [
      `Text: ${fact.factText}`,
      `Type: ${fact.type}`,
      `Importance: ${fact.importance}`,
      `Confidence: ${fact.confidence}`
    ];

    if (fact.entities.length > 0) {
      parts.push(`Entities: ${fact.entities.map(e => `${e.name} (${e.type})`).join(', ')}`);
    }

    if (fact.relations.length > 0) {
      parts.push(`Relations: ${fact.relations.map(r => `${r.subjectId} -> ${r.predicate} -> ${r.objectId}`).join(', ')}`);
    }

    return parts.join('\n');
  }

  /**
   * Validate and normalize action
   */
  private validateAction(action: unknown): ExtractionAction {
    const validActions: ExtractionAction[] = ['ADD', 'UPDATE', 'DELETE', 'NOOP'];
    if (validActions.includes(action as ExtractionAction)) {
      return action as ExtractionAction;
    }
    return 'ADD';
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Create a deduplicator with default configuration
 */
export function createDeduplicator(
  llmClient?: LLMClient,
  vectorStore?: VectorStoreClient,
  config?: Partial<DedupConfig>
): FactDeduplicator {
  return new FactDeduplicator(config, llmClient, vectorStore);
}

/**
 * Quick check if two fact texts are semantically similar
 */
export async function areFactsSimilar(
  factA: string,
  factB: string,
  vectorStore?: VectorStoreClient
): Promise<boolean> {
  if (!vectorStore) {
    // Fall back to text similarity
    const wordsA = new Set(factA.toLowerCase().split(/\s+/).filter(w => w.length > 2));
    const wordsB = new Set(factB.toLowerCase().split(/\s+/).filter(w => w.length > 2));

    if (wordsA.size === 0 || wordsB.size === 0) return false;

    const intersection = new Set(Array.from(wordsA).filter(x => wordsB.has(x)));
    const union = new Set([...Array.from(wordsA), ...Array.from(wordsB)]);

    return (intersection.size / union.size) >= 0.7;
  }

  const [embA, embB] = await Promise.all([
    vectorStore.getEmbedding(factA),
    vectorStore.getEmbedding(factB)
  ]);

  // Calculate cosine similarity
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < embA.length; i++) {
    dotProduct += embA[i] * embB[i];
    normA += embA[i] * embA[i];
    normB += embB[i] * embB[i];
  }

  if (normA === 0 || normB === 0) return false;

  const similarity = dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  return similarity >= 0.85;
}

/**
 * Merge two facts (for UPDATE operations)
 */
export function mergeFacts(
  existing: ExistingFact,
  update: ExtractedFact
): ExtractedFact {
  // Merge entities (prefer new entities but keep stable IDs)
  const mergedEntities = [...existing.entities || []];
  for (const entity of update.entities) {
    const existingIdx = mergedEntities.findIndex(
      e => e.name.toLowerCase() === entity.name.toLowerCase() && e.type === entity.type
    );
    if (existingIdx === -1) {
      mergedEntities.push(entity);
    }
  }

  // Merge relations (prefer new relations)
  const mergedRelations = [...existing.relations || []];
  for (const relation of update.relations) {
    const exists = mergedRelations.some(
      r => r.subjectId === relation.subjectId &&
           r.predicate === relation.predicate &&
           r.objectId === relation.objectId
    );
    if (!exists) {
      mergedRelations.push(relation);
    }
  }

  return {
    ...update,
    existingFactId: existing.id,
    entities: mergedEntities,
    relations: mergedRelations,
    // Take higher importance
    importance: Math.max(existing.importance, update.importance)
  };
}
