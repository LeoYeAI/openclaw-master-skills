#!/usr/bin/env node
/**
 * Four.meme - sell quote via TokenManagerHelper3.trySell (BSC only).
 * Usage: npx tsx quote-sell.ts <tokenAddress> <amountWei>
 */

import { createPublicClient, http } from 'viem';
import { bsc } from 'viem/chains';

const HELPER_ADDRESS = '0xF251F83e40a78868FcfA3FA4599Dad6494E46034' as const;

const HELPER_ABI = [
  {
    name: 'trySell',
    type: 'function',
    stateMutability: 'view',
    inputs: [
      { name: 'token', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
    outputs: [
      { name: 'tokenManager', type: 'address' },
      { name: 'quote', type: 'address' },
      { name: 'funds', type: 'uint256' },
      { name: 'fee', type: 'uint256' },
    ],
  },
] as const;

const RPC_URL = process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org';

async function main() {
  const tokenAddress = process.argv[2] as `0x${string}`;
  const amountWei = BigInt(process.argv[3] ?? '0');

  if (!tokenAddress) {
    console.error('Usage: npx tsx quote-sell.ts <tokenAddress> <amountWei>');
    console.error('BSC only.');
    process.exit(1);
  }

  const client = createPublicClient({
    chain: bsc,
    transport: http(RPC_URL),
  });

  const [tokenManager, quote, funds, fee] = await client.readContract({
    address: HELPER_ADDRESS,
    abi: HELPER_ABI,
    functionName: 'trySell',
    args: [tokenAddress, amountWei],
  });

  const out = {
    tokenManager,
    quote: quote === '0x0000000000000000000000000000000000000000' ? 'native' : quote,
    funds: funds.toString(),
    fee: fee.toString(),
  };
  console.log(JSON.stringify(out, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
