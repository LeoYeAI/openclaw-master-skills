#!/usr/bin/env node
/**
 * Four.meme - query TaxToken contract for fee/tax config (BSC only).
 * Only works for TaxToken type (creatorType 5). Usage: npx tsx get-tax-token-info.ts <tokenAddress>
 */

import { createPublicClient, http } from 'viem';
import { bsc } from 'viem/chains';

const TAX_TOKEN_ABI = [
  { name: 'feeRate', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'uint256' }] },
  { name: 'rateFounder', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'uint256' }] },
  { name: 'rateHolder', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'uint256' }] },
  { name: 'rateBurn', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'uint256' }] },
  { name: 'rateLiquidity', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'uint256' }] },
  { name: 'minDispatch', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'uint256' }] },
  { name: 'minShare', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'uint256' }] },
  { name: 'quote', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'address' }] },
  { name: 'founder', type: 'function', stateMutability: 'view', inputs: [], outputs: [{ type: 'address' }] },
] as const;

const RPC_URL = process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org';

async function main() {
  const tokenAddress = process.argv[2] as `0x${string}`;

  if (!tokenAddress) {
    console.error('Usage: npx tsx get-tax-token-info.ts <tokenAddress>');
    console.error('BSC only. Token must be TaxToken type.');
    process.exit(1);
  }

  const client = createPublicClient({
    chain: bsc,
    transport: http(RPC_URL),
  });

  const [feeRate, rateFounder, rateHolder, rateBurn, rateLiquidity, minDispatch, minShare, quote, founder] =
    await Promise.all([
      client.readContract({ address: tokenAddress, abi: TAX_TOKEN_ABI, functionName: 'feeRate' }),
      client.readContract({ address: tokenAddress, abi: TAX_TOKEN_ABI, functionName: 'rateFounder' }),
      client.readContract({ address: tokenAddress, abi: TAX_TOKEN_ABI, functionName: 'rateHolder' }),
      client.readContract({ address: tokenAddress, abi: TAX_TOKEN_ABI, functionName: 'rateBurn' }),
      client.readContract({ address: tokenAddress, abi: TAX_TOKEN_ABI, functionName: 'rateLiquidity' }),
      client.readContract({ address: tokenAddress, abi: TAX_TOKEN_ABI, functionName: 'minDispatch' }),
      client.readContract({ address: tokenAddress, abi: TAX_TOKEN_ABI, functionName: 'minShare' }),
      client.readContract({ address: tokenAddress, abi: TAX_TOKEN_ABI, functionName: 'quote' }),
      client.readContract({ address: tokenAddress, abi: TAX_TOKEN_ABI, functionName: 'founder' }),
    ]);

  const out = {
    feeRateBps: Number(feeRate),
    feeRatePercent: Number(feeRate) / 100,
    rateFounder: Number(rateFounder),
    rateHolder: Number(rateHolder),
    rateBurn: Number(rateBurn),
    rateLiquidity: Number(rateLiquidity),
    minDispatch: minDispatch.toString(),
    minShare: minShare.toString(),
    quote: quote === '0x0000000000000000000000000000000000000000' ? null : quote,
    founder: founder === '0x0000000000000000000000000000000000000000' ? null : founder,
  };
  console.log(JSON.stringify(out, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
