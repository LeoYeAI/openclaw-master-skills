import { BaseImportAdapter } from './base-adapter.js';
import type {
  ImportSource,
  NormalizedFact,
  AdapterParseResult,
  ProgressCallback,
} from './types.js';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

/**
 * MCP Memory Server entity record.
 */
interface MCPEntity {
  type: 'entity';
  name: string;
  entityType: string;
  observations: string[];
}

/**
 * MCP Memory Server relation record.
 */
interface MCPRelation {
  type: 'relation';
  from: string;
  to: string;
  relationType: string;
}

type MCPRecord = MCPEntity | MCPRelation;

/**
 * Entity type mapping to TotalReclaw fact types.
 */
const ENTITY_TYPE_MAP: Record<string, NormalizedFact['type']> = {
  person: 'fact',
  project: 'fact',
  organization: 'fact',
  tool: 'preference',
  technology: 'preference',
  preference: 'preference',
  goal: 'goal',
  event: 'episodic',
  decision: 'decision',
};

export class MCPMemoryAdapter extends BaseImportAdapter {
  readonly source: ImportSource = 'mcp-memory';
  readonly displayName = 'MCP Memory Server';

  async parse(
    input: { content?: string; file_path?: string },
    onProgress?: ProgressCallback,
  ): Promise<AdapterParseResult> {
    const warnings: string[] = [];
    const errors: string[] = [];

    let content: string;

    if (input.content) {
      content = input.content;
    } else if (input.file_path) {
      try {
        const resolvedPath = input.file_path.replace(/^~/, os.homedir());
        content = fs.readFileSync(resolvedPath, 'utf-8');
      } catch (e) {
        errors.push(`Failed to read file: ${e instanceof Error ? e.message : 'Unknown error'}`);
        return { facts: [], warnings, errors };
      }
    } else {
      // Try default MCP memory path
      const defaultPath = path.join(os.homedir(), '.mcp-memory', 'memory.jsonl');
      try {
        content = fs.readFileSync(defaultPath, 'utf-8');
        warnings.push(`Using default MCP memory path: ${defaultPath}`);
      } catch {
        errors.push(
          'No content, file_path, or file at default path (~/.mcp-memory/memory.jsonl). ' +
          'Provide the memory.jsonl content or file path.',
        );
        return { facts: [], warnings, errors };
      }
    }

    // Parse JSONL records
    const records = this.parseJSONL(content, errors);

    if (onProgress) {
      onProgress({
        current: 0,
        total: records.length,
        phase: 'parsing',
        message: `Parsing ${records.length} MCP Memory records...`,
      });
    }

    // Separate entities and relations
    const entities = new Map<string, MCPEntity>();
    const relations: MCPRelation[] = [];

    for (const record of records) {
      if (record.type === 'entity') {
        // Later entities override earlier ones (append-only file)
        entities.set(record.name, record);
      } else if (record.type === 'relation') {
        relations.push(record);
      }
    }

    // Convert entities to facts
    const rawFacts: Partial<NormalizedFact>[] = [];
    let entityIndex = 0;

    for (const [name, entity] of entities) {
      const factType = ENTITY_TYPE_MAP[entity.entityType.toLowerCase()] || 'fact';

      for (const observation of entity.observations) {
        // Prefix observation with entity name for context
        // "Works at Acme Corp" -> "John works at Acme Corp"
        const text = this.contextualizeObservation(name, observation);

        rawFacts.push({
          text,
          type: factType,
          importance: 6,
          source: 'mcp-memory',
          sourceId: `${name}:${entityIndex}`,
          tags: [entity.entityType],
        });
        entityIndex++;
      }

      if (onProgress) {
        onProgress({
          current: rawFacts.length,
          total: rawFacts.length + relations.length,
          phase: 'parsing',
          message: `Parsed ${rawFacts.length} facts from entities...`,
        });
      }
    }

    // Convert relations to facts
    for (const rel of relations) {
      // Only create a fact if both entities exist
      if (!entities.has(rel.from) || !entities.has(rel.to)) {
        warnings.push(`Relation references unknown entity: ${rel.from} -> ${rel.to}`);
        continue;
      }

      const text = `${rel.from} ${this.humanizeRelationType(rel.relationType)} ${rel.to}`;

      rawFacts.push({
        text,
        type: 'fact',
        importance: 5,
        source: 'mcp-memory',
        sourceId: `rel:${rel.from}:${rel.relationType}:${rel.to}`,
        tags: ['relation'],
      });
    }

    const { facts, invalidCount } = this.validateFacts(rawFacts);

    if (invalidCount > 0) {
      warnings.push(`${invalidCount} observations had invalid/empty text and were skipped`);
    }

    return {
      facts,
      warnings,
      errors,
      source_metadata: {
        entities_count: entities.size,
        relations_count: relations.length,
        observations_total: rawFacts.length,
      },
    };
  }

