'use strict';
const crypto = require('crypto');
const a = require('./aawp-core.node');
const C = process.env.AAWP_CONFIG || '/root/clawd/skills/aawp/.agent-config';
const S = process.env.AAWP_SKILL  || '/root/clawd/skills/aawp';

// Generate a cryptographically random 32-byte AI gate token at module load.
// This token is injected into AAWP_AI_TOKEN env before _l0 starts the daemon.
// The daemon reads it, arms the gate, then clears the env var from its process.
// OpenClaw uses getToken() to retrieve the current token before spawning wallet-manager.js.
const _initialToken = crypto.randomBytes(32).toString('hex');
process.env.AAWP_AI_TOKEN = _initialToken;

module.exports = {
  init:       () => a._l0(C, S, '/tmp/aawp.log'),
  lh:         () => a._c0(S),
  signer:     (lh) => a._g0(C, lh || a._c0(S)),
  relay:      () => a._r0(C),
  sign:       (payload) => a._s0(payload),
  // Returns current AI gate token for injection into child process env.
  // Must be called right before spawning wallet-manager.js.
  getToken:   () => a._a0(),
};
