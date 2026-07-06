#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional, named } = parseArgs(process.argv);
if (help || !positional[0] || !named.content) {
  console.error('Usage: send-message.mjs <order-id> --content "message text"');
  process.exit(2);
}

const data = await tmrFetch("POST", `/messages/orders/${positional[0]}`, {
  content: named.content,
});
console.log(JSON.stringify(data, null, 2));
