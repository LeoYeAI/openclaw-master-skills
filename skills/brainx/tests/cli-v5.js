const assert = require('assert');
const cli = require('../lib/cli');
const phase2 = require('../lib/brainx-phase2');

function makeIo() {
  const logs = [];
  let stdout = '';
  return {
    logs,
    getStdout: () => stdout,
    deps: {
      log: (s) => logs.push(String(s)),
      err: (s) => logs.push(`ERR:${String(s)}`),
      stdout: { write: (s) => { stdout += String(s); } }
    }
  };
}

async function testCmdAddMetadata() {
  const io = makeIo();
  let storedMemory;
  const rag = {
    async storeMemory(memory) {
      storedMemory = memory;
      return { id: 'existing_by_pattern', pattern_key: memory.pattern_key };
    }
  };

  await cli.cmdAdd({
    type: 'learning',
    content: 'Need stricter retry handling',
    context: 'proj',
    tier: 'hot',
    importance: '8',
    tags: 'a,b',
    status: 'in_progress',
    category: 'best_practice',
    patternKey: 'retry.loop',
    recurrenceCount: '3',
    resolutionNotes: 'track in runbook'
  }, { rag, ...io.deps });

  assert.strictEqual(storedMemory.pattern_key, 'retry.loop');
  assert.strictEqual(storedMemory.status, 'in_progress');
  assert.strictEqual(storedMemory.category, 'best_practice');
  assert.strictEqual(storedMemory.recurrence_count, 3);
  assert.deepStrictEqual(storedMemory.tags, ['a', 'b']);

  const payload = JSON.parse(io.logs[0]);
  assert.deepStrictEqual(payload, { ok: true, id: 'existing_by_pattern', pattern_key: 'retry.loop' });
}

async function testCmdSearchContractAndLogging() {
  const io = makeIo();
  const logEvents = [];
  const rag = {
    async search(query, opts) {
      assert.strictEqual(query, 'find memory');
      assert.strictEqual(opts.limit, 5);
      return [
        { id: 'm1', content: 'x', similarity: 0.9, score: 1.1 },
        { id: 'm2', content: 'y', similarity: 0.5, score: 0.6 }
      ];
    },
    async logQueryEvent(evt) {
      logEvents.push(evt);
    }
  };

  await cli.cmdSearch({ query: 'find memory', limit: '5', minSimilarity: '0.2' }, { rag, ...io.deps });

  const payload = JSON.parse(io.logs[0]);
  assert.strictEqual(payload.ok, true);
  assert.strictEqual(payload.results.length, 2);
  assert.strictEqual(logEvents.length, 1);
  assert.strictEqual(logEvents[0].kind, 'search');
  assert.strictEqual(logEvents[0].resultsCount, 2);
  assert.ok(logEvents[0].avgSimilarity >= 0.69 && logEvents[0].avgSimilarity <= 0.71);
}

async function testCmdInjectGuardrailsAndLogging() {
  const io = makeIo();
  const calls = [];
  const logEvents = [];
  const rag = {
    async search(query, opts) {
      calls.push({ query, opts });
      if (opts.tierFilter === 'hot') {
        return [
          { id: 'a', similarity: 0.8, score: 0.9, importance: 9, tier: 'hot', type: 'note', agent: 'coder', context: 'ctx', content: 'HOT content line 1\nline2' },
          { id: 'dup', similarity: 0.7, score: 0.4, importance: 6, tier: 'hot', type: 'note', agent: 'coder', context: 'ctx', content: 'duplicate hot' }
        ];
      }
      return [
        { id: 'dup', similarity: 0.6, score: 0.5, importance: 6, tier: 'warm', type: 'note', agent: 'coder', context: 'ctx', content: 'duplicate warm' },
        { id: 'b', similarity: 0.5, score: 0.2, importance: 5, tier: 'warm', type: 'note', agent: 'coder', context: 'ctx', content: 'LOW SCORE SHOULD FILTER' }
      ];
    },
    async logQueryEvent(evt) {
      logEvents.push(evt);
    }
  };

  await cli.cmdInject({ query: 'inject please', limit: '5', maxTotalChars: '90', minScore: '0.3' }, { rag, ...io.deps });

  assert.strictEqual(calls.length, 2);
  assert.ok(calls.every(c => c.opts.minSimilarity === 0.15));
  const out = io.getStdout();
  assert.ok(out.includes('HOT content'));
  assert.ok(!out.includes('LOW SCORE SHOULD FILTER'));
  assert.ok(out.length <= 90);
  assert.strictEqual(logEvents.length, 1);
  assert.strictEqual(logEvents[0].kind, 'inject');
  assert.strictEqual(logEvents[0].resultsCount, 2);
}

