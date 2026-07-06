#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help) {
  console.error("Usage: list-negotiations.mjs [--intention <id>]");
  process.exit(2);
}

let path = "/negotiations/?role=business";
if (named.intention) path += `&intention_id=${named.intention}`;

const data = await tmrFetch("GET", path);
console.log(JSON.stringify(data, null, 2));
