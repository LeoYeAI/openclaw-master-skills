#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error("Usage: get-reputation.mjs <business-id>");
  process.exit(2);
}

const data = await tmrFetch("GET", `/reviews/reputation/${positional[0]}`);
console.log(JSON.stringify(data, null, 2));
