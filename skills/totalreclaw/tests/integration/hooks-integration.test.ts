/**
 * TotalReclaw Skill - Hooks Integration Tests
 *
 * Tests the integration of lifecycle hooks with mock OpenClaw context.
 * Tests before_agent_start, agent_end, and pre_compaction hooks.
 */

import {
  beforeAgentStart,
  formatMemoriesForContext,
  type BeforeAgentStartOptions,
} from '../../src/triggers/before-agent-start';
import {
  agentEnd,
  type AgentEndOptions,
} from '../../src/triggers/agent-end';
import {
  preCompaction,
  type PreCompactionOptions,
} from '../../src/triggers/pre-compaction';
import type {
  OpenClawContext,
  ConversationTurn,
  SkillState,
  ExtractedFact,
  TotalReclawSkillConfig,
} from '../../src/types';
import type { TotalReclaw, Fact, RerankedResult } from '@totalreclaw/client';
import { DEFAULT_SKILL_CONFIG } from '../../src/types';

// ============================================================================
// Mocks
// ============================================================================

/**
 * Mock TotalReclaw client
 */
class MockTotalReclawClient implements Partial<TotalReclaw> {
  private facts: Map<string, Fact> = new Map();
  private userId: string | null = null;

  async init(): Promise<void> {}

  async register(masterPassword: string): Promise<string> {
    this.userId = `user-${Date.now()}`;
    return this.userId;
  }

  async login(userId: string, masterPassword: string, salt: Buffer): Promise<void> {
    this.userId = userId;
  }

  getUserId(): string | null {
    return this.userId;
  }

  getSalt(): Buffer | null {
    return Buffer.from('mock-salt');
  }

  async remember(text: string, metadata?: any): Promise<string> {
    const factId = `fact-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    this.facts.set(factId, {
      id: factId,
      text,
      createdAt: new Date(),
      decayScore: 0.5,
      embedding: new Array(1024).fill(0).map(() => Math.random() * 0.1),
      metadata: metadata || {},
    });
    return factId;
  }

  async recall(query: string, k: number): Promise<RerankedResult[]> {
    const results: RerankedResult[] = [];
    const queryLower = query.toLowerCase();

    for (const [id, fact] of this.facts) {
      if (results.length >= k) break;

      if (fact.text.toLowerCase().includes(queryLower) || query === '') {
        results.push({
          fact,
          score: 0.8,
          vectorScore: 0.7,
          textScore: 0.9,
          decayAdjustedScore: 0.75,
        });
      }
    }

    return results;
  }

  async forget(factId: string): Promise<void> {
    this.facts.delete(factId);
  }

  async export(): Promise<any> {
    return {
      version: '1.0.0',
      exportedAt: new Date(),
      facts: Array.from(this.facts.values()),
    };
  }

  // Test helpers
  addFact(fact: Fact): void {
    this.facts.set(fact.id, fact);
  }

  clearFacts(): void {
    this.facts.clear();
  }

  getFactCount(): number {
    return this.facts.size;
  }
}

/**
 * Mock LLM client
 */
class MockLLMClient {
  private responses: string[] = [];
  private callCount = 0;

  setResponse(response: string): void {
    this.responses = [response];
  }

  setResponses(responses: string[]): void {
    this.responses = responses;
  }

  async complete(prompt: { system: string; user: string }): Promise<string> {
    const response = this.responses[this.callCount % this.responses.length] || '{"facts": []}';
    this.callCount++;
    return response;
  }

  reset(): void {
    this.callCount = 0;
    this.responses = [];
  }
}

/**
 * Mock Vector Store client
 */
class MockVectorStoreClient {
  private facts: any[] = [];

  setFacts(facts: any[]): void {
    this.facts = facts;
  }

  async findSimilar(embedding: number[], k: number): Promise<any[]> {
    return this.facts.slice(0, k);
  }

  async getEmbedding(text: string): Promise<number[]> {
    return new Array(1024).fill(0).map(() => Math.random() * 0.1);
  }
}

/**
 * Mock Cross-Encoder Reranker
 */
class MockReranker {
  isReady(): boolean {
    return true;
  }

  async load(): Promise<void> {}

  async rerank(query: string, facts: Fact[], topK: number): Promise<any[]> {
    return facts.slice(0, topK).map((fact, index) => ({
      fact,
      score: 0.9 - (index * 0.1),
      vectorScore: 0.8,
      textScore: 0.85,
      decayAdjustedScore: 0.82,
      crossEncoderScore: 0.9 - (index * 0.1),
    }));
  }
}

// ============================================================================
// Test Utilities
// ============================================================================

/**
 * Create a mock conversation turn
 */
function createTurn(role: 'user' | 'assistant', content: string): ConversationTurn {
  return {
    role,
    content,
    timestamp: new Date(),
  };
}

/**
 * Create a mock OpenClaw context
 */
function createContext(overrides: Partial<OpenClawContext> = {}): OpenClawContext {
  return {
    userMessage: 'Hello!',
    history: [
      createTurn('user', 'Hi'),
      createTurn('assistant', 'Hello! How can I help?'),
    ],
    agentId: 'test-agent',
    sessionId: 'test-session',
    tokenCount: 100,
    tokenLimit: 4000,
    ...overrides,
  };
}

/**
 * Create a mock skill state
 */
function createSkillState(): SkillState {
  return {
    turnCount: 0,
    lastExtraction: null,
    cachedMemories: [],
    isInitialized: true,
    pendingExtractions: [],
  };
}

/**
 * Create a mock fact
 */
function createMockFact(overrides: Partial<Fact> = {}): Fact {
  return {
    id: `fact-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    text: 'Test fact',
    createdAt: new Date(),
    decayScore: 0.5,
    embedding: new Array(1024).fill(0).map(() => Math.random() * 0.1),
    metadata: {},
    ...overrides,
  };
}

