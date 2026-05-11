#!/usr/bin/env node
/**
 * Meta Facebook Inbox Setup Wizard
 * Supports multiple Facebook pages with custom aliases.
 * Run: node setup.js
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const CONFIG_PATH = path.join(__dirname, '..', 'config.json');
const DEFAULT_ALIAS = 'fb fanpage';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(prompt) {
  return new Promise(resolve => rl.question(prompt, resolve));
}

function loadConfig() {
  if (fs.existsSync(CONFIG_PATH)) {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  }
  return { pages: [] };
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2) + '\n', 'utf8');
}

function validateUrl(url) {
  return url.startsWith('https://business.facebook.com/') || url.startsWith('https://www.facebook.com/');
}

function showPages(pages) {
  if (pages.length === 0) {
    console.log('  (no pages configured)\n');
    return;
  }
  pages.forEach((p, i) => {
    console.log(`  ${i + 1}. [${p.alias}] ${p.url}`);
  });
  console.log('');
}

async function addPage(config) {
  console.log('\n📋 Instructions:');
  console.log('  1. Open Meta Business Suite in your browser');
  console.log('  2. Go to the Inbox of your Facebook page');
  console.log('  3. Copy the full URL from the address bar');
  console.log('     (e.g. https://business.facebook.com/latest/inbox/all/?&asset_id=123456)\n');

  let url = '';
  while (!url) {
    const input = await question('Paste the Facebook Inbox URL: ');
    const trimmed = input.trim();
    if (!trimmed) {
      console.log('❌ URL cannot be empty.\n');
      continue;
    }
    if (!validateUrl(trimmed)) {
      console.log('❌ URL must start with https://business.facebook.com/ or https://www.facebook.com/\n');
      continue;
    }
    url = trimmed;
  }

  const aliasInput = await question(`Give this page an alias (default: "${DEFAULT_ALIAS}"): `);
  const alias = aliasInput.trim() || DEFAULT_ALIAS;

  // Check for duplicate alias
  const existing = config.pages.find(p => p.alias === alias);
  if (existing) {
    const overwrite = await question(`⚠️  Alias "${alias}" already exists. Overwrite? (y/N): `);
    if (overwrite.toLowerCase() !== 'y') {
      console.log('Skipped.\n');
      return;
    }
    existing.url = url;
  } else {
    config.pages.push({ alias, url });
  }

  saveConfig(config);
  console.log(`\n✅ Page saved: [${alias}] ${url}\n`);
}

async function removePage(config) {
  if (config.pages.length === 0) {
    console.log('No pages to remove.\n');
    return;
  }
  showPages(config.pages);
  const num = await question('Enter page number to remove (or 0 to cancel): ');
  const idx = parseInt(num, 10) - 1;
  if (idx < 0 || idx >= config.pages.length) {
    console.log('Cancelled.\n');
    return;
  }
  const removed = config.pages.splice(idx, 1)[0];
  saveConfig(config);
  console.log(`✅ Removed: [${removed.alias}]\n`);
}

async function main() {
  console.log('\n🔧 Meta Facebook Inbox Setup\n');

  const config = loadConfig();

  console.log('Current pages:');
  showPages(config.pages);

  let running = true;
  while (running) {
    const choice = await question('What would you like to do?\n  1. Add a page\n  2. Remove a page\n  3. Done\n\nChoice (1/2/3): ');
    switch (choice.trim()) {
      case '1':
        await addPage(config);
        break;
      case '2':
        await removePage(config);
        break;
      case '3':
      default:
        running = false;
        break;
    }
  }

  console.log('Current configuration:');
  showPages(config.pages);
  console.log('Setup complete. You can re-run this script anytime to add or remove pages.\n');
  rl.close();
}

main().catch(err => {
  console.error('Error:', err);
  rl.close();
  process.exit(1);
});
