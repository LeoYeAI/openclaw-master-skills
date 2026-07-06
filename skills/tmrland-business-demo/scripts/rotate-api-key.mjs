#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help) {
  console.error("Usage: rotate-api-key.mjs [--role personal|business]");
  process.exit(2);
}

const data = await tmrFetch("POST", "/api-keys/rotate", { role: named.role ?? "personal" });
console.log(JSON.stringify(data, null, 2));
