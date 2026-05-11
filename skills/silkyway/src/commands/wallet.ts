import { Keypair } from '@solana/web3.js';
import bs58 from 'bs58';
import { loadConfig, saveConfig, getWallet, getApiUrl } from '../config.js';
import { createHttpClient } from '../client.js';
import { SdkError } from '../errors.js';
import { outputSuccess } from '../output.js';

export async function walletCreate(label: string) {
  const config = loadConfig();

  if (config.wallets.find((w) => w.label === label)) {
    throw new SdkError('WALLET_EXISTS', `Wallet "${label}" already exists.`);
  }

  const keypair = Keypair.generate();
  const address = keypair.publicKey.toBase58();
  const privateKey = bs58.encode(keypair.secretKey);

  config.wallets.push({ label, address, privateKey });
  if (config.wallets.length === 1) {
    config.defaultWallet = label;
  }

  saveConfig(config);
  outputSuccess({ action: 'wallet_created', label, address });
}

export async function walletList() {
  const config = loadConfig();
  const wallets = config.wallets.map((w) => ({
    label: w.label,
    address: w.address,
    default: w.label === config.defaultWallet,
  }));
  outputSuccess({ wallets });
}

export async function walletFund(opts: { sol?: boolean; usdc?: boolean; wallet?: string }) {
  const config = loadConfig();
  const wallet = getWallet(config, opts.wallet);
  const client = createHttpClient({ baseUrl: getApiUrl(config) });

  const doSol = opts.sol || (!opts.sol && !opts.usdc);
  const doUsdc = opts.usdc || (!opts.sol && !opts.usdc);

  // Determine the token parameter for a single API call
  let token: string;
  if (doSol && doUsdc) {
    token = 'both';
  } else if (doSol) {
    token = 'sol';
  } else {
    token = 'usdc';
  }

  const funded: Record<string, unknown> = {};

  try {
    const res = await client.post('/api/tx/faucet', { wallet: wallet.address, token });
    if (res.data.data.sol) funded.sol = res.data.data.sol;
    if (res.data.data.usdc) funded.usdc = res.data.data.usdc;
  } catch (e: any) {
    funded.error = { code: e.code || 'FAUCET_FAILED', message: e.message };
  }

  outputSuccess({ action: 'wallet_funded', wallet: wallet.label, address: wallet.address, funded });
}
