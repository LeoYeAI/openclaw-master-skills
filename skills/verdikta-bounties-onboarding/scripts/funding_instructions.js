#!/usr/bin/env node
import './_env.js';
import { arg } from './_lib.js';

const address = arg('address');
if (!address) {
  console.error('Usage: node funding_instructions.js --address 0x...');
  process.exit(1);
}

const network = process.env.VERDIKTA_NETWORK || 'base';

console.log('Fund the bot wallet');
console.log('Network:', network === 'base' ? 'Base mainnet' : 'Base Sepolia');
console.log('Bot address:', address);
console.log('---');
console.log('Recommended path (simple):');
console.log('1) Buy ETH via Coinbase (credit card / bank)');
console.log('2) Send ETH on *Base* network to the bot address above');
console.log('---');
console.log('What the bot will do after ETH arrives:');
console.log('- Swap a user-chosen portion of ETH→LINK on Base for judgement fees');
console.log('- Optionally sweep excess ETH to an off-bot address (cold wallet)');
