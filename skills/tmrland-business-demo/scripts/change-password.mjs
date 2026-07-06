#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named.current || !named.new) {
  console.error("Usage: change-password.mjs --current <password> --new <password>");
  process.exit(2);
}

await tmrFetch("PATCH", "/users/me/password", {
  current_password: named.current,
  new_password: named.new,
});
console.log("Password changed successfully.");
