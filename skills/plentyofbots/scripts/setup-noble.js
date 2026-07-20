/**
 * setup-noble.js — Configure @noble/ed25519 v2 with Node.js crypto.
 *
 * @noble/ed25519 v2 requires explicit sha512 configuration.
 * Import this module before using any @noble/ed25519 functions.
 */

import { etc } from '@noble/ed25519';
import { createHash } from 'node:crypto';

if (!etc.sha512Sync) {
  etc.sha512Sync = (/** @type {Uint8Array} */ ...messages) => {
    const hash = createHash('sha512');
    for (const msg of messages) hash.update(msg);
    return new Uint8Array(hash.digest());
  };
}
