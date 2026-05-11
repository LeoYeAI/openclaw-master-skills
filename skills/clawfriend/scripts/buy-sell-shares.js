#!/usr/bin/env node
/**
 * Buy/sell shares script – two modes: on-chain (contract + ABI) or API quote then send tx.
 */

import { checkDependencies } from './check-dependencies.js';
checkDependencies(['ethers']);

import { ethers } from 'ethers';
import { getWallet } from './wallet.js';
import {
  getEnv,
  apiRequest,
  success,
  error,
  warning,
  info
} from './utils.js';
import { CLAW_FRIEND_ABI } from './constants/claw-friend-abi.js';
const CLAW_FRIEND_ADDRESS = `0xCe9aA37146Bd75B5312511c410d3F7FeC2E7f364`

function parseSubject(subject) {
  try {
    return ethers.getAddress(subject);
  } catch (e) {
    throw new Error('Invalid subject: must be EVM address (0x + 40 hex)');
  }
}

function parseAmount(arg) {
  const n = parseInt(arg, 10);
  if (!Number.isInteger(n) || n < 1) {
    throw new Error('Amount must be an integer >= 1');
  }
  return BigInt(n);
}

function getContractWithSigner() {
  const rpc = getEnv('EVM_RPC_URL');
  const address = CLAW_FRIEND_ADDRESS || `0xCe9aA37146Bd75B5312511c410d3F7FeC2E7f364`
  if (!rpc) {
    error('EVM_RPC_URL is required for on-chain mode.');
    process.exit(1);
  }
  if (!address) {
    error('CLAW_FRIEND_ADDRESS is required for on-chain mode.');
    process.exit(1);
  }
  const provider = new ethers.JsonRpcProvider(rpc);
  const wallet = getWallet().connect(provider);
  return new ethers.Contract(address, CLAW_FRIEND_ABI, wallet);
}

export async function getQuoteOnChain(side, subject, amount) {
  const contract = getContractWithSigner();
  const sub = parseSubject(subject);
  const amt = parseAmount(String(amount));
  const supply = await contract.sharesSupply(sub);
  const priceAfterFee =
    side === 'buy'
      ? await contract.getBuyPriceAfterFee(sub, amt)
      : await contract.getSellPriceAfterFee(sub, amt);
  return { supply, priceAfterFee, side, subject: sub, amount: amt };
}

export async function buySharesOnChain(subject, amount) {
  const contract = getContractWithSigner();
  const sub = parseSubject(subject);
  const amt = parseAmount(String(amount));
  const cost = await contract.getBuyPriceAfterFee(sub, amt);
  const tx = await contract.buyShares(sub, amt, { value: cost });
  await tx.wait();
  return tx;
}

export async function sellSharesOnChain(subject, amount) {
  const contract = getContractWithSigner();
  const sub = parseSubject(subject);
  const amt = parseAmount(String(amount));
  const tx = await contract.sellShares(sub, amt);
  await tx.wait();
  return tx;
}

async function execTransaction(txPayload) {
  const rpc = getEnv('EVM_RPC_URL');
  if (!rpc) {
    error('EVM_RPC_URL is required.');
    process.exit(1);
  }
  const provider = new ethers.JsonRpcProvider(rpc);
  const wallet = getWallet().connect(provider);
  const value =
    txPayload.value !== undefined && txPayload.value !== null
      ? typeof txPayload.value === 'string' && txPayload.value.startsWith('0x')
        ? BigInt(txPayload.value)
        : BigInt(txPayload.value)
      : 0n;
  const txRequest = {
    to: ethers.getAddress(txPayload.to),
    data: txPayload.data || '0x',
    value
  };
  if (txPayload.gasLimit != null && txPayload.gasLimit !== '') {
    txRequest.gasLimit = BigInt(txPayload.gasLimit);
  }
  const tx = await wallet.sendTransaction(txRequest);
  await tx.wait();
  return tx;
}

export async function getQuoteFromApi(side, subject, amount) {
  const baseUrl = getEnv('API_DOMAIN', 'https://api.clawfriend.ai');
  const walletAddress = getEnv('EVM_ADDRESS');
  if (!walletAddress) {
    error('EVM_ADDRESS is required for API quote (wallet_address in query).');
    process.exit(1);
  }
  const params = new URLSearchParams({
    side,
    shares_subject: parseSubject(subject),
    amount: String(amount),
    wallet_address: walletAddress
  });
  const quote = await apiRequest(`/v1/share/quote?${params.toString()}`);
  return quote;
}

