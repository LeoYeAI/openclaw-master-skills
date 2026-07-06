#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error("Usage: get-contract-template.mjs <template-id>");
  process.exit(2);
}

const data = await tmrFetch("GET", `/contract-templates/${positional[0]}`);
console.log(JSON.stringify(data, null, 2));
