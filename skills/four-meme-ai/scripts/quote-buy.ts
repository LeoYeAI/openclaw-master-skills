#!/usr/bin/env node
/**
 * Four.meme - buy quote via TokenManagerHelper3.tryBuy (BSC only).
 * Usage: npx tsx quote-buy.ts <tokenAddress> <amountWei> [fundsWei]
 */

import { createPublicClient, http } from 'viem';
import { bsc } from 'viem/chains';

const HELPER_ADDRESS = '0xF251F83e40a78868FcfA3FA4599Dad6494E46034' as const;

const HELPER_ABI = [
  {
    name: 'tryBuy',
    type: 'function',
    stateMutability: 'view',
    inputs: [
      { name: 'token', type: 'address' },
      { name: 'amount', type: 'uint256' },
      { name: 'funds', type: 'uint256' },
    ],
    outputs: [
      { name: 'tokenManager', type: 'address' },
      { name: 'quote', type: 'address' },
      { name: 'estimatedAmount', type: 'uint256' },
      { name: 'estimatedCost', type: 'uint256' },
      { name: 'estimatedFee', type: 'uint256' },
      { name: 'amountMsgValue', type: 'uint256' },
      { name: 'amountApproval', type: 'uint256' },
      { name: 'amountFunds', type: 'uint256' },
    ],
  },
] as const;

const RPC_URL = process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org';

async function main() {
  const tokenAddress = process.argv[2] as `0x${string}`;
  const amountWei = BigInt(process.argv[3] ?? '0');
  const fundsWei = BigInt(process.argv[4] ?? '0');

  if (!tokenAddress) {
    console.error('Usage: npx tsx quote-buy.ts <tokenAddress> <amountWei> [fundsWei]');
    console.error('BSC only. amountWei: token amount (0 for funds-based); fundsWei: quote to spend (0 for amount-based)');
    process.exit(1);
  }

  const client = createPublicClient({
    chain: bsc,
    transport: http(RPC_URL),
  });

  const [
    tokenManager,
    quote,
    estimatedAmount,
    estimatedCost,
    estimatedFee,
    amountMsgValue,
    amountApproval,
    amountFunds,
  ] = await client.readContract({
    address: HELPER_ADDRESS,
    abi: HELPER_ABI,
    functionName: 'tryBuy',
    args: [tokenAddress, amountWei, fundsWei],
  });

  const out = {
    tokenManager,
    quote: quote === '0x0000000000000000000000000000000000000000' ? 'native' : quote,
    estimatedAmount: estimatedAmount.toString(),
    estimatedCost: estimatedCost.toString(),
    estimatedFee: estimatedFee.toString(),
    amountMsgValue: amountMsgValue.toString(),
    amountApproval: amountApproval.toString(),
    amountFunds: amountFunds.toString(),
  };
  console.log(JSON.stringify(out, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
