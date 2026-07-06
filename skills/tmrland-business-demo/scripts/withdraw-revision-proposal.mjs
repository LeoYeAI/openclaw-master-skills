#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named, positional } = parseArgs(process.argv);
if (help || !positional[0] || !named.message_id) {
  console.error("Usage: withdraw-revision-proposal.mjs <order-id> --message_id <uuid>");
  process.exit(2);
}

const data = await tmrFetch("POST", `/orders/${positional[0]}/withdraw-revision`, { message_id: named.message_id });
console.log(JSON.stringify(data, null, 2));
