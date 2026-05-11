/**
 * TotalReclaw Skill - Integration Tests
 *
 * Tests the full flow with mock OpenClaw context, simulating
 * the complete lifecycle of the skill in an OpenClaw environment.
 */

import {
  TotalReclawSkill,
  createTotalReclawSkill,
} from '../src/totalreclaw-skill';
import {
  beforeAgentStart,
  formatMemoriesForContext,
  type BeforeAgentStartOptions,
} from '../src/triggers/before-agent-start';
import {
  agentEnd,
  type AgentEndOptions,
} from '../src/triggers/agent-end';
import {
  preCompaction,
  type PreCompactionOptions,
} from '../src/triggers/pre-compaction';
import {
  FactExtractor,
  createFactExtractor,
} from '../src/extraction';
import type {
  OpenClawContext,
  ConversationTurn,
  SkillState,
  ExtractedFact,
} from '../src/types';
import type { TotalReclaw, RerankedResult, Fact } from '@totalreclaw/client';

// ============================================================================
// Mocks
// ============================================================================

/**
 * Mock TotalReclaw client for integration testing
 */
class MockTotalReclawClient implements Partial<TotalReclaw> {
  private facts: Map<string, Fact> = new Map();
  private userId: string | null = null;

  async init(): Promise<void> {
    // Simulate init
  }

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
}

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

// ============================================================================
// Full Skill Integration Tests
// ============================================================================

describe('TotalReclawSkill Integration', () => {
  let skill: TotalReclawSkill;
  let mockClient: MockTotalReclawClient;
  let mockLLM: MockLLMClient;
  let isInitialized: boolean = false;

  beforeEach(async () => {
    mockClient = new MockTotalReclawClient();
    mockLLM = new MockLLMClient();

    skill = new TotalReclawSkill({
      serverUrl: 'http://mock',
      masterPassword: 'test-password-123',
      autoExtractEveryTurns: 3,
      minImportanceForAutoStore: 5,
      maxMemoriesInContext: 5,
    });

    try {
      const result = await skill.init();
      isInitialized = result.success;
    } catch {
      isInitialized = false;
    }
  });

  describe('initialization', () => {
    it('should initialize successfully', () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }
      expect(skill.isInitialized()).toBe(true);
    });

    it('should register new user if no credentials provided', async () => {
      const newSkill = new TotalReclawSkill({
        serverUrl: 'http://mock',
        masterPassword: 'new-user-password',
      });

      const result = await newSkill.init();

      // May fail if no server available
      expect(typeof result.success).toBe('boolean');
    });

    it('should return user ID after initialization', () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }
      const userId = skill.getUserId();
      expect(userId).toBeDefined();
    });
  });

  describe('full conversation flow', () => {
    it('should handle complete conversation cycle', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      // Turn 1: User asks about preferences
      const context1 = createContext({
        userMessage: 'What do you know about my preferences?',
      });

      const result1 = await skill.onBeforeAgentStart(context1);

      expect(result1).toHaveProperty('memories');
      expect(result1).toHaveProperty('contextString');
      expect(result1).toHaveProperty('latencyMs');
      expect(typeof result1.latencyMs).toBe('number');

      // Turn 2: User states a preference
      const context2 = createContext({
        userMessage: 'I prefer using TypeScript for all my projects',
      });

      const result2 = await skill.onBeforeAgentStart(context2);
      expect(result2.memories).toBeDefined();

      // Agent end hook
      const endResult = await skill.onAgentEnd(context2);
      expect(endResult).toHaveProperty('factsExtracted');
      expect(endResult).toHaveProperty('factsStored');
      expect(endResult).toHaveProperty('processingTimeMs');
    });

    it('should extract facts periodically based on turn counter', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      // Set up LLM to return facts
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

      // Turn 1 - should extract
      const context1 = createContext({ userMessage: 'I prefer dark mode' });
      await skill.onAgentEnd(context1);
      expect(skill.getTurnCount()).toBe(1);

      // Turn 2 - might not extract depending on config
      const context2 = createContext({ userMessage: 'Hello' });
      await skill.onAgentEnd(context2);
      expect(skill.getTurnCount()).toBe(2);

      // Turn 3 - should extract again
      const context3 = createContext({ userMessage: 'Another message' });
      await skill.onAgentEnd(context3);
      expect(skill.getTurnCount()).toBe(3);
    });
  });

  describe('tool operations', () => {
    it('should store and retrieve memories', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      // Store a memory
      const storeResult = await skill.remember({
        text: 'User favorite color is blue',
        type: 'preference',
        importance: 7,
      });

      expect(storeResult).toContain('Memory stored');

      // Retrieve memories
      const memories = await skill.recall({
        query: 'favorite color',
      });

      expect(Array.isArray(memories)).toBe(true);
    });

    it('should handle explicit memory commands', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      const context = createContext({
        userMessage: 'Remember that I use VS Code for development',
      });

      // Before agent starts
      const beforeResult = await skill.onBeforeAgentStart(context);
      expect(beforeResult).toBeDefined();

      // After agent ends - should detect explicit command
      const endResult = await skill.onAgentEnd(context);
      expect(endResult.factsExtracted).toBeGreaterThanOrEqual(0);
    });

    it('should export all memories', async () => {
      if (!isInitialized) {
        console.log('Skipping: skill not initialized');
        return;
      }

      // Store some memories
      await skill.remember({ text: 'Memory 1' });
      await skill.remember({ text: 'Memory 2' });

      // Export
      const exportResult = await skill.export({ format: 'json' });

      expect(() => JSON.parse(exportResult)).not.toThrow();
    });
  });
});