async function testCmdResolveLifecycleUpdate() {
  const io = makeIo();
  const queries = [];
  const db = {
    async query(sql, params) {
      queries.push({ sql, params });
      if (/UPDATE brainx_memories/.test(sql)) {
        return {
          rowCount: 1,
          rows: [{ id: 'm1', pattern_key: 'pk1', status: params[1], resolved_at: params[2], promoted_to: params[3], resolution_notes: params[4] }]
        };
      }
      return { rowCount: 1, rows: [] };
    }
  };

  await cli.cmdResolve({ id: 'm1', status: 'resolved', resolutionNotes: 'fixed' }, { db, ...io.deps });

  assert.strictEqual(queries.length, 2);
  assert.ok(/UPDATE brainx_memories/.test(queries[0].sql));
  assert.ok(/UPDATE brainx_patterns/.test(queries[1].sql));
  assert.strictEqual(queries[0].params[0], 'm1');
  assert.strictEqual(queries[0].params[1], 'resolved');
  assert.ok(queries[0].params[2]);
  const payload = JSON.parse(io.logs[0]);
  assert.strictEqual(payload.updated, 1);
}

async function testPromoteCandidatesDefaultsAndJson() {
  const io = makeIo();
  let lastParams;
  const db = {
    async query(sql, params) {
      assert.ok(sql.includes('FROM brainx_patterns'));
      lastParams = params;
      return {
        rows: [
          { pattern_key: 'pk1', recurrence_count: 4, last_status: 'pending', representative_content: 'x' }
        ]
      };
    }
  };

  await cli.cmdPromoteCandidates({}, { db, ...io.deps });

  assert.deepStrictEqual(lastParams, [3, 30, 50]);
  const payload = JSON.parse(io.logs[0]);
  assert.deepStrictEqual(payload.thresholds, { minRecurrence: 3, days: 30 });
  assert.strictEqual(payload.count, 1);
}

async function testMetricsOutput() {
  const io = makeIo();
  let call = 0;
  const db = {
    async query(_sql, _params) {
      call += 1;
      const responses = [
        { rows: [{ key: 'pending', count: 2 }] },
        { rows: [{ key: 'learning', count: 1 }] },
        { rows: [{ key: 'warm', count: 2 }] },
        { rows: [{ pattern_key: 'pk1', recurrence_count: 5 }] },
        { rows: [{ query_kind: 'search', calls: 3, avg_duration_ms: '12.34' }] }
      ];
      return responses[call - 1];
    }
  };

  await cli.cmdMetrics({ days: '14', topPatterns: '5' }, { db, ...io.deps });
  const payload = JSON.parse(io.logs[0]);
  assert.strictEqual(payload.window_days, 14);
  assert.strictEqual(payload.top_recurring_patterns.length, 1);
  assert.strictEqual(payload.query_performance[0].query_kind, 'search');
}

