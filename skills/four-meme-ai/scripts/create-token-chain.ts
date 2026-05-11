#!/usr/bin/env node
/**
 * Four.meme - submit createToken tx on BSC (TokenManager2.createToken).
 * Uses createArg and signature from create-token-api.ts output.
 *
 * Usage:
 *   npx tsx create-token-chain.ts <createArgHex> <signatureHex> [--value=wei]
 *   ... | npx tsx create-token-chain.ts -- [--value=wei]
 *
 * Env: PRIVATE_KEY. Optional: CREATION_FEE_WEI, BSC_RPC_URL.
 */

import { createWalletClient, http, parseAbi } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { bsc } from 'viem/chains';

const TOKEN_MANAGER2_BSC = '0x5c952063c7fc8610FFDB798152D69F0B9550762b' as const;

const ABI = parseAbi([
  'function createToken(bytes args, bytes signature) payable',
]);

/** Get option from argv --key=value, or env var. */
function getOpt(key: string, envKey: string, defaultValue: string): string {
  const prefix = key + '=';
  for (let i = 2; i < process.argv.length; i++) {
    const arg = process.argv[i];
    if (arg.startsWith(prefix)) return arg.slice(prefix.length);
  }
  return process.env[envKey] ?? defaultValue;
}

function toHex(s: string): `0x${string}` {
  if (s.startsWith('0x')) return s as `0x${string}`;
  if (/^[0-9a-fA-F]+$/.test(s)) return ('0x' + s) as `0x${string}`;
  const buf = Buffer.from(s, 'base64');
  return ('0x' + buf.toString('hex')) as `0x${string}`;
}

async function main() {
  const privateKey = process.env.PRIVATE_KEY;
  if (!privateKey) {
    console.error('Set PRIVATE_KEY');
    process.exit(1);
  }
  const pk = privateKey.startsWith('0x') ? (privateKey as `0x${string}`) : (`0x${privateKey}` as `0x${string}`);
  const account = privateKeyToAccount(pk);

  const positionals = process.argv.slice(2).filter((a) => !a.startsWith('--') || a === '--');
  let createArgHex: `0x${string}`;
  let signatureHex: `0x${string}`;
  let creationFeeWei = 0n;
  let stdinJson: { createArg: string; signature: string; creationFeeWei?: string } | null = null;

  if (positionals[0] === '--' || !positionals[0]) {
    const chunks: Buffer[] = [];
    for await (const chunk of process.stdin) chunks.push(Buffer.from(chunk));
    const parsed = JSON.parse(Buffer.concat(chunks).toString('utf8')) as {
      createArg: string;
      signature: string;
      creationFeeWei?: string;
    };
    stdinJson = parsed;
    createArgHex = toHex(parsed.createArg);
    signatureHex = toHex(parsed.signature);
  } else {
    const arg2 = positionals[1];
    if (!arg2) {
      console.error('Usage: npx tsx create-token-chain.ts <createArgHex> <signatureHex> [--value=wei]');
      console.error('   or: ... | npx tsx create-token-chain.ts -- [--value=wei]');
      process.exit(1);
    }
    createArgHex = toHex(positionals[0]);
    signatureHex = toHex(arg2);
  }

  const valueStr = getOpt('--value', 'CREATION_FEE_WEI', '');
  if (valueStr) creationFeeWei = BigInt(valueStr);
  else if (stdinJson?.creationFeeWei) creationFeeWei = BigInt(stdinJson.creationFeeWei);

  const rpcUrl = process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org';
  const client = createWalletClient({
    account,
    chain: bsc,
    transport: http(rpcUrl),
  });

  const hash = await client.writeContract({
    address: TOKEN_MANAGER2_BSC,
    abi: ABI,
    functionName: 'createToken',
    args: [createArgHex, signatureHex],
    value: creationFeeWei,
  });

  console.log(JSON.stringify({ txHash: hash }, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
