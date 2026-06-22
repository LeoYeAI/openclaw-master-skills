#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const rag = require('../lib/openai-rag');

function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (!next || next.startsWith('--')) out[key] = true;
      else {
        out[key] = next;
        i += 1;
      }
    } else {
      out._.push(a);
    }
  }
  return out;
}

function parseIntArg(v, fallback) {
  if (v == null || v === '') return fallback;
  const n = Number.parseInt(v, 10);
  if (Number.isNaN(n)) throw new Error(`Invalid integer: ${v}`);
  return n;
}

function loadDataset(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  if (filePath.endsWith('.jsonl')) {
    return raw
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter(Boolean)
      .map((l, idx) => {
        try {
          return JSON.parse(l);
        } catch (err) {
          throw new Error(`Invalid JSONL at line ${idx + 1}: ${err.message}`);
        }
      });
  }
  const parsed = JSON.parse(raw);
  if (!Array.isArray(parsed)) throw new Error('Dataset JSON must be an array');
  return parsed;
}

function expectedKeysFor(item) {
  const arr = [];
  if (item.expected_key) arr.push(String(item.expected_key));
  if (item.expected_pattern_key) arr.push(String(item.expected_pattern_key));
  if (item.expected_id) arr.push(String(item.expected_id));
  if (Array.isArray(item.expected_keys)) arr.push(...item.expected_keys.map(String));
  return Array.from(new Set(arr));
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const datasetPath = path.resolve(args.dataset || path.join(__dirname, '..', 'tests', 'fixtures', 'memory-eval-sample.jsonl'));
  const k = parseIntArg(args.k, 5);
  const limit = parseIntArg(args.limit, Math.max(10, k));
  const minSimilarity = args.minSimilarity == null ? 0.15 : Number.parseFloat(args.minSimilarity);
  const context = args.context || null;

  const dataset = loadDataset(datasetPath);
  let queries = 0;
  let hitAtK = 0;
  let sumTopSimilarity = 0;
  let topSimilarityCount = 0;
  let duplicateRows = 0;
  let reducedByPattern = 0;
  const details = [];

  for (const item of dataset) {
    if (!item || !item.query) continue;
    queries += 1;
    const rows = await rag.search(item.query, {
      limit,
      minSimilarity: Number.isFinite(minSimilarity) ? minSimilarity : 0.15,
      contextFilter: item.context || context,
      tierFilter: item.tier || null,
      minImportance: item.minImportance || 0
    });
    const topK = rows.slice(0, k);
    const topSimilarity = topK[0] ? Number(topK[0].similarity || 0) : null;
    if (topSimilarity != null) {
      sumTopSimilarity += topSimilarity;
      topSimilarityCount += 1;
    }

    const expected = expectedKeysFor(item);
    const matched = expected.length
      ? topK.some((r) => expected.includes(String(r.pattern_key)) || expected.includes(String(r.id)))
      : null;
    if (matched) hitAtK += 1;

    const uniquePatternOrId = new Set(topK.map((r) => r.pattern_key || `id:${r.id}`));
    duplicateRows += Math.max(0, topK.length - uniquePatternOrId.size);
    reducedByPattern += Math.max(0, topK.length - uniquePatternOrId.size);

    details.push({
      query: item.query,
      expected_keys: expected,
      matched,
      top_similarity: topSimilarity,
      top_ids: topK.map((r) => r.id),
      top_pattern_keys: topK.map((r) => r.pattern_key || null)
    });
  }

  const payload = {
    ok: true,
    dataset: path.relative(process.cwd(), datasetPath),
    queries,
    k,
    limit,
    metrics: {
      hit_at_k_proxy: queries ? Number((hitAtK / queries).toFixed(4)) : null,
      avg_top_similarity: topSimilarityCount ? Number((sumTopSimilarity / topSimilarityCount).toFixed(4)) : null,
      duplicates_reduced: reducedByPattern,
      duplicate_rows_in_topk: duplicateRows
    },
    details
  };

  if (args.json) {
    console.log(JSON.stringify(payload, null, 2));
    return;
  }

  console.log(`BrainX memory eval`);
  console.log(`dataset: ${payload.dataset}`);
  console.log(`queries: ${queries}, k=${k}, limit=${limit}`);
  console.log(`hit@k proxy: ${payload.metrics.hit_at_k_proxy}`);
  console.log(`avg top similarity: ${payload.metrics.avg_top_similarity}`);
  console.log(`duplicates reduced (top-k by pattern collapse proxy): ${payload.metrics.duplicates_reduced}`);
}

main().catch((err) => {
  console.error(err.stack || err.message || err);
  process.exit(1);
});
