#!/usr/bin/env node
/**
 * Transfer LSP7 Tokens CLI
 * 
 * Unified command that can use either direct or relay execution.
 * Uses the modular lib/ structure.
 * 
 * Usage:
 *   node transfer-lsp7.js <token> <to> <amount> [--relay]
 * 
 * Examples:
 *   # Direct execution (controller pays gas)
 *   node transfer-lsp7.js 0x403b... 0x378B... 100
 * 
 *   # Relay execution (gasless, requires SIGN permission)
 *   node transfer-lsp7.js 0x403b... 0x378B... 100 --relay
 */

import { 
  getLSP7Info, 
  getLSP7Balance, 
  buildLSP7TransferPayload, 
  validateLSP7Transfer 
} from '../lib/tokens/lsp7.js';
import { 
  buildExecutePayload, 
  executeDirect,
  executeRelay 
} from '../lib/execute/index.js';
import { loadCredentials } from '../lib/credentials.js';

async function transfer(tokenAddress, toAddress, amount, useRelay = false, options = {}) {
  const creds = loadCredentials();
  const upAddress = creds.universalProfile.address;

  console.log('🐙 LSP7 Token Transfer');
  console.log('======================');
  console.log('From UP:', upAddress);
  console.log('To:', toAddress);
  console.log('Amount:', amount);
  console.log('Mode:', useRelay ? 'Relay (gasless)' : 'Direct (pay gas)');
  console.log('');

  // Get token info
  const info = await getLSP7Info(tokenAddress);
  console.log(`Token: ${info.name} (${info.symbol})`);
  console.log(`Decimals: ${info.decimals}`);

  // Check balance
  const { formatted: balance } = await getLSP7Balance(tokenAddress, upAddress);
  console.log(`Balance: ${balance} ${info.symbol}`);
  console.log('');

  // Validate
  const validation = await validateLSP7Transfer(tokenAddress, upAddress, amount);
  if (!validation.valid) {
    console.error('❌', validation.error);
    process.exit(1);
  }

  // Build transfer payload
  console.log('📝 Building transaction...');
  const transferData = await buildLSP7TransferPayload(
    tokenAddress,
    upAddress,  // from
    toAddress,  // to
    amount
  );

  // Wrap in UP.execute()
  const payload = buildExecutePayload(
    0,             // CALL operation
    tokenAddress,  // target
    0,             // value (0 LYX)
    transferData   // calldata
  );

  // Execute
  console.log('📤 Sending transaction...');
  let result;
  
  if (useRelay) {
    result = await executeRelay(payload);
  } else {
    // Direct execution: controller calls UP.execute() and pays gas
    result = await executeDirect(
      0,             // CALL operation
      tokenAddress,  // target
      0,             // value (0)
      transferData,  // calldata
      { network: options.network || 'mainnet' }
    );
  }

  console.log('');
  console.log('✅ Transfer successful!');
  console.log('TX:', result.txHash);
  console.log('Explorer:', result.explorerUrl);

  return result;
}

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  const useRelay = args.includes('--relay');
  const filteredArgs = args.filter(a => a !== '--relay');
  
  const [tokenAddress, toAddress, amount] = filteredArgs;

  if (!tokenAddress || !toAddress || !amount) {
    console.error('Usage: node transfer-lsp7.js <token-address> <to-address> <amount> [--relay]');
    console.error('');
    console.error('Options:');
    console.error('  --relay    Use relay API (gasless, requires SIGN permission)');
    console.error('');
    console.error('Examples:');
    console.error('  node transfer-lsp7.js 0x403b... 0x378B... 100');
    console.error('  node transfer-lsp7.js 0x403b... 0x378B... 100 --relay');
    process.exit(1);
  }

  transfer(tokenAddress, toAddress, amount, useRelay).catch(error => {
    console.error('');
    console.error('❌ Error:', error.message);
    process.exit(1);
  });
}

export { transfer };
