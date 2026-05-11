#!/usr/bin/env node
/**
 * Four.meme - get TokenCreate, TokenPurchase, TokenSale, LiquidityAdded from TokenManager2 (V2 only).
 * Usage: npx tsx get-recent-events.ts <chainId> <fromBlock> [toBlock]
 * If toBlock omitted, uses "latest". chainId 56 = BSC (TokenManager2 on BSC only for create; events on BSC).
 */

import { createPublicClient, http, parseAbiItem } from 'viem';
import { bsc } from 'viem/chains';

const TOKEN_MANAGER2_BSC = '0x5c952063c7fc8610FFDB798152D69F0B9550762b' as const;

const EVENTS = [
  parseAbiItem(
    'event TokenCreate(address creator, address token, uint256 requestId, string name, string symbol, uint256 totalSupply, uint256 launchTime, uint256 launchFee)'
  ),
  parseAbiItem(
    'event TokenPurchase(address token, address account, uint256 price, uint256 amount, uint256 cost, uint256 fee, uint256 offers, uint256 funds)'
  ),
  parseAbiItem(
    'event TokenSale(address token, address account, uint256 price, uint256 amount, uint256 cost, uint256 fee, uint256 offers, uint256 funds)'
  ),
  parseAbiItem('event LiquidityAdded(address base, uint256 offers, address quote, uint256 funds)'),
];

function getRpcUrl(chainId: number): string {
  if (chainId !== 56) {
    console.error('Events are only on BSC (chainId 56). TokenManager2 is on BSC.');
    process.exit(1);
  }
  return process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org';
}

async function main() {
  const chainId = parseInt(process.argv[2], 10);
  const fromBlock = process.argv[3];
  const toBlock = process.argv[4]; // optional, "latest" if omitted

  if (!chainId || isNaN(chainId) || chainId !== 56 || !fromBlock) {
    console.error('Usage: npx tsx get-recent-events.ts 56 <fromBlock> [toBlock]');
    console.error('Example: npx tsx get-recent-events.ts 56 45000000 45000100');
    process.exit(1);
  }

  const client = createPublicClient({
    chain: bsc,
    transport: http(getRpcUrl(chainId)),
  });

  const fromBlockBigInt = fromBlock === 'latest' ? 'latest' : BigInt(fromBlock);
  const toBlockOpt: 'latest' | bigint | undefined = !toBlock
    ? undefined
    : toBlock === 'latest'
      ? 'latest'
      : BigInt(toBlock);

  const logs = await client.getLogs({
    address: TOKEN_MANAGER2_BSC,
    events: EVENTS,
    fromBlock: fromBlockBigInt,
    ...(toBlockOpt !== undefined && { toBlock: toBlockOpt }),
  });

  const out = logs.map((log) => ({
    eventName: log.eventName,
    blockNumber: Number(log.blockNumber),
    transactionHash: log.transactionHash,
    args: log.args as object,
  }));
  console.log(JSON.stringify(out, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
