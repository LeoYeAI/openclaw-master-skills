/**
 * Direct Transaction Execution (Multi-Chain)
 * 
 * Calls UP.execute() directly — controller sends the transaction and pays gas.
 * Works on ALL chains: LUKSO, Base, Ethereum.
 * 
 * The controller calls execute() on the UP contract. The UP verifies permissions
 * via its owner (KeyManager) using LSP20 lsp20VerifyCall internally.
 * The caller does NOT need to call the KeyManager directly.
 * 
 * For gasless transactions on LUKSO, use relay.js instead (LUKSO relay API only).
 * 
 * REQUIRES:
 * - Controller must have sufficient LSP6 permissions for the action
 * - Controller must have native tokens to pay gas (LYX, ETH)
 */

import { ethers } from 'ethers';
import { getProviderWithCredentials } from '../provider.js';
import { getExplorerUrl } from '../constants.js';

// UP ABI — only the execute functions needed
const UP_ABI = [
  'function execute(uint256 operation, address target, uint256 value, bytes data) payable returns (bytes)',
  'function executeBatch(uint256[] operationTypes, address[] targets, uint256[] values, bytes[] datas) payable returns (bytes[])',
];

/**
 * Execute a payload via UP.execute() on any supported chain.
 * 
 * @param {number} operation - 0=CALL, 1=CREATE, 2=CREATE2, 3=STATICCALL, 4=DELEGATECALL
 * @param {string} target - Target contract address
 * @param {bigint|number} value - Native token value to send (LYX or ETH)
 * @param {string} data - Encoded calldata for target
 * @param {Object} options - Optional overrides
 * @param {string} options.network - 'mainnet'|'testnet'|'base'|'ethereum' (default: 'mainnet')
 * @returns {Promise<{txHash: string, explorerUrl: string}>}
 */
export async function executeDirect(operation, target, value, data, options = {}) {
  const network = options.network || 'mainnet';
  
  const { upAddress, ethersWallet, chainId } = getProviderWithCredentials(network);

  const up = new ethers.Contract(upAddress, UP_ABI, ethersWallet);
  
  const tx = await up.execute(operation, target, value, data);
  const receipt = await tx.wait();

  return {
    txHash: receipt.hash,
    explorerUrl: getExplorerUrl(receipt.hash, chainId),
  };
}

/**
 * Execute a batch of operations in a single transaction.
 * 
 * @param {Array<{operation: number, target: string, value: bigint|number, data: string}>} calls
 * @param {Object} options
 * @returns {Promise<{txHash: string, explorerUrl: string}>}
 */
export async function executeBatch(calls, options = {}) {
  const network = options.network || 'mainnet';
  
  const { upAddress, ethersWallet, chainId } = getProviderWithCredentials(network);

  const up = new ethers.Contract(upAddress, UP_ABI, ethersWallet);
  
  const tx = await up.executeBatch(
    calls.map(c => c.operation),
    calls.map(c => c.target),
    calls.map(c => c.value),
    calls.map(c => c.data),
  );
  const receipt = await tx.wait();

  return {
    txHash: receipt.hash,
    explorerUrl: getExplorerUrl(receipt.hash, chainId),
  };
}

/**
 * Build a UP.execute() payload (helper for relay.js or batch building)
 */
export function buildExecutePayload(operation, target, value, data) {
  const iface = new ethers.Interface(UP_ABI);
  return iface.encodeFunctionData('execute', [operation, target, value, data]);
}

export default { executeDirect, executeBatch, buildExecutePayload };
