import { Keypair, Transaction } from '@solana/web3.js';
import bs58 from 'bs58';
import { loadConfig, saveConfig, getWallet, getApiUrl, getSetupUrl, AccountInfo } from '../config.js';
import { createHttpClient } from '../client.js';
import { outputSuccess } from '../output.js';
import { SdkError, toSilkysigError } from '../errors.js';
import { validateAddress, validateAmount } from '../validate.js';
import { resolveRecipient } from '../contacts.js';

interface OperatorSlot {
  index: number;
  perTxLimit: string;
}

interface ByOperatorAccount {
  pda: string;
  owner: string;
  mint: string;
  mintDecimals: number;
  isPaused: boolean;
  balance: number;
  operatorSlot: OperatorSlot | null;
}

interface AccountDetail {
  pda: string;
  owner: string;
  mint: string;
  mintDecimals: number;
  isPaused: boolean;
  balance: number;
  operators: Array<{
    index: number;
    pubkey: string;
    perTxLimit: string;
  }>;
}

export async function accountSync(opts: { wallet?: string; account?: string }) {
  const config = loadConfig();
  const wallet = getWallet(config, opts.wallet);
  const client = createHttpClient({ baseUrl: getApiUrl(config) });

  if (opts.account) {
    // Direct PDA sync
    validateAddress(opts.account, 'account');
    const res = await client.get(`/api/account/${opts.account}`);
    const acct: AccountDetail = res.data.data;

    // Verify wallet is an operator on this account
    const op = acct.operators.find((o) => o.pubkey === wallet.address);
    if (!op) {
      throw new SdkError(
        'NOT_OPERATOR',
        `Wallet "${wallet.label}" (${wallet.address}) is not an operator on account ${opts.account}`,
      );
    }

    const accountInfo: AccountInfo = {
      pda: acct.pda,
      owner: acct.owner,
      mint: acct.mint,
      mintDecimals: acct.mintDecimals,
      operatorIndex: op.index,
      perTxLimit: Number(op.perTxLimit),
      syncedAt: new Date().toISOString(),
    };
    config.account = accountInfo;
    saveConfig(config);

    const balanceHuman = acct.mintDecimals > 0 ? acct.balance / 10 ** acct.mintDecimals : acct.balance;
    const perTxLimitHuman = acct.mintDecimals > 0 ? Number(op.perTxLimit) / 10 ** acct.mintDecimals : Number(op.perTxLimit);

    outputSuccess({
      action: 'sync',
      pda: acct.pda,
      owner: acct.owner,
      balance: balanceHuman,
      perTxLimit: perTxLimitHuman,
      mint: acct.mint,
    });
    return;
  }

  // Discover by operator
  const res = await client.get(`/api/account/by-operator/${wallet.address}`);
  const accounts: ByOperatorAccount[] = res.data.data.accounts;

  if (accounts.length === 0) {
    outputSuccess({
      action: 'sync',
      found: 0,
      message: `No account found for wallet "${wallet.label}" (${wallet.address}).`,
      hint: `Ask your human to set up your account at:\n  ${getSetupUrl(config, wallet.address)}`,
    });
    return;
  }

  // Deterministic selection: sort by PDA so the same account is always picked
  accounts.sort((a, b) => a.pda.localeCompare(b.pda));
  const selected = accounts[0];
  const slot = selected.operatorSlot!;

  const accountInfo: AccountInfo = {
    pda: selected.pda,
    owner: selected.owner,
    mint: selected.mint,
    mintDecimals: selected.mintDecimals,
    operatorIndex: slot.index,
    perTxLimit: Number(slot.perTxLimit),
    syncedAt: new Date().toISOString(),
  };
  config.account = accountInfo;
  saveConfig(config);

  const formatBalance = (bal: number, decimals: number) => decimals > 0 ? bal / 10 ** decimals : bal;
  const formatLimit = (limit: string, decimals: number) => decimals > 0 ? Number(limit) / 10 ** decimals : Number(limit);

  if (accounts.length === 1) {
    outputSuccess({
      action: 'sync',
      pda: selected.pda,
      owner: selected.owner,
      balance: formatBalance(selected.balance, selected.mintDecimals),
      perTxLimit: formatLimit(slot.perTxLimit, selected.mintDecimals),
      mint: selected.mint,
    });
  } else {
    outputSuccess({
      action: 'sync',
      pda: selected.pda,
      owner: selected.owner,
      balance: formatBalance(selected.balance, selected.mintDecimals),
      perTxLimit: formatLimit(slot.perTxLimit, selected.mintDecimals),
      mint: selected.mint,
      warning: `This wallet is operator on ${accounts.length} accounts. Using ${selected.pda}. The SDK currently supports one account at a time. To target a specific account: silk account sync --account <pda>`,
      allAccounts: accounts.map((a) => ({
        pda: a.pda,
        owner: a.owner,
        balance: formatBalance(a.balance, a.mintDecimals),
      })),
    });
  }
}

