#!/usr/bin/env node
/**
 * Four.meme - One-shot create token: API (create-token-api) + on-chain (create-token-chain).
 * Same args as create-token-api; on success submits createToken tx and outputs txHash.
 *
 * Usage: same as create-token-api, all --key=value
 *   npx tsx create-token-instant.ts --image=./logo.png --name=MyToken --short-name=MTK --desc="My desc" --label=AI [options]
 *
 * Env: PRIVATE_KEY. Optional: BSC_RPC_URL.
 * Options: same as create-token-api (--web-url=, --pre-sale=0, --fee-plan, --tax-options=, --tax-token, etc.).
 * Value for createToken uses API output creationFeeWei; override with --value=wei.
 */

import { createWalletClient, http, parseAbi } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { bsc } from 'viem/chains';
import { runCreateTokenApi } from './create-token-api.ts';

const TOKEN_MANAGER2_BSC = '0x5c952063c7fc8610FFDB798152D69F0B9550762b' as const;
const ABI = parseAbi([
  'function createToken(bytes args, bytes signature) payable',
]);

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

  const data = await runCreateTokenApi();

  const createArgHex = toHex(data.createArg);
  const signatureHex = toHex(data.signature);
  const valueStr = getOpt('--value', 'CREATION_FEE_WEI', '');
  const creationFeeWei = valueStr ? BigInt(valueStr) : BigInt(data.creationFeeWei ?? '0');

  const pk = privateKey.startsWith('0x') ? (privateKey as `0x${string}`) : (`0x${privateKey}` as `0x${string}`);
  const account = privateKeyToAccount(pk);
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
