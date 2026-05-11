#!/usr/bin/env node

import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { readFile } from 'node:fs/promises';

const DEFAULT_SESSIONS_PATH = path.join(
  os.homedir(),
  '.openclaw',
  'agents',
  'main',
  'sessions',
  'sessions.json',
);
const DEFAULT_TELEGRAM_ALLOW_FROM_PATH = path.join(
  os.homedir(),
  '.openclaw',
  'credentials',
  'telegram-default-allowFrom.json',
);

function printHelp() {
  console.log(`Usage: resolve-openclaw-delivery-target.mjs [options]

Options:
  --sessions-path <path>     Override OpenClaw sessions.json path
  --allow-from-path <path>   Override telegram allowFrom path
  --field <name>             Print one field: channel|to|account-id|session-key|source
  --json                     Print the full resolved target as JSON
  --help                     Show this message
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

async function readJsonIfPresent(filePath) {
  try {
    return JSON.parse(await readFile(filePath, 'utf8'));
  } catch (error) {
    if (error && typeof error === 'object' && 'code' in error && error.code === 'ENOENT') {
      return null;
    }
    if (error instanceof SyntaxError) {
      throw new Error(`invalid JSON at ${filePath}`);
    }
    throw error;
  }
}

export function normalizeDeliveryTo(value) {
  const text = String(value ?? '').trim();
  if (!text) {
    return null;
  }
  if (text.startsWith('telegram:')) {
    const normalized = text.slice('telegram:'.length).trim();
    return normalized || null;
  }
  return text;
}

export function normalizeChannel(value) {
  const text = String(value ?? '').trim().toLowerCase();
  return text || null;
}

export function normalizeDeliveryToForChannel(value, channel) {
  const text = String(value ?? '').trim();
  if (!text) {
    return null;
  }
  const normalizedChannel = normalizeChannel(channel);
  if (normalizedChannel && text.toLowerCase().startsWith(`${normalizedChannel}:`)) {
    const normalized = text.slice(normalizedChannel.length + 1).trim();
    return normalized || null;
  }
  return normalizeDeliveryTo(text);
}

function numericTimestamp(value) {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === 'string' && value.trim()) {
    const asNumber = Number(value);
    if (Number.isFinite(asNumber)) {
      return asNumber;
    }
    const asDate = Date.parse(value);
    if (Number.isFinite(asDate)) {
      return asDate;
    }
  }
  return 0;
}

export function collectDirectSessionCandidates(input) {
  if (!input || typeof input !== 'object') {
    return [];
  }

  const candidates = [];
  for (const [sessionKey, session] of Object.entries(input)) {
    if (!session || typeof session !== 'object') {
      continue;
    }

    const origin = session.origin ?? {};
    const deliveryContext = session.deliveryContext ?? {};
    const channel = normalizeChannel(
      deliveryContext.channel ?? origin.provider ?? origin.surface ?? session.lastChannel ?? null,
    );
    const direct = session.chatType === 'direct' || origin.chatType === 'direct' || sessionKey.includes(':direct:');
    if (!channel || !direct) {
      continue;
    }

    const to = normalizeDeliveryToForChannel(
      deliveryContext.to ?? session.lastTo ?? origin.to ?? origin.from ?? sessionKey.split(':').at(-1) ?? null,
      channel,
    );
    if (!to) {
      continue;
    }

    candidates.push({
      accountId:
        typeof deliveryContext.accountId === 'string' && deliveryContext.accountId.trim()
          ? deliveryContext.accountId.trim()
          : typeof session.lastAccountId === 'string' && session.lastAccountId.trim()
            ? session.lastAccountId.trim()
            : typeof origin.accountId === 'string' && origin.accountId.trim()
            ? origin.accountId.trim()
            : null,
      channel,
      sessionKey,
      source: 'sessions',
      to,
      updatedAt: numericTimestamp(session.updatedAt),
    });
  }

  candidates.sort((left, right) => right.updatedAt - left.updatedAt);
  return candidates;
}

export function collectTelegramSessionCandidates(input) {
  return collectDirectSessionCandidates(input).filter((candidate) => candidate.channel === 'telegram');
}

export function resolveTelegramAllowFromTarget(input) {
  const allowFrom = Array.isArray(input?.allowFrom) ? input.allowFrom : [];
  const first = normalizeDeliveryTo(allowFrom[0] ?? null);
  if (!first) {
    return null;
  }
  return {
    accountId: null,
    channel: 'telegram',
    sessionKey: null,
    source: 'allow_from',
    to: first,
    updatedAt: 0,
  };
}

export function resolveDeliveryTarget({ sessions, telegramAllowFrom }) {
  const sessionTarget = collectDirectSessionCandidates(sessions)[0] ?? null;
  if (sessionTarget) {
    return sessionTarget;
  }
  return resolveTelegramAllowFromTarget(telegramAllowFrom);
}

function parseOptions(argv) {
  const options = {
    allowFromPath: DEFAULT_TELEGRAM_ALLOW_FROM_PATH,
    field: null,
    json: false,
    sessionsPath: DEFAULT_SESSIONS_PATH,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg.startsWith('--sessions-path')) {
      options.sessionsPath = parseArgValue(argv, index, arg, '--sessions-path').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--allow-from-path')) {
      options.allowFromPath = parseArgValue(argv, index, arg, '--allow-from-path').trim();
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

  if (options.field && !new Set(['channel', 'to', 'account-id', 'session-key', 'source']).has(options.field)) {
    throw new Error('--field must be one of: channel, to, account-id, session-key, source');
  }

  return options;
}

async function main() {
  const options = parseOptions(process.argv.slice(2));
  const sessions = await readJsonIfPresent(options.sessionsPath);
  const telegramAllowFrom = await readJsonIfPresent(options.allowFromPath);
  const resolved = resolveDeliveryTarget({ sessions, telegramAllowFrom });

  if (!resolved) {
    process.exit(2);
  }

  if (options.json) {
    process.stdout.write(`${JSON.stringify(resolved, null, 2)}\n`);
    return;
  }

  if (options.field === 'to') {
    process.stdout.write(`${resolved.to}\n`);
    return;
  }
  if (options.field === 'channel') {
    if (resolved.channel) {
      process.stdout.write(`${resolved.channel}\n`);
    }
    return;
  }
  if (options.field === 'account-id') {
    if (resolved.accountId) {
      process.stdout.write(`${resolved.accountId}\n`);
    }
    return;
  }
  if (options.field === 'session-key') {
    if (resolved.sessionKey) {
      process.stdout.write(`${resolved.sessionKey}\n`);
    }
    return;
  }
  if (options.field === 'source') {
    process.stdout.write(`${resolved.source}\n`);
    return;
  }

  process.stdout.write(`${resolved.to}\n`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  });
}
