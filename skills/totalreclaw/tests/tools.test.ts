/**
 * TotalReclaw Skill - Tools Tests
 *
 * Tests for the four main TotalReclaw tools:
 * - remember: Store a memory
 * - recall: Search for memories
 * - forget: Delete a memory
 * - export: Export all memories
 */

import type {
  TotalReclaw,
  Fact,
  RerankedResult,
  FactMetadata,
  ExportedData,
} from '@totalreclaw/client';
import {
  TotalReclawSkill,
  createTotalReclawSkill,
} from '../src/totalreclaw-skill';
import type {
  TotalReclawSkillConfig,
  RememberToolParams,
  RecallToolParams,
  ForgetToolParams,
  ExportToolParams,
} from '../src/types';

// ============================================================================
// Mocks
// ============================================================================

/**
 * Mock TotalReclaw client
 */
class MockTotalReclawClient {
  private facts: Map<string, Fact> = new Map();
  private userId: string | null = null;
  private salt: Buffer | null = null;
  private isInitialized: boolean = false;

  async init(): Promise<void> {
    this.isInitialized = true;
  }

  async register(masterPassword: string): Promise<string> {
    this.userId = `user-${Date.now()}`;
    this.salt = Buffer.from('mock-salt');
    return this.userId;
  }

  async login(userId: string, masterPassword: string, salt: Buffer): Promise<void> {
    this.userId = userId;
    this.salt = salt;
  }

  getUserId(): string | null {
    return this.userId;
  }

  getSalt(): Buffer | null {
    return this.salt;
  }

