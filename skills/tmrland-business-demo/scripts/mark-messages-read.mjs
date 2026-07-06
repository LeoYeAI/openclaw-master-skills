#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error("Usage: mark-messages-read.mjs <order-id>");
  process.exit(2);
}

const data = await tmrFetch("POST", `/messages/orders/${positional[0]}/read`);
console.log(JSON.stringify(data, null, 2));
