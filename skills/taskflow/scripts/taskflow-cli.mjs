#!/usr/bin/env node
/**
 * taskflow — CLI entry point (taskflow-011)
 *
 * Commands:
 *   taskflow setup               Interactive first-run onboarding
 *   taskflow status              Pretty terminal summary (all projects)
 *   taskflow export              JSON export to stdout
 *   taskflow sync <mode>         Sync markdown ↔ SQLite (modes: files-to-db | db-to-files | check)
 *   taskflow init                Bootstrap SQLite schema
 *   taskflow install-daemon      Install periodic-sync daemon (LaunchAgent on macOS, systemd on Linux)
 *   taskflow add <project> <title> Create a new task in markdown (source of truth)
 *   taskflow list <project>      List tasks for a project (current tasks by default)
 *   taskflow help                Show this help
 */

import { DatabaseSync } from 'node:sqlite'
import { existsSync, mkdirSync, writeFileSync, readFileSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const SCRIPTS = path.resolve(__dirname, '..', 'scripts')

// Workspace / DB resolution
const workspace = process.env.OPENCLAW_WORKSPACE || process.cwd()
const dbPath    = path.join(workspace, 'memory', 'taskflow.sqlite')

// ── Colour / terminal helpers ─────────────────────────────────────────────
const isTTY = process.stdout.isTTY
const c = {
  reset:  isTTY ? '\x1b[0m'  : '',
  bold:   isTTY ? '\x1b[1m'  : '',
  dim:    isTTY ? '\x1b[2m'  : '',
  green:  isTTY ? '\x1b[32m' : '',
  yellow: isTTY ? '\x1b[33m' : '',
  blue:   isTTY ? '\x1b[34m' : '',
  cyan:   isTTY ? '\x1b[36m' : '',
  red:    isTTY ? '\x1b[31m' : '',
  gray:   isTTY ? '\x1b[90m' : '',
}

function badge(text, color) {
  return `${color}${text}${c.reset}`
}

// Unicode block progress bar  ▏▎▍▌▋▊▉█
const BLOCKS = ' ▏▎▍▌▋▊▉█'

function progressBar(pct, width = 20) {
  const filled   = Math.round((pct / 100) * width * 8)
  const fullBlks = Math.floor(filled / 8)
  const partial  = filled % 8
  const empty    = width - fullBlks - (partial > 0 ? 1 : 0)

  return (
    '█'.repeat(fullBlks) +
    (partial > 0 ? BLOCKS[partial] : '') +
    '░'.repeat(Math.max(0, empty))
  )
}

function statusColor(status) {
  switch (status) {
    case 'active':  return c.green
    case 'paused':  return c.yellow
    case 'done':    return c.gray
    default:        return c.reset
  }
}

// ── Commands ──────────────────────────────────────────────────────────────

// --- status ------------------------------------------------------------------
function cmdStatus() {
  if (!existsSync(dbPath)) {
    console.error(`${c.red}✗${c.reset} DB not found at: ${dbPath}`)
    console.error(`  Run ${c.bold}taskflow setup${c.reset} to get started, or ${c.bold}taskflow init${c.reset} to bootstrap the database.`)
    process.exit(1)
  }

  const db = new DatabaseSync(dbPath)
  db.exec('PRAGMA foreign_keys = ON')

  const projects = db
    .prepare('SELECT id, name, description, status FROM projects ORDER BY id')
    .all()

  if (projects.length === 0) {
    console.log(`${c.dim}No projects found. Add entries to PROJECTS.md and run: taskflow sync files-to-db${c.reset}`)
    return
  }

  const countRows = db
    .prepare('SELECT project_id, status, COUNT(*) AS cnt FROM tasks_v2 GROUP BY project_id, status')
    .all()

  const countsByProject = {}
  for (const row of countRows) {
    if (!countsByProject[row.project_id]) countsByProject[row.project_id] = {}
    countsByProject[row.project_id][row.status] = row.cnt
  }

  console.log()
  console.log(`${c.bold}${c.cyan}  TaskFlow — Project Overview${c.reset}`)
  console.log(`${c.gray}  ${'─'.repeat(60)}${c.reset}`)

  for (const p of projects) {
    const counts = countsByProject[p.id] || {}
    const ip  = counts.in_progress        ?? 0
    const pv  = counts.pending_validation ?? 0
    const bl  = counts.backlog            ?? 0
    const bk  = counts.blocked            ?? 0
    const dn  = counts.done               ?? 0
    const tot = ip + pv + bl + bk + dn
    const pct = tot > 0 ? Math.round((dn / tot) * 10000) / 100 : 0

    const statusStr = badge(` ${p.status} `, statusColor(p.status))

    console.log()
    console.log(`  ${c.bold}${p.name}${c.reset}  ${statusStr}  ${c.gray}(${p.id})${c.reset}`)
    if (p.description) {
      console.log(`  ${c.dim}${p.description}${c.reset}`)
    }

    // Progress bar
    const bar     = progressBar(pct, 24)
    const pctStr  = pct.toFixed(1).padStart(5)
    console.log(`  ${c.green}${bar}${c.reset}  ${c.bold}${pctStr}%${c.reset} done  ${c.gray}(${tot} tasks)${c.reset}`)

    // Task counts row
    const parts = []
    if (ip)  parts.push(`${c.blue}${ip} in-progress${c.reset}`)
    if (pv)  parts.push(`${c.yellow}${pv} pending-validation${c.reset}`)
    if (bk)  parts.push(`${c.red}${bk} blocked${c.reset}`)
    if (bl)  parts.push(`${c.dim}${bl} backlog${c.reset}`)
    if (dn)  parts.push(`${c.gray}${dn} done${c.reset}`)
    if (parts.length) {
      console.log(`  ${parts.join('  ')}`)
    } else {
      console.log(`  ${c.dim}no tasks yet${c.reset}`)
    }
  }

  console.log()
  console.log(`${c.gray}  ${'─'.repeat(60)}${c.reset}`)
  console.log(`${c.dim}  Workspace: ${workspace}${c.reset}`)
  console.log()
}

// --- export ------------------------------------------------------------------
async function cmdExport() {
  // Import the export script — its top-level code runs and writes JSON to stdout.
  await import(path.join(SCRIPTS, 'export-projects-overview.mjs'))
}

// --- sync --------------------------------------------------------------------
async function cmdSync(mode) {
  const VALID_MODES = ['files-to-db', 'db-to-files', 'check']
  if (!VALID_MODES.includes(mode)) {
    console.error(`${c.red}✗${c.reset} Unknown sync mode: ${JSON.stringify(mode)}`)
    console.error(`  Valid modes: ${VALID_MODES.join(' | ')}`)
    process.exit(1)
  }

  const syncScript = path.join(SCRIPTS, 'task-sync.mjs')
  if (!existsSync(syncScript)) {
    console.error(`${c.red}✗${c.reset} task-sync.mjs not found at: ${syncScript}`)
    process.exit(1)
  }

  // task-sync.mjs reads process.argv[2] for the mode.
  process.argv[2] = mode
  await import(syncScript)
}

// --- init --------------------------------------------------------------------
async function cmdInit() {
  const initScript = path.join(SCRIPTS, 'init-db.mjs')
  if (!existsSync(initScript)) {
    console.error(`${c.red}✗${c.reset} init-db.mjs not found at: ${initScript}`)
    process.exit(1)
  }
  await import(initScript)
}

// --- setup helpers -----------------------------------------------------------

/** Convert a human name to a lowercase-hyphenated slug. */
function toSlug(name) {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '')
}

