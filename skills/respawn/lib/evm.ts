import { ethers } from 'ethers'
import { getNetworkDomainRpcUrls } from '@autonomys/auto-utils'
import type { NetworkId } from './network.js'

/** Auto-EVM domain ID on Autonomys */
export const AUTO_EVM_DOMAIN_ID = 0

/**
 * Default MemoryChain contract addresses per network.
 * Override with AUTO_RESPAWN_CONTRACT_ADDRESS env var if your deployment differs.
 */
const MEMORY_CHAIN_ADDRESSES: Record<NetworkId, string> = {
  mainnet: '0x51DAedAFfFf631820a4650a773096A69cB199A3c',
  chronos: '0x5fa47C8F3B519deF692BD9C87179d69a6f4EBf11',
}

export function getMemoryChainAddress(network: NetworkId): string {
  return process.env.AUTO_RESPAWN_CONTRACT_ADDRESS || MEMORY_CHAIN_ADDRESSES[network]
}

/**
 * MemoryChain contract ABI — matches the OpenClaw MemoryChain contract.
 * Source: https://github.com/autojeremy/openclaw-memory-chain
 *
 * The contract stores CID strings directly (no hashing).
 * updateHead(string cid) writes, getHead(address) reads.
 */
export const MEMORY_CHAIN_ABI = [
  {
    inputs: [{ internalType: 'string', name: 'cid', type: 'string' }],
    name: 'updateHead',
    outputs: [],
    stateMutability: 'nonpayable',
    type: 'function',
  },
  {
    inputs: [{ internalType: 'address', name: 'agent', type: 'address' }],
    name: 'getHead',
    outputs: [{ internalType: 'string', name: '', type: 'string' }],
    stateMutability: 'view',
    type: 'function',
  },
  {
    anonymous: false,
    inputs: [
      { indexed: true, internalType: 'address', name: 'agent', type: 'address' },
      { indexed: false, internalType: 'string', name: 'cid', type: 'string' },
      { indexed: false, internalType: 'uint256', name: 'timestamp', type: 'uint256' },
    ],
    name: 'HeadUpdated',
    type: 'event',
  },
] as const

/**
 * Get the Auto-EVM WebSocket RPC URL for a given network.
 */
export function getEvmRpcUrl(network: NetworkId): string {
  const urls = getNetworkDomainRpcUrls({ networkId: network, domainId: String(AUTO_EVM_DOMAIN_ID) })
  if (!urls || urls.length === 0) {
    throw new Error(`No Auto-EVM RPC URL found for network "${network}"`)
  }
  return urls[0]
}

/**
 * Connect to Auto-EVM and return an ethers provider.
 */
export function connectEvmProvider(network: NetworkId): ethers.WebSocketProvider {
  const url = getEvmRpcUrl(network)
  return new ethers.WebSocketProvider(url)
}

/**
 * Derive an EVM private key + address from a BIP39 mnemonic.
 * Uses standard BIP44 derivation path m/44'/60'/0'/0/0 (MetaMask-compatible).
 */
export function deriveEvmKey(mnemonic: string): { privateKey: string; address: string } {
  const mnemonicObj = ethers.Mnemonic.fromPhrase(mnemonic)
  const hdWallet = ethers.HDNodeWallet.fromMnemonic(mnemonicObj, "m/44'/60'/0'/0/0")
  return {
    privateKey: hdWallet.privateKey,
    address: hdWallet.address,
  }
}

/**
 * Create an ethers Wallet (signer) from an EVM private key + provider.
 */
export function createEvmSigner(privateKey: string, provider: ethers.Provider): ethers.Wallet {
  return new ethers.Wallet(privateKey, provider)
}

/**
 * Get a MemoryChain contract instance.
 * Pass a signer for write operations (anchor), or a provider for read-only (gethead).
 */
export function getMemoryChainContract(
  signerOrProvider: ethers.Wallet | ethers.Provider,
  network: NetworkId,
): ethers.Contract {
  const address = getMemoryChainAddress(network)
  return new ethers.Contract(address, MEMORY_CHAIN_ABI, signerOrProvider)
}
