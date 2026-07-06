#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional, named } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error('Usage: negotiation-messages.mjs <session-id> [--send "message text"]');
  process.exit(2);
}

const sessionId = positional[0];

if (named.send) {
  const msg = await tmrFetch("POST", `/negotiations/${sessionId}/messages`, {
    content: named.send,
  });
  console.log(JSON.stringify(msg, null, 2));
}

const data = await tmrFetch("GET", `/negotiations/${sessionId}/messages`);
console.log(JSON.stringify(data, null, 2));
