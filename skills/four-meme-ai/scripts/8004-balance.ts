#!/usr/bin/env node
/**
 * EIP-8004 NFT – query balance (number of identity NFTs owned by address).
 *
 * Usage:
 *   npx tsx 8004-balance.ts <ownerAddress>
 *
 * Optional env: BSC_RPC_URL, 8004_NFT_ADDRESS.
 * Default contract: 0x8004A169FB4a3325136EB29fA0ceB6D2e539a432 (BSC).
 */

import { createPublicClient, http, parseAbi } from 'viem';
import { bsc } from 'viem/chains';

const DEFAULT_8004_NFT = '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432' as const;

const ABI = parseAbi(['function balanceOf(address owner) view returns (uint256)']);

function isAddress(s: string): boolean {
  return /^0x[0-9a-fA-F]{40}$/.test(s);
}

async function main() {
  const ownerAddress = process.argv[2];
  if (!ownerAddress || !isAddress(ownerAddress)) {
    console.error('Usage: 8004-balance.ts <ownerAddress>');
    console.error('  ownerAddress: 0x... wallet address');
    process.exit(1);
  }

  const contractAddress = (process.env['8004_NFT_ADDRESS'] || process.env.EIP8004_NFT_ADDRESS || DEFAULT_8004_NFT) as `0x${string}`;
  const rpcUrl = process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org';

  const client = createPublicClient({
    chain: bsc,
    transport: http(rpcUrl),
  });

  const balance = await client.readContract({
    address: contractAddress,
    abi: ABI,
    functionName: 'balanceOf',
    args: [ownerAddress as `0x${string}`],
  });

  console.log(JSON.stringify({ owner: ownerAddress, balance: Number(balance) }, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
