'use strict';

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Multicall3 is deployed at the same address on all EVM chains
const MULTICALL3_ADDR = '0xcA11bde05977b3631167028862bE2a173976CA11';

const MULTICALL3_ABI = [
  'function aggregate3((address target, bool allowFailure, bytes callData)[] calls) payable returns ((bool success, bytes returnData)[])',
];

/**
 * Batch multiple calls into a single wallet execute() via Multicall3.aggregate3.
 * @param {Array} calls - [{ to, value, data, description }]
 * @param {string} walletAddr - AAWP wallet address
 * @param {object} chain - chain config from CHAINS
 * @param {Function} socketQuery - the socketQuery function for signing
 * @param {Function} getNonce - async function returning next nonce
 * @returns {string} txHash
 */
async function batchExecute(calls, walletAddr, chain, socketQuery, getNonce) {
  if (!calls || calls.length === 0) throw new Error('No calls to batch');

  // If only one call has value > 0, we need to sum total value
  const totalValue = calls.reduce((sum, c) => sum + BigInt(c.value || '0'), 0n);

  // Encode Multicall3.aggregate3
  const iface = new ethers.Interface(MULTICALL3_ABI);
  const multicallArgs = calls.map(c => ({
    target: c.to,
    allowFailure: false,
    callData: c.data || '0x',
  }));
  const data = iface.encodeFunctionData('aggregate3', [multicallArgs]);

  const nonce = await getNonce();
  const deadline = Math.floor(Date.now() / 1000) + 3600;

  console.log(`\n📦 Batch executing ${calls.length} calls via Multicall3`);
  for (let i = 0; i < calls.length; i++) {
    console.log(`  ${i + 1}. ${calls[i].description || calls[i].to} (value: ${calls[i].value || '0'})`);
  }

  // Inject guardian private key as gas_key (same logic as sign-worker.js)
  let gasKey;
  try {
    const gPath = path.join(process.env.AAWP_SKILL || '/root/clawd/skills/aawp', 'config/guardian.json');
    const g = JSON.parse(fs.readFileSync(gPath, 'utf8'));
    if (g.privateKey) gasKey = g.privateKey.replace(/^0x/, '');
  } catch (_) {}
  gasKey = process.env.AAWP_GUARDIAN_KEY || process.env.AAWP_GAS_KEY || gasKey;

  const result = await socketQuery({
    cmd: 'sign',
    wallet: walletAddr,
    to: MULTICALL3_ADDR,
    value: '0x' + totalValue.toString(16),
    nonce: Number(nonce),
    deadline,
    chain_id: chain.chainId,
    rpc: chain.rpcOverride || chain.rpc,
    data,
    gas_key: gasKey,
  });

  if (result.error) throw new Error(`Batch sign failed: ${result.error}`);
  return result.result;
}

module.exports = { batchExecute, MULTICALL3_ADDR };
