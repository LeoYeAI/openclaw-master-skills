import { BaseImportAdapter } from './base-adapter.js';
import type {
  ImportSource,
  NormalizedFact,
  AdapterParseResult,
  ProgressCallback,
} from './types.js';

/**
 * Mem0 memory structure from their API/export.
 */
interface Mem0Memory {
  id: string;
  memory: string;
  hash?: string;
  metadata?: {
    category?: string;
    created_at?: string;
    updated_at?: string;
  };
  user_id?: string;
  agent_id?: string;
  categories?: string[];
}

interface Mem0ApiResponse {
  results: Mem0Memory[];
  next?: string; // pagination cursor
  total?: number;
}

interface Mem0ExportFile {
  export_date?: string;
  user_id?: string;
  memories: Mem0Memory[];
}

/**
 * Category mapping from Mem0 categories to TotalReclaw types.
 */
const CATEGORY_MAP: Record<string, NormalizedFact['type']> = {
  preference: 'preference',
  preferences: 'preference',
  like: 'preference',
  dislike: 'preference',
  fact: 'fact',
  personal: 'fact',
  biographical: 'fact',
  decision: 'decision',
  goal: 'goal',
  objective: 'goal',
  experience: 'episodic',
  event: 'episodic',
  memory: 'episodic',
};

export class Mem0Adapter extends BaseImportAdapter {
  readonly source: ImportSource = 'mem0';
  readonly displayName = 'Mem0';

  async parse(
    input: { content?: string; api_key?: string; source_user_id?: string; api_url?: string },
    onProgress?: ProgressCallback,
  ): Promise<AdapterParseResult> {
    const warnings: string[] = [];
    const errors: string[] = [];

    let memories: Mem0Memory[];

    if (input.content) {
      // Parse from pasted content or export file
      memories = this.parseExportContent(input.content, errors);
    } else if (input.api_key) {
      // Fetch from Mem0 API
      memories = await this.fetchFromApi(
        input.api_key,
        input.source_user_id,
        input.api_url,
        onProgress,
        errors,
      );
    } else {
      errors.push('Mem0 import requires either content (export file) or api_key');
      return { facts: [], warnings, errors };
    }

    if (onProgress) {
      onProgress({
        current: 0,
        total: memories.length,
        phase: 'parsing',
        message: `Parsing ${memories.length} Mem0 memories...`,
      });
    }

    // Convert Mem0 memories to NormalizedFacts
    const rawFacts: Partial<NormalizedFact>[] = memories.map((mem) => ({
      text: mem.memory,
      type: this.mapCategory(mem.categories, mem.metadata?.category),
      importance: 6, // Mem0 doesn't provide importance — default to 6 (above threshold)
      source: 'mem0' as ImportSource,
      sourceId: mem.id,
      sourceTimestamp: mem.metadata?.updated_at || mem.metadata?.created_at,
      tags: mem.categories || [],
    }));

    const { facts, invalidCount } = this.validateFacts(rawFacts);

    if (invalidCount > 0) {
      warnings.push(`${invalidCount} memories had invalid/empty text and were skipped`);
    }

    return { facts, warnings, errors, source_metadata: { total_from_source: memories.length } };
  }

  /**
   * Parse Mem0 export file or pasted JSON.
   */
  private parseExportContent(content: string, errors: string[]): Mem0Memory[] {
    try {
      const data = JSON.parse(content.trim());

      // Handle export file format: { memories: [...] }
      if (data.memories && Array.isArray(data.memories)) {
        return data.memories;
      }

      // Handle API response format: { results: [...] }
      if (data.results && Array.isArray(data.results)) {
        return data.results;
      }

      // Handle bare array
      if (Array.isArray(data)) {
        return data;
      }

      errors.push('Unrecognized Mem0 format. Expected { memories: [...] }, { results: [...] }, or bare array.');
      return [];
    } catch (e) {
      errors.push(`Failed to parse Mem0 JSON: ${e instanceof Error ? e.message : 'Unknown error'}`);
      return [];
    }
  }

  /**
   * Fetch all memories from Mem0 API with pagination.
   */
  private async fetchFromApi(
    apiKey: string,
    sourceUserId?: string,
    apiUrl?: string,
    onProgress?: ProgressCallback,
    errors?: string[],
  ): Promise<Mem0Memory[]> {
    const baseUrl = apiUrl || 'https://api.mem0.ai';
    const allMemories: Mem0Memory[] = [];
    let page = 1;
    const pageSize = 100;
    let hasMore = true;

    while (hasMore) {
      try {
        const url = new URL(`${baseUrl}/v1/memories/`);
        url.searchParams.set('page', String(page));
        url.searchParams.set('page_size', String(pageSize));
        if (sourceUserId) {
          url.searchParams.set('user_id', sourceUserId);
        }

        const response = await fetch(url.toString(), {
          headers: {
            Authorization: `Token ${apiKey}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          const errorText = await response.text();
          errors?.push(`Mem0 API error (${response.status}): ${errorText.slice(0, 200)}`);
          break;
        }

        const data: Mem0ApiResponse = await response.json();
        const memories = data.results || [];
        allMemories.push(...memories);

        if (onProgress) {
          onProgress({
            current: allMemories.length,
            total: data.total || allMemories.length,
            phase: 'fetching',
            message: `Fetched ${allMemories.length} memories from Mem0...`,
          });
        }

        hasMore = memories.length === pageSize;
        page++;

        // Safety limit: 10,000 memories max
        if (allMemories.length >= 10_000) {
          errors?.push('Reached 10,000 memory limit. Some memories may not have been fetched.');
          break;
        }
      } catch (e) {
        errors?.push(`Mem0 API fetch error: ${e instanceof Error ? e.message : 'Unknown error'}`);
        break;
      }
    }

    return allMemories;
  }

  /**
   * Map Mem0 category to TotalReclaw fact type.
   */
  private mapCategory(
    categories?: string[],
    singleCategory?: string,
  ): NormalizedFact['type'] {
    const allCategories = [
      ...(categories || []),
      ...(singleCategory ? [singleCategory] : []),
    ];

    for (const cat of allCategories) {
      const mapped = CATEGORY_MAP[cat.toLowerCase()];
      if (mapped) return mapped;
    }

    return 'fact'; // default
  }
}
