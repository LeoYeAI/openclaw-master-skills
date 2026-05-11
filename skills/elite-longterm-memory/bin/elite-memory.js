#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const TEMPLATES = {
  'session-state': `# SESSION-STATE.md — Active Working Memory

This file is the agent's "RAM" — survives compaction, restarts, distractions.
Chat history is a BUFFER. This file is STORAGE.

## Current Task
[None]

## Key Context
[None yet]

## Pending Actions
- [ ] None

## Recent Decisions
[None yet]

---
*Last updated: ${new Date().toISOString()}*
`,

  'memory-md': `# MEMORY.md — Long-Term Memory

## About the User
[Add user preferences, communication style, etc.]

## Projects
[Active projects and their status]

## Decisions Log
[Important decisions and why they were made]

## Lessons Learned
[Mistakes to avoid, patterns that work]

## Preferences
[Tools, frameworks, workflows the user prefers]

---
*Curated memory — distill insights from daily logs here*
`,

  'daily-template': `# {{DATE}} — Daily Log

## Tasks Completed
- 

## Decisions Made
- 

## Lessons Learned
- 

## Tomorrow
- 
`
};

const commands = {
  init: () => {
    console.log('🧠 Initializing Elite Longterm Memory...\n');
    
    // Create SESSION-STATE.md
    if (!fs.existsSync('SESSION-STATE.md')) {
      fs.writeFileSync('SESSION-STATE.md', TEMPLATES['session-state']);
      console.log('✓ Created SESSION-STATE.md (Hot RAM)');
    } else {
      console.log('• SESSION-STATE.md already exists');
    }
    
    // Create MEMORY.md
    if (!fs.existsSync('MEMORY.md')) {
      fs.writeFileSync('MEMORY.md', TEMPLATES['memory-md']);
      console.log('✓ Created MEMORY.md (Curated Archive)');
    } else {
      console.log('• MEMORY.md already exists');
    }
    
    // Create memory directory
    if (!fs.existsSync('memory')) {
      fs.mkdirSync('memory', { recursive: true });
      console.log('✓ Created memory/ directory');
    } else {
      console.log('• memory/ directory already exists');
    }
    
    // Create today's log
    const today = new Date().toISOString().split('T')[0];
    const todayFile = `memory/${today}.md`;
    if (!fs.existsSync(todayFile)) {
      const content = TEMPLATES['daily-template'].replace('{{DATE}}', today);
      fs.writeFileSync(todayFile, content);
      console.log(`✓ Created ${todayFile}`);
    }
    
    console.log('\n🎉 Elite Longterm Memory initialized!');
    console.log('\nNext steps:');
    console.log('1. Add SESSION-STATE.md to your agent context');
    console.log('2. Configure LanceDB plugin in clawdbot.json');
    console.log('3. Review SKILL.md for full setup guide');
  },
  
  today: () => {
    const today = new Date().toISOString().split('T')[0];
    const todayFile = `memory/${today}.md`;
    
    if (!fs.existsSync('memory')) {
      fs.mkdirSync('memory', { recursive: true });
    }
    
    if (!fs.existsSync(todayFile)) {
      const content = TEMPLATES['daily-template'].replace('{{DATE}}', today);
      fs.writeFileSync(todayFile, content);
      console.log(`✓ Created ${todayFile}`);
    } else {
      console.log(`• ${todayFile} already exists`);
    }
  },
  
  status: () => {
    console.log('🧠 Elite Longterm Memory Status\n');
    
    // Check SESSION-STATE.md
    if (fs.existsSync('SESSION-STATE.md')) {
      const stat = fs.statSync('SESSION-STATE.md');
      console.log(`✓ SESSION-STATE.md (${(stat.size / 1024).toFixed(1)}KB, modified ${stat.mtime.toLocaleString()})`);
    } else {
      console.log('✗ SESSION-STATE.md missing');
    }
    
    // Check MEMORY.md
    if (fs.existsSync('MEMORY.md')) {
      const stat = fs.statSync('MEMORY.md');
      const lines = fs.readFileSync('MEMORY.md', 'utf8').split('\n').length;
      console.log(`✓ MEMORY.md (${lines} lines, ${(stat.size / 1024).toFixed(1)}KB)`);
    } else {
      console.log('✗ MEMORY.md missing');
    }
    
    // Check memory directory
    if (fs.existsSync('memory')) {
      const files = fs.readdirSync('memory').filter(f => f.endsWith('.md'));
      console.log(`✓ memory/ (${files.length} daily logs)`);
    } else {
      console.log('✗ memory/ directory missing');
    }
    
    // Check LanceDB
    const lancedbPath = path.join(process.env.HOME, '.clawdbot/memory/lancedb');
    if (fs.existsSync(lancedbPath)) {
      console.log('✓ LanceDB vectors initialized');
    } else {
      console.log('• LanceDB not initialized (optional)');
    }
  },
  
  help: () => {
    console.log(`
🧠 Elite Longterm Memory CLI

Commands:
  init     Initialize memory system in current directory
  today    Create today's daily log file
  status   Check memory system health
  help     Show this help

Usage:
  npx elite-longterm-memory init
  npx elite-longterm-memory status
`);
  }
};

const command = process.argv[2] || 'help';

if (commands[command]) {
  commands[command]();
} else {
  console.log(`Unknown command: ${command}`);
  commands.help();
}
