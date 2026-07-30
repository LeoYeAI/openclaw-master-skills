#!/usr/bin/env node

/**
 * cross-chain-deploy-data.js
 *
 * Retrieves the LSP23 deployment calldata for a Universal Profile,
 * enabling cross-chain redeployment on any network where the same
 * LSP23 factory and implementation contracts are deployed.
 *
 * Usage:
 *   node cross-chain-deploy-data.js <upAddress> [--chain lukso|lukso-testnet] [--verify]
 *
 * The --verify flag checks that the required base contracts exist on
 * all supported target chains (Base, Ethereum).
 */

import { ethers } from 'ethers';

// ── Constants ──────────────────────────────────────────────────────

const LSP23_FACTORY = '0x2300000A84D25dF63081feAa37ba6b62C4c89a30';

const EVENTS = {
  DeployedERC1167Proxies: '0xe20570ed9bda3b93eea277b4e5d975c8933fd5f85f2c824d0845ae96c55a54fe',
  DeployedContracts: '0x1ea27dabd8fd1508e844ab51c2fd3d9081f2684346857f9187da6d4a1aa7d3e6',
};

const DEPLOY_SELECTOR = '0x6a66a753'; // deployERC1167Proxies

// Base contracts that must exist on target chains for redeployment
const BASE_CONTRACTS = {
  LSP23LinkedContractsFactory: '0x2300000A84D25dF63081feAa37ba6b62C4c89a30',
  UniversalProfileInit_v014: '0x3024D38EA2434BA6635003Dc1BDC0daB5882ED4F',
  LSP6KeyManagerInit_v014: '0x2Fe3AeD98684E7351aD2D408A43cE09a738BF8a4',
  PostDeploymentModule: '0x000000000066093407b6704B89793beFfD0D8F00',
};

const RPCS = {
  lukso: 'https://rpc.mainnet.lukso.network',
  'lukso-testnet': 'https://rpc.testnet.lukso.network',
  base: 'https://mainnet.base.org',
  ethereum: 'https://eth.llamarpc.com',
};

// ── Core Functions ─────────────────────────────────────────────────

/**
 * Find the LSP23 deployment event for a Universal Profile.
 * Returns the transaction hash of the deployment.
 */
async function findDeploymentTx(upAddress, rpcUrl) {
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const upTopic = ethers.zeroPadValue(upAddress, 32);

  // Try proxy deployment first (most common)
  let logs = await provider.getLogs({
    address: LSP23_FACTORY,
    topics: [EVENTS.DeployedERC1167Proxies, upTopic],
    fromBlock: 0,
    toBlock: 'latest',
  });

  let deploymentType = 'proxy';

  // Fall back to full contract deployment
  if (logs.length === 0) {
    logs = await provider.getLogs({
      address: LSP23_FACTORY,
      topics: [EVENTS.DeployedContracts, upTopic],
      fromBlock: 0,
      toBlock: 'latest',
    });
    deploymentType = 'full';
  }

  if (logs.length === 0) {
    return null;
  }

  return {
    txHash: logs[0].transactionHash,
    blockNumber: parseInt(logs[0].blockNumber, 16) || logs[0].blockNumber,
    deploymentType,
    keyManagerAddress: logs[0].topics[2]
      ? ethers.getAddress('0x' + logs[0].topics[2].slice(26))
      : null,
  };
}

/**
 * Get the full deployment calldata from a transaction.
 */
async function getDeploymentCalldata(txHash, rpcUrl) {
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const tx = await provider.getTransaction(txHash);

  if (!tx) throw new Error(`Transaction ${txHash} not found`);
  if (tx.to?.toLowerCase() !== LSP23_FACTORY.toLowerCase()) {
    throw new Error(`Transaction target is not LSP23 factory: ${tx.to}`);
  }

  const selector = tx.data.slice(0, 10);
  if (selector !== DEPLOY_SELECTOR) {
    console.warn(`⚠️  Unexpected function selector: ${selector} (expected ${DEPLOY_SELECTOR})`);
  }

  return {
    factoryAddress: tx.to,
    calldata: tx.data,
    calldataLength: (tx.data.length - 2) / 2,
    functionSelector: selector,
    value: tx.value.toString(),
    from: tx.from,
  };
}

/**
 * Verify that all required base contracts exist on a target chain.
 */
async function verifyBaseContracts(rpcUrl, chainName) {
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const results = {};
  let allPresent = true;

  for (const [name, address] of Object.entries(BASE_CONTRACTS)) {
    const code = await provider.getCode(address);
    const present = code !== '0x' && code.length > 2;
    const byteSize = present ? (code.length - 2) / 2 : 0;
    results[name] = { address, present, byteSize };
    if (!present) allPresent = false;
  }

  return { chain: chainName, allPresent, contracts: results };
}

