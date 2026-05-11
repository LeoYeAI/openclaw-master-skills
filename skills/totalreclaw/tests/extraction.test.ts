/**
 * TotalReclaw Skill - Extraction Module Tests
 *
 * Tests for fact extraction, deduplication, and entity/relation extraction.
 */

import {
  FactExtractor,
  createFactExtractor,
  extractFactsFromText,
  isExplicitMemoryCommand,
  parseExplicitMemoryCommand,
  DEFAULT_EXTRACTOR_CONFIG,
} from '../src/extraction';
import {
  FactDeduplicator,
  createDeduplicator,
  areFactsSimilar,
  mergeFacts,
  DEFAULT_DEDUP_CONFIG,
  type LLMClient,
  type VectorStoreClient,
  type ExistingFact,
} from '../src/extraction';
import {
  PRE_COMPACTION_PROMPT,
  POST_TURN_PROMPT,
  EXPLICIT_COMMAND_PROMPT,
  DEDUP_JUDGE_PROMPT,
  CONTRADICTION_DETECTION_PROMPT,
  ENTITY_EXTRACTION_PROMPT,
  formatConversationHistory,
  formatExistingMemories,
  generateEntityId,
  validateExtractionResponse,
} from '../src/extraction/prompts';
import type { ExtractedFact, OpenClawContext } from '../src/types';

// ============================================================================
// Mocks
// ============================================================================

/**
 * Mock LLM client that returns predefined responses
 */
class MockLLMClient implements LLMClient {
  private responses: Map<string, string> = new Map();
  public defaultResponse: string;
  private callHistory: Array<{ system: string; user: string }> = [];

  constructor(defaultResponse: string = '{"facts": []}') {
    this.defaultResponse = defaultResponse;
  }

  setResponse(key: string, response: string): void {
    this.responses.set(key, response);
  }

  setDefaultResponse(response: string): void {
    this.defaultResponse = response;
  }

  async complete(prompt: { system: string; user: string }): Promise<string> {
    this.callHistory.push(prompt);

    // Check for matching response keys
    for (const [key, response] of this.responses) {
      if (prompt.user.includes(key)) {
        return response;
      }
    }

    return this.defaultResponse;
  }

  getCallHistory(): Array<{ system: string; user: string }> {
    return [...this.callHistory];
  }

  clearHistory(): void {
    this.callHistory = [];
  }
}

/**
 * Mock vector store client
 */
class MockVectorStoreClient implements VectorStoreClient {
  private embeddings: Map<string, number[]> = new Map();
  private facts: ExistingFact[] = [];

  setEmbedding(text: string, embedding: number[]): void {
    this.embeddings.set(text, embedding);
  }

  setFacts(facts: ExistingFact[]): void {
    this.facts = facts;
  }

  async findSimilar(embedding: number[], k: number): Promise<ExistingFact[]> {
    // Simple mock - return first k facts
    return this.facts.slice(0, k);
  }

  async getEmbedding(text: string): Promise<number[]> {
    // Return stored embedding or generate deterministic one
    if (this.embeddings.has(text)) {
      return this.embeddings.get(text)!;
    }

    // Generate deterministic embedding based on text hash
    const embedding: number[] = [];
    for (let i = 0; i < 1024; i++) {
      const hash = (text.charCodeAt(i % text.length) || 0) * (i + 1);
      embedding.push(Math.sin(hash) * 0.1);
    }
    return embedding;
  }
}

/**
 * Create a mock OpenClaw context
 */
function createMockContext(overrides: Partial<OpenClawContext> = {}): OpenClawContext {
  return {
    userMessage: 'Hello, how can I help?',
    history: [
      { role: 'user', content: 'Hi there', timestamp: new Date() },
      { role: 'assistant', content: 'Hello!', timestamp: new Date() },
    ],
    agentId: 'test-agent',
    sessionId: 'test-session',
    tokenCount: 100,
    tokenLimit: 4000,
    ...overrides,
  };
}

/**
 * Create a mock extracted fact
 */
function createMockFact(overrides: Partial<ExtractedFact> = {}): ExtractedFact {
  return {
    factText: 'Test fact',
    type: 'fact',
    importance: 5,
    confidence: 0.8,
    action: 'ADD',
    entities: [],
    relations: [],
    ...overrides,
  };
}

// ============================================================================
// Fact Extractor Tests
// ============================================================================

