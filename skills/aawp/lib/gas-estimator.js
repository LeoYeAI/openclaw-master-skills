'use strict';

const { ethers } = require('ethers');

// Legacy chains that don't support EIP-1559
const LEGACY_CHAINS = ['bsc'];

/**
 * Get dynamic gas price for a chain.
 * EIP-1559 chains: maxFeePerGas = baseFee * 1.5 + maxPriorityFeePerGas
 * Legacy chains (BSC): gasPrice * 1.1
 * @returns {{ maxFeePerGas, maxPriorityFeePerGas } | { gasPrice }}
 */
async function getGasPrice(provider, chainKey) {
  const feeData = await provider.getFeeData();

  if (LEGACY_CHAINS.includes(chainKey) || !feeData.maxFeePerGas) {
    // Legacy pricing
    const base = feeData.gasPrice || 3000000000n;
    const gasPrice = (base * 110n) / 100n; // +10%
    return { gasPrice };
  }

  // EIP-1559
  const baseFee = feeData.maxFeePerGas - (feeData.maxPriorityFeePerGas || 0n);
  const maxPriorityFeePerGas = feeData.maxPriorityFeePerGas || ethers.parseUnits('1', 'gwei');
  const maxFeePerGas = (baseFee * 150n) / 100n + maxPriorityFeePerGas;

  return { maxFeePerGas, maxPriorityFeePerGas };
}

/**
 * Estimate gas cost in native currency (ETH/BNB/MATIC).
 * @param {object} provider
 * @param {object} txParams - { to, value, data }
 * @param {string} chainKey
 * @returns {{ gasLimit: bigint, gasCostWei: bigint, gasCostEth: string }}
 */
async function estimateGasCost(provider, txParams, chainKey) {
  const gasLimit = await provider.estimateGas(txParams).catch(() => 200000n);
  const prices = await getGasPrice(provider, chainKey);
  const effectivePrice = prices.gasPrice || prices.maxFeePerGas;
  const gasCostWei = BigInt(gasLimit) * effectivePrice;

  return {
    gasLimit,
    gasCostWei,
    gasCostEth: ethers.formatEther(gasCostWei),
  };
}

module.exports = { getGasPrice, estimateGasCost };
