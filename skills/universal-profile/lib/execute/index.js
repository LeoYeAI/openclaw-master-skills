/**
 * Execute Module - Multi-Chain Transaction Execution
 * 
 * Two execution methods:
 * 
 * 1. DIRECT (all chains) — Controller calls UP.execute() and pays gas
 *    - executeDirect(operation, target, value, data, { network })
 *    - executeBatch(calls, { network })
 * 
 * 2. RELAY (LUKSO only) — Gasless via LUKSO relay service API
 *    - executeRelay(payload, { network })
 *    - Requires SIGN + EXECUTE_RELAY_CALL permissions and relay quota
 * 
 * Supported networks: 'mainnet' (LUKSO), 'testnet', 'base', 'ethereum'
 * 
 * Example:
 *   import { executeDirect, buildExecutePayload } from './lib/execute/index.js';
 *   import { buildLSP7TransferPayload } from './lib/tokens/lsp7.js';
 *   
 *   const tokenData = await buildLSP7TransferPayload(tokenAddr, from, to, amount);
 *   const { txHash } = await executeDirect(0, tokenAddr, 0, tokenData, { network: 'base' });
 */

export { 
  executeDirect, 
  executeBatch,
  buildExecutePayload 
} from './direct.js';

export { 
  executeRelay, 
  getRelayQuota 
} from './relay.js';

import directModule from './direct.js';
import relayModule from './relay.js';

export default {
  ...directModule,
  ...relayModule
};
