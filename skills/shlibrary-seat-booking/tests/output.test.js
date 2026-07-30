const test = require('node:test');
const assert = require('node:assert/strict');

const { printUsage } = require('../scripts/lib/output');

test('printUsage includes auth-file and profile-dir options for CLI commands', () => {
  const lines = [];
  const originalLog = console.log;
  console.log = (...args) => {
    lines.push(args.join(' '));
  };

  try {
    printUsage();
  } finally {
    console.log = originalLog;
  }

  const output = lines.join('\n');
  assert.match(output, /\[--profile-dir 目录\]/);
  assert.match(output, /\[--auth-file 文件\]/);
  assert.match(output, /node book_seat\.js list --auth-file/);
});
