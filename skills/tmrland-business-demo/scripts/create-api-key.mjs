#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help) {
  console.error("Usage: create-api-key.mjs [--role personal|business] [--permissions read,write]");
  process.exit(2);
}

const body = { role: named.role ?? "personal" };
if (named.permissions) body.permissions = named.permissions.split(",");

const data = await tmrFetch("POST", "/api-keys", body);
console.log(`⚠️  Save this key now — it cannot be retrieved again:`);
console.log(`    ${data.raw_key}`);
console.log(JSON.stringify(data, null, 2));
