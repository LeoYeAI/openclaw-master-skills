#!/usr/bin/env node

// Disabled for security-hardening.
// Rationale: this script previously combined local file reads + outbound posting,
// which triggers code-safety exfiltration heuristics in shared skill contexts.
//
// Use one of these safer paths instead:
// 1) OpenClaw message/tooling flow from the agent runtime
// 2) Neynar posting flow with explicit, reviewed payload assembly

console.error('post_cast_farcaster_agent.js is disabled for security hardening.');
console.error('Use the Neynar/OpenClaw posting path instead.');
process.exit(1);
