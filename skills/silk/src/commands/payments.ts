import { loadConfig, getWallet, getApiUrl } from '../config.js';
import { createHttpClient } from '../client.js';
import { SdkError } from '../errors.js';
import { outputSuccess } from '../output.js';

export async function paymentsList(opts: { wallet?: string }) {
  const config = loadConfig();
  const wallet = getWallet(config, opts.wallet);
  const client = createHttpClient({ baseUrl: getApiUrl(config) });

  const res = await client.get(`/api/transfers`, { params: { wallet: wallet.address } });
  const transfers = res.data.data.transfers;

  outputSuccess({ transfers });
}

export async function paymentsGet(transferPda: string) {
  const config = loadConfig();
  const client = createHttpClient({ baseUrl: getApiUrl(config) });

  const res = await client.get(`/api/transfers/${transferPda}`);
  const transfer = res.data.data.transfer;

  if (!transfer) {
    throw new SdkError('TRANSFER_NOT_FOUND', `Transfer not found: ${transferPda}`);
  }

  outputSuccess({ transfer });
}
