#!/usr/bin/env node

/**
 * GoPlus AgentGuard — SessionStart Auto-Scan Hook
 *
 * Runs on session startup to discover and scan newly installed skills.
 * For each skill in ~/.claude/skills/:
 *   1. Calculate artifact hash
 *   2. Check trust registry — skip if already registered with same hash
 *   3. Run quickScan for new/updated skills
 *   4. Report results to stderr (scan-only, does NOT modify trust registry)
 *
 * OPT-IN: This script only runs when AGENTGUARD_AUTO_SCAN=1.
 * Without this env var, the script exits immediately.
 *
 * To register scanned skills, use: /agentguard trust attest
 *
 * Exits 0 always (informational only, never blocks session startup).
 */

import { readdirSync, existsSync, appendFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';

// ---------------------------------------------------------------------------
// Opt-in gate: only run when explicitly enabled
// ---------------------------------------------------------------------------

if (process.env.AGENTGUARD_AUTO_SCAN !== '1') {
  process.exit(0);
}

// ---------------------------------------------------------------------------
// Load AgentGuard engine
// ---------------------------------------------------------------------------

const agentguardPath = join(
  import.meta.url.replace('file://', ''),
  '..', '..', '..', '..', 'dist', 'index.js'
);

let createAgentGuard;
try {
  const gs = await import(agentguardPath);
  createAgentGuard = gs.createAgentGuard || gs.default;
} catch {
  try {
    const gs = await import('@goplus/agentguard');
    createAgentGuard = gs.createAgentGuard || gs.default;
  } catch {
    // Can't load engine — exit silently
    process.exit(0);
  }
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const SKILLS_DIRS = [
  join(homedir(), '.claude', 'skills'),
  join(homedir(), '.openclaw', 'skills'),
];
const AGENTGUARD_DIR = join(homedir(), '.agentguard');
const AUDIT_PATH = join(AGENTGUARD_DIR, 'audit.jsonl');

function ensureDir() {
  if (!existsSync(AGENTGUARD_DIR)) {
    mkdirSync(AGENTGUARD_DIR, { recursive: true });
  }
}

function writeAuditLog(entry) {
  try {
    ensureDir();
    appendFileSync(AUDIT_PATH, JSON.stringify(entry) + '\n');
  } catch {
    // Non-critical
  }
}

// ---------------------------------------------------------------------------
// Discover skills
// ---------------------------------------------------------------------------

/**
 * Find all skill directories under ~/.claude/skills/ and ~/.openclaw/skills/
 * A skill directory is one that contains a SKILL.md file.
 */
function discoverSkills() {
  const skills = [];
  for (const skillsDir of SKILLS_DIRS) {
    if (!existsSync(skillsDir)) continue;
    try {
      const entries = readdirSync(skillsDir, { withFileTypes: true });
      for (const entry of entries) {
        if (!entry.isDirectory()) continue;
        const skillDir = join(skillsDir, entry.name);
        const skillMd = join(skillDir, 'SKILL.md');
        if (existsSync(skillMd)) {
          skills.push({ name: entry.name, path: skillDir });
        }
      }
    } catch {
      // Can't read skills dir
    }
  }
  return skills;
}

// ---------------------------------------------------------------------------
// Main — scan-only mode (no trust registry mutations)
// ---------------------------------------------------------------------------

async function main() {
  const skills = discoverSkills();
  if (skills.length === 0) {
    process.exit(0);
  }

  const { scanner } = createAgentGuard();

  let scanned = 0;
  const results = [];

  for (const skill of skills) {
    // Skip self (agentguard)
    if (skill.name === 'agentguard') continue;

    try {
      const result = await scanner.quickScan(skill.path);
      scanned++;

      results.push({
        name: skill.name,
        risk_level: result.risk_level,
        risk_tags: result.risk_tags,
      });

      // Audit log — only record skill name, risk level, and tag names (no code/evidence)
      writeAuditLog({
        timestamp: new Date().toISOString(),
        event: 'auto_scan',
        skill_name: skill.name,
        risk_level: result.risk_level,
        risk_tags: result.risk_tags,
      });
    } catch {
      // Skip skills that fail to scan
    }
  }

  // Output summary to stderr (shown as status message)
  if (scanned > 0) {
    const lines = results.map(r =>
      `  ${r.name}: ${r.risk_level}${r.risk_tags.length ? ` [${r.risk_tags.join(', ')}]` : ''}`
    );
    process.stderr.write(
      `GoPlus AgentGuard: scanned ${scanned} skill(s)\n${lines.join('\n')}\n` +
      `Use /agentguard trust attest to register trusted skills.\n`
    );
  }

  process.exit(0);
}

main();
