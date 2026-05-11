#!/usr/bin/env node
import './_env.js';
import { formatEther, formatUnits } from 'ethers';
import { getNetwork, providerFor, loadWallet, linkBalance } from './_lib.js';

const network = getNetwork();
const provider = providerFor(network);
const wallet = await loadWallet();
const address = wallet.address;

const ethBal = await provider.getBalance(address);
const { bal, dec, linkAddr } = await linkBalance(network, provider, address);
const linkHuman = Number(formatUnits(bal, dec));

console.log('Funding status');
console.log('Network:', network);
console.log('Address:', address);
console.log('ETH:', formatEther(ethBal));
console.log('LINK token:', linkAddr);
console.log('LINK:', linkHuman.toFixed(6));