/** Print a summary of what was created and what to do next. */
function printSetupSummary(createdFiles) {
  console.log()
  console.log(`${c.bold}${c.green}  ✓ TaskFlow setup complete!${c.reset}`)
  console.log()
  if (createdFiles.length > 0) {
    console.log(`${c.bold}  Created:${c.reset}`)
    for (const f of createdFiles) {
      console.log(`    ${c.cyan}${f}${c.reset}`)
    }
    console.log()
  }
  console.log(`${c.bold}  Next steps:${c.reset}`)
  console.log(`    ${c.cyan}taskflow status${c.reset}           — view all projects`)
  console.log(`    ${c.cyan}taskflow sync files-to-db${c.reset} — re-sync after editing markdown`)
  console.log(`    ${c.cyan}taskflow help${c.reset}             — full command reference`)
  console.log()
}

/**
 * Offer to install (or describe) the periodic-sync daemon.
 * macOS → LaunchAgent; Linux → systemd user timer.
 *
 * @param {Function|null} ask   - readline ask helper (null when non-interactive)
 * @param {boolean} autoYes     - skip interactive prompt and accept
 */
async function offerLaunchAgent(ask, autoYes = false) {
  const os = process.platform

  if (os === 'linux') {
    console.log()
    console.log(`${c.dim}  Linux detected. Run ${c.cyan}taskflow install-daemon${c.dim} to install the systemd user timer.${c.reset}`)
    return
  }

  if (os !== 'darwin') {
    console.log()
    console.log(`${c.dim}  Platform '${os}' not supported for automatic daemon install.${c.reset}`)
    console.log(`  ${c.gray}Manual cron: * * * * * OPENCLAW_WORKSPACE=${workspace} ${process.execPath} ${path.join(workspace, 'taskflow', 'scripts', 'task-sync.mjs')} files-to-db${c.reset}`)
    return
  }

  // macOS — offer LaunchAgent
  const plistDest = path.join(
    process.env.HOME || '',
    'Library', 'LaunchAgents', 'com.taskflow.sync.plist'
  )

  if (existsSync(plistDest)) {
    console.log(`  ${c.green}✓${c.reset} LaunchAgent already installed at ${plistDest}`)
    return
  }

  const tmplPath = path.join(__dirname, '..', 'system', 'com.taskflow.sync.plist.xml')
  if (!existsSync(tmplPath)) return

  // Non-interactive without --yes: skip LaunchAgent silently
  if (!ask && !autoYes) return

  // Interactive: prompt user
  if (ask && !autoYes) {
    console.log()
    const ans = (await ask('Install LaunchAgent for automatic 60s sync? [Y/n] ')).trim().toLowerCase()
    if (ans === 'n') return
  }

  try {
    const nodeBin = process.execPath
    const plistContent = readFileSync(tmplPath, 'utf8')
      .replace(/\{\{workspace\}\}/g, workspace)
      .replace(/<string>\/usr\/local\/bin\/node<\/string>/, `<string>${nodeBin}</string>`)

    writeFileSync(plistDest, plistContent, 'utf8')
    console.log(`  ${c.green}created${c.reset} ${plistDest}`)

    // Ensure logs dir exists
    const logsDir = path.join(workspace, 'logs')
    if (!existsSync(logsDir)) {
      mkdirSync(logsDir, { recursive: true })
      console.log(`  ${c.green}created${c.reset} logs/`)
    }

    // Load the agent
    const { execSync } = await import('node:child_process')
    try {
      execSync(`launchctl load "${plistDest}"`, { stdio: 'pipe' })
      console.log(`  ${c.green}loaded${c.reset}  com.taskflow.sync LaunchAgent (sync every 60s)`)
    } catch {
      console.log(`  ${c.yellow}!${c.reset} Could not load LaunchAgent automatically. Run manually:`)
      console.log(`    launchctl load "${plistDest}"`)
    }
  } catch (e) {
    console.log(`  ${c.yellow}!${c.reset} LaunchAgent install failed: ${e.message}`)
  }
}

// --- install-daemon ----------------------------------------------------------
/**
 * Detect platform and install the appropriate sync daemon:
 *   macOS  → ~/Library/LaunchAgents/com.taskflow.sync.plist  (launchctl)
 *   Linux  → ~/.config/systemd/user/taskflow-sync.{service,timer}  (systemctl --user)
 */
