#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error("Usage: get-credit-reviews.mjs <business-id>");
  process.exit(2);
}

const data = await tmrFetch("GET", `/credit/${positional[0]}/reviews`);
console.log(JSON.stringify(data, null, 2));
