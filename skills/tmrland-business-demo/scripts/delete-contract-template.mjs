#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error("Usage: delete-contract-template.mjs <template-id>");
  process.exit(2);
}

await tmrFetch("DELETE", `/contract-templates/${positional[0]}`);
console.log("Template deleted.");
