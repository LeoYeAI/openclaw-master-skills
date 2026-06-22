// BrainX V5 smoke test

const db = require('../lib/db');

(async () => {
  try {
    await db.health();
    const ext = await db.query(
      "select exists(select 1 from pg_extension where extname='vector') as has_vector"
    );
    const hasVector = ext.rows?.[0]?.has_vector;

    const tables = await db.query(
      "select count(*)::int as n from information_schema.tables where table_schema='public' and table_name like 'brainx_%'"
    );
    const nTables = tables.rows?.[0]?.n ?? 0;

    if (!hasVector) throw new Error('pgvector extension not installed in this database');
    if (nTables < 3) throw new Error(`schema not installed (found ${nTables} brainx_* tables)`);

    console.log('BrainX V5 health: OK');
    console.log(`- pgvector: ${hasVector ? 'yes' : 'no'}`);
    console.log(`- brainx tables: ${nTables}`);
    process.exit(0);
  } catch (err) {
    console.error('BrainX V5 health: FAIL');
    console.error(err?.message || err);
    process.exit(1);
  }
})();
