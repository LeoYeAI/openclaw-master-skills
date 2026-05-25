#!/usr/bin/env node
/**
 * OpenClaw Buddy -- Pearl Manager CLI
 * Usage: node pearls.js <command> [args]
 *
 * Commands:
 *   list                          List all pearls with sizes
 *   read <slug>                   Print a pearl's content
 *   create <slug> [--file path]   Create a pearl from stdin or file
 *   edit <slug> [--file path]     Replace a pearl's content
 *   delete <slug>                 Delete a pearl
 *   rename <old-slug> <new-slug>  Rename a pearl file
 *   generate <topic>               Generate a pearl on a specific topic
 *   generate --all                Regenerate all pearls from memory
 *   sync                          Update relay specialties from current pearls
 */

import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SKILL_DIR = path.resolve(__dirname, '..');
const PEARLS_DIR = process.env.PEARLS_DIR
  ? path.resolve(process.env.PEARLS_DIR)
  : path.join(SKILL_DIR, 'pearls');

const RELAY_URL = process.env.CLAWBUDDY_URL || 'https://clawbuddy.help';
const RELAY_TOKEN = process.env.CLAWBUDDY_TOKEN;

// --- Helpers ---

function ensureDir() {
  if (!fs.existsSync(PEARLS_DIR)) {
    fs.mkdirSync(PEARLS_DIR, { recursive: true });
  }
}

function pearlPath(slug) {
  // Sanitize slug
  const safe = slug.replace(/\.md$/, '').replace(/[^a-z0-9-]/gi, '-').toLowerCase();
  return path.join(PEARLS_DIR, `${safe}.md`);
}

function listPearls() {
  ensureDir();
  const files = fs.readdirSync(PEARLS_DIR).filter(f => f.endsWith('.md')).sort();
  if (files.length === 0) {
    console.log('No pearls found.');
    console.log(`Directory: ${PEARLS_DIR}`);
    console.log('Run "node pearls.js generate" to create pearls from experience.');
    return;
  }
  console.log(`Pearls (${files.length}) in ${PEARLS_DIR}:\n`);
  for (const file of files) {
    const stat = fs.statSync(path.join(PEARLS_DIR, file));
    const slug = file.replace(/\.md$/, '');
    const kb = (stat.size / 1024).toFixed(1);
    console.log(`  ${slug.padEnd(30)} ${kb} KB`);
  }
}

function slugToTitle(slug) {
  return slug
    .split('-')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
    .replace(/ And /g, ' & ');
}

// --- Commands ---

function cmdList() {
  listPearls();
}

function cmdRead(args) {
  const slug = args[0];
  if (!slug) {
    console.error('Usage: node pearls.js read <slug>');
    process.exit(1);
  }
  const fp = pearlPath(slug);
  if (!fs.existsSync(fp)) {
    console.error(`Pearl not found: ${slug}`);
    console.error(`Expected at: ${fp}`);
    process.exit(1);
  }
  process.stdout.write(fs.readFileSync(fp, 'utf-8'));
}

function cmdCreate(args) {
  const slug = args[0];
  if (!slug) {
    console.error('Usage: node pearls.js create <slug> [--file path]');
    console.error('  Without --file, reads content from stdin.');
    process.exit(1);
  }

  const fp = pearlPath(slug);
  if (fs.existsSync(fp)) {
    console.error(`Pearl already exists: ${slug}`);
    console.error('Use "edit" to update, or "delete" first.');
    process.exit(1);
  }

  const content = getContent(args);
  ensureDir();
  fs.writeFileSync(fp, content);
  console.log(`Created: ${slug} (${(content.length / 1024).toFixed(1)} KB)`);
}

function cmdEdit(args) {
  const slug = args[0];
  if (!slug) {
    console.error('Usage: node pearls.js edit <slug> [--file path]');
    console.error('  Without --file, reads content from stdin.');
    process.exit(1);
  }

  const fp = pearlPath(slug);
  if (!fs.existsSync(fp)) {
    console.error(`Pearl not found: ${slug}`);
    console.error('Use "create" for new pearls.');
    process.exit(1);
  }

  const content = getContent(args);
  fs.writeFileSync(fp, content);
  console.log(`Updated: ${slug} (${(content.length / 1024).toFixed(1)} KB)`);
}

function cmdDelete(args) {
  const slug = args[0];
  if (!slug) {
    console.error('Usage: node pearls.js delete <slug>');
    process.exit(1);
  }

  const fp = pearlPath(slug);
  if (!fs.existsSync(fp)) {
    console.error(`Pearl not found: ${slug}`);
    process.exit(1);
  }

  fs.unlinkSync(fp);
  console.log(`Deleted: ${slug}`);
}

function cmdRename(args) {
  const oldSlug = args[0];
  const newSlug = args[1];
  if (!oldSlug || !newSlug) {
    console.error('Usage: node pearls.js rename <old-slug> <new-slug>');
    process.exit(1);
  }

  const oldPath = pearlPath(oldSlug);
  const newPath = pearlPath(newSlug);

  if (!fs.existsSync(oldPath)) {
    console.error(`Pearl not found: ${oldSlug}`);
    process.exit(1);
  }
  if (fs.existsSync(newPath)) {
    console.error(`Target already exists: ${newSlug}`);
    process.exit(1);
  }

  fs.renameSync(oldPath, newPath);
  console.log(`Renamed: ${oldSlug} -> ${newSlug}`);
}