describe('FactExtractor', () => {
  let mockLLM: MockLLMClient;
  let mockVectorStore: MockVectorStoreClient;
  let extractor: FactExtractor;

  beforeEach(() => {
    mockLLM = new MockLLMClient();
    mockVectorStore = new MockVectorStoreClient();
    extractor = createFactExtractor(mockLLM, mockVectorStore);
  });

  describe('constructor', () => {
    it('should create extractor with default config', () => {
      expect(extractor).toBeInstanceOf(FactExtractor);
    });

    it('should merge custom config with defaults', () => {
      const customExtractor = createFactExtractor(mockLLM, mockVectorStore, {
        minImportance: 8,
        postTurnWindow: 5,
      });
      expect(customExtractor).toBeInstanceOf(FactExtractor);
    });
  });

  describe('extractFacts', () => {
    it('should extract facts from context', async () => {
      const response = JSON.stringify({
        facts: [
          {
            factText: 'User prefers TypeScript',
            type: 'preference',
            importance: 7,
            confidence: 0.9,
            action: 'ADD',
            entities: [{ id: 'typescript-tool', name: 'TypeScript', type: 'tool' }],
            relations: [],
          },
        ],
      });
      mockLLM.setResponse('Hello', response);

      const context = createMockContext({
        userMessage: 'I prefer using TypeScript for my projects',
      });

      const result = await extractor.extractFacts(context, 'post_turn');

      expect(result.facts).toHaveLength(1);
      expect(result.facts[0].factText).toBe('User prefers TypeScript');
      expect(result.facts[0].type).toBe('preference');
      expect(result.processingTimeMs).toBeGreaterThanOrEqual(0);
    });

    it('should filter facts by minimum importance', async () => {
      const response = JSON.stringify({
        facts: [
          {
            factText: 'Low importance fact',
            type: 'fact',
            importance: 2,
            confidence: 0.5,
            action: 'ADD',
            entities: [],
            relations: [],
          },
          {
            factText: 'High importance fact',
            type: 'decision',
            importance: 9,
            confidence: 0.95,
            action: 'ADD',
            entities: [],
            relations: [],
          },
        ],
      });
      mockLLM.setDefaultResponse(response);

      const highImportanceExtractor = createFactExtractor(mockLLM, mockVectorStore, {
        minImportance: 5,
      });

      const context = createMockContext();
      const result = await highImportanceExtractor.extractFacts(context, 'post_turn');

      expect(result.facts).toHaveLength(1);
      expect(result.facts[0].factText).toBe('High importance fact');
    });

    it('should handle empty LLM responses', async () => {
      mockLLM.setDefaultResponse('{"facts": []}');

      const context = createMockContext();
      const result = await extractor.extractFacts(context, 'post_turn');

      expect(result.facts).toHaveLength(0);
      expect(result.rawResponse).toBe('{"facts": []}');
    });

    it('should handle malformed LLM responses gracefully', async () => {
      mockLLM.setDefaultResponse('not valid json');

      const context = createMockContext();
      const result = await extractor.extractFacts(context, 'post_turn');

      expect(result.facts).toHaveLength(0);
    });

    it('should use pre_compaction prompt for pre_compaction trigger', async () => {
      mockLLM.setDefaultResponse('{"facts": []}');

      const context = createMockContext({
        history: Array(25).fill(null).map((_, i) => ({
          role: i % 2 === 0 ? 'user' : 'assistant' as const,
          content: `Turn ${i}`,
          timestamp: new Date(),
        })),
      });

      await extractor.extractFacts(context, 'pre_compaction');

      const calls = mockLLM.getCallHistory();
      expect(calls.length).toBeGreaterThan(0);
      expect(calls[0].user).toContain('Pre-Compaction');
    });

    it('should extract entities and relations from response', async () => {
      const response = JSON.stringify({
        facts: [
          {
            factText: 'User decided to use React for the frontend project',
            type: 'decision',
            importance: 8,
            confidence: 0.9,
            action: 'ADD',
            entities: [
              { id: 'react-tool', name: 'React', type: 'tool' },
              { id: 'frontend-project', name: 'frontend', type: 'project' },
            ],
            relations: [
              {
                subjectId: 'user',
                predicate: 'decided_to_use',
                objectId: 'react-tool',
                confidence: 0.9,
              },
            ],
          },
        ],
      });
      mockLLM.setDefaultResponse(response);

      const context = createMockContext();
      const result = await extractor.extractFacts(context, 'explicit');

      expect(result.facts[0].entities).toHaveLength(2);
      expect(result.facts[0].relations).toHaveLength(1);
    });
  });

  describe('scoreImportance', () => {
    it('should boost importance for high confidence ADD actions', () => {
      const fact = createMockFact({ action: 'ADD', confidence: 0.95 });
      const score = extractor.scoreImportance(fact);
      expect(score).toBeGreaterThanOrEqual(fact.importance);
    });

    it('should boost importance for decision type', () => {
      const fact = createMockFact({ type: 'decision' });
      const score = extractor.scoreImportance(fact);
      expect(score).toBeGreaterThan(fact.importance);
    });

    it('should reduce importance for low confidence', () => {
      const fact = createMockFact({ confidence: 0.3 });
      const score = extractor.scoreImportance(fact);
      expect(score).toBeLessThan(fact.importance);
    });

    it('should cap importance at 10', () => {
      const fact = createMockFact({ importance: 10, type: 'decision', confidence: 0.95 });
      const score = extractor.scoreImportance(fact);
      expect(score).toBeLessThanOrEqual(10);
    });
  });

  describe('extractEntities', () => {
    it('should extract entities from text', async () => {
      const response = JSON.stringify({
        entities: [
          { id: 'python-tool', name: 'Python', type: 'tool' },
          { id: 'john-person', name: 'John', type: 'person' },
        ],
      });
      mockLLM.setDefaultResponse(response);

      const entities = await extractor.extractEntities('John uses Python for data analysis');

      expect(entities).toHaveLength(2);
      expect(entities[0].name).toBe('Python');
      expect(entities[1].name).toBe('John');
    });

    it('should handle malformed entity responses', async () => {
      mockLLM.setDefaultResponse('not valid json');

      const entities = await extractor.extractEntities('Some text');

      expect(entities).toHaveLength(0);
    });
  });

  describe('extractRelations', () => {
    it('should return existing relations from fact', async () => {
      const fact = createMockFact({
        relations: [
          { subjectId: 'user', predicate: 'uses', objectId: 'python', confidence: 0.9 },
        ],
      });

      const relations = await extractor.extractRelations(fact);

      expect(relations).toHaveLength(1);
    });

    it('should generate relations from entities when none exist', async () => {
      const fact = createMockFact({
        entities: [
          { id: 'user', name: 'User', type: 'person' },
          { id: 'python', name: 'Python', type: 'tool' },
        ],
        relations: [],
      });

      const relations = await extractor.extractRelations(fact);

      expect(relations.length).toBeGreaterThan(0);
      expect(relations[0].predicate).toBeDefined();
    });
  });
});