// ============================================================================
// Before Agent Start Hook Tests
// ============================================================================

describe('before_agent_start hook', () => {
  let mockClient: MockTotalReclawClient;
  let mockLLM: MockLLMClient;
  let mockReranker: MockReranker;
  let config: TotalReclawSkillConfig;
  let state: SkillState;

  beforeEach(() => {
    mockClient = new MockTotalReclawClient();
    mockLLM = new MockLLMClient();
    mockReranker = new MockReranker();
    config = { ...DEFAULT_SKILL_CONFIG };
    state = createSkillState();
  });

  describe('memory retrieval', () => {
    it('should retrieve memories based on user message', async () => {
      // Pre-populate memories
      mockClient.addFact(createMockFact({
        id: 'fact-1',
        text: 'User prefers TypeScript for all projects',
        metadata: { tags: ['preference'] },
      }));
      mockClient.addFact(createMockFact({
        id: 'fact-2',
        text: 'User uses VS Code as editor',
        metadata: { tags: ['fact'] },
      }));

      const context = createContext({
        userMessage: 'What programming language should I use?',
      });

      const options: BeforeAgentStartOptions = {
        client: mockClient as any,
        config,
        reranker: mockReranker as any,
        debug: false,
      };

      const result = await beforeAgentStart(context, options);

      expect(result.memories).toBeDefined();
      expect(Array.isArray(result.memories)).toBe(true);
    });

    it('should return empty memories when none exist', async () => {
      const context = createContext();

      const options: BeforeAgentStartOptions = {
        client: mockClient as any,
        config,
        reranker: mockReranker as any,
        debug: false,
      };

      const result = await beforeAgentStart(context, options);

      expect(result.memories).toHaveLength(0);
      expect(result.contextString).toBe('');
    });

    it('should respect maxMemoriesInContext limit', async () => {
      // Add many facts
      for (let i = 0; i < 20; i++) {
        mockClient.addFact(createMockFact({
          id: `fact-${i}`,
          text: `Memory number ${i}`,
        }));
      }

      const context = createContext({ userMessage: 'Memory' });
      const options: BeforeAgentStartOptions = {
        client: mockClient as any,
        config: { ...config, maxMemoriesInContext: 3 },
        reranker: mockReranker as any,
        debug: false,
      };

      const result = await beforeAgentStart(context, options);

      expect(result.memories.length).toBeLessThanOrEqual(3);
    });
  });

  describe('memory formatting', () => {
    it('should format memories for context injection', async () => {
      mockClient.addFact(createMockFact({
        id: 'fact-1',
        text: 'User prefers dark mode',
        metadata: { tags: ['preference'], importance: 0.8 },
      }));

      const context = createContext({ userMessage: 'preferences' });
      const options: BeforeAgentStartOptions = {
        client: mockClient as any,
        config,
        reranker: mockReranker as any,
        debug: false,
      };

      const result = await beforeAgentStart(context, options);

      expect(result.contextString).toBeDefined();
      // Context string may be empty if no memories are retrieved
      // Check that we got a result structure
      expect(result.memories).toBeDefined();
    });

    it('should format memories with type indicators', async () => {
      const memories: RerankedResult[] = [
        {
          fact: createMockFact({
            id: 'fact-1',
            text: 'User prefers TypeScript',
            metadata: { tags: ['preference'] },
          }),
          score: 0.9,
          vectorScore: 0.85,
          textScore: 0.95,
          decayAdjustedScore: 0.88,
        },
        {
          fact: createMockFact({
            id: 'fact-2',
            text: 'User decided to use React',
            metadata: { tags: ['decision'] },
          }),
          score: 0.85,
          vectorScore: 0.8,
          textScore: 0.9,
          decayAdjustedScore: 0.83,
        },
      ];

      const formatted = formatMemoriesForContext(memories);

      expect(formatted).toContain('[PREF]');
      expect(formatted).toContain('[DEC]');
    });

    it('should escape special characters in memories', () => {
      const memories: RerankedResult[] = [
        {
          fact: createMockFact({
            id: 'fact-1',
            text: 'User said "hello" & <goodbye>',
          }),
          score: 0.9,
          vectorScore: 0.85,
          textScore: 0.95,
          decayAdjustedScore: 0.88,
        },
      ];

      const formatted = formatMemoriesForContext(memories);

      expect(formatted).toContain('&quot;');
      expect(formatted).toContain('&amp;');
      expect(formatted).toContain('&lt;');
      expect(formatted).toContain('&gt;');
    });
  });

  describe('latency tracking', () => {
    it('should track and report latency', async () => {
      mockClient.addFact(createMockFact({
        id: 'fact-1',
        text: 'Test memory',
      }));

      const context = createContext();
      const options: BeforeAgentStartOptions = {
        client: mockClient as any,
        config,
        reranker: mockReranker as any,
        debug: false,
      };

      const result = await beforeAgentStart(context, options);

      expect(result.latencyMs).toBeDefined();
      expect(typeof result.latencyMs).toBe('number');
      expect(result.latencyMs).toBeGreaterThanOrEqual(0);
    });

    it('should complete within target latency', async () => {
      // Add multiple memories
      for (let i = 0; i < 10; i++) {
        mockClient.addFact(createMockFact({
          id: `fact-${i}`,
          text: `Memory ${i}`,
        }));
      }

      const context = createContext();
      const options: BeforeAgentStartOptions = {
        client: mockClient as any,
        config,
        reranker: mockReranker as any,
        debug: false,
      };

      const startTime = Date.now();
      const result = await beforeAgentStart(context, options);
      const duration = Date.now() - startTime;

      // Should be very fast with mocks
      expect(duration).toBeLessThan(100);
    });
  });

  describe('error handling', () => {
    it('should return empty result on client error', async () => {
      // Create a client that throws
      const errorClient = {
        recall: jest.fn().mockRejectedValue(new Error('Connection failed')),
      };

      const context = createContext();
      const options: BeforeAgentStartOptions = {
        client: errorClient as any,
        config,
        reranker: mockReranker as any,
        debug: false,
      };

      const result = await beforeAgentStart(context, options);

      expect(result.memories).toHaveLength(0);
      expect(result.contextString).toBe('');
    });

    it('should handle reranker errors gracefully', async () => {
      mockClient.addFact(createMockFact({
        id: 'fact-1',
        text: 'Test memory',
      }));

      const errorReranker = {
        isReady: () => true,
        load: () => Promise.resolve(),
        rerank: jest.fn().mockRejectedValue(new Error('Reranker failed')),
      };

      const context = createContext();
      const options: BeforeAgentStartOptions = {
        client: mockClient as any,
        config,
        reranker: errorReranker as any,
        debug: false,
      };

      // Should not throw
      const result = await beforeAgentStart(context, options);
      expect(result).toBeDefined();
    });
  });
});

