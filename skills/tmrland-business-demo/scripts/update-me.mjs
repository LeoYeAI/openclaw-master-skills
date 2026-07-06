#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || (!named["display-name"] && !named.locale)) {
  console.error("Usage: update-me.mjs [--display-name X] [--locale zh|en]");
  process.exit(2);
}

const body = {};
if (named["display-name"]) body.display_name = named["display-name"];
if (named.locale) body.locale_preference = named.locale;

const data = await tmrFetch("PATCH", "/users/me", body);
console.log(JSON.stringify(data, null, 2));