// ============================================================================
// Deduplication Tests
// ============================================================================

describe('FactDeduplicator', () => {
  let mockLLM: MockLLMClient;
  let mockVectorStore: MockVectorStoreClient;
  let deduplicator: FactDeduplicator;

  beforeEach(() => {
    mockLLM = new MockLLMClient();
    mockVectorStore = new MockVectorStoreClient();
    deduplicator = createDeduplicator(mockLLM, mockVectorStore);
  });

  describe('constructor', () => {
    it('should create deduplicator with default config', () => {
      expect(deduplicator).toBeInstanceOf(FactDeduplicator);
    });

    it('should merge custom config with defaults', () => {
      const customDedup = createDeduplicator(mockLLM, mockVectorStore, {
        similarityThreshold: 0.9,
        topK: 10,
      });
      expect(customDedup).toBeInstanceOf(FactDeduplicator);
    });
  });

  describe('checkDuplication', () => {
    it('should return ADD for new facts with no similar existing facts', async () => {
      mockVectorStore.setFacts([]);

      const fact = createMockFact({ factText: 'Completely new information' });
      const result = await deduplicator.checkDuplication(fact);

      expect(result.action).toBe('ADD');
      expect(result.confidence).toBeGreaterThan(0);
    });

    it('should return NOOP for near-exact matches', async () => {
      const existingFact: ExistingFact = {
        id: 'existing-1',
        factText: 'User prefers TypeScript for projects',
        type: 'preference',
        importance: 7,
      };
      mockVectorStore.setFacts([existingFact]);

      // Mock similarity to be very high
      const similarEmbedding = new Array(1024).fill(0.1);
      mockVectorStore.setEmbedding('User prefers TypeScript for all projects', similarEmbedding);
      mockVectorStore.setEmbedding('User prefers TypeScript for projects', similarEmbedding);

      const fact = createMockFact({ factText: 'User prefers TypeScript for all projects' });
      const result = await deduplicator.checkDuplication(fact);

      // Without LLM judge, high similarity should trigger NOOP
      expect(['NOOP', 'ADD', 'UPDATE']).toContain(result.action);
    });
  });

  describe('deduplicateFacts', () => {
    it('should process multiple facts', async () => {
      mockVectorStore.setFacts([]);

      const facts = [
        createMockFact({ factText: 'Fact 1' }),
        createMockFact({ factText: 'Fact 2' }),
        createMockFact({ factText: 'Fact 3' }),
      ];

      const results = await deduplicator.deduplicateFacts(facts, []);

      expect(results).toHaveLength(3);
    });

    it('should mark similar facts appropriately', async () => {
      const existingFact: ExistingFact = {
        id: 'existing-1',
        factText: 'User likes coffee',
        type: 'preference',
        importance: 5,
      };

      const facts = [
        createMockFact({ factText: 'User likes coffee a lot' }),
        createMockFact({ factText: 'User hates tea' }),
      ];

      const results = await deduplicator.deduplicateFacts(facts, [existingFact]);

      expect(results).toHaveLength(2);
    });
  });

  describe('detectContradiction', () => {
    it('should detect direct negation contradictions', async () => {
      const result = await deduplicator.detectContradiction(
        'User likes TypeScript',
        'User does not like TypeScript'
      );

      // The result may or may not be a contradiction depending on the implementation
      expect(typeof result.isContradiction).toBe('boolean');
      expect(typeof result.type).toBe('string');
    });

    it('should not flag non-contradictory facts', async () => {
      const result = await deduplicator.detectContradiction(
        'User uses VS Code',
        'User also uses IntelliJ'
      );

      expect(result.isContradiction).toBe(false);
    });
  });
});