async function cmdInstallDaemon() {
  const os = process.platform
  const { execSync } = await import('node:child_process')

  console.log()
  console.log(`${c.bold}${c.cyan}  TaskFlow — Install Sync Daemon${c.reset}`)
  console.log(`${c.gray}  ${'─'.repeat(52)}${c.reset}`)
  console.log(`  Platform:  ${c.bold}${os}${c.reset}`)
  console.log(`  Workspace: ${c.bold}${workspace}${c.reset}`)
  console.log()

  // Ensure logs dir exists
  const logsDir = path.join(workspace, 'logs')
  if (!existsSync(logsDir)) {
    mkdirSync(logsDir, { recursive: true })
    console.log(`  ${c.green}created${c.reset} logs/`)
  }

  if (os === 'darwin') {
    // ── macOS: LaunchAgent ───────────────────────────────────────────────
    const plistDest = path.join(process.env.HOME || '', 'Library', 'LaunchAgents', 'com.taskflow.sync.plist')
    const tmplPath  = path.join(__dirname, '..', 'system', 'com.taskflow.sync.plist.xml')

    if (!existsSync(tmplPath)) {
      console.error(`${c.red}✗${c.reset} Template not found: ${tmplPath}`)
      process.exit(1)
    }

    if (existsSync(plistDest)) {
      console.log(`  ${c.green}✓${c.reset} LaunchAgent already installed: ${plistDest}`)
      console.log(`  ${c.dim}To reinstall, unload and remove it first:${c.reset}`)
      console.log(`    launchctl unload "${plistDest}" && rm "${plistDest}"`)
      return
    }

    const nodeBin = process.execPath
    const plistContent = readFileSync(tmplPath, 'utf8')
      .replace(/\{\{workspace\}\}/g, workspace)
      .replace(/\{\{node\}\}/g, nodeBin)

    writeFileSync(plistDest, plistContent, 'utf8')
    console.log(`  ${c.green}created${c.reset}  ${plistDest}`)

    try {
      execSync(`launchctl load "${plistDest}"`, { stdio: 'pipe' })
      console.log(`  ${c.green}loaded${c.reset}   com.taskflow.sync (syncs every 60s)`)
    } catch (e) {
      console.log(`  ${c.yellow}!${c.reset} Could not load automatically. Run:`)
      console.log(`    launchctl load "${plistDest}"`)
    }

    console.log()
    console.log(`  ${c.bold}Verify:${c.reset}  launchctl list | grep taskflow`)
    console.log(`  ${c.bold}Logs:${c.reset}    ${workspace}/logs/taskflow-sync.{stdout,stderr}.log`)

  } else if (os === 'linux') {
    // ── Linux: systemd user timer ────────────────────────────────────────
    const systemdDir  = path.join(process.env.HOME || '', '.config', 'systemd', 'user')
    const svcSrc      = path.join(__dirname, '..', 'system', 'taskflow-sync.service')
    const timerSrc    = path.join(__dirname, '..', 'system', 'taskflow-sync.timer')
    const svcDest     = path.join(systemdDir, 'taskflow-sync.service')
    const timerDest   = path.join(systemdDir, 'taskflow-sync.timer')

    for (const src of [svcSrc, timerSrc]) {
      if (!existsSync(src)) {
        console.error(`${c.red}✗${c.reset} Template not found: ${src}`)
        process.exit(1)
      }
    }

    // Create systemd user dir if needed
    if (!existsSync(systemdDir)) {
      mkdirSync(systemdDir, { recursive: true })
      console.log(`  ${c.green}created${c.reset} ${systemdDir}`)
    }

    const nodeBin = process.execPath

    for (const [src, dest] of [[svcSrc, svcDest], [timerSrc, timerDest]]) {
      const content = readFileSync(src, 'utf8')
        .replace(/\{\{workspace\}\}/g, workspace)
        .replace(/\{\{node\}\}/g, nodeBin)
      writeFileSync(dest, content, 'utf8')
      console.log(`  ${c.green}created${c.reset}  ${dest}`)
    }

    // Reload systemd user daemon and enable+start the timer
    try {
      execSync('systemctl --user daemon-reload', { stdio: 'pipe' })
      console.log(`  ${c.green}reloaded${c.reset} systemd user daemon`)
    } catch {
      console.log(`  ${c.yellow}!${c.reset} daemon-reload failed (is systemd --user running?)`)
    }

    try {
      execSync('systemctl --user enable --now taskflow-sync.timer', { stdio: 'pipe' })
      console.log(`  ${c.green}enabled${c.reset}  taskflow-sync.timer (syncs every 60s)`)
    } catch (e) {
      console.log(`  ${c.yellow}!${c.reset} Could not enable timer automatically. Run:`)
      console.log(`    systemctl --user daemon-reload`)
      console.log(`    systemctl --user enable --now taskflow-sync.timer`)
    }

    console.log()
    console.log(`  ${c.bold}Verify:${c.reset}  systemctl --user status taskflow-sync.timer`)
    console.log(`  ${c.bold}Logs:${c.reset}    journalctl --user -u taskflow-sync.service`)
    console.log(`           ${workspace}/logs/taskflow-sync.{stdout,stderr}.log`)

  } else {
    console.error(`${c.red}✗${c.reset} Platform '${os}' is not supported by install-daemon.`)
    console.error(`  Supported platforms: darwin (macOS), linux`)
    console.error()
    console.error(`  Manual cron fallback:`)
    console.error(`    * * * * * OPENCLAW_WORKSPACE=${workspace} ${process.execPath} ${path.join(workspace, 'taskflow', 'scripts', 'task-sync.mjs')} files-to-db`)
    process.exit(1)
  }

  console.log()
}

/**
 * Offer to set up Apple Notes sync (macOS only).
 * Creates the note via apple-notes-export.mjs and saves the ID to config.
 *
 * @param {Function|null} ask  - readline ask helper
 */
