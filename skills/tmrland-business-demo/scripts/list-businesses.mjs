#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help) {
  console.error("Usage: list-businesses.mjs [--limit N]");
  process.exit(2);
}

const limit = Number.parseInt(named.limit ?? "20", 10);
const data = await tmrFetch("GET", `/businesses/?limit=${limit}`);
console.log(JSON.stringify(data, null, 2));