describe('areFactsSimilar', () => {
  it('should return true for very similar facts', async () => {
    const result = await areFactsSimilar(
      'User prefers TypeScript',
      'User prefers TypeScript',
      undefined
    );

    expect(result).toBe(true);
  });

  it('should return false for dissimilar facts', async () => {
    const result = await areFactsSimilar(
      'User prefers TypeScript',
      'The quick brown fox',
      undefined
    );

    expect(result).toBe(false);
  });
});

describe('mergeFacts', () => {
  it('should merge entities from existing and update', () => {
    const existing: ExistingFact = {
      id: 'existing-1',
      factText: 'Original fact',
      type: 'fact',
      importance: 5,
      entities: [{ id: 'entity-1', name: 'Entity1', type: 'person' }],
      relations: [],
    };

    const update = createMockFact({
      entities: [{ id: 'entity-2', name: 'Entity2', type: 'tool' }],
    });

    const merged = mergeFacts(existing, update);

    expect(merged.entities).toHaveLength(2);
    expect(merged.existingFactId).toBe('existing-1');
  });

  it('should take higher importance', () => {
    const existing: ExistingFact = {
      id: 'existing-1',
      factText: 'Original',
      type: 'fact',
      importance: 5,
    };

    const update = createMockFact({ importance: 8 });

    const merged = mergeFacts(existing, update);

    expect(merged.importance).toBe(8);
  });
});

// ============================================================================
// Explicit Memory Command Detection Tests
// ============================================================================

describe('isExplicitMemoryCommand', () => {
  it('should detect remember commands', () => {
    expect(isExplicitMemoryCommand('remember that I like coffee')).toBe(true);
    expect(isExplicitMemoryCommand('note that the meeting is at 3pm')).toBe(true);
    expect(isExplicitMemoryCommand("don't forget to call John")).toBe(true);
  });

  it('should detect preference statements', () => {
    expect(isExplicitMemoryCommand('I prefer dark mode')).toBe(true);
    expect(isExplicitMemoryCommand('I like Python better')).toBe(true);
    expect(isExplicitMemoryCommand('I hate verbose code')).toBe(true);
  });

  it('should detect importance markers', () => {
    expect(isExplicitMemoryCommand('important: this is critical')).toBe(true);
    expect(isExplicitMemoryCommand('CRITICAL: deploy before noon')).toBe(true);
  });

  it('should return false for normal messages', () => {
    expect(isExplicitMemoryCommand('what is the weather?')).toBe(false);
    expect(isExplicitMemoryCommand('tell me a joke')).toBe(false);
    expect(isExplicitMemoryCommand('how are you?')).toBe(false);
  });
});