async function offerAppleNotes(ask) {
  if (process.platform !== 'darwin') return

  if (!ask) return   // non-interactive: skip silently

  console.log()
  const ans = (await ask(
    'Set up Apple Notes sync? This creates a shared note that stays updated with your project status. (y/N) '
  )).trim().toLowerCase()

  if (ans !== 'y') return

  const notesScript = path.join(SCRIPTS, 'apple-notes-export.mjs')
  if (!existsSync(notesScript)) {
    console.log(`  ${c.yellow}!${c.reset} apple-notes-export.mjs not found — skipping Notes setup.`)
    return
  }

  console.log()
  console.log(`  ${c.bold}Creating Apple Note…${c.reset}`)
  try {
    await import(notesScript)
    console.log()
    console.log(`  ${c.green}✓${c.reset} Apple Notes sync configured.`)
    console.log(`    Run ${c.cyan}taskflow notes${c.reset} to update manually.`)
    console.log(`    For hourly auto-refresh, add a LaunchAgent or cron:`)
    console.log(`    ${c.gray}0 * * * * OPENCLAW_WORKSPACE=${workspace} ${process.execPath} ${notesScript}${c.reset}`)
  } catch (e) {
    console.log(`  ${c.yellow}!${c.reset} Apple Notes setup failed: ${e.message}`)
    console.log(`    You can retry anytime with: ${c.cyan}taskflow notes${c.reset}`)
  }
}

// --- setup -------------------------------------------------------------------
async function cmdSetup(args) {
  // ── Parse CLI flags (non-interactive mode) ─────────────────────────────
  const nameIdx = args.indexOf('--name')
  const descIdx = args.indexOf('--desc')
  const nonInteractiveName = nameIdx !== -1 ? args[nameIdx + 1] : null
  const nonInteractiveDesc = descIdx !== -1 ? args[descIdx + 1] : null
  const nonInteractive = nonInteractiveName !== null
  const skipLaunchAgent = args.includes('--no-launchagent')
  const autoYes = args.includes('--yes') || args.includes('-y')

  // ── Common paths ────────────────────────────────────────────────────────
  const projectsFile = path.join(workspace, 'PROJECTS.md')
  const tasksDir     = path.join(workspace, 'tasks')
  const plansDir     = path.join(workspace, 'plans')
  const memoryDir    = path.join(workspace, 'memory')

  // ── Readline setup ──────────────────────────────────────────────────────
  let rl  = null
  let ask = null

  if (!nonInteractive) {
    const { createInterface } = await import('node:readline/promises')
    rl = createInterface({ input: process.stdin, output: process.stdout })
    rl.on('SIGINT', () => {
      console.log(`\n\n${c.yellow}Setup interrupted. No changes were committed.${c.reset}\n`)
      rl.close()
      process.exit(0)
    })
    ask = (q) => rl.question(`${c.cyan}?${c.reset} ${q}`)
  }

  const close = () => { if (rl) { rl.close(); rl = null } }

  // ── Header ──────────────────────────────────────────────────────────────
  console.log()
  console.log(`${c.bold}${c.cyan}  TaskFlow Setup${c.reset}`)
  console.log(`${c.gray}  ${'─'.repeat(52)}${c.reset}`)
  console.log(`  Workspace: ${c.bold}${workspace}${c.reset}`)
  console.log()

  // ── Detect current state ────────────────────────────────────────────────
  const hasProjects = existsSync(projectsFile)
  const hasDb       = existsSync(dbPath)

  // ── Scenario 1: Fully set up ────────────────────────────────────────────
  if (hasProjects && hasDb) {
    console.log(`${c.green}✓${c.reset} Already set up — PROJECTS.md and DB both present.`)
    console.log()
    cmdStatus()

    if (!nonInteractive) {
      const ans = await ask('Re-sync markdown → DB now? [y/N] ')
      close()
      if (ans.trim().toLowerCase() === 'y') {
        console.log()
        await cmdSync('files-to-db')
        console.log()
        console.log(`${c.green}✓${c.reset} Sync complete.`)
        console.log()
      }
    }
    return
  }

  // ── Scenario 2: PROJECTS.md exists but no DB ────────────────────────────
  if (hasProjects && !hasDb) {
    console.log(`${c.yellow}!${c.reset} PROJECTS.md found but no SQLite DB.`)

    if (!nonInteractive) {
      const ans = await ask('Initialize DB and sync markdown → DB now? [Y/n] ')
      if (ans.trim().toLowerCase() === 'n') {
        close()
        console.log()
        console.log('Aborted — no changes made.')
        console.log()
        return
      }
    }

    console.log()
    await cmdInit()
    console.log()
    await cmdSync('files-to-db')

    if (!skipLaunchAgent) await offerLaunchAgent(ask, autoYes)
    await offerAppleNotes(ask)
    close()
    printSetupSummary([])
    return
  }

  // ── Scenario 3: Clean slate ──────────────────────────────────────────────
  console.log(`${c.dim}  No existing workspace detected. Starting fresh.${c.reset}`)
  console.log()

  // Create required directories
  const createdFiles = []
  for (const [dir, label] of [[tasksDir, 'tasks/'], [plansDir, 'plans/'], [memoryDir, 'memory/']]) {
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true })
      console.log(`  ${c.green}created${c.reset} ${label}`)
      createdFiles.push(label)
    }
  }

  // Collect project definitions
  const projects = []

  if (nonInteractive) {
    // Non-interactive: single project from flags
    projects.push({ name: nonInteractiveName, desc: nonInteractiveDesc || '' })
  } else {
    // Interactive: first project
    const firstName = (await ask("What's your first project name? ")).trim()
    if (!firstName) {
      close()
      console.log(`\n${c.red}✗${c.reset} Project name is required. Aborting.`)
      console.log()
      process.exit(1)
    }
    const firstDesc = (await ask('One-liner description (optional, press Enter to skip): ')).trim()
    projects.push({ name: firstName, desc: firstDesc })

    // Loop for additional projects
    let addMore = true
    while (addMore) {
      const moreAns = (await ask('Add another project? [y/N] ')).trim().toLowerCase()
      if (moreAns !== 'y') {
        addMore = false
      } else {
        const n = (await ask('  Project name: ')).trim()
        if (n) {
          const d = (await ask('  Description (optional): ')).trim()
          projects.push({ name: n, desc: d })
        }
      }
    }
  }

  // Load tasks template
  const tasksTmplPath = path.join(__dirname, '..', 'templates', 'tasks-template.md')
  let tasksTmpl = null
  try { tasksTmpl = readFileSync(tasksTmplPath, 'utf8') } catch { /* use fallback */ }

  // Build PROJECTS.md content
  let projectsMd = `# Projects\n\n`
  projectsMd += `<!-- ============================================================
  PROJECTS.md — Project Registry
  ============================================================

  FORMAT: One ## block per project. The slug (## heading text)
  is the canonical project ID used in task IDs, file names,
  and SQLite foreign keys. Keep it lowercase and hyphenated.

  FIELDS:
    Name        Human-readable display name (any capitalization).
    Status      One of: active | paused | done
    Description One-sentence summary of the project's purpose.
  ============================================================ -->\n\n`

  for (const p of projects) {
    const slug = toSlug(p.name)

    // Append project block
    projectsMd += `## ${slug}\n- Name: ${p.name}\n- Status: active\n`
    if (p.desc) projectsMd += `- Description: ${p.desc}\n`
    projectsMd += '\n'

    // Create tasks file from template (or fallback)
    const tasksFile = path.join(tasksDir, `${slug}-tasks.md`)
    const tasksContent = tasksTmpl
      ? tasksTmpl
          .replace(/\{\{Project Name\}\}/g, p.name)
          .replace(/\{\{slug\}\}/g, slug)
      : `# ${p.name} — Tasks\n\n## In Progress\n\n## Pending Validation\n\n## Backlog\n\n- [ ] (task:${slug}-001) [P2] First task for this project\n\n## Blocked\n\n## Done\n`

    writeFileSync(tasksFile, tasksContent, 'utf8')
    createdFiles.push(`tasks/${slug}-tasks.md`)
    console.log(`  ${c.green}created${c.reset} tasks/${slug}-tasks.md`)
  }

  // Write PROJECTS.md
  writeFileSync(projectsFile, projectsMd, 'utf8')
  createdFiles.push('PROJECTS.md')
  console.log(`  ${c.green}created${c.reset} PROJECTS.md`)
  console.log()

  // Init DB
  console.log(`${c.bold}  Initializing database…${c.reset}`)
  await cmdInit()
  console.log()

  // Sync files → DB
  console.log(`${c.bold}  Syncing markdown → DB…${c.reset}`)
  await cmdSync('files-to-db')

  // Offer LaunchAgent / cron (interactive only — rl still open)
  if (!skipLaunchAgent) await offerLaunchAgent(ask, autoYes)
  await offerAppleNotes(ask)
  close()

  printSetupSummary(createdFiles)
}


