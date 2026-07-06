#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional, named } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error('Usage: update-contract-template.mjs <template-id> [--name X] [--terms \'{"scope":"full"}\']');
  process.exit(2);
}

const body = {};
if (named.name) body.name = named.name;
if (named.terms) body.default_terms = JSON.parse(named.terms);

const data = await tmrFetch("PATCH", `/contract-templates/${positional[0]}`, body);
console.log(JSON.stringify(data, null, 2));