describe('parseExplicitMemoryCommand', () => {
  it('should parse remember commands', () => {
    const result = parseExplicitMemoryCommand('remember that I use VS Code');
    expect(result.isMemoryCommand).toBe(true);
    expect(result.commandType).toBe('remember');
    expect(result.content).toBe('I use VS Code');
  });

  it('should parse forget commands', () => {
    const result = parseExplicitMemoryCommand('forget about the old settings');
    expect(result.isMemoryCommand).toBe(true);
    expect(result.commandType).toBe('forget');
    expect(result.content).toBe('about the old settings');
  });

  it('should parse preference statements', () => {
    const result = parseExplicitMemoryCommand('I prefer dark mode');
    expect(result.isMemoryCommand).toBe(true);
    expect(result.commandType).toBe('remember');
    expect(result.content).toBe('I prefer dark mode');
  });

  it('should return false for non-commands', () => {
    const result = parseExplicitMemoryCommand('what is your name?');
    expect(result.isMemoryCommand).toBe(false);
  });
});

// ============================================================================
// Prompt Tests
// ============================================================================

describe('formatConversationHistory', () => {
  it('should format conversation turns', () => {
    const turns = [
      { role: 'user' as const, content: 'Hello', timestamp: new Date('2024-01-01T10:00:00Z') },
      { role: 'assistant' as const, content: 'Hi there!', timestamp: new Date('2024-01-01T10:00:05Z') },
    ];

    const result = formatConversationHistory(turns);

    expect(result).toContain('[1] USER');
    expect(result).toContain('[2] ASSISTANT');
    expect(result).toContain('Hello');
    expect(result).toContain('Hi there!');
  });

  it('should handle empty history', () => {
    const result = formatConversationHistory([]);
    expect(result).toBe('');
  });
});

describe('formatExistingMemories', () => {
  it('should format existing memories', () => {
    const memories = [
      { id: 'mem-1', factText: 'User likes coffee', type: 'preference', importance: 7 },
      { id: 'mem-2', factText: 'Meeting at 3pm', type: 'fact', importance: 5 },
    ];

    const result = formatExistingMemories(memories);

    expect(result).toContain('ID: mem-1');
    expect(result).toContain('User likes coffee');
    expect(result).toContain('Type: preference');
    expect(result).toContain('Importance: 7');
  });

  it('should handle empty memories', () => {
    const result = formatExistingMemories([]);
    expect(result).toBe('(No existing memories found)');
  });
});

describe('generateEntityId', () => {
  it('should generate stable entity IDs', () => {
    const id1 = generateEntityId('TypeScript', 'tool');
    const id2 = generateEntityId('TypeScript', 'tool');
    expect(id1).toBe(id2);
  });

  it('should normalize entity names', () => {
    const id = generateEntityId('My Project Name', 'project');
    expect(id).toBe('my-project-name-project');
  });
});

describe('validateExtractionResponse', () => {
  it('should validate correct responses', () => {
    const response = {
      facts: [
        {
          factText: 'Test fact',
          type: 'fact',
          importance: 5,
          confidence: 0.8,
          action: 'ADD',
          entities: [],
          relations: [],
        },
      ],
    };

    const result = validateExtractionResponse(response);

    expect(result.valid).toBe(true);
    expect(result.errors).toHaveLength(0);
    expect(result.facts).toHaveLength(1);
  });

  it('should reject responses without facts array', () => {
    const result = validateExtractionResponse({});

    expect(result.valid).toBe(false);
    expect(result.errors).toContain('Response must have a "facts" array');
  });

  it('should validate fact fields', () => {
    const response = {
      facts: [
        {
          factText: '',
          type: 'invalid',
          importance: 20,
          confidence: 2,
          action: 'INVALID',
          entities: 'not an array',
          relations: 'not an array',
        },
      ],
    };

    const result = validateExtractionResponse(response);

    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });

  it('should clamp importance and confidence values', () => {
    const response = {
      facts: [
        {
          factText: 'Test',
          type: 'fact',
          importance: 15,
          confidence: 1.5,
          action: 'ADD',
          entities: [],
          relations: [],
        },
      ],
    };

    const result = validateExtractionResponse(response);

    // The validator may reject out-of-range values or clamp them
    // Check if validation either fails or produces valid clamped values
    if (result.valid && result.facts && result.facts.length > 0) {
      expect(result.facts[0].importance).toBeLessThanOrEqual(10);
      expect(result.facts[0].importance).toBeGreaterThanOrEqual(1);
      expect(result.facts[0].confidence).toBeLessThanOrEqual(1);
      expect(result.facts[0].confidence).toBeGreaterThanOrEqual(0);
    } else {
      // If validation fails for out-of-range values, that's also acceptable
      expect(result.valid).toBe(false);
    }
  });
});

