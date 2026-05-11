#!/usr/bin/env node
/**
 * Four.meme - execute sell on TokenManager2 (BSC only).
 * Usage: npx tsx execute-sell.ts <tokenAddress> <amountWei> [minFundsWei]
 * Env: PRIVATE_KEY. Sends approve(tokenManager, amount) then sellToken(token, amount).
 */

import { createPublicClient, createWalletClient, http } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
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

const TM2_ABI_SIMPLE = [
  {
    name: 'sellToken',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'token', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
    outputs: [],
  },
] as const;

const TM2_ABI_WITH_MIN_FUNDS = [
  {
    name: 'sellToken',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'origin', type: 'uint256' },
      { name: 'token', type: 'address' },
      { name: 'amount', type: 'uint256' },
      { name: 'minFunds', type: 'uint256' },
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
  const amountWei = BigInt(process.argv[3] ?? '0');
  const minFundsWei = process.argv[4] ? BigInt(process.argv[4]) : null;

  if (!tokenAddress || amountWei <= 0n) {
    console.error('Usage: npx tsx execute-sell.ts <tokenAddress> <amountWei> [minFundsWei]');
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

  const [, tokenManager] = await publicClient.readContract({
    address: HELPER_ADDRESS,
    abi: HELPER_ABI,
    functionName: 'getTokenInfo',
    args: [tokenAddress],
  }).then((r) => [r[0], r[1]] as const);

  const approveHash = await walletClient.writeContract({
    address: tokenAddress,
    abi: ERC20_ABI,
    functionName: 'approve',
    args: [tokenManager as `0x${string}`, amountWei],
  });
  const receipt = await publicClient.waitForTransactionReceipt({ hash: approveHash });
  if (receipt.status !== 'success') {
    console.error('Approve failed');
    process.exit(1);
  }

  const tm2 = tokenManager as `0x${string}`;
  const hash: `0x${string}` =
    minFundsWei !== null
      ? await walletClient.writeContract({
          address: tm2,
          abi: TM2_ABI_WITH_MIN_FUNDS,
          functionName: 'sellToken',
          args: [0n, tokenAddress, amountWei, minFundsWei],
        })
      : await walletClient.writeContract({
          address: tm2,
          abi: TM2_ABI_SIMPLE,
          functionName: 'sellToken',
          args: [tokenAddress, amountWei],
        });

  console.log(JSON.stringify({ txHash: hash }, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
