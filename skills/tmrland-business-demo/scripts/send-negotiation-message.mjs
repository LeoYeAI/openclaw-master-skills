#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional, named } = parseArgs(process.argv);
if (help || !positional[0] || !named.content) {
  console.error('Usage: send-negotiation-message.mjs <session-id> --content "message text"');
  process.exit(2);
}

const data = await tmrFetch("POST", `/negotiations/${positional[0]}/messages`, {
  content: named.content,
});
console.log(JSON.stringify(data, null, 2));
