#!/usr/bin/env node
// Minimal helper to run Jules commands with predictable output.
// Usage examples:
//   node scripts/jules.js version
//   node scripts/jules.js list-sessions
//   node scripts/jules.js new --repo . --task "write unit tests"
//   node scripts/jules.js pull --session 123456

import { spawnSync } from 'node:child_process';

function die(msg, code = 1) {
  console.error(msg);
  process.exit(code);
}

function run(args) {
  const r = spawnSync('jules', args, { encoding: 'utf8' });
  if (r.error) die(String(r.error));
  if (r.status !== 0) {
    // forward stderr for debugging
    process.stderr.write(r.stderr || '');
    process.stdout.write(r.stdout || '');
    process.exit(r.status ?? 1);
  }
  return r.stdout;
}

function arg(name) {
  const i = process.argv.indexOf(name);
  if (i === -1) return null;
  return process.argv[i + 1] || null;
}

const cmd = process.argv[2];
if (!cmd || cmd === '--help' || cmd === '-h') {
  console.log('Usage: node scripts/jules.js <version|list-repos|list-sessions|new|pull> ...');
  process.exit(0);
}

if (cmd === 'version') {
  process.stdout.write(run(['version']));
  process.exit(0);
}

if (cmd === 'list-repos') {
  process.stdout.write(run(['remote', 'list', '--repo']));
  process.exit(0);
}

if (cmd === 'list-sessions') {
  process.stdout.write(run(['remote', 'list', '--session']));
  process.exit(0);
}

if (cmd === 'new') {
  const repo = arg('--repo') || '.';
  const task = arg('--task') || arg('--session');
  if (!task) die('Missing --task (or --session)');
  const parallel = arg('--parallel');
  const args = ['remote', 'new', '--repo', repo, '--session', task];
  if (parallel) args.push('--parallel', parallel);
  process.stdout.write(run(args));
  process.exit(0);
}

if (cmd === 'pull') {
  const session = arg('--session');
  if (!session) die('Missing --session');
  process.stdout.write(run(['remote', 'pull', '--session', session]));
  process.exit(0);
}

die('Unknown command: ' + cmd);
