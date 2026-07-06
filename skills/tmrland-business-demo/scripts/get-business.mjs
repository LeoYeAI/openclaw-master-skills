#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error("Usage: get-business.mjs <business-id>");
  process.exit(2);
}

const data = await tmrFetch("GET", `/businesses/${positional[0]}`);
console.log(JSON.stringify(data, null, 2));
