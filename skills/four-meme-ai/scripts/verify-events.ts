#!/usr/bin/env node
/**
 * Verification helper: fetch TokenManager2 events for the last N blocks on BSC.
 * Usage: npx tsx verify-events.ts [blockCount]
 * Default blockCount 50. No private key or tx, read-only.
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

function getBscRpcUrl(): string {
  return process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org';
}

async function main() {
  const blockCount = parseInt(process.argv[2] ?? '50', 10) || 50;
  const rpcUrl = getBscRpcUrl();
  const client = createPublicClient({
    chain: bsc,
    transport: http(rpcUrl),
  });
  const block = await client.getBlockNumber();
  const fromBlock = block - BigInt(blockCount);
  const toBlock = block;
  const logs = await client.getLogs({
    address: TOKEN_MANAGER2_BSC,
    events: EVENTS,
    fromBlock: fromBlock < 0n ? 0n : fromBlock,
    toBlock,
  });
  console.log(JSON.stringify({ fromBlock: String(fromBlock), toBlock: String(toBlock), count: logs.length, events: logs.map((l) => ({ eventName: l.eventName, blockNumber: Number(l.blockNumber), args: l.args })) }, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
