/**
 * Relay Execution (LSP25) — LUKSO ONLY
 * 
 * Gasless execution via LUKSO's transaction relay service API.
 * NOT available on Base, Ethereum, or other chains.
 * 
 * The controller signs the payload, and the relay service submits the
 * transaction on-chain. Gas is paid from the UP's relay quota.
 * 
 * For non-LUKSO chains, use direct.js (controller pays gas).
 * 
 * REQUIRES:
 * - EXECUTE_RELAY_CALL permission (0x400000)
 * - SIGN permission (0x200000) - for ERC-1271 verification by relayer
 * - Relay quota (check via LUKSO relay API)
 */

import { ethers } from 'ethers';
import { getProviderWithCredentials } from '../provider.js';
import { getExplorerUrl } from '../constants.js';

// LSP25 version constant
const LSP25_VERSION = 25n;

// Relayer endpoints
const RELAYER_URLS = {
  mainnet: 'https://relayer.mainnet.lukso.network/api',
  testnet: 'https://relayer.testnet.lukso.network/api'
};

// ABIs needed for relay execution
const UP_ABI = ['function owner() view returns (address)'];
const KM_ABI = ['function getNonce(address, uint128) view returns (uint256)'];

/**
 * Execute a payload via relay (gasless)
 * 
 * @param {string} payload - The encoded UP.execute() calldata
 * @param {Object} options - Optional overrides
 * @param {string} options.network - 'mainnet' or 'testnet'
 * @param {number} options.value - LYX value to send (default: 0)
 * @returns {Promise<{txHash: string, explorerUrl: string}>}
 */
export async function executeRelay(payload, options = {}) {
  const network = options.network || 'mainnet';
  const value = options.value || 0;
  
  const {
    upAddress,
    controllerAddress,
    privateKey,
    ethersProvider,
    chainId
  } = getProviderWithCredentials(network);

  // Get Key Manager address
  const up = new ethers.Contract(upAddress, UP_ABI, ethersProvider);
  const kmAddress = await up.owner();
  const km = new ethers.Contract(kmAddress, KM_ABI, ethersProvider);

  // Get nonce for our controller
  const nonce = await km.getNonce(controllerAddress, 0);

  // Build LSP25 message
  // Format: version || chainId || nonce || validityTimestamps || value || payload
  const encodedMessage = ethers.solidityPacked(
    ['uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'bytes'],
    [LSP25_VERSION, chainId, nonce, 0n, BigInt(value), payload]
  );

  // EIP-191 v0 hash with Key Manager as intended validator
  const hash = ethers.keccak256(
    ethers.concat(['0x19', '0x00', kmAddress, encodedMessage])
  );

  // Sign
  const sig = new ethers.SigningKey(privateKey).sign(hash);
  const signature = ethers.Signature.from(sig).serialized;

  // Verify signature locally
  const recovered = ethers.recoverAddress(hash, signature);
  if (recovered.toLowerCase() !== controllerAddress.toLowerCase()) {
    throw new Error(`Signature verification failed! Recovered: ${recovered}, Expected: ${controllerAddress}`);
  }

  // Build relay request
  const relayRequest = {
    address: upAddress,
    transaction: {
      abi: payload,
      signature,
      nonce: nonce.toString(),
      validityTimestamps: '0x0'
    }
  };

  // Send to relayer
  const relayerUrl = RELAYER_URLS[network] || RELAYER_URLS.mainnet;
  const response = await fetch(`${relayerUrl}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(relayRequest)
  });

  const result = await response.json();

  if (!response.ok || !result.transactionHash) {
    if (response.status === 401) {
      throw new Error(
        'Relay API returned 401 Unauthorized. ' +
        'The SIGN permission (0x200000) is required for gasless relay transactions. ' +
        'Use direct execution instead, or add SIGN permission to your controller.'
      );
    }
    throw new Error(`Relay failed: ${response.status} - ${JSON.stringify(result)}`);
  }

  const explorerChainId = network === 'testnet' ? 4201 : 42;
  return {
    txHash: result.transactionHash,
    explorerUrl: getExplorerUrl(result.transactionHash, explorerChainId)
  };
}

/**
 * Check relay quota for a UP (requires signed request)
 * 
 * @param {Object} options - Optional overrides
 * @param {string} options.network - 'mainnet' or 'testnet'
 * @returns {Promise<{quota: number, unit: string, totalQuota: number, resetDate: number}>}
 */
export async function getRelayQuota(options = {}) {
  const network = options.network || 'mainnet';
  const relayerUrl = RELAYER_URLS[network] || RELAYER_URLS.mainnet;

  // Load credentials
  const { loadAndValidateCredentials } = await import('../credentials.js');
  const creds = loadAndValidateCredentials();
  
  const upAddress = creds.universalProfile.address;
  const privateKey = creds.controller.privateKey;
  
  const timestamp = Math.floor(Date.now() / 1000);
  const wallet = new ethers.Wallet(privateKey);
  
  const messageHash = ethers.solidityPackedKeccak256(
    ['address', 'uint256'],
    [upAddress, timestamp]
  );
  const signature = await wallet.signMessage(ethers.getBytes(messageHash));

  const response = await fetch(`${relayerUrl}/quota`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address: upAddress, timestamp, signature })
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Failed to get quota: ${response.status} - ${body}`);
  }

  return response.json();
}

export default { executeRelay, getRelayQuota };