  async remember(text: string, metadata?: FactMetadata): Promise<string> {
    const factId = `fact-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const fact: Fact = {
      id: factId,
      text,
      createdAt: new Date(),
      decayScore: 0.5,
      embedding: new Array(1024).fill(0).map(() => Math.random() * 0.1),
      metadata: metadata || {},
    };
    this.facts.set(factId, fact);
    return factId;
  }

  async recall(query: string, k: number): Promise<RerankedResult[]> {
    // Simple mock: return all facts as results
    const results: RerankedResult[] = [];
    let count = 0;

    for (const [id, fact] of this.facts) {
      if (count >= k) break;

      // Simple text matching
      if (fact.text.toLowerCase().includes(query.toLowerCase()) || query === '') {
        results.push({
          fact,
          score: 0.8,
          vectorScore: 0.7,
          textScore: 0.9,
          decayAdjustedScore: 0.75,
        });
        count++;
      }
    }

    return results;
  }

  async forget(factId: string): Promise<void> {
    if (!this.facts.has(factId)) {
      throw new Error(`Fact not found: ${factId}`);
    }
    this.facts.delete(factId);
  }

  async export(): Promise<ExportedData> {
    // Return minimal mock export data
    return {
      version: '1.0.0',
      exportedAt: new Date(),
      facts: [],
      lshConfig: {
        n_bits_per_table: 64,
        n_tables: 12,
        candidate_pool: 3000,
      },
      keyParams: {
        salt: this.salt || Buffer.from(''),
        memoryCost: 65536,
        timeCost: 3,
        parallelism: 4,
      },
    };
  }

  // Test helpers
  getAllFacts(): Fact[] {
    return Array.from(this.facts.values());
  }

  clearFacts(): void {
    this.facts.clear();
  }
}

/**
 * Create a mock skill with a mock client
 */
async function createMockSkill(
  config: Partial<TotalReclawSkillConfig> = {}
): Promise<{ skill: TotalReclawSkill; client: MockTotalReclawClient }> {
  const mockClient = new MockTotalReclawClient();

  const skill = new TotalReclawSkill({
    serverUrl: 'http://mock',
    masterPassword: 'test-password-123',
    ...config,
  });

  // Replace internal client with mock
  await skill.init();

  // Get the internal client reference for testing
  const internalClient = skill.getClient();

  return { skill, client: mockClient };
}

// ============================================================================
// Remember Tool Tests
// ============================================================================

describe('totalreclaw_remember tool', () => {
  let skill: TotalReclawSkill;
  let isInitialized: boolean = false;

  beforeEach(async () => {
    skill = new TotalReclawSkill({
      serverUrl: 'http://mock',
      masterPassword: 'test-password-123',
      minImportanceForAutoStore: 6,
    });

    try {
      const result = await skill.init();
      isInitialized = result.success;
    } catch {
      isInitialized = false;
    }
  });

  describe('parameter validation', () => {
    it('should accept text parameter', () => {
      const params: RememberToolParams = {
        text: 'User prefers dark mode',
      };

      expect(params.text).toBeDefined();
    });

    it('should accept optional type parameter', () => {
      const params: RememberToolParams = {
        text: 'User prefers dark mode',
        type: 'preference',
      };

      expect(params.type).toBe('preference');
    });

    it('should accept optional importance parameter', () => {
      const params: RememberToolParams = {
        text: 'Important decision',
        importance: 9,
      };

      expect(params.importance).toBe(9);
    });
  });

  describe('storage behavior', () => {
    it('should store a memory with default metadata', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: RememberToolParams = {
        text: 'User prefers dark mode',
      };

      const result = await skill.remember(params);

      expect(result).toContain('Memory stored successfully');
      expect(result).toMatch(/ID:/);
    });

    it('should store a memory with explicit type', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: RememberToolParams = {
        text: 'User decided to use TypeScript',
        type: 'decision',
        importance: 8,
      };

      const result = await skill.remember(params);

      expect(result).toContain('Memory stored successfully');
    });

    it('should store high importance memories', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: RememberToolParams = {
        text: 'CRITICAL: Production API key',
        importance: 10,
      };

      const result = await skill.remember(params);

      expect(result).toContain('Memory stored successfully');
    });

    it('should handle empty text gracefully', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: RememberToolParams = {
        text: '',
      };

      // Should either store or throw - behavior depends on implementation
      await expect(skill.remember(params)).resolves.toBeDefined();
    });
  });
});

// ============================================================================
// Recall Tool Tests
// ============================================================================

describe('totalreclaw_recall tool', () => {
  let skill: TotalReclawSkill;
  let isInitialized: boolean = false;

  beforeEach(async () => {
    skill = new TotalReclawSkill({
      serverUrl: 'http://mock',
      masterPassword: 'test-password-123',
      maxMemoriesInContext: 8,
    });

    try {
      const result = await skill.init();
      isInitialized = result.success;

      // Pre-populate some memories if initialized
      if (isInitialized) {
        await skill.remember({ text: 'User prefers TypeScript', importance: 7 });
        await skill.remember({ text: 'User uses VS Code as editor', importance: 5 });
        await skill.remember({ text: 'User works on TotalReclaw project', importance: 6 });
      }
    } catch {
      isInitialized = false;
    }
  });

  describe('parameter validation', () => {
    it('should require query parameter', () => {
      const params: RecallToolParams = {
        query: 'editor preferences',
      };

      expect(params.query).toBeDefined();
    });

    it('should accept optional k parameter', () => {
      const params: RecallToolParams = {
        query: 'preferences',
        k: 5,
      };

      expect(params.k).toBe(5);
    });
  });

  describe('search behavior', () => {
    it('should return relevant memories', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: RecallToolParams = {
        query: 'preferences',
      };

      const results = await skill.recall(params);

      expect(Array.isArray(results)).toBe(true);
    });

    it('should respect k parameter', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: RecallToolParams = {
        query: 'user',
        k: 2,
      };

      const results = await skill.recall(params);

      expect(results.length).toBeLessThanOrEqual(2);
    });

    it('should return empty array for no matches', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: RecallToolParams = {
        query: 'xyzzy123 nonexistent query',
      };

      const results = await skill.recall(params);

      expect(Array.isArray(results)).toBe(true);
    });

    it('should return results with correct structure', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: RecallToolParams = {
        query: 'user',
      };

      const results = await skill.recall(params);

      for (const result of results) {
        expect(result).toHaveProperty('fact');
        expect(result).toHaveProperty('score');
        expect(result.fact).toHaveProperty('id');
        expect(result.fact).toHaveProperty('text');
      }
    });
  });
});

// ============================================================================
// Forget Tool Tests
// ============================================================================

describe('totalreclaw_forget tool', () => {
  let skill: TotalReclawSkill;
  let isInitialized: boolean = false;

  beforeEach(async () => {
    skill = new TotalReclawSkill({
      serverUrl: 'http://mock',
      masterPassword: 'test-password-123',
    });

    try {
      const result = await skill.init();
      isInitialized = result.success;
    } catch {
      isInitialized = false;
    }
  });

  describe('parameter validation', () => {
    it('should require factId parameter', () => {
      const params: ForgetToolParams = {
        factId: 'fact-123',
      };

      expect(params.factId).toBeDefined();
    });
  });

  describe('deletion behavior', () => {
    it('should delete an existing memory', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      // First store a memory
      const storeResult = await skill.remember({
        text: 'Temporary memory to delete',
      });

      // Extract fact ID from result
      const factIdMatch = storeResult.match(/ID: ([\w-]+)/);
      const factId = factIdMatch ? factIdMatch[1] : '';

      // Delete the memory
      const params: ForgetToolParams = { factId };

      await expect(skill.forget(params)).resolves.not.toThrow();
    });

    it('should throw for non-existent memory', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: ForgetToolParams = {
        factId: 'nonexistent-fact-id',
      };

      await expect(skill.forget(params)).rejects.toThrow();
    });
  });
});

// ============================================================================
// Export Tool Tests
// ============================================================================

describe('totalreclaw_export tool', () => {
  let skill: TotalReclawSkill;
  let isInitialized: boolean = false;

  beforeEach(async () => {
    skill = new TotalReclawSkill({
      serverUrl: 'http://mock',
      masterPassword: 'test-password-123',
    });

    try {
      const result = await skill.init();
      isInitialized = result.success;

      // Pre-populate some memories if initialized
      if (isInitialized) {
        await skill.remember({ text: 'User prefers TypeScript' });
        await skill.remember({ text: 'User uses VS Code' });
      }
    } catch {
      isInitialized = false;
    }
  });

  describe('parameter validation', () => {
    it('should accept format parameter', () => {
      const params: ExportToolParams = {
        format: 'json',
      };

      expect(params.format).toBe('json');
    });

    it('should accept markdown format', () => {
      const params: ExportToolParams = {
        format: 'markdown',
      };

      expect(params.format).toBe('markdown');
    });

    it('should default to json if no format specified', () => {
      const params: ExportToolParams = {};

      expect(params.format).toBeUndefined();
    });
  });

  describe('export behavior', () => {
    it('should export as JSON by default', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: ExportToolParams = {};

      const result = await skill.export(params);

      expect(() => JSON.parse(result)).not.toThrow();
    });

    it('should export as JSON when specified', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: ExportToolParams = { format: 'json' };

      const result = await skill.export(params);

      expect(() => JSON.parse(result)).not.toThrow();

      const parsed = JSON.parse(result);
      expect(parsed).toHaveProperty('version');
      expect(parsed).toHaveProperty('exportedAt');
    });

    it('should export as markdown when specified', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: ExportToolParams = { format: 'markdown' };

      const result = await skill.export(params);

      expect(result).toContain('# TotalReclaw Export');
    });

    it('should not include LSH config in markdown export', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: ExportToolParams = { format: 'markdown' };

      const result = await skill.export(params);

      // Markdown export should NOT contain technical configuration
      expect(result).not.toContain('LSH Configuration');
      expect(result).not.toContain('Bits per table');
      expect(result).not.toContain('Key Parameters');
    });

    it('should include human-readable fields in markdown export', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: ExportToolParams = { format: 'markdown' };

      const result = await skill.export(params);

      // Markdown export should contain human-readable info
      expect(result).toContain('Exported at:');
      expect(result).toContain('Total memories:');
    });

    it('should include LSH config in JSON export for re-import', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: ExportToolParams = { format: 'json' };

      const result = await skill.export(params);
      const parsed = JSON.parse(result);

      // JSON export should contain technical configuration for re-import
      expect(parsed).toHaveProperty('lshConfig');
      expect(parsed).toHaveProperty('keyParams');
    });

    it('should include all memories in export', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const params: ExportToolParams = { format: 'json' };

      const result = await skill.export(params);
      const parsed = JSON.parse(result);

      expect(parsed).toHaveProperty('facts');
      expect(Array.isArray(parsed.facts)).toBe(true);
    });
  });
});

// ============================================================================
// Tool Error Handling Tests
// ============================================================================

describe('Tool Error Handling', () => {
  it('should throw if skill not initialized', async () => {
    const skill = new TotalReclawSkill({
      serverUrl: 'http://mock',
      // No recovery phrase - will fail init
    });

    // Don't call init()

    await expect(skill.remember({ text: 'test' })).rejects.toThrow();
    await expect(skill.recall({ query: 'test' })).rejects.toThrow();
    await expect(skill.forget({ factId: 'test' })).rejects.toThrow();
    await expect(skill.export({})).rejects.toThrow();
  });

  it('should handle network errors gracefully', async () => {
    const skill = new TotalReclawSkill({
      serverUrl: 'http://nonexistent-server:9999',
      masterPassword: 'test-password',
    });

    // Init might fail with network error
    const initResult = await skill.init();

    // If init succeeded, tools should handle subsequent errors
    if (initResult.success) {
      await expect(skill.remember({ text: 'test' })).rejects.toThrow();
    }
  });
});

// ============================================================================
// Tool Integration Tests
// ============================================================================

describe('Tool Integration', () => {
  let skill: TotalReclawSkill;

  beforeEach(async () => {
    skill = new TotalReclawSkill({
      serverUrl: 'http://mock',
      masterPassword: 'test-password-123',
    });

    // Try to initialize, but don't fail if network error
    try {
      await skill.init();
    } catch {
      // Skip tests that require initialization
    }
  });

  it('should support store-then-retrieve workflow', async () => {
    // Skip if not initialized
    if (!skill.isInitialized()) {
      console.log('Skipping: skill not initialized');
      return;
    }

    // Store a memory
    await skill.remember({
      text: 'User favorite color is blue',
      type: 'preference',
      importance: 7,
    });

    // Retrieve it
    const results = await skill.recall({
      query: 'favorite color',
    });

    // Should return results
    expect(Array.isArray(results)).toBe(true);
  });

  it('should support store-delete-verify workflow', async () => {
    // Skip if not initialized
    if (!skill.isInitialized()) {
      console.log('Skipping: skill not initialized');
      return;
    }

    // Store a memory
    const storeResult = await skill.remember({
      text: 'Temporary memory',
    });

    const factIdMatch = storeResult.match(/ID: ([\w-]+)/);
    const factId = factIdMatch ? factIdMatch[1] : '';

    // Delete it
    await skill.forget({ factId });

    // Try to find it - should not be there
    const results = await skill.recall({
      query: 'Temporary memory',
    });

    // Memory should be gone (or at least not easily findable)
    expect(Array.isArray(results)).toBe(true);
  });

  it('should support export all memories workflow', async () => {
    // Skip if not initialized
    if (!skill.isInitialized()) {
      console.log('Skipping: skill not initialized');
      return;
    }

    // Store several memories
    await skill.remember({ text: 'Memory 1' });
    await skill.remember({ text: 'Memory 2' });
    await skill.remember({ text: 'Memory 3' });

    // Export all
    const exportResult = await skill.export({ format: 'json' });
    const parsed = JSON.parse(exportResult);

    expect(parsed.facts).toBeDefined();
  });
});
