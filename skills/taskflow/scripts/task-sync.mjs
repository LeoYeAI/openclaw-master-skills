#!/usr/bin/env node
/**
 * task-sync.mjs -- Sync task markdown files to/from SQLite
 *
 * Usage:
 *   node scripts/task-sync.mjs files-to-db     # parse markdown, update DB
 *   node scripts/task-sync.mjs check            # detect drift, exit 1 if mismatch
 *   node scripts/task-sync.mjs db-to-files      # project DB state into markdown
 *
 * Environment:
 *   OPENCLAW_WORKSPACE  Path to the workspace root (defaults to process.cwd())
 */
import { DatabaseSync } from 'node:sqlite'
import { readFileSync, writeFileSync, readdirSync, existsSync } from 'node:fs'
import path from 'node:path'
import { createHash } from 'node:crypto'

// === PATHS (taskflow-001: portable, no hardcoded paths) ===
const workspace = process.env.OPENCLAW_WORKSPACE || process.cwd()
const dbPath    = path.join(workspace, 'memory', 'taskflow.sqlite')
const tasksDir  = path.join(workspace, 'tasks')

const mode = process.argv[2] || 'check'
if (!['files-to-db', 'check', 'db-to-files'].includes(mode)) {
  console.error('Usage: node scripts/task-sync.mjs [files-to-db|check|db-to-files]')
  process.exit(1)
}

// === STARTUP CHECKS (taskflow-020: clear errors for missing paths) ===
if (!existsSync(workspace)) {
  console.error(`ERROR: Workspace directory not found: ${workspace}`)
  console.error('Set OPENCLAW_WORKSPACE to your workspace root and try again.')
  process.exit(1)
}
if (!existsSync(tasksDir)) {
  console.error(`ERROR: Tasks directory not found: ${tasksDir}`)
  console.error(`Create it with: mkdir -p "${tasksDir}"`)
  process.exit(1)
}
if (!existsSync(dbPath)) {
  console.error(`ERROR: Database file not found: ${dbPath}`)
  console.error('Run init-db.mjs first to create the database schema.')
  process.exit(1)
}

const db = new DatabaseSync(dbPath)
db.exec('PRAGMA foreign_keys = ON')

// === LOCK (taskflow-002: atomic single-UPDATE acquisition) ===
let lockAcquired = false

function acquireLock() {
  const owner = `task-sync:${mode}`
  const until = new Date(Date.now() + 60_000).toISOString() // 60s TTL

  // Ensure the singleton row exists
  db.exec(`INSERT OR IGNORE INTO sync_state (id, lock_owner, lock_until) VALUES (1, NULL, NULL)`)

  // Single atomic UPDATE: succeeds only when no valid lock is held
  const result = db.prepare(`
    UPDATE sync_state
    SET lock_owner = ?, lock_until = ?
    WHERE id = 1
      AND (lock_owner IS NULL OR lock_until < datetime('now'))
  `).run(owner, until)

  if (result.changes === 0) {
    const row = db.prepare('SELECT lock_owner, lock_until FROM sync_state WHERE id = 1').get()
    console.error(`Sync locked by ${row?.lock_owner} until ${row?.lock_until}`)
    process.exit(1)
  }

  lockAcquired = true
}

function releaseLock(result) {
  const now = new Date().toISOString()
  db.prepare(
    'UPDATE sync_state SET lock_owner = NULL, lock_until = NULL, last_sync_at = ?, last_result = ? WHERE id = 1'
  ).run(now, result)
  lockAcquired = false
}

// === SIGNAL HANDLERS (taskflow-019: release lock on exit) ===
function handleSignal(signal) {
  if (lockAcquired) {
    try { releaseLock(`interrupted: ${signal}`) } catch (_) {}
  }
  process.exit(signal === 'SIGTERM' ? 0 : 130)
}
process.on('SIGTERM', () => handleSignal('SIGTERM'))
process.on('SIGINT',  () => handleSignal('SIGINT'))

// === PARSE MARKDOWN ===
const STATUS_MAP = {
  'in progress':        'in_progress',
  'pending validation': 'pending_validation',
  'backlog':            'backlog',
  'done':               'done',
  'blocked':            'blocked',
}

const TASK_RE = /^- \[([ x])\] \(task:([a-z0-9-]+)\)\s*(?:\[([^\]]*)\])?\s*(?:\[([^\]]*)\])?\s*(.+)$/

