#!/usr/bin/env node
/**
 * apple-notes-export.mjs (taskflow-012)
 *
 * Generates an HTML project-status summary from TaskFlow markdown files and
 * writes it to an Apple Note via osascript.
 *
 * Config: $OPENCLAW_WORKSPACE/taskflow.config.json
 *   {
 *     "appleNotesId":     "x-coredata://...",   // persisted after first run
 *     "appleNotesFolder": "Notes",               // Notes folder name
 *     "appleNotesTitle":  "TaskFlow - Project Status"
 *   }
 *
 * Usage:
 *   node scripts/apple-notes-export.mjs
 *   taskflow notes
 *
 * macOS only — exits gracefully on other platforms.
 */

import { existsSync, readFileSync, writeFileSync, readdirSync } from 'node:fs'
import { execSync } from 'node:child_process'
import path from 'node:path'

// ── Platform guard ─────────────────────────────────────────────────────────
if (process.platform !== 'darwin') {
  console.log('[apple-notes-export] Skipping: Apple Notes sync is macOS only.')
  process.exit(0)
}

// ── Paths ──────────────────────────────────────────────────────────────────
const workspace  = process.env.OPENCLAW_WORKSPACE || process.cwd()
const configPath = path.join(workspace, 'taskflow.config.json')
const tasksDir   = path.join(workspace, 'tasks')
const projectsFile = path.join(workspace, 'PROJECTS.md')

// ── Config helpers ─────────────────────────────────────────────────────────

/**
 * Read taskflow.config.json (returns {} if missing or unparseable).
 */
function readConfig() {
  if (!existsSync(configPath)) return {}
  try {
    return JSON.parse(readFileSync(configPath, 'utf8'))
  } catch {
    return {}
  }
}

/**
 * Merge `updates` into taskflow.config.json (non-destructive patch).
 */
function writeConfig(updates) {
  const current = readConfig()
  const merged  = { ...current, ...updates }
  writeFileSync(configPath, JSON.stringify(merged, null, 2) + '\n', 'utf8')
}

// ── Parse PROJECTS.md ──────────────────────────────────────────────────────