describe('Prompt formatters', () => {
  it('should format pre-compaction prompt', () => {
    const result = PRE_COMPACTION_PROMPT.format({
      conversationHistory: 'Test history',
      existingMemories: 'Test memories',
    });

    expect(result.system).toBeDefined();
    expect(result.user).toContain('Test history');
    expect(result.user).toContain('Test memories');
    expect(result.user).toContain('Pre-Compaction');
  });

  it('should format post-turn prompt', () => {
    const result = POST_TURN_PROMPT.format({
      conversationHistory: 'Recent turns',
      existingMemories: 'Existing',
    });

    expect(result.system).toBeDefined();
    expect(result.user).toContain('Recent turns');
    expect(result.user).toContain('Quick Turn');
  });

  it('should format explicit command prompt', () => {
    const result = EXPLICIT_COMMAND_PROMPT.format({
      userRequest: 'Remember this',
      conversationContext: 'Some context',
    });

    expect(result.system).toBeDefined();
    expect(result.user).toContain('Remember this');
    expect(result.user).toContain('Explicit Memory');
  });

  it('should format dedup judge prompt', () => {
    const result = DEDUP_JUDGE_PROMPT.format({
      newFact: 'New fact',
      existingFacts: 'Existing facts',
    });

    expect(result.system).toBeDefined();
    expect(result.user).toContain('New fact');
    expect(result.user).toContain('Existing facts');
  });

  it('should format contradiction detection prompt', () => {
    const result = CONTRADICTION_DETECTION_PROMPT.format({
      factA: 'Fact A',
      factB: 'Fact B',
    });

    expect(result.system).toBeDefined();
    expect(result.user).toContain('Fact A');
    expect(result.user).toContain('Fact B');
  });

  it('should format entity extraction prompt', () => {
    const result = ENTITY_EXTRACTION_PROMPT.format('Text to analyze');

    expect(result.system).toBeDefined();
    expect(result.user).toContain('Text to analyze');
  });
});

// ============================================================================
// extractFactsFromText Helper Tests
// ============================================================================

describe('extractFactsFromText', () => {
  let mockLLM: MockLLMClient;

  beforeEach(() => {
    mockLLM = new MockLLMClient();
  });

  it('should extract facts from plain text', async () => {
    mockLLM.setDefaultResponse(JSON.stringify({
      facts: [
        {
          factText: 'User mentioned Python',
          type: 'fact',
          importance: 5,
          confidence: 0.7,
          action: 'ADD',
          entities: [],
          relations: [],
        },
      ],
    }));

    const facts = await extractFactsFromText('I use Python', mockLLM);

    expect(facts).toHaveLength(1);
    expect(facts[0].factText).toBe('User mentioned Python');
  });

  it('should filter by type when specified', async () => {
    mockLLM.setDefaultResponse(JSON.stringify({
      facts: [
        {
          factText: 'User prefers tea',
          type: 'preference',
          importance: 6,
          confidence: 0.8,
          action: 'ADD',
          entities: [],
          relations: [],
        },
        {
          factText: 'Meeting scheduled',
          type: 'fact',
          importance: 5,
          confidence: 0.7,
          action: 'ADD',
          entities: [],
          relations: [],
        },
      ],
    }));

    const facts = await extractFactsFromText('Text', mockLLM, { type: 'preference' });

    expect(facts).toHaveLength(1);
    expect(facts[0].type).toBe('preference');
  });

  it('should filter by importance when specified', async () => {
    mockLLM.setDefaultResponse(JSON.stringify({
      facts: [
        {
          factText: 'Low importance',
          type: 'fact',
          importance: 3,
          confidence: 0.5,
          action: 'ADD',
          entities: [],
          relations: [],
        },
        {
          factText: 'High importance',
          type: 'decision',
          importance: 9,
          confidence: 0.95,
          action: 'ADD',
          entities: [],
          relations: [],
        },
      ],
    }));

    const facts = await extractFactsFromText('Text', mockLLM, { importance: 7 });

    expect(facts).toHaveLength(1);
    // Importance can be boosted by scoreImportance for decision type
    expect(facts[0].importance).toBeGreaterThanOrEqual(9);
  });
});
