#!/usr/bin/env node
/**
 * init-db.mjs — TaskFlow SQLite bootstrap (idempotent)
 *
 * Reads schema/taskflow.sql and executes it against the TaskFlow SQLite DB.
 * Safe to run multiple times — all DDL uses IF NOT EXISTS.
 *
 * DB path resolution (in order):
 *   1. $OPENCLAW_WORKSPACE/memory/taskflow.sqlite
 *   2. process.cwd()/memory/taskflow.sqlite
 *
 * Usage:
 *   node scripts/init-db.mjs
 *   npm run init-db
 *
 * Requires: Node >=22.5 (node:sqlite / DatabaseSync)
 */

import { DatabaseSync } from 'node:sqlite';
import { readFileSync, mkdirSync, existsSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// ---------------------------------------------------------------------------
// Resolve paths
// ---------------------------------------------------------------------------

const __dirname = dirname(fileURLToPath(import.meta.url));
const schemaPath = resolve(__dirname, '..', 'schema', 'taskflow.sql');

const workspaceRoot = process.env.OPENCLAW_WORKSPACE
  ? process.env.OPENCLAW_WORKSPACE
  : process.cwd();

const memoryDir = join(workspaceRoot, 'memory');
const dbPath = join(memoryDir, 'taskflow.sqlite');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function log(msg) {
  const ts = new Date().toISOString();
  console.log(`[${ts}] ${msg}`);
}

function err(msg) {
  const ts = new Date().toISOString();
  console.error(`[${ts}] ERROR: ${msg}`);
}

/**
 * Split a SQL file into individual statements, stripping comments and blanks.
 * Handles multi-line statements and PRAGMA directives.
 */
function splitStatements(sql) {
  // Remove -- line comments
  const stripped = sql.replace(/--[^\n]*/g, '');
  // Split on semicolons, filter blank/whitespace-only entries
  return stripped
    .split(';')
    .map(s => s.trim())
    .filter(s => s.length > 0);
}

/**
 * Detect the statement type for human-readable logging.
 */
function describeStatement(stmt) {
  const upper = stmt.trimStart().toUpperCase();
  if (upper.startsWith('CREATE TABLE IF NOT EXISTS')) {
    const m = stmt.match(/CREATE TABLE IF NOT EXISTS\s+(\S+)/i);
    return m ? `CREATE TABLE IF NOT EXISTS ${m[1]}` : 'CREATE TABLE (IF NOT EXISTS)';
  }
  if (upper.startsWith('CREATE INDEX IF NOT EXISTS')) {
    const m = stmt.match(/CREATE INDEX IF NOT EXISTS\s+(\S+)/i);
    return m ? `CREATE INDEX IF NOT EXISTS ${m[1]}` : 'CREATE INDEX (IF NOT EXISTS)';
  }
  if (upper.startsWith('CREATE')) {
    return stmt.trimStart().split(/\s+/).slice(0, 4).join(' ');
  }
  if (upper.startsWith('INSERT OR IGNORE')) {
    const m = stmt.match(/INTO\s+(\S+)/i);
    return m ? `INSERT OR IGNORE INTO ${m[1]}` : 'INSERT OR IGNORE';
  }
  if (upper.startsWith('PRAGMA')) {
    return stmt.trimStart().split('\n')[0].trim();
  }
  return stmt.trimStart().split(/\s+/).slice(0, 3).join(' ');
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

log('TaskFlow init-db starting');
log(`Schema: ${schemaPath}`);
log(`DB:     ${dbPath}`);

// Ensure memory directory exists
if (!existsSync(memoryDir)) {
  mkdirSync(memoryDir, { recursive: true });
  log(`Created directory: ${memoryDir}`);
} else {
  log(`Directory exists:  ${memoryDir}`);
}

// Read schema
let schemaSQL;
try {
  schemaSQL = readFileSync(schemaPath, 'utf8');
} catch (e) {
  err(`Cannot read schema file: ${schemaPath}\n${e.message}`);
  process.exit(1);
}

// Open (or create) DB
let db;
try {
  db = new DatabaseSync(dbPath);
  log(`Opened DB (created if new): ${dbPath}`);
} catch (e) {
  err(`Cannot open SQLite DB at ${dbPath}\n${e.message}`);
  process.exit(1);
}

// Execute each statement
const statements = splitStatements(schemaSQL);
log(`Executing ${statements.length} SQL statement(s)...`);
console.log('');

let ok = 0;
let skipped = 0;

for (const stmt of statements) {
  const label = describeStatement(stmt);
  try {
    db.exec(stmt);
    log(`  ✓  ${label}`);
    ok++;
  } catch (e) {
    // PRAGMA errors on read-only pragmas are non-fatal; everything else is fatal.
    if (stmt.trim().toUpperCase().startsWith('PRAGMA')) {
      log(`  ~  ${label} (skipped — ${e.message})`);
      skipped++;
    } else {
      err(`Failed: ${label}\n       ${e.message}`);
      db.close?.();
      process.exit(1);
    }
  }
}

// Verify expected tables exist
const EXPECTED_TABLES = [
  'projects',
  'tasks_v2',
  'task_transitions_v2',
  'sync_state',
  'legacy_key_map',
];

console.log('');
log('Verifying tables...');

const tableRows = db
  .prepare("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
  .all();
const existingTables = new Set(tableRows.map(r => r.name));

let allPresent = true;
for (const t of EXPECTED_TABLES) {
  if (existingTables.has(t)) {
    log(`  ✓  table: ${t}`);
  } else {
    log(`  ✗  MISSING table: ${t}`);
    allPresent = false;
  }
}

// Verify singleton sync_state row
const syncRow = db.prepare('SELECT id FROM sync_state WHERE id = 1').get();
if (syncRow) {
  log(`  ✓  sync_state singleton row present`);
} else {
  log(`  ✗  sync_state singleton row MISSING`);
  allPresent = false;
}

// Summary
console.log('');
if (allPresent) {
  log(`init-db complete — ${ok} statement(s) executed, ${skipped} skipped`);
  log(`TaskFlow DB is ready at: ${dbPath}`);
} else {
  err('init-db completed with warnings — some expected tables are missing');
  process.exit(1);
}
