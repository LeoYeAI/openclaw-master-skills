#!/usr/bin/env node
import './_env.js';
// Prints the decrypted private key to stdout ONLY when explicitly acknowledged.
// Do NOT paste the output into chat. Redirect to a local file if you must.

import fs from 'node:fs/promises';
import { Wallet } from 'ethers';
import { arg } from './_lib.js';

const ack = process.argv.includes('--i-know-what-im-doing');
if (!ack) {
  console.error('Refusing to export private key without --i-know-what-im-doing');
  console.error('Example: node export_private_key.js --i-know-what-im-doing > private_key.txt');
  process.exit(2);
}

const keystorePath = arg('keystore', process.env.VERDIKTA_KEYSTORE_PATH);
const password = process.env.VERDIKTA_WALLET_PASSWORD;
if (!keystorePath || !password) {
  console.error('Set VERDIKTA_KEYSTORE_PATH and VERDIKTA_WALLET_PASSWORD (or pass --keystore).');
  process.exit(1);
}

const json = await fs.readFile(keystorePath, 'utf-8');
const wallet = await Wallet.fromEncryptedJson(json, password);

// Print only the private key (no extra formatting)
process.stdout.write(wallet.privateKey.replace(/^0x/, '') + '\n');
