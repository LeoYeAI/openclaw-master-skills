#!/usr/bin/env node
/**
 * Four.meme - get token info via TokenManagerHelper3 (BSC only).
 * Usage: npx tsx get-token-info.ts <tokenAddress>
 */

import { createPublicClient, http } from 'viem';
import { bsc } from 'viem/chains';

const HELPER_ADDRESS = '0xF251F83e40a78868FcfA3FA4599Dad6494E46034' as const;

const HELPER_ABI = [
  {
    name: 'getTokenInfo',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'token', type: 'address' }],
    outputs: [
      { name: 'version', type: 'uint256' },
      { name: 'tokenManager', type: 'address' },
      { name: 'quote', type: 'address' },
      { name: 'lastPrice', type: 'uint256' },
      { name: 'tradingFeeRate', type: 'uint256' },
      { name: 'minTradingFee', type: 'uint256' },
      { name: 'launchTime', type: 'uint256' },
      { name: 'offers', type: 'uint256' },
      { name: 'maxOffers', type: 'uint256' },
      { name: 'funds', type: 'uint256' },
      { name: 'maxFunds', type: 'uint256' },
      { name: 'liquidityAdded', type: 'bool' },
    ],
  },
] as const;

const RPC_URL = process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org';

async function main() {
  const tokenAddress = process.argv[2] as `0x${string}`;

  if (!tokenAddress) {
    console.error('Usage: npx tsx get-token-info.ts <tokenAddress>');
    console.error('BSC only.');
    process.exit(1);
  }

  const client = createPublicClient({
    chain: bsc,
    transport: http(RPC_URL),
  });

  const helperAddress = HELPER_ADDRESS;
  const result = await client.readContract({
    address: helperAddress,
    abi: HELPER_ABI,
    functionName: 'getTokenInfo',
    args: [tokenAddress],
  });

  const [
    version,
    tokenManager,
    quote,
    lastPrice,
    tradingFeeRate,
    minTradingFee,
    launchTime,
    offers,
    maxOffers,
    funds,
    maxFunds,
    liquidityAdded,
  ] = result;

  const out = {
    version: Number(version),
    tokenManager,
    quote: quote === '0x0000000000000000000000000000000000000000' ? null : quote,
    lastPrice: lastPrice.toString(),
    tradingFeeRate: Number(tradingFeeRate) / 10000,
    minTradingFee: minTradingFee.toString(),
    launchTime: Number(launchTime),
    offers: offers.toString(),
    maxOffers: maxOffers.toString(),
    funds: funds.toString(),
    maxFunds: maxFunds.toString(),
    liquidityAdded,
  };
  console.log(JSON.stringify(out, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
