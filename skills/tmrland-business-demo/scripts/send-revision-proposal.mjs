#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named, positional } = parseArgs(process.argv);
if (help || !positional[0] || !named.content) {
  console.error("Usage: send-revision-proposal.mjs <order-id> --content '...'");
  process.exit(2);
}

const data = await tmrFetch("POST", `/orders/${positional[0]}/revision-proposal`, { content: named.content });
console.log(JSON.stringify(data, null, 2));
