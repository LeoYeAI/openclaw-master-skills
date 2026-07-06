#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help } = parseArgs(process.argv);
if (help) {
  console.error("Usage: get-kyc.mjs");
  process.exit(2);
}

const data = await tmrFetch("GET", "/wallet/kyc");
console.log(JSON.stringify(data, null, 2));