// --- add ---------------------------------------------------------------------
function parseAddArgs(rawArgs) {
  const out = {
    project: null,
    title: null,
    priority: 'P2',
    owner: null,
    status: 'backlog',
    note: null,
    json: false,
    dryRun: false,
    sync: false,
  }

  const rest = [...rawArgs]
  if (!rest.length) return out

  out.project = rest.shift() || null
  if (rest[0] && !rest[0].startsWith('--')) {
    out.title = (rest.shift() || '').trim()
  }

  while (rest.length) {
    const tok = rest.shift()
    if (!tok.startsWith('--')) {
      if (!out.title) out.title = tok.trim()
      else out.title += ` ${tok.trim()}`
      continue
    }

    if (tok === '--priority') out.priority = (rest.shift() || '').trim()
    else if (tok === '--owner') out.owner = (rest.shift() || '').trim()
    else if (tok === '--status') out.status = (rest.shift() || '').trim()
    else if (tok === '--note') out.note = (rest.shift() || '').trim()
    else if (tok === '--json') out.json = true
    else if (tok === '--dry-run') out.dryRun = true
    else if (tok === '--sync') out.sync = true
    else {
      console.error(`${c.red}✗${c.reset} Unknown flag for add: ${tok}`)
      process.exit(1)
    }
  }

  return out
}

