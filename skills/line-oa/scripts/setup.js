#!/usr/bin/env node
/**
 * LINE Official Account Setup Wizard
 * Run: node setup.js
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { exec } = require('child_process');

const CONFIG_PATH = path.join(__dirname, '..', 'config.json');
const LINE_OA_URL = 'https://chat.line.biz/';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(prompt) {
  return new Promise(resolve => rl.question(prompt, resolve));
}

function openBrowser(url) {
  const platform = process.platform;
  const cmd = platform === 'darwin' ? 'open' :
              platform === 'win32' ? 'start' :
              'xdg-open';
  
  exec(`${cmd} "${url}"`, (err) => {
    if (err) {
      console.log(`⚠️  Could not auto-open browser. Please manually visit: ${url}`);
    }
  });
}

async function main() {
  console.log('\n🔧 LINE Official Account Setup\n');
  
  // Check if config already exists
  if (fs.existsSync(CONFIG_PATH)) {
    const existing = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    console.log(`✅ Configuration already exists:`);
    console.log(`   ${existing.chatUrl}\n`);
    const overwrite = await question('Do you want to reconfigure? (y/N): ');
    if (overwrite.toLowerCase() !== 'y') {
      console.log('Setup cancelled.\n');
      rl.close();
      return;
    }
  }

  console.log('Opening LINE Official Account Manager in your browser...\n');
  openBrowser(LINE_OA_URL);
  
  console.log('📋 Instructions:');
  console.log('  1. Log in with your LINE Business ID');
  console.log('  2. Select your official account from the list');
  console.log('  3. Once on the chat interface, copy the full URL from the address bar');
  console.log('     (Should look like: https://chat.line.biz/Uebba4fb369276676ecc288d8b7181e49)\n');
  
  let chatUrl = '';
  let valid = false;
  
  while (!valid) {
    chatUrl = await question('Paste your LINE OA chat URL here: ');
    chatUrl = chatUrl.trim();
    
    if (!chatUrl) {
      console.log('❌ URL cannot be empty. Try again.\n');
      continue;
    }
    
    if (!chatUrl.startsWith('https://chat.line.biz/')) {
      console.log('❌ Invalid URL. Must start with https://chat.line.biz/\n');
      continue;
    }
    
    const parts = chatUrl.split('/');
    const accountId = parts[parts.length - 1];
    
    if (!accountId || accountId.length < 10) {
      console.log('❌ URL seems incomplete. Make sure to copy the full URL.\n');
      continue;
    }
    
    valid = true;
  }
  
  // Write config
  const config = { chatUrl };
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2) + '\n', 'utf8');
  
  console.log('\n✅ Configuration saved!');
  console.log(`   ${chatUrl}`);
  console.log('\nYou can now use LINE OA commands with OpenClaw.\n');
  
  rl.close();
}

main().catch(err => {
  console.error('Error:', err);
  rl.close();
  process.exit(1);
});
