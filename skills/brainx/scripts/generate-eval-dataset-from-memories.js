#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { Client } = require('pg');

async function main() {
  const outPath = process.argv[2] || path.join(__dirname, '..', 'tests', 'fixtures', 'memory-eval-real.jsonl');
  const limit = Number.parseInt(process.argv[3] || '80', 10);
  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) throw new Error('DATABASE_URL is required');

  const client = new Client({ connectionString: databaseUrl });
  await client.connect();
  try {
    const { rows } = await client.query(
      `SELECT id, context, content
       FROM brainx_memories
       WHERE superseded_by IS NULL
         AND content IS NOT NULL
       ORDER BY last_seen DESC NULLS LAST, created_at DESC
       LIMIT $1`,
      [limit]
    );

    const lines = rows.map((r) => {
      const content = String(r.content || '').replace(/\s+/g, ' ').trim();
      const query = content.length > 120 ? content.slice(0, 120) : content;
      return JSON.stringify({
        query,
        expected_id: r.id,
        context: r.context || null
      });
    });

    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, `${lines.join('\n')}\n`, 'utf8');
    console.log(JSON.stringify({ ok: true, outPath, count: lines.length }, null, 2));
  } finally {
    await client.end();
  }
}

main().catch((err) => {
  console.error(err.stack || err.message || err);
  process.exit(1);
});