  /**
   * Parse JSONL content into records.
   */
  private parseJSONL(content: string, errors: string[]): MCPRecord[] {
    const records: MCPRecord[] = [];
    const lines = content.split('\n').filter((line) => line.trim().length > 0);

    for (let i = 0; i < lines.length; i++) {
      try {
        const record = JSON.parse(lines[i]);
        if (record.type === 'entity' || record.type === 'relation') {
          records.push(record as MCPRecord);
        } else {
          // Unknown record type — skip silently (future-proofing)
        }
      } catch {
        errors.push(`Line ${i + 1}: Invalid JSON — skipped`);
      }
    }

    return records;
  }

  /**
   * Add entity context to an observation.
   *
   * Heuristic: if the observation already starts with the entity name
   * (case-insensitive) or a pronoun, return as-is. Otherwise prefix.
   *
   * Examples:
   *  - ("John", "Works at Acme Corp") -> "John works at Acme Corp"
   *  - ("John", "John likes TypeScript") -> "John likes TypeScript" (no double prefix)
   *  - ("John", "He prefers React") -> "John prefers React"
   */
  private contextualizeObservation(entityName: string, observation: string): string {
    const obsLower = observation.toLowerCase().trim();
    const nameLower = entityName.toLowerCase();

    // Already starts with the entity name
    if (obsLower.startsWith(nameLower)) {
      return observation.trim();
    }

    // Starts with a pronoun — replace it
    const pronouns = ['he ', 'she ', 'they ', 'it ', 'his ', 'her ', 'their ', 'its '];
    for (const pronoun of pronouns) {
      if (obsLower.startsWith(pronoun)) {
        return entityName + ' ' + observation.trim().slice(pronoun.length);
      }
    }

    // Starts with a verb (lowercase first word) — prefix entity name
    const firstChar = observation.trim()[0];
    if (firstChar && firstChar === firstChar.toLowerCase()) {
      return `${entityName} ${observation.trim()}`;
    }

    // Observation is a standalone sentence — prefix with "About {entity}: "
    return `${entityName}: ${observation.trim()}`;
  }

  /**
   * Convert relation type slug to human-readable text.
   *
   * "works_on" -> "works on"
   * "MEMBER_OF" -> "is a member of"
   */
  private humanizeRelationType(relationType: string): string {
    const slug = relationType.toLowerCase().replace(/_/g, ' ');

    // Common relation type mappings
    const mappings: Record<string, string> = {
      'works on': 'works on',
      'works at': 'works at',
      'member of': 'is a member of',
      'belongs to': 'belongs to',
      'created by': 'was created by',
      'depends on': 'depends on',
      'uses': 'uses',
      'knows': 'knows',
      'related to': 'is related to',
      'part of': 'is part of',
      'friend of': 'is friends with',
      'manages': 'manages',
      'reports to': 'reports to',
      'located in': 'is located in',
      'lives in': 'lives in',
    };

    return mappings[slug] || slug;
  }
}