async function testPiiScrubHelpers() {
  const scrubbed = phase2.scrubTextPII(
    'email me at jane@example.com or call (415) 555-1234 with sk-1234567890abcdef1234',
    { enabled: true, replacement: '[REDACTED]' }
  );
  assert.strictEqual(scrubbed.redacted, true);
  assert.ok(scrubbed.reasons.includes('email'));
  assert.ok(scrubbed.reasons.includes('phone'));
  assert.ok(scrubbed.reasons.some((r) => r.includes('key') || r.includes('openai')));
  assert.ok(!scrubbed.text.includes('jane@example.com'));
  const tags = phase2.mergeTagsWithMetadata(['a'], { redacted: true, reasons: ['email'] });
  assert.deepStrictEqual(tags, ['a', 'pii:redacted', 'pii:email']);
}

async function testSemanticDedupeMergePlanHelper() {
  const now = new Date('2026-02-24T00:00:00.000Z');
  const plan = phase2.deriveMergePlan(
    { id: 'm1', recurrence_count: 2, first_seen: new Date('2026-02-01T00:00:00.000Z'), last_seen: new Date('2026-02-20T00:00:00.000Z') },
    { recurrence_count: null, first_seen: null, last_seen: null },
    now
  );
  assert.strictEqual(plan.found, true);
  assert.strictEqual(plan.finalId, 'm1');
  assert.strictEqual(plan.finalRecurrence, 3);
  assert.strictEqual(plan.finalLastSeen.toISOString(), now.toISOString());
}

async function testPiiAllowlistContextHelper() {
  const cfg = {
    piiScrubEnabled: true,
    piiScrubAllowlistContexts: ['internal-safe', 'trusted']
  };
  assert.strictEqual(phase2.shouldScrubForContext('internal-safe', cfg), false);
  assert.strictEqual(phase2.shouldScrubForContext('other-context', cfg), true);
}

async function testLifecycleRunPromoteDegradeAndPatternSync() {
  const io = makeIo();
  const calls = [];
  const db = {
    async query(sql, params) {
      calls.push({ sql, params });
      if (calls.length === 1) return { rows: [{ id: 'p1' }] }; // promote preview
      if (calls.length === 2) return { rows: [{ id: 'd1' }] }; // degrade preview
      if (/UPDATE brainx_memories/.test(sql) && sql.includes("SET status = 'promoted'")) {
        return { rowCount: 1, rows: [{ id: 'p1', pattern_key: 'pk1', status: 'promoted' }] };
      }
      if (/UPDATE brainx_memories/.test(sql) && sql.includes("COALESCE(importance, 5) <= $2")) {
        return { rowCount: 1, rows: [{ id: 'd1', pattern_key: 'pk1', status: 'wont_fix' }] };
      }
      if (/UPDATE brainx_patterns/.test(sql)) {
        return { rowCount: 1, rows: [] };
      }
      throw new Error(`unexpected query: ${sql}`);
    }
  };

  await cli.cmdLifecycleRun({}, { db, ...io.deps });

  assert.ok(calls.some((c) => /UPDATE brainx_memories/.test(c.sql) && c.sql.includes("SET status = 'promoted'")));
  assert.ok(calls.some((c) => /UPDATE brainx_memories/.test(c.sql) && c.sql.includes("COALESCE(importance, 5) <= $2")));
  assert.ok(calls.some((c) => /UPDATE brainx_patterns/.test(c.sql)));
  const payload = JSON.parse(io.logs[0]);
  assert.strictEqual(payload.updated.promoted, 1);
  assert.strictEqual(payload.updated.degraded, 1);
}

async function run() {
  const tests = [
    testCmdAddMetadata,
    testCmdSearchContractAndLogging,
    testCmdInjectGuardrailsAndLogging,
    testCmdResolveLifecycleUpdate,
    testPromoteCandidatesDefaultsAndJson,
    testMetricsOutput,
    testPiiScrubHelpers,
    testSemanticDedupeMergePlanHelper,
    testPiiAllowlistContextHelper,
    testLifecycleRunPromoteDegradeAndPatternSync
  ];

  for (const t of tests) {
    await t();
  }

  console.log(`cli-v5 tests: ${tests.length} passed`);
}

run().catch((err) => {
  console.error(err.stack || err.message || err);
  process.exit(1);
});
