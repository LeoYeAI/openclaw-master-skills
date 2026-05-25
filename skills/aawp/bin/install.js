#!/usr/bin/env node
'use strict';

const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { execSync, spawnSync } = require('child_process');

const VERSION    = require('../package.json').version;
const SKILL_NAME = 'aawp';
const RAW_BASE   = 'https://raw.githubusercontent.com/aawp-ai/aawp/main/skills/aawp';
const FALLBACK   = 'https://aawp.ai/skill';

// ── ANSI colors ───────────────────────────────────────────────────────────────
const isTTY  = process.stdout.isTTY;
const c = (code, s) => isTTY ? `\x1b[${code}m${s}\x1b[0m` : s;
const bold   = s => c('1', s);
const dim    = s => c('2', s);
const green  = s => c('32', s);
const blue   = s => c('34', s);
const yellow = s => c('33', s);
const red    = s => c('31', s);

const info    = s => console.log(`  ${blue('→')} ${s}`);
const success = s => console.log(`  ${green('✓')} ${s}`);
const warn    = s => console.log(`  ${yellow('!')} ${s}`);
const fail    = s => console.log(`  ${red('✗')} ${s}`);

// ── Fetch helper ──────────────────────────────────────────────────────────────
async function fetchText(url) {
  if (typeof fetch !== 'undefined') {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.text();
  }
  return new Promise((resolve, reject) => {
    const proto = url.startsWith('https') ? require('https') : require('http');
    proto.get(url, res => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return fetchText(res.headers.location).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) return reject(new Error(`HTTP ${res.statusCode}`));
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks).toString()));
      res.on('error', reject);
    }).on('error', reject);
  });
}

async function downloadSkillMd() {
  try {
    return await fetchText(`${RAW_BASE}/SKILL.md`);
  } catch {
    return fetchText(`${FALLBACK}/SKILL.md`);
  }
}

// ── Client detection ──────────────────────────────────────────────────────────
const HOME = os.homedir();

function hasCmd(cmd) {
  try { execSync(`command -v ${cmd}`, { stdio: 'ignore' }); return true; } catch { return false; }
}
function dirExists(p) {
  try { return fs.statSync(p).isDirectory(); } catch { return false; }
}

const CLIENTS = [
  {
    name: 'OpenClaw',
    detect: () => hasCmd('clawhub'),
    install: async () => {
      const r = spawnSync('clawhub', ['install', SKILL_NAME], { stdio: 'inherit' });
      return r.status === 0;
    },
    skillDir: null,
  },
  {
    name: 'Cursor',
    detect: () => hasCmd('cursor') || dirExists(path.join(HOME, '.cursor')),
    skillDir: path.join(HOME, '.cursor', 'skills'),
  },
  {
    name: 'Claude Code',
    detect: () => hasCmd('claude') || dirExists(path.join(HOME, '.claude')),
    skillDir: path.join(HOME, '.claude', 'skills'),
  },
  {
    name: 'Gemini CLI',
    detect: () => hasCmd('gemini') || dirExists(path.join(HOME, '.gemini')),
    skillDir: path.join(HOME, '.gemini', 'skills'),
  },
  {
    name: 'OpenCode',
    detect: () => hasCmd('opencode') || dirExists(path.join(HOME, '.config', 'opencode')),
    skillDir: path.join(HOME, '.config', 'opencode', 'skills'),
  },
  {
    name: 'Goose',
    detect: () => hasCmd('goose') || dirExists(path.join(HOME, '.config', 'goose')),
    skillDir: path.join(HOME, '.config', 'goose', 'skills'),
  },
];

const UNIVERSAL_DIR = path.join(HOME, '.agents', 'skills');

// ── Install to dir ────────────────────────────────────────────────────────────
function installToDir(baseDir, skillMd) {
  const dest = path.join(baseDir, SKILL_NAME);
  fs.mkdirSync(dest, { recursive: true });
  fs.writeFileSync(path.join(dest, 'SKILL.md'), skillMd, 'utf8');
  return dest;
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  console.log('');
  console.log(`  ${bold('AAWP Skill Installer')} ${dim('v' + VERSION)}`);
  console.log(`  ${dim('AI Agent Wallet Protocol — aawp.ai')}`);
  console.log('');

  const detected = CLIENTS.filter(c => c.detect());
  const detectedNames = detected.map(c => c.name);

  if (detected.length === 0) {
    info('No AI clients detected — installing to universal ~/.agents/skills/');
  } else {
    info(`Detected: ${detectedNames.join(', ')}`);
  }
  console.log('');

  info('Downloading SKILL.md...');
  let skillMd;
  try {
    skillMd = await downloadSkillMd();
    success('SKILL.md fetched');
  } catch (e) {
    fail(`Failed to download SKILL.md: ${e.message}`);
    process.exit(1);
  }
  console.log('');

  let count = 0;

  const openclaw = detected.find(c => c.name === 'OpenClaw');
  if (openclaw) {
    info('Installing via clawhub (OpenClaw)...');
    try {
      const ok = await openclaw.install();
      if (ok) { success('Installed via clawhub'); count++; }
      else { warn('clawhub failed — falling back to file install'); }
    } catch (e) {
      warn(`clawhub error: ${e.message}`);
    }
    console.log('');
  }

  const seenDirs = new Set();
  const dirsToInstall = [];

  for (const client of detected) {
    if (client.skillDir && !seenDirs.has(client.skillDir)) {
      seenDirs.add(client.skillDir);
      dirsToInstall.push({ dir: client.skillDir, label: client.name });
    }
  }

  if (!seenDirs.has(UNIVERSAL_DIR)) {
    dirsToInstall.push({ dir: UNIVERSAL_DIR, label: 'universal (~/.agents/skills)' });
  }

  for (const { dir, label } of dirsToInstall) {
    const shortDir = dir.replace(HOME, '~');
    info(`Installing to ${shortDir}/aawp/ ${dim('(' + label + ')')}`);
    try {
      const dest = installToDir(dir, skillMd);
      success(`Installed → ${dest.replace(HOME, '~')}/SKILL.md`);
      count++;
    } catch (e) {
      fail(`Failed: ${e.message}`);
    }
  }

  console.log('');
  if (count > 0) {
    console.log(`  ${bold(green('AAWP skill installed!'))}`);
    console.log('');
    console.log(`  ${dim('Restart your AI client to load the skill.')}`);
    console.log(`  ${dim('Then ask: "set up my AAWP wallet"')}`);
    console.log(`  ${dim('Full autonomy (24/7 daemon + cron): clawhub install aawp')}`);
    console.log(`  ${dim('Docs: https://aawp.ai  ·  https://github.com/aawp-ai/aawp')}`);
  } else {
    warn('Nothing was installed.');
    console.log(`  ${dim('Try manually: copy SKILL.md to your client\'s skills directory.')}`);
  }
  console.log('');
}

main().catch(e => {
  fail(`Unexpected error: ${e.message}`);
  process.exit(1);
});
