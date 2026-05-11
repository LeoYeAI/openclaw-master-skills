#!/usr/bin/env node

import process from 'node:process';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

function printHelp() {
  console.log(`Usage: resolve-openclaw-user-timezone.mjs [options]

Options:
  --configured-timezone <iana>  Override configured user timezone (mainly for tests)
  --host-timezone <iana>        Override detected host timezone (mainly for tests)
  --field <name>                Print one field: timezone|source
  --json                        Print the full resolved timezone as JSON
  --help                        Show this message
`);
}

function parseArgValue(argv, index, current, label) {
  if (current.includes('=')) {
    return current.slice(current.indexOf('=') + 1);
  }
  const next = argv[index + 1];
  if (!next || next.startsWith('--')) {
    throw new Error(`${label} requires a value`);
  }
  return next;
}

export function validateTimeZone(value) {
  const timeZone = String(value ?? '').trim();
  if (!timeZone) {
    return null;
  }
  try {
    new Intl.DateTimeFormat('en-US', { timeZone }).format(new Date());
    return timeZone;
  } catch {
    return null;
  }
}

export function resolveHostTimeZone(hostTimeZone) {
  return validateTimeZone(hostTimeZone) ?? validateTimeZone(Intl.DateTimeFormat().resolvedOptions().timeZone) ?? 'UTC';
}

export function resolveUserTimeZone({ configuredTimeZone, hostTimeZone } = {}) {
  const configured = validateTimeZone(configuredTimeZone);
  if (configured) {
    return {
      source: 'config',
      timezone: configured,
    };
  }

  return {
    source: 'host',
    timezone: resolveHostTimeZone(hostTimeZone),
  };
}

async function readConfiguredUserTimeZone() {
  try {
    const { stdout } = await execFileAsync('openclaw', ['config', 'get', 'agents.defaults.userTimezone'], {
      env: process.env,
    });
    return String(stdout ?? '').trim() || null;
  } catch {
    return null;
  }
}

function parseOptions(argv) {
  const options = {
    configuredTimeZone: null,
    field: null,
    hostTimeZone: null,
    json: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg.startsWith('--configured-timezone')) {
      options.configuredTimeZone = parseArgValue(argv, index, arg, '--configured-timezone').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--host-timezone')) {
      options.hostTimeZone = parseArgValue(argv, index, arg, '--host-timezone').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--field')) {
      options.field = parseArgValue(argv, index, arg, '--field').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg === '--json') {
      options.json = true;
      continue;
    }
    throw new Error(`unknown option: ${arg}`);
  }

  if (options.field && !new Set(['timezone', 'source']).has(options.field)) {
    throw new Error('--field must be one of: timezone, source');
  }

  return options;
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const configuredTimeZone = options.configuredTimeZone ?? (await readConfiguredUserTimeZone());
  const resolved = resolveUserTimeZone({
    configuredTimeZone,
    hostTimeZone: options.hostTimeZone,
  });

  if (options.json) {
    process.stdout.write(`${JSON.stringify(resolved, null, 2)}\n`);
    return;
  }

  if (options.field === 'source') {
    process.stdout.write(`${resolved.source}\n`);
    return;
  }
  if (options.field === 'timezone') {
    process.stdout.write(`${resolved.timezone}\n`);
    return;
  }

  process.stdout.write(`${resolved.timezone}\n`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  });
}
