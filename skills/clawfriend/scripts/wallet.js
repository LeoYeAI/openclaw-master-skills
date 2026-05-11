#!/usr/bin/env node
/**
 * Wallet management for ClawFriend
 * Handles wallet generation, storage, and message signing
 */

// Check dependencies first
import { checkDependencies } from './check-dependencies.js';
checkDependencies(['ethers']);

import { ethers } from 'ethers';
import {
  getClawFriendConfig,
  updateClawFriendConfig,
  getEnv,
  success,
  error,
  warning,
  info
} from './utils.js';

/**
 * Check if wallet exists in config
 */
export function hasWallet() {
  const privateKey = getEnv('EVM_PRIVATE_KEY');
  const address = getEnv('EVM_ADDRESS');
  return !!(privateKey && address);
}

/**
 * Get wallet from config
 */
export function getWallet() {
  const privateKey = getEnv('EVM_PRIVATE_KEY');
  if (!privateKey) {
    throw new Error('No private key found in config. Run: node wallet.js generate');
  }
  return new ethers.Wallet(privateKey);
}

/**
 * Generate new wallet
 */
export function generateWallet() {
  const wallet = ethers.Wallet.createRandom();
  
  // Store in config
  updateClawFriendConfig({
    env: {
      EVM_PRIVATE_KEY: wallet.privateKey,
      EVM_ADDRESS: wallet.address
    }
  });
  
  return {
    address: wallet.address,
    privateKey: wallet.privateKey
  };
}

/**
 * Sign registration message
 */
export async function signRegistrationMessage(name) {
  const wallet = getWallet();
  const message = `Register my agent on ClawFriend: ${name.trim()}`;
  const signature = await wallet.signMessage(message);

  return {
    message,
    signature,
    address: wallet.address
  };
}

/**
 * CLI Commands
 */
async function main() {
  const command = process.argv[2];
  
  try {
    switch (command) {
      case 'check': {
        if (hasWallet()) {
          const address = getEnv('EVM_ADDRESS');
          success(`Wallet found: ${address}`);
          info('Network: BNB (Chain ID: 56)');
        } else {
          warning('No wallet found in config');
          info('Run: node wallet.js generate');
        }
        break;
      }
      
      case 'generate': {
        if (hasWallet()) {
          const address = getEnv('EVM_ADDRESS');
          warning(`Wallet already exists: ${address}`);
          warning('To generate a new wallet, first remove EVM_PRIVATE_KEY from config');
          process.exit(1);
        }
        
        const wallet = generateWallet();
        success('EVM Wallet Created Successfully!');
        info(`Network: BNB (Chain ID: 56)`);
        info(`Address: ${wallet.address}`);
        warning('The private key has been stored securely in your OpenClaw config.');
        warning('You may need to fund this wallet with BNB on BNB network for future transactions.');
        break;
      }
      
      case 'sign': {
        const name = process.argv[3];
        if (!name) {
          error('Usage: node wallet.js sign <agent-name>');
          process.exit(1);
        }
        
        const result = await signRegistrationMessage(name);
        success('Message signed successfully!');
        console.log('\nMessage:', result.message);
        console.log('Signature:', result.signature);
        console.log('Address:', result.address);
        break;
      }
      
      case 'address': {
        const address = getEnv('EVM_ADDRESS');
        if (address) {
          console.log(address);
        } else {
          error('No wallet found');
          process.exit(1);
        }
        break;
      }

      case 'balance': {
        const rpcUrl = getEnv('EVM_RPC_URL', 'https://bsc-dataseed.binance.org');
        const address = getEnv('EVM_ADDRESS');
        if (!address) {
          error('Set EVM_ADDRESS in config to check balance on-chain.');
          process.exit(1);
        }
        const provider = new ethers.JsonRpcProvider(rpcUrl || 'https://bsc-dataseed.binance.org');
        const balanceWei = await provider.getBalance(address);
        const balanceBnb = ethers.formatEther(balanceWei);
        success(`Balance: ${balanceBnb} BNB`);
        info(`Address: ${address}`);
        info('Network: BNB (Chain ID: 56) - balance from RPC on-chain');
        break;
      }
      
      default: {
        console.log('ClawFriend Wallet Manager\n');
        console.log('Usage:');
        console.log('  node wallet.js check              - Check if wallet exists');
        console.log('  node wallet.js generate           - Generate new wallet');
        console.log('  node wallet.js sign <name>        - Sign registration message');
        console.log('  node wallet.js address            - Display wallet address');
        console.log('  node wallet.js balance            - Get BNB balance on-chain (RPC)');
        break;
      }
    }
  } catch (e) {
    error(e.message);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
