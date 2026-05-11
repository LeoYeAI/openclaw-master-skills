#!/usr/bin/env node

import os from 'node:os';
import path from 'node:path';
import process from 'node:process';

export function readEnvOptionalString(name) {
  const raw = process.env[name];
  if (typeof raw !== 'string') {
    return null;
  }
  const trimmed = raw.trim();
  return trimmed ? trimmed : null;
}

export function readEnvString(name, fallback = '') {
  return readEnvOptionalString(name) ?? fallback;
}

export function readEnvFlag(name, fallback = false) {
  const raw = process.env[name];
  if (typeof raw !== 'string' || !raw.trim()) {
    return fallback;
  }

  switch (raw.trim().toLowerCase()) {
    case '1':
    case 'true':
    case 'yes':
    case 'on':
      return true;
    case '0':
    case 'false':
    case 'no':
    case 'off':
      return false;
    default:
      throw new Error(`invalid boolean value in ${name}: ${raw}`);
  }
}

export function readEnvParsed(name, fallback, parseFn) {
  const raw = readEnvOptionalString(name);
  return raw === null ? fallback : parseFn(raw, name);
}

export function resolveWorkspaceRootFromEnv(defaultRoot = path.join(os.homedir(), '.openclaw', 'workspace')) {
  return path.resolve(readEnvOptionalString('OPENCLAW_WORKSPACE_ROOT') ?? defaultRoot);
}

export function getProcessEnvSnapshot(overrides = {}) {
  return {
    ...process.env,
    ...overrides,
  };
}