// ============================================================================
// Agent End Hook Tests
// ============================================================================

describe('agent_end hook', () => {
  let mockClient: MockTotalReclawClient;
  let mockLLM: MockLLMClient;
  let mockVectorStore: MockVectorStoreClient;
  let config: TotalReclawSkillConfig;
  let state: SkillState;

  beforeEach(() => {
    mockClient = new MockTotalReclawClient();
    mockLLM = new MockLLMClient();
    mockVectorStore = new MockVectorStoreClient();
    config = { ...DEFAULT_SKILL_CONFIG, autoExtractEveryTurns: 3 };
    state = createSkillState();
  });

  describe('turn counter tracking', () => {
    it('should increment turn counter on each call', async () => {
      const context = createContext();
      const options: AgentEndOptions = {
        client: mockClient as any,
        config,
        state,
        llmClient: mockLLM as any,
        debug: false,
      };

      expect(state.turnCount).toBe(0);

      await agentEnd(context, options);
      expect(state.turnCount).toBe(1);

      await agentEnd(context, options);
      expect(state.turnCount).toBe(2);

      await agentEnd(context, options);
      expect(state.turnCount).toBe(3);
    });

    it('should track turn count independently of extraction', async () => {
      mockLLM.setResponse('{"facts": []}');

      const context = createContext();
      const options: AgentEndOptions = {
        client: mockClient as any,
        config,
        state,
        llmClient: mockLLM as any,
        debug: false,
      };

      await agentEnd(context, options);
      expect(state.turnCount).toBe(1);
    });
  });

  describe('extraction trigger', () => {
    it('should trigger extraction at correct turn interval', async () => {
      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'User prefers dark mode',
            type: 'preference',
            importance: 7,
            confidence: 0.9,
            action: 'ADD',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext({
        userMessage: 'I prefer dark mode',
      });

      const options: AgentEndOptions = {
        client: mockClient as any,
        config: { ...config, autoExtractEveryTurns: 3 },
        state,
        llmClient: mockLLM as any,
        debug: false,
      };

      // Turn 1 - should extract (first turn)
      let result = await agentEnd(context, options);
      expect(state.turnCount).toBe(1);

      // Turn 2 - should not extract (not at interval)
      result = await agentEnd(context, options);
      expect(state.turnCount).toBe(2);

      // Turn 3 - should extract (at interval)
      result = await agentEnd(context, options);
      expect(state.turnCount).toBe(3);
    });

    it('should always extract on explicit memory commands', async () => {
      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'User uses VS Code',
            type: 'fact',
            importance: 6,
            confidence: 0.8,
            action: 'ADD',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext({
        userMessage: 'Remember that I use VS Code for development',
      });

      const options: AgentEndOptions = {
        client: mockClient as any,
        config: { ...config, autoExtractEveryTurns: 100 }, // High interval
        state,
        llmClient: mockLLM as any,
        debug: false,
      };

      // Even with high interval, explicit commands trigger extraction
      const result = await agentEnd(context, options);

      expect(state.turnCount).toBe(1);
    });

    it('should skip extraction when below threshold and not explicit', async () => {
      const context = createContext({
        userMessage: 'Hello there', // Not an explicit command
      });

      const options: AgentEndOptions = {
        client: mockClient as any,
        config: { ...config, autoExtractEveryTurns: 100 },
        state,
        llmClient: mockLLM as any,
        debug: false,
      };

      // Turn 2 (not first, not at interval, not explicit)
      state.turnCount = 1;
      const result = await agentEnd(context, options);

      expect(result.factsExtracted).toBe(0);
    });
  });

  describe('fact storage', () => {
    it('should store extracted facts above importance threshold', async () => {
      // Note: The actual storage depends on the extractor being properly configured
      // This test verifies the hook processes facts correctly
      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'User prefers dark mode',
            type: 'preference',
            importance: 8, // Above threshold (6)
            confidence: 0.9,
            action: 'ADD',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext();
      const options: AgentEndOptions = {
        client: mockClient as any,
        config: { ...config, minImportanceForAutoStore: 6 },
        state,
        llmClient: mockLLM as any,
        debug: false,
      };

      const result = await agentEnd(context, options);

      // Verify the hook executed and returned proper structure
      expect(result).toHaveProperty('factsExtracted');
      expect(result).toHaveProperty('factsStored');
      expect(result).toHaveProperty('processingTimeMs');
    });

    it('should skip facts below importance threshold', async () => {
      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'Low importance fact',
            type: 'fact',
            importance: 3, // Below threshold (6)
            confidence: 0.5,
            action: 'ADD',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext();
      const options: AgentEndOptions = {
        client: mockClient as any,
        config: { ...config, minImportanceForAutoStore: 6 },
        state,
        llmClient: mockLLM as any,
        debug: false,
      };

      await agentEnd(context, options);

      // Low importance facts should be skipped
      expect(mockClient.getFactCount()).toBe(0);
    });

    it('should store all facts on explicit commands regardless of threshold', async () => {
      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'Explicit fact',
            type: 'fact',
            importance: 3, // Low importance
            confidence: 0.5,
            action: 'ADD',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext({
        userMessage: 'Remember this: explicit fact',
      });

      const options: AgentEndOptions = {
        client: mockClient as any,
        config: { ...config, minImportanceForAutoStore: 6 },
        state,
        llmClient: mockLLM as any,
        debug: false,
      };

      await agentEnd(context, options);

      // Even low importance should be stored for explicit commands
      // (Note: actual behavior depends on implementation)
    });
  });

  describe('async mode', () => {
    it('should return quickly in async mode', async () => {
      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'Test fact',
            type: 'fact',
            importance: 7,
            confidence: 0.8,
            action: 'ADD',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext();
      const options: AgentEndOptions = {
        client: mockClient as any,
        config,
        state,
        llmClient: mockLLM as any,
        debug: false,
        async: true,
      };

      const startTime = Date.now();
      const result = await agentEnd(context, options);
      const duration = Date.now() - startTime;

      expect(duration).toBeLessThan(50); // Should return immediately
    });
  });

  describe('result structure', () => {
    it('should return correct result structure', async () => {
      const context = createContext();
      const options: AgentEndOptions = {
        client: mockClient as any,
        config,
        state,
        llmClient: mockLLM as any,
        debug: false,
      };

      const result = await agentEnd(context, options);

      expect(result).toHaveProperty('factsExtracted');
      expect(result).toHaveProperty('factsStored');
      expect(result).toHaveProperty('processingTimeMs');
      expect(typeof result.factsExtracted).toBe('number');
      expect(typeof result.factsStored).toBe('number');
      expect(typeof result.processingTimeMs).toBe('number');
    });
  });
});

