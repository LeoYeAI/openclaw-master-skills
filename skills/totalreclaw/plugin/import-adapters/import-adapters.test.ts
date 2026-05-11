/**
 * Unit tests for import adapters (Task 9).
 *
 * Run with: npx tsx import-adapters/import-adapters.test.ts
 *
 * Uses TAP-style output (no test framework dependency).
 */

import { Mem0Adapter } from './mem0-adapter.js';
import { MCPMemoryAdapter } from './mcp-memory-adapter.js';
import { BaseImportAdapter } from './base-adapter.js';
import { getAdapter } from './index.js';
import type {
  NormalizedFact,
  AdapterParseResult,
  ImportSource,
  ProgressCallback,
} from './types.js';

// ---------------------------------------------------------------------------
// TAP Helpers
// ---------------------------------------------------------------------------

let passed = 0;
let failed = 0;
let testNum = 0;

function assert(condition: boolean, message: string): void {
  testNum++;
  if (condition) {
    passed++;
    console.log(`ok ${testNum} - ${message}`);
  } else {
    failed++;
    console.log(`not ok ${testNum} - ${message}`);
  }
}

function assertThrows(fn: () => void, message: string): void {
  try {
    fn();
    failed++;
    testNum++;
    console.log(`not ok ${testNum} - ${message} (did not throw)`);
  } catch {
    passed++;
    testNum++;
    console.log(`ok ${testNum} - ${message}`);
  }
}

// ---------------------------------------------------------------------------
// Concrete subclass to test protected BaseImportAdapter.validateFact()
// ---------------------------------------------------------------------------

class TestAdapter extends BaseImportAdapter {
  readonly source: ImportSource = 'mem0';
  readonly displayName = 'Test Adapter';

  async parse(): Promise<AdapterParseResult> {
    return { facts: [], warnings: [], errors: [] };
  }

  // Expose protected methods for testing
  public testValidateFact(fact: Partial<NormalizedFact>): NormalizedFact | null {
    return this.validateFact(fact);
  }

