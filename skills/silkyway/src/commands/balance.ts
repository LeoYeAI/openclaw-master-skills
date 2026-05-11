import { loadConfig, getWallet, getApiUrl } from '../config.js';
import { createHttpClient } from '../client.js';
import { outputSuccess } from '../output.js';

export async function balance(opts: { wallet?: string }) {
  const config = loadConfig();
  const wallet = getWallet(config, opts.wallet);
  const client = createHttpClient({ baseUrl: getApiUrl(config) });

  const res = await client.get(`/api/wallet/${wallet.address}/balance`);
  const data = res.data.data;

  outputSuccess({ wallet: wallet.label, address: wallet.address, sol: data.sol, tokens: data.tokens });
}
