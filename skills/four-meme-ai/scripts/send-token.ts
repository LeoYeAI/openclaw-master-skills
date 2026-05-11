#!/usr/bin/env node
/**
 * Four.meme - send BNB or ERC20 from current wallet to a target address (BSC).
 *
 * Usage:
 *   npx tsx send-token.ts <toAddress> <amountWei> [tokenAddress]
 *   - toAddress: recipient wallet address (0x...)
 *   - amountWei: amount in wei (for BNB or token decimals)
 *   - tokenAddress: optional; omit or use "BNB" / "0x0" for native BNB; otherwise ERC20 token contract address
 *
 * Env: PRIVATE_KEY. Optional: BSC_RPC_URL.
 */

import { createWalletClient, http, parseAbi } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { bsc } from 'viem/chains';

const ZERO = '0x0000000000000000000000000000000000000000' as const;

const ERC20_ABI = parseAbi([
  'function transfer(address to, uint256 amount) returns (bool)',
]);

function isAddress(s: string): boolean {
  return /^0x[0-9a-fA-F]{40}$/.test(s);
}

async function main() {
  const privateKey = process.env.PRIVATE_KEY;
  if (!privateKey) {
    console.error('Set PRIVATE_KEY');
    process.exit(1);
  }
  const pk = privateKey.startsWith('0x') ? (privateKey as `0x${string}`) : (`0x${privateKey}` as `0x${string}`);
  const account = privateKeyToAccount(pk);

  const toAddress = process.argv[2];
  const amountWeiRaw = process.argv[3];
  const tokenAddress = process.argv[4]; // optional: BNB if omitted or "BNB" or 0x0

  if (!toAddress || !amountWeiRaw) {
    console.error('Usage: send-token.ts <toAddress> <amountWei> [tokenAddress]');
    console.error('  toAddress:   recipient 0x... address');
    console.error('  amountWei:   amount in wei (for BNB or token smallest unit)');
    console.error('  tokenAddress: optional; omit or BNB/0x0 = native BNB; else ERC20 contract address');
    process.exit(1);
  }
  if (!isAddress(toAddress)) {
    console.error('Invalid toAddress:', toAddress);
    process.exit(1);
  }

  const amountWei = BigInt(amountWeiRaw);
  if (amountWei <= 0n) {
    console.error('amountWei must be positive');
    process.exit(1);
  }

  const isNative =
    !tokenAddress ||
    tokenAddress.toUpperCase() === 'BNB' ||
    tokenAddress === ZERO ||
    tokenAddress.toLowerCase() === '0x0000000000000000000000000000000000000000';

  const rpcUrl = process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org';
  const client = createWalletClient({
    account,
    chain: bsc,
    transport: http(rpcUrl),
  });

  let txHash: `0x${string}`;

  if (isNative) {
    txHash = await client.sendTransaction({
      to: toAddress as `0x${string}`,
      value: amountWei,
    });
  } else {
    if (!isAddress(tokenAddress)) {
      console.error('Invalid tokenAddress:', tokenAddress);
      process.exit(1);
    }
    txHash = await client.writeContract({
      address: tokenAddress as `0x${string}`,
      abi: ERC20_ABI,
      functionName: 'transfer',
      args: [toAddress as `0x${string}`, amountWei],
    });
  }

  console.log(JSON.stringify({ txHash, to: toAddress, amountWei: amountWei.toString(), native: isNative }, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
