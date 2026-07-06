#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help) {
  console.error("Usage: list-questions.mjs [--category X] [--sort hot] [--limit N]");
  process.exit(2);
}

const limit = Number.parseInt(named.limit ?? "20", 10);
const sort = named.sort ?? "created_at";
let path = `/apparatus/?sort_by=${sort}&limit=${limit}`;
if (named.category) path += `&category=${named.category}`;

const data = await tmrFetch("GET", path);
console.log(JSON.stringify(data, null, 2));