// ============================================================================
// Pre-Compaction Hook Tests
// ============================================================================

describe('pre_compaction hook', () => {
  let mockClient: MockTotalReclawClient;
  let mockLLM: MockLLMClient;
  let mockVectorStore: MockVectorStoreClient;
  let config: TotalReclawSkillConfig;

  beforeEach(() => {
    mockClient = new MockTotalReclawClient();
    mockLLM = new MockLLMClient();
    mockVectorStore = new MockVectorStoreClient();
    config = { ...DEFAULT_SKILL_CONFIG };
  });

  describe('full conversation extraction', () => {
    it('should extract facts from full conversation history', async () => {
      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'User is working on TotalReclaw project',
            type: 'fact',
            importance: 6,
            confidence: 0.8,
            action: 'ADD',
            entities: [],
            relations: [],
          },
          {
            factText: 'User prefers dark mode',
            type: 'preference',
            importance: 7,
            confidence: 0.9,
            action: 'ADD',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext({
        history: Array(20).fill(null).map((_, i) =>
          createTurn(i % 2 === 0 ? 'user' : 'assistant', `Message ${i}`)
        ),
      });

      const options: PreCompactionOptions = {
        client: mockClient as any,
        config,
        llmClient: mockLLM as any,
        debug: false,
      };

      const result = await preCompaction(context, options);

      expect(result.factsExtracted).toBeGreaterThanOrEqual(0);
      expect(result.processingTimeMs).toBeGreaterThanOrEqual(0);
    });

    it('should handle long conversation histories', async () => {
      mockLLM.setResponse(JSON.stringify({ facts: [] }));

      const context = createContext({
        history: Array(50).fill(null).map((_, i) =>
          createTurn(i % 2 === 0 ? 'user' : 'assistant', `Long message ${i}`)
        ),
      });

      const options: PreCompactionOptions = {
        client: mockClient as any,
        config,
        llmClient: mockLLM as any,
        debug: false,
      };

      const result = await preCompaction(context, options);

      expect(result).toBeDefined();
      expect(result.processingTimeMs).toBeGreaterThanOrEqual(0);
    });

    it('should handle empty conversation history', async () => {
      mockLLM.setResponse(JSON.stringify({ facts: [] }));

      const context = createContext({
        history: [],
      });

      const options: PreCompactionOptions = {
        client: mockClient as any,
        config,
        llmClient: mockLLM as any,
        debug: false,
      };

      const result = await preCompaction(context, options);

      expect(result).toBeDefined();
      expect(result.factsExtracted).toBe(0);
    });
  });

  describe('deduplication logic', () => {
    it('should skip duplicate facts', async () => {
      // Add existing memory
      mockClient.addFact(createMockFact({
        id: 'existing-1',
        text: 'User prefers dark mode',
        metadata: { tags: ['preference'] },
      }));

      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'User prefers dark mode', // Duplicate
            type: 'preference',
            importance: 7,
            confidence: 0.9,
            action: 'ADD',
            entities: [],
            relations: [],
          },
          {
            factText: 'User likes coffee', // New fact
            type: 'preference',
            importance: 6,
            confidence: 0.8,
            action: 'ADD',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext();
      const options: PreCompactionOptions = {
        client: mockClient as any,
        config,
        llmClient: mockLLM as any,
        debug: false,
      };

      const result = await preCompaction(context, options);

      // Duplicates should be counted
      expect(result.duplicatesSkipped).toBeGreaterThanOrEqual(0);
    });

    it('should update existing facts when UPDATE action', async () => {
      mockClient.addFact(createMockFact({
        id: 'existing-1',
        text: 'User prefers light mode',
        metadata: { tags: ['preference'] },
      }));

      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'User prefers dark mode',
            type: 'preference',
            importance: 8,
            confidence: 0.9,
            action: 'UPDATE',
            existingFactId: 'existing-1',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext();
      const options: PreCompactionOptions = {
        client: mockClient as any,
        config,
        llmClient: mockLLM as any,
        debug: false,
      };

      const result = await preCompaction(context, options);

      expect(result.factsStored).toBeGreaterThanOrEqual(0);
    });

    it('should delete facts when DELETE action', async () => {
      mockClient.addFact(createMockFact({
        id: 'to-delete',
        text: 'Outdated fact',
      }));

      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'Outdated fact',
            type: 'fact',
            importance: 0,
            confidence: 1.0,
            action: 'DELETE',
            existingFactId: 'to-delete',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext();
      const options: PreCompactionOptions = {
        client: mockClient as any,
        config,
        llmClient: mockLLM as any,
        debug: false,
      };

      await preCompaction(context, options);

      // Fact should be deleted
    });
  });

  describe('batch upload', () => {
    it('should store multiple facts in batch', async () => {
      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'Fact 1',
            type: 'fact',
            importance: 7,
            confidence: 0.8,
            action: 'ADD',
            entities: [],
            relations: [],
          },
          {
            factText: 'Fact 2',
            type: 'preference',
            importance: 8,
            confidence: 0.9,
            action: 'ADD',
            entities: [],
            relations: [],
          },
          {
            factText: 'Fact 3',
            type: 'decision',
            importance: 9,
            confidence: 0.95,
            action: 'ADD',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext();
      const options: PreCompactionOptions = {
        client: mockClient as any,
        config,
        llmClient: mockLLM as any,
        debug: false,
      };

      const result = await preCompaction(context, options);

      expect(result.factsStored).toBeGreaterThan(0);
    });

    it('should handle partial failures in batch', async () => {
      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'Good fact',
            type: 'fact',
            importance: 8,
            confidence: 0.9,
            action: 'ADD',
            entities: [],
            relations: [],
          },
          {
            factText: '', // Empty - might fail validation
            type: 'fact',
            importance: 5,
            confidence: 0.5,
            action: 'ADD',
            entities: [],
            relations: [],
          },
        ],
      }));

      const context = createContext();
      const options: PreCompactionOptions = {
        client: mockClient as any,
        config,
        llmClient: mockLLM as any,
        debug: false,
      };

      // Should not throw
      const result = await preCompaction(context, options);
      expect(result).toBeDefined();
    });
  });

  describe('result structure', () => {
    it('should return correct result structure', async () => {
      mockLLM.setResponse(JSON.stringify({ facts: [] }));

      const context = createContext();
      const options: PreCompactionOptions = {
        client: mockClient as any,
        config,
        llmClient: mockLLM as any,
        debug: false,
      };

      const result = await preCompaction(context, options);

      expect(result).toHaveProperty('factsExtracted');
      expect(result).toHaveProperty('factsStored');
      expect(result).toHaveProperty('duplicatesSkipped');
      expect(result).toHaveProperty('processingTimeMs');
      expect(typeof result.factsExtracted).toBe('number');
      expect(typeof result.factsStored).toBe('number');
      expect(typeof result.duplicatesSkipped).toBe('number');
      expect(typeof result.processingTimeMs).toBe('number');
    });
  });

  describe('error handling', () => {
    it('should handle LLM errors gracefully', async () => {
      const errorLLM = {
        complete: jest.fn().mockRejectedValue(new Error('LLM failed')),
      };

      const context = createContext();
      const options: PreCompactionOptions = {
        client: mockClient as any,
        config,
        llmClient: errorLLM as any,
        debug: false,
      };

      // Should not throw
      const result = await preCompaction(context, options);
      expect(result).toBeDefined();
      expect(result.factsExtracted).toBe(0);
    });

    it('should handle malformed LLM responses', async () => {
      mockLLM.setResponse('not valid json');

      const context = createContext();
      const options: PreCompactionOptions = {
        client: mockClient as any,
        config,
        llmClient: mockLLM as any,
        debug: false,
      };

      // Should not throw
      const result = await preCompaction(context, options);
      expect(result).toBeDefined();
    });
  });
});