function parseProjects() {
  if (!existsSync(projectsFile)) return {}
  const lines = readFileSync(projectsFile, 'utf8').split('\n')
  const projects = {}
  let currentSlug = null

  for (const line of lines) {
    const h2 = line.match(/^## (.+)/)
    if (h2) {
      currentSlug = h2[1].trim()
      projects[currentSlug] = { name: currentSlug, desc: '' }
      continue
    }
    if (!currentSlug) continue
    const nameMatch = line.match(/^- Name: (.+)/)
    if (nameMatch) { projects[currentSlug].name = nameMatch[1].trim(); continue }
    const descMatch = line.match(/^- Description: (.+)/)
    if (descMatch) { projects[currentSlug].desc = descMatch[1].trim() }
  }
  return projects
}

// ── Parse task files ───────────────────────────────────────────────────────

function parseTasks(projects) {
  const result = { in_progress: [], pending: [], backlog: [], done: [], blocked: [] }

  if (!existsSync(tasksDir)) return result

  const files = readdirSync(tasksDir)
    .filter(f => f.endsWith('-tasks.md'))
    .sort()

  for (const file of files) {
    const slug     = file.replace('-tasks.md', '')
    const projName = projects[slug]?.name ?? slug
    const lines    = readFileSync(path.join(tasksDir, file), 'utf8').split('\n')

    let section = null
    for (const line of lines) {
      const trimmed = line.trim()
      if (trimmed.startsWith('## ')) {
        const h = trimmed.slice(3).toLowerCase()
        if (h.includes('in progress'))  section = 'in_progress'
        else if (h.includes('pending')) section = 'pending'
        else if (h.includes('backlog')) section = 'backlog'
        else if (h.includes('done'))    section = 'done'
        else if (h.includes('blocked')) section = 'blocked'
        else section = null
        continue
      }
      if (!trimmed.startsWith('- [') || section === null) continue

      // Strip checkbox, task ID, priority/owner tags
      let text = trimmed
        .replace(/^- \[.\]\s*/, '')
        .replace(/\(task:\S+\)\s*/g, '')
        .replace(/\[P\d\]\s*/g, '')
        .replace(/\[\S+\]\s*/g, '')
        .trim()
      if (!text) continue

      result[section].push(`${projName}: ${text}`)
    }
  }
  return result
}

// ── HTML generation ────────────────────────────────────────────────────────

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function ul(items) {
  if (!items || items.length === 0) {
    return '<ul><li><span style="color:#666;">None</span></li></ul>'
  }
  return '<ul>' + items.map(i => `<li>${escapeHtml(i)}</li>`).join('') + '</ul>'
}

function generateHtml(tasks, title) {
  const { in_progress, pending, backlog, done, blocked } = tasks
  const top   = [...in_progress, ...pending].slice(0, 5)
  const next3 = in_progress.length > 0 ? in_progress.slice(0, 3) : backlog.slice(0, 3)

  const now = new Date()
  const stamp = now.toLocaleString('en-US', {
    timeZone: 'America/Chicago',
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: true,
  }) + ' CST'

  return `<div style="font-family:-apple-system,Helvetica,Arial,sans-serif; line-height:1.35;">
<h1>${escapeHtml(title)}</h1>
<h2>🎯 Top Priorities</h2>${ul(top)}
<h2>🚧 In Progress (${in_progress.length})</h2>${ul(in_progress)}
<h2>⏳ Pending Validation (${pending.length})</h2>${ul(pending)}
<h2>📥 Backlog (top 12)</h2>${ul(backlog.slice(0, 12))}
<h2>✅ Recently Done</h2>${ul(done.slice(0, 10))}
<h2>🧱 Blockers</h2>${ul(blocked)}
<h2>▶️ Next 3 Actions</h2>${ul(next3)}
<p style="color:#888; font-size:0.85em;"><b>Updated:</b> ${escapeHtml(stamp)} &middot; Source: tasks/*.md</p>
</div>`
}

// ── AppleScript helpers ────────────────────────────────────────────────────

/**
 * Escape a string for embedding inside an AppleScript string literal.
 */
function asEscape(str) {
  // In AppleScript, backslash and double-quote need to be escaped for shell
  // We'll write HTML to a temp file and read it in AppleScript to avoid quoting issues.
  return str
}

const TMP_HTML = '/tmp/taskflow-apple-notes.html'

/**
 * Check whether a note with the given Core Data ID exists.
 * Returns true/false.
 */
function noteExists(noteId) {
  const script = `
tell application "Notes"
  try
    set n to note id "${noteId}"
    return (name of n) as text
  on error
    return "NOT_FOUND"
  end try
end tell
`
  try {
    const result = execSync(`/usr/bin/osascript -e '${script.replace(/'/g, "'\\''")}'`, {
      encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe']
    }).trim()
    return result !== 'NOT_FOUND'
  } catch {
    return false
  }
}

/**
 * Update an existing note by Core Data ID.
 */
function updateNote(noteId, title, html) {
  writeFileSync(TMP_HTML, html, 'utf8')
  const script = `
set noteBody to (do shell script "cat /tmp/taskflow-apple-notes.html")
tell application "Notes"
  try
    set targetNote to note id "${noteId}"
    set name of targetNote to "${title.replace(/"/g, '\\"')}"
    set body of targetNote to noteBody
    return (id of targetNote) as text
  on error errMsg
    error errMsg
  end try
end tell
`
  const result = execSync(`/usr/bin/osascript << 'OSASCRIPT'\n${script}\nOSASCRIPT`, {
    encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe']
  }).trim()
  return result
}

/**
 * Create a new note in the specified folder.
 * Returns the new note's Core Data ID.
 */
function createNote(title, html, folder) {
  writeFileSync(TMP_HTML, html, 'utf8')
  const script = `
set noteBody to (do shell script "cat /tmp/taskflow-apple-notes.html")
tell application "Notes"
  launch
  delay 0.5
  set targetFolder to missing value
  try
    set targetFolder to folder "${folder.replace(/"/g, '\\"')}"
  on error
    -- folder not found, use default account
  end try
  if targetFolder is missing value then
    set newNote to make new note with properties {name:"${title.replace(/"/g, '\\"')}", body:noteBody}
  else
    set newNote to make new note at targetFolder with properties {name:"${title.replace(/"/g, '\\"')}", body:noteBody}
  end if
  return (id of newNote) as text
end tell
`
  const result = execSync(`/usr/bin/osascript << 'OSASCRIPT'\n${script}\nOSASCRIPT`, {
    encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe']
  }).trim()
  return result
}

// ── Main ───────────────────────────────────────────────────────────────────

async function main() {
  const config = readConfig()
  const folder = config.appleNotesFolder ?? 'Notes'
  const title  = config.appleNotesTitle  ?? 'TaskFlow - Project Status'
  let   noteId = config.appleNotesId     ?? null

  // Parse content
  const projects = parseProjects()
  const tasks    = parseTasks(projects)
  const html     = generateHtml(tasks, title)

  const { in_progress, pending, backlog, done, blocked } = tasks
  console.log(`[apple-notes-export] ${in_progress.length} in-progress, ${backlog.length} backlog, ${done.length} done`)

  // Retry loop (up to 3 attempts)
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      if (noteId && noteExists(noteId)) {
        // Update existing note
        console.log(`[apple-notes-export] Updating existing note…`)
        updateNote(noteId, title, html)
        console.log(`[apple-notes-export] ✓ Note updated (${noteId})`)
        break
      } else {
        // Create new note (either no ID configured, or note was deleted)
        if (noteId) {
          console.log(`[apple-notes-export] Previous note not found — creating new note…`)
        } else {
          console.log(`[apple-notes-export] No note configured — creating new note in "${folder}"…`)
        }
        const newId = createNote(title, html, folder)
        if (!newId) throw new Error('osascript returned empty note ID')

        noteId = newId
        writeConfig({
          appleNotesId:     noteId,
          appleNotesFolder: folder,
          appleNotesTitle:  title,
        })
        console.log(`[apple-notes-export] ✓ Note created and ID saved to taskflow.config.json`)
        console.log(`[apple-notes-export]   ID: ${noteId}`)
        break
      }
    } catch (err) {
      console.error(`[apple-notes-export] Attempt ${attempt} failed: ${err.message}`)
      if (attempt < 3) {
        await new Promise(r => setTimeout(r, 2000))
      } else {
        console.error('[apple-notes-export] All retries exhausted. Note not updated.')
        process.exit(1)
      }
    }
  }
}

await main()
