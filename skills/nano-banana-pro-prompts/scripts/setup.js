#!/usr/bin/env node
/**
 * setup.js - Downloads/updates Nano Banana Pro prompt library from GitHub
 *
 * Fully dynamic: reads manifest.json first to discover all categories.
 * New/renamed/removed categories are handled automatically — no hardcoding.
 *
 * Usage:
 *   node scripts/setup.js           # Download missing files only
 *   node scripts/setup.js --force   # Force re-download all (get latest)
 *   node scripts/setup.js --check   # Auto-update if stale (> 24h)
 */

import { existsSync, mkdirSync, statSync, writeFileSync, readFileSync, readdirSync, unlinkSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const refsDir = join(__dirname, '..', 'references');
const stampFile = join(refsDir, '.last-updated');

const BASE_URL = 'https://raw.githubusercontent.com/YouMind-OpenLab/nano-banana-pro-prompts-recommend-skill/main/references';
const STALE_HOURS = 24;

function isStale() {
  if (!existsSync(stampFile)) return true;
  const ts = parseInt(readFileSync(stampFile, 'utf8').trim(), 10);
  return (Date.now() - ts) / 1000 / 3600 > STALE_HOURS;
}

async function fetchText(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} — ${url}`);
  return res.text();
}

async function setup() {
  const args = process.argv.slice(2);
  const forceMode = args.includes('--force');
  const checkMode = args.includes('--check');

  if (checkMode && !isStale()) {
    // Silent no-op when fresh
    return;
  }

  if (!existsSync(refsDir)) mkdirSync(refsDir, { recursive: true });

  const label = forceMode ? 'Updating' : 'Downloading';
  console.log(`[setup] ${label} Nano Banana Pro prompt library from GitHub...`);

  // Step 1: Fetch manifest — discover categories dynamically
  let categories;
  try {
    const manifestText = await fetchText(`${BASE_URL}/manifest.json`);
    const manifest = JSON.parse(manifestText);
    categories = manifest.categories; // [{ slug, title, file, count }]
    // Save manifest locally
    writeFileSync(join(refsDir, 'manifest.json'), manifestText, 'utf8');
    console.log(`  manifest: ${categories.length} categories, ${manifest.totalPrompts} prompts total`);
  } catch (err) {
    console.warn(`[setup] Could not fetch manifest: ${err.message}`);
    console.warn('[setup] Falling back to existing local manifest...');
    const localManifest = join(refsDir, 'manifest.json');
    if (!existsSync(localManifest)) {
      console.error('[setup] No manifest available. Run with --force to retry.');
      process.exit(0);
    }
    categories = JSON.parse(readFileSync(localManifest, 'utf8')).categories;
  }

  // Step 2: Clean up stale files not in current manifest
  const validFiles = new Set([...categories.map(c => c.file), 'manifest.json', '.last-updated', '.gitkeep']);
  if (forceMode && existsSync(refsDir)) {
    for (const f of readdirSync(refsDir)) {
      if (!validFiles.has(f)) {
        unlinkSync(join(refsDir, f));
        console.log(`  removed stale: ${f}`);
      }
    }
  }

  // Step 3: Download each category file
  let downloaded = 0, skipped = 0, failed = 0;
  for (const cat of categories) {
    const dest = join(refsDir, cat.file);
    if (!forceMode && existsSync(dest) && statSync(dest).size > 100) {
      skipped++;
      continue;
    }
    process.stdout.write(`  → ${cat.file} (${cat.title}, ${cat.count} prompts) ... `);
    try {
      const text = await fetchText(`${BASE_URL}/${cat.file}`);
      writeFileSync(dest, text, 'utf8');
      console.log('✓');
      downloaded++;
    } catch (err) {
      console.log(`✗ (${err.message})`);
      failed++;
    }
  }

  // Step 4: Write timestamp
  if (failed === 0) writeFileSync(stampFile, String(Date.now()), 'utf8');

  if (downloaded > 0) {
    console.log(`[setup] Done! ${downloaded} file(s) ${forceMode ? 'updated' : 'downloaded'}. Skill is ready.`);
  } else if (skipped === categories.length) {
    console.log('[setup] All references up to date. Use --force to refresh.');
  }
  if (failed > 0) console.warn(`[setup] ${failed} file(s) failed. Run again to retry.`);
}

setup().catch(err => {
  console.warn('[setup] Warning (non-fatal):', err.message);
  process.exit(0);
});