export async function buySharesViaApi(subject, amount) {
  const quote = await getQuoteFromApi('buy', subject, amount);
  if (!quote.transaction) {
    error('API did not return a transaction. Check wallet_address and response.');
    process.exit(1);
  }
  return execTransaction(quote.transaction);
}

export async function sellSharesViaApi(subject, amount) {
  const quote = await getQuoteFromApi('sell', subject, amount);
  if (!quote.transaction) {
    error('API did not return a transaction. Check wallet_address and response.');
    process.exit(1);
  }
  return execTransaction(quote.transaction);
}

function usage() {
  console.log('ClawFriend Buy/Sell Shares\n');
  console.log('Usage:');
  console.log('  node buy-sell-shares.js buy <subject> <amount> [--on-chain]');
  console.log('  node buy-sell-shares.js sell <subject> <amount> [--on-chain]');
  console.log('  node buy-sell-shares.js quote <side> <subject> <amount> [--on-chain]');
  console.log('\n  subject = EVM address of shares subject (agent)');
  console.log('  amount  = number of shares (integer >= 1)');
  console.log('  --on-chain = use contract directly; otherwise use API quote');
}

async function main() {
  const argv = process.argv.slice(2);
  const command = argv[0];
  const useOnChain = argv.includes('--on-chain');
  const args = argv.filter((a) => a !== '--on-chain');

  try {
    if (command === 'buy') {
      const [subjectArg, amountArg] = args.slice(1, 3);
      if (!subjectArg || !amountArg) {
        error('Usage: node buy-sell-shares.js buy <subject> <amount> [--on-chain]');
        process.exit(1);
      }
      parseSubject(subjectArg);
      parseAmount(amountArg);
      if (useOnChain) {
        info('Buying shares on-chain...');
        const tx = await buySharesOnChain(subjectArg, amountArg);
        success(`Tx confirmed: ${tx.hash}`);
      } else {
        info('Getting quote from API and sending tx...');
        const tx = await buySharesViaApi(subjectArg, amountArg);
        success(`Tx confirmed: ${tx.hash}`);
      }
      return;
    }

    if (command === 'sell') {
      const [subjectArg, amountArg] = args.slice(1, 3);
      if (!subjectArg || !amountArg) {
        error('Usage: node buy-sell-shares.js sell <subject> <amount> [--on-chain]');
        process.exit(1);
      }
      parseSubject(subjectArg);
      parseAmount(amountArg);
      if (useOnChain) {
        info('Selling shares on-chain...');
        const tx = await sellSharesOnChain(subjectArg, amountArg);
        success(`Tx confirmed: ${tx.hash}`);
      } else {
        info('Getting quote from API and sending tx...');
        const tx = await sellSharesViaApi(subjectArg, amountArg);
        success(`Tx confirmed: ${tx.hash}`);
      }
      return;
    }

    if (command === 'quote') {
      const [sideArg, subjectArg, amountArg] = args.slice(1, 4);
      if (!sideArg || !subjectArg || !amountArg) {
        error('Usage: node buy-sell-shares.js quote <side> <subject> <amount> [--on-chain]');
        process.exit(1);
      }
      const side = sideArg.toLowerCase();
      if (side !== 'buy' && side !== 'sell') {
        error('side must be buy or sell');
        process.exit(1);
      }
      parseSubject(subjectArg);
      parseAmount(amountArg);
      if (useOnChain) {
        const q = await getQuoteOnChain(side, subjectArg, amountArg);
        info(`Supply: ${q.supply.toString()}`);
        info(`Price after fee (${side}): ${q.priceAfterFee.toString()} wei`);
        success('Quote (on-chain)');
      } else {
        const quote = await getQuoteFromApi(side, subjectArg, amountArg);
        console.log(JSON.stringify(quote, null, 2));
        success('Quote (API)');
      }
      return;
    }

    usage();
  } catch (e) {
    error(e.message);
    process.exit(1);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
