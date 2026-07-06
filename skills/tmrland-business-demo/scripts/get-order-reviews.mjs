#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error("Usage: get-order-reviews.mjs <order-id>");
  process.exit(2);
}

const data = await tmrFetch("GET", `/reviews/order/${positional[0]}`);
console.log(JSON.stringify(data, null, 2));