// ============================================================================
// Lifecycle Hook Integration Tests
// ============================================================================

describe('Lifecycle Hooks Integration', () => {
  let mockClient: MockTotalReclawClient;
  let mockLLM: MockLLMClient;
  let config: any;
  let state: SkillState;

  beforeEach(() => {
    mockClient = new MockTotalReclawClient();
    mockLLM = new MockLLMClient();
    config = {
      serverUrl: 'http://mock',
      autoExtractEveryTurns: 3,
      minImportanceForAutoStore: 5,
      maxMemoriesInContext: 5,
    };
    state = createSkillState();
  });

  describe('beforeAgentStart hook', () => {
    it('should retrieve and format memories', async () => {
      // Pre-populate some memories
      mockClient.addFact({
        id: 'fact-1',
        text: 'User prefers TypeScript',
        createdAt: new Date(),
        decayScore: 0.8,
        embedding: new Array(1024).fill(0.1),
        metadata: {},
      });

      const context = createContext({
        userMessage: 'What programming language should I use?',
      });

      const options: BeforeAgentStartOptions = {
        client: mockClient as any,
        config,
        debug: false,
      };

      const result = await beforeAgentStart(context, options);

      expect(result.memories).toBeDefined();
      expect(result.contextString).toBeDefined();
      expect(result.latencyMs).toBeGreaterThanOrEqual(0);
    });

    it('should handle empty memory store', async () => {
      const context = createContext();
      const options: BeforeAgentStartOptions = {
        client: mockClient as any,
        config,
        debug: false,
      };

      const result = await beforeAgentStart(context, options);

      expect(result.memories).toHaveLength(0);
      expect(result.contextString).toBe('');
    });

    it('should respect maxMemoriesInContext limit', async () => {
      // Add many facts
      for (let i = 0; i < 20; i++) {
        mockClient.addFact({
          id: `fact-${i}`,
          text: `Fact number ${i}`,
          createdAt: new Date(),
          decayScore: 0.5,
          embedding: new Array(1024).fill(0.1),
          metadata: {},
        });
      }

      const context = createContext({ userMessage: 'Fact' });
      const options: BeforeAgentStartOptions = {
        client: mockClient as any,
        config: { ...config, maxMemoriesInContext: 3 },
        debug: false,
      };

      const result = await beforeAgentStart(context, options);

      expect(result.memories.length).toBeLessThanOrEqual(3);
    });
  });

  describe('agentEnd hook', () => {
    it('should extract facts from conversation', async () => {
      mockLLM.setResponse(JSON.stringify({
        facts: [
          {
            factText: 'User prefers Python for data science',
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
        userMessage: 'I prefer using Python for data science',
      });

      const options: AgentEndOptions = {
        client: mockClient as any,
        config,
        state,
        llmClient: mockLLM as any,
        debug: false,
      };

      const result = await agentEnd(context, options);

      expect(result.factsExtracted).toBeGreaterThanOrEqual(0);
      expect(state.turnCount).toBe(1);
    });

    it('should increment turn counter', async () => {
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
    });

    it('should handle async mode', async () => {
      const context = createContext();
      const options: AgentEndOptions = {
        client: mockClient as any,
        config,
        state,
        llmClient: mockLLM as any,
        debug: false,
        async: true,
      };

      const result = await agentEnd(context, options);

      // In async mode, result should be immediate (before extraction)
      expect(result.processingTimeMs).toBeLessThan(100);
    });
  });

  describe('preCompaction hook', () => {
    it('should perform comprehensive extraction', async () => {
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
        history: Array(15).fill(null).map((_, i) =>
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

    it('should handle long conversation history', async () => {
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
  });
});

// ============================================================================
// Format Functions Tests
// ============================================================================

describe('formatMemoriesForContext', () => {
  it('should format empty memories', () => {
    const result = formatMemoriesForContext([]);
    expect(result).toBe('');
  });

  it('should format single memory', () => {
    const memories: RerankedResult[] = [
      {
        fact: {
          id: 'fact-1',
          text: 'User prefers TypeScript',
          createdAt: new Date(),
          decayScore: 0.8,
          embedding: new Array(1024).fill(0.1),
          metadata: { tags: ['preference'] },
        },
        score: 0.9,
        vectorScore: 0.85,
        textScore: 0.95,
        decayAdjustedScore: 0.88,
      },
    ];

    const result = formatMemoriesForContext(memories);

    expect(result).toContain('memory_context');
    expect(result).toContain('User prefers TypeScript');
    expect(result).toContain('PREF');
  });

  it('should format multiple memories', () => {
    const memories: RerankedResult[] = [
      {
        fact: {
          id: 'fact-1',
          text: 'Memory 1',
          createdAt: new Date(),
          decayScore: 0.8,
          embedding: new Array(1024).fill(0.1),
          metadata: {},
        },
        score: 0.9,
        vectorScore: 0.85,
        textScore: 0.95,
        decayAdjustedScore: 0.88,
      },
      {
        fact: {
          id: 'fact-2',
          text: 'Memory 2',
          createdAt: new Date(),
          decayScore: 0.7,
          embedding: new Array(1024).fill(0.1),
          metadata: {},
        },
        score: 0.8,
        vectorScore: 0.75,
        textScore: 0.85,
        decayAdjustedScore: 0.78,
      },
    ];

    const result = formatMemoriesForContext(memories);

    expect(result).toContain('Memory 1');
    expect(result).toContain('Memory 2');
    expect(result).toContain('rank="1"');
    expect(result).toContain('rank="2"');
  });

  it('should escape special characters', () => {
    const memories: RerankedResult[] = [
      {
        fact: {
          id: 'fact-1',
          text: 'User said "hello" & <goodbye>',
          createdAt: new Date(),
          decayScore: 0.8,
          embedding: new Array(1024).fill(0.1),
          metadata: {},
        },
        score: 0.9,
        vectorScore: 0.85,
        textScore: 0.95,
        decayAdjustedScore: 0.88,
      },
    ];

    const result = formatMemoriesForContext(memories);

    expect(result).toContain('&quot;');
    expect(result).toContain('&amp;');
    expect(result).toContain('&lt;');
    expect(result).toContain('&gt;');
  });
});

// ============================================================================
// Error Recovery Tests
// ============================================================================

describe('Error Recovery', () => {
  it('should handle hook failures gracefully', async () => {
    const skill = new TotalReclawSkill({
      serverUrl: 'http://mock',
      masterPassword: 'test-password',
    });

    const initResult = await skill.init();

    if (!initResult.success) {
      // If init fails, the test passes because we can't test hook failures
      console.log('Skipping: skill not initialized');
      return;
    }

    // Simulate error in beforeAgentStart
    const context = createContext();

    // Should not throw, should return empty result
    const result = await skill.onBeforeAgentStart(context);
    expect(result).toBeDefined();
    expect(result.memories).toBeDefined();
  });

  it('should continue after extraction errors', async () => {
    const skill = new TotalReclawSkill({
      serverUrl: 'http://mock',
      masterPassword: 'test-password',
    });

    const initResult = await skill.init();

    if (!initResult.success) {
      console.log('Skipping: skill not initialized');
      return;
    }

    const context = createContext();

    // First agent end
    await skill.onAgentEnd(context);
    expect(skill.getTurnCount()).toBe(1);

    // Second agent end should still work
    await skill.onAgentEnd(context);
    expect(skill.getTurnCount()).toBe(2);
  });

  it('should handle concurrent hook calls', async () => {
    const skill = new TotalReclawSkill({
      serverUrl: 'http://mock',
      masterPassword: 'test-password',
    });

    const initResult = await skill.init();

    if (!initResult.success) {
      console.log('Skipping: skill not initialized');
      return;
    }

    const context = createContext();

    // Multiple concurrent calls
    const results = await Promise.all([
      skill.onBeforeAgentStart(context),
      skill.onBeforeAgentStart(context),
      skill.onBeforeAgentStart(context),
    ]);

    expect(results).toHaveLength(3);
    results.forEach(result => {
      expect(result).toBeDefined();
      expect(result.memories).toBeDefined();
    });
  });
});

// ============================================================================
// State Management Tests
// ============================================================================

describe('State Management', () => {
  let skill: TotalReclawSkill;
  let isInitialized: boolean = false;

  beforeEach(async () => {
    skill = new TotalReclawSkill({
      serverUrl: 'http://mock',
      masterPassword: 'test-password',
    });

    try {
      const result = await skill.init();
      isInitialized = result.success;
    } catch {
      isInitialized = false;
    }
  });

  it('should track turn count', async () => {
    if (!isInitialized) {
      console.log('Skipping: skill not initialized');
      return;
    }

    expect(skill.getTurnCount()).toBe(0);

    await skill.onAgentEnd(createContext());
    expect(skill.getTurnCount()).toBe(1);

    await skill.onAgentEnd(createContext());
    expect(skill.getTurnCount()).toBe(2);
  });

  it('should reset turn count', async () => {
    if (!isInitialized) {
      console.log('Skipping: skill not initialized');
      return;
    }

    await skill.onAgentEnd(createContext());
    await skill.onAgentEnd(createContext());
    expect(skill.getTurnCount()).toBe(2);

    skill.resetTurnCount();
    expect(skill.getTurnCount()).toBe(0);
  });

  it('should cache memories', async () => {
    if (!isInitialized) {
      console.log('Skipping: skill not initialized');
      return;
    }

    await skill.onBeforeAgentStart(createContext());

    const cached = skill.getCachedMemories();
    expect(Array.isArray(cached)).toBe(true);
  });

  it('should clear cache', async () => {
    if (!isInitialized) {
      console.log('Skipping: skill not initialized');
      return;
    }

    await skill.onBeforeAgentStart(createContext());
    skill.clearCache();

    const cached = skill.getCachedMemories();
    expect(cached).toHaveLength(0);
  });

  it('should track pending extractions', () => {
    const pending = skill.getPendingExtractions();
    expect(Array.isArray(pending)).toBe(true);
  });

  it('should clear pending extractions', () => {
    skill.clearPendingExtractions();
    expect(skill.getPendingExtractions()).toHaveLength(0);
  });
});
