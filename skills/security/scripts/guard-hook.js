#!/usr/bin/env node

/**
 * GoPlus AgentGuard PreToolUse / PostToolUse Hook (Claude Code)
 *
 * Uses the common adapter + engine architecture.
 * Reads Claude Code hook input from stdin, delegates to evaluateHook(),
 * and outputs allow / deny / ask via Claude Code protocol.
 *
 * PreToolUse exit codes:
 *   0  = allow (or JSON with permissionDecision)
 *   2  = deny  (stderr = reason shown to Claude)
 *
 * PostToolUse: appends audit log entry (async, always exits 0)
 */

import { join } from 'node:path';

// ---------------------------------------------------------------------------
// Load AgentGuard engine + adapters
// ---------------------------------------------------------------------------

const agentguardPath = join(import.meta.url.replace('file://', ''), '..', '..', '..', '..', 'dist', 'index.js');

let createAgentGuard, ClaudeCodeAdapter, evaluateHook, loadConfig;
try {
  const gs = await import(agentguardPath);
  createAgentGuard = gs.createAgentGuard || gs.default;
  ClaudeCodeAdapter = gs.ClaudeCodeAdapter;
  evaluateHook = gs.evaluateHook;
  loadConfig = gs.loadConfig;
} catch {
  try {
    const gs = await import('@goplus/agentguard');
    createAgentGuard = gs.createAgentGuard || gs.default;
    ClaudeCodeAdapter = gs.ClaudeCodeAdapter;
    evaluateHook = gs.evaluateHook;
    loadConfig = gs.loadConfig;
  } catch {
    process.stderr.write('GoPlus AgentGuard: unable to load engine, allowing action\n');
    process.exit(0);
  }
}

// ---------------------------------------------------------------------------
// Read stdin
// ---------------------------------------------------------------------------

function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf-8');
    process.stdin.on('data', (chunk) => (data += chunk));
    process.stdin.on('end', () => {
      try {
        resolve(JSON.parse(data));
      } catch {
        resolve(null);
      }
    });
    setTimeout(() => resolve(null), 5000);
  });
}

// ---------------------------------------------------------------------------
// Claude Code output helpers
// ---------------------------------------------------------------------------

function outputDeny(reason) {
  process.stderr.write(reason + '\n');
  process.exit(2);
}

function outputAsk(reason) {
  console.log(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'ask',
      permissionDecisionReason: reason,
    },
  }));
  process.exit(0);
}

function outputAllow() {
  process.exit(0);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const input = await readStdin();
  if (!input) {
    process.exit(0);
  }

  const adapter = new ClaudeCodeAdapter();
  const config = loadConfig();
  const agentguard = createAgentGuard();

  const result = await evaluateHook(adapter, input, { config, agentguard });

  if (result.decision === 'deny') outputDeny(result.reason || 'Action blocked');
  else if (result.decision === 'ask') outputAsk(result.reason || 'Action requires confirmation');
  else outputAllow();
}

main();
