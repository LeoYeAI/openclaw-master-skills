#!/usr/bin/env node
import './_env.js';
import { Contract, formatEther } from 'ethers';
import { getNetwork, providerFor, loadWallet, LINK, linkBalance, parseEth, arg } from './_lib.js';

const ethAmount = arg('eth');
if (!ethAmount) {
  console.error('Usage: node swap_eth_to_link_0x.js --eth 0.02');
  process.exit(1);
}

const network = getNetwork();
if (network !== 'base') {
  console.error('This script currently supports mainnet Base only (VERDIKTA_NETWORK=base).');
  process.exit(1);
}

const chainId = 8453;
const sellToken = 'ETH';
const buyToken = LINK[network];

const zeroX = process.env.ZEROX_BASE_URL || 'https://api.0x.org';
const apiKey = process.env.ZEROX_API_KEY;

const provider = providerFor(network);
const wallet = await loadWallet();
const signer = wallet.connect(provider);

const sellAmountWei = parseEth(ethAmount);

// Quote + transaction
const url = new URL(`${zeroX}/swap/v1/quote`);
url.searchParams.set('chainId', String(chainId));
url.searchParams.set('sellToken', sellToken);
url.searchParams.set('buyToken', buyToken);
url.searchParams.set('sellAmount', sellAmountWei.toString());
url.searchParams.set('takerAddress', signer.address);
url.searchParams.set('slippagePercentage', '0.01');

const headers = { 'Accept': 'application/json' };
if (apiKey) headers['0x-api-key'] = apiKey;

const resp = await fetch(url, { headers });
if (!resp.ok) {
  const text = await resp.text();
  throw new Error(`0x quote failed: ${resp.status} ${text}`);
}
const quote = await resp.json();

// Send tx
const tx = await signer.sendTransaction({
  to: quote.to,
  data: quote.data,
  value: BigInt(quote.value || sellAmountWei.toString()),
  gasLimit: quote.gas ? BigInt(quote.gas) : undefined
});
console.log('Sent swap tx:', tx.hash);
const receipt = await tx.wait();
console.log('Confirmed in block:', receipt.blockNumber);

const { bal, dec, linkAddr } = await linkBalance(network, provider, signer.address);
const link = new Contract(linkAddr, ['function symbol() view returns (string)'], provider);
const sym = await link.symbol();
const human = Number(bal) / (10 ** dec);
console.log(`LINK balance: ~${human.toFixed(4)} ${sym}`);
console.log(`ETH remaining: ${formatEther(await provider.getBalance(signer.address))}`);
