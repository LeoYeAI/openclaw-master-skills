import { createClient } from './client.js';
import { formatApiError, formatNetworkError, isApiSuccess } from './errors.js';

export async function executeBalance(_input, ctx) {
  const client = createClient(ctx);

  let res;
  try {
    res = await client.get('/v1/generation/balance', { retries: 3 });
  } catch (err) {
    return formatNetworkError(err);
  }

  if (!isApiSuccess(res)) {
    return formatApiError(res);
  }

  const credits = typeof res.data === 'number' ? res.data : (res.data?.balance ?? res.data);
  return {
    ok: true,
    phase: 'completed',
    balance: credits,
    errorCode: null,
    errorMessage: null,
  };
}
