#!/usr/bin/env node
import './_env.js';
import fs from 'node:fs/promises';
import path from 'node:path';
import { arg, resolvePath } from './_lib.js';
import { defaultSecretsDir, ensureDir } from './_paths.js';

const baseUrl = process.env.VERDIKTA_BOUNTIES_BASE_URL || 'https://bounties.verdikta.org';

const outPathRaw = arg('out', `${defaultSecretsDir()}/verdikta-bounties-bot.json`);
const outPath = resolvePath(outPathRaw);
const name = arg('name');
const owner = arg('owner');
const description = arg('description', 'AI agent worker for Verdikta bounties.');

if (!name || !owner) {
  console.error('Usage: node bot_register.js --name "MyBot" --owner 0x... [--description ...]');
  process.exit(1);
}

const resp = await fetch(`${baseUrl}/api/bots/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name, ownerAddress: owner, description })
});

const data = await resp.json();
if (!resp.ok) {
  throw new Error(`register failed: ${resp.status} ${JSON.stringify(data)}`);
}

await ensureDir(path.dirname(outPath));
await fs.writeFile(outPath, JSON.stringify(data, null, 2), { mode: 0o600 });

console.log('Registered bot. Saved response to:', outPath);
console.log('API key (keep secret):', data?.apiKey || data?.api_key || data?.bot?.apiKey || data?.bot?.api_key || '(check file)');