function escapeTaskTitle(title) {
  return title.replace(/\s+/g, ' ').trim()
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

async function cmdAdd(rawArgs) {
  const args = parseAddArgs(rawArgs)
  const allowedStatus = ['backlog', 'in_progress', 'pending_validation', 'blocked', 'done']
  const allowedPriority = ['P0', 'P1', 'P2', 'P3', 'P9']
  const sectionByStatus = {
    in_progress: 'In Progress',
    pending_validation: 'Pending Validation',
    backlog: 'Backlog',
    blocked: 'Blocked',
    done: 'Done',
  }

  if (!args.project || !args.title) {
    console.error(`${c.red}✗${c.reset} Usage: taskflow add <project> <title> [--priority P2] [--owner codex] [--status backlog|in_progress|pending_validation|blocked|done] [--note "..."] [--json] [--dry-run] [--sync]`)
    process.exit(1)
  }

  const project = args.project.trim().toLowerCase()
  const title = escapeTaskTitle(args.title)
  const status = args.status.toLowerCase()
  const priority = args.priority.toUpperCase()
  const BANNED_HEADERS = /^(in progress|pending validation|backlog|blocked|done)$/i

  if (!title || BANNED_HEADERS.test(title) || /\r|\n/.test(title)) {
    console.error(`${c.red}✗${c.reset} Invalid task title.`)
    process.exit(1)
  }
  if (!allowedStatus.includes(status)) {
    console.error(`${c.red}✗${c.reset} Invalid --status '${args.status}'. Allowed: ${allowedStatus.join(', ')}`)
    process.exit(1)
  }
  if (!allowedPriority.includes(priority)) {
    console.error(`${c.red}✗${c.reset} Invalid --priority '${args.priority}'. Allowed: ${allowedPriority.join(', ')}`)
    process.exit(1)
  }
  if (args.owner && !/^[A-Za-z0-9._-]{1,64}$/.test(args.owner)) {
    console.error(`${c.red}✗${c.reset} Invalid --owner '${args.owner}'. Use letters, numbers, dot, underscore, dash.`)
    process.exit(1)
  }

  const projectsFile = path.join(workspace, 'PROJECTS.md')
  if (!existsSync(projectsFile)) {
    console.error(`${c.red}✗${c.reset} PROJECTS.md not found at: ${projectsFile}`)
    process.exit(1)
  }
  const projectsText = readFileSync(projectsFile, 'utf8')
  const projectHeader = new RegExp(`^##\\s+${escapeRegex(project)}\\s*$`, 'm')
  if (!projectHeader.test(projectsText)) {
    console.error(`${c.red}✗${c.reset} Unknown project '${project}'. Add it to PROJECTS.md first.`)
    process.exit(1)
  }

  const taskFile = path.join(workspace, 'tasks', `${project}-tasks.md`)
  if (!existsSync(taskFile)) {
    console.error(`${c.red}✗${c.reset} Task file not found: ${taskFile}`)
    process.exit(1)
  }

  const original = readFileSync(taskFile, 'utf8')
  const idRe = new RegExp(`\\(task:${escapeRegex(project)}-(\\d{1,})\\)`, 'g')
  let m
  let maxN = 0
  while ((m = idRe.exec(original)) !== null) {
    const n = Number(m[1])
    if (Number.isFinite(n) && n > maxN) maxN = n
  }
  const nextId = `${project}-${String(maxN + 1).padStart(3, '0')}`

  const sectionHeader = `## ${sectionByStatus[status]}`
  const lines = original.split(/\n/)
  const secIdx = lines.findIndex(l => l.trim() === sectionHeader)
  if (secIdx < 0) {
    console.error(`${c.red}✗${c.reset} Section '${sectionHeader}' not found in ${taskFile}`)
    process.exit(1)
  }

  let insertIdx = lines.length
  for (let i = secIdx + 1; i < lines.length; i++) {
    if (/^##\s+/.test(lines[i])) {
      insertIdx = i
      break
    }
  }

  const checkbox = status === 'done' ? '[x]' : '[ ]'
  let taskLine = `- ${checkbox} (task:${nextId}) [${priority}]`
  if (args.owner) taskLine += ` [${args.owner}]`
  taskLine += ` ${title}`

  const insertion = [taskLine]
  if (args.note) insertion.push(`  - note: ${args.note.replace(/\s+/g, ' ').trim()}`)
  if (insertIdx > 0 && lines[insertIdx - 1] !== '') insertion.unshift('')

  lines.splice(insertIdx, 0, ...insertion)
  const updated = lines.join('\n')

  const payload = {
    id: nextId,
    project,
    title,
    priority,
    status,
    owner: args.owner || null,
    note: args.note || null,
    file: taskFile,
    section: sectionByStatus[status],
    dryRun: args.dryRun,
  }

  if (args.dryRun) {
    if (args.json) console.log(JSON.stringify(payload, null, 2))
    else {
      console.log(`${c.cyan}[dry-run]${c.reset} would create ${c.bold}${nextId}${c.reset} in ${taskFile}`)
      console.log(`  section: ${sectionByStatus[status]}`)
      console.log(`  line: ${taskLine}`)
      if (args.note) console.log(`  note: ${args.note}`)
    }
    return
  }

  writeFileSync(taskFile, updated, 'utf8')
  if (args.sync) await cmdSync('files-to-db')

  if (args.json) console.log(JSON.stringify(payload, null, 2))
  else {
    console.log(`${c.green}✓${c.reset} Added ${c.bold}${nextId}${c.reset} to ${project} (${sectionByStatus[status]}).`)
    console.log(`  ${taskFile}`)
  }
}

// --- list --------------------------------------------------------------------
function parseListArgs(rawArgs) {
  const out = {
    project: null,
    all: false,
    status: null,
    priority: null,
    owner: null,
    json: false,
    limit: null,
  }

  const rest = [...rawArgs]
  if (!rest.length) return out

  if (rest[0] && !rest[0].startsWith('--')) {
    out.project = (rest.shift() || '').trim() || null
  }

  while (rest.length) {
    const tok = rest.shift()
    if (tok === '--all') out.all = true
    else if (tok === '--status') out.status = (rest.shift() || '').trim()
    else if (tok === '--priority') out.priority = (rest.shift() || '').trim()
    else if (tok === '--owner') out.owner = (rest.shift() || '').trim()
    else if (tok === '--project') out.project = (rest.shift() || '').trim() || null
    else if (tok === '--json') out.json = true
    else if (tok === '--limit') {
      const n = Number(rest.shift())
      if (!Number.isFinite(n) || n <= 0) {
        console.error(`${c.red}✗${c.reset} --limit must be a positive number`)
        process.exit(1)
      }
      out.limit = Math.floor(n)
    } else {
      console.error(`${c.red}✗${c.reset} Unknown flag for list: ${tok}`)
      process.exit(1)
    }
  }

  return out
}

function splitCsv(input) {
  return (input || '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean)
}

function firstNoteLine(notes) {
  if (!notes) return null
  const line = String(notes).split(/\r?\n/).map(s => s.trim()).find(Boolean)
  return line || null
}

function formatTaskLine(task) {
  const owner = task.owner_model ? ` [${task.owner_model}]` : ''
  const note = task.first_note ? `\n    ${c.dim}note:${c.reset} ${task.first_note}` : ''
  return `  - (${task.id}) [${task.priority}]${owner} ${task.title}${note}`
}

function resolveProject(db, projectRef) {
  const raw = (projectRef || '').trim()
  if (!raw) return { project: null }

  const exactId = db.prepare('SELECT id, name FROM projects WHERE id = ?').get(raw.toLowerCase())
  if (exactId) return { project: exactId }

  const all = db.prepare('SELECT id, name FROM projects ORDER BY id').all()
  const ref = raw.toLowerCase()

  const exactName = all.filter(p => String(p.name || '').toLowerCase() === ref)
  if (exactName.length === 1) return { project: exactName[0] }

  const starts = all.filter(p => p.id.toLowerCase().startsWith(ref) || String(p.name || '').toLowerCase().startsWith(ref))
  if (starts.length === 1) return { project: starts[0] }

  const contains = all.filter(p => p.id.toLowerCase().includes(ref) || String(p.name || '').toLowerCase().includes(ref))
  if (contains.length === 1) return { project: contains[0] }

  const candidates = starts.length ? starts : contains
  if (candidates.length > 1) return { project: null, ambiguous: true, candidates }

  return { project: null }
}

function cmdList(rawArgs) {
  const args = parseListArgs(rawArgs)
  const allowedStatus = ['in_progress', 'pending_validation', 'blocked', 'backlog', 'done']
  const allowedPriority = ['P0', 'P1', 'P2', 'P3', 'P9']
  const statusOrder = ['in_progress', 'pending_validation', 'blocked', 'backlog', 'done']
  const statusLabel = {
    in_progress: 'In Progress',
    pending_validation: 'Pending Validation',
    blocked: 'Blocked',
    backlog: 'Backlog',
    done: 'Done',
  }
  const priorityRank = { P0: 0, P1: 1, P2: 2, P3: 3, P9: 4 }

  if (!args.project) {
    console.error(`${c.red}✗${c.reset} Usage: taskflow list <project> [--project <slug|name>] [--all] [--status in_progress,backlog] [--priority P1,P2] [--owner codex] [--json] [--limit N]`)
    process.exit(1)
  }

  if (!existsSync(dbPath)) {
    console.error(`${c.red}✗${c.reset} DB not found at: ${dbPath}`)
    console.error(`  Run ${c.bold}taskflow init${c.reset} and ${c.bold}taskflow sync files-to-db${c.reset} first.`)
    process.exit(1)
  }

  const selectedStatuses = args.status ? splitCsv(args.status).map(s => s.toLowerCase()) : null
  if (selectedStatuses) {
    const invalid = selectedStatuses.filter(s => !allowedStatus.includes(s))
    if (invalid.length) {
      console.error(`${c.red}✗${c.reset} Invalid --status value(s): ${invalid.join(', ')}`)
      console.error(`  Allowed: ${allowedStatus.join(', ')}`)
      process.exit(1)
    }
  }

  const selectedPriorities = args.priority ? splitCsv(args.priority).map(p => p.toUpperCase()) : null
  if (selectedPriorities) {
    const invalid = selectedPriorities.filter(p => !allowedPriority.includes(p))
    if (invalid.length) {
      console.error(`${c.red}✗${c.reset} Invalid --priority value(s): ${invalid.join(', ')}`)
      console.error(`  Allowed: ${allowedPriority.join(', ')}`)
      process.exit(1)
    }
  }

  const db = new DatabaseSync(dbPath)
  db.exec('PRAGMA foreign_keys = ON')

  const resolved = resolveProject(db, args.project)
  if (!resolved.project) {
    if (resolved.ambiguous) {
      console.error(`${c.red}✗${c.reset} Ambiguous project reference '${args.project}'.`)
      console.error(`  Matches: ${resolved.candidates.map(p => `${p.id} (${p.name})`).join(', ')}`)
      process.exit(1)
    }
    console.error(`${c.red}✗${c.reset} Unknown project '${args.project}' in DB.`)
    console.error(`  Run ${c.bold}taskflow sync files-to-db${c.reset} if it exists in PROJECTS.md.`)
    process.exit(1)
  }
  const project = resolved.project

  const rows = db.prepare(`
    SELECT id, project_id, title, status, priority, owner_model, notes
    FROM tasks_v2
    WHERE project_id = ?
  `).all(project.id)

  const defaultStatuses = ['in_progress', 'pending_validation', 'blocked', 'backlog']
  const wantedStatuses = selectedStatuses || (args.all ? [...statusOrder] : defaultStatuses)

  let filtered = rows
    .filter(r => wantedStatuses.includes(r.status))
    .filter(r => !selectedPriorities || selectedPriorities.includes(r.priority))
    .filter(r => !args.owner || (r.owner_model || '').toLowerCase() === args.owner.toLowerCase())
    .map(r => ({ ...r, first_note: firstNoteLine(r.notes) }))

  filtered.sort((a, b) => {
    const s = statusOrder.indexOf(a.status) - statusOrder.indexOf(b.status)
    if (s !== 0) return s
    const p = (priorityRank[a.priority] ?? 999) - (priorityRank[b.priority] ?? 999)
    if (p !== 0) return p
    return a.id.localeCompare(b.id)
  })

  if (args.limit) filtered = filtered.slice(0, args.limit)

  if (args.json) {
    const grouped = {}
    for (const s of statusOrder) grouped[s] = []
    for (const row of filtered) grouped[row.status].push(row)

    console.log(JSON.stringify({
      project: { id: project.id, name: project.name },
      filters: {
        all: args.all,
        status: wantedStatuses,
        priority: selectedPriorities,
        owner: args.owner || null,
        limit: args.limit || null,
      },
      total: filtered.length,
      tasks: filtered,
      grouped,
    }, null, 2))
    return
  }

  console.log()
  console.log(`${c.bold}${project.name}${c.reset} ${c.gray}(${project.id})${c.reset}`)
  console.log(`${c.dim}Showing ${filtered.length} task(s)${c.reset}`)

  if (!filtered.length) {
    console.log(`${c.dim}No matching tasks.${c.reset}`)
    console.log()
    return
  }

  for (const status of statusOrder) {
    const bucket = filtered.filter(r => r.status === status)
    if (!bucket.length) continue
    console.log()
    console.log(`${c.bold}${statusLabel[status]}${c.reset} ${c.gray}(${bucket.length})${c.reset}`)
    for (const task of bucket) console.log(formatTaskLine(task))
  }

  console.log()
}

// --- notes -------------------------------------------------------------------
async function cmdNotes() {
  const notesScript = path.join(SCRIPTS, 'apple-notes-export.mjs')
  if (!existsSync(notesScript)) {
    console.error(`${c.red}✗${c.reset} apple-notes-export.mjs not found at: ${notesScript}`)
    process.exit(1)
  }
  await import(notesScript)
}

// --- help --------------------------------------------------------------------
function cmdHelp() {
  console.log(`
${c.bold}taskflow${c.reset} — TaskFlow CLI

${c.bold}USAGE${c.reset}
  taskflow <command> [options]

${c.bold}COMMANDS${c.reset}
  ${c.cyan}setup${c.reset}                     Interactive first-run onboarding. Creates workspace
                            directories, PROJECTS.md, task files, initializes the
                            DB, syncs, and optionally installs the LaunchAgent.
    ${c.dim}--name <name>${c.reset}           Non-interactive: project name (skips all prompts)
    ${c.dim}--desc <desc>${c.reset}           Non-interactive: project description
    ${c.dim}--no-launchagent${c.reset}        Skip LaunchAgent / cron prompt
    ${c.dim}--yes, -y${c.reset}              Auto-accept all yes/no prompts

  ${c.cyan}status${c.reset}                    Pretty terminal summary of all projects with task counts
                            and progress bars.

  ${c.cyan}export${c.reset}                    Output a full JSON snapshot of all projects and tasks to
                            stdout. Pipe to a file for dashboard consumption.

  ${c.cyan}sync${c.reset} <mode>               Sync task markdown files ↔ SQLite.
    ${c.dim}files-to-db${c.reset}             Parse markdown, write to DB (markdown is authoritative)
    ${c.dim}db-to-files${c.reset}             Regenerate markdown from DB state
    ${c.dim}check${c.reset}                   Detect drift, exit 1 if mismatch (good for CI/cron)

  ${c.cyan}init${c.reset}                      Bootstrap (or re-bootstrap) the SQLite schema. Idempotent.

  ${c.cyan}install-daemon${c.reset}            Install the periodic-sync daemon for your OS.
                            macOS  → ~/Library/LaunchAgents/com.taskflow.sync.plist (launchctl)
                            Linux  → ~/.config/systemd/user/taskflow-sync.{service,timer}
                            Detects platform automatically; templates are in taskflow/system/.

  ${c.cyan}add${c.reset} <project> <title>     Create a task line in markdown (source of truth).
    ${c.dim}--priority <P0|P1|P2|P3|P9>${c.reset}  Task priority (default: P2)
    ${c.dim}--owner <tag>${c.reset}           Optional owner/model tag (e.g. codex)
    ${c.dim}--status <status>${c.reset}       backlog|in_progress|pending_validation|blocked|done
    ${c.dim}--note <text>${c.reset}           Optional note line under the task
    ${c.dim}--json${c.reset}                  Emit machine-readable JSON output
    ${c.dim}--dry-run${c.reset}               Show what would be written without editing files
    ${c.dim}--sync${c.reset}                  Run files-to-db sync after write

  ${c.cyan}list${c.reset} <project>            List tasks for one project (current tasks by default).
    ${c.dim}--project <slug|name>${c.reset}   Alternate project selector flag (supports fuzzy match)
    ${c.dim}--all${c.reset}                   Include done tasks
    ${c.dim}--status <csv>${c.reset}          Filter statuses (e.g. in_progress,backlog)
    ${c.dim}--priority <csv>${c.reset}        Filter priorities (e.g. P1,P2)
    ${c.dim}--owner <tag>${c.reset}           Filter by exact owner/model tag
    ${c.dim}--json${c.reset}                  Emit machine-readable JSON output
    ${c.dim}--limit <n>${c.reset}             Limit total tasks returned after sorting

  ${c.cyan}notes${c.reset}                     Push current project status to Apple Notes (macOS only).
                            Creates a new note on first run; edits in-place on subsequent
                            runs (preserves any share link). Note ID is saved to
                            \$OPENCLAW_WORKSPACE/taskflow.config.json.

  ${c.cyan}help${c.reset}                      Show this message.

${c.bold}ENVIRONMENT${c.reset}
  OPENCLAW_WORKSPACE        Root workspace directory (default: cwd)
                            DB is resolved as \$OPENCLAW_WORKSPACE/memory/taskflow.sqlite

${c.bold}EXAMPLES${c.reset}
  taskflow setup
  taskflow setup --name "My Project" --desc "A cool thing" --no-launchagent
  taskflow init
  taskflow sync files-to-db
  taskflow status
  taskflow export > /tmp/projects.json
  taskflow sync check && echo "in sync"
  taskflow add dashboard "Ship calendar API retry logic" --priority P1 --owner codex
  taskflow add taskflow "Document parser edge case" --status blocked --note "Waiting on repro"
  taskflow list taskflow
  taskflow list --project "TaskFlow" --all
  taskflow list task --status backlog,pending_validation --json
  taskflow notes
`)
}

// ── Dispatch ─────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv

switch (cmd) {
  case 'setup':
    await cmdSetup(args)
    break

  case 'status':
    cmdStatus()
    break

  case 'export':
    await cmdExport()
    break

  case 'sync':
    await cmdSync(args[0] || 'check')
    break

  case 'init':
    await cmdInit()
    break

  case 'install-daemon':
    await cmdInstallDaemon()
    break

  case 'add':
    cmdAdd(args)
    break

  case 'list':
    cmdList(args)
    break

  case 'notes':
    await cmdNotes()
    break

  case 'help':
  case '--help':
  case '-h':
    cmdHelp()
    break

  case undefined:
    // No args: show status as a sensible default
    cmdStatus()
    break

  default:
    console.error(`${c.red}✗${c.reset} Unknown command: ${JSON.stringify(cmd)}`)
    console.error(`  Run ${c.bold}taskflow help${c.reset} for usage.`)
    process.exit(1)
}
