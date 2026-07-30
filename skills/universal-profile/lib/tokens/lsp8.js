/**
 * LSP8 Token Module
 * 
 * Provides functions to build LSP8 (identifiable digital asset / NFT) payloads.
 * This module does NOT execute transactions - it only builds calldata.
 * Use the execute module (lib/execute/) to actually send transactions.
 * 
 * TODO: Implement LSP8 functions
 */

import { ethers } from 'ethers';
import { getProviderWithCredentials } from '../provider.js';

// LSP8 ABI (subset we need)
const LSP8_ABI = [
  'function name() view returns (string)',
  'function symbol() view returns (string)',
  'function totalSupply() view returns (uint256)',
  'function balanceOf(address) view returns (uint256)',
  'function tokenOwnerOf(bytes32 tokenId) view returns (address)',
  'function tokenIdsOf(address owner) view returns (bytes32[])',
  'function transfer(address from, address to, bytes32 tokenId, bool force, bytes data) external'
];

/**
 * Get LSP8 token info
 * 
 * @param {string} tokenAddress - Token contract address
 * @param {Object} options - Optional overrides
 * @returns {Promise<{name, symbol, totalSupply}>}
 */
export async function getLSP8Info(tokenAddress, options = {}) {
  const network = options.network || 'mainnet';
  const { ethersProvider } = getProviderWithCredentials(network);
  
  const token = new ethers.Contract(tokenAddress, LSP8_ABI, ethersProvider);
  
  const [name, symbol, totalSupply] = await Promise.all([
    token.name(),
    token.symbol(),
    token.totalSupply()
  ]);

  return {
    address: tokenAddress,
    name,
    symbol,
    totalSupply: totalSupply.toString()
  };
}

/**
 * Get LSP8 tokens owned by an address
 * 
 * @param {string} tokenAddress - Token contract address
 * @param {string} ownerAddress - Address to check
 * @param {Object} options - Optional overrides
 * @returns {Promise<{balance, tokenIds}>}
 */
export async function getLSP8TokensOf(tokenAddress, ownerAddress, options = {}) {
  const network = options.network || 'mainnet';
  const { ethersProvider } = getProviderWithCredentials(network);
  
  const token = new ethers.Contract(tokenAddress, LSP8_ABI, ethersProvider);
  const [balance, tokenIds] = await Promise.all([
    token.balanceOf(ownerAddress),
    token.tokenIdsOf(ownerAddress)
  ]);

  return {
    balance: Number(balance),
    tokenIds: tokenIds.map(id => id.toString())
  };
}

/**
 * Build LSP8 transfer calldata
 * 
 * @param {string} tokenAddress - Token contract address
 * @param {string} from - Sender address
 * @param {string} to - Recipient address
 * @param {string} tokenId - Token ID (bytes32)
 * @param {Object} options - Optional overrides
 * @returns {string} Encoded transfer calldata
 */
export function buildLSP8TransferPayload(tokenAddress, from, to, tokenId, options = {}) {
  const force = options.force !== undefined ? options.force : true;
  const data = options.data || '0x';
  
  const iface = new ethers.Interface(LSP8_ABI);
  return iface.encodeFunctionData('transfer', [
    from,
    to,
    tokenId,
    force,
    data
  ]);
}

export default {
  getLSP8Info,
  getLSP8TokensOf,
  buildLSP8TransferPayload
};
