#!/usr/bin/env node
/**
 * Transfer shares script – API (get tx then send) or direct on-chain transferShares.
 */

import { checkDependencies } from './check-dependencies.js';
checkDependencies(['ethers']);

import { ethers } from 'ethers';
import { getWallet } from './wallet.js';
import { getEnv, apiRequest, success, error, info } from './utils.js';
import { CLAW_FRIEND_ABI } from './constants/claw-friend-abi.js';

const CLAW_FRIEND_ADDRESS = '0xCe9aA37146Bd75B5312511c410d3F7FeC2E7f364';

function parseAddress(label, value) {
  try {
    return ethers.getAddress(value);
  } catch (e) {
    throw new Error(`Invalid ${label}: must be EVM address (0x + 40 hex)`);
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
  const address = CLAW_FRIEND_ADDRESS || '0xCe9aA37146Bd75B5312511c410d3F7FeC2E7f364';
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
    value,
  };
  if (txPayload.gasLimit != null && txPayload.gasLimit !== '') {
    txRequest.gasLimit = BigInt(txPayload.gasLimit);
  }
  const tx = await wallet.sendTransaction(txRequest);
  await tx.wait();
  return tx;
}

export async function getTransferFromApi(subject, toAddress, amount) {
  const walletAddress = getEnv('EVM_ADDRESS');
  if (!walletAddress) {
    error('EVM_ADDRESS is required for API transfer (wallet_address in query).');
    process.exit(1);
  }
  const params = new URLSearchParams({
    shares_subject: parseAddress('shares_subject', subject),
    to_address: parseAddress('to_address', toAddress),
    amount: String(amount),
    wallet_address: walletAddress,
  });
  const res = await apiRequest(`/v1/share/transfer?${params.toString()}`);
  return res;
}

export async function transferSharesViaApi(subject, toAddress, amount) {
  const res = await getTransferFromApi(subject, toAddress, amount);
  if (!res.transaction) {
    error('API did not return a transaction. Check wallet_address and response.');
    process.exit(1);
  }
  return execTransaction(res.transaction);
}

export async function transferSharesOnChain(subject, toAddress, amount) {
  const contract = getContractWithSigner();
  const sub = parseAddress('subject', subject);
  const to = parseAddress('to', toAddress);
  const amt = parseAmount(String(amount));
  const tx = await contract.transferShares(sub, to, amt);
  await tx.wait();
  return tx;
}

function usage() {
  console.log('ClawFriend Transfer Shares\n');
  console.log('Usage:');
  console.log('  node transfer-shares.js transfer <subject> <to_address> <amount> [--on-chain]');
  console.log('\n  subject    = EVM address of shares subject (agent)');
  console.log('  to_address = EVM address of recipient');
  console.log('  amount     = number of shares (integer >= 1)');
  console.log('  --on-chain = use contract directly; otherwise use API');
}

async function main() {
  const argv = process.argv.slice(2);
  const command = argv[0];
  const useOnChain = argv.includes('--on-chain');
  const args = argv.filter((a) => a !== '--on-chain');

  try {
    if (command === 'transfer') {
      const [subjectArg, toArg, amountArg] = args.slice(1, 4);
      if (!subjectArg || !toArg || !amountArg) {
        error('Usage: node transfer-shares.js transfer <subject> <to_address> <amount> [--on-chain]');
        process.exit(1);
      }
      parseAddress('subject', subjectArg);
      parseAddress('to_address', toArg);
      parseAmount(amountArg);
      if (useOnChain) {
        info('Transferring shares on-chain...');
        const tx = await transferSharesOnChain(subjectArg, toArg, amountArg);
        success(`Tx confirmed: ${tx.hash}`);
      } else {
        info('Getting transfer tx from API and sending...');
        const tx = await transferSharesViaApi(subjectArg, toArg, amountArg);
        success(`Tx confirmed: ${tx.hash}`);
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
