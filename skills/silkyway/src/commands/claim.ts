import { Keypair, Transaction } from '@solana/web3.js';
import bs58 from 'bs58';
import { loadConfig, getWallet, getApiUrl } from '../config.js';
import { createHttpClient } from '../client.js';
import { outputSuccess } from '../output.js';
import { validateClaim } from '../validate.js';

export async function claim(transferPda: string, opts: { wallet?: string }) {
  const config = loadConfig();
  const wallet = getWallet(config, opts.wallet);
  const client = createHttpClient({ baseUrl: getApiUrl(config) });

  await validateClaim(client, transferPda, wallet.address);

  // 1. Build unsigned claim tx
  const buildRes = await client.post('/api/tx/claim-transfer', {
    claimer: wallet.address,
    transferPda,
  });

  const txBase64 = buildRes.data.data.transaction;

  // 2. Sign
  const tx = Transaction.from(Buffer.from(txBase64, 'base64'));
  const keypair = Keypair.fromSecretKey(bs58.decode(wallet.privateKey));
  tx.sign(keypair);

  // 3. Submit
  const submitRes = await client.post('/api/tx/submit', {
    signedTx: tx.serialize().toString('base64'),
  });

  outputSuccess({ action: 'claim', transferPda, txid: submitRes.data.data.txid });
}
