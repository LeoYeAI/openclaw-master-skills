import type {
  NormalizedFact,
  ImportSource,
  AdapterParseResult,
  ProgressCallback,
} from './types.js';

/**
 * Abstract base class for import adapters.
 *
 * Each adapter:
 * 1. Fetches or reads source data
 * 2. Parses into NormalizedFact[]
 * 3. Validates each fact
 *
 * The caller (import tool) handles encryption + storage.
 */
export abstract class BaseImportAdapter {
  abstract readonly source: ImportSource;
  abstract readonly displayName: string;

  /**
   * Parse source data into normalized facts.
   *
   * For API sources, this fetches from the API.
   * For file sources, this parses the provided content.
   */
  abstract parse(
    input: { content?: string; api_key?: string; source_user_id?: string; api_url?: string; file_path?: string },
    onProgress?: ProgressCallback,
  ): Promise<AdapterParseResult>;

  /**
   * Validate and clean a single fact.
   * Returns null if the fact should be skipped.
   */
  protected validateFact(fact: Partial<NormalizedFact>): NormalizedFact | null {
    // Text is required and must be non-empty
    if (!fact.text || typeof fact.text !== 'string' || fact.text.trim().length < 3) {
      return null;
    }

    // Truncate to 512 chars
    const text = fact.text.trim().slice(0, 512);

    // Normalize type
    const validTypes = ['fact', 'preference', 'decision', 'episodic', 'goal', 'context', 'summary'] as const;
    const type = validTypes.includes(fact.type as typeof validTypes[number])
      ? (fact.type as NormalizedFact['type'])
      : 'fact';

    // Normalize importance to 1-10
    let importance = fact.importance ?? 5;
    if (importance < 0 || importance > 1) {
      // Already on 1-10 scale
      importance = Math.max(1, Math.min(10, Math.round(importance)));
    } else {
      // 0-1 scale — convert to 1-10
      importance = Math.max(1, Math.round(importance * 10));
    }

    return {
      text,
      type,
      importance,
      source: fact.source ?? this.source,
      sourceId: fact.sourceId,
      sourceTimestamp: fact.sourceTimestamp,
      tags: fact.tags,
    };
  }

  /**
   * Batch-validate an array of partial facts.
   */
  protected validateFacts(
    rawFacts: Partial<NormalizedFact>[],
  ): { facts: NormalizedFact[]; invalidCount: number } {
    const facts: NormalizedFact[] = [];
    let invalidCount = 0;

    for (const raw of rawFacts) {
      const validated = this.validateFact(raw);
      if (validated) {
        facts.push(validated);
      } else {
        invalidCount++;
      }
    }

    return { facts, invalidCount };
  }
}