function parseTaskFile(filePath) {
  const content = readFileSync(filePath, 'utf8')
  const lines   = content.split(/\r?\n/)
  const tasks   = []
  let currentStatus = null
  const slug = path.basename(filePath).replace(/-tasks\.md$/, '')

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    // Section header
    const headerMatch = line.match(/^## (.+)$/)
    if (headerMatch) {
      const normalized = headerMatch[1].trim().toLowerCase()
      currentStatus = STATUS_MAP[normalized] || null
      continue
    }

    if (!currentStatus) continue

    const taskMatch = line.match(TASK_RE)
    if (taskMatch) {
      const [, , id, tag1, tag2, title] = taskMatch

      // Parse priority and model from tags
      let priority = 'P2', model = null
      for (const tag of [tag1, tag2]) {
        if (!tag) continue
        if (/^P\d$/.test(tag)) priority = tag
        else model = tag
      }

      // Check for note on next line
      let notes = null
      if (i + 1 < lines.length) {
        const noteMatch = lines[i + 1].match(/^\s+- note:\s*(.+)$/)
        if (noteMatch) notes = noteMatch[1].trim()
      }

      tasks.push({
        id,
        project_id: slug,
        title: title.trim(),
        status: currentStatus,
        priority,
        owner_model: model,
        notes,
        source_file: `tasks/${slug}-tasks.md`,
      })
    }
  }
  return tasks
}

function parseAllFiles() {
  const files    = readdirSync(tasksDir).filter(f => f.endsWith('-tasks.md'))
  const allTasks = []
  for (const f of files) {
    allTasks.push(...parseTaskFile(path.join(tasksDir, f)))
  }
  return allTasks
}

// === DB READ ===
function getDbTasks() {
  return db.prepare(
    'SELECT id, project_id, title, status, priority, owner_model, notes, source_file FROM tasks_v2 ORDER BY id'
  ).all()
}

// === HASH (taskflow-012: include notes field) ===
function hashTasks(tasks) {
  const sorted = [...tasks].sort((a, b) => a.id.localeCompare(b.id))
  const data   = sorted
    .map(t => `${t.id}|${t.status}|${t.priority}|${t.owner_model || ''}|${t.title}|${t.notes || ''}`)
    .join('\n')
  return createHash('sha256').update(data).digest('hex').slice(0, 16)
}

// === DIFF ===
function diffTasks(fileTasks, dbTasks) {
  const fileMap = new Map(fileTasks.map(t => [t.id, t]))
  const dbMap   = new Map(dbTasks.map(t => [t.id, t]))
  const diffs   = []

  for (const [id, ft] of fileMap) {
    const dt = dbMap.get(id)
    if (!dt) {
      diffs.push({ type: 'file_only', id, task: ft })
    } else {
      const changes = []
      if (ft.status !== dt.status) changes.push(`status: ${dt.status} → ${ft.status}`)
      if (ft.priority !== dt.priority) changes.push(`priority: ${dt.priority} → ${ft.priority}`)
      if ((ft.owner_model || null) !== (dt.owner_model || null)) changes.push(`model: ${dt.owner_model} → ${ft.owner_model}`)
      if (ft.title !== dt.title) changes.push('title changed')
      if (changes.length) diffs.push({ type: 'changed', id, changes, fileTask: ft, dbTask: dt })
    }
  }

  for (const [id] of dbMap) {
    if (!fileMap.has(id)) {
      diffs.push({ type: 'db_only', id, task: dbMap.get(id) })
    }
  }

  return diffs
}

// === WRITE TO DB ===
function syncFilesToDb(fileTasks, dbTasks, diffs) {
  // Auto-create projects referenced in files but missing from the projects table.
  const knownProjects  = new Set(db.prepare('SELECT id FROM projects').all().map(r => r.id))
  const upsertProject  = db.prepare(`
    INSERT OR IGNORE INTO projects (id, name, description, status, source_file)
    VALUES (?, ?, '', 'active', ?)
  `)
  const missingProjects = new Set()

  for (const t of fileTasks) {
    if (!knownProjects.has(t.project_id) && !missingProjects.has(t.project_id)) {
      missingProjects.add(t.project_id)
      const name = t.project_id.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
      upsertProject.run(t.project_id, name, `tasks/${t.project_id}-tasks.md`)
      console.log(`  Auto-created missing project: ${t.project_id} ("${name}")`)
    }
  }

  const upsert = db.prepare(`
    INSERT INTO tasks_v2 (id, project_id, title, status, priority, owner_model, notes, source_file, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'))
    ON CONFLICT(id) DO UPDATE SET
      title       = excluded.title,
      status      = excluded.status,
      priority    = excluded.priority,
      owner_model = excluded.owner_model,
      notes       = COALESCE(excluded.notes, tasks_v2.notes),
      source_file = excluded.source_file,
      updated_at  = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  `)
  const insertTransition = db.prepare(`
    INSERT INTO task_transitions_v2 (task_id, from_status, to_status, reason, actor)
    VALUES (?, ?, ?, ?, 'sync')
  `)

  let updated = 0, added = 0

  for (const diff of diffs) {
    if (diff.type === 'file_only') {
      const t = diff.task
      upsert.run(t.id, t.project_id, t.title, t.status, t.priority, t.owner_model, t.notes, t.source_file)
      insertTransition.run(t.id, null, t.status, 'added via file sync')
      added++
    } else if (diff.type === 'changed') {
      const t = diff.fileTask
      upsert.run(t.id, t.project_id, t.title, t.status, t.priority, t.owner_model, t.notes, t.source_file)
      if (diff.dbTask.status !== t.status) {
        insertTransition.run(t.id, diff.dbTask.status, t.status, `file sync: ${diff.changes.join(', ')}`)
      }
      updated++
    }
    // db_only tasks stay in DB (no silent drops)
  }

  // Update hashes
  const allFileTasks = parseAllFiles()
  const allDbTasks   = getDbTasks()
  db.prepare('UPDATE sync_state SET files_hash = ?, db_hash = ? WHERE id = 1').run(
    hashTasks(allFileTasks), hashTasks(allDbTasks)
  )

  return { added, updated, dbOnly: diffs.filter(d => d.type === 'db_only').length }
}

