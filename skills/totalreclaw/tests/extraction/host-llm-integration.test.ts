/**
 * Host Agent LLM Integration Test (T088)
 *
 * Validates that the TotalReclaw skill can use the host agent's LLM
 * for fact extraction, without needing a separate LLM API key.
 *
 * This is the production architecture:
 * - OpenClaw provides its LLM via the skill interface
 * - NanoClaw provides its LLM via the Agent SDK
 * - The skill never calls an LLM directly; it delegates to the host
 *
 * The test mocks an OpenClaw-like environment where the host agent
 * provides an LLM client that implements the LLMClient interface.
 */
import {
  FactExtractor,
  createFactExtractor,
  isExplicitMemoryCommand,
} from '../../src/extraction/extractor';
import type { LLMClient } from '../../src/extraction/dedup';
import type { OpenClawContext } from '../../src/types';

describe('Host Agent LLM Integration (T088)', () => {
  /**
   * Mock OpenClaw host LLM client.
   *
   * In production, this would be implemented by the OpenClaw runtime
   * (e.g., via the `llm-task` plugin tool). The skill instructs the
   * agent to invoke llm-task, which runs a separate LLM call using
   * the agent's configured model (Claude, GPT-4, etc.).
   *
   * For this test, we simulate the host LLM returning structured
   * extraction results.
   */
  class MockHostLLM implements LLMClient {
    public callCount = 0;
    public lastPrompt: { system: string; user: string } | null = null;

    async complete(prompt: { system: string; user: string }): Promise<string> {
      this.callCount++;
      this.lastPrompt = prompt;

      // Simulate a structured extraction response from the host LLM
      return JSON.stringify({
        facts: [
          {
            factText: 'User prefers TypeScript over JavaScript for new projects',
            type: 'preference',
            importance: 7,
            confidence: 0.95,
            action: 'ADD',
            entities: [
              { id: 'typescript-tool', name: 'TypeScript', type: 'tool' },
              { id: 'javascript-tool', name: 'JavaScript', type: 'tool' },
            ],
            relations: [
              {
                subjectId: 'user-person',
                predicate: 'prefers',
                objectId: 'typescript-tool',
                confidence: 0.95,
              },
            ],
          },
        ],
        metadata: {
          totalTurnsAnalyzed: 3,
          extractionTimestamp: new Date().toISOString(),
        },
      });
    }
  }

  const makeContext = (message: string): OpenClawContext => ({
    userMessage: message,
    history: [
      { role: 'user' as const, content: message, timestamp: new Date() },
    ],
    agentId: 'test-agent',
    sessionId: 'test-session',
    tokenCount: 100,
    tokenLimit: 4000,
  });

  test('FactExtractor accepts host LLM client via constructor', () => {
    const hostLLM = new MockHostLLM();
    const extractor = new FactExtractor(hostLLM);
    expect(extractor).toBeDefined();
  });

  test('extraction uses host LLM (no separate API key needed)', async () => {
    const hostLLM = new MockHostLLM();
    const extractor = new FactExtractor(hostLLM);

    const context = makeContext(
      'I prefer TypeScript over JavaScript for new projects'
    );
    const result = await extractor.extractFacts(context, 'post_turn');

    // The host LLM was called
    expect(hostLLM.callCount).toBe(1);
    // Facts were extracted
    expect(result.facts.length).toBeGreaterThanOrEqual(1);
    // The extracted fact contains the expected content
    const fact = result.facts[0];
    expect(fact.factText).toContain('TypeScript');
    expect(fact.type).toBe('preference');
    expect(fact.action).toBe('ADD');
  });

  test('host LLM receives system and user prompts', async () => {
    const hostLLM = new MockHostLLM();
    const extractor = new FactExtractor(hostLLM);

    const context = makeContext('Remember that I like Python');
    await extractor.extractFacts(context, 'post_turn');

    // Verify the prompt structure matches what the host LLM expects
    expect(hostLLM.lastPrompt).not.toBeNull();
    expect(hostLLM.lastPrompt!.system).toContain('memory extraction engine');
    expect(hostLLM.lastPrompt!.user).toContain('Python');
  });

  test('extraction works with pre_compaction trigger', async () => {
    const hostLLM = new MockHostLLM();
    const extractor = new FactExtractor(hostLLM);

    const context: OpenClawContext = {
      userMessage: 'Let me think about this',
      history: Array.from({ length: 20 }, (_, i) => ({
        role: (i % 2 === 0 ? 'user' : 'assistant') as 'user' | 'assistant',
        content: `Turn ${i + 1} content`,
        timestamp: new Date(Date.now() - (20 - i) * 60000),
      })),
      agentId: 'test-agent',
      sessionId: 'test-session',
      tokenCount: 3500,
      tokenLimit: 4000,
    };

    const result = await extractor.extractFacts(context, 'pre_compaction');
    expect(hostLLM.callCount).toBe(1);
    expect(result.facts.length).toBeGreaterThanOrEqual(1);
  });

  test('extraction works with explicit trigger', async () => {
    const hostLLM = new MockHostLLM();
    const extractor = new FactExtractor(hostLLM);

    const context = makeContext('Remember that I prefer dark mode in all editors');
    const result = await extractor.extractFacts(context, 'explicit');

    expect(hostLLM.callCount).toBe(1);
    expect(result.facts.length).toBeGreaterThanOrEqual(1);
  });

  test('createFactExtractor convenience function works with host LLM', () => {
    const hostLLM = new MockHostLLM();
    const extractor = createFactExtractor(hostLLM);
    expect(extractor).toBeInstanceOf(FactExtractor);
  });

  test('isExplicitMemoryCommand detects remember commands', () => {
    expect(isExplicitMemoryCommand('Remember that I like Python')).toBe(true);
    expect(isExplicitMemoryCommand('Note that my deadline is Friday')).toBe(true);
    expect(isExplicitMemoryCommand('What is the weather?')).toBe(false);
  });

  test('entities and relations are extracted via host LLM', async () => {
    const hostLLM = new MockHostLLM();
    const extractor = new FactExtractor(hostLLM);

    const context = makeContext('I use TypeScript for all my projects');
    const result = await extractor.extractFacts(context, 'post_turn');

    const fact = result.facts[0];
    expect(fact.entities.length).toBeGreaterThanOrEqual(1);
    expect(fact.relations.length).toBeGreaterThanOrEqual(1);

    // Verify entity structure
    const tsEntity = fact.entities.find(e => e.name === 'TypeScript');
    expect(tsEntity).toBeDefined();
    expect(tsEntity!.type).toBe('tool');
  });

  test('host LLM error is handled gracefully', async () => {
    const brokenLLM: LLMClient = {
      async complete() {
        return 'not valid json {{{';
      },
    };

    const extractor = new FactExtractor(brokenLLM);
    const context = makeContext('Test message');
    const result = await extractor.extractFacts(context, 'post_turn');

    // Should not throw, but facts should be empty (parsing failed)
    expect(result.facts).toHaveLength(0);
  });
});