async function cmdGenerate(args) {
  // Delegate to generate-pearls.js
  const genScript = path.join(__dirname, 'generate-pearls.js');
  const genArgs = [];

  const allFlag = args.includes('--all');

  if (allFlag) {
    // Full generation from all memory — no --topic flag
  } else {
    // Requires a topic description as remaining args
    const topic = args.filter(a => a !== '--all').join(' ').trim();
    if (!topic) {
      console.error('Usage: node pearls.js generate <topic description>');
      console.error('       node pearls.js generate --all');
      console.error('');
      console.error('Examples:');
      console.error('  node pearls.js generate "VPS hosting and server setup"');
      console.error('  node pearls.js generate "Docker troubleshooting patterns"');
      console.error('  node pearls.js generate --all   # regenerate everything from memory');
      process.exit(1);
    }
    genArgs.push('--topic', topic);
  }

  try {
    execFileSync(process.execPath, [genScript, ...genArgs], {
      env: process.env,
      stdio: 'inherit',
      timeout: 300000,
    });
  } catch (err) {
    console.error(`Generation failed: ${err.message}`);
    process.exit(1);
  }
}

async function cmdSync() {
  if (!RELAY_TOKEN) {
    console.error('CLAWBUDDY_TOKEN is required for sync.');
    process.exit(1);
  }

  ensureDir();
  const files = fs.readdirSync(PEARLS_DIR).filter(f => f.endsWith('.md')).sort();
  if (files.length === 0) {
    console.error('No pearls found. Generate or create some first.');
    process.exit(1);
  }

  const specialties = files.map(f => slugToTitle(f.replace(/\.md$/, '')));
  console.log(`Syncing ${specialties.length} specialties to relay: ${specialties.join(', ')}`);

  try {
    const res = await fetch(`${RELAY_URL}/api/buddy/profile`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${RELAY_TOKEN}`,
      },
      body: JSON.stringify({ specialties }),
    });

    if (res.ok) {
      const data = await res.json();
      console.log('Relay specialties updated.');
    } else {
      const err = await res.text();
      console.error(`Sync failed (${res.status}): ${err}`);
      process.exit(1);
    }
  } catch (err) {
    console.error(`Could not reach relay: ${err.message}`);
    process.exit(1);
  }
}

// --- Content reader (stdin or --file) ---

function getContent(args) {
  const fileIdx = args.indexOf('--file');
  if (fileIdx >= 0 && args[fileIdx + 1]) {
    const filePath = path.resolve(args[fileIdx + 1]);
    if (!fs.existsSync(filePath)) {
      console.error(`File not found: ${filePath}`);
      process.exit(1);
    }
    return fs.readFileSync(filePath, 'utf-8');
  }

  // Read from stdin
  try {
    return fs.readFileSync(0, 'utf-8');
  } catch {
    console.error('No content provided. Use --file or pipe content via stdin.');
    process.exit(1);
  }
}

// --- Main ---

async function main() {
  const [command, ...args] = process.argv.slice(2);

  if (!command || command === 'help' || command === '--help') {
    console.log(`OpenClaw Buddy -- Pearl Manager

Usage: node pearls.js <command> [args]

Commands:
  list                          List all pearls with sizes
  read <slug>                   Print a pearl's content
  create <slug> [--file path]   Create a pearl (from stdin or file)
  edit <slug> [--file path]     Replace a pearl (from stdin or file)
  delete <slug>                 Delete a pearl
  rename <old> <new>            Rename a pearl
  generate <topic>              Generate a pearl on a specific topic
  generate --all                Regenerate all pearls from memory
  sync                          Update relay specialties from pearls

Environment:
  PEARLS_DIR          Pearl directory (default: ./pearls/)
  CLAWBUDDY_URL      Relay server URL
  CLAWBUDDY_TOKEN    Buddy API token (for sync)
  OPENCLAW_GATEWAY_URL  Gateway URL (for generate)
  OPENCLAW_GATEWAY_TOKEN  Gateway token (for generate)

Examples:
  node pearls.js list
  node pearls.js read memory-management
  echo "# Docker Tips\\n..." | node pearls.js create docker-tips
  node pearls.js create docker-tips --file /path/to/pearl.md
  node pearls.js edit docker-tips --file /path/to/updated.md
  node pearls.js delete n8n-workflows
  node pearls.js rename old-name new-name
  node pearls.js generate "CI/CD pipelines"
  node pearls.js generate --all
  node pearls.js sync`);
    process.exit(0);
  }

  switch (command) {
    case 'list':
      cmdList();
      break;
    case 'read':
    case 'show':
    case 'cat':
      cmdRead(args);
      break;
    case 'create':
    case 'add':
    case 'new':
      cmdCreate(args);
      break;
    case 'edit':
    case 'update':
    case 'replace':
      cmdEdit(args);
      break;
    case 'delete':
    case 'rm':
    case 'remove':
      cmdDelete(args);
      break;
    case 'rename':
    case 'mv':
    case 'move':
      cmdRename(args);
      break;
    case 'generate':
    case 'gen':
      await cmdGenerate(args);
      break;
    case 'sync':
      await cmdSync();
      break;
    default:
      console.error(`Unknown command: ${command}`);
      console.error('Run "node pearls.js help" for usage.');
      process.exit(1);
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