  public testValidateFacts(
    rawFacts: Partial<NormalizedFact>[],
  ): { facts: NormalizedFact[]; invalidCount: number } {
    return this.validateFacts(rawFacts);
  }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

async function runTests(): Promise<void> {
  // =========================================================================
  // Mem0Adapter
  // =========================================================================

  console.log('# Mem0Adapter');

  // --- parses API response format ---
  {
    const content = JSON.stringify({
      results: [
        { id: 'mem-1', memory: 'User prefers dark mode', categories: ['preference'] },
        { id: 'mem-2', memory: 'User works at Acme Corp', categories: ['fact'] },
      ],
    });

    const adapter = new Mem0Adapter();
    const result = await adapter.parse({ content });

    assert(result.facts.length === 2, 'Mem0: API response format yields 2 facts');
    assert(result.facts[0].text === 'User prefers dark mode', 'Mem0: first fact text correct');
    assert(result.facts[0].type === 'preference', 'Mem0: preference category mapped');
    assert(result.facts[0].source === 'mem0', 'Mem0: source is mem0');
    assert(result.facts[1].type === 'fact', 'Mem0: fact category mapped');
    assert(result.facts[1].sourceId === 'mem-2', 'Mem0: sourceId preserved');
  }

  // --- parses export file format ---
  {
    const content = JSON.stringify({
      export_date: '2026-03-10',
      memories: [
        { id: 'mem-1', memory: 'User likes TypeScript' },
      ],
    });

    const adapter = new Mem0Adapter();
    const result = await adapter.parse({ content });

    assert(result.facts.length === 1, 'Mem0: export file format yields 1 fact');
    assert(result.facts[0].text === 'User likes TypeScript', 'Mem0: export fact text correct');
  }

  // --- parses bare array format ---
  {
    const content = JSON.stringify([
      { id: 'mem-1', memory: 'User prefers Python' },
      { id: 'mem-2', memory: 'User dislikes Java' },
    ]);

    const adapter = new Mem0Adapter();
    const result = await adapter.parse({ content });

    assert(result.facts.length === 2, 'Mem0: bare array yields 2 facts');
    assert(result.facts[0].text === 'User prefers Python', 'Mem0: bare array first fact correct');
  }

  // --- skips empty/short memories ---
  {
    const content = JSON.stringify({
      results: [
        { id: 'mem-1', memory: '' },
        { id: 'mem-2', memory: 'Valid fact here' },
        { id: 'mem-3', memory: 'ab' }, // too short (< 3 chars)
      ],
    });

    const adapter = new Mem0Adapter();
    const result = await adapter.parse({ content });

    assert(result.facts.length === 1, 'Mem0: skips empty/short memories, keeps 1 valid');
    assert(result.facts[0].text === 'Valid fact here', 'Mem0: only valid fact kept');
    const hasWarning = result.warnings.some((w) => w.includes('2 memories had invalid'));
    assert(hasWarning, 'Mem0: warning about 2 invalid memories');
  }

  // --- returns errors on invalid JSON ---
  {
    const adapter = new Mem0Adapter();
    const result = await adapter.parse({ content: 'not json {{{' });

    assert(result.facts.length === 0, 'Mem0: invalid JSON yields 0 facts');
    assert(result.errors.length > 0, 'Mem0: invalid JSON produces error');
    assert(
      result.errors[0].includes('Failed to parse Mem0 JSON'),
      'Mem0: error message mentions JSON parse failure',
    );
  }

  // --- returns error when no content or api_key ---
  {
    const adapter = new Mem0Adapter();
    const result = await adapter.parse({});

    assert(result.facts.length === 0, 'Mem0: no input yields 0 facts');
    assert(result.errors.length > 0, 'Mem0: no input produces error');
    assert(
      result.errors[0].includes('requires either content'),
      'Mem0: error message mentions required input',
    );
  }

  // --- category mapping ---
  {
    const content = JSON.stringify({
      results: [
        { id: '1', memory: 'User likes hiking', categories: ['like'] },
        { id: '2', memory: 'User dislikes rain', categories: ['dislike'] },
        { id: '3', memory: 'Graduated in 2020', categories: ['biographical'] },
        { id: '4', memory: 'Wants to learn Rust', categories: ['objective'] },
        { id: '5', memory: 'Visited Paris in 2023', categories: ['event'] },
        { id: '6', memory: 'Chose React over Vue', categories: ['decision'] },
        { id: '7', memory: 'Some unknown category', categories: ['zzz_unknown'] },
      ],
    });

    const adapter = new Mem0Adapter();
    const result = await adapter.parse({ content });

    assert(result.facts[0].type === 'preference', 'Mem0: "like" -> preference');
    assert(result.facts[1].type === 'preference', 'Mem0: "dislike" -> preference');
    assert(result.facts[2].type === 'fact', 'Mem0: "biographical" -> fact');
    assert(result.facts[3].type === 'goal', 'Mem0: "objective" -> goal');
    assert(result.facts[4].type === 'episodic', 'Mem0: "event" -> episodic');
    assert(result.facts[5].type === 'decision', 'Mem0: "decision" -> decision');
    assert(result.facts[6].type === 'fact', 'Mem0: unknown category defaults to fact');
  }

  // --- importance defaults to 6 ---
  {
    const content = JSON.stringify({
      results: [
        { id: 'mem-1', memory: 'User prefers dark mode' },
      ],
    });

    const adapter = new Mem0Adapter();
    const result = await adapter.parse({ content });

    assert(result.facts[0].importance === 6, 'Mem0: default importance is 6');
  }

  // --- handles unrecognized format ---
  {
    const content = JSON.stringify({ some_key: 'some_value' });

    const adapter = new Mem0Adapter();
    const result = await adapter.parse({ content });

    assert(result.facts.length === 0, 'Mem0: unrecognized format yields 0 facts');
    assert(
      result.errors.some((e) => e.includes('Unrecognized Mem0 format')),
      'Mem0: unrecognized format error message',
    );
  }

  // =========================================================================
  // MCPMemoryAdapter
  // =========================================================================

  console.log('# MCPMemoryAdapter');

  // --- parses entities with observations ---
  {
    const content = [
      JSON.stringify({ type: 'entity', name: 'John', entityType: 'person', observations: ['Works at Acme Corp', 'Prefers TypeScript'] }),
      JSON.stringify({ type: 'entity', name: 'Project Alpha', entityType: 'project', observations: ['Uses React'] }),
    ].join('\n');

    const adapter = new MCPMemoryAdapter();
    const result = await adapter.parse({ content });

    assert(result.facts.length === 3, 'MCP: 2 entities with 3 total observations -> 3 facts');
    // "Works at Acme Corp" starts with uppercase verb -> prefixed: "John: Works at Acme Corp"
    // Actually the adapter checks if it starts lowercase (verb) or uppercase (standalone sentence)
    // "Works" starts uppercase -> "John: Works at Acme Corp"
    assert(result.facts[0].text.includes('John'), 'MCP: first fact includes entity name');
    assert(result.facts[0].text.includes('Acme Corp'), 'MCP: first fact includes observation');
    assert(result.facts[1].text.includes('TypeScript'), 'MCP: second fact includes TypeScript');
    assert(result.facts[0].source === 'mcp-memory', 'MCP: source is mcp-memory');
  }

  // --- contextualizes observations correctly ---
  {
    const content = [
      JSON.stringify({
        type: 'entity', name: 'John', entityType: 'person',
        observations: [
          'works at Acme Corp',       // lowercase verb -> "John works at Acme Corp"
          'John likes TypeScript',     // already starts with name -> unchanged
          'He prefers React',          // pronoun -> replaced: "John prefers React"
          'An avid hiker',             // uppercase start -> "John: An avid hiker"
        ],
      }),
    ].join('\n');

    const adapter = new MCPMemoryAdapter();
    const result = await adapter.parse({ content });

    assert(result.facts.length === 4, 'MCP: 4 observations -> 4 facts');
    assert(result.facts[0].text === 'John works at Acme Corp', 'MCP: lowercase verb prefixed with entity name');
    assert(result.facts[1].text === 'John likes TypeScript', 'MCP: already has entity name, unchanged');
    assert(result.facts[2].text === 'John prefers React', 'MCP: pronoun "He" replaced with entity name');
    assert(result.facts[3].text === 'John: An avid hiker', 'MCP: uppercase standalone sentence prefixed with colon');
  }

  // --- parses relations ---
  {
    const content = [
      JSON.stringify({ type: 'entity', name: 'John', entityType: 'person', observations: ['Developer'] }),
      JSON.stringify({ type: 'entity', name: 'Project Alpha', entityType: 'project', observations: ['Deadline March'] }),
      JSON.stringify({ type: 'relation', from: 'John', to: 'Project Alpha', relationType: 'works_on' }),
    ].join('\n');

    const adapter = new MCPMemoryAdapter();
    const result = await adapter.parse({ content });

    // 2 observations + 1 relation = 3 facts
    assert(result.facts.length === 3, 'MCP: 2 observations + 1 relation = 3 facts');
    assert(
      result.facts[2].text === 'John works on Project Alpha',
      'MCP: relation converted to human-readable text',
    );
    assert(result.facts[2].type === 'fact', 'MCP: relation type defaults to fact');
  }

  // --- later entity overrides earlier (append-only semantics) ---
  {
    const content = [
      JSON.stringify({ type: 'entity', name: 'John', entityType: 'person', observations: ['Old observation'] }),
      JSON.stringify({ type: 'entity', name: 'John', entityType: 'person', observations: ['New observation'] }),
    ].join('\n');

    const adapter = new MCPMemoryAdapter();
    const result = await adapter.parse({ content });

    // Only the later entity should be used (Map overwrites)
    assert(result.facts.length === 1, 'MCP: duplicate entity keeps only latest');
    assert(
      result.facts[0].text.includes('New observation'),
      'MCP: latest entity observations used',
    );
  }

  // --- warns on orphaned relations ---
  {
    const content = [
      JSON.stringify({ type: 'relation', from: 'Unknown', to: 'Also Unknown', relationType: 'knows' }),
    ].join('\n');

    const adapter = new MCPMemoryAdapter();
    const result = await adapter.parse({ content });

    const hasWarning = result.warnings.some((w) => w.includes('unknown entity'));
    assert(hasWarning, 'MCP: warns on orphaned relation with unknown entities');
    // Orphaned relation should not produce a fact
    assert(result.facts.length === 0, 'MCP: orphaned relation produces no facts');
  }

  // --- handles empty/blank lines in JSONL ---
  {
    const content = [
      '',
      JSON.stringify({ type: 'entity', name: 'Alice', entityType: 'person', observations: ['Likes coffee'] }),
      '   ',
      JSON.stringify({ type: 'entity', name: 'Bob', entityType: 'person', observations: ['Likes tea'] }),
      '',
    ].join('\n');

    const adapter = new MCPMemoryAdapter();
    const result = await adapter.parse({ content });

    assert(result.facts.length === 2, 'MCP: blank lines in JSONL are skipped');
    assert(result.errors.length === 0, 'MCP: blank lines do not produce errors');
  }

  // --- invalid JSON lines produce errors ---
  {
    const content = [
      JSON.stringify({ type: 'entity', name: 'Alice', entityType: 'person', observations: ['Valid'] }),
      'this is not json',
      JSON.stringify({ type: 'entity', name: 'Bob', entityType: 'person', observations: ['Also valid'] }),
    ].join('\n');

    const adapter = new MCPMemoryAdapter();
    const result = await adapter.parse({ content });

    assert(result.facts.length === 2, 'MCP: valid facts parsed despite invalid line');
    assert(result.errors.length === 1, 'MCP: one error for the invalid JSON line');
    assert(result.errors[0].includes('Line 2'), 'MCP: error references correct line number');
  }

  // --- entity type mapping ---
  {
    const content = [
      JSON.stringify({ type: 'entity', name: 'React', entityType: 'tool', observations: ['Frontend framework'] }),
      JSON.stringify({ type: 'entity', name: 'Launch', entityType: 'goal', observations: ['Ship by March'] }),
      JSON.stringify({ type: 'entity', name: 'Meeting', entityType: 'event', observations: ['Quarterly review'] }),
      JSON.stringify({ type: 'entity', name: 'PickedAWS', entityType: 'decision', observations: ['Over GCP'] }),
    ].join('\n');

    const adapter = new MCPMemoryAdapter();
    const result = await adapter.parse({ content });

    assert(result.facts[0].type === 'preference', 'MCP: "tool" entityType -> preference');
    assert(result.facts[1].type === 'goal', 'MCP: "goal" entityType -> goal');
    assert(result.facts[2].type === 'episodic', 'MCP: "event" entityType -> episodic');
    assert(result.facts[3].type === 'decision', 'MCP: "decision" entityType -> decision');
  }

  // --- no content and no file_path (and no default file) ---
  {
    const adapter = new MCPMemoryAdapter();
    // Pass a non-existent file_path to trigger the file read error path
    const result = await adapter.parse({ file_path: '/tmp/definitely-does-not-exist-totalreclaw-test.jsonl' });

    assert(result.facts.length === 0, 'MCP: missing file yields 0 facts');
    assert(result.errors.length > 0, 'MCP: missing file produces error');
  }

  // --- relation type humanization ---
  {
    const content = [
      JSON.stringify({ type: 'entity', name: 'A', entityType: 'person', observations: ['exists'] }),
      JSON.stringify({ type: 'entity', name: 'B', entityType: 'project', observations: ['exists'] }),
      JSON.stringify({ type: 'relation', from: 'A', to: 'B', relationType: 'MEMBER_OF' }),
    ].join('\n');

    const adapter = new MCPMemoryAdapter();
    const result = await adapter.parse({ content });

    const relFact = result.facts.find((f) => f.tags?.includes('relation'));
    assert(
      relFact?.text === 'A is a member of B',
      `MCP: MEMBER_OF humanized to "is a member of" (got: ${relFact?.text})`,
    );
  }

  // =========================================================================
  // BaseImportAdapter (via TestAdapter)
  // =========================================================================

  console.log('# BaseImportAdapter');

  const testAdapter = new TestAdapter();

  // --- text validation: minimum 3 chars ---
  {
    assert(testAdapter.testValidateFact({ text: '' }) === null, 'Base: empty text returns null');
    assert(testAdapter.testValidateFact({ text: 'ab' }) === null, 'Base: 2-char text returns null');
    assert(testAdapter.testValidateFact({ text: '   ' }) === null, 'Base: whitespace-only text returns null');
    assert(testAdapter.testValidateFact({ text: 'a  ' }) === null, 'Base: 1-char trimmed text returns null');

    const result = testAdapter.testValidateFact({ text: 'abc' });
    assert(result !== null, 'Base: 3-char text is valid');
    assert(result?.text === 'abc', 'Base: 3-char text preserved');
  }

  // --- text truncation at 512 chars ---
  {
    const longText = 'x'.repeat(600);
    const result = testAdapter.testValidateFact({ text: longText });

    assert(result !== null, 'Base: long text is valid');
    assert(result!.text.length === 512, `Base: text truncated to 512 chars (got ${result!.text.length})`);
  }

  // --- text is trimmed ---
  {
    const result = testAdapter.testValidateFact({ text: '  hello world  ' });
    assert(result !== null, 'Base: padded text is valid');
    assert(result!.text === 'hello world', 'Base: text is trimmed');
  }

  // --- type normalization ---
  {
    const validTypes = ['fact', 'preference', 'decision', 'episodic', 'goal', 'context', 'summary'] as const;

    for (const t of validTypes) {
      const result = testAdapter.testValidateFact({ text: 'test fact', type: t });
      assert(result?.type === t, `Base: type "${t}" preserved`);
    }

    const invalidResult = testAdapter.testValidateFact({ text: 'test fact', type: 'bogus' as any });
    assert(invalidResult?.type === 'fact', 'Base: invalid type defaults to "fact"');

    const missingResult = testAdapter.testValidateFact({ text: 'test fact' });
    assert(missingResult?.type === 'fact', 'Base: missing type defaults to "fact"');
  }

  // --- importance scale conversion (0-1 -> 1-10) ---
  {
    // 0-1 scale conversion
    const r0 = testAdapter.testValidateFact({ text: 'test fact', importance: 0.0 });
    assert(r0?.importance === 1, `Base: importance 0.0 -> 1 (got ${r0?.importance})`);

    const r05 = testAdapter.testValidateFact({ text: 'test fact', importance: 0.5 });
    assert(r05?.importance === 5, `Base: importance 0.5 -> 5 (got ${r05?.importance})`);

    const r1 = testAdapter.testValidateFact({ text: 'test fact', importance: 1.0 });
    assert(r1?.importance === 10, `Base: importance 1.0 -> 10 (got ${r1?.importance})`);

    const r03 = testAdapter.testValidateFact({ text: 'test fact', importance: 0.3 });
    assert(r03?.importance === 3, `Base: importance 0.3 -> 3 (got ${r03?.importance})`);

    const r08 = testAdapter.testValidateFact({ text: 'test fact', importance: 0.8 });
    assert(r08?.importance === 8, `Base: importance 0.8 -> 8 (got ${r08?.importance})`);
  }

  // --- importance already on 1-10 scale ---
  {
    const r5 = testAdapter.testValidateFact({ text: 'test fact', importance: 5 });
    assert(r5?.importance === 5, `Base: importance 5 stays 5 (got ${r5?.importance})`);

    const r10 = testAdapter.testValidateFact({ text: 'test fact', importance: 10 });
    assert(r10?.importance === 10, `Base: importance 10 stays 10 (got ${r10?.importance})`);

    const r7 = testAdapter.testValidateFact({ text: 'test fact', importance: 7 });
    assert(r7?.importance === 7, `Base: importance 7 stays 7 (got ${r7?.importance})`);
  }

  // --- importance clamping ---
  {
    const rNeg = testAdapter.testValidateFact({ text: 'test fact', importance: -5 });
    assert(rNeg?.importance === 1, `Base: importance -5 clamped to 1 (got ${rNeg?.importance})`);

    const rHuge = testAdapter.testValidateFact({ text: 'test fact', importance: 100 });
    assert(rHuge?.importance === 10, `Base: importance 100 clamped to 10 (got ${rHuge?.importance})`);
  }

  // --- importance default ---
  {
    const rDefault = testAdapter.testValidateFact({ text: 'test fact' });
    assert(rDefault?.importance === 5, `Base: missing importance defaults to 5 (got ${rDefault?.importance})`);
  }

  // --- source defaults to adapter's source ---
  {
    const result = testAdapter.testValidateFact({ text: 'test fact' });
    assert(result?.source === 'mem0', 'Base: source defaults to adapter source');

    const withSource = testAdapter.testValidateFact({ text: 'test fact', source: 'mcp-memory' });
    assert(withSource?.source === 'mcp-memory', 'Base: explicit source preserved');
  }

  // --- validateFacts batch ---
  {
    const rawFacts: Partial<NormalizedFact>[] = [
      { text: 'Valid fact one' },
      { text: '' },               // invalid
      { text: 'Valid fact two' },
      { text: 'xy' },             // too short
      { text: 'Valid fact three' },
    ];

    const { facts, invalidCount } = testAdapter.testValidateFacts(rawFacts);
    assert(facts.length === 3, `Base: validateFacts keeps 3 valid out of 5 (got ${facts.length})`);
    assert(invalidCount === 2, `Base: validateFacts counts 2 invalid (got ${invalidCount})`);
  }

  // =========================================================================
  // getAdapter factory
  // =========================================================================

  console.log('# getAdapter factory');

  // --- valid sources ---
  {
    const mem0 = getAdapter('mem0');
    assert(mem0 instanceof Mem0Adapter, 'getAdapter("mem0") returns Mem0Adapter');

    const mcp = getAdapter('mcp-memory');
    assert(mcp instanceof MCPMemoryAdapter, 'getAdapter("mcp-memory") returns MCPMemoryAdapter');
  }

  // --- unknown source throws ---
  {
    assertThrows(
      () => getAdapter('nonexistent' as ImportSource),
      'getAdapter throws on unknown source',
    );
  }

  // --- error message lists valid sources ---
  {
    try {
      getAdapter('bogus' as ImportSource);
      assert(false, 'getAdapter should throw for bogus source');
    } catch (e: unknown) {
      const msg = (e as Error).message;
      assert(msg.includes('mem0'), 'getAdapter error lists "mem0" as valid source');
      assert(msg.includes('mcp-memory'), 'getAdapter error lists "mcp-memory" as valid source');
    }
  }

  // =========================================================================
  // Summary
  // =========================================================================

  console.log(`\n1..${testNum}`);
  console.log(`# pass: ${passed}`);
  console.log(`# fail: ${failed}`);

  if (failed > 0) {
    console.log('\nFAILED');
    process.exit(1);
  } else {
    console.log('\nALL TESTS PASSED');
    process.exit(0);
  }
}

runTests().catch((err) => {
  console.error('Test runner failed:', err);
  process.exit(1);
});
