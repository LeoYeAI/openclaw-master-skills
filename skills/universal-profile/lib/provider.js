/**
 * Shared RPC Provider Setup
 * 
 * Multi-chain support: LUKSO, Base, and Ethereum.
 * The UP address is the same across all chains (deployed via LSP23 CREATE2).
 */

import { createPublicClient, createWalletClient, http } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { lukso, luksoTestnet, base, mainnet } from 'viem/chains';
import { ethers } from 'ethers';
import { loadCredentials } from './credentials.js';

// Network configurations: name → { chainId, rpcUrl, viemChain }
const NETWORKS = {
  mainnet:  { chainId: 42,    rpcUrl: 'https://42.rpc.thirdweb.com',         viemChain: lukso },
  testnet:  { chainId: 4201,  rpcUrl: 'https://rpc.testnet.lukso.network',   viemChain: luksoTestnet },
  base:     { chainId: 8453,  rpcUrl: 'https://mainnet.base.org',            viemChain: base },
  ethereum: { chainId: 1,     rpcUrl: 'https://eth.llamarpc.com',            viemChain: mainnet },
};

/**
 * Resolve a network identifier to its config.
 * Accepts: 'mainnet', 'testnet', 'base', 'ethereum', or a chain ID number.
 */
export function resolveNetwork(network = 'mainnet') {
  if (typeof network === 'number') {
    const entry = Object.entries(NETWORKS).find(([, v]) => v.chainId === network);
    return entry ? NETWORKS[entry[0]] : NETWORKS.mainnet;
  }
  return NETWORKS[network] || NETWORKS.mainnet;
}

/**
 * Get RPC URL for a network
 */
export function getRpcUrl(network = 'mainnet') {
  return resolveNetwork(network).rpcUrl;
}

/**
 * Get viem chain config
 */
export function getChain(network = 'mainnet') {
  return resolveNetwork(network).viemChain;
}

/**
 * Create a viem public client (read-only)
 */
export function createProvider(network = 'mainnet') {
  return createPublicClient({
    chain: getChain(network),
    transport: http(getRpcUrl(network))
  });
}

/**
 * Create a viem wallet client (for signing/sending)
 */
export function createSigner(privateKey, network = 'mainnet') {
  const account = privateKeyToAccount(privateKey);
  return {
    account,
    client: createWalletClient({
      account,
      chain: getChain(network),
      transport: http(getRpcUrl(network))
    })
  };
}

/**
 * Create an ethers provider
 */
export function createEthersProvider(network = 'mainnet') {
  return new ethers.JsonRpcProvider(getRpcUrl(network));
}

/**
 * Create an ethers wallet (provider + signer)
 */
export function createEthersWallet(privateKey, network = 'mainnet') {
  const provider = createEthersProvider(network);
  return new ethers.Wallet(privateKey, provider);
}

/**
 * Get configured provider and credentials for any supported network.
 * @param {string|number} network - 'mainnet'|'testnet'|'base'|'ethereum' or chain ID
 */
export function getProviderWithCredentials(network = 'mainnet') {
  const creds = loadCredentials();
  const resolved = resolveNetwork(network);
  const provider = createProvider(network);
  const ethersProvider = createEthersProvider(network);
  const { account, client: walletClient } = createSigner(creds.controller.privateKey, network);
  const ethersWallet = createEthersWallet(creds.controller.privateKey, network);
  
  return {
    // Credentials
    upAddress: creds.universalProfile.address,
    controllerAddress: creds.controller.address,
    privateKey: creds.controller.privateKey,
    
    // Viem clients
    publicClient: provider,
    walletClient,
    account,
    
    // Ethers clients
    ethersProvider,
    ethersWallet,
    
    // Network info
    network: typeof network === 'string' ? network : Object.entries(NETWORKS).find(([, v]) => v.chainId === network)?.[0] || 'mainnet',
    chainId: resolved.chainId,
  };
}

export { NETWORKS };