// === WRITE TO FILES (taskflow-003: blocked is first-class) ===
const STATUS_ORDER = ['in_progress', 'pending_validation', 'blocked', 'backlog', 'done']
const STATUS_HEADERS = {
  in_progress:        'In Progress',
  pending_validation: 'Pending Validation',
  blocked:            'Blocked',
  backlog:            'Backlog',
  done:               'Done',
}

function projectDbToFiles(dbTasks) {
  const byProject = new Map()
  for (const t of dbTasks) {
    if (!byProject.has(t.project_id)) byProject.set(t.project_id, [])
    byProject.get(t.project_id).push(t)
  }

  // Preserve existing file headers (everything before the first ## section)
  const files   = readdirSync(tasksDir).filter(f => f.endsWith('-tasks.md'))
  const headers = new Map()
  for (const f of files) {
    const content = readFileSync(path.join(tasksDir, f), 'utf8')
    const slug    = f.replace(/-tasks\.md$/, '')
    const lines   = content.split(/\r?\n/)
    const headerLines = []
    for (const line of lines) {
      if (line.startsWith('## ')) break
      headerLines.push(line)
    }
    headers.set(slug, headerLines.join('\n').trimEnd())
  }

  // All project slugs from DB
  const slugs = db.prepare('SELECT id FROM projects ORDER BY id').all().map(r => r.id)
  let filesWritten = 0

  for (const slug of slugs) {
    const tasks  = byProject.get(slug) || []
    const header = headers.get(slug) || `# Tasks: ${slug}`

    let md = header + '\n\n'
    for (const section of STATUS_ORDER) {
      md += `## ${STATUS_HEADERS[section]}\n`
      const sectionTasks = tasks
        .filter(t => t.status === section)
        .sort((a, b) => a.priority.localeCompare(b.priority) || a.id.localeCompare(b.id))

      if (sectionTasks.length === 0) {
        md += '\n'
      } else {
        for (const t of sectionTasks) {
          const checkbox = t.status === 'done' ? '[x]' : '[ ]'
          const modelTag = t.owner_model ? ` [${t.owner_model}]` : ''
          md += `- ${checkbox} (task:${t.id}) [${t.priority}]${modelTag} ${t.title}\n`
          if (t.notes) md += `  - note: ${t.notes}\n`
        }
        md += '\n'
      }
    }

    writeFileSync(path.join(tasksDir, `${slug}-tasks.md`), md)
    filesWritten++
  }

  return { filesWritten }
}

// === MAIN ===
try {
  if (mode !== 'check') acquireLock()

  const fileTasks = parseAllFiles()
  const dbTasks   = getDbTasks()
  const diffs     = diffTasks(fileTasks, dbTasks)

  if (mode === 'check') {
    const fileHash = hashTasks(fileTasks)
    const dbHash   = hashTasks(dbTasks)
    if (diffs.length === 0) {
      console.log(`OK: ${fileTasks.length} tasks in sync (hash: ${fileHash})`)
      process.exit(0)
    } else {
      console.log(`DRIFT DETECTED: ${diffs.length} differences`)
      console.log(`  File hash: ${fileHash}`)
      console.log(`  DB hash:   ${dbHash}`)
      for (const d of diffs) {
        if (d.type === 'file_only')  console.log(`  + ${d.id} (in files, not DB)`)
        else if (d.type === 'db_only') console.log(`  - ${d.id} (in DB, not files)`)
        else console.log(`  ~ ${d.id}: ${d.changes.join(', ')}`)
      }
      process.exit(1)
    }
  } else if (mode === 'files-to-db') {
    const result = syncFilesToDb(fileTasks, dbTasks, diffs)
    console.log(`Synced files → DB: ${result.added} added, ${result.updated} updated, ${result.dbOnly} DB-only preserved`)
    releaseLock('ok')
  } else if (mode === 'db-to-files') {
    const freshDbTasks = getDbTasks()
    const result       = projectDbToFiles(freshDbTasks)
    console.log(`Projected DB → files: ${result.filesWritten} files written`)
    releaseLock('ok')
  }
} catch (err) {
  if (mode !== 'check') {
    try { releaseLock(`failed: ${err.message}`) } catch (_) {}
  }
  console.error(err)
  process.exit(1)
}
