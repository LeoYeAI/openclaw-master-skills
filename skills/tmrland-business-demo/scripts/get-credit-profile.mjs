#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error("Usage: get-credit-profile.mjs <business-id>");
  process.exit(2);
}

const data = await tmrFetch("GET", `/credit/${positional[0]}/profile`);
console.log(JSON.stringify(data, null, 2));
