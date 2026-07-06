#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named.name) {
  console.error('Usage: create-contract-template.mjs --name X [--terms \'{"scope":"full"}\'] [--locked a,b] [--negotiable c,d]');
  process.exit(2);
}

const body = { name: named.name };
if (named.terms) body.default_terms = JSON.parse(named.terms);
if (named.locked) body.locked_fields = named.locked.split(",");
if (named.negotiable) body.negotiable_fields = named.negotiable.split(",");

const data = await tmrFetch("POST", "/contract-templates/", body);
console.log(JSON.stringify(data, null, 2));