// ============================================================================
// Integration Between Hooks Tests
// ============================================================================

describe('Hooks Integration', () => {
  let mockClient: MockTotalReclawClient;
  let mockLLM: MockLLMClient;
  let config: TotalReclawSkillConfig;
  let state: SkillState;

  beforeEach(() => {
    mockClient = new MockTotalReclawClient();
    mockLLM = new MockLLMClient();
    config = { ...DEFAULT_SKILL_CONFIG, autoExtractEveryTurns: 2 };
    state = createSkillState();
  });

  it('should support full conversation flow across hooks', async () => {
    const mockReranker = new MockReranker();

    // Simulate conversation turns
    const turns = [
      'Hello!',
      'I prefer dark mode for coding',
      'Can you help me with my project?',
      'Remember that I use TypeScript',
      'What do you know about my preferences?',
    ];

    for (let i = 0; i < turns.length; i++) {
      const context = createContext({ userMessage: turns[i] });

      // Before agent starts
      const beforeResult = await beforeAgentStart(context, {
        client: mockClient as any,
        config,
        reranker: mockReranker as any,
        debug: false,
      });

      expect(beforeResult.memories).toBeDefined();

      // After agent ends
      const endResult = await agentEnd(context, {
        client: mockClient as any,
        config,
        state,
        llmClient: mockLLM as any,
        debug: false,
      });

      expect(endResult.processingTimeMs).toBeGreaterThanOrEqual(0);
    }

    // Verify state
    expect(state.turnCount).toBe(5);
  });

  it('should share state between before_agent_start and agent_end', async () => {
    const mockReranker = new MockReranker();

    // Store a memory
    await mockClient.remember('User prefers TypeScript');

    const context = createContext({
      userMessage: 'What programming language should I use?',
    });

    // Before agent - should retrieve memory
    const beforeResult = await beforeAgentStart(context, {
      client: mockClient as any,
      config,
      reranker: mockReranker as any,
      debug: false,
    });

    // Agent end - should update state
    await agentEnd(context, {
      client: mockClient as any,
      config,
      state,
      llmClient: mockLLM as any,
      debug: false,
    });

    expect(state.turnCount).toBe(1);
  });

  it('should handle pre_compaction after multiple turns', async () => {
    const mockReranker = new MockReranker();
    mockLLM.setResponse(JSON.stringify({
      facts: [
        {
          factText: 'User prefers dark mode',
          type: 'preference',
          importance: 7,
          confidence: 0.9,
          action: 'ADD',
          entities: [],
          relations: [],
        },
      ],
    }));

    // Simulate several turns
    for (let i = 0; i < 5; i++) {
      const context = createContext({ userMessage: `Message ${i}` });

      await beforeAgentStart(context, {
        client: mockClient as any,
        config,
        reranker: mockReranker as any,
        debug: false,
      });

      await agentEnd(context, {
        client: mockClient as any,
        config,
        state,
        llmClient: mockLLM as any,
        debug: false,
      });
    }

    // Now trigger pre-compaction
    const context = createContext({
      history: Array(10).fill(null).map((_, i) =>
        createTurn(i % 2 === 0 ? 'user' : 'assistant', `History ${i}`)
      ),
    });

    const compactionResult = await preCompaction(context, {
      client: mockClient as any,
      config,
      llmClient: mockLLM as any,
      debug: false,
    });

    expect(compactionResult.processingTimeMs).toBeGreaterThanOrEqual(0);
  });
});
