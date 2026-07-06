#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error("Usage: revoke-api-key.mjs <key-id>");
  process.exit(2);
}

await tmrFetch("DELETE", `/api-keys/${positional[0]}`);
console.log("API key revoked.");