export async function accountStatus(opts: { wallet?: string }) {
  const config = loadConfig();
  getWallet(config, opts.wallet); // validate wallet exists

  if (!config.account) {
    throw new SdkError('NO_ACCOUNT', 'No account synced. Run: silk account sync');
  }

  const client = createHttpClient({ baseUrl: getApiUrl(config) });
  const res = await client.get(`/api/account/${config.account.pda}`);
  const acct: AccountDetail = res.data.data;

  const op = acct.operators.find((o) => o.index === config.account!.operatorIndex);
  const perTxLimit = op ? Number(op.perTxLimit) : config.account.perTxLimit;
  const perTxLimitHuman = acct.mintDecimals > 0 ? perTxLimit / 10 ** acct.mintDecimals : perTxLimit;
  const balanceHuman = acct.mintDecimals > 0 ? acct.balance / 10 ** acct.mintDecimals : acct.balance;

  outputSuccess({
    action: 'status',
    pda: acct.pda,
    owner: acct.owner,
    balance: balanceHuman,
    mint: acct.mint,
    isPaused: acct.isPaused,
    operatorIndex: config.account.operatorIndex,
    perTxLimit: perTxLimitHuman,
  });
}

export async function accountEvents(opts: { type?: string; wallet?: string }) {
  const config = loadConfig();
  getWallet(config, opts.wallet); // validate wallet exists

  if (!config.account) {
    throw new SdkError('NO_ACCOUNT', 'No account synced. Run: silk account sync');
  }

  const client = createHttpClient({ baseUrl: getApiUrl(config) });
  const params = opts.type ? `?eventType=${opts.type}` : '';
  const res = await client.get(`/api/account/${config.account.pda}/events${params}`);
  const events = res.data.data;

  outputSuccess({ action: 'events', pda: config.account.pda, events });
}

export async function accountDeposit(amount: string, opts: { wallet?: string }) {
  const config = loadConfig();
  const wallet = getWallet(config, opts.wallet);

  if (!config.account) {
    throw new SdkError('NO_ACCOUNT', 'No account synced. Run: silk account sync');
  }

  const amountNum = validateAmount(amount);
  const amountRaw = Math.round(amountNum * 10 ** config.account.mintDecimals);

  const client = createHttpClient({ baseUrl: getApiUrl(config) });

  // 1. Build unsigned transaction
  const buildRes = await client.post('/api/account/deposit', {
    depositor: wallet.address,
    accountPda: config.account.pda,
    amount: amountRaw,
  });

  const { transaction: txBase64 } = buildRes.data.data;

  // 2. Sign the transaction
  const tx = Transaction.from(Buffer.from(txBase64, 'base64'));
  const keypair = Keypair.fromSecretKey(bs58.decode(wallet.privateKey));
  tx.sign(keypair);

  // 3. Submit signed transaction
  try {
    const submitRes = await client.post('/api/tx/submit', {
      signedTx: tx.serialize().toString('base64'),
    });

    const { txid } = submitRes.data.data;
    outputSuccess({ action: 'deposit', txid, amount: amountNum });
  } catch (err) {
    throw toSilkysigError(err);
  }
}

export async function accountWithdraw(amount: string, opts: { wallet?: string }) {
  const config = loadConfig();
  const wallet = getWallet(config, opts.wallet);

  if (!config.account) {
    throw new SdkError('NO_ACCOUNT', 'No account synced. Run: silk account sync');
  }

  const amountNum = validateAmount(amount);
  const amountRaw = Math.round(amountNum * 10 ** config.account.mintDecimals);

  const client = createHttpClient({ baseUrl: getApiUrl(config) });

  // 1. Build unsigned transaction (transfer back to own wallet)
  const buildRes = await client.post('/api/account/transfer', {
    signer: wallet.address,
    accountPda: config.account.pda,
    recipient: wallet.address,
    amount: amountRaw,
  });

  const { transaction: txBase64 } = buildRes.data.data;

  // 2. Sign the transaction
  const tx = Transaction.from(Buffer.from(txBase64, 'base64'));
  const keypair = Keypair.fromSecretKey(bs58.decode(wallet.privateKey));
  tx.sign(keypair);

  // 3. Submit signed transaction
  try {
    const submitRes = await client.post('/api/tx/submit', {
      signedTx: tx.serialize().toString('base64'),
    });

    const { txid } = submitRes.data.data;
    outputSuccess({ action: 'withdraw', txid, amount: amountNum });
  } catch (err) {
    throw toSilkysigError(err);
  }
}

export async function accountSend(recipient: string, amount: string, opts: { memo?: string; wallet?: string }) {
  recipient = resolveRecipient(recipient);
  const config = loadConfig();
  const wallet = getWallet(config, opts.wallet);

  if (!config.account) {
    throw new SdkError('NO_ACCOUNT', 'No account synced. Run: silk account sync');
  }

  validateAddress(recipient, 'recipient');
  const amountNum = validateAmount(amount);

  // Convert to smallest units
  const amountRaw = Math.round(amountNum * 10 ** config.account.mintDecimals);

  const client = createHttpClient({ baseUrl: getApiUrl(config) });

  // 1. Build unsigned transaction
  const buildRes = await client.post('/api/account/transfer', {
    signer: wallet.address,
    accountPda: config.account.pda,
    recipient,
    amount: amountRaw,
  });

  const { transaction: txBase64 } = buildRes.data.data;

  // 2. Sign the transaction
  const tx = Transaction.from(Buffer.from(txBase64, 'base64'));
  const keypair = Keypair.fromSecretKey(bs58.decode(wallet.privateKey));
  tx.sign(keypair);

  // 3. Submit signed transaction
  try {
    const submitRes = await client.post('/api/tx/submit', {
      signedTx: tx.serialize().toString('base64'),
    });

    const { txid } = submitRes.data.data;
    outputSuccess({ action: 'send', txid, amount: amountNum, recipient });
  } catch (err) {
    throw toSilkysigError(err);
  }
}
