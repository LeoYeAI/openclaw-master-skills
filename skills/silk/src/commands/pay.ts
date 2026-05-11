import { Keypair, Transaction } from '@solana/web3.js';
import bs58 from 'bs58';
import { loadConfig, getWallet, getApiUrl, getClaimUrl } from '../config.js';
import { createHttpClient } from '../client.js';
import { outputSuccess } from '../output.js';
import { validatePay } from '../validate.js';
import { resolveRecipient } from '../contacts.js';

export async function pay(recipient: string, amount: string, opts: { memo?: string; wallet?: string }) {
  recipient = resolveRecipient(recipient);
  const config = loadConfig();
  const wallet = getWallet(config, opts.wallet);
  const client = createHttpClient({ baseUrl: getApiUrl(config) });

  const amountNum = await validatePay(client, recipient, amount, wallet.address);

  // 1. Build unsigned transaction
  const buildRes = await client.post('/api/tx/create-transfer', {
    sender: wallet.address,
    recipient,
    amount: amountNum,
    token: 'usdc',
    memo: opts.memo || '',
  });

  const { transaction: txBase64, transferPda } = buildRes.data.data;

  // 2. Sign the transaction
  const tx = Transaction.from(Buffer.from(txBase64, 'base64'));
  const keypair = Keypair.fromSecretKey(bs58.decode(wallet.privateKey));
  tx.sign(keypair);

  // 3. Submit signed transaction
  const submitRes = await client.post('/api/tx/submit', {
    signedTx: tx.serialize().toString('base64'),
  });

  const { txid } = submitRes.data.data;
  const claimUrl = getClaimUrl(config, transferPda);
  outputSuccess({ action: 'pay', transferPda, txid, amount: amountNum, recipient, claimUrl });
}
