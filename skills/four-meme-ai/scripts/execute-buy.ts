#!/usr/bin/env node
/**
 * Four.meme - execute buy on TokenManager2 (BSC only).
 * Usage:
 *   npx tsx execute-buy.ts <tokenAddress> amount <amountWei> <maxFundsWei>   # buy fixed token amount
 *   npx tsx execute-buy.ts <tokenAddress> funds <fundsWei> <minAmountWei>   # spend fixed quote (e.g. BNB)
 * Env: PRIVATE_KEY. Only V2 tokens (version 2 from getTokenInfo).
 */

import { createPublicClient, createWalletClient, http } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { bsc } from 'viem/chains';

const HELPER_ADDRESS = '0xF251F83e40a78868FcfA3FA4599Dad6494E46034' as const;
const ZERO = '0x0000000000000000000000000000000000000000' as const;

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

const TM2_ABI = [
  {
    name: 'buyToken',
    type: 'function',
    stateMutability: 'payable',
    inputs: [
      { name: 'token', type: 'address' },
      { name: 'amount', type: 'uint256' },
      { name: 'maxFunds', type: 'uint256' },
    ],
    outputs: [],
  },
  {
    name: 'buyTokenAMAP',
    type: 'function',
    stateMutability: 'payable',
    inputs: [
      { name: 'token', type: 'address' },
      { name: 'funds', type: 'uint256' },
      { name: 'minAmount', type: 'uint256' },
    ],
    outputs: [],
  },
] as const;

const ERC20_ABI = [
  {
    name: 'approve',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'spender', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
    outputs: [{ type: 'bool' }],
  },
] as const;

const RPC_URL = process.env.BSC_RPC_URL || 'https://bsc-dataseed.binance.org';

async function main() {
  const pk = process.env.PRIVATE_KEY;
  if (!pk) {
    console.error('Set PRIVATE_KEY');
    process.exit(1);
  }
  const account = privateKeyToAccount(
    (pk.startsWith('0x') ? pk : '0x' + pk) as `0x${string}`
  );

  const tokenAddress = process.argv[2] as `0x${string}`;
  const mode = process.argv[3]; // 'amount' | 'funds'
  const arg1 = process.argv[4];
  const arg2 = process.argv[5];

  if (!tokenAddress || !mode || !arg1 || !arg2) {
    console.error('Usage:');
    console.error('  execute-buy.ts <token> amount <amountWei> <maxFundsWei>');
    console.error('  execute-buy.ts <token> funds <fundsWei> <minAmountWei>');
    process.exit(1);
  }

  const publicClient = createPublicClient({
    chain: bsc,
    transport: http(RPC_URL),
  });
  const walletClient = createWalletClient({
    account,
    chain: bsc,
    transport: http(RPC_URL),
  });

  const [version, tokenManager, quote] = await publicClient.readContract({
    address: HELPER_ADDRESS,
    abi: HELPER_ABI,
    functionName: 'getTokenInfo',
    args: [tokenAddress],
  }).then((r) => [r[0], r[1], r[2]] as const);

  if (Number(version) !== 2) {
    console.error('Only TokenManager2 (V2) tokens are supported. This token is version', version);
    process.exit(1);
  }

  const amountWei = mode === 'amount' ? BigInt(arg1) : 0n;
  const maxFundsWei = mode === 'amount' ? BigInt(arg2) : 0n;
  const fundsWei = mode === 'funds' ? BigInt(arg1) : 0n;
  const minAmountWei = mode === 'funds' ? BigInt(arg2) : 0n;

  const tryBuyResult = await publicClient.readContract({
    address: HELPER_ADDRESS,
    abi: HELPER_ABI,
    functionName: 'tryBuy',
    args: [tokenAddress, amountWei, fundsWei],
  });
  const amountMsgValue = tryBuyResult[5];
  const amountApproval = tryBuyResult[6];

  if (quote !== ZERO && amountApproval > 0n) {
    const approveHash = await walletClient.writeContract({
      address: quote,
      abi: ERC20_ABI,
      functionName: 'approve',
      args: [tokenManager, amountApproval],
    });
    console.error('Approved quote token. Tx:', approveHash);
    const receipt = await publicClient.waitForTransactionReceipt({ hash: approveHash });
    if (receipt.status !== 'success') {
      console.error('Approve failed');
      process.exit(1);
    }
  }

  let hash: `0x${string}`;
  if (mode === 'amount') {
    hash = await walletClient.writeContract({
      address: tokenManager as `0x${string}`,
      abi: TM2_ABI,
      functionName: 'buyToken',
      args: [tokenAddress, amountWei, maxFundsWei],
      value: amountMsgValue,
    });
  } else {
    hash = await walletClient.writeContract({
      address: tokenManager as `0x${string}`,
      abi: TM2_ABI,
      functionName: 'buyTokenAMAP',
      args: [tokenAddress, fundsWei, minAmountWei],
      value: amountMsgValue,
    });
  }

  console.log(JSON.stringify({ txHash: hash }, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
