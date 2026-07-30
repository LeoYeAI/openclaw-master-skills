/**
 * Token Modules Index
 * 
 * Re-exports all token-related functions.
 * Each token module builds calldata only - use execute/ to send transactions.
 */

// LSP7 - Fungible tokens
export {
  getLSP7Info,
  getLSP7Balance,
  buildLSP7TransferPayload,
  validateLSP7Transfer
} from './lsp7.js';

// LSP8 - NFTs / Identifiable Digital Assets
export {
  getLSP8Info,
  getLSP8TokensOf,
  buildLSP8TransferPayload
} from './lsp8.js';

// Default export
import lsp7 from './lsp7.js';
import lsp8 from './lsp8.js';

export default {
  lsp7,
  lsp8
};
