#!/usr/bin/env node
/**
 * export-projects-overview.mjs (taskflow-009)
 * 
 * Reads the TaskFlow SQLite DB and emits a clean JSON summary to stdout.
 * 
 * Output shape:
 *   {
 *     exported_at: ISO string,
 *     projects: [ { id, name, description, status, task_counts, progress_pct } ],
 *     recent_transitions: [ { task_id, from_status, to_status, reason, at } ]
 *   }
 * 
 * Usage:
 *   node scripts/export-projects-overview.mjs
 *   node scripts/export-projects-overview.mjs | jq .
 */

import { DatabaseSync } from 'node:sqlite'
import path from 'node:path'
import { existsSync } from 'node:fs'

// ── DB path resolution ─────────────────────────────────────────────────────
const workspace = process.env.OPENCLAW_WORKSPACE || process.cwd()
const dbPath = path.join(workspace, 'memory', 'taskflow.sqlite')

if (!existsSync(dbPath)) {
  process.stderr.write(
    `[taskflow-export] DB not found at: ${dbPath}\n` +
    `  Run 'taskflow init' to bootstrap the database.\n`
  )
  process.exit(1)
}

const db = new DatabaseSync(dbPath)
db.exec('PRAGMA foreign_keys = ON')
db.exec('PRAGMA journal_mode = WAL')

// ── Fetch projects ─────────────────────────────────────────────────────────
const projects = db
  .prepare('SELECT id, name, description, status FROM projects ORDER BY id')
  .all()

// ── Task counts per project ────────────────────────────────────────────────
const ALL_STATUSES = ['in_progress', 'pending_validation', 'backlog', 'blocked', 'done']

const countRows = db
  .prepare(`
    SELECT project_id, status, COUNT(*) AS cnt
    FROM tasks_v2
    GROUP BY project_id, status
  `)
  .all()

// Build lookup: { project_id: { status: count } }
const countsByProject = {}
for (const row of countRows) {
  if (!countsByProject[row.project_id]) countsByProject[row.project_id] = {}
  countsByProject[row.project_id][row.status] = row.cnt
}

// ── Assemble project objects ───────────────────────────────────────────────
const projectsOut = projects.map((p) => {
  const counts = countsByProject[p.id] || {}

  const task_counts = {
    in_progress:         counts.in_progress         ?? 0,
    pending_validation:  counts.pending_validation  ?? 0,
    backlog:             counts.backlog              ?? 0,
    blocked:             counts.blocked              ?? 0,
    done:                counts.done                ?? 0,
  }

  const total = Object.values(task_counts).reduce((s, n) => s + n, 0)
  const progress_pct = total > 0
    ? Math.round((task_counts.done / total) * 10000) / 100   // 2 decimal places
    : 0

  return {
    id:           p.id,
    name:         p.name,
    description:  p.description,
    status:       p.status,
    task_counts,
    progress_pct,
  }
})

// ── Recent transitions (last 20) ───────────────────────────────────────────
const recentTransitions = db
  .prepare(`
    SELECT task_id, from_status, to_status, reason, at
    FROM task_transitions_v2
    ORDER BY id DESC
    LIMIT 20
  `)
  .all()

// Reverse so oldest-first within the window (more natural for consumers)
recentTransitions.reverse()

// ── Output ─────────────────────────────────────────────────────────────────
const output = {
  exported_at:         new Date().toISOString(),
  projects:            projectsOut,
  recent_transitions:  recentTransitions,
}

process.stdout.write(JSON.stringify(output, null, 2) + '\n')