/**
 * Full retrieval: find deployment + get calldata + optional verification.
 */
async function getCrossChainDeployData(upAddress, options = {}) {
  const chain = options.chain || 'lukso';
  const rpcUrl = RPCS[chain];
  if (!rpcUrl) throw new Error(`Unknown chain: ${chain}`);

  // 1. Find deployment
  const deployment = await findDeploymentTx(upAddress, rpcUrl);
  if (!deployment) {
    throw new Error(
      `No LSP23 deployment found for ${upAddress} on ${chain}. ` +
        'This UP may have been deployed via legacy lsp-factory (pre-LSP23).'
    );
  }

  // 2. Get calldata
  const calldataInfo = await getDeploymentCalldata(deployment.txHash, rpcUrl);

  const result = {
    upAddress: ethers.getAddress(upAddress),
    keyManagerAddress: deployment.keyManagerAddress,
    sourceChain: chain,
    deploymentType: deployment.deploymentType,
    blockNumber: deployment.blockNumber,
    txHash: deployment.txHash,
    factoryAddress: calldataInfo.factoryAddress,
    functionSelector: calldataInfo.functionSelector,
    calldataLength: calldataInfo.calldataLength,
    calldata: calldataInfo.calldata,
    value: calldataInfo.value,
  };

  // 3. Optional: verify target chains
  if (options.verify) {
    const targetChains = ['lukso', 'base', 'ethereum'].filter((c) => c !== chain);
    result.targetChainVerification = {};
    for (const target of targetChains) {
      result.targetChainVerification[target] = await verifyBaseContracts(RPCS[target], target);
    }
  }

  return result;
}

// ── CLI ────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const upAddress = args.find((a) => a.startsWith('0x'));
  const chain = args.includes('--chain') ? args[args.indexOf('--chain') + 1] : 'lukso';
  const verify = args.includes('--verify');
  const jsonOutput = args.includes('--json');

  if (!upAddress) {
    console.error('Usage: cross-chain-deploy-data.js <upAddress> [--chain lukso] [--verify] [--json]');
    process.exit(1);
  }

  try {
    const result = await getCrossChainDeployData(upAddress, { chain, verify });

    if (jsonOutput) {
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    console.log('\n🔗 LSP23 Cross-Chain Deployment Data');
    console.log('════════════════════════════════════════');
    console.log(`UP Address:       ${result.upAddress}`);
    console.log(`KeyManager:       ${result.keyManagerAddress}`);
    console.log(`Source Chain:     ${result.sourceChain}`);
    console.log(`Deployment Type:  ${result.deploymentType}`);
    console.log(`Block:            ${result.blockNumber}`);
    console.log(`TX Hash:          ${result.txHash}`);
    console.log(`Factory:          ${result.factoryAddress}`);
    console.log(`Selector:         ${result.functionSelector}`);
    console.log(`Calldata Size:    ${result.calldataLength} bytes`);
    console.log(`Value:            ${result.value} wei`);
    console.log('\n📦 Calldata:');
    console.log(result.calldata);

    if (result.targetChainVerification) {
      console.log('\n🌐 Target Chain Verification:');
      for (const [chainName, info] of Object.entries(result.targetChainVerification)) {
        const status = info.allPresent ? '✅' : '❌';
        console.log(`\n  ${status} ${chainName}`);
        for (const [name, contract] of Object.entries(info.contracts)) {
          const icon = contract.present ? '✅' : '❌';
          const size = contract.present ? `${contract.byteSize.toLocaleString()} bytes` : 'missing';
          console.log(`    ${icon} ${name}: ${size}`);
        }
      }
    }

    console.log('\n💡 To redeploy on another chain, send this calldata to');
    console.log(`   ${result.factoryAddress} on the target chain.`);
    console.log('   The same salt produces the same UP address.\n');
  } catch (err) {
    console.error(`❌ ${err.message}`);
    process.exit(1);
  }
}

export { getCrossChainDeployData, findDeploymentTx, getDeploymentCalldata, verifyBaseContracts, BASE_CONTRACTS, RPCS, LSP23_FACTORY };

// Run CLI only when executed directly
const isDirectRun = process.argv[1] && (
  process.argv[1].endsWith('cross-chain-deploy-data.js') ||
  process.argv[1].endsWith('cross-chain-deploy-data')
);
if (isDirectRun) main();
