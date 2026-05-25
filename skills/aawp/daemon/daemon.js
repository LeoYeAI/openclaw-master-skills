#!/usr/bin/env node
'use strict';
const addon = require(process.env.AAWP_CORE || '/root/clawd/skills/aawp/core/aawp-core.node');
const C = process.env.AAWP_CONFIG || '/root/clawd/skills/aawp/.agent-config';
const S = process.env.AAWP_SKILL  || '/root/clawd/skills/aawp';
addon._l0(C, S, process.env.AAWP_LOG || '/tmp/aawp-daemon.log');
addon._a0(); // start accepting connections (v2.1.0+)
const sockPath = addon._x0(); // get socket path
require('fs').writeFileSync('/tmp/.aawp-daemon.lock', JSON.stringify({sock: sockPath}));
console.log('[AAWP] listening on', sockPath);
setInterval(() => {}, 1 << 30);
