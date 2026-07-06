#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help } = parseArgs(process.argv);
if (help) {
  console.error("Usage: mark-all-read.mjs");
  process.exit(2);
}

const data = await tmrFetch("POST", "/notifications/read-all");
console.log(JSON.stringify(data, null, 2));
