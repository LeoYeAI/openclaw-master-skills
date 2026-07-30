/**
 * LSP7 Token Module
 * 
 * Provides functions to build LSP7 (fungible token) payloads.
 * This module does NOT execute transactions - it only builds calldata.
 * Use the execute module (lib/execute/) to actually send transactions.
 * 
 * Example:
 *   import { buildLSP7TransferPayload, getLSP7Info } from './lib/tokens/lsp7.js';
 *   import { buildExecutePayload, executeRelay } from './lib/execute/index.js';
 *   
 *   // 1. Get token info
 *   const info = await getLSP7Info(tokenAddress);
 *   
 *   // 2. Build transfer calldata
 *   const data = await buildLSP7TransferPayload(tokenAddress, from, to, '100');
 *   
 *   // 3. Wrap in UP.execute() and send
 *   const payload = buildExecutePayload(0, tokenAddress, 0, data);
 *   const { txHash } = await executeRelay(payload);
 */

import { ethers } from 'ethers';
import { getProviderWithCredentials } from '../provider.js';

// LSP7 ABI (subset we need)
const LSP7_ABI = [
  'function decimals() view returns (uint8)',
  'function totalSupply() view returns (uint256)',
  'function balanceOf(address) view returns (uint256)',
  'function transfer(address from, address to, uint256 amount, bool force, bytes data) external',
  'function authorizedAmountFor(address operator, address tokenOwner) view returns (uint256)',
  // ERC725Y for metadata
  'function getData(bytes32) view returns (bytes)'
];

// LSP4 Data Keys for token metadata
const LSP4_TOKEN_NAME_KEY = '0xdeba1e292f8ba88238e10ab3c7f88bd4be4fac56cad5194b6ecceaf653468af1';
const LSP4_TOKEN_SYMBOL_KEY = '0x2f0a68ab07768e01943a599e73362a0e17a63a72e94dd2e384d2c1d4db932756';

/**
 * Decode LSP4 metadata value (string)
 */
function decodeLSP4String(data) {
  if (!data || data === '0x') return '';
  try {
    // LSP4 strings are encoded as: offset (32 bytes) + length (32 bytes) + data
    // Or just the raw string bytes
    const bytes = ethers.getBytes(data);
    if (bytes.length <= 64) {
      // Try direct UTF8 decode
      return ethers.toUtf8String(data);
    }
    // ABI decode
    return ethers.AbiCoder.defaultAbiCoder().decode(['string'], data)[0];
  } catch {
    // Fallback: just decode as UTF8
    try {
      return ethers.toUtf8String(data);
    } catch {
      return '';
    }
  }
}

/**
 * Get LSP7 token info
 * 
 * @param {string} tokenAddress - Token contract address
 * @param {Object} options - Optional overrides
 * @returns {Promise<{name, symbol, decimals, totalSupply}>}
 */
export async function getLSP7Info(tokenAddress, options = {}) {
  const network = options.network || 'mainnet';
  const { ethersProvider } = getProviderWithCredentials(network);
  
  const token = new ethers.Contract(tokenAddress, LSP7_ABI, ethersProvider);
  
  const [nameData, symbolData, decimals, totalSupply] = await Promise.all([
    token.getData(LSP4_TOKEN_NAME_KEY),
    token.getData(LSP4_TOKEN_SYMBOL_KEY),
    token.decimals(),
    token.totalSupply()
  ]);

  return {
    address: tokenAddress,
    name: decodeLSP4String(nameData) || 'Unknown Token',
    symbol: decodeLSP4String(symbolData) || '???',
    decimals: Number(decimals),
    totalSupply: ethers.formatUnits(totalSupply, decimals)
  };
}

/**
 * Get LSP7 balance for an address
 * 
 * @param {string} tokenAddress - Token contract address
 * @param {string} holderAddress - Address to check balance for
 * @param {Object} options - Optional overrides
 * @returns {Promise<{balance, formatted, decimals}>}
 */
export async function getLSP7Balance(tokenAddress, holderAddress, options = {}) {
  const network = options.network || 'mainnet';
  const { ethersProvider } = getProviderWithCredentials(network);
  
  const token = new ethers.Contract(tokenAddress, LSP7_ABI, ethersProvider);
  const decimals = await token.decimals();
  const balance = await token.balanceOf(holderAddress);

  return {
    balance: balance.toString(),
    formatted: ethers.formatUnits(balance, decimals),
    decimals: Number(decimals)
  };
}

/**
 * Build LSP7 transfer calldata
 * 
 * This returns the encoded function call data for LSP7.transfer().
 * Wrap this in UP.execute() to actually transfer tokens.
 * 
 * @param {string} tokenAddress - Token contract address
 * @param {string} from - Sender address (usually the UP)
 * @param {string} to - Recipient address
 * @param {string} amount - Human-readable amount (e.g., "100", not raw decimals)
 * @param {Object} options - Optional overrides
 * @param {boolean} options.force - Force transfer even if recipient is not a UP (default: true)
 * @param {string} options.data - Additional data to pass (default: '0x')
 * @returns {Promise<string>} Encoded transfer calldata
 */
export async function buildLSP7TransferPayload(tokenAddress, from, to, amount, options = {}) {
  const network = options.network || 'mainnet';
  const force = options.force !== undefined ? options.force : true;
  const data = options.data || '0x';
  
  const { ethersProvider } = getProviderWithCredentials(network);
  
  const token = new ethers.Contract(tokenAddress, LSP7_ABI, ethersProvider);
  const decimals = await token.decimals();
  const amountInWei = ethers.parseUnits(amount.toString(), decimals);

  return token.interface.encodeFunctionData('transfer', [
    from,
    to,
    amountInWei,
    force,
    data
  ]);
}

/**
 * Validate a transfer can be made
 * 
 * @param {string} tokenAddress - Token contract address  
 * @param {string} from - Sender address
 * @param {string} amount - Human-readable amount
 * @param {Object} options - Optional overrides
 * @returns {Promise<{valid, balance, required, error?}>}
 */
export async function validateLSP7Transfer(tokenAddress, from, amount, options = {}) {
  const network = options.network || 'mainnet';
  const { ethersProvider } = getProviderWithCredentials(network);
  
  const token = new ethers.Contract(tokenAddress, LSP7_ABI, ethersProvider);
  const decimals = await token.decimals();
  const balance = await token.balanceOf(from);
  const required = ethers.parseUnits(amount.toString(), decimals);

  if (balance < required) {
    return {
      valid: false,
      balance: ethers.formatUnits(balance, decimals),
      required: amount,
      error: `Insufficient balance. Have: ${ethers.formatUnits(balance, decimals)}, Need: ${amount}`
    };
  }

  return {
    valid: true,
    balance: ethers.formatUnits(balance, decimals),
    required: amount
  };
}

export default {
  getLSP7Info,
  getLSP7Balance,
  buildLSP7TransferPayload,
  validateLSP7Transfer
};
