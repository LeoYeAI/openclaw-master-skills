#!/usr/bin/env node
import './_env.js';
import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import { Wallet } from 'ethers';
import fs from 'node:fs/promises';
import path from 'node:path';
import { arg, hasFlag, resolvePath } from './_lib.js';
import { defaultSecretsDir, ensureDir } from './_paths.js';

const importMode = hasFlag('import');
const outArg = arg('out', `${defaultSecretsDir()}/verdikta-wallet.json`);
const password = process.env.VERDIKTA_WALLET_PASSWORD;
if (!password) {
  console.error('Missing VERDIKTA_WALLET_PASSWORD');
  process.exit(1);
}

let wallet;

if (importMode) {
  const rl = readline.createInterface({ input, output });
  try {
    const key = (await rl.question('Paste private key (hex, with or without 0x): ')).trim();
    const hex = key.replace(/^0x/, '');
    if (!/^[a-fA-F0-9]{64}$/.test(hex)) {
      console.error('Invalid private key format (expected 64 hex chars).');
      process.exit(1);
    }
    wallet = new Wallet(`0x${hex}`);
  } finally {
    rl.close();
  }
} else {
  wallet = Wallet.createRandom();
}

const json = await wallet.encrypt(password);
const out = resolvePath(outArg);

await ensureDir(path.dirname(out));
await fs.writeFile(out, json, { mode: 0o600 });

console.log(importMode ? 'Wallet imported and encrypted' : 'Bot wallet created');
console.log('Address:', wallet.address);
console.log('Keystore:', out);
console.log('Next: fund this address with ETH on Base, then swap some ETH→LINK.');
